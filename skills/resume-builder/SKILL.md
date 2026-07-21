---
name: resume-builder
description: 'Build, rewrite, tailor, or improve a resume/CV and render it as an ATS-safe tagged PDF. Use whenever the user wants a resume created or updated, asks to tailor one to a job posting, mentions applying to jobs/internships/grad programs, or shares career materials (old resume, LinkedIn export, transcript, project list) — even if they never say the word "resume". Also use for "turn my experience into a CV" or converting a resume to a cleaner format, and to start or update a career vault (career-vault.md). Strongest for English-language, one-page, student/early-career resumes into any market: headings and month names render in English, section order is fixed (education first), and there are no dedicated certification/license/spoken-language sections yet. Standardized non-English forms (Japanese rirekisho), multi-page senior-academic CVs, USAJOBS federal formats, and design portfolios are out of template scope — still invoke the skill so it can say what transfers and help honestly.'
---

# resume-builder

Turn a person's real experience into a one-page, evidence-based resume,
rendered with Typst as a tagged PDF that survives 2026 screening
pipelines — then prove it survives them.

**The loop is build → test → iterate.** A resume is not done when the
PDF exists; it is done when `resume-evaluator` passes it.

Non-negotiables, because modern screening stacks can detect all three:
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
every answer lands there as well as in the resume. Before the first
vault write, say in one line what it will store — full history
including gaps with true reasons, visa details, references, the Q&A
log — and offer three modes: full vault; minimal vault (FACT lines
only — no Gaps & flags ledger, no CONTEXT references); session-only
(no persistent vault, resume yaml only). State the trade-off
honestly: minimal and session-only weaken the honesty ledger and the
evaluator's gap-check. Hold the vault's
first disk write until the step-2 workspace gate — it is the most
sensitive file this skill produces. Read
`references/career-vault.md` for the format and the projection rules —
the vault is what makes repeat applications cheap and twenty tailored
variants mutually honest. Vault on file and a new posting in hand:
intake collapses to "what's new since <updated>?" — reuse the
confirmed workspace and jump to step 4 (steps 3 and 5 still re-derive
market and register from the new posting, never from the last
application).

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

Confirm where working files (`career-vault.md`, yaml projections,
jd-analysis output, rendered PDFs, `application-ledger.md`) will live.
If that location is inside a git repository, check the paths are
ignored (`git check-ignore`) and offer to add ignores *before* writing.
Career data silently landing in someone's tracked repo is a real harm.
Two more checks while confirming: if the location sits inside a
cloud-synced folder (iCloud/Drive/Dropbox), say so — gitignore does
not stop a sync client from uploading the vault; and after the first
write, `chmod 600` the vault, its projections, rendered PDFs, and
evaluator/cold-read output on POSIX systems — the whole workspace
carries the same personal data. The copy actually sent with an
application is unaffected.

### 3. Identify the field, market, and level

Identify target field + seniority **and target market** (the job's
country/region — not the user's). Posting on hand? Run step 4 first
and take market and level from its decoded-level line; field you
still infer from the posting and materials. No posting? Infer all
three from materials and stated goal. Confirm all three in one line.
The market sets paper size, language, page budget, and the
photo/personal-data rules. US/Canada target → **skip
`references/regional.md` entirely**; its baseline is already this
toolkit's default. Any other market, or multi-market plans → read it
(it also covers markets it doesn't list). Then read the matching field
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
the evaluator's scoring rubric later. If an analysis file for this
posting already exists from an earlier session, check its seen-date
before tailoring against it: the posting is task input (fetched fresh
at use), so if the date is weeks old, re-fetch the source first —
gone means warn the user the role may be closed; changed means
re-analyze. No posting → build a strong general version for the
field; say so and move on.

### 5. Draft evidence, not prose

Read `references/writing-rules.md` before writing any bullet — and
apply its Register section first: name the industry × market ×
employer-type cell you're writing for, out loud. The default
energetic-tech tone is a *choice*, and for a German bank or a UK
ministry it's the wrong one.

Know your budgets before drafting, not after: pick the template
candidate now (the register cell decides — typst-guide §Choosing a
template; step 7 still confirms with the user), then calibrate —
render a throwaway skeleton yaml written per data-schema.md (basics,
one entry, three deliberately overlong bullets) through
`scripts/render.sh -t <candidate>` and run `scripts/check_bullets.py`
on the PDF for measured line capacity; three bullets, not one, so the
wrapped-line medians have enough votes. Plan the space division —
bullets per entry, chars per bullet — so the first real render
confirms rather than discovers. Decide the bullet discipline now, in
the yaml: set `meta.bullet_lines: 1` unless the register genuinely
wants two-line bullets, and leave a `# why` comment when it does. An
unset knob is a decision by omission — render.sh prints the measured
wrap state either way, and that report is not for scrolling past.
When a check does fail, the failure
carries information: escalate per the writing-rules ladder;
re-rendering unchanged text is not an attempt.

For each experience: extract claims from the material, demand
quantification (ask the user for numbers rather than inventing
ranges), attach a concrete artifact where possible (repo, paper,
launched thing). Apply the bullet formula; run the AI-slop checklist.
If a section is thin, tell the user it's thin and what would
strengthen it — do not pad.

### 6. Content → the data file

Write the data file per `assets/templates/data-schema.md` (read it
first — dates are `YYYY-MM` strings, absence means "don't render",
strings with `:` need quoting). Content and presentation stay fully
separated: the yaml holds finished prose; templates never rewrite it.
Tailoring to a posting? Name the file `resume-<company>-<role>.yaml`
next to the vault so applications accumulate instead of overwriting;
a general version is plain `resume.yaml`.

render.sh validates the file against the schema first — fix its
findings before reading any typst error. When drafting from a vault,
also run `scripts/check_projection.py resume.yaml career-vault.md` —
a missing hard fact means the vault gets the fact, with the user's
answer, before the yaml keeps it.

### 7. Render

```sh
scripts/render.sh path/to/resume.yaml            # -> resume.pdf next to it
scripts/render.sh resume.yaml -t compact -o out.pdf
```

Three templates ship, one data contract, identical parse-safety —
`compact` (designed/dense — tech, startups, AI/ML), `classic`
(serif/conservative — banking, consulting, law, government), `onecol`
(neutral default). Confirm step 5's candidate with the user and
record the pick as `meta.template` in the yaml so re-renders need no
flag; selection detail and the show-both-pages flow:
`references/typst-guide.md` §Choosing a template.

Requires Typst ≥ 0.15 (`brew install typst` / see
`references/typst-guide.md` for other platforms and troubleshooting).
One page for students and early-career; the script warns on budget
overflow. If it overflows, cut content by priority (typst-guide has the
order) — never squeeze a fit by shrinking type below the sizes the
template ships with, or margins below its shipped margins.

### 8. Verify — mandatory, not optional

Run the `resume-evaluator` skill on the rendered PDF (with the
jd-analyzer output if step 4 ran). Fix what it reports, re-render,
re-run until L0–L3 pass clean. Show the user the final report.
`check_projection` also prints a directional metric-pair audit —
confirm each pair it lists for manual review against the vault before
shipping.

This applies to *every* later edit, not just the first build: folding
in an answer, a cold-read fix, or a cut re-runs the same render and
the same checks — the bullet report in the render output is part of
what you read each time. A revision pass that ships a new two-line
bullet unnoticed is the exact failure the knob exists to prevent.

You wrote this resume, so your judgment of it is compromised by
familiarity — **dispatch the evaluator's L4/L5 to a fresh-context
subagent when the host supports it** (cold-reader protocol: the
evaluator's SKILL.md). If the evaluator skill isn't installed, run
its scripts directly from its `scripts/` directory and say the
judgment layers were skipped or self-run. If neither the skill nor
its scripts are reachable (this skill installed standalone), say so
plainly and hand over the PDF labeled UNVERIFIED — render.sh's smoke
check is not the battery, and L0–L3 are never judged by eye; offer to
install `resume-evaluator` (ships beside this skill in the cvsmith
releases) before the user submits anywhere.

**Do not present a PDF to the user as finished before it has passed.**

### 9. After the send

When a projection ships for a real application, offer — in one line —
to log a **prepared** row (channel + sent version) in
`application-ledger.md` beside the vault; the row turns applied only
when the user confirms submission, never at render. Respect a no.
Outcome updates and funnel reads are the `application-tracker`
skill's job (installed beside this skill); if it is absent, read and
append the ledger directly using its format — same degradation
pattern as the evaluator. Format and doctrine ship with
application-tracker: its `references/application-ledger.md`.

## Iterating with the user

Show the rendered PDF (or its page image) alongside the evaluator
report. Take edits back through the yaml — never hand-edit the PDF, and
re-run the evaluator after every render. Any new fact surfaced
mid-loop — a number the user supplies, an artifact, a correction —
enters the vault first, then the yaml (corrections supersede per the
vault's CUT rule); the projection invariant holds during iteration,
not just at intake. Small honest improvements over polish theater: a
new number beats a fancier verb.

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
