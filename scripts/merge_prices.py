#!/usr/bin/env python3
"""Merge AI-extracted session prices into the profiled listings.

Input:  data/listings_profiled.csv (enrich_profile.py) + data/price_batches/out_*.jsonl
        (one JSON per listing, read by AI from website price snippets in data/price_batches/batch_*.jsonl)
Output: data/listings_profiled.csv, adding:
  scan_price_initial / scan_price_followup / scan_price_single / scan_price_currency
  scan_price_usd      initial, else single, else follow-up, converted with fixed approximate FX
  scan_duration_min, remote_price, price_package, business_type, price_confidence, price_evidence
Usage: python3 scripts/merge_prices.py
"""
import csv, json
import os
from collections import Counter
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
FX = {"USD": 1, "CAD": 0.73, "AUD": 0.66, "NZD": 0.60, "GBP": 1.30, "EUR": 1.15, "ZAR": 0.055, "RON": 0.23}  # same as price-tools prototype
COLS = ["scan_price_initial", "scan_price_followup", "scan_price_single", "scan_price_currency", "scan_price_usd",
        "scan_duration_min", "remote_price", "price_package", "business_type", "price_confidence", "price_evidence"]


def main():
    ai = {}
    for f in sorted((DATA / "price_batches").glob("out_*.jsonl")):
        for line in open(f):
            if line.strip():
                o = json.loads(line); ai[str(o["cid"])] = o
    rows = list(csv.DictReader(open(DATA / "listings_profiled.csv")))
    for r in rows:
        o = ai.get(r["cid"], {})
        main_price = next((o.get(k) for k in ("scan_price_initial", "scan_price_single", "scan_price_followup") if o.get(k)), None)
        cur = o.get("currency") or ""
        r.update({
            "scan_price_initial": o.get("scan_price_initial") or "", "scan_price_followup": o.get("scan_price_followup") or "",
            "scan_price_single": o.get("scan_price_single") or "", "scan_price_currency": cur if main_price else "",
            "scan_price_usd": round(main_price * FX.get(cur, 1)) if main_price else "",
            "scan_duration_min": o.get("duration_min") or "", "remote_price": o.get("remote_price") or "",
            "price_package": o.get("package") or "", "business_type": o.get("business_type") or "",
            "price_confidence": o.get("confidence") or "" if o else "", "price_evidence": (o.get("evidence") or "")[:160],
        })
    fields = [k for k in rows[0] if k not in COLS] + COLS
    with open(DATA / "listings_profiled.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

    priced = [r for r in rows if r["scan_price_usd"] != ""]
    print(f"AI rows: {len(ai)} | matched: {sum(r['cid'] in ai for r in rows)} | with scan price: {len(priced)}")
    print("business_type:", Counter(r["business_type"] for r in rows if r["business_type"]).most_common())
    print("confidence:", Counter(r["price_confidence"] for r in priced).most_common())
    usd = sorted(int(r["scan_price_usd"]) for r in priced)
    if usd:
        print(f"USD: min {usd[0]} | median {usd[len(usd)//2]} | max {usd[-1]}")
        by = {}
        for r in priced:
            for d in [d for d in r["devices_all"].split("; ") if d] or ["(no device)"]:
                by.setdefault(d, []).append(int(r["scan_price_usd"]))
        for d, v in sorted(by.items(), key=lambda x: -len(x[1])):
            v.sort(); print(f"  {d}: n={len(v)} median ${v[len(v)//2]} range ${v[0]}-${v[-1]}")


if __name__ == "__main__":
    main()
