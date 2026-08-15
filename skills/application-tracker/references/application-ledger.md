# Application ledger

One markdown row per application preserves the at-send context needed to connect later outcomes to an identifiable target and document.

## Format

```markdown
# Application ledger

## Applications

### <Company> — <Role> (<row-id>)
- posting: <URL or snapshot path>
- target_field: <field | ?>
- target_level: <level | ?>
- channel: <direct | referral | recruiter | board | ?>
- prepared: <YYYY-MM-DD>
- applied: <YYYY-MM-DD | no>
- recommendation: <READY TO SEND | REVISE | DO NOT APPLY | UNREVIEWED | ?>
- craft: <n/10 | ?>
- variant: <stable label | default>
- pdf: <path | ?>
- pdf_sha256: <64 hex | ?>
- yaml: <path | ?>
- yaml_sha256: <64 hex | ?>
- status: prepared | applied <date> -> screen <date> -> interview <date> -> offer <date> | rejected(<stage>) <date> | withdrawn <date> | closed-no-response <date>
- outcome: <latest observed outcome | unknown>
- next: <action and date | none>
- notes: <only decision-relevant context>

## Variants
- <label>: <one stable content or positioning difference>

## Learnings
- <date> — observation: <association>; basis: <which comparable rows and counts>; scope: <where it may apply>; next: <what to test or change>
```

## At-send rule

Compute hashes from the files that were actually submitted, not from paths remembered later; a path is mutable while the digest identifies the bytes.

If the applied file differs from the prepared file, update the row to the sent bytes and record the change; do not overwrite an older applied row when producing a new version.

Snapshots are optional when stable storage exists, but hashes and paths are not substitutes for backups; if copying sent artifacts into a per-application folder, preserve the original files and restrictive permissions.

## Status rules

Prepared is not applied; applied requires explicit user confirmation.

Every transition carries its date; terminal states are rejected, accepted or declined offer, withdrawn, and closed-no-response, and each terminal state sets `next: none`.

Unknown fields use `?`; uncertainty stays visible and does not exclude a real applied row from basic totals.

## Outcome reads

Start with applied count, response count, screen count, interview count, offer count, rejection count, open count, and closed-no-response count; show denominators beside rates.

Before comparing variants or recommendations, check target field, target_level, channel, dates, and employer mix; materially different groups are not evidence about the resume change.

Even comparable rows support an association, not a causal conclusion; use repeated directional evidence to choose the next variant and continue observing.

Do not optimize for response rate alone when later stages deteriorate; the useful outcome is progression toward interviews and offers, and a variant that attracts mismatched screens may be worse.

## Minimal example

```markdown
### Cascadia AI — ML Engineering Intern (cascadia-2026-08)
- posting: jd-cascadia-ml-intern.posting.txt
- target_field: ai-ml
- target_level: intern
- channel: direct
- prepared: 2026-08-13
- applied: 2026-08-14
- recommendation: READY TO SEND
- craft: 9/10
- variant: eval-first
- pdf: applications/cascadia-2026-08/resume.pdf
- pdf_sha256: <64 hex>
- yaml: applications/cascadia-2026-08/resume.yaml
- yaml_sha256: <64 hex>
- status: applied 2026-08-14
- outcome: unknown
- next: close as no-response on 2026-09-04 if no event
- notes: graduation and work-authorization gates met
```
