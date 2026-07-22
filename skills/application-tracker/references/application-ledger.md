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

## Format

One block per application:

```markdown
### <Company> — <Role> (prepared YYYY-MM-DD)
- channel: posting | referral (<who>) | recruiter outreach | other
- sent: resume-<company>-<role>.yaml -> <pdf filename> (rendered YYYY-MM-DD)
- jd: jd-<company>-<role>.md          (when jd-analyzer ran)
- status: prepared -> applied YYYY-MM-DD -> screen YYYY-MM-DD -> interview(n) YYYY-MM-DD -> offer YYYY-MM-DD | rejected(<stage>) YYYY-MM-DD | no response (21+ days)
- next: <action> by <date> | none
```

A row starts as **prepared** the day the resume renders. It becomes
**applied** only when the user confirms they submitted — dated the
actual submission date, never the render date. A rendered PDF is not
an application. Funnel denominators count applied rows only; prepared
rows are pipeline, not applications.

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
Meta roles on file), ask which role in one clause — never guess,
never update both.

A real row:

```markdown
### Stripe — Backend Engineering Intern (prepared 2026-07-13)
- channel: referral (Maya Chen, infra team)
- sent: resume-stripe-backend-intern.yaml -> resume-stripe-backend-intern.pdf (rendered 2026-07-13)
- jd: jd-stripe-backend-intern.md
- status: prepared -> applied 2026-07-14 -> screen 2026-07-21
- next: confirm phone-screen slot by 2026-07-24
```

## Capture — pull, never ritual

The skill never demands bookkeeping and never opens a "let's update
your ledger" session. Rows appear at natural moments only:

- **A tailored resume renders for a real application** — offer, in
  one line, to log a prepared row: channel + sent version. Respect a
  no.
- **The user confirms submission** ("sent it", "applied last night")
  — flip prepared to applied with the actual submission date; confirm
  in one clause.
- **The user mentions an outcome in any conversation** ("got a screen
  at X", "Y rejected me", "never heard back from Z") — update the row
  silently and confirm in one clause.
- That's all.

## Reading the funnel

Only when the user asks how the search is going (or asks directly):
summarize applied rows by channel and resume variant, response rate,
callback rate, furthest stage reached. Fixed definitions, so every
session computes the same funnel: a **response** is any employer
reply tied to the application (a rejection is a response); a
**callback** is reaching screen or beyond (a rejection is never a
callback); both rates divide by applied rows; **no response** means
applied with nothing back for 21+ days — younger silence is
*pending*, not a data point. Prepared rows get a one-line pipeline
count, never a rate. The evidence is the ledger's own numbers — *its*
referral vs cold-posting response rates are what justify shifting
effort, so act on the funnel's figures. (BLS job-search guidance
treats resumes, networking, interviewing, and negotiation as one
funnel — a resource list, not comparative outcome data; don't cite it
as proof one channel beats another.) Zero callbacks across 5+ applied
rows on one variant is a signal to inspect targeting and JD coverage
— a prompt for investigation, not proof of cause.

## Handoffs — honest ones

- **Screen or interview reached** — interview prep is out of this
  skill's scope; say so. The vault's FACT lines and Q&A log are the
  story bank: offer a one-page brief projected from the vault for the
  specific interview.
- **Offer or negotiation** — out of scope; say so plainly.
