# Recipe template

Every recipe in `Skill/divi-page-builder/recipes/{sections,pages,edits}/` follows this exact
shape, in this order. A recipe is a *pattern expressed as fields* — it never hardcodes a color,
font or spacing value; every design value is a pointer into `tokens.json` (or, for these docs,
`recipes/sample-tokens.json`), so the same recipe produces a correctly-branded section on any
client's site. Copy this file, fill in the sections below, and delete this paragraph.

````markdown
# <Recipe name>

**Use for:** <one line> · **SEO:** <heading level rules, alt text, links>

## Structure
```text
section (<purpose>)
└─ row column_structure="…"
   ├─ column 1_2: heading (h1) · text · button
   └─ column 1_2: image
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[section_tone=dark].attrs.background_color` | `colors.palette[0].hex` |
| heading `title_font` | `typography.scale.h1.font` | `typography.heading_font` + `\|700\|\|\|\|\|\|\|` |
| … | … | … |

## Required fields · Optional fields
Two short lists; each field links to its module page.

## Responsive rules
Which values need `_tablet`/`_phone`, and why.

## Variations
2–3 bullets, each saying which attributes change.

## Worked example (sample-tokens.json)
```divi
<complete page containing this section, 0 validator errors>
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `section.txt --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one H1 on the page
- [ ] every image has alt text and a Media Library URL
````

## Section-by-section notes

- **Name.** A short, human name for the pattern (e.g. "Hero split", "Three-up blurb row"), not a
  file name or module list.
- **Use for / SEO.** One line each. SEO calls out anything that affects crawlability or
  accessibility specifically for this pattern — e.g. "exactly one `h1` per page; this section
  supplies it" or "every `et_pb_image` needs real `alt` text describing the photo, not the
  filename."
- **Structure.** An ASCII tree of tags and column splits only — no attributes, no copy. This is
  the skeleton every worked example must match, and what `section_exemplars` in `tokens.json`
  should be checked against when adapting the recipe to a real site.
- **Token mapping.** One row per attribute whose *value* should come from tokens rather than being
  invented. The token path always starts from a top-level `tokens.json` key
  (`module_styles`, `typography`, `spacing`, `colors`, `presets`, `section_exemplars`) and reads
  left to right the way you'd actually look it up: pick the `module_styles[slug]` entry whose
  `contexts[].section_tone` (and, for column-scoped modules, `column_type`) matches where this
  attribute is being used, then read `.attrs.<name>`. Always give a fallback for a site whose
  tokens don't have a matching entry, so the recipe still works on a thinner `tokens.json`.
  See `recipes/README.md` §2 for a full worked example against `sample-tokens.json`.
- **Required / Optional fields.** Split the module fields this recipe actually sets into "must be
  filled in for every use" vs. "sensible without being set." Link each to its
  `reference/modules/<slug>.md` page.
- **Responsive rules.** Name every attribute that needs a `_tablet`/`_phone` variant (most sizing
  and padding attributes do) and explain the reasoning if it's not obvious (e.g. "the hero
  heading drops from 56px to 34px on phone so it doesn't wrap past two lines").
- **Variations.** 2-3 bullets describing a close relative of this recipe and exactly which
  attributes change to get there (e.g. "image-left variant: swap the two columns' children") —
  never a full second worked example.
- **Worked example.** A complete page (not a fragment) built from `sample-tokens.json`'s values,
  tagged ` ```divi ` so `research/tools/check_doc_examples.py` validates it — it must pass with 0
  errors. This is the example a reader can copy, run through the verification loop below, and see
  exactly what the recipe produces.
- **Checklist.** What the *agent using the skill* runs on a real page: only the skill's own tools,
  relative to the skill directory, against the target site's `tokens.json` (validate → preview →
  `publish.py draft`, see `recipes/README.md` §5). Never point it at `sample-tokens.json`, at repo
  paths (`Skill/divi-page-builder/…`, `research/…`) or at the local test site: an installed skill
  has none of them. Recipe-specific checks (heading levels, alt text, invented content) follow.

## Developer verification loop (repo only, not part of the skill)

Before a recipe is written down, its worked example goes through this loop in the repo. None of
it belongs in a recipe's Checklist.

1. **Validate** against the fictional sample brand:
   `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json`
   (add `--fragment` for a section on its own) — 0 errors.
2. **Check every doc example:** `python3 research/tools/check_doc_examples.py Skill/divi-page-builder`
   — 0 failing (errors, heading skips, and a missing H1 in page recipes all fail).
3. **Preview:** `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json`.
4. **Push to the local site:** `research/tools/push_local.sh <file> "<title>"` publishes a
   `Plan Test: <title>` page on `divi-test.local` and prints `<id> <url>`. For page recipes, swap
   image URLs for a local placeholder first (`research/tools/wp-local.sh media import ... --porcelain`).
5. **Screenshot:** `node research/python-renderer-spike/shoot.mjs <outdir> <name> <url> --width 1440,390`
   (Node 22+, headless; not browser automation) at desktop (1440) and phone (390).
6. **Inspect the real output where the recipe depends on it**, e.g. `curl` the pushed page: the FAQ
   recipe's JSON-LD must parse and match the accordion; pricing feature lines must render as
   single `<li>`s with the `-` line as `et_pb_not_available`. Recipes with tricky content also go
   into `tests/fixtures/valid/` and `tests/test_divi_judge.py` `DiviJudgeTest.FILES`
   (`PP_LIVE_TESTS=1`, compares our parser with Divi's own).
7. **Clean up:** `research/tools/wp-local.sh post delete <id> --force`.
