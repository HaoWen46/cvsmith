"""M2 exit criterion, executable: the evaluator catches every planted
failure in the fixtures and raises zero false positives on the good one.

Fixtures are generated fresh (see fixtures/generate.py) so these tests
exercise the real render path too.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills/resume-evaluator/scripts"
GENERATE = REPO / "evals/fixtures/generate.py"


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("fixtures")
    subprocess.run([sys.executable, str(GENERATE), "--out", str(out)],
                   check=True, capture_output=True, text=True)
    return out


def run_script(script: str, pdf: Path, *extra: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / f"{script}.py"), str(pdf), "--json", *extra],
        capture_output=True, text=True)
    assert proc.returncode in (0, 1), f"{script} crashed:\n{proc.stderr}"
    return proc.returncode, json.loads(proc.stdout)


def failed_ids(report: dict) -> set[str]:
    return {c["check_id"] for c in report["checks"] if c["level"] == "fail"}


ALL_SCRIPTS = ["extract_text", "parse_sim", "hidden_text_check", "lint_structure"]


# ── zero false positives ─────────────────────────────────────────────

@pytest.mark.parametrize("script", ALL_SCRIPTS)
def test_good_resume_passes(fixtures, script):
    code, report = run_script(script, fixtures / "good.pdf")
    assert code == 0, f"{script} false-positived on the good resume: {report}"
    assert report["verdict"] == "pass"
    assert not failed_ids(report)


def test_good_resume_parses_fully(fixtures):
    _, report = run_script("parse_sim", fixtures / "good.pdf")
    assert {"education", "experience", "projects", "skills"} <= set(report["sections"])
    assert report["contact"]["emails"] == ["sam.casey@example.com"]
    assert report["contact"]["name_guess"] == "Sam Casey"


def test_good_resume_within_page_budget(fixtures):
    code, report = run_script("lint_structure", fixtures / "good.pdf",
                              "--page-budget", "1")
    assert code == 0
    assert report["metrics"]["pages"] == 1


# ── every planted failure is caught ──────────────────────────────────

def test_image_only_fails_extraction(fixtures):
    code, report = run_script("extract_text", fixtures / "image_only.pdf")
    assert code == 1
    assert "text_layer" in failed_ids(report)


def test_image_only_fails_structure(fixtures):
    code, report = run_script("lint_structure", fixtures / "image_only.pdf")
    assert code == 1
    assert "image_pages" in failed_ids(report)


def test_white_text_is_exposed(fixtures):
    code, report = run_script("hidden_text_check", fixtures / "white_text.pdf")
    assert code == 1
    assert "invisible_text" in failed_ids(report)
    hidden = " ".join(report["invisible_words"])
    assert "INVISIBLE_STUFFING_MARKER" in hidden, \
        "the report must surface the hidden content itself"


def test_tiny_text_is_exposed(fixtures):
    code, report = run_script("hidden_text_check", fixtures / "tiny_text.pdf")
    assert code == 1
    assert "microscopic_text" in failed_ids(report)
    assert any("MICRO_STUFFING_MARKER" in w for w in report["tiny_words"])


def test_transparent_text_over_dark_is_exposed(fixtures):
    # Hidden text whose bbox sits on a dark rectangle: the background
    # supplies ink, the glyphs never do. The naive min-luminance check
    # passes it; the glyph-contrast check must not.
    code, report = run_script("hidden_text_check", fixtures / "transparent_text.pdf")
    assert code == 1
    assert "invisible_text" in failed_ids(report)
    hidden = " ".join(report["invisible_words"])
    assert "TRANSPARENT_MARKER" in hidden, \
        "fully transparent text over a dark banner must be surfaced"
    assert "SAMECOLOR_MARKER" in hidden, \
        "same-color-as-background text must be surfaced"


def test_partial_edge_text_is_exposed(fixtures):
    # External review finding 4: hidden_text_check.py's offpage_text check
    # only caught words wholly beyond a page edge, not words CROSSING one
    # (half visible, half clipped by any viewer/printer that honors the
    # page box). One straddling word per edge, plus the wholly-off-page
    # case the check already caught, all in fixtures/broken-src/
    # partial_edge_text.typ.
    code, report = run_script("hidden_text_check", fixtures / "partial_edge_text.pdf")
    assert code == 1
    assert "offpage_text" in failed_ids(report)

    by_word = {w["text"]: w for w in report["offpage_words"]}
    assert by_word["RIGHTCROSSWORD"]["edges"] == ["right"], \
        "a word straddling the right edge must be caught, not just words " \
        "wholly beyond it"
    assert by_word["LEFTCROSSWORD"]["edges"] == ["left"]
    assert by_word["TOPCROSSWORD"]["edges"] == ["top"]
    assert by_word["BOTTOMCROSSWORD"]["edges"] == ["bottom"]
    # the pre-existing wholly-off-page case must still be caught too
    assert by_word["WHOLLYOFFPAGECONTROL"]["edges"] == ["right"]

    detail = " ".join(c["detail"] for c in report["checks"]
                       if c["check_id"] == "offpage_text")
    assert "RIGHTCROSSWORD" in detail and "right" in detail, \
        "the report must name the word and the edge it crosses"


def test_no_false_positive_offpage_on_legit_fixtures(fixtures):
    # Calibration check for BBOX_EDGE_EPS: every other fixture generate.py
    # builds — every template x good/sparse/long-meta, the other planted-
    # failure fixtures, twocol, wonky_headings — must still pass
    # offpage_text. Real templates keep >=0.5in margins (see the measured-
    # margin comment on BBOX_EDGE_EPS in hidden_text_check.py), so none of
    # their word bboxes come anywhere near a page edge.
    checked = 0
    for pdf in sorted(fixtures.glob("*.pdf")):
        if pdf.name == "partial_edge_text.pdf":
            continue
        _, report = run_script("hidden_text_check", pdf)
        offpage = [c for c in report["checks"] if c["check_id"] == "offpage_text"]
        assert offpage and offpage[0]["level"] == "pass", \
            f"{pdf.name} false-positived offpage_text: {offpage}"
        checked += 1
    assert checked >= 10, \
        "sweep should cover every legit fixture generate.py builds"


# ── malformed PDFs keep the JSON contract ────────────────────────────

@pytest.mark.parametrize("script", ALL_SCRIPTS)
def test_malformed_pdf_reports_json_not_traceback(tmp_path, script):
    garbage = tmp_path / "garbage.pdf"
    garbage.write_bytes(b"%PDF-1.7\nthis is not a real pdf body\n" + b"\x00" * 64)
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / f"{script}.py"), str(garbage), "--json"],
        capture_output=True, text=True)
    assert proc.returncode == 1, \
        f"{script} must FAIL a malformed file, not crash: {proc.stderr}"
    report = json.loads(proc.stdout)  # the JSON contract holds even here
    assert report["verdict"] == "fail"
    assert "readable" in failed_ids(report)


def test_two_column_fails_structure(fixtures):
    code, report = run_script("lint_structure", fixtures / "twocol.pdf")
    assert code == 1
    assert "single_column" in failed_ids(report)


def test_wonky_headings_fail_routing(fixtures):
    code, report = run_script("parse_sim", fixtures / "wonky_headings.pdf")
    assert code == 1
    assert "core_sections" in failed_ids(report)
    assert report["unknown_headings"], "unrecognized headings must be surfaced"


def test_page_budget_enforced(fixtures):
    # the two-page-ish twocol fixture against a 1-page budget
    code, report = run_script("lint_structure", fixtures / "good.pdf",
                              "--page-budget", "0")
    assert code == 1
    assert "page_budget" in failed_ids(report)


# ── grouped experience (academic-track CVs) ──────────────────────────

def test_a4_paper_from_meta(tmp_path):
    src = (REPO / "evals/fixtures/resume-sample/resume.yaml").read_text()
    a4 = src.replace("page_budget: 1", "page_budget: 1\n  paper: a4\n  lang: en")
    yaml = tmp_path / "resume-a4.yaml"
    yaml.write_text(a4)
    pdf = tmp_path / "resume-a4.pdf"
    subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(yaml), "-o", str(pdf)],
        check=True, capture_output=True, text=True)
    code, report = run_script("lint_structure", pdf)
    assert code == 0
    size = next(c for c in report["checks"] if c["check_id"] == "page_size")
    assert size["level"] == "pass" and "a4" in size["detail"], size


def test_bullet_check_measures_and_enforces(tmp_path):
    check = REPO / "skills/resume-builder/scripts/check_bullets.py"
    pdf = tmp_path / "sample.pdf"
    subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(REPO / "evals/fixtures/resume-sample/resume.yaml"),
         "-t", "compact", "-o", str(pdf)],
        check=True, capture_output=True, text=True)

    proc = subprocess.run([sys.executable, str(check), str(pdf), "--json"],
                          capture_output=True, text=True)
    assert proc.returncode == 0
    report = json.loads(proc.stdout)
    assert len(report["bullets"]) >= 6, "should find every true bullet (7 in fixture; en-dash pseudo-markers excluded)"
    assert any(b["lines"] >= 2 for b in report["bullets"]), \
        "fixture is known to wrap some bullets in compact"
    assert report["measured_capacity_chars"] > 60, \
        "self-calibrated capacity must come from full first lines"
    assert all(b["over_by_chars"] > 0 for b in report["bullets"]
               if b["lines"] > 1), "wrapped bullets must carry cut guidance"

    proc = subprocess.run([sys.executable, str(check), str(pdf), "--max-lines", "1"],
                          capture_output=True, text=True)
    assert proc.returncode == 1, "one-line budget must fail on wrapped bullets"


def test_render_sh_reports_bullets_when_knob_unset(tmp_path):
    # Silent default is the failure mode: with no bullet_lines set, the
    # render must still SHOW the wrap state so two-line bullets are a
    # visible choice, not an invisible accident. Build stays green.
    proc = subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(REPO / "evals/fixtures/resume-sample/resume.yaml"),
         "-t", "compact", "-o", str(tmp_path / "report.pdf")],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    out = proc.stdout + proc.stderr
    assert "[bullets]" in out, "unset knob must still print the measurement"
    assert "2 lines" in out, "fixture is known to wrap bullets in compact"


def test_render_sh_enforces_bullet_lines(tmp_path):
    src = (REPO / "evals/fixtures/resume-sample/resume.yaml").read_text()
    strict = src.replace("page_budget: 1", "page_budget: 1\n  bullet_lines: 1")
    yaml = tmp_path / "strict.yaml"
    yaml.write_text(strict)
    proc = subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(yaml), "-t", "compact", "-o", str(tmp_path / "strict.pdf")],
        capture_output=True, text=True)
    assert proc.returncode != 0, \
        "render.sh must fail the build when bullet_lines is violated"
    assert "bullet" in (proc.stdout + proc.stderr).lower()


# ── failed gates must not clobber the last good pdf ──────────────────

def render_to(yaml: Path, pdf: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(yaml), "-o", str(pdf)],
        capture_output=True, text=True)


def test_failed_render_preserves_last_good_pdf(tmp_path):
    # A gate failure must leave the previous good PDF untouched at -o —
    # clobbering it turns "build failed" into "artifact destroyed".
    pdf = tmp_path / "resume.pdf"
    proc = render_to(REPO / "evals/fixtures/resume-sample/resume.yaml", pdf)
    assert proc.returncode == 0, proc.stderr
    good = pdf.read_bytes()

    src = (REPO / "evals/fixtures/resume-sample/resume.yaml").read_text()
    bad = src.replace("page_budget: 1", "page_budget: 1\n  bullet_lines: 1")
    bad = bad.replace(
        "    bullets:\n      - Built an offline evaluation harness",
        "    bullets:\n      - CLOBBERCANARY " + "overlong filler " * 20
        + "end.\n      - Built an offline evaluation harness")
    assert "CLOBBERCANARY" in bad
    yaml = tmp_path / "clobber.yaml"
    yaml.write_text(bad)

    proc = render_to(yaml, pdf)
    assert proc.returncode != 0, "bullet_lines: 1 must fail this render"
    assert pdf.read_bytes() == good, \
        "failed render replaced the previous good PDF"
    text = subprocess.run(["pdftotext", str(pdf), "-"],
                          capture_output=True, text=True).stdout
    assert "CLOBBERCANARY" not in text


def test_failed_smoke_gate_preserves_last_good_pdf(tmp_path):
    # Same guarantee for the extraction smoke gate: a header-only render
    # (<200 extracted chars) must not overwrite a seeded good PDF.
    pdf = tmp_path / "resume.pdf"
    proc = render_to(REPO / "evals/fixtures/resume-sample/resume.yaml", pdf)
    assert proc.returncode == 0, proc.stderr
    good = pdf.read_bytes()

    minimal = tmp_path / "minimal.yaml"
    minimal.write_text("basics:\n"
                       "  name: Sam Casey\n"
                       "  email: sam.casey@example.com\n")
    proc = render_to(minimal, pdf)
    assert proc.returncode != 0, "header-only render must fail the smoke gate"
    assert "suspiciously small" in proc.stderr
    assert pdf.read_bytes() == good, \
        "failed smoke gate replaced the previous good PDF"


def test_render_refuses_to_overwrite_the_data_file(tmp_path):
    # `render.sh resume.yaml -o resume.yaml` must refuse loudly — the old
    # behavior replaced the YAML source with a PDF and exited 0.
    yaml = tmp_path / "resume.yaml"
    yaml.write_text(
        (REPO / "evals/fixtures/resume-sample/resume.yaml").read_text())
    before = yaml.read_text()
    proc = render_to(yaml, yaml)
    assert proc.returncode != 0, \
        "rendering onto the data file must fail, not destroy the source"
    assert yaml.read_text() == before, "the data file must be untouched"


def test_render_refuses_non_pdf_output(tmp_path):
    # The whole class: -o pointing at any non-.pdf path (another yaml, a
    # vault, notes.md) silently replaces source material with a PDF.
    proc = render_to(REPO / "evals/fixtures/resume-sample/resume.yaml",
                     tmp_path / "notes.txt")
    assert proc.returncode != 0
    assert ".pdf" in (proc.stdout + proc.stderr)
    assert not (tmp_path / "notes.txt").exists()


def test_repeat_renders_are_byte_identical(tmp_path):
    # SOURCE_DATE_EPOCH is pinned to the data file's mtime, so re-rendering
    # unchanged data yields the same bytes — no drifting PDF timestamps.
    a, b = tmp_path / "a.pdf", tmp_path / "b.pdf"
    src = REPO / "evals/fixtures/resume-sample/resume.yaml"
    assert render_to(src, a).returncode == 0
    assert render_to(src, b).returncode == 0
    assert a.read_bytes() == b.read_bytes(), \
        "re-rendering unchanged data must be byte-stable"


def test_successful_render_leaves_no_temp_files(tmp_path):
    pdf = tmp_path / "resume.pdf"
    proc = render_to(REPO / "evals/fixtures/resume-sample/resume.yaml", pdf)
    assert proc.returncode == 0, proc.stderr
    assert "rendered:" in proc.stdout
    assert pdf.is_file()
    assert not list(tmp_path.glob(".render-*")), \
        "compile temp files must not survive a successful render"


def test_render_sh_prints_output_digest(tmp_path):
    # Attribution (application-tracker's ledger snapshot, in particular)
    # comes from a digest, not from write-protecting the derived output
    # path — render.sh must print one every successful render so a
    # second same-company/role render is distinguishable from the first
    # without diffing PDF bytes by hand.
    pdf = tmp_path / "resume.pdf"
    src = REPO / "evals/fixtures/resume-sample/resume.yaml"
    proc = render_to(src, pdf)
    assert proc.returncode == 0, proc.stderr
    m = re.search(r"^sha256: ([0-9a-f]{12})$", proc.stdout, re.MULTILINE)
    assert m, f"no sha256 digest line in stdout:\n{proc.stdout}"
    want = hashlib.sha256(pdf.read_bytes()).hexdigest()[:12]
    assert m.group(1) == want, "printed digest must match the actual output bytes"

    # The ledger's `sent:` line promises an exact yaml+PDF snapshot, so
    # render.sh must also hash the input yaml — a second, additive line,
    # never a replacement for the PDF digest above.
    ym = re.search(r"^yaml sha256: ([0-9a-f]{12})$", proc.stdout, re.MULTILINE)
    assert ym, f"no yaml sha256 digest line in stdout:\n{proc.stdout}"
    want_yaml = hashlib.sha256(src.read_bytes()).hexdigest()[:12]
    assert ym.group(1) == want_yaml, \
        "printed yaml digest must match the actual input yaml bytes"


def test_render_sh_digest_changes_on_content_change(tmp_path):
    # The overwrite itself is fine (iterating re-renders the same derived
    # path on purpose) — what must never happen silently is two different
    # sets of bytes reporting the same digest, since that digest is the
    # only signal a ledger row has that its snapshot is stale.
    pdf = tmp_path / "resume.pdf"
    src = (REPO / "evals/fixtures/resume-sample/resume.yaml").read_text()
    first = render_to(REPO / "evals/fixtures/resume-sample/resume.yaml", pdf)
    assert first.returncode == 0, first.stderr
    d1 = re.search(r"^sha256: ([0-9a-f]{12})$", first.stdout, re.MULTILINE).group(1)

    changed = tmp_path / "changed.yaml"
    changed.write_text(src.replace("Sam Casey", "Sam Casey Jr"))
    second = render_to(changed, pdf)
    assert second.returncode == 0, second.stderr
    d2 = re.search(r"^sha256: ([0-9a-f]{12})$", second.stdout, re.MULTILINE).group(1)

    assert d1 != d2, "changed content must produce a different digest"


def test_grouped_experience_renders_and_routes(tmp_path):
    pdf = tmp_path / "academic.pdf"
    subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(REPO / "evals/fixtures/academic-sample/resume.yaml"),
         "-o", str(pdf)],
        check=True, capture_output=True, text=True)

    text = subprocess.run(["pdftotext", str(pdf), "-"],
                          capture_output=True, text=True).stdout
    for heading in ("RESEARCH EXPERIENCE", "TEACHING EXPERIENCE",
                    "INDUSTRY EXPERIENCE"):
        assert heading in text, f"grouped section {heading!r} missing"

    code, report = run_script("parse_sim", pdf)
    assert code == 0, f"academic CV failed routing: {report}"
    assert "experience" in report["sections"]
    assert not report["unknown_headings"], \
        "grouped headings must be router-recognized, not creative"
