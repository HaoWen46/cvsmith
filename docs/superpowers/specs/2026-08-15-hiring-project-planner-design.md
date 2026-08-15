# Hiring Project Planner Design

**Status:** Approved in conversation on 2026-08-15; implementation authorized.

## Outcome

Add one portable agent skill that turns a supplied current job description into either a bounded research dispatch or a research-backed project-and-demonstration brief optimized for hiring evidence per unit of build cost.

The artifact is a handoff to a later project-building agent; this skill does not build, verify, track, or claim completion of the project.

## Why a separate skill

`jd-analyzer` extracts the target contract, while this skill decides what a purpose-built project would need to demonstrate and how a later agent could prove it; candidate evidence, resume writing, evaluation, and application tracking remain separate concerns.

The skill must work in a fresh session from a JD alone and must not require a resume, career vault, repository, project history, prior chat, or machine-specific state.

## Observed baseline failures

- An unguided agent chose a project before current research and expanded it into a ten-task platform spanning a RAG agent, frontend, auth, PostgreSQL, Redis, Kubernetes, Terraform, AWS, observability, and CI despite a same-day application deadline.
- A second agent treated every JD phrase as mandatory project coverage and added a catalogue of fashionable adjacent tools, turning a focused infrastructure proof into Kafka, Flink, ClickHouse, Kubernetes, a service mesh, cloud deployment, GitOps, supply-chain security, and multiple incident programs.
- A research-only agent expanded the posting into seventeen research areas, imposed arbitrary source and word quotas, and asked for candidate-specific information even though the requested handoff had to be self-contained.
- Initial forward tests with the first skill draft rejected bonus-stack stuffing but still produced five- or six-component executor plans that could not create reviewer-usable evidence before a same-day application deadline; a plan-only system needs an explicit negative decision rather than a future platform disguised as current payoff.
- A later positive control selected a coherent local project but invented benchmark counts and top-k metrics; acceptance quantities therefore require a JD, user, source, or preserved pilot basis rather than familiar evaluation defaults.

These failures require a positive output schema and ordered gates, not another essay telling an agent to be concise.

## Minimal artifact model

The skill writes one canonical `hiring-project-brief.md` with one of three terminal states.

- `RESEARCH DISPATCH`: decisive current evidence is missing; the document contains a self-contained bounded research contract and no selected project.
- `READY FOR EXECUTOR`: decisive research is sufficient; the document contains the decision-owning agent's selected project-and-demonstration contract for a later builder.
- `NO PROJECT RECOMMENDED`: evidence and constraints show that no package can produce worthwhile verified evidence inside the target window or cost; the document records the negative decision and contains no executor contract.

A user who explicitly wants research delegated may receive a separate `hiring-project-research-dispatch.md`; it must contain only the dispatch section copied from the canonical brief, so it creates no second source of truth.

## Decision sequence

1. Read the supplied JD or an existing target brief and record source and access date without creating candidate-specific requirements.
2. Separate binary gates that a project cannot repair, then reduce the remaining posting to two through five central demonstrable capabilities and explicit constraints.
3. Retain a research question only when two plausible answers cause different plan actions, and derive its timebox from the execution window rather than a universal quota.
4. Research current role reality, technical behavior, proof standards, and commodity risk, or emit a fresh-session research dispatch and stop.
5. The main agent reads compact returns and decisive originals, labels JD facts separately from research hypotheses, and owns all rankings and selections.
6. Compare at most three coherent proof packages when alternatives materially differ, test reviewer-usable acceptance evidence against the execution window, and preserve deliberately uncovered requirements as gaps.
7. Select the smallest feasible package or explicitly recommend no project; write only the state-appropriate contract and do not implement it.

## Research boundary

Research may disambiguate and rank requirements already supported by the JD, choose a current implementation or proof method, expose commodity risk, and establish feasibility.

Research must not silently turn market trends, adjacent tools, or repeated posting language into new target requirements.

Workers gather bounded first-hand evidence and return `finding | source | observed date or version | capability affected | plan implication | uncertainty`; they do not choose a project, rank options, decide inclusion, or write the final brief.

There is no fixed source, posting, token, word, percentage, default-duration, or per-worker quota; research stops when unresolved questions cannot change the plan or a real deadline-derived timebox ends, and an absent or expired window stays unset until the user or decision-owning agent supplies one.

## Selection rule

Select for hiring proof per total cost, not novelty, fashionable stack breadth, architectural completeness, or keyword count.

Every proposed component must map to a prioritized capability and an observable demonstration; remove it if the same proof survives without it, and do not force every required noun into the package.

The real use case must be coherent enough for a recruiter and interviewer to understand, but production imitation is not a goal unless the JD makes production operation central and the proof cannot be obtained more cheaply.

Do not fabricate probabilities, ROI scores, achieved metrics, future resume claims, benchmark counts, or metric cutoffs; define evidence the later build would have to produce, require a stated basis for every number, and recommend no project when that evidence cannot become usable before the target window closes.

## Required ready-state content

- JD source, access date, role thesis, project-irreparable gates, explicit constraints, and a two-to-five-row capability-to-proof table.
- A decision register containing only plan-changing research with dated or versioned sources and unresolved uncertainty.
- Up to three coherent options when comparison is useful, with use case, capability coverage, observable demo, minimum components, cost, execution risk, and commodity risk.
- One main-agent selection with rationale and explicit rejected scope.
- An executor contract containing objective, hiring belief, real use case, must-build components, non-goals, acceptance evidence, recruiter surface, technical walkthrough, constraints, kill or pivot conditions, and required return artifacts.
- A completion gate that checks the handoff rather than pretending the project exists.
- A no-project state containing the failed feasibility or payoff condition, decisive evidence, smallest package considered, reversal condition, and target-safe next action.

## Scope and integration

Update only the new skill, its one reference contract, direct behavioral fixtures and structural tests, and the two top-level workflow descriptions needed to make the sixth skill discoverable.

Do not add a database, vault, MCP server, agent framework, generator script, implementation tracker, candidate schema, or machine-dependent configuration.
