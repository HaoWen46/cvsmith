# stuff for resume (sam's notes, very rough)

## meridian internship details (jun-sep 2025)
- the eval harness thing: python + pytest, ran every night against 1200
  old support tickets, it caught 3 retrieval regressions before they
  shipped to prod. manager said this was the main win of my internship
- latency: p95 was 480ms, got it to 210ms. did two things: warmed the
  embedding cache on deploy + switched the vector index from flat
  search to HNSW
- red team suite: 41 prompt injection cases, they made it a required
  pre-deploy gate for both production assistants after i left

## research group (oct 2024 - may 2025, prof. lin's systems group)
- trace-driven simulator for GPU cluster schedulers, python
- reproduced 3 baselines from published papers, all within 2%
- found a starvation edge case, it's in their benchmark suite now
- workshop paper at HotCloud 2025, i'm 2nd author (Casey, Okafor, Lin,
  "Preemption-Aware Scheduling for Shared GPU Clusters"). presented the
  poster myself

## ledgerlite (ongoing since 2023)
- rust + sqlite, append-only ledger with double-entry validation
- 1.4k stars, 27 outside contributors, signed releases mac+linux
- github.com/samcasey-demo/ledgerlite

## whisperboard (jan-apr 2024)
- local-first meeting transcriber
- fine-tuned whisper-small on ~30h of noisy lecture recordings
- WER went from 18.2% to 11.6% on my held-out set

## misc
- ICPC pacific northwest regional, 5th place team, nov 2024
- dean's list 6 quarters
- coursework that matters: ML, distributed systems, NLP, databases
- portfolio site: samcasey.example.com
