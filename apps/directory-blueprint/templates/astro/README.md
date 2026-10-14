# Astro skeleton: what Gate 5 copies and what it fills

This folder is a complete, buildable Astro 5 project. Gate 5 copies it to `output/<slug>/site/` and fills the data files. It does not write pages from scratch. Smoke-tested 2026-09-28 with a synthetic 27-listing export: `npm install && npm run build` produced 43 pages, a sitemap with thin listings excluded, badges, robots.txt.

## Fill these (in this order)

| File | What goes in | Source |
|---|---|---|
| `src/data/site.json` | brand, domain, tagline, niche words, state, launch date, **publisher** (name, url, email, bio, image, sameAs), contact form endpoint (the form service at launch, or the mail worker's `/claim` after `scripts/mail_worker.py wire-form`; the claim page shows its sent notice on `/claim/?sent=1`), tier prices and Stripe Payment Links, **design tokens**, home FAQ. `domain` is the domain the member owns or intends to register (the category shape from Gate 1, without `https://`); every canonical URL, the sitemap and the schema ids are built from it, so the site builds with it before registration and `05-build-report.md` lists the registration as a launch blocker until it is done | `01-scope.md` (brand, domain, publisher, inspired site), `04-plan.md` (tokens, tiers) |
| `src/data/listings.csv` | the Gate 3 output, row per listing | copy of `output/<slug>/03-listings-enriched.csv` |
| `src/data/attributes.json` | the vertical's attribute set: `key` (must equal a CSV column), `label`, `faq` template with `{plural}`, `{singular}`, `{city}`, `{state}`, and on the attributes `04-plan.md` names as service pages a `service` block (`slug`, `title`, `intro`: 80 to 200 words written at Gate 5) | `03-attributes.json` |
| `src/data/city-copy.json` | per `city_slug`: `intro` (array of paragraphs, 500 to 800 words of real local copy; lower floors for small cities and 120 words with 2 to 6 FAQs on a town page, wiki/framework/page-types.md) and `faqs` (4 to 6 `{q, a}` from the data). Cities without an entry build with a short data-driven fallback and the build prints a warning naming them | written by Claude at Gate 5 from the enriched data |
| `src/pages/index.astro` | the buyer's guide block marked `GATE 5` (400 to 600 words) | written at Gate 5 |
| `src/pages/about.astro` | the "Why this directory exists" block marked `GATE 5` (150 to 250 words, publisher's voice) | `01-scope.md` |
| `public/images/publisher.jpg` | the publisher photo named in site.json | member |
| `public/images/listings/<slug>/...` | owner-supplied photos for claimed premium or featured listings; paths go in the CSV `photos` column, `|` separated | claims and sales |
| `src/pages/resources/<slug>.md` | optional resource pages (copy `_example.md`; files starting with `_` are not built) | member request, see wiki/framework/authority-and-links.md |

## CSV columns the site reads

From Gate 2: `name, phone, website, address, street, city, state_code, postal_code, county, latitude, longitude, type, subtypes, rating, reviews, reviews_tags, description, working_hours, verified, location_link, area_service, slug, city_slug, thin, featured, featured_cities, claimed`.
From Gate 3: one column per attribute key with `true` / `false` / `not enough info`, and `description_enriched`.
Sales columns the member flips by hand: `featured` (`city` / `county` / `state`), `featured_cities` (city slugs for county), `premium` (`true`), `best_of_rank` (1 to 3), `claimed` (`true`), `photos`.
`owned` is never read by the site (footprint rule).

## What the skeleton already does

- Routes: `/`, `/directory/` (browse, noindex), `/directory/<state>/`, `/directory/<state>/<city>/`, `/company/<state>/<city>/<slug>/`, `/search/` (noindex), `/claim/`, `/featured/`, `/about/`, `/contact/`, `/privacy/`, `/terms/`, `/resources/`, `/resources/<slug>/`, `/services/` and `/services/<slug>/` (only when an attribute carries a `service` block and at least the city floor of listings confirm it), `/favicon.svg`, `/badge/<slug>/` + `/badge/<slug>.svg`, `/robots.txt`, `/sitemap-index.xml`.
- City floor (default 3) with under-floor cities folded into the nearest city page (or kept as an indexed small-town page when further than `foldMaxKm`); nearby cities by distance; card order featured, then best-of rank, then rating x log(reviews); 60-card cap with an "All N" list below.
- Two listing states: basic (no photos, nofollow website link) and optimized (claimed premium or any featured tier: photos, followed link, embedded map, badge).
- Launch lean: thin listings (`thin=true`, or under 5 reviews or no description) and the badge, claim, featured and legal pages carry `noindex` and are excluded from the sitemap. Claiming or a paid tier un-thins a page.
- JSON-LD per page type (WebSite, Organization with founder and publisher, Person on About, CollectionPage + ItemList of the business type on city and service pages, the business type from `niche.schemaType` with hours on listings (no `aggregateRating`: the ratings are Google's, wiki/seo/schema.md), telephone in E.164, FAQPage, BreadcrumbList, Article on resources), `datePublished` from `launchDate` and `dateModified` from the build date.
- Internal links: every listing page lists four other listings from its city (the next four in the city's order, so every listing is linked from four others) and the service pages it appears on; the home page has a "See all N cities" button under the eight city cards and the footer an "All N cities" link.
- A default favicon (`/favicon.svg`: the brand's first letter on the header color).
- Design tokens from `site.json` as CSS variables; no eyebrow labels, no colored card borders, cards carry data.
- Facts as visible text: FAQs, hours and attributes are never in accordions.

## Optional settings in `site.json` (added on the pilot, 2026-09-29)

| Key | What it does | Default |
|---|---|---|
| `design.heading`, `design.headingWeight`, `design.link`, `design.buttonRadius` | heading color and weight, link color, button corners | the base tokens |
| `design.band`, `design.bandText` | home hero and footer band | the surface color |
| `design.action`, `design.actionText` | the call-to-action band | the accent |
| `sortAttribute` | listings with this attribute true sort first in their group | none |
| `confirmedLabel` | the short label after the count of listings whose `sortAttribute` is true, on the stat strip, the city cards and the city key facts (pilot: "confirmed builders") | `confirmed` |
| `vettingSteps` | four `{title, text}` steps drawn as numbered cards above the vetting text on the home page; write them from the `vetting` copy | a generic four-step set |
| `foldMaxKm` | under-floor towns further than this from any city page get a page of their own, indexed and in the sitemap, listed under "Smaller towns" on the state hub and left out of the navigation; they need an entry in `city-copy.json` like any city page (120-word floor, 2 to 6 FAQs). `0` means no cap. `04-plan.md` may change it and says how many town pages the value produces | `40` (km, the pilot's value) |
| `cityFilter` | a filter field over the full city list on the home page | off |
| `vetting`, `stateIntro` | paragraphs for "How listings are vetted" and the state hub intro | the skeleton's text, none |

| `heroPoints` | short true statements shown with check marks under the hero buttons | none |
| `footerAbout` | the paragraph in the footer's About column | a sentence built from the brand, niche and state |
| `featuredPreview` | `true` fills unsold featured positions with the page's best real listings so the design can be reviewed; the cards carry `data-preview` and `scripts/check_live.py` refuses a live site that shows them. Must be `false` at launch. | `false` |
| (listings.csv) `socials` | optional column, `facebook=url\|instagram=url\|...`, written by `scripts/add_socials.py` from what `scripts/fetch_sites.py --socials` found on each business's own site; rendered as icons under Contact on the listing page and as `sameAs` in its schema (networks: facebook, instagram, x, linkedin, youtube, tiktok, pinterest) | none |
| `niche.schemaType` | the schema.org type of every listed business: the closest `LocalBusiness` subtype for the vertical (`RoofingContractor`, `Plumber`, `Electrician`, `HVACBusiness`, `GeneralContractor`, `Locksmith`, `MovingCompany`, `HousePainter`, `Dentist` ...). Set at Gate 4; only a type that exists on schema.org, otherwise leave the default | `LocalBusiness` |
| `design.favicon` | path of a favicon file of your own in `public/` (for example `/favicon.png`) | the generated `/favicon.svg` |
| `design.gold` | highlight color for headings on dark bands (the featured band) | `#F5B940` |
| `design.goldLight`, `design.goldDeep` | the light and deep ends of the gold gradient on featured ribbons and card bands | `#FFD86B`, `#D9950F` |
| `disclaimer` | the Disclaimer card in the listing-page sidebar (the pilot names the state licensing board) | a generic paragraph: public sources, independent businesses, no license or insurance check |
| `publisher.sameAs` | profile links; the footer shows an icon for Facebook, Instagram, LinkedIn, YouTube, X, Pinterest and TikTok | none |

## Search

The home page hero and the `/search/` page carry the same form (`src/components/SearchForm.astro`): a two-box search (what, and near) with suggestions as you type. The first box's list offers matching services first (a pick becomes a chip inside the box, Backspace on an empty box removes the last one) and businesses after them (a pick opens the listing). There is no server: `src/pages/search-index.json.ts` writes `search-index.json` at build time (every listing and city page, small fields plus the confirmed services, about 200 bytes per listing) and `public/search.js` fetches it the first time a visitor touches a box. Picking a city fills the city box. Nothing searches until Search is pressed (or Enter): that opens `/search/?s=&near=&f=` (noindex, out of the sitemap), which renders the matching listings and can be shared as a link. Filters combine as AND. "Near me" uses the browser's location to pick the nearest city page, with an eight-second timeout. Without JavaScript the search page points the visitor to the state hub.

Web fonts: self-hosted `@fontsource` imports in `src/styles/fonts.css` with the packages in `package.json`. The skeleton ships the master template's pair, Roboto Slab 800 for headings and Roboto for body; swap both when Gate 4 derives another pair from a design pointer, and check the license (SIL OFL or similar).

`dump-cities.mjs` (in the site folder, run at Gate 5) exports the city structure exactly as the site builds it, folds included, for `scripts/make_city_packets.py`: `node dump-cities.mjs [05-zip-county.json] ../05-cities.json`. The first argument is optional: a JSON object mapping five-digit ZIP codes to county names (`{ "80202": "Denver County", ... }`), built from a public ZIP-to-county table, so every packet can name the county of each listing. Without it the script says so on one line and uses the CSV's own `county` column, which a DataForSEO pull leaves blank and an Outscraper export sometimes fills with a neighborhood name, so the packets' county line may be empty and the city copy leans on the fact sheet for county facts instead.

## Build and deploy

```
npm install
npm run build        # -> dist/
```
On npm 11 `npm install` prints `npm warn allow-scripts 3 packages have install scripts not yet covered by allowScripts` naming esbuild and sharp. It is a warning, not an error; the build still passes, and the member may ignore it (or run the `npm approve-scripts` line it suggests).
Cloudflare Pages: connect the repo, framework preset Astro, build command `npm run build`, output `dist`. Or upload `dist/` by hand. Rebuild and redeploy on every CSV change.

## Looking at the build on your own computer
`dist/` uses paths that start at the domain root (`/_astro/...`, `/directory/florida/miami/`). Served by a web server it is correct. Opened as a file it has no styling and dead links.

- **Default:** double-click `preview-site.command` (Mac) or `preview-site.bat` (Windows). It installs and builds if needed, then runs `astro preview --open`. Nothing is copied and what you see is what deploys.
- **To hand someone a folder:** `python3 scripts/make_local_preview.py <site>/dist <output>/preview` writes a copy with relative paths and the stylesheet inside each page. Deploy `dist/`, never the copy.

A `<base href>` tag does not solve this. It only changes how relative URLs resolve, and these URLs start with a slash, which a browser resolves against the root of the disk. Tested on the pilot.

## Two Astro compiler quirks to keep in mind when editing pages
- `set:html` does not work on an element inside a `.map()` expression. Build the HTML string first and put `set:html` on the wrapper (see `paragraphs()` in `src/lib/load.mjs` and `JsonLd.astro`).
- `<p>` elements inside a `.map()` expression fail to compile. Use `paragraphs()` for lists of paragraphs.
