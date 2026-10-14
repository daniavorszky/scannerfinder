#!/usr/bin/env python3
"""
extract_claims.py — find candidate factual claims in a draft.

A script can reliably FIND claims (numbers, percentages, prices, ratings, dates);
it cannot judge whether they are TRUE. Verification is Claude's job in Stage 7,
using a web search against credible sources. This tool just surfaces the
candidates with enough surrounding context to check each one.

Standard library only — no install needed.

Usage:
    python scripts/extract_claims.py <article.md>
    python scripts/extract_claims.py <article.md> --json
"""

import argparse
import json
import os
import re
import sys

# Each pattern targets one kind of checkable claim. Named so the report tells the
# reviewer what sort of fact they're looking at.
PATTERNS = {
    "percentage": r"\b\d{1,3}(?:\.\d+)?\s?%",
    "price": r"[$£€]\s?\d[\d,]*(?:\.\d{1,2})?(?:\s?(?:/|per)\s?\w+)?",
    "rating": r"\b\d(?:\.\d)?\s?(?:/\s?5|out of\s?(?:5|10)|stars?)\b",
    "large_number": r"\b\d{1,3}(?:,\d{3})+\b|\b\d{4,}\b",
    "multiplier": r"\b\d+(?:\.\d+)?x\b",
    "year_or_date": r"\b(?:19|20)\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b",
}

# Superlatives are worth flagging even without a number: "the fastest", "the most
# affordable" are claims that need backing too.
SUPERLATIVE = r"\b(?:the\s+)?(?:most|least|best|worst|fastest|slowest|cheapest|largest|smallest|highest|lowest|leading|number one|#1)\b"


def strip_for_context(text):
    """Light cleanup so sentence context reads well, keeping the numbers intact."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    return text


def split_sentences(text):
    # Keep it simple; over-splitting is fine for review context.
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def find_claims(raw):
    text = strip_for_context(raw)
    sentences = split_sentences(text)
    claims = []
    for i, sentence in enumerate(sentences, 1):
        matched = {}
        for label, pat in PATTERNS.items():
            found = re.findall(pat, sentence, flags=re.IGNORECASE)
            if found:
                matched[label] = found
        supers = re.findall(SUPERLATIVE, sentence, flags=re.IGNORECASE)
        if supers:
            matched["superlative"] = supers
        if matched:
            claims.append({
                "sentence_no": i,
                "sentence": sentence,
                "matches": matched,
            })
    return claims


def main():
    ap = argparse.ArgumentParser(description="Extract candidate factual claims for verification.")
    ap.add_argument("file", help="path to the article markdown file")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: file not found: {args.file}")
        sys.exit(1)

    with open(args.file, encoding="utf-8") as f:
        raw = f.read()

    claims = find_claims(raw)

    if args.json:
        print(json.dumps({"count": len(claims), "claims": claims}, indent=2))
        return

    print("=" * 60)
    print(f"CLAIM CANDIDATES — {os.path.basename(args.file)}")
    print("=" * 60)
    if not claims:
        print("No numeric or superlative claims detected.")
        print("(Still sanity-check any qualitative factual statements yourself.)")
        return
    print(f"Found {len(claims)} sentence(s) with checkable claims.")
    print("Verify each against a CREDIBLE source (official page, research, .gov,")
    print("established news). Soften anything you can't verify.\n")
    for c in claims:
        kinds = ", ".join(c["matches"].keys())
        print(f"[{c['sentence_no']}] ({kinds})")
        print(f"    {c['sentence']}")
        print()


if __name__ == "__main__":
    main()
