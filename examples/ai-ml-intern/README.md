# Worked example: AI/ML intern, end to end

The full cvsmith flow on a synthetic candidate ("Sam Casey" — every
person, employer, metric, and URL is invented). Each artifact here is a
real output of following the skills, not a mockup.

## The flow

```
messy materials ──▶ resume-builder ──▶ career-vault.md ──▶ resume.yaml ──▶ render.sh ──▶ resume.pdf
   + follow-up Q&A                           │                  │                            │
                                    check_projection.py ◀────────┘                            │
                                              │                                                │
                                    projection-report.md                                       │
      +                                                                                        │
  job posting ──▶ jd-analyzer ──▶ jd-analysis.md ──────────────────────▶ resume-evaluator ◀────┘
                                                                              │
                                                                        eval-report.md
```

1. **Raw materials** — what users actually have:
   [`old_resume.txt`](../../evals/fixtures/materials-sample/old_resume.txt)
   (objective-statement fluff, "responsible for" bullets, a 26-item
   keyword-dump skills list) and
   [`project_notes.md`](../../evals/fixtures/materials-sample/project_notes.md)
   (the real numbers, buried in rough notes). Not every fact in the
   resume traces to these two files alone — the exact graduation
   month, the HotCloud paper's URL, the confirmed HotCloud author
   order (the notes list "Casey, Okafor, Lin" but also claim "2nd
   author" — a contradiction resolved by asking, not by guessing),
   and two of the tailored skill entries (`eval harnesses`, `GitHub
   Actions`/`Postgres`) came from follow-up questions, not the raw
   dump. Real intake asks those questions; this worked example makes
   that step visible instead of skipping it:
   [`career-vault.md`](career-vault.md) is the persistent record (per
   `references/career-vault.md`'s format) with a `## Q&A log` naming
   exactly what was elicited and when.
2. **Builder output** — the extracted, evidence-first data file:
   [`resume.yaml`](../../evals/fixtures/resume-sample/resume.yaml)
   (doubles as the CI fixture). Compare bullet-for-bullet with the old
   resume: same facts, from "Helped improve the speed of the retrieval
   system" to "Cut p95 retrieval latency from 480 ms to 210 ms by …".
   The keyword dump became three defensible skill groups.
   [`projection-report.md`](projection-report.md) is
   `check_projection.py`'s actual output against the vault above —
   every hard fact (18 numbers, 9 dates, 4 urls, 10 identity fields,
   6 contact/personal fields, 20 skill tokens, 2 directional metric
   pairs) verified, not merely asserted, plus one
   number-coincidence the script correctly can't resolve on its own
   (the HotCloud "2nd author" claim vs. an unrelated nearby number) and
   hands to a human instead of guessing — resolved honestly in the
   report via the vault's own Q&A-log confirmation.
3. **Rendered PDF** — [`resume.pdf`](resume.pdf): one page, tagged
   PDF/UA-1 + PDF/A-2a, single column, vendored fonts, rendered with
   the designed `compact` template (accent name, tag rows, dense).
   Rebuild it with
   `skills/resume-builder/scripts/render.sh evals/fixtures/resume-sample/resume.yaml -t compact`
   (or drop `-t compact` for the roomier `onecol` look).
4. **Target posting** —
   [`ml-intern-posting.md`](../../evals/fixtures/jd-sample/ml-intern-posting.md):
   a realistic posting with buzzwords, a wish-list, culture noise, and
   one buried hard gate.
5. **JD analysis** — [`jd-analysis.md`](jd-analysis.md): must-haves
   ranked by signal, evidence targets that describe proof (not
   keywords), culture noise quarantined — and the graduation gate
   surfaced before any tailoring effort is spent.
6. **Evaluation** — [`eval-report.md`](eval-report.md): all four
   deterministic layers pass; L4 scores the evidence 9/10 and then
   reports both eligibility gates honestly (graduation: not met; work
   authorization: unconfirmed); L5 simulates the skim and the skeptic.
   Verdict: **MECHANICAL: READY, TARGET FIT: NOT READY for this
   posting** (calendar and an open form question, not the resume) —
   which is the point: the toolkit tells the truth rather than
   optimizing a doomed application.

## Why this example includes a failed gate

Because that's what honest tooling looks like in practice. The most
valuable output of the analyzer isn't vocabulary polish — it's
"check this one line before you spend an evening tailoring."
