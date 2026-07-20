---
name: resume-evaluator
description: Test, score, and stress-check any resume PDF the way 2026 screening pipelines do — ATS parseability, hidden-text/integrity screening, structure lint, job-description alignment, and a recruiter-skim critique. Use whenever the user asks "is my resume good / ATS-safe / will it pass screening", shares a resume PDF for review or feedback, wants two resume versions compared, or after ANY resume is generated or re-rendered (the builder's output is not done until this passes).
---

# resume-evaluator

Adversarial test harness for resume PDFs. Four deterministic script
layers (L0–L3) reproduce what screening machinery does; two judgment
layers (L4–L5) reproduce what the humans after it do. Output is one
fixed-format report with a ranked fix list.

**Deterministic layers are scripts only — never eyeball them.** Your
eyes cannot see a missing text layer, a scrambled extraction order, or
white text; the scripts exist because vision is the wrong instrument.
Conversely, L4/L5 are judgment — scripts can't do them; you run those
with your own reading.

## Running the battery

Scripts live in `scripts/` (self-contained; `uv run` resolves their
deps from inline metadata — plain `python3` works if pypdf, pdfplumber,
pdf2image, Pillow are installed; poppler recommended for L0's
second extractor and required by pdf2image).

```sh
uv run scripts/extract_text.py resume.pdf --json        # L0 extraction
uv run scripts/parse_sim.py resume.pdf --json           # L1 field routing
uv run scripts/hidden_text_check.py resume.pdf --json   # L2 integrity
uv run scripts/lint_structure.py resume.pdf --json --page-budget 1  # L3
```

Run all four, always, in that order (each exits 0 pass / 1 fail; the
JSON lists per-check `pass`/`warn`/`fail` with details). Page budget:
1 for students/early-career unless the user's field says otherwise.

- `extract_text.py --dump` prints the extracted text in reading order —
  read it yourself for L0 judgment calls and to sanity-check that what
  the machine sees is what the page shows.
- A `warn` is not a `fail`: report it, weigh it, don't block on it
  (e.g. untagged PDFs from other tools still parse).

## L4 — JD alignment (judgment, rubric-guided)

Only when a job posting / jd-analyzer output exists. Read
`references/rubric.md` §L4, then score how well the resume's *evidence*
covers the posting's ranked requirements: per-requirement coverage
(strong evidence / weak evidence / absent), natural vocabulary overlap,
and misallocated space (strong evidence for things the JD doesn't ask).
Name the gaps precisely — "no evidence against requirement 2
(distributed systems); the queueing bullet could carry it if scale
were stated" — so the builder can act.

No JD available? Skip L4, say so in the report.

## L5 — human simulation (judgment, rubric-guided)

Read `references/rubric.md` §L5. Two passes over the *rendered page*
(view the PDF or its raster, not the yaml):

1. **Six-second skim**: what actually lands — name, current role/
   school, one or two bullets, brands? Is the strongest fact visible
   without reading?
2. **Skeptical deep read**: which claims feel inflated, vague, or
   AI-generated? What would a picky senior engineer probe in an
   interview? Any bullet that survives neither a number nor an
   artifact check gets named.

## Report — always this exact structure

```
# Resume evaluation: <file>

## Verdict
<one line: READY / NOT READY + the single most important reason>

## Deterministic layers
| Layer | Result | Notes |
|---|---|---|
| L0 extraction | PASS/FAIL | ... |
| L1 parse sim | PASS/FAIL | ... |
| L2 integrity | PASS/FAIL | ... |
| L3 structure | PASS/FAIL | ... |

## L4 — JD alignment (skipped if no JD)
<coverage score /10 + per-requirement table: requirement, evidence, strength>

## L5 — recruiter simulation
<what landed in 6s; what a skeptic flags; score /10>

## Fix list (ranked)
1. <highest-impact fix, concrete>
2. ...
```

## Iteration protocol

When invoked from the builder: report → builder fixes yaml → re-render
→ re-run **everything** (fixes shift layout; L2/L3 can regress). Loop
until L0–L3 pass and L4/L5 have no ranked fix the user declined.
Standalone on a third-party PDF: same battery; for fixes, recommend
the failure-modes catalog (`references/failure-modes.md`) — it maps
every common failure to its concrete fix, and offer the builder skill
for a rebuild when the PDF is beyond patching (image-based, two-column
template, etc.).

If a script crashes on a malformed PDF, that *is* a finding: report the
file as unparseable (what a vendor pipeline would conclude), not the
harness as broken.

The report never softens to match anyone's preference — not the
user's, not the builder's. If the user overrode a mechanical
recommendation and the checks fail, the report says so and names the
uses the file is unsafe for. A reassuring false PASS is the one output
this skill must never produce.
