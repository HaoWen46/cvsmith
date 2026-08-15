#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pdf2image>=1.17", "pillow>=10.0"]
# ///
"""Build evaluator PDFs from reviewable fixture sources."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RENDER = REPO / "skills/resume-builder/scripts/render.sh"
GOOD = HERE / "resume-sample/resume.yaml"


def run(command: list[str]) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        sys.exit(f"error: {' '.join(command)}\n{result.stdout}{result.stderr}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=HERE / "build")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if not shutil.which("typst"):
        sys.exit("error: typst not found")
    run([str(RENDER), str(GOOD), "-o", str(args.out / "good.pdf")])
    for source in sorted((HERE / "broken-src").glob("*.typ")):
        run(["typst", "compile", str(source), str(args.out / f"{source.stem}.pdf")])
    from pdf2image import convert_from_path
    pages = [page.convert("RGB") for page in convert_from_path(str(args.out / "good.pdf"), dpi=150)]
    pages[0].save(args.out / "image_only.pdf", save_all=True, append_images=pages[1:])
    built = sorted(path.name for path in args.out.glob("*.pdf"))
    print(f"built {len(built)} fixtures: {', '.join(built)}")


if __name__ == "__main__":
    main()
