---
title: Gate 6 launch — ScannerFinder
type: launch
status: LIVE on scannerfinder.com (2026-10-12)
updated: 2026-10-12
---

# Gate 6 — Launch lean

> **LIVE 2026-10-12 at https://scannerfinder.com** (and www). `check_live.py` on the domain + pages.dev: **All checks passed**, including `X-Robots-Tag: noindex` on pages.dev. The dripfeed can start.

## Deploy
- Cloudflare Pages, project `scannerfinder` (account: ScannerFinder), production branch `main`.
- Deploy: `cd site && npm run build && npx wrangler pages deploy dist --project-name scannerfinder --branch main --commit-dirty=true`
- Last deploy: 2026-10-13 10:02 (957 pages: + Tools menu with ROI Calculator, Saira Condensed/system-ui typography). Earlier 2026-10-13 (955 pages: mobile hamburger + 2×2 stats, every device × country page with thin ones noindex, search by region/country, near-me by nearest listing, logos on cards and listing pages). Previous: 2026-10-12 (934 pages, static, with no adapter). `404.html`, `_headers`, `_redirects` present.
- Custom domains: `scannerfinder.com`, `www.scannerfinder.com` (CNAME → scannerfinder.pages.dev, proxied; added by Dan 2026-10-12). Both serve the site (canonical = apex). www → apex: 301 Redirect Rule (Dan, 2026-10-13), checked: path and query string preserved.

## DNS records to add (Cloudflare → scannerfinder.com → DNS → Records)
| Type | Name | Target | Proxy |
|---|---|---|---|
| CNAME | `@` | `scannerfinder.pages.dev` | Proxied (orange) |
| CNAME | `www` | `scannerfinder.pages.dev` | Proxied (orange) |
The MX/TXT records for Email Routing (hello@) stay untouched. Alternative: Workers & Pages → scannerfinder → Custom domains → "Activate domain" on each pending entry.

## Live check
- `check_live.py https://scannerfinder.pages.dev --expect-urls 513` → **All checks passed** (2026-10-12): home 200 + H1 + canonical to scannerfinder.com, a 404 for unknown addresses, robots.txt with sitemap, 513 URLs in the sitemap, indexable pages, /claim/ and /featured/ noindex, no preview cards.
- `check_live.py https://scannerfinder.com --pages-dev https://scannerfinder.pages.dev --expect-urls 513` → **All checks passed** (2026-10-12; run with resolution forced through Cloudflare's IPs because the local resolver still had the old NXDOMAIN cached).

## Incident at deploy (fixed)
The first `wrangler pages project create` (without `--force`, Wrangler 4.149) delegated to Workers and ran an automatic setup step: it installed `@astrojs/cloudflare`, added the adapter to `astro.config.mjs`, created `wrangler.jsonc` + `public/.assetsignore` + `.wrangler/`, built SSR and **deployed a separate Worker named `scannerfinder`**. On Pages, that version answered 404 on the home page. Fixed: adapter and package removed, the generated files moved to `output/scannerfinder/_wrangler-autoconfig-2026-10-12/`, a clean static rebuild, the Pages project created with `--force` (the kit's instruction), redeployed. **The `scannerfinder` Worker was deleted** on 2026-10-12, with Dan's approval.

## Indexed at launch
- In the sitemap: 513 = home, About, 7 country hubs, 66 regions, 38 device pages, 3 feature pages, 397 non-thin listings.
- `noindex`: 412 thin listings (fewer than 5 reviews or no description), claim, featured, legal, browse, search, badges.

## Dripfeed (Omega Indexer) — DROPPED
- Dan, 2026-10-13: we don't do the Omega indexing. Indexing happens naturally (sitemap + internal links). The files below stay as an ordered list in case we need them.
- Ordered list: [06-sitemap-urls.txt](06-sitemap-urls.txt) (home → hubs → About → regions largest to smallest → devices → features → listings by rating × reviews).
- Per day: [06-dripfeed.csv](06-dripfeed.csv): ~60 URLs/day, **9 days**.
- ~~Start: after `check_live.py` passes.~~ Not applicable.

## Widening (every 30 days)
Read the indexed count + clicks (the indexing tool's report + Cloudflare Web Analytics; GSC is allowed, since there's no microsite network). If the indexed count grows: the next tranche of thin listings → index (claimed ones first, then by review count), rebuild, resubmit.

## The 30-day check: **2026-11-11**
Indexed pages, clicks, first claims, first featured inquiry.

## After launch (agreed with Dan)
- Claim form → involve.me (until then: a pre-filled email to hello@).
- Stripe Payment Links: Premium $97/yr, Region $29/mo, Country $149/mo → `site.json` `tiers`, rebuild, redeploy.
- Brand featured ($49/mo) — v1.1.
