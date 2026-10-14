#!/usr/bin/env python3
"""Gate 2: clean a Google Maps listings export (Outscraper, or scripts/fetch_dataforseo.py output) into the directory's listing set.

Usage:
  python3 scripts/clean_listings.py input/listings-raw.csv \
      --niche "pool builder,pool builders,pool construction,custom pools" --category "swimming pool contractor" \
      --state FL --out output/fl-swimming-pool-contractors/02-listings-clean.csv \
      [--owned-phones 4075550100,3055550100] [--min-reviews 1] [--thin-reviews 5]

The output folder is output/<slug>/ with slug = <state code, lowercase>-<category plural, kebab-case>
(fl-swimming-pool-contractors, co-fence-contractors), set at Gate 1. --niche takes the words this trade
puts in its business names (plural and singular), not the broad product word; --category is the Maps
category label. Either flag alone is accepted.

Rules are specified in wiki/framework/listings-cleaning.md. Prints the clean report to stdout
and writes it next to --out as 02-clean-report.md. Rows that carry the category only as a secondary
Google category are kept and counted in the report (with their primary types); whether they stay is
the member's Gate 4 decision, never a Gate 2 drop.
"""
import argparse, csv, json, re, sys, os, unicodedata
from collections import Counter
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

KEEP = ["name","phone","website","address","street","city","state_code","postal_code","county",
        "latitude","longitude","type","subtypes","category","rating","reviews",
        "reviews_per_score_1","reviews_per_score_2","reviews_per_score_3","reviews_per_score_4","reviews_per_score_5",
        "reviews_tags","about","description","posts","working_hours","business_status","verified",
        "photo","logo","place_id","google_id","cid","location_link","area_service",
        "domain","email_1","email_2","email_3","phone_1","phone_2","phone_3","last_updated_time","source"]
ADDED = ["slug","city_slug","owned","thin","featured","featured_cities","claimed"]

def slug(s):
    """Lowercase ASCII, hyphens between runs of anything else. Accented letters are transliterated
    (NFKD, combining marks dropped) so "Cañon City" becomes canon-city, never ca-on-city; a slug that was
    already ASCII does not change. Used for `slug` and `city_slug` alike."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s or "x"

def norm_phone(p):
    d = re.sub(r"\D", "", p or "")
    return d[-10:] if len(d) >= 10 else d

def norm_addr(r):
    return slug((r.get("street") or r.get("address") or "") + " " + (r.get("postal_code") or ""))

def site_domain(u):
    u = (u or "").strip().lower()
    if not u: return ""
    u = re.sub(r"^https?://", "", u).split("/")[0].split("?")[0]
    return u[4:] if u.startswith("www.") else u
TRACKING = re.compile(r"^(utm_|se_|y_source|gclid|fbclid|msclkid|gad_|ref$|source$|campaign$)", re.I)

def clean_url(u):
    """Outscraper keeps the Maps tracking query, often percent-encoded into the path
    (https://site.com/%3Futm_source%3Dgoogle), which 404s. Decode it and drop tracking parameters."""
    u = (u or "").strip()
    if not u or u.lower() == "none": return ""
    if re.search(r"%3F|%26|%3D", u, re.I):
        u = re.sub(r"%3F", "?", re.sub(r"%26", "&", re.sub(r"%3D", "=", u, flags=re.I), flags=re.I), flags=re.I)
    try:
        s = urlsplit(u)
        q = [(k, v) for k, v in parse_qsl(s.query, keep_blank_values=True) if not TRACKING.search(k)]
        return urlunsplit((s.scheme, s.netloc, s.path or "/", urlencode(q), s.fragment))
    except ValueError:
        return u

def to_int(v):
    try: return int(float(v))
    except: return 0

def has_text(r):
    """Prose about the business, for the thin flag: a non-empty description, or an about value that is
    not attribute JSON. Both sources put Google's attributes in about as JSON (the DataForSEO pull on
    every row), so a JSON about is data, not text."""
    if (r.get("description") or "").strip(): return True
    ab = (r.get("about") or "").strip()
    if not ab: return False
    try:
        json.loads(ab); return False
    except ValueError:
        return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv"); ap.add_argument("--niche", default="", help="comma-separated name terms (optional when --category is given)")
    ap.add_argument("--state", required=True, help="two-letter state_code")
    ap.add_argument("--out", required=True); ap.add_argument("--category", default="", help="Maps category fallback (matched in type/subtypes/category)")
    ap.add_argument("--owned-phones", default=""); ap.add_argument("--min-reviews", type=int, default=1)
    ap.add_argument("--thin-reviews", type=int, default=5); ap.add_argument("--city-floor", type=int, default=3)
    ap.add_argument("--max-age-days", type=int, default=365, help="DataForSEO rows only: drop rows whose last_updated_time is older than this (0 = keep all)")
    a = ap.parse_args()
    terms = [t.strip().lower() for t in a.niche.split(",") if t.strip()]
    if not terms and not a.category.strip():
        ap.error("give --niche, --category, or both")
    cat = a.category.strip().lower()
    owned = {norm_phone(p) for p in a.owned_phones.split(",") if p.strip()}

    with open(a.csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    steps = [("rows in", len(rows))]

    rows = [r for r in rows if (r.get("state_code") or "").upper() == a.state.upper()]; steps.append(("state filter", len(rows)))
    rows = [r for r in rows if (r.get("business_status") or "OPERATIONAL").upper() == "OPERATIONAL"]; steps.append(("drop closed", len(rows)))
    if a.max_age_days and rows and rows[0].get("source") == "dataforseo":
        # The Listings database has no closure flag; staleness is the proxy. In the Florida pool
        # comparison (2026-09-29) a 12-month cutoff removed 193 rows: 72 closed per Outscraper,
        # 109 gone from Maps, 12 still open.
        import datetime
        cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=a.max_age_days)).strftime("%Y-%m-%d")
        rows = [r for r in rows if (r.get("last_updated_time") or "9999")[:10] >= cutoff]; steps.append((f"drop not updated in {a.max_age_days} days", len(rows)))
    rows = [r for r in rows if to_int(r.get("reviews")) >= a.min_reviews]; steps.append(("zero reviews out", len(rows)))
    def match_kind(r):
        """How a row passes rule 4: "name" (a niche term in the name), "type" (the category is the
        primary Google category), "secondary" (the category only in subtypes/category), or None."""
        n = (r.get("name") or "").lower()
        if any(t in n for t in terms): return "name"
        if cat:
            if cat in (r.get("type") or "").lower(): return "type"
            if cat in " ".join((r.get(k) or "") for k in ("subtypes","category")).lower(): return "secondary"
        return None
    kept = []
    for r in rows:
        k = match_kind(r)
        if k:
            r["_match"] = k; kept.append(r)   # _match is not in KEEP, so it never reaches the CSV
    rows = kept; steps.append(("name/category match", len(rows)))

    rows.sort(key=lambda r: -to_int(r.get("reviews")))
    seen_p, seen_a, out = set(), set(), []
    for r in rows:
        p, ad = norm_phone(r.get("phone")), norm_addr(r)
        if p and p in seen_p: continue
        if ad and ad in seen_a: continue
        if p: seen_p.add(p)
        if ad: seen_a.add(ad)
        out.append(r)
    rows = out; steps.append(("dedupe phone+address", len(rows)))

    slugs = Counter()
    for r in rows:
        r["city_slug"] = slug(r.get("city"))
        base = f"{slug(r.get('name'))}-{r['city_slug']}"
        slugs[base] += 1
        r["slug"] = base if slugs[base] == 1 else f"{base}-{slug(r.get('postal_code'))}"
        r["owned"] = "true" if norm_phone(r.get("phone")) in owned else "false"
        r["thin"] = "true" if (to_int(r.get("reviews")) < a.thin_reviews or not has_text(r)) else "false"
        r["website"] = clean_url(r.get("website"))
        r["featured"] = ""; r["featured_cities"] = ""; r["claimed"] = ""

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KEEP + ADDED, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

    # Website domains of the kept rows, one per line, for Outscraper's Emails & Contacts scraper
    # (run on the cleaned list only: $3 per 1,000 domains after 500 free, 2026-09-29 pricing).
    domains = sorted({d for d in (site_domain(r.get("website")) for r in rows) if d})
    dom_path = os.path.join(os.path.dirname(a.out) or ".", "02-domains.txt")
    with open(dom_path, "w") as f: f.write("\n".join(domains) + ("\n" if domains else ""))

    cities = Counter(r.get("city") for r in rows)
    floor_cities = {c: n for c, n in cities.items() if n >= a.city_floor}
    types = Counter((r.get("type") or "").strip() or "(no type)" for r in rows)
    secondary = [r for r in rows if r.get("_match") == "secondary"]
    sec_types = Counter((r.get("type") or "").strip() or "(no type)" for r in secondary)
    n_in = steps[0][1]; rate = (len(rows) / n_in * 100) if n_in else 0
    lines = ["# Clean report", "", "| step | rows |", "|---|---|"] + [f"| {k} | {v} |" for k, v in steps]
    dfs = bool(rows) and (rows[0].get("source") == "dataforseo")
    rate_note = ("  (a DataForSEO pull is filtered by category before it arrives, so most rows pass; rows that carry the category only as a secondary one come through too and are counted below for the member's Gate 4 decision)" if dfs
                 else ("  (a loose scrape keeps 2 to 15%, a targeted category export about 20 to 25%; outside both, check the niche terms)" if not 2 <= rate <= 25 else ""))
    lines += ["", f"**Keep rate:** {rate:.1f}%" + rate_note,
              f"**Cities:** {len(cities)}, clearing the {a.city_floor}-listing floor: {len(floor_cities)}, holding {sum(floor_cities.values())} of the {len(rows)} kept rows",
              f"**Owned rows found:** {sum(1 for r in rows if r['owned']=='true')} (listed like any other; see footprint-rules)",
              f"**Thin rows (noindex at launch):** {sum(1 for r in rows if r['thin']=='true')} (under {a.thin_reviews} reviews, or no description text; attribute JSON in `about` does not count as text)",
              f"**Website domains written to 02-domains.txt:** {len(domains)} (upload to Outscraper's Emails & Contacts scraper if the pull had no emails)",
              "", "## Kept rows by primary type", "",
              "The `type` column is the primary Google category. Every other type here got in through the name terms or the category fallback.", ""]
    lines += [f"- {t}: {n}" for t, n in types.most_common()]
    lines += ["", "## Kept only by the category fallback", ""]
    if not cat:
        lines += ["No `--category` given, so every kept row matched on its name."]
    else:
        lines += [f"{len(secondary)} rows carry \"{a.category.strip()}\" only as a secondary category: neither the name terms nor the primary type matched. "
                  "They are kept and flagged here, not dropped; whether they stay is the member's decision at Gate 4 (04-exclusions.csv)."]
        if secondary:
            lines += ["", "Top primary types among them:", ""] + [f"- {t}: {n}" for t, n in sec_types.most_common(10)]
    lines += ["", "## Cities by count", ""]
    lines += [f"- {c}: {n}" for c, n in cities.most_common()]
    rep = "\n".join(lines) + "\n"
    with open(os.path.join(os.path.dirname(a.out) or ".", "02-clean-report.md"), "w") as f: f.write(rep)
    print(rep)

if __name__ == "__main__":
    main()
