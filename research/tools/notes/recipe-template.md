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
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file>` — fast visual check
- [ ] `research/tools/push_local.sh <file> "<title>"` — push to divi-test.local, note the printed id/url
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> <name> <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
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
- **Checklist.** The exact verification loop every recipe in Tasks 16-19 was run through before
  being written down (see `recipes/README.md` §5): validate against the sample tokens, render a
  fast Python preview, push to the local WordPress test site, and screenshot it at desktop and
  phone widths with the headless-Chrome helper — not with browser automation tools, since the
  helper is faster and scriptable. Delete the test page once you've looked at the screenshots.
