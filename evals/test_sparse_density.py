from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
RENDER = REPO / "skills/resume-builder/scripts/render.sh"
PARSE = REPO / "skills/resume-evaluator/scripts/parse_sim.py"
LINT = REPO / "skills/resume-evaluator/scripts/lint_structure.py"
FIXTURES = ("sparse-sample", "resume-sample", "academic-sample")


def report(script: Path, pdf: Path) -> dict:
    proc = subprocess.run(["uv", "run", str(script), str(pdf), "--json"], capture_output=True, text=True)
    assert proc.returncode in (0, 1), proc.stderr
    return json.loads(proc.stdout)


@pytest.mark.skipif(not shutil.which("typst"), reason="typst not installed")
@pytest.mark.parametrize("fixture", FIXTURES)
@pytest.mark.parametrize("template", ("onecol", "compact", "classic"))
def test_content_density_does_not_change_routing_or_column_read(tmp_path, fixture, template):
    source = REPO / f"evals/fixtures/{fixture}/resume.yaml"
    pdf = tmp_path / f"{fixture}-{template}.pdf"
    proc = subprocess.run([str(RENDER), str(source), "-t", template, "-o", str(pdf)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    parsed = report(PARSE, pdf)
    linted = report(LINT, pdf)
    assert parsed["contact"]["name_guess"]
    assert any(item["check_id"] == "single_column" and item["level"] != "fail" for item in linted["checks"])
    if "experience" in parsed.get("sections", {}):
        assert parsed["metrics"]["date_ranges"].get("experience", 0) > 0
