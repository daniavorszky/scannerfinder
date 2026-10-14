# Astro skeleton, one-screen file map

The real project lives in `templates/astro/` (see its README for what Gate 5 fills). This is the map.

```
templates/astro/
├── package.json              astro ^5, @astrojs/sitemap, @fontsource/roboto + roboto-slab
├── astro.config.mjs          site URL from site.json; sitemap filter drops noindex paths
├── src/
│   ├── data/                 site.json · listings.csv · attributes.json · city-copy.json   (the fills)
│   ├── lib/load.mjs          CSV parser, listing model, city floor + folding (foldMaxKm keeps remote towns as indexed pages), nearby cities,
│   │                         sort order, noindex set, hours parsing, FAQ fallbacks, paragraphs()
│   ├── styles/global.css     structure only; tokens come from site.json
│   ├── layouts/Base.astro    head, robots, canonical, OG, tokens, site-level JSON-LD, header, footer
│   ├── layouts/Resource.astro  markdown resource pages (Article schema, byline)
│   ├── components/           JsonLd · Breadcrumbs · Card · Rating · Faq · AttributeGrid · ClaimCta · FeaturedBand · DirectoryHub · SearchForm · SocialLinks · Byline
│   └── pages/
│       ├── index.astro                       home (the master template's hero, cities, featured band, guide, FAQ)
│       ├── directory/index.astro             browse page: search, every city, every listing (noindex)
│       ├── directory/[state]/index.astro     state hub
│       ├── directory/[state]/[city]/index.astro   city page = the money page
│       ├── company/[state]/[city]/[slug]/index.astro  listing page, basic or optimized
│       ├── search.astro · search-index.json.ts   client-side search (noindex)
│       ├── claim.astro · featured.astro · about.astro · contact.astro · privacy.astro · terms.astro · 404.astro
│       ├── resources/index.astro · resources/_example.md
│       ├── badge/[slug].svg.ts · badge/[slug]/index.astro
│       └── robots.txt.ts
├── public/                   search.js, _headers (Cloudflare), images/ (publisher photo, owner-supplied listing photos)
└── preview-site.command / .bat   double-click to serve dist/ as it deploys
```

Build: `npm run build` -> `dist/`. Look at it: `preview-site.command` (Mac) or `preview-site.bat` (Windows). Deploy: Cloudflare Pages with Wrangler (`npx wrangler pages deploy dist`). The structure is the [[master-template]].
