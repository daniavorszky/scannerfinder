#!/usr/bin/env python3
"""Gate 3 helper: read each kept listing's own website into the enrichment cache.

Use when the Outscraper export carries no text to enrich from (empty reviews_tags, posts and
description). Reads the home page plus up to three internal pages whose link looks like
services, about, construction, financing or warranty. No API, no key, no cost.

Usage:
  python3 scripts/fetch_sites.py output/<slug>/02-listings-clean.csv --cache output/<slug>/03-cache/sites \
      [--workers 24] [--timeout 12] [--limit 0] [--retry-failed]

Writes one JSON per listing slug: {slug, website, status, pages: [{url, title, meta, headings, nav, text}],
socials: {facebook, instagram, x, linkedin, youtube, tiktok, pinterest: url}}. The socials are the profile links
found on the pages read (share and login links skipped). A listing that already has a cache file is skipped, so a
rerun only reads what is new. --socials reads just the home page of every cached site that has no socials yet and
adds them, without touching the rest of the cache; scripts/add_socials.py then writes them into the listings CSV.
At the end the script prints the tally by raw status and one summary line by group (readable, no website,
blocked, dead, script-rendered, other), read from the cache for every listing, for the Gate 3 report.
Method is specified in wiki/framework/enrichment.md.
"""
import argparse, csv, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import ssl, urllib.request, urllib.error

csv.field_size_limit(10**9)

# Profile links worth keeping, by network. Order matters: x.com and twitter.com both map to "x".
NETWORKS = (("facebook", "facebook.com"), ("instagram", "instagram.com"), ("x", "x.com"), ("x", "twitter.com"),
            ("linkedin", "linkedin.com"), ("youtube", "youtube.com"), ("tiktok", "tiktok.com"), ("pinterest", "pinterest.com"))
NOT_PROFILE = re.compile(r"/(sharer|share|intent|login|signup|dialog|plugins|home\.php|hashtag|explore|reel/|p/|photo\.php|watch|embed|policies|help|about)\b|[?&](u|url|text|share)=", re.I)


def socials_from(links, page_url):
    """Profile links per network from a page's links, first one wins."""
    out = {}
    for href, _ in links:
        try: u = urljoin(page_url, href).split("#")[0]
        except Exception: continue
        host = urlparse(u).netloc.lower().removeprefix("www.").removeprefix("m.")
        path = urlparse(u).path.rstrip("/")
        for net, dom in NETWORKS:
            if (host == dom or host.endswith("." + dom)) and path and not NOT_PROFILE.search(u):
                if net not in out: out[net] = u
                break
    return out


UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
SOCIAL = ("facebook.com", "instagram.com", "linkedin.com", "yelp.com", "google.com", "youtube.com",
          "x.com", "twitter.com", "nextdoor.com", "houzz.com", "thumbtack.com", "angi.com", "homeadvisor.com",
          "business.site", "linktr.ee", "tiktok.com")
# Inner pages worth reading, any vertical. Add the vertical's own words with --want "term|term".
WANT_BASE = r"service|about|construct|build|install|repair|custom|design|remodel|renovat|financ|warrant|commercial|residential|faq|pricing|process"
WANT = re.compile(WANT_BASE, re.I)
SKIP = re.compile(r"\.(pdf|jpe?g|png|gif|webp|svg|zip|mp4|docx?)($|\?)|/(blog|news|tag|category|cart|wp-login|privacy|terms)\b|^(mailto|tel|javascript):", re.I)
MAX_BYTES = 1_500_000
MAX_TEXT = 8000
DROP = {"script", "style", "noscript", "svg", "template", "iframe"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self.headings, self.links, self.text = "", "", [], [], []
        self._skip = 0; self._in_title = False; self._h = None; self._a = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in DROP: self._skip += 1
        elif tag == "title": self._in_title = True
        elif tag == "meta" and (a.get("name") or a.get("property") or "").lower() in ("description", "og:description"):
            if not self.meta: self.meta = (a.get("content") or "").strip()
        elif tag in ("h1", "h2", "h3"): self._h = []
        elif tag == "a" and a.get("href"): self._a = [a["href"], []]
        if tag in ("p", "br", "div", "li", "h1", "h2", "h3", "h4", "tr", "section"): self.text.append("\n")

    def handle_endtag(self, tag):
        if tag in DROP and self._skip: self._skip -= 1
        elif tag == "title": self._in_title = False
        elif tag in ("h1", "h2", "h3") and self._h is not None:
            h = " ".join("".join(self._h).split())
            if h and len(h) < 140: self.headings.append(h)
            self._h = None
        elif tag == "a" and self._a:
            self.links.append((self._a[0], " ".join("".join(self._a[1]).split())))
            self._a = None

    def handle_data(self, d):
        if self._skip: return
        if self._in_title: self.title += d; return
        if self._h is not None: self._h.append(d)
        if self._a: self._a[1].append(d)
        self.text.append(d)


def clean(s):
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s).strip()


_CTX_OK = ssl.create_default_context()
_CTX_ANY = ssl._create_unverified_context()


def get(url, timeout):
    """Standard library only, so it runs on a stock Mac Python. Tries a verified TLS connection first and
    an unverified one when the certificate is bad (small business sites often have one)."""
    for ctx in (_CTX_OK, _CTX_ANY):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en", "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                ctype = r.headers.get("content-type", "")
                if "html" not in ctype and ctype: return None, f"not html ({ctype[:30]})", r.url
                raw = r.read(MAX_BYTES)
                enc = r.headers.get_content_charset() or "utf-8"
                if enc.lower() == "iso-8859-1": enc = "utf-8"
                return raw.decode(enc, errors="replace"), "ok", r.url
        except urllib.error.HTTPError as e:
            return None, f"http {e.code}", url
        except ssl.SSLError:
            continue
        except urllib.error.URLError as e:
            if isinstance(e.reason, ssl.SSLError) or "CERTIFICATE" in str(e.reason).upper(): continue
            return None, type(e.reason).__name__ if hasattr(e, "reason") else "URLError", url
        except Exception as e:
            return None, type(e).__name__, url
    return None, "ssl", url


def parse(html, url):
    p = Page()
    try: p.feed(html)
    except Exception: pass
    return p, {"url": url, "title": clean(p.title)[:200], "meta": clean(p.meta)[:400],
               "headings": list(dict.fromkeys(p.headings))[:40],
               "nav": list(dict.fromkeys(t for _, t in p.links if t and len(t) < 40))[:60],
               "text": clean("".join(p.text))[:MAX_TEXT]}


def fetch(row, cache, timeout, retry=False):
    path = os.path.join(cache, row["slug"] + ".json")
    if os.path.exists(path):
        if not retry: return "cached"
        with open(path, encoding="utf-8") as f: old = json.load(f)
        if old.get("website") == (row.get("website") or "").strip() and (old["status"] == "ok" or old["status"].startswith(("no website", "social"))): return "cached"
    site = (row.get("website") or "").strip()
    out = {"slug": row["slug"], "website": site, "status": "", "pages": []}
    if not site or site.lower() == "none":
        out["status"] = "no website"
    elif any(s in urlparse(site).netloc.lower() for s in SOCIAL):
        out["status"] = "social or profile link, not read"
    else:
        if not site.startswith("http"): site = "http://" + site
        html, st, final = get(site, timeout)
        out["status"] = st
        if html:
            p, page = parse(html, final); out["pages"].append(page)
            host = urlparse(final).netloc.lower().removeprefix("www.")
            seen, picks = {final.rstrip("/")}, []
            for href, text in p.links:
                if SKIP.search(href): continue
                u = urljoin(final, href).split("#")[0]
                if urlparse(u).netloc.lower().removeprefix("www.") != host: continue
                if u.rstrip("/") in seen: continue
                if WANT.search(urlparse(u).path) or WANT.search(text):
                    seen.add(u.rstrip("/")); picks.append(u)
            out["socials"] = socials_from(p.links, final)
            for u in picks[:3]:
                h2, st2, f2 = get(u, timeout)
                if h2:
                    p2, page2 = parse(h2, f2); out["pages"].append(page2)
                    for k, v in socials_from(p2.links, f2).items(): out["socials"].setdefault(k, v)
            if sum(len(pg["text"]) for pg in out["pages"]) < 200: out["status"] = "ok but empty (script-rendered or parked)"
    with open(path, "w", encoding="utf-8") as f: json.dump(out, f, ensure_ascii=False)
    return out["status"]


GROUPS = ("readable", "no website", "blocked", "dead", "script-rendered", "other")
DEAD = ("gaierror", "ConnectionRefusedError", "ConnectionResetError", "TimeoutError", "timeout", "RemoteDisconnected",
        "IncompleteRead", "ssl", "URLError", "OSError", "BadStatusLine")


def group(status):
    """A raw status folded into one of GROUPS for the summary line."""
    st = (status or "").strip()
    if st == "ok": return "readable"
    if st == "no website": return "no website"
    if st.startswith("ok but empty"): return "script-rendered"
    m = re.match(r"http (\d{3})$", st)
    if m:
        code = int(m.group(1))
        if code in (401, 403, 405, 406, 429, 999): return "blocked"
        if code in (404, 410) or code >= 500: return "dead"
        return "other"
    if st in DEAD or st.endswith("Error"): return "dead"
    return "other"


def summary(rows, cache):
    """One line by group over the cache files of every listing in the CSV."""
    counts = {g: 0 for g in GROUPS}; missing = 0
    for r in rows:
        path = os.path.join(cache, r["slug"] + ".json")
        if not os.path.exists(path): missing += 1; continue
        try:
            with open(path, encoding="utf-8") as f: counts[group(json.load(f).get("status", ""))] += 1
        except Exception: counts["other"] += 1
    line = ", ".join(f"{counts[g]} {g}" for g in GROUPS)
    return f"summary: {line} (of {len(rows)} listings" + (f", {missing} not fetched yet" if missing else "") + ")"


def add_socials(row, cache, timeout):
    """--socials: read the home page again for a cached site and store its profile links."""
    path = os.path.join(cache, row["slug"] + ".json")
    if not os.path.exists(path): return "no cache"
    with open(path, encoding="utf-8") as f: old = json.load(f)
    if "socials" in old: return "had socials"
    if old["status"] != "ok" or not old["pages"]: old["socials"] = {}; st = "not readable"
    else:
        html, st, final = get(old["pages"][0]["url"], timeout)
        old["socials"] = socials_from(parse(html, final)[0].links, final) if html else {}
        st = "ok" if html else st
    with open(path, "w", encoding="utf-8") as f: json.dump(old, f, ensure_ascii=False)
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--cache", required=True)
    ap.add_argument("--workers", type=int, default=24); ap.add_argument("--timeout", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--retry-failed", action="store_true", help="read again every listing whose last read failed or whose URL changed")
    ap.add_argument("--want", default="", help='extra inner-page words for this vertical, regex alternatives, e.g. "new-?pool|enclosure|spa"')
    ap.add_argument("--socials", action="store_true", help="only add social profile links to cached sites that have none yet (home page read again)")
    a = ap.parse_args()
    global WANT
    if a.want.strip(): WANT = re.compile(WANT_BASE + "|" + a.want.strip(), re.I)
    os.makedirs(a.cache, exist_ok=True)
    with open(a.csv, newline="", encoding="utf-8") as f: rows = list(csv.DictReader(f))
    if a.limit: rows = rows[:a.limit]
    tally, done = {}, 0
    with ThreadPoolExecutor(a.workers) as ex:
        futs = [ex.submit(add_socials, r, a.cache, a.timeout) if a.socials else ex.submit(fetch, r, a.cache, a.timeout, a.retry_failed) for r in rows]
        for fu in as_completed(futs):
            try: st = fu.result()
            except Exception as e: st = "error " + type(e).__name__
            tally[st] = tally.get(st, 0) + 1; done += 1
            if done % 200 == 0: print(f"{done}/{len(rows)}", file=sys.stderr, flush=True)
    print(f"listings: {len(rows)}")
    for k, v in sorted(tally.items(), key=lambda x: -x[1]): print(f"  {k}: {v}")
    print(summary(rows, a.cache))


if __name__ == "__main__":
    main()
