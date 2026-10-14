---
title: Monetization Slots
type: framework
status: draft
updated: 2026-09-28
---

# Monetization Slots

The ladder from the video plus receipts from operators in the community, with what the build has to include for each rung.

| Rung | In v1? | What the site needs |
|---|---|---|
| Display ads | No (Ezoic wants ~250k visitors/mo; Mediavine/Raptive harder) | nothing |
| **Featured listings, $29 to $500 a month each** | **Yes** | featured slots on every city page and the home page, a `/featured/` page with tiers and Payment Links, a `featured` column in the CSV that Gate 5 reads |
| **Premium listing, $97 a year** (the easiest sale) | **Yes** | the optimized listing state (photos, all links, embedded map), a "Listed on [Brand]" badge the business embeds on its own site with a link back, a `premium` column |
| **Best-of placement, one-time, $100 floor up to $1,200, always with a press release** (operators' receipts; Trust Analytica charges $750 for the same thing) | **Yes** | the city page is the "best [niche] in [city]" list; a `best_of_rank` column pins the paid position; the package is placement plus a press release (AB Newswire, about $10) plus the badge. The $100 floor exists to pay for the release. |
| Your own services (SEO, GMB optimization, a site) | **Yes, the main one for most members** | nothing on the site; the listing is the reason to call. See the outreach section below. |
| Sell leads | Yes, later | a per-city lead form or a tracked number (WhatConverts) once the pages rank |
| Podcast feature (Podstack) | member's choice, off the site | a founder interview sold with the listing; nothing to build |
| Influence | always | keep the audience; do not over-monetize early |

## The claim flow
Every listing page carries "Is this your business? Claim it." The claim form (no backend, `templates/claim-form.html`) captures business, contact, proof (website email domain or a phone call), and the wish list (fix details, add photos). Claiming is free. A claimed listing gets `claimed=true` in the CSV and a "Claimed" mark. Claim requests are the featured-listing sales pipeline.

**Verify before anything changes.** No owner logins in v1 (spam outran real signups on mature directories). Each claim is checked by hand: a real local business, not a lead-gen site or aggregator; email domain matches the website; phone matches the Maps row. Then edit the CSV and rebuild ([[refresh-and-upkeep]]).

## Featured tiers (defaults, edit in `templates/featured-tiers.md`)
- **City featured, $29/mo:** top card on one city page, followed link, photo.
- **County featured, $99/mo:** top card on a cluster of cities, followed link, photo, "featured" mark on the listing page.
- **State featured, $499/mo:** home page block plus every city page in the cluster, followed link, description rewrite, lead form on their listing page.
One business per tier per city. Sold by hand: the member sends the Payment Link, flips the `featured` column (`city` / `county` / `state`), rebuilds.

**Pricing is an open decision.** The video's range is monthly ($29 to $500). The room's receipts are a $97 a year premium listing and a one-time best-of package up to $1,200. Ship both shapes in the template and let the pilot pick.

## The two listing states
- **Basic (unclaimed):** name, address, phone, rating, review count, attributes, description, map link, nofollow website link. No photos, no social links.
- **Optimized (claimed and premium, or any featured tier):** photos supplied by the owner, every link (site and socials, followed), the embedded Google map, hours, the badge. This gap is the pitch: "you've got a listing and it's not optimized."

## The badge is a link, so it ships as HTML
The badge snippet in `templates/featured-tiers.md` is an HTML embed, never a JPEG. The line that works: "send this to your developer or we'll do it for you." Offer to install it, because the point is the link from the owner's site to their listing page. Word it as accreditation ("Verified [niche] on [Brand]", "Best [niche] in [city] [year]"), which is also how it gets placed ([[authority-and-links]]).

## The best-of play (credited to Bradley Benner)
The city page ranks the top listings, so every city page is a "best [niche] in [city]" list. Call the businesses on it to congratulate them and open the relationship. Six months later, call the ones not on it: "we're updating our best-of list." Charge for the placement, packaged with a press release and the badge. The `best_of_rank` column controls the pinned positions; unpaid positions stay data-sorted.

**The press release anatomy:** the release is about the business, not the directory. Its three links go to the business's home page, to its listing page on the directory, and to the city best-of page. One release strengthens three parts of the directory. Sell the top spot from $100 and up; the first $100 covers the release ([[authority-and-links]]).

## The outreach the directory unlocks
- The warm line: "You and I are connected because you've got a listing on my directory, the largest directory of [niche] in [state]. Is your map listing correct?"
- Then the optimization pitch, then the low-ticket SEO or GMB entry offer. For operators who run them, directories are the number one client source; one gets one to two audit requests a day off a single directory.
- Self-submissions on an aged directory are the warmest calls of all.

## The double-dip pitch (the outreach script the directory unlocks)
"I own this directory, and I also own five websites around your area that get leads." Outreach the member is doing anyway for lead sales; the directory makes the owner listen. Exclusive leads, not shared like Angie's.

## See also
[[page-types]] · [[footprint-rules]] · [[refresh-and-upkeep]] · [[authority-and-links]]
