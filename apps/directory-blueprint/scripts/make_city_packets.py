#!/usr/bin/env python3
"""Gate 5 helper: turn the city structure (05-cities.json, written by the site's dump-cities.mjs)
into readable packets, batched for the city copy run.

Every number a writer may use is printed in the packet, because check_city_copy.py rejects
any number in the copy that is not in the packet or on the fact sheet.

Usage:
  python3 scripts/make_city_packets.py output/<slug>/05-cities.json --attributes output/<slug>/03-attributes.json \
      --out output/<slug>/05-cache/city-batches --done output/<slug>/05-cache/city-copy \
      --niche "<niche plural>" --state "<State>" [--words-per-batch 4800] [--city-facts output/<slug>/05-city-facts.json]

Every batch opens with a `directory:` line naming the vertical and the state, so
scripts/city-copy-instructions.md stays general. Under-floor towns that keep a page of their own
(foldMaxKm) are included with a shorter band; they are indexed like any city page. The packet is
place-first (page-types, 2026-09-30): it prints what the local trade leans toward, the places the
listings' own sites name as where they work, and an optional city-facts block; it prints no counts
of unknowns, because the copy says nothing about what is unknown.
"""
import argparse, glob, json, os, re, textwrap
from collections import Counter


def band(n):
    # Word floors by page size (wiki/framework/page-types.md). Under 3 listings is a town page kept by foldMaxKm.
    return (120, 800) if n < 3 else (250, 800) if n < 5 else (380, 800) if n < 10 else (500, 800)


def first_sentences(text, k=3, cap=420):
    s = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    return " ".join(s[:k])[:cap]


def places_named(c, place_names):
    """Towns and counties the listings' own descriptions name, other than the city itself: the
    service-area geography the place-first copy is written from."""
    text = " ".join(l.get("description") or "" for l in c["listings"])
    found = Counter()
    for m in re.finditer(r"\b([A-Z][a-zA-Z.'-]+(?: [A-Z][a-zA-Z.'-]+){0,3}) Count(?:y|ies)\b", text):
        found[m.group(1) + " County"] += 1
    for name in place_names:
        if name == c["name"]: continue
        n = len(re.findall(r"(?<![A-Za-z])" + re.escape(name) + r"(?![A-Za-z])", text))
        if n: found[name] += n
    return found


def render(c, labels, place_names, facts):
    lo, hi = band(c["count"])
    L = [f"### {c['slug']}", f"city: {c['name']}", f"listings on this page: {c['count']}", f"intro band: {lo} to {hi} words"]
    if c.get("underFloor"): L.append("page type: small town with its own page (too far from a larger city to share one); 2 to 4 paragraphs, 2 to 6 FAQs")
    if facts.get(c["slug"]):
        L.append("city facts (each with its source; use what is here, add nothing):")
        L += [f"  - {x}" for x in facts[c["slug"]]]
    counties = Counter(l["county"] for l in c["listings"] if l["county"])
    L.append("counties of the listings (from ZIP codes): " + ", ".join(f"{k} {v}" for k, v in counties.most_common()))
    towns = Counter(l["basedIn"] for l in c["listings"] if l["basedIn"] and l["basedIn"] != c["name"])
    if towns:
        L += textwrap.wrap("smaller towns whose listings sit on this page: " + ", ".join(f"{k} {v}" for k, v in towns.most_common()), 300, subsequent_indent="  ")
    L.append(f"total Google reviews across the listings: {c['totalReviews']}; average rating: {c['avgRating']:.1f}")
    L.append("what the local trade leans toward (listings confirming each on their own site): " + ", ".join(f"{labels[k]} {v}" for k, v in c["attrCounts"].items() if v and k in labels))
    pl = places_named(c, place_names)
    if pl:
        L += textwrap.wrap("places the listings' own websites name as where they work (mentions): " + ", ".join(f"{k} {v}" for k, v in pl.most_common(20)), 300, subsequent_indent="  ")
    L.append("nearby city pages: " + ", ".join(f"{n['name']} {n['count']}" for n in c["nearby"]))
    L.append("listings, in the order the page shows them:")
    for l in c["listings"]:
        head = f"  {l['position']}. {l['name']} | {l['rating']:.1f} from {l['reviews']} reviews"
        if l["basedIn"] and l["basedIn"] != c["name"]: head += f" | based in {l['basedIn']}"
        if l["county"]: head += f" | {l['county']}"
        L.append(head)
        L += textwrap.wrap("     yes: " + (", ".join(labels[k] for k in l["yes"]) or "none stated") + (" | no: " + ", ".join(labels[k] for k in l["no"]) if l["no"] else ""), 300, subsequent_indent="       ")
        if l["position"] <= 20 and l.get("description"):
            L += textwrap.wrap("     note: " + first_sentences(l["description"]), 300, subsequent_indent="       ")
    return L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cities"); ap.add_argument("--attributes", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--done", required=True); ap.add_argument("--words-per-batch", type=int, default=4800); ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--niche", required=True, help='the niche phrase the first paragraph must carry, e.g. "pool builders"')
    ap.add_argument("--state", default="", help="the state's name, printed on the directory line")
    ap.add_argument("--city-facts", default="", help="optional JSON {city-slug: [\"fact (source)\", ...]} rendered as a city facts block")
    a = ap.parse_args()
    facts = json.load(open(a.city_facts, encoding="utf-8")) if a.city_facts else {}
    labels = {x["key"]: x["label"] for x in json.load(open(a.attributes, encoding="utf-8")) if not x["key"].startswith("_")}
    cities = json.load(open(a.cities, encoding="utf-8"))   # every page that renders, small-town pages included
    place_names = sorted({c["name"] for c in cities} | {l["basedIn"] for c in cities for l in c["listings"] if l.get("basedIn")}, key=len, reverse=True)
    header = f"directory: {a.niche}" + (f" in {a.state}" if a.state else "")
    done = set()
    for p in glob.glob(os.path.join(a.done, "*.json")):
        try: done |= set(json.load(open(p, encoding="utf-8")).keys())
        except Exception: pass
    todo = [c for c in cities if c["slug"] not in done]
    batches, cur, w = [], [], 0
    for c in todo:
        target = {120: 160, 250: 320, 380: 460, 500: 620}[band(c["count"])[0]] + 330
        if cur and w + target > a.words_per_batch: batches.append(cur); cur, w = [], 0
        cur.append(c); w += target
    if cur: batches.append(cur)
    os.makedirs(a.out, exist_ok=True)
    for p in glob.glob(os.path.join(a.out, "batch-*")):
        if int(os.path.basename(p)[6:8]) >= a.start: os.remove(p)
    for i, b in enumerate(batches, a.start):
        name = f"batch-{i:02d}"
        with open(os.path.join(a.out, name + ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {name}: {len(b)} cities\n{header}\n\n" + "\n\n".join("\n".join(render(c, labels, place_names, facts)) for c in b) + "\n")
        json.dump([c["slug"] for c in b], open(os.path.join(a.out, name + ".slugs.json"), "w"))
    towns = sum(1 for c in cities if c.get("underFloor"))
    print(f"pages: {len(cities)} ({towns} small-town pages), already written: {len(cities) - len(todo)}, to do: {len(todo)} in {len(batches)} batches")
    print("cities per batch:", [len(b) for b in batches])


if __name__ == "__main__":
    main()
