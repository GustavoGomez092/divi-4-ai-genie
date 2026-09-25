# Text — et_pb_text

- **Kind:** module
- **Goes inside:** column
- **Children:** none
- **CSS selector:** `%%order_class%%`

## Minimal valid example

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Example text.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Content tab

### Text — `main_content`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| content | tiny_mce | HTML (between the tags) |  | R H | Body |

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

### Text — `text`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| ol_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Ordered List Item Indent |
| ol_position | select | `inside`, `outside` | inside | R | Ordered List Style Position |
| ol_type | select | `decimal`, `armenian`, `cjk-ideographic`, `decimal-leading-zero`, `georgian`, `hebrew`, `hiragana`, `hiragana-iroha`, `katakana`, `katakana-iroha`, `lower-alpha`, `lower-greek`, `lower-latin`, `lower-roman`, `upper-alpha` … | decimal | R | Ordered List Style Type |
| quote_border_color | color-alpha | color |  | R H S | Blockquote Border Color |
| quote_border_weight | range | length: em, rem, px, cm, mm, in… | 5px | R H S | Blockquote Border Weight |
| text_orientation | text_align | `left`, `center`, `right`, `justified` | left | R | Text Alignment |
| ul_item_indent | range | length: %, em, rem, px, cm, mm… | 0px | R | Unordered List Item Indent |
| ul_position | select | `outside`, `inside` | outside | R | Unordered List Style Position |
| ul_type | select | `disc`, `circle`, `square`, `none` | disc | R | Unordered List Style Type |

### Heading Text — `header`

| attribute | type | values | default | R H S | label |
|---|---|---|---|---|---|
| header_2_font | font | font string |  | R | Heading 2 Font |
| header_2_font_size | range | length: %, em, rem, px, cm, mm… | 26px | R H S | Heading 2 Text Size |
| header_2_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Heading 2 Letter Spacing |
| header_2_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Heading 2 Line Height |
| header_2_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Heading 2 Text Alignment |
| header_2_text_color | color-alpha | color |  | R H S | Heading 2 Text Color |
| header_2_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['header_2_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Heading 2 Text Shadow Blur Strength |
| header_2_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Heading 2 Text Shadow Color |
| header_2_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['header_2_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Heading 2 Text Shadow Horizontal Length |
| header_2_text_shadow_style | presets_shadow |  | none | · | Heading 2 Text Shadow |
| header_2_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['header_2_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Heading 2 Text Shadow Vertical Length |
| header_3_font | font | font string |  | R | Heading 3 Font |
| header_3_font_size | range | length: %, em, rem, px, cm, mm… | 22px | R H S | Heading 3 Text Size |
| header_3_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Heading 3 Letter Spacing |
| header_3_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Heading 3 Line Height |
| header_3_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Heading 3 Text Alignment |
| header_3_text_color | color-alpha | color |  | R H S | Heading 3 Text Color |
| header_3_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['header_3_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Heading 3 Text Shadow Blur Strength |
| header_3_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Heading 3 Text Shadow Color |
| header_3_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['header_3_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Heading 3 Text Shadow Horizontal Length |
| header_3_text_shadow_style | presets_shadow |  | none | · | Heading 3 Text Shadow |
| header_3_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['header_3_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Heading 3 Text Shadow Vertical Length |
| header_4_font | font | font string |  | R | Heading 4 Font |
| header_4_font_size | range | length: %, em, rem, px, cm, mm… | 18px | R H S | Heading 4 Text Size |
| header_4_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Heading 4 Letter Spacing |
| header_4_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Heading 4 Line Height |
| header_4_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Heading 4 Text Alignment |
| header_4_text_color | color-alpha | color |  | R H S | Heading 4 Text Color |
| header_4_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['header_4_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Heading 4 Text Shadow Blur Strength |
| header_4_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Heading 4 Text Shadow Color |
| header_4_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['header_4_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Heading 4 Text Shadow Horizontal Length |
| header_4_text_shadow_style | presets_shadow |  | none | · | Heading 4 Text Shadow |
| header_4_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['header_4_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Heading 4 Text Shadow Vertical Length |
| header_5_font | font | font string |  | R | Heading 5 Font |
| header_5_font_size | range | length: %, em, rem, px, cm, mm… | 16px | R H S | Heading 5 Text Size |
| header_5_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Heading 5 Letter Spacing |
| header_5_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Heading 5 Line Height |
| header_5_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Heading 5 Text Alignment |
| header_5_text_color | color-alpha | color |  | R H S | Heading 5 Text Color |
| header_5_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['header_5_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Heading 5 Text Shadow Blur Strength |
| header_5_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Heading 5 Text Shadow Color |
| header_5_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['header_5_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Heading 5 Text Shadow Horizontal Length |
| header_5_text_shadow_style | presets_shadow |  | none | · | Heading 5 Text Shadow |
| header_5_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['header_5_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Heading 5 Text Shadow Vertical Length |
| header_6_font | font | font string |  | R | Heading 6 Font |
| header_6_font_size | range | length: %, em, rem, px, cm, mm… | 14px | R H S | Heading 6 Text Size |
| header_6_letter_spacing | range | length: em, rem, px, cm, mm, in… | 0px | R H S | Heading 6 Letter Spacing |
| header_6_line_height | range | length: %, em, rem, px, cm, mm… | 1em | R H S | Heading 6 Line Height |
| header_6_text_align | text_align | `left`, `center`, `right`, `justify` |  | R | Heading 6 Text Alignment |
| header_6_text_color | color-alpha | color |  | R H S | Heading 6 Text Color |
| header_6_text_shadow_blur_strength | range | length: em, rem, px, cm, mm, in… | ['header_6_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0.3em', 'preset4': '0em', 'preset5': '0em'}] | R H S | Heading 6 Text Shadow Blur Strength |
| header_6_text_shadow_color | color-alpha | color | rgba(0,0,0,0.4) | R H S | Heading 6 Text Shadow Color |
| header_6_text_shadow_horizontal_length | range | length: em, rem, px, cm, mm, in… | ['header_6_text_shadow_style', {'none': '0em', 'preset1': '0em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0em', 'preset5': '0.08em'}] | R H S | Heading 6 Text Shadow Horizontal Length |
| header_6_text_shadow_style | presets_shadow |  | none | · | Heading 6 Text Shadow |
| header_6_text_shadow_vertical_length | range | length: em, rem, px, cm, mm, in… | ['header_6_text_shadow_style', {'none': '0em', 'preset1': '0.1em', 'preset2': '0.08em', 'preset3': '0em', 'preset4': '0.08em', 'preset5': '0.08em'}] | R H S | Heading 6 Text Shadow Vertical Length |

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
| Font | `header_`, `link_`, `ol_`, `quote_`, `text_`, `ul_` | [design-families.md#font](../design-families.md#font) |
| Position | (none) | [design-families.md#position](../design-families.md#position) |
| Scroll effects | (none) | [design-families.md#scroll-effects](../design-families.md#scroll-effects) |
| Sizing | (none) | [design-families.md#sizing](../design-families.md#sizing) |
| Spacing | (none) | [design-families.md#spacing](../design-families.md#spacing) |
| Text | (none) | [design-families.md#text](../design-families.md#text) |
| Transform | (none) | [design-families.md#transform](../design-families.md#transform) |
| Transitions | (none) | [design-families.md#transitions](../design-families.md#transitions) |
| Visibility | (none) | [design-families.md#visibility](../design-families.md#visibility) |

R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). See [value-formats.md](../value-formats.md).
