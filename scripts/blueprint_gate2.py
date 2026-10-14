#!/usr/bin/env python3
"""Gate 2 (Directory Blueprint) for ScannerFinder: converts the public export into the kit's
listings layout and applies the kit's cleaning rules, adapted to 7 countries.

Input:  data/directory_listings.csv (831 practitioners, decisions already applied by export_directory.py)
        data/raw_listings.jsonl     (raw DataForSEO: hours, attributes, topics, freshness, categories)
Output: apps/directory-blueprint/output/scannerfinder/02-listings-clean.csv, 02-domains.txt, 02-clean-report.md

Deviations from the kit's clean_listings.py (it isn't edited, its functions are imported):
- no state filter: `state_code` = country code (the country plays the "state" role), `state` = region;
- no niche/category filter: the list was already filtered by brand + manual review;
- zero-review and stale (>365 days) rows are FLAGGED (`zero_reviews`, `stale`), not dropped:
  the decision belongs to Dan at Gate 4 (04-exclusions.csv);
- emails are blanked: the site doesn't need them, they stay in the internal master.
"""
import csv, json, os, sys, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.dirname(HERE)
KIT = os.path.join(PROJ, "apps", "directory-blueprint")
sys.path.insert(0, os.path.join(KIT, "scripts"))
from clean_listings import KEEP, ADDED, slug, norm_phone, norm_addr, site_domain, clean_url, to_int, has_text  # noqa: E402
from fetch_dataforseo import to_row  # noqa: E402

# SF_DATA / SF_SLUG run a separate country batch (e.g. data/batch-de-ro -> output/scannerfinder-de-ro) without touching the main run.
DATA_DIR = os.environ.get("SF_DATA") or os.path.join(PROJ, "data")
SRC = os.path.join(DATA_DIR, "directory_listings.csv")
RAW = os.path.join(DATA_DIR, "raw_listings.jsonl")
OUT_DIR = os.path.join(KIT, "output", os.environ.get("SF_SLUG") or "scannerfinder")
OUT = os.path.join(OUT_DIR, "02-listings-clean.csv")
MAX_AGE_DAYS, THIN_REVIEWS, CITY_FLOOR = 365, 5, 3

# Columns from our profile that the kit doesn't know; they go after the kit's own columns.
OURS = ["country", "region", "practitioner_type", "credentials", "devices", "device_models", "other_devices",
        "service", "remote_sessions", "free_consultation", "animal_sessions", "session_price", "followup_price",
        "price_currency", "session_price_usd", "session_minutes", "booking_platform",
        "claimed_on_scannerfinder", "profile_completeness"]
FLAGS = ["zero_reviews", "stale", "city_fallback"]


def main():
    items = {}
    with open(RAW) as f:
        for line in f:
            it = json.loads(line)["item"]
            items.setdefault(str(it.get("cid")), it)
    with open(SRC, newline="", encoding="utf-8") as f:
        src = list(csv.DictReader(f))

    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=MAX_AGE_DAYS)).strftime("%Y-%m-%d")
    rows, missing_raw = [], 0
    for s in src:
        it = items.get(s["id"])
        if it is None:
            missing_raw += 1; it = {}
        r = to_row(it, s["country_code"]) if it else {k: "" for k in KEEP}
        # Our cleaned values take precedence over the raw ones.
        r.update({
            "name": s["name"], "phone": s["phone"], "website": clean_url(s["website"]), "address": s["address"],
            "city": s["city"], "state": s["region"], "state_code": s["country_code"], "postal_code": s["postcode"],
            "latitude": s["latitude"], "longitude": s["longitude"], "description": s["description"],
            "rating": s["google_rating"], "reviews": s["google_reviews"] or "0",
            "verified": "true" if s["verified"] == "yes" else r.get("verified", "false"),
            "location_link": s["google_maps_url"] or r.get("location_link", ""),
            "email_1": "", "email_2": "", "email_3": "", "source": "dataforseo",
        })
        for k in OURS:
            r[k] = s.get(k, "")
        r["region"] = s["region"]; r["country"] = s["country"]
        r["slug"] = s["slug"]  # already unique, used by the project's export and by the invites
        city = s["city"].strip()
        r["city_fallback"] = "false" if city else "true"
        r["city_slug"] = slug((city or s["region"] or s["country"]).replace("ß", "ss"))  # kit slug() drops ß
        r["zero_reviews"] = "true" if to_int(r["reviews"]) == 0 else "false"
        r["stale"] = "true" if (r.get("last_updated_time") or "9999")[:10] < cutoff else "false"
        r["owned"] = "false"  # Gate 1 Q4: none
        r["thin"] = "true" if (to_int(r["reviews"]) < THIN_REVIEWS or not has_text(r)) else "false"
        r["featured"] = ""; r["featured_cities"] = ""; r["claimed"] = "true" if s["claimed_on_scannerfinder"] == "yes" else ""
        rows.append(r)

    steps = [("rows in (directory_listings.csv)", len(rows))]
    # Dedupe, stricter than the kit (2026-10-12): the kit drops any repeated phone or address, which here
    # dropped separate branches of the same business and different practitioners in a shared clinic.
    # Duplicate = same phone in the same city, or same address with the same phone or website.
    # Keep the row with more reviews; device info from the dropped one moves to the kept one if it's missing.
    rows.sort(key=lambda r: -to_int(r.get("reviews")))
    out, dupes = [], []
    for r in rows:
        p, ad, dom, city = norm_phone(r.get("phone")), norm_addr(r) if r.get("address") else "", site_domain(r.get("website")), slug(r.get("city"))
        hit = None
        for k in out:
            if k["state_code"] != r["state_code"]:
                continue
            kp, kad, kdom = norm_phone(k.get("phone")), norm_addr(k) if k.get("address") else "", site_domain(k.get("website"))
            same_p, same_a, same_d = bool(p) and p == kp, bool(ad) and ad == kad, bool(dom) and dom == kdom
            if (same_p and city == slug(k.get("city"))) or (same_a and (same_p or same_d)):
                hit = k; break
        if hit:
            for col in ("devices", "device_models", "other_devices"):
                if not hit.get(col) and r.get(col): hit[col] = r[col]
            r["_kept"] = hit["slug"]; dupes.append(r)
        else:
            out.append(r)
    rows = out; steps.append(("dedupe (same phone + city, or same address + phone/site)", len(rows)))
    # The same city name in different regions of a country (Springfield IL/MO/MA) → city_slug + region.
    regions_per_city = {}
    for r in rows:
        regions_per_city.setdefault((r["state_code"], r["city_slug"]), set()).add(r["region"].strip())
    collided = 0
    for r in rows:
        if len(regions_per_city[(r["state_code"], r["city_slug"])]) > 1 and r["region"].strip():
            r["city_slug"] = slug(f"{r['city_slug']} {r['region']}".replace("ß", "ss")); collided += 1
    steps.append((f"city names repeated across regions → slug with region ({collided} rows)", len(rows)))
    rows.sort(key=lambda r: (r["state_code"], r["city_slug"], r["slug"]))

    slugs = Counter(r["slug"] for r in rows)
    assert not [k for k, v in slugs.items() if v > 1], "duplicate slugs"

    os.makedirs(OUT_DIR, exist_ok=True)
    cols = KEEP + ADDED + [c for c in OURS if c not in KEEP + ADDED] + FLAGS
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    domains = sorted({d for d in (site_domain(r.get("website")) for r in rows) if d})
    with open(os.path.join(OUT_DIR, "02-domains.txt"), "w") as f:
        f.write("\n".join(domains) + "\n")

    # Report
    n = len(rows); c = lambda k: sum(1 for r in rows if r[k] == "true")
    by_cc = Counter(r["state_code"] for r in rows)
    cities = Counter((r["state_code"], r["city_slug"]) for r in rows)
    floor = {k: v for k, v in cities.items() if v >= CITY_FLOOR}
    no_region = Counter(r["state_code"] for r in rows if not r["region"].strip())
    types = Counter((r.get("type") or "").strip() or "(no type)" for r in rows)
    stale_zero = sum(1 for r in rows if r["stale"] == "true" and r["zero_reviews"] == "true")
    L = ["# Gate 2 — Clean report (ScannerFinder)", "",
         f"Generated by `scripts/blueprint_gate2.py` on {datetime.date.today()}. The cleaning proper (brand filter, manual review of 72 cases, "
         "13 sellers/MLM/training excluded) was done earlier in the project pipeline; this gate converts to the kit's format and checks.", "",
         "| step | rows |", "|---|---|"] + [f"| {k} | {v} |" for k, v in steps] + [
         "", "## Deviations from the kit's rules", "",
         "- **No state filter:** 7 countries; `state_code` = country code, `state` = region.",
         "- **No niche/category filter:** the list is already filtered by device brand + manual review.",
         f"- **Zero reviews: {c('zero_reviews')} rows flagged, NOT dropped** (the kit drops them). Many are solo practitioners found by brand. Decision at Gate 4.",
         f"- **Stale (DataForSEO not updated in {MAX_AGE_DAYS} days, before {cutoff}): {c('stale')} rows flagged, NOT dropped** (the kit drops them as likely closed). {stale_zero} of them also have zero reviews. Decision at Gate 4.",
         "- **Emails removed** from the site file (they stay in the internal master `data/listings_profiled.csv`).",
         "", "## Results", "",
         f"- **Kept:** {n} · duplicates removed: {len(dupes)}" + ("".join(f"\n  - `{d['slug']}` → kept `{d['_kept']}`" for d in dupes) if dupes else ""),
         f"- **By country:** " + " · ".join(f"{k} {v}" for k, v in by_cc.most_common()),
         f"- **Thin (noindex at launch):** {c('thin')} of {n} (under {THIN_REVIEWS} reviews or no description). Gate 3 can clear the flag for those with ≥5 reviews and real text on their site.",
         f"- **Cities:** {len(cities)}; ≥{CITY_FLOOR} listings: {len(floor)}, holding {sum(floor.values())} of {n} listings.",
         f"- **No city in the data:** {c('city_fallback')} (city_slug taken from the region/country — to fix at Gate 4).",
         f"- **No region:** " + (" · ".join(f"{k} {v}" for k, v in no_region.most_common()) or "0") + " — GB/ZA/NZ come without a region from DataForSEO; regions are derived at Gate 4 if we use region hubs.",
         f"- **Hours (working_hours):** {sum(1 for r in rows if r.get('working_hours') not in ('', '{}'))} · **review topics:** {sum(1 for r in rows if r.get('reviews_tags'))} · **claimed on Google:** {sum(1 for r in rows if r.get('verified') == 'true')}",
         f"- **Domains in 02-domains.txt:** {len(domains)}",
         f"- **Owned:** 0 (Gate 1 Q4).",
         "", "## Same address, kept both (to check at Gate 4)", "",
         "Different names at the same address: a shared clinic (keep both) or the same business under two names (exclude one at Gate 4).", ""]
    by_addr = {}
    for r in rows:
        if r.get("address"):
            by_addr.setdefault((r["state_code"], norm_addr(r)), []).append(r)
    L += [f"- {g[0]['city']}: " + " · ".join(f"`{x['slug']}` ({x['reviews']} rev)" for x in g)
          for g in by_addr.values() if len(g) > 1] or ["- none"]
    L += ["", "## Listings by primary Google category (top 20)", ""] + [f"- {t}: {v}" for t, v in types.most_common(20)] + [
         "", f"## Cities with ≥{CITY_FLOOR} listings", ""] + [f"- {cc} {cs}: {v}" for (cc, cs), v in sorted(floor.items(), key=lambda kv: -kv[1])]
    rep = "\n".join(L) + "\n"
    with open(os.path.join(OUT_DIR, "02-clean-report.md"), "w") as f:
        f.write(rep)
    print(rep)


if __name__ == "__main__":
    main()
