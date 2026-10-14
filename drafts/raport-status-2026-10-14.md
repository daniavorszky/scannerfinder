# ScannerFinder.com — raport de stare (14.10.2026, actualizat 14:15)

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
- **Deploy-ul îl rulează Dan, cu `sfdeploy`.** Claude face build-ul și auditul, Dan rulează comanda, apoi Claude verifică live cu curl. `sfdeploy` e o comandă scurtă adăugată în `~/.zshrc` (backup: `~/.zshrc.bak-sfdeploy`). Merge din orice folder: face build-ul, arată contul Cloudflare (`whoami`) și urcă pe Pages.
- **Listele de orașe/regiuni pe coloane** se ordonează pe verticală: alfabetic în jos pe coloana 1, apoi coloana 2.
- **Paginile cu hartă** arată 10 locații pe pagină (model mypeptidematch.com/clinics/…). Toate cardurile rămân în HTML, pentru SEO.

## Ce s-a făcut (pe scurt)

1. **Date:** extragere DataForSEO (EN $6.61, DE/RO $2.38). Curățare a dublurilor, producătorilor și distribuitorilor MLM. Descrieri rescrise cu AI în registrul wellness (EN 819, DE/RO 871, 0 FAIL). Crawl de emailuri. Scoruri pentru invitații (tier A/B/C).
2. **Site live pe 12.10:** pagini de țară, regiune, oraș și listare; pagini pe aparat și aparat × țară; /search/; /claim/; pagini legale; /affiliate-disclosure/.
3. **Corecții UX (sesiunea „Corecții site”):** meniu hamburger pe mobil. Reparat linkul ZYTO din pagina de țară și căutarea „aparat + locație” de pe homepage. Testat „near me”. Pe paginile de regiune: explorer cu hartă Leaflet și filtre live. Pastile pe homepage. ROI Calculator: câmpuri cu USD/%, nume complete de țări, câmpul „Other” și ZYTO Evox.
4. **Pagini noi:** Tools + ROI Calculator, Blog (3 articole placeholder lorem ipsum, noindex), /best-practitioners/, /statistics/ (+ CSV CC BY 4.0), /llms.txt. Pagini pentru toate orașele cu cel puțin o listare.
5. **SEO:** ghiduri pe toate cele 10 pagini de aparat, /bioresonance/ (pillar), /bioresonance-machines/ (B2B), /bioresonance/does-it-work/. Toate sunt live din 14.10. Follow-up GSC programat pe **01.11.2026**.
6. **DE + RO (14.10):** integrate în site (16 Länder, 15 județe) și publicate.
7. **Azi (sesiunea „Reorganizare coloane”):** footer pe desktop, cu coloana Contact mutată sub logo și tagline. Ordine nouă a blocurilor pe paginile de țară, regiune și oraș. Textul ocupă toată lățimea. Corectat orașul gol pentru ReikiWorx (→ Rustenburg, ZA); redirectul 301 de pe vechiul URL e live.
8. **După prânz (sesiunea 4a83f083):**
   - Listele de orașe/regiuni de pe 4 coloane curg acum pe verticală. Live, verificat pe /directory/united-states/ și /directory/romania/.
   - Paginarea câte 10 pe paginile cu hartă. Harta arată doar pinurile paginii curente, iar un filtru nou readuce lista la pagina 1. Live, verificat pe California: 41 de practicieni, paginile 1–10 și 11–20.
   - Deploy-ul a fost reparat; detaliile sunt mai jos, la „Ce am încercat”. Build-ul durează acum 5 s în loc de 7,5 s.
   - Build: 3.051 de pagini (1.634 listări). Sitemap-ul are 1.022 de URL-uri.
9. **12:40–14:10 (3 sesiuni, toate live):**
   - **Hărți și filtre.** Fără plafonul de 60 de carduri (`maxCardsPerCity`): toate listările apar ca carduri, cu paginare de câte 10. Listele pliate „All other / N more practitioners” au fost scoase. Filtrul arată locurile cu ≥3 listări; linkul „View all cities/states (N)” le deschide pe toate. Filtrele sunt ordonate A–Z, iar eticheta e „City”. Dropdown-ul Sort are o săgeată proprie, cu spațiere corectă.
   - **Pagini de țară, regiune și oraș.** Primul bloc e „Find a practitioner by device in …”, cu pilule cu număr. „Cities with the most practitioners” stă sub „… in numbers”. Pe regiuni, „Towns in {Regiune} with listed practitioners” e pliat; pe București se numește „Areas in Bucharest”. Blocul „Do you offer … sessions?” e ultimul înainte de footer, pe toate paginile.
   - **Homepage.** Butonul „See all 135 regions” a fost scos. Ordinea blocurilor: cifre → pilulele cu device-uri (centrate, 5 pe rând, +50% spațiu deasupra) → țări. Țările sunt ordonate după numărul de listări: DE 709, US 387, GB 176, RO 116… Pe carduri scrie „709 practitioners”, fără „bioresonance”. „Highest-rated” arată doar 3 listări.
   - **Pagini de device.** /devices/ și /services/ folosesc pilule. Harta cu filtre e și pe paginile de device, pe cele device × țară (61) și pe servicii. Pe device × țară, blocul „by region” e pliat. Ordinea pe /devices/<x>/: „in numbers” → hartă → (48px) → intro + ghid → „by country” / „by region” → FAQ. Toate textele sunt pe lățime 100%, inclusiv Methodology de pe /statistics/.
   - **Date.** „Medicina Biorezonanta Sector 4” are acum orașul Bucharest; vechiul URL face 301 spre /bucharest/ (verificat live).

## Problema actuală

**Nicio problemă deschisă pe site (14:15).** Toate schimbările de mai sus sunt live, iar redirect-urile Rustenburg și Sector 4 răspund cu 301. Deploy-ul îl face Dan, cu `sfdeploy`. Claude verifică apoi cu `curl`.

**Singura limitare:** dev server-ul local nu pornește din preview, din cauza permisiunilor macOS pe iCloud. Fix-ul e la Dan: System Settings → Privacy & Security → Full Disk Access → Claude. Până atunci, testele se fac pe o copie a build-ului din scratchpad.

## Fișiere relevante

- `site/astro.config.mjs` — generează `_redirects` și lista de noindex. Redirect-urile se adaugă aici, nu în `public/_redirects`.
- `site/package.json` — scriptul `deploy` (Pages, cu `whoami`). Comanda `sfdeploy` e în `~/.zshrc`.
- `site/src/components/ListingExplorer.astro` + `public/explorer.js` — hartă, filtre, paginare
- `DirectoryHub.astro` (homepage), `FamilyPage.astro` (device/servicii), `pages/directory/[state]/…` (țară, regiune, oraș), `global.css`
- `site/src/data/listings.csv` + `03-listings-enriched.csv` — corecturile de oraș (ReikiWorx, Sector 4)

## Ce am încercat (problemele de azi)

1. **Redirect-uri 404.** Regula pusă direct în `public/_redirects` a fost suprascrisă la build. Am mutat-o în generatorul din `astro.config.mjs` și acum funcționează. Aceeași greșeală s-a repetat la Sector 4 și am reparat-o la fel.
2. **Deploy blocat.** Avea trei cauze:
   - erori EPERM, pentru că iCloud sincroniza `node_modules`;
   - token-ul LeadLocal, citit din `.env` din `DGA OS/`;
   - scriptul `npm run deploy`, care urca pe Workers.

   Toate trei sunt rezolvate prin `node_modules.nosync` și `sfdeploy`.
3. **Domeniul servea câteva secunde versiunea veche după deploy.** E propagare, iar a doua verificare cu `curl` trece.

## Rămase deschise (în afara problemei curente)

- Întrebări fără răspuns din sesiunile de azi:
  - Scoatem butonul „See all regions” și din template-ul Blueprint?
  - Ascundem device-ul paginii din filtrul Technology?
  - Pliem blocul „States/Regions with listed practitioners” de pe țări și blocurile „by country/region” de pe /devices/<x>/?
  - Graficele de pe /statistics/ trec și ele la lățime 100%?
  - Ștergem „Sector 4” și din descrierea listării?

- Invitațiile tier A (53 prin email, 33 prin formular) sunt pregătite, dar netrimise. E outreach, deci așteaptă aprobarea lui Dan.
- Decizie Dan: hub-uri în germană (`/de/`) și română (`/ro/`). Paginile pentru animale în DE sunt aprobate, dar blocate până există paginile DE.
- Cele 3 articole lorem ipsum de pe blog trebuie înlocuite cu articole reale.
