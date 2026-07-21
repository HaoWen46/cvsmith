# The application ledger — from tailored resumes to callback evidence

A resume is DONE when the evaluator passes it; an *application* is in
flight once sent and logged. The ledger is the second half of that
seam: it is what turns twenty tailored resumes into callback-rate
evidence instead of twenty PDFs in a folder.

## What it is

One markdown file — `application-ledger.md` — beside the vault in the
user's confirmed workspace. Same privacy class as the vault: the
step-2 gate's location rules apply, `chmod 600`, gitignored, never
leaves the machine. Projections and PDFs are what get sent; the
ledger, like the vault, never is.

## Format

One block per application:

```markdown
### <Company> — <Role> (applied YYYY-MM-DD)
- channel: posting | referral (<who>) | recruiter outreach | other
- sent: resume-<company>-<role>.yaml -> <pdf filename> (rendered YYYY-MM-DD)
- jd: jd-<company>-<role>.md          (when jd-analyzer ran)
- status: applied -> screen -> interview(n) -> offer | rejected(<stage>) | no response (>N days)
- next: <action> by <date>
```

A real row:

```markdown
### Stripe — Backend Engineering Intern (applied 2026-07-14)
- channel: referral (Maya Chen, infra team)
- sent: resume-stripe-backend-intern.yaml -> resume-stripe-backend-intern.pdf (rendered 2026-07-13)
- jd: jd-stripe-backend-intern.md
- status: applied -> screen
- next: confirm phone-screen slot by 2026-07-24
```

## Capture — pull, never ritual

The skill never demands bookkeeping and never opens a "let's update
your ledger" session. Rows appear at natural moments only:

- **A tailored resume renders for a real application** — offer, in
  one line, to log channel + sent version. Respect a no.
- **The user mentions an outcome in any conversation** ("got a screen
  at X", "Y rejected me", "never heard back from Z") — update the row
  silently and confirm in one clause.
- That's all.

## Reading the funnel

Only when the user asks how the search is going (or asks directly):
summarize applications by channel and resume variant, response rate,
furthest stage reached. Diagnose with the ledger's own data — e.g.
referral vs cold-posting response rates (networking and direct
contact outperform cold applications — BLS job-search guidance), or
a variant with zero callbacks across 5+ applications, which means
revisit targeting and JD coverage before polishing prose.

## Handoffs — honest ones

- **Screen or interview reached** — interview prep is out of this
  skill's scope; say so. The vault's FACT lines and Q&A log are the
  story bank: offer a one-page brief projected from the vault for the
  specific interview.
- **Offer or negotiation** — out of scope; say so plainly.
