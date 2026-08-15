# Experience
Lifecycle: active
Scope: Meridian Labs internship and UW systems research
Dates: 2024-10 to 2025-09

## Meridian Labs internship

### Problem and context
The fixture describes retrieval evaluation, latency, and prompt-injection testing for two production assistants.

### Candidate actions and ownership
- Built the nightly Python/pytest RAG evaluation harness, implemented cache warming and HNSW retrieval changes, built the 41-case adversarial suite, and presented regression findings.
- Unknown: Collaborator contributions, deployment authority beyond the documented team decision, and the exact benchmark protocol.

### Mechanisms
- Nightly evaluation over 1,200 support tickets measured recall@10 and answer correctness; retrieval optimization paired latency improvement with a recall guardrail; adversarial cases became a required pre-deploy gate.

### Outcomes and artifacts
- 3 retrieval regressions caught before release; p95 retrieval latency reduced from 480 ms to 210 ms while recall@10 stayed within 1 point; 41 prompt-injection cases covered two assistants.

### Evidence map
- FACT: Candidate ownership is limited to implementation and presenting findings; sole production-deployment authority is not supported.
- SOURCE: `synthetic-source:../career-vault.md#experience` — sha256 `268f01e810c350fa868898ddd6b13328b0d3979e97ada49d65d97d98908f0cbd`.

## UW systems research

### Problem and context
The fixture describes bursty GPU-cluster workloads, published scheduling baselines, and starvation behavior.

### Candidate actions and ownership
- Built a trace-driven simulator, reproduced 3 baselines within 2%, added a starvation case, evaluated a preemption-aware policy, co-authored the paper as 2nd author, and presented the poster.
- Unknown: Policy ideation split, trace provenance, independent reproduction, and collaborator contributions.

### Mechanisms
- Trace-driven simulation compared published baselines and a preemption-aware policy while retaining completed-job count as a guardrail.

### Outcomes and artifacts
- Reduced p99 queueing delay 31% on bursty traces without reducing completed jobs.

### Evidence map
- FACT: Research result, paper, and poster share one source body and must not be counted as independent corroboration.
- SOURCE: `synthetic-source:../career-vault.md#experience` and `#publications-and-awards` — sha256 `268f01e810c350fa868898ddd6b13328b0d3979e97ada49d65d97d98908f0cbd`.

## Relationships
- Each experience is separate; mechanisms and results inside one experience share context.

## Currentness
- Historical support: The fixture dates the work to 2024-2025.
- Present capability: No recent source establishes retained proficiency.

## Conflicts and questions
- Conflict: None supplied.
- Question: Which repositories, benchmark records, deployment logs, paper records, and candidate explanations can establish ownership and measurement conditions?

## Lifecycle
- State: active.
- Reason: Both bodies preserve distinct supported mechanisms and outcomes.
- Revive when: Not applicable while active.
