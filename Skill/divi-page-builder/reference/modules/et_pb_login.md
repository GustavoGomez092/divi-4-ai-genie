# Login — et_pb_login

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_login`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_login _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_login][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| title | text |  |  | R H | Title |

### Redirect — `redirect`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| current_page_redirect | yes_no_button | `off`, `on` | off | · | Redirect To The Current Page |

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

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |

## Design tab

### Fields — `form_field`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_fields | color-alpha | color |  | R H S | Fields Border Color |
| border_color_all_fields_focus | color-alpha | color |  | R H S | Fields Focus Border Color |
| border_color_bottom_fields | color-alpha | color |  | R H S | Fields Bottom Border Color |
| border_color_bottom_fields_focus | color-alpha | color |  | R H S | Fields Focus Bottom Border Color |
| border_color_left_fields | color-alpha | color |  | R H S | Fields Left Border Color |
| border_color_left_fields_focus | color-alpha | color |  | R H S | Fields Focus Left Border Color |
| border_color_right_fields | color-alpha | color |  | R H S | Fields Right Border Color |
| border_color_right_fields_focus | color-alpha | color |  | R H S | Fields Focus Right Border Color |
| border_color_top_fields | color-alpha | color |  | R H S | Fields Top Border Color |
| border_color_top_fields_focus | color-alpha | color |  | R H S | Fields Focus Top Border Color |
| border_radii_fields | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Fields Rounded Corners |
| border_radii_fields_focus | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Fields Focus Rounded Corners |
| border_style_all_fields | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Border Style |
| border_style_all_fields_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Focus Border Style |
| border_style_bottom_fields | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Bottom Border Style |
| border_style_bottom_fields_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Focus Bottom Border Style |
| border_style_left_fields | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Left Border Style |
| border_style_left_fields_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Focus Left Border Style |
| border_style_right_fields | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Right Border Style |
| border_style_right_fields_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Focus Right Border Style |
| border_style_top_fields | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Top Border Style |
| border_style_top_fields_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Fields Focus Top Border Style |
| border_styles_fields | composite |  |  | · | Fields Border Styles |
| border_styles_fields_focus | composite |  |  | · | Fields Focus Border Styles |
| border_width_all_fields | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Border Width |
| border_width_all_fields_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Focus Border Width |
| border_width_bottom_fields | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Bottom Border Width |
| border_width_bottom_fields_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Focus Bottom Border Width |
| border_width_left_fields | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Left Border Width |
| border_width_left_fields_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Focus Left Border Width |
| border_width_right_fields | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Right Border Width |
| border_width_right_fields_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Focus Right Border Width |
| border_width_top_fields | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Top Border Width |
| border_width_top_fields_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Fields Focus Top Border Width |
| box_shadow_blur_fields | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_fields', {'none': '', 'preset1': '18px', 'preset2': '18px', 'preset3': '18px', 'preset4': '0px', 'preset5': '0px', 'preset6': '18px', 'preset7': '0px'}] | R H S | Box Shadow Blur Strength |
| box_shadow_color_fields | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_fields | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_fields', {'none': '', 'preset1': '0px', 'preset2': '6px', 'preset3': '0px', 'preset4': '10px', 'preset5': '0px', 'preset6': '0px', 'preset7': '10px'}] | R H S | Box Shadow Horizontal Position |
| box_shadow_position_fields | select | `outer`, `inner` | ['box_shadow_style_fields', {'none': 'outer', 'preset1': 'outer', 'preset2': 'outer', 'preset3': 'outer', 'preset4': 'outer', 'preset5': 'outer', 'preset6': 'inner', 'preset7': 'inner'}] | R | Box Shadow Position |
| box_shadow_spread_fields | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_fields', {'none': '', 'preset1': '0px', 'preset2': '0px', 'preset3': '-6px', 'preset4': '0px', 'preset5': '10px', 'preset6': '0px', 'preset7': '0px'}] | R H S | Box Shadow Spread Strength |
| box_shadow_style_fields | select_box_shadow |  | none | · | Fields Box Shadow |
| box_shadow_vertical_fields | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_fields', {'none': '', 'preset1': '2px', 'preset2': '6px', 'preset3': '12px', 'preset4': '10px', 'preset5': '6px', 'preset6': '0px', 'preset7': '10px'}] | R H S | Box Shadow Vertical Position |
| form_field_background_color | color-alpha | color |  | R H S | Fields Background Color |
| form_field_custom_margin | custom_margin | spacing string |  | R H S | Fields Margin |
| form_field_custom_padding | custom_padding | spacing string |  | R H S | Fields Padding |
| form_field_focus_background_color | color-alpha | color |  | R H S | Fields Focus Background Color |
| form_field_focus_text_color | color-alpha | color |  | R H S | Fields Focus Text Color |
| use_focus_border_color | yes_no_button | `off`, `on` | off | · | Use Focus Borders |

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

### Button — `button`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
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
| custom_css_newsletter_button | custom_css |  |  | · | Login Button:<span>.et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login.et_pb_login .et_pb_login_form .et_pb_newsletter_button.et_pb_button</span> |
| custom_css_newsletter_description | custom_css |  |  | · | Login Description:<span>.et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login .et_pb_newsletter_description</span> |
| custom_css_newsletter_fields | custom_css |  |  | · | Login Fields:<span>.et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login .et_pb_newsletter_form input</span> |
| custom_css_newsletter_form | custom_css |  |  | · | Login Form:<span>.et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login .et_pb_newsletter_form</span> |
| custom_css_newsletter_title | custom_css |  |  | · | Login Title:<span> .et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login h2, .et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login h1.et_pb_module_header, .et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login h3.et_pb_module_header, .et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login h4.et_pb_module_header, .et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login h5.et_pb_module_header, .et_pb_login_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_login h6.et_pb_module_header</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Animation | (none) | [design-families.md#animation](../design-families.md#animation) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Button | `button_` | [design-families.md#button](../design-families.md#button) |
| CSS ID & classes | (none) | [design-families.md#css-id-and-classes](../design-families.md#css-id-and-classes) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `body_`, `button_`, `form_field_`, `header_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
