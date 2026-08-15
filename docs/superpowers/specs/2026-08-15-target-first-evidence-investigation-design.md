# Candidate evidence and target-resume workflow design

Status: The workflow is approved in conversation; this written specification awaits user review before implementation planning.

## Objective

Produce a truthful, strategically selective resume that improves the candidate's chance of an interview without exhausting the main agent's context, confusing durable candidate facts with temporary job targeting, or delegating judgment to subagents.

The system must remain a portable set of skills and files rather than depend on this machine, a hosted service, a particular agent runtime, or a private memory system.

## Minimum skill split

| Skill | Trigger and sole responsibility |
| --- | --- |
| `candidate-evidence` | Use when the user supplies resumes, repositories, reports, portfolios, project folders, employment material, or asks to organize or refresh reusable career evidence; it owns durable target-neutral evidence intake, investigation, indexing, source tracking, conflicts, currentness, and reversible archiving. |
| `jd-analyzer` | Use when the user supplies or compares current job descriptions; it produces a separate temporary brief for each target and never mutates candidate evidence. |
| `resume-builder` | Use when the user asks for a resume for a chosen target from prepared or available evidence; it owns comparative selection, page allocation, claim wording, YAML creation, rendering, and delivery. |
| `resume-evaluator` | Use when an exact rendered resume must be assessed; it evaluates the actual PDF rather than an intended draft. |
| `application-tracker` | Use only when an application is prepared, submitted, or receives an outcome; it records the exact artifacts and status needed for outcome learning. |

There is no orchestrator skill, separate project skill, separate experience skill, or project-investigator skill; the active main agent composes the applicable skills from their visible descriptions.

## Skill discovery contract

Before loading a skill, an agent can see its name, trigger description, and location; each description must therefore state when the skill applies and its boundary, while detailed workflow belongs in the loaded skill body.

The descriptions must make combined use discoverable: a task containing candidate files and a JD can load `candidate-evidence`, `jd-analyzer`, and `resume-builder`, while evaluation and tracking activate only when their own outputs or events exist.

Descriptions must not attempt to encode the whole workflow, advertise unsupported guarantees, or make one skill appear to own another skill's decisions.

## Artifact boundaries

Static candidate files and repositories remain unchanged and authoritative; the evidence workspace stores compact derived understanding and source locators, not copied repositories, complete reports, or raw agent transcripts.

The durable evidence workspace contains `index.md` plus semantically named evidence documents such as `distributed-training-research.md` or `payments-platform-role.md`; generated numbers, opaque IDs, numeric filename prefixes, UUIDs, and machine-specific absolute paths are prohibited.

The evidence workspace belongs with the user's career materials or chosen output directory, not inside the installed skill and not in agent memory; portable locators use URLs or paths relative to a named source root.

Each JD brief is temporary and target-specific; it may be discarded when stale without damaging the candidate evidence workspace, prior resumes, or the application ledger.

Each resume is a temporary projection from one JD brief and the durable evidence workspace; target-specific fit, ranking, omission, wording, and page decisions must not flow back into durable evidence.

The application ledger records only the target identity, dates, status, exact sent artifact identity, and outcome fields needed for later analysis; preserving the full JD is optional rather than required.

## Candidate evidence model

An evidence document represents the natural body of work supported by the sources: it may be an employment role, research effort, product, project, component, related project family, or shared result, and the agent must not force these into mutually exclusive project records.

When several projects share a report, mechanism, benchmark, role, or outcome, the common finding is documented once and linked by semantic filename or heading; the index makes the relationship visible so one result is not counted as several independent achievements.

Each detailed evidence document records scope and dates, problem and users, candidate actions and ownership, technical or operational mechanism, outcomes and artifacts, exact source map, conflicts and unknowns, currentness, relationships, and lifecycle rationale.

Each index entry is a substantive capsule rather than zero-context metadata: semantic title and link, what the body of work accomplished, the candidate's contribution, strongest defensible signal, source and ownership state, currentness, relationships, material uncertainty, lifecycle state, and revival condition.

Durable documents contain observed target-neutral facts and uncertainty only; JD fit, target vocabulary, resume placement, comparative ranking, `OMIT-FOR` rules, and claims invented from implication are prohibited.

Source identity uses a stable URL or a path relative to a named root plus the strongest cheap revision marker available, such as a Git commit or content digest; if identity or freshness cannot be established, the document says so instead of assuming it is current.

The workspace is current only when every candidate source supplied for this run is represented and the revision markers for previously represented material still match; unchanged sources are reused without rereading their bodies.

## Archive and currentness

Archive is a reversible lifecycle state, not deletion, age-based punishment, or a folder that disappears from comparison.

The index keeps a substantive capsule for archived work so the main agent can notice unusual relevance without loading its detailed document or raw sources; active and archived sections are both read during portfolio comparison.

An evidence body may be archived when supported evidence is persistently weak, redundant, superseded for present-tense use, contradicted, or dominated by stronger evidence across plausible targets; the archive reason and concrete revival condition are required.

Age alone never decides archive status, and recent technology never wins by novelty alone; historical accomplishment, present capability, market relevance, and source reliability are separate judgments.

When an archive or currentness judgment depends on technology or industry change, the agent verifies current outcome-bearing reality such as maintained use, deployed adoption, observed hiring demand, or stronger replacement evidence; it does not treat an age cutoff, popularity narrative, vendor statement, or inherited resume heuristic as ground truth.

A dated artifact can prove what the candidate did then, but a material present-tense capability claim requires recent use, a current artifact, or dated candidate confirmation.

A target-specific omission never changes durable lifecycle state; an archived body is revived when a new target or new source satisfies its recorded revival condition.

## Workflow for static candidate files and one target JD

1. Route from visible skill descriptions: load `jd-analyzer` for the JD, `candidate-evidence` for candidate files or a stale evidence workspace, and `resume-builder` for the requested resume.
2. `jd-analyzer` creates a disposable target brief containing eligibility gates, priorities, level, evidence demands, terminology, ambiguities, and contradictions; it does not average multiple JDs into one fictional role.
3. The main agent checks `candidate-evidence/index.md` and its source revision markers; if every supplied source is represented and unchanged, it reuses the workspace, otherwise `candidate-evidence` performs only the missing or stale intake work.
4. During intake, the main agent reads a substantive overview of every supplied body of work, such as the relevant resume entry, README introduction, report abstract or executive summary, role overview, or equivalent; title, date, tags, stars, file tree, and repository metadata alone are insufficient.
5. The main agent identifies natural evidence bodies and relationships, updates semantically named documents and the substantive index, and marks unresolved ownership, conflicts, missing measurements, freshness, and archive conditions without using the JD to rank or word the findings.
6. `resume-builder` reads the target brief and the complete substantive index, compares every active and archived capsule, identifies contenders, coverage gaps, redundancies, and uncertainties, and performs the first target-specific filter itself.
7. The main agent opens detailed documents for contenders and enough decisive original material to judge them; when a selected repository or report needs substantial raw-source investigation, it uses the `candidate-evidence` workflow and may delegate bounded collection work under the subagent contract below.
8. The main agent asks one compact question batch only when the answers could change eligibility, ownership, evidence selection, claim safety, or interview defensibility, then makes every final selection, grouping, omission, and page-allocation decision.
9. `resume-builder` creates fresh YAML, renders the PDF, and performs visual inspection; `resume-evaluator` then evaluates that exact PDF and the builder iterates until sendable or reports the remaining blocker.
10. The agent presents the PDF, YAML, evaluation report, and a compact selection table explaining included evidence, omitted contenders, unresolved risks, and user actions; `application-tracker` runs only when preparation, submission, or an outcome is being recorded.

No broad raw-source discovery resumes after page allocation unless verification exposes a specific gap that could materially change a selected claim or project.

## Multiple-JD reuse

`jd-analyzer` keeps each JD as a separate target brief and may add a temporary comparison of shared requirements and meaningful differences; it never collapses distinct roles into an average target.

The candidate evidence workspace is created or refreshed once and reused across targets; a source discovery made during one application is durable only when recorded in target-neutral form.

`resume-builder` performs a separate selection and projection for each chosen JD, so reuse occurs at the evidence layer rather than by reusing target-specific rankings or blindly editing the previous resume.

Deleting an old JD brief must leave the evidence workspace valid, and adding a new JD must not trigger source reprocessing when candidate revisions are unchanged.

## Main-agent and subagent authority

Subagents are optional context-isolation workers for main-selected unread repositories, reports, histories, or evidence conflicts; they are an economic tool for raw-source collection, not decision makers.

The main agent first reads every substantive index capsule, chooses what deserves deeper investigation, defines bounded target-neutral factual questions, and decides whether subagent isolation is worth its coordination cost.

Subagents do not receive a JD, target beliefs, comparative portfolio state, or authority to rank, shortlist, keep, discard, archive, revive, write resume prose, or recommend placement.

Each subagent returns compact source-bound findings: inspected source locators and revisions, factual observations, candidate-action and ownership evidence, measurement method and result, conflicts, unread relevant regions, and unresolved factual questions; narrative persuasion and repeated summaries are rejected.

The main agent reads every returned record, opens the decisive original locations for finalists, resolves cross-project relationships and conflicts, owns all durable document changes, and makes every comparative and resume decision.

If subagents are unavailable or their output is untrustworthy, the main agent performs the same selected investigation serially; no claim becomes safer merely because several agents repeated it.

## Context discipline

The main agent keeps the target brief and complete substantive index in context, then loads detailed evidence documents and original source regions only for plausible contenders or conflict resolution.

The substantive index reduces the search space without hiding the substance of the portfolio; it is intentionally richer than metadata and intentionally smaller than the detailed evidence documents.

Repository search begins from a bounded overview and source map, then narrows to files, commits, report sections, tests, benchmarks, or releases that could answer a concrete factual question; unbounded recursive reading and raw transcript retention are prohibited.

Hashes, Git revisions, file listings, and search tools may establish change and locate evidence without placing file bodies in context; they never substitute for reading substantive evidence used in a decision.

This is not a Markdown-only evidence claim: Markdown stores portable derived understanding, while original repositories, reports, PDFs, Git history, and candidate answers remain authoritative and are inspected with available local, GitHub, document, or PDF tools when needed.

## User interaction

For bulk intake, report what evidence documents were created, updated, reused, or archived and show a compact table of unresolved sources, ownership, conflicts, and candidate questions instead of dumping investigation notes.

For resume creation, show the target understood, candidate evidence reused or refreshed, exact delivered artifacts, evaluator verdict, and a compact `selected | omitted | reason | risk` table.

Questions are batched after the agent has exhausted available sources and are limited to facts that could change the outcome; the user is not asked to restate information already present in supplied material.

The final PDF must remain legible, aesthetically credible, information-dense without crowding, skimmable by a human, and defensible in interview discussion; passing deterministic checks or looking polished is not itself success.

## Minimal implementation surface

- Add `skills/candidate-evidence/SKILL.md` with the intake, currentness, archive, investigation, portability, and user-handoff contracts.
- Add one concise `candidate-evidence` reference defining the evidence workspace, substantive index, semantic document shape, and subagent return shape; do not add a database, service, generated-ID scheme, or custom retrieval layer.
- Narrow `skills/resume-builder/SKILL.md` to target-specific comparison, selection, construction, rendering, and handoff; remove ownership of broad source intake and durable career-vault maintenance.
- Retire or migrate the monolithic `resume-builder` career-vault reference so target-neutral evidence rules have one owner and target-specific directives cannot contaminate the durable workspace.
- Clarify in `jd-analyzer` that briefs are independent, temporary, and disposable; change evaluator and tracker only where their handoff boundary is currently inconsistent.
- Add focused workflow tests and portable fixtures before changing behavior; use existing source, render, PDF, and evaluation tools rather than inventing infrastructure.

## Behavioral acceptance criteria

- Skill descriptions route candidate files, one or many JDs, resume construction, exact-PDF evaluation, and application events to the correct skill or skill combination without an orchestrator.
- Existing unchanged evidence is reused, while a new or changed supplied source refreshes only affected semantic documents and index entries.
- The main agent reads a substantive overview for every supplied evidence body and the complete substantive index before filtering; zero-context metadata never decides what survives.
- Shared reports, mechanisms, roles, and outcomes are represented once with semantic relationships and cannot inflate the number of independent achievements.
- Durable evidence remains target-neutral, and deleting a stale JD brief does not remove or invalidate candidate evidence.
- Archived evidence remains visible through a substantive capsule and revival condition, old evidence can beat recent weak evidence, and novelty alone does not establish current value.
- Archive and currentness decisions based on external change cite current outcome-bearing evidence or remain explicitly uncertain; no inherited age or trend heuristic is accepted by default.
- Subagents return source-bound factual records without JD context, rankings, recommendations, archive decisions, or resume prose; the main agent verifies decisive originals and owns every decision.
- A 25-body portfolio can be compared without loading all repositories or reports into the main context, while the agent can still investigate any item whose substance could change selection.
- The delivered resume uses supported claims, survives exact-PDF structural and visual evaluation, and includes a compact user-facing explanation of consequential selections, omissions, and risks.
- No absolute machine path, hostname, home directory, agent-session identifier, hosted account, or private memory dependency appears in the portable skill or evidence format.

## Failure handling

If a supplied item lacks a substantive overview, the main agent performs a bounded source read or asks for the missing material and marks it unresolved; it does not infer value from metadata.

If source identity cannot be made portable, store a semantic named-root locator and mark freshness unknown; never persist the current machine's absolute path as a requirement.

If a subagent returns judgment, unsupported prose, omitted sources, or an overbroad dump, the main agent rejects or narrows that record and performs the decision-relevant verification itself.

If selective loading misses stronger evidence, weakens claim safety, or makes the final resume less useful than the current workflow, the implementation fails even if it saves tokens.

## Rollout boundary

The checkout is already dirty with unrelated staged and unstaged work; design, implementation, tests, and commits must name only files intentionally owned by this change and must preserve all other user changes.

The written specification requires user review before implementation planning, and implementation is not complete until focused workflow tests, the relevant existing suite, package inspection, an exact flagship render, and visual PDF review pass from an intentional diff.
