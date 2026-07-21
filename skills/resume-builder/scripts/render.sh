#!/usr/bin/env bash
# render.sh — resume.yaml -> tagged, ATS-safe PDF via Typst.
#
#   usage: render.sh <resume.yaml> [-t template] [-o out.pdf]
#
# Defaults: template "onecol", output next to the data file (<stem>.pdf).
# Compiles with PDF/UA-1 + PDF/A-2a and only the vendored fonts, so output
# is identical on every machine and always carries a tagged structure tree.
# Runs a light extraction smoke check; the full battery is resume-evaluator's.
set -euo pipefail

usage() { echo "usage: $0 <resume.yaml> [-t template] [-o out.pdf]" >&2; exit 2; }

[ $# -ge 1 ] || usage
DATA=$1; shift
TEMPLATE=""
OUT=""
while getopts "t:o:" opt; do
  case $opt in
    t) TEMPLATE=$OPTARG ;;
    o) OUT=$OPTARG ;;
    *) usage ;;
  esac
done

[ -f "$DATA" ] || { echo "error: data file not found: $DATA" >&2; exit 1; }

# Template precedence: -t flag > meta.template in the yaml > onecol.
# Projections carry their own template so re-renders stay one command.
if [ -z "$TEMPLATE" ]; then
  TEMPLATE=$(awk '$1 == "template:" {print $2; exit}' "$DATA")
  TEMPLATE=${TEMPLATE:-onecol}
fi

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
SKILL_DIR=$(dirname "$SCRIPT_DIR")
TEMPLATES_DIR=$SKILL_DIR/assets/templates
FONTS_DIR=$SKILL_DIR/assets/fonts
TPL=$TEMPLATES_DIR/$TEMPLATE.typ
[ -f "$TPL" ] || { echo "error: no such template: $TEMPLATE (in $TEMPLATES_DIR)" >&2; exit 1; }

command -v typst >/dev/null || { echo "error: typst not found (need >= 0.15): https://typst.app" >&2; exit 1; }

if [ -z "$OUT" ]; then
  base=$(basename "$DATA")
  OUT=$(dirname "$DATA")/${base%.*}.pdf
fi

# The templates pin vendored fonts; fail loudly if typst can't see them.
for fam in "Source Sans 3" "Inter" "Source Serif 4"; do
  if ! typst fonts --font-path "$FONTS_DIR" --ignore-system-fonts | grep -q "^$fam$"; then
    echo "error: vendored font '$fam' not found under $FONTS_DIR" >&2
    exit 1
  fi
done

# Build in a scratch dir: typst's file access is rooted there, so the
# compile sees exactly the template set + one data file and nothing else.
BUILD=$(mktemp -d)
trap 'rm -rf "$BUILD"' EXIT
cp "$TEMPLATES_DIR"/*.typ "$BUILD"/
cp "$DATA" "$BUILD"/data.yaml
cat > "$BUILD"/main.typ <<EOF
#import "$TEMPLATE.typ": render
#render(yaml("data.yaml"))
EOF

typst compile --pdf-standard ua-1,a-2a --font-path "$FONTS_DIR" --ignore-system-fonts \
  "$BUILD"/main.typ "$OUT"

# L0 smoke: a resume whose text layer is tiny will never survive parsing.
if command -v pdftotext >/dev/null; then
  chars=$(pdftotext "$OUT" - | tr -d '[:space:]' | wc -c | tr -d ' ')
  if [ "$chars" -lt 200 ]; then
    echo "error: extracted text layer is suspiciously small ($chars chars)" >&2
    exit 1
  fi
else
  echo "note: pdftotext not found — skipped extraction smoke check" >&2
fi

if command -v pdfinfo >/dev/null; then
  pages=$(pdfinfo "$OUT" | awk '/^Pages:/ {print $2}')
  budget=$(awk '$1 == "page_budget:" {print $2; exit}' "$DATA")
  if [ -n "${budget:-}" ] && [ "$pages" -gt "$budget" ]; then
    echo "warning: $pages pages exceeds page_budget $budget" >&2
  fi
fi

# Opt-in bullet-line discipline: meta.bullet_lines caps rendered lines
# per bullet, measured from the PDF's geometry (the render is the truth;
# character counts are only a pencil sketch). Violations fail the build.
blimit=$(awk '$1 == "bullet_lines:" {print $2; exit}' "$DATA")
if [ -n "${blimit:-}" ]; then
  if command -v uv >/dev/null; then
    uv run --script "$SCRIPT_DIR/check_bullets.py" "$OUT" --max-lines "$blimit" || exit 1
  else
    echo "warning: meta.bullet_lines set but uv not found — bullet check skipped" >&2
  fi
fi

echo "rendered: $OUT"
