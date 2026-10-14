#!/usr/bin/env python3
"""Gate 5 helper: check city copy before it reaches city-copy.json.

Reads the answers in 05-cache/city-copy/*.json (each a JSON object: city_slug -> {intro: [paragraphs],
faqs: [{q, a}]}), the city packets and the fact sheet.

Checks per city:
  - the copy gate (scripts/lint_copy.py): banned words and phrases, no em dash, niche term in the
    first paragraph, 4 to 6 FAQs (2 to 6 on a town page, lint_copy.faq_band), each answer 20 to 120 words
  - the word band for the city's size: 500 to 800 with 10 listings or more, 380 to 800 with 5 to 9,
    250 to 800 with 3 or 4, 120 to 800 for a small-town page kept by foldMaxKm (small pages are not
    padded to 500); the band comes from the packet's `intro band:` line
  - every number in the copy appears in that city's packet or on the fact sheet
  - no percentages and no dollar amounts
  - no wording about how the directory was built (website errors, search engines, "attribute", "packet")
Across cities:
  - no sentence of an intro or an FAQ answer appears in three or more cities (swapped-city boilerplate)
  - no opening (first eight words, city name removed) is shared by three or more cities
  The tally runs over every answers file in --copy plus the batch being checked, so a batch checked
  with --only is measured against the batches already written and a runner can fix its own share.
  Only the checked batch's cities are reported. The full run (no --only, or --write) lists the batch
  numbers to rerun with run_batches.py --only.

Usage:
  python3 scripts/check_city_copy.py --copy output/<slug>/05-cache/city-copy --batches output/<slug>/05-cache/city-batches \
      --facts output/<slug>/05-fact-sheet.md --niche "<niche plural>" [--only batch-03] [--write output/<slug>/site/src/data/city-copy.json]

--only checks one answers file against its own batch. --write needs every city answered and nothing failing.
"""
import argparse, glob, json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lint_copy as lc  # noqa: E402

# Words that belong to how the directory was built, not to what a homeowner reads.
INTERNAL_SRC = (r"(?:its|their|the|this|a) (?:web ?site|site|listing|footer|record|maps listing)s? (?:says?|said|lists?|states?|mentions?|shows?|names?|describes?)|according to (?:its|their|the)|on google maps|says? on (?:its|their) (?:web ?site|site)|does not (?:say|mention|list|state)|held out of search|search engines?|sitemap|noindex|not[- ]found|access error|server error|returned an? |"
                      r"refused the request|loaded empty|loaded securely|when the data was collected|\bpackets?\b|\battributes?\b|fact sheet|"
                      # The copy is about the town, not the directory's inventory of its listings (page-types, 2026-09-30).
                      r"\blistings? (?:say|says|state|states|mention|mentions|have|has|carry|carries|show|shows|name|names|touch|touches)\b|"
                      r"of the \d+ listings|\d+ listings\b|\blistings? (?:with|whose|have no|has no)\b|on record\b|no website\b|"
                      r"(?:website|site) (?:did not load|could not be read|shows almost nothing|says little)|nothing could be confirmed|"
                      r"(?:directory|we) (?:has|have) not checked|how the page is ordered|nothing on record|no answers\b|"
                      # Tallies in disguise, comparisons with other cities, and the buyer's-guide lesson about review counts (2026-09-30).
                      r"\b\d+ (?:NICHE_NOUNS|builders?|contractors?|companies|firms?|businesses|shops?|providers?|installers?|dealers?|pros|professionals|practices?|clinics?|agencies|agents?|studios?|of them|of the \d+) (?:say|says|state|states|name|names|mention|mentions|list|lists|describe|describes|also|here|in all)\b|"
                      r"\b(?:more|fewer|less|higher|lower) (?:than|here than) in (?:most|some|other|the other|any)|than in [A-Z][a-z]+(?: [A-Z][a-z]+)?\b|"
                      r"\bin this (?:group|batch)\b|most towns|other towns|tells you (?:far )?less|read (?:the )?ratings? (?:alongside|with) (?:the )?(?:review )?counts?")
INTERNAL = re.compile(INTERNAL_SRC.replace("NICHE_NOUNS|", ""), re.I)


def set_niche(niche):
    """Add the niche's own nouns ("pool builders" -> pool builders?, builders?) to the tally pattern."""
    global INTERNAL
    words = [w for w in re.findall(r"[a-z]+", (niche or "").lower()) if len(w) > 2]
    # The head noun ("builders" in "pool builders") and the whole phrase; not every word, since "10 pools" is a count of pools, not of businesses.
    nouns = sorted({re.escape(w).rstrip("s") + "s?" for w in words[-1:]} | ({re.escape(" ".join(words)).rstrip("s") + "s?"} if len(words) > 1 else set()))
    INTERNAL = re.compile(INTERNAL_SRC.replace("NICHE_NOUNS|", "|".join(nouns) + "|" if nouns else ""), re.I)

NUM = re.compile(r"(?<![A-Za-z0-9#])\d[\d,]*(?:\.\d+)?")
WORDNUM = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12"}


def numbers(text):
    return {n.replace(",", "").rstrip(".") for n in NUM.findall(text)}


def load_packets(folder):
    packets, bands, names = {}, {}, {}
    for p in glob.glob(os.path.join(folder, "batch-*.md")):
        for block in re.split(r"\n(?=### )", open(p, encoding="utf-8").read()):
            m = re.match(r"### (\S+)\ncity: (.+)\n", block)
            if not m: continue
            slug = m.group(1); packets[slug] = block; names[slug] = m.group(2).strip()
            b = re.search(r"intro band: (\d+) to (\d+) words", block)
            bands[slug] = (int(b.group(1)), int(b.group(2)))
    return packets, bands, names


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copy", required=True); ap.add_argument("--batches", required=True); ap.add_argument("--facts", required=True)
    ap.add_argument("--niche", required=True); ap.add_argument("--only", default=""); ap.add_argument("--write", default="")
    a = ap.parse_args()
    set_niche(a.niche)
    packets, bands, names = load_packets(a.batches)
    fact_nums = numbers(open(a.facts, encoding="utf-8").read())
    words, phrases = lc.load_bans()
    every = sorted(glob.glob(os.path.join(a.copy, "*.json")))
    files = [os.path.join(a.copy, a.only + ".json")] if a.only else every
    copy, fails, source = {}, defaultdict(list), {}
    for p in files:
        try: data = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print(f"FAIL {os.path.basename(p)}: not valid JSON ({e})"); sys.exit(1)
        for slug, block in data.items():
            if slug in copy: fails[slug].append("written twice")
            copy[slug] = block; source[slug] = os.path.basename(p)
    # The other batches already answered: their sentences and openings join the tally so a batch checked
    # with --only sees what the rest of the run wrote, but only the checked batch's cities can fail on it.
    others = {}
    for p in every:
        if os.path.realpath(p) in {os.path.realpath(f) for f in files}: continue
        try: data = json.load(open(p, encoding="utf-8"))
        except Exception: continue   # a half-written file from a run in flight; its own check will report it
        for slug, block in data.items():
            if slug not in copy: others[slug] = block; source[slug] = os.path.basename(p)
    expected = set(json.load(open(os.path.join(a.batches, a.only + ".slugs.json")))) if a.only else set(packets)
    for s in expected - set(copy):
        if a.only or a.write: fails[s].append("not written")
    sent_seen, opener_seen, total_words = defaultdict(set), defaultdict(set), 0

    def tally(slug, block):
        """Add a city's sentences (intro and FAQ answers, nine words or more, city name removed) and its
        opening to the shared tallies. FAQ questions are left out: people in different cities ask the same things."""
        intro = [p for p in block.get("intro", []) if p.strip()]; faqs = block.get("faqs", [])
        name = names.get(slug, "\0").lower()
        body = "\n\n".join(intro) + "\n" + "\n".join(f.get("a", "") for f in faqs)
        for s in re.split(r"(?<=[.!?])\s+", body):
            k = " ".join(re.sub(r"[^a-z0-9 ]", "", s.lower().replace(name, "")).split())
            if len(k.split()) >= 9: sent_seen[k].add(slug)
        if intro:
            k = " ".join(re.sub(r"[^a-z ]", "", intro[0].lower().replace(name, "")).split()[:8])
            opener_seen[k].add(slug)

    for slug, block in others.items(): tally(slug, block)
    for slug, block in copy.items():
        if slug not in packets: fails[slug].append("no such city in the packets"); continue
        intro = [p for p in block.get("intro", []) if p.strip()]; faqs = block.get("faqs", [])
        text = "\n\n".join(intro)
        gates, rep = lc.check_prose(text, words, phrases, niche=a.niche, band=bands[slug], label=slug)
        total_words += rep["words"]
        if not gates["in_word_band"]: fails[slug].append(f"intro is {rep['words']} words, band is {bands[slug][0]} to {bands[slug][1]}")
        if not gates["niche_in_first_paragraph"]: fails[slug].append(f'"{a.niche}" is not in the first paragraph')
        if rep["forbidden_words"]: fails[slug].append(f"banned words: {sorted(set(rep['forbidden_words']))}")
        if rep["forbidden_phrases"]: fails[slug].append(f"banned phrases: {sorted(set(rep['forbidden_phrases']))}")
        faq_lo, faq_hi = lc.faq_band(bands[slug])   # a town page with one or two listings cannot carry four honest questions
        if not (faq_lo <= len(faqs) <= faq_hi): fails[slug].append(f"{len(faqs)} FAQs, need {faq_lo} to {faq_hi}")
        everything = text + "\n" + "\n".join(f.get("q", "") + "\n" + f.get("a", "") for f in faqs)
        for i, f in enumerate(faqs, 1):
            n = lc.count_words(f.get("a", ""))
            if not (lc.FAQ_ANSWER_WORDS[0] <= n <= lc.FAQ_ANSWER_WORDS[1]): fails[slug].append(f"FAQ {i} answer is {n} words, band is 20 to 120")
            bw = lc.la.find_forbidden_words(f.get("a", "") + " " + f.get("q", ""), words); bp = lc.la.find_forbidden_phrases(f.get("a", "") + " " + f.get("q", ""), phrases)
            if bw or bp: fails[slug].append(f"FAQ {i} banned: {sorted(set(list(bw) + list(bp)))}")
        if re.search(r"[—–]| -- ", everything): fails[slug].append("dash used as punctuation")
        if "%" in everything or re.search(r"\bpercent\b", everything, re.I): fails[slug].append("percentage used; give the count from the packet")
        if "$" in everything: fails[slug].append("dollar amount used; the packet has no prices")
        inside = sorted({m.group(0).lower() for m in INTERNAL.finditer(everything)})
        if inside: fails[slug].append(f"internal wording a homeowner should not read: {inside} (say \"its website could not be read\", \"no details on record\", or cut the sentence)")
        allowed = numbers(packets[slug]) | fact_nums
        allowed |= {w for w in WORDNUM.values()}
        bad = sorted(n for n in numbers(everything) if n not in allowed and re.sub(r"\.0+$", "", n) not in allowed)
        if bad: fails[slug].append(f"numbers not in the packet or the fact sheet: {bad}")
        tally(slug, block)
    shared_batches = set()
    for kind, seen in (("sentence", sent_seen), ("opening", opener_seen)):
        for k, s in seen.items():
            if len(s) < 3: continue
            for slug in s:
                if slug not in copy: continue   # another batch's city: it fails in its own check, not here
                where = sorted({source.get(o, "?") for o in s if o != slug})
                fails[slug].append(f'{kind} shared with {len(s) - 1} other cities ({", ".join(sorted(o for o in s if o != slug))}, in {", ".join(where)}): "{k[:80]}"')
                shared_batches |= {source[o] for o in s if o in source}
    print(f"cities written: {len(copy)}, failing: {len(fails)}, intro words in total: {total_words}"
          + (f" (shared sentences and openings tallied with {len(others)} cities from the other batches)" if others else ""))
    for s, e in sorted(fails.items())[:80]: print(f"FAIL {s}: " + "; ".join(e))
    if len(fails) > 80: print(f"... and {len(fails) - 80} more")
    if shared_batches and not a.only:
        nums = sorted(re.sub(r"\D", "", b) for b in shared_batches)
        print(f"shared sentences or openings cross batches; reword them in the answers files, or rerun those batches so each city reads as its own place: "
              f"scripts/run_batches.py city-copy --slug <slug> --niche \"{a.niche}\" --only <num>, for {', '.join(nums)}")
    if fails: sys.exit(1)
    if a.write:
        out = {"_readme": "Written at Gate 5 from the city packets and the fact sheet. Checked by scripts/check_city_copy.py. Do not edit by hand; edit the files in 05-cache/city-copy and run the check with --write."}
        for slug in sorted(copy): out[slug] = {"intro": [p.strip() for p in copy[slug]["intro"] if p.strip()], "faqs": copy[slug]["faqs"]}
        json.dump(out, open(a.write, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"wrote {a.write}")


if __name__ == "__main__":
    main()
