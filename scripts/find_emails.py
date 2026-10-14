#!/usr/bin/env python3
"""Crawl practitioner websites for contact emails.

Input:  data/listings_include.csv (needs url/domain)
Cache:  data/email_cache.jsonl (one line per domain, appended as results land -> resumable)
Output: data/listings_include_emails.csv with columns
        site_emails  - emails found on the site (same-domain first)
        best_email   - one pick for outreach: same-domain site email > other site email > DataForSEO email
        email_source - site-domain | site-other | dataforseo | ''
        site_status  - ok | no_email_on_site | unreachable | no_site

Fetch helpers adapted from .claude/skills/outscraper-forms-emails/scripts/enrich_contacts.py.
Usage: python3 scripts/find_emails.py [--workers 16]
"""
import csv, gzip, html as htmllib, json, os, re, ssl, argparse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
CACHE = DATA / "email_cache.jsonl"

CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UAS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
]
LINK_WORDS = ("contact", "about", "book", "appointment", "get-in-touch", "reach",
              "kontakt", "impressum", "ueber-uns", "uber-uns", "termin", "despre", "programare")
PATHS = ["/contact", "/contact-us", "/contact/", "/contact-us/", "/about", "/about-us", "/pages/contact",
         "/impressum", "/kontakt", "/impressum/", "/kontakt/", "/despre-noi"]
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,24}")
JUNK = re.compile(r"(sentry|wixpress|example\.|domain\.com|email\.com|yourname|yourdomain|godaddy|squarespace|"
                  r"wix\.com|\.png$|\.jpe?g$|\.gif$|\.webp$|\.svg$|noreply|no-reply|donotreply|@2x|u00|"
                  r"schema\.org|cloudflare|placeholder|test@|user@|name@|mysite\.|example@|sample@|john@doe|jane@doe|@email\.|firstname|lastname)", re.I)


def fetch(url, timeout=12, ua=0):
    req = urllib.request.Request(url, headers={
        "User-Agent": UAS[ua % len(UAS)], "Accept": "text/html,*/*;q=0.8",
        "Accept-Encoding": "gzip", "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        data = r.read(1_500_000)
        if r.headers.get("Content-Encoding") == "gzip":
            try: data = gzip.decompress(data)
            except Exception: pass
        return r.geturl(), data.decode("utf-8", "ignore")


def cf_decode(hexstr):
    k = int(hexstr[:2], 16)
    return "".join(chr(int(hexstr[i:i + 2], 16) ^ k) for i in range(2, len(hexstr), 2))


def extract(page):
    page = htmllib.unescape(page)
    found = set(m.lower() for m in re.findall(r"mailto:([^\"'?>\s]+)", page, re.I))
    found |= set(m.lower() for m in EMAIL_RX.findall(page))
    for h in re.findall(r'data-cfemail="([0-9a-f]+)"', page, re.I) + re.findall(r"/cdn-cgi/l/email-protection#([0-9a-f]+)", page, re.I):
        try: found.add(cf_decode(h).lower())
        except Exception: pass
    clean = set()
    for e in found:
        e = e.strip(".,;:()[]<>\"'").replace("%20", "")
        if EMAIL_RX.fullmatch(e) and not JUNK.search(e) and len(e) < 80:
            clean.add(e)
    return clean


def links(base, page):
    out = []
    for href in re.findall(r'<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\']', page, re.I):
        if any(w in href.lower() for w in LINK_WORDS) and not href.lower().startswith(("mailto:", "tel:")):
            full = urljoin(base, href)
            if urlparse(full).netloc.replace("www.", "") == urlparse(base).netloc.replace("www.", ""):
                out.append(full)
    return list(dict.fromkeys(out))[:4]


def probe(url):
    dom = urlparse(url if "//" in url else "http://" + url).netloc.replace("www.", "")
    home = base = None
    for v in (url, f"https://{dom}", f"https://www.{dom}", f"http://{dom}"):
        for ua in range(2):
            try:
                base, home = fetch(v, ua=ua); break
            except Exception:
                continue
        if home: break
    if not home:
        return {"status": "unreachable", "emails": []}
    emails = extract(home)
    visited = {base}
    for u in links(base, home) + [urljoin(base, p) for p in PATHS]:
        if u in visited or (emails and len(visited) > 3): continue
        visited.add(u)
        try:
            _, p = fetch(u, timeout=10)
            emails |= extract(p)
        except Exception:
            continue
        if len(visited) >= 8: break
    site_dom = urlparse(base).netloc.replace("www.", "").lower()
    ranked = sorted(emails, key=lambda e: (not e.endswith("@" + site_dom) and site_dom.split(".")[0] not in e.split("@")[1], e))
    return {"status": "ok" if ranked else "no_email_on_site", "emails": ranked, "site_dom": site_dom}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=16); args = ap.parse_args()
    rows = list(csv.DictReader(open(DATA / "listings_include.csv")))
    cache = {}
    if CACHE.exists():
        for line in open(CACHE):
            o = json.loads(line); cache[o["url"]] = o["res"]
    todo = sorted({r["url"] for r in rows if r["url"] and r["url"] not in cache})
    print(f"{len(todo)} sites to crawl ({len(cache)} cached)", flush=True)
    with open(CACHE, "a") as cf, ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(probe, u): u for u in todo}
        for i, f in enumerate(as_completed(futs), 1):
            u = futs[f]
            try: res = f.result()
            except Exception as e: res = {"status": f"error:{type(e).__name__}", "emails": []}
            cache[u] = res
            cf.write(json.dumps({"url": u, "res": res}) + "\n"); cf.flush()
            if i % 50 == 0 or i == len(todo): print(f"  {i}/{len(todo)}", flush=True)

    out = []
    for r in rows:
        res = cache.get(r["url"]) if r["url"] else None
        site = [e for e in (res or {}).get("emails", []) if not JUNK.search(e)]
        site_dom = (res or {}).get("site_dom", "")
        dfs = [e.strip() for e in r["emails"].split(";") if e.strip()]
        if site:
            best = site[0]
            src = "site-domain" if site_dom and (best.endswith("@" + site_dom) or site_dom.split(".")[0] in best.split("@")[1]) else "site-other"
        elif dfs:
            best, src = dfs[0], "dataforseo"
        else:
            best, src = "", ""
        status = (res or {}).get("status", "no_site") if r["url"] else "no_site"
        out.append({**r, "site_emails": "; ".join(site), "best_email": best, "email_source": src, "site_status": status})
    with open(DATA / "listings_include_emails.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    from collections import Counter
    print(Counter(o["email_source"] or "none" for o in out))
    print(Counter(o["site_status"] for o in out))


if __name__ == "__main__":
    main()
