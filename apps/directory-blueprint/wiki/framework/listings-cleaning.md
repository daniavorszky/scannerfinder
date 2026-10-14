---
title: Listings Cleaning (Gate 2)
type: framework
status: current
updated: 2026-09-30
---

# Listings Cleaning (Gate 2)

Most of what a scrape returns is junk. From 100k+ raw rows the video keeps 5 to 6%. The rules are deterministic and live in `scripts/clean_listings.py`; this page is the specification the script implements. The numbers quoted from the Florida pool runs and the Colorado fence dry run are illustrations from one run each, not targets for any vertical.

## Rules, in order
1. **State filter.** Keep rows whose `state_code` equals the target state. Outscraper category pulls leak across borders.
2. **Drop closed.** `business_status` must be `OPERATIONAL` (drop `CLOSED_PERMANENTLY`, `CLOSED_TEMPORARILY`).
3. **Zero reviews out.** `reviews` must be greater than 0. (Video rule: "remove rows with zero reviews.")
3b. **Freshness (DataForSEO input only).** Drop rows whose `last_updated_time` is older than 365 days (`--max-age-days`). The Listings database has no closure flag, so staleness stands in for it. The 12-month cutoff is general, a database staleness proxy, not tuned to any vertical; one run's illustration: in the Florida pool comparison it removed 72 closed businesses and 109 listings gone from Maps while costing 12 open ones, and on the Colorado fence dry run (2026-09-30) it dropped 22 of 398 rows, two of them fence companies with 27 and 42 reviews. A member who wants those back sets `--max-age-days 0` and accepts the closed ones with them.
4. **Name must contain the niche, or the row carries the category.** Case-insensitive match of any of the niche terms against `name`, **or** `type`/`subtypes`/`category` contains the target Maps category (`--category`). The niche terms are the words businesses put in their names for this trade, plural and singular, never the broad product word: for a swimming pool contractor directory that is `--niche "pool builder,pool builders,pool construction,custom pools" --category "swimming pool contractor"`, for fence contractors `--niche "fence,fencing,fences" --category "fence contractor"`. Check the terms against a few names in the raw file before running (`pool` alone kept cleaners, supply stores and public pools on the pilot). The video says "names must contain whatever's in your niche"; the category fallback keeps "Blue Haven" style brands that are clearly in category. The fallback also keeps rows that carry the category only as a secondary one (on a DataForSEO pull every row carries it somewhere, so nothing is filtered out by this rule); the report counts those rows and their primary types, and whether they stay is the member's Gate 4 decision, never a Gate 2 drop (no default drop of any listing class; Shawn, 2026-09-29).
5. **Dedupe.** First on normalized `phone`, then on normalized `address` + `postal_code`. Keep the row with more reviews.
6. **Flag owned.** Rows whose phone matches `--owned-phones` get `owned=true`. They are **kept and treated like any other listing**; the flag exists only so the report can show them and so nobody accidentally gives them special treatment ([[footprint-rules]]).
7. **Thin flag.** `reviews < 5` or no description text gets `thin=true` (used by [[launch-lean]], not dropped). The text test reads `description`; `about` counts only when it is prose, and an `about` value that parses as JSON is Google's attribute data, not text ([[outscraper-columns]]; the DataForSEO pull writes JSON there on every row, Outscraper on most). On the Colorado fence dry run this flagged 129 of 368 rows, 38 of them for an empty description alone. The flag is provisional: Gate 3 clears it for a listing with five or more reviews once its own website gave real text (`merge_enriched.py`), so a strong business with an empty Maps description is not held out of the sitemap for that.

## The report (`02-clean-report.md`)
Rows in, rows after each rule, final keep rate, how many cities clear the 3-listing floor and how many kept rows those cities hold, owned rows found, thin rows, domains written, then three lists: the kept rows by `type` (primary Google category), the rows kept only by the category fallback (name and primary type did not match) with their top primary types, and the cities with counts. On an Outscraper export a keep rate outside 2 to 25% is flagged; the niche terms are probably wrong. On a DataForSEO pull the keep rate is high by construction (the pull is filtered by category before it arrives; 92.5% on the Colorado fence dry run) and says nothing about the terms; read the type lists instead.

## Output columns
The script keeps the columns listed in [[outscraper-columns]] under "used by the pipeline" and adds `slug`, `city_slug`, `owned`, `thin`, `featured` (empty), `claimed` (empty).

## The domains file (`02-domains.txt`)
One website domain per line for every kept row (1,320 of 1,819 on one Florida pool pull, 261 of 368 on the Colorado fence dry run). It exists for the Outscraper path, where the raw export carries no emails: the member uploads this file to Outscraper's Emails and Contacts scraper ($3 per 1,000 domains after 500 free, checked 2026-09-29), about $5 for a cleaned state instead of paying for every junk row of the raw export. The DataForSEO path already carries web-sourced emails (573 of 2,350 rows on the Florida pull). Either way an address gets a domain check and a bounce test before the claim flow sends anything ([[refresh-and-upkeep]]). Emails never appear on a page.

## See also
[[outscraper-columns]] · [[enrichment]]
