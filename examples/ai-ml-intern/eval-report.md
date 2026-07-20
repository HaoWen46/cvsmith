# Resume evaluation: examples/ai-ml-intern/resume.pdf

Evaluated 2026-07-21 against jd-analysis.md (Cascadia AI ML intern).

## Verdict
**NOT READY — for this specific posting** — the resume itself is clean
(all deterministic layers pass, evidence is strong), but the posting's
graduation gate ("Dec 2027 or later" vs. Sam's Jun 2026) fails before
any scoring matters. READY for equivalent Summer-2026-eligible roles.

## Deterministic layers
| Layer | Result | Notes |
|---|---|---|
| L0 extraction | PASS | 1,767 chars, clean encoding, extractor token overlap 1.00 |
| L1 parse sim | PASS | all 6 sections route under standard headings; name/email/dates parse |
| L2 integrity | PASS | 291 words checked — every one puts ink on its bbox; no tiny/off-page/zero-width text |
| L3 structure | PASS | 1/1 pages, letter, tagged PDF, fonts embedded, single column |

## L4 — JD alignment: 9/10 on evidence, gated at 0 by eligibility
| # | Requirement | Evidence | Strength |
|---|---|---|---|
| 1 | LLM evaluation | eval harness bullet: 1,200 tickets nightly, 3 regressions caught | **strong** |
| 2 | LLM application work | RAG latency bullet: p95 480→210 ms via cache warmup + HNSW | **strong** |
| 3 | Python + testing | "(Python, pytest)" load-bearing in the harness bullet | **strong** |
| 4 | Measurement mindset | WER 18.2→11.6% on held-out set; baselines reproduced within 2% | **strong** |
| 5 | Graduation Dec 2027+ | Education: Sep 2022 – Jun 2026 | **gate fails** |
| 6 | US work authorization | not stated on resume (normal); user must confirm | unknown |

Nice-to-haves: HNSW (strong), OSS with 1.4k stars + 27 contributors
(strong, linked), workshop publication (strong, linked), Rust
(strong), GPU systems research (strong). Vocabulary already mirrors
the JD's real terms (harness, regressions, red-team, held-out) —
nothing bolted on.

## L5 — recruiter simulation: 9/10
**Six-second skim:** lands "Sam Casey — CS @ UW — ML intern with
eval/RAG numbers". The 480→210 ms and 1,200-ticket figures pop; GitHub
star count anchors the projects section. Visual hierarchy is clean;
nothing competes with the strongest facts.

**Skeptical read:** every major claim carries a number or artifact and
would survive probing ("how did you catch the regressions?" — the
harness bullet already names the mechanism). Flags: (1) "now a
required pre-deploy gate" is a strong claim an interviewer will probe
— Sam should be ready to name who required it; (2) the publications
URL must resolve to the real paper in a real application (synthetic
here).

## Fix list (ranked)
1. **Eligibility**: don't submit to this posting — target the Summer
   2026 cycle of the same teams. No resume change fixes a calendar.
2. Confirm work authorization before applying to US roles (not a
   resume line; a form answer).
3. Keep a one-line answer ready for the "required pre-deploy gate"
   probe (who mandated it, when) — phrasing is fine, just be ready.
