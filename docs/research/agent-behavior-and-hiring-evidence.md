# Research baseline: agent behavior, portfolio retrieval, and hiring evidence

Status: Evidence review and bounded local pressure test; not an approved production redesign.

Updated: 2026-08-15

## Purpose

cvsmith should help a candidate obtain appropriate interviews with a truthful, defensible, role-specific resume; artifact beauty, agent sophistication, token use, and test coverage are constraints or intermediate measures, not the objective.

The expected intake is a current job description plus a candidate or project inventory, followed by selective inspection of repositories, reports, prior resumes, and archived evidence only when a read can change selection or claim strength.

The central engineering question is not whether instructions sound persuasive; it is whether the model-harness system follows the intended read order, preserves evidence boundaries, stops searching at a defensible point, and produces an application artifact that survives parser and human screening.

## Decision summary

| Question | Current conclusion | Confidence | Product consequence |
| --- | --- | --- | --- |
| Can a Skill change agent behavior? | Yes, sometimes materially, but gains depend on the exact skill, task, model, harness, retrieval path, and verifier; irrelevant or stale skills can hurt. | High for conditionality; low for cvsmith effect size. | Keep the skill focused and evaluate it against no-skill and prior-skill baselines on the actual Codex workflow. |
| Is prose alone enough to control intake? | No; the local tests produced sensible answers but violated prescribed read order or skipped required workflow components. | Medium from bounded local tests plus agent-interface research. | Use explicit state artifacts, constrained transitions, observable read traces, and executable checks where semantics permit. |
| Should all supplied projects be inspected first? | The main agent should inspect a substantive overview of every project in the expected normal portfolio after fixing the target, but should not deep-read every raw artifact. | Medium; local probes support selective raw reads but did not test metadata-only filtering against whole-card review. | Use target-first whole-portfolio survey, main-agent triage, selective dirty-work investigation, main-agent original-source study, and exact-claim verification. |
| Should full context always be rejected? | No; small, fully observable inputs can be cheaper and more accurate to load directly, while large or trajectory-heavy inputs need pruning and retrieval. | High that no universal rule exists. | Make the retrieval policy conditional on bounded size and observability rather than worshipping either long context or RAG. |
| Is a Markdown vault sufficient? | Markdown is sufficient for a bounded set of substantive project cards; it is not a reason to paste full reports, repositories, or trajectory history into context. | Medium; the archive probe shows bad read order and verbose output, not that a 60-line vault needs a retrieval service. | Keep concise cards directly readable and raw sources external; add an index or reader only after measured scale or retrieval failures justify it. |
| Should old material be deleted by age? | No; age, historical validity, present proficiency, target relevance, evidence quality, and page value are different variables. | High for rejecting a universal cutoff; low for any universal replacement formula. | Archive cold evidence reversibly, revive by target and gap, and require current evidence only for present-tense capability claims. |
| Should one subagent inspect every project? | No; multi-agent systems add coordination and verification failure surfaces and often lose to a structured single agent under matched budgets. | Medium across non-resume benchmarks. | Let the main agent survey and triage all cards, delegate only selected dirty-work investigations or conflict checks, require factual records, and make the main agent study finalists and verify every selected claim. |
| What resume intervention has causal hiring support? | Clearer, lower-error writing has direct field evidence; most popular layout, keyword, page-count, quantification, and recency rules do not. | High for the narrow writing result; low for broad transfer to technical corporate hiring. | Preserve rigorous proofreading and readable hierarchy, but do not encode unsupported ATS or formatting folklore as optimization truth. |
| Is visual quality irrelevant? | No; it is a defensive constraint and a human-screening interface, not a proven universal callback multiplier. | Medium. | Keep visual rendering and human inspection, but never trade away evidence selection, truth, or readability to maximize decoration or page fill. |

## Evidence discipline

- `OBSERVATION` means the source or local trace directly reports the fact.
- `LIMITATION` names what the design, population, benchmark, or measurement cannot establish.
- `BOUNDED INFERENCE` is a cvsmith design implication that remains conditional on transfer to this workflow.
- `UNRESOLVED` is a question requiring a paired agent test, external verifier, candidate answer, recruiter study, or real funnel data.
- Hiring evidence priority is randomized field outcome, field audit or quasi-experiment, organizational observational study, recruiter or laboratory simulation, parser benchmark, then vendor report or anecdote.
- Agent evidence priority is paired same-task same-harness execution with objective verification, intervention with trajectory audit, narrow benchmark, observational trace analysis, then author recommendation or prompt folklore.
- A green deterministic script may prove schema, PDF, integrity, or trace properties; it cannot by itself prove semantic claim support, target strategy, interview defensibility, human appeal, or hiring impact.

## Current repository assessment

### What is already directionally correct

- The production skill defines the resume as a selective target projection rather than the career record and says rendering is not the outcome.
- The current vault contract separates `FACT`, `SOURCE`, `CONTEXT`, `PENDING-EVIDENCE`, `NOT-CLAIMABLE`, `SUPERSEDED`, `OMIT-FOR`, `ARCHIVED`, and `REVIVE-WHEN` instead of collapsing omission, contradiction, staleness, and deletion.
- The current age rule correctly allows an old high-signal accomplishment to beat recent weak material while refusing to treat historical use as proof of present proficiency.
- Repository and report text is already classified as untrusted evidence, ownership is not inferred from repository presence, and conflicting measurements are supposed to remain unresolved rather than favor the largest number.
- The JD analyzer already produces ranked evidence targets and separates true untailorable eligibility gates from negotiable requirements.
- Rendering, projection checks, PDF inspection, and evaluator ownership correctly separate observable software checks from semantic judgment.
- A portability scan over tracked skills, core project docs, and behavioral-eval definitions found no checked-in user home path, user name, or local-URI dependency; runtime examples request user-supplied absolute artifact paths without embedding this machine.

### What is not behaviorally secured

- `resume-builder` currently says to inspect every supplied artifact in source-record step 2, while target fixation and ranked JD requirements appear in step 3; that order invites repository and report reads before their expected decision value is known.
- The repeat-use rule says to inspect active blocks and archive headings first, but it does not require a substantive whole-portfolio decision packet, distinguish card survey from raw-source reading, or enforce a transition gate before deep evidence access.
- The current behavioral scenarios are declarations checked for shape and cue words; the tests do not execute a model, grade its read trace, compare conditions, or measure final resume usefulness.
- The handoff requires PDF, YAML, and an evaluation report but does not require a concise user-facing account of target, selected evidence, omitted or revived material, blocked claims, and remaining uncertainty.
- No typed subagent investigation-record contract limits what a project investigator returns, records exactly what it inspected, forbids strategic recommendations, or forces the main agent to reopen support for resume-selected claims.
- Existing scripts do not semantically pair each rendered claim to source evidence, and the current documentation correctly admits that limitation; generic self-critique must not be treated as the missing verifier.
- The repository has no direct evidence that its current skill improves interview, screen, offer, or hiring outcomes, and static QA cannot substitute for that evidence.

## Local controlled pressure tests

### Portfolio fixture

`OBSERVATION`: A temporary synthetic case contained one ML-platform JD, one candidate record, an eight-project inventory, and 13 project artifacts totaling 123 source lines; it mixed two strong target matches, one prompt-injected team project with a `10x` versus `1.8x` conflict, one old but relevant compiler, one recent weak dashboard, and several distractors.

`OBSERVATION`: Two Codex model tiers each ran one unchanged-skill baseline and one experimental `TARGET -> INVENTORY -> PROBE` overlay under the same read-only harness, disabled plugins and memories, identical output schema, and a stop-before-drafting checkpoint.

| Model tier | Arm | Project artifacts read | Cumulative input tokens | Cached input tokens | Output tokens | Top two |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Smaller | Current skill | 12 across all 8 projects | 75,070 | 58,624 | 7,316 | EvalForge, QueueWeaver |
| Smaller | State overlay | 5 overviews across 5 projects | 62,129 | 47,488 | 7,003 | EvalForge, QueueWeaver |
| Stronger | Current skill | 13 across all 8 projects | 154,238 | 133,888 | 8,026 | EvalForge, QueueWeaver |
| Stronger | State overlay | 9 across 5 projects | 134,832 | 105,216 | 5,819 | EvalForge, QueueWeaver |

`OBSERVATION`: The overlay reduced reported cumulative input tokens by 17.2% on the smaller model and 12.6% on the stronger model while preserving the top two projects and the rejection of the recent weak dashboard.

`OBSERVATION`: The smaller overlay read the portfolio before the candidate record despite the stated transition order and stopped before validating the strongest outcome; the stronger overlay followed the target order but skipped the production skill's required JD-analyzer handoff and still deep-read decision-critical reports.

`LIMITATION`: CLI input-token totals are cumulative across model turns and include repeated harness context, so they are a comparable workflow-cost signal within each paired run, not the literal size of one final context window.

`LIMITATION`: Each cell has one trajectory, the prompts differ by the experimental overlay, the fixture is synthetic, and the checkpoint tests intake rather than final resume quality or interviews; these results reject complacency but do not establish a production effect size.

`BOUNDED INFERENCE`: Target-first state control can reduce unnecessary reads without obviously damaging shortlist quality, but a prose overlay cannot guarantee transition fidelity or retention of every required subsystem.

### Archive fixture

`OBSERVATION`: A repeat-use test supplied a 12-entry archive, a recent weak active project, an old compiler, an old RTOS project, stale Kubernetes evidence, and a new embedded-systems JD.

`OBSERVATION`: The agent correctly revived the 2018 compiler and 2019 RTOS evidence, rejected the recent dashboard, and distinguished dated accomplishment support from present C or C++ proficiency.

`OBSERVATION`: The same agent read the entire vault before reading the JD and returned a decision row for every cold archive entry, consuming 42,413 cumulative input tokens and 15,149 output tokens for a short 60-line vault.

`LIMITATION`: The vault was small enough that a full read was not operationally catastrophic, and only one smaller-model trajectory ran; the test demonstrates that current instructions do not enforce selective retrieval, not how cost scales on every model.

`BOUNDED INFERENCE`: The current evidence-lifecycle semantics are substantially better than an age cutoff, but the workflow needs to fix the target before survey, separate concise card review from raw-source access, and suppress irrelevant decision narration; this trace does not justify a database, index, or block-reader requirement.

## What current agent research supports

### Skills are conditional interventions

- `OBSERVATION`: [SkillsBench v4](https://arxiv.org/abs/2602.12670) reports 87 deterministic tasks, 18 model-harness configurations, and a mean pass-rate change from 33.9% without curated skills to 50.5% with them; focused bundles and compact or standard documentation outperform larger or comprehensive bundles in its analysis.
- `LIMITATION`: SkillsBench uses carefully curated specialist tasks and skills, only three selected public trials per cell, and no resume domain; its aggregate cannot prove cvsmith helps or identify the optimal cvsmith workflow.
- `OBSERVATION`: [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) reports only a 1.2-point aggregate improvement across about 565 fixed-commit tasks, zero pass-rate improvement for 39 of 49 public skills, 10.5% average token overhead, and degradation from some version-mismatched guidance.
- `OBSERVATION`: [Skills in realistic settings](https://arxiv.org/abs/2604.04323) reports that retrieval and distractors erode curated-skill gains and that query-specific refinement can recover performance when initial skills are relevant, while also hurting at least one reported setup.
- `BOUNDED INFERENCE`: A portable skill is useful only when it is accurate, compact, task-relevant, discoverable by the harness, and tested against negative interference; loading or generating more skill text is not itself progress.

### State, interfaces, and feedback matter more than slogans

- `OBSERVATION`: [StateFlow](https://arxiv.org/abs/2403.11322) improved narrow interactive benchmarks by encoding explicit states, legal actions, feedback, and termination rather than relying on an undifferentiated ReAct loop.
- `OBSERVATION`: [SWE-agent](https://arxiv.org/abs/2405.15793) found that bounded file views, concise tool feedback, edit guardrails, and compressed history changed coding-agent outcomes; in its 300-task ablation, a 100-line view beat full-file display and the last five observations beat full history.
- `OBSERVATION`: [Agentless](https://arxiv.org/abs/2407.01489) showed that a simple localization, repair, and validation pipeline could be competitive with more autonomous coding agents, and external reproduction or regression tests materially improved patch selection.
- `BOUNDED INFERENCE`: cvsmith should use named states with explicit entry artifacts, permitted reads, outputs, and exit gates, then verify the trace; merely placing numbered prose sections in a skill is weaker control.

### Retrieval must be adaptive

- `OBSERVATION`: [Agent Retrieval Bench](https://arxiv.org/abs/2607.24882) reports no universally dominant repository retrieval method and shows that logged agents can miss every gold file on a substantial share of tasks even with retrieval support.
- `OBSERVATION`: [Long Context vs. RAG](https://arxiv.org/abs/2501.01880) found long context ahead of the best tested RAG setup on its filtered text-QA corpus while RAG uniquely solved some questions; this is contradictory evidence against a universal retrieval rule.
- `OBSERVATION`: SWE-agent's own ablations found both too little and too much file context harmful, and exhaustive iterative search could underperform no dedicated search tool.
- `BOUNDED INFERENCE`: Load a small, bounded, fully observable source directly; otherwise retrieve progressively from an inventory, preserve an escape path when retrieval is wrong, and measure both misses and context cost.

### Memory is a retrieval policy, not a pile of notes

- `OBSERVATION`: [Agent Workflow Memory](https://arxiv.org/abs/2409.07429) improved WebArena task success and reduced steps by selectively reusing induced workflows, but its online method could learn incorrect workflows and incompatible memories could impair one another.
- `BOUNDED INFERENCE`: cvsmith memory should retain evidence identity, lifecycle, currentness, source lineage, and reusable workflow state; it should not replay raw histories or treat a prior resume's wording as source truth.
- `UNRESOLVED`: No reviewed study establishes that a Markdown, JSONL, SQLite, vector, graph, or hybrid career vault produces better technical-hiring outcomes; the format must be selected by measured retrieval fidelity, portability, privacy, and maintenance cost.

### Subagents are conditional and untrusted

- `OBSERVATION`: [MAST](https://arxiv.org/abs/2503.13657) analyzes failures across seven multi-agent systems and reports system failure rates from 41% to 86.7%, including context loss, task violations, repetition, incomplete verification, and incorrect termination; an objective-verification intervention improved one studied workflow but did not make the class reliable.
- `OBSERVATION`: [Intrinsic self-correction research](https://arxiv.org/abs/2310.01798) found that model-only critique often failed or degraded reasoning without external feedback and that multi-agent debate did not beat matched self-consistency in its tested setup.
- `BOUNDED INFERENCE`: Use a subagent only to isolate or parallelize a main-selected project investigation, never because “more agents” sounds thorough; require a bounded factual record without recommendations and make the main agent study decisive originals and verify selected claims.

## What hiring research supports

- `OBSERVATION`: A [randomized field experiment with nearly half a million online-labor-market jobseekers](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.04528) found that nongenerative writing assistance reduced errors, improved readability, increased hiring by about 8%, and increased wages by about 10% without detected employer-satisfaction harm.
- `LIMITATION`: That experiment concerned new platform entrants, profile text in an online contract market, and nongenerative writing assistance; it does not establish that LLM tailoring, technical-project selection, quantified bullets, one-page layouts, or ATS keyword strategies cause corporate interviews.
- `OBSERVATION`: A [scenario experiment with 445 recruiters](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283280) found lower stated interview probabilities for resumes with spelling errors, supporting rigorous proofreading but not a real-world callback effect by itself.
- `OBSERVATION`: A [preregistered UK audit field experiment with 9,022 applications](https://pubmed.ncbi.nlm.nih.gov/36471010/) found that expressing prior employment as years worked rather than calendar dates increased callbacks relative to both gap and no-gap conditions, apparently by making experience more salient.
- `LIMITATION`: The employment-gap result is a specific truthful representation intervention; it does not justify deleting dates, concealing chronology, or applying one date format in every market.
- `OBSERVATION`: [Hiring as Exploration](https://academic.oup.com/restud/article/93/2/1200/8160842) uses 88,666 applications from one Fortune 500 firm and models exploration-aware screening that could improve selected-candidate hiring rates and diversity relative to historical practice and supervised selection.
- `LIMITATION`: Hiring as Exploration is archival and counterfactual, faces selective labels, and studies firm screening rather than resume writing; at most it motivates retaining uncertain high-upside evidence for cheap probes instead of ranking only familiar signals.
- `UNRESOLVED`: No strong recent field evidence found in this review isolates a universal benefit from one-page resumes, a specific layout, columns, a font, keyword density, an ATS score, mandatory quantified bullets, action verbs, a six-second scan rule, a last-ten-years cutoff, or a fixed technical-skill recency window.
- `BOUNDED INFERENCE`: cvsmith should treat readable hierarchy, parser-safe structure, error-free prose, and socially ordinary design as defensive requirements while testing strategic content choices rather than presenting aesthetic or ATS folklore as causal truth.

## Candidate workflow hypothesis to test

This state machine is a falsifiable design hypothesis derived from the evidence and local traces; it is not yet the production contract.

| State | Permitted evidence access | Required state artifact | Exit gate |
| --- | --- | --- | --- |
| `TARGET` | JD snapshot, user constraints, eligibility records, relevant prior funnel facts only. | Ranked target beliefs, gates, level, market, and uncertainty. | Target is explicit or clearly labeled as assumed. |
| `SURVEY` | One substantive card or bounded original overview for every project in the normal portfolio, including archived cards; no bulk raw-source reads. | Complete comparison frame covering problem, candidate role, mechanism, result or artifact, sources, currentness, ownership, and unknowns. | Every project has substance or an explicit `insufficient-overview` status. |
| `TRIAGE` | Complete card set and target beliefs. | Main-agent `investigate`, `reserve`, or `cold-for-target` decisions with target-specific reasons and promotion conditions. | Each investigation has a decision-changing question and no disposition rests on metadata alone. |
| `INVESTIGATE` | Main-selected repositories, reports, histories, or conflict-bearing evidence, optionally isolated in workers. | Factual source maps, observations, claim material, conflicts, reads, unread regions, and open questions without ranking or recommendations. | The main agent can identify the projects still capable of winning page space. |
| `STUDY` | Decisive original material for every final contender, read by the main agent. | Cross-project comparison and main-agent final project selection. | The main agent has formed its own view and no unstudied reserve could plausibly displace a winner. |
| `VERIFY` | Exact authored code, tests, releases, history, report methods, benchmark data, and candidate answers for selected claims. | Source-bound support record for each resume-eligible claim. | Every selected claim has support, limitations, ownership status, and currentness scope. |
| `ALLOCATE` | Verified support records and target beliefs; no new broad discovery. | One row per candidate bullet plus explicit overflow and omission routing. | Page slots carry the strongest nonredundant beliefs. |
| `BUILD` | Allocation, writing rules, schema, and selected template. | YAML and rendered PDF. | Objective build checks pass and the page is visually coherent. |
| `EVALUATE` | Current PDF bytes, YAML, target analysis, vault evidence, and objective reports. | Verdict with blockers, high-value revisions, and residual uncertainty. | `READY TO SEND` and no accessible high-value improvement remains. |
| `PRESENT` | Final artifacts and compact decision history. | User-facing handoff table and artifact links. | User can understand what was built, why, what was omitted, and what remains uncertain. |
| `LEARN` | Confirmed application event and later funnel outcome. | Immutable sent-artifact record plus descriptive outcome. | Outcome is logged without claiming wording causality. |

## Context and vault architecture hypothesis

- Keep raw resumes, reports, repositories, and PDFs as external source artifacts; do not copy their complete contents into the main agent context or the vault.
- Represent each project with a stable ID and a concise substantive card containing dates, problem, candidate role and actions, technical mechanism, result or artifact, source locators, ownership status, currentness scope, material unknowns, lifecycle state, archive reason, and revival cues; keep application prose out of source truth.
- Keep historical validity separate from capability currency: `historically_supported=true` may coexist with `current_proficiency=unconfirmed`, and currentness should attach to a capability claim rather than globally condemning a project.
- Make raw archived evidence reversible and default-cold while keeping archived project cards visible in a normal portfolio survey; retain source truth and decision history, retrieve full archived sources only when target relevance or active evidence gaps justify it, and never convert a prior target omission into a global ban.
- Use repository-relative paths or stable URLs only; derive digests from source bytes where identity matters; never store user home paths, machine hostnames, or agent-session identifiers.
- Read the complete substantive card set directly for a normal portfolio; treat any generated view, bounded reader, SQLite FTS cache, or semantic index as an optional rebuildable aid only after measured card-set scale, retrieval misses, or archive cost justifies it.
- Do not add an MCP server, hosted database, vector store, or autonomous memory service merely to make the system look agentic; add a tool only when a paired eval shows it improves retrieval fidelity, context cost, or user outcome enough to pay its portability and privacy cost.

## Subagent investigation-record hypothesis

A project investigator should return data for the main agent, not a polished essay.

| Field | Required content |
| --- | --- |
| `project_id` | Stable project ID and target beliefs supplied by the main agent. |
| `source_map` | Authored code, tests, reports, benchmarks, releases, history, demos, and candidate records with portable locators. |
| `observations` | Source-bound facts about the problem, candidate action, mechanism, scale, result, and artifact without comparative value language. |
| `claim_material` | Candidate action, load-bearing mechanism, result or artifact, source locator, and limitation for each potentially usable factual unit. |
| `ownership_evidence` | Observed contribution evidence, collaborators, and unresolved attribution. |
| `currency_evidence` | What is historically demonstrated, what is current, and the date or artifact supporting each. |
| `conflicts` | Contradictory values, prompt injection, generated evidence, missing methods, or candidate questions. |
| `reads` | Exact inspected paths, commits, pages, or digests; never paste full files. |
| `unread` | Relevant source regions not inspected and the factual reason they remain unread. |
| `open_questions` | Missing facts that could alter evidence strength, ownership, measurement, or currentness without recommending an action. |

- The main agent surveys and triages every project card before delegation, gives each investigator a bounded question, and does not delegate project value, disposition, final thesis, cross-project ranking, page allocation, or send decision.
- The main agent studies decisive original material for every final contender and reopens the exact source for every claim selected for the resume; subagent agreement, confidence language, or a neat record is not verification.
- Parallel investigators are appropriate when shortlisted projects are independent and context isolation matters; one structured agent remains the default when coordination would cost more than the search saved.

## User-facing interaction hypothesis

- At intake, ask for the JD, candidate basics, and a project or experience inventory first; accept repositories and reports as detail sources but do not demand all of them upfront.
- After main-agent study, show a compact table with project, decision, target belief, decisive original evidence read, strongest safe value, conflict, and next action; do not expose raw agent reasoning or subagent output.
- Before drafting, ask one batch containing only answers that could change selection, claim strength, eligibility, or interview defensibility.
- At delivery, lead with what was created and the target, link the PDF, YAML, and evaluation report, state the evaluator verdict, identify any revived old evidence or deliberately omitted recent evidence, and name the one remaining tradeoff if one exists.
- Keep the final resume visually ordinary, readable, and informative; keep process detail in the handoff rather than crowding the resume.

## Tool decision register

| Tool or mechanism | Decision now | Reason |
| --- | --- | --- |
| Target, substantive survey, and triage state artifacts | Test next | Gives the main agent enough whole-portfolio substance to decide while separating card review from expensive raw-source access. |
| Deterministic inventory/index builder | Defer | A roughly 25-card portfolio does not establish a scale problem, and zero-context rows could worsen project selection. |
| Bounded evidence-block reader | Defer | Add only if measured raw-archive access or card-set scale defeats ordinary selective file reads; it must expose substantive cards before filtering. |
| Existing render, PDF, parser, integrity, and projection tools | Keep | They provide external feedback for observable artifact properties and should remain separate from semantic judgment. |
| Typed project-investigator schema | Test conditionally | Could isolate repository context and conflicts, but only after shortlist and with main-agent source verification. |
| SQLite FTS cache | Defer | Portable and local, but unnecessary until direct card reading shows measured miss or scale problems. |
| Embedding or vector database | Defer | No current evidence that semantic retrieval benefit offsets installation, privacy, staleness, and false-relevance risks for typical portfolios. |
| MCP or hosted vault service | Reject by default | Expands deployment, privacy, and maintenance scope without evidence that the normal local-folder use case needs it. |
| Generic reflection or agent debate | Reject as verifier | Model-only critique is not grounded claim verification and can add cost or regressions. |

## Evaluation required before production changes

- Convert the temporary portfolio and archive fixtures into executable, repository-portable behavioral evals whose grader inspects read order, files touched, shortlist quality, conflict handling, currentness, report compactness, and cumulative cost.
- Compare no skill, current skill, exhaustive raw-source reading, whole-card survey with selective investigation, and metadata-only triage under the same model-harness stack; use metadata-only triage as a negative control and include distractors, prompt-injected sources, conflicting measurements, old relevant evidence, and recent weak evidence.
- Run repeated paired trajectories across at least a weaker and stronger supported model, then expand only until the uncertainty around shortlist errors, unsafe claims, and cost deltas is small enough for a release decision; do not choose a ceremonial run count in advance.
- Grade the final artifact separately from intake: blind target coverage, semantic source support, interview defensibility, parser output, visual inspection, concise handoff, and any regression against the current resume baseline.
- Test subagents as an ablation, not a default: single structured agent versus shortlisted parallel investigators under matched or reported token budgets, with main-agent verification held constant.
- Log real applications only with exact sent artifacts and confirmed funnel states; use outcomes descriptively unless assignment or a defensible causal design separates wording effects from candidate, role, timing, market, and application-selection confounds.
- Reject a candidate design if it saves tokens by missing a top project, weakens truth or ownership checks, hides uncertainty, worsens human readability, or becomes machine-specific.

## Claims explicitly not adopted

- No universal project-age cutoff, last-ten-years rule, or automatic preference for recent technology.
- No universal one-page rule, six-second rule, ATS score, keyword-density target, quantified-bullet mandate, or action-verb formula.
- No assumption that a parser benchmark describes every employer's ATS or that one-column layout is a causal hiring optimizer.
- No assumption that every project deserves a subagent, every report deserves deep reading, or every source belongs in a persistent vault.
- No filtering of a normal portfolio from names, dates, tags, stars, repository metadata, headings, or lifecycle labels without substantive project context.
- No assumption that Markdown alone bounds retrieval, that a vector database automatically fixes retrieval, or that a longer context automatically fixes missing evidence.
- No assumption that subagent consensus, self-critique, a static scenario file, a green test suite, an evaluator score, or an attractive PDF proves interview effectiveness.
- No deletion of truthful history merely because the industry changed; material becomes cold, noncurrent, superseded, contradicted, or target-omitted for explicit reasons and can be revived only under an explicit evidence contract.

## Primary sources

- [SkillsBench v4](https://arxiv.org/abs/2602.12670) — paired curated-skill benchmark across models and harnesses; preprint revised in 2026.
- [SWE-Skills-Bench](https://arxiv.org/abs/2603.15401) — fixed-commit public SWE-skill benchmark; 2026 preprint.
- [Skills in realistic settings](https://arxiv.org/abs/2604.04323) — retrieval, distractor, and refinement conditions; 2026 preprint.
- [StateFlow](https://arxiv.org/abs/2403.11322) — explicit state-driven agent workflows.
- [SWE-agent](https://arxiv.org/abs/2405.15793) — agent-computer interface and context ablations.
- [Agentless](https://arxiv.org/abs/2407.01489) — simple staged localization, repair, and validation.
- [Agent Workflow Memory](https://arxiv.org/abs/2409.07429) — selective workflow-memory induction and reuse.
- [Agent Retrieval Bench](https://arxiv.org/abs/2607.24882) — repository-context retrieval; 2026 preprint.
- [Long Context vs. RAG](https://arxiv.org/abs/2501.01880) — contradictory full-context evidence from text QA.
- [MAST](https://arxiv.org/abs/2503.13657) — taxonomy and trace analysis of multi-agent failure.
- [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) — intrinsic self-correction and matched-response critique evidence.
- [Algorithmic Writing Assistance on Jobseekers' Resumes Increases Hires](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.04528) — randomized online-labor-market field experiment.
- [Costly mistakes](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0283280) — recruiter scenario experiment on spelling errors.
- [Reducing discrimination against job seekers with and without employment gaps](https://pubmed.ncbi.nlm.nih.gov/36471010/) — preregistered UK audit field experiment and lab follow-ups.
- [Hiring as Exploration](https://academic.oup.com/restud/article/93/2/1200/8160842) — archival and counterfactual high-skill screening study.
