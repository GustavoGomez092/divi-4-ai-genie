# Contact Form — et_pb_contact_form

- **Kind:** module
- **Goes inside:** column
- **Children:** `et_pb_contact_field`
- **CSS selector:** `%%order_class%%.et_pb_contact_form_container`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_contact_form _builder_version="4.27.9" _module_preset="default"][et_pb_contact_field _builder_version="4.27.9" _module_preset="default"][/et_pb_contact_field][/et_pb_contact_form][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Spam Protection — `spam`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| captcha | yes_no_button | `on`, `off` | on | · | Use Basic Captcha |
| recaptcha_list | select_with_option_groups | `0`, `manage` | 0\|none | · | reCAPTCHA v3 Account |
| recaptcha_min_score | range |  | 0.5 | · | Minimum Score |
| spam_provider | select | `recaptcha` | recaptcha | · | Service Provider |
| use_spam_service | yes_no_button | `on`, `off` | off | · | Use A Spam Protection Service |

### Email — `email`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_message | textarea |  |  | · | Message Pattern |
| email | text |  |  | · | Email Address |

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| submit_button_text | text |  |  | R H | Submit Button |
| success_message | text |  |  | · | Success Message |
| title | text |  |  | R H | Title |

### Redirect — `redirect`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| redirect_url | text |  |  | · | Redirect URL |
| use_redirect | yes_no_button | `off`, `on` | off | · | Enable Redirect URL |

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

### Fields — `form_field`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| form_field_background_color | color-alpha | color |  | R H S | Fields Background Color |
| form_field_custom_margin | custom_margin | spacing string |  | R H S | Fields Margin |
| form_field_custom_padding | custom_padding | spacing string |  | R H S | Fields Padding |
| form_field_focus_background_color | color-alpha | color |  | R H S | Fields Focus Background Color |
| form_field_focus_text_color | color-alpha | color |  | R H S | Fields Focus Text Color |

### Title Text — `title`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| title_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h1 | · | Title Heading Level |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_captcha_field | custom_css |  |  | · | Captcha Field:<span>.et_pb_contact_form_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_contact_form_container input.et_pb_contact_captcha</span> |
| custom_css_captcha_label | custom_css |  |  | · | Captcha Text:<span>.et_pb_contact_form_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_contact_form_container .et_pb_contact_right p</span> |
| custom_css_contact_button | custom_css |  |  | · | Contact Button:<span>.et_pb_contact_form_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_contact_form_container.et_pb_contact_form_container .et_contact_bottom_container .et_pb_contact_submit.et_pb_button</span> |
| custom_css_contact_fields | custom_css |  |  | · | Form Fields:<span>.et_pb_contact_form_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_contact_form_container input</span> |
| custom_css_contact_title | custom_css |  |  | · | Contact Title:<span>.et_pb_contact_form_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_contact_form_container .et_pb_contact_main_title</span> |
| custom_css_text_field | custom_css |  |  | · | Message Field:<span>.et_pb_contact_form_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_contact_form_container textarea.et_pb_contact_message</span> |

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
| Font | `captcha_`, `form_field_`, `title_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Button (`button_`): `button_alignment`
- Font (`captcha_`): `captcha_text_align`
- Text: `background_layout`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
