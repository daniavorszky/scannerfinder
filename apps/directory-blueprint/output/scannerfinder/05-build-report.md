---
title: Gate 5 build report — ScannerFinder
type: report
status: approved 2026-10-12
updated: 2026-10-12
---

# Gate 5 — Build report

**The site builds** (`npm run build`, 0 warnings): **935 pages**, **513 in the sitemap**. Build folder: `site/` (Astro 5), deploy output `site/dist/` (iCloud-excluded via `dist.nosync`, like `node_modules.nosync`).

## Pages

| Type | Built | In the sitemap |
|---|---|---|
| Home, About, legal, claim, featured, search, browse | 11 | home + About |
| Country hubs `/directory/<country>/` | 7 | 7 |
| Regions `/directory/<country>/<region>/` | 66 | 66 |
| Brand pages `/devices/` + 10 brands + 27 brand × country | 38 | 38 |
| Feature pages `/services/` + remote + pets and horses | 3 | 3 |
| Listings `/company/<country>/<region>/<slug>/` | 810 | 397 (the 413 thin ones are `noindex`) |

## What changed from the kit (only in `site/`, the kit is intact)
- `src/lib/load.mjs`: multi-country (`site.countries[]`), the region fills the city slot, no fold; listings in regions <3 keep their URL and appear on the country hub; `devices` / `services` families; brand × country pages (≥3, devices only); `inName` ("the United States").
- New pages: `src/components/FamilyPage.astro`, `src/pages/devices/[...slug].astro`; rewritten: country hub, browse; adapted: region, listing, home, DirectoryHub, Base (logo, nav Countries/Devices, footer), FeaturedBand, ClaimCta, 404, search, About, `astro.config.mjs` (redirects per country).
- Listing page: **Google review topics removed** (they repeated health claims, e.g. "food intolerances"); `addressCountry` from the data (not `US`); device links go to the brand × country page.
- Data scripts (project): [blueprint_regions.py](../../../../scripts/blueprint_regions.py) (regions: GB postcode → ITL1, ZA/NZ by city, abbreviations normalized), [wellness_lint.py](../../../../scripts/wellness_lint.py) (descriptions + region copy + intros).

## Copy (all checked)
| Block | Count | Checks |
|---|---|---|
| Region copy (`city-copy.json`) | 66 | `check_city_copy.py --write` 0 FAIL · `lint_copy.py` 66/66 PASS · wellness_lint 0 |
| Brand + brand × country + feature intros | 39 | wellness_lint 0, in their band |
| Country intros (`site.countryCopy`) | 7 | wellness_lint 0, ≤4 numbers each |
| Home (buyer's guide + 6 FAQs) | 1 | `lint_copy` PASS 1,041 words |
| About (publisher's voice) | 1 | `lint_copy` PASS 445 words |
| Fact sheet | [05-fact-sheet.md](05-fact-sheet.md) | official sources; not used in the region copy (deliberately) |

Indexes `/devices/` and `/services/` are link lists → below the word floor (expected).

## Audit (935 pages)
One H1 per page ✓ · title on every page ✓ · JSON-LD parses ✓ · no `aggregateRating` ✓ · **0 broken internal links** ✓ · no `noindex` page in the sitemap ✓ · no placeholder text outside claim/featured ✓ · `featuredPreview: false` ✓ · mobile 375 px without horizontal scroll ✓ · console without errors ✓.

## Launch blockers (Gate 6) — status after Dan's answer (2026-10-12)
- Claim form: **after launch** (involve.me); until then the form opens a pre-filled email to hello@.
- Stripe: **after launch**; until then the buttons go to /claim/?tier=… .
- DNS/Cloudflare: Dan is logged in to CF (Arc); `wrangler login` needed.
- hello@: **solved** (CF Email Routing).
- Photo: **solved** (600×902).

Original list:
1. **Claim form:** `contact.formEndpoint` = `formspree.io/f/REPLACE_BEFORE_LAUNCH` → a Formspree form (or the mail worker after launch).
2. **Stripe Payment Links:** Premium $97/yr, Region $29/mo, Country $149/mo, Best-of → in `site.json` `tiers`.
3. **DNS:** scannerfinder.com moves from SpreadSimple to Cloudflare Pages (Dan's Cloudflare account + `wrangler login`).
4. **hello@scannerfinder.com** must receive mail.
5. **Publisher photo** ≥600 px (the current one is 160 px).

## What the fact sheet found ([05-fact-sheet.md](05-fact-sheet.md): 35 official sources, 7 unsourced items not usable)
- **FDA, warning letter to ZYTO (21 June 2023):** the scanner is cleared only to measure galvanic skin response; using it to name conditions (Alzheimer's, HIV, melanoma) = diagnosis. ZYTO also recalled its software in 2015 for claims beyond its clearance. → our copy is fine (we never say a scan "finds" anything), but practitioners who make such claims on their own sites are a reputational risk for the directory.
- **UK ASA (advice of 6 Jan 2026; rulings 2018, 2019, 22 April 2026):** no evidence that bioresonance devices diagnose or treat; a CE mark is not proof that they work. → listing names like "Food Intolerance Testing NI" are exactly what the ASA has sanctioned (for the business, not us), but the risk is real.
- **FDA General Wellness (6 Jan 2026):** "relaxation / stress management" claims are wellness only without mentioning any disease. "Biofeedback" is itself a Class II device type → we use it only as a description of the device the practitioner uses, never as a softer word for an effect.
- No official statements specific to bioresonance in Canada, South Africa or New Zealand; there the general advertising rules apply.

## For Dan's review (not blockers)
- `lkhjytfryuiy-wetumpka` (Alabama): the business name is junk, no site, 0 reviews → **recommend drop** in `04-exclusions.csv`.
- Business names with medical words stay as they are (they're the business's own name): "Bio Resonance Diagnostics New York", "Food Intolerance Testing NI", "VURV Thyroid Clinic", "Allergy Elimination Centre Shuswap". Alternative: drop them as a matter of image.
- The bio on About + in `site.json` is still Claude's draft (approved as a direction, not finally).
- Brand featured ($49/mo) = v1.1, not built.

## How to view it
Locally: double-click `site/preview-site.command` (serves `dist/` as it will be deployed). Don't open `dist/index.html` directly.
