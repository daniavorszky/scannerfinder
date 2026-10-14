---
title: Authority and Links: how the directory gets strong enough to matter
type: framework
status: draft
updated: 2026-09-28
---

# Authority and Links: how the directory gets strong enough to matter

The directory exists partly to pass strength down to the member's microsites and clients, so it has to earn some first. Two positions, both true:

1. **The directory-sized hole:** in some niche and state combinations there is a directory-sized hole. Build the complete, enriched, well-structured directory and it ranks without links, the way microsites do. This is the Blueprint's default assumption and why Gates 2 to 6 are what they are.
2. **The SEO project:** if you want the directory to carry weight, treat it as a regular SEO project. You pay for links or you pay someone to do the outreach. The DA/DR number matters less than it did; hyperlocal relevance matters more.

The Blueprint builds for position 1 and ships the hooks for position 2. Nothing below is a Gate. It is the work after launch, in the order operators do it.

## The five link sources the site is built to support

| Source | What the build ships | The work |
|---|---|---|
| **Badges** | An HTML embed per premium and best-of listing (`templates/featured-tiers.md`), linking to the business's listing page | Send the snippet, not a JPEG: "send this to your developer or we'll do it for you." Offer to install it. Word it as accreditation: "Verified [niche] on [Brand]." |
| **Press releases** | Best-of positions (`best_of_rank`) and a listing page per business | One release per best-of sale, about the business. Its three links: the business's home page, its listing page, and the city best-of page. The $100 floor on a best-of sale pays for the release (AB Newswire, about $10). |
| **Resource pages** | Optional `/resources/[slug]/` pages ([[site-architecture]], [[page-types]]) | Write the most in-depth page on one topic in one place (hotlines, state rules, what realtors say, local stats). Then ask the Chamber of Commerce, city sites and associations to update their link to it. "You just need something different." Written with the seo-content-engine skill when DataForSEO is connected, by hand otherwise, and linted either way ([[copy-gate]]). |
| **Local content plus creator outreach** | The city page's local copy block and the resource pages | Research the city on YouTube (realtor tours, neighborhood videos), write from the transcript like a local, then tell the creator: "we just published an article, would you like to comment?" |
| **The national month** | Nothing to build | Every month is national something month. Pitch realtors a piece for their site on that hook and get the link back. Manual, one real email at a time. |

Plus one side effect: when the member does SEO for a client who is listed, the client's listing page is one of the pages they build links to. Client work strengthens the directory.

## Rules
- Links go to listing pages, city pages and resource pages, not only the home page. A directory is many small entry points.
- Outreach is one real email to one real person. No templated blasts; the directory is also the member's client-getter and its reputation is theirs.
- No link schemes between the member's own microsites and the directory ([[footprint-rules]] still holds). Owned sites are listed like any other business and buy tiers at the public price if they want a followed link.
- Track what was placed where in the repo (a `links.md` in `output/<slug>/`), so a rebuild never drops a page someone linked to. Never change a URL that has an inbound link.

## See also
[[publisher-entity]] · [[monetization-slots]] · [[launch-lean]]
