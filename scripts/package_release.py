#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""Package skills into release `.skill` zips — repo-local.

Replaces the machine-specific skill-creator packager the release
checklist used to point at. Each skill folder becomes `<name>.skill`,
a zip rooted at `<name>/` so it unpacks to the exact layout the GitHub
release assets have always shipped. Junk never ships: `__pycache__/`,
`*.pyc`, `.DS_Store`, `node_modules/`, any `evals/` subdir.

Two gates, both fatal (stderr + exit 1):
- frontmatter sanity: SKILL.md opens with `---` frontmatter that
  actually parses as YAML, whose `name` matches the shipped directory
  and whose `description` is a non-empty string — a line-grep let
  `name: [unclosed` ship as a package no skill loader could read;
- contract check: every `scripts/<file>`, `references/<file>`, and
  `assets/<file>` path that SKILL.md or any bundled .md doc mentions
  (including docs nested under references/ and assets/) must be inside
  the zip, as must SKILL.md itself. Cross-skill dependencies must be
  written as prose naming the sibling skill, never as a bare path —
  the contract is intra-skill by design. A zip that fails the contract
  is removed — a broken release artifact is worse than none.

usage: package_release.py [skill-dir ...] [-o OUTDIR]
  default: every direct subdirectory of skills/ with a SKILL.md -> dist/
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {"__pycache__", "node_modules", "evals"}
EXCLUDED_FILES = {".DS_Store"}
# `scripts/render.sh`, `scripts/check_bullets.py`, ... — the lookbehind
# keeps foreign paths like `.github/scripts/x.py` from binding the contract.
SCRIPT_REF = re.compile(r"(?<![\w/])scripts/([\w.-]+\.[A-Za-z0-9]+)")
# `references/career-vault.md`, `assets/templates/data-schema.md`, ...
FILE_REF = re.compile(r"(?<![\w/])((?:references|assets)/[\w./-]*\.[A-Za-z0-9]+)")


def err(msg: str) -> None:
    print(f"package_release: {msg}", file=sys.stderr)


def frontmatter_ok(skill_md: Path, expected_name: str) -> bool:
    import yaml

    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        err(f"{skill_md}: does not open with --- frontmatter")
        return False
    close = next((i for i, ln in enumerate(lines[1:], 1)
                  if ln.strip() == "---"), None)
    if close is None:
        err(f"{skill_md}: frontmatter never closes")
        return False
    try:
        meta = yaml.safe_load("\n".join(lines[1:close]))
    except yaml.YAMLError as exc:
        err(f"{skill_md}: frontmatter is not valid YAML: {exc}")
        return False
    if not isinstance(meta, dict):
        err(f"{skill_md}: frontmatter must be a YAML mapping")
        return False
    ok = True
    name = meta.get("name")
    if name != expected_name:
        err(f"{skill_md}: frontmatter name {name!r} does not match the "
            f"shipped directory {expected_name!r}")
        ok = False
    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err(f"{skill_md}: frontmatter description missing or empty")
        ok = False
    return ok


def doc_files(skill_dir: Path) -> list[Path]:
    """Every bundled markdown doc that can bind the contract."""
    docs = [skill_dir / "SKILL.md"]
    for sub in ("references", "assets"):
        docs.extend(sorted((skill_dir / sub).rglob("*.md")))
    return [d for d in docs if d.is_file()]


def referenced_paths(skill_dir: Path) -> set[str]:
    """Skill-relative paths the docs mention: scripts, references, assets."""
    refs: set[str] = set()
    for doc in doc_files(skill_dir):
        text = doc.read_text(encoding="utf-8")
        refs.update(f"scripts/{name}" for name in SCRIPT_REF.findall(text))
        refs.update(FILE_REF.findall(text))
    return refs


def ship_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(skill_dir)
        if EXCLUDED_DIRS.intersection(rel.parts[:-1]):
            continue
        if rel.name in EXCLUDED_FILES or rel.suffix == ".pyc":
            continue
        yield path, rel


def package(skill_dir: Path, outdir: Path) -> bool:
    skill_dir = skill_dir.resolve()
    name = skill_dir.name
    if not (skill_dir / "SKILL.md").is_file():
        err(f"{skill_dir}: no SKILL.md")
        return False
    if not frontmatter_ok(skill_dir / "SKILL.md", name):
        return False
    outdir.mkdir(parents=True, exist_ok=True)
    zpath = outdir / f"{name}.skill"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, rel in ship_files(skill_dir):
            zf.write(path, f"{name}/{rel.as_posix()}")
        shipped = set(zf.namelist())
    wanted = [f"{name}/SKILL.md"] + [f"{name}/{ref}"
                                     for ref in sorted(referenced_paths(skill_dir))]
    missing = [w for w in wanted if w not in shipped]
    if missing:
        for m in missing:
            err(f"{name}: referenced but absent from zip: {m}")
        zpath.unlink()
        err(f"{name}: removed {zpath}")
        return False
    print(f"{zpath.name}: {len(shipped)} files, {zpath.stat().st_size} bytes")
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Package skills into release .skill zips.")
    ap.add_argument("skill_dirs", nargs="*", type=Path,
                    help="skill directories (default: every skills/* with a SKILL.md)")
    ap.add_argument("-o", "--outdir", type=Path, default=REPO / "dist",
                    help="output directory (default: dist/)")
    args = ap.parse_args(argv)
    dirs = args.skill_dirs or sorted(
        d for d in (REPO / "skills").iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file())
    if not dirs:
        err("nothing to package")
        return 1
    results = [package(d, args.outdir) for d in dirs]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
