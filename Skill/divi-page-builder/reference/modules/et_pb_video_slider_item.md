# Video — et_pb_video_slider_item

- **Kind:** child
- **Goes inside:** `et_pb_video_slider`
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_video_slider _builder_version="4.27.9" _module_preset="default"][et_pb_video_slider_item _builder_version="4.27.9" _module_preset="default"][/et_pb_video_slider_item][/et_pb_video_slider][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_title | text |  |  | · | Admin Label |

### Video — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| src | upload | URL |  | R H | Video MP4/URL |
| src_webm | upload | URL |  | R H | Video Webm |

### Overlay — `overlay`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| image_src | upload | URL |  | R H | Image Overlay URL |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __get_oembed | computed |  |  | · |  |
| __is_oembed | computed |  |  | · |  |
| __oembed_thumbnail | computed |  |  | · |  |

## Design tab

### Controls — `arrows_color`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| background_layout | select | `dark`, `light` | dark | R H S | Slider Arrows Color |
| font_icon | select_icon | icon string |  | R H S | Icon |
| icon_font_size | range | length: %, em, rem, px, cm, mm… | 96px | R H S | Play Icon Font Size |
| play_icon_color | color-alpha | color |  | R H S | Play Icon Color |
| use_icon_font_size | yes_no_button | `off`, `on` | off | · | Use Play Icon Font Size |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Scroll effects: `motion_trigger_start`, `scroll_blur`, `scroll_blur_enable`, `scroll_effects`, `scroll_fade`, `scroll_fade_enable`, `scroll_horizontal_motion`, `scroll_horizontal_motion_enable`, `scroll_rotating`, `scroll_rotating_enable`, `scroll_scaling`, `scroll_scaling_enable`, `scroll_vertical_motion`, `scroll_vertical_motion_enable`
- Visibility: `disabled_on`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
