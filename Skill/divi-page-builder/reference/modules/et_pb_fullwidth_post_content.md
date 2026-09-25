# Fullwidth Post Content — et_pb_fullwidth_post_content

- **Kind:** module
- **Goes inside:** fullwidth section
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section fullwidth="on" _builder_version="4.27.9" _module_preset="default"][et_pb_fullwidth_post_content _builder_version="4.27.9" _module_preset="default"][/et_pb_fullwidth_post_content][/et_pb_section]
```

## Content tab

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

## Design tab

### Text — `text`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_fullwidth_post_content.json) | decimal | R | Ordered List Style Type |
| quote_border_color | color-alpha | color |  | R H | Blockquote Border Color |
| quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H | Blockquote Border Weight |
| ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

### Image — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_image | color-alpha | color |  | R H S | Image Border Color |
| border_color_bottom_image | color-alpha | color |  | R H S | Image Bottom Border Color |
| border_color_left_image | color-alpha | color |  | R H S | Image Left Border Color |
| border_color_right_image | color-alpha | color |  | R H S | Image Right Border Color |
| border_color_top_image | color-alpha | color |  | R H S | Image Top Border Color |
| border_radii_image | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Image Rounded Corners |
| border_style_all_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Border Style |
| border_style_bottom_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Bottom Border Style |
| border_style_left_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Left Border Style |
| border_style_right_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Right Border Style |
| border_style_top_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Top Border Style |
| border_styles_image | composite |  |  | · | Image Border Styles |
| border_width_all_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Border Width |
| border_width_bottom_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Bottom Border Width |
| border_width_left_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Left Border Width |
| border_width_right_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Right Border Width |
| border_width_top_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Top Border Width |
| box_shadow_blur_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Blur Strength |
| box_shadow_color_image | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Horizontal Position |
| box_shadow_position_image | select | `outer`, `inner` | depends on `box_shadow_style_image` | R | Box Shadow Position |
| box_shadow_spread_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Spread Strength |
| box_shadow_style_image | select_box_shadow |  | none | · | Image Box Shadow |
| box_shadow_vertical_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Vertical Position |

### Border — `border`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_css | color-alpha | color |  | R H S | Border Color |
| border_color_bottom_css | color-alpha | color |  | R H S | Bottom Border Color |
| border_color_left_css | color-alpha | color |  | R H S | Left Border Color |
| border_color_right_css | color-alpha | color |  | R H S | Right Border Color |
| border_color_top_css | color-alpha | color |  | R H S | Top Border Color |
| border_radii_css | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Rounded Corners |
| border_style_all_css | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Border Style |
| border_style_bottom_css | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Bottom Border Style |
| border_style_left_css | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Left Border Style |
| border_style_right_css | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Right Border Style |
| border_style_top_css | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Top Border Style |
| border_styles_css | composite |  |  | · | Border Styles |
| border_width_all_css | range | length: em, rem, px, cm, mm, in… |  | R H S | Border Width |
| border_width_bottom_css | range | length: em, rem, px, cm, mm, in… |  | R H S | Bottom Border Width |
| border_width_left_css | range | length: em, rem, px, cm, mm, in… |  | R H S | Left Border Width |
| border_width_right_css | range | length: em, rem, px, cm, mm, in… |  | R H S | Right Border Width |
| border_width_top_css | range | length: em, rem, px, cm, mm, in… |  | R H S | Top Border Width |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Animation | (none) | [design-families.md#animation](../design-families.md#animation) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| CSS ID & classes | (none) | [design-families.md#css-id-and-classes](../design-families.md#css-id-and-classes) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `header_`, `header_2_`, `header_3_`, `header_4_`, `header_5_`, `header_6_`, `link_`, `ol_`, `quote_`, `text_`, `ul_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
