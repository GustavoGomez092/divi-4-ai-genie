# Field — et_pb_contact_field

- **Kind:** child
- **Goes inside:** `et_pb_contact_form`
- **Children:** none
- **CSS selector:** `.et_pb_contact_form_container %%order_class%%.et_pb_contact_field`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_contact_form _builder_version="4.27.9" _module_preset="default"][et_pb_contact_field _builder_version="4.27.9" _module_preset="default"][/et_pb_contact_field][/et_pb_contact_form][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| field_id | text |  |  | · | Field ID |
| field_title | text |  | New Field | R H | Title |

### Field Options — `field_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| allowed_symbols | select | `all`, `letters`, `numbers`, `alphanumeric` | all | · | Allowed Symbols |
| booleancheckbox_options | sortable_list |  |  | · | Options |
| checkbox_checked | hidden |  | off | · | Checked By Default |
| checkbox_options | sortable_list |  |  | · | Options |
| field_type | select | `input`, `email`, `text`, `checkbox`, `radio`, `select` | input | · | Type |
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
| fullwidth_field | yes_no_button | `on`, `off` | off | · | Make Fullwidth |

### Field — `form_field`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| form_field_background_color | color-alpha | color |  | R H S | Field Background Color |
| form_field_focus_background_color | color-alpha | color |  | R H S | Field Focus Background Color |
| form_field_focus_text_color | color-alpha | color |  | R H S | Field Focus Text Color |

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

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Scroll effects: `sticky_limit_bottom`, `sticky_limit_top`, `sticky_offset_bottom`, `sticky_offset_surrounding`, `sticky_offset_top`, `sticky_position`, `sticky_transition`
- Text: `background_layout`, `text_shadow_blur_strength`, `text_shadow_color`, `text_shadow_horizontal_length`, `text_shadow_style`, `text_shadow_vertical_length`
- Visibility: `disabled_on`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
