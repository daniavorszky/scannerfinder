---
title: Gate 3 enrich report — ScannerFinder DE + RO
type: report
status: complete, awaiting approval
updated: 2026-10-14
---

# Gate 3 — Enrich report (Germany + Romania)

## How it ran
- Input: [02-listings-clean.csv](02-listings-clean.csv), 871 listings (DE 753 · RO 118). Attributes: [03-attributes.json](03-attributes.json) (the main run's 14, patterns extended with German/Romanian terms). Rules: [main wellness rules](../scannerfinder/03-wellness-rules.md) + [DE/RO addendum](03-wellness-rules.md) (rules 1–9; 7–9 added after the pilot).
- Websites (`fetch_sites.py`): 606 readable, 131 no website, 21 blocked, 87 dead, 14 script-rendered, 12 other; +4 from the project cache. Evidence ~459k tokens (526/listing).
- Pilot of 19 (Brașov, Düsseldorf, Potsdam) read by Claude before the full run, then 22 batches of 40 on Sonnet sub-agents, 3 at a time, paced to the 5-hour window (~6–8% of the window per batch, under 1% of the weekly limit). Total about 3.5M sub-agent tokens.
- Checks: `merge_enriched.py` **871/871, 0 FAIL** + `wellness_lint.py` (extended with German/Romanian claim words and €/lei prices) **0 FAIL**.
- Fixed by Claude after the batches came back: batch 005 (BICOM Body-Check marked NLS; 3 name-only listings marked true), batch 015 (a "confirm the location" line), batch 020 (padding with a hyaluron training and warranty terms), batch 022 (generic "nichtlineares System" marked as the NLS brand).

## Descriptions
Lengths: min 34, median 64, max 109 words. Name-only listings carry Maps facts and a call-ahead line, never a device inferred from the name.

## Attributes (true)
Offers scan sessions 808 (false 4, not enough info 59) · BICOM 102 · Rayonex 66 · NLS 37 · TimeWaver 34 · SCIO/Indigo/Eductor 23 · ZYTO 17 · MORA 8 · NES Health 2 · Asyra 0 · AO Scan 0 · Remote sessions 84 · Free first consultation 47 · Sessions for animals 92

Thin (noindex at launch): **455** of 871.

## For Gate 4 (Dan's decisions)
The full list with slugs is in [03-gate4-notes.md](03-gate4-notes.md). Summary:
1. **Animal-only practices that passed the first filter: 34** (+3 borderline) → exclude, per Dan's 2026-10-13 decision.
2. **offers_scan = false: 4** → exclude: Biofeedback 2014 Satu Mare (device maker), Quantmed Cluj (device seller), Apotheke Marschacht (the "Zyto" is a cytostatics cleanroom), Willmroth (NLS training only).
3. **Other exclusion candidates:** Natur 1 (actually Cape Town), Praxis Volker Gross (site is a farewell note).
4. **Websites to blank** (spam, casino, hair removal, login page, directory, someone else's practice): 7, plus 2 to check.
5. **Location conflicts:** 5 (Konzelmann, Kunert, Schichtl-Ghazouani, Ammerländer Gesundheitshaus, Natur 1).
6. **Possible duplicates:** 4 pairs (Schiff, Lydia Martin, Gerull Kamen/Meschede, HTA Gandesbergen).
7. **not enough info on offers_scan: 59** — mostly name-only listings, many in Romania. Keep as thin (as with the 63 in the main run) or exclude.
8. Judgment calls to confirm (remote from general phone/video consults, BICOM from a supplier link, etc.) are listed in the notes.
