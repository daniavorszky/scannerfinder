---
title: Site Architecture and URL Structure
type: framework
status: draft
updated: 2026-10-05 (service pages, related listings)
---

# Site Architecture and URL Structure

One vertical, one state. Four content layers plus two utility pages.

## Page layers
| Layer | URL | Count | Ranks for |
|---|---|---|---|
| Home | `/` | 1 | `[niche] in [state]`, `[niche] near me` (state-wide) |
| State hub | `/directory/[state]/` | 1 (v1) | `[niche] in [state]` list intent; links every city |
| City page | `/directory/[state]/[city]/` | one per city with at least the minimum listings (see [[page-types]]) | `[niche] in [city]`, `best [niche] [city]` |
| Listing page | `/company/[state]/[city]/[business-slug]/` | one per kept listing | brand + service queries; the long tail |
| Service page (optional) | `/services/[service-slug]/`, index at `/services/` | one per attribute the plan names as a service and that at least the city floor of listings confirm | `[service] [niche] in [state]`: every listing confirmed for the service, the top ones as cards, then every city with its count ([[page-types]]). Indexed and in the sitemap |
| Claim | `/claim/` | 1 | conversion, not ranking |
| Featured / advertise | `/featured/` | 1 | conversion, not ranking |
| About | `/about/` | 1 | the publisher, trust for the cold call ([[publisher-entity]]) |
| Legal | `/privacy/`, `/terms/`, `/contact/` | 3 | realism |
| Resource (optional) | `/resources/[slug]/` | 0 at launch, added on request | linkable reference pages ([[authority-and-links]]) |
| Browse page | `/directory/` | 1 | the search box, every city A to Z and every listing by city; `noindex, follow`, an HTML sitemap with a search box. The nav's niche link and the crumb between Home and the state. Carries none of the home page's copy, so the two never compete |
| Badge snippet | `/badge/[business-slug]/` | one per premium or best-of listing | conversion, not ranking (`noindex`) |

One member's rebuild is the size reference: 4,796 pages generated, 1,028 in the sitemap at launch, thin profiles noindexed.

## URL rules
- Location pages sit under `/directory/`, business pages under `/company/`, both followed by the state's full name and the city: `/directory/florida/naples/` lists the city, `/company/florida/naples/pools-by-wyatt-naples/` is one business (decided by Shawn on 2026-09-30 after the Garage Door Galaxy teardown, which uses `/directory/` for its lists and `/company/south-carolina/anderson/waynes-overhead-doors` for a business). The state segment is derived from `state.name` in `site.json`; `state.slug` overrides it. `/directory/` is the browse-everything page (search, every city, every listing), `noindex, follow`, so the breadcrumb level "[niche]" resolves (Home / Pool Builders / Florida / Naples / Business) without a second copy of the home page. Decided by Shawn on 2026-09-30 over two alternatives: pointing the nav at the home page (the crumb and the nav would both link to `/`) and keeping a noindexed copy of the home page (wasteful). `/company/` and `/company/<state>/<city>/` redirect to the matching directory page through `dist/_redirects`. Resource pages, claim, featured, About and legal stay at the root.
- Lowercase, hyphenated, trailing slash, no `.html`, no query strings for filters. Every filter combination that should rank is a **real page** (one member's WordPress directory had service x city combos only as filter URLs and Google saw them as one page; that was the failure).
- Service pages are statewide in v1. Service by city (`/services/[service]/[city]/`) is not built: most such pages would hold one or two listings. The service page links every city with its count instead, and the city page's FAQ answers the service question for that city.
- No listing page is a dead end: each links four other listings from its city (the next four in the city's order, wrapping, so every listing is linked from four others), its city page, and the service pages it appears on.
- `business-slug` = `[name]-[city]` slugified; collisions get the postal code appended.
- Canonical absolute URL on every page.

## Internal linking (hub and spoke, two directions)
- Home links the state hub and the top 10 to 20 cities by listing count.
- State hub links every city page.
- City page links every listing in it, the featured slots first, the neighboring cities (nearest 5 by coordinates), and up to the state hub.
- Listing page links its city page and the claim page. **Listing pages link out to the business website with `rel="nofollow"` by default;** featured listings get a followed link (that is part of what the tier buys, [[monetization-slots]]).
- Breadcrumbs on every page (also as `BreadcrumbList`, [[schema]]).
- Resource pages link to the city pages they concern and are linked from them and from the footer. Never change a resource or listing URL once it has an inbound link ([[authority-and-links]]).
- **Owned microsites get exactly the same treatment as any other listing.** See [[footprint-rules]].

## Fold cap and sort attribute (pilot, 2026-09-29)
- `foldMaxKm` in `site.json`: an under-floor town further than this from every city page is not folded. It gets a page of its own, indexed and in the sitemap like any city page (Shawn, 2026-09-29), listed on the state hub under "Smaller towns" and left out of the navigation and the home grid. It needs a `city-copy.json` entry with the 120-word floor ([[page-types]]). Without a cap the pilot would have shown a Lake Placid business under Lake Wales, 68 km away. **Default: 40 km**, the pilot's value, shipped in the skeleton's `site.json`; a reader in a town 40 km from the nearest city page would not call that page "near me". Gate 4 may change it in `04-plan.md` (a sparse state wants a larger value, a dense one a smaller), with the number of town pages it produces stated next to the choice; the dry run of 2026-09-30 chose 60 km for Colorado and got 21 town pages.
- `sortAttribute` in `site.json`: listings where that attribute is true sort ahead of the rest, after paid positions. Optional; the pilot used its core-work attribute.
- Gate 4 decisions that remove or alter listings live in `04-exclusions.csv` and are applied by `scripts/apply_exclusions.py` when the listings are copied into the site. The enriched CSV is never edited. Every row is the member's decision; the Blueprint sets no default that drops a class of listing.

## Navigation
Top bar (base look, optional): listings and cities count, updated date, claim link. Header: logo, [State], top cities, Claim Your Listing, and one action button (Get Featured by default). Footer: About, Contact, Privacy, Terms, Resources (when any exist), the top cities, and the publisher line "[Brand] is published by [Name]" linking to About.

## See also
[[page-types]] · [[page-sections]] · [[on-page-rules]]
