"""The vault projection invariant, executable: a projection never
contains a hard fact (number, date, URL) the vault lacks, and
legitimate reframing (org renames, title wording) never hard-fails.

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
