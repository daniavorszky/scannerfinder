---
title: Copy gate (Gate 5)
type: seo
status: active
updated: 2026-09-30
---

# Copy gate

The design-seed checklist catches the visual tells of a Claude-coded site ([[design-seed]]). This gate catches the prose tells, and it runs at Gate 5: on `city-copy.json` and the resource pages before `npm run build`, and on the built home, state and About pages in `dist/` after it, since those draw copy from `site.json`. It uses Rank Expand Academy's own **seo-content-engine** skill, shipped in `skills/seo-content-engine/`, in two ways.

## 1. Lint every short block (no account needed)

`scripts/lint_copy.py` reads the skill's hard-ban list (`skills/seo-content-engine/references/forbidden_words.txt`) plus the Blueprint's own additions (`scripts/copy-bans.txt`: swapped-city boilerplate such as "nestled", "vibrant", "in the heart of", and the community's banned openers) and applies them with the skill's own functions. Standard library only, exit 1 on any failure, so the loop is run, fix, rerun.

| Copy | Command | Gates |
|---|---|---|
| City blocks and FAQs | `python3 scripts/lint_copy.py output/<slug>/site/src/data/city-copy.json --niche "<niche plural>" --city-sizes output/<slug>/05-city-sizes.json` | the word and FAQ band for the city's size class ([[page-types]]: 500 to 800 words and 4 to 6 FAQs with 10 listings or more, down to 120 words and 2 to 6 FAQs on a town page), each answer 20 to 120 words, niche term in the first paragraph, no banned words or phrases, no em dashes |
| About page (built) | `python3 scripts/lint_copy.py output/<slug>/site/dist/about/index.html --min-words 300 --max-words 500` | page band from [[page-types]], bans, em dashes |
| Home (built) | `python3 scripts/lint_copy.py output/<slug>/site/dist/index.html --min-words 800 --max-words 1500 --niche "<niche plural>"` | page band, niche early, bans, em dashes. The buyer's guide block inside it stays 400 to 600 words and the FAQ 5 to 8 questions |
| State hub (built) | `python3 scripts/lint_copy.py output/<slug>/site/dist/directory/<state>/index.html --min-words 300 --max-words 500` | page band, bans, em dashes |
| Resource page | `python3 scripts/lint_copy.py output/<slug>/site/src/pages/resources/<slug>.md --min-words 1200 --niche "<topic>"` | 1,200 words or more, topic early, bans, em dashes |

Reading grade is reported, not gated (the skill's rule: the right grade depends on the audience). Expect grade 7 to 10 for local service copy; above 12, shorten sentences.

`.astro` pages are linted as a whole, fixed paragraphs included, so the band is the page band, not the block band. Do not lint the home page from `index.astro`: it undercounts (666 words on the dry run against 1,195 built) and its first paragraph after stripping is the H1 expression, so the niche check fails for the wrong reason.

**Why the built home band is 800 to 1,500.** The master template's structure (city cards, stat row, search labels, hero promises, the four vetting steps) is about 300 words of text in `dist/index.html` before any copy is written. With the guide at its 400 to 600 and the FAQ at 5 to 8 questions, the old 1,200 cap forced the dry run to cut the FAQ to five and the vetting text to two paragraphs (1,516 words on the first build, 1,195 after four trims). The cap on the built page is now 1,500 so the guide and FAQ bands in [[page-types]] can hold at the same time; the written copy is still about 800 to 1,200.

### Added on the pilot (2026-09-29)

- **Lint the built page when its copy comes from data.** `lint_copy.py` accepts `dist/.../index.html` and counts the text inside `<main>`, leaving out breadcrumbs and lists of city links. The home, state and About pages draw copy from `site.json`, so the `.astro` source undercounts them.
- **Small-city floors:** `--city-sizes <json>` ([[page-types]]); a small-town page with 1 or 2 listings has a 120-word floor and 2 to 6 FAQs. Both checkers take the FAQ band from `lint_copy.faq_band` since 2026-09-30, so they agree.
- **City copy has its own checker**, `scripts/check_city_copy.py`, which runs the copy gate and adds four tests: every number must be in the city's data or on the fact sheet, no percentages or dollar amounts, no internal wording, and no sentence or opening shared by three or more cities.
- **The buyer's guide and the skill.** Decided by Shawn, 2026-09-29: use the skill when it is available. The skill writes one long article per run and stops for approval at each stage, while the buyer's guide block is 400 to 600 words inside a page capped at 1,200, so the home page carries the skill's article cut to the block and linted, and the full article may go on as a resource page. Without a DataForSEO connection the block is written by hand from the fact sheet and linted, which is what the pilot did.

## 2. Write the article-shaped pages with the skill (DataForSEO optional)

Resource pages, the home buyer's guide and any local article ([[authority-and-links]]) are the copy that is actually article-shaped: one topic, one page, built to earn a link. For these, run the skill's full workflow (say "use the seo-content-engine skill for the resource page on <topic>"). Stage 1 pulls the live top results for the topic through the member's own DataForSEO connection and the later stages draft, humanize, fact-check and export.

- DataForSEO is **optional** on the member path. The launch (Gates 1 to 6) needs none of it. Without a connection, write these pages by hand from the sources you have (state rules, hotlines, realtor videos) and lint them with the table above.
- The skill finds the connection by tool name under any prefix: a claude.ai DataForSEO connector or a server added with `claude mcp add` both work. Members set it up themselves; the skill never asks for a credential in chat and `references/credentials.md` ships blank. If a member fills that file in on their own machine, it stays on their machine.
- The connector exposes no account-balance tool, so the skill's balance line may not appear. That is not an error.

## What the skill is not for

The city block. The skill writes one long-form article per run (TL;DR, sections, verdict, median competitor length plus ten percent). A city page is 500 to 800 words of local copy above the listing cards, written from the enriched data, and sixty of them would be sixty runs of the wrong shape. Lint them, do not generate them.

## Source

Wired 2026-09-29 from the skill at version 2.0.0. DataForSEO is optional, the skill ships in the zip, and it is still in test.
