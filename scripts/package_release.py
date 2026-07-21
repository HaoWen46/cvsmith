#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package skills into release `.skill` zips — repo-local, stdlib only.

Replaces the machine-specific skill-creator packager the release
checklist used to point at. Each skill folder becomes `<name>.skill`,
a zip rooted at `<name>/` so it unpacks to the exact layout the GitHub
release assets have always shipped. Junk never ships: `__pycache__/`,
`*.pyc`, `.DS_Store`, `node_modules/`, any `evals/` subdir.

Two gates, both fatal (stderr + exit 1):
- frontmatter sanity: SKILL.md opens with `---` and carries `name:`
  and `description:` lines (line checks only — CI's skill-structure
  job does the richer validation);
- contract check: every `scripts/<file>` that SKILL.md or
  references/*.md mentions must be inside the zip, as must SKILL.md
  itself. A zip that fails the contract is removed — a broken release
  artifact is worse than none.

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


def err(msg: str) -> None:
    print(f"package_release: {msg}", file=sys.stderr)


def frontmatter_ok(skill_md: Path) -> bool:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        err(f"{skill_md}: does not open with --- frontmatter")
        return False
    close = next((i for i, ln in enumerate(lines[1:], 1)
                  if ln.strip() == "---"), None)
    if close is None:
        err(f"{skill_md}: frontmatter never closes")
        return False
    ok = True
    for key in ("name:", "description:"):
        if not any(ln.startswith(key) for ln in lines[1:close]):
            err(f"{skill_md}: frontmatter missing {key} line")
            ok = False
    return ok


def referenced_scripts(skill_dir: Path) -> set[str]:
    docs = [skill_dir / "SKILL.md",
            *sorted((skill_dir / "references").glob("*.md"))]
    refs: set[str] = set()
    for doc in docs:
        if doc.is_file():
            refs.update(SCRIPT_REF.findall(doc.read_text(encoding="utf-8")))
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
    if not frontmatter_ok(skill_dir / "SKILL.md"):
        return False
    outdir.mkdir(parents=True, exist_ok=True)
    zpath = outdir / f"{name}.skill"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, rel in ship_files(skill_dir):
            zf.write(path, f"{name}/{rel.as_posix()}")
        shipped = set(zf.namelist())
    wanted = [f"{name}/SKILL.md"] + [f"{name}/scripts/{ref}"
                                     for ref in sorted(referenced_scripts(skill_dir))]
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
