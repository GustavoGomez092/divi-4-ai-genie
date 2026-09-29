# Contact Form — divi/contact-form

Customizable contact form that emails submissions and supports captcha and conditional logic.

- **Block:** `divi/contact-form` (Divi 4: `et_pb_contact_form`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** `divi/contact-field`
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h1`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `captchaField` (Captcha Field), `captchaLabel` (Captcha Text), `contactButton` (Contact Button), `contactFields` (Form Fields), `contactTitle` (Contact Title), `freeForm`, `mainElement`, `textField` (Message Field)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/contact-form {"title":{"innerContent":{"desktop":{"value":"Request a site visit"}}},"builderVersion":"5.13.1"} --><!-- wp:divi/contact-field {"fieldItem":{"innerContent":{"desktop":{"value":"Name"}},"advanced":{"id":{"desktop":{"value":"Name"}},"type":{"desktop":{"value":"input"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/contact-form --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/contact-form` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Request a site visit"
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
| `button.innerContent` | `linkTarget` | enum | `on`, `off` | desktop | · | D4 `url_new_window` |
| `button.innerContent` | `linkUrl` | url |  | desktop | · | D4 `button_url` |
| `button.innerContent` | `rel` | enum | list of: `bookmark`, `external`, `nofollow`, `noreferrer`, `noopener` | desktop | · | D4 `button_rel` |
| `button.innerContent` | `text` | text |  | R | hover | D4 `button_text`, `submit_button_text` |
| `email.innerContent` | — | text |  | desktop | · | D4 `custom_message` |
| `redirect.innerContent` | — | url |  | desktop | · | D4 `redirect_url` |
| `title.innerContent` | — | text |  | R | hover | D4 `title` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `button.decoration.background` | [Background](../design-families.md#background) |
| `button.decoration.border` | [Border](../design-families.md#border) |
| `button.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.background` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.border` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.boxShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.font` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textEffects` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.sizing` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.spacing` | [Button](../design-families.md#button) |
| `button.decoration.button.innerContent` | [Button](../design-families.md#button) |
| `button.decoration.font` | [Font](../design-families.md#font) |
| `button.decoration.font.font` | [Font](../design-families.md#font) |
| `button.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `button.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `button.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `button.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `captcha.decoration.font` | [Font](../design-families.md#font) |
| `captcha.decoration.font.font` | [Font](../design-families.md#font) |
| `captcha.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `captcha.decoration.font.textShadow` | [Font](../design-families.md#font) |
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
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
| `module.decoration.border` | [Border](../design-families.md#border) |
| `module.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.disabledOn` | [Disabled on](../design-families.md#disabled-on) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.interactions` | [Interactions](../design-families.md#interactions) |
| `module.decoration.layout` | [Layout](../design-families.md#layout) |
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
| `title.decoration.font` | [Font](../design-families.md#font) |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `checkbox.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_background_color (color-alpha) |
| `checkbox.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active |  |
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
| `email.advanced.receiver` | — | text |  | desktop | · | D4 `email` |
| `field.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `form_field_focus_background_color` |
| `field.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active | D4 `border_radii_form_field_focus` |
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
| `field.advanced.focusUseBorder` | — | onoff |  | R | hover, sticky, focus, checked, active | D4 `use_focus_border_color` |
| `field.advanced.placeholder.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `placeholder_color` |
| `field.advanced.placeholder.font.font` | `letterSpacing` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `lineHeight` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `size` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `module.advanced.showLabels` | — | onoff |  | R | hover |  |
| `module.advanced.successMessage` | — | text |  | desktop | · | D4 `success_message` |
| `module.advanced.uniqueId` | — | text |  | desktop | · | D4 `_unique_id` |
| `radio.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_background_color (color-alpha) |
| `radio.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active |  |
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
| `redirect.advanced.useRedirect` | — | onoff |  | desktop | · | D4 `use_redirect` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.link` | [Link](../design-families.md#link) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |
| `module.advanced.spamProtection` | [Spam protection](../design-families.md#spam-protection) |
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
| `css` | `captchaField` | text |  | R | hover, sticky | D4 `custom_css_captcha_field` |
| `css` | `captchaLabel` | text |  | R | hover, sticky | D4 `custom_css_captcha_label` |
| `css` | `contactButton` | text |  | R | hover, sticky | D4 `custom_css_contact_button` |
| `css` | `contactFields` | text |  | R | hover, sticky | D4 `custom_css_contact_fields` |
| `css` | `contactTitle` | text |  | R | hover, sticky | D4 `custom_css_contact_title` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `textField` | text |  | R | hover, sticky | D4 `custom_css_text_field` |
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
<summary>Render defaults (8): what Divi uses when an attribute is unset — don't repeat these</summary>

- `button.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `button.decoration.sizing` — desktop `{"alignment":"right"}`
- `button.innerContent` — desktop `{"text":"Submit"}`
- `module.advanced.showLabels` — desktop `"off"`
- `module.advanced.spamProtection` — desktop `{"enabled":"off","useBasicCaptcha":"on"}`
- `module.meta.adminLabel` — desktop `"Contact Form"`
- `redirect.advanced.useRedirect` — desktop `"off"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h1"}`

</details>
