# Tabs — et_pb_tabs

- **Kind:** module
- **Goes inside:** column
- **Children:** `et_pb_tab`
- **CSS selector:** `%%order_class%%.et_pb_tabs`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_tabs _builder_version="4.27.9" _module_preset="default"][et_pb_tab _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_tab][/et_pb_tabs][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

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

### Tab Text — `tab`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| active_tab_background_color | color-alpha | color |  | R H S | Active Tab Background Color |
| active_tab_text_color | color-alpha | color |  | R H S | Active Tab Text Color |
| inactive_tab_background_color | color-alpha | color |  | R H S | Inactive Tab Background Color |

### Body Text — `body`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_tabs.json) | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

## Advanced tab

### Custom CSS — `custom_css`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| custom_css_active_tab | custom_css |  |  | · | Active Tab:<span>.et_pb_tabs_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_tabs .et_pb_tabs_controls li.et_pb_tab_active</span> |
| custom_css_tab | custom_css |  |  | · | Tab:<span>.et_pb_tabs_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_tabs .et_pb_tabs_controls li</span> |
| custom_css_tabs_content | custom_css |  |  | · | Tabs Content:<span>.et_pb_tabs_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_tabs .et_pb_tab</span> |
| custom_css_tabs_controls | custom_css |  |  | · | Tabs Controls:<span>.et_pb_tabs_<%= typeof( module_order ) !== 'undefined' ?  module_order : '<span class="et_pb_module_order_placeholder"></span>' %>.et_pb_tabs .et_pb_tabs_controls</span> |

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
| Font | `body_`, `body_link_`, `body_ol_`, `body_quote_`, `body_ul_`, `tab_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
