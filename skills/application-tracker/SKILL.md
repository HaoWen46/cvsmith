---
name: application-tracker
description: 'Track job applications and their outcomes in an application ledger. Use whenever the user reports anything that happened to an application — got a screen or interview, an offer, a rejection, no response / ghosted — or says they applied or submitted a resume somewhere, wants to log, update, or review applications, asks which resume version went to which company, plans follow-ups, or asks how their job search is going. Rows live in application-ledger.md beside the career vault, same privacy rules; rows start as prepared and turn applied only on confirmed submission so callback rates stay honest. Also use when an interview or offer arrives to log the stage — interview prep and negotiation themselves are out of scope; the skill says so and offers a vault-based brief instead.'
---

# application-tracker

Turn sent resumes into callback-rate evidence. One markdown ledger,
one row per application, updated at the moments things actually
happen — never a bookkeeping session. Row format and the full
doctrine: `references/application-ledger.md` — read it before the
first write.

## 1. Workspace — same gate as the vault

The ledger is personal data — where someone is applying and how it's
going. Nothing in this skill transmits it anywhere: the file stays in
the user's confirmed workspace, and only projections ever ship. Be
honest about the boundary of that promise, though — ledger content
quoted into the conversation is processed by whatever host runs the
agent, and a cloud-hosted session sends it to that provider like any
other message. Keep quoting minimal in remote-hosted sessions.
Before the first write, confirm where it lives (beside
`career-vault.md` when resume-builder is in use). Inside a git
repository? Check the path is ignored (`git check-ignore`) and offer
to add ignores *before* writing. Inside a cloud-synced folder
(iCloud/Drive/Dropbox)? Say so — gitignore does not stop a sync
client from uploading it. On POSIX systems create the file with 600
permissions *before* content lands in it
(`install -m 600 /dev/null application-ledger.md`), never write
first and chmod after. The `applications/` snapshot directory
(section 2, applied transition) is created beside the ledger under
the identical rule — same confirmed workspace, same gitignore check,
before any snapshot lands in it — but not the identical mode: a
directory needs its own execute bit for traversal, so `applications/`
and every per-application snapshot subdirectory under it are created
700, not 600 (`mkdir -m 700`); a 600 directory blocks the first file
copied into it with `Permission denied`. The yaml and PDF copied into
those subdirectories are files, so they stay 600, same as the ledger.

## 2. Capture — pull, never ritual

Rows appear when the user says something, never on a schedule:

- A resume ships for a real application — offer, in one line, to log
  a **prepared** row (channel + sent version + variant label — an
  existing label from the ledger's `## Variants` legend, never
  invented free text; `references/application-ledger.md`).
  Respect a no.
- The user says they submitted — flip the row to **applied**, dated
  the actual submission date; before snapshotting, recompute *both* the
  live PDF's digest and the live yaml's digest and compare each to this
  row's `sent:` PDF and yaml digests. Both matching proceeds silently.
  PDF matches but the yaml doesn't — not yet a question: try a
  mechanical fix first. The already-matching PDF carries the exact
  epoch that produced it (`render.sh` pins `SOURCE_DATE_EPOCH` into the
  output), so pull that epoch back out and re-render the *live* yaml
  with it pinned, to a scratch path. Reproduces the `sent:` PDF digest
  — the live yaml renders byte-for-byte to what shipped: **output-
  equivalent, not proven the original source** (a different yaml can
  render to the same bytes; the re-render can't distinguish them, and
  doesn't need to — rendering to exactly the sent bytes is the only
  property the row claims). Record its digest with a dated note saying
  that, and snapshot it alongside the already-matching PDF. Doesn't reproduce it — *now* it's
  a **question, not an auto-verdict**: ask which yaml actually produced
  the sent file, same fail-closed rules as a PDF mismatch (below); if
  the user can't say, the snapshot's yaml side is marked unresolved
  rather than silently paired with a live yaml that never earned it —
  the PDF side still snapshots, since its digest was never in doubt.
  A PDF mismatch (yaml aside) is the same **question, not an
  auto-verdict** it always was — surface both digests and ask which
  bytes actually shipped: "the current file" (a legitimate final edit)
  rewrites `sent:` to the live digests with a dated supersession note
  and snapshots the live pair; "the earlier one" goes through the
  existing recovery path (Applied transition,
  `references/application-ledger.md`) and only reaches `snapshot:
  unrecoverable` on the user's explicit say-so. Either way the row
  never silently ends up holding bytes — or a yaml — it didn't confirm;
  `sent:` and `snapshot:` carry pdf+yaml digests, not pdf alone, and
  now both are actually checked, not just disclosed as a gap;
  snapshotting itself is bookkeeping the skill does, never the user —
  confirm the outcome in one clause.
- The user mentions an outcome ("got a screen at X", "Y rejected me",
  "never heard back from Z") — update the row and confirm in one
  clause.

Two situations the update rules must not assume away:

- **No row exists** for the application the user just mentioned
  (they applied before this skill existed, or declined logging at
  the time) — create the row *now*, at the stage they reported.
  Fill what the mention carries, mark what it doesn't as unknown
  (`applied ? -> rejected(unknown stage) 2026-07-21`), and ask at
  most one clause to recover the applied date. A rejection with an
  unknown applied date still counts in the funnel's numerators and
  denominators; a lost row counts nowhere, which is worse.
- **More than one row matches** ("Meta got back to me" against two
  Meta roles, or "Stripe rejected me" against two open rows sharing
  the same company *and* role on different postings) — ask which
  role, or which posting when company and role are both identical, in
  one clause; never guess, never update both. If the user doesn't
  know, note the ambiguity on both rows rather than picking one.
- **A second application to the same company and role** (reapplying
  after rejection, or a distinct req with the same title) is never a
  match for the situation above — it always gets its own new row,
  its own `posting` reference, and its own snapshot on applied. The
  old row is left untouched; nothing is overwritten in place.

Every stage transition gets its date (`applied 2026-07-14 -> screen
2026-07-20 -> rejected(screen) 2026-07-21`). Terminal outcomes
(rejected, offer accepted/declined, withdrawn, closed no-response)
set `next: none` — an open `next:` on a dead row poisons follow-up
reads.

Never open a "let's update your ledger" session; never demand
bookkeeping.

## 3. Prepared vs applied — honest denominators

A rendered resume is a **prepared** row; it turns **applied** only on
the user's confirmed submission, dated the day they submitted, not
the day it rendered. Callback rate is callbacks over applied rows;
prepared rows are pipeline, not applications. Logging renders as
applications corrupts every rate the ledger exists to measure.

The same honesty applies to *which bytes* a rate is attributed to:
`render.sh`'s derived output path is deterministic and reused on
purpose while iterating, so the live PDF a `sent:` line names can be
re-rendered again after this application already shipped. The applied
transition's snapshot (above) is what keeps a rate attributable to
the resume that actually went out, not to whatever happens to be at
that path later — and that snapshot now carries a yaml digest
alongside the PDF's (render.sh prints both). Both digests are guarded,
not just the PDF's: a yaml mismatch behind a matching PDF resolves
mechanically (re-render the live yaml at the epoch that produced the
matching PDF, check the result) before it ever reaches the user, and
only an unreproducible re-render — or an outright PDF mismatch —
surfaces a question (`references/application-ledger.md`, Applied
transition). The one gap left is inherent, not a shortcut: two yamls
that happen to render to byte-identical PDFs are indistinguishable by
digest alone, so that coincidence can't be out-argued — every other way
a live-yaml substitution could hide now gets caught before a silent
snapshot.

## 4. Funnel reads — on request only

When the user asks how the search is going: applied rows by channel
and by the row's `variant` label (a reusable strategy tag drawn from
the ledger's `## Variants` legend, not free text and not the
per-application sent filename — `references/application-ledger.md`),
response rate, callback rate, furthest stage reached, per-variant
stage conversion, and median response latency. The definitions are
fixed so two sessions never compute two different funnels:

- **response** = any employer reply tied to the application,
  rejection included; **response rate** = responses / applied rows.
- **callback** = the row ever reached screen or beyond; **callback
  rate** = callbacks / applied rows. Callback is a *furthest-stage-
  ever* fact, not a current-status fact: a row that reached screen and
  was then rejected stays a callback forever. A rejection is a
  response, and it is a callback if and only if the row had already
  reached screen or beyond when it arrived — a straight rejection off
  the application is a response and not a callback. Never read a row's
  current status to decide this; read its furthest stage.
- **no response** = applied, nothing back, and 21+ days elapsed
  (before that it's just *pending*). Prepared rows sit in no
  denominator, ever.
- **stage conversion** (per variant) = applied->screen, screen->
  interview, interview->offer, each dividing by rows that reached the
  *prior* stage, not by all applied rows — full formulas in
  `references/application-ledger.md`.
- **median response latency** (per variant) = median days from
  applied-date to the dated first response, over applied rows with
  both dates known; rows missing either date are excluded and the
  exclusion count is reported, never silently dropped or imputed.

Diagnose from the ledger's own numbers — its referral vs cold-posting
response rates are the evidence, not external guidance. Zero
callbacks across 5+ applied rows on one variant: inspect targeting
and JD coverage — a prompt for investigation, not proof of cause.

`variant` names CV-content strategy only — never the submission
channel, which already has its own field — so a per-variant comparison
that pools rows across channels can quietly credit (or blame) the
resume for what the channel actually did. Report per-variant numbers
channel-stratified, or state the channel mix alongside them, so a
referral effect can't masquerade as a content effect — full rule and
formulas in `references/application-ledger.md` (`## Variants`,
`Reading the funnel`).

When a real conclusion follows from those numbers — not the numbers
alone — persist it as a dated entry in the ledger's `## Learnings`
section (`references/application-ledger.md`): date, conclusion,
`basis:` naming the applied-row count per variant and channel mix
behind it. Only when the user actually asked for the read, never a
scheduled recap; entries are appended, never rewritten.
`resume-builder` reads `## Learnings` before tailoring the next
resume — a funnel that gets computed but never remembered helps no
future application.

**Follow-up plans** read straight off the `next:` fields: when the
user asks what to chase, list open rows whose `next:` date is due or
overdue, oldest first — never invent follow-ups for rows that have
none.

## 5. Handoffs — honest ones

Screen, interview, offer: log the stage. Interview prep and
negotiation are out of scope — say so plainly, then offer a one-page
interview brief projected from the career vault (facts + Q&A stories
for the specific company) when resume-builder's `career-vault.md`
exists.

## 6. Standalone degradation

Works without resume-builder or a vault: the ledger is plain markdown
in any confirmed private location, and the workspace gate above still
applies. No vault means no projected interview brief — say so rather
than improvising one. Ships beside the other cvsmith skills in the
releases.
