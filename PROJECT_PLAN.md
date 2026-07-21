# cvsmith — Project Plan

**Agent skills that teach AI agents how to build, tailor, and adversarially test resumes — rendered with Typst, verified with the same classes of checks 2026 screening stacks run.**

Living doc: architecture, principles, status, and roadmap. Workflow
detail lives in the three `SKILL.md` files (source of truth); this file
holds what spans them. History lives in git, not here.
Last updated: 2026-07-21.

---

## 1. Problem statement (why this exists)

As of mid-2026, most high-volume resume screening runs some version of
an LLM-mediated pipeline: **parse → structure into fields → embed
against the job description → score → rank**. Design assumptions (a
conservative model of 2026 screening; sources §9; perishable claims
live under freshness stamps in
`skills/resume-builder/references/screening-2026.md`):

1. **Parsing is the gate.** If extraction fails or sections misroute,
   the candidate is eliminated before any intelligence evaluates them.
2. **Keyword stuffing is dead and actively harmful.** Screeners use
   semantic matching and flag manipulation; the target is honest
   semantic coverage, not token overlap.
3. **Hidden text is detected and punished.** Production detectors
   cross-check rendered pixels against extracted text (86–93%
   precision, ~$0.0001–0.01/file — arXiv 2605.28999). A builder must
   *prove* it produced nothing that looks like hidden content.
4. **Generic AI prose is a negative signal.** Polish is free now;
   differentiators are specificity, quantification, verifiable claims.
5. **The market is a barbell.** Entry-level tech postings down, AI
   postings growing — field-aware tailoring is the leverage point.

Existing tools are static SaaS checkers or scripts wrapping an LLM API.
cvsmith is neither: portable agent skills (SKILL.md conventions —
Claude Code / Cowork / Agent SDK, readable by any framework honoring
them) that make a capable agent behave like an expert resume engineer
with a verification loop.

## 2. Product principles

1. **Evaluator > builder.** Anyone can generate a resume; the moat is
   the harness that runs a PDF through the same classes of checks
   screening stacks use.
   Build → test → iterate — TDD for resumes. A resume is done when it
   *passes*, not when it exists.
2. **Skills, not services.** No server, no API keys on the core path.
   Deterministic checks are bundled scripts; judgment runs on the host
   agent.
3. **Honesty is a feature.** Never fabricate, never stuff, never hide
   text — and the evaluator proves it. Ethics and self-interest agree
   here (detection is real). The evaluator's report never softens to
   please anyone; a reassuring false PASS is the one forbidden output.
4. **Meet users where they are.** No filing rituals, no required
   folders, no assumption this repo is even present. Intake adapts to
   pasted text, attachments, files in place, remote pointers, or
   nothing at all.
5. **The vault makes it persistent.** One user-owned `career-vault.md`
   is the exhaustive evidence base; every resume is a *projection* of
   it (per target: `resume-<company>-<role>.yaml`). Projections never
   contain a fact the vault lacks — that invariant keeps N tailored
   variants simultaneously honest, and makes application #14 cost
   minutes. A file, not agent memory: the user owns and ports it.
6. **Conventions follow the target, not the user.** Two axes beyond
   field: *audience* (HR pipeline vs. faculty reader vs. both) and
   *market* (the job's country, never the user's). Parse mechanics are
   invariant everywhere; evidence emphasis, register, paper, language,
   and personal-data rules follow the target.
7. **Activate, don't enumerate.** For vast situational knowledge
   (register across industry × culture, unlisted markets/fields),
   references name the axis, pin the invariants, and aim the model's
   own latent knowledge via procedure: name the cell, sample 2–3 real
   artifacts from it, confirm with the user. Literal text is reserved
   for what latent knowledge gets wrong: post-cutoff screening facts,
   the model's own failure modes (padding, agreeable capitulation,
   slop vocabulary), and invariants that keep iteration measurable
   (schema, rubrics, report formats). Deterministic checks stay
   scripts. Field/market files grow on demand, never speculatively.
8. **Doctrine is versioned and scheduled; inputs are fetched; nothing
   is re-derived per query.** Three knowledge tiers: stable mechanics
   (bundled, never researched at runtime), slow-cycle facts (stamped
   `Last verified` / `Verify by`; the repo re-verifies on schedule —
   monthly CI cron fails on stale stamps), task-scoped facts (the
   posting, the company — always fetched fresh; that's input, not
   research). Same question, same answer — or iteration stops being
   measurable.
9. **Typst, not LaTeX.** Typst ≥ 0.15 emits tagged PDF/UA-1 + PDF/A-2a
   dual — a real structure tree for parsers — with syntax an agent can
   reason about. Templates are pure functions of the data file.

## 3. Deliverables

Three skills, one repo; installable individually as `.skill` packages
or used from a checkout.

| Skill | One-liner |
|---|---|
| `resume-builder` | Vault-first intake → evidence drafting → `resume.yaml` → Typst render → mandatory evaluator loop |
| `resume-evaluator` | Adversarial harness: L0–L3 deterministic scripts + L4 JD-alignment + L5 recruiter-skim judgment, fixed report |
| `jd-analyzer` | Posting → ranked must-haves with evidence targets, decoded seniority, vocabulary map, market |

`jd-analyzer` stays separate on purpose: building is per-person,
tailoring is per-application, and the evaluator consumes the analyzer's
output as its L4 rubric. Small skills with clean interfaces compose
better and trigger more precisely.

## 4. Repository layout (current)

```
cvsmith/
├── README.md · LICENSE (MIT) · PROJECT_PLAN.md · MAINTENANCE.md
├── pyproject.toml · uv.lock          # uv-managed env (dev deps; scripts also carry PEP 723)
├── .github/
│   ├── scripts/check_freshness.py    # Verify-by stamp checker (monthly cron = strict)
│   └── workflows/ci.yml              # skill lint · freshness · template render · evaluator pytest
├── skills/
│   ├── resume-builder/
│   │   ├── SKILL.md                  # workflow (vault-first intake … mandatory verify; user-conflict protocol)
│   │   ├── references/
│   │   │   ├── screening-2026.md     # the pipeline + why each rule exists   [stamped]
│   │   │   ├── writing-rules.md      # bullet formula · anti-slop · honesty mechanics · Register
│   │   │   ├── career-vault.md       # vault format + projection rules
│   │   │   ├── regional.md           # market table · photo/personal-data doctrine · fallback   [stamped]
│   │   │   ├── tools-and-sources.md  # knowledge tiers · external-tool catalog · board APIs
│   │   │   ├── typst-guide.md        # template API · constraints · overflow triage
│   │   │   └── fields/{ai-ml[stamped], swe, academic, generic}.md
│   │   ├── assets/
│   │   │   ├── fonts/source-sans-3/  # vendored OFL — identical render everywhere
│   │   │   └── templates/{onecol.typ, data-schema.md}
│   │   └── scripts/render.sh         # yaml → PDF/UA-1+A-2a, font + text-layer + budget checks
│   ├── resume-evaluator/
│   │   ├── SKILL.md                  # L0–L5 protocol · fixed report · iteration rules
│   │   ├── references/{rubric.md, failure-modes.md}
│   │   └── scripts/{_report.py, extract_text.py, parse_sim.py,
│   │               hidden_text_check.py, lint_structure.py}   # PEP 723, standalone via uv run
│   └── jd-analyzer/
│       ├── SKILL.md                  # decompose · decode level+market · evidence targets · output format
│       └── references/requirement-taxonomy.md
├── evals/
│   ├── evals.json                    # 3 prompts + graded assertions per skill (M4)
│   ├── test_evaluator.py             # 15 tests: planted failures caught, zero false positives
│   └── fixtures/
│       ├── resume-sample/ · academic-sample/        # synthetic personas (Sam Casey / Dana Okafor)
│       ├── materials-sample/ · jd-sample/           # messy inputs + synthetic posting
│       ├── broken-src/*.typ · generate.py           # planted failures, built not committed
│       └── build/                                   # gitignored output
└── examples/ai-ml-intern/            # real outputs of following the skills, incl. honest NOT-READY verdict
```

Skill anatomy is canonical: frontmatter `name` + pushy `description`
(the only always-in-context cost, ~230 words across all three), body
loads on trigger (≤ ~180 lines each), references load only behind
explicit conditions (e.g. US target → regional.md never loads).

## 5. Cross-component contracts

The workflows live in the SKILL.md files. What must stay consistent
*between* components:

- **`resume.yaml` schema** — defined in
  `skills/resume-builder/assets/templates/data-schema.md`. Templates
  are pure functions of it; the evaluator's parse simulation checks
  that rendered output routes back into the same fields. Notable keys:
  `meta.{target_field, page_budget, paper, lang}`,
  `experience[].group` (research/teaching/industry → grouped
  standard-headed sections).
- **Evaluator layers** — L0 extraction, L1 parse sim, L2 integrity
  (raster-vs-text), L3 structure: scripts only, exit 0/1, `--json`
  contract (`verdict`, `checks[]` with pass/warn/fail, `metrics`).
  L4 JD-alignment and L5 human sim: agent judgment per `rubric.md`.
  Deterministic layers are never eyeballed; judgment layers are never
  scripted.
- **jd-analyzer output** — fixed markdown format (must-have table with
  evidence targets, vocabulary map, culture noise, notes) consumed by
  the builder for tailoring and by the evaluator as the L4 rubric.
  Location/market flows through it to the builder.
- **Evaluator report** — fixed template (verdict, layer table, L4/L5
  scores, ranked fix list). The builder is not done until this passes;
  the report never softens.
- **Sibling dependency** — builder invokes evaluator (and jd-analyzer
  when a posting exists); when a sibling skill isn't installed, run
  its scripts directly / follow its workflow and say which judgment
  layers were skipped.

## 6. Status & roadmap

| Milestone | Status |
|---|---|
| M0 scaffold (repo, CI, schema draft) | **done** |
| M1 render path (`onecol.typ`, `render.sh`, fixture) | **done** — 1 page, tagged, extraction-clean |
| M2 evaluator harness (4 scripts, planted-failure fixtures, tests) | **done** — every plant caught, zero false positives |
| M3 the three SKILL.md files + reference library | **done** — 3 skills, 13 references |
| M4 eval loop | **done** — 18 independent-agent runs, 2 iterations (Fable 5: 15/15 vs 10/15; Sonnet 5: 26/26 vs 21/26). Three repo bugs found by the runs, fixed. Contamination lesson recorded (eval metadata stays grader-side). Description trigger-optimization remains a backlog item |
| M5 release | **done** — v0.1.0 tagged; `.skill` packages on GitHub Releases; three templates; worked example |

Post-v0.1 backlog, in rough priority order:

1. **Description trigger-optimization** — deferred from M4 to
   post-v0.1. Blocked from agent sessions (`claude -p` gets 401 when
   nested); run from a normal terminal when convenient. The 22-query
   eval set is already written at
   `m4-workspace/trigger-eval-resume-builder.json`;
   the command is the skill-creator's
   `python -m scripts.run_loop --eval-set <that file> --skill-path
   skills/resume-builder --model <session model> --max-iterations 3`.
   Proxy result 2026-07-21 (after the scoped-description rewrite): a
   blind fresh-context harness — 3 independent judges per query, seeing
   only the message + the three skill descriptions — scored 22/22 with
   every vote unanimous, including correct first-skill routing (JD
   tailoring → jd-analyzer first; check-only → evaluator). Results in
   `m4-workspace/trigger-eval-results-2026-07-21.json`. The run_loop
   from a real terminal remains the sanctioned closure.
2. ~~`compact.typ` / styled second template~~ — **done**: Inter-based
   designed variant (accent name/headers, gray meta, tag rows,
   `meta.accent` knob), parse-verified; heading letter-spacing found
   to fracture extraction per-font and banned in typst-guide. The
   user-conflict "split" offer is now concrete.
3. **Localization** — month names + L1 heading taxonomy beyond
   English (DE/FR/ES first); until then the toolkit is strongest for
   English-language applications into any market, and says so.
4. **Photo support** — only with proper tagged-PDF alt text and the
   regional doctrine's narrow opt-in; never a hack.
5. **Field files on demand** — finance/consulting/etc. get literal
   guides only when real usage shows the generic+register procedure
   falling short.
6. **v0.2+ scope candidates** — cover letters, LinkedIn profile text,
   interview-prep from the vault (the architecture extends: intake →
   analyze → draft → verify).
7. **Typst Universe** — maybe publish the template standalone; not a
   v0.1 concern.
8. **`meta.section_order` (allowlisted)** — drivers: academic
   publications-early, experienced education-last; only if real usage
   hits the limitation (field guides now state the fixed order
   honestly instead of implying reorder support).
9. **DOCX / plain-text export** — PDF-only is a deliberate scope
   choice (tagged PDF is the parse-safe format); a Word/plain-text
   path is future work for employers who explicitly request it
   (common in academia/government/agency recruiting).

## 7. Toolchain & operations

- **Typst ≥ 0.15** (verified 0.15.1): `--pdf-standard ua-1,a-2a` dual
  export works; hard constraint: PDF/UA-1 fails without
  `set document(title: ...)` — templates always emit title/author.
- **Python ≥ 3.11 via uv**: `uv sync` for the dev env
  (pyproject/uv.lock); evaluator scripts carry PEP 723 inline deps so
  `uv run` works standalone outside this repo. Poppler
  (`pdftotext`/`pdfinfo`) for extraction checks and pdf2image.
- **No LLM API keys anywhere** — judgment layers run on the host agent.
- **CI** (all on push/PR; monthly cron): SKILL.md frontmatter lint,
  freshness stamps (strict on cron), fixture render through every
  template, full evaluator pytest. Fixture PDFs are generated, never
  committed.
- **Maintenance** — MAINTENANCE.md: what decays, cadence (market facts
  each recruiting season ~6mo, vendor mechanics ~12mo), tool-update
  protocol (`uv lock --upgrade` quarterly; fixture tests are the
  regression net). The repo checks the calendar so user sessions never
  re-check the world.

## 8. Risks & open questions

- **End-to-end proof is one eval cycle deep.** M4's 18 agent runs
  exercised the instructions (100% of assertions with-skill);
  real-user usage beyond eval fixtures is still the open question.
- **ATS behavior is a black box.** Open-library simulation ≠ vendor
  parsers. Mitigations: conservative rules, dual-extractor agreement,
  failure-modes catalog grown from real reports, consented
  commercial-parser ground-truth path when a real-world failure
  appears.
- **Trigger quality unknown.** Descriptions are written pushy but
  untuned; description-optimization is backlog #1.
- **Single-maintainer freshness.** Stamps + cron surface staleness,
  but re-verification still needs a human or scheduled agent to act.
- **English-centricity** (months, L1 taxonomy) is stated, not solved —
  backlog #3.
- **Evaluator self-agreement** — two layers of defense now: M4's
  independent-agent runs check the doctrine isn't circular, and the
  cold-reader protocol (evaluator SKILL.md) moves L4/L5 judgment into
  a fresh-context subagent so the context that wrote a resume never
  scores its own skim. Scripts were always immune; judgment now is
  too, where hosts support subagents.

## 9. Research base (2026-verified)

Jobscan "How AI Resume Screening Works" (Jul 2026) · ATS Verification
"AI Resume Screening in 2026" (Jun 2026) · HBR "AI Has Broken Hiring"
(Jun 2026) · arXiv 2605.28999 "Measuring Real-World Prompt Injection in
LLM Resume Screening" (May 2026) · Indeed Hiring Lab labor update (Jan
2026) · Metaintro new-grad market analysis (Apr 2026) · CNBC
entry-level AI-skills report (Apr 2026) · Typst 0.15 release (Jun
2026). Vendor primary sources for mechanism claims: Greenhouse Real
Talent product page
(https://www.greenhouse.com/uk/product-features/greenhouse-real-talent)
· Ashby "AI-Assisted Application Review in Practice"
(https://www.ashbyhq.com/blog/recruiting/ai-assisted-application-review-in-practice)
· Workday "AI for Talent" HiredScore datasheet (workday.com).
Perishable claims from these are frozen into stamped references
(`screening-2026.md`, `fields/ai-ml.md`, `regional.md`) and re-verified
per MAINTENANCE.md, not per query.
