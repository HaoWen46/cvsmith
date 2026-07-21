"""M2 exit criterion, executable: the evaluator catches every planted
failure in the fixtures and raises zero false positives on the good one.

Fixtures are generated fresh (see fixtures/generate.py) so these tests
exercise the real render path too.
"""

from __future__ import annotations

import json
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
    assert len(report["bullets"]) >= 10, "should find every bullet"
    assert any(b["lines"] >= 2 for b in report["bullets"]), \
        "fixture is known to wrap some bullets in compact"

    proc = subprocess.run([sys.executable, str(check), str(pdf), "--max-lines", "1"],
                          capture_output=True, text=True)
    assert proc.returncode == 1, "one-line budget must fail on wrapped bullets"


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
