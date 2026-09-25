# Map — et_pb_map

- **Kind:** module
- **Goes inside:** column
- **Children:** `et_pb_map_pin`
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_map _builder_version="4.27.9" _module_preset="default"][et_pb_map_pin _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_map_pin][/et_pb_map][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Map — `map`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| address | text |  |  | · | Map Center Address |
| google_api_key | text |  |  | · | Google API Key |
| google_maps_script_notice | warning |  |  | · |  |
| map_center_map | center_map |  |  | · |  |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| address_lat | hidden |  |  | · |  |
| address_lng | hidden |  |  | · |  |
| zoom_level | hidden |  | 18 | · |  |

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

### Controls — `controls`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| mobile_dragging | yes_no_button | `on`, `off` | on | · | Draggable On Mobile |
| mouse_wheel | yes_no_button | `on`, `off` | on | · | Mouse Wheel Zoom |

### Map — `child_filters`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Map Blur |
| child_filter_brightness | range |  | 100% | R H S | Map Brightness |
| child_filter_contrast | range |  | 100% | R H S | Map Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Map Hue |
| child_filter_invert | range |  | 0% | R H S | Map Invert |
| child_filter_opacity | range |  | 100% | R H S | Map Opacity |
| child_filter_saturate | range |  | 100% | R H S | Map Saturation |
| child_filter_sepia | range |  | 0% | R H S | Map Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R H | Map Blend Mode |
| grayscale_filter_amount | range |  | 0 | R | Grayscale Filter Amount (%) |
| use_grayscale_filter | yes_no_button | `off`, `on` | off | · | Use Grayscale Filter |

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
