# DataForSEO Tool Reference

**Important:** match DataForSEO tools by **name, not by server prefix.** The tools may
be exposed under any prefix — a claude.ai connector uses a UUID prefix
(`mcp__<uuid>__serp_organic_live_advanced`), a CLI-added server uses its own name. So
identify each tool by the operation in its name (e.g. `serp_organic_live_advanced`),
whatever precedes it, and call it with its full actual name as loaded. NEVER hardcode or
require a `dfs-mcp:` prefix — that will fail against a connector. The names below are the
**expected operations**; verify against the actually-loaded tools at runtime and pick the
closest match by function if a name differs.

This skill uses DataForSEO for **SERP analysis only** — it does NOT do
keyword research and pulls NO keyword metrics (no search volume, difficulty, CPC,
or intent). The user's keyword/topic is taken verbatim and used to fetch and
analyze the live top-ranking competitors.

## Which endpoints Stage 1 uses

Four calls, in sequence:

- **SERP API (Advanced)** — the live top-ranking results (organic URLs) plus SERP
  features: People Also Ask, AI Overview + its cited sources, and featured snippet.
- **OnPage Instant Pages** — per-page structure (word count, headings, readability,
  link counts), one batched live call.
- **OnPage Raw HTML** — the stored page HTML as one text blob, for reading the body
  (format confirmation + entity extraction).
- **DataForSEO Labs Ranked Keywords** — the real keywords each page ranks for, one
  call per finalized URL.

## Step A — SERP pull (expected tool)

- `serp_google_organic_live_advanced` (by name, any prefix)

Request essentials:
- `keyword` — the **sanitized** user phrase (see Keyword sanitization below).
- `location_code` + `language_code` — from `references/locations.json` /
  `references/languages.json`; default United States (2840) / English (en).
- `depth: 20` — pass explicitly, ONE call only. Do NOT let it default to 10 and do
  NOT run a second SERP call for more results (~2 billable SERP units).

From the response (filter on your side):
- Keep `type == "organic"`. Also capture People Also Ask, AI Overview (+ cited
  sources), and featured snippet for the FAQ section.
- Apply `references/excluded-domains.md` (hard by domain/URL; soft judged from
  URL+title) BEFORE any fetch, so junk never reaches the paid calls.
- Drop clearly off-topic titles. Keep survivors in Google's rank order.
- Carry each survivor's `rank_absolute` to the report. (Provisional: it includes
  ads/features, so filtered results leave gaps — drop after live testing if
  confusing.)
- Capture all SERP features for the Opportunities section: People Also Ask (+ any
  "Things to know" panel), People Also Search / Related Searches, Featured Snippet, and AI Overview (+
  cited sources). Say "none found" for any that are absent.

## Step B — Instant Pages (expected tool)

- `on_page_instant_pages` (by name, any prefix)

Batching: ≤20 URLs per request, ≤5 identical domains. Per page read: `url`,
`meta.title`, `meta.description`, `meta.htags` (h1/h2/h3),
`content.plain_text_word_count`, `content.flesch_kincaid_readability_index`,
`internal_links_count`, `external_links_count`.
Post-fetch, drop thin pages (very low word count / no heading structure).
Do NOT use `onpage_score` — it's technical health, not content quality.

## Step C — body content, tiered (for relevance + entity extraction)

Get each survivor's article body, cheapest-reliable first — do NOT use a raw-HTML
endpoint (we never surface it and it's messy):
1. **HTTP fetch** the URL directly (free). If it returns real article content, use it.
2. **If blocked / thin / empty** (common for large, JS-heavy, bot-protected sites) →
   `on_page_content_parsing` (live) — it renders the page and returns clean
   article text.
3. **If that also fails** → use the Instant Pages technical metrics (word count,
   headings, readability) alone.
**Unfetchable is never an auto-drop** — big authoritative sites are the hardest to
fetch, so fall through the tiers and only judge on technical metrics as a last resort.

## Step D — Ranked Keywords (expected tool)

- `dataforseo_labs_google_ranked_keywords` (by name, any prefix)

One call per finalized page URL. Set `target` = the FULL page URL (with `https://`)
to get keywords for that *page*, not the whole domain. `location_code` +
`language_code` as above. **Cap the response** with `limit: 10` and
`order_by: ["keyword_data.keyword_info.search_volume,desc"]` so each call returns
only that page's top ~10 keywords by search volume. Without the cap it returns 100+
keywords and errors as "output too large". Capture `keyword` AND
`keyword_data.keyword_info.search_volume` together as a pair for every keyword —
never the keyword without its volume; drop the other fields.

## Report format (Stage 1 output)

**Verbatim rule:** titles, H2s, entities, and FAQ/PAA questions are shown EXACTLY as
fetched — never reworded. Only the format label and the entity *grouping* are your
synthesis; everything quoted must match the source.

Per page (Google rank order):
- `rank_absolute`, detected format, title, meta description, h1 + key h2s, word
  count, readability, internal/external link counts
- **Ranked keywords:** Keyword A (volume), Keyword B (volume), … — the volume in
  parentheses is REQUIRED on every keyword (capture keyword + search_volume as a pair;
  don't drop the volume when extracting from a saved response).
- **Entities:** product/tool/brand/price/tech names taken ONLY from the fetched page
  body (never from your own knowledge); "(page could not be fetched)" if the fetch
  failed. Drop off-topic mentions.

Then synthesized (aggregated across pages):
- **Keyword targets:** primary / secondary / long-tail — a clean list, **NO volume**
  (so user-added keywords look uniform; we can't fetch metrics for new ones)
- **Entity / topic checklist:** recurring entities — a clean list
- **Dominant format** (recommendation with the why), then **Opportunities** (People
  Also Ask, Top Pages FAQ, Related Searches, Featured Snippet, AI Overview + cited
  sources), then **targets**: word count = **median** competitor word count **+10%**
  (median, not mean); reading level = pages' average readability as a reference.

## Keyword sanitization (before any SERP call)

DataForSEO's keyword field has rules; clean the user's phrase first:
- Strip emojis and UTF/special symbols (they cause errors or bad data).
- Remove commas (DataForSEO ignores them anyway).
- Trim to 700 characters max.
- Neutralize search-operator prefixes that trigger 5× billing if present as
  operators: `allinanchor:`, `allintext:`, `allintitle:`, `allinurl:`, `cache:`,
  `define:`, `filetype:`, `id:`, `inanchor:`, `info:`, `intext:`, `intitle:`,
  `inurl:`, `link:`, `site:`.
- A keyword can't consist solely of these: `< > | \ " - + = ~ ! : * ( ) [ ] { }`.
After cleaning, show the user the sanitized phrase and confirm it still matches
their intent before searching.

## Deriving the analysis (Claude, from the two calls above)

- **Entity/topic checklist** — products, tools, brands, and subtopics recurring
  across competitor titles + headings; the coverage checklist for the article.
- **Structure** — common heading patterns → the outline skeleton to match or beat.
- **Word-count target** — average competitor `plain_text_word_count` + 10%, no cap.
- **Reading level** — average competitor readability as a target reference.

## Error handling

- **Auth / 401 (or `status_code` 40101):** credentials are wrong or expired. Send
  the user back to the Option 1/2 setup in `references/setup.md`.
- **403 / access-denied / insufficient-funds:** the login is valid but the account
  can't fetch this data yet — usually a fresh or low-balance account that needs
  funding or verification. Stop cleanly and offer the retry / switch-credentials
  choice (see Stage 1 in SKILL.md). Do NOT improvise diagnostic commands.
- **Validating credentials:** always test against the account endpoint
  `https://api.dataforseo.com/v3/appendix/user_data` (free, returns 20000 for any
  valid login and includes `money.balance`). Do NOT validate against SERP or
  OnPage endpoints — those can return 403 on a low-balance account even when the
  credentials are correct.
- **Empty SERP:** the keyword may be too niche for the chosen market, or the
  location/language pairing is off. Confirm the market and try a broader phrase.
- **Instant Pages 40501 (duplicate crawl host):** don't send the same domain twice
  while a prior task on it is still queued; split domains across requests.
- **Tool not found:** the module may be disabled on the server. List available
  the loaded DataForSEO tools and adapt.
