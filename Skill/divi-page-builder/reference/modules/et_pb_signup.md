# Email Optin — et_pb_signup

- **Kind:** module
- **Goes inside:** column
- **Children:** `et_pb_signup_custom_field`
- **CSS selector:** `%%order_class%%.et_pb_subscribe`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_signup _builder_version="4.27.9" _module_preset="default"][et_pb_signup_custom_field _builder_version="4.27.9" _module_preset="default"][/et_pb_signup_custom_field][/et_pb_signup][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Email Account — `provider`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| activecampaign_list | select_with_option_groups | `0`, `manage` | 0\|none | · | ActiveCampaign List |
| aweber_list | select_with_option_groups | `0`, `manage` | 0\|none | · | Aweber List |
| campaign_monitor_list | select_with_option_groups | `0`, `manage` | 0\|none | · | CampaignMonitor List |
| constant_contact_list | select_with_option_groups | `0`, `manage` | 0\|none | · | ConstantContact List |
| convertkit_list | select_with_option_groups | `0`, `manage` | 0\|none | · | ConvertKit List |
| emma_list | select_with_option_groups | `0`, `manage` | 0\|none | · | Emma List |
| feedblitz_list | select_with_option_groups | `0`, `manage` | 0\|none | · | Feedblitz List |
| feedburner_uri | text |  |  | · | Feed Title |
| fluentcrm_list | select_with_option_groups | `0`, `manage` | 0\|none | · | FluentCRM List |
| getresponse_list | select_with_option_groups | `0`, `manage` | 0\|none | · | GetResponse List |
| hubspot_list | select_with_option_groups | `0`, `manage` | 0\|none | · | HubSpot List |
| icontact_list | select_with_option_groups | `0`, `manage` | 0\|none | · | iContact List |
| infusionsoft_list | select_with_option_groups | `0`, `manage` | 0\|none | · | Infusionsoft List |
| madmimi_list | select_with_option_groups | `0`, `manage` | 0\|none | · | MadMimi List |
| mailchimp_list | select_with_option_groups | `0`, `manage` | 0\|none | · | MailChimp List |
| mailerlite_list | select_with_option_groups | `0`, `manage` | 0\|none | · | MailerLite List |
| mailpoet_list | select_with_option_groups | `0`, `manage` | 0\|none | · | MailPoet List |
| mailster_list | select_with_option_groups | `0`, `manage` | 0\|none | · | Mailster List |
| ontraport_list | select_with_option_groups | `0`, `manage` | 0\|none | · | Ontraport List |
| provider | select | `activecampaign`, `aweber`, `campaign_monitor`, `constant_contact`, `convertkit`, `emma`, `feedblitz`, `feedburner`, `fluentcrm`, `getresponse`, `hubspot`, `icontact`, `infusionsoft`, `madmimi`, `mailchimp` … (21 options; full list in scripts/schema/et_pb_signup.json) | mailchimp | · | Service Provider |
| salesforce_list | select_with_option_groups | `0`, `manage` | 0\|none | · | SalesForce List |
| sendinblue_list | select_with_option_groups | `0`, `manage` | 0\|none | · | SendinBlue List |

### Fields — `fields`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| first_name_field | yes_no_button | `on`, `off` | on | · | Show First Name Field |
| last_name_field | yes_no_button | `on`, `off` | on | · | Show Last Name Field |
| name_field | yes_no_button | `on`, `off` | off | · | Use Single Name Field |
| name_field_only | yes_no_button | `on`, `off` | on | · | Name |
| use_custom_fields | yes_no_button | `on`, `off` | off | · | Use Custom Fields |
| use_custom_fields_notice | warning |  |  | · |  |

### Success Action — `success_action`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| success_action | select | `message`, `redirect` | message | · | Action |
| success_message | text |  | Success! | · | Message |
| success_redirect_query | multiple_checkboxes | `name`, `last_name`, `email`, `ip_address`, `css_id` |  | · | Redirect URL Query |
| success_redirect_url | text |  |  | · | Redirect URL |

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_text | text |  | Subscribe | R H | Button |
| description | tiny_mce | HTML (between the tags) |  | R H | Body |
| footer_content | tiny_mce | HTML (between the tags) |  | R H | Footer |
| title | text |  |  | R H | Title |

### Spam Protection — `spam`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| recaptcha_list | select_with_option_groups | `0`, `manage` | 0\|none | · | reCAPTCHA v3 Account |
| recaptcha_min_score | range |  | 0.5 | · | Minimum Score |
| spam_provider | select | `recaptcha` | recaptcha | · | Service Provider |
| use_spam_service | yes_no_button | `on`, `off` | off | · | Use A Spam Protection Service |

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

### Layout — `layout`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| email_fullwidth | yes_no_button | `on`, `off` | on | R | Email Fullwidth |
| first_name_fullwidth | yes_no_button | `on`, `off` | on | R | First Name Fullwidth |
| last_name_fullwidth | yes_no_button | `on`, `off` | on | R | Last Name Fullwidth |
| layout | select | `left_right`, `right_left`, `top_bottom`, `bottom_top` | left_right | · | Layout |
| name_fullwidth | yes_no_button | `on`, `off` | on | R | Name Fullwidth |

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
| box_shadow_blur_fields | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_fields` | R H S | Box Shadow Blur Strength |
| box_shadow_color_fields | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_fields | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_fields` | R H S | Box Shadow Horizontal Position |
| box_shadow_position_fields | select | `outer`, `inner` | depends on `box_shadow_style_fields` | R | Box Shadow Position |
| box_shadow_spread_fields | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_fields` | R H S | Box Shadow Spread Strength |
| box_shadow_style_fields | select_box_shadow |  | none | · | Fields Box Shadow |
| box_shadow_vertical_fields | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_fields` | R H S | Box Shadow Vertical Position |
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
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_signup.json) | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

## Advanced tab

### Privacy — `privacy`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| ip_address | yes_no_button | `on`, `off` | on | · | Include IP Address |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_newsletter_button | custom_css |  |  | · | Subscribe Button:<span>.et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe.et_pb_subscribe .et_pb_newsletter_button.et_pb_button</span> |
| custom_css_newsletter_description | custom_css |  |  | · | Opt-in Description:<span>.et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_description</span> |
| custom_css_newsletter_fields | custom_css |  |  | · | Opt-in Form Fields:<span> .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_newsletter_form p input[type="text"], .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_newsletter_form p textarea, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_newsletter_form p select, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_newsletter_form p .input[type="radio"] + label i, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_newsletter_form p .input[type="checkbox"] + label i</span> |
| custom_css_newsletter_form | custom_css |  |  | · | Opt-in Form:<span>.et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_form</span> |
| custom_css_newsletter_title | custom_css |  |  | · | Opt-in Title:<span> .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_description h2, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_description h1.et_pb_module_header, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_description h3.et_pb_module_header, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_description h4.et_pb_module_header, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_description h5.et_pb_module_header, .et_pb_signup_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_subscribe .et_pb_newsletter_description h6.et_pb_module_header</span> |

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
| Font | `body_`, `body_link_`, `body_ol_`, `body_quote_`, `body_ul_`, `form_field_`, `header_`, `result_message_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
