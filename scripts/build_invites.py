#!/usr/bin/env python3
"""Build the merge list for profile-claim invitations (one row per practitioner with an email).

Input:  data/listings_profiled.csv
Output (merge fields used by drafts/invite-email.md: email, business_name, city, country_name, device_phrase,
        profile_clause, search_volume, claim_url):
  data/invite_tier_<T>_email.csv    countries where B2B cold email to published addresses is allowed with opt-out (US, CA, AU, NZ)
  data/invite_tier_<T>_contact.csv  GB / IE / ZA (PECR / GDPR / POPIA need prior consent) + rows whose email was dropped
                                    in data/email_overrides.csv -> send via the site's contact form or phone
Usage: python3 scripts/build_invites.py --tier A [--claim-base https://scannerfinder.com/claim/]
"""
import argparse, csv, re
import os
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
COUNTRY = {"US": "the US", "GB": "the UK", "CA": "Canada", "AU": "Australia", "NZ": "New Zealand", "IE": "Ireland", "ZA": "South Africa", "DE": "Germany", "RO": "Romania"}
# monthly Google searches for scan/bioresonance terms per country (business plan, DataForSEO 2026-10-09)
SEARCHES = {"US": "13,000", "GB": "4,800", "CA": "1,800", "AU": "1,300", "ZA": "400", "IE": "300", "NZ": "280"}
SYMBOL = {"USD": "$", "CAD": "C$", "AUD": "A$", "NZD": "NZ$", "GBP": "£", "EUR": "€", "ZAR": "R"}
KIND = {"bioresonance therapy": "bioresonance", "biofeedback": "biofeedback", "health/wellness scan": "wellness scan",
        "frequency therapy": "frequency therapy", "intolerance/allergy testing": "bioresonance testing"}
BRAND = {"Asyra/Qest4": "QEST4", "SCIO/Indigo/Eductor": "SCIO", "NES Health": "NES", "NLS": "NLS"}


EMAIL_COUNTRIES = {"US", "CA", "AU", "NZ"}


def clean_name(t):
    t = re.sub(r"[^\w\s&'’.,-]", "", t).strip()          # drop emoji / decorative symbols
    t = re.split(r"\s[|–-]\s|\s{2,}", t)[0].strip()      # "Name | tagline" / "Name  tagline" (after emoji) -> "Name"
    return t[:60]


def device_phrase(r):
    fams = [d for d in r["devices_all"].split("; ") if d and "out of scope" not in d]
    if fams:
        b = BRAND.get(fams[0], fams[0])
        return b + "s" if b.lower().endswith("scan") else b + " scans"
    return (KIND.get(r.get("service_kind") or "", "bioresonance")) + " sessions"


def city_of(r):
    if r["city"]:
        return r["city"]
    last = (r.get("address") or "").split(",")[-1].replace(r.get("zip") or "~", "").strip()  # "Forest Row RH18 5LJ" -> "Forest Row"
    return last if last and not any(ch.isdigit() for ch in last) else "your area"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tier", default="A"); ap.add_argument("--claim-base", default="{claim_base}/")
    a = ap.parse_args()
    eo = DATA / "email_overrides.csv"
    drop = {o["cid"] for o in csv.DictReader(open(eo)) if o["action"] == "drop_email"} if eo.exists() else set()
    rows = [r for r in csv.DictReader(open(DATA / "listings_profiled.csv"))
            if r["status"] == "include" and r["invite_tier"] == a.tier and (r["final_email"] or r["contact_page_url"])]
    out = []
    for r in rows:
        r["city"] = city_of(r)
        price = r["scan_price_initial"] or r["scan_price_single"]
        has_price = bool(price and r["scan_price_currency"])
        clause = (f"your {device_phrase(r)}, {r['city']} location and {SYMBOL.get(r['scan_price_currency'], '')}{price} session price"
                  if has_price else f"your {device_phrase(r)} and {r['city']} location")
        email = "" if r["cid"] in drop else r["final_email"].split(";")[0].strip()
        out.append({
            "channel": "email" if email and r["country"] in EMAIL_COUNTRIES else "contact_form",
            "email": email, "contact_page_url": r["contact_page_url"], "contact_form": r["contact_form"], "phone": r["phone"], "business_name": clean_name(r["title"]), "city": r["city"],
            "country": r["country"], "country_name": COUNTRY.get(r["country"], r["country"]), "device_phrase": device_phrase(r),
            "profile_clause": clause, "search_volume": SEARCHES.get(r["country"], ""), "claim_url": a.claim_base + r["cid"],
            "email_quality": r["email_quality"], "invite_score": r["invite_score"], "pays_for_ads": r["pays_for_ads"],
            "cid": r["cid"], "url": r["url"],
        })
    for ch, suffix in (("email", "email"), ("contact_form", "contact")):
        part = [o for o in out if o["channel"] == ch]
        path = DATA / f"invite_tier_{a.tier}_{suffix}.csv"
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(part)
        print(f"{len(part)} rows -> {path.name}")
    n_de = sum(1 for o in out if o["country"] == "DE")
    if n_de:  # Dan, 2026-10-13: always warn - Germany is contact-form only (UWG §7 bans unsolicited B2B email)
        print(f"\n⚠️  GERMANY: {n_de} rows. Contact forms ONLY - no cold email to German practitioners (UWG §7 + GDPR), "
              "even where an email address is known. The email column is for reference, not for sending.")


if __name__ == "__main__":
    main()
