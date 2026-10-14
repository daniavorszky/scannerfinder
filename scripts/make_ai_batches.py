#!/usr/bin/env python3
"""Build the input batches for the two AI reading steps (price + device), from the cached website text.

Input:  data/listings_profiled.csv (after enrich_profile.py) + data/site_text_cache.jsonl
Output: data/price_batches/batch_NN.jsonl  - rows with price_candidates: {cid, title, country, devices, category, text}
        data/device_batches/batch_NN.jsonl - include rows with no device family: {cid, title, category, country,
                                             gbp_description, site_text, ext_links}
Sub-agents read each batch and write out_NN.jsonl next to it (schemas: see merge_prices.py / merge_devices.py and the
existing out_*.jsonl of the main run). Then run merge_prices.py, detect_site_tech.py, merge_devices.py.
Usage: SF_DATA=data/batch-de-ro python3 scripts/make_ai_batches.py [--batches 5]
"""
import argparse, csv, json, os, re
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
PRICE_WORDS = re.compile(r"[$£€]|\b(?:eur|euro|lei|ron)\b|preis|kosten|honorar|pre[țt]|tarif|price|fee", re.I)
SCAN_WORDS = re.compile(r"bio-?resonan|bio-?rezonan|biofeedback|scan|zyto|bicom|rayocomp|metatron|timewaver|analyse|analiz|testung|frequenz", re.I)


def windows(text, rx, width=350, limit=4):
    out, last = [], -10**9
    for m in rx.finditer(text):
        if m.start() - last < width:
            continue
        out.append(text[max(0, m.start() - width): m.end() + width]); last = m.start()
        if len(out) >= limit:
            break
    return " … ".join(out)


def split(rows, n):
    k = max(1, -(-len(rows) // n))
    return [rows[i:i + k] for i in range(0, len(rows), k)]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--batches", type=int, default=5); a = ap.parse_args()
    rows = list(csv.DictReader(open(DATA / "listings_profiled.csv")))
    cache = {}
    for line in open(DATA / "site_text_cache.jsonl"):
        o = json.loads(line); cache[o["url"]] = o["res"]
    price, device = [], []
    for r in rows:
        if r["status"] != "include":
            continue
        res = cache.get(r["url"], {}); text = res.get("text", "")
        if r["price_candidates"] and text:
            price.append({"cid": r["cid"], "title": r["title"], "country": r["country"], "devices": r["devices_all"],
                          "category": r["category"], "text": windows(text, PRICE_WORDS)[:2400]})
        if not r["devices_all"]:
            device.append({"cid": r["cid"], "title": r["title"], "category": r["category"], "country": r["country"],
                           "gbp_description": r["description"][:800],
                           "site_text": (text[:700] + " … " + windows(text, SCAN_WORDS, 250, 3))[:2200] if text else "",
                           "ext_links": res.get("ext_links", "")[:600]})
    for name, items in (("price_batches", price), ("device_batches", device)):
        d = DATA / name; d.mkdir(exist_ok=True)
        for i, chunk in enumerate(split(items, a.batches), 1):
            with open(d / f"batch_{i:02d}.jsonl", "w") as f:
                f.write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in chunk))
        print(f"{name}: {len(items)} rows in {min(a.batches, len(items))} batches")


if __name__ == "__main__":
    main()
