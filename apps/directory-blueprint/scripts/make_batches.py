#!/usr/bin/env python3
"""Gate 3 helper: cut the evidence packets into batches an enrichment run can read in one go.

Groups listings by city, keeps a city together where it fits, and skips every listing that
already has an answer in the enriched cache, so a rerun only batches what is new or missing.
Each batch is a plain text file (short lines, readable top to bottom) plus the list of slugs.

Usage:
  python3 scripts/make_batches.py --evidence output/<slug>/03-cache/evidence \
      --enriched output/<slug>/03-cache/enriched --out output/<slug>/03-cache/batches \
      --attributes output/<slug>/03-attributes.json [--max-tokens 26000] [--max-listings 40] [--start 11]

Every batch file opens with the attribute table from the per-vertical file (key, what a true needs),
so scripts/enrichment-instructions.md stays general and the vertical's own rules travel with the batch.
"""
import argparse, glob, json, os, shutil, textwrap


def render(pk):
    L = [f"### {pk['slug']}", f"name: {pk['name']}", f"city: {pk['city']}",
         f"maps_type: {pk['maps_type']}", f"maps_subtypes: {pk['maps_subtypes']}"]
    stars = [str(int(float(x))) if str(x).strip() not in ("", "None") else "0" for x in pk["stars_1_to_5"]]
    L.append(f"rating: {pk['rating']} from {int(float(pk['reviews']))} reviews (1 star: {stars[0]}, 2: {stars[1]}, 3: {stars[2]}, 4: {stars[3]}, 5 star: {stars[4]})")
    L.append(f"hours_posted: {'yes' if pk['has_hours'] else 'no'}")
    if pk.get("maps_about"): L.append("maps_about: " + "; ".join(pk["maps_about"]))
    if pk.get("maps_description"): L.append("maps_description: " + pk["maps_description"])
    L.append(f"site_status: {pk['site_status']}")
    for k in ("site_title", "site_meta"):
        if pk.get(k): L.append(f"{k}: {pk[k]}")
    for k in ("site_headings", "site_menu"):
        if pk.get(k): L += textwrap.wrap(f"{k}: " + " | ".join(pk[k]), 300, subsequent_indent="  ")
    if pk.get("quotes"):
        L.append(f"description band: {'80' if len(pk['quotes']) <= 2 else '120'} to 200 words")
        L.append("quotes (the patterns that found them are loose; read what the sentence says):")
        for k, qs in pk["quotes"].items():
            for q in qs: L += textwrap.wrap(f"  [{k}] {q}", 300, subsequent_indent="      ")
    else:
        L.append("description band: 50 to 90 words")
        L.append("quotes: none")
    return L


def attribute_table(attrs):
    L = ["## Attributes for this directory (answer every key, in this order)", ""]
    L.append("| Key | True when the business's own words say it |")
    L.append("|---|---|")
    for x in attrs:
        if x["key"].startswith("_"): continue
        tw = x.get("true_when") or x.get("label", "")
        if x.get("core"): tw += " (core work: when this is false, the description says plainly what the business does instead)"
        L.append(f"| `{x['key']}` | {tw} |")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True); ap.add_argument("--enriched", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--attributes", required=True, help="the per-vertical attribute file (03-attributes.json); its table is printed at the top of every batch")
    ap.add_argument("--max-tokens", type=int, default=26000); ap.add_argument("--max-listings", type=int, default=40)
    ap.add_argument("--start", type=int, default=1, help="number of the first batch, so new batches do not reuse a number already answered")
    a = ap.parse_args()
    attrs = json.load(open(a.attributes, encoding="utf-8"))
    if not isinstance(attrs, list) or not attrs or "key" not in attrs[0]:
        raise SystemExit(f"ERROR: {a.attributes} is not a list of attributes (see scripts/examples/attributes-pool-builders.json)")
    if not all(x.get("true_when") for x in attrs if not x["key"].startswith("_")):
        print(f"note: some attributes in {a.attributes} have no true_when line; the label is printed instead. Add one per attribute so writers know what a true needs.")
    table = attribute_table(attrs)
    done = set()
    for p in glob.glob(os.path.join(a.enriched, "*.json")):
        try: done |= {x["slug"] for x in json.load(open(p, encoding="utf-8"))}
        except Exception: pass
    cities = []
    for p in glob.glob(os.path.join(a.evidence, "*.json")):
        pks = [pk for pk in json.load(open(p, encoding="utf-8")) if pk["slug"] not in done]
        if pks: cities.append(pks)
    cities.sort(key=lambda c: (-len(c), c[0]["city"]))
    batches, cur, tok = [], [], 0
    for pks in cities:
        for pk in pks:
            lines = render(pk); t = sum(len(x) for x in lines) // 4 + 20
            if cur and (tok + t > a.max_tokens or len(cur) >= a.max_listings):
                batches.append(cur); cur, tok = [], 0
            cur.append((pk["slug"], lines)); tok += t
    if cur: batches.append(cur)
    os.makedirs(a.out, exist_ok=True)
    for p in glob.glob(os.path.join(a.out, "batch-*")):
        if int(os.path.basename(p)[6:9]) >= a.start: os.remove(p)
    for i, b in enumerate(batches, a.start):
        name = f"batch-{i:03d}"
        with open(os.path.join(a.out, name + ".md"), "w", encoding="utf-8") as f:
            f.write(f"# {name}: {len(b)} listings\n\n{table}\n\n## Listings\n\n" + "\n\n".join("\n".join(l) for _, l in b) + "\n")
        with open(os.path.join(a.out, name + ".slugs.json"), "w", encoding="utf-8") as f:
            json.dump([s for s, _ in b], f)
    n = sum(len(b) for b in batches)
    print(f"already answered: {len(done)}, to do: {n} listings in {len(batches)} batches")
    print("listings per batch:", [len(b) for b in batches])


if __name__ == "__main__":
    main()
