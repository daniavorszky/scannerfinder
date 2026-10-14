# Flux de revendicare + înscriere — plan

Status: **aprobat 2026-10-14** (Faza 0 decisă, vezi „Decizii” la final). Input: [proprietary-data-ideas.md](proprietary-data-ideas.md), deciziile din [_overview.md](../_overview.md) (prețuri publicate doar după confirmare, mediane nepublicate = stimulent de revendicare, n ≥ 5, DE = doar formulare).

## Constrângerea

1.634 listări, **0 revendicate**. Fără revendicări nu avem prețuri confirmate, nu avem date proprietare, nu avem venit, iar invitațiile tier A stau blocate. Pagina /claim/ de azi e un `mailto:`. Asta e gâtul de sticlă, nu traficul.

## Principiul: „give to get”, în trepte

Fiecare treaptă cere puțin și dă imediat ceva înapoi. Răsplata vine **pe loc**, nu „la final”. Raportul centralizat e o răsplată întârziată (luni de zile, până avem n), deci e bonus, nu cârligul principal.

| Pas | Ce cerem | Timp | Ce primesc pe loc |
|---|---|---|---|
| 1. Revendicare | listarea, nume, rol, email | 60 s | link de confirmare; profil marcat „claimed” |
| 2. Profil public | corectează ce am pre-completat + preț ședință, durată, aparat, link programări, logo/foto, declarații | 3–4 min | **Benchmark nivel 1** (prețul tău vs oraș/țară/aparat) + urcă peste nerevendicați |
| 3. Date de cabinet (private, opționale, pe blocuri) | aparat (achiziție, an, abonament, satisfacție, intenție de schimbare), economie (ședințe/săpt., pachete, suplimente), clienți (surse, buget marketing), certificare | 5 min, blocuri separate | **Benchmark nivel 2** — fiecare bloc deblochează comparația lui |
| 4. Upsell | Premium / poziții featured | — | plată Stripe |

Raportul anual „State of Bioenergetic Scanning” = bonus pentru cine a completat pasul 3 (copie completă gratis, înaintea publicului).

## Benchmark-ul (lead magnet-ul principal)

Pagină privată `/my/benchmark/`, deschisă prin sesiune magic-link. Regula de confidențialitate: doar agregate, **n ≥ 5** per grup; sub prag cade automat la nivelul următor (oraș → regiune → țară → aparat global). Cold start rezolvat: avem 178 de prețuri extrase de pe site-uri + date Google pentru toți.

Criterii, în ordinea valorii pentru practician:

1. **Prețul ședinței** — percentila ta în oraș/regiune, țară și pe aparat. (seed: 178 prețuri)
2. **Preț pe minut** — preț ÷ durată. Arată cine e ieftin pe ședință dar scump pe timp. (seed: 260 durate)
3. **Reputație** — rating + nr. recenzii Google vs colegii din regiune. Disponibil azi pentru toți, fără niciun input.
4. **Vizibilitate pe ScannerFinder** — afișări, click-uri pe telefon/site/direcții la listarea ta vs media din oraș. Necesită tracking de evenimente (vezi Faza 1). Raportul lunar = argument de upsell.
5. **Cerere locală** — căutări pe ScannerFinder pentru orașul/aparatul tău, căutări fără rezultat în jur („white space”), volum Google în țară.
6. **Densitate concurențială** — câți practicieni cu același aparat la ≤25 km.
7. **Completitudine profil** — % al tău vs media orașului + poziția ta în listare (ordonarea e după %).
8. **Maturitate digitală** — % din colegi cu programare online, consultație gratuită, ședințe la distanță, reclame plătite. Doar agregat, niciodată per cabinet. (seed: detect_site_tech.py)
9. *(nivel 2)* **Aparatul** — cât au plătit alții pentru același model (nou/second-hand/leasing), abonament software, satisfacție cu producătorul, % care vor să schimbe în 12 luni.
10. *(nivel 2)* **Rentabilitate** — payback-ul tău vs colegi (din ROI Calculator + ședințe/săptămână reale).
11. *(nivel 2)* **Model de venit** — % care vând suplimente, coș mediu, pachete vs ședință unică.

## Arhitectura (rămânem pe Cloudflare)

Site-ul rămâne Astro static pe Pages. Adăugăm:

- **Pages Functions** (`site/functions/`) — API: `/api/claim`, `/api/verify`, `/api/profile`, `/api/benchmark`, `/api/stripe/webhook`, `/api/event`.
- **D1** creat cu `--jurisdiction eu` (GDPR, practicieni din DE/RO).
- **R2** pentru logo/foto/certificate încărcate.
- **Turnstile** pe formulare (anti-spam, gratuit).
- **Email tranzacțional** pentru magic link + notificări (decizie deschisă).
- **Admin** `/admin/` protejat cu Cloudflare Access (doar Dan): coada de revendicări, aprobare, diff între profilul pre-completat și ce a trimis practicianul.

**Publicarea modificărilor:** proiectul Pages e cu upload direct (fără git, deci fără deploy hook). La volumul de la început (zeci de revendicări): Claude exportă revendicările aprobate din D1 → `claims-overlay.json` → build → Dan rulează `sfdeploy`. Când trecem de ~10/zi, mutăm overlay-ul pe randare la cerere.

### Schema D1 (schiță)

- `claims` — id, listing_slug (null = practică nouă), status (pending / verified / approved / rejected), email, name, role, verify_method, created_at
- `sessions` — token_hash, claim_id, expires_at
- `profile_public` — claim_id, version, data (JSON), consents (wellness, accuracy, terms, marketing separat), submitted_at
- `profile_private` — claim_id, block, data (JSON), aggregate_consent, submitted_at
- `payments` — claim_id, stripe_customer, subscription_id, tier, status, period_end
- `events` — listing_slug, type (view / phone / site / directions / booking), day, count — fără IP
- `searches` — tech, place, results_count, day, count

### Verificarea proprietarului

1. **Link din invitație** (token semnat, trimis la emailul găsit pe site-ul lor) → verificat automat.
2. **Email pe domeniul site-ului** sau identic cu emailul găsit de noi (master: `listings_profiled.csv`) → verificat prin magic link.
3. **Altfel** (Gmail etc., ~38% dintre practicieni) → coadă manuală: Dan/VA sună la numărul din Google, sau cerem un cod pus temporar pe site/Facebook.

## Plata

- **Stripe Checkout** (nu Payment Links) — avem nevoie de `listing_slug` în metadata ca webhook-ul să activeze automat Premium în D1.
- Produse din `site.json tiers`: Premium $97/an, City $29/lună, State $149/lună, Best-of de la $100 o dată (County „coming soon” rămâne ascuns).
- Upsell-ul apare **după** pasul 2, nu înainte. Nu cerem bani înainte să fi dat valoare.
- Customer Portal Stripe pentru anulare/schimbare card — zero cod.
- Facturare: entitatea din /legal-notice/ e Neocomm Business Distribution SRL (RO). TVA pentru clienți UE B2B (taxare inversă, cod TVA), UE B2C (OSS), non-UE (fără TVA) + raportare e-Factura — **de confirmat cu contabilul**; Stripe Tax sau facturi Oblio.

## Legal / GDPR (blocant pentru DE)

- Pasul 2: bife obligatorii — „serviciul meu e wellness, nu diagnostic/tratament”, „datele sunt corecte”, Termeni + Privacy. Marketing = bifă separată, nebifată.
- Pasul 3: consimțământ explicit pentru folosirea datelor **doar în agregat** (benchmark + raport), cu ștergere la cerere.
- Nu colectăm afecțiuni/motive medicale ale clienților (categorie specială GDPR).
- Actualizare /privacy/: D1 UE, Cloudflare + Stripe + furnizorul de email ca operatori asociați, retenție.

## Faze de deploy

| # | Fază | Livrabil | Cine |
|---|---|---|---|
| 0 | Decizii | răspunsurile de mai jos | Dan |
| 1 | Infrastructură | D1 (eu), R2, Turnstile, Functions de bază, tracking `events` + `searches` pornit imediat (datele de vizibilitate nu se pot recupera retroactiv) | Claude build, Dan deploy |
| 2 | Revendicare pași 1–2 | /claim/ în 2 pași cu pre-completare din master, magic link, admin, overlay → build | Claude |
| 3 | Benchmark nivel 1 | /my/benchmark/ cu criteriile 1–8 | Claude |
| 4 | Pas 3 + certificare | blocuri private, upload certificat → insignă „verified”, benchmark nivel 2 | Claude |
| 5 | Stripe | Checkout + webhook + portal, test mode întâi | Claude build; Dan creează contul/produsele (Red: bani) |
| 6 | Invitații tier A | 53 email + 33 formulare (GB/ZA/DE pe formular) | Red — aprobare Dan |
| 7 | Raport | „State of Bioenergetic Scanning” când n ≥ 5 pe grupurile principale (estimat Q1 2027) | Claude |

Fazele 1–3 sunt minimul ca să deblocăm invitațiile. Stripe poate veni după primele 20 de revendicări — nimeni nu plătește Premium pe o listare pe care n-a revendicat-o încă.

## Metrici

- Rata de revendicare din invitații (țintă: 15% din tier A).
- % care trec de la pasul 2 la pasul 3 (țintă: 40%).
- Revendicări → Premium (țintă: 5–10%).
- Nr. de grupuri oraș/aparat cu n ≥ 5 (pragul pentru raport).

## Decizii (Dan, 2026-10-14)

- **Lead magnet:** benchmark privat imediat după pasul 2, iar raportul anual e bonus pentru pasul 3.
- **Promisiune:** revendicarea e gratuită permanent. Premium $97/an e upsell separat. „Free for the first year” a fost scos din invitație.
- **Email tranzacțional:** prin setup-ul m.scannerfinder.com. *De rezolvat în Faza 1:* setup-ul acela are deocamdată doar o căsuță (Workspace/Zoho) și niciun furnizor de trimitere prin API. Magic link-urile pleacă din Functions, deci avem nevoie de un furnizor cu API pe același DNS, iar trimiterile tranzacționale trebuie ținute separat de reputația domeniului de cold outreach.
- **Stripe:** contul existent al Neocomm. Claude construiește în test mode, Dan creează produsele live.

## Faza 1 — LIVE 2026-10-14 (verificat: /api/health ok, 8 tabele; hit trimis la matomo.php)

- **Tracking = Matomo** (decizia lui Dan; serverul propriu din UE, stats.mkstack.com, site ID 3), nu D1. Rulează fără cookie-uri, deci nu trebuie banner. Click-urile pe listări merg ca evenimente `Listing / phone|website|directions|maps|claim / <slug>`, iar căutările ca Site Search (cuvânt + „near” oraș, tehnologia ca categorie, nr. rezultate; 0 = white space). Codul e în `site/public/track.js`, iar pe alte domenii decât scannerfinder.com nu trimite nimic. Benchmark-ul (Faza 3) citește datele prin Reporting API-ul Matomo, cu token-ul ținut ca secret în Cloudflare.
- **D1** `scannerfinder` (id în `site/wrangler.toml`, jurisdicție UE): tabelele claims, sessions, profile_public, profile_private, payments (`site/migrations/`).
- **Pages Functions:** `site/functions/api/health.js` (verifică legătura cu D1).
- **R2:** neactivat pe cont (cere activare din dashboard) → amânat pentru Faza 2.
- **Turnstile + email tranzacțional:** în Faza 2. DNS-ul scannerfinder.com e pe Cloudflare, iar m.scannerfinder.com nu are încă MX.

## Faza 2 — LIVE 2026-10-14 (test real cap-coadă de Dan: email de confirmare, profil v1 în D1, ambele notificări primite)

- **Pagini:** /claim/ (pasul 1: cauți listarea în search-index sau „My practice is not listed”, apoi nume, rol, email), /claim/verify/ (buton → POST, ca scanerele de email să nu consume token-ul), /claim/profile/ (pasul 2: listare, aparat, certificare prin link, prețuri, ședințe, descriere, corecturi, 3 consimțăminte obligatorii + marketing opțional). Toate noindex.
- **API** (`site/functions/api/claim/`): `start` (max 3 linkuri pe adresă pe oră, honeypot), `verify` (link de o oră, single-use → cookie `sf_claim` de 30 de zile), `me`, `profile` (salvează o versiune nouă la fiecare trimitere).
- **Verificarea proprietarului** (`_lib/claim.js`): `known_email` (hash-ul emailului găsit pe site-ul lor) → `domain_email` (domeniul site-ului, fără freemail) → `manual` (status `email_confirmed`, îi suni la numărul din Google).
- **Pre-completare:** `scripts/build-claim-data.mjs` rulează la fiecare build → `functions/_data/claim-data.json` (doar pe server): 1.634 listări, 1.115 cu emailuri cunoscute (doar hash-uri), 1.376 cu domeniu, 204 cu preț găsit pe site.
- **Emailuri:** Maileroo de pe `noreply@notify.scannerfinder.com`, cu reply-to `hello@scannerfinder.com`. Notificările pentru admin („claim verified / needs a check”, „profile vN to review”) merg la `ADMIN_EMAIL` (scannerfinder_leads@emailr.eu). Local (`.dev.vars` MAIL_DEV=1) nu se trimite nimic.
- **D1:** migrarea 0003 (`claims.details`) aplicată și pe baza live.
- **Încă neconstruit:** publicarea profilurilor aprobate (export din D1 → overlay → build), care vine odată cu primele revendicări reale. Nu există încă un admin UI: aprobarea o face Claude prin D1, la cererea lui Dan.

## Decizii 2026-10-14 (seara, Dan)

- **Aprobare = varianta A (mixtă).** Profil aprobat automat dacă proprietarul e confirmat (`known_email` / `domain_email`) și textul trece de `wellness_lint`. Restul (Gmail etc., status `email_confirmed`) așteaptă ca Dan să sune și să spună „aprobă X”.
- **Prețul e privat implicit.** La pasul 2, practicianul alege explicit „Show my session price on my listing” sau „Keep it private” (`price_public`, obligatoriu dacă a dat un preț). Prețul intră oricum în benchmark și în rapoarte (doar grupuri cu n ≥ 5). Pe listare: prețul, dacă e public, altfel „Price confirmed by the practitioner, ask when booking”. **De ce:** prețurile individuale publice ar permite oricui să calculeze medianele (stimulentul de revendicare) și ar împinge practicienii spre prețuri „de vitrină” sau spre omiterea lor.

## Publicarea profilurilor aprobate (construită 2026-10-14)

- **Script:** [`scripts/publish_claims.py`](../scripts/publish_claims.py). Citește revendicările și ultima versiune a profilului din D1, aprobă automat după regula A (folosește `BANNED`/`PRICE` din `wellness_lint.py`), scrie `site/src/data/claims-overlay.json` (doar câmpurile publicabile; un preț privat nu ajunge în fișier, doar `price_confirmed`) și listează ce așteaptă după Dan: proprietari de sunat, cu telefonul din Google; descrieri care pică lint-ul; cabinete noi.
- **Opțiuni:** `--approve ID` (după ce Dan a sunat), `--reject ID`, `--drop-description ID` (păstrează textul nostru), `--dry-run`, `--local DIR` (D1 local, pentru teste), `--out PATH` (de pe Mac-ul secundar se scrie direct în copia de pe Mac mini).
- **Site:** `load.mjs` aplică overlay-ul peste rândurile CSV înainte de orice altă procesare (aparatele declarate schimbă și paginile pe aparat, prin coloanele de atribute). Pe listare apar blocul „From the practitioner” (preț sau „price confirmed”, durată, pachete, buton „Book a session” cu evenimentul Matomo `booking`) și „Claimed by the owner” în locul butonului de revendicare.
- **Fluxul:** `publish_claims.py` → build → deploy (pe Mac mini). Emailul „your profile is live” vine odată cu benchmark-ul (Faza 3), fiindcă îl promite.
- Certificarea (`certification_url`) nu se publică încă: Dan verifică manual linkul.
- Testat pe D1 local cu 4 cazuri (domeniu confirmat + preț public, manual + `--approve`, lint picat + `--drop-description`, preț privat): paginile generate sunt corecte, prețul privat nu apare nicăieri în HTML.

## Faza 3 — benchmark, construit 2026-10-14 (testat local; vizibilitatea din Matomo se verifică live)

- **Pagina:** `/claim/benchmark/` (noindex, are nevoie de sesiunea de revendicare). Se deschide **imediat după pasul 2**: butonul „See how your price compares” din confirmarea profilului.
- **API:** `functions/api/claim/benchmark.js`. Grupuri cu **n ≥ 5**, practicianul nu e niciodată numărat în propriul grup, doar mediana și intervalul p25–p75 (fără min/max).
  - Preț: oraș, regiune, țară, aparat în țară, aparat în toate țările.
  - Preț pe minut: țară, toate țările.
  - Rating și recenzii Google în regiune.
  - Practicieni la ≤25 km (total și pe aparat).
  - Completitudinea profilului și poziția pe pagina regiunii.
  - Din Matomo (ultimele 30 de zile): afișări și click-uri pe listare vs media regiunii, căutări care numesc orașul (inclusiv fără rezultat).
- **Date:** `functions/_data/benchmark-data.json`, generat la build de `build-claim-data.mjs`. Prețurile de pornire sunt aceleași ca pe /statistics/ (`session-prices.json`, 178), cursurile vin din `merge_prices.py`. Revendicările aprobate le înlocuiesc la cerere (inclusiv prețurile private, folosite doar agregat). Profilul propriu contează imediat, chiar înainte de aprobare.
- **Matomo:** `functions/_lib/matomo.js`, POST cu `MATOMO_TOKEN` (utilizator `scannerfinder-api`, doar View pe site-ul 3, „secure requests only”), cache de o oră. Fără token sau la eroare, secțiunile afișează un mesaj de rezervă.
- **Barele** pornesc de la 0 (ratingul pe 0–5, completitudinea pe 0–100), ca să nu exagereze diferențele; sub fiecare bară e o propoziție cu valorile (accesibilitate).
