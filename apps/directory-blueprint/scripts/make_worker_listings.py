#!/usr/bin/env python3
"""Writes the compact listings file the mail Worker matches senders against.

  python3 scripts/make_worker_listings.py output/<slug>/site/src/data/listings.csv output/<slug>/worker/src/listings.json

One short record per listing: slug, name, city, phone digits, website host, rating, reviews, featured flag.
"""
import csv, json, re, sys
from urllib.parse import urlparse

csv.field_size_limit(10**9)
src, out = sys.argv[1], sys.argv[2]
rows = []
for r in csv.DictReader(open(src, encoding="utf-8-sig")):
    host = urlparse((r.get("website") or "").strip()).netloc.lower().removeprefix("www.")
    rows.append({"slug": r["slug"], "name": r["name"], "city": r["city"], "phone": re.sub(r"\D", "", r.get("phone") or "")[-10:],
                 "host": host, "rating": r.get("rating") or "", "reviews": r.get("reviews") or "", "featured": (r.get("featured") or "").strip() or ""})
json.dump(rows, open(out, "w"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(rows)} listings written to {out}")
