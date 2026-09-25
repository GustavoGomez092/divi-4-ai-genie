# Post Title — et_pb_post_title

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_post_title _builder_version="4.27.9" _module_preset="default"][/et_pb_post_title][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Elements — `elements`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| author | yes_no_button | `on`, `off` | on | R H | Show Author |
| categories | yes_no_button | `on`, `off` | on | R H | Show Post Categories |
| comments | yes_no_button | `on`, `off` | on | R H | Show Comments Count |
| date | yes_no_button | `on`, `off` | on | R H | Show Date |
| date_format | text |  | M j, Y | · | Date Format |
| featured_image | yes_no_button | `on`, `off` | on | R H | Show Featured Image |
| featured_placement | select | `below`, `above`, `background` | below | · | Featured Image Placement |
| meta | yes_no_button | `on`, `off` | on | R H | Show Meta |
| title | yes_no_button | `on`, `off` | on | R H | Show Title |

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

### Sizing — `width`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| force_fullwidth | yes_no_button | `off`, `on` | on | · | Force Fullwidth |
| image_height | range |  | auto | S | Featured Image Height |
| image_max_height | range |  | none | S | Featured Image Max Height |
| image_max_width | range |  | none | S | Featured Image Max Width |
| image_width | range |  | 100% | S | Featured Image Width |

### Image — `image_settings`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| image_alignment | align | `left`, `center`, `right` | center | · | Image Alignment |

### Text — `text`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| text_background | yes_no_button | `off`, `on` | off | · | Use Text Background Color |
| text_bg_color | color-alpha | color | rgba(255,255,255,0.9) | R H S | Text Background Color |
| text_color | select | `dark`, `light` | dark | H | Text Color |

### Title Text — `title`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| title_all_caps | hidden |  |  | · |  |
| title_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h1 | · | Title Heading Level |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_post_image | custom_css |  |  | · | Featured Image:<span>.et_pb_post_title_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_title_featured_container</span> |
| custom_css_post_meta | custom_css |  |  | · | Meta:<span>.et_pb_post_title_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> .et_pb_title_meta_container</span> |
| custom_css_post_title | custom_css |  |  | · | Title:<span>.et_pb_post_title_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %> h1</span> |

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
| Font | `meta_`, `title_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Text: `background_layout`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
