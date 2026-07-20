# Failure-mode catalog — symptom → detection → fix

The recurring ways resumes die in machine screening, what the harness
shows when they do, and the concrete fix. Grows from real-world
reports; when you meet a new mode, add it here with the same shape.

## Extraction failures (L0)

### Image-based PDF
- **Symptom**: `text_layer` FAIL, ~0 chars extracted. Common causes:
  scanned paper, "export as image" from design tools (Canva, Figma,
  Photoshop), photographed documents.
- **Why fatal**: the ATS sees literally nothing; OCR at the vendor
  side is rare and unreliable for layout.
- **Fix**: rebuild from source material through the builder; there is
  no patch for pixels. (Design-tool users: they may still have the
  editable source to export text-first.)

### Broken font encoding
- **Symptom**: `encoding` FAIL — replacement chars (�) or gibberish in
  extraction while the page *looks* fine.
- **Cause**: subsetted fonts without a ToUnicode map (some LaTeX
  setups, some print-driver "PDFs", some design exports).
- **Fix**: re-export from the original tool with embedded+mapped
  fonts, or rebuild. Verify with `extract_text.py --dump`.

### Parser disagreement
- **Symptom**: `extractor_agreement` FAIL/WARN — pdftotext and pypdf
  recover different content.
- **Cause**: exotic PDF constructs (form XObjects for text, weird
  transparency groups, content in annotations).
- **Fix**: re-export as vanilla PDF (print-to-PDF often normalizes);
  rebuild if persistent. Different ATS stacks use different parsers —
  agreement is the safety margin.

## Routing failures (L1)

### Creative section headings
- **Symptom**: `core_sections` FAIL / `unknown_headings` listing lines
  like "My Journey", "What I Bring".
- **Fix**: rename to standard headings (Experience, Projects, Skills,
  Education). Personality lives in bullets, not in section names.

### Contact info the parser can't find
- **Symptom**: `contact_email` FAIL or `name_line` FAIL.
- **Causes**: contact in an image or icon-decorated header, name in a
  graphic, email split by styling, header/footer regions some parsers
  strip.
- **Fix**: name as the first text line, email/phone as plain text
  directly under it. Icons decorate; they must never *replace* text.

### Unparseable dates
- **Symptom**: `experience_dates` FAIL — entries exist, no ranges
  parse.
- **Causes**: "Summer 2024", "6/24–9/24", dates buried mid-sentence,
  tables that separate dates from entries.
- **Fix**: "Jun 2024 – Sep 2024" format, visually attached to its
  entry. Gap-detection features misread missing dates as gaps.

## Integrity failures (L2) — the career-enders

### Hidden/white text
- **Symptom**: `invisible_text` FAIL, hidden content quoted in the
  report.
- **Reality**: production detectors run this exact cross-modal check
  and treat hits as manipulation/injection. This doesn't lose a few
  ranking points; it flags the candidate, sometimes account-wide.
- **Fix**: delete the hidden content entirely. Then address honestly
  whatever gap the stuffing was compensating for (that's a builder +
  jd-analyzer conversation).

### Microscopic / zero-width tricks
- **Symptom**: `microscopic_text` or `zero_width_chars` FAIL.
- **Fix**: same as above — remove, then solve the real gap. Zero-width
  characters sometimes arrive *accidentally* via copy-paste from web
  pages; still remove them (detectors don't ask about intent).

## Structure failures (L3)

### Multi-column layout
- **Symptom**: `single_column` FAIL with the column position named.
- **Why**: parsers read in different orders (left-block-first,
  row-wise, tag-order); columns scramble at least one of them —
  sentences interleave, dates detach from entries.
- **Fix**: single column. The information density loss is smaller than
  the parse-risk gain; use the compact spacing knobs instead.

### Unembedded fonts
- **Symptom**: `fonts_embedded` FAIL naming the fonts.
- **Fix**: re-export with embedding on (cvsmith templates always
  embed the vendored set). Non-embedded text renders differently —
  or not at all — on the parser's machine.

### Tables as layout
- **Symptom**: often surfaces as L0 disagreement or L1 date failures
  rather than a dedicated check — table cell order is parser-defined.
- **Fix**: no tables for entry layout. Right-aligned meta via the
  template's grid is fine (it keeps one text line per entry row).

### Multi-page for early-career
- **Symptom**: `page_budget` FAIL.
- **Fix**: cut in the typst-guide's order (coursework → weakest
  project bullet → minor-entry bullets → summary → oldest minor
  entry). Two pages of thin content reads worse than one dense page —
  to machines (diluted embedding relevance) and humans (skim cost)
  alike.

## Not failures (don't "fix" these)

- **Untagged PDF** (`tagged_pdf` WARN) on third-party resumes: most
  tools don't tag; parsing still works geometrically. cvsmith output
  is always tagged — treat the warn as a rebuild nudge, not a defect.
- **pdftotext missing** (`extractor_agreement` WARN): environment
  limitation, not a resume property. Install poppler for full checks.
- **Right-aligned dates**: not a second column; the L3 detector is
  specifically built to tell them apart.
- **Raw content-stream order ≠ visual order** on grid rows (dates
  emitted before/after titles depending on extractor mode): layout-
  aware extraction and the tag tree both read correctly, token
  agreement stays 1.0, and L1 parses line-wise. Real but low-severity;
  not worth breaking the meta column over.
- **En-dash date ranges** ("Jun 2025 – Sep 2025"): a strictly
  ASCII-hyphen regex misses these, but every real extractor and L1's
  range parser handle the en dash, and it's the typographically
  correct range mark. Kept deliberately; a parser too naive for en
  dashes fails a dozen other universals first. (Recorded so it isn't
  relitigated every audit.)
