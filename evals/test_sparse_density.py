"""Regression test for external review finding 3 (round-5): a sparse but
perfectly normal CV — Education, one ordinary job, Projects, Skills, no
summary/publications/awards — used to render a visibly correct PDF whose
text layer nonetheless mis-ordered under poppler's default (non -layout)
extraction: Experience/Education date ranges landed AFTER the Skills
heading, purely because there wasn't enough other content on the page to
keep the right-aligned date column from reading as an independent column.
The same structure with more content (the resume-sample fixture) always
passed — density alone flipped the verdict, which meant sparse
candidates were penalized for having concise resumes.

Root cause was the templates (onecol/compact/classic), not parse_sim:
`pdftotext -raw` and `-layout` both showed the underlying content-stream
order was correct; only poppler's column-clustering heuristic split it,
and only when nothing else on the page crossed the horizontal gap
between the body text and the flush-right meta column. The fix ties the
meta (dates/location) text's position to the body text with a small
fixed gap instead of flush-aligning it to the page margin, so it can
never form a page-wide, density-dependent column.

Fixtures are generated fresh via fixtures/generate.py, same pattern as
test_evaluator.py.

Round-6 (external review finding 7) extends this file: the round-5 fix
above is extraction-correct but was visually inconsistent — dates start
at a different x on every entry (unavoidable once the rail can't be a
real right-aligned column), and templates whose meta row can have an
empty left-side (compact's tag row when an entry carries no `tags`)
used to leave the date as a bare, contextless value sitting at the true
left margin. Two real right-aligned rail constructs were tried and
empirically confirmed (see scratch evidence in the round-6 changeset
notes) to reproduce the exact sparse-density misordering above on every
template — `h(1fr)` fill inside one line, and a grid cell with an
inline `align(right)` sub-box — because poppler's column heuristic
keys on final glyph geometry, not the Typst construct that produced it.
Extraction order is non-negotiable, so the round-6 templates instead
emitted a uniform "·" separator immediately before the meta text on
every row() call, in every template, whether or not left-side is
present — so meta was never bare, even though its x position still
varied.

Round-8 (finding 9 + direct user feedback: dates "aesthetically bad")
revisits this: round-6's uniform "·" marker fixed the bare-value
problem but created a new one — whenever nothing preceded the marker
on its own visual line (compact's tagless experience/project entries,
or any template's atomic date box wrapping alone under a long
institution/organization name in the long-meta fixture), the line
rendered as a lone "· date", a punctuation mark with nothing attached
to it, at the left margin. That is the "detached marker" finding 9
names. A third right-aligned rail construct was tried and measured
this round — a same-baseline title+fill+date line boxed unbreakable,
and place(right + horizon) anchored per entry — and both still
reproduce the exact sparse-density misordering above in a minimal
repro, independent of density: true right-alignment remains
impossible under this repo's extraction-correctness invariant. The
fix instead drops the marker character entirely, keeping only the
small fixed gap (extraction order was always carried by the gap, not
the dot — confirmed in the round-8 scratch repro). A bare date with a
small, formula-derivable lead-in gap (page margin + a fixed relative
h()) lands at the same x on every entry that has nothing preceding it
on its line, in a given template — a stable, predictable position —
and is never a detached, contextless marker. The tests below check
that invariant (no marker, ever) and the positional-stability
replacement for finding 9, alongside the round-7 atomic-range and
round-5/6 extraction-order checks, which this round leaves intact.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills/resume-evaluator/scripts"
GENERATE = REPO / "evals/fixtures/generate.py"
TEMPLATES = ("onecol", "compact", "classic")

MONTH = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
# Deliberately excludes a bare 4-digit year: every date in these fixtures
# has a month component ("Jun 2025"), and a bare \d{4} would also match
# the last four digits of a phone number in the header's contact line.
DATE_TOKEN = rf"(?:{MONTH} \d{{4}}|Present)"


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("sparse-fixtures")
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


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("script", ALL_SCRIPTS)
def test_sparse_fixture_passes_every_layer(fixtures, template, script):
    code, report = run_script(script, fixtures / f"sparse_{template}.pdf")
    assert code == 0, f"{template}/{script} failed on the sparse fixture: {report}"
    assert report["verdict"] == "pass"
    assert not failed_ids(report)


@pytest.mark.parametrize("template", TEMPLATES)
def test_sparse_fixture_dates_attribute_to_their_section(fixtures, template):
    # The exact regression: date ranges must be counted under experience
    # and education, not silently dropped/misrouted after Skills.
    _, report = run_script("parse_sim", fixtures / f"sparse_{template}.pdf")
    assert {"education", "experience", "projects", "skills"} <= set(report["sections"])
    ranges = report["metrics"]["date_ranges"]
    assert ranges.get("experience", 0) >= 1, \
        f"{template}: sparse Experience section lost its date range " \
        f"(reading-order regression): {ranges}"
    assert ranges.get("education", 0) >= 1, \
        f"{template}: sparse Education section lost its date range: {ranges}"


@pytest.mark.parametrize("template", TEMPLATES)
def test_dense_fixture_still_passes_parse_sim(fixtures, template):
    # The density-dependence is the heart of the finding: a fix that only
    # helped the sparse case (or accidentally broke the dense one) would
    # not actually resolve it.
    pdf = fixtures.parent / "dense-density-check" / f"{template}.pdf"
    pdf.parent.mkdir(exist_ok=True)
    subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(REPO / "evals/fixtures/resume-sample/resume.yaml"),
         "-t", template, "-o", str(pdf)],
        check=True, capture_output=True, text=True)
    code, report = run_script("parse_sim", pdf)
    assert code == 0, f"{template}: dense fixture regressed: {report}"
    ranges = report["metrics"]["date_ranges"]
    assert ranges.get("experience", 0) >= 1
    assert ranges.get("education", 0) >= 1


@pytest.mark.parametrize("template", TEMPLATES)
def test_sparse_reading_order_matches_visible_order_in_raw_text(fixtures, template):
    # Belt-and-suspenders on the actual mechanism: in the sparse fixture's
    # extracted text (default pdftotext, no -layout), the Experience
    # entry's date range must appear before the SKILLS heading — not
    # flushed to the end of the document behind it.
    pdf = fixtures / f"sparse_{template}.pdf"
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                          capture_output=True, text=True).stdout
    skills_idx = text.upper().find("SKILLS")
    dates_idx = text.find("Jun 2025")
    assert skills_idx != -1, f"{template}: SKILLS heading not found in extracted text"
    assert dates_idx != -1, f"{template}: experience date range not found in extracted text"
    assert dates_idx < skills_idx, \
        f"{template}: experience dates ({dates_idx}) still land after " \
        f"SKILLS ({skills_idx}) in the default-mode text layer"


# ── round-8 (finding 9): never a detached separator marker ─────────────
#
# Round-6's uniform "·" marker fixed the round-5 bare-value regression
# but created the defect finding 9 names and the user called out
# directly: whenever nothing preceded the marker on its own visual line
# (a tagless experience/project entry, or an atomic date box wrapping
# alone under a long institution/organization name), the line rendered
# as a lone "· date" — a punctuation mark with nothing attached to it,
# at the left margin. The fix drops the marker character entirely,
# keeping only the small fixed gap that was always what kept this
# construct out of poppler's column-clustering heuristic (not the dot
# — see the round-8 scratch repro under dates8/repro/cand_c_sparse).
# The tests below (a) assert the marker never appears again, on any
# template/density/fixture, and (b) assert the resulting bare date
# still lands at a stable, predictable x per template — the positive
# half of finding 9's requirement once true right-alignment was
# confirmed impossible (see the templates' row() comments for the
# measured failure mechanism of the two rail constructs re-tried this
# round).

def extract_lines(pdf: Path) -> list[str]:
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                          capture_output=True, text=True).stdout
    return text.splitlines()


def _dense_pdf(fixtures: Path, template: str) -> Path:
    pdf = fixtures.parent / "dense-density-check" / f"{template}.pdf"
    pdf.parent.mkdir(exist_ok=True)
    subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(REPO / "evals/fixtures/resume-sample/resume.yaml"),
         "-t", template, "-o", str(pdf)],
        check=True, capture_output=True, text=True)
    return pdf


MARKED_DATE_RE = re.compile(rf"·\s*{DATE_TOKEN}")


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("kind", ["sparse", "long_meta", "dense"])
def test_no_date_is_ever_led_by_a_detached_separator_marker(fixtures, template, kind):
    pdf = _dense_pdf(fixtures, template) if kind == "dense" \
        else fixtures / f"{kind}_{template}.pdf"
    lines = extract_lines(pdf)
    marked = [l for l in lines if MARKED_DATE_RE.search(l)]
    assert not marked, \
        f"{template}/{kind}: found a date still led by the detached '·' " \
        f"marker (finding 9 regression): {marked!r}"


def test_sparse_compact_experience_date_has_no_detached_marker(fixtures):
    # The exact case finding 7 named and finding 9 flagged as still
    # ugly: compact's experience entry in the sparse fixture carries no
    # `tags`, so its meta row's left-side is `none` and the date range
    # is the only content on that line. It must render as a bare date
    # — not a marker-only line — while still actually appearing (the
    # regression this whole file guards is dates disappearing/misrouted,
    # not just the marker's presence).
    lines = extract_lines(fixtures / "sparse_compact.pdf")
    marked = [l for l in lines if re.match(rf"^\s*·\s*{DATE_TOKEN}", l)]
    assert not marked, \
        f"compact: found a marker-led date line (finding 9 regression): {marked!r}"
    bare = [l for l in lines if re.match(rf"^\s*{DATE_TOKEN}", l)]
    assert bare, \
        "compact: expected the tag-less experience entry's date range to " \
        "still render on its own line (without the detached marker) in " \
        "the sparse fixture"


def _cluster_by_line(words: list, tolerance: float = 2.0) -> list[list]:
    # Group words into visual lines by top-coordinate proximity rather
    # than exact/rounded equality: mixing a bold/regular or
    # differently-sized run on the *same* baseline (e.g. a bold
    # institution name next to an italic meta date) can put their word
    # bounding boxes a fraction of a point apart in "top", which
    # round(top, 1) treats as two different lines. That false split
    # would misclassify a normal trailing-inline date as "bare".
    groups: list[dict] = []
    for w in sorted(words, key=lambda w: w["top"]):
        for g in groups:
            if abs(g["top"] - w["top"]) <= tolerance:
                g["words"].append(w)
                break
        else:
            groups.append({"top": w["top"], "words": [w]})
    return [g["words"] for g in groups]


def _bare_date_line_x0s(pdf: Path) -> list[float]:
    # x0 (left edge, in PDF points) of every visual line whose full text
    # is *only* a date/date-range token — the "nothing else preceded it
    # on this line" case that used to carry the detached marker.
    import pdfplumber

    bare_re = re.compile(rf"^{DATE_TOKEN}(?:\s*[–-]\s*{DATE_TOKEN})?$")
    xs = []
    with pdfplumber.open(str(pdf)) as doc:
        for page in doc.pages:
            words = page.extract_words()
            for line_words in _cluster_by_line(words):
                line_words.sort(key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in line_words)
                if bare_re.match(text):
                    xs.append(line_words[0]["x0"])
    return xs


@pytest.mark.parametrize("template", TEMPLATES)
def test_bare_date_lines_land_at_a_stable_x_per_template(fixtures, template):
    # Finding 9's positive requirement: once a date renders with
    # nothing else on its line (confirmed marker-free above), it must
    # still land at a predictable x on every entry that has one — not
    # an arbitrary spot that drifts with unrelated content. The
    # construct that produces a bare date line resolves, for a given
    # template, to the same x every time: the enclosing block's own
    # left edge plus one fixed relative h() gap — independent of
    # whether that block started empty (compact's tagless tags/stack
    # row) or the atomic date box wrapped alone under a long
    # institution/organization name (long-meta fixture). Gather every
    # bare date line across the two fixtures that produce this case and
    # require them within a tight tolerance of each other.
    sparse_pdf = fixtures / f"sparse_{template}.pdf"
    long_meta_pdf = fixtures / f"long_meta_{template}.pdf"
    xs = _bare_date_line_x0s(sparse_pdf) + _bare_date_line_x0s(long_meta_pdf)
    assert xs, f"{template}: expected at least one bare date line across " \
        f"the sparse/long-meta fixtures to check position stability"
    assert max(xs) - min(xs) <= 2.5, \
        f"{template}: bare date lines land at inconsistent x positions " \
        f"{xs} (points) — not a stable, predictable spot (finding 9)"


@pytest.mark.parametrize("template", TEMPLATES)
def test_long_left_content_meta_wraps_without_overlap_or_clipping(fixtures, template):
    # Graceful degradation: pairing very long institution/organization/
    # title/location strings with the inline meta rail must never
    # overlap glyphs or clip text off the page, on any template.
    import pdfplumber

    pdf = fixtures / f"long_meta_{template}.pdf"
    with pdfplumber.open(str(pdf)) as doc:
        for page in doc.pages:
            words = page.extract_words()
            by_line: dict[float, list] = {}
            for w in words:
                by_line.setdefault(round(w["top"], 1), []).append(w)
            for top, line_words in by_line.items():
                line_words.sort(key=lambda w: w["x0"])
                for a, b in zip(line_words, line_words[1:]):
                    assert a["x1"] <= b["x0"] + 0.5, \
                        f"{template}: overlapping words on page {page.page_number} " \
                        f"at top={top}: {a['text']!r} (x1={a['x1']:.1f}) vs " \
                        f"{b['text']!r} (x0={b['x0']:.1f})"
                for w in line_words:
                    assert w["x1"] <= page.width - 2, \
                        f"{template}: word {w['text']!r} clipped past the page " \
                        f"edge on page {page.page_number} (x1={w['x1']:.1f}, " \
                        f"page width {page.width:.1f})"


# ── round-7 (finding 7): date ranges are atomic, never split mid-range ──
#
# Every row() call site above puts dates/location behind the same
# "\u{00b7}" separator so meta is never bare (round-6). What round-6
# didn't guard against: on a crowded line (long institution/organization
# names, as in the long-meta fixture), the *range itself* could wrap
# internally — its own tokens landing on two different lines, e.g.
# onecol's "Sep" orphaned from "2022 - Jun 2026", or classic breaking
# before "- Sep 2025". Both read as a parsing/date error, not a line
# wrap, to anything downstream (evaluator, ATS, a human skimming). The
# fix wraps the separator + date-range meta text in a `box()` (the same
# unbreakable-unit pattern compact's header already used for contact
# items) so the whole range moves to the next line as one atomic piece
# instead of splitting — but only for dates: an unbounded string (e.g.
# a long location) boxed the same way would run off the page instead of
# wrapping, so location rows are deliberately left non-atomic.

RANGE_RE = re.compile(rf"{DATE_TOKEN}\s*–\s*{DATE_TOKEN}")

# Expected number of *date ranges* (a start AND an end, rendered as
# "<date> – <date>") each fixture's source YAML produces, per
# evals/fixtures/{sparse,resume,long-meta}-sample/resume.yaml —
# independent of template. A lone date with no counterpart (an award's
# bare date, or a project with no start/end) isn't a "range" and isn't
# counted here; this section is specifically about finding 7's failure
# mode — a range's own tokens landing on two different lines.
EXPECTED_RANGES = {
    "sparse": 2,      # education + experience
    "dense": 4,       # education + 2x experience + 1x project (whisperboard)
    "long_meta": 2,   # education + experience
}


def atomic_range_count(pdf: Path) -> int:
    # Count full "<date> – <date>" matches that land entirely on a
    # single pdfplumber word-line (shared baseline `top`, i.e. one visual
    # line). A date range split across two lines never produces this
    # match on either line, so a shortfall here is a direct,
    # unambiguous signal of the finding-7 regression: the range's
    # tokens split internally instead of wrapping as a unit.
    import pdfplumber

    found = 0
    with pdfplumber.open(str(pdf)) as doc:
        for page in doc.pages:
            words = page.extract_words()
            by_line: dict[float, list] = {}
            for w in words:
                by_line.setdefault(round(w["top"], 1), []).append(w)
            for line_words in by_line.values():
                line_words.sort(key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in line_words)
                found += len(RANGE_RE.findall(text))
    return found


@pytest.mark.parametrize("template", TEMPLATES)
def test_sparse_date_ranges_are_atomic(fixtures, template):
    pdf = fixtures / f"sparse_{template}.pdf"
    count = atomic_range_count(pdf)
    assert count == EXPECTED_RANGES["sparse"], \
        f"{template}: expected {EXPECTED_RANGES['sparse']} atomic date " \
        f"range(s) sharing one baseline in the sparse fixture, found " \
        f"{count} — a range's tokens split across lines (finding 7 " \
        f"regression)"


@pytest.mark.parametrize("template", TEMPLATES)
def test_dense_date_ranges_are_atomic(fixtures, template):
    # Same invariant, dense fixture: the fix isn't a sparse-only patch,
    # and boxing meta must not regress the fixture with the most content
    # (2 experience entries + a dated project alongside education).
    pdf = fixtures.parent / "dense-density-check" / f"{template}.pdf"
    pdf.parent.mkdir(exist_ok=True)
    subprocess.run(
        ["bash", str(REPO / "skills/resume-builder/scripts/render.sh"),
         str(REPO / "evals/fixtures/resume-sample/resume.yaml"),
         "-t", template, "-o", str(pdf)],
        check=True, capture_output=True, text=True)
    count = atomic_range_count(pdf)
    assert count == EXPECTED_RANGES["dense"], \
        f"{template}: expected {EXPECTED_RANGES['dense']} atomic date " \
        f"range(s) sharing one baseline in the dense fixture, found " \
        f"{count}"


@pytest.mark.parametrize("template", TEMPLATES)
def test_long_meta_date_ranges_are_atomic(fixtures, template):
    # The direct reproduction of finding 7: long institution/organization
    # names crowd the inline meta rail close to the line-wrap point, and
    # before the fix this split the range mid-token (onecol: "Sep"
    # orphaned from "2022 - Jun 2026"; classic: break before "- Sep
    # 2025"). The whole range must now wrap as a unit instead.
    pdf = fixtures / f"long_meta_{template}.pdf"
    count = atomic_range_count(pdf)
    assert count == EXPECTED_RANGES["long_meta"], \
        f"{template}: expected {EXPECTED_RANGES['long_meta']} atomic date " \
        f"range(s) sharing one baseline in the long-meta fixture, found " \
        f"{count} — a range's tokens split across two lines (finding 7 " \
        f"regression)"


@pytest.mark.parametrize("template", TEMPLATES)
def test_long_meta_reading_order_matches_visible_order(fixtures, template):
    # Belt-and-suspenders on the round-5/6 extraction-order invariant:
    # boxing the meta rail for atomicity must not reintroduce the
    # sparse-density misordering bug by accidentally forming a real
    # right-aligned column. Same check as
    # test_sparse_reading_order_matches_visible_order_in_raw_text, run
    # against the long-meta fixture instead.
    pdf = fixtures / f"long_meta_{template}.pdf"
    text = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), "-"],
                          capture_output=True, text=True).stdout
    skills_idx = text.upper().find("SKILLS")
    dates_idx = text.find("Sep 2022")
    assert skills_idx != -1, f"{template}: SKILLS heading not found in extracted text"
    assert dates_idx != -1, f"{template}: education date range not found in extracted text"
    assert dates_idx < skills_idx, \
        f"{template}: education dates ({dates_idx}) still land after " \
        f"SKILLS ({skills_idx}) in the default-mode text layer"


# ── round-9 (finding 9, reopened): dates actually on the right ─────────
#
# Round-8 closed only the "detached marker" half of finding 9. The
# user's own words — "the date somehow isn't properly placed on the
# right hand side ... aesthetically bad" — and the finding's own second
# clause ("other dates appear after varying metadata") stayed open:
# round-8's row() just concatenated left-side + a fixed small h() gap +
# date, so a date's x position was purely a function of how long the
# preceding text happened to be. Measuring every date's x0 across
# templates showed a 40-500pt scatter with nothing landing near the
# right margin, confirmed independently against the committed
# examples/ai-ml-intern/resume.pdf.
#
# Round-9 revisits the "untried construct" flagged in the review: an
# inline dot-leader (repeated literal "." glyphs filling a `box(width:
# 1fr)` between the left content and the date, all inside the same
# paragraph/line — not a separate grid column, not an `h(1fr)` blank
# gap) — a classic table-of-contents leader. Measured empirically this
# round (scratch: dates9/expt3, dates9/expt4):
#
#   - When the row has real left-side content before the leader
#     (institution/organization/title/tags text — the overwhelming
#     majority of date rows in practice), the leader+date now lands
#     exactly at the content box's right edge on every entry, in every
#     template, at every density (sparse/long-meta/dense) — true
#     right-alignment, and it does NOT reproduce the round-5/6/8
#     reading-order regression: SKILLS still follows the dates in the
#     default-mode (`pdftotext`, no `-layout`) text layer. The
#     difference from the three previously-tried-and-rejected rail
#     constructs (round-6's `h(1fr)`/`align(right)`, round-8's
#     box+h(1fr)/place(right+horizon)) is that the leader fills the gap
#     with actual glyphs (periods), so there is never an *uncrossed
#     whitespace* gap for poppler's column heuristic to key on — the
#     gap itself is text content, in the same run as the date.
#   - When the row has NO left-side content (compact's tagless
#     experience/project meta row) — i.e. the leader would span the
#     entire line width with nothing else on it — the exact same
#     construct DOES reproduce the reading-order regression: measured
#     fresh this round (scratch: dates9/expt2), the tagless date got
#     flushed to the end of the document, after SKILLS, exactly like
#     the pre-round-5 bug. A lone full-width run of leader dots is
#     apparently still enough like an isolated column for poppler to
#     mis-order, even though it's non-whitespace. This row() branch
#     therefore deliberately keeps round-8's fixed-gap, left-flush
#     fallback (no leader) — traded for a real, tested reading-order
#     guarantee over cosmetic consistency in this one edge case.
#   - The same fallback also catches the rare case where the leader+
#     date, boxed atomically, doesn't fit the remainder of a line
#     crowded by an extremely long institution/organization name (see
#     long-meta's Education entry in onecol/classic) and wraps whole to
#     its own new line: Typst trims the leading h() gap at the start of
#     a wrapped line, so it lands at the same stable left position as
#     the no-left-content fallback above — still consistent, just not
#     right-aligned. This is the same known, tested tradeoff, not a new
#     one.
#
# Net effect: the vast majority of dates — every entry that has any
# left-side content at all, at every density — are now genuinely
# right-aligned to a shared x, on every template. The remaining
# no-left-content/extreme-wrap edge cases keep the round-8 stable-left
# fallback, verified unchanged by the existing
# test_bare_date_lines_land_at_a_stable_x_per_template above. The test
# below is the new, positive half of finding 9's requirement: it
# doesn't just check the bare-orphan subset, it checks every dated row
# that has real left-side content, across sparse/long-meta/dense, and
# requires them to land at one shared x per template, near the page's
# right margin.

def _rail_date_x1s(pdf: Path) -> list[float]:
    # x1 (right edge, PDF points) of every date-range whose visual line
    # actually used the dot-LEADER construct (real left-side content,
    # then a run of leader "." glyphs, then the date) — excludes both
    # the no-left-content fallback and the round-9-follow-up
    # measure-and-fallback case, where the plain fixed-gap construct
    # can legitimately land real text immediately before a date on the
    # same line (e.g. a long institution name's last wrapped word
    # butting up against the date with only a small h() gap, no
    # leader) when the leader was predicted not to fit. That fallback
    # line intentionally does NOT right-align (see the round-9
    # follow-up doctrine comment in the templates' row()) so it must
    # not be counted here — requiring an actual run of 2+ leader dots
    # between the content and the date is what tells the two apart.
    import pdfplumber

    xs = []
    with pdfplumber.open(str(pdf)) as doc:
        for page in doc.pages:
            words = page.extract_words()
            # tolerance widened from _cluster_by_line's 2.0pt default: the
            # leader itself is set at 0.7em (a noticeably smaller font
            # than the surrounding body/meta text), which shifts its word
            # bbox's "top" enough (~2.1pt, measured) to fall outside the
            # default tolerance and get silently sorted into its own
            # cluster — invisible to the "before" text below even though
            # it renders on the same visual line. Reproduced against the
            # sparse/long-meta fixtures while adding the round-9-followup
            # dot-run check.
            for line_words in _cluster_by_line(words, tolerance=3.0):
                line_words.sort(key=lambda w: w["x0"])
                text = " ".join(w["text"] for w in line_words)
                m = RANGE_RE.search(text)
                if not m:
                    continue
                before = text[:m.start()]
                # real left-side content precedes the range on this line...
                if not re.search(r"[A-Za-z0-9]", before.replace(".", "")):
                    continue
                # ...AND an actual leader-dot run separates them (this is
                # what distinguishes the dot-leader construct from the
                # plain fixed-gap fallback, which never emits a leader).
                # Round 9 (finding 7): the leader's dots are SPACED now
                # — 3pt on each side of every "." — to cut extraction
                # pollution, so they no longer form an unbroken `\.{2,}`
                # run in extracted text. Two or more dots separated only
                # by whitespace is the same construct and the same
                # signal; a fixed-gap fallback row still has none.
                if not re.search(r"\.(?:\s*\.){1,}", before):
                    continue
                xs.append(line_words[-1]["x1"])
    return xs


@pytest.mark.parametrize("template", TEMPLATES)
def test_dated_rows_with_left_content_land_at_a_consistent_right_x(fixtures, template):
    # The positive half of finding 9 the round-8 test didn't cover:
    # every date row that has real left-side content (the dot-leader
    # rows, not the rare bare/wrap-alone fallback) must land at the
    # SAME x, near the page's right margin, on every template — not an
    # x that drifts with how long the preceding text happens to be.
    sparse_pdf = fixtures / f"sparse_{template}.pdf"
    long_meta_pdf = fixtures / f"long_meta_{template}.pdf"
    dense_pdf = _dense_pdf(fixtures, template)
    xs = (_rail_date_x1s(sparse_pdf) + _rail_date_x1s(long_meta_pdf)
          + _rail_date_x1s(dense_pdf))
    assert xs, f"{template}: expected at least one dot-leader-aligned " \
        f"date row across the sparse/long-meta/dense fixtures"
    assert max(xs) - min(xs) <= 1.5, \
        f"{template}: dot-leader date rows land at inconsistent right " \
        f"edges {xs} (points) — not a shared right-aligned x (finding 9)"
    import pdfplumber
    with pdfplumber.open(str(sparse_pdf)) as doc:
        page_width = doc.pages[0].width
    assert min(xs) >= page_width * 0.85, \
        f"{template}: dot-leader date rows land at x1={xs}, not close " \
        f"to the page's right margin (page width {page_width:.1f}) — " \
        f"finding 9's 'dates on the right hand side' is still unmet"


# ── round-9 follow-up (finding 9, still-open half): no dangling leader ──
#
# The mirror image of test_no_date_is_ever_led_by_a_detached_separator_
# marker above. Round-9's doctrine comment claimed the extreme-length-
# name case's "leader+date, boxed atomically... wraps whole to its own
# new line", but no code ever enforced that: `box(width: 1fr, ...)` was
# not nested inside the atomic date box, so Typst could lay the
# leader's repeated "." glyphs out on the CURRENT line (reaching the
# right margin) while pushing only the date box down to a new line by
# itself — the exact "punctuation with nothing attached to it" defect
# finding 9 originally named, reproduced with a leader instead of a
# "·". Reproduced pre-fix against this exact fixture set: long-meta's
# onecol Education row ended a line "...Engineering ......................."
# (nothing after the dots) with "Sep 2022 – Jun 2026" stranded,
# left-flush, on the line below; classic's Experience row did the same.
#
# The fix: row() now predicts (via `layout()` + `measure()`) whether
# the leader construct will fit in the available width before ever
# emitting it, falling back to the plain fixed-gap construct (no
# leader at all) when it won't — see the templates' row() comments.
DANGLING_LEADER_RE = re.compile(r"\.{2,}\s*$")


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("kind", ["sparse", "long_meta", "dense"])
def test_no_dangling_leader_before_a_wrapped_date(fixtures, template, kind):
    pdf = _dense_pdf(fixtures, template) if kind == "dense" \
        else fixtures / f"{kind}_{template}.pdf"
    lines = extract_lines(pdf)
    dangling = [l for l in lines if DANGLING_LEADER_RE.search(l)]
    assert not dangling, \
        f"{template}/{kind}: found a line ending in a bare leader-dot run " \
        f"with nothing following it — the leader was emitted but the " \
        f"date it belongs to wrapped away to the next line alone " \
        f"(dangling-leader regression): {dangling!r}"


@pytest.mark.parametrize("template", TEMPLATES)
@pytest.mark.parametrize("kind", ["sparse", "long_meta", "dense"])
def test_dot_leader_rows_still_pass_hidden_text_check(fixtures, template, kind):
    # The dot leader is real, visible ink (fill: muted, same gray as the
    # existing meta text) — not a decorative near-background color. A
    # too-faint leader (e.g. the "hair" divider gray used elsewhere in
    # these templates) reads as background-matched/invisible text to
    # hidden_text_check's luminance-contrast heuristic, which is a
    # correctness requirement (ATS hidden-text-stuffing detection), not
    # a cosmetic one — reproduced and fixed this round when the leader
    # was first drafted with `fill: hair`.
    pdf = _dense_pdf(fixtures, template) if kind == "dense" \
        else fixtures / f"{kind}_{template}.pdf"
    _, report = run_script("hidden_text_check", pdf)
    assert report["verdict"] == "pass", \
        f"{template}/{kind}: hidden_text_check failed on the dot-leader " \
        f"render: {report}"
