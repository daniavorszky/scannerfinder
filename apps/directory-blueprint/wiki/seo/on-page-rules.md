---
title: On-Page SEO Rules
type: seo
status: draft
updated: 2026-09-30
---

# On-Page SEO Rules

- **Titles:** city page `[Niche] in [City], [ST] ([N] Listed) | [Brand]`; listing `[Business] | [Niche] in [City], [ST]`; state hub `[Niche] in [State]: Every City | [Brand]`; home `[Niche] in [State] | [Brand]`.
- **Meta descriptions:** written for home, state and city pages from the data (count, top-rated, price range). Listing pages: first sentence of the description.
- One H1 per page. H2 for sections, H3 for cards. Listing cards are H3.
- Byline (name, link to About, dates) on every resource page. The home page buyer's guide carries no byline (the locked [[master-template]], 2026-09-30); the publisher is named on the home page in the vetting band ("Published by [Name]", linked to About), in the footer line and on About. Listing and city pages carry the `dateModified` line, no byline ([[publisher-entity]]).
- Internal links per [[site-architecture]]. Breadcrumbs on every page.
- Outbound business links `rel="nofollow"` unless featured.
- Images: `.webp`, lazy below the fold, alt = business name + niche + city. No hotlinking Google photos.
- Canonical absolute URL, `robots` per [[launch-lean]] (index or noindex), `theme-color`, Open Graph + Twitter card on every page.
- Pagination: none in v1. A city with more than 60 listings splits by sub-area only if the data supports it; otherwise cap the cards at 60 sorted by featured, then rating x reviews, and keep the rest reachable from an "All [N] [niche] in [city]" list block.
- Site speed: static, no client JS except the claim form validation. One member's rebuild went 89 to 96 mobile PageSpeed on the same stack.

## See also
[[schema]] · [[launch-lean]]
