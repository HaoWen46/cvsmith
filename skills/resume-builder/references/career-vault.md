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
- NOT-CLAIMABLE: <something that must never be claimed — absent,
  disproven, or actively disclaimed — and why>
- PENDING-EVIDENCE: <something true-ish but not yet confirmed enough
  to claim — what's missing before it could go on a resume>

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
repeating dead-end edits across sessions. Two more prefixes carry a
mechanical contract, not just a filing convention:
`NOT-CLAIMABLE:`/`PENDING-EVIDENCE:` mark a line whose content must
never be treated as support for anything it mentions — a definite "no"
(absent, disproven, actively disclaimed) or a "not yet" (true-ish but
unconfirmed) respectively. `check_projection.py` (below) reads this as
a real exclusion: a token, date, URL, or skill found ONLY inside a line
carrying either marker (case-insensitive; any dash style — "NOT–
CLAIMABLE" counts too) is never positive evidence, for any check, and
never silently indistinguishable from a fact absent everywhere either
— it surfaces as its own labeled WARN ("matched only an excluded vault
line"). Write the disclaimer once, here, instead of relying on prose
buried in Gaps & flags or a Q&A answer the script cannot parse for
intent.

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
  `uv run scripts/check_projection.py <projection.yaml> career-vault.md`
  (the exact file just written — a stale `resume.yaml` left over from
  an earlier session is not the file to check) verifies that every
  number, date, URL, and identity token in the projection has vault
  support — but presence is not meaning: a mechanical PASS proves the
  tokens exist where they should, never that the sentence around them
  is true (its own docstring says exactly what it checks and how
  leniently). A skill or tool name (a `stack` entry, a `coursework`
  item, an item under a top-level `skills:` group) gets a different,
  stricter rule: it is an atomic token, not a sentence, so it is
  fail-closed — every significant word of it must appear somewhere in
  the vault (mod case, punctuation, and word order), boundary-matched
  so a single-letter or symbol-suffixed name (`R`, `C++`, `C#`) still
  requires real evidence rather than tokenizing away to nothing, or the
  check fails outright (`skill_unsupported`); vault it with evidence,
  or cut it, same as any other unsupported fact. Every OTHER schema
  field this script doesn't explicitly classify (a genuinely new field
  neither this doc nor the script anticipated) still gets swept for
  numbers, but also raises its own `unchecked_field` WARN — schema
  drift can surface loudly instead of silently reopening a fact class
  nobody's checking. Two narrow, conservative exceptions bind a sliver
  of meaning on top of the sentence-shaped claims, and both only ever
  WARN for a human, never FAIL on their own: a claim whose numbers
  verify but whose wording shares no content word with the one vault
  line that actually holds them (`claim_semantic_mismatch` — "raised
  revenue 40% across 3 regions" verified only by "reduced latency 40%
  across 3 services" is the same two numbers describing a different
  achievement), and a claim whose own vault entry can't be located by
  anchor but whose numbers only turn up outside anything currently
  claimed (`number_unanchored_support`). A third case sits outside both:
  a token, date, URL, or skill whose only vault trace is a line marked
  `NOT-CLAIMABLE:`/`PENDING-EVIDENCE:` (above) is not support at all —
  the vault is actively saying the opposite, or "not yet" — and gets
  its own labeled WARN (`*_excluded_only`), never a silent pass and
  never folded into the plain "no support anywhere" FAIL. No lexical
  check — this one included — can fully tell a synonym swap from a
  verb-and-object swap on word overlap alone, so the script also always
  prints a claim -> source pairing section: every content claim —
  numeric or not, bullets and summary and honors alike, not just the
  numeric ones — next to the exact vault line(s) supporting it (or its
  best-scoring line, when no honest threshold exists to grade a claim
  with no number to anchor a search to — that row is labeled `info`,
  not `pass`: `pass` means this script actually confirmed something).
  That pairing table, read by a human against the vault, is the actual
  guarantee this invariant rests on; the WARN checks are only its
  automatic, narrow subset — the verdict line reports the full
  pass/warn/info breakdown every run, and says "0 need manual audit"
  only when the warn and info counts are both genuinely zero (an
  excluded-only pairing counts too, never a silent pass dressed up as
  "nothing to review"). Presence *is* scoped to the entry,
  though: every `### <org> — <title> (<start>–<end>)` heading under
  Experience (same shape for Education/Projects — institution/degree
  or name in place of org/title) is a block the script can match a
  projection entry to by those same tokens, so a fact belonging to one
  employer can no longer verify by existing anywhere else in the
  vault — it must exist under *that* heading, or the script calls it
  misattributed. An entry whose tokens don't resolve to exactly one
  heading (typo, rename not yet recorded, or a vault section that
  simply never adopted the heading format) falls back to a whole-vault
  check with a WARN flagging that it couldn't be scoped — never a
  silent pass with no signal that scoping failed, and never a free
  pass to borrow a fact a sibling entry in the same projection is
  already matched to (that is still `number_misattributed`, same as a
  scoped entry's own misattribution). The semantic invariant stays on
  the builder and the user's review; the script exists so no hard fact
  can enter unnoticed, not so anyone can skip the read. When any of
  this leaves claims needing that read, the verdict line says so —
  `PASS — N claim(s) need manual audit` — instead of reading as an
  unqualified clean bill.
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
