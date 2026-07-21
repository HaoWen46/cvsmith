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


# ── the known gap: tokens are checked for presence, not direction ────

@pytest.mark.xfail(
    reason="bag-of-tokens check: both numbers exist in the vault, so a "
           "reversed metric passes — token presence cannot bind numbers "
           "to direction (documented gap, see check_projection.py)",
    strict=False)
def test_reversed_metric_should_fail(tmp_path):
    code, report = run_check(*write_pair(
        tmp_path,
        resume=RESUME + "      - Brought build time 210 s -> 480 s.\n",
        vault=VAULT + "- FACT: brought build time 480 s -> 210 s\n"))
    assert code == 1, "reversed direction is a fabrication the checker misses"


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


# ── the real pair (gitignored; local-only truth) ─────────────────────

@pytest.mark.skipif(
    not (DRAFTS / "resume-ml-ta.yaml").is_file()
    or not (DRAFTS / "career-vault.md").is_file(),
    reason="drafts/ is gitignored personal data, absent in CI")
def test_real_pair_is_clean():
    code, report = run_check(DRAFTS / "resume-ml-ta.yaml",
                             DRAFTS / "career-vault.md")
    assert code == 0, \
        f"false positives on the repo's one real honest pair: {report}"
    assert report["verdict"] == "pass"
    assert not ids_at(report, "fail")
