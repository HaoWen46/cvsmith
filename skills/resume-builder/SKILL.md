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

**Research discipline.** Bundled references are the doctrine; trust
them within their `Verify by:` windows instead of re-researching per
task (same question must get the same answer, or iteration stops being
measurable). Fetch fresh only what is *task-scoped*: the posting, the
company, the user's links. Full tier rules + external-tool catalog:
`references/tools-and-sources.md` — read it when tempted to search
the web for screening/market facts, or when a PDF defeats the bundled
extractors.

## Workflow

### 1. Intake — meet the material where it lives

**Check for a career vault first.** If `career-vault.md` exists in the
workspace (or the user has one elsewhere), read it and ask only what's
new — never re-interview a person whose answers are already on file.
No vault yet? Create one as intake proceeds: every extracted fact and
every answer lands there as well as in the resume. Read
`references/career-vault.md` for the format and the projection rules —
the vault is what makes repeat applications cheap and twenty tailored
variants mutually honest.

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

### 3. Identify the field, market, and level

Infer target field + seniority **and target market** (the job's
country/region — not the user's) from materials and stated goal;
confirm all three in one line. The market sets paper size, language,
page budget, and the photo/personal-data rules. US/Canada target →
**skip `references/regional.md` entirely**; its baseline is already
this toolkit's default. Any other market, or multi-market plans →
read it (one canonical vault, one projection per market; never blend
conventions; it also covers markets it doesn't list). Then read the matching field
reference:

- AI/ML/LLM/agents roles → `references/fields/ai-ml.md`
- software engineering → `references/fields/swe.md`
- grad school, REUs, fellowships, research programs →
  `references/fields/academic.md` (different reader, different
  emphasis; supports research/teaching/industry experience grouping)
- anything else → `references/fields/generic.md` (a research procedure,
  not static rules — follow it)

The target also decides *who reads the output*: HR pipelines (parse +
embed + rank), faculty (15-second human skim, no ranking), or both.
Mechanical parse-safety rules stay constant — they cost nothing and
university HR layers parse too — but evidence emphasis follows the
reader.

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

## When the user is wrong about mechanics

Users own their story; the toolkit owns verified mechanics. When a
requested change conflicts with what the evaluator measures (two-column
layout, creative headings, contact in a graphic, keyword blocks):

1. **Show, don't argue** — run the relevant script on a version with
   their change and show the concrete failure. Evidence persuades
   where opinion doesn't.
2. **Offer the split** — a parse-safe version for portals/uploads and
   a styled version for humans they'll hand it to directly. Both from
   the same yaml; different templates. This resolves most standoffs.
3. **If they still insist**: comply on aesthetics (their document,
   their call), record the failed checks in the final evaluator report
   without softening, and say plainly which uses it's unsafe for.
4. **Never comply on integrity** — hidden text, invented facts,
   microscopic keywords. Not at any level of insistence. Explain that
   detectors flag these as manipulation and the flag attaches to the
   *person*, then offer the honest alternative for whatever gap the
   trick was meant to cover.
