---
title: Publisher Entity: a real person owns the directory
type: framework
status: draft
updated: 2026-09-30
---

# Publisher Entity: a real person owns the directory

A directory is a magazine about a niche in a state, and a magazine has a publisher. Operators who do this well put a real person on every directory, with videos, and Google and ChatGPT know who owns what. The Blueprint makes that the default rather than a nice-to-have, because the people who look the directory up are the businesses the member is about to call.

## What Gate 1 collects
- The name of the person who fronts the directory (the member, a partner, or a persona the member is prepared to operate as a real identity: consistent name, photo, bio, contact).
- The person's own website, if any. This is the top of the schema hierarchy; every asset they own points back to it with `sameAs`.
- A short bio (60 to 120 words), a photo, and optionally a video for the About page.
- The contact email and phone that appear on Contact. Cold-email domains forward to the real domain.

## What Gate 5 builds from it
- **About page** with the person front and center: photo, bio, why this directory exists, how listings are vetted, the correction and removal route ([[refresh-and-upkeep]]). Not a generic "about us."
- **Schema:** the directory's `Organization` carries `founder` (a `Person` with `name`, `url` pointing at their personal site, `sameAs` for their profiles) and `publisher`. The About page emits the `Person`. See [[schema]].
- **Byline on resource pages:** every resource page names the person as author ([[on-page-rules]]). The buyer's guide on the home page has no byline (the locked [[master-template]]); there the person is named in the vetting band ("Published by [Name]", linked to About), in the footer line and on About.
- **Footer:** "[Brand] is published by [Name]" with a link to About.

## Rules
- Out-of-state ownership is not a problem. A Florida directory owned by someone in Ohio is a magazine, and readers expect magazines to have publishers elsewhere. What is a problem is anonymity.
- The person must be findable and consistent across the member's assets. Same name, same photo, same bio shape on the personal site, the directory and the microsites that carry an author.
- If a persona is used instead of a real person, it is operated as a real identity for years, not a stock photo and a first name. If the member is not prepared to do that, they use their own name.
- Videos are optional and worth it: a 60-second "why I built this" on About is the strongest trust signal for a cold-called business owner.

## Naming
The Blueprint recommends the **category shape**, `[state][niche].com`, and Gate 1 offers only that ([[gate-1-intake]]). For the record: some operators name theirs "Best of [place]" because people type "best roofers near me" and it reads as a publication. That is their shape, not the taught one. Mention it only if a member asks; do not present it as an option.

## See also
[[authority-and-links]] · [[schema]] · [[design-seed]]
