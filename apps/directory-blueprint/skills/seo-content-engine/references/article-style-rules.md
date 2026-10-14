# Article Style Rules

How every article must be written — voice, humanizer, keyword handling, structure,
and formatting. This is the floor: it holds even when a brand voice is active (voice
changes rhythm and register, never these rules). Where a rule is about *what to
build* (section order, per-format structure), that lives in
`references/article-format-guidelines.md` (what to build) and `references/article-template-guidelines.md` (how to write each section); this file is the writing rules.

## Hard-ban list (linter-enforced)

A short set of pure AI tells must never appear. They live in
`references/forbidden_words.txt`; `scripts/lint_article.py` reads that file and fails
the Fact Check + Quality Audit gate (Stage 6) if any show up. At time of writing:
the words *delve*, *tapestry*, *kaleidoscope*, *linchpin*, *underscore*, and filler
phrases like "in conclusion", "it's worth noting", "in today's fast-paced world",
"unlock the potential", "navigating the landscape", "not only... but also", "shed
light on". Defer to the txt file if this summary and the file differ.

Everything below the humanizer heading is the larger *avoid-and-rewrite* set. It is
NOT hard-failed by the linter — avoid it while drafting (Stage 5) and reach for the
plainer word. It's guidance, because many of these are the right word once in a while.

---

## Humanizer — sound like a person

AI prose gives itself away with a small set of habits: dressy filler words, padded
transitions, hedging, buzzwords, and a few structural tics. Cut them and the writing
reads human. The single test: could a reader believe a chatbot produced this from a
one-line prompt? If yes, it isn't done.

Each group below pairs the words to avoid with plainer swaps. Reach for the swap —
but treat the swaps as a menu, not a find-and-replace. Don't trade one overused word
for another used ten times over; vary your wording so no single substitute becomes
its own tell. If a flagged word is genuinely the most exact choice in a spot, keep
it; that's rare, and the sentence usually reads better reworked.

### Alternatives/Substitutions

The word swaps below are grouped by the kind of tell they fix — dressed-up words,
padded transitions, hedging, buzzwords, corporate filler, and product-writing terms.
Each line is "avoid → reach for instead."

#### Dressed-up verbs and nouns
- delve into → look at, dig into *(also hard-banned)*
- underscore → point to, show *(also hard-banned)*
- leverage → use, tap
- utilize → use
- facilitate → help, make easier
- foster → build, grow, encourage
- harness → put to work, use
- streamline → simplify, tighten
- bolster → back, strengthen
- illuminate → make clear, show
- pivotal → central, key moment
- realm → space, field

#### Padded transitions
- that being said → still, even so
- at its core → basically
- to put it simply → put plainly
- a key takeaway is → the point is
- from a broader perspective → stepping back
- in order to → to
- with regards to / in terms of → about, for

#### Hedging that weakens the point
- generally speaking → usually
- tends to → often
- arguably → drop it, or make the claim outright
- to some extent → partly
- broadly speaking → overall
Better still: cut the hedge and state something specific. A number or a named source
beats a soft qualifier every time.

#### Buzzwords (usually delete, don't swap)
- revolutionary / revolutionize → name the actual change
- innovative → show what's new instead of labeling it
- cutting-edge / state-of-the-art → advanced, current, or cut
- game-changing → major, or cut
- transformative → say what it changes
- a plethora of / a myriad of → many, plenty
- take it to the next level → name the specific gain

#### Corporate filler
- aforementioned → that, the one above
- commence → start
- subsequently → then, after
- paradigm shift → big shift
- best practices → what works, proven methods
- holistic → whole, complete
- actionable insights → useful takeaways

#### Product-writing swaps (these come up a lot)
- "key features" → what it does well, main features
- "seamless integration" → works with, plugs into
- "comprehensive" → full, complete, end-to-end
- "robust" → solid, reliable, strong
- "user-friendly" → easy to use, simple

---

## Structure the writing to be lifted

- **Answer first.** Lead with the actual answer — the pick, the verdict, the
  definition — in the opening lines, not after a wind-up. Search engines and AI
  answer tools pull the first clear statement, and readers who skim want it up top.
  Put the conclusion first, then support it underneath.
- **Self-contained sections.** Write each section so it makes sense on its own. Don't
  lean on "as covered above" or "as we saw earlier" — a reader (or an AI engine)
  lifting one section out should still get a complete thought.

## Structural tics to avoid

- **Em dashes.** They're a heavy tell. Default to commas, colons, periods, or
  parentheses. One or two across a whole article is tolerable if a sentence truly
  needs it; more than that reads as machine-written. (Number-range dashes like
  "$10–15" are fine.)
- **Sentence-opening connectors.** Don't begin a sentence with "Furthermore,"
  "Moreover," "Additionally," "In addition," or "On top of that." Start fresh, or
  bridge with something concrete like "That's because…".
- **Rule-of-three padding.** Skip the reflexive triple ("cheaper, faster, easier").
  Name the one thing that actually matters.
- **Repeated sentence shapes.** If several sentences in a row share the same skeleton,
  break it — change the openings and the lengths so the rhythm isn't robotic.
- **Rhetorical questions.** One per article at most, and only if it pulls its weight.
- **Narrating the article.** Don't announce what a section will do or recap what came
  before. Just write the next thing.

---

## Voice

- Address the reader as "you", not "users" or "people".
- Use contractions (you'll, it's, don't).
- First-person "I" is fine when the piece has a clear point of view; save "we" for
  genuinely company-authored content.
- Active voice by default; passive only when it honestly reads better.

---

## Readability

Write for the audience set in Stage 1 — an aim, not a fixed grade:
- Short sentences; break any that sprawl past ~25 words.
- Plain, concrete words ahead of abstract or Latin-root ones.
- One idea per sentence.

`lint_article.py` reports a readability score so you can catch a section that drifted
dense, but it does not fail the run on it — read it against the audience (a developer
piece can run denser than one for first-time buyers).

---

## Paragraphs and layout

- Keep paragraphs short — a few sentences, rarely more than five. Vary their length
  so the page has rhythm.
- Add a heading roughly every 250–300 words so nothing becomes a wall of text.
- Use bullet lists for three or more parallel items.
- Tables are allowed where they genuinely help a comparison (unlike some guides, we
  don't ban them) — but don't force structured prose into a table for its own sake.
- **Bold the label** on any labeled item so it's scannable: rating-block lines,
  step labels, pros/cons headers, "pick X if" lines, mistake callouts. A bare
  unbolded label reads as default chatbot output.

---

## Headings

- One H1 (the title). H2s for main sections, H3s for sub-points beneath them.
- Nest at most two levels (H2 → H3). Don't go to H4.
- Every content H2 should carry at least one entity or specific from the Stage 1
  checklist, so no section is generic filler.

---

## Keyword handling

**Placement (required):**
- **Title:** include the exact target keyword, near the front where it reads naturally.
- **First ~100 words / first 200 characters** of the intro.
- **At least two H2 headings** — use the exact keyword in one and a close variant in
  the other where natural. (If two genuinely can't be done without forcing it, one is
  the floor — but with a well-chosen primary this is almost always doable.)
- **Final section** (the verdict/close), once.

`lint_article.py --keyword "<primary keyword>"` checks the intro, an H2, and the close.

**Usage (placement over volume):**
- Use the **exact target keyword phrasing** in these key spots — that exact wording
  is what you're ranking for, so don't dilute it with a synonym where the real term
  fits. Variants are for natural flow *around* the exact term, not a replacement for it.
- Keep density light and unforced (roughly 0.5–2% of the text). Repeating the term or
  padding with near-variants is stuffing, which search engines penalize.
- **Use the Stage 1 keyword targets that fit naturally, and cover the entity/topic
  checklist.** Topic coverage — hitting the subtopics the top pages cover — matters
  more than keyword count. Cover the topics; place the exact keyword where it belongs;
  don't cram in every target for its own sake.

---

## Specifics over generalities

This applies to *claims* — assertions a reader could reasonably ask you to back up —
not to every sentence (don't bolt a number onto ordinary or connecting sentences).
When you make a general claim ("SEO drives traffic", "many teams use X"), either
ground it with a number, a name, a date, or a concrete example, or cut it. A sourced
figure beats a vague claim, and a filler line like "this matters for businesses"
inside an on-topic article earns nothing — remove it.

---

## Clean output

- No placeholder tokens ever: no `[Insert Image Here]`, `[TODO]`, `[link]`, or any
  bracketed marker. Everything you output is publish-ready.
- No image placeholders or "add a screenshot here" notes — images are the user's job
  in their CMS.
- Real, descriptive anchor text on links, never "click here".
- (Links themselves are welcome: internal links from Stage 2 and cited sources /
  official references from Stage 6. Just no placeholder syntax.)

---

## The final check

Read the finished piece once more and ask: does any of it sound like a chatbot on a
basic prompt? If a section does, it's the weakest section — rewrite it. The bar is
prose a knowledgeable person would be happy to publish under their own name.
