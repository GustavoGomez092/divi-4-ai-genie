# Skill test results — brief-01 (Emergency Water Heater Repair in Miami)

Validator command for every run:
`python3 Skill/divi-page-builder/scripts/validate.py page.txt --tokens Skill/divi-page-builder/recipes/sample-tokens.json --json`

## Baseline (no skill, no tokens; sonnet, fresh context)

| metric | result |
|---|---|
| validator | **9 errors, 24 warnings** |
| errors by code | `E_UNKNOWN_ATTR` ×5 (`number_suffix`, `bar_bg_color` on `et_pb_number_counter`: invented attributes), `E_VALUE_FORMAT` ×4 (`font_icon="&#xe092;"`: not a Divi icon value) |
| warnings by code | `W_OFF_PALETTE_COLOR` ×19, `W_OFF_SCALE_SPACING` ×5 |
| exactly one H1 | yes |
| site fonts/colors | no: invented a navy/orange-red palette (`#0B3C5D`/`#E1562F`) and left every font at the Divi default |

Observed failure modes: invents plausible-looking attributes, guesses the icon value format, and has
no way to know the brand (every color off-palette and every font default).

## With skill, run 1 (sonnet, fresh context; SKILL.md + file access)

| metric | result |
|---|---|
| validator | **0 errors, 0 warnings** (re-run independently by the controller) |
| `W_OFF_PALETTE_COLOR` / `W_OFF_BRAND_FONT` | 0 / 0 |
| exactly one H1 | yes (`et_pb_heading title_level="h1"`); rendered heading walk h1→h2→h3→h3→h2→h3→h4, no skips |
| fonts in shortcode | Montserrat (headings, counters), Lato (body): only the brand's fonts |
| preview | `preview.py render`: 40 modules, 97.9% of 190 attributes read; gap: `et_pb_accordion_item` `icon_color`, `open_toggle_text_color` (renderer coverage, not a page error) |
| publish | `publish.py draft` → draft page (deleted afterwards), status `draft` confirmed via WP-CLI |

Workflow followed: SKILL.md → recipes/README.md → recipes/pages/service-landing.md → five section
recipes → two module pages → tokens.json → compose → validate → preview → draft. Sections chosen:
hero-centered, services-grid, stats-counters, faq (with JSON-LD), cta-band. It correctly dropped
image sections because the brief had no images (hard rule: never hotlink or invent media).

Stumbles (from the agent's log):
1. **No icon lookup table.** It grepped the skill for already-used `font_icon` codes and reused four
   of them. The result is valid, but it can't choose an icon by meaning. → already a final-wave item (`reference/icons.md`).
2. **`et_pb_number_counter` suffixes** ("25+", "4.9★"). It resolved this correctly from the module
   page (`number` is plain text; `percent_sign="off"`). No doc change needed.
3. **Image sections**: unsure whether to include them without assets. It resolved this correctly from
   the hard rules. No doc change needed.

Visual check (real Divi via `preview.py serve --exact`; the logged-out browser can't open the WP
draft preview, and the `--exact` Playground render is the same real-Divi engine):
- 1440: navy/orange palette, Montserrat headings, Lato body; layout as designed.
- 390: no horizontal overflow; responsive sizes applied (h1 34px, h2 28px).
- **Problem:** both buttons and both FAQ toggle titles render in **Open Sans** (Divi's default).
  The recipes never set `button_font` / accordion `title_font`, so these fall back to the Customizer
  fonts. The sample site's Customizer uses Lato body and Montserrat headings (`colors.customizer`), which
  the preview doesn't apply ("defaults only"). The validator can't see it: an unset font isn't
  off-brand. 13 recipe files share this gap (only hero-split / service-landing set `button_font`, once each).
- Blurb icons and counters sit at opacity≈0 until Divi's scroll animations run (a normal Divi
  default; seen in a throttled background tab). Not a page defect.
- The blurb body copy ("Fast diagnosis and repair for…") was written by the agent. The brief gave only
  service names. This is acceptable copywriting (not a testimonial, price or stat), and the brief's
  verbatim items are all present.

Doc fix after run 1: in recipes/README.md plus every recipe with buttons, toggles, accordions or tabs,
set fonts explicitly from `colors.customizer`: `button_font` and `tab_font` get the body font;
accordion/toggle `title_font` gets the heading font.

## With skill, run 2 (fresh sonnet agent, after fixes f7580d8 + d0e5256)

| metric | result |
|---|---|
| validator | **0 errors, 0 warnings** (re-run independently) |
| `W_OFF_PALETTE_COLOR` / `W_OFF_BRAND_FONT` | 0 / 0 |
| exactly one H1 | yes; rendered walk H1 H2 H3×7 H2 H3 H3 H4, no skips |
| fonts in shortcode | `button_font` Lato ×2, `toggle_font`/`closed_toggle_font` Montserrat ×2 each, plus the usual heading/body fonts |
| preview | 39 modules, 97.9% of 189 attributes read; same accordion styling gap as run 1 |
| publish | `publish.py draft` → draft confirmed via WP-CLI, then deleted |

Visual check (real Divi, `preview.py serve --exact`):
- **Run-1 problem fixed:** buttons render in Lato and FAQ toggle titles in Montserrat. No element
  in the page content falls back to Open Sans.
- 390: no horizontal overflow; h1 34px.
- Navy/orange palette, Montserrat/Lato throughout.

Stumbles (agent log):
1. No icon catalog (same as run 1) → final-wave `reference/icons.md`.
2. **`recipes/sections/faq.md` said to leave the accordion's `toggle_level` at the default `h5`**,
   which contradicts the no-skipped-levels hard rule. The page assemblies already set `h3`.
   Both runs noticed and overrode it. Fixed in 786b705: faq.md now says `toggle_level="h3"` under the section `h2`
   (prose, mapping table, required fields, and the example).
3. Number counter free-text `number`: resolved correctly from the module schema. No doc change.

## Verdict

Success criteria met on run 2: 0 validator errors, 0 off-palette/off-brand warnings, exactly one H1,
the navy/orange Montserrat/Lato look, and no phone overflow. Baseline → skill: 9 errors / 24
warnings → 0 / 0.
