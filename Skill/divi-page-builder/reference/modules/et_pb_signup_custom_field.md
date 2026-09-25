# Custom Field — et_pb_signup_custom_field

- **Kind:** child
- **Goes inside:** `et_pb_signup`
- **Children:** none
- **CSS selector:** `.et_pb_newsletter_form %%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_signup _builder_version="4.27.9" _module_preset="default"][et_pb_signup_custom_field _builder_version="4.27.9" _module_preset="default"][/et_pb_signup_custom_field][/et_pb_signup][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Field — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| field_id | text |  |  | · | ID |
| field_title | text |  |  | · | Name |

### Field Options — `field_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| allowed_symbols | select | `all`, `letters`, `numbers`, `alphanumeric` | all | · | Allowed Symbols |
| checkbox_checked | hidden |  | off | · | Checked By Default |
| checkbox_options | sortable_list |  |  | · | Options |
| field_type | select | `none`, `input`, `email`, `text`, `checkbox`, `radio`, `select` | none | · | Type |
| hidden | yes_no_button | `on`, `off` | off | · | Hidden Field |
| max_length | range |  | 0 | · | Maximum Length |
| min_length | range |  | 0 | · | Minimum Length |
| radio_options | sortable_list |  |  | · | Options |
| required_mark | yes_no_button | `on`, `off` | on | · | Required Field |
| select_options | sortable_list |  |  | · | Options |

### Conditional Logic — `conditional_logic`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| conditional_logic | yes_no_button | `on`, `off` | off | · | Enable |
| conditional_logic_relation | yes_no_button | `on`, `off` | off | · | Relation |
| conditional_logic_rules | conditional_logic |  |  | · | Rules |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |

## Design tab

### Layout — `layout`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| fullwidth_field | yes_no_button | `on`, `off` | depends on `parent:layout` | · | Make Fullwidth |

### Field — `form_field`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| form_field_background_color | color-alpha | color |  | R H S | Field Background Color |
| form_field_focus_background_color | color-alpha | color |  | R H S | Field Focus Background Color |
| form_field_focus_text_color | color-alpha | color |  | R H S | Field Focus Text Color |

### Border — `border`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_focus | color-alpha | color |  | R H S | Input Focus Border Color |
| border_color_bottom_focus | color-alpha | color |  | R H S | Input Focus Bottom Border Color |
| border_color_left_focus | color-alpha | color |  | R H S | Input Focus Left Border Color |
| border_color_right_focus | color-alpha | color |  | R H S | Input Focus Right Border Color |
| border_color_top_focus | color-alpha | color |  | R H S | Input Focus Top Border Color |
| border_radii_focus | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Input Focus Rounded Corners |
| border_style_all_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Input Focus Border Style |
| border_style_bottom_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Input Focus Bottom Border Style |
| border_style_left_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Input Focus Left Border Style |
| border_style_right_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Input Focus Right Border Style |
| border_style_top_focus | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Input Focus Top Border Style |
| border_styles_focus | composite |  |  | · | Input Focus Border Styles |
| border_width_all_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Input Focus Border Width |
| border_width_bottom_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Input Focus Bottom Border Width |
| border_width_left_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Input Focus Left Border Width |
| border_width_right_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Input Focus Right Border Width |
| border_width_top_focus | range | length: em, rem, px, cm, mm, in… |  | R H S | Input Focus Top Border Width |
| use_focus_border_color | yes_no_button | `off`, `on` | off | · | Use Focus Borders |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `form_field_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
