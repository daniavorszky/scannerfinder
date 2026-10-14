---
title: JSON-LD Schema per Page Type
type: seo
status: draft
updated: 2026-10-05 (no aggregateRating, business subtype, E.164)
---

# JSON-LD Schema per Page Type

The Microsite Blueprint's example site shipped with zero schema. Do not repeat that. Every page emits JSON-LD in `<head>`, generated from the CSV.

| Page | Types |
|---|---|
| Home | `WebSite` (+ `SearchAction` only if a search exists), `Organization` (the directory brand, with `founder` and `publisher` as the `Person` from Gate 1 and `sameAs` to the person's own site and profiles, [[publisher-entity]]), `ItemList` of featured businesses, `FAQPage` |
| State hub | `CollectionPage`, `ItemList` of city pages, `BreadcrumbList` |
| City page | `CollectionPage`, `ItemList` where each item is the business type (`@id` of the listing page's business, name, address, telephone, url = the listing page), `FAQPage` for the local FAQ block, `BreadcrumbList` |
| Service page | `CollectionPage`, `ItemList` of the business type (the cards shown), `BreadcrumbList`; the services index is a `CollectionPage` with an `ItemList` of the service pages |
| Listing page | The business type with `address`, `geo`, `telephone`, `url` (business site), `openingHoursSpecification` from `working_hours`, `makesOffer` for confirmed services, `image` only for claimed or featured listings with owner-supplied photos ([[page-types]] image policy); `BreadcrumbList` |
| About | `AboutPage`, `Person` (name, `url` = their personal site, `image`, `sameAs` profiles, `worksFor` or `owns` the directory `Organization`) |
| Resource page | `Article` with `author` = the `Person`, `publisher` = the `Organization`, `datePublished`, `dateModified`, `BreadcrumbList` |
| Claim / Featured / Badge snippet | `WebPage` only |

Rules: every `WebPage`, `CollectionPage` and `LocalBusiness` carries `datePublished` (first build) and `dateModified` (this build's date, so every rebuild is a refresh; [[refresh-and-upkeep]]); **no `aggregateRating` anywhere**; no `Review` objects (we do not host review text); one JSON-LD block per type. Validate a sample of each page type with the Rich Results test before Gate 6.

**No rating markup.** The stars on the page are Google's rating and are shown as such ("reviews on Google"). Google's review snippet rules do not allow marking up ratings or reviews taken from another website, and a local business type is not eligible for stars on ratings a site supplies about it, so `aggregateRating` built from the Maps data risks a structured data manual action for nothing. It was removed from the template on 2026-10-05 after a member's build flagged it. Ratings come back into the schema only if the directory collects its own reviews, which v1 does not.

**The business type.** `niche.schemaType` in `site.json` is the `@type` of every listed business. Gate 4 sets it to the closest `LocalBusiness` subtype that exists on schema.org for the vertical (`RoofingContractor`, `Plumber`, `Electrician`, `HVACBusiness`, `GeneralContractor`, `Locksmith`, `MovingCompany`, `HousePainter`, `Dentist`, `AutoRepair` ...) and records it in `04-plan.md`. When no subtype fits, `HomeAndConstructionBusiness` for a trade, else the default `LocalBusiness`. Never invent a type.

**Telephone** is written in E.164 (`+13055551234`) in the schema; the page shows the readable form.

The `Person` and `Organization` use one `@id` each across the site (`https://{{DOMAIN}}/#publisher`, `https://{{DOMAIN}}/#person`) so every page's markup points at the same two entities. The hierarchy starts at the person's own website; the directory's `sameAs` points there, and the personal site should point back.

## See also
[[on-page-rules]] · [[page-types]] · [[publisher-entity]]
