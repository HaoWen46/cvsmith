"""package_release.py builds release .skill zips matching the shipped
layout (top-level dir = skill folder name) and refuses to leave behind
a zip whose SKILL.md or references mention a script, reference, or
asset the zip lacks — and whose frontmatter would not actually load.

Same harness style as the other eval tests: the script runs as a
subprocess under the ambient interpreter (pyyaml present for the
frontmatter parse), exit codes and zip contents are the assertion
surface.
"""

from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts/package_release.py"
SKILLS = REPO / "skills"


def run_packager(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, cwd=REPO)


def test_packages_resume_builder(tmp_path):
    proc = run_packager(SKILLS / "resume-builder", "-o", tmp_path)
    assert proc.returncode == 0, proc.stderr
    zpath = tmp_path / "resume-builder.skill"
    assert zpath.is_file(), "no zip produced"
    names = set(zipfile.ZipFile(zpath).namelist())
    assert "resume-builder/SKILL.md" in names
    for script in ("scripts/validate_yaml.py", "scripts/check_projection.py",
                   "scripts/check_bullets.py", "scripts/render.sh"):
        assert f"resume-builder/{script}" in names, f"{script} not in zip"
    junk = [n for n in names if "__pycache__" in n or n.endswith(".pyc")]
    assert not junk, f"junk shipped: {junk}"


def test_missing_referenced_script_fails_and_removes_zip(tmp_path):
    skill = tmp_path / "synthetic"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: synthetic\n"
        "description: synthetic skill for the contract check\n"
        "---\n\n"
        "Run `scripts/missing.py` on the input.\n")
    (skill / "scripts" / "present.py").write_text("print('here')\n")
    out = tmp_path / "out"
    proc = run_packager(skill, "-o", out)
    assert proc.returncode == 1
    assert "missing.py" in proc.stderr
    assert not (out / "synthetic.skill").exists(), "bad zip left behind"


def make_skill(root: Path, name: str, frontmatter: str, body: str = "") -> Path:
    skill = root / name
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(frontmatter + "\n" + body)
    return skill


def test_malformed_yaml_frontmatter_fails(tmp_path):
    # `name: [unclosed` passes a line-grep but no skill loader can parse
    # it — the packager must reject what would ship broken.
    skill = make_skill(
        tmp_path, "synthetic",
        "---\n"
        "name: [unclosed\n"
        "description: has the line, is not yaml\n"
        "---\n")
    proc = run_packager(skill, "-o", tmp_path / "out")
    assert proc.returncode == 1
    assert "frontmatter" in proc.stderr
    assert not (tmp_path / "out" / "synthetic.skill").exists()


def test_frontmatter_name_must_match_directory(tmp_path):
    skill = make_skill(
        tmp_path, "synthetic",
        "---\n"
        "name: something-else\n"
        "description: name diverges from the shipped directory\n"
        "---\n")
    proc = run_packager(skill, "-o", tmp_path / "out")
    assert proc.returncode == 1
    assert "something-else" in proc.stderr


def test_missing_referenced_reference_fails_and_removes_zip(tmp_path):
    # The contract covers references and assets, not just scripts —
    # including mentions nested inside references/*.md.
    skill = make_skill(
        tmp_path, "synthetic",
        "---\n"
        "name: synthetic\n"
        "description: synthetic skill for the reference contract\n"
        "---\n",
        "Read `references/present.md` before anything.\n")
    (skill / "references").mkdir()
    (skill / "references" / "present.md").write_text(
        "See also `references/absent.md` and `assets/missing.typ`.\n")
    out = tmp_path / "out"
    proc = run_packager(skill, "-o", out)
    assert proc.returncode == 1
    assert "absent.md" in proc.stderr
    assert "missing.typ" in proc.stderr
    assert not (out / "synthetic.skill").exists(), "bad zip left behind"


def test_default_discovery_packages_every_skill(tmp_path):
    # Read skills/ at runtime — the skill roster grows; never hardcode a count.
    expected = sorted(d.name for d in SKILLS.iterdir()
                      if d.is_dir() and (d / "SKILL.md").is_file())
    assert expected, "no skills found — repo layout changed?"
    proc = run_packager("-o", tmp_path)
    assert proc.returncode == 0, proc.stderr
    built = sorted(p.name.removesuffix(".skill")
                   for p in tmp_path.glob("*.skill"))
    assert built == expected
