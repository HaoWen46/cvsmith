# Hiring project brief contract

Write one target-specific agent handoff using the common header plus exactly one state body; remove instructional placeholders from the finished artifact.

## Common header

```markdown
# Hiring project brief: <role at company or role descriptor>
Status: RESEARCH DISPATCH | READY FOR EXECUTOR | NO PROJECT RECOMMENDED
JD source: <URL or supplied-copy locator>
Accessed: <YYYY-MM-DD>
Constraints: <execution window, evidence-use deadline, cost, platform, or "not supplied">

## Target reduction
Role thesis: <one sentence describing the work and strongest proof burden>

### Project-irreparable gates
| Gate | JD source | State | Consequence |
|---|---|---|---|

### Central capabilities
| Capability | JD FACT and source | Observable proof | Explicit constraint |
|---|---|---|---|

### Excluded JD material
| Item | Why it is not central | Revisit condition |
|---|---|---|
```

The central-capability table must contain two to five rows; exclusions remain visible so reduction cannot silently become omission or later reappear as keyword-driven scope.

## State A: RESEARCH DISPATCH

Use this state when the user requests research-only work, current evidence cannot be accessed, or any unresolved answer can still change the project or proof design.

Do not include project options, a selected project, components, build steps, resume language, or an executor contract in this state.

```markdown
## Decision-changing research
Research timebox: <real supplied deadline-derived limit and remaining execution time, or "not supplied; next owner must set">
| Question | Plausible answer A -> action | Plausible answer B -> different action | Evidence needed | Source scope | Stop condition |
|---|---|---|---|---|---|

## Research packets

### <semantic question name>
Question: <one bounded factual question>
Capability affected: <one or more central capabilities>
Decision changed: <priority, project choice, proof method, component, or feasibility>
Decision branches: <plausible answer A -> action; plausible answer B -> different action>
Inspect: <narrow live sources, versions, repositories, behavior, or measurements>
Do not: <expand requirements, rank options, select a project, write the final brief, or dump raw sources>
Return: finding | source | observed date or version | capability affected | plan implication | unresolved uncertainty
Timebox: <actual remaining deadline-derived research time, or "not supplied"; return partial findings and uncertainty when it expires>
Stop when: <evidence selects one decision branch, the uncertainty is irreducible, or the timebox expires>

## Dispatch return gate
- [ ] Every finding is current, directly source-bound, and limited to a named decision.
- [ ] Every question has two plausible answers that cause different actions; questions failing this test were removed.
- [ ] No deadline, percentage, default duration, per-worker slice, or source quota was invented when a real execution window was absent.
- [ ] JD FACT is separate from RESEARCH HYPOTHESIS.
- [ ] Conflicts, missing evidence, and unread regions are explicit.
- [ ] No worker recommended or selected a project.

## Next owner
The decision-owning main agent must read every compact return, inspect decisive originals, update this same brief, choose any options, and change status only when no unresolved research can alter the plan.
```

Terminal check for `RESEARCH DISPATCH`: the packet is runnable in a fresh session with the JD context it needs, contains no candidate evidence dependency, and makes no project decision.

## State B: READY FOR EXECUTOR

Use this state only after the main agent has reviewed enough current evidence to own the selection; remove all worker instructions and unresolved research that could still change the plan.

```markdown
## Decision register
| Type | Finding | Source and observed date or version | Plan implication | Uncertainty |
|---|---|---|---|---|
| JD FACT | ... | ... | ... | ... |
| RESEARCH HYPOTHESIS | ... | ... | ... | ... |

## Proof-package options
| Package | Real use case | Central capabilities proved | Observable demonstration | Minimum components | Acceptance evidence fits execution window? | Cost and execution risk | Commodity risk |
|---|---|---|---|---|---|---|---|

## Main-agent decision
Selected package: <one package>
Hiring belief: <what a skeptical reviewer should believe after seeing verified evidence>
Why this wins: <proof-per-total-cost rationale grounded in the register>
Rejected scope: <tools, features, and production imitation removed because they do not earn enough proof>
Coverage gaps: <required capabilities or terms this package intentionally leaves unproved and why>
Residual uncertainty: <what remains uncertain without invalidating the selection>

## Executor contract
Objective: <the artifact and evidence to produce, not a resume outcome guarantee>
Real use case: <specific user, painful task, input, and useful output>
Operating constraints: <execution window, evidence-use deadline, budget, environment, data, and external dependencies>

### Must-build components
| Component | Central capability | Observable proof | Why minimum |
|---|---|---|---|

### Proof-first build sequence
| Increment | Runnable behavior | Evidence produced | Stop check |
|---|---|---|---|

### Non-goals
- <explicitly excluded feature, platform, integration, scale imitation, or polish>

### Acceptance evidence
| Hiring belief | Required artifact or measurement | Method, conditions, and quantity basis | Pass, fail, or report rule |
|---|---|---|---|

### Demonstration surfaces
Recruiter surface: <one plain-language problem, mechanism, and evidence summary>
Supported JD terms after verification: <covered term -> acceptance artifact; omit bonus and uncovered terms; none are claims before verification>
Interviewer walkthrough: <short sequence showing behavior, mechanism, one tradeoff or failure, and measured evidence>

### Kill or pivot conditions
- <condition that makes the proof weak, infeasible, generic, or too costly -> smallest corrective pivot>

### Executor return contract
Return: <repository or runnable artifact, exact run instructions, raw and summarized measurements, demo assets, decision notes, known failures, limitations, and unverified claims>
Do not return: <unsupported metrics, "production" claims, invented users, hidden keyword content, or assertions without evidence pointers>

## Handoff completion gate
- [ ] Every capability claimed as covered has visible acceptance evidence and a walkthrough surface; uncovered requirements remain explicit gaps.
- [ ] Every component maps to one central capability and necessary proof.
- [ ] Removing any remaining component would materially weaken the hiring belief.
- [ ] The acceptance evidence and reviewer surfaces plausibly fit the supplied execution window and evidence-use deadline.
- [ ] Every numeric acceptance quantity or metric cutoff is JD-supplied, user-supplied, source-bound, or explicitly deferred to a preserved executor pilot with a decision basis.
- [ ] Only covered JD terms are mapped to future evidence, never treated as completed claims or padded with non-claims.
- [ ] Non-goals and kill conditions bound the executor against stack stuffing and production cosplay.
- [ ] The document contains no source-level implementation, repository scaffold, resume bullets, achieved metrics, or claim that the project was built.
```

Terminal check for `READY FOR EXECUTOR`: current evidence is sufficient for the decision, the main agent selected the package, the executor can act without prior chat, and this skill did not implement the project.

## State C: NO PROJECT RECOMMENDED

Use this state only after current evidence and supplied constraints are sufficient to show that no project can produce worthwhile verified evidence for the target window or cost; use `RESEARCH DISPATCH` instead when research could still reverse the decision.

Do not include a selected project, must-build components, build sequence, supported-term map, or executor contract in this state.

```markdown
## No-project decision
Reason: <failed gate, evidence-use deadline, execution cost, weak proof, or commodity risk>
Target consequence: <why a new project cannot improve this application or target enough in time>

### Decisive evidence
| Type | Finding | Source and observed date or version | Decision implication | Uncertainty |
|---|---|---|---|---|

### Smallest package considered
| Proof package | Acceptance evidence required | Earliest credible evidence window | Why it misses the target or payoff bar |
|---|---|---|---|

Reversal condition: <new deadline, lower-cost proof method, resolved gate, or evidence that could make planning worthwhile>
Target-safe next action: <what the user can do now without claiming an unbuilt project; do not perform another skill's work>

## No-project completion gate
- [ ] The decision rests on current evidence or hard supplied constraints, not pessimism or missing research.
- [ ] The target deadline is compared with reviewer-usable acceptance evidence, not source-code completion.
- [ ] No future platform plan is disguised as useful work for the current application.
- [ ] The document contains no selected project, implementation plan, candidate-evidence update, resume prose, or achieved claim.
```

Terminal check for `NO PROJECT RECOMMENDED`: the main agent owns the negative decision, states what could reverse it, and stops without creating work that cannot help the target.
