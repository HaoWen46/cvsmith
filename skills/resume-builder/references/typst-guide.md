# Typst rendering guide

Use `scripts/render.sh`; it validates the YAML, compiles a tagged PDF with vendored fonts, checks extraction and page fill, rejects wrapped bullets, and publishes only after those steps finish.

```sh
scripts/render.sh /absolute/path/resume.yaml -o /absolute/path/resume.pdf
scripts/render.sh /absolute/path/resume.yaml -t classic -o /absolute/path/resume.pdf
```

## Templates

- `onecol`: neutral default for an unknown or mixed register.
- `compact`: denser modern presentation; `meta.accent` controls its restrained accent color.
- `classic`: monochrome serif presentation for a conservative register.

All templates use the same linear content renderer and display every content key in `assets/templates/data-schema.md`; template choice changes presentation, not content coverage.

Choose by the target's register and show alternatives when the user has a real preference; do not choose a template merely because its fill measurement is larger.

## Requirements

- Typst 0.15 or newer.
- Poppler for `pdftotext`, `pdfinfo`, and raster-based checks.
- The bundled Inter and Source Serif 4 font directories intact.

## Page triage

When the page exceeds its budget, cut weak or redundant material before touching typography: marginal coursework or honors, the weakest project or bullet, repeated mechanism, optional summary, then the oldest minor entry.

When a bullet wraps, return to its evidence-allocation row: remove the weakest optional signal, tighten the selected mechanism or result, or split a distinct high-value atom that earns an uncovered requirement; do not solve a content decision with typography.

When the fill check warns, inspect the rendered page; recover stronger available evidence or ask one focused question, then accept intentional whitespace when the material is exhausted.

Do not shrink below the shipped sizes, squeeze margins, add filler, repeat claims, or switch templates solely to move the fill number.

## Template invariants

A template must keep standard section headings, visible text inside the page box, a real document title and author, a single linear reading order, and vendored embedded fonts.

Add a template only for a presentation need the existing three cannot meet; implement it as `assets/templates/<name>.typ` exposing `render(data)`, add its name to `validate_yaml.py`, and verify the same fixture through the full evaluator battery.

## Common failures

- Unknown template or font: use an existing template and keep `assets/fonts/` intact.
- YAML parse error: quote values containing `: ` and keep list entries as strings.
- Missing document title: restore `set document(...)` in the shared renderer.
- Overfull page: use the cut order above.
- Weak extraction or odd reading order: redesign the layout and rerender; do not add extraction-only text.
