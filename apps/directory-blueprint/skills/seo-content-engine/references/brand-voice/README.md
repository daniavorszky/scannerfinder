# Brand Voice Samples

This folder holds writing samples the skill can imitate. It only matters if you
pick the "match my writing" option — you don't have to use it at all.

## How it works

At Stage 5 the skill asks how the article should sound and gives you three
choices: use the default voice, match your writing, or describe the voice
yourself in a line or two. This folder is for the middle option — but you don't
have to use the folder: you can also just paste a few article links and the skill
will fetch and match them. When you pick "match my writing", the skill reads your
samples (folder files and/or the URLs you paste) and writes the new article in the
same voice. The other two options ignore this folder, so leave it empty if you're
not using it.

## What to put in this folder

Save 3 to 6 articles you've already published, as `.md` or `.txt` files. Include
just the article text — the headings and paragraphs a reader would see. Leave out
navigation menus, footers, author bios, share buttons, and comment threads, since
those aren't your writing and only muddy the sample.

Use pieces you're happy with and that sound the way you want future articles to
sound. A couple of samples is enough to start; more gives the skill a steadier
read on your voice, with little added benefit past six.

Mix the article types on purpose. A roundup, a comparison, and a how-to together
let the skill separate the parts that stay the same across everything you write —
your sentence length, your formality, how direct your opinions are — from the
parts that belong to one format. That mix is what makes the voice match hold up
across different articles, rather than copying the structure of a single post.

## Suggested layout

Filenames don't matter to the skill; it reads every `.md` and `.txt` here. Names
that say what each piece is just make the folder easier for you to manage:

```
references/brand-voice/
├── roundup-best-project-tools.md
├── comparison-notion-vs-asana.md
├── how-to-set-up-a-crm.md
├── review-figma.md
└── guide-content-marketing-basics.md
```

## What the skill takes from your samples

It looks for the habits that make your writing recognizable: how long your
sentences run and how much they vary, how formal or casual you are, the words you
reach for and whether you use contractions, how you open and close a section, and
whether you state opinions plainly or hold back. It also notes how you bridge
between ideas (your connecting phrases) and how often you reach for specifics like
numbers, names, and dates. These are the traits it carries into the new article.

## What it does not take

It does not copy any facts from your samples — no statistics, prices, product
names, or claims. Those come only from the research stages and still get checked at
Stage 6 (Fact Check + Quality Audit). Your old writing decides how the article
sounds, never what it says.

It also can't override the writing rules. If a sample uses a word on the
forbidden list in `references/article-style-rules.md`, the skill still won't use it.
Matching your voice never unlocks those words.

And it doesn't copy your formatting or linking conventions — it won't replicate your
CMS layout, your internal-link patterns, or your heading style. Voice only.
