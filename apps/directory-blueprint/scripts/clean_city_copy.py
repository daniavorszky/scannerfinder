#!/usr/bin/env python3
"""Gate 5 helper: replace wording about how the directory was built with plain wording,
in the city copy cache. Mechanical and narrow: whole clauses with a fixed shape only.
Anything it cannot handle is left for a rewrite and still fails check_city_copy.py.

Usage:
  python3 scripts/clean_city_copy.py output/<slug>/05-cache/city-copy [--write]
Without --write it prints what it would change.
"""
import argparse, glob, json, os, re

RULES = [
    # "held out of search": drop the clause or the sentence
    (r",? and \d+ (?:are|is) held out of search until they have more reviews or detail", ""),
    (r",? and none is held out of search", ""),
    (r"(?:^|(?<=[.!?] ))[^.!?]*held out of search[^.!?]*[.!?] ?", ""),
    # "no answer on any attribute"
    (r"\b(have|has|give|gives|gave) no answers? (?:yet )?on any attribute(?: yet)?", r"\1 no details on record"),
    (r"\bno answers? on any attribute", "no details on record"),
    (r"\bwith no answers? on any attribute", "with no details on record"),
    (r"\bconfirmed attributes\b", "confirmed details"),
    (r"\bso few attributes can be reported\b", "so little can be reported"),
    # website errors
    (r"\b(?:website|site)(?: link)? (?:returned|gave) an? (?:not[- ]found|access|server) error(?: when the data was collected)?", "website could not be read"),
    (r"\bhas a link that returned a not[- ]found error", "has a website that could not be read"),
    (r"\bhas a site that returned an access error", "has a website that could not be read"),
    (r"\bwebsite refused the request to read it", "website could not be read"),
    (r"\bwebsite could not be loaded securely", "website could not be read"),
    (r"\b(?:website|site|page)(?: itself)? loaded empty", "website could not be read"),
    (r"\bthe site returned an error", "the website could not be read"),
    (r"\bwebsite could not be read, so its services could not be read", "website could not be read"),
]


def clean(text):
    out = text
    for rx, rep in RULES:
        out = re.sub(rx, rep, out, flags=re.I)
    out = re.sub(r"  +", " ", out).strip()
    if out and out != text and out[0].islower(): out = out[0].upper() + out[1:]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--write", action="store_true"); ap.add_argument("--only", default="")
    a = ap.parse_args()
    n = 0
    for p in sorted(glob.glob(os.path.join(a.folder, "*.json"))):
        if a.only and os.path.basename(p)[:-5] not in a.only.split(","): continue
        d = json.load(open(p, encoding="utf-8")); ch = False
        for slug, c in d.items():
            for i, para in enumerate(c["intro"]):
                new = clean(para)
                if new != para: n += 1; ch = True; c["intro"][i] = new
                if not a.write and new != para: print(f"{slug}: {len(para.split())} -> {len(new.split())} words")
            c["intro"] = [x for x in c["intro"] if x.strip()]
            for f in c["faqs"]:
                for k in ("q", "a"):
                    new = clean(f[k])
                    if new != f[k]: n += 1; ch = True; f[k] = new
        if ch and a.write: json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"blocks changed: {n}")


if __name__ == "__main__":
    main()
