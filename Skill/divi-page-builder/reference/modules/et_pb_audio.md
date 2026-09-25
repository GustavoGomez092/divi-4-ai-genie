# Audio — et_pb_audio

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%.et_pb_audio_module`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_audio _builder_version="4.27.9" _module_preset="default"][/et_pb_audio][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Audio — `audio`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| audio | upload | URL |  | · | Audio File |

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| album_name | text |  |  | R H | Album |
| artist_name | text |  |  | R H | Artist |
| title | text |  |  | R H | Title |

### Image — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| image_url | upload | URL |  | R H | Image |

### Other — `-`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __audio | computed |  |  | · |  |

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

### Title Text — `title`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| title_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h2 | · | Title Heading Level |

### Image — `image`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all_image | color-alpha | color |  | R H S | Image Border Color |
| border_color_bottom_image | color-alpha | color |  | R H S | Image Bottom Border Color |
| border_color_left_image | color-alpha | color |  | R H S | Image Left Border Color |
| border_color_right_image | color-alpha | color |  | R H S | Image Right Border Color |
| border_color_top_image | color-alpha | color |  | R H S | Image Top Border Color |
| border_radii_image | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Image Rounded Corners |
| border_style_all_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Border Style |
| border_style_bottom_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Bottom Border Style |
| border_style_left_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Left Border Style |
| border_style_right_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Right Border Style |
| border_style_top_image | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Image Top Border Style |
| border_styles_image | composite |  |  | · | Image Border Styles |
| border_width_all_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Border Width |
| border_width_bottom_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Bottom Border Width |
| border_width_left_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Left Border Width |
| border_width_right_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Right Border Width |
| border_width_top_image | range | length: em, rem, px, cm, mm, in… |  | R H S | Image Top Border Width |
| box_shadow_blur_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '18px', 'preset2': '18px', 'preset3': '18px', 'preset4': '0px', 'preset5': '0px', 'preset6': '18px', 'preset7': '0px'}] | R H S | Box Shadow Blur Strength |
| box_shadow_color_image | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '0px', 'preset2': '6px', 'preset3': '0px', 'preset4': '10px', 'preset5': '0px', 'preset6': '0px', 'preset7': '10px'}] | R H S | Box Shadow Horizontal Position |
| box_shadow_position_image | select | `outer`, `inner` | ['box_shadow_style_image', {'none': 'outer', 'preset1': 'outer', 'preset2': 'outer', 'preset3': 'outer', 'preset4': 'outer', 'preset5': 'outer', 'preset6': 'inner', 'preset7': 'inner'}] | R | Box Shadow Position |
| box_shadow_spread_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '0px', 'preset2': '0px', 'preset3': '-6px', 'preset4': '0px', 'preset5': '10px', 'preset6': '0px', 'preset7': '0px'}] | R H S | Box Shadow Spread Strength |
| box_shadow_style_image | select_box_shadow |  | none | · | Image Box Shadow |
| box_shadow_vertical_image | range | length: em, rem, px, cm, mm, in… | ['box_shadow_style_image', {'none': '', 'preset1': '2px', 'preset2': '6px', 'preset3': '12px', 'preset4': '10px', 'preset5': '6px', 'preset6': '0px', 'preset7': '10px'}] | R H S | Box Shadow Vertical Position |
| child_filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Image Blur |
| child_filter_brightness | range |  | 100% | R H S | Image Brightness |
| child_filter_contrast | range |  | 100% | R H S | Image Contrast |
| child_filter_hue_rotate | range |  | 0deg | R H S | Image Hue |
| child_filter_invert | range |  | 0% | R H S | Image Invert |
| child_filter_opacity | range |  | 100% | R H S | Image Opacity |
| child_filter_saturate | range |  | 100% | R H S | Image Saturation |
| child_filter_sepia | range |  | 0% | R H S | Image Sepia |
| child_mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R H | Image Blend Mode |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_audio_buttons | custom_css |  |  | · | Player Buttons:<span> .et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .mejs-button.mejs-playpause-button button:before,.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .mejs-button.mejs-volume-button.mejs-mute button:before</span> |
| custom_css_audio_content | custom_css |  |  | · | Audio Content:<span>.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_pb_audio_module_content</span> |
| custom_css_audio_cover_art | custom_css |  |  | · | Audio Cover Art:<span>.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_pb_audio_cover_art</span> |
| custom_css_audio_meta | custom_css |  |  | · | Audio Meta:<span>.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_audio_module_meta</span> |
| custom_css_audio_sliders | custom_css |  |  | · | Player Sliders:<span> .et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_audio_container .mejs-controls .mejs-time-rail .mejs-time-total,.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_audio_container .mejs-controls .mejs-horizontal-volume-slider .mejs-horizontal-volume-total</span> |
| custom_css_audio_sliders_current | custom_css |  |  | · | Player Sliders Current:<span> .et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_audio_container .mejs-controls .mejs-time-rail .mejs-time-current,.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_audio_container .mejs-controls .mejs-time-rail .mejs-time-handle,.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_audio_container .mejs-controls .mejs-horizontal-volume-slider .mejs-horizontal-volume-current,.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_audio_container .mejs-controls .mejs-horizontal-volume-slider .mejs-horizontal-volume-handle</span> |
| custom_css_audio_timer | custom_css |  |  | · | Player Timer:<span>.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .mejs-time.mejs-duration-container .mejs-duration</span> |
| custom_css_audio_title | custom_css |  |  | · | Audio Title:<span>.et_pb_audio_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_audio_module .et_pb_audio_module_content h2</span> |

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
| Font | `caption_`, `title_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
