# ScannerFinder — wellness rules for Gate 3 descriptions

These rules are added to `scripts/enrichment-instructions.md`. Where the two conflict, these win.
Checked automatically by `scripts/wellness_lint.py` (project) after `merge_enriched.py`.

## Why
None of these devices has scientific validation as a diagnostic tool. ScannerFinder is the publisher of every description, so it never repeats a health claim, even when the business makes it on its own site. The register is wellness, never medicine (decision in the project overview).

## Rules
1. **No health claims.** Never write that a device, scan or session diagnoses, detects, tests for, measures, identifies, treats, cures, heals, relieves, fixes or prevents anything: no disease, condition, allergy, intolerance, deficiency, infection, toxin, parasite or symptom. Do this even when the packet says it. Leave the claim out; do not soften it, quote it or attribute it.
2. **Describe the session, not the outcome.** Neutral words: "offers ZYTO scan sessions", "bioresonance sessions with a BICOM device", "biofeedback sessions", "wellness scans". The practitioner's focus can be named in wellness words only: wellbeing, balance, relaxation, stress, energy, lifestyle, nutrition coaching, emotional support, sleep routines.
3. **Banned words in the description** (except inside the business's own name, which is written as is): diagnose, diagnosis, diagnostic, detect, treat, treats, treatment(s), treating, cure(s), heal, heals, healing, disease(s), illness, disorder(s), symptom(s), patient(s), medical, clinical, allergy, allergies, intolerance(s), cancer, Lyme, pain, parasite(s), toxin(s), infection(s), deficiency, deficiencies, prescription, remedy, remedies, test results, root cause.
4. **No prices.** Prices are shown only after the practitioner confirms them (decision 2026-10-12). Don't write amounts, packages or "affordable".
5. **The device** is named only when the packet names it. The business's own Google description (`maps_description`) counts as the business's words, just like its website (Dan, 2026-10-12). Never infer a brand from the business name or the Maps category.
6. **Credentials** only as the packet states them ("naturopathic doctor (ND)", "registered homeopath"), without calling them medical.
7. **Language:** plain, international English. No superlatives, no promises ("transformative", "life-changing", "holistic journey").
