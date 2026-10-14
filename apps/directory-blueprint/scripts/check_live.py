#!/usr/bin/env python3
"""Gate 6 helper: check a deployed directory from the outside.

Reads only. Run it against the real domain after the deploy, and against the pages.dev
address to confirm that address is kept out of search.

Usage:
  python3 scripts/check_live.py https://example.com [--pages-dev https://project.pages.dev] [--expect-urls 1076]
"""
import argparse, re, sys, urllib.request, urllib.error

UA = {"User-Agent": "directory-blueprint-check/1.0"}


def get(url):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20)
        return r.status, dict((k.lower(), v) for k, v in r.headers.items()), r.read().decode("utf-8", "replace"), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, dict((k.lower(), v) for k, v in e.headers.items()), e.read().decode("utf-8", "replace"), url
    except Exception as e:
        return 0, {}, str(e), url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base"); ap.add_argument("--pages-dev", default=""); ap.add_argument("--expect-urls", type=int, default=0)
    a = ap.parse_args()
    base = a.base.rstrip("/"); ok = True

    def line(passed, text):
        nonlocal ok
        ok = ok and passed
        print(("PASS  " if passed else "FAIL  ") + text)

    s, h, body, _ = get(base + "/")
    line(s == 200, f"home page answers 200 (got {s})")
    line("<h1" in body, "home page has an H1")
    m = re.search(r'<link rel="canonical" href="([^"]+)"', body)
    line(bool(m), f"home page has a canonical: {m.group(1) if m else 'none'}")
    line('content="noindex' not in body, "home page is not noindex")
    line('data-preview="1"' not in body, "home page shows no preview featured cards (set featuredPreview to false in site.json and rebuild)")

    s, _, body, _ = get(base + "/this-page-does-not-exist-check/")
    line(s == 404, f"an unknown address answers 404 (got {s}). 200 here means the host is serving the home page for every unknown address")

    s, _, body, _ = get(base + "/robots.txt")
    line(s == 200 and "Sitemap:" in body, "robots.txt is served and names the sitemap")

    s, _, body, _ = get(base + "/sitemap-index.xml")
    parts = re.findall(r"<loc>(.*?)</loc>", body)
    line(s == 200 and parts, f"sitemap index is served with {len(parts)} part(s)")
    urls = []
    for p in parts:
        p = base + "/" + p.rsplit("/", 1)[-1]
        _, _, b, _ = get(p); urls += re.findall(r"<loc>(.*?)</loc>", b)
    line(bool(urls), f"sitemap lists {len(urls)} addresses")
    if a.expect_urls: line(len(urls) == a.expect_urls, f"sitemap count matches the launch plan ({a.expect_urls})")

    sample = [u for u in urls if u.count("/") >= 6][:1] + [u for u in urls if u.count("/") == 5][:1]
    for u in sample:
        local = base + "/" + u.split("/", 3)[3]
        s, _, b, _ = get(local)
        line(s == 200 and 'content="noindex' not in b, f"a page from the sitemap answers 200 and is indexable: /{u.split('/', 3)[3]}")

    for path in ("/claim/", "/featured/"):
        s, _, b, _ = get(base + path)
        line(s == 200 and 'content="noindex' in b, f"{path} is served and noindex")

    if a.pages_dev:
        s, h, _, _ = get(a.pages_dev.rstrip("/") + "/")
        line("noindex" in h.get("x-robots-tag", ""), f"the pages.dev address sends X-Robots-Tag: noindex (got '{h.get('x-robots-tag', 'nothing')}')")

    print("\nAll checks passed." if ok else "\nSomething failed. Fix it before the dripfeed starts.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
