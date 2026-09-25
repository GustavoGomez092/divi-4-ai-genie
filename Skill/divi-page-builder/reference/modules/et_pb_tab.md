# Tab — et_pb_tab

- **Kind:** child
- **Goes inside:** `et_pb_tabs`
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_tabs _builder_version="4.27.9" _module_preset="default"][et_pb_tab _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_tab][/et_pb_tabs][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content | tiny_mce | HTML (between the tags) |  | R H | Body |
| title | text |  |  | R H | Title |

### Link — `link_options`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| link_option_url | text |  |  | · | Module Link URL |
| link_option_url_new_window | select | `off`, `on` | off | · | Module Link Target |

## Design tab

### Body Text — `body`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| body_ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| body_ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| body_ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … (19 options; full list in scripts/schema/et_pb_tab.json) | decimal | R | Ordered List Style Type |
| body_quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| body_quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| body_ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| body_ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| body_ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

## Shared design families

| family | prefix(es) | reference |
|---|---|---|
| Background | (none) | [design-families.md#background](../design-families.md#background) |
| Custom CSS | (none) | [design-families.md#custom-css](../design-families.md#custom-css) |
| Display conditions | (none) | [design-families.md#display-conditions](../design-families.md#display-conditions) |
| Filters | (none) | [design-families.md#filters](../design-families.md#filters) |
| Font | `body_`, `body_link_`, `body_ol_`, `body_quote_`, `body_ul_`, `tab_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

**Family fields not on this module.** These rows of a linked family's table do not exist here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.

- Font (`tab_`): `tab_text_align`
- Spacing: `custom_margin`
- Visibility: `disabled_on`

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
