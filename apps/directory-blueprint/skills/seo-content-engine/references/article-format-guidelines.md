# Article Format Guidelines

Which structure to build. The format has to match the search intent behind the
keyword, and the fastest read on that intent is the SERP itself: if the pages ranking
for a keyword are all "best tools" lists, a long essay is fighting the format Google
already rewards. Stage 1 reads the dominant format off the ranking pages and suggests
it; the user confirms or overrides at the outline stage (Stage 4). This file covers
the formats; for *how to write* each section, see
`references/article-template-guidelines.md`, and for the writing rules themselves see
`references/article-style-rules.md`.

## Contents

1. How intent maps to format (read first)
2. Universal rules (apply to every format)
3. Listicle / Roundup — "Best X for Y"
4. Alternatives — "Best X Alternatives"
5. Comparison — "X vs Y"
6. Review — "X Review"
7. How-to Guide — "How to X"
8. Pillar Guide — "The Complete Guide to X"
9. Answer Post — "What is X" / question keywords
10. Tone by format; ambiguous formats; Custom

---

## 1. How intent maps to format (read first)

Every keyword sits in one search intent. Match the format to it, and check the Stage 1
SERP to confirm what's actually ranking:

- **Commercial investigation** (comparing options before buying): Listicle/Roundup,
  Alternatives, Comparison. The reader wants organized, analyzed choices.
- **Transactional / decision** (ready to act on one thing): Review, sometimes
  Comparison. The reader wants a verdict.
- **Informational — procedural** (wants to do something): How-to Guide.
- **Informational — understanding** (wants to know something): Answer Post for a
  narrow question, Pillar Guide for a broad topic.

**SERP-match rule:** the ranking pages tell you the format Google rewards for this
query. Suggest that format. But the user's real goal wins — if they want a genuine
comparison and the SERP is listicles, build the comparison and note the mismatch.
Don't force a format just because it ranks; match intent, then differentiate.

---

## 2. Universal rules (apply to every format)

These are the **structural** requirements — the sections every article needs. For
*how to write* them (answer-first, self-contained sections, keyword placement,
forbidden openers, voice, humanizer), see `references/article-style-rules.md`; this
section doesn't repeat those.

- **Freshness anchor.** A "What's New in [current year]" section after the intro (and
  after the TL;DR where one exists). Include only changes that are BOTH recent (~last 12
  months) AND relevant to the topic; **skip the section entirely if nothing qualifies** —
  don't pad it with a stale or off-topic item (see the What's New template). Compute the
  year at runtime; never hardcode it.
- **E-E-A-T block.** A "How We Evaluated" section is required for the product
  formats (Listicle, Alternatives, Comparison, Review) and must describe real
  evaluation, not boilerplate.
- **FAQ.** Every format ends with an FAQ (3–6 questions), just before the verdict.
  Seed the questions from the Stage 1 Opportunities data — see the FAQ template.
- **Cover the checklist, then beat it.** The Stage 1 entity/topic checklist is your
  completeness test — match what the ranking pages cover, then add the angle they miss
  (often the specific audience fit). The deep-sections template is for that.
- **Cluster linking.** Where it fits, link to related posts on the same site (from
  Stage 2 sources) — Google reads an interlinked cluster as topical authority.
- **Title.** Give the article a specific title with the keyword and the current year
  (computed at runtime). Each format below has a title pattern and example.
- **Verdict close.** Every format ends with a stance-taking close (a verdict), never a
  flat "Conclusion" — see the Verdict template.

---

## 3. Listicle / Roundup — "Best X for Y"

**Intent:** commercial investigation — the reader wants an analyzed shortlist with a
clear winner. Strongest featured-snippet format for "best/top X" queries.

**Analysis, not aggregation:** the rule that makes or breaks a roundup. Listing
options with generic blurbs is thin content and gets demoted. Every pick needs a real
judgment — who it suits, a genuine weakness, real pricing.

**No TL;DR here.** The **ranked list is the answer block** — a short "Best [X]" H2 with
a numbered list of picks, right after the intro, is what Google lifts as the snippet.
Don't add a separate TL;DR on top; it would just duplicate the role.

**Title format:** `[Number] Best [category] for [use case] ([modifier])` — where the
modifier is a value cue like "Ranked & Tested", "Reviewed", "Compared". Example:
"8 Best Payroll Apps for Small Businesses (Ranked & Tested)".

**Intro hook:** open on the reader's real friction with the category or a claim about
what most lists get wrong, then state the basis for the ranking. Keep it concrete and
specific to the audience.

**Structure:**
- H1 naming the category and use case
- Intro, then the ranked list of picks (the snippet target)
- Freshness anchor
- "How We Evaluated"
- A comparison section covering every pick on the same criteria
- One section per pick (aim 5–8, **cap at 7** — engagement drops past that), pick name
  in the heading. See the per-product template.
- "How to Choose" — guidance by use case
- FAQ
- Verdict (carries the keyword) — restate the winner

**Notes:** commit to a real winner. #1 is the one you'd actually pick.

---

## 4. Alternatives — "Best X Alternatives"

**Intent:** commercial investigation from readers who want to replace a specific tool.
The "baseline product" is the tool named in the keyword that they're looking to
replace (e.g. for "Best Mailchimp Alternatives", the baseline is Mailchimp).

**No TL;DR here** — like a roundup, the ranked list is the answer block.

**Title format:** `[Number] Best [baseline product] Alternatives ([modifier])` — with a
value cue like "Ranked & Tested". Example: "7 Best Mailchimp Alternatives (Ranked & Tested)".

**Intro hook:** open on the specific, relatable reason someone wants to move off the
baseline product — one honest frustration — then turn to what actually works. Don't
open by describing how popular the baseline is.

**Structure:** same ranked-list answer block as a roundup, but every pick is framed
against the baseline:
- H1: "Best [baseline product] Alternatives"
- Intro, then the ranked list of alternatives
- "Why look past [baseline product]" — honest pain points
- Freshness anchor · "How We Evaluated"
- One section per alternative — **and each section states plainly how it differs from
  the baseline product** (the reason to switch, migration friction, price gap), not a
  generic feature dump. The reader already knows the baseline; give them the delta.
- Comparison section: alternatives against the baseline product
- FAQ
- Verdict (keyword)

**Notes:** every alternative earns its spot by being *different from* the baseline in a
way that matters, not just "also good."

---

## 5. Comparison — "X vs Y"

**Intent:** late commercial investigation — narrowed to two, wants a decision.

**Title format:** `[X] vs [Y] ([year]): Which Should You Pick?` — Example:
"Stripe vs Square (2026): Which Should You Pick?".

**Intro hook:** name the single biggest difference between the two in the first
sentence. Don't call them both great — the reader came to choose one.

**Structure:**
- H1: "[X] vs [Y]"
- Intro, then an answer-first TL;DR that **names the overall winner** and the
  use-case winners (no hedging in the TL;DR — it must call it)
- Freshness anchor · "How We Compared"
- An at-a-glance side-by-side on the main dimensions
- One section per dimension (pricing, core features, ease of use, support,
  integrations), each naming a winner for that dimension
- **"Key Differences"** — a short bulleted section capturing the handful of
  differences that actually decide it ("X does [thing]; Y does [other thing] instead")
- "Who should pick X" / "Who should pick Y" — specific scenarios for each
- FAQ
- Verdict (keyword) — the overall pick plus the main caveat

**Notes:** call a winner in every dimension and overall. A comparison that won't
choose fails its job. Stay fair to both sides.

---

## 6. Review — "X Review"

**Intent:** transactional/decision — close to buying one product, wants an honest
verdict.

**Title format:** `[Product] Review ([year]): Is It Worth It?` — Example:
"Notion Calendar Review (2026): Is It Worth It?".

**Intro hook:** open on the single most surprising or counterintuitive thing about the
product — something a reader wouldn't expect. Don't open by announcing what the review
will cover.

**Structure:**
- H1: "[Product] Review"
- Intro, then an answer-first TL;DR with the verdict and a rating (repeat the rating in
  the verdict too — those are the two anchor points)
- Freshness anchor — latest version, recent changes
- "How We Evaluated"
- "What is [product]" — brief background and positioning
- Feature sections with real, specific observations
- "Pricing" — the tiers and a value read (real prices, no "contact sales")
- "Pros and Cons" — honest and specific
- **"Who it's for"** — 2–3 specific personas (name the person and the reason it fits),
  and who should skip it
- "Alternatives to consider" — 2–3 briefly
- FAQ
- Verdict (keyword) — restate the rating and give a concrete buy / don't-buy / buy-if call

**Notes:** a review with no real cons isn't trusted. Ground claims in specifics.

---

## 7. How-to Guide — "How to X"

**Intent:** informational, procedural — wants a working procedure.

**Title format:** `How to [do the task] ([year] Guide)` — Example:
"How to Set Up a Podcast RSS Feed (2026 Guide)".

**Intro hook + outcome:** open on the payoff or the friction, then promise the concrete
outcome ("By the end, you'll have [result]").

**Structure:**
- H1: "How to [task]"
- Intro that promises the outcome, then an answer-first short version of the steps
- Freshness anchor if the method changes
- "What you'll need" — only if there are real prerequisites
- Numbered step sections, in order
- "Troubleshooting" or "Common Mistakes"
- FAQ
- Verdict/close (keyword)

**Step-writing specifics:**
- Each step is its own H2, starting with the action, not background: "Generate the feed
  URL", not "About feed URLs". Sub-steps go in H3s beneath.
- Open each step with the action to take; close it with what the reader should now have
  done, so they know they're on track before the next step.
- Move straight into each step — don't announce it with "Next, let's…".
- Note the rough time a step takes if it helps set expectations.

**Notes:** every step must be followable on its own. Answer the core "how" early for
snippet capture.

---

## 8. Pillar Guide — "The Complete Guide to X"

**Intent:** broad informational + topical-authority hub for a content cluster.

**Title format:** `The Complete Guide to [topic] ([year])` — Example:
"The Complete Guide to Container Gardening (2026)".

**Intro hook:** open on the scale, stakes, or a common misconception about the topic,
then give the answer-first one-paragraph summary of the core question.

**Structure:**
- H1: "The Complete Guide to [topic]"
- Intro, then an answer-first one-paragraph answer to the core question
- Freshness anchor — what changed this year
- Sections progressing fundamentals → advanced, covering the full Stage 1 checklist,
  each linking out to deeper cluster posts where they exist (Stage 2 sources)
- "Common Mistakes" or "Best Practices"
- FAQ
- Verdict/close (keyword) — recap + next step

**Notes:** depth and structure win. A pillar is a hub — link to supporting posts so the
cluster reads as authority. Pillars decay: flag anything version- or date-bound so it's
easy to keep current.

---

## 9. Answer Post — "What is X" / question keywords

**Intent:** informational, narrow — wants a clear answer to a specific question.
Optimized for featured snippets and AI citation.

**Title format:** `What Is [topic]? [short framing] ([year])` — Example:
"What Is a Roth IRA? A Plain-English Guide (2026)".

**Intro hook:** open on a surprising fact or a common misconception about the term,
then give the direct answer.

**Structure:**
- H1 as the question
- A direct 40–80 word answer immediately (prime snippet target)
- Freshness anchor if the topic moves fast
- "What is [X]" — expanded definition
- "How [X] works" / "Why [X] matters"
- "Types of [X]" or "Examples of [X]" — with a concrete example each
- FAQ
- Verdict/close (keyword)

**Notes:** answer in the first ~100 words, then expand. Each section should be
independently quotable.

---

## 10. Tone, ambiguity, and custom formats

### Tone by format
- **Listicle/Roundup** — opinionated, comparative, specific ("the top pick is X because…").
- **Alternatives** — pragmatic, solution-focused ("if X isn't working, here's what does").
- **Comparison** — decisive but fair ("both are solid, but X wins for Y").
- **Review** — honest and balanced ("the good, the bad, the call").
- **How-to Guide** — instructional and patient ("do this, then this").
- **Pillar Guide** — authoritative and thorough, a hub that sends readers deeper.
- **Answer Post** — clear and example-driven ("here's what it means, here's an example").

### When the format is ambiguous
If the keyword's wording and the SERP disagree, the SERP wins — build for what's
actually ranking, and confirm with the user. If the ranking pages are split across
formats with no majority, surface that at the outline stage and let the user choose; a
split SERP usually means mixed intent, so the user's goal decides.

### Custom — the user described their own format
When the user picks "None of these fit — I'll describe the article I want": take their
description, find the closest format above, start from its structure, and adapt —
adding, dropping, or reordering sections to fit their intent. Keep the universal rules
(section 2) and the style rules regardless. Show the adapted outline at the approval
gate like any other format.
