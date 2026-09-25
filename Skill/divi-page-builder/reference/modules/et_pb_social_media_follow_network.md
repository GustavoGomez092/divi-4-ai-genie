# Social Network — et_pb_social_media_follow_network

- **Kind:** child
- **Goes inside:** `et_pb_social_media_follow`
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_social_media_follow _builder_version="4.27.9" _module_preset="default"][et_pb_social_media_follow_network _builder_version="4.27.9" _module_preset="default"][/et_pb_social_media_follow_network][/et_pb_social_media_follow][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Network — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content | hidden |  |  | · | Body |
| skype_action | select | `call`, `chat` | call | · | Skype Button Action |
| skype_url | text |  |  | · | Account Name |
| social_network | select | ``, `amazon`, `bandcamp`, `behance`, `bitbucket`, `buffer`, `codepen`, `deviantart`, `dribbble`, `facebook`, `flikr`, `flipboard`, `foursquare`, `github`, `goodreads` … (51 options; full list in scripts/schema/et_pb_social_media_follow_network.json) |  | · | Social Network |

### Link — `link`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| url | text |  | # | · | Account Link URL |

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

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_follow_button | custom_css |  |  | · | Follow Button:<span>.et_pb_social_media_follow_network_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_social_network_link a.follow_button</span> |
| custom_css_social_icon | custom_css |  |  | · | Social Icon:<span>.et_pb_social_media_follow_network_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_social_network_link a.icon</span> |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Border | (none) | [design-families.md#border](../design-families.md#border) |
| Box shadow | (none) | [design-families.md#box-shadow](../design-families.md#box-shadow) |
| Button | `button_` | [design-families.md#button](../design-families.md#button) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
