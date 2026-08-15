# Objective failure modes

Use this only after an objective layer reports the corresponding problem; the report identifies observable PDF behavior, not an employer outcome.

## L0 extraction

- Little or no text: rebuild from editable source instead of submitting an image-only export.
- Broken character mapping: re-export with embedded mapped fonts or rebuild through the supplied renderer.
- Extractors recover materially different words: simplify the PDF construction and rerun both extractors.
- Poppler unavailable: install it and rerun; a single-extractor warning is an environment limitation.

## L1 routing sanity

- No standard sections: rename creative headings to conventional labels such as Experience, Projects, Education, and Skills.
- Name or email missing from the header block: render them as ordinary visible text before the first section.
- Experience dates not recognized: use a conventional month-or-year range and inspect extracted text order.
- Unknown heading warning: inspect the extraction; rename a real section, or ignore an entry line falsely shaped like a heading.

L1 recognizes a small English heading and contact vocabulary; it is a sanity check, not a reproduction of a named parser.

## L2 integrity

- Invisible, transparent, background-matched, microscopic, zero-width, or off-page text: remove it and render the intended visible content normally.
- Metadata injection or bulk keywords: clear the hostile document metadata and regenerate the PDF.
- Metadata identity mismatch: correct or remove stale author metadata.
- Raster unavailable: install Poppler and rerun before treating invisible content as checked.

## L3 structure

- Likely multiple columns: redesign into one linear content column; dates and entry metadata stay inline.
- Image-only page: rebuild as real text.
- Unembedded fonts: export with embedding or use the supplied renderer.
- Page budget exceeded: cut or restructure content; the budget is author-provided, not universal.
- Untagged PDF or unusual page size: inspect as a compatibility warning unless the target explicitly requires otherwise.

## Escalation

If a clean-looking third-party PDF triggers a geometry heuristic, inspect the page and extraction before changing it; if the warning is a false positive, report the concrete geometry rather than adding a resume-specific exception.

After any fix, rerender from source and rerun the affected layer against the new PDF hash.
