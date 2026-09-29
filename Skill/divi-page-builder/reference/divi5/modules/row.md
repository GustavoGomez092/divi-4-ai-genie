# Row — divi/row

Horizontal layout slot inside a section that holds one or more columns side by side.

- **Block:** `divi/row` (Divi 4: `et_pb_row`)
- **Category:** structure · **scope:** core
- **Goes inside:** `divi/section`
- **Children:** `divi/column`
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eLicensed, insured plumbers at your door in 60 minutes.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/row` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "module": {
    "advanced": {
      "columnStructure": {
        "desktop": {
          "value": "4_4"
        }
      }
    },
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
| `button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.background` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.border` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.boxShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.font` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textEffects` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.sizing` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.spacing` | [Button](../design-families.md#button) |
| `button.decoration.button.innerContent` | [Button](../design-families.md#button) |
| `content.decoration.bodyFont.body.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.body.list` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.body.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.body.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.dropCap.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.dropCap.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.link.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.link.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.link.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.list` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.border` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.list` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.textShadow` | [Body font](../design-families.md#font-body) |
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
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `module.advanced.columnStructure` | — | text |  | desktop | · | D4 `column_structure` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
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

Legacy, from Divi's Divi 4 conversion map only. The validator accepts them so that converted pages validate, but they appear only in Divi's conversion outlines: no Divi 5 module code reads them. Don't write them.

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `backgroundHorizontalOffset1` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_horizontal_offset_1` |
| `backgroundHorizontalOffset2` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_horizontal_offset_2` |
| `backgroundHorizontalOffset3` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_horizontal_offset_3` |
| `backgroundHorizontalOffset4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_horizontal_offset_4` |
| `backgroundHorizontalOffset5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_horizontal_offset_5` |
| `backgroundHorizontalOffset6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_horizontal_offset_6` |
| `backgroundImageHeight1` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_height_1` |
| `backgroundImageHeight2` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_height_2` |
| `backgroundImageHeight3` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_height_3` |
| `backgroundImageHeight4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_height_4` |
| `backgroundImageHeight5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_height_5` |
| `backgroundImageHeight6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_height_6` |
| `backgroundImageWidth1` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_width_1` |
| `backgroundImageWidth2` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_width_2` |
| `backgroundImageWidth3` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_width_3` |
| `backgroundImageWidth4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_width_4` |
| `backgroundImageWidth5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_width_5` |
| `backgroundImageWidth6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_image_width_6` |
| `backgroundVerticalOffset1` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_vertical_offset_1` |
| `backgroundVerticalOffset2` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_vertical_offset_2` |
| `backgroundVerticalOffset3` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_vertical_offset_3` |
| `backgroundVerticalOffset4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_vertical_offset_4` |
| `backgroundVerticalOffset5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_vertical_offset_5` |
| `backgroundVerticalOffset6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `background_vertical_offset_6` |
| `columnPaddingMobile` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `column_padding_mobile` |
| `columns.column-1.background` | `image.url` | image |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `bg_img_1` |
| `columns.column-1.spacing` | `padding.bottom` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_bottom_1` |
| `columns.column-1.spacing` | `padding.left` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_1` |
| `columns.column-1.spacing` | `padding.linkedX` | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_right_link_1` |
| `columns.column-1.spacing` | `padding.linkedY` | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_bottom_link_1` |
| `columns.column-1.spacing` | `padding.right` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_right_1` |
| `columns.column-1.spacing` | `padding.top` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_1` |
| `columns.column-2.background` | `image.url` | image |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `bg_img_2` |
| `columns.column-2.spacing` | `padding.bottom` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_bottom_2` |
| `columns.column-2.spacing` | `padding.left` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_2` |
| `columns.column-2.spacing` | `padding.linkedX` | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_right_link_2` |
| `columns.column-2.spacing` | `padding.linkedY` | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_bottom_link_2` |
| `columns.column-2.spacing` | `padding.right` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_right_2` |
| `columns.column-2.spacing` | `padding.top` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_2` |
| `columns.column-3.background` | `image.url` | image |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `bg_img_3` |
| `columns.column-3.spacing` | `padding.bottom` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_bottom_3` |
| `columns.column-3.spacing` | `padding.left` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_3` |
| `columns.column-3.spacing` | `padding.linkedX` | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_right_link_3` |
| `columns.column-3.spacing` | `padding.linkedY` | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_bottom_link_3` |
| `columns.column-3.spacing` | `padding.right` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_right_3` |
| `columns.column-3.spacing` | `padding.top` | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_3` |
| `columns.column-4.background` | `image.url` | image |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `bg_img_4` |
| `columns.column-5.background` | `image.url` | image |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `bg_img_5` |
| `columns.column-6.background` | `image.url` | image |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `bg_img_6` |
| `content` | — | html |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `content` |
| `customCssAfter1` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_after_1` |
| `customCssAfter2` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_after_2` |
| `customCssAfter3` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_after_3` |
| `customCssAfter4` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_after_4` |
| `customCssAfter5` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_after_5` |
| `customCssAfter6` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_after_6` |
| `customCssBefore1` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_before_1` |
| `customCssBefore2` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_before_2` |
| `customCssBefore3` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_before_3` |
| `customCssBefore4` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_before_4` |
| `customCssBefore5` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_before_5` |
| `customCssBefore6` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_before_6` |
| `customCssMain1` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_main_1` |
| `customCssMain2` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_main_2` |
| `customCssMain3` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_main_3` |
| `customCssMain4` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_main_4` |
| `customCssMain5` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_main_5` |
| `customCssMain6` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `custom_css_main_6` |
| `customPaddingLastEdited` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `custom_padding_last_edited` |
| `padding1LastEdited` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_1_last_edited` |
| `padding1Phone` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_1_phone` |
| `padding1Tablet` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_1_tablet` |
| `padding2LastEdited` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_2_last_edited` |
| `padding2Phone` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_2_phone` |
| `padding2Tablet` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_2_tablet` |
| `padding3LastEdited` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_3_last_edited` |
| `padding3Phone` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_3_phone` |
| `padding3Tablet` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_3_tablet` |
| `padding4LastEdited` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_4_last_edited` |
| `padding4Phone` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_4_phone` |
| `padding4Tablet` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_4_tablet` |
| `padding5LastEdited` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_5_last_edited` |
| `padding5Phone` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_5_phone` |
| `padding5Tablet` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_5_tablet` |
| `padding6LastEdited` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_6_last_edited` |
| `padding6Phone` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_6_phone` |
| `padding6Tablet` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_6_tablet` |
| `paddingBottom4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_bottom_4` |
| `paddingBottom5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_bottom_5` |
| `paddingBottom6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_bottom_6` |
| `paddingLeft4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_4` |
| `paddingLeft5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_5` |
| `paddingLeft6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_6` |
| `paddingLeftRightLink4` | — | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_right_link_4` |
| `paddingLeftRightLink5` | — | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_right_link_5` |
| `paddingLeftRightLink6` | — | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_left_right_link_6` |
| `paddingMobile` | — | text |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `padding_mobile` |
| `paddingRight4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_right_4` |
| `paddingRight5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_right_5` |
| `paddingRight6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_right_6` |
| `paddingTop4` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_4` |
| `paddingTop5` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_5` |
| `paddingTop6` | — | length |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_6` |
| `paddingTopBottomLink4` | — | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_bottom_link_4` |
| `paddingTopBottomLink5` | — | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_bottom_link_5` |
| `paddingTopBottomLink6` | — | onoff |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; style each column on its own `divi/column` block (`module.decoration.*`, `css`); D4 `padding_top_bottom_link_6` |

<details>
<summary>Render defaults (1): what Divi uses when an attribute is unset — don't repeat these</summary>

- `module.meta.adminLabel` — desktop `"Row"`

</details>
