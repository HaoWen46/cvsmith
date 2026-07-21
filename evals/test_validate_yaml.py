"""validate_yaml.py catches every planted schema violation with the right
yaml path and raises zero false positives on the real fixtures.

Same harness style as test_evaluator.py: scripts run under the ambient
interpreter (pyyaml present), --json output is the assertion surface.
"""

from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "skills/resume-builder/scripts/validate_yaml.py"
FIXTURES = {
    "resume-sample": REPO / "evals/fixtures/resume-sample/resume.yaml",
    "academic-sample": REPO / "evals/fixtures/academic-sample/resume.yaml",
}


def run_validator(path: Path) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--json"],
        capture_output=True, text=True)
    assert proc.returncode in (0, 1), f"validator crashed:\n{proc.stderr}"
    return proc.returncode, json.loads(proc.stdout)


def fails(report: dict) -> list[dict]:
    return [c for c in report["checks"] if c["level"] == "fail"]


def mutated(tmp_path: Path, fixture: str, old: str, new: str) -> Path:
    src = FIXTURES[fixture].read_text()
    assert old in src, f"fixture drifted: {old!r} not found in {fixture}"
    out = tmp_path / "resume.yaml"
    out.write_text(src.replace(old, new))
    return out


# ── zero false positives on the real fixtures ────────────────────────

@pytest.mark.parametrize("fixture", sorted(FIXTURES))
def test_real_fixture_passes_clean(fixture):
    code, report = run_validator(FIXTURES[fixture])
    assert code == 0, f"false positive on {fixture}: {report}"
    assert report["verdict"] == "pass"
    assert not fails(report)
    warns = [c for c in report["checks"] if c["level"] == "warn"]
    assert not warns, f"unexpected warnings on {fixture}: {warns}"


# ── every planted violation is caught, with the right yaml path ──────

def test_optional_key_typo_is_caught(tmp_path):
    bad = mutated(tmp_path, "resume-sample", "honors:", "honours:")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "known_keys"
    assert "education[0].honours" in f[0]["detail"]
    assert "honors" in f[0]["detail"], "suggestion must surface the fix"


def test_top_level_section_typo_is_caught(tmp_path):
    bad = mutated(tmp_path, "resume-sample", "\nprojects:\n", "\nproject:\n")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "known_keys"
    assert f[0]["detail"].startswith("project:")
    assert "projects" in f[0]["detail"], "suggestion must surface the fix"
    assert "render" in f[0]["detail"], \
        "the silent-content-loss consequence must be named"


def test_bad_month_is_caught(tmp_path):
    bad = mutated(tmp_path, "resume-sample",
                  "start: 2025-06", "start: 2025-13")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "dates"
    assert "experience[0].start" in f[0]["detail"]
    assert "2025-13" in f[0]["detail"]


def test_link_missing_url_is_caught(tmp_path):
    bad = mutated(
        tmp_path, "resume-sample",
        "- label: GitHub\n      url: https://github.com/samcasey-demo\n",
        "- label: GitHub\n")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "required_keys"
    assert "basics.links[0]" in f[0]["detail"]
    assert "url" in f[0]["detail"]


def test_empty_bullets_is_caught(tmp_path):
    yml = textwrap.dedent("""\
        basics:
          name: Test Person
          email: test@example.com
        experience:
          - organization: Somewhere Labs
            title: Intern
            start: 2025-06
            end: 2025-09
            bullets: []
        """)
    path = tmp_path / "resume.yaml"
    path.write_text(yml)
    code, report = run_validator(path)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "empties"
    assert "experience[0].bullets" in f[0]["detail"]


def test_bad_group_enum_is_caught(tmp_path):
    # unknown group values silently drop the entry from a grouped render
    bad = mutated(tmp_path, "academic-sample",
                  "group: industry", "group: volunteer")
    code, report = run_validator(bad)
    assert code == 1
    f = fails(report)
    assert len(f) == 1, f"expected exactly the planted violation: {f}"
    assert f[0]["check_id"] == "values"
    assert "experience[3].group" in f[0]["detail"]
    assert "volunteer" in f[0]["detail"]


# ── the exit-code contract's third leg ───────────────────────────────

def test_unparseable_yaml_exits_2(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("basics: [unclosed\n")
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(path), "--json"],
        capture_output=True, text=True)
    assert proc.returncode == 2
    assert "error:" in proc.stderr
