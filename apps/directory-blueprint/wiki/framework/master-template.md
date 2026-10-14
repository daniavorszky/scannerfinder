---
title: The Master Template
type: framework
status: locked by Shawn, 2026-09-30
updated: 2026-10-05 (see-all button, service links, related listings, favicon)
---

# The Master Template

`templates/astro/` is the directory. Its structure, page set, section order and interaction patterns are the Blueprint's default and carry the most weight in every build. The sites a member names at Gate 1 are **design pointers**: they lend a palette, a type pairing, a card and button style, imagery direction, and at most a page pattern or two. They never replace the structure below. When a pointer and the template disagree on structure, the template wins; when they disagree on look, the pointer wins, subject to the [[design-seed]] tells and the contrast check.

Decided by Shawn on 2026-09-30 after twelve rounds of design review on the Florida pool builders pilot. The result of those rounds is what `templates/astro/` builds, and the reference site in `templates/master-reference/site/` is that build as finished HTML: the first reference in every build and the look a member gets when they name no site of their own (Shawn, 2026-10-01).

## Where it lives

- **The template:** `templates/astro/` in this folder. Its `src/data/site.json`, `src/styles/fonts.css` and `package.json` ship the reference build's look as the defaults (navy `#0B2545`, amber action `#F5A623` with navy text, Roboto Slab 800 and Roboto, 8px radius), so a build with no design pointer looks like the reference build.
- **The reference site:** `templates/master-reference/site/` is the whole reference build as HTML, 1,719 pages: `templates/astro/` rendered on the first real directory's data (a pool builders directory for Florida, 1,557 listings, 145 city and town pages). It is the heaviest-weighted example in every build and comes before any other reference: Gate 4 reads its pages when a member's pointer is weighed against the template, Gate 5 compares the built home, state, city and listing pages against the same pages there (same sections, same order, same markup patterns), and a build with no design pointer should look like it. Read the HTML directly: `site/index.html` (home), `site/directory/index.html` (browse), `site/directory/florida/index.html` (state hub), `site/directory/florida/naples/index.html` (a city), `site/directory/florida/vernon/index.html` (a small city), `site/company/florida/naples/classic-pools-of-naples-naples/index.html` (a listing), `site/featured/index.html`, `site/claim/index.html`, `site/about/index.html`, and `site/_astro/*.css` for the stylesheet. The member looks at it by asking Claude to show it (`python3 templates/master-reference/view_reference_site.py` serves it locally and opens the browser) or with `view-reference-site.command` or `.bat` in that folder.
- **What the reference site is not:** a source of content. Its listings, descriptions, city copy, FAQs, buyer's guide, publisher, contact details and domain belong to that directory and are never copied, quoted or reused in a member's build; every fact in a build comes from the member's own data. Its copy also predates two rules, and the rules win: descriptions there sometimes name their source ("its site says"), which [[enrichment]] now forbids, and its five town pages carry no copy band and no FAQ, which [[page-types]] now requires, so a town page is modelled on the small city page plus the town rules in [[page-types]], never on those five. Its claim form endpoint is a placeholder.
- **The screenshots** beside it (`home.png`, `city.png` and so on) are the same build at 1280px, for a quick look at the whole page when reading HTML is not enough.
- **The history:** the reference build is the first directory built with this Blueprint, after twelve rounds of design review.

## The weighting rule, in one line

**Structure from the template, look from the pointers, facts from the data.** A Gate 4 plan lists what the pointers change (tokens, fonts, imagery, one or two patterns) and nothing else; everything not listed is the template as shipped.

## Site structure

| Layer | URL | Role |
|---|---|---|
| Home | `/` | The ranking page for "[niche] in [state]": hero with search, stat row, city cards, featured band, highest-rated grid, claim callout, city index, vetting band, buyer's guide, FAQ. |
| Browse | `/directory/` | Search, every city A to Z, every listing by city. `noindex, follow`. The nav's niche link and the breadcrumb level between Home and the state. |
| State hub | `/directory/[state]/` | The by-city page: intro copy, featured band, every city with counts, smaller towns (under-floor pages kept by `foldMaxKm`; indexed and in the sitemap like any city page, with a 120-word band), FAQ. |
| City page | `/directory/[state]/[city]/` | The money page: key facts, place-first copy split around the cards, featured band, cards, overflow list, FAQ cards, nearby city cards, claim callout. |
| Listing | `/company/[state]/[city]/[slug]/` | One business: head with rating, two columns (About, Services, Contact and Hours on the left; map, Location, Claim, Disclaimer on the right). |
| Search | `/search/` | Client-side results from `search-index.json`. `noindex`. |
| Featured | `/featured/` | Tier cards, three steps, contact callout. Buttons open the claim form with the tier. |
| Claim, About, Contact, Privacy, Terms | root | As the template ships them. |

Breadcrumbs on every location and business page: Home › [Niche] › [State] › [City] › [Business], with chevrons, and the BreadcrumbList schema to match.

## Navigation

Brand wordmark on the left (the home link; there is no Home item), then the niche in plural (to `/directory/`), About, Contact, and one amber button, "Get listed", to the claim page. Navy bar, white text. The largest cities live in the footer, not the nav.

## Home page, section by section

1. **Hero.** Navy band. H1 "[Niche] in [State]" with the state in the action color. One line: "Ratings, services and a phone number for every [singular] in [State]." The search bar: one white pill with the what box, the city box and an amber Search button. Under it, one row of three short consumer promises with check marks (`heroPoints`, three or four words each). A small underlined text link to the buyer's guide. At the foot, the four figures as a quiet row with line icons: listings, cities, verified companies, Google reviews (`confirmedLabel` names the third). No buttons in the hero, no photo unless the member supplies one.
2. **Find [niche] in your city.** Tinted band, centered heading, the eight largest cities as white cards: name (H3), count, verified count. No colored borders. Under the cards, one button, "See all N cities", to section 7.
3. **Featured band.** Full-bleed navy, gold heading, up to three cards with a gold gradient band, a navy Featured tab, and a dashed "This position is open" card while positions are unsold. `featuredPreview` fills unsold positions with the page's best real listings for review, marked in the HTML, and must be off at launch. The costs link sits under the cards. The same band renders on the state hub and every city page (`FeaturedBand.astro`).
4. **Highest-rated [niche].** Six cards, rating weighted by review count, floor 4.5 and 25 reviews, confirmed builders only when `sortAttribute` is set.
5. **Claim callout.** The amber band: "Own a [singular] business in [State]?" with Claim your listing and Get featured.
6. **Find [niche] by service.** Only when the build has service pages ([[page-types]]): each service title with its count, linking to its page.
7. **Find [niche] by city.** Every city page as a four-column A to Z list, name left, count right, letter headings as plain text.
8. **How listings are vetted.** Tinted band, centered heading, four numbered steps (`vettingSteps`), the vetting text in a narrow measure.
9. **How to choose a [singular] in [State].** The buyer's guide as an article: centered title, lead paragraph, numbered H3s, no byline. The publisher is named on the home page in the vetting band ("Published by [Name]", linked to About), in the footer line and on About; a byline sits only on resource pages ([[on-page-rules]], [[publisher-entity]]).
10. **Frequently asked questions.** Question and answer cards in three columns with a question mark, every answer visible.

## City page

Tinted head with breadcrumbs, H1 "[Niche] in [City], [ST]" and the key facts as pills. First half of the copy, then the featured band, then "Best [niche] in [City]" as cards, then the overflow past `maxCardsPerCity` as "N more [niche] in [City]" in a compact list, then the second half of the copy, FAQ cards, "[Niche] near [City]" as city cards with H3s, and the claim callout. The copy follows the place-first rule in [[page-types]].

## Listing page

Head: breadcrumbs, mark, H1, rating line (stars, score, count with fixed gaps), "[Niche] listing in [City], [ST]". Source order under it: About, Services and details (confirmed services as tiles with a check and an H3 each, a stated No as a tile with a cross, the unknowns folded into one muted line, then the service pages the business appears on as chips), Contact and Hours, then "Other [niche] in [City]": four listings from the same city with their ratings and a link to the city page. On screen the contact box comes first. Sidebar: map embed (optimized and preview listings only), Location with Get directions, phone, website and Maps links, the claim card, the disclaimer card (`disclaimer`). Social profile icons under Contact when the business links them from its own site (`socials` column). Schema: the business type from `niche.schemaType` with `makesOffer` for confirmed services and `sameAs` for profiles, no rating markup ([[schema]]).

## Service page

Tinted head with breadcrumbs (Home, Services, the service), H1 "[Service title] in [State]" and the key facts as pills. The intro, the top listings as cards, "[Service title] by city" as the city list with counts, the other services, the claim callout. Built only for the attributes the plan names ([[page-types]]).

## Cards

Listing card: H3 name, rating line, address, up to three chips, phone with a handset icon pinned to the card's foot. City card: name, count, verified count. Featured card: gold band with the navy tab, city, rating, name, excerpt, chips, link.

## Settings that carry the look

`design.*` tokens (bg, surface, text, heading, headerBg, band, tint, accent, action at 7.6 to 1 against navy text, gold, goldLight, goldDeep, radius, shadow), `src/styles/fonts.css` for self-hosted fonts, `heroImage` when the member supplies one. Everything else is structure and stays.

## What a design pointer may change

- Colors, within the contrast rule, recorded with measurements in `04-plan.md`.
- Type pairing, openly licensed and self-hosted.
- Card radius and shadow, button radius.
- Hero imagery, member-owned or licensed.
- At most one or two page patterns, named in the plan, that do not remove a section above.

## What a design pointer may not change

The page set and URLs, the nav, the section order on any page, the search, the featured band and its preview mode, the attribute grid, the listing sidebar, the breadcrumbs, the footer's four columns, or any rule in [[page-types]], [[on-page-rules]], [[schema]] and [[launch-lean]].

## See also
[[design-seed]] · [[page-sections]] · [[page-types]] · [[site-architecture]]
