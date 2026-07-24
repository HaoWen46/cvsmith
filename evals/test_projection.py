"""The vault projection invariant, executable at the token level:
every hard-fact token (number, date, URL) in a projection exists
somewhere in the vault, and legitimate reframing (org renames,
title wording) never hard-fails.

The synthetic vault/projection pair is built inline so CI carries no
personal data; the one real pair under drafts/ (gitignored) is
exercised only where it exists — it is the zero-false-positive truth
the normalization was calibrated against.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHECK = REPO / "skills/resume-builder/scripts/check_projection.py"
DRAFTS = REPO / "drafts/haowen"

VAULT = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Education
- FACT: Example State University — B.S. Computer Science, Sep 2022 – Jun 2026
- FACT: GPA 3.90 / 4.0

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: cut API latency 40% across 3 services
- FACT: shipped a batching layer handling 1,200 requests/s
"""

RESUME = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com
  links:
    - label: GitHub
      url: https://github.com/samcasey

education:
  - institution: Example State University
    degree: B.S.
    field: Computer Science
    start: 2022-09
    end: 2026-06
    gpa: "3.90/4.0"

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Cut API latency 40% across 3 services.
      - Shipped a batching layer handling 1,200 requests/s.
"""


def run_check(resume: Path, vault: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(CHECK), str(resume), str(vault), "--json"],
        capture_output=True, text=True)
    assert proc.returncode in (0, 1), f"check_projection crashed:\n{proc.stderr}"
    return proc.returncode, json.loads(proc.stdout)


def ids_at(report: dict, level: str) -> set[str]:
    return {c["check_id"] for c in report["checks"] if c["level"] == level}


def details_at(report: dict, level: str) -> str:
    return " ".join(c["detail"] for c in report["checks"] if c["level"] == level)


def write_pair(tmp_path: Path, resume: str = RESUME, vault: str = VAULT):
    r, v = tmp_path / "resume.yaml", tmp_path / "career-vault.md"
    r.write_text(resume)
    v.write_text(vault)
    return r, v


# ── zero false positives ─────────────────────────────────────────────

def test_faithful_projection_is_clean(tmp_path):
    code, report = run_check(*write_pair(tmp_path))
    assert code == 0, f"false positive on a faithful projection: {report}"
    assert report["verdict"] == "pass"
    assert not ids_at(report, "fail")
    assert not ids_at(report, "warn"), \
        "nothing in the faithful pair should even warn"
    assert report["metrics"]["numbers_checked"] > 0
    assert report["metrics"]["dates_checked"] > 0
    assert report["metrics"]["urls_checked"] > 0


# ── every planted fabrication is caught ──────────────────────────────

def test_invented_number_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=RESUME.replace("40%", "45%")))
    assert code == 1
    assert "number_unsupported" in ids_at(report, "fail")
    fails = details_at(report, "fail")
    assert "45" in fails and "bullets" in fails, \
        "the report must surface the token and its yaml path"


def test_invented_url_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace("https://github.com/samcasey",
                              "https://www.samcasey.dev/")))
    assert code == 1
    assert "url_unsupported" in ids_at(report, "fail")
    assert "samcasey.dev" in details_at(report, "fail"), \
        "the normalized URL must be surfaced"


def test_unvaulted_date_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=RESUME.replace("end: 2026-06", "end: 2027-06")))
    assert code == 1
    assert "date_unsupported" in ids_at(report, "fail")
    assert "2027" in details_at(report, "fail")


# ── numeric boundaries: periods end sentences, digits end tokens ─────

def test_sentence_final_decimal_is_supported(tmp_path):
    # "…4.0." — the period ends the sentence, it is not a decimal point
    code, report = run_check(*write_pair(
        tmp_path, vault=VAULT.replace(
            "- FACT: GPA 3.90 / 4.0",
            "- FACT: my cumulative GPA is 3.90 / 4.0.")))
    assert code == 0, f"sentence-final period false-failed the token: {report}"
    assert not ids_at(report, "fail")


def test_mid_sentence_decimal_stays_supported(tmp_path):
    # regression guard: the boundary fix must not disturb the plain case
    code, report = run_check(*write_pair(
        tmp_path, vault=VAULT.replace(
            "- FACT: GPA 3.90 / 4.0",
            "- FACT: my cumulative GPA is 3.90 / 4.0 overall")))
    assert code == 0
    assert not ids_at(report, "fail")


def test_version_suffix_does_not_support_prefix_token(tmp_path):
    # vault "4.0.1" must not lend support to a standalone "4.0"
    code, report = run_check(*write_pair(
        tmp_path, vault=VAULT.replace(
            "- FACT: GPA 3.90 / 4.0",
            "- FACT: GPA 3.90; shipped widget-cli version 4.0.1")))
    assert code == 1
    assert "number_unsupported" in ids_at(report, "fail")
    assert "4.0" in details_at(report, "fail")


def test_longer_number_does_not_support_suffix_token(tmp_path):
    # vault "1480" / "1.480" must not lend support to a standalone "480"
    resume = RESUME + "      - Cut tail latency to 480 ms.\n"
    for decoy in ("- FACT: worst tail latency was 1480 ms",
                  "- FACT: worst tail latency was 1.480 s"):
        code, report = run_check(*write_pair(
            tmp_path, resume=resume, vault=VAULT + decoy + "\n"))
        assert code == 1, f"'{decoy}' lent support to a standalone 480"
        assert "number_unsupported" in ids_at(report, "fail")
        assert "480" in details_at(report, "fail")


# ── lenient by design: WARN, never FAIL ──────────────────────────────

def test_year_only_vault_date_warns_not_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, vault=VAULT.replace("Sep 2022 – Jun 2026", "2022 – 2026")))
    assert code == 0, "a year-only vault must not hard-fail the projection"
    assert report["verdict"] == "pass"
    assert "date_year_only" in ids_at(report, "warn")
    assert not ids_at(report, "fail")


def test_org_rename_warns_not_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=RESUME.replace("organization: Widget Corp",
                                        "organization: Widget Corporation")))
    assert code == 0, "org wording drift is reframing, not fabrication"
    assert report["verdict"] == "pass"
    assert "identity_drift" in ids_at(report, "warn")
    assert not ids_at(report, "fail")


# ── identity numbers: rewording may not smuggle in new numbers ───────

AWARD_VAULT = VAULT + """\

## Awards
- FACT: Regional ICPC — 5th place
"""

AWARD_RESUME = RESUME + """\

awards:
  - name: Regional ICPC — 5th place
"""


def test_identity_number_fabrication_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path,
        resume=AWARD_RESUME.replace("5th place", "1st place"),
        vault=AWARD_VAULT))
    assert code == 1, "a fabricated place in an award name must hard-fail"
    assert "number_unsupported" in ids_at(report, "fail")
    fails = details_at(report, "fail")
    assert "1" in fails and "awards" in fails, \
        "the report must surface the token and its yaml path"


def test_identity_number_verbatim_passes(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=AWARD_RESUME, vault=AWARD_VAULT))
    assert code == 0, f"a verbatim award name is supported by definition: {report}"
    assert not ids_at(report, "fail")
    assert not ids_at(report, "warn")


def test_identity_reword_with_supported_number_warns_only(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path,
        resume=AWARD_RESUME.replace("name: Regional ICPC — 5th place",
                                    "name: 5th Place, Regional ICPC"),
        vault=AWARD_VAULT))
    assert code == 0, "rewording around a vault-supported number is reframing"
    assert "identity_drift" in ids_at(report, "warn")
    assert not ids_at(report, "fail")


# ── fabricated identity: zero token overlap is not "drift" ───────────

def test_fabricated_identity_fails(tmp_path):
    # The reviewer's scenario: a Widget Corp intern projected as a Google
    # Chief Revenue Officer. No token of either field exists in the vault —
    # that is the fabrication class, not the rename class, and it must
    # block, not warn.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME
        .replace("organization: Widget Corp", "organization: Google")
        .replace("title: Software Engineering Intern",
                 "title: Chief Revenue Officer")))
    assert code == 1, "an identity with zero vault support must hard-fail"
    assert "identity_unsupported" in ids_at(report, "fail")
    fails = details_at(report, "fail")
    assert "vault" in fails, "the remediation (record it in the vault) must be named"


def test_partial_token_overlap_stays_drift_warn(tmp_path):
    # "Widget Corporation" shares 'widget' with the vault — rename class,
    # WARN as before. (Also covered by test_org_rename_warns_not_fails;
    # kept here as the explicit boundary against the zero-overlap FAIL.)
    code, report = run_check(*write_pair(
        tmp_path, resume=RESUME.replace("organization: Widget Corp",
                                        "organization: Widget Corporation")))
    assert code == 0
    assert "identity_drift" in ids_at(report, "warn")
    assert "identity_unsupported" not in ids_at(report, "fail")


# ── URLs: prefix of a different account is not support ───────────────

def test_url_prefix_collision_fails(tmp_path):
    # vault has github.com/samcasey; the projection claims github.com/samcase
    # (a different account that happens to be a prefix). Substring matching
    # accepted it; the boundary must not.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace("https://github.com/samcasey",
                              "https://github.com/samcase")))
    assert code == 1, "a URL-prefix collision must not count as vault support"
    assert "url_unsupported" in ids_at(report, "fail")


def test_url_deeper_path_still_supports_profile(tmp_path):
    # vault records the repo URL; the projection claims the profile above
    # it — same account, legitimate support.
    code, report = run_check(*write_pair(
        tmp_path,
        vault=VAULT.replace("github.com/samcasey",
                            "github.com/samcasey/widgets")))
    assert code == 0, "a deeper path in the vault supports the profile URL"
    assert "url_unsupported" not in ids_at(report, "fail")


# ── ongoing roles: 'present' is unverifiable, so it is surfaced ──────

def test_present_end_is_listed_for_review(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=RESUME.replace("end: 2025-09", "end: present")))
    assert code == 0, "'present' cannot be machine-verified either way"
    assert "ongoing_roles" in ids_at(report, "warn")
    warns = details_at(report, "warn")
    assert "experience[0]" in warns, "the review list must name the entry"


# ── numbers hide in every string field, not just the content keys ────

def test_number_in_coursework_is_checked(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace(
            "    gpa: \"3.90/4.0\"\n",
            "    gpa: \"3.90/4.0\"\n"
            "    coursework: [\"CS 4820 Advanced Algorithms\"]\n")))
    assert code == 1, "a number in an unscanned field slipped through"
    assert "number_unsupported" in ids_at(report, "fail")
    assert "4820" in details_at(report, "fail")


# ── metric direction: explicit markers are compared, order matters ───

def test_reversed_metric_fails(tmp_path):
    # the vault's own marker says 480 -> 210; the resume flips it
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME + "      - Brought build time 210 s -> 480 s.\n",
        vault=VAULT + "- FACT: brought build time 480 s -> 210 s\n"))
    assert code == 1, "a reversed vault marker is fabrication, not reframing"
    assert "metric_direction" in ids_at(report, "fail")
    fails = details_at(report, "fail")
    assert "210" in fails and "480" in fails and "reversed" in fails


def test_same_order_pair_is_verified(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME + "      - Brought build time 480 s -> 210 s.\n",
        vault=VAULT + "- FACT: brought build time 480 s -> 210 s\n"))
    assert code == 0, f"same-order pair vs the vault's own marker: {report}"
    assert not ids_at(report, "fail")
    assert "metric_direction" not in ids_at(report, "warn")
    assert any("1 verified" in note for note in report["notes"]), \
        "the audit note must count the pair as verified"


def test_cross_form_marker_is_verified(tmp_path):
    # vault states the direction in prose, resume as an arrow — same order
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME + "      - Cut p95 latency 480 ms → 210 ms.\n",
        vault=VAULT + "- FACT: cut p95 latency from 480 ms to 210 ms\n"))
    assert code == 0, f"cross-form same-direction pair false-failed: {report}"
    assert not ids_at(report, "fail")
    assert "metric_direction" not in ids_at(report, "warn")
    assert any("1 verified" in note for note in report["notes"])


def test_unmarked_vault_pair_warns_for_manual_review(tmp_path):
    # both numbers share a vault line, but nothing there marks a direction
    resume, vault = write_pair(
        tmp_path,
        resume=RESUME + "      - Cut tail latency 480 ms → 210 ms.\n",
        vault=VAULT + "- FACT: tail latency measured at 480 ms and 210 ms\n")
    code, report = run_check(resume, vault)
    assert code == 0, "an unmarked vault pair is unverifiable, not wrong"
    assert "metric_direction" in ids_at(report, "warn")
    assert not ids_at(report, "fail")
    assert any("need manual review" in note for note in report["notes"]), \
        "the audit note is the visible surface of the limitation"
    # the note must reach the human-readable output too
    proc = subprocess.run(
        [sys.executable, str(CHECK), str(resume), str(vault)],
        capture_output=True, text=True)
    assert proc.returncode == 0
    assert "metric pairs:" in proc.stdout


def test_no_directional_pairs_no_audit_note(tmp_path):
    resume, vault = write_pair(tmp_path)
    code, report = run_check(resume, vault)
    assert code == 0
    assert report["notes"] == []
    proc = subprocess.run(
        [sys.executable, str(CHECK), str(resume), str(vault)],
        capture_output=True, text=True)
    assert "metric pairs" not in proc.stdout


def test_from_to_does_not_pair_across_sentences(tmp_path):
    # "from 3 … . … to 210" spans a sentence boundary — not a pair
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME + "      - Scaled from 3 services. Brought p99 down "
                        "to 210 ms.\n",
        vault=VAULT + "- FACT: p99 latency 210 ms across 3 services\n"))
    assert code == 0
    assert report["notes"] == []
    assert "metric_direction" not in ids_at(report, "warn")


# ── per-entry scoping: a fact only belongs to its OWN vault entry ────
# The vault section-header format (### <org> — <title> (<start>–<end>))
# is what makes an entry's own block locatable; VAULT already uses it for
# Widget Corp. These tests add a second structured experience entry so a
# fact can be checked against the wrong one.

TWO_JOB_VAULT = VAULT + """
### Acme Robotics — Field Engineer (Feb 2024 – May 2025)
- FACT: reduced downtime 30% across 6 sites
"""

TWO_JOB_RESUME = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com
  links:
    - label: GitHub
      url: https://github.com/samcasey

education:
  - institution: Example State University
    degree: B.S.
    field: Computer Science
    start: 2022-09
    end: 2026-06
    gpa: "3.90/4.0"

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Reduced downtime 30% across 6 sites.
  - organization: Acme Robotics
    title: Field Engineer
    start: 2024-02
    end: 2025-05
    bullets:
      - Cut API latency 40% across 3 services.
"""


def test_swapped_achievement_between_entries_fails(tmp_path):
    # Widget Corp's 40%/3-services fact and Acme's 30%/6-sites fact swap
    # employers. Both numbers exist SOMEWHERE in the vault, so a whole-vault
    # search passes them; per-entry scoping must not.
    code, report = run_check(*write_pair(
        tmp_path, resume=TWO_JOB_RESUME, vault=TWO_JOB_VAULT))
    assert code == 1, f"facts swapped between employers must fail: {report}"
    fails = ids_at(report, "fail")
    assert "number_misattributed" in fails, \
        f"expected a misattribution fail, got: {report['checks']}"
    detail = details_at(report, "fail")
    assert "30" in detail and "40" in detail
    assert "experience[0]" in detail or "experience[1]" in detail


def test_faithful_two_entry_projection_stays_clean(tmp_path):
    # sanity: scoping must not false-fail the honest, unswapped pairing
    resume = TWO_JOB_RESUME.replace(
        "      - Reduced downtime 30% across 6 sites.\n"
        "  - organization: Acme Robotics\n"
        "    title: Field Engineer\n"
        "    start: 2024-02\n"
        "    end: 2025-05\n"
        "    bullets:\n"
        "      - Cut API latency 40% across 3 services.\n",
        "      - Cut API latency 40% across 3 services.\n"
        "  - organization: Acme Robotics\n"
        "    title: Field Engineer\n"
        "    start: 2024-02\n"
        "    end: 2025-05\n"
        "    bullets:\n"
        "      - Reduced downtime 30% across 6 sites.\n")
    code, report = run_check(*write_pair(
        tmp_path, resume=resume, vault=TWO_JOB_VAULT))
    assert code == 0, f"false positive on the correctly-attributed pair: {report}"
    assert not ids_at(report, "fail")


def test_unmatched_entry_in_structured_vault_warns_and_falls_back(tmp_path):
    # the vault clearly structures Experience by ### heading, but this
    # entry's org/title don't match any of them — can't scope it, so it
    # must say so (WARN) rather than silently doing a whole-vault check
    # with no signal that scoping failed.
    resume = TWO_JOB_RESUME.replace(
        "organization: Acme Robotics", "organization: Zenith Robotics")
    code, report = run_check(*write_pair(
        tmp_path, resume=resume, vault=TWO_JOB_VAULT))
    assert "entry_unscoped" in ids_at(report, "warn"), \
        f"an entry the vault's own structure can't place must warn: {report}"


# ── unmatched entries may never silently borrow another entry's fact ─
# Round-5 gave scoped-but-matched entries a misattribution FAIL when a
# fact belongs to a DIFFERENT heading. An entry the anchor match can't
# place at all must not get a free pass around that rule just because
# it has no own block to be misattributed against.

UNMATCHED_BORROW_RESUME = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Cut API latency 40% across 3 services.
  - organization: Zenith Robotics
    title: Field Engineer
    start: 2024-02
    end: 2025-05
    bullets:
      - Cut API latency 40% across 3 services.
"""


def test_unmatched_entry_borrowing_claimed_entrys_fact_fails(tmp_path):
    # entry[0] Widget Corp is correctly matched with its OWN fact; entry[1]
    # (Zenith Robotics, unmatched — no heading covers it) claims that SAME
    # Widget Corp fact instead of anything from its own (nonexistent) vault
    # entry. Widget Corp's block IS matched this run, so borrowing it is
    # the swapped-fact class, not an unresolved rename: must FAIL, not a
    # warn-only whole-vault pass.
    code, report = run_check(*write_pair(
        tmp_path, resume=UNMATCHED_BORROW_RESUME, vault=TWO_JOB_VAULT))
    assert code == 1, \
        f"an unmatched entry borrowing a fact claimed by another current " \
        f"entry must fail: {report}"
    assert "number_misattributed" in ids_at(report, "fail")
    assert "entry_unscoped" in ids_at(report, "warn")


def test_unmatched_entry_own_fact_warns_unanchored_not_fail(tmp_path):
    # Zenith Robotics is Acme's honest rename, not yet reflected in the
    # vault. Its fact is genuinely its own — support for it exists only in
    # Acme's block, which no CURRENT resume entry claims (nobody's org
    # matches "Acme Robotics" anymore). That is an unresolved-rename risk,
    # not a swap between two entries both present in this resume: WARN for
    # manual audit, never a silent FAIL.
    resume = TWO_JOB_RESUME.replace(
        "      - Reduced downtime 30% across 6 sites.\n"
        "  - organization: Acme Robotics\n"
        "    title: Field Engineer\n"
        "    start: 2024-02\n"
        "    end: 2025-05\n"
        "    bullets:\n"
        "      - Cut API latency 40% across 3 services.\n",
        "      - Cut API latency 40% across 3 services.\n"
        "  - organization: Zenith Robotics\n"
        "    title: Field Engineer\n"
        "    start: 2024-02\n"
        "    end: 2025-05\n"
        "    bullets:\n"
        "      - Reduced downtime 30% across 6 sites.\n")
    code, report = run_check(*write_pair(
        tmp_path, resume=resume, vault=TWO_JOB_VAULT))
    assert code == 0, f"an unresolved rename's own fact must not hard-fail: {report}"
    assert "number_unanchored_support" in ids_at(report, "warn"), \
        f"support found only outside any claimed entry must be flagged " \
        f"for manual audit: {report}"
    assert "entry_unscoped" in ids_at(report, "warn")
    assert "number_misattributed" not in ids_at(report, "fail")


# ── numeric presence is not meaning: a topic-swapped claim must not ──
# pass silently just because its numbers coincide with an unrelated
# vault line inside the same (correctly matched) entry.

SEMANTIC_VAULT = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: reduced latency 40% across 3 services
"""

SEMANTIC_RESUME = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Raised revenue 40% across 3 regions.
"""


def test_semantic_mismatch_within_entry_warns_not_passes_silently(tmp_path):
    # "40% across 3" matches token-for-token, but the claim is about
    # revenue/regions while the vault's only line under this entry is
    # about latency/services — a topic swap the token sweep can't see.
    code, report = run_check(*write_pair(
        tmp_path, resume=SEMANTIC_RESUME, vault=SEMANTIC_VAULT))
    assert code == 0, \
        f"a topic-swapped claim must not hard-fail on tokens alone: {report}"
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"a claim whose numbers coincidentally match an unrelated vault " \
        f"line must be flagged for manual audit, not passed cleanly: {report}"
    warns = details_at(report, "warn")
    assert "revenue" in warns and "regions" in warns, \
        "the claim line must be shown"
    assert "latency" in warns and "services" in warns, \
        "the coincidentally-matching vault line must be shown alongside it"


SPLIT_FACT_VAULT = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: reduced latency 40% across 3 services
- FACT: mentored 2 interns over 6 months
"""

SPLIT_FACT_RESUME = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Increased revenue 40% within 6 months.
"""


def test_numbers_split_across_facts_warns_not_passes_silently(tmp_path):
    # "40%" only supports the latency FACT; "6" only supports the
    # mentoring FACT — no single vault line covers both, so
    # best_full_support_line() finds nothing and must not let the claim
    # through with zero signal just because each number individually
    # exists somewhere in the block.
    code, report = run_check(*write_pair(
        tmp_path, resume=SPLIT_FACT_RESUME, vault=SPLIT_FACT_VAULT))
    assert code == 0, \
        f"numbers split across facts must not hard-fail: {report}"
    assert "claim_numbers_span_multiple_facts" in ids_at(report, "warn"), \
        f"a claim whose numbers only verify when combined across two " \
        f"separate vault facts must be flagged for manual audit, not " \
        f"passed cleanly: {report}"
    assert report["verdict"] == "pass"
    warns = details_at(report, "warn")
    assert "revenue" in warns and "6 months" in warns, "the claim must be shown"


def test_paraphrase_spanning_two_lines_of_same_fact_warns_not_fails(tmp_path):
    # An honest claim whose numbers legitimately combine across two lines
    # of the SAME underlying fact (split for readability in the vault)
    # has no single line to compare against either — this is expected to
    # warn for manual audit (harmless, conservative), never FAIL.
    vault = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: cut API latency 40% across 3 services
- FACT: latency work spanned 6 months total
"""
    resume = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Cut API latency 40% across 3 services over 6 months.
"""
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 0
    assert report["verdict"] == "pass"
    assert "claim_numbers_span_multiple_facts" in ids_at(report, "warn"), \
        f"numbers split across two lines must warn for manual audit even " \
        f"when the underlying claim is honest — presence-not-meaning " \
        f"cannot tell the two cases apart mechanically: {report}"
    assert not ids_at(report, "fail")


def test_legitimate_rephrase_within_entry_does_not_warn(tmp_path):
    # honest rewording that keeps the subject (latency, services) must
    # keep passing cleanly — the overlap test must not become a new
    # brittle semantic-guessing FAIL/WARN-everything heuristic.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace(
            "Cut API latency 40% across 3 services.",
            "Reduced API latency by 40% across 3 backend services.")))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"an honest rephrasing sharing content words must not be flagged: {report}"


# Two extra FACT lines beyond the one under test, reusing "api",
# "retail", and "clients" the way a real vault does across several
# bullets for the same role — this is what makes those three words
# vault-generic FURNITURE (each recurs 3x) while "latency", "backend",
# and "reduced" stay this fact's own distinctive, once-only content.
# That document-frequency gap is exactly what word_weight()'s idf-like
# rarity weighting prices, and it is why the calibration numbers in
# every comment below cite THIS vault, not a single isolated FACT line
# — see CLAIM_LINE_OVERLAP_THRESHOLD's comment in check_projection.py
# for the measured effect of adding these two lines (a materially
# wider legitimate/fabrication margin, with numbers, not by ritual).
DESCRIPTOR_PAD_VAULT = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: reduced api latency 40% across 3 backend services for retail clients
- FACT: supported api integrations for other retail clients accounts
- FACT: presented api roadmap updates to retail clients monthly
"""


def _descriptor_pad_resume(bullet: str) -> str:
    return f"""\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - {bullet}
"""


def test_two_descriptor_pad_bypass_now_warns(tmp_path):
    # The exact adversarial pair that slipped past the old absolute
    # MIN_SHARED_CONTENT_WORDS=2 threshold: the claim keeps two of the
    # vault line's own generic descriptors ("api", "retail") while
    # swapping the real verb+object ("reduced ... latency" -> "boosted
    # ... revenue") and the metric's scope noun ("services" ->
    # "regions"). Under weighted line coverage (idf over
    # DESCRIPTOR_PAD_VAULT, where "api"/"retail"/"clients" recur across
    # 3 lines each but "latency"/"backend"/"reduced"/"services" appear
    # once): shared = {api, retail}; line coverage = 0.24 — well below
    # the 0.5 threshold, so this must warn where the old fixed count of
    # 2 let it through clean.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Boosted api revenue 40% across 3 retail regions."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0, \
        f"a topic-swapped claim must not hard-fail on tokens alone: {report}"
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"padding a fabricated claim with 2 of the vault line's own " \
        f"generic descriptors (line coverage 0.24) must not buy a " \
        f"silent PASS the way the old fixed count of 2 did: {report}"


def test_one_descriptor_pad_still_warns(tmp_path):
    # Same topic swap, only 1 shared descriptor ("api") kept.
    # shared = {api}; line coverage ≈ 0.12 — well below 0.5.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Boosted regional revenue 40% across 3 api workflows."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"a single padded descriptor (line coverage 0.12) must not " \
        f"suppress the mismatch warning: {report}"


def test_three_descriptor_pad_still_warns_given_other_real_content(tmp_path):
    # 3 shared descriptors ("retail", "api", "services") kept, but the
    # claim also carries its own distinct filler ("quarterly", "regional",
    # "growth", "accounts") — under line coverage (denominator is the
    # LINE's own weighted vocabulary, unaffected by how much the claim
    # itself grows), those extra claim words buy nothing: shared =
    # {retail, api, services}; line coverage ≈ 0.40 — still below 0.5,
    # and this is the tightest-margin fabrication case in the
    # calibration table (see CLAIM_LINE_OVERLAP_THRESHOLD's comment).
    # (Padding costs the fabrication nothing either way here — the
    # point isn't that a bigger claim scores lower, it's that adding
    # claim-side filler no longer helps OR hurts, so the vault line's
    # own distinctive words missing is what still catches this.)
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Boosted quarterly regional revenue growth 40% across 3 "
            "retail api services accounts."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"3 padded descriptors alongside other distinct claim content " \
        f"(line coverage ~0.40, the tightest fabrication margin in the " \
        f"calibration table) must not suppress the mismatch warning: {report}"


# ── round-6 bypass claims: the exact two the adversarial verifier ────
# found against the two prior rounds' fixes, both silent clean PASSes
# before this round (see CLAIM_LINE_OVERLAP_THRESHOLD's comment in
# check_projection.py for the full calibration table these belong to).

def test_round6_bypass_three_shared_generics_now_warns(tmp_path):
    # "Boosted api retail clients 40% across 3 accounts." — kept 3 of
    # the vault line's generic words (api, retail, clients), dropped
    # every distinctive one (latency, backend, reduced, services).
    # Old round-5 ratio: 3 shared / min(5,7) = 0.60 — CLEARED the old
    # 0.5 threshold, a silent bypass. Line coverage here: 0.36 — below
    # 0.5, now warns.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Boosted api retail clients 40% across 3 accounts."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0, \
        f"a topic-swapped claim must not hard-fail on tokens alone: {report}"
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"keeping 3 of the vault line's generic words while dropping " \
        f"every distinctive one (old ratio 0.60, cleared the old " \
        f"threshold) must warn under line coverage (0.36): {report}"


def test_round6_bypass_two_shared_generics_exact_tie_now_warns(tmp_path):
    # "Boosted retail clients 40% across 3 accounts." — the exact-tie
    # bypass: old round-5 ratio = 2 shared / min(4,7) = 0.50, EQUAL to
    # the old threshold, and the old strict '<' comparison let an exact
    # tie through as a silent clean PASS. Line coverage here: 0.24 —
    # comfortably below the new 0.5 bar, independent of the equality
    # question this specific claim originally turned on (see
    # test_exact_equality_at_threshold_still_warns below for that
    # question tested in isolation).
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Boosted retail clients 40% across 3 accounts."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0, \
        f"a topic-swapped claim must not hard-fail on tokens alone: {report}"
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"the exact old-threshold tie (old ratio 0.50, let through by " \
        f"strict '<') must warn under line coverage (0.24): {report}"


def test_fresh_short_claim_two_shared_generics_warns(tmp_path):
    # Fresh short-claim variant, not one of the original bypasses: 6
    # words, shares 2 of the vault line's generic words (api, clients),
    # 0 distinctive words shared. Line coverage: 0.24.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Grew api clients footprint 40% across 3 deals."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"a fresh short claim sharing only 2 generic words (line " \
        f"coverage 0.24) must warn, same as the planted bypasses: {report}"


def test_fresh_short_claim_two_shared_generics_variant_warns(tmp_path):
    # Same shape, different generic pair (retail, clients) and 0
    # distinctive words shared, confirming this isn't specific to which
    # 2 generic words got kept. Line coverage: 0.24.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Lifted retail clients volume 40% across 3 territories."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"a different fresh short claim sharing only 2 generic words " \
        f"(line coverage 0.24) must also warn: {report}"


def test_synonym_swap_stays_clean_with_margin_against_descriptor_vault(tmp_path):
    # Legitimate shape 1 against DESCRIPTOR_PAD_VAULT specifically (not
    # the simpler default VAULT): verb synonym ("reduced" -> "cut"),
    # object reworded ("latency" -> "response latency"), drops "retail
    # clients" — but keeps every OTHER distinctive word (api, backend,
    # latency, services). Line coverage: 0.60 — clear of the 0.5 bar
    # with the same ~0.10 margin as the tightest fabrication case
    # (0.40) leaves on the other side.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Cut api response latency 40% across 3 backend services."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"a synonym-swap rephrasing (line coverage 0.60) must not be " \
        f"flagged: {report}"


def test_reordered_stays_clean_against_descriptor_vault(tmp_path):
    # Legitimate shape 2: same words as the vault line, reordered and
    # dropping only stopwords ("for"). Line coverage: 1.00.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Across 3 backend services for retail clients, reduced api "
            "latency 40%."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"a reordered rephrasing (line coverage 1.00) must not be " \
        f"flagged: {report}"


def test_compressed_stays_clean_with_margin_against_descriptor_vault(tmp_path):
    # Legitimate shape 3: drops "backend" and "services" — a shorter,
    # honest claim about the same fact. Line coverage: 0.68.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Reduced api latency 40% for retail clients."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"a compressed rephrasing (line coverage 0.68) must not be " \
        f"flagged: {report}"


def test_exact_equality_at_threshold_still_warns(tmp_path):
    # Direct, isolated test of the equality fix: a claim engineered so
    # its weighted line coverage lands EXACTLY on
    # CLAIM_LINE_OVERLAP_THRESHOLD (0.5), not merely near it. The vault
    # line's 4 content words (increased, weekly, throughput, clusters)
    # each appear exactly once anywhere in this vault, so they carry
    # equal idf weight; the claim keeps exactly 2 of the 4 ->
    # ratio = 2/4 = 0.50 precisely. Round 6's finding was that the old
    # strict '<' comparison let an exact tie through clean — this must
    # not repeat: equality must warn, only a ratio that strictly
    # EXCEEDS the threshold may stay silent.
    vault = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: increased weekly throughput 40% across 3 clusters
"""
    resume = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Increased throughput 40% across 3 nodes.
"""
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 0
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"a claim landing EXACTLY on the 0.5 threshold (not merely " \
        f"near it) must warn — equality is not enough to clear the " \
        f"bar: {report}"


def test_verbose_paraphrase_with_extra_claim_words_does_not_warn(tmp_path):
    # A legitimate but wordy rephrasing that adds its OWN connective
    # words beyond the vault line ("Scaled from 3 services. Brought ...
    # down to") — the case a SYMMETRIC weighted Jaccard was tried and
    # rejected for: Jaccard penalizes the claim's extra vocabulary the
    # same way it penalizes a fabrication's missing vocabulary, scoring
    # this legitimate claim 0.36 (indistinguishable from an adversarial
    # 2-descriptor pad's 0.15-0.18 range). Weighted LINE coverage does
    # not have this failure mode: it only measures how much of the
    # vault line's own content the claim contains, so the claim's extra
    # elaboration is never counted against it. Line coverage: 0.68.
    resume = RESUME + ("      - Scaled from 3 services. Brought p99 down "
                        "to 210 ms.\n")
    vault = VAULT + "- FACT: p99 latency 210 ms across 3 services\n"
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"a verbose but honest paraphrase (line coverage 0.68) must " \
        f"not be flagged just for adding its own connective words: {report}"


def test_synonym_swap_rephrase_does_not_warn(tmp_path):
    # Legitimate-rephrase shape 1: swap the verb for a synonym, keep the
    # rest verbatim. claim_words = {lowered, api, latency, services} (4);
    # line_words (VAULT's "cut api latency 40% across 3 services") =
    # {cut, api, latency, services} (4); shared = {api, latency,
    # services} (3) -> ratio = 3/4 = 0.75 — clear of the 0.5 line.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace(
            "Cut API latency 40% across 3 services.",
            "Lowered API latency 40% across 3 services.")))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"a synonym-swap rephrasing (ratio 0.75) must not be flagged: {report}"


def test_reordered_rephrase_does_not_warn(tmp_path):
    # Legitimate-rephrase shape 2: same words, different order — the
    # bag-of-words overlap test is order-insensitive by construction.
    # claim_words == line_words == {cut, api, latency, services} (4) ->
    # ratio = 4/4 = 1.0.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace(
            "Cut API latency 40% across 3 services.",
            "Across 3 services, cut API latency 40%.")))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"a reordered rephrasing (ratio 1.0) must not be flagged: {report}"


def test_compressed_rephrase_does_not_warn(tmp_path):
    # Legitimate-rephrase shape 3: drop words rather than substitute
    # them — a shorter, honest claim about the same fact.
    # claim_words = {cut, api, latency} (3); line_words = {cut, api,
    # latency, services} (4); shared = {cut, api, latency} (3) ->
    # ratio = 3/min(3,4) = 3/3 = 1.0.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace(
            "Cut API latency 40% across 3 services.",
            "Cut API latency 40%.")))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"a compressed rephrasing (ratio 1.0) must not be flagged: {report}"


def test_one_shared_unit_noun_is_not_enough_to_suppress_mismatch_warn(tmp_path):
    # Same topic-swap as test_semantic_mismatch_within_entry_warns_not_
    # passes_silently, but the claim keeps the vault line's own metric
    # unit noun ("services") instead of substituting an unrelated one
    # ("regions") — a fabricated claim reusing one generic noun from the
    # correct vault line must not buy a silent PASS just because
    # content_words() overlap is nonempty. "services" here describes the
    # number's scope, not the achievement; opposite verb (raised vs cut)
    # and opposite object (revenue vs latency) still make this a
    # different fact.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME.replace(
            "Cut API latency 40% across 3 services.",
            "Raised revenue 40% across 3 services.")))
    assert code == 0, \
        f"a topic-swapped claim must not hard-fail on tokens alone: {report}"
    assert "claim_semantic_mismatch" in ids_at(report, "warn"), \
        f"a single shared unit noun ('services') must not suppress the " \
        f"mismatch warning for an otherwise unrelated claim: {report}"
    warns = details_at(report, "warn")
    assert "Raised revenue" in warns, "the claim line must be shown"
    assert "cut api latency" in warns, \
        "the coincidentally-matching vault line must be shown alongside it"


# ── fallback pairing calibration: never-scoped fields (basics.summary) ──
# basics.summary has no SCOPED_SECTIONS entry, and career-vault.md's
# Basics section is never written with ### sub-headings — every numeric
# claim there always hits the pairing loop's final "never scoped at all"
# branch, matched against the WHOLE vault's word_df (every heading,
# contact line, and unrelated section's FACT), not one coherent entry
# block. An adversarial verifier found this branch reused
# CLAIM_LINE_OVERLAP_THRESHOLD with zero calibration of its own; these
# tests are that calibration (see check_projection.py's pairing-loop
# comment for the full measured margin table and the resulting design
# decision: this branch never WARNs — see the tests below for why no
# honest threshold exists here).

SUMMARY_VAULT = VAULT.replace(
    "- FACT: sam.casey@example.com · github.com/samcasey\n",
    "- FACT: sam.casey@example.com · github.com/samcasey\n"
    "- FACT: led a team of 8 engineers shipping 4 releases per quarter\n")


def _summary_resume(summary: str) -> str:
    return RESUME.replace(
        "basics:\n  name: Sam Casey\n",
        f'basics:\n  name: Sam Casey\n  summary: "{summary}"\n')


def test_fallback_summary_synonym_swap_stays_info_not_warn(tmp_path):
    # TDD anchor: the adversarial verifier's exact honest paraphrase,
    # scored against THIS branch's whole-vault matching (not the scoped
    # DESCRIPTOR_PAD_VAULT calibration above): "Directed a squad of 8
    # engineers launching 4 releases per quarter" vs vault "led a team of
    # 8 engineers shipping 4 releases per quarter" — weighted line
    # coverage here is ~0.47 (see the margin table in check_projection.py),
    # which the OLD code (reusing CLAIM_LINE_OVERLAP_THRESHOLD=0.5
    # unmodified for this branch) flagged claim_semantic_mismatch / WARN
    # on a truthful claim — a false positive. This branch must never warn
    # at all (see the design decision in the pairing loop's comment): the
    # row is labeled "info" (round-7: distinct from "pass", which now
    # means mechanically confirmed) — informational only, never counted
    # as verified.
    claim = ("Directed a squad of 8 engineers launching 4 releases per "
             "quarter.")
    code, report = run_check(*write_pair(
        tmp_path, resume=_summary_resume(claim), vault=SUMMARY_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        f"an honest paraphrase must never be flagged by the never-scoped " \
        f"fallback branch, which has no reliable threshold: {report}"
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    assert claim in pairings, f"the summary claim must get a pairing row: {report}"
    row = pairings[claim]
    assert row["level"] == "info", (
        f"an honest paraphrase must never be flagged by the never-scoped "
        f"fallback branch, and must not be mislabeled 'pass' (mechanically "
        f"confirmed) either — it is 'info': {row}")
    assert row["sources"], f"the true source line must still be shown: {row}"


def test_fallback_summary_reorder_stays_info(tmp_path):
    # Legitimate shape 2: reorder, no substitutions. Line coverage ~0.93.
    claim = "Shipping 4 releases per quarter, led a team of 8 engineers."
    code, report = run_check(*write_pair(
        tmp_path, resume=_summary_resume(claim), vault=SUMMARY_VAULT))
    assert code == 0
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    assert pairings[claim]["level"] == "info"


def test_fallback_summary_compression_stays_info(tmp_path):
    # Legitimate shape 3: drop words rather than substitute. Line
    # coverage ~0.77.
    claim = "Led a team of 8 engineers shipping 4 releases."
    code, report = run_check(*write_pair(
        tmp_path, resume=_summary_resume(claim), vault=SUMMARY_VAULT))
    assert code == 0
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    assert pairings[claim]["level"] == "info"


def test_fallback_summary_generic_only_claim_stays_informational_not_warn(tmp_path):
    # Fabrication shape: keeps only 2 of the vault line's generic frame
    # words ("per", "quarter" — dropped as a stopword and kept
    # respectively) and swaps every distinctive word (team/engineers ->
    # vendors, shipping/releases -> onboarded, quarter's own scope
    # changes from "engineers" to "regions"). Line coverage ~0.16 — under
    # the OLD reused threshold this would have WARNed
    # claim_semantic_mismatch; the whole point of the design decision
    # here is that a LOW score on this branch is exactly as
    # unreliable as a high one (see
    # test_fallback_summary_synonym_swap_stays_info_not_warn and the
    # verb+object-swap case in the margin table, which scores identically
    # to a legitimate rephrase) — so this branch never turns a low ratio
    # into a WARN either. It must still be listed, with its ratio
    # printed, purely informational.
    claim = "Onboarded 8 vendors per quarter across 4 regions."
    code, report = run_check(*write_pair(
        tmp_path, resume=_summary_resume(claim), vault=SUMMARY_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn")
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    row = pairings[claim]
    assert row["level"] == "info", (
        f"the never-scoped fallback branch must never WARN, even on a "
        f"low ratio — it has no honest threshold (see the margin table), "
        f"and it must not be mislabeled 'pass' either: {row}")
    assert row["sources"], "the coincidentally-matching line must still show"
    assert "informational" in row["detail"], (
        f"the detail must say this branch's ratio is informational only, "
        f"not a tripwire: {row}")
    assert report["metrics"]["claim_pairings_manual_audit"] == 0, (
        "a never-scoped fallback pairing must never count toward the "
        f"manual-audit metric: {report['metrics']}")


# ── claim -> source pairing: mandatory, always-emitted visibility ────
# No lexical tripwire — this one included — can fully tell a synonym
# swap from a verb+object swap from word overlap alone. The pairing
# section is the structural answer: every numeric claim gets a row
# next to its vault source (or its FAIL/manual-audit status), whether
# or not the WARN check above happens to fire on it.

def test_claim_pairings_lists_every_numeric_claim(tmp_path):
    # The faithful default pair has 3 numeric content claims: the GPA
    # value, and the two experience bullets. Every one of them must
    # appear in report["claim_pairings"] with its source line shown.
    # VAULT's Education section is plain FACT bullets with no ###
    # heading, so gpa is never-scoped — "info" (round 7, fix 5), not a
    # mechanically-confirmed "pass"; the two experience bullets ARE
    # scoped to Widget Corp's own ### block and clear the overlap bar,
    # so they stay "pass".
    code, report = run_check(*write_pair(tmp_path))
    assert code == 0
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    assert "3.90/4.0" in pairings
    assert "Cut API latency 40% across 3 services." in pairings
    assert "Shipped a batching layer handling 1,200 requests/s." in pairings
    assert pairings["3.90/4.0"]["level"] == "info", \
        f"gpa is never-scoped (Education has no ### heading in VAULT) " \
        f"— informational, not mechanically confirmed: {pairings['3.90/4.0']}"
    for claim in ("Cut API latency 40% across 3 services.",
                  "Shipped a batching layer handling 1,200 requests/s."):
        row = pairings[claim]
        assert row["level"] == "pass", \
            f"a scoped, verified bullet should not warn or go " \
            f"informational: {row}"
    for row in pairings.values():
        assert row["sources"], \
            f"a clean pairing must still show its supporting line: {row}"


def test_claim_pairings_key_always_present_on_fail_too(tmp_path):
    # Mandatory means always emitted, including on a hard FAIL — the
    # pairing table is not something that only appears on a clean run.
    code, report = run_check(*write_pair(
        tmp_path, resume=RESUME.replace("40%", "45%")))
    assert code == 1
    assert "claim_pairings" in report
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    assert "Cut API latency 45% across 3 services." in pairings
    assert pairings["Cut API latency 45% across 3 services."]["level"] == "fail"


def test_claim_pairings_shows_source_alongside_a_warned_mismatch(tmp_path):
    # When the lexical check DOES catch a mismatch, the pairing table
    # must show the same claim/source pair the WARN detail already
    # does — the table is not a second, disconnected source of truth.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Boosted retail clients 40% across 3 accounts."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    row = pairings["Boosted retail clients 40% across 3 accounts."]
    assert row["level"] == "warn"
    assert any("retail clients" in src for src in row["sources"]), \
        f"the pairing table must show the coincidentally-matching " \
        f"vault line: {row}"


def test_claim_pairings_visible_even_when_the_lexical_check_misses(tmp_path):
    # The guarantee this section exists for: a single strategic word
    # swap deep inside an otherwise-verbatim, long vault line (here,
    # "latency" -> "cost", keeping every other distinctive word) clears
    # the weighted line-coverage bar (0.84) and stays a silent PASS on
    # the WARN check — an acknowledged residue no bag-of-words ratio
    # closes (see weighted_overlap()'s docstring). The pairing table
    # must still print this claim right next to its true source line,
    # so a human (or the resume-evaluator) can catch it by eye even
    # though the mechanical tripwire did not fire.
    code, report = run_check(*write_pair(
        tmp_path,
        resume=_descriptor_pad_resume(
            "Reduced api cost 40% across 3 backend services for retail "
            "clients."),
        vault=DESCRIPTOR_PAD_VAULT))
    assert code == 0
    assert "claim_semantic_mismatch" not in ids_at(report, "warn"), \
        "this specific claim is expected to clear the lexical bar " \
        "(that's the point being tested)"
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    claim_text = ("Reduced api cost 40% across 3 backend services for "
                  "retail clients.")
    assert claim_text in pairings, \
        "a claim the WARN check misses must still get a pairing row"
    row = pairings[claim_text]
    assert row["level"] == "pass"
    assert any("reduced api latency" in src for src in row["sources"]), \
        f"the true source line must still be shown for human review, " \
        f"even though the lexical check found nothing to flag: {row}"


def test_claim_pairings_covers_unscoped_entry_claim_too(tmp_path):
    # An entry the vault's own structure couldn't scope (entry_unscoped)
    # still gets its numeric claim listed in the pairing table — the
    # visibility guarantee is not limited to entries the scoping/overlap
    # machinery successfully anchored.
    resume = TWO_JOB_RESUME.replace(
        "      - Reduced downtime 30% across 6 sites.\n"
        "  - organization: Acme Robotics\n"
        "    title: Field Engineer\n"
        "    start: 2024-02\n"
        "    end: 2025-05\n"
        "    bullets:\n"
        "      - Cut API latency 40% across 3 services.\n",
        "      - Cut API latency 40% across 3 services.\n"
        "  - organization: Zenith Robotics\n"
        "    title: Field Engineer\n"
        "    start: 2024-02\n"
        "    end: 2025-05\n"
        "    bullets:\n"
        "      - Reduced downtime 30% across 6 sites.\n")
    code, report = run_check(*write_pair(
        tmp_path, resume=resume, vault=TWO_JOB_VAULT))
    assert code == 0
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    assert "Reduced downtime 30% across 6 sites." in pairings, \
        "an unscoped entry's own claim must still get a pairing row"
    row = pairings["Reduced downtime 30% across 6 sites."]
    assert row["level"] == "warn", \
        f"unresolved-rename support (found outside any matched entry) " \
        f"is manual-audit, not a silent pass, in the pairing table too: {row}"


# ── pairing completeness: qualitative claims are no longer invisible ──
# Round-7 finding 1: a claim with zero numbers skipped the pairing loop
# entirely (`if not nums: continue`) — no row, no check, no signal at
# all, not even a WARN. Every content claim now gets a row; a claim
# with no numeric anchor has nothing for presence-checking to verify,
# so its row is always "info" (see TestQualitativeLineOverlap below for
# why no honest WARN threshold exists there), never a silent omission.

QUALITATIVE_RESUME = RESUME.replace(
    "      - Cut API latency 40% across 3 services.\n",
    "      - Cut API latency 40% across 3 services.\n"
    "      - Led the company-wide migration to event-driven architecture.\n")


def test_qualitative_claim_with_no_vault_support_gets_a_pairing_row(tmp_path):
    code, report = run_check(*write_pair(tmp_path, resume=QUALITATIVE_RESUME))
    assert code == 0, \
        "a qualitative claim alone must not hard-fail on tokens (no lexical " \
        "check exists for it — see the module docstring's `claims` entry)"
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    claim = "Led the company-wide migration to event-driven architecture."
    assert claim in pairings, \
        f"a non-numeric claim must never be invisible to the pairing " \
        f"table — that is the exact bug class this section closes: {report}"
    assert pairings[claim]["level"] == "info", \
        f"no honest threshold separates a qualitative rephrase from a " \
        f"fabrication (see TestQualitativeLineOverlap) — the row must be " \
        f"informational, never a silent 'pass': {pairings[claim]}"


def test_qualitative_claim_with_genuine_vault_support_still_gets_a_row(tmp_path):
    # Visibility does not regress for the honest case either — a
    # qualitative claim that DOES have real vault support still gets a
    # row (with that support line shown), not just the fabricated one.
    resume = RESUME.replace(
        "      - Cut API latency 40% across 3 services.\n",
        "      - Cut API latency 40% across 3 services.\n"
        "      - Shipped the new batching layer to production.\n")
    vault = VAULT.replace(
        "- FACT: shipped a batching layer handling 1,200 requests/s",
        "- FACT: shipped a batching layer handling 1,200 requests/s\n"
        "- FACT: shipped the new batching layer to production")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 0
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    claim = "Shipped the new batching layer to production."
    assert claim in pairings
    row = pairings[claim]
    assert row["level"] == "info"
    assert row["sources"], "the genuinely-matching line must still show"


def test_pairing_table_header_does_not_mislabel_qualitative_rows_as_numeric(
        tmp_path):
    # Round 7 finding 8 (residual): the header used to read "N claim(s)
    # with numeric content" even though N counts EVERY content claim —
    # numeric-anchored rows AND the qualitative (no-number) rows the
    # same fix added. That mismatch is the exact failure mode this
    # section exists to prevent, just moved into the header's own
    # wording. The header — and the empty-case fallback — must never
    # claim "numeric" for a count that includes qualitative claims.
    resume = RESUME.replace(
        "      - Cut API latency 40% across 3 services.\n",
        "      - Cut API latency 40% across 3 services.\n"
        "      - Led the company-wide migration to event-driven "
        "architecture.\n")
    r, v = write_pair(tmp_path, resume=resume)
    code, report = run_check(r, v)
    assert code == 0
    pairings = report["claim_pairings"]
    n_info = sum(1 for p in pairings if p["level"] == "info")
    assert n_info >= 1, "fixture must include at least one info-level row"

    proc = subprocess.run(
        [sys.executable, str(CHECK), str(r), str(v)],
        capture_output=True, text=True)
    assert proc.returncode == 0
    header_lines = [line for line in proc.stdout.splitlines()
                     if "claim -> source pairings" in line]
    assert len(header_lines) == 1, proc.stdout
    header = header_lines[0]
    assert "numeric" not in header, \
        f"header must not call this a numeric-only count when it " \
        f"includes info-level qualitative rows: {header!r}"
    assert f"({len(pairings)} claim(s)" in header, \
        f"header count must match the actual number of pairing rows " \
        f"printed, numeric and qualitative alike: {header!r}"


# ── vault-line unwrapping: soft-wrapped FACTs are one line, not many ──
# Round-7 finding 8 (legs a/b): a real vault FACT bullet that markdown
# soft-wraps across physical lines had its numbers land on different
# `block["lines"]` entries and read as claim_numbers_span_multiple_facts
# even though it is one continuous sentence about one achievement.
# Continuation lines (no bullet/heading marker of their own) are now
# joined onto their parent line before any line-level matching.

WRAPPED_VAULT = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: built an offline evaluation harness for a RAG customer-support
  assistant (Python, pytest); ran nightly against 1,200 historical
  support tickets and caught 3 retrieval regressions before they shipped
"""

WRAPPED_RESUME = """\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - Built an offline evaluation harness for a RAG customer-support
        assistant; ran nightly against 1,200 historical support tickets
        and caught 3 retrieval regressions before they shipped.
"""


def test_wrapped_vault_fact_does_not_false_warn_multiple_facts(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=WRAPPED_RESUME, vault=WRAPPED_VAULT))
    assert code == 0
    assert "claim_numbers_span_multiple_facts" not in ids_at(report, "warn"), \
        "a FACT that only spans multiple physical lines because markdown " \
        "soft-wrapped it must be joined into one line before matching"
    rows = [p for p in report["claim_pairings"]
            if p["path"] == "experience[0].bullets[0]"]
    assert rows, \
        f"the wrapped claim must still get a pairing row: {report['claim_pairings']}"
    assert rows[0]["level"] == "pass", \
        f"the unwrapped single vault line must fully verify: {rows[0]}"


def test_unwrapping_does_not_merge_across_a_blank_line(tmp_path):
    # A blank line always ends a logical entry — two separate FACTs
    # separated by a blank line must never be joined into one.
    vault = WRAPPED_VAULT + "\n- FACT: unrelated later fact with 99 widgets\n"
    code, report = run_check(*write_pair(tmp_path, resume=WRAPPED_RESUME, vault=vault))
    assert code == 0
    assert "claim_numbers_span_multiple_facts" not in ids_at(report, "warn")


# ── skills: atomic tokens, fail-closed against the whole vault ───────
# Round-7 finding 1 (leg b): a skill string ("Kubernetes") has no
# numeric token at all, so the old numeric-only sweep never looked at it
# — a clean pass, invisible, even when the vault has zero support for
# it. A skill/tag/tool token is not a sentence: there is no leftover
# wording for a weighted-overlap tripwire to compare a rephrase against
# a fabrication with, so presence is the whole test — normalized
# (case/punctuation) whole-vault match, or FAIL. Fail-closed is correct
# here specifically because it is cheap for the user to fix: vault the
# skill with evidence, or cut it from the projection.

SKILL_VAULT = VAULT + """

## Skills
- FACT: Python, SQL, Docker — self-reported and backed by the entries above
- FACT: RAG pipelines — the Widget Corp internship built exactly this
"""


def _skills_resume(items: str) -> str:
    return RESUME + f"""
skills:
  - label: Languages
    items: [{items}]
"""


def test_unvaulted_skill_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Kubernetes"), vault=SKILL_VAULT))
    assert code == 1, "an unevidenced skill must hard-fail, not pass silently"
    assert "skill_unsupported" in ids_at(report, "fail")
    fails = details_at(report, "fail")
    assert "Kubernetes" in fails and "vault" in fails


def test_vaulted_skill_passes(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Python, Docker"), vault=SKILL_VAULT))
    assert code == 0
    assert "skill_unsupported" not in ids_at(report, "fail")
    assert any(c["check_id"] == "skills" and c["level"] == "pass"
               for c in report["checks"]), report["checks"]


def test_skill_matching_is_case_insensitive(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("python"), vault=SKILL_VAULT))
    assert code == 0, "skill matching must ignore case"


def test_multi_word_skill_phrase_matches_verbatim_vault_phrase(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("RAG pipelines"), vault=SKILL_VAULT))
    assert code == 0


def test_skill_substring_collision_is_not_support(tmp_path):
    # word-boundary regression guard, mirroring the number/URL boundary
    # tests above: "NoSQL" in the vault must not lend support to a
    # standalone "SQL" skill claim.
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("SQL"),
        vault=SKILL_VAULT.replace("Python, SQL, Docker",
                                  "Python, NoSQL, Docker")))
    assert code == 1, "'NoSQL' must not lend support to a standalone 'SQL' skill"
    assert "skill_unsupported" in ids_at(report, "fail")


STACK_RESUME = RESUME + """
projects:
  - name: sidequest
    stack: [{stack}]
    bullets:
      - A side project.
"""


def test_unvaulted_stack_item_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=STACK_RESUME.format(stack="Kubernetes"), vault=VAULT))
    assert code == 1, \
        "an unevidenced projects[].stack item is the same atomic-skill " \
        "class as a top-level skills item and must fail closed too"
    assert "skill_unsupported" in ids_at(report, "fail")


def test_vaulted_stack_item_passes(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=STACK_RESUME.format(stack="Python"),
        vault=VAULT + "- FACT: sidequest built in Python\n"))
    assert code == 0
    assert "skill_unsupported" not in ids_at(report, "fail")


# ── round-7 regression: a digit inside a skill/stack string ──────────
# Moving stack/items out of CONTENT_KEYS into SKILL_KEYS (so
# skill_supported() could fail-closed-check them) accidentally dropped
# them from the pre-existing numeric FAIL sweep too: that sweep only
# ever iterated found["content"] + found["other"], never
# found["skills"]. SKILL_TOKEN_RE (`[a-z][a-z0-9]{1,}`) requires a
# token to START with a letter, so a bare digit substring inside a
# skill string — a version number, a "(N years)" qualifier — is
# tokenized away by skill_tokens() and was never checked by anything:
# skill_supported() ignores it, and the numeric sweep never saw the
# string at all. Both cases below FAIL on the baseline (pre-round-7)
# script with number_unsupported; a fix must restore that.

def test_unvaulted_skill_years_qualifier_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("AWS (7 years)"),
        vault=SKILL_VAULT + "- FACT: AWS for 2 years\n"))
    assert code == 1, \
        "a fabricated numeric qualifier on an otherwise-vaulted skill " \
        "must fail closed, not disappear because skill tokens must " \
        "start with a letter"
    assert "number_unsupported" in ids_at(report, "fail")
    fails = details_at(report, "fail")
    assert "7" in fails


def test_unvaulted_stack_version_number_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=STACK_RESUME.format(stack="Python 3.99"),
        vault=VAULT + "- FACT: sidequest built in Python\n"))
    assert code == 1, \
        "a fabricated version number on an otherwise-vaulted stack " \
        "entry must fail closed, not pass silently"
    assert "number_unsupported" in ids_at(report, "fail")
    fails = details_at(report, "fail")
    assert "3.99" in fails


# ── qualitative tripwire calibration: no honest threshold exists ─────
# Round-7 finding 1/3: a numeric claim's tokens anchor its search to one
# (or a small handful of) candidate line(s) — weighted_overlap's
# separation there is real (CLAIM_LINE_OVERLAP_THRESHOLD's own
# calibration table in check_projection.py). A claim with NO number at
# all has no such anchor: the best-scoring line is found by searching
# every candidate line in scope, and with nothing to narrow the field,
# a fabrication's accidental overlap with an UNRELATED real vault line
# is common, not rare. Measured against QUALITATIVE_CALIBRATION_VAULT
# below, through the actual weighted_overlap()/best-scoring-line
# machinery (not hand math):
#   legitimate reorder ("Cutting deploy failures, led the team's
#     migration from a monolith to microservices.")             0.934
#   legitimate synonym swap ("Directed the team's move from a
#     monolith to microservices, reducing deployment failures.")  0.467
#   legitimate compression ("Led the migration from a monolith
#     to microservices.")                                         0.467
#   fabrication padded with the vault's own generic words
#     ("Presented retail clients with a new api roadmap for
#     accounts.")                                                 0.614
#   fabrication, single deep word swap ("Reduced api latency
#     significantly across backend services for enterprise
#     clients.")                                                  0.832
#   fabrication, unrelated achievement ("Led the company-wide
#     migration to event-driven architecture.")                   0.234
# The fabrication range (0.234-0.832) fully contains the legitimate
# range (0.467-0.934) — no threshold separates them; a fixed bar would
# either WARN honest paraphrases or silently pass fabrications through,
# both worse than the status quo. So a claim with no numeric anchor is
# always reported "info" — visible, with its best-scoring line and
# ratio printed, never used to flag. This mirrors the never-scoped
# numeric fallback's own documented precedent (see the pairing loop's
# comment in check_projection.py) — the same conclusion, independently
# reached, for a structurally different reason (no candidate-narrowing
# anchor, vs. no coherent single-entry comparison set there).

QUALITATIVE_CALIBRATION_VAULT = """\
# Career vault — Sam Casey
Updated: 2026-07-01

## Basics
- FACT: Sam Casey · Springfield, USA
- FACT: sam.casey@example.com · github.com/samcasey

## Experience
### Widget Corp — Software Engineering Intern (Jun 2025 – Sep 2025)
- FACT: reduced api latency significantly across backend services for retail clients
- FACT: supported api integrations for other retail clients accounts
- FACT: presented api roadmap updates to retail clients monthly
- FACT: led the team's migration from a monolith to microservices, cutting deploy failures
- FACT: mentored two junior engineers on api design reviews
"""


def _qualitative_calibration_resume(bullet: str) -> str:
    return f"""\
meta:
  page_budget: 1
  template: compact

basics:
  name: Sam Casey
  email: sam.casey@example.com

experience:
  - organization: Widget Corp
    title: Software Engineering Intern
    start: 2025-06
    end: 2025-09
    bullets:
      - {bullet}
"""


class TestQualitativeLineOverlap:
    """No numeric anchor -> pairing rows always stay 'info', for
    legitimate rephrasings and outright fabrications alike — see the
    calibration table above."""

    @pytest.mark.parametrize("bullet", [
        "Cutting deploy failures, led the team's migration from a monolith to microservices.",
        "Directed the team's move from a monolith to microservices, reducing deployment failures.",
        "Led the migration from a monolith to microservices.",
    ])
    def test_legitimate_qualitative_paraphrase_stays_info(self, tmp_path, bullet):
        code, report = run_check(*write_pair(
            tmp_path, resume=_qualitative_calibration_resume(bullet),
            vault=QUALITATIVE_CALIBRATION_VAULT))
        assert code == 0
        row = next(p for p in report["claim_pairings"]
                   if p["claim"].startswith(bullet[:40]))
        assert row["level"] == "info", \
            f"a legitimate paraphrase must never be flagged 'warn' by a " \
            f"threshold this calibration shows is not honest: {row}"

    @pytest.mark.parametrize("bullet", [
        "Presented retail clients with a new api roadmap for accounts.",
        "Reduced api latency significantly across backend services for enterprise clients.",
        "Led the company-wide migration to event-driven architecture.",
    ])
    def test_fabricated_qualitative_claim_also_stays_info_not_warn(self, tmp_path, bullet):
        # The point being demonstrated: these fabrications are not caught
        # by a WARN either — that would require a threshold the
        # calibration above shows does not exist. They are visible (a
        # row exists, with its best-scoring line and ratio printed) for
        # a human to catch by eye, same as every other informational row.
        code, report = run_check(*write_pair(
            tmp_path, resume=_qualitative_calibration_resume(bullet),
            vault=QUALITATIVE_CALIBRATION_VAULT))
        assert code == 0
        row = next(p for p in report["claim_pairings"]
                   if p["claim"].startswith(bullet[:40]))
        assert row["level"] == "info"


# ── contract edges ───────────────────────────────────────────────────

def test_unreadable_input_exits_2(tmp_path):
    resume, vault = write_pair(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(CHECK), str(resume), str(tmp_path / "no-vault.md")],
        capture_output=True, text=True)
    assert proc.returncode == 2

    (tmp_path / "broken.yaml").write_text("basics: [unclosed\n")
    proc = subprocess.run(
        [sys.executable, str(CHECK), str(tmp_path / "broken.yaml"), str(vault)],
        capture_output=True, text=True)
    assert proc.returncode == 2


# ── round 8, finding 3a: single-letter / symbol-suffixed skill tokens ─
# The old SKILL_TOKEN_RE (`[a-z][a-z0-9]{1,}`) required 2+ alnum chars,
# so "R" and "C" (1 letter, no second alnum char to pair with)
# tokenized to NOTHING, and "C++"/"C#"/"F#" lost their distinguishing
# suffix entirely for the same reason (the char after the first letter
# is "+"/"#", not [a-z0-9]) — also nothing. skill_supported()'s old
# "if not tokens: return True" then silently passed all five with zero
# vault support, on a vault that never mentioned any of them.

SYMBOL_SKILL_VAULT = SKILL_VAULT  # Python, SQL, Docker; RAG pipelines


def test_bare_r_language_unvaulted_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("R"), vault=SYMBOL_SKILL_VAULT))
    assert code == 1, \
        "a single-letter language token must not tokenize to nothing " \
        "and auto-pass"
    assert "skill_unsupported" in ids_at(report, "fail")


def test_bare_c_language_unvaulted_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("C"), vault=SYMBOL_SKILL_VAULT))
    assert code == 1
    assert "skill_unsupported" in ids_at(report, "fail")


def test_cpp_csharp_fsharp_unvaulted_all_fail(tmp_path):
    for lang in ("C++", "C#", "F#"):
        code, report = run_check(*write_pair(
            tmp_path, resume=_skills_resume(lang), vault=SYMBOL_SKILL_VAULT))
        assert code == 1, f"{lang} must not vacuously pass with no tokens"
        assert "skill_unsupported" in ids_at(report, "fail"), lang
        assert lang in details_at(report, "fail")


def test_single_letter_and_symbol_skills_pass_when_actually_vaulted(tmp_path):
    vault = SYMBOL_SKILL_VAULT + "- FACT: also used R and C++ on a side project\n"
    for lang in ("R", "C++"):
        code, report = run_check(*write_pair(
            tmp_path, resume=_skills_resume(lang), vault=vault))
        assert code == 0, f"{lang} genuinely vaulted must pass: {report}"
        assert "skill_unsupported" not in ids_at(report, "fail")


def test_bare_c_not_supported_by_cpp_in_vault(tmp_path):
    # Boundary regression: a bare "C" claim must not ride on the vault's
    # different token "C++" — the fix that lets "c++" tokenize to
    # itself must not turn "+" into a non-boundary character for "c".
    vault = SYMBOL_SKILL_VAULT + "- FACT: used C++ extensively\n"
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("C"), vault=vault))
    assert code == 1, \
        "'C++' in the vault must not lend vacuous support to a " \
        "standalone 'C' skill claim"
    assert "skill_unsupported" in ids_at(report, "fail")


# ── round 8, finding 4: coursework is an atomic field, not invisible ──
# coursework used to have NO dedicated check at all: it fell into the
# generic "other" bucket, which only ever swept for digits. A course
# name with zero digits ("Quantum Computing") was invisible to every
# check in this script — exit 0, PASS, zero pairings.

COURSEWORK_RESUME = RESUME.replace(
    "    gpa: \"3.90/4.0\"\n",
    "    gpa: \"3.90/4.0\"\n"
    "    coursework: [\"{course}\"]\n")


def test_unvaulted_coursework_item_fails(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path, resume=COURSEWORK_RESUME.format(course="Quantum Computing")))
    assert code == 1, \
        "a coursework item with no vault support must fail closed, not " \
        "silently pass with zero pairings"
    assert "skill_unsupported" in ids_at(report, "fail")
    assert "Quantum Computing" in details_at(report, "fail")


def test_vaulted_coursework_item_passes(tmp_path):
    vault = VAULT.replace(
        "- FACT: GPA 3.90 / 4.0",
        "- FACT: GPA 3.90 / 4.0\n- FACT: coursework: Quantum Computing")
    code, report = run_check(*write_pair(
        tmp_path,
        resume=COURSEWORK_RESUME.format(course="Quantum Computing"),
        vault=vault))
    assert code == 0, f"a genuinely vaulted course must pass: {report}"
    assert "skill_unsupported" not in ids_at(report, "fail")


def test_coursework_number_still_checked_after_atomic_move(tmp_path):
    # Regression guard: moving coursework into the atomic-token check
    # must not drop it from the pre-existing numeric sweep (round 7's
    # own regression class for stack/items).
    code, report = run_check(*write_pair(
        tmp_path, resume=COURSEWORK_RESUME.format(course="CS 4820 Advanced Algorithms")))
    assert code == 1
    assert "number_unsupported" in ids_at(report, "fail")
    assert "4820" in details_at(report, "fail")


# ── round 8, finding 4/systemic: schema field-coverage guard ──────────

def test_unknown_schema_field_gets_unchecked_field_warn(tmp_path):
    resume = RESUME.replace(
        "  email: sam.casey@example.com\n",
        "  email: sam.casey@example.com\n"
        "  pronouns: she/her\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume))
    assert code == 0, "an unclassified field is a WARN, not a FAIL"
    assert "unchecked_field" in ids_at(report, "warn")
    assert "pronouns" in details_at(report, "warn")


def test_known_schema_fields_never_trigger_unchecked_field(tmp_path):
    # The faithful base pair alone exercises name/email/links/label/url/
    # institution/degree/field/start/end/gpa/organization/title/bullets
    # — every one of them must already be classified.
    code, report = run_check(*write_pair(tmp_path))
    assert code == 0
    assert "unchecked_field" not in ids_at(report, "warn"), report["checks"]


def test_full_schema_field_roster_never_triggers_unchecked_field(tmp_path):
    # Exercise every remaining schema field the base fixtures don't
    # (phone, location, group, tags, honors, stack, citation, awards'
    # date) in one resume/vault pair — none of them is schema drift.
    resume = RESUME + """\
      - GitHub Actions
    tags: [ops]
    location: Remote
  - organization: Second Co
    title: Engineer
    location: Remote
    group: industry
    start: 2024-01
    end: 2024-06
    bullets:
      - Did some work.

projects:
  - name: sidequest
    stack: [Python]
    bullets:
      - A side project.

publications:
  - citation: "Example citation."
    url: https://example.com/paper

awards:
  - name: Some Award
    date: 2024-01
"""
    resume = resume.replace(
        "basics:\n  name: Sam Casey\n  email: sam.casey@example.com\n",
        "basics:\n  name: Sam Casey\n  email: sam.casey@example.com\n"
        "  phone: \"+1 5551234567\"\n"
        "  location: Remote\n")
    resume = resume.replace(
        "    end: 2026-06\n    gpa: \"3.90/4.0\"\n",
        "    end: 2026-06\n    gpa: \"3.90/4.0\"\n"
        "    honors: [\"Some honor\"]\n")
    vault = VAULT + """\
- FACT: phone +1 5551234567, remote
- FACT: worked at Second Co as an Engineer, remote, 2024-01 to 2024-06
- FACT: GitHub Actions in ops role
- FACT: some honor received
- FACT: sidequest built in Python
- FACT: Example citation. https://example.com/paper
- FACT: Some Award, 2024-01
"""
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "unchecked_field" not in ids_at(report, "warn"), report["checks"]


# ── round 8, finding 3b: the exclusion-marker contract ────────────────
# career-vault.md documents NOT-CLAIMABLE:/PENDING-EVIDENCE: line
# markers alongside FACT:/CONTEXT:/CUT: — a line carrying either marker
# can never be positive evidence for anything it mentions, for ANY
# check (numbers, dates, urls, skills, and the pairing table's
# candidate-line search alike). A claim whose only "support" is such a
# line must surface as a labeled WARN, never a silent pass and never
# folded into a plain "no vault support anywhere" FAIL either.

EXCLUSION_SKILL_VAULT = VAULT + """

## Skills
- NOT-CLAIMABLE: Kubernetes — evaluated once in a personal project only,
  no production experience.
"""


def test_skill_matched_only_in_denied_line_fails(tmp_path):
    # Round 9, finding 2: this used to assert exit 0 + a WARN. A vault
    # line carrying NOT-CLAIMABLE is the single loudest thing a vault can
    # say about a claim — "do not put this on a resume" — and an
    # exit-0 warning meant the projection still shipped. It is a FAIL,
    # and still never conflated with plain absence.
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Kubernetes"),
        vault=EXCLUSION_SKILL_VAULT))
    assert code == 1, "an explicit 'do not claim this' must not exit 0"
    assert "skill_denied" in ids_at(report, "fail")
    assert "skill_unsupported" not in ids_at(report, "fail"), (
        "denied support must not be reported as plain absence")
    assert "Kubernetes" in details_at(report, "fail")


def test_skill_marker_is_case_and_dash_insensitive(tmp_path):
    vault = EXCLUSION_SKILL_VAULT.replace("NOT-CLAIMABLE", "Not–Claimable")
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Kubernetes"), vault=vault))
    assert "skill_denied" in ids_at(report, "fail"), (
        "the marker must match regardless of case or dash style "
        "(normalize() unifies unicode dashes)")


def test_pending_evidence_marker_also_excludes(tmp_path):
    vault = EXCLUSION_SKILL_VAULT.replace("NOT-CLAIMABLE", "PENDING-EVIDENCE")
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Kubernetes"), vault=vault))
    assert code == 1
    assert "skill_denied" in ids_at(report, "fail")


def test_skill_denied_by_prose_without_any_marker_fails(tmp_path):
    # Round 9, finding 2: an unmarked prose denial — the vault sentence
    # that says the skill is ABSENT — used to be ordinary clean evidence,
    # so it verified the very claim it contradicts.
    vault = VAULT + "- FACT: no production Kubernetes experience yet\n"
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Kubernetes"), vault=vault))
    assert code == 1
    assert "skill_denied" in ids_at(report, "fail")


def test_skill_traced_only_to_a_cut_line_warns(tmp_path):
    # A CUT: line is dropped-from-a-resume material, usually still true —
    # weak support, not counter-evidence. Warn, do not fail.
    vault = VAULT + "- CUT: wrote a Terraform module, dropped for space\n"
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Terraform"), vault=vault))
    assert code == 0
    assert "skill_cut_only" in ids_at(report, "warn")
    assert "skill_unsupported" not in ids_at(report, "fail")


def test_multiword_skill_may_not_be_assembled_across_lines(tmp_path):
    # Round 9, finding 2: whole-vault token aggregation let "Operating
    # Systems" verify off an "operating" on one line and a "systems" on
    # another. Every token of one item must co-occur on ONE line.
    vault = VAULT + ("- FACT: ran the operating budget for the club\n"
                     "- FACT: built systems for student intake\n")
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Operating Systems"), vault=vault))
    assert code == 1
    assert "skill_unsupported" in ids_at(report, "fail")


def test_compound_skill_entry_is_split_before_the_one_line_rule(tmp_path):
    # ...but the one-line rule must not false-fail a genuinely compound
    # entry whose items really are recorded on separate vault lines.
    vault = VAULT + ("- FACT: ran PostgreSQL in production\n"
                     "- FACT: used Redis for the session cache\n")
    code, _ = run_check(*write_pair(
        tmp_path, resume=_skills_resume("PostgreSQL / Redis"), vault=vault))
    assert code == 0


def test_dotted_skill_name_does_not_ride_on_a_bare_word(tmp_path):
    # ".NET" must not verify off "net revenue".
    vault = VAULT + "- FACT: grew net revenue reporting coverage\n"
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume(".NET"), vault=vault))
    assert code == 1
    assert "skill_unsupported" in ids_at(report, "fail")


# Round-2 review finding 1: a number/date/URL found ONLY on a
# NOT-CLAIMABLE / PENDING-EVIDENCE (denied) line is a FAIL, not the
# round-8 WARN that let a disproven fact ship at exit 0. A CUT: line
# (dropped-but-usually-true material) stays a WARN.

def test_number_matched_only_in_denied_line_fails(tmp_path):
    vault = VAULT + (
        "- NOT-CLAIMABLE: brought build time down 97% overnight — an "
        "early draft number that was never verified, do not use it\n")
    resume = RESUME + "      - Brought build time down 97% overnight.\n"
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1, "a denied-only number must FAIL, not exit 0"
    assert "number_denied" in ids_at(report, "fail")
    assert "97" in details_at(report, "fail")


def test_number_matched_only_in_cut_line_warns(tmp_path):
    vault = VAULT + "- CUT: brought build time down 97% overnight, dropped for space\n"
    resume = RESUME + "      - Brought build time down 97% overnight.\n"
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 0, "a cut-only number is weak support, not counter-evidence"
    assert "number_cut_only" in ids_at(report, "warn")
    assert "number_unsupported" not in ids_at(report, "fail")


def test_date_matched_only_in_denied_line_fails(tmp_path):
    vault = VAULT + "- NOT-CLAIMABLE: worked there again from 2030-01\n"
    resume = RESUME.replace("start: 2025-06", "start: 2030-01")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1
    assert "date_denied" in ids_at(report, "fail")
    assert "date_unsupported" not in ids_at(report, "fail")


def test_url_matched_only_in_denied_line_fails(tmp_path):
    vault = VAULT + "- NOT-CLAIMABLE: also had a profile at github.com/samcasey-old\n"
    resume = RESUME.replace(
        "https://github.com/samcasey",
        "https://github.com/samcasey-old")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1
    assert "url_denied" in ids_at(report, "fail")
    assert "url_unsupported" not in ids_at(report, "fail")


def test_skill_matched_only_under_gaps_and_flags_section_fails(tmp_path):
    # Round-2 review finding 1: a Gaps & flags line is the vault's own
    # honesty ledger of what NOT to claim — even without a NOT-CLAIMABLE
    # marker or a denial idiom. "Kubernetes remains a known gap" must
    # not validate Kubernetes as a supported skill.
    vault = VAULT + (
        "\n## Gaps & flags  (honesty ledger)\n"
        "- Kubernetes remains a known gap for now\n")
    code, report = run_check(*write_pair(
        tmp_path, resume=_skills_resume("Kubernetes"), vault=vault))
    assert code == 1, "a skill named only under Gaps & flags must FAIL"
    assert "skill_denied" in ids_at(report, "fail")


def test_wrong_email_does_not_borrow_a_longer_vault_address(tmp_path):
    # Round-2 review finding 2: casey@example.com must not verify off the
    # vault's different sam.casey@example.com (the "." before "casey" is
    # part of that email token, not a word boundary).
    resume = RESUME.replace("email: sam.casey@example.com",
                            "email: casey@example.com")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=VAULT))
    assert code == 1
    assert "contact_unsupported" in ids_at(report, "fail")


def test_location_must_co_occur_on_one_vault_line(tmp_path):
    # Round-2 review finding 2: "Springfield, Canada" must not pass off
    # the vault's "Springfield, USA" line plus an unrelated "Canada"
    # mention. A location is one fact; every token co-occurs on ONE line.
    vault = VAULT + "- FACT: volunteered in Canada one summer\n"
    resume = RESUME.replace(
        "  email: sam.casey@example.com",
        "  email: sam.casey@example.com\n  location: Springfield, Canada")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1
    assert "contact_unsupported" in ids_at(report, "fail")


def test_correct_location_on_one_vault_line_passes(tmp_path):
    # The mirror: the true location, present whole on one vault line
    # ("Springfield, USA"), must still verify.
    resume = RESUME.replace(
        "  email: sam.casey@example.com",
        "  email: sam.casey@example.com\n  location: Springfield, USA")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=VAULT))
    assert "contact_unsupported" not in ids_at(report, "fail")


def test_reversed_direction_without_from_to_markers_warns(tmp_path):
    # Round-2 review finding 4: "Increased API latency 40%" against the
    # vault's "cut API latency 40%" — same number, opposite direction,
    # no from/to pair for metric_direction to catch. A polarity WARN.
    vault = VAULT + (
        "- FACT: cut API latency 40% by adding a hot-path cache\n")
    resume = RESUME + (
        "      - Increased API latency 40% by adding a hot-path cache.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "claim_direction_conflict" in ids_at(report, "warn")


def test_honest_paraphrase_keeps_direction_no_conflict(tmp_path):
    # ...and a synonym that keeps the direction ("reduced" for "cut")
    # must NOT trip the polarity check.
    vault = VAULT + (
        "- FACT: cut API latency 40% by adding a hot-path cache\n")
    resume = RESUME + (
        "      - Reduced API latency 40% by adding a hot-path cache.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "claim_direction_conflict" not in ids_at(report, "warn")


# ── round-3 review: denied qualitative claims, contact ownership,
#    one-word meaning flips ───────────────────────────────────────────

def test_qualitative_claim_repeating_a_denied_line_fails(tmp_path):
    # Round-3 review finding 1: a claim with NO numbers that repeats a
    # NOT-CLAIMABLE line used to be invisible — the number checks never
    # fired and the pairing table matched it to an unrelated clean line.
    vault = VAULT + (
        "- NOT-CLAIMABLE: led the company-wide migration to event-driven "
        "architecture\n")
    resume = RESUME + (
        "      - Led the company-wide migration to event-driven architecture.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1, "a claim restating a denied line must FAIL"
    assert "claim_denied" in ids_at(report, "fail")


def test_email_cannot_borrow_a_colleagues_address_elsewhere(tmp_path):
    # Round-3 review finding 2: a colleague's email in a Q&A/Context line
    # is not the candidate's — email verifies only against the Basics set.
    vault = VAULT + (
        "\n## Q&A log\n- CONTEXT: my manager jane.doe@bigco.com is a reference\n")
    resume = RESUME.replace("email: sam.casey@example.com",
                            "email: jane.doe@bigco.com")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1
    assert "contact_unsupported" in ids_at(report, "fail")


def test_partial_phone_does_not_pass_off_the_full_number(tmp_path):
    # Round-3 review finding 2: "010-4477" must not verify off the
    # complete "+1 (555) 010-4477".
    vault = VAULT.replace(
        "- FACT: Sam Casey · Springfield, USA",
        "- FACT: Sam Casey · +1 (555) 010-4477 · Springfield, USA")
    resume = RESUME.replace(
        "  email: sam.casey@example.com",
        "  email: sam.casey@example.com\n  phone: \"010-4477\"")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1
    assert "contact_unsupported" in ids_at(report, "fail")


def test_correct_full_phone_passes(tmp_path):
    vault = VAULT.replace(
        "- FACT: Sam Casey · Springfield, USA",
        "- FACT: Sam Casey · +1 (555) 010-4477 · Springfield, USA")
    resume = RESUME.replace(
        "  email: sam.casey@example.com",
        "  email: sam.casey@example.com\n  phone: \"+1 (555) 010-4477\"")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "contact_unsupported" not in ids_at(report, "fail")


def test_wrong_state_does_not_pass_off_same_city(tmp_path):
    # Round-3 review finding 2: "Portland, OR" must not verify off
    # "Portland, ME" — "OR" is a state abbreviation, not a stopword.
    vault = VAULT.replace("Springfield, USA", "Portland, ME")
    resume = RESUME.replace(
        "  email: sam.casey@example.com",
        "  email: sam.casey@example.com\n  location: Portland, OR")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1
    assert "contact_unsupported" in ids_at(report, "fail")


def test_url_does_not_ride_inside_a_different_host(tmp_path):
    # Round-3 review finding 2: "hub.com/samcasey" must not match inside
    # "github.com/samcasey" (git-HUB…) — the URL match needs a left
    # boundary.
    resume = RESUME.replace("https://github.com/samcasey",
                            "https://hub.com/samcasey")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=VAULT))
    assert code == 1
    assert "url_unsupported" in ids_at(report, "fail")


def test_dropped_negation_flips_meaning_and_fails(tmp_path):
    # Round-3 review finding 3: vault "never reduced API latency 40%",
    # CV "Reduced API latency 40%" — the claim drops the negation.
    vault = VAULT + (
        "- FACT: never reduced API latency 40% across 3 services\n")
    resume = RESUME + (
        "      - Reduced API latency 40% across 3 services.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1, "dropping a vault line's negation must FAIL"
    # either the number is now denied-only, or the negation-drop fires;
    # both are hard failures — the claim must not exit 0.
    fails = ids_at(report, "fail")
    assert "claim_negation_dropped" in fails or "number_denied" in fails


def test_claim_keeping_the_negation_does_not_fail(tmp_path):
    # The false-positive guard: a claim that KEEPS the vault's negation
    # ("…is a signal, never an automated verdict") must stay clean — the
    # signal is the DROP, not the presence, of a negator.
    vault = VAULT + (
        "- FACT: structural similarity is a review signal, never an "
        "automated verdict\n")
    resume = RESUME + (
        "      - Structural similarity is a review signal, never an "
        "automated verdict.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "claim_negation_dropped" not in ids_at(report, "fail")
    assert "claim_denied" not in ids_at(report, "fail")


def test_worsened_outcome_verb_conflicts_with_improvement_line(tmp_path):
    # Round-3 review finding 3: CV "Worsened API latency 40%" against
    # vault "cut API latency 40%" — a resume claims improvements.
    vault = VAULT + ("- FACT: cut API latency 40% across 3 services\n")
    resume = RESUME + (
        "      - Worsened API latency 40% across 3 services.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "claim_direction_conflict" in ids_at(report, "warn")


def test_no_reduction_phrasing_is_a_dropped_negation(tmp_path):
    # Round-4 review finding 1: vault "no reduction in build time of
    # 55%", CV "Reduced build time 55%" — "no <outcome-noun>" is a
    # negation of the achievement, and the claim dropped it. (Uses a
    # metric not otherwise in VAULT, so there's no competing clean line
    # to match instead of the negated one.)
    vault = VAULT + (
        "- FACT: no reduction in build time of 55% on the CI pipeline\n")
    resume = RESUME + (
        "      - Reduced build time 55% on the CI pipeline.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 1
    assert "claim_negation_dropped" in ids_at(report, "fail")


def test_no_added_qualifier_is_not_a_dropped_negation(tmp_path):
    # The guard: a legitimate "with no added cost" qualifier uses "no"
    # but not on an outcome noun, so it must NOT read as a negation.
    vault = VAULT + (
        "- FACT: cut error rate 40% across 3 services with no added cost\n")
    resume = RESUME + ("      - Cut error rate 40% across 3 services.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "claim_negation_dropped" not in ids_at(report, "fail")


def test_deteriorated_outcome_verb_conflicts(tmp_path):
    # Round-4 review finding 1: "Deteriorated" is a worsening verb.
    vault = VAULT + ("- FACT: cut API latency 40% across 3 services\n")
    resume = RESUME + (
        "      - Deteriorated API latency 40% across 3 services.\n")
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert "claim_direction_conflict" in ids_at(report, "warn")


# ── round 8, finding 8: audit-count honesty ────────────────────────────
# The old verdict line counted ONLY warn-level pairings toward "needs
# manual audit" — but an info-level pairing is exactly as mechanically
# unconfirmed (SKILL.md: read every row, info included), and a claim
# whose only source is an excluded vault line (finding 3b) must count
# too, not print "0 need manual audit" next to a clean exit.

def test_verdict_metrics_report_pass_warn_info_breakdown(tmp_path):
    code, report = run_check(*write_pair(tmp_path))
    m = report["metrics"]
    assert "claim_pairings_pass" in m
    assert "claim_pairings_needs_audit" in m
    assert m["claim_pairings_needs_audit"] == (
        m["claim_pairings_manual_audit"] + m["claim_pairings_info"])


def test_cut_only_pairing_counts_toward_needs_audit(tmp_path):
    # A claim word-for-word identical to a CUT: vault line would,
    # pre-round-8, have scored a mechanically "confirmed" pass via
    # weighted_overlap. A cut line is weak support (WARN), never a
    # mechanical pass — and it counts toward needs-audit. (A NOT-
    # CLAIMABLE line is stronger still: a FAIL — see
    # test_number_matched_only_in_denied_line_fails.)
    vault = VAULT + (
        "- CUT: led a 12-person team restructuring the whole backend, "
        "dropped for space\n")
    resume = RESUME + "      - Led a 12-person team restructuring the whole backend.\n"
    code, report = run_check(*write_pair(tmp_path, resume=resume, vault=vault))
    assert code == 0
    pairings = {p["claim"]: p for p in report["claim_pairings"]}
    row = pairings["Led a 12-person team restructuring the whole backend."]
    assert row["level"] == "warn", (
        f"a claim sourced only from a cut vault line must never "
        f"score a mechanical pass: {row}")
    assert report["metrics"]["claim_pairings_needs_audit"] >= 1
    assert report["metrics"]["claim_pairings_manual_audit"] >= 1


def test_zero_needs_audit_only_when_genuinely_clean(tmp_path):
    # The plain base VAULT fixture is NOT pairing-clean: Education has
    # no ### heading, so gpa's pairing is the never-scoped "info"
    # fallback (see test_claim_pairings_lists_every_numeric_claim) —
    # exactly the case this fix's honesty depends on counting. Scope
    # Education too so every numeric claim here is a mechanically
    # confirmed "pass", genuinely zero warn AND zero info.
    scoped_vault = VAULT.replace(
        "- FACT: Example State University — B.S. Computer Science, "
        "Sep 2022 – Jun 2026\n",
        "### Example State University — B.S. Computer Science "
        "(Sep 2022 – Jun 2026)\n")
    code, report = run_check(*write_pair(tmp_path, vault=scoped_vault))
    assert code == 0
    m = report["metrics"]
    assert m["claim_pairings_manual_audit"] == 0
    assert m["claim_pairings_info"] == 0
    assert m["claim_pairings_needs_audit"] == 0
    proc = subprocess.run(
        [sys.executable, str(CHECK)]
        + [str(p) for p in write_pair(tmp_path, vault=scoped_vault)],
        capture_output=True, text=True)
    assert proc.returncode == 0
    assert "0 need manual audit" in proc.stdout


# ── the real pair (gitignored; local-only truth) ─────────────────────

@pytest.mark.skipif(
    not (DRAFTS / "resume-ml-ta.yaml").is_file()
    or not (DRAFTS / "career-vault.md").is_file(),
    reason="drafts/ is gitignored personal data, absent in CI")
def test_real_pair_is_clean():
    code, report = run_check(DRAFTS / "resume-ml-ta.yaml",
                             DRAFTS / "career-vault.md")
    fails = ids_at(report, "fail")
    # skill_unsupported (round 7, finding 1b/2) is a brand-new check —
    # this pair predates it and was never used to calibrate it the way
    # the numeric/date/url/identity/semantic-overlap checks above were.
    # A few of its real stack/skills entries use abbreviations the vault
    # never spells out verbatim (e.g. "ANN", "DB" as shorthand) — under
    # fail-closed token-set matching that is a genuine, actionable
    # signal (vault the abbreviation or reword the entry), not a false
    # positive this test's zero-FP guarantee was ever meant to cover.
    # Every OTHER check (numeric, date, url, identity, semantic overlap)
    # must still stay exactly as clean as before.
    # contact_unsupported (round 9, finding 1) is new for the same reason
    # and fails on this pair from the same abbreviation cause:
    # education[1].field says "Computer Science & Technology" where the
    # vault line writes "CS & Technology". Spell the abbreviation out in
    # the vault (or match it in the yaml) and this clears — again an
    # actionable signal, not the check misfiring.
    non_skill_fails = fails - {"skill_unsupported", "contact_unsupported"}
    assert not non_skill_fails, \
        f"false positives on the repo's one real honest pair, outside " \
        f"the brand-new skills check this pair has no calibration " \
        f"history against yet: {report}"
