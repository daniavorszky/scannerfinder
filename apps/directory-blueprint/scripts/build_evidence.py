#!/usr/bin/env python3
"""Gate 3 helper: boil each listing down to a short evidence packet, batched by city.

Reads the clean CSV and the site cache written by fetch_sites.py. For every attribute it pulls
at most two short quotes from the listing's own website. The packet is what gets read at
enrichment, instead of whole pages, so the cost per listing is small and every answer can be
traced to a quote. This script finds quotes; it does not answer attributes.

Usage:
  python3 scripts/build_evidence.py output/<slug>/02-listings-clean.csv \
      --sites output/<slug>/03-cache/sites --out output/<slug>/03-cache/evidence \
      --patterns output/<slug>/03-attributes.json

The pattern source is the per-vertical attribute file written at Gate 3 (each attribute carries a
`pattern`; see scripts/examples/attributes-pool-builders.json for the shape).

Writes one JSON per city slug (a list of packets) and prints the token estimate for the cost gate.
"""
import argparse, csv, json, os, re
from collections import defaultdict

csv.field_size_limit(10**9)
SNIP = 110      # characters kept on each side of a match
PER_ATTR = 2


def load_patterns(path):
    """The pattern source is the per-vertical attribute file (a list of attributes, each with a
    `pattern`), or a plain {key: regex} object. Both compile to {key: regex}."""
    data = json.load(open(path, encoding="utf-8"))
    items = data.items() if isinstance(data, dict) else ((x["key"], x.get("pattern", "")) for x in data)
    pats = {}
    for k, v in items:
        if k.startswith("_"): continue
        if not v: raise SystemExit(f"ERROR: {path}: attribute {k} has no pattern (a regex of the words that count as evidence)")
        try: pats[k] = re.compile(v, re.I)
        except re.error as e: raise SystemExit(f"ERROR: {path}: pattern for {k} does not compile: {e}")
    return pats


def quotes(text, rx):
    out, last = [], -10**9
    for m in rx.finditer(text):
        if m.start() - last < SNIP * 2: continue
        a, b = max(0, m.start() - SNIP), min(len(text), m.end() + SNIP)
        q = " ".join(text[a:b].split())
        core = " ".join(text[max(0, m.start() - 25):m.end() + 25].split())
        if any(core in o for o in out): continue
        out.append(q); last = m.start()
        if len(out) >= PER_ATTR: break
    return out


def about_flags(raw):
    try: d = json.loads(raw)
    except Exception: return []
    flags = []
    for group, items in d.items():
        if not isinstance(items, dict): continue
        for k, v in items.items():
            if v is True: flags.append(k)
            elif v and v is not False: flags.append(f"{k}: {v}")
    return flags[:14]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--sites", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--patterns", required=True)
    a = ap.parse_args()
    pats = load_patterns(a.patterns)
    with open(a.csv, newline="", encoding="utf-8") as f: rows = list(csv.DictReader(f))
    os.makedirs(a.out, exist_ok=True)
    by_city, chars, with_site, hits = defaultdict(list), 0, 0, defaultdict(int)
    for r in rows:
        p = os.path.join(a.sites, r["slug"] + ".json")
        site = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {"status": "not read", "pages": []}
        pages = site["pages"]
        text = "\n".join(pg["text"] for pg in pages)
        # Sentences first: a quote from body copy says more than a run of menu labels.
        body = "\n".join(ln for ln in dict.fromkeys(text.split("\n")) if len(ln) >= 70)
        pk = {"slug": r["slug"], "name": r["name"], "city": r["city"], "maps_type": r["type"],
              "maps_subtypes": r["subtypes"], "rating": r["rating"], "reviews": r["reviews"],
              "stars_1_to_5": [r.get(f"reviews_per_score_{i}", "") for i in range(1, 6)],
              "has_hours": bool((r.get("working_hours") or "").strip() not in ("", "None", "{}")),
              "maps_about": about_flags(r.get("about") or ""),
              "maps_description": (r.get("description") or "").strip() if (r.get("description") or "").strip() != "None" else "",
              "site_status": site["status"]}
        if pages:
            with_site += 1
            pk["site_title"] = pages[0]["title"]; pk["site_meta"] = pages[0]["meta"]
            heads, nav = [], []
            for pg in pages: heads += pg["headings"]; nav += pg["nav"]
            pk["site_headings"] = list(dict.fromkeys(heads))[:14]
            pk["site_menu"] = list(dict.fromkeys(nav))[:24]
            pk["pages_read"] = [pg["url"] for pg in pages]
            ev = {}
            for k, rx in pats.items():
                q = quotes(body, rx)
                if len(q) < PER_ATTR: q = (q + [x for x in quotes(text, rx) if x not in q])[:1 if not q else PER_ATTR]
                if q: ev[k] = q; hits[k] += 1
            pk["quotes"] = ev
        chars += len(json.dumps(pk, ensure_ascii=False))
        by_city[r["city_slug"]].append(pk)
    for c, pks in by_city.items():
        with open(os.path.join(a.out, c + ".json"), "w", encoding="utf-8") as f:
            json.dump(pks, f, ensure_ascii=False, indent=1)
    n = len(rows)
    print(f"listings: {n}, cities: {len(by_city)}, with readable site: {with_site}")
    print(f"evidence total: {chars:,} chars, about {chars // 4:,} tokens, {chars // 4 // max(n, 1)} tokens per listing")
    print("listings with at least one quote, per attribute:")
    for k in pats: print(f"  {k}: {hits[k]}")


if __name__ == "__main__":
    main()
