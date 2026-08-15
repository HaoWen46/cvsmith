---
name: resume-builder
description: Use when the user asks to create, rewrite, tailor, or improve a resume or CV for a chosen role, field, or job description; turn prepared candidate evidence into editable YAML and a rendered PDF; or revise resume content or layout after evaluation. Do not use for durable candidate-evidence intake alone, JD analysis alone, PDF review alone, application tracking, or interview preparation.
---

# resume-builder

Build the strongest role-specific resume the candidate can safely defend; the objective is a credible interview opportunity, not a completed template or high internal score.

All `scripts/`, `references/`, and `assets/` paths below are relative to this skill directory.

## Read only what the task needs

- Always read `assets/templates/data-schema.md`, `references/writing-rules.md`, and the matching `references/fields/<field>.md` before drafting.
- Read `references/regional.md` when the target market is unsettled and `references/typst-guide.md` when choosing or debugging a template.
- Use sibling skills by their own instructions: `candidate-evidence` for durable source intake or refresh, `jd-analyzer` for a posting, `resume-evaluator` for the exact PDF, and `application-tracker` only after handoff or submission.

## Inputs and privacy

Require one target brief plus `candidate-evidence/index.md`; accept selected evidence documents, decisive original sources, relevant application learnings, and a legacy `career-vault.md` when available.

If candidate evidence is absent, stale, or missing supplied material, invoke `candidate-evidence` first with candidate sources only; do not perform broad repository, report, portfolio, or archive intake inside this skill.

Treat a legacy career vault as source material for the current run and use `candidate-evidence` for any durable update or repeated-use migration.

Confirm the output directory before writing private files, warn when it is cloud-synced, verify intended private paths are ignored inside a repository, and explain once that hosted agents process content they read.

## Fix the target

When a posting exists, run `jd-analyzer`, use its separate disposable brief, and settle binary eligibility gates before spending work on the resume; stop target-specific polishing after a failed gate unless the user explicitly wants a reusable draft.

Without a posting, state the assumed field, level, market, and page budget and label the result general rather than pretending it was validated for a specific role.

Use relevant application-ledger learnings only as scoped associations that may motivate a variant; never treat outcomes as candidate evidence or proof that wording caused a response.

## Compare the whole evidence index

The main agent reads every substantive capsule in the complete Active and Archive sections before its first target-specific disposition; names, dates, tags, lifecycle labels, or repository metadata alone cannot eliminate an item.

Compare each capsule against eligibility, ranked evidence demands, plausible technical or outcome signal, distinctiveness, ownership risk, currentness needs, uncertainty, redundancy, and page competition.

Keep every body that could plausibly cover an uncovered priority, displace a current contender, or resolve a decision-changing uncertainty; use no fixed project quota, age cutoff, fashionable-technology preference, or numeric selection formula.

All target-specific rankings, reserves, omissions, and page decisions belong only to this resume's working state and compact decision report; never write them into durable candidate evidence.

## Study finalists

The main agent opens detailed evidence documents for plausible contenders and enough decisive original material to form its own view of technical depth, result quality, ownership, currentness, target relevance, and interview value.

Use relevant authored code and tests, benchmark method and data, report methods and results, releases, history, records, or candidate answers; a README, evidence capsule, or subagent summary may orient the read but cannot replace stronger originals that could change the decision.

When a selected raw source needs substantial investigation or a durable fact changes, invoke `candidate-evidence`; subagents may collect bounded source facts there, but the main agent reviews their records, opens decisive originals, and makes every comparative and resume decision.

If a finalist weakens under primary review, promote and study a reserve under the same rule; the whole repository or report remains optional unless reading it could change selection or claim safety.

After source review, ask one compact question batch only for answers that could change eligibility, ownership, selection, measurement, currentness, claim safety, or interview defensibility.

## Allocate before prose

Write one private thesis sentence stating the identity the page should establish and the two or three evidence bodies that carry it; record it in `meta.thesis`, which never renders.

Derive three to five target beliefs from the thesis and ranked requirements, decompose contender evidence into causal atoms, and make atoms compete for each page slot.

A causal atom is candidate action -> load-bearing mechanism -> result or artifact; keep that chain intact, let one atom produce at most one bullet, and split only when another independent action, result, or target belief earns space.

Record each candidate row as `target belief | source atom | core result or artifact | load-bearing mechanism | optional scale or quality signal | overflow`, then route distinct useful overflow to an uncovered belief, reusable interview facts to `candidate-evidence`, and duplicate or incidental payload out of the projection.

No broad source discovery resumes after allocation unless verification exposes a specific gap that could materially change a selected claim or body of work.

## Draft for practical effect

Apply `references/writing-rules.md`: record-risk facts must survive ordinary record or reference checks, while assertive framing is acceptable when the candidate can explain it naturally under skeptical interview probing and no realistic contradiction is exposed.

Phrase selected rows one-for-one; every bullet should carry one target belief through the intact action, mechanism, and result or artifact, with a scale or quality signal only when it materially strengthens that belief.

Every rendered bullet must occupy exactly one physical line; when one wraps, remove the weakest payload, tighten the mechanism or result, or promote a distinct high-value atom instead of shrinking type or joining unrelated claims.

Use posting vocabulary only where visible evidence supports it, choose `onecol` by default, use `compact` for dense early-career material, and use `classic` only when its register fits the target.

Keep the page socially ordinary: no hidden text, keyword stuffing, fake public artifacts, inflated titles, decorative ratings, generated-sounding filler, or tricks a recruiter would regard as manipulation.

## Render, verify, and inspect

Create fresh YAML following `assets/templates/data-schema.md`; never edit a prior target's projection in place when doing so could erase what was sent.

The compatibility field `meta.vault` may point to `candidate-evidence/index.md`; ensure every selected record value, number, URL, and skill appears in an active substantive capsule before running the projection scanner.

Render with:

```sh
scripts/render.sh /absolute/path/resume.yaml -o /absolute/path/resume.pdf
```

When an evidence index exists, run:

```sh
uv run scripts/check_projection.py /absolute/path/resume.yaml /absolute/path/candidate-evidence/index.md --json
```

Fix exact record, number, URL, and skill mismatches, then review every listed claim and lifecycle note directly against selected evidence and decisive originals; the scanner does not pair claims to sources or judge meaning.

Open every rendered page at normal size and fix clipping, wrapping, weak hierarchy, dense walls, conspicuous accidental whitespace, or anything that looks unfinished; accept intentional whitespace when honest evidence is exhausted rather than padding or manipulating type.

## Evaluate and iterate

Invoke `resume-evaluator` with the current PDF, YAML, evidence index, selected evidence documents, and target brief; after any content or layout change, re-render and rerun affected checks because the artifact changed.

Fix eligibility and exposure first, then target coverage, hierarchy, and writing; redesign a bad line or section instead of layering exceptions around it.

Stop only when the evaluator says `READY TO SEND` and no accessible high-value improvement remains, or report the exact blocker; a score threshold, green test, or attractive page alone is not completion.

## Handoff

Lead with the final PDF, editable YAML, evaluation report, target, and recommendation; label the artifact `UNREVIEWED` and list remaining checks when no evaluator was available.

Include one compact table with `selected or omitted evidence | target reason | decisive source read | remaining risk`; distinguish consequential exclusions from globally weak evidence without writing target decisions into the evidence workspace.

Offer `application-tracker` after delivery; a prepared row records the artifact, and only confirmed submission makes it applied.
