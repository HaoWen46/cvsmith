# Candidate Evidence Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add one portable `candidate-evidence` skill, remove durable evidence intake from `resume-builder`, and prove the five-skill handoff works without adding infrastructure.

**Architecture:** Candidate sources remain authoritative and unchanged; `candidate-evidence` creates a target-neutral `candidate-evidence/index.md` plus semantic evidence documents, `jd-analyzer` creates disposable target briefs, and `resume-builder` selects from those two inputs. Existing rendering and evaluation tools remain unchanged; the legacy `meta.vault` field may point to `candidate-evidence/index.md` for compatibility in this slice.

**Tech Stack:** Markdown skills and references, JSON behavioral scenarios, Python tests through `uv`, existing packaging and resume-rendering tools.

## Global Constraints

- Add exactly one skill and no orchestrator, database, service, retrieval layer, generated-ID scheme, or new script.
- Keep static candidate sources unchanged; store no absolute machine path, hostname, home directory, session identifier, or private-memory dependency in portable artifacts.
- Use semantic evidence filenames and headings; prohibit numeric prefixes, opaque IDs, UUIDs, and JD-conditioned durable findings.
- Keep every skill and reference decision-dense with one paragraph or list item per physical line and no instruction file above 180 lines.
- Let the main agent read every substantive index capsule, select every investigation, inspect decisive original evidence, and make every ranking, archive, resume, and send decision.
- Let subagents return only compact source-bound facts from main-selected raw sources without receiving the JD or making recommendations.
- Preserve unrelated staged and unstaged work; every commit names only intentional paths.

---

### Task 1: Prove the missing boundary and add `candidate-evidence`

**Files:**
- Create: `skills/candidate-evidence/SKILL.md`
- Create: `skills/candidate-evidence/references/evidence-workspace.md`
- Create: `evals/trigger-eval-candidate-evidence.json`
- Modify: `evals/evals.json`
- Modify: `evals/test_eval_scenarios.py`
- Modify: `evals/test_workflow_contract.py`

**Interfaces:**
- Consumes: User-supplied resumes, repositories, reports, portfolios, employment material, source locators, and an optional existing evidence workspace.
- Produces: `candidate-evidence/index.md`, semantic detailed documents, compact candidate questions, and source-bound investigation records.

- [ ] **Step 1: Add the failing catalog and behavioral-scenario tests**

Change `SKILLS` in `evals/test_eval_scenarios.py` to include `candidate-evidence`; change the workflow contract to expect five skill directories and to load the candidate skill; add two `candidate-evidence` cases to `evals/evals.json`: target-neutral intake from `evals/fixtures/materials-sample/`, and refresh/reuse behavior when a JD is also present.

The first case must require semantic documents plus a substantive index, unchanged originals, source-bound facts, ownership uncertainty, and no JD language; the second must require unchanged source reuse, separate JD handling, and main-agent-only archive and selection decisions.

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `uv run pytest -q evals/test_eval_scenarios.py evals/test_workflow_contract.py`

Expected: FAIL because `candidate-evidence` is required by the test catalog but its skill directory and scenario block do not exist.

- [ ] **Step 3: Run a fresh-agent baseline without the new skill**

Give five fresh agents only the current `resume-builder` skill plus `old_resume.txt` and `project_notes.md`, ask each to organize reusable evidence without a JD, and record whether they create a monolithic target-contaminated vault, perform target work prematurely, or fail to produce semantic evidence documents and a substantive reusable index.

Run one second baseline scenario with the same candidate files plus the ML-intern posting and record whether candidate facts become conditioned on the JD or whether the builder broadly ingests and decides before a separate evidence workspace exists.

- [ ] **Step 4: Initialize the skill scaffold, then retain only required files**

Resolve the selected `skill-creator` directory from the runtime's skill metadata, then run `uv run "$cvsmith_skill_creator_dir/scripts/init_skill.py" candidate-evidence --path skills --resources references --interface display_name="Candidate Evidence" --interface short_description="Organize reusable career evidence" --interface default_prompt="Organize these candidate materials into reusable target-neutral evidence."`; delete the generated `skills/candidate-evidence/agents/openai.yaml` with `apply_patch` and remove its now-empty directory because this repository's minimal shipped surface is only `SKILL.md` plus one reference.

- [ ] **Step 5: Write the minimal skill and workspace contract**

Write `SKILL.md` with a trigger-only description and the shortest behavioral sequence that closes observed baseline failures: protect private output, check source revisions, survey every supplied body substantively, model natural bodies and relationships, update target-neutral semantic evidence, archive reversibly without a fixed age or count heuristic, verify current outcome-bearing reality when industry change matters, optionally dispatch bounded factual investigation, ask one consequential question batch, and present created/reused/archived/conflicted results compactly.

Write `references/evidence-workspace.md` with only the `index.md` and detailed-document shapes, source revision rules, active/archive semantics, relationship rules, subagent return fields, and legacy-vault migration rule; keep canonical resume-eligible facts in the substantive index so the existing projection scanner can consume it without a new tool.

- [ ] **Step 6: Add trigger cases that distinguish evidence intake from resume construction**

Add positive trigger prompts for logging a project, importing a GitHub repository or report, refreshing experience evidence, resolving candidate-source conflicts, and organizing a reusable portfolio; add negative prompts for tailoring a prepared resume, analyzing a JD alone, evaluating a PDF, tracking an application, and interview preparation.

- [ ] **Step 7: Run GREEN checks and one with-skill forward test**

Run: `uv run pytest -q evals/test_eval_scenarios.py evals/test_workflow_contract.py evals/test_line_discipline.py evals/test_packaging.py`

Run the first baseline prompt with the new skill in five fresh contexts and verify that output shape, source reads, main-agent authority, semantic naming, and target neutrality converge on the recorded assertions; manually read every result and tighten only wording tied to an observed failure.

- [ ] **Step 8: Commit the new skill slice**

Run: `git commit --only -m "feat: add candidate evidence skill" -- skills/candidate-evidence/SKILL.md skills/candidate-evidence/references/evidence-workspace.md evals/trigger-eval-candidate-evidence.json evals/evals.json evals/test_eval_scenarios.py evals/test_workflow_contract.py`

### Task 2: Narrow the four existing skills to their approved handoffs

**Files:**
- Modify: `skills/resume-builder/SKILL.md`
- Delete: `skills/resume-builder/references/career-vault.md`
- Modify: `skills/jd-analyzer/SKILL.md`
- Modify: `skills/resume-evaluator/SKILL.md`
- Modify: `skills/application-tracker/SKILL.md`
- Modify: `evals/trigger-eval-resume-builder.json`
- Modify: `evals/evals.json`

**Interfaces:**
- Consumes: A disposable JD brief and `candidate-evidence/index.md`, then selected evidence documents and decisive original sources.
- Produces: A fresh target-specific YAML/PDF, exact-PDF evaluation, and optional prepared/applied tracker event without changing durable candidate evidence for target fit.

- [ ] **Step 1: Add failing integrated behavior assertions**

Update the resume-builder scenarios so pure career-material intake belongs to `candidate-evidence`, builder selection starts from the complete substantive index, target-specific omission never enters durable evidence, the main agent opens finalist details and decisive originals, and the handoff includes a compact `selected | omitted | reason | risk` table.

Change the final pure-intake entries in `evals/trigger-eval-resume-builder.json` to `false`; keep combined requests that explicitly ask for a finished resume as `true` because both skills may trigger.

- [ ] **Step 2: Run the integrated scenario tests and verify RED**

Run: `uv run pytest -q evals/test_eval_scenarios.py evals/test_workflow_contract.py`

Expected: FAIL because the builder still owns career-vault intake and durable target-specific `OMIT-FOR` state, and the JD/evaluator/tracker handoffs still name the monolithic vault.

- [ ] **Step 3: Remove intake and archive ownership from `resume-builder`**

Replace broad artifact ingestion with: require or invoke `candidate-evidence`; read the disposable target brief plus complete substantive evidence index; make the target-specific first filter; load contender documents and decisive originals selectively; decide every selection and omission; build, render, evaluate, and present artifacts plus the compact decision table.

Keep legacy `meta.vault` compatibility by pointing it to `candidate-evidence/index.md`; do not rename schema fields or modify scripts in this slice because the current scanner already accepts that Markdown file and no failing behavior requires a migration tool.

- [ ] **Step 4: Remove the obsolete monolithic reference and clarify sibling boundaries**

Delete `skills/resume-builder/references/career-vault.md`; make `jd-analyzer` state that every brief is separate, temporary, and disposable; make `resume-evaluator` accept the evidence index and selected evidence documents; make `application-tracker` live beside the evidence workspace and not require a retained full JD.

- [ ] **Step 5: Run GREEN checks and an integrated fresh-agent case**

Run: `uv run pytest -q evals/test_eval_scenarios.py evals/test_workflow_contract.py evals/test_line_discipline.py evals/test_packaging.py`

Give a fresh agent the new candidate skill, updated builder and JD analyzer, the synthetic candidate files, and one JD; verify the agent creates or reuses target-neutral evidence, analyzes the JD separately, filters from the whole substantive index, studies finalists, and keeps every comparative decision in the main agent.

- [ ] **Step 6: Commit the handoff slice**

Run: `git commit --only -m "refactor: separate evidence intake from resume building" -- skills/resume-builder/SKILL.md skills/resume-builder/references/career-vault.md skills/jd-analyzer/SKILL.md skills/resume-evaluator/SKILL.md skills/application-tracker/SKILL.md evals/trigger-eval-resume-builder.json evals/evals.json`

### Task 3: Align the product surface and verify the actual package

**Files:**
- Modify: `README.md`
- Modify: `PROJECT_PLAN.md`
- Modify only if fresh-agent evidence exists: `docs/research/agent-behavior-and-hiring-evidence.md`

**Interfaces:**
- Consumes: The verified five-skill implementation and fresh-agent results.
- Produces: Accurate discovery documentation, packaged portable skills, and an evidence-backed completion report.

- [ ] **Step 1: Update the public workflow without adding architecture prose**

Add `candidate-evidence` to the README and product-contract tables, change `resume-builder` ownership from intake to target-specific selection/building, describe candidate evidence as durable and JDs as disposable, and change package/fresh-agent references from four skills to five.

- [ ] **Step 2: Record only measured behavior**

If baseline and with-skill runs completed, add one compact decision-register entry containing prompts, observed baseline failure, observed candidate behavior, remaining uncertainty, and source artifact locations; do not claim hiring causality or independent verification from a self-report.

- [ ] **Step 3: Run focused and full verification**

Run: `uv run pytest -q evals/test_workflow_contract.py evals/test_eval_scenarios.py evals/test_line_discipline.py evals/test_packaging.py`

Run: `uv run pytest -q evals/`

Expected: all relevant tests pass; any unrelated dirty-baseline failure is reported with the exact test and left untouched unless it blocks this feature.

- [ ] **Step 4: Package and inspect all skills**

Run `cvsmith_package_dir=$(mktemp -d)` followed by `uv run scripts/package_release.py -o "$cvsmith_package_dir"`; verify exactly five `.skill` archives, inspect `candidate-evidence.skill` for only `SKILL.md` and `references/evidence-workspace.md`, and scan every archive for machine-specific paths or cache artifacts.

- [ ] **Step 5: Render and visually inspect the flagship artifact**

Run `skills/resume-builder/scripts/render.sh evals/fixtures/resume-sample/resume.yaml -o examples/ai-ml-intern/resume.pdf`, run the exact-PDF evaluator battery, open `examples/ai-ml-intern/resume.pdf`, and confirm the skill-boundary change did not regress layout, extraction, structure, or claim checking.

- [ ] **Step 6: Review the final diff against the scope ceiling**

Reject any added service, database, generated ID, retrieval helper, redundant document, new script, JD-conditioned durable field, subagent judgment, or machine path; run `git diff --check` and confirm every changed file maps to a task above.

- [ ] **Step 7: Commit the product-surface slice**

Run: `git commit --only -m "docs: describe the five-skill resume workflow" -- README.md PROJECT_PLAN.md docs/research/agent-behavior-and-hiring-evidence.md`
