# ScannerFinder.com — raport de stare (14.10.2026)

Surse: 7 sesiuni Claude Code din grupul ScannerFinder (11–14.10.2026) + overview-urile celor două proiecte.

## Obiectiv

scannerfinder.com să devină directorul de referință pentru practicienii care oferă scanări bioenergetice/biorezonanță (ZYTO, AO Scan, BICOM, NES, SCIO, NLS etc.). Profile verificate și date pe care nu le publică altcineva: prețul ședinței, transparența comercială, certificarea de la producător. Venit secundar, estimat la ~1.100 USD/lună în anul 2. Sursele de venit: listări premium, lead generation (cereri de ofertă de la distribuitori), afiliere.

## Structura proiectului

- **Lansare + site:** `03-projects/2026-10-scannerfinder-directory-launch/`
  - `data/` — extragerile DataForSEO (EN), plus `data/batch-de-ro/` pentru DE/RO
  - `scripts/` — extragere, curățare, logo-uri, invitații, wellness_lint
  - `apps/directory-blueprint/output/scannerfinder/site/` — site-ul Astro, cu deploy pe Cloudflare Pages (proiectul `scannerfinder`)
  - `apps/price-tools/` — prototipul ROI Calculator / Price Index
- **Conținut SEO:** `03-projects/2026-10-scannerfinder-seo-content/` (keyword map, analiza MyPeptideMatch). Codul rămâne în `site/` din proiectul de lansare.
- **Live:** 1.634 listări în 9 țări (US, GB, CA, AU, ZA, IE, NZ, DE 709, RO 116), 1.839 pagini.

## Decizii deja luate

- **Registru wellness:** niciodată „diagnostic” sau „tratament”. Toate textele trec prin `wellness_lint.py`.
- **Ierarhia site-ului:** țară → regiune → oraș → listare, plus pagini pe aparat și pe aparat × țară. Paginile cu mai puțin de 3 listări (`cityFloor`) se generează, dar sunt noindex și rămân în afara sitemap-ului.
- **Fără prețuri publice la ședințe:** medianele și intervalele de preț nu se publică. Ele sunt stimulentul ca practicienii să-și revendice listarea. Excepție: /statistics/ arată mediane doar pentru grupuri cu n ≥ 5. Prețurile de achiziție ale aparatelor sunt publice.
- **Excluderi:** practicile care lucrează doar cu animale (190) nu intră în director. Ce rămâne exclus din ranking e listat în `site.json bestExclude`.
- **Germania:** doar formulare de contact, niciodată cold email (UWG §7). Avertismentul se repetă de fiecare dată.
- **Logo-uri:** pe listări (Google, apoi site-ul firmei). Unde lipsește logo-ul, apar inițialele.
- **Publisher:** DGA, în locul lui Andrei Ploieșteanu. /legal-notice/ e pe Neocomm Business Distribution SRL.
- **Lead-uri:** FormSubmit.co → scannerfinder_leads@emailr.eu (activat și testat).
- **Indexare:** naturală, din sitemap. Fără indexare plătită (Omega).
- **Design:** tipografia preluată de la mypeptidematch.com (Saira Condensed + font de sistem).
- **Meniu:** Practitioners ▾, Technologies ▾, Tools, Blog. About și Contact sunt doar în footer.
- **Căutare:** tehnologie → regiune/oraș → nume (opțional).
- **Fără /compare/ și fără /bioresonance/cost/.** Pentru llms.txt nu se face o copie Markdown a fiecărei pagini.
- **Deploy-ul îl rulează Dan.** Claude face build-ul și auditul, Dan rulează comanda, apoi Claude verifică live cu curl.

## Ce s-a făcut (pe scurt)

1. **Date:** extragere DataForSEO (EN $6.61, DE/RO $2.38). Curățare a dublurilor, producătorilor și distribuitorilor MLM. Descrieri rescrise cu AI în registrul wellness (EN 819, DE/RO 871, 0 FAIL). Crawl de emailuri. Scoruri pentru invitații (tier A/B/C).
2. **Site live pe 12.10:** pagini de țară, regiune, oraș și listare; pagini pe aparat și aparat × țară; /search/; /claim/; pagini legale; /affiliate-disclosure/.
3. **Corecții UX (sesiunea „Corecții site”):** meniu hamburger pe mobil. Reparat linkul ZYTO din pagina de țară și căutarea „aparat + locație” de pe homepage. Testat „near me”. Pe paginile de regiune: explorer cu hartă Leaflet și filtre live. Pastile pe homepage. ROI Calculator: câmpuri cu USD/%, nume complete de țări, câmpul „Other” și ZYTO Evox.
4. **Pagini noi:** Tools + ROI Calculator, Blog (3 articole placeholder lorem ipsum, noindex), /best-practitioners/, /statistics/ (+ CSV CC BY 4.0), /llms.txt. Pagini pentru toate orașele cu cel puțin o listare.
5. **SEO:** ghiduri pe toate cele 10 pagini de aparat, /bioresonance/ (pillar), /bioresonance-machines/ (B2B), /bioresonance/does-it-work/. Toate sunt live din 14.10. Follow-up GSC programat pe **01.11.2026**.
6. **DE + RO (14.10):** integrate în site (16 Länder, 15 județe) și publicate.
7. **Azi (sesiunea „Reorganizare coloane”):** footer pe desktop, cu coloana Contact mutată sub logo și tagline. Ordine nouă a blocurilor pe paginile de țară, regiune și oraș. Textul ocupă toată lățimea. Corectat orașul gol pentru ReikiWorx (→ Rustenburg, ZA).

## Problema actuală

> **Rezolvată 14.10, 12:08:** deploy rulat de Dan (3.052 pagini); verificat live: URL-ul vechi → `301` spre `/rustenburg/`, Rustenburg `200`.

Adresa veche `/directory/south-africa/north-west-province/north-west-province/` a fost live câteva ore, iar acum **dă 404 în loc de 301 spre Rustenburg** (verificat live la 09:06 UTC).

**Cauză:** `astro.config.mjs` rescrie `public/_redirects` la fiecare build. Linia adăugată manual a fost ștearsă.

**Fix:** redirect-ul a fost mutat în generatorul din `astro.config.mjs`, cu o notă că redirect-urile se adaugă acolo. Fix-ul e făcut local, dar **mai trebuie deploy**:

```bash
cd "/Users/id/Library/Mobile Documents/com~apple~CloudDocs/_ WorkOS/DGA OS/03-projects/2026-10-scannerfinder-directory-launch/apps/directory-blueprint/output/scannerfinder/site" && npm run build && npx wrangler pages deploy dist --project-name scannerfinder --branch main
```

După deploy: `curl -sI` pe URL-ul vechi trebuie să întoarcă `301` cu `location: …/rustenburg/`.

## Fișiere relevante

- `site/astro.config.mjs` — generează `_redirects` și lista de noindex
- `site/src/data/listings.csv` și `output/scannerfinder/03-listings-enriched.csv` — orașul ReikiWorx, corectat în ambele

## Ce am încercat

1. Am adăugat regula direct în `public/_redirects`. Rezultat: a fost suprascrisă la build și pe live a rămas 404.
2. Am mutat regula în generatorul din `astro.config.mjs` și am rulat config-ul. Regula apare acum în `_redirects`. Rămâne de confirmat live, după deploy.

## Rămase deschise (în afara problemei curente)

- Invitațiile tier A (53 prin email, 33 prin formular) sunt pregătite, dar netrimise. E outreach, deci așteaptă aprobarea lui Dan.
- Decizie Dan: hub-uri în germană (`/de/`) și română (`/ro/`). Paginile pentru animale în DE sunt aprobate, dar blocate până există paginile DE.
- Cele 3 articole lorem ipsum de pe blog trebuie înlocuite cu articole reale.
