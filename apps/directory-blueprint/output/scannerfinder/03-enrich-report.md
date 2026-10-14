---
title: Gate 3 enrich report — ScannerFinder
type: report
status: approved 2026-10-12
updated: 2026-10-12
---

# Gate 3 — Enrich report

## How it ran
- Input: [02-listings-clean.csv](02-listings-clean.csv), 819 listings. Attributes: [03-attributes.json](03-attributes.json) (14; core = `offers_scan`; 10 device brands). Niche rules: [03-wellness-rules.md](03-wellness-rules.md).
- Websites (`fetch_sites.py`): 435 readable, 134 no website, 107 blocked, 51 dead, 52 script-rendered, 40 other. +41 filled from the project cache (`data/site_text_cache.jsonl`) for blocked/JS sites → **528 with text**.
- Evidence: ~425k tokens (518/listing). 21 batches: pilot (20, approved by Dan) + 20 × 40 on 5 Sonnet sub-agents in parallel. Sub-agent cost: ~1.9M tokens (≈2.3k/listing, below the 4k estimate).
- Checks: `merge_enriched.py` **819/819, 0 FAIL** (openers checked across all batches) + `wellness_lint.py` **0 FAIL** (medical words, prices, narrated unknowns).

## Deviation from the kit: word bands
The sub-agents padded descriptions up to the kit's floor (120 words) with empty sentences. 242 sentences were removed from 328 descriptions ("opening hours are posted", "testimonials are published", payment types; the pre-cleanup version is in `03-cache/enriched-prefill/`). Useful facts were kept (appointments, parking, access, women-owned). Bands lowered to **80–200** (with text) / **35–90** (without) / 60 floor (little text). Lengths now: min 35, median 72, max 157 words.

## Attributes (true)
Offers scan sessions 747 · ZYTO 141 · BICOM 25 · Asyra / Qest4 62 · NES Health 23 · Rayonex 18 · NLS (Metatron, Oberon) 34 · SCIO / Indigo / Eductor 98 · MORA 9 · TimeWaver 6 · AO Scan 63 · Remote sessions 176 · Free first consultation 65 · Sessions for animals 61

Thin (noindex at launch): **417** of 819 (was 425).

## For Gate 4 (Dan's decisions)
1. **`offers_scan` = false: 9 listings** — they don't offer scans (exclusion candidates): `mora-thai-therapy-beaconsfield`, `quantum-biofeedback-courses-canada-milton`, `the-hideout-hair-beauty-training-academy-corby`, `bioresonance-practitioners-association-reading`, `biocommunicaiton-holistic-bioresonance-technology-bethesda`, `shambhala-life-extending-wellness-center-and-retreat-kelseyville`, `hawaii-healy-kihei`, `lighthouse-gift-shop-pahrump`, `mari-mora-therapy-santa-ana`
2. **`offers_scan` = not enough info: 63** — mostly a name/category with no text. Keep them (thin, noindex) or exclude.
3. **Expired domains (websites → casino/spam):** `bicom-homeo-clinic-auckland`, the two Cheltenham Equilibrium listings, the Durban counterpulsation listing → `blank_website` in 04-exclusions.
4. **Las Vegas:** `las-vegas-body-wellness-llc` and `healing-waters-las-vegas` share one site — the same business or two?
5. **"Quantum biofeedback" read as SCIO: 19 of the 98 SCIO marks** have no device name in the text (the sub-agents applied the rule inconsistently). Recommendation: SCIO only when the device is named (SCIO/Indigo/Eductor/QXCI) → re-check scio=true listings without the word in the text.
6. **Non-core businesses that offer scans as a side service** (dental practice, cardiac practice, fitness, beauty): stay in.
7. From Gate 2: 213 zero-review, 30 stale, 11 shared addresses.

## Sample (8 random descriptions)

**The Holistic Hub London** (GB · London, 5 rev)

> Founded by Sharmila Hume, The Holistic Hub takes a bioregulatory approach to wellbeing from its London base, with bioresonance sessions, nutritional supplements, BRMT and Weleda products. Programmes include BioPerformance and Brain Health, with a recovery room on site, and lifestyle support runs alongside. Clients complete a history form, then talk through their background before sessions begin. Both in-person and online sessions are available, and people travel from across the UK and abroad. Appointments are recommended. Rated 5.0 from 5 Google reviews, all of them five stars.

**RESONANT FREQUENCY / RF LAB by OHM Center** (US · New York, 0 rev)

> A partnership between Resonant Frequency Magazine and OHM Center, RF LAB in New York gives the public access to energy instruments the magazine writes about. Acupuncturists work with electricity, magnets, structured water, Rife, PEMF, Scenar, bioresonance, infrared and millimeter waves. Call to ask which instruments are in use and how to book.

**Inner Wisdom Healing, LLC** (US · Lisbon, 6 rev)

> Inner Wisdom Healing, LLC in Lisbon has served clients since 2009 under Heather Rose, a National Board Certified Health and Wellness Coach. Qest4 bio-energetic analysis sits alongside intuitive tarot and oracle readings, life and wellness coaching, and Emotion Code and Body Code sessions. Rated 4.3 from 6 Google reviews, five of them at five stars and one at one star.

**Renew Wellness Center** (CA · Winkler, 239 rev)

> Renew Wellness Center in Winkler, Manitoba, offers massage therapy from a Registered Massage Therapist or a student, athletic therapy, acupuncture, counselling, craniosacral therapy and lymphedema services. Its frequency-based services include bioresonance and red light therapy from a Registered Holistic Nutrition Practitioner, who also gives nutritional and lifestyle guidance. The center serves the Pembina and Red River Valley regions, including Morden, Plum Coulee, Altona, Carman and Morris, and offers direct billing for many services. Booking is online and appointments are required. Rated 5.0 from 239 Google reviews, 229 of them five stars.

**Vitality Wellness** (US · Beverly, 0 rev)

> Vitality Wellness Beverly offers non-invasive ZYTO wellness scans for people who want insight into stress, energetic balance and personalized wellness support. Services are by appointment in Beverly, Massachusetts, with mobile visits across the North Shore and surrounding areas. The practice is owned by women and offers family-friendly options for children. The scans involve no needles and are for wellness and educational purposes. The entrance, parking, restroom and seating are wheelchair accessible. Call or book online to confirm hours and availability.

**Holistic Healthy Path** (US · Orland Park, 28 rev)

> Holistic Healthy Path in Orland Park is a women-owned practice led by Dr Natalia. An initial consultation includes a painless full body scan with Sensitiv Imago devices, followed by bio-resonance therapy sessions, and 24-unit EESystem sessions are available in the office. Cardiovascular screening, products, specials and video testimonials are on offer. Appointments are required. Rated 5.0 from 28 Google reviews, every one of them five stars. Reviews, recommendations and research pages are published, and specials are listed for EESystem sessions.

**Healthful Transformations - Holistic Coach - Energy Therapies** (US · Grand Junction, 11 rev)

> Healthful Transformations in Grand Junction is a holistic coaching and energy practice using advanced body scanning devices and Solex AO software to create frequencies tailored to each client. It also uses SRT software for an energetic reset and offers the Slenderiiz product. Rated 5.0 from 11 Google reviews, all of them five stars.

**Nova Spa** (US · Plano, 229 rev)

> Nova Spa opened its Plano location after establishing a spa in Frisco. Menu items include head massage, facial skin care, foot and body massage, cupping, ear picking, foot care and a bioresonance steam chamber session. Rated 4.9 from 229 Google reviews, 219 of them five stars. The spa is owned by women and offers memberships, online scheduling and a free parking lot, and an appointment is recommended.

## Dan's decisions (2026-10-12)
1. The 9 `offers_scan=false` → excluded (`drop` in [04-exclusions.csv](04-exclusions.csv)).
2. The 63 `not enough info` → kept (thin, noindex).
3. Compromised domains → link removed (`blank_website`) — 7 found in the end, not 4: + Harmonic Convergence Gunnison, Soulbody Kingwood (expired) and Pure Nature Life Rockdale (hacked).
4. SCIO re-checked: 19 marks with no device named → `not enough info` (SCIO 98 → 79).
5. Zero-review (213), stale (30), shared addresses (11) → kept.
