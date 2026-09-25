# Row — et_pb_row

- **Kind:** structure element
- **Goes inside:** —
- **Children:** `et_pb_column`
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Column Structure — `column_structure`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| column_structure | column-structure | `4_4`, `1_2,1_2`, `1_3,1_3,1_3`, `1_4,1_4,1_4,1_4`, `1_5,1_5,1_5,1_5,1_5`, `1_6,1_6,1_6,1_6,1_6,1_6`, `2_5,3_5`, `3_5,2_5`, `1_3,2_3`, `2_3,1_3`, `1_4,3_4`, `3_4,1_4`, `1_4,1_2,1_4`, `1_5,3_5,1_5`, `1_4,1_4,1_2` … (20 options; full list in scripts/schema/et_pb_row.json) | 4_4 | · | Column Structure |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_background_1 | computed |  |  | · |  |
| __video_background_2 | computed |  |  | · |  |
| __video_background_3 | computed |  |  | · |  |
| __video_background_4 | computed |  |  | · |  |
| __video_background_5 | computed |  |  | · |  |
| __video_background_6 | computed |  |  | · |  |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Row Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Row Link Target |

## Design tab

### Sizing — `width`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| gutter_width | range |  | 3 | H | Gutter Width |
| make_equal | yes_no_button | `off`, `on` | off | · | Equalize Column Heights |
| use_custom_gutter | yes_no_button | `off`, `on` | off | · | Use Custom Gutter Width |

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
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
