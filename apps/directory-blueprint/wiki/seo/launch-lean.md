---
title: Launch Lean (Gate 6)
type: seo
status: draft
updated: 2026-10-05
---

# Launch Lean (Gate 6)

One member's rebuild rule, adopted as the house rule: generate everything, publish the strong pages first, earn trust, widen. That rebuild launched 4,796 pages with 1,028 in the sitemap and about 1,100 thin profiles noindexed, and went from 166 to 887 indexed pages in about 30 days.

## What enters the sitemap at launch
- Home, state hub, every city page that clears the 3-listing floor, every small-town page kept by `foldMaxKm` (Shawn, 2026-09-29: town pages are indexed too), claim, featured, legal.
- Listing pages with `thin=false` (5+ reviews and a description).
- The service pages and their index, when the build has them ([[page-types]]).

## What ships `noindex` at launch
- Listing pages with `thin=true`. They still render, still link, still carry schema, and still show "claim this listing" (a claim is the cheapest way to un-thin a page).
- Cities under the floor that are folded (they do not get a page; their listings sit on the nearest city page). A town further than `foldMaxKm` from every city page is not folded: it keeps a page of its own, indexed and in the sitemap ([[site-architecture]]), and its listing pages follow the normal thin rule.
- The resources index, until a real resource page exists (the skeleton's `_example.md` is not one).

## Widening
Every 30 days: read indexed count and clicks (indexing tool report + Cloudflare analytics, no GSC on a network directory per [[footprint-rules]]). If indexed pages are growing, flip the next tranche of thin pages to index (claimed ones first, then by review count), rebuild, resubmit.

## Indexing
Omega Indexer, dripfeed. Sitemap URL list is the input; a 1,000-page launch runs 7 to 10 days. Same lesson as the Microsite Playbook Step 6, but here the sitemap really exists and really matters.

## Found on the pilot (2026-09-29)
- **The site must ship a `404.html`.** Cloudflare Pages treats a site without one as a single-page app and answers every unknown address with the home page and a 200. The skeleton now has `src/pages/404.astro`.
- **The pages.dev address must be kept out of search.** `public/_headers` sends `X-Robots-Tag: noindex` on `:project.pages.dev` and on preview addresses. Check it after the deploy; it cannot be checked before.
- **Drag and drop takes 1,000 files.** A directory of any size is over that (the pilot has 1,726). Deploy with `npx wrangler pages deploy dist`, which takes 20,000. The member logs in to Cloudflare; Claude never does.
- **Check from the outside before the dripfeed starts:** `scripts/check_live.py https://<domain> --pages-dev https://<project>.pages.dev --expect-urls <n>`.
- **Order the dripfeed.** Home, state hub and About, then city pages from largest to smallest, then listings by rating and review count. Gate 6 writes `06-sitemap-urls.txt` and `06-dripfeed.csv`.
- **Under-floor towns beyond the fold cap** keep a page of their own, indexed and in the sitemap ([[site-architecture]]; Shawn, 2026-09-29). The line above about cities under the floor holds for towns inside the cap, which are folded.
- **The launch date** in `site.json` feeds `datePublished`. Set it on the day of the deploy, not at build time.
- **A gate that cannot deploy still produces its artifact.** When the domain or the Cloudflare login is missing, `06-launch.md` says so at the top and lists what the member has to do.

## The 30-day check (write the date into `06-launch.md`)
Indexed pages, clicks, first claim requests, first featured inquiry. That is the receipt the course pins.

## See also
[[on-page-rules]] · [[schema]]
