# The application ledger — from tailored resumes to callback evidence

A resume is DONE when the evaluator passes it; an *application* is in
flight once sent and logged. The ledger is the second half of that
seam: it is what turns twenty tailored resumes into callback-rate
evidence instead of twenty PDFs in a folder.

## What it is

One markdown file — `application-ledger.md` — beside the vault in the
user's confirmed workspace. Same privacy class as the vault: the
workspace gate's location rules apply (this skill's SKILL.md; the
same gate as resume-builder's step 2) — created mode 600 before
content lands in it, gitignored, never itself transmitted by these
skills. Projections and PDFs are what get sent; the ledger, like the
vault, never is. (The honest caveat from the SKILL.md applies here
too: content quoted into a hosted conversation reaches that host —
the file staying local is a promise about the file.)

Applied rows also get an `applications/` snapshot directory beside the
ledger (below, Applied transition) — same workspace, same gitignore
treatment, same never-transmitted rule, but not the same mode: a
directory needs its own execute bit for traversal, so `applications/`
and every per-application snapshot subdirectory under it are created
700, not the ledger's 600 — a 600 directory refuses the first file
copied into it. The yaml and PDF copied into those subdirectories are
files, so they stay mode 600. It is not a second place to look; it
exists only so a `snapshot:` path in the ledger always resolves to
something real.

## Format

One block per application:

```markdown
### <Company> — <Role> (prepared YYYY-MM-DD)
- posting: <req ID | posting URL> | ?
- channel: posting | referral (<who>) | recruiter outreach | other
- variant: <strategy tag — must appear in this file's ## Variants legend>
- sent: resume-<company>-<role>.yaml (yaml sha256 <12-hex>) -> <pdf filename> (rendered YYYY-MM-DD, sha256 <12-hex>)
- jd: jd-<company>-<role>.md          (when jd-analyzer ran)
- status: prepared -> applied YYYY-MM-DD -> screen YYYY-MM-DD -> interview(n) YYYY-MM-DD -> offer YYYY-MM-DD | rejected(<stage>) YYYY-MM-DD | no response (21+ days)
- snapshot: applications/<company>-<role>-<applied-date>-<n>/ (sha256 <12-hex>, yaml sha256 <12-hex>) | not yet applied
- next: <action> by <date> | none
```

A row starts as **prepared** the day the resume renders. It becomes
**applied** only when the user confirms they submitted — dated the
actual submission date, never the render date. A rendered PDF is not
an application. Funnel denominators count applied rows only; prepared
rows are pipeline, not applications.

**posting** is the requisition ID or posting URL — what lets a row be
matched back to the actual listing (and, with `variant`, what tells
two applications to the same company+role apart later). Unknown is
written `?`, the same affordance dates use below, never omitted.

**variant** is a reusable strategy label — `ml-heavy`, `generalist`,
`infra-systems`, whatever tags the *content approach* the sent resume
took — not a per-application filename, and not free text either: it
must be one of the labels defined once in this file's `## Variants`
legend (below). It is also never a channel wearing a variant's
clothes: `channel` (above) already carries *how* the application went
in — posting, referral, recruiter outreach, other — so a label that
actually names a channel (`referral-warm` and its like) belongs there,
not here (`## Variants`, below, has the full rule and why mixing the
two corrupts a comparison). The same label recurs across many rows on
purpose: it is the field the funnel groups by to answer "does my
ml-heavy resume get more callbacks than my generalist one," which
company/role alone can never answer — and that answer is only honest
if spelling drift never splits one strategy into two, label reuse
never merges two different ones into one, and a channel effect never
gets mistaken for a content one. At upsert, a variant that doesn't
already match a legend entry (case- and spelling-insensitive) is never
created silently: the skill offers the nearest existing label first,
or adds it to the legend on explicit confirmation that it's genuinely
new (`## Variants`, below, has the full rule).

**sent** carries two digests now, not just a filename: the rendered
PDF's, and — since Finding 5's yaml-substitution gap — the input
yaml's. `render.sh` prints both on every successful render, `sha256:
<12-hex>` for the PDF and `yaml sha256: <12-hex>` for the yaml (see
`resume-builder/scripts/render.sh`); copy both values in when logging
the prepared row. render.sh does not — and must not — block
re-rendering the same derived output path (iterating on a resume
re-renders it on purpose), so the filename alone stops meaning
anything specific once a second render happens; the digests are what
still do.

**Every stage transition carries its date** — stage-to-stage time is
half of what the funnel can teach, and an undated `-> rejected` can
never say how long the screen took. A date the user can't recall is
written `?`, not omitted and not invented. **Terminal outcomes**
(rejected, offer accepted or declined, withdrawn, closed as
no-response) set `next: none` — a dead row with an open action item
corrupts every follow-up read.

**Rows are upserted, never assumed.** An outcome mention with no
existing row (the application predates the ledger, or logging was
declined at the time) creates the row at the reported stage with
unknowns marked: `status: applied ? -> rejected(unknown stage)
2026-07-21`. Ask at most one clause to recover the applied date, then
move on. When two rows match the mention ("Meta got back to me", two
Meta roles on file — or "Stripe rejected me" against two *open* rows
sharing the same company **and** role, e.g. two Stripe Backend
Engineering Intern postings on different reqs), ask which role, or
which posting when role and company are both identical, in one clause
— never guess, never update both, never pick the more-recent row as a
default. **A second application to the same company and
role** (reapplying after rejection, or a distinct req with the same
title) is never a match for that disambiguation — it is always a new
row with its own `posting`, its own `prepared` date, and its own
snapshot on applied — distinct even if both rows apply on the same
calendar date, by the sequence number described in Applied transition
below; the old row is left exactly as it was.

### Applied transition — the snapshot

The moment a row's `status` gains its `applied YYYY-MM-DD`, the skill
— never the user — creates
`applications/<company>-<role>-<applied-date>-<n>/` beside the ledger
(mode 700 — a directory needs its own execute bit for traversal, so
600 here would block the copy below with `Permission denied`;
gitignored, same as the ledger itself), copies the exact yaml and PDF
that were sent into it (mode 600, same as the ledger — these are
files, not directories), and records the directory's path plus both
digests — the PDF's sha256 and the yaml's — in the row's `snapshot:`
field.

Before that copy runs, the skill recomputes **two** digests from what
currently sits at the live paths — the derived PDF's sha256 and the
input yaml's sha256 — and compares each to this row's own `sent:`
field, recorded at prepare time.

- **Both match** — proceed with the copy below, silently.
- **PDF matches, yaml doesn't.** The confirmed bytes are not in
  doubt — only which yaml sourced them is — so this is not yet a
  question, it's a mechanical check first. `render.sh` pins
  `SOURCE_DATE_EPOCH` into the compiled PDF (see `sent:`, above), so
  the already-matching PDF itself carries the exact epoch that
  produced it. Pull that epoch back out, pin it, and re-render the
  *live* yaml with it to a scratch path:
  - **Reproduces the `sent:` PDF digest** — the live yaml renders,
    byte-for-byte, to the bytes that shipped. That is **output
    equivalence, not provenance**: it proves the live yaml is *a*
    faithful source of the sent PDF, not that it is provably the exact
    yaml originally used (two different yamls — a reordered key, a
    changed comment, altered whitespace — can render to identical
    bytes). Output equivalence is all the ledger needs here, though:
    the source it snapshots renders to exactly what the employer got,
    which is the only property the row's audit trail is claiming. So
    record the live yaml's digest against the row with a dated note
    that says precisely that — `[corrected YYYY-MM-DD: live yaml
    reproduces sent PDF byte-for-byte (output-equivalent), digest was
    <12-hex>]` — and snapshot the now-verified yaml alongside the
    already-matching PDF. Do not write "confirmed the original source";
    the re-render cannot show that, only that the two render alike.
  - **Doesn't reproduce it** — the live yaml did not produce the sent
    PDF. *Now* it escalates to a question, same fail-closed rule as a
    PDF mismatch: ask which yaml actually produced the sent file. If
    the user can point to it, verify it the same way (re-render,
    compare) and snapshot that yaml; if it's genuinely lost, the
    snapshot's yaml side is recorded `yaml: unresolved (see sent: PDF
    digest)` rather than silently paired with a live yaml that never
    earned it — the PDF side still snapshots normally, since its
    digest was never in question. A labeled gap is honest; a silent
    wrong pairing is exactly what this guard exists to prevent.
- **PDF doesn't match** (whatever the yaml side shows) — something
  re-rendered at the shared path since prepare (a later application,
  or a legitimate final edit to *this* application — both look
  identical to the guard: `render.sh` overwrote the path in place,
  exactly as it's meant to) — this is a **question for the user, never
  an auto-verdict**. Fail-closed still governs — the only forbidden
  outcome is silently snapshotting bytes the row didn't record — but
  "the row's own `sent:` digest is always the truth" is not itself a
  safe default: sometimes the live file *is* what actually shipped, and
  treating it as corruption would wrongly discard a legitimate last
  edit. So: stop, surface both digests plainly (quote the live one and
  the `sent:` one), and ask which bytes were actually sent.

- **"The current file — I made final edits before sending."** The live
  bytes are what shipped; the prepared-time digest was simply
  overtaken by a legitimate edit. Update the row: rewrite `sent:` to
  the live PDF and yaml digests, and append a dated supersession note
  that keeps the prepared-time digest for audit rather than discarding
  it — `[superseded YYYY-MM-DD: prepared-time sha256 <12-hex>, yaml
  sha256 <12-hex>]`. Then snapshot the live yaml+PDF pair into
  `applications/...` as usual, and proceed. This is not a weakening of
  fail-closed: a dated, explicit user answer *is* the evidence that
  was missing — the row still never silently ends up holding bytes it
  never confirmed.
- **"The earlier one — the live file is a later, unrelated
  re-render."** The recorded `sent:` digest is still what was
  submitted; the recovery path is unchanged from before. An unmodified
  yaml re-renders byte-identical to what shipped (`render.sh` pins
  output bytes to `SOURCE_DATE_EPOCH`, not wall-clock time), so
  re-rendering from this row's `sent:` yaml and re-checking the result
  against `sent:`'s PDF digest recovers the exact PDF that was sent
  without touching whatever now occupies the live path. Only when
  that's not possible (the yaml has since been edited or deleted —
  most commonly, a second application to the same company and role
  reused the shared `resume-<company>-<role>.yaml` filename and
  overwrote this row's tailoring in place) and the user explicitly
  acknowledges the loss does the row instead get `snapshot:
  unrecoverable` — a labeled gap is honest; a silent copy of the wrong
  bytes under this row's name is exactly the corruption this guard
  exists to prevent.

Either branch, the guard's automated check now covers both digests,
not the PDF alone: a PDF match paired with a yaml mismatch resolves
mechanically through the epoch re-render above before ever reaching a
question, and only an unreproducible re-render, or an outright PDF
mismatch, surfaces one for the user to answer. The one case the guard
genuinely cannot resolve: two yamls that happen to render to
byte-identical PDFs are indistinguishable by digest, so a substitution
that's truly invisible at the byte level stays invisible — that's an
inherent limit of content-addressing, not a shortcut this guard is
taking. Everything else a live-yaml substitution could hide — an edit
that changes the yaml's content without a corresponding re-render, or
vice versa — is now caught before it reaches a silent snapshot, not
left for a human to notice by reading the row.

`<n>` is a per-company+role sequence number, not a date suffix: 1 for
the first row ever to reach applied under that company and role, 2
for the next (a reapply after rejection, or a distinct req sharing
the same title), and so on. It is never omitted, even for the first
application — the template always carries it, so no row's path can
degrade into a bare `<company>-<role>-<applied-date>/`. Deriving the
disambiguator from a running count, not from the date, is what keeps
two rows applied on the *same* calendar day (a same-day reapply after
an instant rejection, or two same-titled reqs at one company applied
to in one sitting) from ever landing on the same directory name.
Before writing, the skill checks whether its target
`applications/<...>-<n>/` directory already exists; if it does and
does not belong to this row (a different posting, a different
prepared date, or otherwise not this application), that is proof `<n>`
collided, and the skill increments to the next unused value instead
of writing into — or silently overwriting — another row's snapshot.
This is what the `sent:` filename alone cannot promise: `render.sh`
reuses a deterministic derived output path by design, so the live
file at that path can be re-rendered — for the next application, or a
later edit — after this one already shipped. The snapshot is copied
once, at the moment of applied, and is never touched again; the
ledger row for *this* application always resolves to those exact
bytes no matter what happens later at the live path, and no matter
how many other applications to the same company and role come before
or after it. Before applied, `snapshot:` reads `not yet applied` —
there is nothing to freeze yet.

A real row:

```markdown
### Stripe — Backend Engineering Intern (prepared 2026-07-13)
- posting: REQ-48213
- channel: referral (Maya Chen, infra team)
- variant: infra-systems
- sent: resume-stripe-backend-intern.yaml (yaml sha256 9c1f2e3a4b5c) -> resume-stripe-backend-intern.pdf (rendered 2026-07-13, sha256 a1b2c3d4e5f6)
- jd: jd-stripe-backend-intern.md
- status: prepared -> applied 2026-07-14 -> screen 2026-07-21
- snapshot: applications/stripe-backend-engineering-intern-2026-07-14-1/ (sha256 a1b2c3d4e5f6, yaml sha256 9c1f2e3a4b5c)
- next: confirm phone-screen slot by 2026-07-24
```

Same-day collision, worked: a distinct req at the same company and
role, applied the same calendar date as the row above, gets its own
`<n>` and its own snapshot directory — never the row above's:

```markdown
### Stripe — Backend Engineering Intern (prepared 2026-07-14)
- posting: REQ-51009
- channel: posting
- variant: generalist
- sent: resume-stripe-backend-intern.yaml (yaml sha256 d4e5f6a7b8c9) -> resume-stripe-backend-intern.pdf (rendered 2026-07-14, sha256 7f8e9d0c1b2a)
- jd: jd-stripe-backend-intern-req51009.md
- status: prepared -> applied 2026-07-14
- snapshot: applications/stripe-backend-engineering-intern-2026-07-14-2/ (sha256 7f8e9d0c1b2a, yaml sha256 d4e5f6a7b8c9)
- next: none
```

Both rows share company, role, and applied date; `posting` and `<n>`
are what keep `applications/stripe-backend-engineering-intern-2026-07-14-1/`
and `applications/stripe-backend-engineering-intern-2026-07-14-2/`
textually distinct, so neither row's snapshot can be written into or
mistaken for the other's.

Legitimate final edit, worked: the user tailors one more bullet after
prepare, re-renders (same derived path, new bytes), and confirms they
sent *that* file — the applied-transition digest check catches the
mismatch, asks, and gets "the current file":

```markdown
### Notion — Platform Engineering Intern (prepared 2026-07-10)
- posting: REQ-77120
- channel: posting
- variant: generalist
- sent: resume-notion-platform-intern.yaml (yaml sha256 445566778899) -> resume-notion-platform-intern.pdf (rendered 2026-07-12, sha256 aabbccddeeff) [superseded 2026-07-12: prepared-time sha256 112233445566, yaml sha256 998877665544]
- jd: jd-notion-platform-intern.md
- status: prepared -> applied 2026-07-12
- snapshot: applications/notion-platform-engineering-intern-2026-07-12-1/ (sha256 aabbccddeeff, yaml sha256 445566778899)
- next: none
```

`sent:` now names the bytes that actually shipped (2026-07-12's
render); the prepared-time digests from 2026-07-10 live on in the
`[superseded ...]` note so the audit trail isn't lost, just no longer
the row's authoritative claim.

Yaml-only mismatch, worked: the user reopens the yaml after prepare,
tweaks a comment and re-wraps a long line — edits that change the
file's *bytes* (so its sha256 changes; a digest is content-based, and
an edit that touched only mtime would leave the sha identical and
never trip this branch at all) but not what Typst renders — then
confirms submission. The live PDF digest still matches `sent:`, but the
live yaml's digest doesn't. The epoch re-render against the already-
matching PDF reproduces the PDF byte-for-byte, so the live yaml is
confirmed **output-equivalent** — it renders to the bytes that
shipped — without ever asking the user anything. (That is not a claim
that this is the identical yaml originally used; it is the claim the
ledger actually needs: the snapshotted source renders to what was
sent.)

```markdown
### Anthropic — Research Engineering Intern (prepared 2026-07-15)
- posting: REQ-90210
- channel: posting
- variant: ml-heavy
- sent: resume-anthropic-research-intern.yaml (yaml sha256 220099aabbcc) -> resume-anthropic-research-intern.pdf (rendered 2026-07-15, sha256 66ffeecc1122) [corrected 2026-07-16: yaml digest updated to the live file's 220099aabbcc — it reproduces this PDF byte-for-byte (output-equivalent); prepared-time yaml digest, now superseded, was 771122aabbcc]
- jd: jd-anthropic-research-intern.md
- status: prepared -> applied 2026-07-16
- snapshot: applications/anthropic-research-engineering-intern-2026-07-16-1/ (sha256 66ffeecc1122, yaml sha256 220099aabbcc)
- next: none
```

Read the digests carefully — the audit trail depends on it. The `sent:`
field and the `snapshot:` both hold **220099aabbcc**, the *live*
yaml's digest: the one confirmed to render the shipped PDF, and so the
authoritative record of what was sent. The `[corrected ...]` note holds
**771122aabbcc**, the *prepared-time* digest that the user's later edit
superseded — kept only as history, never snapshotted. The rule is
uniform: the field always carries the current/authoritative value and
the bracket note carries the old one, so `sent:` and `snapshot:` agree
by construction. The PDF digest never moved; only the yaml's did, and
the mechanical re-render — not a question to the user — is what
resolved it. Had the re-render *not* reproduced the PDF, the row would
instead have gone to the same question a PDF mismatch asks: which yaml
actually produced this file.

## Variants — a controlled legend

`variant` only does its job — letting the funnel group "does my
ml-heavy resume beat my generalist one" across every row that used
each strategy — if the same strategy is always spelled the same way,
and a label is never quietly reused for a different strategy later.
Free text fails both silently: `ml-heavy` and `ML Heavy` split one
strategy's rows into two smaller, weaker samples; reusing `generalist`
eight months later for an approach that has nothing to do with the
first `generalist` merges two strategies' outcomes into one number
that means nothing. Neither failure announces itself — the funnel just
quietly reports the wrong thing.

**A variant names CV content, never submission channel.** `channel`
(Format, above) already answers *how* the application went in —
posting, referral, recruiter outreach, other. A legend entry that
actually names a channel (`referral-warm`, `cold-apply`, anything
answering "how did this get in front of them" rather than "what did
the resume lead with") duplicates that field under a different name,
and does it silently: two rows built from the identical resume content
but sent through different channels would end up sorted into different
"strategies" for no content reason, and a channel effect (referrals
simply convert better than cold postings, independent of wording) reads
back as if it were a content effect (that resume's wording must be
better). That failure is exactly as invisible as the spelling-drift and
label-reuse ones above — the funnel just quietly credits the wrong
variable. Every legend entry must name an approach to the *resume
itself* — what it leads with, what it cuts, how it's organized — never
the path it was submitted through.

So the ledger keeps one legend, defined here, in this file, once each
label is first used:

```markdown
## Variants

- ml-heavy — leads with ML/production-systems experience over generalist SWE breadth
- generalist — no domain-specific emphasis, broad SWE coverage
- infra-systems — leads with infrastructure/systems-reliability experience over product-feature work
```

One line per label: the label, an em dash, a short description of the
*content approach* it names (not a per-application detail — company
and role already live in the row's own header — and not the submission
path either — that's `channel`'s job). At upsert, when a mentioned
variant doesn't already match a legend entry case- and
spelling-insensitively, that is a signal, never silent freedom to
invent a new label on the spot: offer the nearest existing entry first
("did you mean `ml-heavy`?"); only when the user confirms this is
genuinely a new *content* strategy does it get its own new legend line,
added in the same update. If what's actually different is the channel
— a referral, a warm intro, a recruiter reaching out first, for a
resume whose content is otherwise the same strategy already in the
legend — that is not a new variant: it is the existing variant plus a
`channel` value on the row, and the legend is left untouched. A label
is never created by the ledger inferring one on its own, and never
merged into an existing one without the user saying it's the same
strategy.

## Capture — pull, never ritual

The skill never demands bookkeeping and never opens a "let's update
your ledger" session. Rows appear at natural moments only:

- **A tailored resume renders for a real application** — offer, in
  one line, to log a prepared row: channel + sent version + variant
  (an existing `## Variants` label, or a one-clause offer to add a new
  one). Respect a no.
- **The user confirms submission** ("sent it", "applied last night")
  — flip prepared to applied with the actual submission date; verify
  *both* the live PDF's and the live yaml's digests against `sent:`
  and snapshot the pair (Applied transition, above) as part of that
  same update — silent when both match. PDF matches but the yaml
  doesn't: resolve mechanically first (epoch re-render against the
  already-matching PDF), and only ask if that re-render fails. PDF
  itself doesn't match: ask which bytes actually shipped rather than
  assuming the row's prepare-time digest is automatically right — "the
  current file" rewrites `sent:` to the live digests with a dated
  supersession note and snapshots the live pair; "the earlier one"
  goes through the existing recovery/`unrecoverable` path — confirm
  the outcome in one clause either way. The snapshot is bookkeeping the
  skill does, never something asked of the user; only the disambiguating
  question is.
- **The user mentions an outcome in any conversation** ("got a screen
  at X", "Y rejected me", "never heard back from Z") — update the row
  silently and confirm in one clause.
- That's all.

## Reading the funnel

Only when the user asks how the search is going (or asks directly):
summarize applied rows by channel and by the row's `variant:` label —
group on that field, never on company/role or the sent filename, so
rates for the same strategy accumulate across every application it
was used on — plus response rate, callback rate, furthest stage
reached, per-variant stage conversion, and median response latency.
Fixed definitions, so every session computes the same funnel: a
**response** is any employer reply tied to the application (a
rejection is a response); a **callback** is a row that EVER reached
screen or beyond — a furthest-stage-ever fact, not a current-status
one, so a row that got a screen and was rejected afterwards stays a
callback (reading a row's current status here would delete exactly the
rows that prove a variant works, and corrupt the learnings the next CV
is chosen from); a rejection arriving before any screen is a response
and not a callback; both rates divide by applied rows;
**no response** means applied with nothing back for 21+ days — younger
silence is *pending*, not a data point. Prepared rows get a one-line
pipeline count, never a rate.

**Stage conversion**, per variant, read off the dated `status:`
transitions: `applied -> screen` = (rows that reached screen or
beyond) / (applied rows for that variant); `screen -> interview` =
(rows that reached interview(n) or beyond) / (rows that reached
screen); `interview -> offer` = (rows that reached offer) / (rows that
reached interview). Each stage's denominator is the count of rows that
*reached the prior stage* — not all applied rows — which is what makes
this a conversion funnel rather than callback rate repeated three
times. A row whose relevant transition date reads `?` still counts
(the stage was reached; only the timing is unknown) — report it in the
count, never drop it silently.

**Median response latency**, per variant: the median, over applied
rows that have a dated first response (screen, interview, offer, or
rejection — whichever transition came first, and it must be dated) of
(first-response-date − applied-date) in days. A row with an undated
`applied ?` or an undated first-response transition is excluded from
the median — report the excluded count alongside the number (e.g.
"median 6 days, n=9, 2 excluded for missing dates"); never impute a
date and never average an unknown in as zero.

**Per-variant comparisons are channel-stratified, not just
variant-grouped.** Variant isolates content; channel isolates
submission path; the two are different axes on purpose (Format,
above), and a "does ml-heavy beat generalist" read that silently pools
one variant's referral rows against another variant's cold-posting
rows is comparing channels while claiming to compare content. Where
sample size allows, report per-variant numbers broken out by channel
("ml-heavy via posting: 2/3 to screen; ml-heavy via referral: 1/1 to
screen") rather than one pooled figure. Where a full per-channel split
would leave cells too small to mean anything, report the pooled
per-variant figure *alongside* that variant's channel mix ("ml-heavy,
n=5 applied: 4 posting / 1 referral") so a reader can see whether one
channel is doing the work before crediting — or blaming — the resume's
content for it. The same stratification (or disclosed mix) applies to
stage conversion and median latency above, not response/callback rate
alone.

**Channel is the only confound the ledger can actually stratify — name
the others, because they are real and uncontrolled.** A variant is
chosen for a job, and jobs differ in more than submission channel:
seniority/level of the target role, field, employer selectivity, how
eligible the candidate was for each, and *when* each was sent (a market
that cooled over the season). The ledger records channel and can split
on it; it does **not** control for the rest. So a raw "ml-heavy beats
generalist" can really be "ml-heavy happened to go to more junior /
less selective / earlier-season roles" — the content may be innocent.
Before a funnel read steers the next draft, say this out loud: state
what each variant was *aimed at* (rough level and selectivity mix, and
the date span), and if a variant's targets skew easier or its rows are
older, discount the comparison accordingly or decline to draw one. The
honest conclusion is often "these variants weren't sent to comparable
jobs, so the difference isn't attributable to the CV" — and a draft
must never be made worse on a difference that the target mix, not the
content, produced. `resume-builder` reads this the same way (its
`## Learnings`/funnel step): a per-variant number without its target
mix is not actionable.

Keep every denominator honest: applied rows only, `?` dates counted
and disclosed as exclusions rather than dropped invisibly, so two runs
against the same ledger always produce the same numbers. The evidence
is the ledger's own numbers — *its* referral vs cold-posting response
rates, and *its* stage conversion and latency by variant, are what
justify shifting effort, so act on the funnel's figures. (BLS
job-search guidance treats resumes, networking, interviewing, and
negotiation as one funnel — a resource list, not comparative outcome
data; don't cite it as proof one channel beats another.) Zero
callbacks across 5+ applied rows on one variant is a signal to inspect
targeting and JD coverage — a prompt for investigation, not proof of
cause.

When a read like that actually lands on a conclusion — not just the
numbers, but a stated takeaway ("ml-heavy is converting better than
generalist at the screen stage," "the referral channel, not the
content, is carrying ml-heavy's callback rate") — persist it in `##
Learnings` (below), dated, with its basis. That happens only when the
user asked for the read in the first place; it is never a scheduled
recap, and it is what lets the next tailoring session start from what
this one already learned instead of from zero.

## Learnings

Funnel reads (above) compute numbers on request and then, by default,
those numbers evaporate — nothing about "ml-heavy is outperforming
generalist" survives past the conversation it was said in, so the next
resume gets tailored exactly as blind as the first one. This section
is the fix: it is what `resume-builder` reads (alongside the vault and
the new JD) before tailoring, so an application's outcome actually
feeds back into the next attempt instead of just sitting in the ledger
as a number nobody consulted again.

**Pull-based, exactly like every other write in this file**: an entry
is added only when the user asks for a funnel read and a real
conclusion follows from the numbers — never a scheduled recap, never
manufactured just to have something to write. When one does land,
append a dated entry:

```markdown
## Learnings

- 2026-07-23: ml-heavy reaches screen at roughly 2x generalist's rate
  (4/9 vs 2/9); basis: 9 applied ml-heavy rows (7 posting, 2 referral),
  9 applied generalist rows (all posting) — both past the 5-applied-
  row-per-variant floor below which no conclusion is drawn, and the
  funnel read behind this was channel-stratified first, since ml-heavy
  carries the only referrals; the 2x holds within posting-only too
  (3/7 vs 2/9), so it isn't just the referral effect.
```

One line per entry: the date, the conclusion in the same terms the
user heard it, and a `basis:` clause naming exactly how many applied
rows per variant it rests on and their channel mix. Two caveats are
load-bearing and must be in the `basis:`, never dropped:

- **The sample floor.** `resume-builder` draws nothing from a variant
  with fewer than 5 applied rows (`resume-builder/SKILL.md`), so a
  Learnings entry must not either — an entry whose `basis:` shows a
  variant under 5 rows is recording an observation, not a conclusion,
  and must say so in those words ("too few rows to act on yet") rather
  than stating a multiple like "2x" that the builder is told to ignore.
  The worked entry above clears the floor deliberately (9 rows each);
  a 2/3-vs-1/3 read is a note that the sample is still too small, not a
  "2x" finding.
- **The channel mix**, the identical channel-stratification the funnel
  read itself had to report above, so a conclusion can never be quoted
  back later stripped of the caveat that made it honest. Entries are **appended, never rewritten**: when a
later read revises or narrows an earlier conclusion (more rows came
in, the picture changed), that gets its own new dated entry — the old
one stays, visibly stale-dated, because what was believed when is
itself part of the evidence. Nothing here is a standing instruction
the tracker acts on by itself; it is a dated note left for whoever
tailors the next resume to read first.

## Handoffs — honest ones

- **Screen or interview reached** — interview prep is out of this
  skill's scope; say so. The vault's FACT lines and Q&A log are the
  story bank: offer a one-page brief projected from the vault for the
  specific interview.
- **Offer or negotiation** — out of scope; say so plainly.
