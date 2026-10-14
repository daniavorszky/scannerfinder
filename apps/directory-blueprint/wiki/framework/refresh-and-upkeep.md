---
title: Refresh and Upkeep: how a static directory stays alive
type: framework
status: draft
updated: 2026-09-17
---

# Refresh and Upkeep: how a static directory stays alive

A directory is more work than a microsite after launch: owners want to edit their listing and spam wants in. The rules below come from operators who run mature directories. The static rebuild answers both without logins or a CMS. Listing data changes when a claim, a sale or a correction changes it, not on a calendar.

## No logins. One door.
- Members do not give listing owners accounts in v1. Operators of mature WordPress directories removed all front-end access because spam signups outran real ones.
- The only way in is the claim form (`templates/claim-form.html`). Every submission is checked before anything changes: is it a real local business (not a lead-gen site, not a directory, not a franchise aggregator), does the email domain match the website, does the phone match the Maps listing. Then the CSV is edited and the site rebuilt.
- Every self-submission is a warm lead. Call it the same day: "I saw you submitted, welcome." Then the featured pitch.

## Rebuild on change
- A claimed listing, a sold slot, a corrected phone number, a new city: edit the CSV, re-run Gate 5, redeploy. Never hand-edit generated pages.
- Keep the CSV in the repo. The git history is the audit trail of who was added, featured or removed and when.
- Phase 2 only: a git-based CMS on top of the Astro repo, or GoHighLevel webhooks on the forms, if a VA needs to work the directory without touching the CSV. Konstantin's route on the call. Not in v1.

## Money pages follow the general refresh advice
The 90-day refresh (swap images, bump `dateModified`, keep facts out of accordions, push fan-out queries) is general SEO advice for money pages, not a directory listing rule (Shawn, 2026-09-17). It applies to the directory the way it applies to any site: the home page, the state hub and the city pages are money pages, so treat them as such. Listing pages and the listing data are not on a refresh calendar. A re-pull of the state is a member's choice when the data has aged, run as Gates 2 and 3 again with the diff reviewed before rebuild.

What Gate 5 does regardless: sets `datePublished` on first build and `dateModified` on every rebuild, and keeps FAQs, hours and attributes as visible text.

## Corrections and removals
A public directory publishes other people's businesses. Ship a correction and removal route on the contact page, answer within a week, and honor removal requests by clearing the row and rebuilding. Add a one-line disclaimer on listing pages: listings are compiled from public sources and are not endorsements; verify licensing before hiring.

## See also
[[monetization-slots]] · [[launch-lean]] · [[schema]]
