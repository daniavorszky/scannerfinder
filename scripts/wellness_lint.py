#!/usr/bin/env python3
"""Wellness check for the Gate 3 descriptions (ScannerFinder), run after the kit's merge_enriched.py.

Usage: python3 scripts/wellness_lint.py <answers.json | region-copy.json> [...]
Rules: apps/directory-blueprint/output/scannerfinder/03-wellness-rules.md
Checks each description (with the business name removed): banned medical words, prices.
Exit 1 if anything fails.
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLEAN = os.path.join(os.path.dirname(HERE), "apps", "directory-blueprint", "output", os.environ.get("SF_SLUG") or "scannerfinder", "02-listings-clean.csv")
BANNED = re.compile(
    r"\b(diagnos\w*|detect\w*|treat|treats|treating|treatments?|cures?|cured|curing|heal|heals|healing|"
    r"diseases?|illness\w*|disorders?|symptoms?|patients?|medical(ly)?|clinical(ly)?|allerg\w*|intoleran\w*|"
    r"cancer|lyme|pain|parasit\w*|toxins?|infections?|deficienc\w*|prescri\w*|remed(y|ies)|test results|root causes?|"
    # German/Romanian leftovers from DE + RO source text (2026-10-12)
    r"diagnose|therapien?\b|heilung|krankheit\w*|allergie\w*|unverträglich\w*|entgiftung|ausleitung|schmerz\w*|"
    r"tratament\w*|vindec\w*|boal[aăe]\w*|diagnostic\w*|depistare|alergi\w*|intoleran[țt]\w*|detoxifiere)\b", re.I)
# Narrating what is unknown is banned by the kit (enrichment-instructions.md), but merge_enriched.py doesn't catch every form.
UNKNOWN = re.compile(r"\bno (website|reviews?|opening hours|hours|service details|details)\b|\bcannot be confirmed\b|\bcould not be confirmed\b|"
                     r"\bhave not been published\b|\bhas not been published\b|\bnot (been )?published\b|\bunknown\b|\bunclear\b", re.I)
BLOOD = re.compile(r"\bblood\b", re.I)
PRICE = re.compile(r"[$£€]\s?\d|\d\s?€|\b\d+\s?(usd|gbp|eur|euro|zar|aud|cad|nzd|rand|lei|ron)\b|\bR\s?\d{2,}|\baffordabl\w*|\bper session\b", re.I)


def main(paths):
    names, all_names = {}, []
    if os.path.exists(CLEAN):
        with open(CLEAN, newline="", encoding="utf-8") as f:
            names = {r["slug"]: r["name"] for r in csv.DictReader(f)}
    all_names = sorted(set(names.values()), key=len, reverse=True)
    fails = 0
    for p in paths:
        data = json.load(open(p, encoding="utf-8"))
        if isinstance(data, dict):   # region copy (city-copy format): {slug: {intro: [...], faqs: [{q, a}]}}
            data = [{"slug": k, "description": " ".join(v.get("intro", []) + [f.get("q", "") + " " + f.get("a", "") for f in v.get("faqs", [])]), "_names": True}
                    for k, v in data.items() if not k.startswith("_")]
        for x in data:
            d = x.get("description") or ""
            for name in (all_names if x.get("_names") else [names.get(x.get("slug"), "")]):
                if name and len(name) > 3:
                    d = re.sub(re.escape(name), " ", d, flags=re.I)
            probs = [f"word '{m.group(0)}'" for m in BANNED.finditer(d)] + [f"price '{m.group(0)}'" for m in PRICE.finditer(d)] \
                + [f"unknown narrated '{m.group(0)}'" for m in UNKNOWN.finditer(d)] + [f"medical service '{m.group(0)}'" for m in BLOOD.finditer(d)]
            if probs:
                fails += 1
                print(f"FAIL {x.get('slug')}: " + ", ".join(dict.fromkeys(probs)))
    print(f"wellness lint: {fails} listing(s) failing")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
