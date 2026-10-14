# Featured tiers (edit per directory)

| Tier | Price | Placement | Payment Link |
|---|---|---|---|
| City featured | $29/mo | top card on one city page, followed link, photo | {{STRIPE_LINK_CITY}} |
| County featured | $99/mo | top card across a cluster of cities, featured mark on the listing page | {{STRIPE_LINK_COUNTY}} |
| State featured | $499/mo | home page block + every city page in the cluster, description rewrite, lead form | {{STRIPE_LINK_STATE}} |
| Premium listing | $97/yr | the optimized listing state (owner photos, all links followed, embedded map, hours) + the badge below | {{STRIPE_LINK_PREMIUM}} |
| Best-of placement | one-time, $100 floor, $750 to $1,200 typical | pinned position on the "best [niche] in [city]" list (`best_of_rank`), a press release (AB Newswire) whose three links go to the business's site, its listing page and the city best-of page, the badge | {{STRIPE_LINK_BESTOF}} |

Rules: one business per tier per city. Sold by hand. After payment, set the `featured` column for that listing to `city`, `county` or `state`, set `featured_cities` if county, rebuild, redeploy. Cancel = clear the column, rebuild. Premium sets `premium=true`; best-of sets `best_of_rank` (1 to 3) on the city page.

Prices are the video's monthly range plus receipts from operators in the community ($97 a year premium; best-of from $100, the floor that pays for the press release, up to $1,200; Trust Analytica charges $750 for a top-10 listing). Pick per directory; the pilot decides the default.

**Suggested default for a new directory:** premium $97/yr, best-of $250 one-time with the release, city featured $29/mo. Skip county and state featured until a city slot has sold. Used on the first directory built with this Blueprint.

## The badge (ships with premium and best-of)
Gate 5 generates `/badge/[business-slug].svg` and a snippet page at `/badge/[business-slug]/` the owner can copy:

```html
<a href="https://{{DOMAIN}}/{{STATE}}/{{CITY}}/{{BUSINESS_SLUG}}/" rel="noopener">
  <img src="https://{{DOMAIN}}/badge/{{BUSINESS_SLUG}}.svg" alt="{{BUSINESS_NAME}} is listed on {{BRAND}}" width="180" height="60">
</a>
```

The badge links to the business's own listing page, so every badge placed on an owner's site is a natural inbound link to the directory. Wording on the badge: "Verified {{NICHE}} on {{BRAND}}" for premium, "Best {{NICHE}} in {{CITY}} {{YEAR}}" for best-of. Send it as this HTML, never as an image file, and offer to install it: "send this to your developer or we'll do it for you". The snippet page at `/badge/[business-slug]/` carries the copy button and that offer.
