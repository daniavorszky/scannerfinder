#!/usr/bin/env python3
"""Gate 5 helper: copy the enriched listings into the site, applying the Gate 4 exclusions.

The enriched CSV is never edited. Decisions made at Gate 4 live in 04-exclusions.csv
(slug, action, reason) and are applied here, so re-running Gates 2 and 3 keeps them.

Actions:
  drop            the listing is left out of the site
  blank_website   the listing stays, its website field is emptied (hijacked or dead site)

Usage:
  python3 scripts/apply_exclusions.py output/<slug>/03-listings-enriched.csv \
      --exclusions output/<slug>/04-exclusions.csv --out output/<slug>/site/src/data/listings.csv
"""
import argparse, csv, sys
from collections import Counter

csv.field_size_limit(10**9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--exclusions", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.csv, newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f); cols = rd.fieldnames; rows = list(rd)
    with open(a.exclusions, newline="", encoding="utf-8-sig") as f:
        ex = list(csv.DictReader(f))
    slugs = {r["slug"] for r in rows}
    unknown = [e["slug"] for e in ex if e["slug"] not in slugs]
    bad = [e for e in ex if e["action"] not in ("drop", "blank_website")]
    if unknown or bad:
        for s in unknown: print(f"ERROR: {s} is in the exclusions file but not in the listings")
        for e in bad: print(f"ERROR: unknown action '{e['action']}' for {e['slug']}")
        sys.exit(1)
    drop = {e["slug"] for e in ex if e["action"] == "drop"}
    blank = {e["slug"] for e in ex if e["action"] == "blank_website"}
    out, done = [], Counter()
    for r in rows:
        if r["slug"] in drop: done["dropped"] += 1; continue
        if r["slug"] in blank: r["website"] = ""; done["website blanked"] += 1
        out.append(r)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
    print(f"listings in: {len(rows)}, written: {len(out)}")
    for k, v in done.items(): print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
