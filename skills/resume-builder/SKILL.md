---
name: resume-builder
description: Build, rewrite, tailor, or improve a resume/CV and render it as an ATS-safe tagged PDF. Use whenever the user wants a resume created or updated, asks to tailor one to a job posting, mentions applying to jobs/internships/grad programs, or shares career materials (old resume, LinkedIn export, transcript, project list) — even if they never say the word "resume". Also use when someone asks "turn my experience into a CV" or wants their resume converted to a cleaner format.
---

# resume-builder

Turn a person's real experience into a one-page, evidence-based resume,
rendered with Typst as a tagged PDF that survives 2026 screening
pipelines — then prove it survives them.

**The loop is build → test → iterate.** A resume is not done when the
PDF exists; it is done when `resume-evaluator` passes it. Anyone can
generate a resume; the value here is the verification loop and the
honesty discipline.

Non-negotiables, because screening stacks now detect all three:
- **Never fabricate** — no invented employers, titles, dates, metrics,
  or degrees. Weak sections get flagged to the user, not padded.
- **Never stuff keywords** — semantic match beats token match; screeners
  flag manipulation.
- **Never hide text** — white text, microscopic text, off-page text.
  The evaluator's L2 check will catch it anyway; vendors' checks do too.

Read `references/screening-2026.md` once per session before drafting —
it explains what the pipeline you're writing for actually does, and why
each rule below exists.

## Workflow

### 1. Intake — meet the material where it lives

Users don't follow filing rituals. Adapt to however material shows up:

- **Already in the conversation** — pasted text, attachments, offhand
  mentions. Inventory it first; never ask the user to re-supply or
  relocate something they already provided.
- **On disk** — ask where things live and read them in place. Offer
  (never auto-run) a scan of the obvious spots — cwd, Desktop,
  Downloads, Documents — for resume-shaped files: `*resume*`, `*cv*`,
  `*transcript*`, LinkedIn's `Profile.pdf`.
- **Remote pointers** — GitHub profiles/repos and personal sites are
  fetchable; use connected tools (Drive, Notion, …) when available.
  LinkedIn pages don't scrape: ask for LinkedIn's "Save to PDF" export
  (Profile → More → Save to PDF) instead.
- **Nothing at all** — interview instead. Ask for: education + dates,
  every job/internship/research stint (org, title, dates, what they
  did), projects with links, skills they can defend. One batch of
  questions, then drill into the two or three strongest items.

Messy is fine — extraction is your job. After inventory, ask **one
focused batch** of gap questions, only about things that change the
resume: missing dates, missing numbers, unclear scope, target field and
level. Don't interrogate; don't ask for what you already have.

### 2. Workspace — before writing anything personal

Confirm where working files (`resume.yaml`, rendered PDFs) will live.
If that location is inside a git repository, check the paths are
ignored (`git check-ignore`) and offer to add ignores *before* writing.
Career data silently landing in someone's tracked repo is a real harm.

### 3. Identify the field, load its conventions

Infer target field + seniority from materials and stated goal; confirm
with the user in one line. Then read the matching reference:

- AI/ML/LLM/agents roles → `references/fields/ai-ml.md`
- software engineering → `references/fields/swe.md`
- anything else → `references/fields/generic.md` (a research procedure,
  not static rules — follow it)

### 4. Tailor against a posting (when one exists)

If the user has a target job posting, invoke the `jd-analyzer` skill on
it and keep its output file: it becomes the tailoring target now and
the evaluator's scoring rubric later. No posting → build a strong
general version for the field; say so and move on.

### 5. Draft evidence, not prose

Read `references/writing-rules.md` before writing any bullet. For each
experience: extract claims from the material, demand quantification
(ask the user for numbers rather than inventing ranges), attach a
concrete artifact where possible (repo, paper, launched thing). Apply
the bullet formula; run the AI-slop checklist. If a section is thin,
tell the user it's thin and what would strengthen it — do not pad.

### 6. Content → `resume.yaml`

Write the data file per `assets/templates/data-schema.md` (read it
first — dates are `YYYY-MM` strings, absence means "don't render",
strings with `:` need quoting). Content and presentation stay fully
separated: the yaml holds finished prose; templates never rewrite it.

### 7. Render

```sh
scripts/render.sh path/to/resume.yaml            # -> resume.pdf next to it
scripts/render.sh resume.yaml -t onecol -o out.pdf
```

Requires Typst ≥ 0.15 (`brew install typst` / see
`references/typst-guide.md` for other platforms and troubleshooting).
One page for students and early-career; the script warns on budget
overflow. If it overflows, cut content by priority (typst-guide has the
order) — never shrink fonts below 9.5pt or margins below 1.2cm.

### 8. Verify — mandatory, not optional

Run the `resume-evaluator` skill on the rendered PDF (with the
jd-analyzer output if step 4 ran). Fix what it reports, re-render,
re-run until L0–L3 pass clean. Show the user the final report. If the
evaluator skill isn't installed, run its scripts directly from its
`scripts/` directory and say the judgment layers (L4/L5) were skipped.

**Do not present a PDF to the user as finished before it has passed.**

## Iterating with the user

Show the rendered PDF (or its page image) alongside the evaluator
report. Take edits back through the yaml — never hand-edit the PDF, and
re-run the evaluator after every render. Small honest improvements over
polish theater: a new number beats a fancier verb.
