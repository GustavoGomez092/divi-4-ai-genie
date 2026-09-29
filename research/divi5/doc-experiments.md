# Divi 5: experiments behind the hand-written references

Evidence for `Skill/divi-page-builder/reference/divi5/{page-format,structure,value-formats}.md` (Task 9), in addition
to the research spikes in this folder. Run on 2026-09-28 against `http://divi-5-test.local` (LocalWP, Divi 5.13.1,
WordPress 7.1.2). Paths are relative to `wp-content/themes/Divi/includes/builder-5/` unless they start with
`research/`, `tests/` or `Skill/`.

Method for every live check: build the block markup with `divi5_blocks.new_block` / `render_block` / `serialize`
(canonical form, `builderVersion` 5.13.1), validate it with `validate.py`, then publish it with
`research/tools/divi5/render_check.sh` (creates a published page with `_et_pb_use_builder=on`, curls it, counts module
order classes, reads `debug.log`, deletes the page) and read the saved HTML (CSS is inlined as
`et-core-unified-<id>-cached-inline-styles`). All test pages were deleted by the script.

## 1. Bare `….decoration.font` vs `….decoration.font.font`

Page: one section holding six modules:

| block | where the style was written | rendered |
|---|---|---|
| `divi/blurb` | `title.decoration.font.desktop.value = {size: 51px, color: #ff0001}` (bare) | no rule contains `#ff0001` or `51px`; title `h4` default |
| `divi/blurb` | `title.decoration.font.font.desktop.value = {size: 52px, color: #ff0002}` | `.et_pb_blurb_1 .et_pb_module_header{color:#ff0002!important;font-size:52px}` |
| `divi/heading` | bare `{size: 53px, color: #ff0003, headingLevel: h2}` | no `#ff0003`/`53px` rule; rendered `<h1>` (the bare `headingLevel` was ignored too) |
| `divi/heading` | `.font.font` `{size: 54px, color: #ff0004, headingLevel: h3}` | `color:#ff0004!important;font-size:54px`, rendered `<h3>` |
| `divi/toggle` | `openToggle.decoration.font.desktop.value.color = #ff0005` (bare) | no `#ff0005` rule |
| `divi/toggle` | `openToggle.decoration.font.font.desktop.value.color = #ff0006` | `.et_pb_toggle_1.et_pb_toggle.et_pb_toggle_open>h5.et_pb_toggle_title{color:#ff0006!important}` |

`validate.py` reported **0 errors** for all six (the bare paths are in the schema's union path model).

Source: `server/Packages/Module/Options/Element/ElementStyle.php:297-305` passes the element's `decoration.font` group
to `FontStyle::style()`, which styles only `$attr['font']`, `$attr['textShadow']` and `$attr['textEffects']`
(`server/Packages/Module/Options/Font/FontStyle.php:130-250`). The heading tag comes from
`decoration.font.font.desktop.value.headingLevel` (`server/Packages/Module/Layout/Components/ModuleElements/ModuleElements.php:1026-1042`).
No module PHP reads keys written directly under an element's `decoration.font`. Even for the elements where the dump
lists bare leaves (toggle `openToggle`), Divi's converter targets `.font.font`
(`open_toggle_text_color` → `openToggle.decoration.font.font.*.color`, `research/divi5-schema/modules/toggle.json`).

## 2. Layout form: `display: "block"` on structure blocks

Same page, three sections, all blocks `builderVersion` 5.13.1:

- Sections/rows/columns **with** `module.decoration.layout.desktop.value.display = "block"`:
  `et_pb_section_0 et_pb_section et_section_regular et_block_section`, `et_pb_row_0 et_pb_row et_block_row`,
  `et_pb_column_0 et_pb_column et_pb_column_1_2 et_block_column` (Divi 4 widths from `module.advanced.type`).
- The same `1_2,1_2` row **without** the layout attribute: `et_flex_section`, `et_flex_row`, and both columns
  `et_flex_column et_flex_column_24_24 et_flex_column_24_24_tablet et_flex_column_24_24_phone`: the `1_2` type is
  ignored and each column is full width.
- Modules without their own `layout` render `et_flex_module` (Divi 5's flex column, `.et_flex_module{display:flex;
  --flex-direction:column; row-gap:var(--module-gutter)…}`). Every module rendered, with the expected content and CSS.

## 3. Doc examples, rendered

All 32 example sections of the three references (page-format, structure, value-formats), on one page: HTTP 200,
145 blocks → 145 module order classes, 0 `et_d4_element`, 0 new `debug.log` lines. Observations used by the docs:

- Section classes: fullwidth `et_pb_fullwidth_section et_section_regular`; specialty `et_section_specialty`.
- Specialty: inner columns `1_2,1_2` inside a `3_4` specialty column rendered `et_pb_column_inner et_pb_column_3_8`
  (scaled, as in Divi 4).
- Order classes are `et_pb_<snake_case name>_<N>`, first in the class list: `et_pb_fullwidth_header_0`,
  `et_pb_accordion_item_0`, `et_pb_map_pin_0`, `et_pb_text_0`. Source: `ModuleUtils::get_module_order_class_name_base()`
  / `get_module_class_by_name()` (`server/Packages/ModuleUtils/ModuleUtils.php:2754-2790`); none of the in-scope
  modules overrides it in `module.json`, so `divi/cta` is `et_pb_cta_N` (Divi 4: `et_pb_promo`).
- `css.desktop.value.mainElement = "letter-spacing: 1px;"` on a text → `.et_pb_text_0{text-align:start;letter-spacing:1px}`.
- `module.advanced.htmlAttributes` `{class: "hero-lead", id: "intro"}` → the class and `id="intro"` on the module
  wrapper (Divi 5.13.1 still reads it: `server/Packages/Module/Options/IdClasses/IdClassesClassnames.php`,
  `server/Packages/Module/Module.php:479`).
- `module.decoration.attributes` row `{name: "data-track", value: "hero-lead"}` → `data-track="hero-lead"`.
- Image `image.innerContent` `{src, alt, titleText}` → `<img … alt="…" title="…">`
  (`ModuleElements.php:1403-1420` maps `alt` → `alt`, `titleText` → `title`).
- `&#91;20%&#93;` in text content is output as the entities (renders `[20%]`, no shortcode run).
- A heading `size` per breakpoint: desktop without a media query, tablet in `@media only screen and (max-width:980px)`,
  phone in `@media only screen and (max-width:767px)`.
- `title.decoration.font.font.desktop.hover.color` on a blurb → `.et_pb_blurb_0:hover .et_pb_module_header{color:…}`
  (hover of the module, not only the title). Phone values land in the `max-width:767px` media query.
- `$variable` color on a button background → `background-color:var(--gcid-primary-color)`; the Customizer heading font
  `$variable({"type":"content","value":{"name":"--et_global_heading_font",…}})$` → `font-family:var(--et_global_heading_font)`.
- Gradient `stops` `[{position: 0, color}, {position: 100, color}]` → `linear-gradient(90deg,#1e3a8a 0%,#3b82f6 100%)`.
- `transform` `{rotate: {x,y,z}, scale: {x,y}}` → `transform:scaleX(1.05) scaleY(1.05) rotateX(0deg) rotateY(0deg) rotateZ(-3deg)`.
- Border `radius` object on `image.decoration.border` → the four `border-*-radius` declarations on `.et_pb_image_wrap`.
- Button `button.decoration.button.icon.settings` `{"unicode":"&#xf095;","type":"fa","weight":"900"}` →
  a `data-icon` attribute holding the glyph U+F095 (written as the raw character) and `font-family:"FontAwesome"; font-weight:900`.
- Links: button `linkTarget: "on"` → `target="_blank"`; blurb `title.innerContent.url` wraps the title and the icon in
  `<a>`; `module.advanced.link.url` adds `et_clickable`; icon `icon.innerContent.url` renders the icon as `<a>`.
- An accordion with `title.decoration.font.font` `headingLevel: "h3"` and items that set none: both items rendered
  `<h3 class="et_pb_toggle_title">` (the items' default is `h5`).
- A section with `module.decoration.sticky` `{position: "top"}` and a `sticky`-state background printed the sticky rule
  under the class Divi adds while the element is stuck (`….et_pb_section_12.et_pb_sticky{background-color:#f1f5f9!important}`).

## 4. Icons: Divi 4 strings, the converter, and Divi 5's icon list

- Divi's converter splits the Divi 4 value on `||`: part 1 → `unicode`, part 2 → `type`, part 3 → `weight`, empty parts
  dropped (`ValueExpansion::convertFontIcon()`, `server/Packages/Conversion/ValueExpansion.php:31-49`).
- The 35 converted fixtures confirm it value for value (`tests/fixtures/divi5/converted/*.html` against
  `tests/fixtures/{valid,render}/*.txt`): `font_icon="&#xf0a9;||fa||900"` (×12) → `{"unicode":"&#xf0a9;","type":"fa","weight":"900"}`
  (×12), `&#xe03b;||divi||400` → `{"unicode":"&#xe03b;","type":"divi","weight":"400"}`, `button_icon="&#x45;||divi||400"` →
  `button.decoration.button.icon.settings` `{"unicode":"&#x45;","type":"divi","weight":"400"}`, and so on (45 icon values).
- Rendering looks the icon up in `visual-builder/packages/icon-library/src/components/icon-font/iconList.json` and
  needs all three keys: `find_icon_in_list()` returns null unless `unicode`, `weight` and `type` are set and match an
  entry (`server/Packages/IconLibrary/IconFont/Utils.php:60-81`); `process_font_icon()` returns null for a type other
  than `divi`/`fa` (`:186-230`).
- `Skill/divi-page-builder/reference/icons.md` (generated from Divi 4.27.9's picker) lists 1,989 values; converted to
  `(unicode, type, weight)` triples they are **exactly** the 1,989 entries of Divi 5.13.1's `iconList.json` (0 missing
  either way; an entry's `type` is `divi` when its `styles` include `divi`, else `fa`).

## 5. Spacing and radius sync flags

`syncVertical`/`syncHorizontal` (spacing) and `sync` (radius) are not read by the style declarations:
`server/Packages/StyleLibrary/Declarations/Spacing/Spacing.php:85-125` loops over `top, right, bottom, left` only
and prints every side whose value is not `''`; the border declaration reads `topLeft, topRight, bottomRight,
bottomLeft` only (`Declarations/Border/Border.php:70`). The flags are Visual Builder UI state, like Divi 4's
`true|false` spacing parts. (The code comments say side values must be strings; a number is printed as-is, see §8.)

## 6. Column structures and specialty values in Divi 5's builder

- `visual-builder/build/settings.js` / `constant-library.js`: `regular` = the same 20 row structures as Divi 4;
  `columnInner` = `4_4`, `1_2,1_2`, `1_3,1_3,1_3`; `columnInnerWide` adds `1_4,1_4,1_4,1_4`; `columnSpecialty` = the
  9 specialty arrangements with their specialty-column position (same as Divi 4's `et_builder_get_columns_layout()`).
- `visual-builder/build/edit-post.js`: when the builder creates a specialty section it sets the specialty column's
  `module.advanced.specialtyColumns` to `"4"` for a `2_3` column and `"3"` otherwise (Divi 4's
  `data-specialty_columns`, `includes/builder/functions.php:6204-6337`).
- `server/Packages/ModuleLibrary/Column/ColumnModule.php:307-322`: the column reads `module.advanced.type` (width) and
  adds `et_pb_specialty_column` when `specialtyColumns` is set.

## 7. Legacy conversion-only attributes

The row/row-inner flat attributes (`customCssMain1`, `padding1Phone`, `columns.column-1.spacing`,
`backgroundImageHeight1`, …), the section's `columnsBackground`/`columnsPadding`/`columnsCss`/`columnsCssFields`/
`prevBackgroundColor`/`nextBackgroundColor`, the map's `mapCenterMap`/`googleMapsScriptNotice` and a bare `content`
on modules that have no `content` element occur in Divi 5.13.1 only in the conversion outlines
(`server/_all_modules_conversion_outline.php`, `visual-builder/build/module-library.js`); `grep` finds them in no
module PHP. In the fixture corpus only one appears, once (`nextBackgroundColor` in `tests/fixtures/divi5/divi-ai/layout.html`,
from a Divi AI premade).

## 8. Values the validator accepts but Divi doesn't render

Two more probe pages (same method), `builderVersion` 5.13.1:

| value | validator | rendered |
|---|---|---|
| `module.decoration.spacing` `{"padding": {"top": 41, "bottom": "42px"}}` (a JSON number) | 0 findings | `padding-top:41!important;padding-bottom:42px!important`: the unitless `41` is invalid CSS, so no top padding |
| background `gradient` without `"enabled"` (`type`, `direction`, numeric stops) | 0 findings | no gradient rule at all |
| `gradient` `{"enabled": "on", …}`, stops `position` `"0%"` / `"100%"` | 0 findings | no gradient rule at all |
| stops `position` `0`/`100` (numbers, `direction` omitted), or `"0"`/`"100"` (strings, `direction` `90deg`) | 0 findings | `linear-gradient(180deg,#… 0%,#… 100%)` (`direction` defaults to `180deg`) |
| font `style` as a string `"italic"` instead of `["italic"]` | 0 findings | `font-style:italic` (works) |
| blurb `icon` `{"unicode": "&#xf095;", "type": "fa"}` (no `weight`) | `E5_BAD_VALUE` | no icon element at all (`find_icon_in_list()` needs all three keys) |

