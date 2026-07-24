# cvsmith

**Agent skills that teach AI agents how to build, tailor, and adversarially test resumes — rendered with Typst, verified with the same classes of checks modern screening stacks run.**

Not a resume generator, not a SaaS checker. cvsmith is a set of portable skills (SKILL.md + references + scripts, Claude Code / Cowork / Agent SDK compatible) that make any capable agent behave like an expert resume engineer with a verification loop: **build → test → iterate**, like TDD for resumes.

## Why

As of 2026, most high-volume resume screening runs some version of an LLM-mediated pipeline — parse → structure → embed against the job description → score → rank — though vendors differ in mechanism (Workday's HiredScore grades against requisition requirements, Greenhouse matches recruiter-weighted criteria, Ashby checks per-criterion and surfaces a sortable fit percentage). cvsmith targets the strictest common denominator, which changes what a good resume tool must do:

- **Parsing is the gate.** If extraction fails, no intelligence ever evaluates the candidate. Single-column, text-layer, tagged PDFs with standard headings are cvsmith's non-negotiables — the strictest-common-denominator choice, engineered for the most conservative documented parser behavior rather than any vendor's best case.
- **Keyword stuffing is dead and harmful.** Modern screeners use semantic matching and flag manipulation. The target is honest semantic coverage of the JD, not token overlap.
- **Hidden text is detected, and the flag sticks to the person.** Production detectors cross-check rendered pixels against extracted text; documented vendor responses range from recruiter-visible manipulation flags to automated rejection. A builder must *prove* it produced nothing that looks like hidden content.
- **Generic AI prose is a negative signal.** Differentiators are specificity, quantification, and verifiable claims.

The moat is the **evaluator**: a test harness that runs a PDF through the same classes of checks screening stacks use.

## The skills

| Skill | One-liner |
|---|---|
| `resume-builder` | Interview the user, ingest raw materials, draft evidence-based content, render via Typst templates |
| `resume-evaluator` | Adversarial test harness: parse simulation, hidden-text check, structure lint, JD-alignment scoring, recruiter-skim critique |
| `jd-analyzer` | Decompose a job posting into ranked requirements, vocabulary, and evidence targets to tailor against |
| `application-tracker` | Track applications and outcomes in a ledger beside the vault — prepared vs. applied kept distinct so callback rates stay honest |

Design principles, full component specs, and the research base live in [PROJECT_PLAN.md](PROJECT_PLAN.md).

## Quickstart (render path)

Write a `resume.yaml` following the
[data schema](skills/resume-builder/assets/templates/data-schema.md)
(sample: [`evals/fixtures/resume-sample/resume.yaml`](evals/fixtures/resume-sample/resume.yaml)), then:

```sh
skills/resume-builder/scripts/render.sh path/to/resume.yaml
```

Output is a tagged PDF/UA-1 + PDF/A-2a file rendered with vendored fonts
— same layout and text on every machine, and byte-identical when the
same data file is re-rendered — smoke-checked for a healthy text layer.

## Install

This repo is **private**, and its GitHub release always lags the
working tree — a tag gets cut only when the maintainer chooses to, so
the checkout can (and often does) carry fixes no release or `main` has
yet. Pick the path that matches what you actually have access to.

Either way, Claude Code discovers *personal* skills only at
`~/.claude/skills/<skill-name>/SKILL.md` — a `.skill` zip has to be
**extracted** there (or the skill directory symlinked/copied there),
not saved as-is; a `.skill` file sitting directly in `~/.claude/skills/`
has no `SKILL.md` at a path Claude Code looks for and never loads.
*(Personal-skill discovery path last verified against Claude Code's
docs: 2026-07, verify by: 2027-07.)*

### Primary: from a checkout (matches this tree exactly, no release needed)

Clone or pull this repo, then either point your agent at `skills/`
directly — the checkout is already laid out as
`skills/<skill-name>/SKILL.md`, no extraction needed — or symlink each
skill into the path Claude Code discovers, which stays live across
future `git pull`:

```sh
mkdir -p ~/.claude/skills
for skill in resume-builder resume-evaluator jd-analyzer application-tracker; do
  rm -rf ~/.claude/skills/"$skill"
  ln -s "$(pwd)/skills/$skill" ~/.claude/skills/"$skill"
done
```

The `rm -rf` is not optional if you have ever installed these from a
`.skill` zip. `ln -sf` does **not** replace an existing *directory*:
it creates the link *inside* it (`~/.claude/skills/resume-builder/
resume-builder`), the previously extracted copy stays exactly where
Claude Code discovers it, and you keep running the old version while
believing you are on the checkout. Verify what you actually got:

```sh
ls -l ~/.claude/skills | grep -E 'resume-|jd-analyzer|application-tracker'
```

Each of the four must show as a symlink (`->` your checkout). A plain
directory means an extracted copy is still in place.

Or build the same `.skill` zips the releases ship, from your checkout,
without waiting on a tag:

```sh
uv run scripts/package_release.py    # writes dist/<skill>.skill
mkdir -p ~/.claude/skills
for skill in resume-builder resume-evaluator jd-analyzer application-tracker; do
  unzip -o "dist/$skill.skill" -d ~/.claude/skills/
done
```

Confirm each landed where Claude Code looks:

```sh
ls ~/.claude/skills/*/SKILL.md
```

### Secondary: GitHub Releases (requires repo access; reflects the last tag, not this tree)

[github.com/HaoWen46/cvsmith/releases](https://github.com/HaoWen46/cvsmith/releases)
404s for anyone without collaborator access — the repo isn't public,
and there's no plan to change that here. If you *do* have access:

```sh
gh auth login   # once, if `gh auth status` isn't already logged in
gh release download --repo HaoWen46/cvsmith --pattern '*.skill' --dir /tmp/cvsmith-release
mkdir -p ~/.claude/skills
for skill in resume-builder resume-evaluator jd-analyzer application-tracker; do
  unzip -o "/tmp/cvsmith-release/$skill.skill" -d ~/.claude/skills/
done
```

The release is a snapshot of whatever commit was last tagged — it can
be behind an active checkout (this one included) by any number of
unreleased commits. When in doubt, use the primary path above.

Each skill installs and runs standalone — fonts
vendored, scripts carrying inline dependencies (`uv run` just works) —
but the four compose into one workflow, and a skill running without
its siblings degrades explicitly rather than silently: the builder
without the evaluator labels its output UNVERIFIED, without
jd-analyzer it marks its inline posting analysis as a degraded
substitute, and without the tracker it logs only a minimal ledger row.
**Install all four for the advertised loop**; the minimum useful pair
is resume-builder + resume-evaluator, because the builder's definition
of done is the evaluator's — and the evaluator's is not "MECHANICAL
and TARGET FIT both READY". Those two say the CV is honest and
on-target; the third surface, CRAFT, says whether it is worth sending,
and a CRAFT band of ≤6 is `NOT DONE` however many READY lines sit
beside it (`skills/resume-evaluator/SKILL.md`, "CRAFT"). Done means
all three.

## Status

**v0.1.2** — eight external review rounds folded in; 298 planted-fixture tests:

- [x] **M0–M3** — Scaffold, render path, evaluator harness, the first three skills + references
- [x] **M4** — Eval loop: 18 agent runs across two model tiers (Fable 5 and Sonnet 5 executors), one run per eval/condition — directional, not statistical. With-skill swept both iterations (100% of assertions vs 67%/81% for baselines), though some assertions check the skill's own contract, and two with-skill runs saw grading metadata (scores stand on objective checks). Three repo bugs were found *by* the runs and fixed
- [x] **M5** — Worked example ([examples/ai-ml-intern](examples/ai-ml-intern)), three templates spanning the register axis, packaged `.skill` releases
- [x] **Review hardening (v0.1.1)** — Four adversarial review rounds folded in, every finding reproduced before fixing: fail-closed integrity gate (transparent-text and XMP channels covered, unverified never passes), render/validation guards against silent source loss, fabrication-class identity checks, application-tracker update semantics, a stricter packaging contract, byte-reproducible renders, and claims aligned to documented vendor behavior
- [x] **Review hardening (v0.1.2)** — Four further review rounds, every finding reproduced before fixing. Projection checker: denied vault material (NOT-CLAIMABLE / PENDING-EVIDENCE / prose denials / Gaps & flags) now fails closed for numbers, dates, URLs, skills, **and qualitative claims**; whole-token identity/URL/entry matching (no substring collisions); ownership-scoped, complete-value contact checks (email/phone/location); reversed-metric detection in either word order, plus dropped-negation ("no reduction in X" included) and worsened-outcome tripwires. Evaluator: CRAFT gates run completion, with an explicit `## Run status`, an evidence-based gate-status rule (persisted analysis → attached facts → user statement → unconfirmed), a coherent no-JD completion state, and a page-economy (dense-but-underfull) craft criterion. Reports — projection output, README tallies, and the eval-report's L0/L2 metrics — are freshness-tested against live script runs, not just the PDF. **Known gaps, disclosed not hidden:** (1) truth-checking is lexical, so a semantic synonym swap in a long line can still pass — the always-on claim→source pairing table plus human/evaluator attestation is the actual guarantee, not the mechanical tripwires; (2) the suite exercises the deterministic tooling, not live agent-following-contract behavior — that needs a model-in-the-loop eval harness, still unbuilt

## Requirements

- [Typst](https://typst.app/) ≥ 0.15 (PDF/UA-1 tagged output)
- [uv](https://docs.astral.sh/uv/) — runs the schema-validation gate in `render.sh` and the evaluator scripts (`uv sync` sets up the test environment)
- Poppler (`pdftotext`) for extraction checks

## A note on personal data

The skills read your materials wherever they already live — pasted into chat, attached, or in place on disk. Nothing has to be moved into any particular folder, and the builder checks that a workspace path is gitignored before writing personal data into any git repo. One honest boundary: the *files* (vault, ledger, projections) are never transmitted by these skills, but anything quoted into the conversation is processed by whatever host runs your agent — a cloud-hosted session sends that text to its model provider like any other message. If you develop *inside this checkout*, `materials/`, `output/`, and `drafts/` are pre-gitignored for scratch use. Everything under `evals/fixtures/` and `examples/` is synthetic or sanitized — real career materials never belong in this repo.

## License

[MIT](LICENSE)
