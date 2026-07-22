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

Grab the `.skill` files from the
[latest release](https://github.com/HaoWen46/cvsmith/releases) and add
them to your agent's skills (Claude Code: save under `~/.claude/skills/`
or use your client's skill-import), or clone this repo and point your
agent at `skills/`. Each skill installs and runs standalone — fonts
vendored, scripts carrying inline dependencies (`uv run` just works) —
but the four compose into one workflow, and a skill running without
its siblings degrades explicitly rather than silently: the builder
without the evaluator labels its output UNVERIFIED, without
jd-analyzer it marks its inline posting analysis as a degraded
substitute, and without the tracker it logs only a minimal ledger row.
**Install all four for the advertised loop**; the minimum useful pair
is resume-builder + resume-evaluator, because the builder's definition
of done is the evaluator passing.

## Status

**v0.1.1** — all milestones complete, hardened by four external review rounds:

- [x] **M0–M3** — Scaffold, render path, evaluator harness, the first three skills + references
- [x] **M4** — Eval loop: 18 agent runs across two model tiers (Fable 5 and Sonnet 5 executors), one run per eval/condition — directional, not statistical. With-skill swept both iterations (100% of assertions vs 67%/81% for baselines), though some assertions check the skill's own contract, and two with-skill runs saw grading metadata (scores stand on objective checks). Three repo bugs were found *by* the runs and fixed
- [x] **M5** — Worked example ([examples/ai-ml-intern](examples/ai-ml-intern)), three templates spanning the register axis, packaged `.skill` releases
- [x] **Review hardening (v0.1.1)** — Four adversarial review rounds folded in, every finding reproduced before fixing: fail-closed integrity gate (transparent-text and XMP channels covered, unverified never passes), render/validation guards against silent source loss, fabrication-class identity checks, application-tracker update semantics, a stricter packaging contract, byte-reproducible renders, and claims aligned to documented vendor behavior (92 planted-fixture tests)

## Requirements

- [Typst](https://typst.app/) ≥ 0.15 (PDF/UA-1 tagged output)
- [uv](https://docs.astral.sh/uv/) — runs the schema-validation gate in `render.sh` and the evaluator scripts (`uv sync` sets up the test environment)
- Poppler (`pdftotext`) for extraction checks

## A note on personal data

The skills read your materials wherever they already live — pasted into chat, attached, or in place on disk. Nothing has to be moved into any particular folder, and the builder checks that a workspace path is gitignored before writing personal data into any git repo. One honest boundary: the *files* (vault, ledger, projections) are never transmitted by these skills, but anything quoted into the conversation is processed by whatever host runs your agent — a cloud-hosted session sends that text to its model provider like any other message. If you develop *inside this checkout*, `materials/`, `output/`, and `drafts/` are pre-gitignored for scratch use. Everything under `evals/fixtures/` and `examples/` is synthetic or sanitized — real career materials never belong in this repo.

## License

[MIT](LICENSE)
