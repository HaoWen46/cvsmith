#!/usr/bin/env bash
# resume.yaml -> validated, tagged PDF through the selected Typst template.
set -euo pipefail

usage() { echo "usage: $0 <resume.yaml> [-t template] [-o out.pdf]" >&2; exit 2; }

[ $# -ge 1 ] || usage
DATA=$1
shift
TEMPLATE=""
OUT=""
while getopts "t:o:" opt; do
  case "$opt" in
    t) TEMPLATE=$OPTARG ;;
    o) OUT=$OPTARG ;;
    *) usage ;;
  esac
done

[ -f "$DATA" ] || { echo "error: data file not found: $DATA" >&2; exit 2; }
command -v uv >/dev/null || { echo "error: uv not found" >&2; exit 2; }
command -v typst >/dev/null || { echo "error: typst >= 0.15 is required" >&2; exit 2; }

meta_value() {
  awk -v key="$1:" '
    in_meta && $1 == key { gsub(/["'\''\r]/, "", $2); print $2; exit }
    /^meta:/ { in_meta=1; next }
    in_meta && /^[^ #]/ { exit }
  ' "$DATA"
}

if [ -z "$TEMPLATE" ]; then
  TEMPLATE=$(meta_value template)
  TEMPLATE=${TEMPLATE:-onecol}
fi

SCRIPT_DIR=$(cd -- "$(dirname -- "$0")" && pwd)
SKILL_DIR=$(dirname "$SCRIPT_DIR")
TEMPLATES_DIR=$SKILL_DIR/assets/templates
FONTS_DIR=$SKILL_DIR/assets/fonts
TEMPLATE_FILE=$TEMPLATES_DIR/$TEMPLATE.typ
[ -f "$TEMPLATE_FILE" ] || { echo "error: unknown template: $TEMPLATE" >&2; exit 2; }

if [ -z "$OUT" ]; then
  filename=$(basename "$DATA")
  OUT=$(dirname "$DATA")/${filename%.*}.pdf
fi
case "$OUT" in
  *.pdf) ;;
  *) echo "error: output must end in .pdf: $OUT" >&2; exit 2 ;;
esac
if [ -e "$OUT" ] && [ "$OUT" -ef "$DATA" ]; then
  echo "error: output path is the input file: $OUT" >&2
  exit 2
fi

if [ -z "${SOURCE_DATE_EPOCH:-}" ]; then
  SOURCE_DATE_EPOCH=$(stat -c %Y "$DATA" 2>/dev/null || stat -f %m "$DATA" 2>/dev/null || echo 0)
  export SOURCE_DATE_EPOCH
fi

font_list=$(typst fonts --font-path "$FONTS_DIR" --ignore-system-fonts 2>&1 || true)
missing_fonts=""
for family in "Inter" "Source Serif 4"; do
  printf '%s\n' "$font_list" | grep -qx "$family" || missing_fonts="$missing_fonts '$family'"
done
if [ -n "$missing_fonts" ]; then
  echo "error: vendored fonts unavailable:$missing_fonts" >&2
  exit 2
fi

uv run --script "$SCRIPT_DIR/validate_yaml.py" "$DATA" --template "$TEMPLATE"

named_vault=$(meta_value vault)
if [ -n "$named_vault" ]; then
  VAULT=$(dirname "$DATA")/$named_vault
  [ -r "$VAULT" ] || { echo "error: meta.vault is not readable: $VAULT" >&2; exit 2; }
else
  VAULT=$(dirname "$DATA")/career-vault.md
fi

if [ -e "$VAULT" ] && [ ! -r "$VAULT" ]; then
  echo "warning: projection check COULD NOT RUN: vault is unreadable; source exposure is UNCHECKED" >&2
elif [ -r "$VAULT" ]; then
  projection_code=0
  uv run --script "$SCRIPT_DIR/check_projection.py" "$DATA" "$VAULT" || projection_code=$?
  case "$projection_code" in
    0) ;;
    1) echo "warning: objective resume/vault mismatches remain; fix them before sending" >&2 ;;
    2) echo "warning: projection scan could not run; source exposure is unchecked" >&2 ;;
    *) echo "error: projection scan returned unexpected exit $projection_code" >&2; exit 2 ;;
  esac
else
  echo "note: projection check skipped: no career vault found; source exposure is UNCHECKED" >&2
fi

BUILD_DIR=$(mktemp -d)
TEMP_PDF=$(mktemp "$(dirname "$OUT")/.render-XXXXXX")
cleanup() { rm -rf "$BUILD_DIR"; rm -f "$TEMP_PDF"; }
trap cleanup EXIT
cp "$TEMPLATES_DIR"/*.typ "$BUILD_DIR"/
cp "$DATA" "$BUILD_DIR"/data.yaml
printf '#import "%s.typ": render\n#render(yaml("data.yaml"))\n' "$TEMPLATE" > "$BUILD_DIR"/main.typ

typst compile -f pdf --pdf-standard ua-1,a-2a --font-path "$FONTS_DIR" --ignore-system-fonts "$BUILD_DIR"/main.typ "$TEMP_PDF"

if command -v pdftotext >/dev/null; then
  extracted_chars=$(pdftotext "$TEMP_PDF" - | tr -d '[:space:]' | wc -c | tr -d ' ')
  [ "$extracted_chars" -ge 200 ] || { echo "error: extracted text is too small ($extracted_chars characters)" >&2; exit 1; }
else
  echo "note: pdftotext unavailable; extraction smoke check skipped" >&2
fi

page_budget=$(meta_value page_budget)
if [ -n "$page_budget" ]; then
  uv run --script "$SCRIPT_DIR/check_fill.py" "$TEMP_PDF" --budget "$page_budget"
else
  uv run --script "$SCRIPT_DIR/check_fill.py" "$TEMP_PDF"
fi

uv run --script "$SCRIPT_DIR/check_bullets.py" "$TEMP_PDF" --max-lines 1

mv -f "$TEMP_PDF" "$OUT"

sha256() {
  if command -v sha256sum >/dev/null; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

echo "rendered: $OUT"
echo "pdf sha256: $(sha256 "$OUT")"
echo "yaml sha256: $(sha256 "$DATA")"
