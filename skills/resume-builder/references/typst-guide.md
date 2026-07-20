# Typst guide — templates, rendering, troubleshooting

## The pieces

- `assets/templates/onecol.typ` — default template. Exposes one
  function: `render(data)`. Pure function of the yaml data; fixed
  section order; real H1/H2 tags in the PDF structure tree.
- `assets/templates/data-schema.md` — the `resume.yaml` contract.
  Read it before writing yaml.
- `assets/fonts/source-sans-3/` — vendored OFL fonts, so rendering is
  identical on every machine. Templates pin "Source Sans 3".
- `scripts/render.sh` — the only supported way to compile:

```sh
scripts/render.sh resume.yaml                 # -> resume.pdf next to the yaml
scripts/render.sh resume.yaml -t onecol -o /path/out.pdf
```

It compiles with `--pdf-standard ua-1,a-2a` (tagged PDF/UA-1 +
PDF/A-2a), `--ignore-system-fonts` (vendored fonts only), then smoke-
checks the text layer and the page budget. Don't call `typst compile`
directly for real output — you'd lose the standards flags and checks.

## Requirements

- Typst ≥ 0.15: `brew install typst` (macOS), `snap install typst` or
  the GitHub release binary (Linux), `winget install --id Typst.Typst`
  (Windows). Check with `typst --version`.
- For the smoke checks: poppler (`pdftotext`, `pdfinfo`) — optional
  but recommended (`brew install poppler` / `apt install poppler-utils`).

## Hard constraints discovered the hard way

- **PDF/UA-1 export fails without a document title.** Templates must
  always call `set document(title: ..., author: ...)` — onecol.typ
  derives both from `basics.name`. If you write a new template, keep
  this or renders break with "missing document title".
- **YAML gotchas that break compiles or data:** quote strings
  containing `:` (`"GPA: 3.8"` → quote it), quote phone numbers
  (`"+1 ..."` — else YAML may parse oddly), dates stay strings
  (`2025-06` is fine unquoted; `present` is a literal), apostrophes
  inside single-quoted YAML need doubling — prefer double quotes.
- **Absence over emptiness:** omit a section key entirely rather than
  leaving `[]` — templates render what exists.

## Page-overflow triage (in cut order)

When render.sh warns the page budget is exceeded, cut in this order —
never shrink type below 9.5pt or margins below 1.2cm to squeeze:

1. Coursework/honors lines in Education
2. Weakest bullet of the weakest Projects entry (or the entry itself)
3. Third/fourth bullets on minor experience entries
4. Summary (it was optional anyway)
5. Oldest minor experience entry

## Writing a new template

Keep these invariants or the evaluator will fail your output:
single column; sections via `heading(level: 2)` with standard names;
name via `heading(level: 1)`; no `place()` overlaying text; no text
outside the page box; fonts from the vendored set (or extend the font
check in render.sh); document title/author set. Add the template as
`assets/templates/<name>.typ` exposing `render(data)` — render.sh and
CI pick it up automatically by filename.

## Troubleshooting

| Symptom | Cause → fix |
|---|---|
| `missing document title` | template didn't `set document(title: ...)` |
| `unknown font family: Source Sans 3` | fonts dir missing/moved — render.sh checks this; keep `assets/fonts/` intact |
| yaml error `expected string, found int` | unquoted value YAML typed as number (GPA, phone) — quote it |
| bullets render as one paragraph | yaml list item wrapped wrong — each bullet is one `- ` list entry |
| overfull page | see cut order above; check `page_budget` warning from render.sh |
| weird glyph boxes in PDF | character outside font coverage — replace exotic Unicode (fancy quotes/arrows) with plain equivalents |
