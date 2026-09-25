# Design families

Most Divi modules share the same groups of design options. Each group is documented once here.
Field names use `{p}` for a module-specific prefix. For example, the Font family's `{p}_font_size` becomes
`header_font_size`, `body_font_size` or `button_font_size` depending on the module; each module page lists its prefixes.

Columns: **R** responsive (`_tablet`/`_phone` + `_last_edited`), **H** hover (`__hover` + `__hover_enabled`),
**S** sticky (`__sticky` + `__sticky_enabled`). Value grammars are in [value-formats.md](value-formats.md).

<!-- BEGIN GENERATED FAMILIES -->
## Animation
<a id="animation"></a>

Used by 54 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| animation_delay | range |  | 0ms | R | Animation Delay |
| animation_direction | select | `center`, `left`, `right`, `bottom`, `top` | center | R | Animation Direction |
| animation_duration | range |  | 1000ms | R | Animation Duration |
| animation_intensity_flip | range |  | 50% | R | Animation Intensity |
| animation_intensity_fold | range |  | 50% | R | Animation Intensity |
| animation_intensity_roll | range |  | 50% | R | Animation Intensity |
| animation_intensity_slide | range |  | 50% | R | Animation Intensity |
| animation_intensity_zoom | range |  | 50% | R | Animation Intensity |
| animation_repeat | select | `once`, `loop` | once | R | Animation Repeat |
| animation_speed_curve | select | `ease-in-out`, `ease`, `ease-in`, `ease-out`, `linear` | ease-in-out | R | Animation Speed Curve |
| animation_starting_opacity | range |  | 0% | R | Animation Starting Opacity |
| animation_style | select_animation | `none`, `fade`, `slide`, `bounce`, `zoom`, `flip`, `fold`, `roll` | none | · | Animation Style |

## Attributes
<a id="attributes"></a>

Used by 17 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_rel | multiple_checkboxes | `bookmark`, `external`, `nofollow`, `noreferrer`, `noopener` |  | · | Button Relationship |

## Background
<a id="background"></a>

Used by 62 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_background | computed |  |  | R H S |  |
| allow_player_pause | yes_no_button | `off`, `on` | off | R H S | Pause Video When Another Video Plays |
| background_blend | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R H S | Background Image Blend |
| background_color | color-alpha | color |  | R H S | Background Color |
| background_color_gradient_direction | range |  | 180deg | R H S | Gradient Direction |
| background_color_gradient_direction_radial | select | `center`, `top left`, `top`, `top right`, `right`, `bottom right`, `bottom`, `bottom left`, `left` | center | R H S | Gradient Position |
| background_color_gradient_overlays_image | yes_no_button | `off`, `on` | off | R H S | Place Gradient Above Background Image |
| background_color_gradient_repeat | yes_no_button | `off`, `on` | off | R H S | Repeat Gradient |
| background_color_gradient_stops | gradient-stops |  | #2b87da 0%\|#29c4a9 100% | R H S | Gradient Stops |
| background_color_gradient_type | select | `linear`, `circular`, `elliptical`, `conic` | linear | R H S | Gradient Type |
| background_color_gradient_unit | select | `%`, `px`, `em`, `rem`, `ex`, `ch`, `pc`, `pt`, `cm`, `mm`, `in`, `vh`, `vw`, `vmin`, `vmax` | % | R H S | Gradient Unit |
| background_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| background_image | upload | URL |  | R H S | Background Image |
| background_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| background_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| background_mask_aspect_ratio | multiple_buttons | `landscape`, `square`, `portrait` | landscape | R H S | Mask Aspect Ratio |
| background_mask_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R H S | Mask Blend Mode |
| background_mask_color | color-alpha | color | #ffffff | R H S | Mask Color |
| background_mask_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Mask Height |
| background_mask_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Mask Horizontal Offset |
| background_mask_position | select | `top_left`, `top_center`, `top_right`, `center_left`, `center`, `center_right`, `bottom_left`, `bottom_center`, `bottom_right` | center | R H S | Mask Position |
| background_mask_size | select | `stretch`, `cover`, `contain`, `custom` | stretch | R H S | Mask Size |
| background_mask_style | select-mask | `layer-blob`, `arch`, `bean`, `blades`, `caret`, `chevrons`, `corner-blob`, `corner-lake`, `corner-paint`, `corner-pill`, `corner-square`, `diagonal-bars-2`, `diagonal-bars`, `diagonal-pills`, `diagonal` … | layer-blob | R H S | Mask Style |
| background_mask_transform | multiple_buttons | `flip_horizontal`, `flip_vertical`, `rotate_90_degree`, `invert` |  | R H S | Mask Transform |
| background_mask_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Mask Vertical Offset |
| background_mask_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Mask Width |
| background_pattern_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R H S | Pattern Blend Mode |
| background_pattern_color | color-alpha | color | rgba(0,0,0,0.2) | R H S | Pattern Color |
| background_pattern_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Pattern Height |
| background_pattern_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Pattern Horizontal Offset |
| background_pattern_repeat | select | `repeat`, `repeat-x`, `repeat-y`, `space`, `round` | repeat | R H S | Pattern Repeat |
| background_pattern_repeat_origin | select | `top_left`, `top_center`, `top_right`, `center_left`, `center`, `center_right`, `bottom_left`, `bottom_center`, `bottom_right` | top_left | R H S | Pattern Repeat Origin |
| background_pattern_size | select | `initial`, `cover`, `contain`, `stretch`, `custom` | initial | R H S | Pattern Size |
| background_pattern_style | select-pattern | `polka-dots`, `3d-diamonds`, `checkerboard`, `confetti`, `crosses`, `cubes`, `diagonal-stripes-2`, `diagonal-stripes`, `diamonds`, `honeycomb`, `inverted-chevrons-2`, `inverted-chevrons`, `ogees`, `pills`, `pinwheel` … | polka-dots | R H S | Pattern Style |
| background_pattern_transform | multiple_buttons | `flip_horizontal`, `flip_vertical`, `rotate_90_degree`, `invert` |  | R H S | Pattern Transform |
| background_pattern_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Pattern Vertical Offset |
| background_pattern_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Pattern Width |
| background_position | select | `top_left`, `top_center`, `top_right`, `center_left`, `center`, `center_right`, `bottom_left`, `bottom_center`, `bottom_right` | center | R H S | Background Image Position |
| background_repeat | select | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | no-repeat | R H S | Background Image Repeat |
| background_size | select | `cover`, `contain`, `initial`, `stretch`, `custom` | cover | R H S | Background Image Size |
| background_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |
| background_video_height | text |  |  | R H S | Background Video Height |
| background_video_mp4 | upload | URL |  | R H S | Background Video MP4 |
| background_video_pause_outside_viewport | yes_no_button | `off`, `on` | on | R H S | Pause Video While Not In View |
| background_video_webm | upload | URL |  | R H S | Background Video Webm |
| background_video_width | text |  |  | R H S | Background Video Width |
| parallax | yes_no_button | `off`, `on` | off | R H S | Use Parallax Effect |
| parallax_method | select | `on`, `off` | on | R H S | Parallax Method |
| use_background_color_gradient | yes_no_button | `off`, `on` | off | R H S | Use Background Color Gradient |

## Border
<a id="border"></a>

Used by 59 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| border_color_all | color-alpha | color |  | R H S | Border Color |
| border_color_bottom | color-alpha | color |  | R H S | Bottom Border Color |
| border_color_left | color-alpha | color |  | R H S | Left Border Color |
| border_color_right | color-alpha | color |  | R H S | Right Border Color |
| border_color_top | color-alpha | color |  | R H S | Top Border Color |
| border_radii | border-radius | length: %, em, rem, px, cm, mm… |  | R H S | Rounded Corners |
| border_style_all | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Border Style |
| border_style_bottom | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Bottom Border Style |
| border_style_left | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Left Border Style |
| border_style_right | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Right Border Style |
| border_style_top | select | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` |  | R H S | Top Border Style |
| border_styles | composite |  |  | · | Border Styles |
| border_width_all | range | length: em, rem, px, cm, mm, in… |  | R H S | Border Width |
| border_width_bottom | range | length: em, rem, px, cm, mm, in… |  | R H S | Bottom Border Width |
| border_width_left | range | length: em, rem, px, cm, mm, in… |  | R H S | Left Border Width |
| border_width_right | range | length: em, rem, px, cm, mm, in… |  | R H S | Right Border Width |
| border_width_top | range | length: em, rem, px, cm, mm, in… |  | R H S | Top Border Width |

## Box shadow
<a id="box-shadow"></a>

Used by 60 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| box_shadow_blur | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style` | R H S | Box Shadow Blur Strength |
| box_shadow_color | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style` | R H S | Box Shadow Horizontal Position |
| box_shadow_position | select | `outer`, `inner` | depends on `box_shadow_style` | R | Box Shadow Position |
| box_shadow_spread | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style` | R H S | Box Shadow Spread Strength |
| box_shadow_style | select_box_shadow |  | none | · | Box Shadow |
| box_shadow_vertical | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style` | R H S | Box Shadow Vertical Position |

## Button
<a id="button"></a>

Used by 17 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| box_shadow_blur_{p} | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_button` | R H S | Box Shadow Blur Strength |
| box_shadow_color_{p} | color-alpha | color | rgba(0,0,0,0.3) | R H S | Shadow Color |
| box_shadow_horizontal_{p} | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_button` | R H S | Box Shadow Horizontal Position |
| box_shadow_position_{p} | select | `outer`, `inner` | depends on `box_shadow_style_button` | R | Box Shadow Position |
| box_shadow_spread_{p} | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_button` | R H S | Box Shadow Spread Strength |
| box_shadow_style_{p} | select_box_shadow |  | none | · | Button Box Shadow |
| box_shadow_vertical_{p} | range | length: em, rem, px, cm, mm, in… | depends on `box_shadow_style_button` | R H S | Box Shadow Vertical Position |
| custom_{p} | yes_no_button | `off`, `on` | off | · | Use Custom Styles For Button  |

## CSS ID & classes
<a id="css-id-and-classes"></a>

Used by 54 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| module_class | text |  |  | · | CSS Class |
| module_id | text |  |  | · | CSS ID |

## Custom CSS
<a id="custom-css"></a>

Used by 62 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_after | custom_css |  |  | · | After:<span>.et_pb_post_content_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>:after</span> |
| custom_css_before | custom_css |  |  | · | Before:<span>.et_pb_post_content_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>:before</span> |
| custom_css_free_form | custom_css |  |  | · | CSS:<span>.et_pb_post_content_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %></span> |
| custom_css_main_element | custom_css |  |  | · | Main Element:<span>.et_pb_post_content_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %></span> |

## Display conditions
<a id="display-conditions"></a>

Used by 63 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| display_conditions | display_conditions |  |  | · | Display Conditions |

## Filters
<a id="filters"></a>

Used by 62 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| filter_blur | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Blur |
| filter_brightness | range |  | 100% | R H S | Brightness |
| filter_contrast | range |  | 100% | R H S | Contrast |
| filter_hue_rotate | range |  | 0deg | R H S | Hue |
| filter_invert | range |  | 0% | R H S | Invert |
| filter_opacity | range |  | 100% | R H S | Opacity |
| filter_saturate | range |  | 100% | R H S | Saturation |
| filter_sepia | range |  | 0% | R H S | Sepia |
| mix_blend_mode | select | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … | normal | R | Blend Mode |

## Font
<a id="font"></a>

Used by 149 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| {p}_font | font | font string |  | R | Text Font |
| {p}_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Text Text Size |
| {p}_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Text Letter Spacing |
| {p}_line_height | range | length: %, em, rem, px, cm, mm… | 1.7em | R H S | Text Line Height |
| {p}_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Text Text Alignment |
| {p}_text_color | color-alpha | color |  | R H S | Text Text Color |
| {p}_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | depends on `text_text_shadow_style` | R H S | Text Shadow Blur Strength |
| {p}_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Text Shadow Color |
| {p}_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | depends on `text_text_shadow_style` | R H S | Text Shadow Horizontal Length |
| {p}_text_shadow_style | presets_shadow |  | none | · | Text Shadow |
| {p}_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | depends on `text_text_shadow_style` | R H S | Text Shadow Vertical Length |

## Position
<a id="position"></a>

Used by 63 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| horizontal_offset | range |  |  | R H S | Horizontal Offset |
| position_origin_a | position | `top_left`, `top_right`, `bottom_left`, `bottom_right`, `center_left`, `center_center`, `center_right`, `top_center`, `bottom_center` | top_left | R H S | Location |
| position_origin_f | position | `top_left`, `top_right`, `bottom_left`, `bottom_right`, `center_left`, `center_center`, `center_right`, `top_center`, `bottom_center` | top_left | R H S | Location |
| position_origin_r | position | `top_left`, `top_right`, `bottom_left`, `bottom_right` | top_left | R H S | Offset Origin  |
| positioning | select | `none`, `relative`, `absolute`, `fixed` | none | R H S | Position |
| vertical_offset | range |  |  | R H S | Vertical Offset |
| z_index | range |  |  | R H S | Z Index |

## Scroll effects
<a id="scroll-effects"></a>

Used by 61 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| motion_trigger_start | select | `middle`, `top`, `bottom` | middle | · | Motion Effect Trigger |
| scroll_blur | motion |  | 0\|40\|60\|100\|10\|0\|0 | R | Set Blur |
| scroll_blur_enable | yes_no_button | `off`, `on` | off | · | Enable Blur |
| scroll_effects | composite |  |  | · | Scroll Transform Effects |
| scroll_fade | motion |  | 0\|50\|50\|100\|0\|100\|100 | R | Set Fading In and Out |
| scroll_fade_enable | yes_no_button | `off`, `on` | off | · | Enable Fading In and Out |
| scroll_horizontal_motion | motion |  | 0\|50\|50\|100\|4\|0\|-4 | R | Set Horizontal Motion |
| scroll_horizontal_motion_enable | yes_no_button | `off`, `on` | off | · | Enable Horizontal Motion |
| scroll_rotating | motion |  | 0\|50\|50\|100\|90\|0\|0 | R | Set Rotating |
| scroll_rotating_enable | yes_no_button | `off`, `on` | off | · | Enable Rotating |
| scroll_scaling | motion |  | 0\|50\|50\|100\|70\|100\|100 | R | Set Scaling Up and Down |
| scroll_scaling_enable | yes_no_button | `off`, `on` | off | · | Enable Scaling Up and Down |
| scroll_vertical_motion | motion |  | 0\|50\|50\|100\|4\|0\|-4 | R | Set Vertical Motion |
| scroll_vertical_motion_enable | yes_no_button | `off`, `on` | off | · | Enable Vertical Motion |
| sticky_limit_bottom | select | `none`, `body`, `section`, `row`, `column` | none | R | Bottom Sticky Limit |
| sticky_limit_top | select | `none`, `body`, `section`, `row`, `column` | none | R | Top Sticky Limit |
| sticky_offset_bottom | range |  | 0px | R | Sticky Bottom Offset |
| sticky_offset_surrounding | yes_no_button | `on`, `off` | on | R | Offset From Surrounding Sticky Elements |
| sticky_offset_top | range |  | 0px | R | Sticky Top Offset |
| sticky_position | select | `none`, `top`, `bottom`, `top_bottom` | none | R | Sticky Position |
| sticky_transition | yes_no_button | `on`, `off` | on | R | Transition Default and Sticky Styles |

## Sizing
<a id="sizing"></a>

Used by 56 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| height | range |  | auto | R H S | Height |
| max_height | range |  | none | R H S | Max Height |
| max_width | range |  | none | R H S | Max Width |
| min_height | range |  | auto | R H S | Min Height |
| module_alignment | align | `left`, `center`, `right` |  | R | Module Alignment |
| width | range |  | auto | R H S | Width |

## Spacing
<a id="spacing"></a>

Used by 62 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_margin | custom_margin | length: %, em, rem, px, cm, mm… |  | R H S | Margin |
| custom_padding | custom_padding | length: %, em, rem, px, cm, mm… |  | R H S | Padding |

## Text
<a id="text"></a>

Used by 42 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| background_layout | select | `dark`, `light` | dark | R H S | Text Color |
| text_orientation | text_align | `left`, `center`, `right`, `justified` |  | R | Text Alignment |
| text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | depends on `text_shadow_style` | R H S | Text Shadow Blur Strength |
| text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Text Shadow Color |
| text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | depends on `text_shadow_style` | R H S | Text Shadow Horizontal Length |
| text_shadow_style | presets_shadow |  | none | · | Text Shadow |
| text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | depends on `text_shadow_style` | R H S | Text Shadow Vertical Length |

## Transform
<a id="transform"></a>

Used by 63 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| transform_origin | transform |  | 50%\|50% | R S | Transform Origin |
| transform_rotate | transform |  | 0deg\|0deg\|0deg | R S | Transform Rotate |
| transform_scale | transform |  | 100%\|100% | R S | Transform Scale |
| transform_skew | transform |  | 0deg\|0deg | R S | Transform Skew |
| transform_styles | composite |  |  | R H S | Transform |
| transform_translate | transform |  | 0px\|0px | R S | Transform Translate |

## Transitions
<a id="transitions"></a>

Used by 63 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| hover_transition_delay | range |  | 0ms | R | Transition Delay |
| hover_transition_duration | range |  | 300ms | R | Transition Duration |
| hover_transition_speed_curve | select | `ease-in-out`, `ease`, `ease-in`, `ease-out`, `linear` | ease | R | Transition Speed Curve |

## Visibility
<a id="visibility"></a>

Used by 63 module/prefix combinations. `{p}` = the prefix listed on each module page.

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| disabled_on | multiple_checkboxes | `phone`, `tablet`, `desktop` |  | · | Disable on |
| overflow-x | select | ``, `visible`, `scroll`, `hidden`, `auto` |  | R H S | Horizontal Overflow |
| overflow-y | select | ``, `visible`, `scroll`, `hidden`, `auto` |  | R H S | Vertical Overflow |

<!-- END GENERATED FAMILIES -->
