# Accordion — et_pb_accordion

- **Kind:** module
- **Goes inside:** column
- **Children:** `et_pb_accordion_item`
- **CSS selector:** `%%order_class%%.et_pb_accordion`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_accordion _builder_version="4.27.9" _module_preset="default"][et_pb_accordion_item _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_accordion_item][/et_pb_accordion][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Toggle Icon — `extended_icon`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| toggle_icon | select_icon | icon string |  | R H S | Icon |

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

### Title Text — `toggle`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| open_toggle_text_color | color-alpha | color |  | R H S | Open Title Text Color |
| toggle_level | multiple_buttons | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | h5 | · | Title Heading Level |

### Toggle — `toggle_layout`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| closed_toggle_background_color | color-alpha | color |  | R H S | Closed Toggle Background Color |
| open_toggle_background_color | color-alpha | color |  | R H S | Open Toggle Background Color |

### Icon — `icon`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| icon_color | color-alpha | color |  | R H S | Icon Color |
| icon_font_size | range |  | 16px | R H S | Icon Font Size |
| use_icon_font_size | yes_no_button | `off`, `on` | off | · | Use Icon Font Size |

### Body Text — `body`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_accordion.json) | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

## Advanced tab

### Scroll Effects — `scroll_effects`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| enable_grid_motion | yes_no_button | `off`, `on` | off | · | Apply Motion Effects To Child Elements |

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_open_toggle | custom_css |  |  | · | Open Toggle:<span>.et_pb_accordion_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_accordion .et_pb_toggle_open</span> |
| custom_css_toggle | custom_css |  |  | · | Toggle:<span>.et_pb_accordion_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_accordion .et_pb_toggle</span> |
| custom_css_toggle_content | custom_css |  |  | · | Toggle Content:<span>.et_pb_accordion_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_accordion .et_pb_toggle_content</span> |
| custom_css_toggle_icon | custom_css |  |  | · | Toggle Icon:<span>.et_pb_accordion_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_accordion .et_pb_toggle_title:before</span> |
| custom_css_toggle_title | custom_css |  |  | · | Toggle Title:<span>.et_pb_accordion_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_accordion .et_pb_toggle_title</span> |

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
| Font | `body_`, `body_link_`, `body_ol_`, `body_quote_`, `body_ul_`, `closed_toggle_`, `toggle_` | [design-families.md#font](../design-families.md#font) |
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
