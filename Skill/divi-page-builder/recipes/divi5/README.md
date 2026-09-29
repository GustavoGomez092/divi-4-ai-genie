# Divi 5 recipes

The Divi 5 recipes are the [Divi 4 recipes](../README.md) written as Divi 5 blocks. The patterns are the same:
the sections, the column splits, the purpose, the SEO notes and the variations. Each Divi 5 file links to its
shared recipe for those, and holds what changes on Divi 5: the block structure, the **field mapping** (which
`tokens.json` path feeds which Divi 5 attribute path), the Divi 5 responsive rules, a worked example in canonical
block markup and a checklist. Read [reference/divi5/page-format.md](../../reference/divi5/page-format.md) first.

The worked examples use [`sample-tokens.json`](sample-tokens.json): the same fictional "Miami Rapid Plumbing"
brand as the Divi 4 examples (navy, orange, Montserrat/Lato), stored the way a Divi 5 site stores its design
system:

| role | id in `sample-tokens.json` | value |
|---|---|---|
| brand navy (backgrounds, dark text) | global color `gcid-r6navy0001` | `#0B2A3C` |
| brand orange (buttons, icons) | global color `gcid-r6orange001` | `#F97316` |
| accent (Customizer primary color) | `gcid-primary-color` | `#F97316` |
| hero section padding | number variable `gvid-r6secpad01` | `clamp(48px, 8vw, 96px)` |
| corner radius | number variable `gvid-r6radius01` | `12px` |
| primary button look | module preset `r6btnpreset1` (its CSS is in the tokens) | orange, white text, 12px corners |
| "Free Quote CTA" button | module preset `11111111-2222-3333-4444-555555555555` (converted from Divi 4; `css: null`) | unknown |

The ids are opaque: `r6…` comes from the test fixture the ids were captured from; a real site's ids are random
(`gcid-7k2x9…`). The file is **only** for the examples: a real page always uses the target site's own
`tokens.json` (`scripts/extract_tokens.py`, [design-tokens.md §7](../../reference/design-tokens.md#7-divi-5-sites)).

## 1. From a token path to an attribute path

Divi 5 tokens hold Divi 5 attribute JSON, so a token path ends in the same attribute path you write. The
Hero-context heading bundle, `module_styles["divi/heading"]` (context `section_label` "Hero", `column_type`
`1_2`), has `attrs.title.decoration.font.font` →
`{"desktop": {"value": {"headingLevel": "h1", "family": "Montserrat", "weight": "700", "color": "#ffffff",
"size": "56px"}}, "tablet": {"value": {"size": "42px"}}, "phone": {"value": {"size": "34px"}}}`: that object goes
into the new heading at `title.decoration.font.font`, breakpoints included. A recipe's Field mapping table names
the attribute path, the token path, and a fallback for a thinner `tokens.json`.

Copying a bundle:

- **Copy its `attrs` whole**, including keys the table didn't mention (a hover background next to the color).
- **Leave out** what a bundle carries only because Divi's converter wrote it: `module.decoration.layout` on
  modules (structure blocks get it anyway, below) and `""` values (`"right": ""` means unset).
- **Keep `module_preset` and `html_attributes`** (as `modulePreset` and `module.advanced.htmlAttributes`); the
  site's CSS may target its classes.
- Fonts on buttons are never in a heading/text bundle: set `family` from `typography.body_font` (and `weight`)
  on `button.decoration.font.font`, as on Divi 4.

The Divi 4 attributes the recipes use, and where they live on Divi 5:

| Divi 4 | Divi 5 |
|---|---|
| `background_color` | `module.decoration.background` → `color` |
| `custom_padding` (+`_tablet`/`_phone`) | `module.decoration.spacing` → `padding` `{top, bottom, …}` per breakpoint |
| `width`, `max_width`, `module_alignment` | `module.decoration.sizing` → `width`, `maxWidth`, `alignment` |
| `title_font`, `title_text_color`, `title_font_size`, `title_level` | `title.decoration.font.font` → `family`, `weight`, `color`, `size`, `headingLevel` |
| `text_font`, `text_text_color`, `text_font_size`, `text_line_height` | `content.decoration.bodyFont.body.font` → `family`, `weight`, `color`, `size`, `lineHeight` |
| `text_orientation` (text), `title_text_align` (heading) | `textAlign` in that font value |
| `custom_button`, `button_bg_color`(`__hover`), `button_text_color`, `button_border_*`, `button_font` | `button.decoration.button` → `enable`; `.background` → `color` (+ `hover` state); `.font.font` → `color`, `family`, `size`; `.border` → `styles.all.width`/`color`, `radius` |
| `button_alignment` | `module.advanced.alignment` |
| `_module_preset` | `modulePreset` (a list; omit it for the site default) |
| `admin_label` | `module.meta.adminLabel` |

There are no `_last_edited` or `__hover_enabled` flags: a `tablet`/`phone` key or a `hover` state is its own
switch ([value-formats.md](../../reference/divi5/value-formats.md#breakpoints)).

## 2. `$variable` or literal

Write the reference whenever the site has an id for the role, and the literal otherwise
([design-tokens.md §7.4](../../reference/design-tokens.md#74-references-versus-literals)):

1. **A bundle value that is already a `$variable(…)$` string** is copied as it is. The Hero section bundle's
   background is `$variable({"type":"color","value":{"name":"gcid-r6navy0001","settings":{}}})$`, its padding
   `gvid-r6secpad01`: the new section references both, and never writes `#0B2A3C` or `96px`.
2. **A literal that equals a `colors.global` value used in that role** (its `roles` list the attribute path)
   becomes the reference: an orange button background is `gcid-r6orange001`, whose roles include
   `button.decoration.background.color`. A `colors.palette` entry with `global` says the same.
3. **Accent, heading, body and link colors** that no global covers use the Customizer ids, which always exist:
   the eyebrow's orange is the accent, `gcid-primary-color`.
4. **Everything else is literal**, from the tokens: `#ffffff` headings, the `#cbd5e1` body copy, the `#ea580c`
   hover (none of them has an id).

An id not in `tokens.json` renders as nothing, and an unknown preset id also drops the module's default preset
styling: never invent one (`W5_UNKNOWN_VARIABLE`, `W5_UNKNOWN_PRESET`). A global color can be adjusted with
`settings` (`{"opacity": 85}` renders `hsl(from var(--gcid-…) … / 0.85)`): the background-image hero tints its
photo with the brand navy that way. Use it only for a shade of a brand color that has no id of its own.

**Presets.** A bundle's `module_preset` goes on the new block as `modulePreset`, with the bundle's `attrs` next to
it. `r6btnpreset1` supplies the orange, the white label and the 12px corners; the Hero button bundle adds only
the hover color (with the same desktop color, since a hover state needs one). A preset whose `css` is `null` is
still a real id whose look is unknown: keep it with its bundle's attrs, as the CTA button does with
`11111111-2222-3333-4444-555555555555`. To get the site's default look, write no `modulePreset` at all.

## 3. Choosing a `module_styles` bundle by context

Each bundle's `contexts` say where the site used it: `section_label`, `section_tone`, `column_type`
(`section_background` holds the section's color). Match the spot you're filling:

1. **`column_type`** must match (`1_2` for a split hero's text column, `4_4` for a single column).
2. **`section_tone`** must match. On Divi 5 it can be `"variable"`: the section's background is a global
   color, so look up `section_background.color`'s id in `colors.global` and judge its value (`gcid-r6navy0001` is
   `#0B2A3C`: dark).
3. **`section_label`** breaks a tie between bundles that match on both.

`module_styles["divi/button"]` in the sample has two bundles, both on navy sections: `[Hero, 1_2]` (preset
`r6btnpreset1`, white label) and `[Free Quote CTA, 4_4]` (preset `11111111-…`, navy label). The split hero's button
takes the first; the centered and background-image heroes have one `4_4` column, so they take the second, as on
Divi 4.

## 4. Section exemplars

`section_exemplars` is each sampled section's design-only block tree (`{name, attrs, media, children}`), the way
`module_styles` is its attributes. Build a new hero on the Hero exemplar (`attrs.module.meta.adminLabel` "Hero"):
a `1_2,1_2` row at `width` 90% / `maxWidth` 1200px, the heading, text and button in the first column and the
image alone in the second, and the section's background and padding exactly as the exemplar has them. Don't
invent a different split or a pixel row width.

## 5. Writing the blocks

- `builderVersion` on every block: the site's `site.divi_version` (the sample's is `5.13.1`).
- Every section, row and column states the layout form (`module.decoration.layout` → `{"display": "block"}`),
  with `columnStructure` on the row and `type` on each column
  ([structure.md](../../reference/divi5/structure.md#the-layout-form-display-block-on-structure-blocks)).
  Modules don't need it.
- Build the JSON with `scripts/divi5_blocks.py`, never by hand: it writes WordPress's canonical escaping, which a
  `$variable()` string needs (its quotes are stored as `\u0022`):

```python
import divi5_blocks as d
navy = '$variable({"type":"color","value":{"name":"gcid-r6navy0001","settings":{}}})$'
text = d.new_block("text", {"content": {"innerContent": {"desktop": {"value": "<p>Hello</p>"}}},
                            "builderVersion": "5.13.1"})
print(d.render_block(text))
```

## 6. Recipe index

| Recipe | Divi 4 original | Divi 5 specifics |
|---|---|---|
| [Hero split](sections/hero-split.md) | [hero-split](../sections/hero-split.md) | preset button, radius variable on the image |
| [Hero centered](sections/hero-centered.md) | [hero-centered](../sections/hero-centered.md) | `sizing.maxWidth` + `alignment` to center the copy block |
| [Hero background image](sections/hero-background-image.md) | [hero-background-image](../sections/hero-background-image.md) | background `image` + a navy gradient from the global color with `opacity` |
| [Hero fullwidth header](sections/hero-fullwidth-header.md) | [hero-fullwidth-header](../sections/hero-fullwidth-header.md) | fullwidth section; the module's own background must be set |
| [Change copy](edits/change-copy.md) | [change-copy](../edits/change-copy.md) | `set-attr`, `extract`→edit→`replace` |
| [Insert section](edits/insert-section.md) | [insert-section](../edits/insert-section.md) | `insert-after`/`insert-before` on a section anchor |
| [Replace section](edits/replace-section.md) | [replace-section](../edits/replace-section.md) | `replace` a section's span |
| [Restyle to tokens](edits/restyle-to-tokens.md) | [restyle-to-tokens](../edits/restyle-to-tokens.md) | `validate.py --tokens`, then `set-attr` per finding |

## 7. The verification loop

As on Divi 4 ([README §5](../README.md#5-the-verification-loop)), against the **target site's** `tokens.json`:

1. **Validate**: `python3 scripts/validate.py page.html --tokens tokens.json` (a lone section with
   `--fragment`): 0 errors, and no `W5_UNKNOWN_VARIABLE` or `W5_UNKNOWN_PRESET`.
2. **Preview**: `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` renders on
   real Divi 5 in Playground with the site's global colors and preset CSS; **stop until the user approves it**.
   Number and font variables (`gvid-…`) print only on a site that defines them, so in the preview a section padded
   by a variable shows Divi's default padding and a radius variable shows square corners; the draft shows them.
3. **Draft**: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"`, then
   review the draft's `preview_url` before publishing ([publishing.md](../../reference/publishing.md)).

Maintainers port a Divi 4 recipe with `research/tools/divi5/port_recipe.py` (repo only): it converts the worked
example with Divi's own converter, cleans and validates it and writes a draft for the human pass.
