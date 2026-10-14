#!/usr/bin/env python3
"""Export the public directory list (what the website shows) from the internal master.

Input:  data/listings_profiled.csv (internal master: all rows, all research columns)
Output: data/directory_listings.csv - only status=include, only public-safe columns, one row per practitioner.
Left out on purpose: emails, outreach scores, ad-pixel / MLM / supplement signals, AI evidence snippets, exclusion reasons.
Prices found on practitioners' websites stay private until the practitioner confirms the profile (decision 2026-10-12):
price columns are blank unless claimed_on_scannerfinder == "yes". The found prices stay in listings_profiled.csv to pre-fill the claim form.
Usage: python3 scripts/export_directory.py
"""
import csv, re, unicodedata
import os
from collections import Counter
from pathlib import Path

DATA = Path(os.environ.get("SF_DATA") or Path(__file__).resolve().parent.parent / "data")
COUNTRY = {"US": "United States", "GB": "United Kingdom", "CA": "Canada", "AU": "Australia", "NZ": "New Zealand",
           "IE": "Ireland", "ZA": "South Africa", "DE": "Germany", "RO": "Romania"}
PUBLIC_DEVICES = {"ZYTO", "BICOM", "Asyra/Qest4", "NES Health", "Rayonex", "NLS", "SCIO/Indigo/Eductor", "MORA",
                  "TimeWaver", "AO Scan"}  # brand pages in scope (business plan); other devices go to device_other
SERVICE = {"bioresonance therapy": "Bioresonance", "biofeedback": "Biofeedback", "health/wellness scan": "Wellness scan",
           "frequency therapy": "Frequency therapy", "intolerance/allergy testing": "Sensitivity testing"}


def slugify(*parts):
    s = unicodedata.normalize("NFKD", " ".join(p for p in parts if p).replace("ß", "ss")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:80]


def clean_name(t):
    t = re.sub(r"[^\w\s&'’.,()/-]", "", t)
    return re.sub(r"\s{2,}", " ", t).strip()


def main():
    rows = [r for r in csv.DictReader(open(DATA / "listings_profiled.csv")) if r["status"] == "include"]
    # city_overrides.csv: city for listings DataForSEO returned without one (found on the site's Impressum or from the address district)
    co = DATA / "city_overrides.csv"
    # force=yes rows also replace a wrong city (the business's own site gives another location) plus address/postcode.
    overrides = {o["cid"]: o for o in csv.DictReader(open(co)) if o["city"]} if co.exists() else {}
    for r in rows:
        o = overrides.get(r["cid"])
        if o and (not (r["city"] or "").strip() or o.get("force") == "yes"):
            r["city"] = o["city"]
            if o.get("force") == "yes":
                r["address"] = o.get("address") or r["address"]; r["zip"] = o.get("postcode") or r["zip"]
    out, seen = [], Counter()
    for r in rows:
        fams = [d for d in r["devices_all"].split("; ") if d]
        public = [d for d in fams if d in PUBLIC_DEVICES]
        other = [d for d in fams if d not in PUBLIC_DEVICES and "out of scope" not in d] + ([r["device_other"]] if r["device_other"] else [])
        name = clean_name(r["title"])
        slug = slugify(name, r["city"]); seen[slug] += 1
        if seen[slug] > 1: slug = f"{slug}-{seen[slug]}"
        price = r["scan_price_initial"] or r["scan_price_single"]
        out.append({
            "id": r["cid"], "slug": slug, "name": name,
            "practitioner_type": r["practitioner_type"], "credentials": r["credentials"],
            "devices": "; ".join(public), "device_models": r["device_models"], "other_devices": "; ".join(dict.fromkeys(other)),
            "service": SERVICE.get(r["service_kind"], "") or ("Bioenergetic scan" if public else ""),
            "remote_sessions": r["remote_scanning"], "free_consultation": r["free_consult"], "animal_sessions": r["animal_scanning"],
            "session_price": price, "followup_price": r["scan_price_followup"], "price_currency": r["scan_price_currency"] if price else "",
            "session_price_usd": r["scan_price_usd"], "session_minutes": r["scan_duration_min"],
            "address": r["address"], "city": r["city"], "region": r["region"], "postcode": r["zip"],
            "country_code": r["country"], "country": COUNTRY.get(r["country"], r["country"]),
            "latitude": r["latitude"], "longitude": r["longitude"],
            "phone": r["phone"], "website": r["url"], "google_maps_url": r["maps_url"],
            "booking_platform": r["booking_platform"] or r["booking_widget"],
            "google_rating": r["rating"], "google_reviews": r["reviews"], "description": r["description"],
            "claimed_on_scannerfinder": "no", "verified": "no", "profile_completeness": "",
        })
    for o in out:  # unconfirmed prices are not published
        if o["claimed_on_scannerfinder"] != "yes":
            for k in ("session_price", "followup_price", "price_currency", "session_price_usd", "session_minutes"):
                o[k] = ""
    for o in out:  # simple completeness % = share of profile fields filled (ordering rule: complete profiles first)
        keys = ["devices", "device_models", "practitioner_type", "session_price", "session_minutes", "phone", "website",
                "booking_platform", "description", "remote_sessions"]
        o["profile_completeness"] = round(100 * sum(bool(o[k]) for k in keys) / len(keys))
    out.sort(key=lambda o: (o["country_code"], o["city"], -o["profile_completeness"], o["name"]))
    with open(DATA / "directory_listings.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    print(f"{len(out)} listings, {len(out[0])} columns -> directory_listings.csv")
    print("countries:", Counter(o["country_code"] for o in out).most_common())
    print("devices:", Counter(d for o in out for d in o["devices"].split("; ") if d).most_common())
    for k in ("devices", "session_price", "phone", "website", "latitude", "booking_platform", "description"):
        print(f"  {k}: {sum(1 for o in out if o[k])}")
    print("duplicate slugs resolved:", sum(v - 1 for v in seen.values() if v > 1))


if __name__ == "__main__":
    main()
