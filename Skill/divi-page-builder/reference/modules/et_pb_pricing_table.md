# Pricing Table — et_pb_pricing_table

- **Kind:** child
- **Goes inside:** `et_pb_pricing_tables`
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_pricing_tables _builder_version="4.27.9" _module_preset="default"][et_pb_pricing_table _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_pricing_table][/et_pb_pricing_tables][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_text | text |  |  | R H | Button |
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| currency | text |  |  | R H | Currency |
| per | text |  |  | R H | Frequency |
| subtitle | text |  |  | R H | Subtitle |
| sum | text |  |  | R H | Price |
| title | text |  |  | R H | Title |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_url | text |  |  | · | Button Link URL |
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |
| url_new_window | select | `off`, `on` | off | · | Button Link Target |

### Background — `background`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_button_bg | computed |  |  | R H S |  |
| button_bg_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| button_bg_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| button_bg_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| button_bg_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |

## Design tab

### Layout — `layout`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| featured | yes_no_button | `off`, `on` | off | · | Make This Table Featured |

### Bullet — `bullet`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| bullet_color | color-alpha | color |  | R H S | Bullet Color |

### Price Text — `price`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_price | color-alpha | color |  | R H S | Border Color |
| border_color_bottom_price | color-alpha | color |  | R H S | Bottom Border Color |
| border_color_left_price | color-alpha | color |  | R H S | Left Border Color |
| border_color_right_price | color-alpha | color |  | R H S | Right Border Color |
| border_color_top_price | color-alpha | color |  | R H S | Top Border Color |
| border_radii_price | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Rounded Corners |
| border_style_all_price | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Border Style |
| border_style_bottom_price | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Bottom Border Style |
| border_style_left_price | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Left Border Style |
| border_style_right_price | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Right Border Style |
| border_style_top_price | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Top Border Style |
| border_styles_price | composite |  |  | · | Border Styles |
| border_width_all_price | range | length: em, rem, px, cm, mm, in… |  | R H S | Border Width |
| border_width_bottom_price | range | length: em, rem, px, cm, mm, in… |  | R H S | Bottom Border Width |
| border_width_left_price | range | length: em, rem, px, cm, mm, in… |  | R H S | Left Border Width |
| border_width_right_price | range | length: em, rem, px, cm, mm, in… |  | R H S | Right Border Width |
| border_width_top_price | range | length: em, rem, px, cm, mm, in… |  | R H S | Top Border Width |
| price_background_color | color-alpha | color |  | R H S | Pricing Area Background Color |

### Title Text — `header`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_background_color | color-alpha | color |  | R H S | Table Header Background Color |
| header_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` |  | · | Title Heading Level |

### Body Text — `body`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_pricing_table.json) | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_currency | custom_css |  |  | · | Currency:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_dollar_sign</span> |
| custom_css_frequency | custom_css |  |  | · | Frequency:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_frequency</span> |
| custom_css_price | custom_css |  |  | · | Price:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_et_price</span> |
| custom_css_pricing_button | custom_css |  |  | · | Pricing Button:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_pricing_table_button</span> |
| custom_css_pricing_content | custom_css |  |  | · | Pricing Content:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_pricing_content</span> |
| custom_css_pricing_heading | custom_css |  |  | · | Pricing Heading:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_pricing_heading</span> |
| custom_css_pricing_item | custom_css |  |  | · | Pricing Item:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> ul.et_pb_pricing li</span> |
| custom_css_pricing_item_excluded | custom_css |  |  | · | Excluded Item:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> ul.et_pb_pricing li.et_pb_not_available</span> |
| custom_css_pricing_subtitle | custom_css |  |  | · | Pricing Subtitle:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_pricing_heading .et_pb_best_value</span> |
| custom_css_pricing_title | custom_css |  |  | · | Pricing Title:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_pricing_heading h2</span> |
| custom_css_pricing_top | custom_css |  |  | · | Pricing Top:<span>.et_pb_pricing_table_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_pricing_content_top</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Attributes | (none) | [design-families.md#attributes](../design-families.md#attributes) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Button | `button_` | [design-families.md#button](../design-families.md#button) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `body_`, `body_link_`, `body_ol_`, `body_quote_`, `body_ul_`, `currency_frequency_`, `excluded_`, `header_`, `price_`, `subheader_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Font (`currency_frequency_`): `currency_frequency_text_align`
- Scroll effects: `sticky_limit_bottom`, `sticky_limit_top`, `sticky_offset_bottom`, `sticky_offset_surrounding`, `sticky_offset_top`, `sticky_position`, `sticky_transition`
- Spacing: `custom_margin`
- Text: `background_layout`
- Visibility: `disabled_on`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
