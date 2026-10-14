# Examples

Example files from one run, kept to show the shape of a per-vertical file. They are not a recommendation of a vertical and the Blueprint never proposes one to a member.

- `attributes-pool-builders.json`: the per-vertical attribute file as written at Gate 3 for a pool builders directory (13 attributes). At Gate 3 write `output/<slug>/03-attributes.json` for the member's vertical in the same shape. Each attribute carries:
  - `key`: the CSV column name, snake_case
  - `label`: what the listing page and the packets show
  - `faq`: the question the attribute can answer on a city page (`{plural}` and `{city}` are filled in)
  - `true_when`: one line saying what the business's own words must state for a `true`; printed at the top of every enrichment batch
  - `pattern`: a case-insensitive regex of the words that count as evidence; `build_evidence.py` uses it to pull quotes and `merge_enriched.py` uses it to trace every `true`
  - `service` (optional, added at Gate 4): `{ "slug", "title", "intro": [] }`. An attribute that carries it gets a statewide service page at `/services/<slug>/` when at least the city floor of listings confirm it. `title` is the page's H1 phrase without the state ("Fiberglass Pool Builders"), `intro` is the 80 to 200 words written at Gate 5. Only for an attribute people search for as a service; which attributes get a page is the member's decision in `04-plan.md`
  - `core` (optional, at most one attribute): marks the attribute that says whether the business does the vertical's core work at all. Add it only when the Maps category is broader than the vertical. What to do with listings that answer `false` to it is a Gate 4 decision for the member (an exclusions row, a sort setting, or nothing), never a Blueprint default.

The same file is copied into the site as `src/data/attributes.json`; the skeleton reads `key`, `label`, `faq` and `service` and ignores the rest.
