# ScannerFinder DE + RO — wellness rules for Gate 3 descriptions

All rules in [../scannerfinder/03-wellness-rules.md](../scannerfinder/03-wellness-rules.md) apply unchanged (English output, no health claims, no prices, device only when named). Additions for Germany and Romania (2026-10-12):

1. **Source text is German or Romanian; the description is written in English.** Translate facts, never claims. `trace.<key>` stays copied exactly from the packet, in the packet's language.
2. **German legal context (HWG, UWG).** German courts treat bioresonance health claims as misleading advertising. Do not carry over anything from "Bioresonanztherapie bei Allergien / Schmerzen / Rauchentwöhnung", "Diagnose", "Heilung", "Testung auf Unverträglichkeiten", "Entgiftung", "Ausleitung". Leave these out entirely.
3. **Professional titles are kept as stated** and translated plainly: Heilpraktiker(in) → "Heilpraktiker (state-licensed alternative practitioner)" on first use (not "non-medical": the lint bans "medical"), then "Heilpraktiker"; Dr. med. / Facharzt → "physician" + specialty; Zahnarzt → "dentist"; medic specialist / medic primar → "physician". Never call a Heilpraktiker a doctor.
4. **Doctors' practices** (dermatology, urology, paediatrics, ENT, dentistry…) are listed for their bioresonance or biofeedback sessions only. Name the specialty in one neutral clause; never describe their medical services, examinations or insurance billing.
5. **Romanian clinics** often advertise "analiză", "testare", "depistare", "tratament" with Chinese analyzers or Metatron: none of it goes in. Write "bioresonance sessions" or "wellness scans".
6. **Place names** keep their local spelling (München, Köln, Iași, Timișoara); the region is not translated.
7. **Invasive or prescription-style offers are left out** of the services list, also for Heilpraktiker: infusions (Vitamin-/Infusionstherapie), injections, bloodletting (Aderlass), leech therapy (Blutegel), ozone, cryolipolysis, chelation. Name the non-invasive wellness offers only (added after the pilot, 2026-10-13).
8. **Never name German New Medicine (GNM, Germanische Heilkunde, Hamer)** or similar disease-cause doctrines, in any language (Noua Medicină Germanică). Leave it out entirely.
9. **A listing whose own text puts it in another country or city** is not described around the conflict ("confirm the location"): write the description from what is offered and flag the slug in the batch report for exclusion at Gate 4.
