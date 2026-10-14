# DE + RO — notes from Gate 3 batches for Gate 4 (decisions by Dan)

Collected from the batch reports and Claude's own checks, 2026-10-13. Updated as batches land.

## Exclusion candidates
- `natur-1-dusseldorf` — own profile places the practice in Cape Town (pilot).
- `quantmed-cluj-napoca` — sells Rayonex devices, no client sessions (offers_scan false, batch 004).
- `belle-peau-cosmetique-erlangen` — website is an unrelated casino page → at least `blank_website` (batch 007).

- `huf-pfote-ilona-wagner-wertheim-am-main` — animal-only practice that slipped past the animal filter → exclude (Dan, 2026-10-13: animal practices out) (batch 011).
- `tanja-konzelmann-heilpraktikerin-craniosacraltherapeutin-gottingen` — site says Ilsfeld (Heilbronn), Maps says Göttingen → fix location or exclude (batch 009).
- Animal-only practices that slipped past the filter (exclude per Dan's decision): `hta-weserlauf-huf-pferdetherapiepraxis-ausbildungszentrum-gandesbergen`, Tierheilpraxis Kaiser, Tierheilpraxis Petra Büttner (batch 009).
- Animal-only (batch 012): `naturlich-tiergesund-alpirsbach`, `ncp-schafer-nature-care-for-pets-amberg`, `tiernaturheilkunde-sabrina-binzenbach-bad-munstereifel`, `pferdetherapie-wei-bad-staffelstein`.
- Animal-only (batch 013): `achim-roeder-alternative-energetische-behandlung-borken`, `pferdesprechstunde-bioresonanz-burgdorf`.
- Risk, not exclusion: `medicina-biorezonanta-bucuresti-sector-4` — its own site is full of disease/diagnosis claims (our description is clean); a link to it may reflect on us (batch 013).
- Animal-only (batch 014): `alternative-tiergesundheit-feuchtwangen`.
- `willmroth-beratung-training-ergolding` — NLS advice/training only, offers_scan false → exclude (batch 014).
- Animal-only (batch 017): `tier-bioresonanz-ostfriesland-krummhorn`, `tierheilpraxis-nicole-messerer-landau-an-der-isar`, `vet-bioresonanz-leezdorf`, `hss-horse-scanning-system-leonberg`.
- Animal-only (batch 015): `tierbetreuung-mit-herz-jessica-becker-gaggenau`, `vitaresonanz-groenkneten`, `harmonie-fur-mensch-und-tier-greven` (check: name says people too), `ekvedo-von-gesunden-pferden-lernen-fridolfing`; borderline `tierheilpraxis-im-hegau-mobile-praxis-gottmadingen`.
- `naturheilpraxis-katrin-kunert-furth` — website/phone point to Weinheim, Maps says Fürth → fix location (batch 015).
- Animal-only (batch 016): `idstein-idstein` (vet centre), `equitherapie-mobile-pferdeheilpraxis-ilvesheim`, `junghund-julia-pokorny-kalchreuth`; borderline `mobile-tierheilpraxis-xenia-albus-hohenstein` (mentions people's wellbeing).
- Animal-only (batch 020): `die-mobile-tierheilpraxis-mit-hz-remchingen`.
- `biofeedback-2014-srl-satu-mare` — device maker (Eductor), no sessions → exclude; partner candidate (batch 020).
- Animal-only (batch 018): `christina-artmann-pferdephysiotherapie-linkenheim-hochstetten`, `dein-tier-in-resonanz-mechernich`, `horse-wave-meckenbeuren`.
- `wir-leben-apotheke-in-marschacht-marschacht` — pharmacy; "Zyto" = cytostatics cleanroom, not ZYTO → exclude (batch 018).
- `naturheilpraxis-birgit-schichtl-ghazouani-heilpraktikerin-mitterfels` — site says Raubling, Maps says Mitterfels → fix location (batch 018).
- Animal-only (batch 019): `pferdephysio-dietz-otzberg`, `praxis-fur-klassische-tierhomoopathie-und-bioresonanz-heilpraktikerin-und-tierhe`.
- `praxis-volker-gross-hum-vet-oberreidenbach` — website is the owner's farewell note → likely closed, exclude (batch 019).
- Animal-only (batch 022): `rebecca-kendlinger-pferdetherapie-tuntenhausen`, `susanne-stohr-unlingen`, `pferdegesundheit-wachter-vlotho`, `pferdeosteopathin-christina-schneppe-wallhausen`.
- `ammerlander-gesundheitshaus-westerstede` — shop + seminars, offers_scan not enough info; site address Barßel-Elisabethfehn vs Maps Westerstede (batch 022).
- Animal-only (batch 021): `katja-vogel-schwanewede`, `sabine-buller-simmerath`; possibly `dog-s-health-harmony-sulz` (name only).

## Possible duplicates
- `naturheilpraxis-schiff-bissingen` / `schiff-josef-bissingen` — same address Marktstraße 16 (batch 008).

- `hta-timewaver-bioresonanztherapie-gandesbergen` — same operator as the excluded Weserlauf horse practice; keep (it lists people too) (batch 009).
- `dr-med-dent-lydia-martin-maintal` / `heilpraktiker-bioresonanz-dr-lydia-martin-maintal` — same practice, dentist + naturopath listing (batch 010).

- Heike Gerull appears twice: `ganzheitliche-beratung-fur-mensch-und-tier-kamen` (batch 010) and `...-meschede` (batch 018) — two locations or one (check).

## Wrong website
- `celine-teufele-...-oberstdorf` — website belongs to another practice (Therapiepraxis Oberstdorf) → `blank_website` candidate (batch 010).

- `om-shanti-natural-healing-by-sonja-bad-peterstal-griesbach` — website is a directory page (firmenmap) → `blank_website` (batch 012).

- `naturheilpraxis-ute-ogroske-dillenburg` — website is gambling spam → `blank_website` (batch 014).

- `life-naturheilpraxis-petra-gregor-heilpraktiker-friedewald` — website is an IPL hair-removal site → `blank_website` (batch 015).

- `vital-praxis-inh-christine-diecks-mohnesee` — website is a holiday-rental page (practice in the same building) → check (batch 018).

- `praxis-fur-regulationsmedizin-petershagen-eggersdorf` — website is a back-office login page → `blank_website` (batch 019).
- `praxis-fur-energie-und-naturheilkunde-kristin-krohs-neusalza-spremberg` — website is a book publisher (Elumantu), probably her own brand → check (batch 019).

## Judgment calls to confirm
- Remote sessions from phone/video consults that don't say bioresonance is remote: Dr. Ziegeler (Hamburg), Bannert, Fiederle, gesund-in-balance (Cologne), wert-voll.de (Frankfurt), Woschek.
- BICOM marked from a consultant/other-site mention: Durgeloh-Netta (Münster, Regumed application consultant), Helix Vital Krefeld (BICOM at the Langenfeld practice).
- Animal sessions true for human practices: Penka Donnert, Seraina Stangier, Brischke.
- offers_scan true on "Quantenresonanz (Bio-Resonanz ähnlich)" (Dumonet).
- Name-only listings (all "not enough info", thin/noindex): ~20 so far, mostly Romania (Bucharest, Arad, Constanța, Oradea, Suceava, Târgu Mureș, Deva, Baia Mare) — keep thin or exclude, as for the 63 in the main run.

## Fixed by Claude during the run
- Batch 005: Kunz BICOM Body-Check was marked NLS → BICOM; 3 name-only listings had offers_scan/device true → "not enough info"; descriptions that narrated missing info rewritten.

## Dan's decisions (2026-10-14) → applied in [04-exclusions.csv](04-exclusions.csv)
1. Animal-only practices: drop (35 incl. the borderline Tierheilpraxis im Hegau, Xenia Albus and Dog's Health; Harmonie für Mensch und Tier kept, it serves people).
2. offers_scan=false (4): drop. 3. Natur 1 (Cape Town) and Volker Gross (closed): drop.
4. Wrong websites (6): `blank_website`; the holiday-rental and publisher sites (Diecks, Krohs) stay, they belong to the practitioner's own building/brand.
5. Location conflicts: Kunert Fürth and Konzelmann Göttingen were stale second listings → drop; Ammerländer moved to its own address (Oldenburger Str. 13a, Barßel-Elisabethfehn) via `city_overrides.csv` (force); Schichtl-Ghazouani kept at the Maps address (the site names Raubling but gives no address) — check on claim.
6. Duplicates: drop Schiff Josef, Gerull Meschede, the 1-review Lydia Martin listing.
7. The 59 "not enough info" listings are kept (thin, noindex).
Side fix: slugs dropped "ß" (Weiß → wei); 17 slugs renamed (map in `03-cache/slug-renames-2026-10-14.json`), merge rerun 871/871 0 FAIL.

## Found during Gate 5 (2026-10-14)
- Possible duplicate: "Heilpraxis zur Quelle mit SuperVision Shanna Becker" listed in Rabenau and in Hohenroda (Hesse) — two locations or one; check on claim.
- Bucharest region copy (batch 14): check the sentence that calls two name-only listings "SCIO listings".
