# SEO Content Engine

A Claude Code skill that studies the live Google results for your topic and writes a
humanized, SEO-optimized article built to compete with the pages already ranking.

## What it does

You give it a keyword or topic. It pulls the live top-ranking pages from Google
(via DataForSEO), analyzes what they cover and how they're structured, then walks you
through building an article that matches the winning format and fills the gaps they
miss. You confirm the direction at each step; it never runs off on its own. The final
output is three files named after your article: a clean Markdown article, a styled
HTML preview, and a plain-text file with the meta title and description for your CMS.

## What makes it different

- **Real SERP analysis, not guesswork.** It reads the actual top-ranking pages for
  your keyword and the real keywords each one ranks for, rather than inventing a plan
  from thin air.
- **Grounded in what's real.** Keyword targets come only from keywords the ranking
  pages actually rank for; entities come only from what those pages actually mention.
  It won't invent keywords, stats, or FAQ questions.
- **Fact-checked.** Every number, price, and claim in the draft is checked against a
  credible source, corrected if wrong, linked to that source, or softened if it can't
  be verified.
- **Written to read human.** A built-in humanizer strips the words and phrases that
  make text sound machine-written, and enforces plain, direct writing.
- **Format-aware.** It detects whether the winning results are roundups, comparisons,
  how-tos, reviews, guides, or answer posts, and builds the matching structure.
- **Your voice, optionally.** Point it at a few of your own articles (links or files)
  and it will match your tone.
- **You stay in control.** It pauses at every stage to show you what it found and let
  you refine before moving on.

## What you'll need

- [Claude Code](https://claude.com/claude-code)
- A **DataForSEO account** with API access to the **SERP API**, **DataForSEO Labs
  API**, and **OnPage API**. These calls are metered, so keep some balance on the
  account — a single run makes several billable calls.

## Install

Install the skill manually — it works the same on any operating system:

1. **Unzip** the downloaded skill file. You'll get a folder named `seo-content-engine`
   containing `SKILL.md`, `README.md`, and the `references`, `scripts`, and `assets`
   folders.
2. **Find your Claude Code skills folder.** It's in your home directory:
   - macOS / Linux: `~/.claude/skills/`
   - Windows: `%USERPROFILE%\.claude\skills\`
   If the `skills` folder doesn't exist yet, create it.
3. **Move the whole `seo-content-engine` folder** into that `skills` folder, so you end
   up with `.../.claude/skills/seo-content-engine/SKILL.md` (the `SKILL.md` sits one
   level inside, not loose in `skills`).
4. **Restart Claude Code** so it picks up the new skill.

Then open Claude Code in any project folder and describe the article you want (see
below). On the first run, the skill walks you through connecting DataForSEO; after
that it remembers your credentials.

## The Workflow

To start, just describe the article in Claude Code — for example: *"Write an SEO
article on 'best CRM for small business' using my SEO Content Engine skill."* The
skill then moves through these stages, pausing for your confirmation at each one:

- **Stage 0 — DataForSEO setup.** Connects your DataForSEO account. Skipped once
  you're connected; runs again only if you change credentials.
- **Stage 1 — SERP analysis.** Confirms your keyword, market, and audience, then pulls
  and analyzes the live top-ranking pages: their structure, the keywords they rank for,
  the entities they cover, and the questions people ask. Ends with a full report.
- **Stage 2 — Existing-content sources.** You point it at your own site's URLs (or
  skip) so the article can link to your related pages.
- **Stage 3 — Product integration.** You name any product, service, or lead magnet you
  want to feature, so the outline can give it a natural home.
- **Stage 4 — Outline + BLUF.** It suggests the format the SERP rewards, builds the
  outline, and gives each section a one-line thesis. You approve before any writing.
- **Stage 5 — Article draft.** It picks a voice (default, match yours, or a brief you
  describe) and writes the article section by section, plus a draft meta title and
  description.
- **Stage 6 — Fact check + quality audit.** It runs the checks: forbidden words,
  keyword placement, readability, and fact-verification of every stat and claim,
  fixing issues until the draft passes.
- **Stage 7 — HTML preview.** It renders the article as a clean, styled HTML page you
  can read in a browser.
- **Stage 8 — Final export.** It saves three files named after your article (topic +
  format) to your folder: the Markdown article, the HTML preview, and a `-meta.txt`
  with the meta title and description for your CMS.

## File structure

```
seo-content-engine/
├── SKILL.md                      the workflow the skill follows
├── README.md                     this file
├── references/
│   ├── setup.md                  DataForSEO connection steps
│   ├── credentials.md            your DataForSEO login — blank this before sharing
│   ├── dfs-mcp-tools.md          how the DataForSEO endpoints are used + report format
│   ├── excluded-domains.md       which results to filter out of the analysis
│   ├── article-format-guidelines.md    the article formats and when to use each
│   ├── article-template-guidelines.md  how to write each section
│   ├── article-style-rules.md    the writing rules and the humanizer
│   ├── forbidden_words.txt       the hard-banned AI tells the linter checks
│   ├── locations.json            DataForSEO country codes
│   ├── languages.json            DataForSEO language codes
│   └── brand-voice/
│       └── README.md             how to supply samples to match your voice
├── scripts/
│   ├── lint_article.py           checks forbidden words, keyword placement, readability
│   └── extract_claims.py         finds every stat/claim to fact-check
└── assets/
    └── preview.template.html     the HTML shell for the Stage 7 preview
```

**Note on credentials:** your DataForSEO login lives in `references/credentials.md`.
It stays on your machine and is never uploaded anywhere. If you share or publish this
skill, blank out that file first.
