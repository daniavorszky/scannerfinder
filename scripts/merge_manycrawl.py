#!/usr/bin/env python3
"""Merge ManyCrawl website_emails results into data/listings_include_emails.csv.

Input:  data/manycrawl_emails.json  - rows from manycrawl_get_table: [{cid, domain, best_email, all_emails, email_type, email_status}]
        data/listings_include_emails.csv - output of find_emails.py
Output: data/listings_final.csv - adds mc_best_email, mc_all_emails, mc_email_type, mc_email_status and
        final_email / final_email_source with priority: ManyCrawl > own crawl (site) > DataForSEO.
"""
import csv, json, re
import os
from collections import Counter
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
JUNK = re.compile(r"example|mysite\.|yourdomain|domain\.com|sentry|wixpress|noreply|no-reply|\.(png|jpe?g|gif|webp|svg)$|"
                  r"hugedomains|aliexpress|you@company|@website\.com|^tiktok@|govt\.nz|funneltogo|mopro\.com|"
                  r"@thenhs\.|sansoxygen", re.I)
FREE = re.compile(r"@(gmail|yahoo|hotmail|outlook|aol|icloud|live|msn|comcast|me|protonmail|proton|pm|btinternet|bigpond|"
                  r"xtra|mweb|telkomsa|sky|ymail|googlemail|rogers|shaw|sympatico|gmx|web|t-online|freenet|arcor|posteo|mail|yahoo\.co|online)\.", re.I)


def quality(email, domain):
    if not email:
        return "none"
    d, ed = (domain or "").replace("www.", "").lower(), email.split("@")[1].lower()
    if d and (ed == d or ed.split(".")[0] in d or d.split(".")[0] in ed):
        return "own-domain"
    return "freemail" if FREE.search(email) else "third-party?"


def main():
    mc_file = DATA / "manycrawl_emails.json"
    mc = {r["cid"]: r for r in json.load(open(mc_file))} if mc_file.exists() else {}
    mc_by_domain = {r["domain"]: r for r in mc.values()}
    rows = list(csv.DictReader(open(DATA / "listings_include_emails.csv")))
    out = []
    for r in rows:
        m = mc.get(r["cid"]) or mc_by_domain.get((r["domain"] or "").replace("www.", "").lower()) or {}
        mc_best = (m.get("best_email") or "").strip().lower()
        if JUNK.search(mc_best):
            mc_best = ""
        own = "" if JUNK.search(r["best_email"] or "") else r["best_email"]
        if mc_best:
            final, src = mc_best, "manycrawl"
        elif own and r["email_source"].startswith("site"):
            final, src = own, f"own-crawl ({r['email_source']})"
        elif own:
            final, src = own, "dataforseo"
        else:
            final, src = "", ""
        out.append({**r, "mc_best_email": mc_best, "mc_all_emails": m.get("all_emails", ""),
                    "mc_email_type": m.get("email_type", ""), "mc_email_status": m.get("email_status", ""),
                    "final_email": final, "final_email_source": src,
                    "email_quality": quality(final, r["domain"])})
    with open(DATA / "listings_final.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print("final_email:", sum(1 for o in out if o["final_email"]), "/", len(out))
    print(Counter(o["final_email_source"] or "none" for o in out))
    print(Counter(o["email_quality"] for o in out))
    both = [o for o in out if o["mc_best_email"] and o["email_source"].startswith("site")]
    print("both found:", len(both), "agree:", sum(1 for o in both if o["mc_best_email"] == o["best_email"].lower()))
    print("manycrawl filled gaps:", sum(1 for o in out if o["mc_best_email"] and not o["best_email"]))


if __name__ == "__main__":
    main()
