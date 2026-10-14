"""Second pass after fetch_logos.py: for every listing still without a logo in site/public/logos/, read the
business's own homepage and take its logo, in this order: JSON-LD "logo", an <img> marked as the logo
(class/id/alt/src contains "logo"), apple-touch-icon, an <link rel=icon> of 96 px or more.
og:image is never used (it is usually a banner or a stock photo).

Usage: python3 scripts/fetch_site_logos.py   (--manifest: only rewrite logos.json)
Then writes site/src/data/logos.json ({slug: "/logos/<file>"}) for every logo file on disk.
"""
import csv, json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_logos import SITE, CSV, OUT  # noqa: E402

UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15'}
SKIP_HOSTS = ('facebook.com', 'instagram.com', 'linktr.ee', 'google.com', 'business.site', 'yelp.com')
# Logos reviewed by eye and thrown out (blank white-on-transparent, platform favicons): never fetched again.
REJ = Path(__file__).resolve().parent.parent / 'data/logos-rejected.txt'
REJECTED = set(REJ.read_text().split()) if REJ.exists() else set()
EXT = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp', 'image/svg+xml': '.svg', 'image/gif': '.gif'}


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(); self.ld = []; self.imgs = []; self.icons = []; self._in_ld = False
    def handle_starttag(self, tag, a):
        a = {k: (v or '') for k, v in a}
        if tag == 'script' and 'ld+json' in a.get('type', ''):
            self._in_ld = True
        elif tag == 'img':
            src = a.get('src') or a.get('data-src') or ''
            marks = ' '.join([a.get('class', ''), a.get('id', ''), a.get('alt', ''), src]).lower()
            if src and 'logo' in marks and not src.startswith('data:'):
                self.imgs.append(src)
        elif tag == 'link':
            rel = a.get('rel', '').lower()
            if 'apple-touch-icon' in rel:
                self.icons.append((999, a.get('href', '')))
            elif 'icon' in rel:
                m = re.match(r'(\d+)x', a.get('sizes', ''))
                if m and int(m.group(1)) >= 96:
                    self.icons.append((int(m.group(1)), a.get('href', '')))
    def handle_endtag(self, tag):
        if tag == 'script': self._in_ld = False
    def handle_data(self, d):
        if self._in_ld: self.ld.append(d)


def ld_logo(chunks):
    for c in chunks:
        for m in re.finditer(r'"logo"\s*:\s*(\{[^{}]*\}|"[^"]+")', c):
            v = m.group(1)
            u = re.search(r'"(?:url|contentUrl)"\s*:\s*"([^"]+)"', v) if v.startswith('{') else re.match(r'"([^"]+)"', v)
            if u: return u.group(1).replace('\\/', '/')
    return ''


def get(url, limit=3_000_000):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return r.headers.get('Content-Type', '').split(';')[0].strip(), r.read(limit), r.geturl()


def fetch(row):
    slug, site = row['slug'], row['website'].strip()
    if any(OUT.glob(f'{slug}.*')):
        return slug, 'has logo'
    if slug in REJECTED:
        return slug, 'rejected'
    if not site.startswith('http') or any(h in site for h in SKIP_HOSTS):
        return slug, 'no website'
    try:
        ctype, html, final = get(site)
        s = Scan(); s.feed(html.decode('utf-8', 'replace'))
        cands = [ld_logo(s.ld)] + s.imgs[:2] + [h for _, h in sorted(s.icons, reverse=True)]
        for c in [c for c in cands if c]:
            try:
                ct, body, _ = get(urljoin(final, c))
            except Exception:  # noqa: BLE001
                continue
            if ct in EXT and 300 < len(body) < 1_500_000:
                (OUT / f'{slug}{EXT[ct]}').write_bytes(body)
                return slug, 'ok'
        return slug, 'no logo found'
    except Exception as e:  # noqa: BLE001
        return slug, f'error: {str(e)[:50]}'


def write_manifest():
    files = {p.stem: f'/logos/{p.name}' for p in sorted(OUT.iterdir()) if p.suffix in EXT.values()}
    (SITE / 'src/data/logos.json').write_text(json.dumps(files, indent=0, sort_keys=True))
    return len(files)


def main():
    if '--manifest' in sys.argv:
        return print('logos on disk:', write_manifest())
    rows = list(csv.DictReader(CSV.open(encoding='utf-8')))
    with ThreadPoolExecutor(8) as ex:
        res = list(ex.map(fetch, rows))
    from collections import Counter
    print(Counter(s.split(':')[0] for _, s in res))
    print('logos on disk:', write_manifest(), 'of', len(rows))


if __name__ == '__main__':
    main()
