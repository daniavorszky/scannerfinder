"""Export published session prices for the site's statistics (2026-10-14).

Reads the AI-extracted prices merged by merge_prices.py (data/listings_profiled.csv and
data/batch-de-ro/listings_profiled.csv: scan_price_usd + price_confidence), keeps medium/high confidence,
joins them to the listings that are actually on the site (by Google cid) and writes
site/src/data/session-prices.json = {slug: usd}. The file is read at build time only, to compute
aggregated medians on /statistics/ and the "in numbers" blocks; no individual price is ever shown
(decision 2026-10-12: a practitioner's own price is published only after they confirm it).

Usage: python3 scripts/export_session_prices.py
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / 'apps/directory-blueprint/output/scannerfinder/site'
SOURCES = [ROOT / 'data/listings_profiled.csv', ROOT / 'data/batch-de-ro/listings_profiled.csv']
KEEP = {'high', 'medium'}


def main():
    prices = {}
    for f in SOURCES:
        if not f.exists():
            continue
        for r in csv.DictReader(f.open(encoding='utf-8')):
            usd, conf, cid = (r.get('scan_price_usd') or '').strip(), (r.get('price_confidence') or '').strip(), (r.get('cid') or '').strip()
            if usd and cid and conf in KEEP:
                try:
                    v = float(usd)
                except ValueError:
                    continue
                if 10 <= v <= 1000:  # outside this band is a package or a parsing slip, not a session
                    prices[cid] = round(v)
    out, seen = {}, 0
    for r in csv.DictReader((SITE / 'src/data/listings.csv').open(encoding='utf-8')):
        cid = (r.get('cid') or '').strip()
        if cid in prices:
            out[r['slug']] = prices[cid]
        seen += 1
    (SITE / 'src/data/session-prices.json').write_text(json.dumps(out, indent=0, sort_keys=True))
    print(f'{len(prices)} usable prices, {len(out)} matched to {seen} site listings')


if __name__ == '__main__':
    main()
