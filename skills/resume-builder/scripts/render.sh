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

# Read a scalar from the yaml's meta: block only — scoped so a folded
# prose line elsewhere can never hijack a knob, and sanitized so quoted
# values and CRLF files (pasted from Windows/web) behave like bare ones.
meta_val() {
  awk -v k="$1:" '
    seen && $1 == k { gsub(/["'\''\r]/, "", $2); print $2; exit }
    /^meta:/ { seen=1 }
    seen && /^[^ #]/ && !/^meta:/ { exit }
  ' "$DATA"
}

# Template precedence: -t flag > meta.template in the yaml > onecol.
# Projections carry their own template so re-renders stay one command.
if [ -z "$TEMPLATE" ]; then
  TEMPLATE=$(meta_val template)
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

# Schema validation before compile: a typoed optional key or section
# name renders a clean-looking PDF with content silently missing —
# the one failure the smoke checks can't see. Clear yaml paths beat
# cryptic typst errors for the required-key class too. No uv, no
# render: skipping the gate is exactly the silent-loss hole it closes.
if command -v uv >/dev/null; then
  uv run --script "$SCRIPT_DIR/validate_yaml.py" "$DATA" || exit 1
else
  echo "error: uv not found — schema validation is required; install it: https://docs.astral.sh/uv/" >&2
  exit 1
fi

# Build in a scratch dir: typst's file access is rooted there, so the
# compile sees exactly the template set + one data file and nothing else.
# Compile lands in a dot-temp beside $OUT (same filesystem, so the final
# mv is atomic — $BUILD may be another fs); the gates read the temp and
# $OUT is replaced only after every gate passes, so a failed build never
# destroys the previous good PDF.
BUILD=$(mktemp -d)
trap 'rm -rf "$BUILD"' EXIT
# mktemp gives the temp (and so the final PDF) mode 600 — deliberate:
# rendered resumes carry the same personal data as their projections.
TMP_OUT=$(mktemp "$(dirname "$OUT")/.render-XXXXXX")
trap 'rm -rf "$BUILD"; rm -f "$TMP_OUT"' EXIT
cp "$TEMPLATES_DIR"/*.typ "$BUILD"/
cp "$DATA" "$BUILD"/data.yaml
cat > "$BUILD"/main.typ <<EOF
#import "$TEMPLATE.typ": render
#render(yaml("data.yaml"))
EOF

# -f pdf: mktemp can't carry a .pdf suffix, so name-based inference is off.
typst compile -f pdf --pdf-standard ua-1,a-2a --font-path "$FONTS_DIR" --ignore-system-fonts \
  "$BUILD"/main.typ "$TMP_OUT"

# L0 smoke: a resume whose text layer is tiny will never survive parsing.
if command -v pdftotext >/dev/null; then
  chars=$(pdftotext "$TMP_OUT" - | tr -d '[:space:]' | wc -c | tr -d ' ')
  if [ "$chars" -lt 200 ]; then
    echo "error: extracted text layer is suspiciously small ($chars chars)" >&2
    exit 1
  fi
else
  echo "note: pdftotext not found — skipped extraction smoke check" >&2
fi

if command -v pdfinfo >/dev/null; then
  pages=$(pdfinfo "$TMP_OUT" | awk '/^Pages:/ {print $2}')
  budget=$(meta_val page_budget)
  if [ -n "${budget:-}" ] && [ "$pages" -gt "$budget" ]; then
    echo "warning: $pages pages exceeds page_budget $budget" >&2
  fi
fi

# Bullet-line discipline: meta.bullet_lines caps rendered lines per
# bullet, measured from the PDF's geometry (the render is the truth;
# character counts are only a pencil sketch). Violations fail the build.
# With no cap set, the measurement still prints — two-line bullets must
# be a visible choice, never an invisible accident.
blimit=$(meta_val bullet_lines)
if [ -n "${blimit:-}" ]; then
  if command -v uv >/dev/null; then
    uv run --script "$SCRIPT_DIR/check_bullets.py" "$TMP_OUT" --max-lines "$blimit" || exit 1
  else
    echo "error: meta.bullet_lines is set but uv not found — install it: https://docs.astral.sh/uv/" >&2
    exit 1
  fi
else
  uv run --script "$SCRIPT_DIR/check_bullets.py" "$TMP_OUT" \
    || echo "warning: bullet measurement failed — wrap state unknown" >&2
fi

mv -f "$TMP_OUT" "$OUT"
echo "rendered: $OUT"
