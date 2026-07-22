# The career vault — persistent memory, per-application projection

A resume is a *projection* of a person's full evidence base onto one
target. The vault is that evidence base, kept as a file the user owns.
It is what makes this skill persistently useful instead of one-shot:
intake happens once and accretes; every new application is a cheap
selection, not a re-interview.

## What it is

One markdown file — `career-vault.md` — in the user's confirmed
workspace (same privacy rules as everything else: personal data, never
in a tracked repo; run the gitignore check before first write).

Structure mirrors the resume schema but is exhaustive where a resume
is selective:

```markdown
# Career vault — <name>
Updated: <date>

## Basics
name / email / phone / location / links  (canonical versions)

## Education
<all of it, including details usually cut: full coursework, thesis,
 GPA history>

## Experience  (every stint, ever — nothing is too small to record)
### <org> — <title> (<start>–<end>) [group: research|teaching|industry]
- FACT: <every claim, with its numbers, at maximum specificity>
- FACT: ...
- CONTEXT: <team size, stack, who to name as reference, probe answers>
- CUT: <material dropped from some resume + why — so it isn't re-litigated>

## Projects
<same shape; include dead projects — they sometimes fit odd postings>

## Publications / Awards / Certifications
<verbatim citations, dates, URLs>

## Gaps & flags  (honesty ledger)
- <known weak spots, employment gaps + true reasons, expiring visas,
  graduation dates — things tailoring must respect, not paper over>

## Q&A log
- <date> Q: <question the builder asked> A: <user's answer>
```

The `FACT:`/`CONTEXT:`/`CUT:` prefixes matter: facts are resume
candidates; context is interview-prep and disambiguation; cuts prevent
repeating dead-end edits across sessions.

## Protocol

- **Session start**: look for the vault before interviewing. If it
  exists, read it, then ask only "what's new since <updated date>?"
  Never re-ask what the vault answers.
- **Before the first write** (no vault yet): state in one line what
  will be stored — full history including gaps with true reasons,
  visa details, references, the Q&A log — and offer three modes:
  full vault; minimal vault (FACT lines only — no Gaps & flags
  ledger, no CONTEXT references); session-only (no persistent vault,
  resume yaml only). State the trade-off honestly: minimal and
  session-only weaken the honesty ledger and the evaluator's
  gap-check.
- **During intake**: every extracted fact and every user answer goes
  into the vault *as well as* the resume. The vault only grows richer;
  facts are corrected, not deleted (move superseded claims to CUT with
  a note). That rule is accuracy bookkeeping, not retention: the file
  *is* the retention policy, and the user may purge any entry — Gaps
  & flags especially — or the whole vault, whenever they choose.
- **Tailoring**: each application gets its own projection —
  `resume-<company>-<role>.yaml` next to the vault, derived by
  *selecting and reframing* vault facts against the jd-analyzer
  output. Projections never contain a fact the vault lacks: if
  tailoring needs a new fact, it enters the vault first (with the
  user's answer), then the yaml. That invariant is what keeps twenty
  tailored resumes honest at once. Its token-level shadow is
  mechanically checkable —
  `scripts/check_projection.py <projection.yaml> career-vault.md`
  verifies that every number, date, URL, and identity token in the
  projection has vault support — but presence is not meaning: the
  script cannot bind a number to the claim it sits in (its own
  docstring says exactly what it checks and how leniently). The
  semantic invariant stays on the builder and the user's review; the
  script exists so no hard fact can enter unnoticed, not so anyone
  can skip the read.
- **Sharing**: the projection is the shareable artifact — facts
  selected for one application, never Gaps & flags, CONTEXT, or the
  Q&A log. Anything that leaves the machine (parser APIs, other
  agents, humans) gets a projection, never the vault.
- **The evaluator's L4** can then be trusted: gaps it finds are real
  gaps in the vault, not artifacts of a forgetful session.

## Why a file and not agent memory

The vault belongs to the user: portable across tools, inspectable,
correctable, and available to any future agent or none. Agent-side
memory may *point* to the vault's location; the content lives in the
user's file.
