---
title: Gate 1 scope — ScannerFinder
type: scope
status: complete, awaiting approval
updated: 2026-10-12
---

# Gate 1 scope — ScannerFinder

Slug: `scannerfinder` (deviation from the `<state>-<category>` convention: the directory spans 7 countries, not one state; the slug was proposed in the project overview).

## 1. Vertical
Practitioners offering bioenergetic / bioresonance wellness scans. This isn't a single Maps category: listings were pulled by brand (ZYTO, BICOM, Asyra/Qest4, NES Health, Rayonex, NLS, SCIO/Indigo/Eductor, MORA, TimeWaver, AO Scan). Excluded: Healy, iTOVi, Chinese analyzers. Source: [business plan](../../../../research/business-plan-2026-10-09.pdf).
Register: wellness only, never diagnosis or treatment.

## 2. "State" → 7 countries
US, GB, CA, AU, ZA, IE, NZ (launch US + GB). A country plays the role of the kit's "state" (hub per country).

## 3. Domain + brand
`scannerfinder.com`, owned (it currently runs a SpreadSimple site). Brand: **ScannerFinder**.

## 4. Owned microsites
None (Dan, 2026-10-12). No listing is flagged `owned`.

## 5. Publisher name
Andrei Ploiesteanu (Dan, 2026-10-12).

## 6. Publisher details
- Photo: [assets/andrei-ploiesteanu.jpg](assets/andrei-ploiesteanu.jpg) (received 2026-10-12, 160×160 px; it gets copied to `site/public/images/` at Gate 5). Small: fine for the byline/footer, soft on About. A ≥600 px version is better.
- Own website: none (Dan, 2026-10-12) → `publisher.url` points to the About page on scannerfinder.com.
- Bio (draft by Claude, awaiting Dan's approval, 107 words):
  > Andrei Ploiesteanu started ScannerFinder with a simple question: who near me actually offers a ZYTO, BICOM or AO Scan session, and what does it cost? The answers were scattered across Facebook pages, booking widgets and distributor sites, and many of the "practitioners" turned out to be people selling the devices.
  >
  > ScannerFinder puts the answer in one place. It lists more than 800 practitioners across seven countries, each checked against their own website. Profiles name the device when the practitioner does, keep sellers and training schools out of the listings, and show a session price only after the practitioner has confirmed it.
  >
  > Practitioners can claim and correct their listing for free.
- Contact email: hello@scannerfinder.com (Dan, 2026-10-12). Mailbox: check that it actually receives mail before launch (or set up the mail worker after launch).
- Profile links (`sameAs`): https://www.linkedin.com/in/andrei-ploiesteanu-68201a153/, https://www.facebook.com/andrei.ploiesteanu.1 (Dan, 2026-10-12).
- Phone: not given → the Contact page goes out without a phone (open, optional).

## 7. The look
ScannerFinder's own identity (Dan, 2026-10-12): the design pointer is scannerfinder.com + [price-tools](../../../price-tools/_overview.md). Tokens: charcoal `#272A31` / `#3B414C`, red-orange accent `#FF422F` (hover `#E8341F`), muted `#A2A9B4`, Nunito Sans, logos `price-tools/assets/logo-dark.png` + `logo-white.png` + `favicon.png`. Gate 4 adapts them to a light reading surface (dark only in the header/footer bands) and measures contrast (white on `#FF422F` falls below 4.5:1 for small text → a darker shade for button text/links).

## 8. Listings source
Already extracted, not via the kit: DataForSEO Business Listings, 2026-10-11 ($6.61), then cleaned, manually reviewed, enriched and profiled in the project pipeline. Gate 2 input: `input/listings-raw.csv` = [directory_listings.csv](../../../../data/directory_listings.csv) (831 practitioners, 35 public columns, our schema, not Outscraper). Internal master: `data/listings_profiled.csv`.

## Facts for Gate 4 (measured 2026-10-12)
- 831 listings: US 398 · GB 181 · ZA 79 · AU 78 · CA 64 · NZ 19 · IE 12.
- **Very sparse geography:** 652 distinct cities; only 28 have ≥3 listings (London 18, Cape Town 15, Centurion/Pretoria 8…; US max 5 in New York). The kit's model (city pages with 500–800 words) produces few city pages and hundreds of 1-listing "town pages". Gate 4 has to choose between country → region → city and brand pages (ZYTO/AO Scan/… × country) as the primary money pages.
- **Direction approved by Dan (2026-10-12):** the money pages are the device-brand pages (brand and brand × country, e.g. "ZYTO scan · US"), not the city pages. Gate 4 details the exact structure (regions, metros, the fold) and brings it back for approval.
- 220 without reviews; 760 with a description (the Google/business description often makes medical claims → it can't be published as-is).

## Open before Gate 5
- Final approval of the bio (draft in Q6); optionally one true sentence from Andrei's own story.
- Photo of at least 600 px (the current one is 160 px).
- Phone for the Contact page (optional).
- Check that hello@scannerfinder.com receives mail.
- DataForSEO login for the kit scripts (not needed: the pull is done).
- Hosting decision: Astro + Cloudflare Pages replaces SpreadSimple (deploy = Red).
