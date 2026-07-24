"""Round-7 finding 10 asked for cheap, deterministic checks on evals.json
itself, since nothing previously touched the scenario file at all.
Round-8 finding 5 sharpened what "checks" has to mean: the green suite
this file produced (219 passed) never validated that the *scenarios
were themselves correct* — it validated shape and arithmetic, and three
scenarios shipped self-contradictory anyway (a docstring overclaiming
what this file does; an evaluator eval whose expectations declared the
work-authorization gate resolved when the prompt never had the
candidate say anything about it; an evaluator eval whose expectations
named authorization as the sole TARGET FIT blocker while its own
attached fixture — Jun 2026 grad — silently failed the attached
posting's own stated Dec-2027-or-later requirement; two tracker evals
whose assertions required recomputing a live file's digest while
declaring no attached files at all). 219 green tests had validated
none of that.

What this file DOES do, still without spinning up an agent (that cost
is the caller's token-budget call, made via the behavioral run harness
— see below):

1. Validates evals.json's shape and that every fixture path it
   references actually resolves on disk (or is in the generate.py
   buildable set) — catches typos/rot in the scenario file itself.
2. Cross-checks the arithmetic asserted by the application-tracker
   funnel scenario (id 5) against application-ledger.md's own funnel
   formulas, on the exact row data quoted in that scenario's prompt.
3. Internal-consistency checks that catch a scenario contradicting its
   own inputs, specifically: (a) a gate a scenario's expectations claim
   is resolved/met must be grounded in something the scenario's own
   prompt or attached files actually state — not asserted on vibes;
   (b) a graduation-date claim is cross-checked against the *actual*
   dates in the fixture yaml and the attached JD text, not eyeballed;
   (c) a scenario whose assertions require live digest recomputation
   must have non-empty attached files; (d) every resume-evaluator
   scenario's expected verdict language matches the CURRENT three-line
   MECHANICAL/TARGET FIT/CRAFT format (SKILL.md "Report" section) —
   the stale two-line phrasing can't silently regress back in.

What this file does NOT do: it does not run resume-builder,
resume-evaluator, jd-analyzer, or application-tracker, and it does not
grade whether an agent following those skills would actually produce
the expected_output. That grading happens by executing each scenario
as a real agent invocation (with-skill vs. baseline, per this repo's
`_comment` field in evals.json) — a token-budget decision made by the
caller at run time, not by this file. A scenario passing every check
here means it is internally coherent and grounded in its own
fixtures — never that the skill it targets behaves as described.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
EVALS_JSON = REPO / "evals/evals.json"


# ── evals.json shape + fixture resolution ──────────────────────────────

@pytest.fixture(scope="module")
def evals_doc() -> dict:
    with open(EVALS_JSON, encoding="utf-8") as f:
        return json.load(f)


def test_evals_json_parses(evals_doc):
    assert "skills" in evals_doc
    assert isinstance(evals_doc["skills"], list) and evals_doc["skills"]


def test_every_skill_block_has_required_shape(evals_doc):
    for skill in evals_doc["skills"]:
        assert isinstance(skill.get("skill_name"), str) and skill["skill_name"], skill
        evals = skill.get("evals")
        assert isinstance(evals, list) and evals, skill["skill_name"]
        for ev in evals:
            missing = [k for k in ("id", "prompt", "files", "expected_output", "assertions")
                       if k not in ev]
            assert not missing, f"{skill['skill_name']} eval {ev.get('id')} missing {missing}"
            assert isinstance(ev["id"], int)
            assert isinstance(ev["prompt"], str) and ev["prompt"].strip()
            assert isinstance(ev["files"], list)
            assert all(isinstance(f, str) for f in ev["files"])
            assert isinstance(ev["expected_output"], str) and ev["expected_output"].strip()
            assert isinstance(ev["assertions"], list) and ev["assertions"], \
                f"{skill['skill_name']} eval {ev['id']} has no assertions"
            assert all(isinstance(a, str) and a.strip() for a in ev["assertions"])


def test_eval_ids_are_sequential_per_skill(evals_doc):
    for skill in evals_doc["skills"]:
        ids = [ev["id"] for ev in skill["evals"]]
        assert ids == list(range(1, len(ids) + 1)), \
            f"{skill['skill_name']} ids not sequential from 1: {ids}"


def _buildable_fixture_names() -> set[str]:
    # evals/fixtures/build/ is gitignored and generated on demand by
    # generate.py (see its own module docstring: "Fixtures are generated,
    # not committed"); CI's pytest run never populates that fixed path
    # (test_evaluator.py etc. generate their own copies under tmp_path
    # instead), so a bare os.path check would fail on a clean checkout
    # for scenarios that predate this file too. Instead, reproduce
    # generate.py's own naming so a typo'd filename still gets caught
    # while a real-but-not-yet-generated one doesn't.
    templates = ("onecol", "compact", "classic")
    names = {"good.pdf", "image_only.pdf"}
    names |= {f"sparse_{t}.pdf" for t in templates}
    names |= {f"long_meta_{t}.pdf" for t in templates}
    broken_src = REPO / "evals/fixtures/broken-src"
    names |= {p.stem + ".pdf" for p in broken_src.glob("*.typ")}
    return names


def test_all_fixture_file_references_resolve(evals_doc):
    buildable = _buildable_fixture_names()
    missing = []
    for skill in evals_doc["skills"]:
        for ev in skill["evals"]:
            for rel_path in ev["files"]:
                path = REPO / rel_path
                if path.is_file():
                    continue
                if path.parent == REPO / "evals/fixtures/build" and path.name in buildable:
                    continue  # not generated yet, but generate.py would produce exactly this
                missing.append(f"{skill['skill_name']}#{ev['id']}: {rel_path}")
    assert not missing, "fixture paths referenced in evals.json don't resolve:\n" + "\n".join(missing)


def test_application_tracker_skill_present(evals_doc):
    # Finding 10: the tracker previously had zero scenarios at all.
    names = [s["skill_name"] for s in evals_doc["skills"]]
    assert "application-tracker" in names


def test_evaluator_scenarios_cover_taxonomy_separation(evals_doc):
    # Finding 10: no evaluator scenario exercised the MECHANICAL/TARGET-FIT
    # split. Cheap tripwire so that coverage can't silently regress away
    # without this test noticing (real behavior is graded by the agent
    # run, not here — this just guards the scenario's continued presence).
    evaluator = next(s for s in evals_doc["skills"] if s["skill_name"] == "resume-evaluator")
    joined = " ".join(ev["expected_output"] + " " + " ".join(ev["assertions"])
                       for ev in evaluator["evals"])
    assert "TARGET FIT: NOT READY" in joined and "MECHANICAL: READY" in joined
    assert "unconfirmed" in joined.lower()


def test_tracker_scenarios_cover_workspace_permission_gating(evals_doc):
    # Round-7 finding 10 (refuted after first fix pass): the tracker's new
    # scenarios covered prepared->applied+digest, digest-mismatch,
    # duplicate-row, variants-legend, and funnel math, but the workspace/
    # permission-gating contract (SKILL.md section 1, "Workspace — same
    # gate as the vault") had zero scenarios and zero grep hits anywhere
    # in this file. Cheap tripwire so that coverage can't silently regress
    # away again (real behavior is graded by the agent run, not here —
    # this just guards the scenario's continued presence).
    tracker = next(s for s in evals_doc["skills"] if s["skill_name"] == "application-tracker")
    joined = " ".join(ev["expected_output"] + " " + " ".join(ev["assertions"])
                       for ev in tracker["evals"])
    lowered = joined.lower()
    assert "git check-ignore" in lowered
    assert "mode 600" in lowered or "600 permissions" in lowered
    assert "mode 700" in lowered or "700" in joined
    assert "icloud" in lowered or "cloud-synced" in lowered
    assert "never write first and chmod after" in lowered


# ── internal consistency: scenarios can't contradict their own inputs ──
#
# Round-8 finding 5: three scenarios shipped self-contradictory — an
# eval that treated a gate as resolved when nothing in its own prompt
# said so, an eval whose expectations ignored a gate its own attached
# fixture actually failed, and tracker evals that required live digest
# recomputation while attaching no files. These checks make that class
# of defect fail loudly instead of shipping green.

AUTH_GATE_KEYWORDS = ("work-authorization", "work authorization")
AUTH_STATEMENT_MARKERS = (
    "us citizen", "u.s. citizen", "citizen and", "no sponsorship needed",
    "don't need sponsorship", "green card", "permanent resident",
    "authorized to work", "i'm authorized", "i am authorized",
)
GATE_RESOLVED_MARKERS = (
    "met", "non-blocking", "neutralized", "resolved", "confirmed",
    "isn't an issue", "isn't a problem", "is fine", "that part's fine",
)


# A few prompts (eval 4) paste the target posting's own text inline —
# "...full text below since it's short.\n\nposting (excerpt, adapted..." —
# and posting boilerplate routinely reads "Must be authorized to work in
# the US". That third-person JD text must never be able to satisfy
# AUTH_STATEMENT_MARKERS on the candidate's behalf, so it has to be cut
# out before searching, not just concatenated in as more prompt text.
PROMPT_EXCERPT_MARKERS = ("posting (excerpt", "posting (adapted", "posting excerpt", "posting:")


def _candidate_authored_portion(prompt: str) -> str:
    """Return only the candidate-authored prefix of a prompt, truncated
    before any embedded posting/JD excerpt so JD boilerplate ("must be
    authorized to work in the US") can't be mistaken for something the
    candidate said."""
    lowered = prompt.lower()
    cut = len(prompt)
    for marker in PROMPT_EXCERPT_MARKERS:
        idx = lowered.find(marker)
        if idx != -1:
            cut = min(cut, idx)
    return prompt[:cut]


def test_work_authorization_claims_require_candidate_statement(evals_doc):
    # Finding 5, defect 2: eval 4 declared the work-authorization gate
    # "met/non-blocking (the prompt neutralized both)" although the
    # candidate never said one word about authorization/citizenship/
    # visa status anywhere in the prompt — there was nothing to
    # "neutralize". A scenario is allowed to leave the gate unconfirmed
    # (that's its own eval, id 6) but is not allowed to claim it
    # resolved without the candidate actually saying so.
    #
    # Round-8 finding 5 (second pass): this guard originally searched
    # AUTH_STATEMENT_MARKERS against the *entire* prompt string, but eval
    # 4's prompt embeds the target posting's own text verbatim, and that
    # posting boilerplate itself contains "Must be authorized to work in
    # the US" — so removing the candidate's actual citizenship sentence
    # left the test passing anyway, keyed off the JD's routine phrasing
    # instead of anything the candidate said. Search only the
    # candidate-authored portion (before any embedded posting excerpt).
    evaluator = next(s for s in evals_doc["skills"] if s["skill_name"] == "resume-evaluator")
    for ev in evaluator["evals"]:
        joined = (ev["expected_output"] + " " + " ".join(ev["assertions"])).lower()
        if not any(k in joined for k in AUTH_GATE_KEYWORDS):
            continue
        if "unconfirmed" in joined:
            continue  # this scenario is explicitly testing the open-question path
        if not any(m in joined for m in GATE_RESOLVED_MARKERS):
            continue  # gate is mentioned but not claimed resolved (nothing to check)
        prompt_lower = _candidate_authored_portion(ev["prompt"]).lower()
        assert any(m in prompt_lower for m in AUTH_STATEMENT_MARKERS), (
            f"resume-evaluator eval {ev['id']}: expectations treat the "
            "work-authorization gate as resolved, but the candidate-authored "
            "portion of the prompt (excluding any embedded posting/JD excerpt) "
            "never has the candidate state an authorization/citizenship/visa "
            "status — there is nothing in the scenario's own inputs to ground "
            "that claim"
        )


MONTH_NUMBERS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
GRAD_REQUIREMENT_RE = re.compile(
    r"graduat\w*\s+([A-Za-z]+)\.?\s+(\d{4})\s+or\s+(later|earlier)", re.IGNORECASE
)


def _grad_requirement_from_text(text: str) -> "tuple[tuple[int, int], str] | None":
    m = GRAD_REQUIREMENT_RE.search(text)
    if not m:
        return None
    month_name, year, qualifier = m.groups()
    month = MONTH_NUMBERS.get(month_name.strip(".").lower())
    if month is None:
        return None
    return (int(year), month), qualifier.lower()


def _candidate_grad_month_year(rel_path: str) -> "tuple[int, int] | None":
    # The only fixture with a known, checkable graduation date is
    # good.pdf, generated from resume-sample/resume.yaml (see
    # evals/fixtures/generate.py: GOOD_YAML). Read the real source
    # rather than hardcoding a date that could drift out of sync with it.
    if rel_path != "evals/fixtures/build/good.pdf":
        return None
    import yaml
    yaml_path = REPO / "evals/fixtures/resume-sample/resume.yaml"
    data = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    end = data["education"][0]["end"]  # "YYYY-MM"
    year, month = end.split("-")
    return int(year), int(month)


def _meets_grad_requirement(candidate: "tuple[int, int]", requirement) -> bool:
    (req_year, req_month), qualifier = requirement
    if qualifier == "later":
        return candidate >= (req_year, req_month)
    return candidate <= (req_year, req_month)


def test_graduation_gate_claims_match_the_actual_fixture_and_jd(evals_doc):
    # Finding 5, defect 3: eval 6 named work-authorization as the "sole"
    # open gate while attaching good.pdf (Jun 2026 grad, per
    # resume-sample/resume.yaml) alongside ml-intern-posting.md, which
    # itself requires "graduating Dec 2027 or later" — a gate the
    # attached fixture fails outright. Cross-check every resume-evaluator
    # eval that pairs a fixture with a known grad date against a JD
    # stating a grad requirement (in the prompt or an attached file)
    # against the real dates, so this class of self-contradiction can't
    # ship silently again.
    evaluator = next(s for s in evals_doc["skills"] if s["skill_name"] == "resume-evaluator")
    for ev in evaluator["evals"]:
        candidate = None
        for f in ev["files"]:
            candidate = _candidate_grad_month_year(f) or candidate
        if candidate is None:
            continue  # no fixture here with a checkable grad date

        blobs = [ev["prompt"]]
        for f in ev["files"]:
            path = REPO / f
            if path.suffix == ".md" and path.is_file():
                blobs.append(path.read_text(encoding="utf-8"))
        requirement = None
        for blob in blobs:
            requirement = _grad_requirement_from_text(blob) or requirement
        if requirement is None:
            continue  # no stated grad requirement to cross-check against

        joined = (ev["expected_output"] + " " + " ".join(ev["assertions"]))
        lowered = joined.lower()
        if _meets_grad_requirement(candidate, requirement):
            assert "graduation-date gate" not in lowered or any(
                m in lowered for m in ("met", "non-blocking", "fine", "neutralized")
            ), (
                f"resume-evaluator eval {ev['id']}: candidate grad date {candidate} "
                f"meets the stated requirement {requirement}, but expectations "
                "name the graduation-date gate without saying it's satisfied"
            )
        else:
            assert "graduation-date gate" in lowered or "grad" in lowered, (
                f"resume-evaluator eval {ev['id']}: candidate grad date {candidate} "
                f"FAILS the requirement {requirement} stated in the scenario's own "
                "prompt/attached JD, but nothing in expected_output/assertions "
                "names the graduation-date gate at all"
            )
            assert any(k in lowered for k in ("not met", "fail", "not ready")), (
                f"resume-evaluator eval {ev['id']}: the graduation-date gate is "
                "named but not stated as failing, even though the candidate's "
                f"grad date {candidate} does not meet {requirement}"
            )


def test_digest_recompute_scenarios_have_attached_files(evals_doc):
    # Finding 5, defect 4: two tracker evals asserted the agent
    # "recomputes the live file's digest" while declaring files: [] —
    # nothing to recompute a digest from. Any scenario whose assertions
    # require live digest recomputation must attach the file(s) it's
    # computing a digest against.
    tracker = next(s for s in evals_doc["skills"] if s["skill_name"] == "application-tracker")
    for ev in tracker["evals"]:
        joined = (ev["expected_output"] + " " + " ".join(ev["assertions"])).lower()
        if "recomputes the live file" in joined or "recompute the live file" in joined:
            assert ev["files"], (
                f"application-tracker eval {ev['id']}: assertions require "
                "recomputing a live file's digest, but no files are attached "
                "for the agent to compute one from"
            )


STALE_VERDICT_PHRASES = ("two-line verdict", "two-surface verdict")
# Note: SKILL.md itself still says "Two READY verdicts, always reported
# side by side" (correct — MECHANICAL and TARGET FIT are the two
# READY-gating surfaces; CRAFT is a third, non-gating surface alongside
# them). That literal quote is fine to appear in a scenario's assertions
# and is deliberately NOT in this list — only phrases that describe a
# scenario's *overall* verdict shape as two-wide are stale.


def test_no_stale_two_surface_verdict_language(evals_doc):
    # The evaluator's contract grew a third always-reported surface,
    # CRAFT (SKILL.md "Verdict rules": "a third surface, CRAFT, is
    # always reported alongside them but never gates either READY").
    # A scenario still describing its overall verdict as two-line/
    # two-surface is describing a stale contract.
    evaluator = next(s for s in evals_doc["skills"] if s["skill_name"] == "resume-evaluator")
    for ev in evaluator["evals"]:
        joined = (ev["expected_output"] + " " + " ".join(ev["assertions"])).lower()
        for phrase in STALE_VERDICT_PHRASES:
            assert phrase not in joined, (
                f"resume-evaluator eval {ev['id']} still describes the stale "
                f"'{phrase}' contract — current contract is three surfaces "
                "(MECHANICAL, TARGET FIT, CRAFT)"
            )


def test_every_resume_evaluator_eval_mentions_craft(evals_doc):
    # Every resume-evaluator eval that runs the battery produces a
    # report with all three verdict surfaces (SKILL.md "Report — always
    # this exact structure": "<three lines, always all three>"). Cheap
    # tripwire so CRAFT coverage can't quietly regress out of the
    # scenario file the way the two-line format quietly regressed in.
    evaluator = next(s for s in evals_doc["skills"] if s["skill_name"] == "resume-evaluator")
    missing = [ev["id"] for ev in evaluator["evals"]
               if "craft" not in (ev["expected_output"] + " " + " ".join(ev["assertions"])).lower()]
    assert not missing, f"resume-evaluator evals with no CRAFT mention: {missing}"


# ── funnel math sanity check (application-tracker eval id 5) ──────────
#
# Reproduces application-ledger.md's stage-conversion / median-latency /
# response-callback formulas against the exact six rows quoted in that
# eval's prompt, and checks the numbers its assertions claim.

STAGE_RANK = {"screen": 1, "interview": 2, "offer": 3}


def reached(row: dict, stage: str) -> bool:
    return any(STAGE_RANK.get(s, -1) >= STAGE_RANK[stage] for s, _ in row["transitions"])


def first_response_date(row: dict) -> "dt.date | None":
    dated = [d for _, d in row["transitions"] if d is not None]
    return min(dated) if dated else None


def stage_conversion(rows: list[dict], variant: str, from_stage: str | None, to_stage: str):
    # from_stage None means "applied" (the funnel's base denominator).
    if from_stage is None:
        base = [r for r in rows if r["variant"] == variant]
    else:
        base = [r for r in rows if r["variant"] == variant and reached(r, from_stage)]
    numerator = [r for r in base if reached(r, to_stage)]
    return len(numerator), len(base)


def median_latency(rows: list[dict], variant: str):
    latencies, excluded = [], 0
    for r in rows:
        if r["variant"] != variant:
            continue
        if r["applied"] is None:
            excluded += 1
            continue
        fr = first_response_date(r)
        if fr is None:
            excluded += 1
            continue
        latencies.append((fr - r["applied"]).days)
    latencies.sort()
    n = len(latencies)
    if n == 0:
        median = None
    elif n % 2 == 1:
        median = latencies[n // 2]
    else:
        median = (latencies[n // 2 - 1] + latencies[n // 2]) / 2
    return median, n, excluded


def _d(s: str) -> "dt.date | None":
    return None if s == "?" else dt.date.fromisoformat(s)


@pytest.fixture
def tracker_rows() -> list[dict]:
    # Exactly the six applied rows quoted in evals.json's
    # application-tracker eval id 5, plus their dated transitions.
    return [
        {  # Row A
            "variant": "ml-heavy", "applied": _d("2026-06-01"),
            "transitions": [("screen", _d("2026-06-10")), ("rejected", _d("2026-06-20"))],
        },
        {  # Row B
            "variant": "ml-heavy", "applied": _d("2026-06-03"),
            "transitions": [("screen", _d("2026-06-09")), ("interview", _d("2026-06-18")),
                             ("offer", _d("2026-06-28"))],
        },
        {  # Row C — still silent
            "variant": "ml-heavy", "applied": _d("2026-06-05"),
            "transitions": [],
        },
        {  # Row D
            "variant": "generalist", "applied": _d("2026-06-01"),
            "transitions": [("rejected", _d("2026-06-04"))],
        },
        {  # Row E — undated applied
            "variant": "generalist", "applied": _d("?"),
            "transitions": [("rejected", _d("2026-06-15"))],
        },
        {  # Row F — still silent
            "variant": "generalist", "applied": _d("2026-06-10"),
            "transitions": [],
        },
    ]


def test_ml_heavy_applied_to_screen_conversion(tracker_rows):
    numerator, base = stage_conversion(tracker_rows, "ml-heavy", None, "screen")
    assert (numerator, base) == (2, 3)


def test_ml_heavy_screen_to_interview_conversion(tracker_rows):
    numerator, base = stage_conversion(tracker_rows, "ml-heavy", "screen", "interview")
    assert (numerator, base) == (1, 2)


def test_ml_heavy_median_latency_excludes_silent_row(tracker_rows):
    median, n, excluded = median_latency(tracker_rows, "ml-heavy")
    assert (median, n, excluded) == (7.5, 2, 1)  # rows A(9d), B(6d); C excluded


def test_generalist_median_latency_excludes_undated_and_silent_rows(tracker_rows):
    median, n, excluded = median_latency(tracker_rows, "generalist")
    assert (median, n, excluded) == (3, 1, 2)  # row D(3d) only; E and F excluded


def test_row_d_is_response_not_callback(tracker_rows):
    row_d = tracker_rows[3]
    # A response is any employer reply; a callback requires reaching screen+.
    assert first_response_date(row_d) is not None  # it's a response
    assert not reached(row_d, "screen")  # never a callback


def test_row_f_crosses_no_response_threshold(tracker_rows):
    row_f = tracker_rows[5]
    today = dt.date(2026, 7, 23)
    elapsed = (today - row_f["applied"]).days
    assert elapsed == 43
    assert elapsed >= 21  # "no response" territory, not "pending"
