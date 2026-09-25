# Person — et_pb_team_member

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_team_member`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_team_member _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_team_member][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| facebook_url | text |  |  | · | Facebook Profile Url |
| linkedin_url | text |  |  | · | LinkedIn Profile Url |
| name | text |  |  | R H | Name |
| position | text |  |  | R H | Position |
| twitter_url | text |  |  | · | X Profile Url |

### Image — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| image_url | upload | URL |  | R H | Image |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |

## Design tab

### Icon — `icon`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| icon_color | color-alpha | color |  | R H S | Icon Color |
| icon_font_size | range | length: %, em, rem, px, cm, mm… | 16px | R H S | Icon Font Size |
| use_icon_font_size | yes_no_button | `off`, `on` | off | · | Use Icon Font Size |

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
| body_link_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['body_link_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Link Text Shadow Blur Strength |
| body_link_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Link Text Shadow Color |
| body_link_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['body_link_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Link Text Shadow Horizontal Length |
| body_link_text_shadow_style | presets_shadow |  | none | · | Link Text Shadow |
| body_link_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['body_link_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Link Text Shadow Vertical Length |
| body_ol_font | font | font string |  | R | Ordered List Font |
| body_ol_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Ordered List Text Size |
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Ordered List Letter Spacing |
| body_ol_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Ordered List Line Height |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Ordered List Text Alignment |
| body_ol_text_color | color-alpha | color |  | R H S | Ordered List Text Color |
| body_ol_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['body_ol_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Ordered List Text Shadow Blur Strength |
| body_ol_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Ordered List Text Shadow Color |
| body_ol_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['body_ol_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Ordered List Text Shadow Horizontal Length |
| body_ol_text_shadow_style | presets_shadow |  | none | · | Ordered List Text Shadow |
| body_ol_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['body_ol_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Ordered List Text Shadow Vertical Length |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_quote_font | font | font string |  | R | Blockquote Font |
| body_quote_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Blockquote Text Size |
| body_quote_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Blockquote Letter Spacing |
| body_quote_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Blockquote Line Height |
| body_quote_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Blockquote Text Alignment |
| body_quote_text_color | color-alpha | color |  | R H S | Blockquote Text Color |
| body_quote_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['body_quote_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Blockquote Text Shadow Blur Strength |
| body_quote_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Blockquote Text Shadow Color |
| body_quote_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['body_quote_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Blockquote Text Shadow Horizontal Length |
| body_quote_text_shadow_style | presets_shadow |  | none | · | Blockquote Text Shadow |
| body_quote_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['body_quote_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Blockquote Text Shadow Vertical Length |
| body_ul_font | font | font string |  | R | Unordered List Font |
| body_ul_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Unordered List Text Size |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Unordered List Letter Spacing |
| body_ul_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Unordered List Line Height |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Unordered List Text Alignment |
| body_ul_text_color | color-alpha | color |  | R H S | Unordered List Text Color |
| body_ul_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['body_ul_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Unordered List Text Shadow Blur Strength |
| body_ul_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Unordered List Text Shadow Color |
| body_ul_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['body_ul_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Unordered List Text Shadow Horizontal Length |
| body_ul_text_shadow_style | presets_shadow |  | none | · | Unordered List Text Shadow |
| body_ul_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['body_ul_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Unordered List Text Shadow Vertical Length |
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
| box_shadow_blur_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '18px', 'preset2': '18px', 'preset3': '18px', 'preset4': '0px', 'preset5': '0px', 'preset6': '18px', 'preset7': '0px'}] | R H S | Box Shadow Blur Strength |
| box_shadow_color_image | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '0px', 'preset2': '6px', 'preset3': '0px', 'preset4': '10px', 'preset5': '0px', 'preset6': '0px', 'preset7': '10px'}] | R H S | Box Shadow Horizontal Position |
| box_shadow_position_image | select | `outer`, `inner` | ['box_shadow_style_image', {'none': 'outer', 'preset1': 'outer', 'preset2': 'outer', 'preset3': 'outer', 'preset4': 'outer', 'preset5': 'outer', 'preset6': 'inner', 'preset7': 'inner'}] | R | Box Shadow Position |
| box_shadow_spread_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '0px', 'preset2': '0px', 'preset3': '-6px', 'preset4': '0px', 'preset5': '10px', 'preset6': '0px', 'preset7': '0px'}] | R H S | Box Shadow Spread Strength |
| box_shadow_style_image | select_box_shadow |  | none | · | Image Box Shadow |
| box_shadow_vertical_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '2px', 'preset2': '6px', 'preset3': '12px', 'preset4': '10px', 'preset5': '6px', 'preset6': '0px', 'preset7': '10px'}] | R H S | Box Shadow Vertical Position |
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Image Blur |
| child_filter_brightness | range |  | 100% | R H S | Image Brightness |
| child_filter_contrast | range |  | 100% | R H S | Image Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Image Hue |
| child_filter_invert | range |  | 0% | R H S | Image Invert |
| child_filter_opacity | range |  | 100% | R H S | Image Opacity |
| child_filter_saturate | range |  | 100% | R H S | Image Saturation |
| child_filter_sepia | range |  | 0% | R H S | Image Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R H | Image Blend Mode |

### Animation — `animation`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| animation | select | `off`, `fade_in`, `left`, `right`, `top`, `bottom` | off | · | Image Animation |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_member_description | custom_css |  |  | · | Member Description:<span>.et_pb_team_member_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_team_member .et_pb_team_member_description</span> |
| custom_css_member_image | custom_css |  |  | · | Member Image:<span>.et_pb_team_member_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_team_member .et_pb_team_member_image</span> |
| custom_css_member_position | custom_css |  |  | · | Member Position:<span>.et_pb_team_member_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_team_member .et_pb_member_position</span> |
| custom_css_member_social_links | custom_css |  |  | · | Member Social Links:<span>.et_pb_team_member_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_team_member .et_pb_member_social_links</span> |
| custom_css_title | custom_css |  |  | · | Title:<span>.et_pb_team_member_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_team_member .et_pb_team_member_description h4</span> |

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
| Font | `body_`, `header_`, `position_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
