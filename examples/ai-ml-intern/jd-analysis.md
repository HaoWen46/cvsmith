# JD analysis: Machine Learning Engineering Intern @ Cascadia AI
Source: evals/fixtures/jd-sample/ml-intern-posting.md (synthetic), seen 2026-07-21
Market: Seattle, WA (hybrid) → US
Decoded level: true intern-level — "own a project end-to-end" with senior
engineers, code review, and eval gates around it; scope words match the title.
Register signal: LLM-product startup, energetic-concrete tone ("catch
regressions before customers do") — one sample of the US-tech register cell.

## Gates (binary — confirm before tailoring)
- **Graduating Dec 2027 or later** ("pursuing a BS/MS… graduating Dec 2027
  or later") — enrollment status; cannot be tailored.
- **US work authorization, no sponsorship** — not a resume line in US
  convention; the application form asks. Confirm before investing effort.

## Must-haves (ranked)
| # | Requirement | JD's words | Evidence target |
|---|---|---|---|
| 1 | Building/using LLM evaluation | "evaluation harnesses", "define metrics, curate datasets, catch regressions" | a bullet naming a harness the candidate built/ran with dataset size and regressions caught — not "evals" in a skills list |
| 2 | Hands-on LLM application work (RAG/agents/fine-tuning) | "retrieval/RAG, agents, fine-tuning, or evaluation" | a shipped/researched LLM pipeline bullet with a measured quality or latency outcome |
| 3 | Strong Python + testing | "Strong Python; comfort with testing frameworks (pytest or similar)" | Python + pytest doing load-bearing work inside a real bullet |
| 4 | Measurement mindset | "baselines, held-out sets, and regression tests" | any before→after metric on a held-out/baseline framing |

## Nice-to-haves
| Requirement | Evidence target |
|---|---|
| Model evaluations at scale | same as must-have #1, larger numbers help |
| Vector DBs / ANN indexes | an index named where it changed a metric (FAISS/HNSW + latency/recall) |
| Systems: profiling, latency, GPU | a profiling/optimization bullet with the mechanism named |
| OSS or publication "we can read" | a URL: repo with real users/contributors, or a paper with venue |
| Rust or Go | either language load-bearing in any project bullet |

## Vocabulary map
| JD term | Common synonyms candidates write instead |
|---|---|
| evaluation harness | test suite, QA pipeline, benchmark script |
| retrieval / RAG stack | search pipeline, semantic search, embeddings app |
| red-team / prompt injection | security testing, adversarial testing |
| regression | bug, quality drop |
| held-out set | test set, validation data |

## Culture noise (no resume action)
- "self-starter", "fast-paced environment", "passionate about the
  transformative potential of AI", "wearing many hats", "mission-driven"

## Red flags / notes
- **The graduation gate is decisive**: "graduating Dec 2027 or later"
  excludes anyone finishing earlier — check the candidate's date before
  any tailoring effort is spent.
- Compensation and duration stated plainly; team specifics present
  (40+ enterprise customers, named responsibilities) — reads like a
  real role, not a ghost posting.
