---
title: Directory Overview
type: framework
status: draft
updated: 2026-09-28
---

# Directory Overview

**A directory is a curated list optimized for on-page SEO.** Home, state pages, city pages, listings. Same intent as a microsite at a larger scale: "pool builders near me" / "pool builders in Florida" / "pool builders in Orlando".

## Why build one (in this order for Academy members)
1. **Boost a vertical you already own.** Microsites in Orlando, Naples and Miami plus one Florida directory means you hold the SERP three ways (microsite, directory, GBP anchor). See [[footprint-rules]] for what that does and does not allow.
2. **Rent the top spots.** Featured listings, premium badges and best-of placements. See [[monetization-slots]].
3. **Get clients from it.** Every listing is a business you now have a reason to call: "we're connected because you have a listing on my directory." For operators in the community who run directories, they are the number one source of SEO clients, and one operator gets one to two audit requests a day cold-calling off a single directory. It is also the showcase: a directory can earn its keep with half its listings deindexed, because it exists to get clients and to show them what you do.
4. Sell leads. Display ads are out at this size (Ezoic wants about 250k visitors a month).

## What a compliant directory looks like
- One niche, one state. Boring, high-ticket local service.
- Category-shape `.com` domain, `[state][niche].com` (the sample shape is `floridapoolbuilders.com`; an example, not a pick), Cloudflare Registrar. That is the recommendation and the only shape Gate 1 offers; best-of naming is a note in [[publisher-entity]] for members who ask.
- Static Astro build, Cloudflare Pages, rebuilt from a CSV.
- Real listings only: cleaned to the 5 to 6% of raw rows that are real businesses with reviews.
- Enriched: attributes and a description per listing, so the list is a tool, not a phone book.
- JSON-LD on every page, a real sitemap, launched lean.
- A claim-your-listing page and featured slots from day one. No owner logins; one door, verified by hand ([[refresh-and-upkeep]]).
- Styled from an inspired site the member picks, so it does not look Claude-coded ([[design-seed]]).
- Published by a named person with an About page and `Person` schema ([[publisher-entity]]). After launch it earns links the way working directories do: badges, press releases, resource pages, local content ([[authority-and-links]]).

## Cost and timeline the course may state
- Listings: a few dollars on DataForSEO for one category in one state (2,000 to 8,000 reviewed rows, measured 2026-09-29; Florida pool contractors $0.89), or about $25 to $120 on Outscraper (Florida pool contractors 8,535 rows, about $24; the video's typical scrape $100, and $317 for 119K rows a scrape run without exact match). DataForSEO holds 95 to 96% of the reviewed open businesses Outscraper finds.
- Build: the member's Claude subscription. Hosting free. Domain $10.44 a year.
- The trade-off, keep it honest: about $250 all-in is 20 to 25 microsites. Build a directory when you already own the vertical or have a buyer for the top spots.
- Timeline: same aging curve as microsites. Indexed month 1, Google decides by month 3, trusted month 6+. One member's rebuild: 166 to 887 indexed pages and 21 to 49 clicks in about 30 days, then the first leads.

> Source: the AI directories video (https://youtu.be/DzphMeAUJuo) and the Academy's community calls.

## See also
[[site-architecture]] · [[monetization-slots]] · [[launch-lean]]
