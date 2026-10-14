---
title: Gate 4 plan — ScannerFinder
type: plan
status: approved 2026-10-12 (all 10)
updated: 2026-10-12
---

# Gate 4 — Plan

Input: [03-listings-enriched.csv](03-listings-enriched.csv) (819) − 9 `drop` from [04-exclusions.csv](04-exclusions.csv) = **810 practitioners** in 7 countries. 7 more get `blank_website` (expired/hacked domains).

## 1. Why the kit's model changes

The kit assumes one state, with city pages. Here, measured on the 810:

| Model | Indexable geo pages | Listings on them | Listings on 1–2 listing pages |
|---|---|---|---|
| City + 40 km fold (kit) | 26 | 216 | **594** |
| City + 80 km fold | 26 | 290 | 520 |
| **Region (state/province/nation) — proposed** | **~65** | **~790** | ~20 |

The geography is too sparse for cities. The money pages are the **device brands** (decided at Gate 1); the geo pages are the second network.

## 2. Architecture and URLs

| Layer | URL | Count | Ranks for |
|---|---|---|---|
| Home | `/` | 1 | "bioresonance practitioner near me", "find a ZYTO scan" |
| Country hub (kit: state hub) | `/directory/<country>/` | 7 | "bioresonance [country]" |
| Region page (kit: city page) | `/directory/<country>/<region>/` | ~65 with ≥3 listings | "bioresonance [California / London / Western Cape]" |
| Listing page | `/company/<country>/<region>/<slug>/` | 810 | business name, long tail |
| **Brand page** (kit: service page) | `/devices/<brand>/` | 10 | "zyto scan near me", "bicom practitioner" |
| **Brand × country** (new) | `/devices/<brand>/<country>/` | 27 with ≥3 listings | "zyto scan usa", "bicom therapy uk" |
| Feature page (kit: service page) | `/services/remote-sessions/`, `/services/pets-and-horses/` | 2 | "remote bioresonance scan", "bioresonance for dogs/horses" |
| Claim, Featured, About, Contact, Privacy, Terms, Browse, Search, Badge | as in the kit | — | conversion / trust |

**Country slugs:** `united-states`, `united-kingdom`, `canada`, `australia`, `south-africa`, `ireland`, `new-zealand` (full names: keyword in the URL, clear to the visitor).

**Regions:**
- US / CA / AU: state/province from DataForSEO, with abbreviations normalized (MN, TX, NSW, VIC, MB…). US ≈ 38 pages, CA 6, AU 4.
- **GB** (178 listings, no region in the data): derived from the postcode area → the 12 official ITL1 regions (London, South East, North West, Scotland, Wales, Northern Ireland…). Offline table, no external calls. Estimate ~10 pages ≥3; London alone ~30.
- **ZA** (77): city → province, mapped by hand (Western Cape, Gauteng, KwaZulu-Natal…). ~4 pages.
- **NZ** (19): city → region (Auckland, Canterbury…). ~2 pages.
- **IE** (12): no regions. The country hub lists everyone (12 is a short list).
- **Regions under 3 listings** (e.g. Hawaii, Maine, Western Australia): their listings appear on the country hub under "Other states/provinces". The listing keeps its URL with the region; there's no separate region page (no thin pages with 1 listing). The kit's fold to the nearest region is turned off (`foldMaxKm` irrelevant): folding Hawaii into California would be wrong.

**Brand × country with ≥3 listings (27):** ZYTO US·CA · SCIO US·ZA·CA·GB·NZ · AO Scan US·CA·AU · Asyra US·GB · NLS GB·US·ZA·AU·IE · BICOM GB·CA·NZ · NES US·AU·CA · Rayonex GB·CA · MORA AU·US. Global brand pages: all 10 (TimeWaver has 6 in total).

Confirmed counts (true): ZYTO 141 · SCIO 79 · AO Scan 63 · Asyra 62 · NLS 34 · BICOM 25 · NES 23 · Rayonex 18 · MORA 9 · TimeWaver 6 · remote 176 · animals 61 · free consultation 64 (filter only, no page — it's a sales argument, not a search).

## 3. Launch lean (Gate 6)

In the sitemap at launch: home, 7 hubs, ~65 regions, 10 brands, 27 brand × country, 2 feature pages, **397 non-thin listings** ≈ **510 URLs**. The 413 thin listings are `noindex` until they're claimed or get ≥5 reviews. Claim, featured, badge, legal, browse and search: `noindex`.

## 4. Data and sorting

- `niche`: singular **bioresonance practitioner**, plural **bioresonance practitioners**, title **Bioresonance Practitioners**. ("Bioresonance" is the most searched generic term; the brands catch ZYTO/AO Scan, which aren't technically bioresonance.)
- `niche.schemaType`: **HealthAndBeautyBusiness** (a LocalBusiness subtype; deliberately not `MedicalBusiness`, so we don't imply a medical service).
- `sortAttribute`: `offers_scan` (confirmed scans first, after paid positions); `confirmedLabel`: "confirmed scan practitioners".
- Card order: featured → best-of → confirmed scan → rating × log(reviews) (as in the kit).
- Prices: not shown (decision 2026-10-12, only after confirmation).

## 5. Monetization (featured slots)

The kit's tiers mapped to the new structure. Prices are a recommendation; the Stripe Payment Links are a launch blocker.

| Tier | Where it appears | Recommended price |
|---|---|---|
| Premium listing | photos, followed link, badge, map on the listing page | **$97 / year** |
| Region featured (kit: city) | top of the region page | **$29 / month** |
| Brand featured (new, v1.1) | top of a brand page (`/devices/zyto/…`) | **$49 / month**, after launch |
| Country featured (kit: state) | top of the country hub + home | **$149 / month** |
| Best-of (one time) | "Top 3" on the region page | **from $100** |

Brand featured is the most valuable slot (high-intent traffic), but it needs extra template code → v1.1, not a launch blocker.

## 6. Look (design tokens)

Source: ScannerFinder brand (Gate 1 Q7) — scannerfinder.com + price-tools. Light reading surface; charcoal only in the header/footer bands. Contrast measured (WCAG, ≥4.5 for text):

| Token | Value | Note |
|---|---|---|
| `headerBg`, `band` | `#272A31` | brand charcoal; white text on it 14.4 ✓ |
| `bandSoft` / `muted` on dark | `#A2A9B4` | 6.1 on charcoal ✓ |
| `bg` / `surface` | `#FFFFFF` / `#F5F6F8` | |
| `heading` | `#272A31` | 13.3 on surface ✓ |
| `text` | `#3B414C` | 10.3 ✓ |
| `muted` | `#5A5D69` | 6.6 ✓ |
| `action` (main button) | `#FF422F` with **charcoal** text | white on `#FF422F` = 3.5 ✗ → charcoal on red 4.2 (passes for large text/bold buttons); alternative below |
| `accent`, `link` | `#C8250F` | darkened brand red: 5.6 on white ✓ (the original `#FF422F` = 3.5 ✗ for links) |
| `accentText` | `#FFFFFF` | white on `#C8250F` 5.6 ✓ |
| font | **Nunito Sans** (SIL OFL, self-hosted @fontsource) for headings + body | the brand font |
| logo | `logo-white.png` in the header (image instead of `logoText`), `favicon.png` | from price-tools/assets |

**Alternative for the main button:** `#C8250F` with white text (5.6 ✓) instead of bright `#FF422F`. Recommendation: **`#C8250F` + white everywhere** (one rule, safe); bright `#FF422F` only as a decorative accent (badges, highlights).

## 7. Template changes (only in `output/scannerfinder/site/`, the kit stays intact)

1. `load.mjs`: multi-country — `site.countries[]` instead of `site.state`; floor/sort per country; region in the city slot; no fold.
2. Routes: `/directory/[state]/` and `/company/[state]/[city]/[slug]/` generated for all 7 countries; country hub with "Other states/provinces".
3. Brand pages: the `service` blocks from `attributes.json` on `/devices/`; a new route `/devices/[brand]/[country]/`.
4. `Base.astro`: logo image; nav with Countries + Devices.
5. Listing page: a "Device" block (brands true), "Remote sessions", "Free first consultation", "Sessions for animals"; the wellness disclaimer (below).
6. Disclaimer (`site.disclaimer`): *"ScannerFinder lists independent wellness practitioners. Scans and sessions described here are wellness services, not medical tests, diagnoses or treatments. Talk to a licensed healthcare professional about any health concern."*

## 8. Copy at Gate 5 (cost on the subscription)

| Block | Count | Estimate |
|---|---|---|
| Region copy (place-first, 300–600 words + 4–6 FAQs, size band per page-types) | ~65 | ~1.2M tokens |
| Brand + brand × country intros (80–200 words) | 37 | ~0.2M |
| Home (buyer's guide 400–600), About, country hubs | 9 | ~0.1M |
| **Fact sheet** (official rules on wellness advertising: FTC/FDA US, ASA/CAP UK, Competition Bureau/Health Canada, ACCC/TGA AU, ASA ZA, ASA NZ, ASAI IE) | 1 | web research |

Total ≈ **1.5M tokens**.

## 9. Domain and hosting

`scannerfinder.com` stays the domain. The build goes on Cloudflare Pages; at Gate 6 the DNS moves from SpreadSimple to Cloudflare (Dan's account — Red, done by you). The price tools (Device Price Index + ROI) come in later as `/tools/…` pages on the same site.

## Decisions for Dan

| # | Decision | Recommendation |
|---|---|---|
| 1 | Geo model: country → **region** → listing (not cities) | **yes** |
| 2 | Regions under 3 listings: no page of their own, listed on the country hub | **yes** |
| 3 | Brand pages at `/devices/<brand>/` + 27 brand × country pages | **yes** |
| 4 | Feature pages: remote sessions + pets & horses | **yes** |
| 5 | Country slugs written in full (`united-kingdom`, not `gb`) | **yes** |
| 6 | Niche term: "Bioresonance Practitioners" | **yes** |
| 7 | Schema type `HealthAndBeautyBusiness` | **yes** |
| 8 | Tiers and prices: Premium $97/yr · Region $29/mo · Country $149/mo · Best-of from $100 · Brand $49/mo in v1.1 | **yes** (or your prices) |
| 9 | Main button `#C8250F` + white (not bright `#FF422F`) | **yes** |
| 10 | Copy at Gate 5 ≈ 1.5M tokens + fact sheet from official sources | **yes** |
