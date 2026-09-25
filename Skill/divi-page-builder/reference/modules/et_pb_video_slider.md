# Video Slider — et_pb_video_slider

- **Kind:** module
- **Goes inside:** column
- **Children:** `et_pb_video_slider_item`
- **CSS selector:** `.et_pb_video_slider%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_video_slider _builder_version="4.27.9" _module_preset="default"][et_pb_video_slider_item _builder_version="4.27.9" _module_preset="default"][/et_pb_video_slider_item][/et_pb_video_slider][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Overlay — `overlay`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_image_overlay | yes_no_button | `on`, `off` | off | R H | Show Image Overlays on Main Video |

### Elements — `elements`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| show_arrows | yes_no_button | `on`, `off` | on | R H | Show Arrows |
| show_thumbnails | select | `on`, `off` | on | R H | Slider Controls |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

## Design tab

### Controls — `colors`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| controls_color | select | `light`, `dark` |  | · | Slider Controls Color |
| font_icon | select_icon | icon string |  | R H S | Icon |
| icon_font_size | range | length: %, em, rem, px, cm, mm… | 96px | R H S | Play Icon Font Size |
| play_icon_color | color-alpha | color |  | R H S | Play Icon Color |
| thumbnail_overlay_color | color-alpha | color |  | R S | Thumbnail Overlay Color |
| use_icon_font_size | yes_no_button | `off`, `on` | off | · | Use Play Icon Font Size |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_arrows | custom_css |  |  | · | Slider Arrows:<span>.et_pb_video_slider.et_pb_video_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et-pb-slider-arrows a</span> |
| custom_css_play_button | custom_css |  |  | · | Play Button:<span>.et_pb_video_slider.et_pb_video_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_video_play</span> |
| custom_css_thumbnail_item | custom_css |  |  | · | Thumbnail Item:<span>.et_pb_video_slider.et_pb_video_slider_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_carousel_item</span> |

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
