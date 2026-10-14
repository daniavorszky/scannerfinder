# Master template, the reference site

`site/` is the reference build: `templates/astro/` rendered on the first real directory's data (pool builders, Florida; 1,557 listings, 145 city and town pages, 1,719 pages), rebuilt 2026-10-05 from the template as it ships. It is the heaviest-weighted example in every build and the first reference to open (`wiki/framework/master-template.md`): the structure, the section order, the markup and the default look. A member who names no site of their own gets this look. A member's design pointers change colors, type, imagery and at most a page pattern or two, never what these pages contain or the order it comes in.

## Looking at it

The easy way: ask Claude to "show me the reference site". It runs `python3 templates/master-reference/view_reference_site.py`, which serves `site/` from this computer on a free port and opens the browser.

By hand: double-click `view-reference-site.command` (Mac) or `view-reference-site.bat` (Windows); close the window to stop it. If macOS refuses to open the file because it came from a download: right-click it, choose Open and confirm, or on macOS 15 and later open System Settings, Privacy & Security, and click Open Anyway. Do not open `site/index.html` by double-clicking: the pages use root paths and show unstyled from disk.

Claude reads the HTML directly:

| Page | File |
|---|---|
| Home | `site/index.html` |
| Browse (`noindex`) | `site/directory/index.html` |
| State hub | `site/directory/florida/index.html` |
| City page | `site/directory/florida/naples/index.html` |
| Small city page (six listings, short copy band, FAQ) | `site/directory/florida/vernon/index.html` |
| Listing page | `site/company/florida/naples/classic-pools-of-naples-naples/index.html` |
| Service page and the services index | `site/services/fiberglass-pools/index.html`, `site/services/index.html` |
| Featured, claim, about, contact | `site/featured/`, `site/claim/`, `site/about/`, `site/contact/` |
| Search, 404, sitemap, robots, headers | `site/search/`, `site/404.html`, `site/sitemap-0.xml`, `site/robots.txt`, `site/_headers` |
| Stylesheet and fonts | `site/_astro/` |

## What it is for, and what it is not for

- **For:** structure, section order, markup patterns, schema shape, the default look. Gate 4 weighs a design pointer against these pages; Gate 5 compares the built home, state, city and listing pages against the same pages here.
- **Not for content.** The listings, descriptions, city copy, FAQs, buyer's guide, publisher, contact details and domain belong to that directory. Nothing from them is copied, quoted or reused in another build; a member's facts come from the member's data.
- **Where it is behind the rules, the rules win.** Some descriptions name their source ("its site says"), which the enrichment rules now forbid, and its five town pages (Lake Placid, Old Town, Bell, Starke, Laurel Hill: one listing each) have no copy band and no FAQ, which the page rules now require, so they are not a model for a town page. A town page is the small city page above with a 120-word band and 2 to 6 FAQs (`wiki/framework/page-types.md`). The four service pages carry the data-driven fallback intro, not the 80 to 200 words a build writes at Gate 5. The claim form endpoint is a placeholder.
- Searching this folder for a rule or a setting returns thousands of pages. Search `wiki/`, `scripts/` and `templates/astro/` for those, and open the files in the table above by path.

## Screenshots

The PNG files are the build at 1280px wide, taken 2026-09-30 when the master template was locked, for a view of the whole page at once. They predate the 2026-10-05 additions (the "See all N cities" button, the service section and links, "Other [niche] in [City]" on the listing page); `site/` has them.

| File | Page |
|---|---|
| `home.png` | Home (cut at the fold of the city index; the hero is shown without its three promises) |
| `state-hub.png` | State hub |
| `city.png` | City page (Naples) |
| `listing.png` | Listing page |
| `featured.png` | Featured page |
| `browse.png` | Browse page |

In the screenshots the featured band shows `featuredPreview` on; in `site/` it is off, as at launch.
