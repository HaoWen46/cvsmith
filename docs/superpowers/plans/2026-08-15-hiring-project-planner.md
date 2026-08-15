# Hiring Project Planner Implementation Plan

> **For agentic workers:** Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` only if this plan is handed to a separate implementation session; preserve the narrow file scope and review every delegated result yourself.

**Goal:** Add a portable skill that converts a current JD into a bounded research dispatch or a smallest-credible project-and-demonstration brief without implementing the project.

**Architecture:** One `SKILL.md` owns ordered behavior and one reference owns the exact artifact contract; JSON pressure cases and small pytest assertions protect routing, boundaries, and required handoffs.

**Tech stack:** Markdown skill documents, JSON behavioral fixtures, and pytest structural checks run through `uv`.

## Constraints

- Work in the current checkout because the new skill must integrate with the uncommitted workflow redesign; do not alter or revert unrelated user changes.
- Use `apply_patch` for edits and keep every agent-facing paragraph or list item on one physical line.
- Do not add runtime code, persistent stores, machine paths, candidate dependencies, or project implementation machinery.
- Treat the three recorded no-skill runs as RED behavioral evidence: premature architecture, keyword-complete scope, adjacent-tool stuffing, arbitrary research quotas, and candidate-dependency drift must become explicit pressure assertions.

## Task 1: Encode the contract as failing tests

**Files:** Modify `evals/test_workflow_contract.py`, `evals/test_eval_scenarios.py`, and `evals/evals.json`; create `evals/trigger-eval-hiring-project-planner.json`.

1. Add the sixth skill to repository coverage and assert its ownership is distinct from JD analysis, candidate evidence, resume writing, and project implementation.
2. Add three behavioral cases: a fresh-session ready brief, a research-dispatch-only request, and a deadline/keyword-pressure case that must reduce scope instead of covering every JD term.
3. Assert the cases cover current research, no candidate dependency, no JD augmentation, main-agent selection, bounded worker returns, and the no-build boundary.
4. Run `uv run pytest -q evals/test_workflow_contract.py evals/test_eval_scenarios.py` and confirm failure because the skill and eval block do not exist.

## Task 2: Implement the smallest skill that satisfies the contract

**Files:** Create `skills/hiring-project-planner/SKILL.md` and `skills/hiring-project-planner/references/hiring-project-brief.md`; modify `README.md` and `PROJECT_PLAN.md`.

1. Write precise trigger metadata and explicit non-triggers so an agent can route the skill without loading unrelated skills.
2. Encode the ordered reduction, decision-changing research gate, worker boundary, main-agent decision, proof-per-cost selection rule, and terminal stop.
3. Define the two-state canonical artifact and its required tables, executor handoff, non-goals, kill conditions, and completion gate in the reference.
4. Update workflow descriptions and skill counts without changing the existing resume path.
5. Run the focused structural, line-discipline, packaging, and behavioral tests.

## Task 3: Forward-test behavior and close loopholes

**Files:** Modify only the new skill/reference, direct tests, or fixtures when an observed failure requires it.

1. Give the new skill to fresh agents on the same three baseline scenarios and inspect artifacts for premature project choice, requirement expansion, tool catalogues, candidate dependencies, implementation work, and decision outsourcing.
2. Repeat the highest-pressure wording across five fresh samples; judge behavior from artifacts rather than self-reported compliance.
3. Tighten only observed loopholes, rerun the pressure case, then run `uv run pytest -q evals/` and package the skill to a temporary output directory.
4. Inspect the archive for referenced-file completeness and machine-specific paths, review the final diff against the approved design, and report any residual behavioral uncertainty without overstating test coverage.
