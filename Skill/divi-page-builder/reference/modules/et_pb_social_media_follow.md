# Social Media Follow — et_pb_social_media_follow

- **Kind:** module
- **Goes inside:** column
- **Children:** `et_pb_social_media_follow_network`
- **CSS selector:** `ul%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_social_media_follow _builder_version="4.27.9" _module_preset="default"][et_pb_social_media_follow_network _builder_version="4.27.9" _module_preset="default"][/et_pb_social_media_follow_network][/et_pb_social_media_follow][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Icon — `icon`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| follow_button | yes_no_button | `off`, `on` | off | R H | Follow Button |
| url_new_window | select | `off`, `on` | on | · | Link Target |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

### Background — `background`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_button_bg | computed |  |  | R H S |  |
| button_bg_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| button_bg_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| button_bg_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| button_bg_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |

## Design tab

### Icon — `icon`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| icon_color | color-alpha | color |  | R H S | Icon Color |
| icon_font_size | range | length: %, em, rem, px, cm, mm… | 16px | R H S | Icon Font Size |
| use_icon_font_size | yes_no_button | `off`, `on` | off | · | Use Custom Icon Size |

### Alignment — `alignment`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| text_orientation | text_align | `left`, `center`, `right` |  | R | Module Alignment |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_follow_button | custom_css |  |  | · | Follow Button:<span>ul.et_pb_social_media_follow_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> li a.follow_button</span> |
| custom_css_social_follow | custom_css |  |  | · | Social Follow:<span>ul.et_pb_social_media_follow_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> li</span> |
| custom_css_social_icon | custom_css |  |  | · | Social Icon:<span>ul.et_pb_social_media_follow_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> li a.icon</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Animation | (none) | [design-families.md#animation](../design-families.md#animation) |
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Button | `button_` | [design-families.md#button](../design-families.md#button) |
| CSS ID & classes | (none) | [design-families.md#css-id-and-classes](../design-families.md#css-id-and-classes) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Button (`button_`): `button_alignment`, `button_icon`, `button_icon_color`, `button_icon_placement`, `button_on_hover`, `button_use_icon`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
