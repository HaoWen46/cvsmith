---
name: application-tracker
description: Track job applications, the exact resume context sent, and later outcomes in a private markdown ledger. Use when a user prepares or submits an application, reports a screen, interview, rejection, offer, withdrawal, or no response, asks which resume went where, wants follow-ups, or asks what the search is showing. Prepared and applied remain distinct; comparisons are associations for the next tailoring decision, not causal claims.
---

# application-tracker

Preserve which target, recommendation, and resume bytes produced each real application outcome so later tailoring can learn from evidence instead of memory.

Read `references/application-ledger.md` before the first write.

## 1. Protect the ledger

Keep `application-ledger.md` beside the candidate evidence workspace in the user's confirmed private workspace; inside a git repository verify the path is ignored before writing, warn if the directory is cloud-synced, and use restrictive permissions where available.

State once that a cloud-hosted agent processes content it reads even when the file itself is never deliberately uploaded.

## 2. Capture events when they happen

Create a `prepared` row when a finished application-specific resume is handed off and the user accepts logging; copy target and evaluator context from the actual files rather than asking the user to retype it.

Turn `prepared` into `applied` only when the user confirms submission; use the actual submission date and capture at-send context before the live files can be overwritten.

At send, store company, role, posting reference, target field and target_level, channel, evaluator recommendation, CRAFT diagnostic when present, PDF path and pdf_sha256, YAML path and yaml_sha256 when present, variant label, and status history.

Do not copy a full posting or JD analysis into the ledger; after the at-send target identity and artifact context are captured, stale JD snapshots and analyses remain disposable rather than becoming an archive.

If live file hashes differ from the prepared row at submission, ask which version was actually sent; never silently attribute an outcome to bytes that may not have left the machine.

When the user reports an outcome, update the matching row with the dated transition and outcome; if multiple rows match, ask which one, and if none exists, create a partial historical row rather than discarding the event.

Terminal outcomes set follow-up to none; each repeated application gets a new row even when company and title match.

## 3. Keep denominators honest

Prepared rows are pipeline, not applications; response rates use applied rows only, and unknown outcomes remain unknown rather than being counted as rejection until the selected no-response window passes.

Do not infer submission merely because a PDF exists, and do not infer a callback stage from vague recruiter contact.

## 4. Read outcomes without pretending causality

When asked how the search is going, report simple counts and rates by stage, then compare only rows reasonably similar in target field, target_level, channel, timing, and employer selectivity.

Call differences associations, not causal proof; resume wording, candidate fit, employer mix, timing, referrals, and chance remain entangled.

Use a pattern to change future tailoring only when its rows are identifiable, at-send context is present, and the same direction appears across comparable applications; otherwise report the observation and keep testing.

Write useful conclusions under `## Learnings` with date, basis, scope, and next action; `resume-builder` may use them to choose emphasis or a variant, never to invent candidate evidence.

## 5. Follow-ups and handoffs

When asked what to chase, list open rows whose explicit follow-up date is due or overdue, oldest first; do not invent a follow-up schedule where none was recorded.

Log screens, interviews, offers, rejections, withdrawals, and no-response closure; interview preparation and negotiation are separate tasks, though a role-specific brief may be built from candidate evidence.

## Standalone use

The ledger works without the other skills, but unavailable target, recommendation, or hash fields remain `?`; missing context must not be backfilled from guesses.
