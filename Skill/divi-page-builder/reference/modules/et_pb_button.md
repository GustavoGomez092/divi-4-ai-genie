# Button — et_pb_button

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_button _builder_version="4.27.9" _module_preset="default"][/et_pb_button][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Link — `link`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_url | text |  |  | · | Button Link URL |
| url_new_window | select | `off`, `on` | off | · | Button Link Target |

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_text | text |  |  | R H | Button |

### Admin Label — `admin_label`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| admin_label | text |  |  | · | Admin Label |

### background — `background`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| __video_button_bg | computed |  |  | R H S |  |
| button_bg_horizontal_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Horizontal Offset |
| button_bg_image_height | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Height |
| button_bg_image_width | range | length: %, em, rem, px, cm, mm… | auto | R H S | Background Image Width |
| button_bg_vertical_offset | range | length: %, em, rem, px, cm, mm… | 0 | R H S | Background Image Vertical Offset |

## Design tab

### Alignment — `alignment`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_alignment | text_align | `left`, `center`, `right` |  | R | Button Alignment |

### Button — `button`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| button_bg_color | background-field |  | False | R H S | Button Background |
| button_border_color | color-alpha | color |  | R H S | Button Border Color |
| button_border_radius | range | length: %, em, rem, px, cm, mm… | 3 | R H S | Button Border Radius |
| button_border_width | range | length: em, rem, px, cm, mm, in… | 2 | R H S | Button Border Width |
| button_icon | select_icon | icon string |  | R | Button Icon |
| button_icon_color | color-alpha | color |  | R H S | Button Icon Color |
| button_icon_placement | select | `right`, `left` | right | R | Button Icon Placement |
| button_on_hover | yes_no_button | `on`, `off` | on | R | Only Show Icon On Hover for Button |
| button_text_size | range | length: %, em, rem, px, cm, mm… | 20 | R H S | Button Text Size |
| button_use_icon | yes_no_button | `on`, `off` | on | · | Show Button Icon |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Animation | (none) | [design-families.md#animation](../design-families.md#animation) |
| Attributes | (none) | [design-families.md#attributes](../design-families.md#attributes) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Button | `button_` | [design-families.md#button](../design-families.md#button) |
| CSS ID & classes | (none) | [design-families.md#css-id-and-classes](../design-families.md#css-id-and-classes) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `button_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
