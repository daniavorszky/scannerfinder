#!/usr/bin/env python3
"""
lint_article.py — countable quality checks for the SEO Content Engine.

Handles the checks that need to be exact rather than judged: forbidden
words/phrases, keyword positioning, and word count, plus a reported readability
signal (not gated). It is
deliberately self-contained (standard library only) so it runs anywhere with
Python 3 and needs no pip install.

Usage:
    python scripts/lint_article.py <article.md> --keyword "primary keyword"
    python scripts/lint_article.py <article.md> --keyword "kw" --min-words 1500 --max-words 2200
    python scripts/lint_article.py <article.md> --keyword "kw" --json

Exit code is 0 when every gate passes, 1 when any gate fails — so it can be
used in a run-fix-rerun loop.
"""

import argparse
import json
import os
import re
import sys

# The forbidden list is NOT defined here on purpose. It lives in
# references/forbidden_words.txt so the writer and this linter read the same
# source and can never drift apart.
FORBIDDEN_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "references", "forbidden_words.txt",
)

# Readability is REPORTED, not gated. There is no universal "correct" grade for a
# blog post, and the right level depends on the audience set in Stage 1, so the
# script surfaces the score for judgement rather than failing the run on it.

# The primary keyword must sit inside the opening of the intro. 200 characters is
# roughly the first sentence or two — early enough to signal relevance.
INTRO_CHAR_WINDOW = 200


def load_forbidden(path):
    """Load words and phrases from the canonical txt file.

    Falls back to an empty list with a warning rather than crashing, so a
    missing file degrades gracefully instead of blocking the whole run.
    """
    words, phrases = [], []
    if not os.path.exists(path):
        print(f"WARNING: forbidden list not found at {path} — skipping that check.")
        return words, phrases
    section = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.upper() == "[WORDS]":
                section = "words"
                continue
            if line.upper() == "[PHRASES]":
                section = "phrases"
                continue
            if section == "words":
                words.append(line.lower())
            elif section == "phrases":
                phrases.append(line.lower())
    return words, phrases


def strip_markdown(text):
    """Reduce markdown to plain prose for readability and word-count math."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)   # code fences
    text = re.sub(r"`[^`]*`", " ", text)                       # inline code
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)          # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)       # links -> anchor text
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE) # headings
    text = re.sub(r"[*_>#]", " ", text)                       # stray md symbols
    text = re.sub(r"(?<!\w)-(?!\w)", " ", text)               # dashes, but keep hyphens inside words (fast-paced)
    return re.sub(r"\s+", " ", text).strip()


def count_syllables(word):
    """Approximate syllable count for one word.

    Heuristic vowel-group counting. It is not perfect, but Flesch-Kincaid only
    needs a stable estimate across the whole document, and errors average out.
    """
    word = re.sub(r"[^a-z]", "", word.lower())
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and not word.endswith(("le", "ie", "ee")):
        count -= 1          # silent trailing 'e'
    return max(count, 1)     # every word has at least one syllable


def flesch_kincaid_grade(text):
    """Flesch-Kincaid Grade Level. Standard coefficients, hence the constants."""
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    words = re.findall(r"[A-Za-z]+", text)
    if not sentences or not words:
        return 0.0
    syllables = sum(count_syllables(w) for w in words)
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = syllables / len(words)
    # Coefficients are the published Flesch-Kincaid formula, not arbitrary.
    grade = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59
    return round(grade, 1)


def find_forbidden_words(prose, words):
    hits = {}
    lower = prose.lower()
    for w in words:
        n = len(re.findall(r"\b" + re.escape(w) + r"\b", lower))
        if n:
            hits[w] = n
    return hits


def find_forbidden_phrases(prose, phrases):
    """Match phrases loosely so 'not only ... but also' is caught with filler
    words in the gap, and punctuation between words doesn't hide a match."""
    hits = {}
    lower = prose.lower()
    for p in phrases:
        parts = [re.escape(tok) for tok in p.split()]
        pattern = r"\b" + r"\W+(?:\w+\W+){0,6}?".join(parts) + r"\b" \
            if len(parts) > 1 else r"\b" + parts[0] + r"\b"
        # Simpler exact-ish match first, then the loose one for multi-word.
        if len(parts) == 1:
            n = len(re.findall(r"\b" + parts[0] + r"\b", lower))
        else:
            n = len(re.findall(pattern, lower))
        if n:
            hits[p] = n
    return hits


def check_keyword_positions(raw_md, keyword):
    """Check the primary keyword sits in intro / an H2 / the conclusion."""
    kw = keyword.lower().strip()
    result = {"in_intro": False, "in_h2": False, "in_conclusion": False}

    prose = strip_markdown(raw_md).lower()
    result["in_intro"] = kw in prose[:INTRO_CHAR_WINDOW]

    for line in raw_md.splitlines():
        if re.match(r"^\s*##\s", line) and not re.match(r"^\s*###", line):
            if kw in line.lower():
                result["in_h2"] = True
                break

    paragraphs = [p for p in re.split(r"\n\s*\n", strip_markdown(raw_md)) if p.strip()]
    if paragraphs:
        result["in_conclusion"] = kw in paragraphs[-1].lower()
    return result


def main():
    ap = argparse.ArgumentParser(description="Countable lint checks for an article.")
    ap.add_argument("file", help="path to the article markdown file")
    ap.add_argument("--keyword", required=True, help="primary keyword to check positions for")
    ap.add_argument("--min-words", type=int, default=None, help="lower bound of target word band")
    ap.add_argument("--max-words", type=int, default=None, help="upper bound of target word band")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: file not found: {args.file}")
        sys.exit(1)

    with open(args.file, encoding="utf-8") as f:
        raw = f.read()

    prose = strip_markdown(raw)
    words, phrases = load_forbidden(FORBIDDEN_FILE)

    word_hits = find_forbidden_words(prose, words)
    phrase_hits = find_forbidden_phrases(prose, phrases)
    grade = flesch_kincaid_grade(prose)
    positions = check_keyword_positions(raw, args.keyword)
    word_count = len(re.findall(r"[A-Za-z0-9]+", prose))

    # Gate logic
    gates = {
        "no_forbidden_words": not word_hits,
        "no_forbidden_phrases": not phrase_hits,
        "keyword_in_intro": positions["in_intro"],
        "keyword_in_h2": positions["in_h2"],
        "keyword_in_conclusion": positions["in_conclusion"],
    }
    if args.min_words is not None:
        gates["above_min_words"] = word_count >= args.min_words
    if args.max_words is not None:
        gates["below_max_words"] = word_count <= args.max_words

    passed = all(gates.values())

    report = {
        "passed": passed,
        "word_count": word_count,
        "readability_grade_signal": grade,  # reported only, not a gate
        "forbidden_words": word_hits,
        "forbidden_phrases": phrase_hits,
        "keyword_positions": positions,
        "gates": gates,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        sys.exit(0 if passed else 1)

    # Human-readable report
    print("=" * 56)
    print(f"LINT REPORT — {os.path.basename(args.file)}")
    print("=" * 56)
    print(f"Word count:     {word_count}"
          + (f"  (target {args.min_words}-{args.max_words})"
             if args.min_words and args.max_words else ""))
    print(f"Readability:    grade {grade} (signal only — judge vs. your audience)")
    print()
    if word_hits:
        print("Forbidden WORDS found:")
        for w, n in sorted(word_hits.items()):
            print(f"  - '{w}' x{n}")
    else:
        print("Forbidden words: none  OK")
    if phrase_hits:
        print("Forbidden PHRASES found:")
        for p, n in sorted(phrase_hits.items()):
            print(f"  - '{p}' x{n}")
    else:
        print("Forbidden phrases: none  OK")
    print()
    print(f"Keyword '{args.keyword}':")
    print(f"  in intro (first {INTRO_CHAR_WINDOW} chars): "
          f"{'OK' if positions['in_intro'] else 'MISSING'}")
    print(f"  in an H2 heading:                {'OK' if positions['in_h2'] else 'MISSING'}")
    print(f"  in conclusion paragraph:         {'OK' if positions['in_conclusion'] else 'MISSING'}")
    print()
    print("-" * 56)
    print(f"RESULT: {'PASS — gate is green' if passed else 'FAIL — fix the items above and re-run'}")
    print("-" * 56)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
