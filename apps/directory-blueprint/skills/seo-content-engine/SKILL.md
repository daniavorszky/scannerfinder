---
name: seo-content-engine
description: Runs an 8-stage interactive workflow (plus a DataForSEO setup step) that uses the DataForSEO MCP (dfs-mcp) to analyze the live competitor SERP for a topic and produce a humanized, SEO-optimized article behind fact-checking and quality audits. Use when the user wants to write a comprehensive blog post or long-form article, analyze competitor rankings for a keyword, build a content brief or outline from the top-ranking pages, or run a structured content-marketing workflow. Also use when the user mentions SEO writing, SERP analysis, competitor content analysis, content briefs, internal linking, or humanizing AI-written copy.
metadata:
  author: skill-creator session
  version: 2.0.0
  mcp-server: dfs-mcp
  environment: Claude Code
---

# SEO Content Engine

An interactive, stage-by-stage workflow: after a DataForSEO setup step, it runs eight
stages that take the user's topic/keyword, study the live top-ranking pages via
DataForSEO, and write an article built to compete (analyze the SERP → brief → write →
humanize → publish). Run stages in order. NEVER skip a stage or auto-advance.

Built for **Claude Code**. Output files land in the user's project; there are no
command-line flags — the user drives everything by chatting.

## Interaction style (applies to the whole skill)

- **Ask exactly ONE thing per turn.** Never stack questions. Keep each message to
  a sentence or two plus the single ask — no heavy paragraphs, no long instruction
  dumps. The user should always know the one thing they need to answer.
- **Plain language.** Don't narrate your reasoning or explain errors unless asked;
  just say what's needed next.
- **Whenever you ask for input, add a one-line explanation and a concrete example**
  so the ask is never ambiguous (e.g. don't say "audience?" — say what you mean and
  give examples).
- **Match the reply format to the situation** — don't force "1 or 2" everywhere:
  - A genuine either/or choice → numbered ("reply **1** or **2**").
  - A single next action with no alternatives → a word ("reply **Continue**").
  - A confirmation → yes/no ("reply **yes**, or give me a better one").
- **Say which skill is running** in your first message of a run ("Running the SEO
  Content Engine"), so the user knows which skill answered even if others are
  installed.

## Progress checklist

Copy this into your reply and tick items as you finish them. It keeps the run
honest and stops stages from being skipped.

```
- [ ] Stage 0: DataForSEO MCP Setup (skip if already connected)
- [ ] Stage 1: SERP Analysis
- [ ] Stage 2: Existing-Content Sources
- [ ] Stage 3: Product Integration
- [ ] Stage 4: Outline + BLUF  (hard approval gate)
- [ ] Stage 5: Article Draft
- [ ] Stage 6: Fact Check + Quality Audit
- [ ] Stage 7: HTML Preview
- [ ] Stage 8: Final Export
```

## Checkpoint Protocol (RUN AT THE END OF EVERY STAGE)

This is the heart of the skill. Do not treat it as optional.

1. **Present inline.** Show the artifact directly in chat — the competitor summary,
   the entity list, the outline. Do NOT auto-generate downloadable files. Offer a
   file (md, xlsx) only if the user asks for one.
2. **Give the takeaway.** 2–3 lines: what was found, what is currently selected,
   and why. Name the specific reasoning.
3. **Invite refinement.** Explicitly ask what to add, drop, swap, or adjust.
4. **Loop.** If the user wants changes, apply them and re-present. Never advance
   on the first pass.
5. **Gate.** Only once the user is satisfied, do BOTH, in order:
   a. **Re-print the FULL progress checklist — every line, Stage 0 through Stage 8.**
      Tick completed stages `[x]` (including the one just finished) and mark the next
      as current (`← we are here`). NEVER abbreviate to just the last/next few — the
      user should see the whole workflow and how much remains.
   b. Ask an explicit go/no-go ("Ready for Stage N?"). Wait for a clear yes; do NOT
      auto-advance.
   Do this at every stage gate, but only at the gate — not on intermediate refinement
   replies.

If a stage produces "nothing useful" (no matching URLs, no fitting product),
say so plainly at step 2 and let the user decide — never force a bad result.

---

## Stage 0: DataForSEO MCP Setup

Runs first, every time. Full step-by-step flow is in `references/setup.md`.

**Check for an already-connected DataForSEO MCP FIRST — before touching
`references/credentials.md`.** Detect it by **tool name**, not server prefix: if any
loaded tool's name contains the DataForSEO operations this skill uses (e.g.
`serp_organic_live_advanced`, `on_page_instant_pages`,
`dataforseo_labs_ranked_keywords`), DataForSEO is connected — whatever prefix it carries
(a claude.ai connector uses a UUID prefix like `mcp__<uuid>__…`, not `dfs-mcp:`). NEVER
require a specific prefix, and don't run CLI commands (`claude mcp list`) or hunt for the
`claude` binary.

- **DataForSEO tools ARE loaded → the connection is live.** Run one free/minimal
  smoke-test call (e.g. `appendix/user_data`, which also returns balance) to confirm it
  works, then hand off to Stage 1. **Do NOT read `credentials.md`, do NOT ask for any
  credential.** (Quiet balance check: stay silent if healthy; only warn if it's low —
  about $0.50 or less — since Stage 1 makes ~20+ calls.)

- **No DataForSEO tools loaded → fall back to `references/credentials.md`:**
  - **Blank** (no `login`/`password` and no `base64_token`) → not set up. Present the
    two connect options (see Hard rules), have the user set up, restart, verify.
  - **Filled** → confirm "use saved credentials (1) or update (2)". On use, sync the
    file's credential into `.claude.json`, validate with one account-endpoint call
    (show login + balance), and restart if the tools aren't yet loaded. On update, take
    the new credential from the file (see below), validate, sync, restart.

**NEVER accept a credential in chat.** Do not ask the user to paste a login:password or
Base64 token — a pasted token is stored in plaintext in the session transcript, and
Base64 decodes to the raw login and password. To set or update credentials, the user
edits `references/credentials.md` in their editor, saves, and replies Continue. **If a
user pastes a credential anyway, refuse to use it** — tell them to remove it from the
chat, put it in `credentials.md` instead, and rotate it (it's now exposed).

**Hard rules:** two ways to connect — (1, safest) the user installs the DataForSEO MCP
themselves (e.g. `claude mcp add`, or a claude.ai connector), so the skill never reads
the secret; or (2) fill in `references/credentials.md` and let the skill sync it.
**DataForSEO is required** — never invent a "no DataForSEO" / web-search fallback or
borrow another SEO skill's behavior. Never print the credential value. One question per
turn.

---

## Stage 1: SERP Analysis

The research stage and entry point after setup. Takes the user's keyword/topic
verbatim (no keyword research, no metrics), pulls the live top-ranking pages, and
analyzes them. Details: `references/dfs-mcp-tools.md` (endpoints/fields),
`references/excluded-domains.md`, `references/locations.json`, `references/languages.json`.

Ask the three targeting questions ONE PER TURN, then run the analysis.

1. **Keyword/topic.** Take what the user gave verbatim — that exact phrase is what gets
   searched (do NOT break it into sub-keywords or "research" alternatives). If none
   given, ask: "the phrase you want to rank for — e.g. 'best CRM for small business'."
   - **Sanitize before searching** (DataForSEO rules): strip emojis and UTF/special
     symbols, remove commas (ignored anyway), trim to ≤700 chars, and neutralize any
     search-operator prefix (`site:`, `intitle:`, `inurl:`, `intext:`, `define:`, etc.)
     that triggers 5× billing. Show the cleaned phrase back and confirm.
2. **Market (one turn).** Confirm target country + language (which Google market the
   SERP reflects) — "e.g. United States / English." Default **United States (2840) /
   English (en)** if unsure; validate against the bundled lists → `location_code` +
   `language_code`.
3. **Audience (one turn).** Ask who will read the article — separate from market; it
   shapes vocabulary, depth, and angle. "e.g. 'small-business owners new to SEO' vs
   'enterprise IT managers'." Default **general audience**. Thread it through the
   analysis angle, outline depth (Stage 4), and drafting (Stage 5).

**After the audience answer, run everything below in ONE GO — no checkpoints until
the final report. Don't pause between calls.**

4. **Pull the SERP — ONE call.** the DataForSEO **SERP Advanced** tool (live; match by name, any prefix), sanitized
   keyword, **`depth: 20`** (pass depth 20 explicitly; do NOT let it default to 10,
   and do NOT run a second SERP call to get more results — one call only). Gives per
   result: `url`, `domain`, `title`, `description`, `rank_absolute`, plus SERP
   features: **People Also Ask**, **AI Overview** (and its cited sources), and any
   **featured snippet**. Keep the organic items; note the PAA / AI-Overview / snippet
   for the FAQ section.
   - **On 403 / access-denied / insufficient-funds**, stop cleanly — do NOT
     improvise diagnostics. Say plainly:
     > DataForSEO authenticated, but the SERP request came back blocked (403) —
     > this usually means the account needs more balance or verification before it
     > can return live data. Reply **1** to top up / verify at
     > https://app.dataforseo.com/ then have me retry, or **2** to switch
     > credentials (in `references/credentials.md`).
5. **Filter — hard excludes (silent).** Apply `references/excluded-domains.md` hard
   rules to the organic results (by domain + URL). This is mechanical. Do NOT print a
   filtering audit — no numbered list, no strikethrough, no keep/drop commentary. Just
   quietly keep the survivors in Google rank order and continue.
6. **Fetch page structure.** the DataForSEO **Instant Pages** tool (live) for the
   survivors (batch into one call if the tool accepts multiple URLs, ≤5 identical
   domains; otherwise per URL). Pull `meta.title`, `meta.description`, `meta.htags`
   (h1/h2/h3), `content.plain_text_word_count`,
   `content.flesch_kincaid_readability_index`, `internal_links_count`,
   `external_links_count`.
7. **Fetch body content — tiered** (for relevance check + entity extraction), each
   survivor, cheapest-reliable first:
   - **(a) HTTP fetch** the URL (free). Use it if it returns real article content.
   - **(b)** If blocked or thin/empty (common for large, JS-heavy sites), fall back to
     the DataForSEO **`on_page_content_parsing`** tool (renders the page, returns clean text).
   - **(c)** If that fails too, use the Instant Pages technical metrics alone.
   - **Unfetchable is NOT an auto-drop** — big sites are hardest to fetch. Fall through
     the tiers; if all fail, judge from metrics and keep the page unless clearly thin.
   - **Entities come ONLY from the text you actually fetched for that page — never from
     your own knowledge of the brand or topic.** If the fetch was blocked or thin (tier
     c), extract only what's genuinely there; if nothing, the entities line reads
     **"(page could not be fetched)"** — don't backfill. Also drop entities not relevant
     to the topic (a client logo or footer mention shouldn't enter the list).
8. **Filter — soft excludes (silent).** From the body (or metrics as fallback),
   quietly drop **thin** pages (very low word count / no real structure) and
   **irrelevant** ones (decent length but not a real article — pure promo/service
   pages). No keep/drop audit. Keep survivors in rank order.
9. **Finalize the set** in Google rank order:
   - **More than 10** → keep the top 10 (lowest `rank_absolute`); omit the rest silently.
   - **10 or fewer** → use all. The report title uses the ACTUAL count ("Top 10 Pages",
     or "Top 4 Pages" if only 4 survived).
10. **Fetch ranked keywords — capped.** the DataForSEO Labs **Ranked Keywords** tool
    (live), one call per finalized URL, `target` = the FULL page URL, with
    **`limit: 10`** and **`order_by: ["keyword_data.keyword_info.search_volume,desc"]`**
    (top ~10 by volume; without the cap it returns 100+ and errors as "output too
    large"). Capture **BOTH** `keyword` AND its `search_volume` as a mandatory pair —
    never the keyword without its volume, including when a large response is saved to a
    file and re-extracted. Tag each result set with its source URL in the working data
    (the response doesn't echo the `target` clearly) — working data only, not the report.
11. **Present the report** in this exact layout (endpoint/field details in
    `references/dfs-mcp-tools.md`):

    ```
    ## SERP Analysis — Top [N] Pages on "[keyword]"

    **Topic:** [keyword]
    **Market:** [country] / [language]
    **Audience:** [audience]

    ## Per-page breakdown

    **1. [url]**
    - **Google Rank (Absolute):** [rank_absolute]
    - **Format:** [inferred format]
    - **Title:** "[verbatim title]"
    - **Meta:** "[verbatim meta description]"
    - **H1:** "[verbatim]" · **H2s:** "[verbatim]" · **Key H3s:** "[verbatim]"
    - **Stats:** [N] words · Flesch–Kincaid Readability Index [X] · [N] internal /
      [N] external links
    - **Ranked Keywords (Search Volume):** [keyword] ([volume]), … — ALWAYS show the
      volume in parentheses after each keyword (that's the whole point of this line);
      never list keywords without their volumes. Use "none returned" only if the page
      genuinely ranked for nothing.
    - **Entities:** [verbatim terms from the fetched page body; "(page could not be
      fetched)" if the fetch failed — never invented from your own knowledge]

    **2. [url]** … (and so on, in Google rank order)
    ```
    Then the synthesized sections below the per-page breakdown:
    - **Verbatim rule:** titles, H2s, entities, and all SERP questions/phrases are
      quoted EXACTLY as fetched — never reworded, and no "(verbatim)" tag on the
      headers (the exact-quoting is just how it's done, not something to label). Only
      the format label and entity *grouping* are your synthesis.
    - **Keyword targets** (synthesized, **NO volume**): choose ONLY from the pooled
      ranked keywords actually returned across the pages — every target must be a
      real ranked keyword that appeared in at least one page's list (verbatim). Do
      NOT invent keywords or pull them from titles, headings, or entities. The user's
      phrase is usually primary; then secondary and long-tail by how central/recurring
      they are. Editable list.
    - **Entity / topic checklist:** every item must map to a real entity extracted
      from the pages (per step 7 — never from your own knowledge) AND be relevant to
      the user's topic. No invented, topically-guessed, or off-topic additions. Minor
      phrasing variation is fine (e.g. "schema" ≈ "schema markup"), but there must be a
      real counterpart on at least one page. Group items into categories by your
      synthesis (items grounded in the pages, grouping is your layer).
    - **Dominant format:** a recommendation — "For this topic, I suggest a [format]
      because …" with the evidence. If the SERP is split, say so.
    - **Opportunities** — everything in the SERP worth acting on, in this order (quote
      all questions/phrases exactly as fetched; say "none found" for any that are
      absent, don't omit silently):
      1. **People Also Ask** — Google's related questions (fold any "Things to know"
         / related-question panel in here too).
      2. **Top Pages FAQ Opportunities** — question-style headings from the ranked
         pages themselves.
      3. **People Also Search / Related Searches** — the adjacent search phrases from
         the SERP (fold both the `people_also_search` and `related_searches` features
         into this one line).
      4. **Featured Snippet** — the current answer box and which page holds it.
      5. **AI Overview** — a short summary of Google's AI answer plus its cited sources
         (the sources verbatim — they show who's winning the AI answer).
    - **Targets:** word count = **median** competitor `plain_text_word_count` **+10%**
      (median, NOT mean — one outlier shouldn't inflate it). Reading level = pages'
      average readability, as a reference point. No "takeaway" paragraph.
11. **Checkpoint — three options.** After presenting, ask:

    > What next?
    > **1** — Looks good, continue to Stage 2 (Existing-Content Sources — I'll ask for
    > your site's URLs so the article can link to your related pages)
    > **2** — Refine the keyword or entity lists
    > **3** — Start over with a different topic or market

    - **Reply 1** → proceed to Stage 2.
    - **Reply 2 → re-show ONLY the two synthesized lists** (keyword targets + entity
      checklist, not the whole report) and ask what to add or drop. Edit from what's
      shown; **no new API calls.** Then:
      - **Drop** → remove it; don't pad back to a count (a focused set beats a padded
        one). Only if the drop leaves the set thin (primary gone, or 1–2 secondaries
        left), flag it and offer to promote something already in the list.
      - **Add** → add it; don't drop others to compensate. If they pile on many
        secondary targets, nudge toward focusing on ~3–5 (a nudge, not an auto-drop).
      - **Off-topic add** → flag it first ("'[item]' doesn't look related to '[topic]'
        — it could dilute focus; add anyway, or did you mean something more specific?")
        then respect their choice.
      - The lists are a pool to draw from, not a must-use set — final selection happens
        at the outline/draft (Stages 4–5). Re-present and show this menu again.
    - **Reply 3** → discard everything and restart Stage 1 from the top. This is the
      ONLY option that re-runs the API calls.
    - Loop on 2 until the user picks 1. Never auto-advance.

---

## Stage 2: Existing-Content Sources

1. **Stop and prompt.** Ask the user for a path to a local file (sitemap, text
   file, spreadsheet) with their existing URLs, or to paste URLs directly, or to
   skip.
2. Read the input and map semantic matches to find natural internal-link
   opportunities for this article.
3. **Fallback:** if nothing matches semantically, say so and skip internal
   linking — do not force an irrelevant link.
4. → **Checkpoint Protocol.**

---

## Stage 3: Product Integration

Gather products BEFORE the outline, so the structure can accommodate them.

1. **Stop and prompt.** Ask whether the user wants to feature or cross-promote any
   products, services, or lead magnets in the article. Request names, target URLs,
   and core value props. If none, say so and move on — no forcing.
2. Note where each product naturally belongs (which topic/section it relates to), so
   the Stage 4 outline can give it a home. Don't write anchor text yet — that happens
   at draft time.
3. **Fallback:** if a product doesn't fit the topic at all, say so plainly and let
   the user decide whether to keep it or drop it.
4. → **Checkpoint Protocol.**

---

## Stage 4: Outline + BLUF

Formats and rules: see `references/article-format-guidelines.md`.

1. **Confirm the format.** Open with the format Stage 1 detected as dominant in the
   SERP, as a suggestion with the evidence — e.g. "8 of the top 10 are 'best tools'
   listicles, so I'd suggest a **Roundup**." Then offer: use that, pick another
   (Listicle/Roundup, Alternatives, Comparison, Review, How-to Guide, Pillar Guide,
   Answer Post), or **"None of these fit — I'll describe the article I want."** The
   suggestion is evidence-based but the user's choice wins. Read the matching blueprint
   first. If nothing fits, use the **Custom** path in
   `references/article-format-guidelines.md` for this run — don't edit the library file
   (you may suggest once that they add it as a permanent blueprint later, never do it
   automatically).
2. **Build the outline** from the blueprint (formats in
   `references/article-format-guidelines.md`; how to write each section in
   `references/article-template-guidelines.md`). **Treat the Stage 1 SERP analysis as
   the backbone:** cover the entity/topic checklist, target the keyword targets, and
   give each Stage 3 product a home. You may add a section the topic clearly needs, but
   flag any addition beyond the Stage 1 output rather than adding it silently. Force
   the universal sections (per `references/article-format-guidelines.md`):
   the universal sections listed in `references/article-format-guidelines.md`
   (answer-first opener, freshness anchor, E-E-A-T "How We Evaluated" for product
   formats, FAQ, keyword in the final heading, entity coverage). Two reminders that
   matter most here: compute the freshness-anchor year at runtime (`date +%Y`, never
   hardcoded, and skip the anchor if nothing recent+relevant qualifies), and seed the
   FAQ only from REAL Stage 1 Opportunities questions — never invent them.
3. **BLUF.** For every H2, write a one-sentence Bottom-Line-Up-Front thesis the
   section must defend.
4. **Length check.** The Stage 1 target is median competitor length +10%. If the
   outline is pushing the article past ~3,000 words, flag it and confirm with the
   user before committing — depth should match the topic, not pad to a number. Most
   articles land well under this; only genuine pillar/ultimate guides justify 3,000+.
5. **Hard approval gate.** Present the full outline + BLUF targets inline. The
   user must review, edit, or approve. Do NOT write any body text yet.
6. → **Checkpoint Protocol** (this checkpoint is a hard stop).

---

## Stage 5: Article Draft

Canonical style rules: see `references/article-style-rules.md`.
How to write each section: see `references/article-template-guidelines.md`.
Brand voice: see `references/brand-voice/README.md`.

1. **Brand voice — always ask, three options (one line each), wait for the pick:**
   1. **Default voice** — the built-in SEO Content Engine voice (plain, active,
      opinionated, general reader); style rules only.
   2. **Match my writing** — read the user's article links and/or `.md`/`.txt` files
      in `references/brand-voice/` and mirror the voice (rhythm, formality, vocabulary,
      how opinionated, openers/closers). For links, fetch them (tiered: HTTP then
      content-parsing, as in Stage 1). If neither link nor file is available, offer 1 or 3.
   3. **Describe it myself** — the user gives a sentence or two on how it should sound;
      apply those traits while drafting.
   In all three: voice only — never copy facts/products/claims from samples, and the
   style rules always apply on top.
2. **Draft progressively, section by section**, defending each BLUF. Draw keywords
   from the Stage 1 keyword targets and cover the Stage 1 entity checklist. Entities
   may be phrased naturally (minor variation of a checklist item is fine), but don't
   introduce products/tools/concepts that have no basis in the Stage 1 checklist.
3. **SEO positioning (mandatory):** the exact keyword in the first 200 chars of the
   intro, in ≥1 H2 (ideally 2), and in the final section — placed deliberately, never
   stuffed. Full keyword + readability rules: `references/article-style-rules.md`.
4. **Anti-AI guardrails + clean output:** enforce the forbidden words/phrases and
   formatting rules in `references/article-style-rules.md` (the floor, even under a
   brand voice — voice is not a vocabulary license). No placeholder tokens; bold the
   label on any labeled item (rating blocks, step labels, pros/cons).
5. **Auto-inject links:** internal links from Stage 2 and product anchors from Stage 3,
   using natural anchor text. **For roundups, alternatives, comparisons, and reviews,
   link each tool/product to its official page** on first mention (tool name as anchor)
   — readers want to click through. These are official-source links, not competitor
   article pages.
6. **Draft the meta title + meta description** (specs in
   `references/article-template-guidelines.md`, section 10) and show them with the
   draft for review — not part of the article body; confirmed at Stage 8.
7. → **Checkpoint Protocol.**

---

## Stage 6: Fact Check + Quality Audit

A hybrid audit: a script handles the countable checks, your reasoning handles the
judgment ones. There is no A/B choice — run both.

1. **Countable checks (script).** Run the linter over the draft:
   ```bash
   python scripts/lint_article.py <draft.md> --keyword "<primary keyword>"
   ```
   It reports forbidden words/phrases, readability signal, keyword positions, and
   word count against the target band.
2. **Judgment checks (reasoning).** Does each section deliver on its BLUF? Does it
   read naturally? Is it structurally complete versus the Stage 1 entity checklist?
3. **Claim verification.** Find candidate hard claims:
   ```bash
   python scripts/extract_claims.py <draft.md>
   ```
   For each stat, percentage, price, rating, or date it flags:
   - Verify it against a **credible source** — the producer/owner of the fact (e.g.
     Statcounter for market-share data, a vendor's own page for its pricing), official
     docs, .gov/.edu, peer-reviewed research, recognized industry research, or
     established news. The test: is this source the *producer* of the fact or just
     repeating it? Cite the producer. Never accept forums, content farms, undated
     blogs, or AI-generated listicles.
   - **Copy values exactly as the source states them — including currency, unit, and
     billing basis.** A price claim is the number PLUS its currency ("$20" ≠ "€20"),
     its unit (per user / per seat / per month), AND its billing basis (billed monthly
     vs. billed annually) — "$24/mo billed monthly" and "$20/mo billed annually" are
     both true and different. NEVER convert a currency, and never swap monthly for
     annual (or vice versa) as a "correction" — that replaces a true number with a
     different true number. State the basis so the figure is unambiguous; if the vendor
     lists both, quote both or keep whichever basis the draft used. Same exactness for
     units, dates, and ratings.
   - **Write the result back into the draft**, not just the report:
     - Wrong number OR wrong currency/unit → correct it in the draft to what the source
       actually says.
     - **Add the source as an external link** on that stat — a verified stat must not
       sit unlinked (this is where external links come from).
     - Can't verify → **soften** it ("many teams", not a fake "73%"); delete only if
       softening fails.
   - **External links** go to credible sources for verified stats and official pages
     for tools/docs the article names. NEVER link the top-X competitor pages. Not
     mandatory — add only where they add authority.
4. **Fix loop.** Apply fixes → re-run the linter → repeat until it passes:
   0 forbidden words/phrases and all three keyword positions satisfied. The
   readability grade is reported as a signal — review it against the Stage 1
   audience, but it does not block the gate. Do not proceed until the gate is green.
5. **Present** the draft alongside the validation report inline. The validation table
   holds only pass/fail quality checks — do NOT put link counts in it. After the
   table, add ONE informational line (not a gate): "Links: [N] internal, [N]
   external." If internal links are 0, add the reason: "No internal links — you
   skipped the existing-content step (Stage 2), so there were no site pages to link
   to. Add URLs there if you want internal linking." Then ask for line-by-line
   feedback or stylistic adjustments. → **Checkpoint Protocol.**

---

## Stage 7: HTML Preview

1. Compile the finalized markdown into a clean, standalone, mobile-responsive
   HTML file using `assets/preview.template.html` as the shell.
2. The template already styles the body, the summary block, and product callouts
   distinctly. Fill in the placeholders; don't hand-roll new CSS.
3. **Label the summary block to match the article's tone** (the markdown article stays
   label-free — this label is preview-only, set via the `summary-label` span):
   - Professional tone → "The Bottom Line" or "Executive Summary"
   - Modern business tone → "In Brief" or "Quick Summary"
   - Tech / startup audience → "TL;DR"
4. Tell the user the preview is ready and where it is.

---

## Stage 8: Final Export

1. **Build the base filename** — a short, filesystem-safe slug from the topic plus the
   article format, so files on the same topic in different formats don't collide:
   `[short-topic-slug]-[format]`. The short-topic-slug is the keyword trimmed of stop
   words (not the full title); the format is one of `roundup`, `alternatives`,
   `comparison`, `review`, `guide`, `pillar`, `answer`. Lowercase, hyphens only, strip
   anything that isn't a letter/number/hyphen, cap the length sensibly. Example:
   `ai-automation-small-business-guide`.
2. Write three files to the user's project root, all sharing that base name:
   - `[base].md` — clean final markdown
   - `[base].html` — the rendered preview
   - `[base]-meta.txt` — the meta title and description in plain text, each on its own
     line with its character count (format/example in
     `references/article-template-guidelines.md`, section 10).
3. **Also show the meta title and description in chat** (drafted at Stage 5) for quick
   review.
4. Confirm the exact file paths so the user can push straight to their CMS or static-site
   generator, and remind them the meta goes in the CMS's meta fields (or a plugin like
   Yoast/RankMath), not the article body. (The filename includes the format for local
   clarity; the URL slug in the meta doesn't need the format tag — different purposes.)
