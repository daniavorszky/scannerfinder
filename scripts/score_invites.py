#!/usr/bin/env python3
"""Score listings for the claim-invite order (written down 2026-10-13; the main run computed it inline on 2026-10-12).

invite_score: ad pixel +3; claimed Google profile, website that loads (site_crawl_status ok), booking (link or widget), published scan price,
email, >=10 Google reviews, email-marketing tool +1 each.  invite_tier: A >= 6, B 4-5, C <= 3. Blank for non-include rows.
Input/output: data/listings_profiled.csv (in place).  Usage: [SF_DATA=...] python3 scripts/score_invites.py [--check]
--check only compares the formula with the scores already in the file.
"""
import argparse, csv, os
from collections import Counter
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")


def score(r):
    s = 3 if r.get("pays_for_ads") == "yes" else 0
    s += sum(bool(x) for x in (r.get("is_claimed") == "True", r.get("site_crawl_status") == "ok", r.get("booking_platform") or r.get("booking_widget"),
                               r.get("scan_price_usd"), r.get("final_email"), r.get("email_tool")))
    s += int(float(r.get("reviews") or 0) >= 10)
    return s


def tier(s):
    return "A" if s >= 6 else "B" if s >= 4 else "C"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    rows = list(csv.DictReader(open(DATA / "listings_profiled.csv")))
    if a.check:
        old = [r for r in rows if r.get("invite_score")]
        print(f"formula matches stored score: {sum(str(score(r)) == r['invite_score'] for r in old)}/{len(old)}")
        return
    for r in rows:
        inc = r["status"] == "include"
        r["invite_score"] = str(score(r)) if inc else ""
        r["invite_tier"] = tier(score(r)) if inc else ""
    with open(DATA / "listings_profiled.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(Counter((r["country"], r["invite_tier"]) for r in rows if r["invite_tier"]).most_common())


if __name__ == "__main__":
    main()
