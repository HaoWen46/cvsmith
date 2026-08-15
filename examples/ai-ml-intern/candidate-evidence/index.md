# Candidate evidence index
Updated: 2026-08-16

Synthetic fixture: Sam Casey and every identity, organization, result, date, and URL in this workspace are invented for cvsmith tests.

## Source state
- `synthetic-source:../career-vault.md` — sha256 `268f01e810c350fa868898ddd6b13328b0d3979e97ada49d65d97d98908f0cbd` — inspected 2026-08-16.
- Migration state: target-neutral facts, limitations, and source relationships were imported; the legacy target-specific omission decision was not imported.
- Authority: the unchanged legacy vault is the supplied source for this fixture; no independent employer, repository, publication, or identity verification exists.

## Active

### [Identity, education, and eligibility](education-and-eligibility.md)
- Scope and dates: Sam Casey in Seattle, WA; University of Washington B.S. in Computer Science from 2023-09 to 2027-12.
- Substance: Contact and education records plus a candidate-supplied US work-authorization statement.
- Contribution: Identity and eligibility are candidate records rather than authored work; no third-party identity check is represented.
- Strongest supported signals: Sam Casey; sam.casey@example.com; +1 (555) 010-4477; Seattle, WA; GitHub https://github.com/samcasey-demo; Portfolio https://samcasey.example.com; B.S.; Computer Science; GPA 3.8/4.0; Machine Learning, Distributed Systems, NLP, and Databases; Dean's List (6 quarters); US work authorization with no sponsorship required for internships.
- Source and ownership state: Supported only by `synthetic-source:../career-vault.md`; eligibility must be reconfirmed for any real submission.
- Currentness: Fixture state dated 2026-08-16; no real-world currentness is implied.
- Relationships: Education dates and authorization are potential application gates but remain target-neutral here.
- Material uncertainty: Legal identity, contact ownership, enrollment, GPA, graduation timing, and authorization are deliberately unverified synthetic values.

### [Meridian Labs internship](experience.md#meridian-labs-internship)
- Scope and dates: Machine Learning Engineering Intern at Meridian Labs in Seattle, WA from 2025-06 to 2025-09.
- Substance: Built retrieval evaluation, latency, and prompt-injection testing mechanisms for production assistants.
- Contribution: Candidate owned harness implementation and presented regression findings; the team, not the candidate alone, selected deployment decisions.
- Strongest supported signals: nightly Python/pytest RAG evals over 1,200 tickets; 3 retrieval regressions caught pre-release; retrieval p95 from 480 to 210 ms using cache warming and HNSW at stable recall@10; 41-case prompt-injection suite required to deploy two production assistants.
- Source and ownership state: Candidate-supplied fixture record only; no source code, benchmark log, ticket set, or deployment record is present.
- Currentness: Historical 2025 work; present proficiency is not separately established.
- Relationships: Evaluation, retrieval, and adversarial testing share one internship context and are not independent experiences.
- Material uncertainty: Dataset construction, quality threshold, production scale, and collaborators' exact contributions are unknown.

### [UW systems research](experience.md#uw-systems-research)
- Scope and dates: Undergraduate Research Assistant at UW Systems Research Group in Seattle, WA from 2024-10 to 2025-05.
- Substance: Built a trace-driven GPU cluster scheduling simulator and evaluated a preemption-aware policy.
- Contribution: Candidate built the simulator, reproduced 3 published baselines within 2%, added a starvation test, co-authored the related paper as 2nd author, and presented its poster.
- Strongest supported signals: GPU cluster scheduling; trace-driven simulation; p99 queueing delay reduced 31% on bursty traces without reducing completed jobs.
- Source and ownership state: Candidate-supplied fixture record only; simulator, traces, paper metadata, and author record are not independently inspected.
- Currentness: Historical 2024-2025 work; present capability is unknown.
- Relationships: Simulator results, publication, and poster are one shared research body rather than three independent signals.
- Material uncertainty: Trace provenance, baseline implementations, statistical variation, and policy authorship split are unknown.

### [Projects, publication, and award](projects-research-and-awards.md)
- Scope and dates: HuggingFace datasets contribution in 2025-08; whisperboard from 2024-01 to 2024-04; ledgerlite from 2023-03 to present; publication and award records dated 2024-2025.
- Substance: Open-source loader fixes, speech-model adaptation, an append-only finance CLI, one systems publication, and one programming-contest result.
- Contribution: Candidate-supplied records attribute the code and results to Sam Casey; repository presence, merged status, authorship, and award identity are not independently verified.
- Strongest supported signals: HuggingFace datasets — upstream contributor at https://github.com/huggingface/datasets/pull/DEMO-1 using Python; fixed CSV row loss and JSONL BOM failures with merged HuggingFace tests; whisperboard at https://github.com/samcasey-demo/whisperboard using Python and PyTorch; fine-tuned Whisper-small on 30 h and cut WER from 18.2% to 11.6% on held-out audio; ledgerlite at https://github.com/samcasey-demo/ledgerlite using Rust and SQLite; append-only finance CLI with double-entry validation; signed macOS/Linux releases, 1.4k stars, and 27 contributors.
- Source and ownership state: All facts derive from the legacy fixture; no linked artifact was fetched.
- Currentness: ledgerlite is recorded as present; every other item is historical and present maintenance is unknown.
- Relationships: The HotCloud publication belongs to the UW systems-research body and is not independent corroboration of the simulator result.
- Material uncertainty: Merge state, benchmark methods, current repository state, download signatures, contribution counts, publication status, and award identity are unknown.

## Skills inventory
- Languages: Python, Rust.
- ML: PyTorch, RAG pipelines, eval harnesses.
- Systems: HNSW, GPU cluster scheduling, Linux, SQLite.

## Publications and awards inventory
- Okafor, D., Casey, S., and Lin, M. (2025). Preemption-Aware Scheduling for Shared GPU Clusters. HotCloud Workshop. https://example.com/hotcloud25-preemption.pdf
- ACM ICPC Pacific Northwest Regional — 5th place — 2024-11.

## Archive
- None; the supplied source does not establish a target-neutral global reason to archive any body of work.

## Open factual questions
- Which source artifacts can independently establish contribution ownership, metrics, publication status, eligibility, and currentness?
- Which claims can the candidate explain precisely enough to defend in an interview?
