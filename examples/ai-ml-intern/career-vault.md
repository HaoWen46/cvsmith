# Career vault — Sam Casey

Synthetic fixture — "Sam Casey" does not exist. Every employer, metric,
date, and URL below is invented for this worked example, matching
[`resume.yaml`](../../evals/fixtures/resume-sample/resume.yaml) fact for
fact — this file is that resume's source evidence, authored per
`skills/resume-builder/references/career-vault.md`'s format so the pair
is self-verifying: run
`skills/resume-builder/scripts/check_projection.py
evals/fixtures/resume-sample/resume.yaml examples/ai-ml-intern/career-vault.md`
and every hard fact in the resume traces back to a line here (see
[`projection-report.md`](projection-report.md) for the actual run).

Updated: 2026-07-15

## Basics
- FACT: Sam Casey · sam.casey@example.com · +1 (555) 010-4477 · Seattle, WA
- FACT: GitHub profile — https://github.com/samcasey-demo
- FACT: portfolio site — https://samcasey.example.com

## Education
### University of Washington — B.S. Computer Science (Sep 2022 – Jun 2026)
- FACT: started fall quarter, Sep 2022; on track to graduate Jun 2026
  (not yet conferred — see Gaps & flags)
- FACT: cumulative GPA 3.8 / 4.0
- FACT: coursework that matters for tailoring: Machine Learning,
  Distributed Systems, NLP, Databases
- FACT: Dean's List, 6 quarters

## Experience
### Meridian Labs — Machine Learning Engineering Intern (Jun 2025 – Sep 2025) [group: industry]
- FACT: built an offline evaluation harness for a RAG customer-support
  assistant (Python, pytest); ran nightly against 1,200 historical
  support tickets and caught 3 retrieval regressions before they shipped
- FACT: cut p95 retrieval latency from 480 ms to 210 ms by warming the
  embedding cache on deploy and switching the vector index from flat
  search to HNSW
- FACT: wrote the team's prompt-injection red-team suite — 41 cases —
  now a required pre-deploy gate for two production assistants
- CONTEXT: manager named the eval harness as the internship's main win;
  fine to name as a reference
- CUT: also touched on-call rotation shadowing — too thin to quantify,
  left off the resume

### UW Systems Research Group — Undergraduate Research Assistant (Oct 2024 – May 2025) [group: research]
- FACT: built a trace-driven simulator for GPU cluster schedulers
  (Python); reproduced 3 published baselines within 2% and surfaced a
  starvation edge case now in the group's benchmark suite
- FACT: co-authored (2nd author) a HotCloud 2025 workshop paper,
  "Preemption-Aware Scheduling for Shared GPU Clusters"; presented the
  poster session personally. project_notes.md lists the names as
  "Casey, Okafor, Lin" but also says "2nd author" — those don't agree
  on who's first; see Publications below for the confirmed author
  order and the Q&A log for how it was resolved
- CONTEXT: Prof. Lin's systems group — official name is "UW Systems
  Research Group," not the "UW research lab" shorthand on the old resume

## Projects
### ledgerlite (ongoing since 2023)
- FACT: append-only personal-finance CLI (Rust, SQLite) with
  double-entry validation; 1.4k GitHub stars, 27 external contributors,
  signed releases for macOS and Linux
- FACT: repo — https://github.com/samcasey-demo/ledgerlite

### whisperboard (Jan 2024 – Apr 2024)
- FACT: local-first meeting transcriber (Python, PyTorch); fine-tuned
  Whisper-small on 30 h of noisy lecture audio, cutting word error rate
  from 18.2% to 11.6% on a held-out set

## Skills
- FACT: Python, Rust, TypeScript, SQL, PyTorch, scikit-learn, Linux,
  Docker — self-reported and backed by the entries above
- FACT: RAG pipelines and eval harnesses — the Meridian Labs internship
  built exactly this (see FACT above); "RAG pipelines" and "eval
  harnesses" are the defensible phrasing, not the raw keyword-dump forms
  ("RAG", "Deep Learning", "AI", "LLMs", ...) on the old resume
- FACT: GitHub Actions and Postgres — GitHub Actions runs ledgerlite's
  release pipeline and the simulator's CI; Postgres backs the eval
  harness's ticket-scoring store at Meridian

## Publications
- FACT: Okafor, D., Casey, S., and Lin, M. (2025). "Preemption-Aware
  Scheduling for Shared GPU Clusters." HotCloud Workshop.
  https://example.com/hotcloud25-preemption.pdf — author order per the
  2026-07-14 confirmation in the Q&A log below, not the raw notes'
  listing order (which the notes themselves contradict — see below)

## Awards
- FACT: ACM ICPC Pacific Northwest Regional — 5th place, Nov 2024

## Gaps & flags
- Degree not yet conferred — Jun 2026 is the expected date; confirm
  before any application implies it's already in hand.
- NOT-CLAIMABLE: an industry return offer from Meridian — none is on
  file; do not imply one on any resume.

## Q&A log
- 2026-07-14 Q: What's your expected graduation, month and year? A:
  Started fall quarter Sep 2022; on track to graduate Jun 2026.
- 2026-07-14 Q: Is there a link for the HotCloud paper? A: The workshop
  proceedings link is https://example.com/hotcloud25-preemption.pdf —
  I don't have it mirrored anywhere else.
- 2026-07-14 Q: Your notes cite that paper as "Casey, Okafor, Lin" but
  also say "I'm 2nd author" — those don't agree on who's listed first.
  What's the actual author order? A: The order in my notes isn't the
  author order, I just typed myself first out of habit. Real order is
  Okafor, Casey, Lin — I'm 2nd author, that part is correct. Use "2nd
  author" and the Okafor/Casey/Lin order for the citation, not the
  order in my notes.
- 2026-07-14 Q: Past the keyword-dump list, what would you actually
  defend as skills from the internship and coursework? A: From
  Meridian — RAG pipelines and the eval harness I built. Beyond that,
  GitHub Actions and Postgres — I used Actions for ledgerlite's release
  pipeline and the simulator's CI, and Postgres for the eval harness's
  ticket store.
- 2026-07-14 Q: What's your GitHub profile URL, not just the repo
  links? A: https://github.com/samcasey-demo
- 2026-07-14 Q: What was your official title at Meridian, and at the
  research group? A: Meridian's offer letter says "Machine Learning
  Engineering Intern." The research group just calls it "Undergraduate
  Research Assistant."
- 2026-07-14 Q: What's the research group's real name — the old resume
  just says "UW research lab"? A: Officially the "UW Systems Research
  Group," Prof. Lin's lab.
