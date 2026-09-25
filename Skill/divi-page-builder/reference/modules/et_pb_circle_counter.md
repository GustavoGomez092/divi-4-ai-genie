# Circle Counter — et_pb_circle_counter

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_circle_counter`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_circle_counter _builder_version="4.27.9" _module_preset="default"][/et_pb_circle_counter][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| number | text |  | 0 | R H | Number |
| title | text |  |  | R H | Title |

### Elements — `elements`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| percent_sign | yes_no_button | `on`, `off` | on | R H | Percent Sign |

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

### Circle — `circle`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| bar_bg_color | color-alpha | color | #7EBEC5 | R H S | Circle Color |
| circle_color | color-alpha | color |  | R H S | Circle Background Color |
| circle_color_alpha | range |  | 0.1 | R H S | Circle Background Opacity |

### Title Text — `title`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| title_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h3 | · | Title Heading Level |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_circle_counter_title | custom_css |  |  | · | Circle Counter Title:<span>.et_pb_circle_counter_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_circle_counter h3</span> |
| custom_css_percent | custom_css |  |  | · | Percent Container:<span>.et_pb_circle_counter_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_circle_counter .percent</span> |
| custom_css_percent_text | custom_css |  |  | · | Percent Text:<span>.et_pb_circle_counter_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_circle_counter .percent p</span> |

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
| Font | `number_`, `title_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Font (`number_`): `number_line_height`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
