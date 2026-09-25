# Recipes

A recipe is a **pattern expressed as fields, not a template to fill in**. It never hardcodes "make
the hero background `#0b2a3c`" — it says "the hero section's `background_color` comes from the
`et_pb_section` bundle whose `contexts[].section_tone` is `dark`." Point the same recipe at a
different client's `tokens.json` and it produces a section that looks like *that* client's site,
because every design value is a lookup, not a literal. `research/tools/notes/recipe-template.md`
defines the exact section-by-section shape every recipe below follows; read that first if you're
writing one. This README explains how to read what a recipe's Token mapping table is asking you to
do, using the real values in [`sample-tokens.json`](sample-tokens.json) — the fictional "Miami
Rapid Plumbing" brand (navy `#0b2a3c`, orange `#f97316`, Montserrat/Lato) extracted from
`tests/fixtures/valid/brand-kit.txt`.

## 1. What a recipe is

A recipe is a **pattern**: a fixed structure (which modules, in which nesting, in which column
split) plus a set of *pointers* into `tokens.json` for every value that should vary by site —
colors, fonts, sizes, spacing, presets. It is not a fill-in-the-blanks template with placeholder
text, and it is not a fixed shortcode string with the hex codes swapped. Following a recipe on a
new client means: build the same structure, then resolve every pointer in its token mapping table
against *that* client's `tokens.json`, falling back only where the site truly has no matching
entry (§2, and `reference/design-tokens.md` §5, "the fidelity rule").

## 2. How to read a token mapping

A recipe's Token mapping table has three columns: the attribute being set, a `tokens.json` path to
read it from, and a fallback for a thinner `tokens.json`. The path always resolves the same way:

1. **Pick a `module_styles[slug]` entry by context.** `module_styles.et_pb_button` in
   `sample-tokens.json` has two bundles. One's `contexts[0]` is
   `{"section_label": "Hero", "section_tone": "dark", "column_type": "1_2", ...}` with
   `attrs.button_text_color = "#ffffff"` and `preset = "default"`; the other's context is
   `{"section_label": "Free Quote CTA", "section_tone": "dark", "column_type": "4_4", ...}` with
   `attrs.button_text_color = "#0b2a3c"` and `preset =
   "11111111-2222-3333-4444-555555555555"`. Both sit on a dark section, but they're different
   bundles because Miami Rapid Plumbing styles a full-width CTA button differently from a
   split-hero button — match `section_tone` **and** `column_type` (and, when there's more than one
   candidate at that tone/column combination, `section_label`) to the spot you're actually placing
   the module, not just the first bundle for that module slug.
2. **Copy `attrs` verbatim**, including anything you didn't expect to need. The chosen
   `et_pb_button` bundle's `attrs` also carries `button_bg_color__hover` and
   `button_bg_color__hover_enabled` — copy those onto the new button even though the recipe's
   table only called out `button_text_color`, because leaving the hover state off is a visible
   regression from how this site's other buttons behave.
3. **Keep `preset` and `module_class` as-is.** The CTA button bundle above has `preset =
   "11111111-2222-3333-4444-555555555555"`, not `"default"` — set
   `_module_preset="11111111-2222-3333-4444-555555555555"` on the new module. Never invent
   attribute values to imitate a preset's look; its contents aren't readable (see
   `reference/design-tokens.md` §1). Likewise, `et_pb_text`'s "About" bundle has `module_class =
   "pp-lead"` — keep that class, since the client's own CSS may target it.
4. **For non-context-scoped tokens** (typography, spacing, colors, presets), read straight off
   the top-level key: `typography.scale.h1.font` is `"Montserrat|700|||||||"`,
   `typography.scale.h1.size` is `"56px"` with `size_tablet: "42px"` / `size_phone: "34px"`, and
   `presets.et_pb_button[0].uuid` is the same
   `11111111-2222-3333-4444-555555555555` seen above — confirming it's a real, reused preset and
   not a one-off.

## 3. Using `section_exemplars`

`section_exemplars` is a real section's shape with the copy stripped out — use it for structure,
the way `module_styles` is used for attributes. Building a new hero section, match the Hero
exemplar's row: `column_structure="1_2,1_2"`, `width="90%"`, `max_width="1200px"` — don't invent a
different split or a fixed pixel width. Match its section-level `custom_padding`
(`"96px||96px||true|false"`, with `custom_padding_tablet`/`_phone` set the same way) rather than
guessing a padding value, and match its column habit: one heading + text + button in the first
column, one image alone in the second. The "Why Choose Us" exemplar shows a different habit worth
copying for a three-up feature row: a full-width heading row (`et_pb_row` with no
`column_structure`, one `4_4` column) followed by a second row with
`column_structure="1_3,1_3,1_3"`, one `et_pb_blurb` per column.

## 4. Recipe index

| Recipe | Type | Use case |
|---|---|---|
| _none yet_ | — | Tasks 16-19 populate `sections/`, `pages/` and `edits/` below; this table grows as each recipe lands. |

- `sections/` — single-section patterns (hero, feature row, CTA band, …).
- `pages/` — full-page compositions built from more than one section recipe.
- `edits/` — patterns for modifying an existing page rather than authoring a new one.

## 5. The verification loop

Every recipe in this directory was checked with the same four-step loop before being written down,
and the worked example in each recipe's own Checklist section names the same steps:

1. **Validate** — `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json`
   must report 0 errors.
2. **Preview** — `python3 Skill/divi-page-builder/scripts/preview.py render <file>` for a fast
   visual check (no Node/PHP/WordPress needed; see `reference/preview.md`).
3. **Push to the local site** — `research/tools/push_local.sh <file> "<title>"` publishes it as a
   `Plan Test: <title>` page on `divi-test.local` and prints `<id> <url>`.
4. **Screenshot** — `node research/python-renderer-spike/shoot.mjs <outdir> <name> <url> --width
   1440,390` (needs Node 22+) captures the real, real-Divi-rendered page at desktop (1440px) and
   phone (390px) widths — not a browser-automation tool, since the helper is scriptable and
   headless. Delete the test page afterwards with
   `research/tools/wp-local.sh post delete <id> --force`.
