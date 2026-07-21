# Field guide: software engineering (general)

The default conventions for backend/frontend/full-stack/platform/mobile
roles when no more specific guide applies.

## What counts as evidence (strongest first)

1. **Shipped things with scale numbers.** Users, requests/s, data
   volume, uptime, teams-served. Scale contextualizes everything else.
2. **Measured improvements.** Latency, cost, build time, error rate,
   test flakiness — before → after, with the mechanism ("by moving X
   to Y"). The mechanism is what proves it was them.
3. **Operational maturity.** On-call, incidents handled, migrations
   executed without downtime, rollout/rollback discipline. Rare and
   prized in early-career candidates.
4. **Code quality leverage.** Tooling, CI, test infrastructure,
   review culture contributions — quantified by what they saved.
5. **Open source / side projects.** Real users or real contributors
   make a side project Experience-grade; otherwise it's a Projects
   entry with a link.

## Vocabulary norms

- Name the stack inline where it did the work ("(Go, Postgres,
  Kafka)"), not as a badge wall. The Skills section corroborates.
- System nouns beat process nouns: service, pipeline, queue, cache,
  index, scheduler — not "solution", "initiative", "effort".
- Standard titles only in the title field; if the internal title was
  weird ("Member of Technical Staff II"), keep it and let the bullets
  explain the level.

## Red flags screeners notice

- Framework soup in Skills with no framework evidence in bullets.
- "Full-stack" with no depth signal on either side.
- Percentage improvements with no absolute anchor.
- Ten one-line jobs (looks like task-hopping) — merge or cut minor
  stints; the resume is claims you want probed in interviews, not an
  employment ledger. (Never falsify dates to close gaps; select what
  to present, don't alter what's true.)

## Entry ordering

Field convention for experienced profiles is education-last; the
templates render Education first (the student/early-career default
this toolkit targets) and don't support reordering — tell the user
rather than implying otherwise.
Students/new grads: Education → Experience → Projects → Skills.
Awards/Publications only when they carry real weight in this field
(ICPC, major hackathons, papers — yes; attendance certificates — no).
