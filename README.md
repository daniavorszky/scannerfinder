# ScannerFinder.com

Code for [scannerfinder.com](https://scannerfinder.com): the Astro site (`apps/directory-blueprint/output/scannerfinder/site/`), its Cloudflare Pages Functions (claim flow, benchmark), and the data scripts (`scripts/`).

- **Deploy:** push to `main`. GitHub Actions builds and uploads to Cloudflare Pages (`.github/workflows/deploy.yml`). Nobody deploys from a laptop.
- **Work here, on the Mac mini** (`~/Code/scannerfinder`), not in iCloud.
- **Plans, decisions, status:** DGA OS → `03-projects/2026-10-scannerfinder-directory-launch/_overview.md` (iCloud). Not in this repo.
- **Internal data** (emails, raw pulls): `data/` is a symlink to that project's `data/` folder and is never committed. After any data change, run `npm run build` on the Mac mini and commit `functions/_data/` (CI cannot rebuild it).
- **Approved claims:** `python3 scripts/publish_claims.py` writes `site/src/data/claims-overlay.json`; commit and push it to publish.
