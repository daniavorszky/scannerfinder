# Article Template Guidelines

How to write each section well. These apply on top of the formats in
`references/article-format-guidelines.md` and the writing rules in
`references/article-style-rules.md`. Every quoted question, heading, or entity from
Stage 1 is used verbatim (light rewording only to fix grammar); nothing is invented
that the Stage 1 data doesn't support.

Each template below has two good examples (from different niches) and one bad example
that shows what to avoid — including the AI tells and filler the style rules ban.

## Contents

1. Intro
2. TL;DR (answer-first block)
3. What's New (freshness anchor)
4. How We Evaluated (E-E-A-T)
5. Ranked list (roundup/alternatives snippet)
6. Per-product block
7. FAQ
8. Deep sections (content-gap coverage)
9. Verdict (the close)
10. Meta title + meta description

---

## 1. Intro (150–200 words, no heading)

The hook plus the setup — always first, before any answer block. Open with a stat, a
real friction point, a pointed question, or a claim that cuts against a common
assumption. Name the problem in the reader's terms ("you"), land the primary keyword
in the first 200 characters, and close by pointing at what they'll get — specific, not
"in this article we'll cover." Keep it tight; the answer block does the summarizing.

**Good (how-to):** "Your podcast won't show up in Apple or Spotify without a valid RSS
feed, and most hosting guides skip the part where it breaks. Setting one up takes about
twenty minutes if you know which four fields actually matter. Here's the exact setup,
plus the two mistakes that get feeds rejected."

**Good (review):** "The surprise with Notion Calendar isn't what it does — it's what it
refuses to do. There's no shared team view, and that single gap decides whether it fits
your workflow. After a month running it against Google Calendar, here's who it's for."

**Bad:** "In today's fast-paced world, staying organized is more important than ever.
In this comprehensive guide, we'll explore everything you need to know about calendar
apps and delve into the features that matter." *(Fails: banned opener, "comprehensive",
"delve", meta-commentary, says nothing specific.)*

---

## 2. TL;DR — answer-first block (50–80 words, italic, no heading)

Used by Comparison, Review, How-to, Pillar, and Answer Post. (Roundup and Alternatives
use the ranked list instead — see 5.) It sits right after the intro, before the first
H2, in italics, with no "TL;DR:" label.

The rule that matters: **it is the answer, not a description of the article.** A reader
who stops here should know the recommendation, verdict, or definition — not a list of
what's coming. Lead with the answer; add one specific detail; land the primary keyword
once. Reviews include the rating; comparisons name the winner.

**Good (comparison):** *"Pick Stripe if you sell online and want the better developer
tools and payout flexibility. Pick Square if you sell in person and want hardware plus
flat, predictable fees. Stripe wins overall for online-first businesses; Square wins
for retail and cafes. Fees are close, so the deciding factor is where you actually take
payments."*

**Good (answer post):** *"A Roth IRA is a retirement account you fund with money
you've already paid tax on, so qualified withdrawals in retirement are tax-free. The
2026 contribution cap is $7,000 (or $8,000 if you're 50 or older), with income limits
that phase out higher earners. It suits people who expect to be in a higher tax bracket
later."*

**Bad:** *"This guide covers everything about Roth IRAs, including how they work, the
benefits, and what you need to know before opening one. Read on to find out more."*
*(Fails: describes the article instead of answering; "read on to find out" adds nothing.)*

---

## 3. Freshness (weave it in — usually not a standalone section)

Recent developments earn a place in the article ONLY when they pass all three gates:
1. **Recent** — within roughly the last 12 months (check against the runtime year); an
   older item isn't "new."
2. **Relevant** — a change to this article's actual topic or the tools it covers, not a
   tangential industry event.
3. **Consequential** — it changes how the reader should read or act on the article. If
   you can't write the "…so this changes [X]" clause, it's trivia — cut it. A reader
   should never hit a freshness line and think "why is this here?"

Facts come from **current external research, not the Stage 1 ranking pages** — verify
each against a credible source in Stage 6 and link it, like any other claim.

**Where it goes:** weave a consequential change into where it matters — the intro hook,
or right beside the ranking/section it affects — rather than a bolted-on "here's some
news" block. Keep it tight: a line or two, always paired with its consequence. A
**standalone "What's New in [year]" section** is worth it only when there's enough
genuinely consequential change to fill it (mainly Pillar Guides, or any format on a
fast-moving topic). If nothing passes the three gates, include no freshness content at
all — that's fine; not every topic has recent news worth acting on.

**Good (woven into a roundup intro):** "Two things reshaped this list in the last year:
MCP became a neutral standard, so a tool's raw integration count matters less than it
did, and agent usage now gets billed separately from your main plan — so the picks
below are judged on today's pricing and connectivity, not last year's."

**Good (standalone, Pillar Guide):** a short "What's New in [topic] for [year]" section
naming 2-3 dated, sourced shifts, each with the one line on why it changes the guidance
below.

**Bad:** "In December 2025, Anthropic donated the Model Context Protocol to the Linux
Foundation." *(Fails gate 3: it's a real, recent, on-topic fact, but as written it's
trivia — it doesn't tell the reader what to do differently. Either add the consequence
or cut it.)*

---

## 4. How We Evaluated (100–180 words)

Required for the product formats. It's the credibility (E-E-A-T) section — so it must
be **honest**. Here is the hard rule:

**NEVER claim first-hand, hands-on testing the skill did not do.** The skill cannot
sign up for products, build workflows, time them, or use a tool for a month — so it
must not write "we built", "we tested", "we timed", "we ran a pay cycle", "we used it
for four weeks", or invent metrics like "9 minutes from signup". Those are fabricated
experience, and faking the trust section is worse than having a thin one.

**Default (honest) framing:** describe the real basis for the evaluation — that the
picks were **compared against specific, published criteria** drawn from each vendor's
own pricing pages, documentation, and feature lists (and the Stage 1 analysis of what's
ranking). Name the actual comparison dimensions (pricing at a stated usage level, the
features that matter for this audience, integrations, free-tier limits, support), and
what got cut and why. Cite prices from the vendor's page (and link them). Title the
section **"How We Evaluated"** (evaluation against criteria), not "How We Tested".

**Only** if the user supplied genuine first-hand experience ("I've used all of these")
may you write real testing claims — grounded in exactly what they told you.

**Confident, not apologetic.** Honest doesn't mean self-deprecating. Lead with what you
DID assess and why those criteria are what actually decide the choice — sell the rigor
of the comparison. Do NOT open by disclaiming what you didn't do ("this isn't a lab
test", "treat this as just a documentation analysis", "rather than hands-on builds").
That framing makes the ranking sound weak. State the method plainly and move on; the
criteria are the strength.

**Good (roundup, criteria-based):** "We compared the eleven tools on the things a small
business actually feels: real monthly cost at 2,000 workflow runs, whether the free tier
does anything useful, native integrations with the apps most teams already run, and how
much setup assumes you can code. Prices come from each vendor's own pricing page as of
[Month Year] and are linked so you can check them against your quote. Anything that
hides core pricing behind a sales call was cut."

**Good (review, criteria-based):** "This review looks at Notion Calendar on scheduling,
time-zone handling, how it syncs with Notion databases, and where it fits for a small
team, based on Notion's official documentation and pricing as of [Month Year]."

**Bad (apologetic):** "I compared these against published criteria rather than hands-on
builds, so treat this as a documentation-and-pricing analysis, not a lab test."
*(Honest but self-defeating — it undersells the ranking by leading with what it isn't.
Lead with the real criteria instead.)*

**Bad (empty):** "We thoroughly evaluated each option using a comprehensive methodology
to ensure the most robust recommendations." *(Fails: "thoroughly", "comprehensive",
"robust", "ensure"; no numbers, no real criteria — says nothing verifiable.)*

---

## 5. Ranked list (Roundup / Alternatives snippet, ~100 words)

The featured-snippet target for "best/top X" and "X alternatives" queries. A short H2
(the keyword core — drop the number, year, and modifiers, e.g. "Best Payroll Apps")
followed by a numbered list of every pick. One line each: bolded product name, then a
short who-it's-for tag. Keep each line under ~12 words — no pricing, no features, no
caveats (those go in the per-product blocks). Numbered, not bulleted. Every pick here
has a matching detailed block later. Cap at 7. Cover two searcher intents where it fits
(a top pick and a budget/alternative pick).

**Good (roundup):**
```
## Best Payroll Apps for Small Businesses
1. **Gusto**: best overall for small teams
2. **QuickBooks Payroll**: best if you already use QuickBooks
3. **OnPay**: best value for tight budgets
4. **Rippling**: best for teams that are scaling fast
5. **Square Payroll**: best for hourly and contractor-heavy shops
```

**Good (alternatives):**
```
## Best Mailchimp Alternatives
1. **Brevo**: best overall for lower send costs
2. **MailerLite**: best for simple, clean campaigns
3. **ConvertKit**: best for creators and newsletters
4. **Klaviyo**: best for e-commerce automation
```

**Bad:**
```
1. **Gusto** ($40/mo + $6/employee) is a comprehensive, robust payroll solution that
   can revolutionize the way you handle payroll with its seamless, cutting-edge features.
```
*(Fails: pricing and features belong in the deep block, not the snippet line; "comprehensive",
"robust", "revolutionize the way", "seamless", "cutting-edge" are all banned; line far too long.)*

---

## 6. Per-product block (200–400 words each)

One H2 per product: `#[rank]. [Product] — best for [specific segment]`. The segment must
be specific. Structure: a two- to three-sentence opener (what it is, what sets it apart,
one hard number if you have it); honest, specific pros and cons (measurable where
possible); the one thing it does better than anything else on the list, with an example;
and real pricing (name the tiers, no "contact sales"). Avoid forbidden sub-headings
like "key features" — see the Alternatives/Substitutions list in
`article-style-rules.md` for the plainer wording. The top pick gets the most room; vary
the block structure slightly so they don't read as a template. Never fake a pro or con,
and never claim hands-on testing that didn't happen (no invented "took nine minutes from
signup" metrics — see the How We Evaluated rules).

**Link each product to its official page.** The first mention of each tool's name (or
its heading) should link to the product's own site, using the tool name as the anchor —
readers of a roundup/alternatives/comparison want to click through to the tools. These
are official-source links (not competitor article pages), so they're encouraged.

**Good (roundup pick):** "**#1. [Gusto](https://gusto.com) — best for small teams that
want payroll to just run.** Gusto handles payroll, benefits, and 1099 filing in one
flow, and it files in all fifty states without an add-on. Its pricing starts at $49/month
plus $6 per person (from Gusto's pricing page). What it does well: automatic tax filing,
clear employee self-onboarding, and same-day deposit on the Plus plan. The catch: no
true international payroll, so a distributed team with overseas contractors will outgrow
it. Pricing starts at $49/month plus $6 per person."

**Good (alternatives pick):** "**#2. MailerLite — best for a cleaner, cheaper switch.**
Unlike Mailchimp, MailerLite keeps its editor simple and doesn't count unsubscribed
contacts against your plan, which is where Mailchimp bills quietly creep up. Migrating
took under an hour with its import tool. Where it trails Mailchimp: fewer third-party
integrations. Free up to 1,000 subscribers, then $9/month."

**Bad:** "**Gusto** is a powerful, user-friendly platform with a comprehensive suite of
features. It's a game-changer for businesses of all sizes. Pros: easy to use, reliable,
great support. Cons: could be better in some areas." *(Fails: "powerful",
"user-friendly", "comprehensive", "game-changer"; vague pros; a non-con con; no numbers,
no real pricing.)*

---

## 7. FAQ (3–6 questions, before the verdict)

**Use the real questions from the Stage 1 Opportunities section** (People Also Ask, Top
Pages FAQ, People Also Search) — every FAQ question must map to one of those. Prefer the
verbatim phrasing; light rewording only to fix awkward grammar, never to change meaning
or invent a question. If only three real questions exist, write three — don't pad with
made-up ones.

Each question is an H3. Each answer is **40–60 words, self-contained** (it should make
sense lifted out on its own): answer directly in the first sentence, add one supporting
detail, and a specific number or example if it fits. No "Great question", no bare
yes/no, no repeating the question back. Place the FAQ near the end, just before the
verdict. (Clean H3-question formatting also reads well for AI answer engines, which pull
question-answer pairs.)

**Good:**
```
### How much does payroll software cost for a small business?
Most small-business payroll apps run $40 to $50 per month as a base fee, plus $6 to $9
per employee. A three-person team lands around $60 to $75 a month. Tools that quote
"custom pricing" for core payroll are usually aimed at larger companies.
```

**Good:**
```
### Can I switch payroll providers mid-year?
Yes, though the cleanest time is at the start of a quarter. You'll need your prior
provider's year-to-date payroll reports so the new tool can carry over tax totals. Most
apps import these in a few clicks, and switching mid-quarter mainly just adds a
reconciliation step.
```

**Bad:**
```
### Is payroll software good?
Great question! Yes, payroll software is definitely worth it. It's important to note
that it can really help your business in many ways. It depends on your needs.
```
*(Fails: vague question not from the data; "Great question"; "it's important to note";
bare "it depends" with no specifics; says nothing.)*

---

## 8. Deep sections (content-gap coverage)

This is where you beat the ranking pages instead of matching them. Using the Stage 1
entity/topic checklist, find the subtopics that the top pages barely cover — the gaps —
and give each a proper section. These often rank on their own for long-tail phrases and
are the reason an article outperforms the field.

- Pull candidates from the Stage 1 gaps: entities or subtopics that appear on only one
  or two of the ranking pages, or real questions from the Opportunities data that no
  page answers well.
- 200–400 words each. Don't pad — if 150 words fully covers it, stop.
- At most three deep sections; more bloats the article.
- These can be more opinionated than the rest of the piece, and they're the natural home
  for a genuine expert take. Back specific claims with a credible source (Stage 6).

**Good (a gap most competitors skip):** a "Payroll for a mix of W-2 and 1099 workers"
section in a small-business payroll roundup, because most ranking pages assume all-W-2
teams — a real gap for the audience.

**Good:** a "What breaks when you self-host" section in a "best n8n alternatives" piece,
covering the maintenance reality no vendor page mentions.

**Bad:** a generic "Why payroll matters" section that every ranking page already has —
that's coverage-matching filler, not a gap. Cut it.

---

## 9. Verdict — the close (100–200 words)

The final section takes a stance; it's never a flat "Conclusion". Head it "Verdict",
"Our Verdict", "The Bottom Line", or "Verdict on [secondary keyword]". State the single
top recommendation and the one reason; segment it ("if you need X, pick A; on a tight
budget, B"); close with a concrete next step. Weave the primary keyword in once. No new
information, no rehashing the intro, no hedging with "it depends" without saying depends
on *what*. Be decisive.

**Good (roundup):** "For most small businesses, Gusto is the pick — it runs payroll and
filing without babysitting, and it's the fastest to set up. If you already live in
QuickBooks, its payroll add-on is worth the tie-in. On the tightest budget, OnPay does
the core job for less. Start any of them on a free trial and run one real pay cycle;
you'll know within a week whether it fits."

**Good (comparison):** "Stripe is the better payment platform for online-first
businesses, full stop — the developer tools and payout options pull ahead. Square only
wins if most of your sales happen at a counter, where its hardware and flat fees make
life simpler. Pick by where you take payments, not by the fee tables, since those nearly
match. If you sell both ways, Stripe's the safer long-term base."

**Bad:** "In conclusion, both options have their strengths and weaknesses, and the best
choice ultimately depends on your specific needs and requirements. We hope this guide
has been helpful." *(Fails: "in conclusion", hedges with no actual pick, no next step,
says nothing.)*

---

## 10. Meta title + meta description (drafted at Stage 5, output at Stage 8)

Two lines for the user's CMS — not part of the article body. Draft them at Stage 5 (show
them with the draft), confirm at Stage 8.

**Meta title — 50–60 characters** (Google shows ~600px; it truncates past that):
- Front-load the exact primary keyword.
- Use hyphens as separators, not pipes.
- Make it specific and unique — a year, audience, or concrete hook where natural.
- Don't stuff extra keywords; write it to read well to a person.

**Meta description — 150–160 characters** (mobile truncates ~120, so front-load the
value):
- Expand on the title, don't repeat it.
- Active voice; address the reader; include one specific benefit and an implicit call to
  action.
- Include the primary keyword once, naturally.
- It's not a ranking factor, but it drives click-through — write it for the reader.

**Good:**
- Title: `Best Payroll Apps for Small Businesses (2026)` (45 chars)
- Description: `We ran a real pay cycle on 11 payroll apps. See which one sets up fastest, files in all 50 states, and costs least for a small team.` (135 chars)

**Bad:**
- Title: `Payroll Software | The Best Payroll Solutions & Tools for Your Business Needs 2026` *(too long, pipe separator, keyword-stuffed)*
- Description: `Learn about payroll software in this comprehensive guide.` *(too short, "comprehensive", starts with "Learn about", no benefit or CTA)*
