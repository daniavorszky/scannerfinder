---
title: Gate 4 plan — ScannerFinder, adding Germany + Romania
type: plan
status: awaiting approval
updated: 2026-10-14
---

# Gate 4 — Plan: Germany + Romania into the live site

Input: [03-listings-enriched.csv](03-listings-enriched.csv) (871) − 46 `drop` in [04-exclusions.csv](04-exclusions.csv) = **825 practitioners** (DE 709 · RO 116); 6 more get `blank_website`. Everything else follows the approved main plan ([../scannerfinder/04-plan.md](../scannerfinder/04-plan.md)): same architecture, same templates, same tiers. This plan only adds two countries to the same site (one build, one sitemap), going from 7 to 9 countries and from 810 to 1,635 practitioners.

## 1. What gets added

| Layer | URL | New pages | Note |
|---|---|---|---|
| Country hub | `/directory/germany/`, `/directory/romania/` | 2 | country intro (main-plan format) |
| Region | `/directory/germany/<land>/`, `/directory/romania/<judet>/` | DE **16** · RO **~15** | ≥3 listings, as in the main plan |
| Listing | `/company/<country>/<region>/<slug>/` | 825 | 398 non-thin indexed, 427 thin `noindex` |
| Brand × country | `/devices/<brand>/germany/` etc. | **9** | DE: BICOM 98 · Rayonex 59 · TimeWaver 33 · NLS 22 · SCIO 9 · MORA 6. RO: ZYTO 15 · NLS 14 · SCIO 14 |
| Global brand pages | `/devices/<brand>/` | 0 new | counts grow (BICOM 25 → 123, Rayonex 18 → 77, TimeWaver 6 → 39); intros refreshed |
| Feature pages | remote / animals | 0 new | +74 remote, +57 animals |

**Sitemap at launch: +~430 URLs** (2 hubs, ~31 regions, 9 brand × country, 398 listings) → about 940 in total.

## 2. Regions (the data has none)

DataForSEO leaves `region` empty for DE and RO, so it's derived offline, as GB was in the main run, in [blueprint_regions.py](../../../../scripts/blueprint_regions.py):
- **Germany → the 16 Länder**, from the postcode. Measured: every Land has ≥3 listings (Bavaria 170, NRW 138, Baden-Württemberg 120, Hesse 58, Lower Saxony 53 … Bremen 4, Saxony-Anhalt 3). A two-digit postcode table is right for most rows; the few border prefixes (e.g. 21 Hamburg/Lower Saxony, 37 Lower Saxony/Hesse/Thuringia, 68 BW/Hesse) are settled by the city name, checked by hand.
- **Romania → județe**, from the first two postcode digits (exact in Romania); the 11 rows without a postcode are mapped by city. Measured: ~15 județe with ≥3 (Bucharest ~20, Cluj 10, Suceava 8, Timiș 8, Iași 7 …); the other ~22 listings appear on the Romania hub under "Other counties", as in the main plan.
- **Names in English where English has one** (Bavaria, North Rhine-Westphalia, Lower Saxony, Thuringia, Hesse; Bucharest), local otherwise (Baden-Württemberg, Cluj, Iași) — the site is English and that's what an English searcher types. Slugs ASCII (`baden-wurttemberg`, `iasi`).

## 3. Copy to write (Gate 5)

| Copy | Count | Band | Checks |
|---|---|---|---|
| Region copy (`city-copy.json`) | ~31 | as the main run (500–800, small regions shorter) + 4–6 FAQs | `check_city_copy.py`, `lint_copy.py`, `wellness_lint.py` (DE/RO words) |
| Country intros (`site.countryCopy`) | 2 | as the main run | wellness_lint |
| Brand × country intros | 9 | 80–200 | wellness_lint |
| Global brand intros refreshed | 6 (BICOM, Rayonex, TimeWaver, NLS, SCIO, MORA) | 80–200 | wellness_lint |
| Home / About numbers | "7 countries / 800+" → "9 countries / 1,600+" | — | lint |
| **Fact sheet addendum** | DE + RO | official sources only | Heilpraktikergesetz (who may practise), HWG/UWG (advertising of health claims), Romanian rules for complementary practice; used only to keep the copy from saying anything wrong, as in the main run |

**Cost estimate:** ~31 region packets at the main run's rate (66 regions on 4 sub-agents) + 17 intros + the fact sheet ≈ 1–1.5M Sonnet tokens ≈ one 5-hour window, paced as Gate 3 was.

## 4. Things that change for the whole site

- **Germany = Bioresonanz country.** BICOM (Regumed) and Rayonex are German makers. The two new BICOM/Rayonex × Germany pages become the biggest brand × country pages on the site.
- **The bio on About** says "more than 800 practitioners across seven countries" → updated to the new totals (publisher's voice kept).
- **Legal pages:** a site that lists German practitioners and is read in Germany should show the operator's identity (name, address, contact) on a legal-notice page. The main plan has Contact + Privacy + Terms but no operator block. Recommendation: add a short "Legal notice" (operator = the company Dan names) before the German pages go live.
- **Outreach note:** German practitioners are invited through contact forms only (UWG §7). This doesn't change the site.

## 5. Decisions for Dan

| # | Decision | Recommendation |
|---|---|---|
| 1 | Add DE + RO to the same site, same architecture (country → region → listing; brand × country ≥3) | **yes** |
| 2 | Regions: 16 Länder from postcodes; Romanian județe from postcodes (≥3 get a page, the rest listed on the hub) | **yes** |
| 3 | Region names in English where one exists (Bavaria, Bucharest), otherwise local | **yes** |
| 4 | 9 new brand × country pages (DE: BICOM, Rayonex, TimeWaver, NLS, SCIO, MORA · RO: ZYTO, NLS, SCIO) | **yes** |
| 5 | Fact sheet addendum for DE/RO (Heilpraktiker law, HWG, Romanian rules) before any region copy | **yes** |
| 6 | Same tiers and prices in DE/RO ($97 / $29 / $149) | **yes** for launch; local pricing later from demand |
| 7 | "Legal notice" page with the operator's identity — which company/address? | **yes, Dan names the operator** |
| 8 | Copy run paced to the 5-hour window (like Gate 3), ~one window | **yes** |
| 9 | No deploy in this step: build + audit locally, deploy stays Gate 6 (Red) | **yes** |
