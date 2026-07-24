"""Regression tripwire: examples/ai-ml-intern/resume.pdf is a tracked,
committed artifact rendered from evals/fixtures/resume-sample/resume.yaml
via render.sh -t compact. Two consecutive external review rounds caught
it stale after template edits — nothing re-rendered it and nothing
noticed the committed PDF no longer matched what the current templates
+ yaml would produce. This test closes that gap.

Pinned-epoch design (why, and what was rejected)
-------------------------------------------------
render.sh derives SOURCE_DATE_EPOCH from the data file's mtime when the
caller doesn't set one, specifically so a byte-identical re-render is
possible — but `git checkout` (and any fresh clone, and CI) resets
mtimes to checkout time, so re-rendering the fixture as-is and comparing
against the tracked PDF would pass or fail based on checkout time, not
on drift. Three ways to pin the epoch were considered:

  (a) Read it back out of the tracked PDF's own docinfo. Typst stamps
      /CreationDate from SOURCE_DATE_EPOCH verbatim (as a UTC
      `D:YYYYMMDDHHMMSSZ` string), so the committed PDF already carries
      the exact epoch that produced it. Self-contained: no new
      committed file, nothing to keep in sync, survives checkout and
      fresh clones equally. Verified empirically before writing this
      test: extracted 20260720191510Z from the committed PDF, converted
      to epoch 1784574910, re-rendered the fixture with
      SOURCE_DATE_EPOCH=1784574910 -t compact into scratch, and its
      sha256 matched the tracked PDF exactly (see below). CHOSEN.

  (b) A committed epoch record beside the example (e.g. a `.epoch`
      file). Works, but is a second source of truth that itself can go
      stale independently of the PDF — and (a) makes it unnecessary
      since the PDF already carries the value. Rejected: no benefit
      over (a), one more file to forget to update.

  (c) `git log -1 --format=%ct` on the yaml fixture or the PDF. Rejected
      outright per the task brief: the worktree carries uncommitted
      round-5/6 changes touching this exact PDF right now, so its
      working-tree mtime and its last-commit time both reflect
      mid-review churn, not a stable release epoch. Even ignoring that,
      it's git-history-shaped state riding along with a content
      freshness check, which is more moving parts than (a) needs.

Verification transcript for (a) (2026-07-22, scratch dir, not repeated
by the test itself since it's a one-time design check, not a per-run
invariant):

    $ python3 -c "... extract /CreationDate ..."
    D:20260720191510Z                                  # -> epoch 1784574910
    $ SOURCE_DATE_EPOCH=1784574910 bash skills/resume-builder/scripts/render.sh \\
        evals/fixtures/resume-sample/resume.yaml -t compact -o /scratch/candidate.pdf
    $ sha256sum /scratch/candidate.pdf examples/ai-ml-intern/resume.pdf
    2460f0a4e92d...  /scratch/candidate.pdf
    2460f0a4e92d...  examples/ai-ml-intern/resume.pdf   # identical

No changes to render.sh were needed: it already treats a caller-supplied
SOURCE_DATE_EPOCH as authoritative and only falls back to the data
file's mtime when the variable is unset (see render.sh's "Reproducible
output" block) — this test simply exercises that existing passthrough.
The fixture yaml is read directly (never copied/mutated): render.sh only
ever reads the data file and copies it into its own mktemp build dir, so
pointing it straight at the tracked fixture leaves the fixture's content
and mtime untouched. Output always lands in pytest's tmp_path, never
over the tracked PDF.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from calendar import timegm
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RENDER_SH = REPO / "skills/resume-builder/scripts/render.sh"
DATA = REPO / "evals/fixtures/resume-sample/resume.yaml"
TRACKED_PDF = REPO / "examples/ai-ml-intern/resume.pdf"
TEMPLATE = "compact"
CI_YML = REPO / ".github/workflows/ci.yml"
CHECK = REPO / "skills/resume-builder/scripts/check_projection.py"
VAULT = REPO / "examples/ai-ml-intern/career-vault.md"
PROJECTION_REPORT = REPO / "examples/ai-ml-intern/projection-report.md"
EXAMPLE_README = REPO / "examples/ai-ml-intern/README.md"

CREATION_DATE_RE = re.compile(rb"/CreationDate\s*\(D:(\d{14})(Z)?\)")


def _expected_typst_version() -> str | None:
    """CI's pinned typst version, read straight from ci.yml so this test's
    notion of "expected" tracks CI instead of drifting into its own
    hardcoded copy. Returns None if it can't be found (message just
    omits the comparison rather than failing on it)."""
    if not CI_YML.is_file():
        return None
    m = re.search(r'TYPST_VERSION:\s*"([\d.]+)"', CI_YML.read_text())
    return m.group(1) if m else None


def _local_typst_version() -> str | None:
    proc = subprocess.run(["typst", "--version"], capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    # "typst 0.15.1 (unknown commit)" -> "0.15.1"
    m = re.search(r"(\d+\.\d+\.\d+)", proc.stdout)
    return m.group(1) if m else proc.stdout.strip()


def _creation_epoch(pdf_bytes: bytes) -> int:
    """Extract the epoch Typst stamped into /CreationDate. Typst's
    reproducible-build path (SOURCE_DATE_EPOCH set) always emits a UTC
    `D:YYYYMMDDHHMMSSZ` string, never an offset form — so a match
    lacking the trailing Z means either the tracked PDF wasn't produced
    reproducibly or the docinfo is otherwise unexpected, which is a real
    failure, not something to paper over."""
    m = CREATION_DATE_RE.search(pdf_bytes)
    assert m is not None, (
        f"could not find a /CreationDate(D:...) entry in {TRACKED_PDF} — "
        "the tracked PDF's docinfo is not in the reproducible-build shape "
        "this test relies on to recover the epoch it was rendered at."
    )
    digits, z = m.group(1).decode(), m.group(2)
    assert z, (
        f"{TRACKED_PDF}'s /CreationDate ({digits!r}) has no trailing 'Z' — "
        "expected a UTC reproducible-build timestamp; cannot safely derive "
        "the epoch it was rendered at."
    )
    year, month, day = int(digits[0:4]), int(digits[4:6]), int(digits[6:8])
    hour, minute, sec = int(digits[8:10]), int(digits[10:12]), int(digits[12:14])
    return timegm((year, month, day, hour, minute, sec, 0, 0, 0))


def _sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_example_resume_pdf_matches_current_templates_and_yaml(tmp_path):
    # Same skip pattern as test_validate_yaml.py's render.sh tests: skip
    # only when typst is genuinely absent. Anything else (version
    # mismatch, a render error) is a real failure below, not a skip.
    if shutil.which("typst") is None:
        pytest.skip("typst not installed — cannot verify example freshness "
                    "(this is a skip, not a pass: install typst to run this "
                    "check for real)")

    assert TRACKED_PDF.is_file(), f"tracked example missing: {TRACKED_PDF}"
    assert DATA.is_file(), f"fixture missing: {DATA}"

    epoch = _creation_epoch(TRACKED_PDF.read_bytes())

    out = tmp_path / "resume.pdf"
    proc = subprocess.run(
        [str(RENDER_SH), str(DATA), "-t", TEMPLATE, "-o", str(out)],
        capture_output=True, text=True,
        env={**__import__("os").environ, "SOURCE_DATE_EPOCH": str(epoch)},
    )
    assert proc.returncode == 0, (
        f"render.sh failed re-rendering the example fixture (exit "
        f"{proc.returncode}) — this is a render error, not drift:\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    assert out.is_file(), f"render.sh exited 0 but produced no output at {out}"

    got = _sha256(out)
    want = _sha256(TRACKED_PDF)
    if got == want:
        return

    local_v = _local_typst_version()
    expected_v = _expected_typst_version()
    version_note = (
        f"Local typst is {local_v!r}; CI pins {expected_v!r} "
        f"(.github/workflows/ci.yml TYPST_VERSION)."
        if local_v and expected_v and local_v != expected_v else
        f"Local typst {local_v!r} matches CI's pinned {expected_v!r} — "
        "version is NOT the explanation, look at template/yaml drift."
        if local_v and expected_v else
        "Could not compare local vs CI typst versions."
    )
    pytest.fail(
        "examples/ai-ml-intern/resume.pdf no longer matches a fresh render "
        f"of {DATA.relative_to(REPO)} with -t {TEMPLATE} at the pinned "
        f"epoch {epoch} (from the tracked PDF's own /CreationDate).\n"
        f"  tracked sha256:  {want}\n"
        f"  rendered sha256: {got}\n"
        f"{version_note}\n"
        "This means either:\n"
        "  1. A template under skills/resume-builder/assets/templates/ "
        "(or evals/fixtures/resume-sample/resume.yaml) changed since the "
        "committed PDF was rendered, and the example is now stale — "
        "re-render it:\n"
        "       skills/resume-builder/scripts/render.sh "
        "evals/fixtures/resume-sample/resume.yaml -t compact "
        "-o examples/ai-ml-intern/resume.pdf\n"
        "     then rerun the full eval battery (uv run pytest evals -q) "
        "and regenerate examples/ai-ml-intern/eval-report.md and "
        "projection-report.md so they describe the new PDF, not the old "
        "one.\n"
        "  2. The local typst binary differs from CI's pinned version "
        "(see the version line above) and produces different bytes for "
        "the same input — install the version CI uses and re-run this "
        "test before concluding the example is actually stale."
    )


# ── round-3 review finding 8: the reports are artifacts too ────────────
# The PDF-only freshness check let the prose reports drift — the README
# said "22 numbers" while projection-report.md's own checker output said
# 18. These tie the committed reports to a fresh checker run so a stale
# report (or a stale hand-written count) fails CI, not a later review.

def _fresh_projection_output() -> str:
    proc = subprocess.run(
        [sys.executable, str(CHECK), str(DATA), str(VAULT)],
        capture_output=True, text=True)
    assert proc.returncode in (0, 1), (
        f"check_projection crashed re-running the example pair:\n{proc.stderr}")
    return proc.stdout.rstrip("\n")


def _fenced_projection_block(md: str) -> str:
    m = re.search(r"```\n(\[projection\].*?)\n```", md, re.DOTALL)
    assert m is not None, "no [projection] fenced block in projection-report.md"
    return m.group(1).rstrip("\n")


def test_projection_report_block_matches_current_checker_output():
    tracked = _fenced_projection_block(PROJECTION_REPORT.read_text())
    fresh = _fresh_projection_output()
    assert tracked == fresh, (
        "examples/ai-ml-intern/projection-report.md's fenced [projection] "
        "block is stale — it no longer matches a fresh run of "
        "check_projection.py against the example vault. Regenerate it "
        "(the block is the verbatim stdout of\n"
        "  skills/resume-builder/scripts/check_projection.py "
        "evals/fixtures/resume-sample/resume.yaml "
        "examples/ai-ml-intern/career-vault.md )."
    )


def test_example_readme_fact_counts_match_checker():
    # The README's "(N numbers, N dates, N urls, N identity fields, N
    # contact/personal fields, N skill tokens, ...)" tallies must match
    # the checker's own reported counts, so the two artifacts can't
    # disagree (round-3 review finding 8: they did — 22 vs 18).
    out = _fresh_projection_output()

    def n(label: str) -> int:
        m = re.search(rf"\b(\d+)\s+{label}", out)
        assert m is not None, f"checker output has no '{label}' count:\n{out}"
        return int(m.group(1))

    counts = {
        "numbers": n("numeric token"),
        "dates": n("date\\(s\\) verified"),
        "urls": n("url\\(s\\) verified"),
        "identity fields": n("name/org/title field"),
        "contact/personal fields": n("contact/personal field"),
        "skill tokens": n("skill token"),
    }
    readme = EXAMPLE_README.read_text()
    for label, want in counts.items():
        m = re.search(rf"(\d+)\s+{re.escape(label)}", readme)
        assert m is not None, (
            f"examples/ai-ml-intern/README.md names no '{label}' count — "
            "keep its fact tally in sync with the checker")
        got = int(m.group(1))
        assert got == want, (
            f"README says {got} {label}, checker verifies {want} — the "
            "README's fact tally is stale (round-3 review finding 8)")


# ── round-4 review finding 8: bind eval-report's cited L0/L2 metrics ────
# The report-freshness tests above cover projection-report + README. The
# eval-report cites deterministic L0/L2 numbers too (char count,
# words_checked, decorative_tokens) — those are script output, so they
# can be pinned the same way. (jd-analysis.md stays unbound: it is a
# judgment artifact, not script output, with nothing deterministic to
# diff against — noted here so the omission is explicit, not forgotten.)

EVAL_REPORT = REPO / "examples/ai-ml-intern/eval-report.md"
EXTRACT = REPO / "skills/resume-evaluator/scripts/extract_text.py"
HIDDEN = REPO / "skills/resume-evaluator/scripts/hidden_text_check.py"


def _script_metrics(script: Path, pdf: Path) -> dict:
    import json
    proc = subprocess.run(
        [sys.executable, str(script), str(pdf), "--json"],
        capture_output=True, text=True)
    assert proc.returncode in (0, 1), (
        f"{script.name} crashed on the example PDF:\n{proc.stderr}")
    return json.loads(proc.stdout).get("metrics", {})


def test_eval_report_l0_l2_metrics_match_scripts():
    if shutil.which("pdftoppm") is None and shutil.which("pdftocairo") is None:
        # hidden_text_check needs poppler to raster; L0 doesn't. Only skip
        # the L2 half if poppler is truly absent.
        pytest.skip("poppler absent — cannot verify L2 metrics")
    report = EVAL_REPORT.read_text()
    l0 = _script_metrics(EXTRACT, TRACKED_PDF)
    l2 = _script_metrics(HIDDEN, TRACKED_PDF)

    cited = {
        "L0 non-space chars": (
            int(re.search(r"([\d,]+) non-space chars", report).group(1).replace(",", "")),
            l0.get("chars")),
        "L2 words_checked": (
            int(re.search(r"(\d+) content words checked", report).group(1)),
            l2.get("words_checked")),
        "L2 decorative_tokens": (
            int(re.search(r"(\d+) decorative leader tokens", report).group(1)),
            l2.get("decorative_tokens")),
    }
    stale = {k: v for k, v in cited.items() if v[0] != v[1]}
    assert not stale, (
        "examples/ai-ml-intern/eval-report.md cites L0/L2 numbers that no "
        "longer match a fresh script run (report value, script value): "
        f"{stale} — regenerate the report's metrics from the current PDF")
