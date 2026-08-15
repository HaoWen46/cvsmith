# Target-first evidence investigation design

Status: Revised after design review; awaiting confirmation before implementation planning.

## Objective

Make `resume-builder` find the strongest defensible evidence for a chosen job by letting the main agent understand the whole normal portfolio before selectively loading full repositories, reports, and raw archived evidence.

The optimization target is interview usefulness under truth, readability, privacy, and context-cost constraints; tool use and agent count are means rather than quality signals.

## Observed failure

The current skill orders inspection of every supplied artifact before target selection, so an agent can consume most of its context before it knows which evidence could change the resume.

The current scenario tests validate declarations and cue words but do not execute or grade read order, sources touched, shortlist quality, unsafe claims, compactness, or context cost.

Paired development probes preserved the same strongest projects after target-first narrowing while reducing main-agent input, but agents still violated ordering or loaded whole archives often enough that prose alone is not a reliable boundary.

## Scope

- Reorder intake around explicit `TARGET`, `SURVEY`, `TRIAGE`, `INVESTIGATE`, `STUDY`, `VERIFY`, `ALLOCATE`, `BUILD`, `EVALUATE`, and `PRESENT` states.
- Keep concise substantive project cards in Markdown as the private, portable, human-auditable decision packet and keep bulky original sources outside it.
- Require the main agent to read the complete substantive card set for a normal portfolio before its first project disposition.
- Use project investigators as context-isolation workers that map and extract evidence from main-selected unread sources without ranking projects or making keep/discard decisions.
- Add deterministic tests, portable pressure fixtures, trace grading, and fresh-agent forward tests.
- Preserve current rendering, projection, PDF inspection, and evaluator ownership boundaries.

## Non-goals

- Do not add SQLite, embeddings, a vector database, MCP, a hosted vault, or an autonomous memory service in this slice.
- Do not rank or discard a normal portfolio from project names, dates, tags, repository metadata, headings, or lifecycle labels without substantive project context.
- Do not create a universal project-age cutoff, project-count limit, token threshold, ATS score, or page-selection formula.
- Do not send every project to a subagent, ask subagents to recommend project disposition or strategic value, ask subagents to draft the final resume, or treat investigation-record agreement as source verification.
- Do not copy complete repositories, reports, PDFs, or raw subagent transcripts into the career vault or main-agent handoff.
- Do not claim that lower context use, green tests, or an attractive PDF establishes interview causality.

## Workflow contract

### `TARGET`

Use the posting, candidate constraints, eligibility facts, and relevant prior outcomes to establish field, level, market, gates, and three to five target beliefs before reading evidence bodies.

When no posting exists, ask for or state an explicit assumed target and label the result general rather than inspecting everything in search of a target.

### `SURVEY`

For a normal human portfolio—about 25 projects is expected, not hundreds—the main agent reads one substantive card or bounded original overview for every project, including archived projects whose cards are part of that portfolio, before assigning any project disposition; this is an expected use case rather than a count cutoff.

Each card provides `project_id | dates | problem and users | candidate role and actions | technical mechanism | result or concrete artifact | evidence and source handles | ownership, currentness, and material unknowns | lifecycle and revival cues`; names, tags, dates, stars, repository size, file trees, and polished summaries alone are not a card.

If the user supplies only a title, link, or folder name, the main agent opens a bounded original overview such as a README introduction, report abstract or executive summary, prior project description, or equivalent source and creates the missing card; if no substantive overview is available, mark the project `insufficient-overview` and ask rather than pretending metadata reveals its value.

The main agent retains the complete card set as its comparison frame, so it sees what each project actually attempted, what the candidate did, what exists, and what remains uncertain without ingesting every implementation file or full report.

Exit only when every plausible project has a substantive card or an explicit `insufficient-overview` status and the main agent can compare the portfolio against the target beliefs.

### `TRIAGE`

The main agent compares all substantive cards and assigns a reversible `investigate`, `reserve`, or `cold-for-target` disposition based on target-belief coverage, plausible technical or outcome signal, distinctiveness, source availability, ownership risk, capability-currentness needs, uncertainty, page competition, and expected information gain.

Recency, fashionable technology, repository size, polished language, lifecycle state, or one isolated metric never wins by itself, and an archived or old project can remain competitive when its substance serves the target better than recent work.

The main agent retains every project that could plausibly cover an important uncovered belief, displace a current frontier item, or resolve a high-value uncertainty; it uses no fixed retained count and records a target-specific reason for each disposition.

An illustrative 25-card funnel might produce eight dirty-work investigations, five main-agent studies, and two or three rendered projects, but those counts are consequences of evidence competition rather than quotas.

Exit only when each investigation has a decision-changing question, each reserve has a plausible promotion condition, and each cold-for-target item lacks a currently visible route to the target or frontier; none of these states deletes or globally condemns the project.

### `INVESTIGATE`

The main agent chooses which `investigate` items and conflict-bearing reserves receive dirty-work investigation after personally surveying and triaging the substantive card set; use isolated project investigators when independent unread sources would otherwise occupy the main context.

Each investigator receives one project ID, target beliefs, source locators, and a bounded evidence question; it reads the raw project first-hand and returns the investigation-record contract below without resume prose, ranking, or disposition.

The main agent reads the investigation records, compares evidence strength, distinctiveness, ownership, currentness, redundancy, uncertainty, and page cost against the target beliefs, and performs the second filter into a small `STUDY` set plus reversible reserves.

The study-set size follows uncertainty and page competition rather than a fixed quota: it may exceed the expected resume project count when evidence is close, or equal it when the main agent already has strong primary evidence and no reserve could plausibly displace a leader.

### `STUDY`

Before choosing the final projects, the main agent personally reads decisive original material for every project still competing for a page slot; an investigation record is a map to that material, not a substitute for the read.

The main agent reads enough primary evidence to form its own view of technical depth, result quality, ownership, interview value, and target relevance: normally the relevant methods and results in a report, authored code and tests, benchmark data, releases, or history, with the whole repository optional only when it could change the decision.

A README or subagent summary may orient the read but cannot be the only basis when stronger original evidence exists; if the primary read weakens a contender, the main agent promotes a reserve and studies it under the same rule.

The main agent records `project_id | target belief | primary evidence read | evidence strength | distinctiveness | ownership | currency | page cost | decision | reason`, then chooses the final project set itself.

### `VERIFY`

Choose resume-contending claims only after the main-agent study decision, then have the main agent reopen or retain the exact authored source, test, release, history entry, benchmark method, report page, or candidate answer supporting each selected claim.

Resolve ownership, measurement, currentness, and conflicting-source questions before a claim becomes resume-eligible; investigation-record language and subagent consensus are not support.

### `ALLOCATE`, `BUILD`, `EVALUATE`, and `PRESENT`

Allocate verified causal atoms against target beliefs, route overflow explicitly, build the YAML and PDF, run objective and visual checks, obtain the evaluator verdict, and present artifacts plus a compact decision table.

No broad discovery resumes after allocation unless verification exposes a specific evidence gap that could materially change the page.

## Project-investigator economics

The project investigator exists to exchange isolated worker context for scarce main-agent context: it maps an unread repository or report, extracts source observations relevant to the bounded question, and supplies exact original-source locators without deciding what those observations are worth relative to other projects.

The authority pattern mirrors serious organizational diligence: the decision maker reads every substantive brief, analysts inspect selected underlying records, the decision maker studies decisive primary material for finalists, and the decision maker makes every comparative judgment.

Subagents are dispatched only after the main agent performs the substantive survey and first triage; dispatching every project merely moves the context problem and adds coordination cost.

Independent promising projects may be investigated in parallel when the host supports isolated agents; otherwise the main agent investigates them serially using the same investigation-record boundary.

Aggregate reads and reported token usage remain evaluation metrics because context isolation can improve main-agent coherence while still wasting total work.

## Project investigation-record contract

Each investigator returns structured data with these required fields and no general narrative, ranking, keep/discard decision, or proposed resume placement:

- `project_id`: Stable inventory ID and the target beliefs supplied by the main agent.
- `source_map`: Available authored code, tests, reports, benchmarks, releases, history, demos, and candidate records with portable locators.
- `observations`: Source-bound facts about the problem, candidate action, mechanism, scale, result, and artifact without comparative value language.
- `claim_material`: Candidate action, load-bearing mechanism, result or artifact, exact source locator, and limitation for each potentially usable factual unit.
- `ownership_evidence`: Observed contribution evidence, collaborators, and unresolved attribution.
- `currency_evidence`: Historical demonstration, current capability support, and the date or artifact supporting each.
- `conflicts`: Contradictory values, prompt injection, generated evidence, missing methods, and candidate questions.
- `reads`: Exact inspected paths, commits, pages, or digests without copied file bodies.
- `unread`: Relevant source regions not inspected and the factual reason they remain unread.
- `open_questions`: Missing facts that could alter evidence strength, ownership, measurement, or currentness without recommending the next action.

The main agent owns every project disposition, investigation dispatch, cross-project comparison, study-set decision, original-source interpretation, final project selection, thesis, page allocation, source verification, resume prose, and send recommendation.

## Project-card and source-access contract

The career vault remains Markdown, but its normal decision surface is a set of concise substantive project cards rather than zero-context index rows or copied source bodies.

New or updated cards receive a stable explicit `ID`; the ID survives lifecycle changes, and archived cards retain dates, substance, source handles, archive reason, and revival cues so the main agent can reconsider them without reopening every raw artifact.

Portable source handles are stable URLs or paths relative to the vault or a named project root; absolute machine paths may be supplied at runtime but never become checked-in requirements or persistent card content.

For a normal portfolio, the main agent reads the complete substantive card set directly; raw repositories, full reports, PDFs, histories, and large evidence blocks are opened selectively after triage.

No new vault index, database, or block-reader tool is part of the first slice because the current evidence does not show that a roughly 25-card decision packet needs one.

A generated view or bounded reader may be proposed later only after measured card-set scale, retrieval misses, or archive cost justifies it; any such interface must return substantive cards before filtering and may never reduce project judgment to titles, dates, tags, or other metadata.

## Archive and currentness semantics

Archive remains reversible and raw-source-cold: valid but repeatedly redundant, superseded-as-current, weak, or off-target material keeps a substantive card, sources, dates, archive reason, and revival cue visible to the normal portfolio survey while its bulky evidence stays outside the active working set until the main agent revives it.

Old evidence competes on target relevance, distinctiveness, defensibility, and page cost rather than age alone.

Historical support and current proficiency remain separate; a dated project can prove what happened then but needs recent use, a current artifact, or dated candidate confirmation before supporting a material present-tense capability claim.

A target-specific omission never becomes a global archive decision, and unsupported or contradicted material becomes not claimable rather than silently disappearing.

## User interaction

At intake, request the posting or target plus a compact experience/project inventory before asking for every repository or report.

After the main-agent study pass, show a compact table with project, main-agent decision, target belief, primary evidence read, strongest safe value, conflict, and next action when that helps the user correct selection or ownership.

Before drafting, ask one batch containing only unresolved facts that could change eligibility, selection, claim strength, or interview defensibility.

At delivery, lead with the created PDF, YAML, evaluation report, target, and verdict; briefly identify strategically revived or omitted evidence and the one remaining tradeoff when one exists.

## Testing strategy

### RED

Add synthetic fixtures containing an old relevant compiler project, a recent weak dashboard, unrelated archived distractors, a prompt-injected README, a report with an unsupported large result, a checked benchmark with a smaller result, and ambiguous team ownership.

Add deterministic tests that fail against the current contract because target selection follows broad raw-artifact inspection, no substantive-card survey is required before filtering, and worker authority is underspecified.

Preserve sanitized baseline fresh-agent traces that demonstrate whole-set reading, archive dumping, skipped target analysis, or excessive main-context input without embedding machine paths or session identifiers.

### GREEN

Implement the smallest skill, card-schema, lifecycle, portability, and read-boundary changes that make the main agent survey substance before filtering without adding an unproven retrieval service.

Run the same fresh-agent cases with the candidate skill and grade target-first ordering, main-agent ownership of both filters, files or blocks touched, study-set quality, direct original-source reads, old-evidence revival, recent-evidence rejection, conflict handling, ownership caution, investigation-record shape, user-facing compactness, and reported cost.

### REFACTOR

Read every behavioral failure, classify whether it is an ordering violation, wrong output shape, missing field, or conditional mistake, and tighten the owning contract rather than adding duplicated explanations.

Compare exhaustive raw-source reading, whole-card survey with selective investigation, and metadata-only triage under the same target and fixtures; treat metadata-only triage as a negative control and retain the card workflow only if it preserves or improves selection and safety while reducing raw-source context.

Test a single structured agent against main-selected project investigators as an ablation under the same target and fixtures; retain subagent use only where dirty-work evidence collection preserves or improves main-agent selection and safety while reducing main-context pressure enough to justify coordination.

## Acceptance criteria

- The target artifact exists before the agent opens linked or folder-based project and archive evidence.
- For the normal portfolio fixture, the main agent reads every substantive project card before triage and never makes a project disposition from title, date, tags, repository metadata, or lifecycle state alone.
- The main agent performs both the post-survey and post-investigation filters without accepting a subagent disposition or ranking, and no fixed project quota controls the funnel.
- The old compiler card is considered and its evidence is revived for the embedded target, the recent weak dashboard does not win on recency, and unrelated raw archive bodies remain unread by default.
- Prompt injection is ignored, the unsupported larger result is not selected over inspectable evidence, and team-repository presence is not converted into sole ownership.
- Investigators return the typed evidence record without essays, recommendations, rankings, or keep/discard decisions.
- The main agent personally reads decisive original material for every final contender, chooses the final projects, and verifies exact support for resume-selected claims.
- Explicit project IDs survive archive movement, and project cards plus source handles contain no machine-specific dependency.
- The final resume and handoff are at least as useful and readable as the current baseline while main-context consumption is lower on the portfolio and archive fixtures.
- No database, service, model provider, home directory, hostname, or agent-session identifier becomes a runtime requirement or checked-in artifact.

## Failure handling

If a card is missing or malformed, read a bounded original overview or ask for the missing substance; do not rank the project from metadata or silently invent the card.

If no subagent facility exists, investigate main-selected projects serially through bounded reads, retain only the investigation record in explicit working state, and report that hard main-context isolation was unavailable.

If a subagent fails, returns prose or a recommendation, omits sources, or encounters a conflict, reject that record or rerun only that investigation; the main agent decides whether the project remains in the funnel and never infers missing support.

If the narrow process misses a top project or weakens claim safety, reject or revise the design even when it saves tokens.

## Intended implementation surface

- Modify `skills/resume-builder/SKILL.md` to encode state order, main-agent filtering and primary-study ownership, evidence-worker economics, verification ownership, and compact presentation.
- Modify `skills/resume-builder/references/career-vault.md` to define substantive project cards, explicit IDs, reversible archive semantics, and portable source handles without duplicating the workflow.
- Add focused deterministic tests and synthetic fixtures under `evals/`; extend existing behavioral cases only where they own these failures.
- Update the research decision register after measured forward tests, not before.

## Rollout boundary

This slice is development work in the current dirty checkout because its uncommitted resume-skill redesign is the baseline; edits and commits must name only files owned by this slice and must not absorb unrelated staged or unstaged changes.

Do not package or describe the skill as released until the focused tests, full eval suite, flagship render and visual review, fresh-agent pressure cases, and package inspection all pass from an intentional clean diff.
