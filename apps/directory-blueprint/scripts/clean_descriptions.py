#!/usr/bin/env python3
"""Gate 3 helper: take wording about how the directory was built out of the listing descriptions
in the enrichment cache. Mechanical and narrow. What it cannot handle still fails merge_enriched.py.

Found on the pilot: the enrichment instructions called a listing's evidence "the packet", and a
third of the descriptions repeated the word to the reader.

Usage:
  python3 scripts/clean_descriptions.py output/<slug>/03-cache/enriched [--write]
"""
import argparse, glob, json, os, re

READ = "could not be read"
RULES = [
    (r"\b(website|site|page|link|address)( on (?:the|its) (?:listing|record))? (?:returned|gave|showed|shows|returns|gives) (?:an? )?(?:http )?(?:\d{3} |not[- ]found |access |server |permission |forbidden )?(?:error|not[- ]found page)(?: page)?(?: when (?:it was )?checked)?", r"\1\2 " + READ),
    (r"\b(website|site|page) (?:timed out|refused (?:the )?(?:connection|request)[^,.;]*|blocked access|could not be (?:reached|loaded|opened)|did not load|would not load|failed to load|was unreachable|loaded empty|loaded blank|loaded (?:as )?an empty page)(?: when (?:it was )?checked)?", r"\1 " + READ),
    (r"\bcould not be read when (?:it was )?checked", READ),
    (r"\bwhen (?:it was )?checked\b", ""),
    (r"\bthe packet's\b", "the record's"), (r"\bThe packet's\b", "The record's"),
    (r"\bthe packet\b", "the record"), (r"\bThe packet\b", "The record"),
    (r"\bits packet\b", "its record"), (r"\bpackets?\b", "record"),
    (r"\battributes\b", "details"), (r"\battribute\b", "detail"),
]


def clean(text):
    out = text
    for rx, rep in RULES:
        out = re.sub(rx, rep, out, flags=re.I if rx.startswith(r"\b(website") or "checked" in rx else 0)
    out = re.sub(r"\s+([,.;])", r"\1", out)
    return re.sub(r"  +", " ", out).strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    n = 0
    for p in sorted(glob.glob(os.path.join(a.folder, "*.json"))):
        d = json.load(open(p, encoding="utf-8")); ch = False
        for x in d:
            new = clean(x["description"])
            if new != x["description"]: n += 1; ch = True; x["description"] = new
        if ch and a.write: json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"descriptions changed: {n}")


if __name__ == "__main__":
    main()
