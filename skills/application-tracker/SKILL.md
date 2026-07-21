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
going — and never leaves the machine. Before the first write, confirm
where it lives (beside `career-vault.md` when resume-builder is in
use). Inside a git repository? Check the path is ignored
(`git check-ignore`) and offer to add ignores *before* writing.
Inside a cloud-synced folder (iCloud/Drive/Dropbox)? Say so —
gitignore does not stop a sync client from uploading it. After the
first write, `chmod 600` on POSIX systems.

## 2. Capture — pull, never ritual

Rows appear when the user says something, never on a schedule:

- A resume ships for a real application — offer, in one line, to log
  a **prepared** row (channel + sent version). Respect a no.
- The user says they submitted — flip the row to **applied**, dated
  the actual submission date; confirm in one clause.
- The user mentions an outcome ("got a screen at X", "Y rejected me",
  "never heard back from Z") — update the row silently and confirm
  in one clause.

Never open a "let's update your ledger" session; never demand
bookkeeping.

## 3. Prepared vs applied — honest denominators

A rendered resume is a **prepared** row; it turns **applied** only on
the user's confirmed submission, dated the day they submitted, not
the day it rendered. Callback rate is callbacks over applied rows;
prepared rows are pipeline, not applications. Logging renders as
applications corrupts every rate the ledger exists to measure.

## 4. Funnel reads — on request only

When the user asks how the search is going: applied rows by channel
and resume variant, response rate, furthest stage reached. Diagnose
from the ledger's own numbers — its referral vs cold-posting response
rates are the evidence, not external guidance. Zero callbacks across
5+ applied rows on one variant: inspect targeting and JD coverage —
a prompt for investigation, not proof of cause.

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
