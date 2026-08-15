from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "skills/resume-evaluator/scripts"
GENERATE = REPO / "evals/fixtures/generate.py"
LAYERS = ("extract_text.py", "parse_sim.py", "hidden_text_check.py", "lint_structure.py")


@pytest.fixture(scope="session")
def fixtures(tmp_path_factory) -> Path:
    if not shutil.which("typst"):
        pytest.skip("typst not installed")
    out = tmp_path_factory.mktemp("pdf-fixtures")
    proc = subprocess.run(["uv", "run", "--script", str(GENERATE), "--out", str(out)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return out


def run(script: str, pdf: Path, *args) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), str(pdf), *args, "--json"], capture_output=True, text=True)
    assert proc.returncode in (0, 1), proc.stderr
    return proc.returncode, json.loads(proc.stdout)


def failed(report: dict) -> set[str]:
    return {item["check_id"] for item in report["checks"] if item["level"] == "fail"}


@pytest.mark.parametrize("script", LAYERS)
def test_good_resume_passes_every_objective_layer(fixtures, script):
    code, report = run(script, fixtures / "good.pdf")
    assert code == 0 and report["result"] == "pass"
    assert len(report["file_sha256"]) == 64


@pytest.mark.parametrize(("fixture", "script", "check"), [
    ("image_only.pdf", "extract_text.py", "text_layer"),
    ("image_only.pdf", "lint_structure.py", "image_pages"),
    ("white_text.pdf", "hidden_text_check.py", "invisible_text"),
    ("transparent_text.pdf", "hidden_text_check.py", "invisible_text"),
    ("tiny_text.pdf", "hidden_text_check.py", "microscopic_text"),
    ("partial_edge_text.pdf", "hidden_text_check.py", "offpage_text"),
    ("twocol.pdf", "lint_structure.py", "single_column"),
    ("wonky_headings.pdf", "parse_sim.py", "unknown_headings"),
])
def test_planted_failure_is_exposed(fixtures, fixture, script, check):
    code, report = run(script, fixtures / fixture)
    assert code == 1
    assert check in failed(report)


@pytest.mark.parametrize("script", LAYERS)
def test_malformed_pdf_returns_a_report_not_a_traceback(tmp_path, script):
    bad = tmp_path / "bad.pdf"
    bad.write_text("not a PDF")
    proc = subprocess.run([sys.executable, str(SCRIPTS / script), str(bad), "--json"], capture_output=True, text=True)
    assert proc.returncode in (1, 2)
    assert "Traceback" not in proc.stderr
    if proc.stdout.strip():
        assert json.loads(proc.stdout)["result"] == "fail"


def test_explicit_page_budget_is_enforced(fixtures):
    code, report = run("lint_structure.py", fixtures / "good.pdf", "--page-budget", "1")
    assert code == 0
    assert any(item["check_id"] == "page_budget" and item["level"] == "pass" for item in report["checks"])


def test_objective_reports_never_claim_employer_outcomes():
    text = "\n".join((SCRIPTS / script).read_text() for script in LAYERS)
    for phrase in ("will pass every ATS", "predicts hiring", "guarantees an interview"):
        assert phrase not in text.casefold()
