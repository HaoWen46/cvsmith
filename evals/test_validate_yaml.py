from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "skills/resume-builder/scripts/validate_yaml.py"
FIXTURE = REPO / "evals/fixtures/resume-sample/resume.yaml"


def run(path: Path, template: str = "compact") -> tuple[int, dict | None, str]:
    proc = subprocess.run(["uv", "run", "--script", str(SCRIPT), str(path), "--template", template, "--json"], capture_output=True, text=True)
    return proc.returncode, json.loads(proc.stdout) if proc.stdout.strip() else None, proc.stderr


def mutate(tmp_path: Path, old: str, new: str) -> Path:
    path = tmp_path / "resume.yaml"
    source = FIXTURE.read_text()
    assert old in source
    path.write_text(source.replace(old, new, 1))
    return path


@pytest.mark.parametrize("fixture", sorted((REPO / "evals/fixtures").glob("*-sample/resume.yaml")))
def test_real_fixtures_validate(fixture):
    code, report, error = run(fixture)
    assert code == 0, error or report
    assert report["result"] == "pass"


@pytest.mark.parametrize(("old", "new", "check"), [
    ("  target_level: intern\n", "  target_level: [intern]\n", "shape"),
    ("  page_budget: 1\n", "  page_budget: 0\n", "value"),
    ("  template: compact\n", "  template: compact\n  paper: legal\n", "value"),
    ("  email: sam.casey@example.com\n", "  email: sam@\n", "value"),
    ("    gpa: \"3.8/4.0\"\n", "    gpa: 3.8\n", "shape"),
    ("    start: 2023-09\n", "    start: 2023-19\n", "date"),
    ("      - Built nightly Python/pytest RAG", "      - action: Built nightly Python/pytest RAG", "shape"),
    ("  - label: Languages\n", "  - label: Languages\n    rating: expert\n", "keys"),
])
def test_invalid_boundary_is_rejected(tmp_path, old, new, check):
    code, report, _ = run(mutate(tmp_path, old, new))
    assert code == 1
    assert any(item["check_id"] == check and item["level"] == "fail" for item in report["checks"])


def test_duplicate_key_is_rejected_before_render(tmp_path):
    path = mutate(tmp_path, "  page_budget: 1\n", "  page_budget: 1\n  page_budget: 2\n")
    code, report, error = run(path)
    assert code == 2 and report is None
    assert "duplicate key" in error


def test_reversed_dates_and_partial_grouping_are_rejected(tmp_path):
    path = mutate(tmp_path, "    start: 2023-09\n    end: 2027-12\n", "    start: 2028-01\n    end: 2027-12\n")
    code, report, _ = run(path)
    assert code == 1 and any("start" in item["detail"] and "after" in item["detail"] for item in report["checks"])
    path = mutate(tmp_path, "    tags: [RAG evaluation", "    group: industry\n    tags: [RAG evaluation")
    code, report, _ = run(path)
    assert code == 1 and any("group every entry" in item["detail"] for item in report["checks"])


def test_all_templates_share_the_content_schema():
    schema = (REPO / "skills/resume-builder/assets/templates/data-schema.md").read_text()
    base = (REPO / "skills/resume-builder/assets/templates/base.typ").read_text()
    assert "Every template renders all content keys" in schema
    assert '"tags" in item' in base and '"stack" in item' in base
    for template in ("onecol", "compact", "classic"):
        code, report, error = run(FIXTURE, template)
        assert code == 0, error or report
