# Regional & market conventions — the market decides, not the passport

Last verified: 2026-07
Verify by: 2028-07

The governing rule: **conventions follow the job's market, not the
user's location or nationality.** A candidate in Taipei applying to a
Berlin startup writes for Berlin. Infer the market from the posting's
location (jd-analyzer captures it) or the stated goal; when ambiguous
or multi-market, ask — it's one question with big consequences.

## What varies by market

| Market | Pages | Paper | Photo | Personal data | Notes |
|---|---|---|---|---|---|
| US / Canada | 1 (early-career) | us-letter | **never** | none — DOB/marital/photo can get a resume discarded for compliance | "resume"; the toolkit's defaults |
| UK / Ireland | 1–2 | a4 | no | none | "CV"; short personal statement accepted |
| DACH (DE/AT/CH) | 1–2 | a4 | traditional yes, tech increasingly optional | DOB common traditionally; trend is Anglo-style, esp. tech/multinational | "Lebenslauf"; conservative industries (banking, Mittelstand) still expect photo+DOB |
| France | 1 | a4 | common, optional | light (age sometimes) | tech sector fine without photo |
| Nordics / NL | 1–2 | a4 | no (NL sometimes) | none | Anglo-style safe |
| Spain / Italy | 1–2 | a4 | sometimes | sometimes | multinationals: Anglo-style |
| Australia / NZ | 2–3 accepted | a4 | no | none | longer CVs genuinely normal |
| India | 1–2 | a4 | not for tech | sometimes DOB | tech sector: Anglo-style |
| Singapore / SEA | 1–2 | a4 | declining | occasionally nationality/visa status (practical, not decorative) | "Singapore PR" line is common and useful |
| Gulf (UAE/SA) | 1–2 | a4 | expected | nationality + visa status expected | practical visa realities; user's call |
| China | 1 | a4 | common | DOB sometimes; 简历 norms lean concise | foreign/tech companies: Anglo-style; domestic platforms (Boss直聘 etc.) have their own profile formats outside PDF scope |
| South Korea | 1–2 | a4 | traditional yes; tech/foreign declining | DOB traditionally | chaebol/traditional firms have their own 이력서 forms; startups/foreign: Anglo-style |
| Japan | — | — | required on forms | on forms | **different documents**: 履歴書 (rirekisho, standardized form) + 職務経歴書 (work history). Out of template scope — say so; foreign/tech companies usually accept an English CV |
| LATAM | 1–2 | a4/letter varies | varies | varies | multinationals: Anglo-style |

Rows are weighted by where users of an English-language toolkit
actually apply; a market's absence means "use the fallback below",
never "unsupported". The table grows on demand like everything else.

## Market not in the table

Do **not** silently default to US style — the US is the outlier on
several conventions (letter paper, hard no-photo). Instead:

1. **Ask the user.** People usually know their market's norms
   ("do employers there expect a photo? how many pages is normal?") —
   one question, and their answer beats a stale web result.
2. **Research the specific market** (task-scoped, always-fresh tier):
   local career-center or government employment guidance, recent
   local recruiter write-ups — checking the landmines specifically:
   photo, personal data, page count, paper, language of application.
3. **When inconclusive, or the employer is a multinational/tech
   company**: use the international default — Anglo-style content
   rules, A4 paper, no photo or personal data, posting's language.
   That combination is acceptable nearly everywhere the other
   conventions are merely traditional.

Say which of the three paths was taken and why; record it in the
vault's notes so the next application to that market skips the
research.

Mechanical parse-safety (single column, real text, standard structure)
holds in every market — multinational employers typically run the
same ATS stacks across markets.

## Photo & personal-data doctrine

Default everywhere: **no photo, no DOB, no marital status, no
nationality** — it's the safe multinational norm, the direction every
market is drifting, and photos are a parse risk besides.

Deviate only when all three hold: the market column says expected, the
*specific employer type* is traditional-local (not a multinational or
tech company), and the user opts in after hearing the tradeoff. Then:
the current template doesn't render photos — say so honestly rather
than improvising layout; for photo-expecting traditional employers,
offer the choice between the photo-less version (usually acceptable in
tech) or building the document outside the template. Photo support
with proper tagged-PDF alt text is a roadmap item, not a hack.

Visa/work-authorization lines: never on US resumes (it's a form
question); practical and normal in Gulf/Singapore contexts; when in
doubt it belongs in the cover letter or form, not the CV.

## Language & spelling

- CV language follows the posting's language by default; confirm when
  the user's materials and the posting differ.
- Set `meta.lang` (and `meta.paper`) per projection — it fixes PDF
  metadata and hyphenation. Spelling follows the market: optimize/
  analyze (US) vs optimise/analyse (UK/AU); pick one and be uniform.
- **Template limitation to state honestly**: date rendering uses
  English month abbreviations, and the evaluator's L1 heading
  taxonomy is English-only. A fully non-English CV renders and passes
  L0/L2/L3 (language-agnostic) but L1's section routing won't
  recognize localized headings — note it in the report instead of
  pretending. Localized months/headings are roadmap items; today the
  toolkit is strongest for English-language applications into any
  market.

## Multi-market applications

The vault stays canonical — facts don't change by geography. Each
market gets its own projection: `resume-us.yaml`, `resume-de.yaml`
(or per-company files carrying the market's settings). What changes
between projections: `meta.paper`, `meta.lang`, spelling, page
budget, evidence emphasis, personal-data lines per the doctrine
above. What never changes: the facts. Never average two markets into
one file — a CV that half-follows two conventions reads wrong in
both.

## Europass

Only when explicitly requested (EU institutions, some public-sector
and academic applications). Private-sector EU employers largely
dislike it. Don't volunteer it; comply when the application demands
the format.
