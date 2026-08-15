"""Bind the worked example to its current source, PDF, checks, and decision."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
EXAMPLE = REPO / "examples/ai-ml-intern"
PDF = EXAMPLE / "resume.pdf"
YAML = REPO / "evals/fixtures/resume-sample/resume.yaml"
VAULT = EXAMPLE / "career-vault.md"
EVIDENCE = EXAMPLE / "candidate-evidence/index.md"
EVIDENCE_DOCUMENTS = [
    EVIDENCE,
    EXAMPLE / "candidate-evidence/education-and-eligibility.md",
    EXAMPLE / "candidate-evidence/experience.md",
    EXAMPLE / "candidate-evidence/projects-research-and-awards.md",
]
LEDGER = EXAMPLE / "application-ledger.md"
JD = EXAMPLE / "jd-analysis.md"
REPORT = EXAMPLE / "eval-report.md"
PROJECTION = REPO / "skills/resume-builder/scripts/check_projection.py"
LAYERS = {
    "L0": (REPO / "skills/resume-evaluator/scripts/extract_text.py", "L0-extraction"),
    "L1": (REPO / "skills/resume-evaluator/scripts/parse_sim.py", "L1-parse-sim"),
    "L2": (REPO / "skills/resume-evaluator/scripts/hidden_text_check.py", "L2-integrity"),
    "L3": (REPO / "skills/resume-evaluator/scripts/lint_structure.py", "L3-structure"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_json(*args: str | Path) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout)


def test_example_files_are_the_current_compact_contract():
    required = [PDF, YAML, VAULT, *EVIDENCE_DOCUMENTS, LEDGER, JD, REPORT, EXAMPLE / "projection-report.md"]
    assert not [path for path in required if not path.is_file()]
    assert len(VAULT.read_text().splitlines()) <= 80
    assert len(YAML.read_text().splitlines()) <= 120


def test_candidate_evidence_migrates_the_legacy_source_without_target_contamination():
    index = EVIDENCE.read_text()
    detail = "\n".join(path.read_text() for path in EVIDENCE_DOCUMENTS[1:])
    assert digest(VAULT) in index
    assert "career-vault.md" in index
    assert "OMIT-FOR" not in index + detail
    data = yaml.safe_load(YAML.read_text())
    assert data["meta"]["vault"].endswith("examples/ai-ml-intern/candidate-evidence/index.md")


def test_example_tracker_is_prepared_and_never_claims_submission():
    ledger = LEDGER.read_text()
    assert "- applied: no" in ledger
    assert "- status: prepared" in ledger
    assert "- outcome: unknown" in ledger
    assert f"- pdf_sha256: {digest(PDF)}" in ledger
    assert f"- yaml_sha256: {digest(YAML)}" in ledger
    assert "status: applied" not in ledger


def test_projection_is_clean_and_reports_current_source_hashes():
    code, payload = run_json(PROJECTION, YAML, EVIDENCE, "--json")
    assert code == 0, payload
    assert payload["result"] == "pass"
    assert payload["resume_sha256"] == digest(YAML)
    assert payload["vault_sha256"] == digest(EVIDENCE)
    assert payload["metrics"]["claims_listed"] == len(payload["claims"])
    assert all(set(row) == {"path", "claim"} for row in payload["claims"])
    assert payload["scope"].startswith("Exact normalized values only")


def test_saved_layer_reports_bind_to_the_current_pdf_and_fresh_runs_pass():
    pdf_digest = digest(PDF)
    for name, (script, layer) in LAYERS.items():
        saved = json.loads((EXAMPLE / f"layer-reports/{name}.json").read_text())
        assert saved["layer"] == layer
        assert saved["result"] == "pass"
        assert saved["file_sha256"] == pdf_digest
        args = [script, PDF, "--json"]
        if name == "L3":
            args.extend(["--page-budget", "1"])
        code, fresh = run_json(*args)
        assert code == 0, fresh
        assert fresh["result"] == "pass"
        assert fresh["file_sha256"] == pdf_digest


def test_target_gates_match_the_source_record():
    analysis = JD.read_text()
    evidence = EVIDENCE.read_text()
    data = yaml.safe_load(YAML.read_text())
    assert "Graduation Dec 2027 or later | line 30 | met" in analysis
    assert data["education"][0]["end"] == "2027-12"
    assert "US work authorization with no sponsorship required" in evidence
    assert "US work authorization without sponsorship | lines 52–53 | met" in analysis


def test_report_is_ready_with_no_required_changes_and_current_hash():
    text = REPORT.read_text()
    assert "Recommendation: READY TO SEND" in text
    assert re.search(r"## Required changes\n+None\b", text)
    assert digest(PDF) in text
    assert "DO NOT APPLY" not in text.split("## Why", 1)[0]


def test_example_pdf_has_one_page_and_target_content():
    from pypdf import PdfReader

    reader = PdfReader(str(PDF))
    assert len(reader.pages) == 1
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for expected in ("RAG evaluation", "recall@10", "prompt-injection", "HNSW", "GPU cluster scheduling"):
        assert expected in text
    assert "Reading Group" not in text
