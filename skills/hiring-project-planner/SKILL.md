---
name: hiring-project-planner
description: Use when the user explicitly asks what project to build for a supplied job description, wants current research before choosing a hiring-focused project, or requests a self-contained research dispatch or project-and-demonstration handoff for another agent. Do not use for JD analysis alone, candidate evidence intake, resume writing, project implementation, or checking whether a project was built.
---

# hiring-project-planner

Produce the smallest research-backed project-and-demonstration contract that could create credible evidence for a supplied target role; the product is the handoff, not the project.

Read `references/hiring-project-brief.md` before writing an artifact.

## Boundaries

- Require a current JD, its preserved text, or a source-grounded target brief; without one, request it instead of brainstorming a generic portfolio project.
- Work in a fresh session without requiring candidate evidence, a resume, career vault, repository, project history, prior chat, installed database, or machine-specific state.
- Accept an execution window, evidence-use deadline, cost ceiling, or platform constraint when supplied, but do not ask what the candidate already knows or owns as a prerequisite.
- If another skill merely identifies a possible evidence gap, offer this skill and wait for user confirmation; an explicit request to plan or research a project is confirmation.
- Do not implement, scaffold, verify, track, or claim completion of the project; do not write resume bullets, mutate candidate evidence, or update an application ledger.
- Treat ATS matching as supportable terminology plus visible evidence, never as a reason to cover every JD term, hide keywords, or add technology.

## 1. Fix the target and output state

Read the whole supplied posting; when given a URL, fetch it fresh, preserve its source and access date, and use a supplied copy when the live posting is unavailable rather than reconstructing it from company reputation.

Use an existing `jd-analyzer` brief when supplied, but do not require or rewrite it; keep this project brief target-specific and disposable rather than storing it as candidate evidence.

Write one `hiring-project-brief.md` with exactly one terminal status: `RESEARCH DISPATCH` when decisive current research must happen elsewhere, `READY FOR EXECUTOR` when a proof package can meet the supplied constraints, or `NO PROJECT RECOMMENDED` when enough evidence shows that no package can earn usable proof within the target window or cost.

If the user explicitly requests a standalone dispatch, also write `hiring-project-research-dispatch.md` containing only the canonical brief's dispatch section; never maintain two independently edited decisions.

## 2. Reduce before ideating

Separate project-irreparable gates such as authorization, clearance, licensure, or date-bound eligibility; a project cannot repair them, and an unresolved or failed gate must remain visible without consuming project scope.

Reduce viable work requirements to two to five central demonstrable capabilities using the posting's responsibilities, explicit requirements, repetition, role scope, and skeptical evidence target; cite the JD basis for each capability.

Record explicit language, platform, domain, deadline, and delivery constraints separately; keep nice-to-haves outside the core unless one is strongly emphasized or adds coherent proof at negligible marginal cost.

Do not turn every noun, bonus item, adjacent tool, generic responsibility, or current market trend into a capability; the reduction is a decision, not a coverage inventory.

Do not force every central capability or required noun into one project; prioritize the strongest hiring beliefs and keep deliberately uncovered requirements explicit rather than buying weak breadth with extra components.

For each central capability, define what a reviewer could observe in a running artifact, measured result, controlled failure, design boundary, or technical walkthrough before naming a project.

## 3. Ask only decision-changing research questions

Before selecting a project, use current research to test technical feasibility, credible proof design, and commodity or tutorial risk for the reduced capabilities; model memory alone cannot produce `READY FOR EXECUTOR`.

Write a research question only when its answer can change capability priority, project choice, proof method, minimum component set, or feasibility; state that decision beside the question.

Before retaining a question, write two plausible answers and the different plan action each would cause; if both answers leave the action unchanged, delete the question instead of researching a capability for completeness.

Research may resolve ambiguity or rank requirements already grounded in the JD and may select a current implementation or proof method; it must not augment the JD with requirements inferred from other employers, trend reports, or fashionable stacks.

Match source to claim: the supplied JD establishes this target's demand; running behavior, maintained source, release records, and narrow technical documentation establish current behavior; reproducible measurements establish performance; current examples and templates can expose commodity risk.

Treat vendor claims, surveys, search rankings, social posts, and generated summaries as leads or narrow evidence, not authority over what the target employer values; preserve disagreement and uncertainty instead of laundering it through confident prose.

Record observed date or version and a direct source pointer for every plan-changing finding; label posting-grounded statements `JD FACT` and external interpretations `RESEARCH HYPOTHESIS`.

Use no fixed source count, posting count, research duration, or word quota; stop when unresolved questions can no longer change the plan, and never keep browsing to decorate a conclusion.

Derive a bounded research timebox only from a real supplied execution window and evidence-use deadline, leaving the downstream builder enough time to produce acceptance evidence; when no window exists and it can change the terminal state, ask one concise constraint question before `READY FOR EXECUTOR` or leave the next timebox unset in `RESEARCH DISPATCH`.

Never invent a deadline, percentage allocation, default duration, per-worker duration, source quota, or similar scheduling heuristic; an expired timebox stays expired until the user or decision-owning agent supplies a real new window.

If current evidence is unavailable, browsing is disallowed, or a decisive question remains unresolved, emit `RESEARCH DISPATCH` and stop without selecting a project.

## 4. Use workers only to save main-context cost

The main agent may investigate directly; use research workers only for independent bounded questions whose raw-source reading would otherwise consume meaningful context.

Give a worker one question, the affected capability and decision, narrow source scope, observed-time requirement, and explicit prohibitions against requirement expansion, option ranking, project selection, or final prose.

Give every worker the actual remaining research timebox when one exists; when it expires, require the compact findings gathered so far plus unresolved uncertainty rather than more browsing.

Require one compact record per decision-changing finding in this shape: `finding | source | observed date or version | capability affected | plan implication | unresolved uncertainty`; request exact pointers rather than copied source bodies.

The main agent reads every return, rejects scope drift and unsupported conclusions, opens the decisive original evidence needed to trust the finding, and owns every capability, option, inclusion, and selection decision.

Worker agreement is not verification, and a worker may report uncertainty or unread regions but never decide what to build, keep, discard, or present.

## 5. Choose proof per total cost

After current research is sufficient, form one coherent proof package or compare at most three only when materially different choices remain; do not create an idea catalogue.

Start from the observable demonstration and work backward to the minimum artifact; a real use case should make the proof intelligible, but production imitation is not intrinsically valuable.

For every component, record `central capability -> observable proof -> why this component is necessary`; remove the component when the same proof survives without it.

Compare options qualitatively on central capability coverage, credibility of the demo, implementation and verification cost, execution risk, and commodity risk under the supplied constraints; do not fabricate hiring probabilities, ROI scores, achieved metrics, or precision the evidence cannot support.

Do not invent an acceptance quota, benchmark size, repetition count, percentile, top-k metric cutoff, coverage target, or pass threshold; every number must come from the JD, a user constraint, current source-bound evidence, or an executor pilot whose result and decision basis are preserved.

Test feasibility against the evidence-use deadline: acceptance evidence and a reviewer-usable surface, not merely source code, must plausibly fit inside the execution window; record required capabilities intentionally left unproved as coverage gaps.

The main agent selects the smallest coherent package with the strongest defensible hiring proof per total cost and records why rejected scope would not change the hiring belief enough to justify its cost.

If no package clears the feasibility and proof-per-cost test, choose `NO PROJECT RECOMMENDED`; state why the project cannot help this target in time, what condition could reverse the decision, and stop instead of handing off a future platform plan.

Bonus technologies may enter only when they solve a load-bearing problem or cheaply strengthen observable proof; keyword coverage, recency, novelty, and visual impressiveness alone never justify them.

## 6. Write the handoff and stop

Follow the exact positive contract in `references/hiring-project-brief.md`; omit sections forbidden by the chosen terminal state rather than filling them with speculation.

In `READY FOR EXECUTOR`, specify the hiring belief, real use case, minimum components, proof-first build sequence, non-goals, acceptance evidence, recruiter surface, supported-JD-term map, explicit coverage gaps, interviewer walkthrough, constraints, kill or pivot conditions, and executor return artifacts.

In `NO PROJECT RECOMMENDED`, record the failed payoff or feasibility condition, decisive evidence, smallest package considered, reversal condition, and target-safe next action; include no selected project or executor contract.

Describe evidence that a later build must produce, never future accomplishments as facts; planned scale, reliability, users, deployment, metrics, and collaboration remain unachieved until independently verified.

Map only terms the selected package could support after verification; do not repeat uncovered or bonus terms in the supported-term map merely to display keyword coverage.

Do not turn the handoff into source-level implementation tasks, a complete production architecture, a repository scaffold, commit plan, resume draft, or application package.

Present the user with the artifact path, terminal status, central capability thesis, and either the next research action or selected proof package in a compact table or paragraph; do not dump worker notes or narrate the entire process.

Stop after delivering the document; project execution belongs to a later agent and requires a separate user instruction.

## Completion check

Finish only when the JD is traceable, the reduction precedes ideation, all plan-changing current research is source-bound or dispatched, the main agent owns the decision, every retained component earns its proof, state-forbidden sections are absent, and no project implementation or candidate-specific artifact was created.
