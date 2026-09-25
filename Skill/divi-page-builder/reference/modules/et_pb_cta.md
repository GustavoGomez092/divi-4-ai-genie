# Call To Action — et_pb_cta

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_promo`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_cta _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_cta][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_text | text |  |  | R H | Button |
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| title | text |  |  | R H | Title |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_url | text |  |  | · | Button Link URL |
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |
| url_new_window | select | `off`, `on` | off | · | Button Link Target |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

### Background — `background`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_button_bg | computed |  |  | R H S |  |
| button_bg_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| button_bg_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| button_bg_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| button_bg_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |
| use_background_color | yes_no_button | `on`, `off` | on | R H S | Use Background Color |

## Design tab

### Title Text — `header`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h2 | · | Title Heading Level |

### Body Text — `body`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| body_link_font | font | font string |  | R | Link Font |
| body_link_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Link Text Size |
| body_link_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Link Letter Spacing |
| body_link_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Link Line Height |
| body_link_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Link Text Alignment |
| body_link_text_color | color-alpha | color |  | R H S | Link Text Color |
| body_link_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | depends on `body_link_text_shadow_style` | R H S | Link Text Shadow Blur Strength |
| body_link_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Link Text Shadow Color |
| body_link_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | depends on `body_link_text_shadow_style` | R H S | Link Text Shadow Horizontal Length |
| body_link_text_shadow_style | presets_shadow |  | none | · | Link Text Shadow |
| body_link_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | depends on `body_link_text_shadow_style` | R H S | Link Text Shadow Vertical Length |
| body_ol_font | font | font string |  | R | Ordered List Font |
| body_ol_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Ordered List Text Size |
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Ordered List Letter Spacing |
| body_ol_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Ordered List Line Height |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Ordered List Text Alignment |
| body_ol_text_color | color-alpha | color |  | R H S | Ordered List Text Color |
| body_ol_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | depends on `body_ol_text_shadow_style` | R H S | Ordered List Text Shadow Blur Strength |
| body_ol_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Ordered List Text Shadow Color |
| body_ol_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | depends on `body_ol_text_shadow_style` | R H S | Ordered List Text Shadow Horizontal Length |
| body_ol_text_shadow_style | presets_shadow |  | none | · | Ordered List Text Shadow |
| body_ol_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | depends on `body_ol_text_shadow_style` | R H S | Ordered List Text Shadow Vertical Length |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_quote_font | font | font string |  | R | Blockquote Font |
| body_quote_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Blockquote Text Size |
| body_quote_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Blockquote Letter Spacing |
| body_quote_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Blockquote Line Height |
| body_quote_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Blockquote Text Alignment |
| body_quote_text_color | color-alpha | color |  | R H S | Blockquote Text Color |
| body_quote_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | depends on `body_quote_text_shadow_style` | R H S | Blockquote Text Shadow Blur Strength |
| body_quote_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Blockquote Text Shadow Color |
| body_quote_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | depends on `body_quote_text_shadow_style` | R H S | Blockquote Text Shadow Horizontal Length |
| body_quote_text_shadow_style | presets_shadow |  | none | · | Blockquote Text Shadow |
| body_quote_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | depends on `body_quote_text_shadow_style` | R H S | Blockquote Text Shadow Vertical Length |
| body_ul_font | font | font string |  | R | Unordered List Font |
| body_ul_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Unordered List Text Size |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Unordered List Letter Spacing |
| body_ul_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Unordered List Line Height |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Unordered List Text Alignment |
| body_ul_text_color | color-alpha | color |  | R H S | Unordered List Text Color |
| body_ul_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | depends on `body_ul_text_shadow_style` | R H S | Unordered List Text Shadow Blur Strength |
| body_ul_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Unordered List Text Shadow Color |
| body_ul_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | depends on `body_ul_text_shadow_style` | R H S | Unordered List Text Shadow Horizontal Length |
| body_ul_text_shadow_style | presets_shadow |  | none | · | Unordered List Text Shadow |
| body_ul_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | depends on `body_ul_text_shadow_style` | R H S | Unordered List Text Shadow Vertical Length |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

### Button — `button`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_alignment | text_align | `left`, `center`, `right` |  | R | Button Alignment |
| button_bg_color | background-field |  | False | R H S | Button Background |
| button_border_color | color-alpha | color |  | R H S | Button Border Color |
| button_border_radius | range | length: %, em, rem, px, cm, mm… | 3 | R H S | Button Border Radius |
| button_border_width | range | length: em, rem, px, cm, mm, in… | 2 | R H S | Button Border Width |
| button_custom_margin | custom_margin | spacing string |  | R H S | Button Margin |
| button_custom_padding | custom_padding | spacing string |  | R H S | Button Padding |
| button_icon | select_icon | icon string |  | R | Button Icon |
| button_icon_color | color-alpha | color |  | R H S | Button Icon Color |
| button_icon_placement | select | `right`, `left` | right | R | Button Icon Placement |
| button_on_hover | yes_no_button | `on`, `off` | on | R | Only Show Icon On Hover for Button |
| button_text_size | range | length: %, em, rem, px, cm, mm… | 20 | R H S | Button Text Size |
| button_use_icon | yes_no_button | `on`, `off` | on | · | Show Button Icon |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_promo_button | custom_css |  |  | · | Promo Button:<span>.et_pb_cta_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_promo.et_pb_promo .et_pb_button.et_pb_promo_button</span> |
| custom_css_promo_description | custom_css |  |  | · | Promo Description:<span>.et_pb_cta_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_promo .et_pb_promo_description</span> |
| custom_css_promo_title | custom_css |  |  | · | Promo Title:<span>.et_pb_cta_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_promo .et_pb_promo_description h2</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Animation | (none) | [design-families.md#animation](../design-families.md#animation) |
| Attributes | (none) | [design-families.md#attributes](../design-families.md#attributes) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Button | `button_` | [design-families.md#button](../design-families.md#button) |
| CSS ID & classes | (none) | [design-families.md#css-id-and-classes](../design-families.md#css-id-and-classes) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `body_`, `button_`, `header_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
