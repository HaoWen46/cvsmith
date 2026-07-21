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
Conversely, L4/L5 are judgment — scripts can't do them; they need a
reader, and *which* reader matters (see "Judgment layers need a cold
reader" before scoring either).

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
- Scope note for non-English CVs: L0/L2/L3 are language-agnostic;
  L1's heading taxonomy is English-only — say so in the report rather
  than scoring localized headings as routing failures.

## Judgment layers need a cold reader

L0–L3 are scripts — context can't bias them. L4/L5 are judgment, and
judgment from the context that *wrote* the resume is compromised: you
know what every bullet meant to say, so you cannot simulate the
recruiter who doesn't. **When the host supports subagents, dispatch
L4/L5 to a fresh-context agent** whose entire input is: the rendered
PDF (or its page image), the jd-analyzer output if one exists, and
`references/rubric.md` — no conversation history, no vault, no build
notes. Its cold read is the product; merge its scores and findings
into the report, attributed as a cold read.

No subagent support (or reviewing a PDF you didn't build — already
cold)? Run L4/L5 yourself, and counter familiarity deliberately: skim
the page image before re-reading any source, and for each bullet ask
what a stranger would think it says — not what you know it means.
Say in the report which mode produced the judgment scores.

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

When an integrity finding (L2) drives the verdict, include a one-line
"see it yourself" so the user doesn't have to take the report on
faith: *open the PDF, select all (Cmd/Ctrl-A), copy into a text
editor — anything that appears there but not on the page is the
hidden content.* Users act faster on findings they can reproduce.

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
harness as broken — *unless* the traceback names a missing tool
(poppler): that is an environment gap, never a file verdict.

The report never softens to match anyone's preference — not the
user's, not the builder's. If the user overrode a mechanical
recommendation and the checks fail, the report says so and names the
uses the file is unsafe for. A reassuring false PASS is the one output
this skill must never produce.

Scoring doctrine (rubric, failure modes) is bundled and stable within
its verify-by windows — don't re-research "what ATSs do" mid-
evaluation; changing rubrics between iterations makes scores
incomparable. Task inputs (the PDF, the JD analysis) are always
current by construction.
