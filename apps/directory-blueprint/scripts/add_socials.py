#!/usr/bin/env python3
"""Write the social profile links found by fetch_sites.py into a listings CSV as a `socials` column.

Usage:
  python3 scripts/add_socials.py output/<slug>/site/src/data/listings.csv --cache output/<slug>/03-cache/sites
  (run it on 03-listings-enriched.csv too, so the next apply_exclusions.py keeps the column)

Column format: facebook=https://...|instagram=https://...  (networks: facebook, instagram, x, linkedin, youtube, tiktok, pinterest).
A row whose cache file has no socials gets an empty cell. Rerunning overwrites the column.
"""
import argparse, csv, json, os

csv.field_size_limit(10**9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--cache", required=True)
    a = ap.parse_args()
    with open(a.csv, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f); cols = list(rd.fieldnames); rows = list(rd)
    if "socials" not in cols: cols.append("socials")
    found, by_net = 0, {}
    for r in rows:
        p = os.path.join(a.cache, r["slug"] + ".json")
        soc = {}
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f: soc = json.load(f).get("socials") or {}
        r["socials"] = "|".join(f"{k}={v}" for k, v in soc.items())
        if soc: found += 1
        for k in soc: by_net[k] = by_net.get(k, 0) + 1
    with open(a.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    print(f"{found} of {len(rows)} listings have at least one profile link; by network: {dict(sorted(by_net.items(), key=lambda x: -x[1]))}")


if __name__ == "__main__":
    main()
