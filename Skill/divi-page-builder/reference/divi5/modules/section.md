# Section — divi/section

Top-level horizontal band that spans the full width of a page and holds rows of content.

- **Block:** `divi/section` (Divi 4: `et_pb_section`)
- **Category:** structure · **scope:** core
- **Goes inside:** the page (`divi/placeholder`)
- **Children:** `divi/column`, `divi/fullwidth-code`, `divi/fullwidth-header`, `divi/fullwidth-image`, `divi/fullwidth-map`, `divi/fullwidth-menu`, `divi/fullwidth-portfolio`, `divi/fullwidth-post-content`, `divi/fullwidth-post-slider`, `divi/fullwidth-post-title`, `divi/fullwidth-slider`, `divi/row`, `divi/row-inner`
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `column_1_after` (Column 1 Before), `column_1_before` (Column 1 Before), `column_1_main` (Column 1 Main Element), `column_2_after` (Column 2 Before), `column_2_before` (Column 2 Before), `column_2_main` (Column 2 Main Element), `column_3_after` (Column 3 Before), `column_3_before` (Column 3 Before), `column_3_main` (Column 3 Main Element), `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eLicensed, insured plumbers at your door in 60 minutes.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/section` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "module": {
    "decoration": {
      "layout": {
        "desktop": {
          "value": {
            "display": "block"
          }
        }
      }
    }
  },
  "builderVersion": "5.13.1"
}
```

**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written `"title":{"innerContent":{"desktop":{"value":{"text":"…"}}}}`. **R** = responsive (a value per breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides `value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); the full value model: [value-formats.md](../value-formats.md).

## Content

None on this block.

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `column1.decoration.background` | [Background](../design-families.md#background) |
| `column1.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `column2.decoration.background` | [Background](../design-families.md#background) |
| `column2.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `column3.decoration.background` | [Background](../design-families.md#background) |
| `column3.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `innerSizing.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
| `module.decoration.border` | [Border](../design-families.md#border) |
| `module.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.disabledOn` | [Disabled on](../design-families.md#disabled-on) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.interactions` | [Interactions](../design-families.md#interactions) |
| `module.decoration.layout` | [Layout](../design-families.md#layout) |
| `module.decoration.overflow` | [Overflow](../design-families.md#overflow) |
| `module.decoration.position` | [Position](../design-families.md#position) |
| `module.decoration.scroll` | [Scroll](../design-families.md#scroll) |
| `module.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `module.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `module.decoration.sticky` | [Sticky](../design-families.md#sticky) |
| `module.decoration.transform` | [Transform](../design-families.md#transform) |
| `module.decoration.transition` | [Transition](../design-families.md#transition) |
| `module.decoration.zIndex` | [Z-index](../design-families.md#z-index) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `module.advanced.innerShadow` | — | onoff |  | desktop | · | D4 `inner_shadow` |
| `module.advanced.type` | — | text |  | desktop | · | D4 `fullwidth`, `specialty` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `column1.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `column2.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `column3.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.dividers.bottom` | [Dividers](../design-families.md#dividers) |
| `module.advanced.dividers.top` | [Dividers](../design-families.md#dividers) |
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.gutter` | [Gutter](../design-families.md#gutter) |
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.link` | [Link](../design-families.md#link) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |
| `module.advanced.text` | [Text](../design-families.md#text) |
| `module.advanced.text.text` | [Text](../design-families.md#text) |
| `module.advanced.text.textShadow` | [Text](../design-families.md#text) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `css` | `after` | text |  | R | hover, sticky | D4 `custom_css_after` |
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `column_1_after` | text |  | R | hover, sticky | D4 `custom_css_after_1` |
| `css` | `column_1_before` | text |  | R | hover, sticky | D4 `custom_css_before_1` |
| `css` | `column_1_main` | text |  | R | hover, sticky | D4 `custom_css_main_1` |
| `css` | `column_2_after` | text |  | R | hover, sticky | D4 `custom_css_after_2` |
| `css` | `column_2_before` | text |  | R | hover, sticky | D4 `custom_css_before_2` |
| `css` | `column_2_main` | text |  | R | hover, sticky | D4 `custom_css_main_2` |
| `css` | `column_3_after` | text |  | R | hover, sticky | D4 `custom_css_after_3` |
| `css` | `column_3_before` | text |  | R | hover, sticky | D4 `custom_css_before_3` |
| `css` | `column_3_main` | text |  | R | hover, sticky | D4 `custom_css_main_3` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `globalColorsInfo` | — | json |  | desktop | · | D4 global_colors_info (Conversion::getAttrMap) |
| `locked` | — | onoff |  | desktop | · |  |
| `on` | — | json |  | desktop | · | block-level attr from Conversion::getAttrMap; value shape not documented |
| `open` | — | onoff |  | desktop | · |  |
| `themeBuilderArea` | — | json |  | desktop | · | theme-builder area marker (Conversion::getAttrMap) |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.meta.adminLabel` | [Admin label](../design-families.md#admin-label) |
| `module.meta.meta.forceVisible` | [Meta](../design-families.md#meta) |
| `module.meta.meta.tocListHeading` | [Meta](../design-families.md#meta) |

Legacy, from Divi's Divi 4 conversion map only. They appear only in Divi's conversion outlines: no Divi 5 module code reads them. The validator warns `W5_LEGACY_ATTR` on them (a warning, so that converted pages still validate). Don't write them.

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `columnsBackground` | — | json |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `columns_background` |
| `columnsCss` | — | json |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `columns_css` |
| `columnsCssFields` | — | json |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `columns_css_fields` |
| `columnsPadding` | — | json |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `columns_padding` |
| `content` | — | html |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `content` |
| `nextBackgroundColor` | — | color |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `next_background_color` |
| `prevBackgroundColor` | — | color |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `prev_background_color` |

<details>
<summary>Render defaults (2): what Divi uses when an attribute is unset — don't repeat these</summary>

- `module.advanced.innerShadow` — desktop `"off"`
- `module.meta.adminLabel` — desktop `"Section"`

</details>
