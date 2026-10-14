---
title: Page Types and Required Contents
type: framework
status: draft
updated: 2026-09-30
---

# Page Types and Required Contents

| Page | Purpose | Required contents and floors |
|---|---|---|
| **Home** | State-wide answer to "[niche] in [state]" | **800 to 1,500 words as built** (linted on `dist/index.html`, [[copy-gate]]): what the directory is, how listings are vetted, top cities grid with counts, featured businesses block, how to choose a [niche] (the buyer's guide, 400 to 600 words), FAQ block (5 to 8), claim + featured CTAs. The master template's structure alone (city cards, stat row, search labels, hero promises, vetting steps) is about 300 words in the built page, so the old 1,200 cap could not hold a 600-word guide and an 8-question FAQ at once (dry run, 2026-09-30: 1,516 words on the first build); the written copy is still about 800 to 1,200. |
| **State hub** | Complete city index | 300 to 500 words intro, every city with its listing count, featured block, FAQ block (3 to 5). |
| **City page** | The money page: "[niche] in [city]" | **500 to 800 words** of real local copy (not swapped-city boilerplate): what matters for this service in this city (climate, permits, typical price range from the enriched data), then the listing cards (featured first, then paid `best_of_rank` positions, then by rating x review count; the city page **is** the "best [niche] in [city]" list, [[monetization-slots]]), then a **local FAQ block of 4 to 6 questions** built from the attribute data, shown as visible text, never an accordion (the "4,800 city pages with local FAQs" feature), nearby cities, claim CTA. Minimum **3 listings** to get a page; cities under that fold into the nearest city with a page. |
| **Listing page** | One business | NAP, hours, rating and review count, the attribute grid (true and false as tiles, the "not enough info" ones folded into one muted line, decided 2026-09-30), the enriched description (120 to 200 words), map link, website link (nofollow unless featured), links to the service pages it appears on, "Other [niche] in [City]" with four listings from the same city, "Is this your business? Claim it", a one-line disclaimer (public sources, not an endorsement, verify licensing). Two states: **basic** (unclaimed: no photos, no social links) and **optimized** (claimed premium or featured: owner-supplied photos, every link followed, embedded map, hours, badge). Pages with fewer than 5 reviews **or** no description are **thin** and ship `noindex` at launch ([[launch-lean]]). |
| **Service page (optional)** | Statewide answer to "[service] [niche] in [state]" | `/services/[slug]/`, built for each attribute that carries a `service` block in `attributes.json` and that at least the city floor of listings confirm. H1 "[Service title] in [State]", key facts (count, cities, date), an intro of **80 to 200 words** written at Gate 5 from the data and the fact sheet (linted on the built page as 140 to 270 words, the structure being about 60; [[copy-gate]]) (what the service is, what to ask; no prices without a source), the top listings as cards by rating x review count (up to `maxCardsPerCity`), then every city with its confirmed count linking to the city page, then the other services. Which attributes get a page is the member's decision at Gate 4: only something people search for as a service, never a trust mark such as a license or a warranty. Indexed, in the sitemap, linked from the home page, the footer and every listing confirmed for it. Added 2026-10-05 after a member's build showed the gap. |
| **Claim** | Conversion | Under 300 words. The form from `templates/claim-form.html`. What claiming gives you (edit details, add photos, respond), what it costs (free). |
| **Featured** | Conversion | Under 400 words. The three tiers from `templates/featured-tiers.md`, what each buys, Payment Link buttons, "we only feature one business per city per tier" scarcity rule. |
| **About** | Trust for the cold call | The publisher front and center: photo, bio, why this directory exists, how listings are vetted, optional video ([[publisher-entity]]). 300 to 500 words. Emits `Person` schema. |
| **Contact / Privacy / Terms** | Realism | Standard copy. Contact must carry a real email and the correction and removal route ([[refresh-and-upkeep]]). |
| **Resource page (optional)** | Links | `/resources/[slug]/`. The most in-depth page on one topic in one place: hotlines, state rules and licensing, local stats, what realtors say, with sources. 1,200 words or more, bylined, dated. Built only when the member names the topic; exists to be linked to by the Chamber of Commerce, associations and city sites ([[authority-and-links]]). |

## What the pilot changed (2026-09-29)
- **City word floor by size.** A page with three listings cannot carry 500 honest words. Pilot floors, approved at Gate 4: 500 words with 10 listings or more, 380 with 5 to 9, 250 with 3 or 4, and 120 for a small-town page with 1 or 2 listings kept by `foldMaxKm` (indexed like any city page, 2 to 6 FAQs; Shawn, 2026-09-29). The ceiling stays 800. The four size classes, which both checkers apply (`lint_copy.py --city-sizes` from the listing counts, `check_city_copy.py` from the packet's band line, both through `lint_copy.faq_band`):

  | Listings on the page | Words | FAQs |
  |---|---|---|
  | 10 or more | 500 to 800 | 4 to 6 |
  | 5 to 9 | 380 to 800 | 4 to 6 |
  | 3 or 4 | 250 to 800 | 4 to 6 |
  | 1 or 2 (town page kept by `foldMaxKm`) | 120 to 800 | 2 to 6 |

  `lint_copy.py` marks each small city in its report; `make_city_packets.py` prints the band on every packet. Before 2026-09-30 `lint_copy.py` applied 4 to 6 FAQs to every page and failed 19 of the dry run's 21 town pages that `check_city_copy.py` had passed.
- **The export holds no prices and no permit data.** City copy states neither. Law, licensing, permits and weather come only from a sourced fact sheet written at Gate 5 (`05-fact-sheet.md`), and a city uses at most one item from it.
- **The reader never sees how the directory was made.** No "the packet", no "attribute", no website error codes, nothing about search engines. Both checkers fail on it.

## City copy is about the place (decided by Shawn, 2026-09-30)
The pilot's first city intros read as an inventory of the listings: how many "say" they remodel, how many "state" a license, whose website "did not load", what is "on record". That is the directory describing its own enrichment, and it is worth nothing to a homeowner or to search. The rule from now on:

- **Subject: the town, in relation to the trade.** Write about having the trade's work done in *this* place (a fence built, a roof replaced, a pool installed, whatever the vertical is): which parts of the area the businesses serve, which materials and kinds of work the local trade leans toward, which neighboring towns share the page, the county and its permit office when the fact sheet names it, the terrain, the soil, the weather exposure or the housing stock when a sourced fact says so. A reader from that town should recognise it; a reader from the next town should notice the difference.
- **Unique to the place.** No sentence may work with the city name swapped. The shared-sentence check in `check_city_copy.py` enforces the letter of this; the writer enforces the spirit.
- **Sources only.** Every local statement comes from the packet (service areas, towns, counties and specialities the businesses themselves name) or from a sourced fact sheet. The fact sheet may carry a per-city section (`05-fact-sheet.md`, or `05-city-facts.json` when there are many): the county building department, a local ordinance, a flood or coastal designation, each with its source. Without a source, a local fact is not written. A short honest intro beats an invented one, which is what the word floors by size are for.
- **Never written:** tallies of what listings "say", "state", "mention" or "have on record"; counts of listings with "no answers" or "nothing on record"; whether a website loaded, could be read, or exists; "this directory has not checked"; how the page is ordered; the words "listing" and "listings" as the subject of a sentence. `check_city_copy.py` rejects these. Businesses are named for what they do in the town, not for what their website says or fails to say.
- **Numbers, sparingly.** The count on the page, a named business's rating and review count where it tells the reader something, the nearby towns. Not a census of attributes.
- **FAQs** follow the same rule: questions a homeowner in that town would ask (who does the specialty work here, who covers the outlying area, who takes repairs as well as new work, which nearby towns have their own page), answered from the packet and the fact sheet, never "how many listings mention X".

The pilot's 134 intros were written under the old instruction and are out of policy; rewriting them is a Gate 5 rerun of the city batches (2.44 million tokens on Sonnet last time) and waits for Shawn's go.

## Copy rules
- Peer-to-peer, plain, no hype, no em dashes (house rule).
- Every number on a page comes from the data (review counts, price ranges, hours). No invented testimonials, no invented "verified" badges. "Not enough info" is an acceptable attribute value and is displayed as such.
- One H1 per page. City page H1 = "[Niche] in [City], [ST]".
- Facts live in visible text. No accordions, no tabs, no "read more" for FAQs, hours or attributes (the freshness rule).

## Image policy
- Unclaimed listings ship **no photos**. Outscraper does not return usable photos, Google photos may not be hotlinked, and copying from a business's social profile is a copyright exposure the member would carry. Some operators do it with an overlay; the Blueprint does not.
- Photos arrive with a claim or a paid tier, supplied by the owner. That gap is part of the upsell.
- City and home pages use member-owned or licensed stock imagery, not listing photos.

## See also
[[site-architecture]] · [[enrichment]] · [[page-sections]] · [[design-seed]] · [[monetization-slots]]
