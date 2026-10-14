#!/usr/bin/env python3
"""Gate 1, on request only: check one vertical in one state against the Step 1 criteria.

  python3 scripts/check_vertical.py --category fence_contractor --state Colorado

Run it when the member asks for a check, or has no vertical yet and names one to three candidates
(wiki/framework/gate-1-intake.md, "The vertical check"). Never run it on a member who arrived with a
vertical and did not ask: the estimate after question 2 already raises a flag when a vertical is
clearly a bad fit, and a scorecard nobody asked for only invites second-guessing.

What it measures (about five cents on the member's DataForSEO account; --quote prints the figure
without spending anything):
  1. the category exists as a Maps category (free)
  2. size: reviewed businesses of that category in the state, against the 200 to 5,000 band
  3. the category says the trade: the share that carries it as the primary category
  4. websites: the share with a website, which is what the enrichment reads

It does not look at search results, volumes or difficulty. Low volume is fine for a directory, a
page one cannot be judged by a script, and every extra number is one more reason for a member to
keep researching instead of building (Shawn, 2026-10-01). The state search stays a look the member
takes in Step 1 of the course.

What it cannot measure, and leaves to the member as three yes or no questions: people compare
before they buy, the ticket is four figures with no favorite company, and there is a real "how to
choose" to write. The bands are the working rules from the Step 1 lesson and the first two builds
(Florida pool builders, Colorado fence contractors), not measured thresholds.

The output is one short card. It ends with one line: the measured checks pass, or which one fails.
"""
import argparse, json, os, sys, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_dataforseo as f   # noqa: E402

SIZE_MIN, SIZE_MAX = 200, 5000
PRIMARY_CLEAN, PRIMARY_MIN = 0.70, 0.50
SITES_MIN = 0.50
QUOTE = 3 * f.PRICE_REQUEST + 30 * f.PRICE_ITEM


def category_exists(auth, cat):
    req = urllib.request.Request(f.CATEGORIES_API, headers={"Authorization": auth})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f.REJECTED if e.code == 401 else f"DataForSEO answered {e.code} on the category list.")
    result = (data.get("tasks") or [{}])[0].get("result") or []
    items = result if (result and "category_name" in result[0]) else ((result[0] if result else {}).get("items") or [])
    names = {(it.get("category_name") or "").lower() for it in items}
    words = [w for w in cat.lower().split("_") if len(w) > 3]
    near = [it.get("category_name") for it in sorted(items, key=lambda it: -(it.get("business_count") or 0))
            if any(w in (it.get("category_name") or "").lower() for w in words)][:6]
    return cat.lower() in names, near


def main():
    ap = argparse.ArgumentParser(description="Check one vertical in one state against the Step 1 criteria. On request only.")
    ap.add_argument("--category", help="DataForSEO category id, e.g. fence_contractor (--find-category on fetch_dataforseo.py lists them)")
    ap.add_argument("--state", help='state name, e.g. "Colorado"')
    ap.add_argument("--service", help=argparse.SUPPRESS)   # accepted and ignored; an earlier version searched with it
    ap.add_argument("--min-reviews", type=int, default=1)
    ap.add_argument("--quote", action="store_true", help="print what the check costs and exit; nothing is spent")
    a = ap.parse_args()
    if a.quote:
        print(f"A vertical check is 3 requests, about ${QUOTE:.2f} on the DataForSEO account (the category lookup is free).")
        return
    if not (a.category and a.state):
        sys.exit("--category and --state are required.")
    a.category = [a.category]
    label = a.category[0].replace("_", " ").capitalize()
    auth = f.load_credentials()

    exists, near = category_exists(auth, a.category[0])
    print(f"Vertical check: {label} in {a.state}")
    if not exists:
        print(f"1. Maps category: NO. '{a.category[0]}' is not a category id." + (f" Close ones: {', '.join(near)}." if near else ""))
        print("Result: not checkable until the service is an exact Maps category. Cost: $0.00")
        return
    print("1. Maps category: yes.")

    res, cost = f.post(auth, dict(f.base_task(a), limit=30))
    total = int(res.get("total_count") or 0)
    if total == 0:
        print(f"2. Size: 0 reviewed businesses in {a.state}. FAIL (check the state spelling).")
        print(f"Result: fails on size. Cost: ${cost:.2f}")
        return
    primary, sites, hcost = f.health(auth, a, res.get("items") or []); cost += hcost

    fails, notes = [], []
    if total < SIZE_MIN:
        size = f"FAIL, under {SIZE_MIN}: few cities clear the three-business floor"; fails.append("size")
    elif total > SIZE_MAX:
        size = f"pass, and large (over {SIZE_MAX:,}): the enrichment is a long run for a first directory"; notes.append("large")
    else:
        size = f"pass (band {SIZE_MIN} to {SIZE_MAX:,})"
    print(f"2. Size: {total:,} reviewed businesses. {size}.")

    share = (primary / total) if primary is not None else None
    if share is None:
        trade = "not measured"; notes.append("primary share not measured")
        print("3. Category says the trade: not measured (no sampled business carries it as the primary category). Look at the Gate 2 report.")
    elif share >= PRIMARY_CLEAN:
        trade = "pass, the category is this trade"
    elif share >= PRIMARY_MIN:
        trade = "pass, with other trades to sort out at Gate 4"; notes.append("sorting")
    else:
        trade = "FAIL, most rows are other trades that carry it as a second category"; fails.append("category too broad")
    if share is not None:
        print(f"3. Category says the trade: {share:.0%} carry it as their primary category. {trade}.")

    wshare = sites / total
    if wshare >= SITES_MIN:
        web = "pass"
    else:
        web = "FAIL, the listings would be a name and a phone number"; fails.append("websites")
    print(f"4. Websites: {wshare:.0%} have one. {web}.")

    print("Yours to answer, yes or no: people get more than one quote for this job; the job runs four figures and nobody has a favorite company; there is something real to explain about choosing one (license, permit, materials, warranty).")
    if fails:
        print(f"Result: FAILS on {', '.join(fails)}. By the Step 1 checks this is a weak directory vertical in {a.state}; the member can still choose to build it. Cost: ${cost:.2f}")
    else:
        print(f"Result: the measured checks pass{' (' + ', '.join(notes) + ')' if notes else ''}. If your three answers are yes, build it. Cost: ${cost:.2f}")


if __name__ == "__main__":
    main()
