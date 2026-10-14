"""Download each listing's Google Business Profile logo (the `logo` column of the site's listings.csv)
and self-host it as site/public/logos/<slug>.jpg at 128 px, so pages never hotlink googleusercontent.

Usage: python3 scripts/fetch_logos.py [--force]
Writes logos-report.csv next to listings.csv (slug, status, bytes). Re-runs skip files already saved.
"""
import csv, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / 'apps/directory-blueprint/output/scannerfinder/site'
CSV = SITE / 'src/data/listings.csv'
OUT = SITE / 'public/logos'
SIZE = 128
force = '--force' in sys.argv


def sized(url):
    # Google profile photo URLs carry the size as /s44-p-k-no-ns-nd/ or =s44...; ask for SIZE px.
    url = re.sub(r'/s\d+(-[a-z0-9-]+)?/', lambda m: f'/s{SIZE}{m.group(1) or ""}/', url)
    return re.sub(r'=s\d+', f'=s{SIZE}', url)


def fetch(row):
    slug, url = row['slug'], row['logo'].strip()
    dest = OUT / f'{slug}.jpg'
    if not url.startswith('https://'):
        return slug, 'no logo', 0
    if dest.exists() and not force:
        return slug, 'cached', dest.stat().st_size
    req = urllib.request.Request(sized(url), headers={'User-Agent': 'Mozilla/5.0 ScannerFinder logo fetch'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                body = r.read()
                if not r.headers.get('Content-Type', '').startswith('image/') or len(body) < 200:
                    return slug, 'not an image', len(body)
            dest.write_bytes(body)
            return slug, 'ok', len(body)
        except Exception as e:  # noqa: BLE001
            err = str(e)
            time.sleep(1 + attempt)
    return slug, f'error: {err[:60]}', 0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(CSV.open(encoding='utf-8')))
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(fetch, rows))
    with (CSV.parent / 'logos-report.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(['slug', 'status', 'bytes']); w.writerows(results)
    from collections import Counter
    print(Counter(s.split(':')[0] for _, s, _ in results))


if __name__ == '__main__':
    main()
