# Directory Blueprint for Claude Code

This folder turns a Google Maps export into a ranked, monetizable local directory: one niche, one state, built as a static Astro site and deployed to Cloudflare Pages. You point Claude Code at it and it builds to spec instead of guessing. It is the sibling of the Microsite Blueprint and works the same way.

## Before you start
- Claude Code installed and working (`claude` runs in your terminal).
- Node.js 20 or newer (`node -v`). Needed for the build in Gate 5. Get it at nodejs.org if the command is missing.
- Your vertical and your state (Step 1 of the course). If you have them, Claude builds them and does not second-guess you. If you are still deciding, name up to three services and Claude checks them against the Step 1 criteria with DataForSEO, about five cents each; it will not pick one out of thin air.
- Your listings, one of two ways: **DataForSEO** (your API login saved once on this computer, from the Terminal, see "Connect DataForSEO" below; a whole state is usually a few dollars and Claude quotes the cost before pulling), or an **Outscraper export** of the exact category in your state saved as `input/listings-raw.csv`. Same-day test on one category and state: DataForSEO found 95 percent of the businesses the Outscraper scrape found, with the same phone and website on 99 percent of them, for $0.89 against about $24, and it includes emails. It does not know when a business closes, so the cleaning step drops anything not updated in a year.
- A domain for the directory (or the intent to register the category name, like [state][niche].com).
- Optional: one or two websites whose look you like (any industry). Without them the directory gets the finished default look, the one in the reference site (ask Claude to "show me the reference site", or double-click `view-reference-site.command` on a Mac or `view-reference-site.bat` on Windows in `templates/master-reference/`).
- Who fronts the directory as publisher: your own name or a persona you will run consistently, their website if any, a short bio and a photo. A directory is a magazine, and a magazine has a publisher.
- Optional, for after launch: the bundled seo-content-engine skill uses the same DataForSEO connection to research and write resource pages.

## Connect DataForSEO (once, in the Terminal)
1. In app.dataforseo.com open **API Access**. You need the API login (your email) and the API password, which is not the password you sign in with. Reset API password emails you a new one.
2. Open the Terminal app (on Windows: PowerShell), type `python3 ` with the space after it (on Windows: `python `), drag `connect_dataforseo.py` from this folder's `scripts` folder into the window, and press Return.
3. Type the login, paste the password (it stays hidden), press Return. It checks the login with DataForSEO and saves it in Claude Code's own settings. Nothing is written into this folder.

That is the whole setup. The DataForSEO connector in claude.ai or the Claude desktop app gives chats the data tools, but it stores no login on the computer, so the listings pull cannot use it. The same step typed by hand is in the Gear Up lesson "Connect DataForSEO to Claude".

## Run it
1. Unzip this folder anywhere. Do not rename the files inside.
2. Either connect DataForSEO (above) or put your Outscraper export in `input/` as `listings-raw.csv`.
3. Open a terminal in this folder and run `claude`.
4. Type: `Read CLAUDE.md and run Gate 1.`
5. Answer the eight scope questions one at a time, approve the scope file, then say `Run Gate 2` and so on through Gate 6. Claude stops after every gate and waits for you. Everything it produces lands in `output/<your-directory>/`.

What the gates do, in one line each:
1. **Scope**: vertical, state, domain, your own microsites if any, the publisher, the look (the default, or a site you name), the listings source. With DataForSEO connected, Claude sizes your category in your state as soon as you name them (about five cents) and speaks up only if the numbers are clearly too thin for a directory. The pull happens here, after you approve the cost.
2. **Clean**: the raw CSV becomes the real businesses with reviews (a loose Outscraper export drops to 5 to 6 percent, a targeted one keeps about a fifth, a DataForSEO pull keeps most rows). You read the report, which also shows which trades got in under your category.
3. **Enrich**: Claude writes the attribute list for your vertical with you, then every listing gets those attributes (true / false / not enough info) and a plain description from the data. If your export has no review text, Claude reads each business's own website, which costs nothing, then tells you what the writing will cost before it starts. The writing runs in batches, each one checked by a script before it counts; `scripts/run_batches.py` can run them from a terminal, a few at a time.
4. **Plan**: which cities get a page, which listings are left out and why, what enters the sitemap at launch, the look (the default, or the design tokens taken from your inspired site). The plan ends with a short table of decisions, each with a recommendation, so one reply approves them.
5. **Build**: the Astro site is generated from `templates/astro/` and your data, every block of copy passes the copy gate, `npm run build` passes. You get a build report that lists what is still missing before launch.
6. **Launch lean**: strong pages in the sitemap (every city and town page among them), thin profiles noindexed, deploy to Cloudflare Pages, dripfeed the sitemap.

## Looking at the site before it is live
In `output/<your-directory>/site/`, double-click `preview-site.command` on a Mac or `preview-site.bat` on Windows. Your browser opens on the site, served from your own computer exactly as it will be deployed. Close the window to stop it. From a terminal the same thing is `npm run preview -- --open`.

On a Mac, the first time, macOS may refuse to open the file because it came from a download. Right-click it, choose Open, and confirm; on macOS 15 and later, open System Settings, Privacy & Security, and click Open Anyway.

Do not open `site/dist/index.html` by double-clicking it. That folder is built for the live domain, so opened as a file it shows no styling and its links lead nowhere. Nothing is broken.

To send someone a folder they can open without installing anything, ask Claude for a preview copy, or run `python3 scripts/make_local_preview.py output/<your-directory>/site/dist output/<your-directory>/preview`. The copy goes stale after a rebuild. Never upload it: the folder to deploy is `site/dist`.

## What it costs in Claude usage
The two writing steps are the expensive ones. Measured on the first real build (1,848 listings, 134 city pages, run as subagents on Sonnet):

| Step | Per unit | On that build |
|---|---|---|
| Gate 3, attributes and descriptions | about 4,000 tokens per listing | 7 million tokens |
| Gate 5, city copy | about 18,000 tokens per city page | 2.4 million tokens |

It runs on your Claude subscription, so there is no API bill, but it counts against your usage. Claude states the projected figure and waits for your approval before each step. The batch runner (`python3 scripts/run_batches.py enrich --slug <your-slug>` and `... city-copy --slug <your-slug> --niche "<your niche>"`) starts one Claude Code run per batch on the same subscription and reruns a batch that fails its check; `--status` shows where things stand and `--dry-run` shows what it would start.

## Have these ready before Gate 5
The site builds without them, but it cannot launch without them:
- the domain registered, and an address on it for the contact page and the claim form (a mailbox, or the mail worker after launch)
- your bio approved, a photo, and links to your profiles
- the Stripe Payment Links for the tiers you want to sell at launch

## After launch
- A sold slot, a claimed listing, a corrected phone number: edit the CSV, `Run Gate 5`, redeploy. Never hand-edit generated pages.
- Sell by hand: send the Stripe Payment Link, flip the column (`featured`, `premium`, `best_of_rank`, `claimed`), rebuild. Tiers and the badge snippet are in `templates/featured-tiers.md`.
- How the directory earns links and clients after launch is in `wiki/framework/authority-and-links.md`.

## After launch, optional: a real hello@ inbox with Claude triage
The mail worker (Extra lesson "Automating Listing Requests") gives the directory a working hello@yourdomain.com without a mailbox provider: every email and claim form gets an acknowledgement within a minute, Claude triages it (what kind of request, which listing, whether the email domain matches the website, what is missing) and you get a review email with a draft and a Send or Ignore page. Nothing goes to a business until you press Send. It runs on Cloudflare's Workers Paid plan ($5 a month) plus cents of Claude API usage, needs the site live on Cloudflare Pages with the domain's DNS in the same account, and takes about an hour. In Claude Code: `Give me the Terminal commands to save the mail keys.` (one key, saved from your own Terminal), then `Deploy the mail worker for my directory. The review emails go to <your address>.`, then `Wire the claim form to the mail worker and deploy the site.` The two dashboard steps (Workers Paid and Email Sending on the root domain before, the Email Routing rule after) are in the lesson and in `templates/worker/README.md`.

## What is in here
```
CLAUDE.md       the rules Claude follows and the six gates
README.md       this page
input/          listings-raw.csv (DataForSEO pull or Outscraper export)
output/         one folder per directory build
scripts/        the helpers Claude runs: the DataForSEO fetch and the vertical check (Gate 1), cleaning (Gate 2), website reading and the enrichment checker (Gate 3), city copy checker and the copy gate (Gate 5), the mail worker setup and its queue (after launch)
skills/         seo-content-engine, the Academy's SEO writing skill (lints all copy, writes resource pages)
templates/      the Astro project Gate 5 copies, the reference site (the finished example and the default look), the claim form, the tier sheet, the mail worker
wiki/           the framework: architecture, page types, SEO, schema, monetization, upkeep
```

Rank Expand Academy, 2026. Questions go in the community, in the directory thread.
