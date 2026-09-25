# Fullwidth Post Slider — et_pb_fullwidth_post_slider

- **Kind:** module
- **Goes inside:** fullwidth section
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_slider`

## Minimal valid example

```divi
[et_pb_section fullwidth="on" _builder_version="4.27.9" _module_preset="default"][et_pb_fullwidth_post_slider _builder_version="4.27.9" _module_preset="default"][/et_pb_fullwidth_post_slider][/et_pb_section]
```

## Content tab

### Content — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content_source | select | `off`, `on` | off | R H | Content Display |
| excerpt_length | text |  | 270 | · | Excerpt Length |
| include_categories | categories |  |  | · | Included Categories |
| more_text | text |  | Read More | R H | Button |
| offset_number | text |  | 0 | · | Post Offset Number |
| orderby | select | `date_desc`, `date_asc`, `title_asc`, `title_desc`, `rand` | date_desc | · | Order |
| posts_number | text |  |  | · | Post Count |
| use_current_loop | yes_no_button | `on`, `off` | off | · | Posts For Current Page |
| use_manual_excerpt | yes_no_button | `on`, `off` | on | · | Use Post Excerpts |

### Elements — `elements`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_arrows | yes_no_button | `on`, `off` | on | R H | Show Arrows |
| show_meta | yes_no_button | `on`, `off` | on | R H | Show Post Meta |
| show_more_button | yes_no_button | `on`, `off` | on | R H | Show Read More Button |
| show_pagination | yes_no_button | `on`, `off` | on | R H | Show Controls |

### Featured Image — `featured_image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| image_placement | select | `background`, `left`, `right`, `top`, `bottom` | background | · | Featured Image Placement |
| show_image | yes_no_button | `on`, `off` | on | R H | Show Featured Image |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __posts | computed |  |  | · |  |

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

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |

## Design tab

### Overlay — `overlay`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| bg_overlay_color | color-alpha | color |  | R S | Background Overlay Color |
| text_border_radius | range | length: %, em, rem, px, cm, mm… | 3 | R S | Text Overlay Border Radius |
| text_overlay_color | color-alpha | color |  | R S | Text Overlay Color |
| use_bg_overlay | yes_no_button | `on`, `off` | on | · | Use Background Overlay |
| use_text_overlay | yes_no_button | `off`, `on` |  | · | Use Text Overlay |

### Navigation — `navigation`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| arrows_custom_color | color-alpha | color |  | R H S | Arrow Color |
| dot_nav_custom_color | color-alpha | color |  | R H S | Dot Navigation Color |

### Title Text — `header`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h2 | · | Title Heading Level |

### Body Text — `body`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_fullwidth_post_slider.json) | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

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
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Image Blur |
| child_filter_brightness | range |  | 100% | R H S | Image Brightness |
| child_filter_contrast | range |  | 100% | R H S | Image Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Image Hue |
| child_filter_invert | range |  | 0% | R H S | Image Invert |
| child_filter_opacity | range |  | 100% | R H S | Image Opacity |
| child_filter_saturate | range |  | 100% | R H S | Image Saturation |
| child_filter_sepia | range |  | 0% | R H S | Image Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema/et_pb_fullwidth_post_slider.json) | normal | R H | Image Blend Mode |

### Sizing — `width`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content_max_width | range |  | 1080px | R H S | Content Max Width |
| content_width | range |  | 80% | R H S | Content Width |

### Animation — `animation`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| auto | yes_no_button | `off`, `on` | off | · | Automatic Animation |
| auto_ignore_hover | yes_no_button | `off`, `on` | off | · | Continue Automatic Slide on Hover |
| auto_speed | text |  | 7000 | · | Automatic Animation Speed (in ms) |

## Advanced tab

### Visibility — `visibility`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_content_on_mobile | yes_no_button | `on`, `off` | on | · | Show Content On Mobile |
| show_cta_on_mobile | yes_no_button | `on`, `off` | on | · | Show CTA On Mobile |
| show_image_video_mobile | yes_no_button | `off`, `on` | off | · | Show Image On Mobile |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_slide_active_controller | custom_css |  |  | · | Slide Active Controller:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider .et-pb-controllers .et-pb-active-control</span> |
| custom_css_slide_arrows | custom_css |  |  | · | Slide Arrows:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider .et-pb-slider-arrows a</span> |
| custom_css_slide_button | custom_css |  |  | · | Slide Button:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider.et_pb_slider a.et_pb_more_button.et_pb_button</span> |
| custom_css_slide_controllers | custom_css |  |  | · | Slide Controllers:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider .et-pb-controllers</span> |
| custom_css_slide_description | custom_css |  |  | · | Slide Description:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider .et_pb_slide_description</span> |
| custom_css_slide_image | custom_css |  |  | · | Slide Image:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider .et_pb_slide_image</span> |
| custom_css_slide_meta | custom_css |  |  | · | Slide Meta:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider .et_pb_slide_description .post-meta</span> |
| custom_css_slide_title | custom_css |  |  | · | Slide Title:<span>.et_pb_fullwidth_post_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_slider .et_pb_slide_description .et_pb_slide_title</span> |

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
| Font | `body_`, `body_link_`, `body_ol_`, `body_quote_`, `body_ul_`, `header_`, `meta_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
