---
status: active
owner: Dan Iavorszky
container_type: project
primary_area: 02-areas/new-business/_overview.md
related_areas: []
claude_role: Operator pentru lansarea directorului scannerfinder.com — extragere și curățare date, structură director, formular de înscriere, conținut. Întreabă pentru Red (cheltuieli API peste buget, publicare, outreach către cabinete, cumpărări).
last_updated: 2026-10-14
---

# ScannerFinder.com — directory launch

## Purpose

scannerfinder.com devine directorul de referință pentru cabinetele/practicienii care oferă scanări bioenergetice (ZYTO, iTOVi, NES, AO Scan, Healy etc.), pe 7 țări, cu profile verificate și informații pe care nu le publică nimeni altcineva (preț ședință, transparență comercială, certificare producător).

## Success Criteria

- Baza de date inițială extrasă (DataForSEO, 7 țări × 10 branduri), curățată de dubluri, producători și distribuitori.
- Formularul de înscriere în 2 pași live (pas 1 obligatoriu, pas 2 profil extins), cu declarațiile legale (nu e diagnostic medical, GDPR, acord comercial separat).
- Directorul publicat pe scannerfinder.com cu listări per țară/oraș/brand. ✅ 2026-10-12 (țară → regiune → listare + pagini pe aparat)

## Load First

- Business plan (2026-10-09): [research/business-plan-2026-10-09.pdf](research/business-plan-2026-10-09.pdf) — originalul e un Claude Doc în claude.ai. Piață, branduri, model de venit, plan de lansare în 6 pași, riscuri.
- Area: [new-business](../../02-areas/new-business/_overview.md)
- Context de nișă: niciun aparat nu are validare științifică ca instrument de diagnostic → toate textele în registru „wellness”, niciodată „diagnostic/tratament”.

## Current Plan

1. **Baza de date** — extragere ✅ 2026-10-11, curățare automată ✅; rămâne review manual (72) + îmbogățire email. ← *în lucru*
2. Formularul de înscriere → **plan 2026-10-14: [research/claim-flow-plan.md](research/claim-flow-plan.md)** (revendicare în 3 pași, benchmark privat ca lead magnet, D1 + Functions pe Cloudflare, Stripe Checkout). Așteaptă deciziile din Faza 0.
3. Restul pașilor din „Plan de lansare” din business plan.

## Decisions

- 2026-10-11: Proiect creat sub `new-business` (precedent: cele-mai-bune.ro — venture propriu în fază de validare).
- Formular în 2 pași; profil extins răsplătit cu vizibilitate (ordonare după % profil complet).
- 2026-10-12: prețul ședinței se publică doar după confirmarea practicianului (nu direct din ce am găsit pe site).
- Trei câmpuri diferențiatoare: preț ședință, transparență comercială, certificare producător (insignă „verificat”).
- 2026-10-12: Prima unealtă de date proprietare = Device Price Index („dai prețul tău → vezi prețurile tuturor”) + ROI Calculator; cold start rezolvat cu prețuri publice (seed). Prototip local, hosting decis la pasul 2.

- 2026-10-12: The directory is built with the Directory Blueprint kit (Gate 1 in progress, [01-scope.md](apps/directory-blueprint/output/scannerfinder/01-scope.md)). The money pages are the device-brand pages (brand × country), not the city pages: 652 cities, only 28 with ≥3 listings.

- 2026-10-13 (DE + RO): animal-only practices (190, Tierheilpraxis/vets) stay **out** of the directory; Claude's first-pass review of DE/RO confirmed by Dan; **Germany = contact forms only**, never cold email (UWG §7) — Dan wants an explicit warning every time (`build_invites.py` prints it); 58 German listings without a city fixed via Impressum (35) or address district + postcode (23) → [city_overrides.csv](data/batch-de-ro/city_overrides.csv).

- 2026-10-12: Gate 3 — descriptions rewritten by AI in the wellness register (no medical claims, no prices; [03-wellness-rules.md](apps/directory-blueprint/output/scannerfinder/03-wellness-rules.md)). The business's Google description counts as its own words for marking the device. Pilot of 20 approved (tone + length).

- 2026-10-13: No paid indexing (Omega); indexing happens naturally from the sitemap.
- 2026-10-13: Every device × country combination gets a page (so a country hub never sends a visitor to the global device list); pages under `cityFloor` (3) are `noindex` and stay out of the sitemap.
- 2026-10-13: Listings show the business's **logo** (cards on region/device/search pages + listing header) — a logo is the business's own mark, not a photo, so it overrides the Blueprint's "no photos on unclaimed listings" rule. Sources: Google profile logo ([scripts/fetch_logos.py](scripts/fetch_logos.py)), then the business's site ([scripts/fetch_site_logos.py](scripts/fetch_site_logos.py)); bad ones reviewed by eye → [data/logos-rejected.txt](data/logos-rejected.txt). 569/809 have a logo (DE/RO 2026-10-14: 594/825, 11 rejected); the rest show initials. Files >40 KB downscaled to 176 px with `sips` (originals in `data/logos-original/`). Logo removed on request.
- 2026-10-13: **Tools** section in the main nav (`/tools/`, entries in `site/src/data/tools.json`; noindex while empty). First tool: [ROI Calculator](apps/directory-blueprint/output/scannerfinder/site/src/pages/tools/roi-calculator.astro), ported from [price-tools](apps/price-tools/_overview.md) with the lead form posting to **FormSubmit.co** → scannerfinder_leads@emailr.eu (Dan chose FormSubmit 2026-10-13; `site.json contact.leadsEndpoint`). FormSubmit activated by Dan 2026-10-13; delivery confirmed with a test lead. Privacy page updated (distributors only with the opt-in box).
- 2026-10-13: **Typography copied from mypeptidematch.com** (Dan): headings Saira Condensed (self-hosted woff2 in `site/public/fonts/`, H1 32→60px/700, H2 26→34px/800, H3 19px/700), body/nav/footer in the system UI font (body 16px, nav 15px/600, footer links 14px, footer text 13px, footer headings 12px uppercase). Replaces Nunito Sans.
- 2026-10-13: Region pages get a **listing explorer** (inspired by mypeptidematch.com/clinics/<state>): live filters on the left (technology, options, minimum rating, town), sort, a Leaflet map with numbered pins (Leaflet 1.9.4 self-hosted in `site/public/vendor/`, OpenStreetMap tiles loaded only when the map scrolls into view; privacy page says so), then the cards. All cards stay in the HTML for SEO. Files: `ListingExplorer.astro`, `public/explorer.js`.
- 2026-10-13: **Publisher changed from Andrei Ploiesteanu to DGA** (DigitalGuild Agency, Organization schema, links to https://digitalguild.agency, no social profiles yet). Andrei's photo moved to `data/archive/`. Logo: `site/public/images/dga-logo.png` (from Dan).
- 2026-10-13: Header menu **Practitioners** ▾ (Find Practitioners → /search/, Browse by Country → /directory/, Best Practitioners in <year> → new data-driven page /best-practitioners/ [top 6 per country by rating × reviews, min 5 reviews], Claim your Listing → /claim/). "Countries" stays in the menu (Dan). Ranking excludes slugs in `site.json bestExclude` (the UK psychic medium, kept in the directory).
- 2026-10-13: Search form = **Technology dropdown → Region or town → Practitioner name (optional)** (technology is the main criterion, Dan). Technology alone → /devices/<tech>/; technology + exact country → /devices/<tech>/<country>/; anything else → /search/ with the technology as a filter. With a technology picked, the location suggestions show counts for that technology only (zero-count places hidden).
- 2026-10-13: **Blog** live at /blog/ (header + footer link). Index modelled on mypeptidematch.com/blog (eyebrow, search, category pills, featured post, Latest Articles, Stay up to date); article page on its post layout (category, tags, byline, share, Key Takeaways, sticky On-this-page TOC, Related Tools, CTA, visible FAQ, Continue Reading). Posts = Markdown in `site/src/content/blog/<slug>.md` (`draft: true` dev only; `placeholder: true` built but noindex + out of sitemap; /blog/ noindex until one real post). 3 lorem ipsum placeholder posts live (Dan) — replace with real articles. "Countries" removed from the header (Dan, 2026-10-13); /directory/ reachable via Practitioners → Browse by Country and the footer.
- 2026-10-14: **Aggregated session prices (median/range per device) are not published.** They're the main incentive for practices to claim their listing and fill in their business data; once a practice has claimed and updated its listing, it sees how it compares with the rest (Dan). ROI Calculator (Dan's choice 2026-10-14): medians and ranges removed, session price field starts empty with a hint "how your price compares → Claim your listing"; no payback until a price is entered. Live 2026-10-14 (checked: 0 medians in the HTML).
- 2026-10-14: **Flux de revendicare** ([plan](research/claim-flow-plan.md), Dan): lead magnet = benchmark privat imediat (prețul tău vs oraș/țară/aparat, n ≥ 5) + raport anual bonus; revendicarea e **gratuită permanent**, Premium $97/an e upsell (invitația a fost corectată); email tranzacțional pe setup-ul m.scannerfinder.com; Stripe = contul existent Neocomm, întâi test mode.
- 2026-10-14: **Tracking = Matomo** (stats.mkstack.com, site 3, server UE, fără cookie-uri; Dan), nu D1: evenimente pe listări + Site Search (căutările fără rezultat = white space). D1 `scannerfinder` (UE) creat pentru revendicări; `wrangler.toml` + `functions/` adăugate în site. Detalii: [plan § Faza 1](research/claim-flow-plan.md).
- 2026-10-14: **Faza 2: revendicarea, construită** (/claim/ → /claim/verify/ → /claim/profile/, API în `functions/api/claim/`, emailuri Maileroo de pe notify.scannerfinder.com, fără R2: certificarea se dovedește prin link). Testată local cap-coadă. Live după ce Dan pune secretul `MAILEROO_API_KEY` și rulează `sfdeploy`. Detalii: [plan § Faza 2](research/claim-flow-plan.md).
- 2026-10-14: **Prețul ședinței e privat implicit** (Dan): public doar dacă practicianul alege explicit; folosit oricum în benchmark și rapoarte (n ≥ 5). Aprobarea profilurilor = automat pentru proprietar confirmat + lint curat, manual (Dan sună) pentru restul. [plan](research/claim-flow-plan.md)
- 2026-10-13: Service/device copy in `attributes.json` may write `{n}` / `{n:US}` instead of counts (filled by `load.mjs` at build), so totals never go stale; optional `service.guide` (sections, faqs, sources, seoTitle/seoDescription) renders only on the brand page. Content and plan: [2026-10-scannerfinder-seo-content](../2026-10-scannerfinder-seo-content/_overview.md).
- 2026-10-13: **/affiliate-disclosure/** (footer link, noindex like the other legal pages). States the three planned revenue sources (Dan, 2026-10-13): premium practitioner listings (never affect organic ranking), lead generation (opt-in distributor quotes from tools; consultation requests via listings are not planned soon — removed), affiliate partnerships (`rel="sponsored"`). If any of these changes, update that page.
- 2026-10-14: **/llms.txt** generated at build (`site/src/pages/llms.txt.ts`) from the site data: summary, guides, countries, technologies, tools, real blog posts (placeholders excluded), policies. No per-page Markdown mirror: AI crawlers read the HTML (Ahrefs 2026: 97% of llms.txt files get zero requests); the lever for AI citations is data-dense content.
- 2026-10-14: **/statistics/** (Practitioners menu + footer + llms.txt): original data built from listings (`site/src/lib/stats.mjs`) — device × country matrix with leader per country, technology profiles (share, remote %), remote sessions by country, share naming a device, practice types; methodology, Dataset schema, `/statistics.csv` (CC BY 4.0), cite box. No prices and no average ratings yet (prices = aggregated medians only, on Dan's word). "In numbers" blocks (`StatBlock.astro`, `countryBlock`/`deviceBlock`/`deviceCountryBlock` in stats.mjs) on every country, device and device × country page, linking to /statistics/.
- 2026-10-14: **Session price medians** added (Dan): `scripts/export_session_prices.py` → `site/src/data/session-prices.json` (build-only, slug → USD; medium/high confidence, $10–$1,000; 178 of 1,634 listings). Shown only as medians with n ≥ 5: /statistics/ "What a scan session costs" (by device and country), price sentence in the "in numbers" blocks, CSV columns. Overall median $127 (n=178). Re-run the script after new price extraction. ROI Calculator has no session-price defaults (removed by another session 2026-10-14 01:40), so nothing to sync.
- 2026-10-14: **Location pages (Dan):** every region and every town with ≥1 listing gets a page (`regionFloor: 1` in site.json; towns at `/directory/<country>/<region>/<town>/`, `[town]/index.astro`). Under `cityFloor` (3) → rendered but noindex + out of sitemap; a town holding all of its region's listings is noindex too (duplicate). Country pages carry the region explorer (map + filters, region filter) capped at 60 cards, the rest as links. `cityFloor` still gates device × country pages.

**Next decision (Dan, deschis 2026-10-14):** de pe ce domeniu pleacă invitațiile cold. Variante: (1) Instantly DFY pe un domeniu separat (libere: getscannerfinder.com, scannerfinderhq.com, tryscannerfinder.com, scannerfinder.org), (2) m.scannerfinder.com cu Google Workspace/Zoho conectat la Instantly. Instantly: plan AppSumo Lifetime Tier 3 (25k leaduri); singurele căsuțe sunt pe adola.ro (client), deci nu se folosesc. Apoi 2–3 săptămâni de warm-up. Între timp, de scris: secvența de invitație actualizată (benchmark în loc de Price Index, „free”) și emailul „your profile is live”. GB/ZA/DE doar prin formular de contact.

## Risks And Constraints

- Legal: afirmații medicale (UE/UK/SUA) — publisher-ul trebuie protejat prin declarații bifate.
- Calitatea datelor: mulți distribuitori MLM (Solex, Healy World) vor apărea ca „cabinete”.
- Scope (din plan): țări US, GB, CA, AU, ZA, IE, NZ (lansare US+GB). Branduri de bază: ZYTO, BICOM, Asyra/Qest4, NES Health, Rayonex, NLS (Metatron/Oberon/Hunter 4025); secundare: SCIO/Indigo/Eductor, MORA, TimeWaver, AO Scan. Excluse: Healy, iTOVi, analizoare chinezești.
- Cererea scade (−33% YoY la „zyto scan”); proiect = venit secundar (~1.100 USD/lună în anul 2, ipoteză).
- NES Health: neshealth.com redirecționează la e4l.com — de verificat rebrand.

## Artifacts

- Raport de stare 2026-10-14 (toate sesiunile, problema curentă = 301 Rustenburg): [drafts/raport-status-2026-10-14.md](drafts/raport-status-2026-10-14.md)
- Draft invitație tier A: [drafts/invite-email.md](drafts/invite-email.md) + [invite_tier_A_email.csv](data/invite_tier_A_email.csv) (53) + [invite_tier_A_contact.csv](data/invite_tier_A_contact.csv) (33), netrimis — blocat de pagina de revendicare + setup m.scannerfinder.com
- Research: [business plan PDF](research/business-plan-2026-10-09.pdf), [idei date proprietare](research/proprietary-data-ideas.md) (2026-10-12, nedecise — input pentru formularul pas 2)
- Directory Blueprint (kit Rank Expand Academy, adăugat 2026-10-12): [apps/directory-blueprint/](apps/directory-blueprint/_overview.md) — Astro → Cloudflare Pages, 6 porți; adaptat la 7 țări + nișă wellness (tabelul de adaptări în overview).
- Price tools (prototip): [apps/price-tools/](apps/price-tools/_overview.md), spec [device-price-tools-spec.md](research/device-price-tools-spec.md), seed [device-prices-seed.csv](data/device-prices-seed.csv) (23 rânduri, 2026-10-12)
- SEO content (separate project, 2026-10-13): [2026-10-scannerfinder-seo-content](../2026-10-scannerfinder-seo-content/_overview.md): MyPeptideMatch analysis + keyword map US/UK/DE/RO
- Scripts: [extract_listings.py](scripts/extract_listings.py), [clean_listings.py](scripts/clean_listings.py)
- Data: `data/raw_listings.jsonl` (brut API), `listings_flat.csv`, `listings_classified.csv`, `listings_include.csv`, `listings_review.csv`

## Handoff

**Pasul 1 — extragere făcută 2026-10-11** ($6.61 credit DataForSEO, sold rămas ~$40.6). 1.023 firme unice → clasificate cu [clean_listings.py](scripts/clean_listings.py): **787 include / 72 review / 164 exclude**.
- Include pe țări: US 371 · GB 177 · AU 77 · ZA 73 · CA 62 · NZ 16 · IE 11 (planul estima min. 410).
- Aparat identificat explicit: ZYTO 136, SCIO/Indigo/Eductor 107, Asyra 49, AO Scan 49, NES 20, BICOM 17, NLS 14, MORA 7, TimeWaver 4, Rayonex 3; restul de 386 = „bioresonance” fără brand în descriere.
- Contact: 732 telefon, 664 site, doar 198 email → emailurile lipsă trebuie îmbogățite înainte de pasul 3 (invitații).
- Fișiere: [listings_include.csv](data/listings_include.csv), [listings_review.csv](data/listings_review.csv), [listings_classified.csv](data/listings_classified.csv) (toate, cu status/motiv/flags).

**Review manual făcut** (57 păstrate / 15 respinse, salvate în [manual_review.csv](data/manual_review.csv) și aplicate automat de clean_listings.py) → **844 include**.
**Emailuri** — crawl propriu ([find_emails.py](scripts/find_emails.py), gratuit): 504/844 cu email (244 pe domeniul propriu, 183 alt domeniu de pe site, 77 doar DataForSEO). Output: [listings_include_emails.csv](data/listings_include_emails.csv). 138 site-uri inaccesibile, 136 fără email pe site, 139 fără site.
**ManyCrawl** (app desktop + MCP `manycrawl`): tabel `session_1791752214646_da25jdqkl`, coloana `website_emails` — terminat 2026-10-12 (~13 min, gratuit): 457/663 domenii cu email. Export → `data/manycrawl_emails.json` → [merge_manycrawl.py](scripts/merge_manycrawl.py) → **[listings_final.csv](data/listings_final.csv)**.
**Rezultat final: 531/844 cu email (63%)** — 295 pe domeniul propriu, 202 freemail (Gmail etc., normal la practicieni solo), 34 `third-party?` de verificat. ManyCrawl și crawl-ul propriu coincid în 90% din cazuri (340/378); ManyCrawl a umplut 37 de goluri. Rămân 313 fără email (telefon/formular).

**Pagini de contact + formular** (2026-10-12, gratuit, scriptul `enrich_contacts.py` din skill-ul outscraper-forms-emails, cache `data/contact_cache.jsonl`): coloane `contact_page_url` + `contact_form` în **[listings_final_contact.csv](data/listings_final_contact.csv)** = fișierul master actual. Formular: 277 pe pagina de contact + 42 pe homepage. Paginile de platformă (Facebook, Booksy, Linktree etc.) marcate „platformă (fără site propriu)”. **584/844 contactabile** prin email sau formular; 260 doar telefon.

**Price tools** (2026-10-12): prototip funcțional în [apps/price-tools/](apps/price-tools/_overview.md) — Device Price Index cu gate + ROI Calculator, branding scannerfinder.com. Site-ul live e pe SpreadSimple și încă promovează iTOVi (exclus în plan) → de aliniat.

**Îmbogățire site (2026-10-12, gratuit, reguli fără AI)** — [enrich_site_details.py](scripts/enrich_site_details.py), cache `data/site_text_cache.jsonl` (textul paginilor, refolosibil pentru AI mai târziu) → **[listings_enriched.csv](data/listings_enriched.csv) = fișierul master actual**. Aparat cunoscut: 519/844 (+105 doar de pe site); preț candidat 208, durată 260, scanare la distanță 102 — toate cu fragment-sursă, prețurile sunt *candidate* (includ și alte servicii). 325 fără aparat identificat.

**Kit de construcție (2026-10-12):** Dan a adus [Directory Blueprint](apps/directory-blueprint/_overview.md) (Astro static + Cloudflare Pages). Site-ul live actual e pe SpreadSimple → decizie de stack înainte de poarta 5.

**Profilare (2026-10-12)** — [enrich_profile.py](scripts/enrich_profile.py) (reguli pe cache, gratuit) + prețuri citite de AI (5 sub-agenți Sonnet pe fragmentele de preț din `data/price_batches/`, unite cu [merge_prices.py](scripts/merge_prices.py)) → **[listings_profiled.csv](data/listings_profiled.csv) = fișierul master actual**. Model aparat 139, tip practician 701 (283 doar „holistic” generic), credențiale 39, platformă programări 110, suplimente 35, semnal MLM 86, consultație gratuită 71, animale 14 (verificate manual), pachete 25. **Preț scanare: 148 cabinete** (high 58 / medium 73 / low 17), mediană 150 $; pe brand: ZYTO 95 $, AO Scan 88 $, SCIO 125 $, Asyra 159 $, Rayonex 172 $, NLS 195 $, BICOM 208 $ → folosite ca valori implicite în calculatorul ROI. `business_type` marchează 9 non-practicieni (4 vânzători de aparate, 3 MLM, 2 training) — de exclus din director, dar distribuitorii sunt parteneri potențiali pentru comision.

**Excluderi + aparate + tehnologii (2026-10-12)** — 13 excluși (9 vânzători aparate / MLM / training + 4 fără scanare), salvați în [manual_review.csv](data/manual_review.csv); distribuitorii păstrați ca parteneri potențiali în [partner_candidates.csv](data/partner_candidates.csv). AI pe cele 325 fără aparat ([merge_devices.py](scripts/merge_devices.py), loturi în `data/device_batches/`): 266 oferă clar scanare, dar majoritatea nu numesc aparatul („bioresonance therapy”); 30 aparate în afara listei (Monicor, Ondamed, Harmonic Egg, FCT…) în `device_other`. Familie de aparat cunoscută: 532/831. Tehnologii din HTML-ul homepage-ului ([detect_site_tech.py](scripts/detect_site_tech.py), gratuit — DataForSEO Technologies acoperea doar 2/5 site-uri mici și nu vede pixelii): **65 plătesc reclame** (Meta Pixel 44, Google Ads 20), booking embed 111, Mailchimp 27, WordPress 194 / Wix 54 / Squarespace 51. `invite_score` / `invite_tier` (pixel reclame +3; profil revendicat, site, booking, preț publicat, email, ≥10 review-uri, tool email +1): **A 86 (81 cu email; US 42, GB 26)**, B 247, C 498.
Ordinea pipeline-ului: `enrich_site_details.py` → `enrich_profile.py` → `merge_prices.py` → `detect_site_tech.py` → `merge_devices.py` (rularea lui `enrich_profile.py` regenerează fișierul fără coloanele de după; excluderile manuale se re-aplică din `manual_review.csv` doar prin `clean_listings.py`).

**Export public pentru director (2026-10-12)** — [export_directory.py](scripts/export_directory.py) → **[directory_listings.csv](data/directory_listings.csv) = fișierul pentru site**: 831 practicieni (doar `include`), 35 coloane publice (fără emailuri, scoruri, pixeli, MLM, fragmente-sursă), `slug` unic, `profile_completeness` % pentru ordonare. Master intern rămâne [listings_profiled.csv](data/listings_profiled.csv). Decis 2026-10-12: prețurile găsite pe site-uri (147) se afișează **doar după confirmarea practicianului** — exportul le lasă goale cât `claimed_on_scannerfinder` ≠ yes; rămân în master pentru pre-completarea formularului de revendicare.

**Directory Blueprint — Gates 1–2 (2026-10-12):** Gate 1 approved ([01-scope.md](apps/directory-blueprint/output/scannerfinder/01-scope.md): publisher Andrei Ploiesteanu, ScannerFinder brand look, money pages = device brands). Gate 2 with [blueprint_gate2.py](scripts/blueprint_gate2.py) → [02-listings-clean.csv](apps/directory-blueprint/output/scannerfinder/02-listings-clean.csv) (819, kit layout + our profile columns, no emails) + [02-clean-report.md](apps/directory-blueprint/output/scannerfinder/02-clean-report.md). Zero-review (213) and stale (30) rows are flagged, not dropped — decision at Gate 4.

**Gate 3 (2026-10-12):** 819 descriptions rewritten in the wellness register + 14 attributes → [03-listings-enriched.csv](apps/directory-blueprint/output/scannerfinder/03-listings-enriched.csv), report [03-enrich-report.md](apps/directory-blueprint/output/scannerfinder/03-enrich-report.md). Pipeline: kit's `fetch_sites.py` → `build_evidence.py` → `make_batches.py` → Sonnet sub-agents → `merge_enriched.py --band 80 200 --short-band 35 90 --thin-floor 60` + [wellness_lint.py](scripts/wellness_lint.py). Next: Gate 4 (plan: brand pages, geo, exclusions).

**Gate 4–5 (2026-10-12):** plan approved (all 10: country → region → listing, /devices/ + brand × country, $97/$29/$149). Site built in [apps/directory-blueprint/output/scannerfinder/site/](apps/directory-blueprint/output/scannerfinder/site/) — 935 pages, 513 in the sitemap, all texts checked; report [05-build-report.md](apps/directory-blueprint/output/scannerfinder/05-build-report.md), fact sheet [05-fact-sheet.md](apps/directory-blueprint/output/scannerfinder/05-fact-sheet.md). Launch blockers: Formspree endpoint, Stripe links (3), DNS to Cloudflare, hello@ receiving, photo ≥600 px. Local preview: `scannerfinder-site` in .claude/launch.json (served from the scratchpad, iCloud blocks preview).

**Gate 6 (2026-10-12): LIVE at https://scannerfinder.com** (Cloudflare Pages, project `scannerfinder`; check_live 100%, pages.dev noindex). Plan: [06-launch.md](apps/directory-blueprint/output/scannerfinder/06-launch.md); no Omega dripfeed (Dan, 2026-10-13), natural indexing; 30-day check 2026-11-11. Worker `scannerfinder` (Wrangler autoconfig) deleted. Redeploy: `cd apps/directory-blueprint/output/scannerfinder/site && npm run build && npx wrangler pages deploy dist --project-name scannerfinder --branch main` (never `pages project create` without `--force` — Wrangler autoconfig turns it into a Worker).

**DE + RO (2026-10-12/13)** — Gate 2 after city fix: 871 (DE 753 · RO 118), 0 without city. **Gate 3 done 2026-10-14:** 871/871 descriptions, 0 FAIL → [03-listings-enriched.csv](apps/directory-blueprint/output/scannerfinder-de-ro/03-listings-enriched.csv), report [03-enrich-report.md](apps/directory-blueprint/output/scannerfinder-de-ro/03-enrich-report.md), Gate 4 decisions in [03-gate4-notes.md](apps/directory-blueprint/output/scannerfinder-de-ro/03-gate4-notes.md). ManyCrawl +45 emails → 649/888. **Gate 4 decisions applied 2026-10-14:** [04-exclusions.csv](apps/directory-blueprint/output/scannerfinder-de-ro/04-exclusions.csv) → **825 listings ready (DE 709 · RO 116)**. **Gate 4–5 done 2026-10-14:** DE/RO in the site (1,634 listings, 9 countries, 16 Länder + 15 județe, 9 brand × country pages, /legal-notice/ for Neocomm Business Distribution SRL); build 1,838 pages, audit clean. **Deploy pending** (Dan runs it; command in the log). — same pipeline, kept separate in [data/batch-de-ro/](data/batch-de-ro/) (every script takes `SF_DATA`; Gate scripts take `SF_SLUG=scannerfinder-de-ro`). DataForSEO **$2.38** (local terms: Bioresonanz…, biorezonanță…) → 1,142 → **888 practitioners** in [directory_listings.csv](data/batch-de-ro/directory_listings.csv) (DE 768 · RO 120). First-pass review by Claude in [manual_review.csv](data/batch-de-ro/manual_review.csv), Dan to confirm; **190 animal-only practices** (Tierheilpraxis, vets) set aside in [animal_practices.csv](data/batch-de-ro/animal_practices.csv), not in the directory. Email 610/894 (Impressum crawl), contactable 642/894; device family 379, AI scan price 68 (median ~$115); invite tiers A 30 / B 260 / C 598 (DE/RO = GDPR/UWG → contact-form route, not cold email). Gate 2: [02-listings-clean.csv](apps/directory-blueprint/output/scannerfinder-de-ro/02-listings-clean.csv) 871. Gate 3: pilot 19 passed; DE/RO rule addendum [03-wellness-rules.md](apps/directory-blueprint/output/scannerfinder-de-ro/03-wellness-rules.md). New scripts: [make_ai_batches.py](scripts/make_ai_batches.py), [score_invites.py](scripts/score_invites.py) (reproduces the 831 old scores). ManyCrawl was down → own crawl only.

**Următorul pas:** invitații începând cu tier A (Red: outreach — aprobare Dan) sau pasul 2 (site).

## Housekeeping

- Subfolder discipline: create `research/`, `drafts/`, `assets/`, `data/`, `scripts/`, `apps/`, `final/` only when there is real work to put inside.
- Link external specs and long docs instead of copying them locally.
- Refresh `last_updated` after meaningful progress.

## Archive Criteria

Archive when:

- Directorul e live cu baza de date inițială și formularul de înscriere funcțional, iar operarea continuă trece într-o arie dedicată (`02-areas/scannerfinder-com/`, area_type: venture).
- Sau Dan renunță la proiect.
