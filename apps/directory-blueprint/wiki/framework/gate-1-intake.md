---
title: Gate 1 intake
type: framework
status: active
updated: 2026-10-01
---

# Gate 1 intake

Gate 1 is a fixed conversation, not an improvised one. Ask the questions below **in this order, one per turn**, each with its one-line why and its example, and write every answer into `output/<slug>/01-scope.md` as it arrives. When all eight are answered, show the scope file and ask for approval. Gate 2 runs after the member approves `01-scope.md`, in the same session if they say so ("approved, run Gate 2" is enough); never before.

## The build folder and its slug

Every artifact goes into `output/<slug>/`. The slug is `<state code, lowercase>-<category plural, kebab-case>`, built from the answers to questions 1 and 2: Colorado plus "fence contractor" is `co-fence-contractors`, Florida plus "swimming pool contractor" is `fl-swimming-pool-contractors`. Use the Maps category's own words, pluralized, not a shortened trade name. State the slug in the scope file; every later script takes it as `--slug` or in `--out`. (The pilot's `florida-pool-builders` folder predates this rule and stays as it is.)

## Hard rules for the whole conversation

- **Never recommend or pre-fill a niche, a state, a domain or a person's name.** Not from this folder, not from the machine (git author, OS user, earlier projects), not from your own judgment. Every option you present is either the member's own words or a shape (category domain, own domain), never a concrete pick. Examples in this wiki (a pool builder vertical, Florida) are examples of the shape, not suggestions.
- **A member who names a vertical is not questioned about it.** Record it and go on. No scorecard, no "have you considered", no second option, no numbers they did not ask for. Members stall on this choice more than on anything else in the course, and the job here is to get them building (Shawn, 2026-10-01). Two exceptions only, both in "The vertical check" below: the member asks for a check (or says they have no vertical, or says they are unsure), or the estimate raises a `VERTICAL FLAG`. Whether a member is unsure is theirs to say; never read doubt into an answer that names a vertical.
- **You never originate a vertical.** A member without one is helped to check the ones they name (below), in their words; if they have none to name, Step 1 of the course (Niche Finder GPT) is where candidates come from.
- **One question per turn**, a sentence of why, one concrete example, and the reply format the answer needs (a word, a URL, a list, a yes or no). No stacked questions. The one exception is the three yes or no points of a requested vertical check, which are asked together because they are one judgment.
- If the member's answer is unclear, ask one follow-up, do not guess.

## Before question 1: is DataForSEO connected

Run `python3 scripts/connect_dataforseo.py --check` (free, prints yes or no and never the login) and keep the answer; do not mention it to the member, it is not their concern until question 8. It decides two things: whether the estimate runs after question 2, and what question 8 offers first.

## The vertical check

There are three situations, and only these.

**1. The member names a vertical and a state and asks nothing.** The normal case. If DataForSEO is connected, run the estimate straight after question 2 (`scripts/fetch_dataforseo.py --category <id> --state <State> --state-code <ST> --estimate`, about five cents, the same request question 8 needs, so it is not paid twice). Keep its numbers for question 8. If it prints `Vertical flags: none.`, say nothing about the vertical and ask question 3. If DataForSEO is not connected, there is no check; ask question 3.

**2. The estimate prints a `VERTICAL FLAG`.** The script flags two things only, both hard: fewer than 100 businesses carry the category as their primary one in that state, or fewer than half have a website. (A third message, no rows at all, is a spelling problem and not a verdict: fix the category id or the state name and run the estimate again, without asking the member to continue.) Tell the member once, in two or three sentences: the number, what it means for the directory (thin city pages, or listings that are a name and a phone number), and one question: "Reply continue to build it anyway, or name another service or state." Take the answer and never raise it again. Do not add criteria of your own to the flag, and do not flag anything the script did not.

**3. The member says they have no vertical, says they are unsure of theirs, or asks "is this a good one".** Then, and only then, run the check:
- If they already own microsites, the course's answer is that service in that state (Step 1: "if you already have microsites, this step is done"). Say so and ask whether that is the directory.
- Otherwise ask for up to three services they are weighing, in their own words, and the state. If they have none to name, send them to the Niche Finder GPT in Step 1 and stop; the check works on candidates, it does not invent them. A half-formed answer ("something with pools") is turned into Maps categories with `scripts/fetch_dataforseo.py --find-category <word>` (free): show the three or four that are trades and ask which one they mean.
- With DataForSEO connected, run `python3 scripts/check_vertical.py --category <id> --state <State>` on the first candidate (about five cents each; the card ends with the cost, so run it without asking first). It prints one card: the category exists, the size against the 200 to 5,000 band, how much of the category is the trade, and how many have a website. Show the card as it is and add nothing to it: no search results, no competitors, no volumes. Then ask the three things the script cannot measure as one yes or no question: do people get more than one quote for this job, does it run four figures with no favorite company, and is there something real to explain about choosing one.
- **The first candidate that passes is the vertical.** Say "this one passes, we build it" and go to question 2 or 3. Check the next candidate only when one fails or the member asks. Never lay candidates side by side, never rank them, never bring up search volumes or difficulty scores: low volume is fine for a directory (Step 1), and a table of numbers is how a member loses a week. Three candidates is the limit for one sitting. A candidate that fails is told with the check it failed, in one line; the member may still say "build it anyway", and then it is built without further comment. If all three fail and the member picks none, send them back to Step 1 with which check each failed.
- Without DataForSEO there is nothing to measure. Ask the three yes or no questions, point at the seven checks in Step 1, and take the member's decision.

A wrong pick costs an afternoon: the Gate 2 report shows other trades and missing websites before any writing is paid for. Say that when a member hesitates. It is the reason not to deliberate.

## The eight questions

**1. Vertical.**
> Which service is this directory for? One Maps category, the way Google names it, for example "roofing contractor" or "swimming pool contractor". If you do not have one yet, say so.
Why: the whole build (cleaning, attributes, copy) hangs on one category. Record the category label and, if DataForSEO is connected, the category id (`--find-category <word>` lists them, free). A member who answers with a vertical goes straight to question 2; "not yet" or "check it" opens the vertical check above, and the intake resumes at question 2 or 3 once a vertical stands. When the check supplied the state and the intake resumes at question 3, run the estimate for the chosen vertical before question 8 so its cost is in hand.

**2. State.**
> Which state? One state per directory, for example "Texas".
Why: one niche, one state is the rule ([[directory-overview]]). Record name and two-letter code. With DataForSEO connected, run the estimate now and keep it for question 8; speak about it only if it prints a `VERTICAL FLAG` (the vertical check above).

**3. Domain.**
> Do you already own the domain? If yes, type it. If not, the shape we build is the category domain, for example texasroofingcontractors.com or [state][niche].com, registered at Cloudflare Registrar (Step 2 of the course). Either way, also type the brand name the site will show, which is the words of the domain with spaces and capitals, for example "Texas Roofing Contractors".
Why: the domain is the brand and the site title. **Category shape is the recommendation.** Do not offer other shapes; if the member asks about "best of" naming, the note is in [[publisher-entity]]. The brand name goes into `site.json` at Gate 5 (name, title, header, schema), so it is needed even when the domain is not registered yet; record the domain as "to register" and the brand name as given. Never propose the brand name; if the member gives only a domain shape, ask for the words once.

**4. Owned microsites.**
> Do you already have microsites or a business of your own in this niche and state? If yes, list their phone numbers, nothing else. If not, say none.
Why: those rows are flagged `owned` and listed like any other business ([[footprint-rules]]). Phone numbers are the only identifier the pipeline needs.

**5. Publisher name.**
> Type the name that fronts the directory as its publisher. Your own name, or a persona you will run consistently everywhere: same name, photo, bio and contact for years.
Why: a directory is a magazine and a magazine has a publisher ([[publisher-entity]]). Never suggest a name.

**6. Publisher details.**
> For that publisher: their own website if there is one (or none), a 60 to 120 word bio, the file name of a photo you will drop in `public/images/`, and the contact email and phone for the Contact page.
Why: the About page, `Person` schema and the `sameAs` hierarchy are built from this at Gate 5. Take the four items in one answer; ask one follow-up for anything missing. A short bio, a missing photo or a missing phone does not block approval of the scope file: record what was given, list the gap under "Open before Gate 5" in `01-scope.md`, and Gate 5 asks for it before the About page is built.

**7. The look.**
> The directory comes with a finished look, the one in the reference site in this folder. Say "show me" and I open it in your browser. Reply "default" to use it. If there is a website whose look you would rather borrow, any industry, paste one or two URLs instead; we borrow the styling (colors, type, cards, buttons), never the content, images or logo.
Why: the [[master-template]] is the default and the fallback (Shawn, 2026-10-01). On "show me", start `python3 templates/master-reference/view_reference_site.py` in the background (it picks a free port, opens the browser and prints the address), tell the member the address, and ask the question again; the member can also double-click `view-reference-site.command` (Mac) or `view-reference-site.bat` (Windows) in `templates/master-reference/`. "Default", "none", "I don't have one" and no answer all mean the master template's tokens as shipped: record "master template look" in the scope file and go on, without offering anything else. A URL is a design pointer and Gate 4 turns it into tokens ([[design-seed]]). The seven sites in [[reference-directories]] are shown only when the member asks to see other looks or examples; never list them unasked. If a named site blocks scripts (Checkatrade and Pickleheads answer 403 to curl from a Mac, checked 2026-09-29), say that Gate 4 derives its tokens from the member's screenshots, not from a fetch, and ask for two or three screenshots (home, a list page, a detail page) pasted into the chat when Gate 4 starts. If none arrive, Gate 4 keeps the master template's tokens and records that in `04-plan.md` ([[design-seed]]).

**8. Listings source.**
> Where do the listings come from? Two ways, both taught:
> 1. **DataForSEO** (default): I run `scripts/fetch_dataforseo.py` with the API login saved on this computer, quote the exact cost first (a whole state is usually a few dollars), and the CSV lands in `input/`. It is a database refreshed on DataForSEO's schedule, not a same-day scrape.
> 2. **Outscraper export**: you run the scrape yourself (Step 3 of the course) and drop the CSV in `input/listings-raw.csv`.
> Reply 1 or 2.
Why: Gate 2 needs a raw CSV. There is no third option and no demo data path: a build starts from real listings or waits.

When the login check before question 1 said yes, do not ask this as an open question: show the estimate already in hand ("2,032 businesses, about $0.77") and ask for a yes to pull, with the Outscraper export as the other answer.

**When the member picks DataForSEO and no login is saved, the Terminal is the instruction, first and only** (first live run, 2026-10-01: a claude.ai or desktop-app connector was connected and gave the script nothing; the by-hand command then failed because the Terminal could not find `claude`, and again with a 401 because the password was not in single quotes). Say, in one message:
> The pull needs your DataForSEO API login saved on this computer once. Open the Terminal app (not this chat) and paste this line:
> `python3 "<absolute path to this folder>/scripts/connect_dataforseo.py"` (on Windows the line starts with `python`, not `python3`)
> It asks for the API login and the API password from app.dataforseo.com/api-access (the API password is not the one you sign in with), checks them, and saves them in Claude Code's settings. Reply "done" when it says saved.
Print the line with the real absolute path so it can be pasted from any Terminal window. The helper finds `claude` wherever it is installed, takes the values without a shell so no quoting can break them, and tests the login before it saves, so a wrong password is reported there and nothing is stored. On "done", run `connect_dataforseo.py --check`, then the estimate. Do not offer the connector as a way to do the pull, do not ask for the login in the chat, and do not run the helper yourself (it waits for typed input). If the member would rather type the lesson's command, it is in the Gear Up lesson "Connect DataForSEO to Claude" with single quotes around both values; `~/.local/bin/claude` replaces `claude` when the Terminal cannot find it. If it keeps failing, the Outscraper export is the way on.

## What 01-scope.md holds

Slug, vertical (label, category id), state (name, code), domain (owned or to register, category shape) and the brand name, owned phone numbers, publisher (name, site, bio, photo file, contact), the look ("master template look", or the design pointers with a note when one blocks scripts), listings source and, when DataForSEO was used, the estimate line or, when the pull already ran, the cost line from `input/listings-raw-report.md`. An "Open before Gate 5" list for anything from question 6 that is missing or short. If the vertical check ran, one line: which candidates were checked and the result of each, or the flag and the member's "continue". Nothing the member did not say.

## See also
[[directory-overview]] · [[design-seed]] · [[reference-directories]] · [[publisher-entity]] · [[footprint-rules]] · [[outscraper-columns]]
