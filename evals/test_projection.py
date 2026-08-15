"""Contract for the compact projection exposure scanner.

The scanner checks observable record values and inventories claims. It does not
decide whether prose means the same thing as a source; the evaluator agent does.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "skills/resume-builder/scripts/check_projection.py"


BASE_RESUME = """\
meta:
  target_field: ai-ml
basics:
  name: Sam Casey
  email: sam@example.com
  links:
    - label: GitHub
      url: https://github.com/sam/demo
education:
  - institution: Example University
    degree: B.S.
    field: Computer Science
    start: 2022-09
    end: 2027-12
experience:
  - organization: Meridian Labs
    title: ML Engineering Intern
    location: Seattle, WA
    start: 2025-06
    end: 2025-09
    bullets:
      - Cut p95 latency from 480 ms to 210 ms across 1,200 tickets.
skills:
  - label: Languages
    items: [Python]
"""


BASE_VAULT = """\
# Career vault — Sam Casey

## Basics
- FACT: Sam Casey · sam@example.com · https://github.com/sam/demo

## Education
### Example University — B.S. Computer Science (Sep 2022 – Dec 2027)

## Experience
### Meridian Labs — ML Engineering Intern (Jun 2025 – Sep 2025)
- FACT: Seattle, WA
- FACT: cut p95 latency from 480 ms to 210 ms across 1,200 tickets using Python
- NOT-CLAIMABLE: managed the entire ML team
- PENDING-EVIDENCE: reduced cloud cost 35%, but the report is missing
- ARCHIVED: 2018 C++ compiler project; revive for compiler or embedded targets
- OMIT-FOR: ai-ml-intern-2027 — compiler project is off-thesis for this projection
- SUPERSEDED: TensorFlow 1.x is no longer current evidence; use the newer skill fact
- CUT: legacy global exclusion retained only for old vault compatibility
"""


def run(tmp_path: Path, resume: str = BASE_RESUME, vault: str = BASE_VAULT):
    resume_path = tmp_path / "resume.yaml"
    vault_path = tmp_path / "career-vault.md"
    resume_path.write_text(resume, encoding="utf-8")
    vault_path.write_text(vault, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(resume_path), str(vault_path), "--json"],
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    return proc, payload, resume_path, vault_path


def check(payload: dict, check_id: str) -> dict:
    return next(item for item in payload["checks"] if item["check_id"] == check_id)


def test_clean_projection_passes_and_binds_both_inputs(tmp_path):
    proc, payload, resume, vault = run(tmp_path)
    assert proc.returncode == 0, proc.stderr or payload
    assert payload["layer"] == "projection"
    assert payload["result"] == "pass"
    assert payload["resume_sha256"] == hashlib.sha256(resume.read_bytes()).hexdigest()
    assert payload["vault_sha256"] == hashlib.sha256(vault.read_bytes()).hexdigest()
    assert {item["check_id"] for item in payload["checks"]} == {
        "record_values",
        "numbers",
        "urls",
        "skills",
    }


def test_every_claim_is_inventory_for_agent_review_not_scoring(tmp_path):
    _, payload, _, _ = run(tmp_path)
    assert payload["claims"]
    assert all(set(row) == {"path", "claim"} for row in payload["claims"])
    assert payload["metrics"]["claims_listed"] == len(payload["claims"])
    assert payload["scope"].startswith("Exact normalized values only")


def test_paraphrase_meaning_is_left_to_the_agent(tmp_path):
    resume = BASE_RESUME.replace(
        "- Cut p95 latency from 480 ms to 210 ms across 1,200 tickets.",
        '- "Halved tail response time for the historical support corpus: p95 480 ms to 210 ms across 1,200 tickets."',
    )
    proc, payload, _, _ = run(tmp_path, resume=resume)
    assert proc.returncode == 0, payload
    row = next(item for item in payload["claims"]
               if item["path"].endswith("bullets[0]"))
    assert row["claim"].startswith("Halved tail response")
    assert "sources" not in row


@pytest.mark.parametrize(
    ("old", "new", "check_id"),
    [
        ("1,200 tickets", "9,999 tickets", "numbers"),
        ("https://github.com/sam/demo", "https://github.com/sam/fake", "urls"),
        ("ML Engineering Intern", "Director of Machine Learning", "record_values"),
        ("items: [Python]", "items: [Kubernetes]", "skills"),
    ],
)
def test_objective_exposure_mismatch_fails(tmp_path, old, new, check_id):
    proc, payload, _, _ = run(tmp_path, resume=BASE_RESUME.replace(old, new))
    assert proc.returncode == 1
    assert payload["result"] == "fail"
    assert check(payload, check_id)["level"] == "fail"


@pytest.mark.parametrize("marker", ["NOT-CLAIMABLE", "PENDING-EVIDENCE", "ARCHIVED", "OMIT-FOR", "SUPERSEDED", "CUT"])
def test_non_active_marker_line_cannot_support_a_skill(tmp_path, marker):
    resume = BASE_RESUME.replace("items: [Python]", "items: [Rust]")
    vault = f"{BASE_VAULT}\n- {marker}: Rust\n"
    proc, payload, _, _ = run(tmp_path, resume=resume, vault=vault)
    assert proc.returncode == 1
    assert check(payload, "skills")["level"] == "fail"


def test_archived_block_headings_and_sources_cannot_support_a_projection(tmp_path):
    resume = BASE_RESUME + """\
projects:
  - name: Cold Compiler
    url: https://github.com/sam/cold-compiler
    start: 2018-01
    end: 2018-06
    bullets:
      - Built a compiler front end.
"""
    vault = BASE_VAULT + """\

## Archive
### Cold Compiler (Jan 2018 – Jun 2018)
- ARCHIVED: built a compiler front end
- SOURCE: https://github.com/sam/cold-compiler
"""
    proc, payload, _, _ = run(tmp_path, resume=resume, vault=vault)
    assert proc.returncode == 1
    assert check(payload, "record_values")["level"] == "fail"
    assert check(payload, "urls")["level"] == "fail"


def test_iso_dates_match_human_month_dates(tmp_path):
    proc, payload, _, _ = run(tmp_path)
    assert proc.returncode == 0, payload
    assert check(payload, "record_values")["level"] == "pass"


def test_every_non_active_vault_state_is_surfaced_without_a_meaning_decision(tmp_path):
    proc, payload, _, _ = run(tmp_path)
    assert proc.returncode == 0
    assert payload["risk_notes"] == [
        {"line": 13, "text": "- NOT-CLAIMABLE: managed the entire ML team"},
        {"line": 14, "text": "- PENDING-EVIDENCE: reduced cloud cost 35%, but the report is missing"},
        {"line": 15, "text": "- ARCHIVED: 2018 C++ compiler project; revive for compiler or embedded targets"},
        {"line": 16, "text": "- OMIT-FOR: ai-ml-intern-2027 — compiler project is off-thesis for this projection"},
        {"line": 17, "text": "- SUPERSEDED: TensorFlow 1.x is no longer current evidence; use the newer skill fact"},
        {"line": 18, "text": "- CUT: legacy global exclusion retained only for old vault compatibility"},
    ]


def test_malformed_yaml_is_could_not_run_with_json_contract(tmp_path):
    proc, payload, _, _ = run(tmp_path, resume="basics: [")
    assert proc.returncode == 2
    assert payload["result"] == "could-not-run"
    assert "resume" in payload["reason"]
    assert "Traceback" not in proc.stderr


def test_plain_output_names_agent_review_boundary(tmp_path):
    resume_path = tmp_path / "resume.yaml"
    vault_path = tmp_path / "career-vault.md"
    resume_path.write_text(BASE_RESUME, encoding="utf-8")
    vault_path.write_text(BASE_VAULT, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(resume_path), str(vault_path)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "review inventory" in proc.stdout.lower()


def test_scanner_stays_structurally_compact():
    lines = SCRIPT.read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 450, f"projection scanner grew to {len(lines)} lines"
