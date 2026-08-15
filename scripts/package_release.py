#!/usr/bin/env -S uv run
"""Package each skill as a zip rooted at its directory name."""

from __future__ import annotations

import argparse
import re
import stat
import sys
import zipfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
MAX_DESCRIPTION = 1024
REFERENCE = re.compile(r"(?<![\w/])((?:scripts|references|assets)/[\w./-]+\.[A-Za-z0-9]+)")
CACHE_DIRECTORIES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
CACHE_FILES = {".DS_Store", "Thumbs.db"}
CACHE_SUFFIXES = {".pyc", ".pyo"}
NON_PORTABLE_PATHS = (
    ("POSIX user-home path", re.compile(r"/(?:Users|home)/[^/\s<>${}\\]+/")),
    ("Windows user-home path", re.compile(r"\b[A-Z]:[\\/]+Users[\\/]+[^\\/\s<>${}]+[\\/]", re.IGNORECASE)),
    ("agent-specific runtime path", re.compile(r"(?<![\w.-])\.(?:claude|codex|agents)\b", re.IGNORECASE)),
)
ARCHIVE_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def error(message: str) -> None:
    print(f"package_release: {message}", file=sys.stderr)


def metadata(skill: Path) -> dict | None:
    lines = (skill / "SKILL.md").read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        error(f"{skill}/SKILL.md: missing frontmatter")
        return None
    try:
        close = lines[1:].index("---") + 1
        value = yaml.safe_load("\n".join(lines[1:close]))
    except (ValueError, yaml.YAMLError) as exc:
        error(f"{skill}/SKILL.md: invalid frontmatter: {exc}")
        return None
    description = value.get("description") if isinstance(value, dict) else None
    if not isinstance(value, dict) or value.get("name") != skill.name:
        error(f"{skill}/SKILL.md: name must equal directory {skill.name!r}")
        return None
    if not isinstance(description, str) or not description.strip() or len(description) > MAX_DESCRIPTION:
        error(f"{skill}/SKILL.md: description must contain 1-{MAX_DESCRIPTION} characters")
        return None
    return value


def files(skill: Path) -> list[Path] | None:
    shipped = []
    for path in sorted(skill.rglob("*")):
        relative = path.relative_to(skill)
        if path.is_symlink():
            error(f"{skill.name}: symlink not allowed: {relative.as_posix()}")
            return None
        if any(part in CACHE_DIRECTORIES for part in relative.parts) or path.name in CACHE_FILES or path.suffix in CACHE_SUFFIXES:
            error(f"{skill.name}: cache artifact not allowed: {relative.as_posix()}")
            return None
        if path.is_file():
            shipped.append(path)
        elif not path.is_dir():
            error(f"{skill.name}: unsupported file type: {relative.as_posix()}")
            return None
    return shipped


def portable(skill: Path, shipped: list[Path]) -> bool:
    for path in shipped:
        text = path.read_bytes().decode("latin-1")
        variants = (text, text.replace(r"\/", "/"), text.replace(r"\\", "\\"))
        for label, pattern in NON_PORTABLE_PATHS:
            if any(pattern.search(value) for value in variants):
                error(f"{skill.name}: {path.relative_to(skill).as_posix()} contains non-portable {label}")
                return False
    return True


def references(skill: Path, shipped: list[Path]) -> set[str]:
    docs = [path for path in shipped if path.suffix == ".md"]
    return {match for doc in docs for match in REFERENCE.findall(doc.read_text(encoding="utf-8"))}


def write_member(bundle: zipfile.ZipFile, name: str, data: bytes, mode: int) -> None:
    info = zipfile.ZipInfo(name, ARCHIVE_TIMESTAMP)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED
    info.external_attr = (stat.S_IFREG | mode) << 16
    bundle.writestr(info, data)


def package(skill: Path, out: Path) -> bool:
    skill = skill.absolute()
    archive = out / f"{skill.name}.skill"
    if archive.is_file() or archive.is_symlink():
        archive.unlink()
    elif archive.exists():
        error(f"{archive}: archive target is not a file")
        return False
    if skill.is_symlink():
        error(f"{skill.name}: skill root cannot be a symlink")
        return False
    if not (skill / "SKILL.md").is_file() or metadata(skill) is None:
        return False
    shipped = files(skill)
    if shipped is None or not portable(skill, shipped):
        return False
    available = {path.relative_to(skill).as_posix() for path in shipped}
    missing = sorted(references(skill, shipped) - available)
    if missing:
        error(f"{skill.name}: documented path(s) missing: {', '.join(missing)}")
        return False
    out.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_STORED) as bundle:
        for path in shipped:
            if path.relative_to(skill).as_posix() == "LICENSE":
                continue
            data = path.read_bytes()
            mode = 0o755 if data.startswith(b"#!") else 0o644
            write_member(bundle, f"{skill.name}/{path.relative_to(skill).as_posix()}", data, mode)
        write_member(bundle, f"{skill.name}/LICENSE", (REPO / "LICENSE").read_bytes(), 0o644)
    count = len(shipped) + ("LICENSE" not in available)
    print(f"{archive.name}: {count} files")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", type=Path)
    parser.add_argument("-o", "--out", type=Path, default=REPO / "dist")
    args = parser.parse_args()
    skills = args.skills or sorted(path for path in (REPO / "skills").iterdir() if (path / "SKILL.md").is_file())
    results = [package(skill, args.out) for skill in skills]
    return 0 if results and all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
