# Slide — et_pb_slide

- **Kind:** child
- **Goes inside:** `et_pb_fullwidth_slider`, `et_pb_slider`
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section fullwidth="on" _builder_version="4.27.9" _module_preset="default"][et_pb_fullwidth_slider _builder_version="4.27.9" _module_preset="default"][et_pb_slide _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_slide][/et_pb_fullwidth_slider][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_text | text |  |  | R H | Button |
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| heading | text |  |  | R H | Title |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_link | text |  | # | · | Button Link URL |
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |
| url_new_window | select | `off`, `on` | off | · | Button Link Target |

### Image &amp; Video — `image_video`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| image | upload | URL |  | R H | Image |
| video_url | upload | URL |  | R H | Video |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_title | text |  |  | · | Admin Label |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_embed | computed |  |  | · |  |

### Background — `background`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_button_bg | computed |  |  | R H S |  |
| button_bg_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| button_bg_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| button_bg_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| button_bg_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |

## Design tab

### Overlay — `overlay`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| bg_overlay_color | color-alpha | color |  | R S | Background Overlay Color |
| text_border_radius | range | length: %, em, rem, px, cm, mm… | 3 | R S | Text Overlay Border Radius |
| text_overlay_color | color-alpha | color |  | R S | Text Overlay Color |
| use_bg_overlay | yes_no_button | `off`, `on` |  | · | Use Background Overlay |
| use_text_overlay | yes_no_button | `off`, `on` |  | · | Use Text Overlay |

### Image — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| alignment | select | `center`, `bottom` | center | · | Image Alignment |
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
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Image Blur |
| child_filter_brightness | range |  | 100% | R H S | Image Brightness |
| child_filter_contrast | range |  | 100% | R H S | Image Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Image Hue |
| child_filter_invert | range |  | 0% | R H S | Image Invert |
| child_filter_opacity | range |  | 100% | R H S | Image Opacity |
| child_filter_saturate | range |  | 100% | R H S | Image Saturation |
| child_filter_sepia | range |  | 0% | R H S | Image Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema/et_pb_slide.json) | normal | R H | Image Blend Mode |

### Navigation — `navigation`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| arrows_custom_color | color-alpha | color |  | R H S | Arrow Color |
| dot_nav_custom_color | color-alpha | color |  | R H S | Dot Navigation Color |

### Title Text — `header`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` |  | · | Title Heading Level |

### Body Text — `body`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_slide.json) | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

## Advanced tab

### Attributes — `attributes`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| image_alt | text |  |  | · | Image Alternative Text |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_slide_button | custom_css |  |  | · | Slide Button:<span>.et_pb_slide_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slide .et_pb_container a.et_pb_more_button.et_pb_button</span> |
| custom_css_slide_container | custom_css |  |  | · | Slide Description Container:<span>.et_pb_slide_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_container</span> |
| custom_css_slide_description | custom_css |  |  | · | Slide Description:<span>.et_pb_slide_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_slide_description</span> |
| custom_css_slide_image | custom_css |  |  | · | Slide Image:<span>.et_pb_slide_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_slide_image</span> |
| custom_css_slide_title | custom_css |  |  | · | Slide Title:<span>.et_pb_slide_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_slide_description .et_pb_slide_title</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Attributes | (none) | [design-families.md#attributes](../design-families.md#attributes) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Button | `button_` | [design-families.md#button](../design-families.md#button) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `body_`, `body_link_`, `body_ol_`, `body_quote_`, `body_ul_`, `header_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Position: `horizontal_offset`, `position_origin_a`, `position_origin_f`, `position_origin_r`, `positioning`, `vertical_offset`
- Sizing: `height`, `max_height`, `min_height`, `module_alignment`
- Spacing: `custom_margin`
- Visibility: `disabled_on`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
