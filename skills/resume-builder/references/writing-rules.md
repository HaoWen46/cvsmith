# Writing rules

Write for interview conversion under ordinary hiring scrutiny: strong enough to win attention, normal enough not to trigger suspicion, and defensible enough not to collapse later.

## Claim boundary

Treat claims by practical exposure, not by whether they can be philosophically certified.

### Record-risk claims

Identity and contact details, employers, titles, dates, degrees, GPA, credentials, publications and authorship, awards, work authorization, public URLs, and public artifact contents are commonly checked against records or third parties; keep them consistent with the source record.

Do not fabricate an employer, credential, degree, title, date, authorization status, publication, award, or public artifact; the expected upside is small and the background or reference check risk is direct.

Numbers need a basis the candidate can explain and that does not conflict with available records; use a defensible estimate, range, or narrower statement when exact precision would be brittle.

### Framing claims

Scope, emphasis, contribution verbs, causal wording, and the interpretation of team results can be assertive when the candidate can explain the mechanism and their part naturally under interview probing.

Prefer the strongest interview-defensible reading of the evidence; public proof is not required, and favorable framing is not a defect merely because an outsider cannot verify it.

Pull back when a normal interviewer, manager, or teammate would likely hear a materially different story, or when the wording implies sole ownership, authority, or causality the candidate cannot explain without retreating.

### Social acceptability

The page should look like a strong ordinary resume: no hidden text, keyword stuffing, fake links, fake credentials, decorative skill ratings, improbable title inflation, or language that sounds generated or manipulative.

When uncertain, choose the strongest version that survives two minutes of direct questioning without contradiction or embarrassment.

## Evidence allocation before prose

Allocate in four passes before prose: list three to five target beliefs, extract causal atoms, map every atom to one belief so competing atoms fight for its slot, then route every atom that loses.

Treat candidate action -> load-bearing mechanism -> result or artifact as one indivisible atom and one possible bullet; split only for another independent action or result serving a different belief, never to make the line shorter or increase bullet count.

For the sample evidence, nightly evaluation + metrics + caught regressions is one atom, HNSW/cache + latency + retained recall is a second, and prompt-injection suite + deploy gate is a third; a mechanism-only line such as `Replaced flat search with HNSW` is an incomplete atom.

A valid row is `target belief | source atom | core result or artifact | load-bearing mechanism | optional scale or quality signal | overflow`; topic labels, percentages, and proposed bullet counts do not decide payload and therefore are not allocations.

Example row: `evaluation reliability | nightly RAG eval -> 1,200 tickets -> 3 regressions caught | core: 3 regressions caught | mechanism: nightly RAG eval | signal: 1,200 tickets | overflow: reusable metric context to candidate evidence`.

Route a distinct high-value atom to another bullet only when it earns an uncovered requirement, useful interview support to candidate evidence, and duplicate context, incidental tools, or secondary metrics to deletion.

Phrase selected rows one-for-one; for the example row: `Built nightly RAG evals over 1,200 tickets, catching 3 regressions before release.`

## Bullet construction

Use the smallest complete shape: strong verb + technical or operational mechanism + result, with problem context only when needed to understand the result.

Lead with what matters to the target role; name tools only when they did load-bearing work; attach scale, quality, speed, reliability, revenue, cost, adoption, or an artifact when one materially strengthens the line.

Avoid duty descriptions and adjective-only impact; “built X with Y, cutting Z” is useful, while “responsible for robust solutions” says almost nothing.

Keep one target belief per bullet and exactly one physical line in the rendered PDF; combine its action, load-bearing mechanism, and result, but split unrelated atoms rather than chaining clauses.

Treat a wrap as an allocation failure, not a word-count exercise: remove the weakest optional signal first, tighten the mechanism or result second, and create another bullet only when the overflow is a distinct high-value atom for an uncovered requirement.

Use present tense for ongoing work and past tense for completed work; omit first-person pronouns and terminal punctuation only if the selected template consistently does so.

## Quantification

Quantify when the number changes the reader's understanding of scale or effect, not to decorate every line.

Useful numbers include before/after values, measured quality, throughput, latency, users, records, dollars, time saved, reliability, or a clear rank; weak numbers include counts that merely restate activity.

If the source gives an outcome without a clean number, name the observable result or artifact rather than inventing precision.

## Anti-slop list

Do not emit these by default: spearheaded, leveraged, utilized, synergy, dynamic, passionate, results-driven, detail-oriented, seasoned, cutting-edge, delve, successfully, effectively, seamlessly, efficiently, proven track record, extensive experience, responsible for, tasked with, duties included, the development and implementation of, or the “not just” construction.

Use `robust` only for a concrete property such as a robust test suite, not as generic praise for a solution, system, or architecture.

Prefer plain verbs: built, wrote, shipped, cut, designed, measured, migrated, scaled, automated, diagnosed, or published.

## Selection and hierarchy

The top third must establish the target identity and strongest evidence; order sections and entries by relevance and strength, then chronology within comparable entries.

Cut duplicated, weak, or off-target material before compressing the layout; one memorable result is worth more than several interchangeable bullets.

Skills shown nowhere else are weak signals; retain them when they are genuine screening terms, but prioritize tools evidenced in bullets, visible stacks, coursework, or publications.

Projects need a usable name, artifact when available, mechanism, and result; coursework belongs only when it is meaningful evidence for the target and the work history cannot carry that signal.

## Final read

Ask four questions of every line: what does it make the reader believe, why does that belief help this target, can the candidate defend it naturally, and is a likely record or reference able to contradict it?

Delete or redesign any line that fails the first two; narrow any line that fails the last two.
