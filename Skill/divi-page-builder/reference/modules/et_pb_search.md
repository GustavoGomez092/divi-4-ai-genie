# Search — et_pb_search

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_search _builder_version="4.27.9" _module_preset="default"][/et_pb_search][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Exceptions — `exceptions`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| exclude_pages | yes_no_button | `off`, `on` |  | · | Exclude Pages |
| exclude_posts | yes_no_button | `off`, `on` | off | · | Exclude Posts |
| include_categories | categories |  |  | · | Exclude Categories |

### Elements — `elements`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_button | yes_no_button | `on`, `off` | on | R H | Show Button |

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| placeholder | text |  |  | R H | Input Placeholder |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

## Design tab

### Button Text — `button`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_color | color-alpha | color |  | R H S | Button and Border Color |

### Field — `form_field`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| form_field_background_color | color-alpha | color |  | R H S | Field Background Color |
| form_field_focus_background_color | color-alpha | color |  | R H S | Field Focus Background Color |
| form_field_focus_text_color | color-alpha | color |  | R H S | Field Focus Text Color |
| placeholder_color | color-alpha | color |  | R H S | Placeholder Color |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_button | custom_css |  |  | · | Button:<span>.et_pb_search_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> input.et_pb_searchsubmit</span> |
| custom_css_input_field | custom_css |  |  | · | Input Field:<span>.et_pb_search_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> input.et_pb_s</span> |

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
| Font | `button_`, `form_field_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
