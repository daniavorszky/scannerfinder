#!/usr/bin/env python3
"""
lint_copy.py, the Gate 5 copy gate for the Directory Blueprint.

Runs the seo-content-engine linter's checks (skills/seo-content-engine) on the SHORT
copy the skill itself does not write: the city blocks and FAQs in city-copy.json, the
About and buyer's guide blocks in the .astro pages, and any markdown file. No DataForSEO
call is made; this is standard library only.

Usage:
    python3 scripts/lint_copy.py output/<slug>/site/src/data/city-copy.json --niche "pool builders"
    python3 scripts/lint_copy.py output/<slug>/site/src/pages/about.astro --min-words 300 --max-words 500
    python3 scripts/lint_copy.py output/<slug>/site/src/pages/index.astro --min-words 800 --max-words 1200 --niche "pool builders"
    python3 scripts/lint_copy.py output/<slug>/site/src/pages/resources/<slug>.md --min-words 1200 --niche "..."
    add --json for machine output

    python3 scripts/lint_copy.py output/<slug>/site/dist/index.html --min-words 800 --max-words 1200 --niche "pool builders"

A built .html page is linted on the text inside <main>: what the visitor reads, including copy that
comes from site.json and the data. Prefer it to the .astro source when a page draws copy from data.

An .astro page is linted as a whole (its fixed paragraphs plus the Gate 5 block), so the
word band is the page band from wiki/framework/page-types.md, not the block band.

With --city-sizes (a JSON file mapping city_slug to its number of listings), each city page gets the band
for its size class from wiki/framework/page-types.md: 500 to 800 words and 4 to 6 FAQs with 10 listings or
more, 380 to 800 with 5 to 9, 250 to 800 with 3 or 4, and for a town page (1 or 2 listings, kept by
foldMaxKm) 120 to 800 words and 2 to 6 FAQs. The report marks every page under 10 as a small city.
Without --city-sizes every city needs 500 words and 4 FAQs. check_city_copy.py reads the same classes
from the packets' band lines and shares faq_band() below, so the two checkers agree.

Gates per city block: the word band and FAQ count for the size class, every FAQ answer
20 to 120 words, the niche term in the first paragraph, no forbidden words or phrases
(the skill's list plus scripts/copy-bans.txt), no em dashes. Reading grade is reported,
not gated (the skill's rule). Exit 1 when any gate fails, so run, fix, rerun.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILL_SCRIPTS = os.path.join(ROOT, "skills", "seo-content-engine", "scripts")
SKILL_FORBIDDEN = os.path.join(ROOT, "skills", "seo-content-engine", "references", "forbidden_words.txt")
LOCAL_BANS = os.path.join(HERE, "copy-bans.txt")

sys.path.insert(0, SKILL_SCRIPTS)
try:
    import lint_article as la  # noqa: E402
except ImportError:
    print(f"ERROR: the seo-content-engine skill is missing at {SKILL_SCRIPTS}. Unzip the Blueprint again.")
    sys.exit(2)

CITY_WORDS = (500, 800)
TOWN_WORDS = (120, 800)     # a small-town page with 1 or 2 listings kept by foldMaxKm (page-types, Shawn 2026-09-29)
FAQ_COUNT = (4, 6)
TOWN_FAQ_COUNT = (2, 6)     # the same page: two honest questions beat four padded ones
FAQ_ANSWER_WORDS = (20, 120)


def load_bans():
    words, phrases = la.load_forbidden(SKILL_FORBIDDEN)
    w2, p2 = la.load_forbidden(LOCAL_BANS)
    return words + w2, phrases + p2


def count_words(text):
    return len(re.findall(r"[A-Za-z0-9]+", text))


def astro_to_text(raw):
    """Keep only the human-readable text of an .astro page: drop the frontmatter
    script, tags, comments and template expressions."""
    raw = re.sub(r"^---.*?---", "", raw, count=1, flags=re.S)
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    raw = re.sub(r"\{[^{}]*\}", " ", raw)
    raw = re.sub(r"</?(p|h[1-6]|li|section|div|br)[^>]*>", "\n\n", raw)
    raw = re.sub(r"<[^>]+>", "", raw)
    return raw


def html_to_text(raw):
    """A built page from dist/: keep the text inside <main>, which is what the visitor reads.
    Header, footer, scripts, styles and JSON-LD are left out."""
    # The page head (H1, lede) sits in its own band above <main> and is part of the copy.
    m = re.search(r'(<div class="page-head.*?)?<main[^>]*>(.*?)</main>', raw, flags=re.S)
    raw = ((m.group(1) or "") + m.group(2)) if m else raw
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S)
    # A page can fence off a block that is not copy (the city index) with copy:skip markers.
    raw = re.sub(r"<!-- copy:skip -->.*?<!-- /copy:skip -->", " ", raw, flags=re.S)
    raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    # Navigation is not copy: breadcrumbs and the lists of city links are left out of the count.
    raw = re.sub(r"<nav[^>]*>.*?</nav>", " ", raw, flags=re.S)
    raw = re.sub(r'<ul class="city-grid"[^>]*>.*?</ul>', " ", raw, flags=re.S)
    raw = re.sub(r"</?(p|h[1-6]|li|section|div|br|dt|dd|article|aside|ul|ol|dl)[^>]*>", "\n\n", raw)
    raw = re.sub(r"<[^>]+>", "", raw)
    for ent, ch in (("&amp;", "&"), ("&quot;", '"'), ("&#39;", "'"), ("&lt;", "<"), ("&gt;", ">"), ("&nbsp;", " ")):
        raw = raw.replace(ent, ch)
    return raw


def md_to_text(raw):
    raw = re.sub(r"^---.*?---", "", raw, count=1, flags=re.S)
    return la.strip_markdown(raw)


def check_prose(prose, words, phrases, niche=None, band=None, label=""):
    """Shared checks for one block of prose. Returns (gates, report)."""
    wc = count_words(prose)
    word_hits = la.find_forbidden_words(prose, words)
    phrase_hits = la.find_forbidden_phrases(prose, phrases)
    em_dashes = prose.count("—") + prose.count(" -- ")
    first_para = next((p for p in re.split(r"\n\s*\n", prose) if p.strip()), "")
    gates = {
        "no_forbidden_words": not word_hits,
        "no_forbidden_phrases": not phrase_hits,
        "no_em_dashes": em_dashes == 0,
    }
    if band:
        gates["in_word_band"] = band[0] <= wc <= band[1]
    if niche:
        gates["niche_in_first_paragraph"] = niche.lower() in first_para.lower()
    report = {
        "label": label,
        "words": wc,
        "reading_grade": la.flesch_kincaid_grade(prose),
        "forbidden_words": word_hits,
        "forbidden_phrases": phrase_hits,
        "em_dashes": em_dashes,
        "gates": gates,
    }
    return gates, report


def city_band(n):
    """Word band by the number of listings on the city page (the size classes in page-types.md). A page
    with three listings cannot carry 500 honest words, so small cities get a lower floor instead of padding."""
    if n is None or n >= 10:
        return CITY_WORDS
    return TOWN_WORDS if n < 3 else (250, CITY_WORDS[1]) if n < 5 else (380, CITY_WORDS[1])


def faq_band(band):
    """The FAQ count band that goes with a word band: a town page (the 120-word floor) takes 2 to 6,
    every other city page 4 to 6. check_city_copy.py calls this with the packet's band."""
    return TOWN_FAQ_COUNT if band[0] < 250 else FAQ_COUNT


def lint_city_copy(path, niche, words, phrases, sizes=None):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    reports = []
    for slug, block in data.items():
        if slug.startswith("_"):
            continue
        intro = "\n\n".join(block.get("intro", []))
        faqs = block.get("faqs", [])
        band = city_band((sizes or {}).get(slug))
        fband = faq_band(band)
        gates, rep = check_prose(intro, words, phrases, niche=niche, band=band, label=slug)
        rep["band"] = band
        rep["faq_band"] = fband
        gates["faq_count"] = fband[0] <= len(faqs) <= fband[1]
        bad_answers = []
        for i, fq in enumerate(faqs):
            a = fq.get("a", "")
            n = count_words(a)
            if not (FAQ_ANSWER_WORDS[0] <= n <= FAQ_ANSWER_WORDS[1]):
                bad_answers.append(f"faq {i + 1}: {n} words")
            fw = la.find_forbidden_words(a, words)
            fp = la.find_forbidden_phrases(a, phrases)
            if fw or fp:
                bad_answers.append(f"faq {i + 1}: {list(fw) + list(fp)}")
            if "—" in a or "—" in fq.get("q", ""):
                bad_answers.append(f"faq {i + 1}: em dash")
        gates["faq_answers_ok"] = not bad_answers
        rep["faqs"] = len(faqs)
        rep["faq_problems"] = bad_answers
        rep["gates"] = gates
        reports.append(rep)
    return reports


def lint_file(path, niche, band, words, phrases):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if path.endswith(".astro"):
        prose = astro_to_text(raw)
    elif path.endswith(".html"):
        prose = html_to_text(raw)
    elif path.endswith(".json"):
        raise SystemExit("For city-copy.json pass --niche and no word band; the city band is fixed.")
    else:
        prose = md_to_text(raw)
    _, rep = check_prose(prose, words, phrases, niche=niche, band=band, label=os.path.basename(path))
    return [rep]


def print_report(reports):
    for r in reports:
        failed = [g for g, ok in r["gates"].items() if not ok]
        status = "PASS" if not failed else "FAIL"
        line = f"{status}  {r['label']}: {r['words']} words, grade {r['reading_grade']}"
        if "faqs" in r:
            line += f", {r['faqs']} FAQs"
        if r.get("band") and r["band"] != CITY_WORDS:
            line += f" (small city, floor {r['band'][0]}" + (f", {r['faq_band'][0]} to {r['faq_band'][1]} FAQs)" if r.get("faq_band") == TOWN_FAQ_COUNT else ")")
        print(line)
        if r["forbidden_words"]:
            print(f"       forbidden words: {r['forbidden_words']}")
        if r["forbidden_phrases"]:
            print(f"       forbidden phrases: {r['forbidden_phrases']}")
        if r["em_dashes"]:
            print(f"       em dashes: {r['em_dashes']}")
        for p in r.get("faq_problems", []):
            print(f"       {p}")
        if failed:
            print(f"       failed gates: {', '.join(failed)}")


def main():
    ap = argparse.ArgumentParser(description="Gate 5 copy gate for the Directory Blueprint.")
    ap.add_argument("file", help="city-copy.json, an .astro page, or a markdown file")
    ap.add_argument("--niche", help='the niche term the copy must name early, e.g. "pool builders"')
    ap.add_argument("--min-words", type=int)
    ap.add_argument("--max-words", type=int)
    ap.add_argument("--city-sizes", help="JSON file mapping city_slug to its number of listings; cities with fewer than 10 get a lower word floor (380 for 5 to 9, 250 for 3 or 4, 120 and 2 to 6 FAQs for a town page with 1 or 2)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"ERROR: file not found: {args.file}")
        sys.exit(1)

    words, phrases = load_bans()
    if args.file.endswith(".json"):
        if not args.niche:
            print("ERROR: --niche is required for city-copy.json")
            sys.exit(1)
        sizes = json.load(open(args.city_sizes, encoding="utf-8")) if args.city_sizes else None
        reports = lint_city_copy(args.file, args.niche, words, phrases, sizes)
    else:
        band = None
        if args.min_words is not None or args.max_words is not None:
            band = (args.min_words or 0, args.max_words or 10**9)
        reports = lint_file(args.file, args.niche, band, words, phrases)

    if args.json:
        print(json.dumps(reports, indent=2))
    else:
        print_report(reports)
    ok = all(all(r["gates"].values()) for r in reports)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
