# Pin — et_pb_map_pin

- **Kind:** child
- **Goes inside:** `et_pb_fullwidth_map`, `et_pb_map`
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section fullwidth="on" _builder_version="4.27.9" _module_preset="default"][et_pb_fullwidth_map _builder_version="4.27.9" _module_preset="default"][et_pb_map_pin _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_map_pin][/et_pb_fullwidth_map][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| title | text |  |  | R H | Title |

### Map — `map`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| map_center_map | center_map |  |  | · |  |
| pin_address | text |  |  | · | Map Pin Address |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| pin_address_lat | hidden |  |  | · |  |
| pin_address_lng | hidden |  |  | · |  |
| zoom_level | hidden |  | 18 | · |  |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
