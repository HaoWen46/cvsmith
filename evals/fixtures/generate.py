#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pdf2image>=1.17",
#     "pillow>=10.0",
# ]
# ///
"""Build the fixture PDFs the evaluator tests run against.

Fixtures are generated, not committed: binary PDFs in git rot, while
sources stay reviewable. The good fixture goes through the real render
path (render.sh); each planted failure compiles from broken-src/*.typ;
the image-only fixture is the good PDF rasterized and re-wrapped.

usage: generate.py [--out DIR]   (default: evals/fixtures/build/)
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent
REPO_ROOT = FIXTURES_DIR.parent.parent
RENDER_SH = REPO_ROOT / "skills/resume-builder/scripts/render.sh"
GOOD_YAML = FIXTURES_DIR / "resume-sample/resume.yaml"


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"error: {' '.join(map(str, cmd))}\n{proc.stdout}{proc.stderr}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=FIXTURES_DIR / "build")
    args = ap.parse_args()
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    if not shutil.which("typst"):
        sys.exit("error: typst not found — needed to build fixtures")

    # the good one, through the real pipeline
    run(["bash", str(RENDER_SH), str(GOOD_YAML), "-o", str(out / "good.pdf")])

    # the planted failures
    for src in sorted((FIXTURES_DIR / "broken-src").glob("*.typ")):
        run(["typst", "compile", str(src), str(out / f"{src.stem}.pdf")])

    # image-only: what "I exported my resume as pictures" looks like to an ATS
    from pdf2image import convert_from_path
    pages = convert_from_path(str(out / "good.pdf"), dpi=150)
    rgb = [p.convert("RGB") for p in pages]
    rgb[0].save(out / "image_only.pdf", save_all=True, append_images=rgb[1:])

    built = sorted(p.name for p in out.glob("*.pdf"))
    print(f"built {len(built)} fixtures in {out}: {', '.join(built)}")


if __name__ == "__main__":
    main()
