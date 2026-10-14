#!/usr/bin/env python3
"""Read each practitioner's website and extract: devices used, session price, session duration, remote scanning.

Rule-based (no AI, free). Every value keeps the text snippet it came from so it can be checked.

Input:  data/listings_final_contact.csv
Cache:  data/site_text_cache.jsonl  (per url: pages fetched + extracted text, resumable)
Output: data/listings_enriched.csv  adds:
  site_devices        devices named on the site (text or manufacturer link)
  devices_all         union of description devices (clean_listings) + site devices
  device_evidence     short snippet per device
  price_candidates    e.g. "$85 (initial scan); $60 (follow-up)"  - amounts found near session/scan words
  duration_candidates e.g. "60 min; 90 min"
  remote_scanning     yes / '' ; remote_evidence snippet
  site_pages_checked  number of pages read
Usage: python3 scripts/enrich_site_details.py [--workers 16] [--limit N]
"""
import argparse, csv, gzip, html as htmllib, json, re, ssl, urllib.request
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlparse

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
CACHE = DATA / "site_text_cache.jsonl"
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
UAS = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"]
LINK_WORDS = ("service", "treatment", "therap", "scan", "bioresonance", "biofeedback", "price", "pricing", "fee", "cost",
              "rate", "about", "what-we-do", "what-is", "how-it-works", "faq", "book", "session", "zyto", "test", "assessment",
              # DE + RO (2026-10-12)
              "leistung", "angebot", "preise", "kosten", "honorar", "behandlung", "bioresonanz", "ueber", "uber-mich",
              "servicii", "preturi", "tarif", "terapie", "biorezonan", "despre")
PLATFORM = re.compile(r"facebook|instagram|linktr\.ee|booksy|vagaro|yelp|business\.site|glossgenius|massagebook|cliniko|"
                      r"as\.me|10to8|beacons\.ai|canva\.link|bit\.ly|youngliving|freeindex|businessinformationsmap|businformaps", re.I)

# In-scope devices (same families as clean_listings.py) + common out-of-scope devices worth recording.
DEVICES = {
    "ZYTO":        r"\bzyto\b",
    "BICOM":       r"\bbicom\b|\bregumed\b",
    "Asyra/Qest4": r"\basyra\b|\bqest ?4\b",
    "NES Health":  r"\bnes (health|scan|bioenergetic|mihealth)|\bbioenergetix\b|\bmihealth\b|\benergy4life\b|\be4l\b",
    "Rayonex":     r"\brayonex\b|\brayocomp\b|bioresonanz nach paul schmidt",
    "NLS":         r"\bnls\b|\bhunter ?4025\b|\bmetatron\b.{0,40}(nls|hunter|4025|scan|system|bio-?resonance|device|machine|analys)"
                   r"|\boberon\b.{0,30}(nls|scan|bio|device|analys)|\bsensitiv imago\b",
    "SCIO/Indigo/Eductor": r"\bscio\b|\beductor\b|\bindigo\b.{0,20}biofeedback|\bquantum biofeedback\b|\bqxci\b|\bquantum xrroid\b",
    "MORA":        r"\bmora\b.{0,20}(therapy|bio-?resonance|device|super|nova)|\bmed-?tronik\b",
    "TimeWaver":   r"\btimewaver\b",
    "AO Scan":     r"\bao ?scan\b|\bsolex\b|\binner voice\b.{0,20}scan",
    # out of scope / other, recorded for transparency
    "Healy (out of scope)":  r"\bhealy\b",
    "iTOVi (out of scope)":  r"\bitovi\b",
    "Biotron":     r"\bbiotron\b",
    "L.I.F.E. System": r"\bl\.?i\.?f\.?e\.? system\b",
    "Rife":        r"\brife\b.{0,20}(machine|frequenc|therapy|device)",
    "Bio-Well/GDV": r"\bbio-?well\b|\bgdv\b",
    "OligoScan":   r"\boligoscan\b",
    "QRMA (out of scope)": r"quantum resonance magnetic|\bqrma\b",
    "EAV/Vega":    r"\bvega ?test\b|\belectro-?acupuncture according to voll\b|\beav\b",
}
MANUFACTURER_LINKS = {"ZYTO": "zyto.com", "BICOM": "regumed", "Asyra/Qest4": "asyra.com", "NES Health": "neshealth",
                      "Rayonex": "rayonex", "TimeWaver": "timewaver", "AO Scan": "solex", "SCIO/Indigo/Eductor": "qxsubspace"}

MONEY = (r"(?:(?:[$£€]|(?-i:\bR) ?|(?-i:AUD|CAD|NZD|USD|ZAR|EUR|RON) ?)\s?\d{2,4}(?:[.,]\d{2})?"
         r"|\d{2,4}(?:[.,](?:\d{2}|-))?\s?(?:€|euro\b|eur\b|lei\b|ron\b))")
SESSION_WORDS = (r"scan|session|consult|assessment|appointment|test|treatment|bioresonance|biofeedback|zyto|follow[- ]?up|initial|first visit"
                 r"|sitzung|behandlung|analyse|testung|bioresonanz|erstbehandlung|anamnese|folgebehandlung"
                 r"|ședin|sedin|consulta|analiz|biorezonan|terapi|evaluare")
PRICE_RX = re.compile(rf"(?:(?:{SESSION_WORDS})[^$£€\n]{{0,60}}?({MONEY}))|(?:({MONEY})[^\n]{{0,40}}?(?:{SESSION_WORDS}))", re.I)
DURATION_RX = re.compile(r"\b(\d{2,3})\s?(?:-|–|to|bis|până la)?\s?(?:\d{2,3}\s?)?(minuten|min(?:ute)?s?|mins|min\.)"
                         r"|\b(1|1[.,]5|2|one|two|eine|zwei|o|două)\s?(?:hour|hr|stunde|stunden|oră|ora|ore)s?\b", re.I)
REMOTE_RX = re.compile(r"remote (?:scan|session|bioresonance|biofeedback|testing|consult)|distance (?:scan|session|healing|testing)|"
                       r"(?:scan|session|consult)s? (?:are )?(?:also )?(?:available )?(?:online|via zoom|by zoom|over zoom|remotely|by phone)|"
                       r"virtual (?:scan|session|consult)|from the comfort of your (?:own )?home|anywhere in the world|hair (?:sample|and nail)|"
                       r"fernbehandlung|fernanalyse|fernbioresonanz|ferntestung|online-?(?:sitzung|beratung|analyse)|haarprobe|"
                       r"la distanță|la distanta|online prin|ședință online|sedinta online", re.I)


def fetch(url, timeout=12, ua=0):
    req = urllib.request.Request(url, headers={"User-Agent": UAS[ua % 2], "Accept": "text/html,*/*;q=0.8",
                                               "Accept-Encoding": "gzip", "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        if "html" not in (r.headers.get("Content-Type") or "html"):
            return r.geturl(), ""
        data = r.read(1_500_000)
        if r.headers.get("Content-Encoding") == "gzip":
            try: data = gzip.decompress(data)
            except Exception: pass
        return r.geturl(), data.decode("utf-8", "ignore")


def to_text(page):
    page = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", page)
    alts = " ".join(re.findall(r'alt\s*=\s*["\']([^"\']{3,120})["\']', page, re.I))
    txt = re.sub(r"(?s)<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", htmllib.unescape(txt + " " + alts)).strip()


def internal_links(base, page):
    host = urlparse(base).netloc.replace("www.", "")
    scored = []
    for href in re.findall(r'<a\b[^>]*?href\s*=\s*["\']([^"\'#]+)["\']', page, re.I):
        full = urljoin(base, href); hl = full.lower()
        if urlparse(full).netloc.replace("www.", "") != host or hl.endswith((".pdf", ".jpg", ".png")):
            continue
        s = sum(w in hl for w in LINK_WORDS)
        if s: scored.append((-s, full))
    return list(dict.fromkeys(u for _, u in sorted(scored)))[:6]


def crawl(url):
    if PLATFORM.search(url):
        return {"status": "platform", "pages": 0, "text": "", "ext_links": ""}
    home = base = None
    dom = urlparse(url if "//" in url else "http://" + url).netloc.replace("www.", "")
    for v in (url, f"https://{dom}", f"https://www.{dom}", f"http://{dom}"):
        for ua in range(2):
            try: base, home = fetch(v, ua=ua); break
            except Exception: continue
        if home: break
    if not home:
        return {"status": "unreachable", "pages": 0, "text": "", "ext_links": ""}
    texts, ext = [to_text(home)], set(re.findall(r'href\s*=\s*["\'](https?://[^"\']+)', home, re.I))
    pages = 1
    for u in internal_links(base, home):
        try:
            _, p = fetch(u, timeout=10)
            texts.append(to_text(p)); ext |= set(re.findall(r'href\s*=\s*["\'](https?://[^"\']+)', p, re.I)); pages += 1
        except Exception:
            continue
    ext_hosts = " ".join(sorted({urlparse(e).netloc.lower() for e in ext}))
    return {"status": "ok", "pages": pages, "text": " ".join(texts)[:120_000], "ext_links": ext_hosts}


def snippet(text, m, width=70):
    a, b = max(0, m.start() - width), min(len(text), m.end() + width)
    return text[a:b].strip()


def extract(res):
    text, ext = res.get("text", ""), res.get("ext_links", "")
    devices, evidence = [], []
    for name, rx in DEVICES.items():
        m = re.search(rx, text, re.I)
        if m:
            devices.append(name); evidence.append(f"{name}: …{snippet(text, m, 50)}…")
        elif name in MANUFACTURER_LINKS and MANUFACTURER_LINKS[name] in ext:
            devices.append(name); evidence.append(f"{name}: link to {MANUFACTURER_LINKS[name]}")
    prices = []
    for m in PRICE_RX.finditer(text):
        amt = (m.group(1) or m.group(2) or "").replace(" ", "")
        ctx = snippet(text, m, 25)
        if amt and amt not in [p[0] for p in prices]:
            prices.append((amt, ctx))
        if len(prices) >= 4: break
    durations = []
    for m in DURATION_RX.finditer(text):
        win = text[max(0, m.start() - 80): m.end() + 80].lower()
        if re.search(SESSION_WORDS, win):
            d = m.group(0).strip()
            if d.lower() not in [x.lower() for x in durations]:
                durations.append(d)
        if len(durations) >= 3: break
    rm = REMOTE_RX.search(text)
    return {
        "site_devices": "; ".join(devices),
        "device_evidence": " | ".join(evidence)[:900],
        "price_candidates": "; ".join(f"{a} ({c})" for a, c in prices)[:600],
        "duration_candidates": "; ".join(durations),
        "remote_scanning": "yes" if rm else "",
        "remote_evidence": snippet(text, rm, 60) if rm else "",
        "site_pages_checked": res.get("pages", 0),
        "site_crawl_status": res.get("status", ""),
    }


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=16); ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    rows = list(csv.DictReader(open(DATA / "listings_final_contact.csv")))
    cache = {}
    if CACHE.exists():
        for line in open(CACHE):
            o = json.loads(line); cache[o["url"]] = o["res"]
    todo = sorted({r["url"] for r in rows if r["url"] and r["url"] not in cache})[: args.limit]
    print(f"{len(todo)} sites to crawl ({len(cache)} cached)", flush=True)
    with open(CACHE, "a") as cf, ThreadPoolExecutor(args.workers) as ex:
        futs = {ex.submit(crawl, u): u for u in todo}
        for i, f in enumerate(as_completed(futs), 1):
            u = futs[f]
            try: res = f.result()
            except Exception as e: res = {"status": f"error:{type(e).__name__}", "pages": 0, "text": "", "ext_links": ""}
            cache[u] = res
            cf.write(json.dumps({"url": u, "res": res}) + "\n"); cf.flush()
            if i % 50 == 0 or i == len(todo): print(f"  {i}/{len(todo)}", flush=True)

    out = []
    for r in rows:
        ext = extract(cache[r["url"]]) if r["url"] in cache else extract({"status": "no_site" if not r["url"] else ""})
        union = [d for d in r["devices"].split("; ") if d] + [d for d in ext["site_devices"].split("; ") if d]
        out.append({**r, **ext, "devices_all": "; ".join(dict.fromkeys(union))})
    with open(DATA / "listings_enriched.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    c = Counter(); [c.update([d for d in o["devices_all"].split("; ") if d] or ["(none)"]) for o in out]
    print("devices_all:", c.most_common())
    print("with any device:", sum(1 for o in out if o["devices_all"]), "/", len(out),
          "| price:", sum(1 for o in out if o["price_candidates"]),
          "| duration:", sum(1 for o in out if o["duration_candidates"]),
          "| remote:", sum(1 for o in out if o["remote_scanning"]))


if __name__ == "__main__":
    main()
