# cvsmith — Project Plan

**Agent skills that teach AI agents how to build, tailor, and adversarially test resumes — rendered with Typst, verified the way 2026 screening stacks actually verify.**

> Repo name: `cvsmith` (primary recommendation).
> Rationale: short, memorable, available-sounding, and the "smith" metaphor matches the design philosophy — a craftsman's toolkit, not a resume generator. Alternates if taken: `resume-foundry`, `typehire`, `tailorsmith`.

---

## 1. Problem statement (why this exists)

As of mid-2026, resume screening is an LLM-mediated pipeline: **parse → structure into fields → embed against the job description → score → rank**. Verified facts driving the design (all from 2026-dated sources; see §9):

1. **Parsing is the gate.** If text extraction fails or misroutes sections, the candidate is eliminated before any intelligence evaluates them. Single-column, text-layer PDFs with standard headings are non-negotiable.
2. **Keyword stuffing is dead and now actively harmful.** Modern screeners (Workday, Greenhouse, Ashby, Oracle layers) use semantic/embedding matching and flag manipulation. The target is ~80–90% *semantic* overlap with the JD via honest tailoring.
3. **Hidden text / prompt injection is detected and punished.** Production detectors hit 86–93% precision at ~$0.0001–0.01/file and cross-check the rendered page against extracted text (arXiv 2605.28999, May 2026). Any tool that *builds* resumes must also *prove* it produced nothing that looks like hidden content.
4. **Generic AI-sounding resumes are a negative signal.** Polished prose is free in 2026 (HBR, June 2026), so differentiators are specificity, quantification, and verifiable claims.
5. **The market is a barbell.** Entry-level tech postings are down sharply, but AI-mentioning postings are the one growing segment. Field-aware tailoring (especially AI/ML/LLM/agent roles) is where the leverage is.

Existing tools are static SaaS checkers or Python scripts wrapping an LLM API. **cvsmith is neither**: it is a set of *agent skills* — portable instruction+asset+script packages (Claude Code / Cowork / Agent SDK compatible, and readable by any agent framework that honors SKILL.md conventions) that make any capable agent behave like an expert resume engineer with a verification loop.

## 2. Product principles

- **Evaluator > builder.** Anyone can generate a resume in 2026. The moat is a test harness that checks a PDF the same way screening vendors do. Build → test → iterate is the core loop, like TDD for resumes.
- **Skills, not services.** No server, no API keys required for the core path. Deterministic checks live in bundled scripts; judgment lives in instructions the agent executes with its own intelligence.
- **Typst, not LaTeX.** Typst 0.15 (June 2026) emits tagged PDF/UA-1 (+ PDF/A-2a dual) — a clean machine-readable structure tree, near-ideal for ATS parsers — with sane syntax, instant compiles, and templates an agent can actually reason about.
- **Honesty is a feature.** The skills never fabricate experience, never stuff keywords, never inject hidden text — and the evaluator *proves* the absence of hidden text. This is both ethics and pure self-interest given 2026 detection.
- **Meet users where they are.** No filing rituals, no required folder layout, no assumption the user even has this repo. Intake adapts to pasted text, attachments, files read in place, remote pointers, or nothing at all — the skill conforms to the user, never the reverse.
- **General-purpose, field-aware.** Works for any field via a field-detection step + per-field reference files; ships deepest coverage for AI/ML/SWE first.

## 3. Deliverables

Three skills + shared assets in one repo, packaged individually as `.skill` files (installable) and usable directly as a git checkout.

| Skill | One-liner |
|---|---|
| `resume-builder` | Interview the user, ingest raw material, draft evidence-based content, render via Typst templates |
| `resume-evaluator` | Adversarial test harness: parse simulation, hidden-text/cross-modal check, structure lint, JD-alignment scoring, recruiter-skim critique |
| `jd-analyzer` | Decompose a job posting into ranked requirements, vocabulary, and evidence targets that the builder tailors against |

`jd-analyzer` is deliberately separate: tailoring is per-application, building is per-person, and the evaluator consumes the analyzer's output as its scoring rubric. Small skills with clean interfaces compose better and trigger more precisely.

## 4. Repository layout

```
cvsmith/
├── README.md                     # what/why, install, quickstart, demo GIF
├── PROJECT_PLAN.md               # this file
├── LICENSE                       # MIT
├── skills/
│   ├── resume-builder/
│   │   ├── SKILL.md              # workflow: intake → field ID → draft → render → handoff to evaluator
│   │   ├── references/
│   │   │   ├── screening-2026.md       # how the 2026 pipeline works; why each rule exists
│   │   │   ├── writing-rules.md        # bullet formulas, quantification, anti-AI-slop list, verb bank
│   │   │   ├── fields/
│   │   │   │   ├── ai-ml.md            # AI/ML/LLM/agent roles: what evidence counts (evals, RAG, agents, papers, OSS)
│   │   │   │   ├── swe.md              # general SWE conventions
│   │   │   │   └── generic.md          # fallback heuristics + how to research an unknown field
│   │   │   └── typst-guide.md          # template API, compile flags for PDF/UA, troubleshooting
│   │   ├── assets/
│   │   │   └── templates/
│   │   │       ├── onecol.typ          # default: single-column, standard headings, tagged-PDF safe
│   │   │       ├── compact.typ         # dense variant for experienced users
│   │   │       └── data-schema.md      # the resume.yaml content schema both templates consume
│   │   └── scripts/
│   │       └── render.sh               # typst compile with PDF/UA flags + font checks
│   ├── resume-evaluator/
│   │   ├── SKILL.md              # test protocol + how to interpret/score/report
│   │   ├── references/
│   │   │   ├── rubric.md               # scoring dimensions & weights; skim-test protocol
│   │   │   └── failure-modes.md        # catalog of real parse failures and their fixes
│   │   └── scripts/
│   │       ├── extract_text.py         # pdftotext + pypdf extraction; reading-order dump
│   │       ├── parse_sim.py            # section/heading/date detection — simulates ATS field routing
│   │       ├── hidden_text_check.py    # cross-modal check: rendered raster vs extracted text (the vendor check)
│   │       └── lint_structure.py       # single-column?, fonts embedded?, tagged PDF?, contact info parseable?
│   └── jd-analyzer/
│       ├── SKILL.md              # decompose JD → requirements table, vocabulary map, evidence targets
│       └── references/
│           └── requirement-taxonomy.md # must-have vs nice-to-have vs culture noise; seniority decoding
├── evals/                        # skill-creator-style eval harness
│   ├── evals.json                # test prompts + assertions per skill
│   └── fixtures/                 # sample materials/, sample JDs, deliberately broken PDFs
├── examples/
│   └── ai-ml-intern/             # end-to-end worked example (sanitized): materials → JD → resume.yaml → PDF → eval report
└── .github/
    └── workflows/
        └── ci.yml                # compile all templates, run evaluator scripts on fixtures, fail on regressions
```

Skill anatomy follows the canonical conventions: SKILL.md ≤ ~500 lines with YAML frontmatter (`name`, pushy trigger-rich `description`), progressive disclosure (metadata → body → references/scripts loaded only when needed), scripts for anything deterministic, per-field reference files so the agent reads only the variant it needs.

## 5. Component specs

### 5.1 `resume-builder`

**Trigger description (draft):** "Build, rewrite, or tailor a resume/CV. Use whenever the user wants a resume created or improved, mentions applying to jobs/internships, or provides career materials — even if they don't say 'resume'."

**Workflow encoded in SKILL.md:**

1. **Intake protocol — meet the material where it lives.** Users don't follow filing rituals; the skill adapts to however material actually shows up:
   - *Already in the conversation.* Pasted text, attachments, offhand mentions — all of it is material. Inventory it first; never ask the user to re-supply or relocate something they already provided.
   - *On disk.* Ask where things live and read them in place. Offer — never auto-run — a consented scan of the obvious spots (cwd, Desktop, Downloads, Documents) for resume-shaped files (`*resume*`, `*cv*`, `*transcript*`, LinkedIn's `Profile.pdf`).
   - *Remote pointers.* GitHub profiles/repos and personal sites are fetchable; use connected tools (Drive, Notion, …) when available. LinkedIn pages don't scrape — ask for LinkedIn's "Save to PDF" export instead.
   - *Nothing at all.* Fall back to a structured interview (defined in references); its output becomes the materials.

   Messy is fine — extraction is the skill's job. After inventory, ask one focused batch of questions covering only gaps that matter (dates, metrics, scope). Working files (`resume.yaml`, renders) go in a user-confirmed workspace; if that workspace is inside a git repo, verify the paths are ignored (offer to add ignores) *before* writing personal data. The `materials/` dir in this repo is a dev-checkout convenience, never a user requirement.
2. **Field identification.** Infer the target field from materials + stated goal; confirm with the user; load the matching `references/fields/*.md` (or follow `generic.md`'s research procedure for unknown fields).
3. **JD ingestion (optional but recommended).** If a target posting exists, invoke `jd-analyzer` and tailor against its output. No JD → build a strong general version for the field.
4. **Evidence drafting.** For each experience: extract claims → demand quantification → apply writing-rules (impact-first bullets, no AI-slop vocabulary, one concrete artifact per claim where possible). Never invent; flag weak sections to the user instead of padding them.
5. **Content → data.** Write `resume.yaml` per `data-schema.md`. Content and presentation are fully separated; templates are pure functions of the data file.
6. **Render.** `scripts/render.sh` compiles with Typst ≥ 0.15, PDF/UA-1 tagging on, fonts embedded, one page for students/early-career.
7. **Mandatory handoff.** Always finish by running `resume-evaluator` on the output and iterating until it passes. The builder is not "done" at PDF; it's done at *verified* PDF.

**Design decisions added 2026-07-21 (from stress-testing the use-case space):**

- **Career vault** (`references/career-vault.md`): a persistent, user-owned `career-vault.md` — the exhaustive evidence base (FACT/CONTEXT/CUT entries + honesty ledger + Q&A log) from which every resume is a *projection*. Intake accretes into it; per-application files (`resume-<company>-<role>.yaml`) select from it; projections never contain a fact the vault lacks. This makes the skill persistently useful (intake once, apply many) and keeps N tailored variants mutually honest. A file, not agent memory, so the user owns and ports it.
- **Audience axis, not just field axis**: HR pipelines (parse+embed+rank) vs. faculty readers (grad school, REUs — `fields/academic.md`) vs. both. Mechanical parse-safety is constant; evidence emphasis follows the reader. Schema gained `experience[].group` (research/teaching/industry) rendering as separate standard-headed sections — the academic convention, still router-recognized.
- **User-conflict protocol** (builder SKILL.md "When the user is wrong about mechanics"): show script evidence, offer a parse-safe + styled split from the same yaml, comply on aesthetics with the failure documented, never comply on integrity. The evaluator's report never softens; a reassuring false PASS is the one forbidden output.
- **Scope boundary**: in-scope = resume/CV-class documents for getting a human or pipeline to say "interview". Out of scope, said explicitly: statements of purpose, cover letters, portfolios, senior-academic full CVs (v0.2+ candidates at most).
- **Activate, don't enumerate.** For vast situational knowledge — register across industry × culture × employer type, unlisted markets, unlisted fields — references name the axis, pin the invariants (facts, honesty, anti-slop, parse mechanics), and give a procedure that *aims the model's own latent knowledge* (deeper and fresher than any shipped table): name the cell, sample 2–3 real artifacts from it, confirm with the user. Literal text is reserved for what latent knowledge gets wrong: post-training-cutoff screening facts, counter-priors (padding thin sections, agreeable capitulation, slop vocabulary — the model's own failure modes), and invariants that keep iteration measurable (schema, rubrics, report formats). Deterministic checks stay scripts. Field/market file growth is demand-driven, never speculative.
- **Market axis** (`references/regional.md`): conventions follow the *job's* market, never the user's location — per-market projections from one canonical vault (`resume-us.yaml`, `resume-de.yaml`), `meta.paper`/`meta.lang` are data-driven in the template, photo/personal-data doctrine defaults to none-anywhere with a narrow traditional-employer opt-in, Japan's rirekisho named as a different document. Stated limitations: no photo rendering yet (needs tagged alt-text design), English-only month names and L1 heading taxonomy — the toolkit is strongest for English-language applications into any market; localization is a roadmap item.

### 5.2 `resume-evaluator`

**Trigger description (draft):** "Test/score/check any resume PDF — ATS parseability, hidden-text safety, JD alignment, recruiter skim quality. Use whenever the user asks 'is my resume good/ATS-safe', provides a resume for review, or after generating any resume."

**Test battery (scripts = deterministic, agent = judgment):**

| Layer | Check | How |
|---|---|---|
| L0 Extraction | Text layer exists, extraction is lossless, reading order sane | `extract_text.py` |
| L1 Parse sim | Sections route to correct fields; headings standard; dates/contact parse | `parse_sim.py` |
| L2 Integrity | No hidden/white/microscopic text; rendered pixels ≙ extracted text; no manipulation signals | `hidden_text_check.py` (raster-vs-text cross-modal diff — the same class of check vendors run) |
| L3 Structure | Single column, tagged PDF, embedded fonts, ≤ page budget | `lint_structure.py` |
| L4 Alignment | Semantic coverage of JD requirements (from `jd-analyzer` output); gaps and overlaps named | agent, guided by `rubric.md` |
| L5 Human sim | 6-second recruiter skim: what lands? Then a skeptical deep read: what claims feel inflated or vague? | agent, guided by `rubric.md` |

**Output format:** a fixed-template report (pass/fail per layer, scored L4/L5, ranked fix list). Deterministic layers must never be eyeballed — scripts only.

### 5.3 `jd-analyzer`

Parses a posting into: must-have vs nice-to-have requirements, seniority signals, the JD's own vocabulary (for natural mirroring, not stuffing), and an "evidence target" per requirement (what a bullet proving it would look like). Output is a structured file consumed by both builder (tailoring) and evaluator (L4 rubric).

## 6. Milestones

**M0 — Scaffold (small).** Repo, license, CI skeleton, directory layout, this plan as living doc. Draft data schema.

**M1 — Render path (medium).** `onecol.typ` + `data-schema.md` + `render.sh`; CI compiles fixtures; verify tagged-PDF output extracts cleanly with `pdftotext` and `pypdf`. *Exit: a resume.yaml → verified-parseable PDF in one command.*

**M2 — Evaluator scripts (medium-large).** The four L0–L3 scripts, tested against fixtures including deliberately broken PDFs (two-column, image-based, white-text-injected, wonky headings). *Exit: evaluator catches every planted failure; zero false positives on the good fixture.*

**M3 — The three SKILL.md files (large — the core writing).** Full workflows, references (screening-2026, writing-rules, ai-ml/swe/generic field guides, rubric, failure-modes). *Exit: a fresh agent with only the skills installed produces a verified resume from messy fixture materials.*

**M4 — Eval loop (medium).** `evals/evals.json` with 3–5 realistic prompts per skill + assertions (e.g., "output PDF passes L0–L3", "no fabricated employers", "report follows template"). Run with-skill vs baseline, review, iterate. Then description-optimization pass for triggering.

**M5 — Polish & release (small).** Worked AI/ML-intern example, README with quickstart, package `.skill` files, tag v0.1.0.

Sequencing note: M1+M2 before M3 on purpose — write instructions against tools that already exist, so the SKILL.md files reference real script names and real failure output.

## 7. Toolchain requirements

- Typst ≥ 0.15 (CLI) — rendering, PDF/UA-1 + PDF/A-2a
- Python 3.11+ — `pypdf`, `pdfplumber` or `pdftotext` (poppler), `Pillow` + `pdf2image` for raster diff in the hidden-text check
- No LLM API keys required: all judgment layers run on the host agent itself (that's the point of skills)

**Verified locally (2026-07-21):** Typst 0.15.1 compiles with `--pdf-standard ua-1,a-2a` and the output extracts cleanly via poppler `pdftotext` 26.04. One hard constraint discovered: PDF/UA-1 export *fails* unless the document sets `set document(title: ...)` — templates must always emit title/author metadata from `basics.name` (also a win for ATS contact parsing). Python env is uv-managed: deps in `pyproject.toml` (dev group), locked in `uv.lock`, synced to `.venv/` (gitignored) via `uv sync`; run scripts with `uv run`.

## 8. Risks & open questions

- **ATS behavior is a black box.** We simulate with open extraction libraries; real Workday/Greenhouse parsers differ. Mitigation: conservative formatting rules + the failure-modes catalog grows from real-world reports.
- **Overfitting to AI/ML.** Mitigation: `generic.md` encodes a *procedure* for unknown fields (research the field's conventions, find 3 exemplar resumes, extract norms) rather than static rules.
- **Typst Universe publication?** Later maybe (the template alone could ship as a package); out of scope for v0.1.
- **Scope creep magnet:** cover letters, LinkedIn profiles, interview prep. Explicitly out of scope until v0.2+; the architecture (intake → analyze → draft → verify) extends naturally when we get there.
- **Name collision check** on `cvsmith` before creating the repo (30 seconds on GitHub search).

## 9. Research base (2026-verified)

Jobscan "How AI Resume Screening Works" (Jul 2026) · ATS Verification "AI Resume Screening in 2026" (Jun 2026) · HBR "AI Has Broken Hiring" (Jun 2026) · arXiv 2605.28999 "Measuring Real-World Prompt Injection in LLM Resume Screening" (May 2026) · Indeed Hiring Lab labor update (Jan 2026) · Metaintro new-grad market analysis (Apr 2026) · CNBC entry-level AI-skills report (Apr 2026) · Typst 0.15 release (Jun 2026). Key stats and rules from these sources get frozen into `references/screening-2026.md` with citations, and that file carries a "last verified" date so future updates re-verify rather than trust stale claims.
