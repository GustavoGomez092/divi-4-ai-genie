# Blurb — et_pb_blurb

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_blurb`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_blurb][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| title | text |  |  | R H | Title |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |
| url | text |  |  | · | Title Link URL |
| url_new_window | select | `off`, `on` | off | · | Title Link Target |

### Image &amp; Icon — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| font_icon | select_icon | icon string |  | R H | Icon |
| image | upload | URL |  | R H | Image |
| use_icon | yes_no_button | `off`, `on` | off | · | Use Icon |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

## Design tab

### Image &amp; Icon — `icon_settings`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_image | color-alpha | color |  | R H S | Image/Icon Border Color |
| border_color_bottom_image | color-alpha | color |  | R H S | Image/Icon Bottom Border Color |
| border_color_left_image | color-alpha | color |  | R H S | Image/Icon Left Border Color |
| border_color_right_image | color-alpha | color |  | R H S | Image/Icon Right Border Color |
| border_color_top_image | color-alpha | color |  | R H S | Image/Icon Top Border Color |
| border_radii_image | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Image/Icon Rounded Corners |
| border_style_all_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image/Icon Border Style |
| border_style_bottom_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image/Icon Bottom Border Style |
| border_style_left_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image/Icon Left Border Style |
| border_style_right_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image/Icon Right Border Style |
| border_style_top_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image/Icon Top Border Style |
| border_styles_image | composite |  |  | · | Image/Icon Border Styles |
| border_width_all_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image/Icon Border Width |
| border_width_bottom_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image/Icon Bottom Border Width |
| border_width_left_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image/Icon Left Border Width |
| border_width_right_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image/Icon Right Border Width |
| border_width_top_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image/Icon Top Border Width |
| box_shadow_blur_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Blur Strength |
| box_shadow_color_image | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Horizontal Position |
| box_shadow_position_image | select | `outer`, `inner` | depends on `box_shadow_style_image` | R | Box Shadow Position |
| box_shadow_spread_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Spread Strength |
| box_shadow_style_image | select_box_shadow |  | none | · | Image Box Shadow |
| box_shadow_vertical_image | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_image` | R H S | Box Shadow Vertical Position |
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Image/Icon Blur |
| child_filter_brightness | range |  | 100% | R H S | Image/Icon Brightness |
| child_filter_contrast | range |  | 100% | R H S | Image/Icon Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Image/Icon Hue |
| child_filter_invert | range |  | 0% | R H S | Image/Icon Invert |
| child_filter_opacity | range |  | 100% | R H S | Image/Icon Opacity |
| child_filter_saturate | range |  | 100% | R H S | Image/Icon Saturation |
| child_filter_sepia | range |  | 0% | R H S | Image/Icon Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R H | Image/Icon Blend Mode |
| icon_alignment | align | `left`, `center`, `right` | center | R S | Image/Icon Alignment |
| icon_color | color-alpha | color | #7EBEC5 | R H S | Icon Color |
| icon_placement | select | `top`, `left` | top | R | Image/Icon Placement |
| image_icon_background_color | color-alpha | color |  | R H S | Image/Icon Background Color |
| image_icon_custom_margin | custom_margin | spacing string |  | R H S | Image/Icon Margin |
| image_icon_custom_padding | custom_padding | spacing string |  | R H S | Image/Icon Padding |
| image_icon_width | range | length: %, em, rem, px, cm, mm… |  | R S | Image/Icon Width |

### Sizing — `width`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content_max_width | range | length: %, em, rem, px, cm, mm… | 550px | R H S | Content Width |

### Title Text — `header`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h4 | · | Title Heading Level |

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

### Animation — `animation`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| animation | select | `top`, `left`, `right`, `bottom`, `off` | top | R | Image/Icon Animation |

## Advanced tab

### Attributes — `attributes`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| alt | text |  |  | · | Image Alt Text |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_blurb_content | custom_css |  |  | · | Blurb Content:<span>.et_pb_blurb_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_blurb .et_pb_blurb_content</span> |
| custom_css_blurb_image | custom_css |  |  | · | Blurb Image:<span>.et_pb_blurb_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_blurb .et_pb_main_blurb_image</span> |
| custom_css_blurb_title | custom_css |  |  | · | Blurb Title:<span>.et_pb_blurb_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_blurb .et_pb_module_header</span> |

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
| Font | `body_`, `header_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

## Gotchas

- `use_icon="on"` shows `font_icon`; `use_icon="off"` shows `image`. Set only the one you use.
- The title's heading level is `header_level` (default `h4`); in a services grid use `h3` under an `h2` section heading.
- `icon_placement="top"|"left"` changes the layout; `left` suits compact feature lists.

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
