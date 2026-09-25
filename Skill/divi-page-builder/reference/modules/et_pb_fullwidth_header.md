# Fullwidth Header — et_pb_fullwidth_header

- **Kind:** module
- **Goes inside:** fullwidth section
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section fullwidth="on" _builder_version="4.27.9" _module_preset="default"][et_pb_fullwidth_header _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_fullwidth_header][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_one_text | text |  |  | R H | Button #1 |
| button_two_text | text |  |  | R H | Button #2 |
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| subhead | text |  |  | R H | Subtitle |
| title | text |  |  | R H | Title |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_one_url | text |  |  | · | Button #1 Link URL |
| button_two_url | text |  |  | · | Button #2 Link URL |
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |

### Images — `images`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_image_url | upload | URL |  | R H | Header Image |
| logo_image_url | upload | URL |  | R H | Logo Image |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content_font_color | hidden |  |  | · |  |
| subhead_font_color | hidden |  |  | · |  |
| title_font_color | hidden |  |  | · |  |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

### Background — `background`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_button_one_bg | computed |  |  | R H S |  |
| __video_button_two_bg | computed |  |  | R H S |  |
| button_one_bg_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| button_one_bg_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| button_one_bg_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| button_one_bg_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |
| button_two_bg_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| button_two_bg_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| button_two_bg_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| button_two_bg_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |

## Design tab

### Layout — `layout`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_fullscreen | yes_no_button | `off`, `on` | off | · | Make Fullscreen |
| text_orientation | text_align | `left`, `center`, `right` | left | · | Text &amp; Logo Alignment |

### Scroll Down Icon — `scroll_down`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_scroll_down | yes_no_button | `off`, `on` | off | · | Show Scroll Down Button |
| scroll_down_icon | select_icon | icon string | ; | R | Icon |
| scroll_down_icon_color | color-alpha | color |  | R H S | Scroll Down Icon Color |
| scroll_down_icon_size | range | length: %, em, rem, px, cm, mm… | 50px | R H S | Scroll Down Icon Size |

### Overlay — `overlay`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| background_overlay_color | color-alpha | color |  | R H S | Background Overlay Color |

### Text — `text`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content_orientation | select | `center`, `bottom` | center | · | Text Vertical Alignment |

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
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema/et_pb_fullwidth_header.json) | normal | R H | Image Blend Mode |
| image_orientation | select | `center`, `bottom` | center | · | Image Alignment |

### Sizing — `width`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content_max_width | range | length: %, em, rem, px, cm, mm… | 100% | R | Content Width |

### Title Text — `title`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| title_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h1 | · | Title Heading Level |

### Body Text — `content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| content_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| content_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_fullwidth_header.json) | decimal | R | Ordered List Style Type |
| content_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| content_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| content_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| content_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| content_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

## Advanced tab

### Attributes — `attributes`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_one_rel | multiple_checkboxes | `bookmark`, `external`, `nofollow`, `noreferrer`, `noopener` |  | · | Button One Relationship |
| button_two_rel | multiple_checkboxes | `bookmark`, `external`, `nofollow`, `noreferrer`, `noopener` |  | · | Button Two Relationship |
| image_alt_text | text |  |  | · | Header Image Alternative Text |
| image_title | text |  |  | · | Header Image Title |
| logo_alt_text | text |  |  | · | Logo Image Alternative Text |
| logo_title | text |  |  | · | Logo Image Title |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_button_1 | custom_css |  |  | · | Button One:<span>.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .header-content-container .header-content .et_pb_button_one.et_pb_button</span> |
| custom_css_button_2 | custom_css |  |  | · | Button Two:<span>.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .header-content-container .header-content .et_pb_button_two.et_pb_button</span> |
| custom_css_content | custom_css |  |  | · | Body:<span> .et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_fullwidth_header .et_pb_header_content_wrapper</span> |
| custom_css_header_container | custom_css |  |  | · | Header Container:<span>.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_fullwidth_header_container</span> |
| custom_css_header_image | custom_css |  |  | · | Header Image:<span>.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_fullwidth_header_container .header-image img</span> |
| custom_css_logo | custom_css |  |  | · | Logo:<span>.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .header-content img.header-logo</span> |
| custom_css_scroll_button | custom_css |  |  | · | Scroll Down Button:<span>.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_fullwidth_header_scroll a .et-pb-icon</span> |
| custom_css_subtitle | custom_css |  |  | · | Subtitle:<span>.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .header-content .et_pb_fullwidth_header_subhead</span> |
| custom_css_title | custom_css |  |  | · | Title:<span> .et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .header-content h1,.et_pb_fullwidth_header_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .header-content .et_pb_module_header</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Animation | (none) | [design-families.md#animation](../design-families.md#animation) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Button | `button_one_`, `button_two_` | [design-families.md#button](../design-families.md#button) |
| CSS ID & classes | (none) | [design-families.md#css-id-and-classes](../design-families.md#css-id-and-classes) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `content_`, `content_link_`, `content_ol_`, `content_quote_`, `content_ul_`, `subhead_`, `title_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Button (`button_one_`): `button_one_alignment`
- Button (`button_two_`): `button_two_alignment`

## Gotchas

- Always set `background_color` explicitly (a token color; over a `background_image`, a color or an `rgba()` overlay you chose): left unset, Divi's default teal `#7EBEC5` shows.
- The title renders at `title_level`, default `h1`: a closing/secondary fullwidth header needs `title_level="h2"`, or the page gets a second H1 (`E_MULTIPLE_H1`).

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
