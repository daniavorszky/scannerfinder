---
status: prototype
owner: Dan Iavorszky
claude_role: Builds and iterates the price tools; asks before hosting, publishing or sending data anywhere.
last_updated: 2026-10-13
---

# Price Tools — Device Price Index + ROI Calculator

## Purpose

Two lead-magnet tools for scannerfinder.com that collect proprietary B2B data: what practitioners paid for their device (unlock-by-contribution, Glassdoor model) and buy-intent leads from the ROI calculator. Spec: [device-price-tools-spec.md](../../research/device-price-tools-spec.md).

## Load First

- Spec: [research/device-price-tools-spec.md](../../research/device-price-tools-spec.md)
- Seed prices: [data/device-prices-seed.csv](../../data/device-prices-seed.csv) (mirrored in the `SEED` array in `index.html` — update both)
- Project: [_overview.md](../../_overview.md)

## Stack

Single static `index.html` (vanilla JS, Nunito Sans from Google Fonts), branding from scannerfinder.com. Logos in `assets/` (`logo-white.png` dark backgrounds, `logo-dark.png` light). Storage: browser localStorage only (`sf_reports`, `sf_unlocked`, `sf_leads`). No secrets, no external writes.

## Run

```bash
python3 serve.py 8795
```

Then open http://localhost:8795. The in-app preview (`scannerfinder-price-tools` in `.claude/launch.json`) serves a copy from the session scratchpad because macOS blocks the preview process from reading iCloud Drive; re-copy after edits.

## Verification

2026-10-12: gate unlocks after a valid report; median shows only at n ≥ 5 per model; demo button (labelled DEMO) exercises the thresholds; ROI checked by hand for ZYTO Elite (upfront $15,950, net $1,771/mo, payback 9.0 months, 4 sessions/week for 12-month payback); no horizontal scroll at 375px; no console errors.

## Live

- 2026-10-13: ROI calculator ported to the site as [/tools/roi-calculator/](../directory-blueprint/output/scannerfinder/site/src/pages/tools/roi-calculator.astro) (first entry in `src/data/tools.json`). Calculator only; the lead form waits for a form endpoint. Device defaults now live in both files: keep them in sync.
- 2026-10-13: **ZYTO Evox** added (both files): no ZYTO list price; modelled as hand cradle $269 + Trinity CZS $1,200 + $350/month software access (practitionerprogram.com, third-party ZYTO program) + session $130 (median of 5 practitioner sites publishing an EVOX price, from `data/site_text_cache.jsonl`). Low-confidence; replace with a ZYTO quote when available.

## Housekeeping

- Keep `SEED` in sync with the CSV.
- Remove the demo button and prototype banner before going live.

## Archive Criteria

Archive when the tools are rebuilt on the production stack (step 2), or if Dan drops the feature.
