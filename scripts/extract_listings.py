#!/usr/bin/env python3
"""Extract Google Maps listings for ScannerFinder.com via DataForSEO Business Listings API.

Credentials: DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD in the workspace-root .env.
Output: data/raw_listings.jsonl (one API item per line) + data/listings_flat.csv (deduped by cid).

Usage:
  python3 scripts/extract_listings.py --dry-run          # plan + call count, no spend
  python3 scripts/extract_listings.py --countries US GB  # subset
  python3 scripts/extract_listings.py                    # all 7 countries
"""
import argparse, base64, csv, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
ROOT = PROJECT.parent.parent
DATA = Path(os.environ.get("SF_DATA") or PROJECT / "data")
ENDPOINT = "https://api.dataforseo.com/v3/business_data/business_listings/search/live"

# Country -> list of "lat,lng,radius_km" circles. Results are filtered by country_code afterwards.
COUNTRIES = {
    "US": ["39.8283,-98.5795,2600", "64.2008,-149.4937,1500", "20.7984,-156.3319,500"],
    "GB": ["54.0000,-2.5000,700"],
    "CA": ["56.1304,-106.3468,3000"],
    "AU": ["-25.2744,133.7751,2500"],
    "ZA": ["-29.0000,24.0000,1000"],
    "IE": ["53.4129,-8.2439,300"],
    "NZ": ["-41.0000,174.0000,900"],
    "DE": ["51.1657,10.4515,500"],
    "RO": ["45.9432,24.9668,450"],
}

# Local-language category terms, searched only in that country (added 2026-10-12 for DE + RO).
LOCAL_TERMS = {
    "DE": ["bioresonanz", "bioresonanztherapie", "bioresonanz-therapie", "bioresonanzanalyse", "bio-resonanz"],
    "RO": ["biorezonanta", "biorezonanță", "biorezonanța", "biorezonantă", "biorezonanta magnetica", "bio-rezonanta"],
}

# Brand -> search terms. "strict" brands are generic words: matched hits must also carry a health signal.
BRANDS = {
    "ZYTO":            {"terms": ["zyto"], "strict": False},
    "BICOM":           {"terms": ["bicom"], "strict": True},
    "Asyra/Qest4":     {"terms": ["asyra", "qest4"], "strict": False},
    "NES Health":      {"terms": ["nes health", "bioenergetix", "nes scan"], "strict": False},
    "Rayonex":         {"terms": ["rayonex", "rayocomp"], "strict": False},
    "NLS":             {"terms": ["metatron", "oberon", "hunter 4025", "nls scan"], "strict": True},
    "SCIO/Indigo":     {"terms": ["scio", "eductor", "quantum biofeedback"], "strict": True},
    "MORA":            {"terms": ["mora therapy", "mora bioresonance"], "strict": False},
    "TimeWaver":       {"terms": ["timewaver"], "strict": False},
    "AO Scan":         {"terms": ["ao scan", "solex"], "strict": True},
    "_category":       {"terms": ["bioresonance", "biofeedback scan", "bio-resonance"], "strict": False},
}
HEALTH_SIGNAL = ("heilprakt", "naturheil", "praxis", "therapie", "gesundheit", "sănătate", "sanatate", "terapie",
                 "cabinet", "naturist", "health", "wellness", "holistic", "naturopath", "chiropract", "nutrition", "bioresonance",
                 "biofeedback", "scan", "therapy", "therapist", "clinic", "acupunct", "homeopath", "energy",
                 "healing", "massage", "integrative", "functional medicine", "alternative medicine")


def load_env():
    env = {}
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    login = os.environ.get("DATAFORSEO_LOGIN") or env.get("DATAFORSEO_LOGIN")
    pw = os.environ.get("DATAFORSEO_PASSWORD") or env.get("DATAFORSEO_PASSWORD")
    if not login or not pw:
        sys.exit("DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD missing from .env")
    return base64.b64encode(f"{login}:{pw}".encode()).decode()


def call(auth, payload):
    req = urllib.request.Request(ENDPOINT, data=json.dumps([payload]).encode(), method="POST",
                                 headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = json.load(r)
            task = body["tasks"][0]
            if task["status_code"] != 20000:
                if task["status_code"] == 40102:  # no search results
                    return [], 0, task.get("cost", 0)
                raise RuntimeError(f'{task["status_code"]} {task["status_message"]}')
            res = (task.get("result") or [{}])[0] or {}
            return res.get("items") or [], res.get("total_count") or 0, task.get("cost", 0)
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt:
                raise
            print(f"  retry after error: {e}", file=sys.stderr)
            time.sleep(3)


def plan(countries):
    for cc in countries:
        for circle in COUNTRIES[cc]:
            for brand, cfg in BRANDS.items():
                for term in cfg["terms"]:
                    for field in ("description", "title"):
                        yield cc, circle, brand, term, field
            for term in LOCAL_TERMS.get(cc, []):
                for field in ("description", "title"):
                    yield cc, circle, "_category", term, field


def has_health_signal(item):
    blob = " ".join(str(item.get(k) or "") for k in ("title", "description", "category")).lower()
    return any(s in blob for s in HEALTH_SIGNAL)


def flatten(item, hits):
    ai = item.get("address_info") or {}
    emails = sorted({c["value"] for c in item.get("contact_info") or [] if c.get("type") == "mail"})
    return {
        "cid": item.get("cid"),
        "title": item.get("title"),
        "category": item.get("category"),
        "country": ai.get("country_code"),
        "region": ai.get("region"),
        "city": ai.get("city"),
        "zip": ai.get("zip"),
        "address": item.get("address"),
        "phone": item.get("phone"),
        "url": item.get("url"),
        "domain": item.get("domain"),
        "emails": "; ".join(emails),
        "is_claimed": item.get("is_claimed"),
        "rating": (item.get("rating") or {}).get("value"),
        "reviews": (item.get("rating") or {}).get("votes_count"),
        "brands_matched": "; ".join(sorted({h[0] for h in hits})),
        "terms_matched": "; ".join(sorted({h[1] for h in hits})),
        "health_signal": has_health_signal(item),
        "description": (item.get("description") or "").replace("\n", " "),
        "maps_url": item.get("check_url"),
        "latitude": item.get("latitude"),
        "longitude": item.get("longitude"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", nargs="+", default=list(COUNTRIES), choices=list(COUNTRIES))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-per-query", type=int, default=1000)
    ap.add_argument("--max-cost", type=float, default=None, help="stop once spend reaches this many USD")
    args = ap.parse_args()

    calls = list(plan(args.countries))
    print(f"{len(calls)} base queries over {args.countries}")
    if args.dry_run:
        return

    auth = load_env()
    DATA.mkdir(exist_ok=True)
    seen, total_cost = {}, 0.0
    with open(DATA / "raw_listings.jsonl", "a") as raw:
        for i, (cc, circle, brand, term, field) in enumerate(calls, 1):
            if args.max_cost is not None and total_cost >= args.max_cost:
                print(f"Cost cap ${args.max_cost:.2f} reached at query {i}/{len(calls)} - stopping.")
                break
            offset = 0
            while True:
                payload = {field: term, "location_coordinate": circle, "limit": 1000, "offset": offset}
                items, total, cost = call(auth, payload)
                total_cost += cost or 0
                kept = 0
                for it in items:
                    if (it.get("address_info") or {}).get("country_code") != cc:
                        continue
                    if BRANDS[brand]["strict"] and not has_health_signal(it):
                        continue
                    raw.write(json.dumps({"q": [cc, brand, term, field], "item": it}) + "\n")
                    entry = seen.setdefault(it["cid"], {"item": it, "hits": []})
                    entry["hits"].append((brand, term))
                    kept += 1
                print(f"[{i}/{len(calls)}] {cc} {brand} {field}='{term}' total={total} got={len(items)} kept={kept} "
                      f"unique={len(seen)} cost=${total_cost:.2f}")
                offset += len(items)
                if not items or offset >= min(total, args.max_per_query):
                    break

    # Rebuild from the full raw log so the CSV covers every run, not only this one.
    seen = {}
    for line in open(DATA / "raw_listings.jsonl"):
        rec = json.loads(line)
        entry = seen.setdefault(rec["item"]["cid"], {"item": rec["item"], "hits": []})
        entry["hits"].append((rec["q"][1], rec["q"][2]))
    rows = [flatten(v["item"], v["hits"]) for v in seen.values()]
    rows.sort(key=lambda r: (r["country"] or "", r["city"] or "", r["title"] or ""))
    out = DATA / "listings_flat.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["cid"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nDone. {len(rows)} unique listings -> {out}  total cost ${total_cost:.2f}")


if __name__ == "__main__":
    main()
