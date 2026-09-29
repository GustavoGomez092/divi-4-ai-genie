# Custom Field — divi/signup-custom-field

An extra input inside an Email Optin module for collecting more than just an email address.

- **Block:** `divi/signup-custom-field` (Divi 4: `et_pb_signup_custom_field`)
- **Category:** child-module · **scope:** core
- **Goes inside:** `divi/signup`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/signup {"title":{"innerContent":{"desktop":{"value":"Seasonal tips"}}},"builderVersion":"5.13.1"} --><!-- wp:divi/signup-custom-field {"fieldItem":{"innerContent":{"desktop":{"value":"Company"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/signup --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/signup-custom-field` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "fieldItem": {
    "innerContent": {
      "desktop": {
        "value": "Company"
      }
    }
  },
  "builderVersion": "5.13.1"
}
```

**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written `"title":{"innerContent":{"desktop":{"value":{"text":"…"}}}}`. **R** = responsive (a value per breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides `value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); the full value model: [value-formats.md](../value-formats.md).

## Content

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `conditionalLogic.innerContent` | — | json |  | desktop | · | D4 `conditional_logic_rules` |
| `fieldItem.innerContent` | — | text |  | R | hover | D4 `field_title` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `checkbox.decoration.background` | [Background](../design-families.md#background) (+ focus, checked, active states) |
| `checkbox.decoration.border` | [Border](../design-families.md#border) (+ focus, checked, active states) |
| `checkbox.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) (+ focus, checked, active states) |
| `checkbox.decoration.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `checkbox.decoration.font.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `checkbox.decoration.font.textEffects` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `checkbox.decoration.font.textShadow` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `checkbox.decoration.icon` | [Icon](../design-families.md#icon) (+ focus, checked, active states) |
| `checkbox.decoration.spacing` | [Spacing](../design-families.md#spacing) (+ focus, checked, active states) |
| `field.decoration.background` | [Background](../design-families.md#background) (+ focus, checked, active states) |
| `field.decoration.border` | [Border](../design-families.md#border) (+ focus, checked, active states) |
| `field.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) (+ focus, checked, active states) |
| `field.decoration.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `field.decoration.font.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `field.decoration.font.textEffects` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `field.decoration.font.textShadow` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `field.decoration.labelFont.font` | [Label font](../design-families.md#font-label) (+ focus, checked, active states) |
| `field.decoration.labelFont.textEffects` | [Label font](../design-families.md#font-label) (+ focus, checked, active states) |
| `field.decoration.labelFont.textShadow` | [Label font](../design-families.md#font-label) (+ focus, checked, active states) |
| `field.decoration.placeholderFont.font` | [Placeholder font](../design-families.md#font-placeholder) (+ focus, checked, active states) |
| `field.decoration.placeholderFont.textEffects` | [Placeholder font](../design-families.md#font-placeholder) (+ focus, checked, active states) |
| `field.decoration.placeholderFont.textShadow` | [Placeholder font](../design-families.md#font-placeholder) (+ focus, checked, active states) |
| `field.decoration.spacing` | [Spacing](../design-families.md#spacing) (+ focus, checked, active states) |
| `fieldItem.decoration.border` | [Border](../design-families.md#border) |
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
| `module.decoration.border` | [Border](../design-families.md#border) |
| `module.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.disabledOn` | [Disabled on](../design-families.md#disabled-on) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.overflow` | [Overflow](../design-families.md#overflow) |
| `module.decoration.position` | [Position](../design-families.md#position) |
| `module.decoration.scroll` | [Scroll](../design-families.md#scroll) |
| `module.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `module.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `module.decoration.sticky` | [Sticky](../design-families.md#sticky) |
| `module.decoration.transform` | [Transform](../design-families.md#transform) |
| `module.decoration.transition` | [Transition](../design-families.md#transition) |
| `module.decoration.zIndex` | [Z-index](../design-families.md#z-index) |
| `radio.decoration.background` | [Background](../design-families.md#background) (+ focus, checked, active states) |
| `radio.decoration.border` | [Border](../design-families.md#border) (+ focus, checked, active states) |
| `radio.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) (+ focus, checked, active states) |
| `radio.decoration.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `radio.decoration.font.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `radio.decoration.font.textEffects` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `radio.decoration.font.textShadow` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `radio.decoration.icon` | [Icon](../design-families.md#icon) (+ focus, checked, active states) |
| `radio.decoration.spacing` | [Spacing](../design-families.md#spacing) (+ focus, checked, active states) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `checkbox.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_background_color (color-alpha) |
| `checkbox.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles` | object |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.all.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.all.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.all.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.bottom.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.bottom.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.bottom.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.left.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.left.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.left.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.right.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.right.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.right.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.top.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.top.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.top.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_text_color (color-alpha) |
| `checkbox.advanced.focus.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `checkbox.advanced.focusUseBorder` | — | onoff |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `letterSpacing` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `lineHeight` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `size` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `conditionalLogic.advanced.enable` | — | onoff |  | desktop | · | D4 `conditional_logic` |
| `conditionalLogic.advanced.relation` | — | onoff |  | desktop | · | D4 `conditional_logic_relation` |
| `field.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `form_field_focus_background_color` |
| `field.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active | D4 `border_radii_form_field_focus` |
| `field.advanced.focus.border` | `styles` | object |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.focus.border` | `styles.all.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_all_form_field_focus` |
| `field.advanced.focus.border` | `styles.all.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_all_form_field_focus` |
| `field.advanced.focus.border` | `styles.all.width` | length |  | R | hover, sticky, focus, checked, active | D4 `border_width_all_form_field_focus` |
| `field.advanced.focus.border` | `styles.bottom.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_bottom_form_field_focus` |
| `field.advanced.focus.border` | `styles.bottom.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_bottom_form_field_focus` |
| `field.advanced.focus.border` | `styles.bottom.width` | length |  | R | hover, sticky, focus, checked, active | D4 `border_width_bottom_form_field_focus` |
| `field.advanced.focus.border` | `styles.left.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_left_form_field_focus` |
| `field.advanced.focus.border` | `styles.left.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_left_form_field_focus` |
| `field.advanced.focus.border` | `styles.left.width` | length |  | R | hover, sticky, focus, checked, active | D4 `border_width_left_form_field_focus` |
| `field.advanced.focus.border` | `styles.right.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_right_form_field_focus` |
| `field.advanced.focus.border` | `styles.right.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_right_form_field_focus` |
| `field.advanced.focus.border` | `styles.right.width` | length |  | R | hover, sticky, focus, checked, active | D4 `border_width_right_form_field_focus` |
| `field.advanced.focus.border` | `styles.top.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_top_form_field_focus` |
| `field.advanced.focus.border` | `styles.top.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_top_form_field_focus` |
| `field.advanced.focus.border` | `styles.top.width` | length |  | R | hover, sticky, focus, checked, active | D4 `border_width_top_form_field_focus` |
| `field.advanced.focus.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `form_field_focus_text_color` |
| `field.advanced.focus.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.focus.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `field.advanced.focusUseBorder` | — | onoff |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `placeholder_color` |
| `field.advanced.placeholder.font.font` | `letterSpacing` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `lineHeight` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `size` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `fieldItem.advanced.allowedSymbols` | — | enum | `all`, `alphanumeric`, `letters`, `numbers` | desktop | · | D4 `allowed_symbols` |
| `fieldItem.advanced.booleanCheckboxOptions` | — | json |  | R | hover, sticky | D4 `booleancheckbox_options` |
| `fieldItem.advanced.checkboxChecked` | — | text |  | desktop | · | D4 `checkbox_checked` |
| `fieldItem.advanced.checkboxOptions` | — | json |  | desktop | · | D4 `checkbox_options` |
| `fieldItem.advanced.fullwidth` | — | onoff |  | desktop | · | D4 `fullwidth_field` |
| `fieldItem.advanced.hidden` | — | onoff |  | desktop | · | D4 `hidden` |
| `fieldItem.advanced.id` | — | text |  | desktop | · | D4 `field_id` |
| `fieldItem.advanced.maxLength` | — | number |  | desktop | · | D4 `max_length` |
| `fieldItem.advanced.minLength` | — | number |  | desktop | · | D4 `min_length` |
| `fieldItem.advanced.predefinedField` | — | text |  | desktop | · | D4 `predefined_field` |
| `fieldItem.advanced.radioOptions` | — | json |  | desktop | · | D4 `radio_options` |
| `fieldItem.advanced.required` | — | onoff |  | desktop | · | D4 `required_mark` |
| `fieldItem.advanced.selectOptions` | — | json |  | desktop | · | D4 `select_options` |
| `fieldItem.advanced.type` | — | enum | `checkbox`, `email`, `input`, `radio`, `select`, `text` | desktop | · | D4 `field_type` |
| `fieldItem.advanced.useFocusBorder` | — | onoff |  | desktop | · | D4 `use_focus_border_color` |
| `radio.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_background_color (color-alpha) |
| `radio.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles` | object |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.all.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.all.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.all.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.bottom.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.bottom.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.bottom.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.left.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.left.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.left.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.right.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.right.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.right.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.top.color` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.top.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.top.width` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_text_color (color-alpha) |
| `radio.advanced.focus.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `radio.advanced.focusUseBorder` | — | onoff |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `letterSpacing` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `lineHeight` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `size` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.link` | [Link](../design-families.md#link) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |
| `module.advanced.text` | [Text](../design-families.md#text) |
| `module.advanced.text.text` | [Text](../design-families.md#text) |
| `module.advanced.text.textShadow` | [Text](../design-families.md#text) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `content` | — | html |  | R | hover, sticky | D4 `content` |
| `css` | `after` | text |  | R | hover, sticky | D4 `custom_css_after` |
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `globalColorsInfo` | — | json |  | desktop | · | D4 global_colors_info (Conversion::getAttrMap) |
| `locked` | — | onoff |  | desktop | · |  |
| `on` | — | json |  | desktop | · | block-level attr from Conversion::getAttrMap; value shape not documented |
| `open` | — | onoff |  | desktop | · |  |
| `themeBuilderArea` | — | json |  | desktop | · | theme-builder area marker (Conversion::getAttrMap) |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.meta.adminLabel` | [Admin label](../design-families.md#admin-label) |
| `module.meta.meta.forceVisible` | [Meta](../design-families.md#meta) |
| `module.meta.meta.tocListHeading` | [Meta](../design-families.md#meta) |

<details>
<summary>Render defaults (6): what Divi uses when an attribute is unset — don't repeat these</summary>

- `fieldItem.advanced.fullwidth` — desktop `"on"`
- `fieldItem.advanced.id` — desktop `""`
- `fieldItem.advanced.required` — desktop `"on"`
- `fieldItem.advanced.type` — desktop `"input"`
- `fieldItem.innerContent` — desktop `"New Field"`
- `module.advanced.html` — desktop `{"elementType":"p"}`

</details>
