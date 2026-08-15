from __future__ import annotations

import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/package_release.py"
SKILLS = REPO / "skills"


def run(*arguments) -> subprocess.CompletedProcess:
    return subprocess.run(["uv", "run", "--locked", str(SCRIPT), *map(str, arguments)], cwd=REPO, capture_output=True, text=True)


def make_skill(root: Path, body: str = "Portable test skill.\n") -> Path:
    skill = root / "portable"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(f"---\nname: portable\ndescription: test skill\n---\n\n{body}")
    return skill


def test_packager_uses_the_repository_lockfile():
    text = SCRIPT.read_text(encoding="utf-8")
    assert "uv run --script" not in text
    assert "# /// script" not in text


def test_packages_every_skill_with_one_correct_root(tmp_path):
    result = run("-o", tmp_path)
    assert result.returncode == 0, result.stderr
    expected = sorted(path.name for path in SKILLS.iterdir() if (path / "SKILL.md").is_file())
    assert sorted(path.stem for path in tmp_path.glob("*.skill")) == expected
    for name in expected:
        with zipfile.ZipFile(tmp_path / f"{name}.skill") as bundle:
            names = bundle.namelist()
        assert f"{name}/SKILL.md" in names
        assert names and all(item.startswith(f"{name}/") for item in names)
        assert not [item for item in names if "__pycache__" in item or item.endswith(".pyc")]


def test_every_archive_carries_the_repository_license(tmp_path):
    result = run("-o", tmp_path)
    assert result.returncode == 0, result.stderr
    expected_license = (REPO / "LICENSE").read_bytes()
    for archive in tmp_path.glob("*.skill"):
        with zipfile.ZipFile(archive) as bundle:
            assert bundle.read(f"{archive.stem}/LICENSE") == expected_license


def test_documented_local_paths_exist_in_each_archive(tmp_path):
    assert run("-o", tmp_path).returncode == 0
    for archive in tmp_path.glob("*.skill"):
        with zipfile.ZipFile(archive) as bundle:
            names = set(bundle.namelist())
        assert f"{archive.stem}/SKILL.md" in names
        for required in ("scripts/render.sh", "scripts/check_projection.py") if archive.stem == "resume-builder" else ():
            assert f"{archive.stem}/{required}" in names


@pytest.mark.parametrize("skill", sorted(path for path in SKILLS.iterdir() if (path / "SKILL.md").is_file()), ids=lambda path: path.name)
def test_skill_metadata_is_loadable_and_compact(skill):
    lines = (skill / "SKILL.md").read_text().splitlines()
    close = lines[1:].index("---") + 1
    meta = yaml.safe_load("\n".join(lines[1:close]))
    assert meta["name"] == skill.name
    assert 0 < len(meta["description"]) <= 1024


def test_missing_documented_file_rejects_archive(tmp_path):
    skill = tmp_path / "broken"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: broken\ndescription: test skill\n---\n\nRun `scripts/missing.py`.\n")
    out = tmp_path / "out"
    result = run(skill, "-o", out)
    assert result.returncode == 1 and "missing.py" in result.stderr
    assert not (out / "broken.skill").exists()


def test_executable_scripts_keep_their_archive_mode(tmp_path):
    assert run(SKILLS / "resume-builder", "-o", tmp_path).returncode == 0
    with zipfile.ZipFile(tmp_path / "resume-builder.skill") as bundle:
        for path in (SKILLS / "resume-builder/scripts").iterdir():
            if path.is_file() and stat.S_IMODE(path.stat().st_mode) & stat.S_IXUSR:
                mode = bundle.getinfo(f"resume-builder/scripts/{path.name}").external_attr >> 16
                assert mode & stat.S_IXUSR


def test_symlinked_file_rejects_archive(tmp_path):
    skill = make_skill(tmp_path / "source")
    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"host-only data")
    (skill / "references").mkdir()
    try:
        (skill / "references/host-cache.bin").symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlinks unavailable: {exc}")
    out = tmp_path / "out"
    result = run(skill, "-o", out)
    assert result.returncode == 1 and "symlink" in result.stderr.lower()
    assert not (out / "portable.skill").exists()


@pytest.mark.parametrize(
    "host_path",
    [
        "/Users/alice/private/resume.pdf",
        "/home/alice/private/resume.pdf",
        r"C:\Users\Alice\private\resume.pdf",
        "~/.claude/skills/resume-builder",
        "~/.codex/skills/resume-builder",
        "~/.agents/skills/resume-builder",
        "$HOME/.claude/skills/resume-builder",
        "${HOME}/.codex/skills/resume-builder",
        r"%USERPROFILE%\.agents\skills\resume-builder",
    ],
)
def test_machine_specific_path_rejects_archive(tmp_path, host_path):
    skill = make_skill(tmp_path / "source", f"Read `{host_path}`.\n")
    out = tmp_path / "out"
    result = run(skill, "-o", out)
    assert result.returncode == 1 and "non-portable" in result.stderr.lower()
    assert not (out / "portable.skill").exists()


def test_source_cache_rejects_archive(tmp_path):
    skill = make_skill(tmp_path / "source")
    cache = skill / "scripts/__pycache__"
    cache.mkdir(parents=True)
    (cache / "module.cpython-312.pyc").write_bytes(b"compiled host state")
    out = tmp_path / "out"
    result = run(skill, "-o", out)
    assert result.returncode == 1 and "cache artifact" in result.stderr.lower()
    assert not (out / "portable.skill").exists()


def test_package_is_reproducible_across_source_mtimes(tmp_path):
    first = make_skill(tmp_path / "first")
    second = make_skill(tmp_path / "second")
    os.utime(first / "SKILL.md", (1_600_000_000, 1_600_000_000))
    os.utime(second / "SKILL.md", (1_700_000_000, 1_700_000_000))
    first_out = tmp_path / "first-out"
    second_out = tmp_path / "second-out"
    assert run(first, "-o", first_out).returncode == 0
    assert run(second, "-o", second_out).returncode == 0
    assert (first_out / "portable.skill").read_bytes() == (second_out / "portable.skill").read_bytes()


def test_failed_rebuild_removes_existing_archive(tmp_path):
    skill = make_skill(tmp_path / "source")
    out = tmp_path / "out"
    assert run(skill, "-o", out).returncode == 0
    (skill / "SKILL.md").write_text("---\nname: portable\ndescription: test skill\n---\n\nRun `scripts/missing.py`.\n")
    result = run(skill, "-o", out)
    assert result.returncode == 1 and "missing.py" in result.stderr
    assert not (out / "portable.skill").exists()


def test_failed_multi_skill_build_removes_every_stale_archive(tmp_path):
    skills = []
    out = tmp_path / "out"
    out.mkdir()
    for name in ("broken-a", "broken-b"):
        skill = tmp_path / name
        skill.mkdir()
        (skill / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test skill\n---\n\nRun `scripts/missing.py`.\n")
        (out / f"{name}.skill").write_bytes(b"stale")
        skills.append(skill)
    result = run(*skills, "-o", out)
    assert result.returncode == 1
    assert not list(out.glob("*.skill"))


@pytest.mark.parametrize("script_name", ["extract_text.py", "parse_sim.py", "hidden_text_check.py", "lint_structure.py"])
def test_installed_evaluator_does_not_write_bytecode(tmp_path, script_name):
    archive_dir = tmp_path / "archive"
    result = run(SKILLS / "resume-evaluator", "-o", archive_dir)
    assert result.returncode == 0, result.stderr
    extracted = tmp_path / "extracted"
    with zipfile.ZipFile(archive_dir / "resume-evaluator.skill") as bundle:
        bundle.extractall(extracted)
    scripts = extracted / "resume-evaluator/scripts"
    result = subprocess.run([sys.executable, str(scripts / script_name), "--help"], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not list(scripts.rglob("__pycache__"))
    assert not list(scripts.rglob("*.pyc"))
