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

import stat
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


def test_source_scripts_are_directly_executable():
    # Belt-and-braces layer for the exit-126 finding: SKILL.md documents
    # `uv run scripts/check_projection.py ...`, and `uv run` doesn't care
    # about the execute bit at all — it runs its own interpreter with the
    # file as an argument. So a regression here (e.g. an editor stripping
    # +x, or a new script added without chmod) would slip past every
    # `uv run`-based test, including the doc-reality one, while still
    # exit-126ing anyone who runs the script bare (tab completion, muscle
    # memory, an older copy-pasted command). Assert directly on the
    # source tree so this can't hide behind the packaging step.
    src_dir = SKILLS / "resume-builder/scripts"
    py_scripts = sorted(src_dir.glob("*.py"))
    assert py_scripts, "no scripts/*.py found — resume-builder layout changed?"
    for script in py_scripts:
        mode = stat.S_IMODE(script.stat().st_mode)
        assert mode & stat.S_IXUSR, (
            f"{script.relative_to(REPO)}: not executable (mode {oct(mode)}) "
            "— direct invocation (no `uv run` prefix) would exit 126")
        shebang = script.read_text(encoding="utf-8").splitlines()[0]
        assert shebang.startswith("#!") and "uv run" in shebang, (
            f"{script.relative_to(REPO)}: shebang {shebang!r} is not a "
            "uv-run PEP 723 shebang — direct execution would use the "
            "system interpreter and likely fail on missing dependencies")


def test_packaged_scripts_preserve_exec_bit(tmp_path):
    # SKILL.md tells the user to invoke scripts/check_projection.py etc.
    # directly; a zip that silently drops the executable bit ships a
    # command that exit-126s the moment someone unpacks it. zipfile.write
    # already folds st_mode into external_attr via ZipInfo.from_file — this
    # locks that behavior in so a future zipfile refactor can't regress it
    # quietly. Compare against the live source tree's modes rather than a
    # hardcoded list, so this test can't go stale as scripts are added.
    proc = run_packager(SKILLS / "resume-builder", "-o", tmp_path)
    assert proc.returncode == 0, proc.stderr
    zpath = tmp_path / "resume-builder.skill"
    src_dir = SKILLS / "resume-builder"
    with zipfile.ZipFile(zpath) as zf:
        script_infos = {
            info.filename: info for info in zf.infolist()
            if "/scripts/" in info.filename and not info.is_dir()
        }
        assert script_infos, "no scripts/ entries found in archive"
        for name, info in script_infos.items():
            rel = Path(name).relative_to("resume-builder")
            src = src_dir / rel
            assert src.is_file(), f"{rel} shipped but missing from source tree"
            src_mode = stat.S_IMODE(src.stat().st_mode)
            zip_mode = (info.external_attr >> 16) & 0o777
            assert zip_mode == src_mode, (
                f"{name}: source mode {oct(src_mode)} != "
                f"archive mode {oct(zip_mode)}")
            if src_mode & stat.S_IXUSR:
                assert zip_mode & stat.S_IXUSR, (
                    f"{name}: source is executable but archive entry is not "
                    "— unzip would ship a script users can't run directly")


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


def test_archive_root_is_skill_directory_for_every_skill(tmp_path):
    # README's install command assumes `unzip <name>.skill -d
    # ~/.claude/skills/` lands SKILL.md at `~/.claude/skills/<name>/SKILL.md`
    # — Claude Code's personal-skill discovery path. Lock the exact
    # archive layout every skill ships, not just resume-builder's, so a
    # future skill can't regress the README's copy-pasteable command.
    proc = run_packager("-o", tmp_path)
    assert proc.returncode == 0, proc.stderr
    built = sorted(tmp_path.glob("*.skill"))
    assert built, "no archives built — packaging default discovery broken?"
    for zpath in built:
        name = zpath.stem
        names = zipfile.ZipFile(zpath).namelist()
        assert f"{name}/SKILL.md" in names, (
            f"{zpath.name}: archive root is not {name}/ — "
            "unzipping to ~/.claude/skills/ would not produce "
            f"~/.claude/skills/{name}/SKILL.md")
        offenders = [n for n in names if not n.startswith(f"{name}/")]
        assert not offenders, f"{zpath.name}: entries outside {name}/ root: {offenders}"
