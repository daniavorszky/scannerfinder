---
title: Design Seed: keep the directory from looking Claude-coded
type: framework
status: current
updated: 2026-10-01
---

# Design Seed: keep the directory from looking Claude-coded

Every AI has a feel of how it builds. A hundred member directories that share one look are a footprint and a trust problem. So the member supplies the variable.

## Gate 1 offers the default look, and takes design pointers from a member who has them
At Scope, question 7 offers the master template's look as it ships (the reference site in `templates/master-reference/`) and takes one or two websites from a member who would rather borrow another look (any industry). Those are **design pointers**: they lend a look, never a structure ([[master-template]]). Record "master template look" or the URLs in `01-scope.md`. When there are pointers, Gate 4 derives from them and writes into `04-plan.md`:
- a palette (background, surface, text, one accent, the action color for buttons, the band color for the hero and footer, the hero accent) as CSS variables, starting from the master template's tokens and recording every change
- type pairing (one heading face, one body face, system stacks allowed)
- card style (flat or shadowed, radius), button style, spacing scale
- header and footer pattern

Borrow the styling, never the content, images or logo. The plan states the derived tokens; the member approves them before Gate 5 builds.

**When a pointer cannot be read by a script** (Checkatrade and Pickleheads answer 403 to a fetch, checked 2026-09-29 and again on the 2026-09-30 dry run; a web search returns what a site is, not how it looks): Gate 4 asks the member for two or three screenshots of the pointer pasted into the chat (home, a list page, a detail page) and derives the tokens from those, measuring contrast on the screenshot's colors like any other pointer. If no screenshots arrive, Gate 4 keeps the master template's tokens, records in `04-plan.md` that the pointer could not be read and that the look is the template's, and moves on; the member can supply screenshots later and rerun the token step.

## The default and the fallback: the master template's look (Shawn, 2026-10-01)
A member with no inspired site gets the master template's look as shipped: the tokens in `templates/astro/src/data/site.json`, which are the look of the reference site in `templates/master-reference/site/`. "Default", "none" and "I don't have one" at question 7 all mean this, and Gate 4 records "master template look, no changes" in `04-plan.md`. Nothing else is offered. The first live run of the zip (2026-10-01) answered "I don't have one" with a table of seven other directories; the member wanted the default and had to say so twice. The reference site is the first and heaviest reference in every build, and the same holds when a pointer cannot be read or the member's screenshots never arrive.

The seven sites in [[reference-directories]] (Potty Directory, Liquidation Map, Discover Plasma, Expertise.com, ThreeBestRated, Checkatrade, Pickleheads) are shown only when a member asks to see other looks or examples. Then: one line each, the member picks one or two, never pick for them, and the niche of an example is never presented as a niche to copy. Gate 4 derives the tokens from the pick like any other pointer. They also remain a comparison set for what a good state page, city page and listing card carry, after the reference site.

## Eyebrows and icons: allowed when borrowed, banned when generic (Shawn, 2026-09-29)
Call 54 named "the small eyebrow text above every title" and icon feature rows as tells, and the first draft of this page banned both. Shawn's ruling on 2026-09-29, after a Gate 4 plan refused to borrow an inspired site's orange uppercase eyebrow and its four icon action cards: **eyebrows (the sub or top headline above a heading) and icons are wanted, as long as they do not look AI-made.** So:
- **Borrow them only from the inspired site.** If the inspired site has an eyebrow line, Gate 4 records its treatment in `design.eyebrows` (case, size, color, where it appears) and Gate 5 uses it in those places. If the inspired site has icons, `design.icons` records the style (filled or outline, one color, size) and the home action row uses that style. If the inspired site has neither, the directory has neither (`none`).
- **The AI version is the tell, not the element.** AI-made: the same generic label above every heading ("Our Services", "Why Choose Us", "Featured"), a three-column row of stock outline icons with a title and a sentence that says nothing, icons as decoration next to headings. Human-made: one eyebrow where the inspired site puts one, saying something specific to this directory ("Find trusted garage door professionals in your area"); an action row where every card is a real destination on the site (find by city, get a quote, read the guide, claim a listing) with an icon that names the action, in one consistent style.
- **Every eyebrow and every card must be specific.** Test: could the line sit on any other directory unchanged? Then cut it. No eyebrow above the H2s of the city page listing blocks, the FAQ or the CTA band unless the inspired site does exactly that.
- **Testimonials stay out.** A directory has no clients to quote at launch, and invented quotes are a trust and legal problem. (Not part of Shawn's ruling; unchanged from the first draft.)
- In the skeleton: the master template ships no eyebrow and no action row (the pilot's design review removed both). When a pointer has one, Gate 4 writes `design.eyebrows` or `design.icons` with the treatment, drafts the line or the cards in `04-plan.md` for approval, and Gate 5 adds them as a page pattern borrowed from the pointer ([[master-template]], "What a design pointer may change"), without removing a section.

## The base look is the master template (2026-09-30)
On 2026-09-29 a screenshot from the video (a pool builder's home page: top bar, pill eyebrow, two-line uppercase H1, two buttons, check-mark row) was translated into the skeleton as its base look. On 2026-09-30, after twelve rounds of design review on the Florida pool builders pilot, Shawn locked the pilot's result as the [[master-template]] and it replaced that base look. What the skeleton renders before Gate 4 touches anything is now the master template: navy header and hero, the search pill, three promises, the quiet stat row, amber buttons with navy text (7.6 to 1), Roboto Slab 800 headings and Roboto body, 8px cards. The screenshot's top bar, pill eyebrow, hero buttons and proof row are gone from the skeleton; the lesson that survived is the translation rule (every element a directory borrows must be something it can honestly say from the data) and the contrast rule (dark text on a bright action color, never white).

**What the base look is.** The default, and a finished one: a member who names no site ships it unchanged (Shawn, 2026-10-01). A member who does name a site gets colors and type derived from it at Gate 4, within the contrast rule, and `04-plan.md` records what changed from the template's tokens. Many directories in navy and amber share a look; that is the accepted cost of a default that needs no decision, and a member can name a site later and rerun the token step. The structure never changes either way ([[master-template]], "What a design pointer may not change").

## The other tells to design out (named on the call while reviewing a fresh Blueprint site)
- No colored card borders. Separate cards with surface color, shadow or spacing.
- Contrast: every button and link passes WCAG AA against its background. Check the call-to-action band in particular.
- A real logo (member supplied, or a wordmark in the heading face) and real imagery where imagery is used. No placeholder gradients.
- The home page's job is still cities, featured businesses and the buyer's guide; an action row sits under the hero and points into those, it does not replace them.
- Cards show data (rating, review count, attributes, phone). A card with nothing but a name and a button reads as generated.

## What the pilot added (Florida pool builders, 2026-09-29)
- **Two looks are what AI tools produce by default, and an inspired site can carry either.** Cream paper with serif headings and a terracotta accent, and Inter with Tailwind blue. A member who names a site with one of those looks gets a directory that reads as AI-built anyway. Say so at Gate 4 and offer another direction. The skeleton's own starting tokens are the master template's navy and amber, which is neither of these; they ship unchanged when the member takes the default.
- **Measure the inspired site's contrast before borrowing its colors.** Six of the eight sites named on the pilot fail WCAG AA somewhere as built, usually white text on a bright accent. Borrow the hue, fix the pairing, and record the change in `04-plan.md`.
- **Eight sites is not a seed.** When a member names more than two, read them all, pick the two or three that can carry a whole directory, present them as directions, and take page patterns (counts in the first line, city links as the way in, a vetting section) from the rest. Patterns are structure, not styling.
- **Commercial fonts cannot be borrowed.** Check that the pair is openly licensed, and self-host it (`src/styles/fonts.css`).

## What every directory shares anyway
The [[master-template]] is the structure: page set, URLs, nav, every section in its order, the search, the featured band, the listing layout. It weighs heaviest in every build. An inspired site is a design pointer for the look (palette, type, cards, imagery) and at most a page pattern or two; it never changes the structure (locked by Shawn, 2026-09-30).

## See also
[[page-sections]] · [[page-types]] · [[footprint-rules]] · [[reference-directories]]
