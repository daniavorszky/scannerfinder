#!/usr/bin/env python3
"""Gate 1/2: pull the listings for one Maps category set in one state from the DataForSEO
Business Listings API and write them as input/listings-raw.csv in the Outscraper column
layout, so scripts/clean_listings.py (Gate 2) runs unchanged.

Usage:
  python3 scripts/fetch_dataforseo.py --find-category pool            # which category ids exist
  python3 scripts/fetch_dataforseo.py --category swimming_pool_contractor --state Florida --state-code FL --estimate
  python3 scripts/fetch_dataforseo.py --category swimming_pool_contractor --state Florida --state-code FL \
      --out input/listings-raw.csv [--max-rows 500] [--min-reviews 1] [--yes]

Credentials (never printed, never shipped, never in this folder): the script reads the login
from the DataForSEO connection the member made in their own Terminal, either with
`python3 scripts/connect_dataforseo.py` (asks for the API login and password, checks them, saves
them) or with the Gear Up lesson's command (`claude mcp add -s user dataforseo -e
DATAFORSEO_LOGIN='...' -e DATAFORSEO_PASSWORD='...' -- npx -y dataforseo-mcp-server@latest`).
Both store the login in Claude Code's own settings, ~/.claude.json. It also accepts
DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD in the environment and a Claude Desktop stdio entry. A
claude.ai connector alone (OAuth) carries no login a script can use. Get the API login at https://app.dataforseo.com/api-access (the API login is the account
email; the API password is separate from the site password). The same account powers the DataForSEO
MCP connector, but the connector is for research, not for a pull of tens of thousands of rows:
this script talks to the REST API directly.

Money: Search costs $0.012 per request (up to 1,000 items) plus $0.00036 per item (published
rates, 2026-09-29). --estimate makes three requests (about five cents): the row count with the
projected cost, how many rows carry the category as their primary one, and how many have a
website. It prints a VERTICAL FLAG line only when the category is clearly a bad fit for a
directory in that state (fewer than 100 primary-category businesses, or fewer than half with a
website); otherwise it says there is none and the build goes on. A real pull asks for confirmation unless --yes is given. --min-reviews 1
(default) filters zero-review rows server-side, which Gate 2 would drop anyway, so you do not
pay for them.

Freshness: rows carry last_updated_time from DataForSEO's database (in the September 2026
sample, 10 to 18 days old). It is a database, not a same-day scrape. Say so in the FAQ.
"""
import argparse, base64, csv, json, math, os, re, sys, time, urllib.request, urllib.error

API = "https://api.dataforseo.com/v3/business_data/business_listings/search/live"
CATEGORIES_API = "https://api.dataforseo.com/v3/business_data/business_listings/categories"
PRICE_REQUEST, PRICE_ITEM, PAGE = 0.012, 0.00036, 1000
# The two hard limits behind a VERTICAL FLAG. Deliberately low: a flag interrupts a member who has
# already chosen, so it fires only when the directory would clearly be thin (Shawn, 2026-10-01).
FLAG_MIN_PRIMARY, FLAG_MIN_SITE_SHARE = 100, 0.5
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CLAUDE_CONFIGS = [os.path.expanduser("~/.claude.json"),
                  os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json"),
                  os.path.join(os.environ.get("APPDATA", ""), "Claude", "claude_desktop_config.json")]

COLUMNS = ["name","phone","website","domain","address","street","city","state","state_code","postal_code","county",
           "latitude","longitude","type","subtypes","category","rating","reviews",
           "reviews_per_score_1","reviews_per_score_2","reviews_per_score_3","reviews_per_score_4","reviews_per_score_5",
           "reviews_tags","about","description","posts","working_hours","business_status","verified",
           "photos_count","photo","logo","place_id","google_id","cid","location_link","area_service",
           "email_1","email_2","email_3","phone_1","phone_2","phone_3","last_updated_time","source"]


def _basic(login, password):
    return "Basic " + base64.b64encode(f"{login}:{password}".encode()).decode()


def _clean(v):
    """A value typed with quotes in a shell that keeps them (cmd.exe) arrives as 'value'. Drop one matching pair."""
    v = (v or "").strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        v = v[1:-1]
    return v


PY = "python" if os.name == "nt" else "python3"   # what the member types; python3 on Windows is a Store stub
NO_LOGIN = ("No DataForSEO login found on this computer. Open a Terminal of your own (not this chat) and run:\n"
            f'  {PY} "{os.path.join(HERE, "connect_dataforseo.py")}"\n'
            "It asks for the API login and API password from app.dataforseo.com/api-access, checks them and saves them "
            "in Claude Code's settings. Or run the Gear Up lesson's command yourself, with single quotes around both values:\n"
            "  claude mcp add -s user dataforseo -e DATAFORSEO_LOGIN='<api login>' -e DATAFORSEO_PASSWORD='<api password>' -- npx -y dataforseo-mcp-server@latest\n"
            "(if the Terminal says claude is not found, start the line with ~/.local/bin/claude). "
            "A claude.ai connector alone is an OAuth link and carries no login this script can read. "
            "Never paste the login into the chat.")
REJECTED = ("DataForSEO rejected the saved login (401). The API password is not the password you sign in with: copy both "
            "values from app.dataforseo.com/api-access (Reset API password emails a new one), then run in a Terminal of your own:\n"
            f'  {PY} "{os.path.join(HERE, "connect_dataforseo.py")}"\n'
            "It replaces the saved entry. Never paste the login into the chat.")


def _auth_from_server(cfg):
    """One mcpServers entry: stdio with the login in env, or http with a Basic header. OAuth entries carry nothing."""
    if not isinstance(cfg, dict):
        return None
    env = cfg.get("env") or {}
    login = _clean(env.get("DATAFORSEO_LOGIN") or env.get("DATAFORSEO_USERNAME")); password = _clean(env.get("DATAFORSEO_PASSWORD"))
    if login and password:
        return _basic(login, password)
    hdr = (cfg.get("headers") or {}).get("Authorization") or ""
    if hdr.lower().startswith("basic ") and "dataforseo" in json.dumps(cfg).lower():
        return hdr
    return None


def load_credentials():
    """The saved login, in this order: the user-scope entry named dataforseo (what connect_dataforseo.py
    and the lesson's command write), the environment, then any other entry that carries a login. The
    helper's entry comes first so an older entry or a placeholder in a shell profile cannot shadow it."""
    named, others = [], []
    for path in CLAUDE_CONFIGS:
        if not os.path.isfile(path):
            continue
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        top = d.get("mcpServers") or {}
        if "dataforseo" in top:
            named.append(top["dataforseo"])
        others += [cfg for name, cfg in top.items() if name != "dataforseo"]
        for proj in (d.get("projects") or {}).values():
            others += list(((proj or {}).get("mcpServers") or {}).values())
    for cfg in named:
        auth = _auth_from_server(cfg)
        if auth:
            return auth
    login = _clean(os.environ.get("DATAFORSEO_LOGIN") or os.environ.get("DATAFORSEO_USERNAME"))
    password = _clean(os.environ.get("DATAFORSEO_PASSWORD"))
    if login and password:
        return _basic(login, password)
    for cfg in others:
        auth = _auth_from_server(cfg)
        if auth:
            return auth
    sys.exit(NO_LOGIN)


def post(auth, task, retries=3, url=API):
    body = json.dumps([task]).encode()
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "Authorization": auth})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
            break
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit(REJECTED)
            if e.code == 402:
                sys.exit("DataForSEO says the account balance is too low (402). Top up at app.dataforseo.com, then run this again.")
            if attempt == retries - 1:
                sys.exit(f"DataForSEO answered {e.code} three times. Try again in a few minutes.")
            time.sleep(3 * (attempt + 1))
        except (urllib.error.URLError, OSError) as e:
            if attempt == retries - 1:
                sys.exit(f"Could not reach DataForSEO ({getattr(e, 'reason', e)}). Check the internet connection and run this again.")
            time.sleep(3 * (attempt + 1))
    if data.get("status_code") != 20000:
        sys.exit(f"DataForSEO error {data.get('status_code')}: {data.get('status_message')}")
    t = data["tasks"][0]
    if t.get("status_code") != 20000:
        sys.exit(f"DataForSEO task error {t.get('status_code')}: {t.get('status_message')}")
    res = (t.get("result") or [{}])[0]
    return res, float(t.get("cost") or 0)


def base_task(a):
    filters = [["address_info.region", "=", a.state]]
    if a.min_reviews > 0:
        filters += ["and", ["rating.votes_count", ">=", a.min_reviews]]
    return {"categories": a.category, "filters": filters,
            "order_by": ["rating.votes_count,desc"]}


def count(auth, a, extra):
    """Rows matching the pull's own filters plus one more condition. One request, no items kept."""
    task = dict(base_task(a), limit=1)
    task["filters"] = task["filters"] + ["and", extra]
    res, cost = post(auth, task)
    return int(res.get("total_count") or 0), cost


def health(auth, a, sample):
    """How many of the rows carry the category as their primary one, and how many have a website.
    The primary category is a label ("Self-storage facility") while the pull works on ids
    (self_storage_facility), and the label cannot be derived from the id (hyphens, apostrophes, two
    spellings of one label). So the labels are read from a sample of the rows themselves. Returns
    primary=None when no sampled row carries the category as its primary one: not measured, never a flag."""
    wanted = {c.lower() for c in a.category}
    labels = sorted({it.get("category") for it in sample
                     if it.get("category") and re.sub(r"[^a-z0-9]+", "_", it["category"].lower()).strip("_") in wanted})
    primary, c1 = None, 0.0
    if labels:
        primary, c1 = count(auth, a, ["category", "in", labels])
    sites, c2 = count(auth, a, ["domain", "<>", None])
    return primary, sites, c1 + c2


def vertical_flags(total, primary, sites, a):
    """The reasons this category in this state is clearly a bad fit. Empty for nearly every real vertical."""
    out = []
    if total == 0:
        return [f"no reviewed business is filed under {', '.join(a.category)} in {a.state}. That is almost always a spelling: "
                "check the category id (--find-category) and the state name, fix it and run the estimate again."]
    if primary is not None and primary < FLAG_MIN_PRIMARY:
        out.append(f"only {primary:,} business{'' if primary == 1 else 'es'} in {a.state} carr{'ies' if primary == 1 else 'y'} this category as the primary one (under {FLAG_MIN_PRIMARY}), "
                   "so few cities would clear the three-business floor and the directory would be thin.")
    if sites / total < FLAG_MIN_SITE_SHARE:
        out.append(f"only {sites / total:.0%} of them have a website (under half), and the Blueprint fills each listing from the business's own site, "
                   "so most pages would be a name and a phone number.")
    return out


def s(v):
    return "" if v is None else str(v)


def own_domain_first(mails, domain):
    d = (domain or "").lower().replace("www.", "")
    own = [m for m in mails if d and m.lower().endswith("@" + d)]
    return own + [m for m in mails if m not in own]


def to_row(it, state_code):
    ai = it.get("address_info") or {}
    rating = it.get("rating") or {}
    dist = it.get("rating_distribution") or {}
    topics = it.get("place_topics") or {}
    ci = it.get("contact_info") or []
    mails = own_domain_first([c["value"] for c in ci if c.get("type") == "mail"], it.get("domain"))
    main_phone = re.sub(r"\D", "", s(it.get("phone")))
    phones = [c["value"] for c in ci if c.get("type") == "telephone" and re.sub(r"\D", "", c["value"])[-10:] != main_phone[-10:]]
    phones = list(dict.fromkeys(phones))
    wt = (it.get("work_time") or {}).get("work_hours") or {}
    row = {
        "name": s(it.get("title")), "phone": s(it.get("phone")), "website": s(it.get("url")), "domain": s(it.get("domain")),
        "address": s(it.get("address")), "street": s(ai.get("address")), "city": s(ai.get("city")), "state": s(ai.get("region")),
        "state_code": state_code, "postal_code": s(ai.get("zip")), "county": "",
        "latitude": s(it.get("latitude")), "longitude": s(it.get("longitude")),
        "type": s(it.get("category")), "subtypes": ", ".join(it.get("additional_categories") or []), "category": s(it.get("category")),
        "rating": s(rating.get("value")), "reviews": s(rating.get("votes_count") or 0),
        "reviews_tags": ", ".join(f"{k} ({v})" for k, v in sorted(topics.items(), key=lambda kv: -kv[1])),
        "about": json.dumps(it.get("attributes") or {}, ensure_ascii=False),
        "description": s(it.get("description")), "posts": "",
        "working_hours": json.dumps(wt.get("timetable") or {}, ensure_ascii=False),
        "business_status": "OPERATIONAL",  # the Listings database carries no closure flag; Gate 2 keeps these rows
        "verified": "true" if it.get("is_claimed") else "false",
        "photos_count": s(it.get("total_photos")), "photo": s(it.get("main_image")), "logo": s(it.get("logo")),
        "place_id": s(it.get("place_id")), "google_id": s(it.get("feature_id")), "cid": s(it.get("cid")),
        "location_link": s(it.get("check_url")), "area_service": "",
        "last_updated_time": s(it.get("last_updated_time")), "source": "dataforseo",
    }
    for i in range(1, 6):
        row[f"reviews_per_score_{i}"] = s(dist.get(str(i), 0))
    for i in range(3):
        row[f"email_{i+1}"] = mails[i] if i < len(mails) else ""
        row[f"phone_{i+1}"] = phones[i] if i < len(phones) else ""
    return row


def main():
    ap = argparse.ArgumentParser(description="Pull one category set in one state from DataForSEO Business Listings.")
    ap.add_argument("--find-category", metavar="WORD",
                    help='list DataForSEO category ids containing WORD (e.g. "pool") and exit; free request')
    ap.add_argument("--category", action="append", default=[],
                    help="DataForSEO category id, repeatable (max 10), e.g. swimming_pool_contractor")
    ap.add_argument("--state", help='state name as Google writes it, e.g. "Florida"')
    ap.add_argument("--state-code", help="two-letter code written into state_code, e.g. FL")
    ap.add_argument("--out", default=os.path.join(ROOT, "input", "listings-raw.csv"))
    ap.add_argument("--estimate", action="store_true", help="three requests, about five cents: row count and projected cost, primary-category count, website share, and a VERTICAL FLAG when the vertical is clearly a bad fit; no pull")
    ap.add_argument("--max-rows", type=int, default=0, help="stop after this many rows (tests)")
    ap.add_argument("--min-reviews", type=int, default=1, help="server-side filter; 0 pulls everything")
    ap.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    a = ap.parse_args()
    auth = load_credentials()

    if a.find_category:
        req = urllib.request.Request(CATEGORIES_API, headers={"Authorization": auth})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sys.exit(REJECTED)
            raise
        result = (data.get("tasks") or [{}])[0].get("result") or []
        # the endpoint returns the categories as the result list itself (free, GET)
        # the endpoint returns [{category_name, business_count}, ...]; category_name is the id to pass as --category
        items = result if (result and "category_name" in result[0]) else ((result[0] if result else {}) or {}).get("items") or []
        word = a.find_category.lower().replace(" ", "_")
        hits = sorted([it for it in items if word in (it.get("category_name") or "").lower()],
                      key=lambda it: -(it.get("business_count") or 0))
        print(f"Category ids containing '{a.find_category}' ({len(hits)}), with businesses worldwide; pass one or more as --category:")
        for it in hits:
            print(f"  {it.get('category_name'):45s} {it.get('business_count') or 0:>12,}")
        return

    if not (a.category and a.state and a.state_code):
        sys.exit("--category, --state and --state-code are required for an estimate or a pull.")
    if len(a.category) > 10:
        sys.exit("At most 10 categories per pull.")
    probe = dict(base_task(a), limit=30 if a.estimate else 1)   # the estimate reads the primary labels from these rows
    res, cost = post(auth, probe)
    total = int(res.get("total_count") or 0)
    target = min(total, a.max_rows) if a.max_rows else total
    requests_needed = max(1, math.ceil(target / PAGE))
    projected = requests_needed * PRICE_REQUEST + target * PRICE_ITEM
    print(f"Categories: {', '.join(a.category)} | State: {a.state}")
    print(f"Rows in the DataForSEO database matching (reviews >= {a.min_reviews}): {total:,}")
    print(f"Rows to pull: {target:,} in {requests_needed} request(s); projected cost about ${projected:.2f} "
          f"(published rates; the account is billed the real figure). Probe cost: ${cost:.4f}")
    if a.estimate:
        if total == 0:
            print("VERTICAL FLAG: " + vertical_flags(0, 0, 0, a)[0])
            return
        primary, sites, hcost = health(auth, a, res.get("items") or [])
        ptext = (f"{primary:,} of {total:,} ({primary / total:.0%}) carry it as their primary one" if primary is not None
                 else "not measured (no sampled row carries it as the primary one)")
        print(f"Primary category: {ptext}. With a website: {sites:,} ({sites / total:.0%}). Check cost: ${hcost:.4f}")
        flags = vertical_flags(total, primary, sites, a)
        for fl in flags:
            print("VERTICAL FLAG: " + fl)
        if not flags:
            print("Vertical flags: none.")
        return
    if total == 0:
        sys.exit("Nothing to pull. Check the category id (see the DataForSEO categories list) and the state spelling.")
    if not a.yes:
        try:
            ans = input("Pull now? Type yes to continue: ").strip().lower()
        except EOFError:
            sys.exit("No terminal to confirm in. After the member's yes, run the same command with --yes.")
        if ans != "yes":
            print("Stopped before pulling."); return

    rows, spent, offset, token, seen = [], cost, 0, None, set()
    while len(rows) < target:
        task = dict(base_task(a), limit=min(PAGE, target - len(rows)))
        if token:
            task["offset_token"] = token
        else:
            task["offset"] = offset
        res, c = post(auth, task); spent += c
        items = res.get("items") or []
        if not items:
            break
        for it in items:
            key = it.get("cid") or it.get("place_id") or (it.get("title"), it.get("address"))
            if key in seen:
                continue
            seen.add(key); rows.append(to_row(it, a.state_code))
        token = res.get("offset_token")
        offset += len(items)
        print(f"  fetched {len(rows):,} / {target:,}", file=sys.stderr)
        if len(items) < task["limit"]:
            break

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS); w.writeheader(); w.writerows(rows)

    with_email = sum(1 for r in rows if r["email_1"])
    off_state = sum(1 for r in rows if r["state"].lower() != a.state.lower())
    primary = sum(1 for r in rows if r["type"].lower().replace(" ", "_") in [c.lower() for c in a.category])
    ages = [r["last_updated_time"][:10] for r in rows if r["last_updated_time"]]
    report = [
        "# Fetch report (DataForSEO Business Listings)", "",
        f"- Pulled: {time.strftime('%Y-%m-%d %H:%M %Z (UTC%z)')} (local time)",
        f"- Categories: {', '.join(a.category)}; state filter: {a.state}; min reviews: {a.min_reviews}",
        f"- Rows in database: {total:,}; rows written: {len(rows):,} to `{os.path.relpath(a.out, ROOT)}`",
        f"- Cost reported by DataForSEO for this run: ${spent:.4f}",
        f"- Rows whose primary category is one you asked for: {primary:,} (the rest carry it as a secondary category; Gate 2 keeps them and lists them by primary type in 02-clean-report.md, and the member decides at Gate 4)",
        f"- Rows with at least one email: {with_email:,} (own-domain address first; check the domain and bounce-test before outreach)",
        f"- Rows outside {a.state} after the filter: {off_state:,}",
        f"- last_updated_time range: {min(ages) if ages else 'n/a'} to {max(ages) if ages else 'n/a'} (database freshness, not a live scrape)",
        "", "Next: `python3 scripts/clean_listings.py input/listings-raw.csv --niche \"<terms>\" --state "
        f"{a.state_code} --category \"<Maps category label>\" --out output/<slug>/02-listings-clean.csv`",
    ]
    rep_path = os.path.join(os.path.dirname(a.out) or ".", "listings-raw-report.md")
    with open(rep_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
