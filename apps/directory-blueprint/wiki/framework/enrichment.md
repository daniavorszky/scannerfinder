---
title: Enrichment (Gate 3)
type: framework
status: draft
updated: 2026-09-30
---

# Enrichment (Gate 3)

"Enrichment is what makes a list into a tool." A raw scrape is a phone book. Attributes and a description per listing turn it into something a buyer uses and Google can distinguish.

## Method (from the video, adapted)
For every kept listing, the LLM reads what is available (`reviews_tags`, `about`, `subtypes`, `description`, `posts`, the website title/description if the enrichment columns exist) and answers each attribute in the vertical's attribute set with exactly one of **true / false / not enough info**. Never guess. "Not enough info" is displayed on the page as such.

Sources the video names for the attribute list: Google Maps review tags, Reddit threads in the niche, Ahrefs modifiers. Our cheaper checklist for building the list: the 7-part modifier taxonomy (material, urgency, scope, equipment brand, property type, condition or age, problem-based).

## When the export has no text (found on the pilot, 2026-09-29)
The Florida pool builders export came back with `reviews_tags` and `posts` empty on every row and `description` on 11 of 1,848. Outscraper's default pull does not always carry them. When that happens the listing's own website is the source:

1. `scripts/fetch_sites.py` reads the home page and up to three internal pages (services, about, install, repair, financing, warranty, pricing; add the vertical's own words with `--want "new-?pool|enclosure|spa"`) into `03-cache/sites/`. No API, no cost, no package to install. Social and profile links are not read.
2. `scripts/build_evidence.py` pulls at most two short quotes per attribute from those pages, using the `pattern` of each attribute in the per-vertical file (`--patterns output/<slug>/03-attributes.json`; every attribute needs one, and `merge_enriched.py` refuses to run when one is missing), and writes one evidence file per city into `03-cache/evidence/`. It finds quotes; it does not answer anything.
3. The LLM answers each attribute from the packet (Maps fields, site title, headings, menu, quotes). **true** needs a quote or a heading that says it. **false** needs the site to say so, or a full service list that leaves it out where it would plainly belong (a leak detection company's menu with no construction page is `new_pool_construction: false`). Everything else is **not enough info**. A listing with no readable site gets "not enough info" across the board unless Maps data answers it.

4. `scripts/make_batches.py --attributes 03-attributes.json` cuts the packets into batches of about 40 listings that skip anything already answered, and prints the vertical's attribute table (key, what a true needs, which key is core work) at the top of each batch. Each batch is answered under the general `scripts/enrichment-instructions.md` and written to `03-cache/enriched/`, either as subagents or through `scripts/run_batches.py enrich --slug <slug>`, which starts one headless Claude Code run per batch (on Sonnet unless `--model` says otherwise), checks it and reruns a failure with the checker's lines. It holds `03-cache/runner.lock` while it runs, so a second start on the same directory refuses while the first is alive (a stale lock from a dead process is cleared), and it prints one summary line at the end (batches passed and failed, listings answered, reported cost, cents a listing, wall time) for the report.
5. `scripts/merge_enriched.py` checks every answer (valid values, a trace behind every true, word band, no dashes, no banned words, no opener shared by four or more listings across the run) and writes `03-listings-enriched.csv` only when nothing fails. The opener tally covers every answers file already in the cache plus the batch being checked, so a single-batch check (`--only`, what the runner uses) sees the other batches' openers but fails only its own listings; the full merge names the slugs and batches to rerun with `run_batches.py --only`.

The cost gate prices step 3 from the real packet sizes, after steps 1 and 2 have run.

**Measured on the pilot (1,848 listings, 2026-09-29):** 138,000 tokens per batch of about 37 listings when run as subagents on Sonnet 5.5, about 3,800 tokens per listing, 7.05 million in total. The first estimate of 2.8 million counted one read and one write per batch and missed that an agent re-reads its context on every step. Quote 4,000 tokens per listing for this method.

**Measured on the dry run (368 listings, fence contractors, Colorado, 2026-09-30):** through the headless runner, 349 listings on Sonnet cost $14.00 as reported by `claude -p`, 4.0 cents a listing, three runs at a time, 25 minutes of wall time; the two batches run on the account's default model cost 16 cents a listing with the same pass rate. The runner defaults to Sonnet for that reason. The cost line quotes both figures: 4,000 tokens a listing on subagents, 4 cents a listing on the runner.

**Description bands used on the pilot:** 120 to 200 words when quotes exist for three attributes or more, 80 to 200 for one or two, 50 to 90 for none. The Blueprint's single 120 to 200 band made writers pad thin listings.

## Attribute set, per vertical
One JSON file per vertical (`output/<slug>/03-attributes.json`) with 8 to 15 attributes, written at Gate 3 for the member's vertical, in the shape `scripts/examples/README.md` describes: each attribute carries `key`, `label`, `faq`, `true_when` (one line saying what the business's own words must state) and `pattern` (the regex `build_evidence.py` and `merge_enriched.py` use). This is the only vertical-specific file in the pipeline; the instruction files are general. `scripts/examples/attributes-pool-builders.json` is one run's file, kept as an example of the shape and not a recommendation.

When the Maps category is broader than the vertical (Google's "swimming pool contractor" category also covers cleaners, repairers and unrelated trades; 259 of 1,848 came back as not builders on the pilot), one attribute may carry `core: true` to record whether the business does the vertical's core work at all. The description then says what the business does instead. What the directory does with those listings (an exclusions row, a `sortAttribute`, or nothing) is a Gate 4 decision for the member; dropping them was one pilot's choice in one industry and is not a Blueprint default (Shawn, 2026-09-29). A license attribute is worded "states a contractor license": the directory reads the claim and does not verify it.

## Description
120 to 200 words, one voice, plain, from the data only. States what they do, where, what stands out in the tags, and the attribute answers in prose. No superlatives that the data does not support. No em dashes.

When there are no quotes (the 50 to 90 word band) the description never says the business "is listed on Google Maps" and never names where the data came from; it opens with what is specific to this business (its name and city, what its Maps category and any Maps phrases say it does), so two such descriptions do not share an opener. The dry run's 17 identical openers all came from that band (2026-09-30).

## Cost gate
Before running: count listings, estimate tokens per listing, state the projected cost in one line and wait for approval. Batch by city, cache results in `03-cache/`, so a rebuild never re-enriches unchanged rows.

## Output
`03-listings-enriched.csv` (clean columns + one column per attribute holding `true`, `false` or `not enough info` + `description_enriched`; the raw Outscraper `description` column is kept untouched) and `03-attributes.json` (the attribute set with display labels and the FAQ question each attribute can answer, e.g. `financing_offered` feeds "Which pool builders in [city] offer financing?"). The Astro skeleton (`templates/astro/`) reads exactly these: attribute columns named by the `key` in `attributes.json`, and `description_enriched` with `description` as the fallback.

## Gate 3 report (added 2026-09-30)
`03-enrich-report.md` is written by hand at the end of the gate and states: the input rows from Gate 2; the attribute file, its count and which key is core work; the website fetch outcome by status (the summary line `fetch_sites.py` prints: readable, no website, blocked, dead, script-rendered, other); the evidence size and the batch count; the runs, with how many passed first time and how many needed a retry; cost and time (the runner's summary line: batches passed and failed, listings answered, reported cost, cents a listing, wall time); the attribute tallies from the merge (true / false / not enough info per key); the thin count before and after the merge; and every warning left in place, with why.

## See also
[[listings-cleaning]] · [[page-types]]

## Social profiles (added 2026-09-30)
The Outscraper basic export carries no social links; they sit in its paid enrichment add-on. The Blueprint takes them from each business's own website instead: `scripts/fetch_sites.py` keeps the Facebook, Instagram, X, LinkedIn, YouTube, TikTok and Pinterest profile links it meets on the pages it reads (share, login and post links skipped), and `--socials` adds them to an existing cache by reading each home page once more. `scripts/add_socials.py` writes them into the listings CSV as a `socials` column; the listing page shows them as icons under Contact, `nofollow` unless the listing is optimized, and lists them as `sameAs` in the LocalBusiness schema. A profile the site does not link is not shown; nothing is searched for.

## Description voice (2026-09-30)

A description states what the business does, offers and states about itself as plain facts, in third person, and never names where the fact came from: no "its site says", "according to its website", "the footer lists", "its listing", "on Google Maps", and no sentence about what the site does not say. The honesty layer is on the page already (the "no information yet" line under the attribute grid, the "compiled from public sources" foot line, the disclaimer card). The rating sentence may name Google reviews as the unit. The evidence rule is unchanged: every statement traces to the packet, and `merge_enriched.py` fails a description that names its source. The same rule applies to city copy (`check_city_copy.py`). Decided by Shawn on 2026-09-30 after feedback on the live pilot's Romance Pools page; the pilot's own descriptions predate it.
