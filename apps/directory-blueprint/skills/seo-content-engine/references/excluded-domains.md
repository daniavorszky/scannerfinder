# Excluded Domains

Stage 1 filters the SERP results before sending anything to Instant Pages. Filtering
to `type == "organic"` removes the ads and SERP widgets, but organic results can
still include pages that aren't article-style content you can learn structure from —
forums, encyclopedias, video and social pages, storefronts. This list removes those.

Apply this **between** the SERP call and the Instant Pages call: decide from the
`domain`, `url`, and `title` the SERP already returned, so excluded pages never cost
an Instant Pages call.

## Hard excludes — drop outright, by domain

These almost never rank as the kind of standalone article we analyze. Drop any
result whose domain matches (including subdomains):

reddit.com, quora.com, pinterest.com, youtube.com, facebook.com, instagram.com,
tiktok.com, x.com, twitter.com, threads.net, amazon.com, ebay.com, etsy.com,
wikipedia.org, wikihow.com, yelp.com, glassdoor.com, indeed.com, tripadvisor.com,
apple.com/app-store, play.google.com

## Hard excludes — drop by URL pattern, any domain

A page can be junk even on an otherwise-fine domain. Drop any URL whose path
contains: `/forum/`, `/forums/`, `/thread/`, `/threads/`, `/community/`,
`/discussion/`, `/discussions/`, `/comments/`, `/profile/`, `/user/`, `/users/`,
`/author/`, `/login`, `/signup`.

(Note: `/category/`, `/tag/` and similar are NOT excluded — real blogs often sit
under those paths. Whether a category-style page is a real article is caught by the
article check below, not a blunt URL ban.)

## Article check — is this actually an article?

Surviving the exclusions isn't enough; a page could be documentation, a pricing or
login page, an app listing, or a bare category index. Filter these out, invisibly to
the user, without any extra API call:

- **Before Instant Pages (from title + URL):** drop obvious non-articles — a
  `/docs/`, `/pricing`, `/download`, or app-store URL, or a title like "Login",
  "Pricing — X", "Sign up".
- **After Instant Pages (from data already fetched):** drop anything that comes back
  with a very low `content.plain_text_word_count` or no real heading structure — that
  isn't an article worth learning from.

Keep the survivors in Google's rank order (the checks only remove, never re-sort),
and present the top ~10. The user sees only the final clean set, not this filtering.

## Soft excludes — judge, don't auto-drop

These domains host both real articles and non-articles, so don't ban them outright.
Decide from the URL + title (before fetching): keep a genuine article, drop a
profile/repo/listing page.

- **medium.com** — keep a real article; drop a bare user profile or tag page.
- **substack.com** — keep a genuine post; drop a subscribe/landing page.
- **github.com** — keep a docs or blog page; drop a code repo or profile.
- **linkedin.com** — keep a genuine long-form article (`/pulse/`); drop a profile
  or company page.

## When a hard-excluded page is genuinely the best reference

Occasionally the query itself is about one of these (e.g. "best subreddits for
marketing"), so a Reddit or YouTube result really is a key reference. In that case:
mention it to the user, summarize its relevant points by hand, and do NOT include it
in the Instant Pages batch or the word-count average — it isn't a comparable article.

## If filtering leaves too few

The goal is a clean set of about 10+ ranking articles. If exclusions leave fewer
than that on a junk-heavy SERP, say so plainly and analyze what's there — don't pad
the set with excluded junk to hit a number.
