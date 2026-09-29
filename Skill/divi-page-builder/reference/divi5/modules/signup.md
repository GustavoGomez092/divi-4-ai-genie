# Email Optin — divi/signup

Newsletter sign-up form connected to a mailing-list provider for collecting subscribers.

- **Block:** `divi/signup` (Divi 4: `et_pb_signup`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** `divi/signup-custom-field`
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h2`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`, `newsletterButton` (Subscribe Button), `newsletterDescription` (Opt-in Description), `newsletterFields` (Opt-in Form Fields), `newsletterForm` (Opt-in Form), `newsletterTitle` (Opt-in Title)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/signup {"title":{"innerContent":{"desktop":{"value":"Seasonal tips"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/signup` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Seasonal tips"
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
| `button.innerContent` | `rel` | json |  | desktop | · | D4 `button_rel` |
| `button.innerContent` | `text` | text |  | R | hover | D4 `button_text` |
| `content.innerContent` | — | html |  | R | hover | D4 `description` |
| `footerContent.innerContent` | — | html |  | R | hover | D4 `footer_content` |
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
| `button.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `button.decoration.font.font`, not here |
| `button.decoration.font.font` | [Font](../design-families.md#font) |
| `button.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `button.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `button.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `button.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `checkbox.decoration.background` | [Background](../design-families.md#background) (+ focus, checked, active states) |
| `checkbox.decoration.border` | [Border](../design-families.md#border) (+ focus, checked, active states) |
| `checkbox.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) (+ focus, checked, active states) |
| `checkbox.decoration.font` | [Font](../design-families.md#font) (+ focus, checked, active states) — container only: write keys under `checkbox.decoration.font.font`, not here |
| `checkbox.decoration.font.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `checkbox.decoration.font.textEffects` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `checkbox.decoration.font.textShadow` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `checkbox.decoration.icon` | [Icon](../design-families.md#icon) (+ focus, checked, active states) |
| `checkbox.decoration.spacing` | [Spacing](../design-families.md#spacing) (+ focus, checked, active states) |
| `content.decoration.bodyFont.body.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.body.list` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.body.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.body.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.dropCap.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.dropCap.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.link.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.link.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.link.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.list` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ol.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.border` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.quote.textShadow` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.font` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.list` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.textEffects` | [Body font](../design-families.md#font-body) |
| `content.decoration.bodyFont.ul.textShadow` | [Body font](../design-families.md#font-body) |
| `field.decoration.background` | [Background](../design-families.md#background) (+ focus, checked, active states) |
| `field.decoration.border` | [Border](../design-families.md#border) (+ focus, checked, active states) |
| `field.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) (+ focus, checked, active states) |
| `field.decoration.font` | [Font](../design-families.md#font) (+ focus, checked, active states) — container only: write keys under `field.decoration.font.font`, not here |
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
| `radio.decoration.font` | [Font](../design-families.md#font) (+ focus, checked, active states) — container only: write keys under `radio.decoration.font.font`, not here |
| `radio.decoration.font.font` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `radio.decoration.font.textEffects` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `radio.decoration.font.textShadow` | [Font](../design-families.md#font) (+ focus, checked, active states) |
| `radio.decoration.icon` | [Icon](../design-families.md#icon) (+ focus, checked, active states) |
| `radio.decoration.spacing` | [Spacing](../design-families.md#spacing) (+ focus, checked, active states) |
| `resultMessage.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `resultMessage.decoration.font.font`, not here |
| `resultMessage.decoration.font.font` | [Font](../design-families.md#font) |
| `resultMessage.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `resultMessage.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `checkbox.advanced.emailFullwidth` | — | onoff |  | R | · |  |
| `checkbox.advanced.firstNameField` | — | onoff |  | desktop | · |  |
| `checkbox.advanced.firstNameFullwidth` | — | onoff |  | R | · |  |
| `checkbox.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_background_color (color-alpha) |
| `checkbox.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_radii_fields_focus (border-radius) |
| `checkbox.advanced.focus.border` | `styles` | object |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.border` | `styles.all.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_all_fields_focus (color-alpha) |
| `checkbox.advanced.focus.border` | `styles.all.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_all_fields_focus (select) |
| `checkbox.advanced.focus.border` | `styles.all.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_all_fields_focus (range) |
| `checkbox.advanced.focus.border` | `styles.bottom.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_bottom_fields_focus (color-alpha) |
| `checkbox.advanced.focus.border` | `styles.bottom.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_bottom_fields_focus (select) |
| `checkbox.advanced.focus.border` | `styles.bottom.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_bottom_fields_focus (range) |
| `checkbox.advanced.focus.border` | `styles.left.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_left_fields_focus (color-alpha) |
| `checkbox.advanced.focus.border` | `styles.left.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_left_fields_focus (select) |
| `checkbox.advanced.focus.border` | `styles.left.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_left_fields_focus (range) |
| `checkbox.advanced.focus.border` | `styles.right.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_right_fields_focus (color-alpha) |
| `checkbox.advanced.focus.border` | `styles.right.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_right_fields_focus (select) |
| `checkbox.advanced.focus.border` | `styles.right.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_right_fields_focus (range) |
| `checkbox.advanced.focus.border` | `styles.top.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_top_fields_focus (color-alpha) |
| `checkbox.advanced.focus.border` | `styles.top.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_top_fields_focus (select) |
| `checkbox.advanced.focus.border` | `styles.top.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_top_fields_focus (range) |
| `checkbox.advanced.focus.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_text_color (color-alpha) |
| `checkbox.advanced.focus.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.focus.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `checkbox.advanced.focusUseBorder` | — | onoff |  | desktop | · | typed from Divi 4 use_focus_border_color (yes_no_button) |
| `checkbox.advanced.ipAddress` | — | onoff |  | desktop | · |  |
| `checkbox.advanced.lastNameField` | — | onoff |  | desktop | · |  |
| `checkbox.advanced.lastNameFullwidth` | — | onoff |  | R | · |  |
| `checkbox.advanced.nameField` | — | onoff |  | desktop | · |  |
| `checkbox.advanced.nameFieldOnly` | — | onoff |  | desktop | · |  |
| `checkbox.advanced.nameFullwidth` | — | onoff |  | R | · |  |
| `checkbox.advanced.placeholder.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `letterSpacing` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `lineHeight` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `size` | length |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `checkbox.advanced.placeholder.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `customFields.advanced.enable` | — | onoff |  | desktop | · | D4 `use_custom_fields` |
| `customFields.advanced.fields` | — | json |  | R | hover, sticky |  |
| `customFields.advanced.notice` | — | text |  | desktop | · | D4 `use_custom_fields_notice` |
| `field.advanced.emailFullwidth` | — | onoff |  | R | · | D4 `email_fullwidth` |
| `field.advanced.firstNameField` | — | onoff |  | desktop | · | D4 `first_name_field` |
| `field.advanced.firstNameFullwidth` | — | onoff |  | R | · | D4 `first_name_fullwidth` |
| `field.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `form_field_focus_background_color` |
| `field.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active | D4 `border_radii_fields_focus`, `border_radii_form_field_focus` |
| `field.advanced.focus.border` | `styles` | object |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.focus.border` | `styles.all.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_all_fields_focus`, `border_color_all_form_field_focus` |
| `field.advanced.focus.border` | `styles.all.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_all_fields_focus`, `border_style_all_form_field_focus` |
| `field.advanced.focus.border` | `styles.all.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | D4 `border_width_all_fields_focus`, `border_width_all_form_field_focus` |
| `field.advanced.focus.border` | `styles.bottom.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_bottom_fields_focus`, `border_color_bottom_form_field_focus` |
| `field.advanced.focus.border` | `styles.bottom.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_bottom_fields_focus`, `border_style_bottom_form_field_focus` |
| `field.advanced.focus.border` | `styles.bottom.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | D4 `border_width_bottom_fields_focus`, `border_width_bottom_form_field_focus` |
| `field.advanced.focus.border` | `styles.left.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_left_fields_focus`, `border_color_left_form_field_focus` |
| `field.advanced.focus.border` | `styles.left.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_left_fields_focus`, `border_style_left_form_field_focus` |
| `field.advanced.focus.border` | `styles.left.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | D4 `border_width_left_fields_focus`, `border_width_left_form_field_focus` |
| `field.advanced.focus.border` | `styles.right.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_right_fields_focus`, `border_color_right_form_field_focus` |
| `field.advanced.focus.border` | `styles.right.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_right_fields_focus`, `border_style_right_form_field_focus` |
| `field.advanced.focus.border` | `styles.right.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | D4 `border_width_right_fields_focus`, `border_width_right_form_field_focus` |
| `field.advanced.focus.border` | `styles.top.color` | color |  | R | hover, sticky, focus, checked, active | D4 `border_color_top_fields_focus`, `border_color_top_form_field_focus` |
| `field.advanced.focus.border` | `styles.top.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | D4 `border_style_top_fields_focus`, `border_style_top_form_field_focus` |
| `field.advanced.focus.border` | `styles.top.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | D4 `border_width_top_fields_focus`, `border_width_top_form_field_focus` |
| `field.advanced.focus.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `form_field_focus_text_color` |
| `field.advanced.focus.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.focus.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `field.advanced.focusUseBorder` | — | onoff |  | desktop | · | D4 `use_focus_border_color` |
| `field.advanced.ipAddress` | — | onoff |  | desktop | · | D4 `ip_address` |
| `field.advanced.lastNameField` | — | onoff |  | desktop | · | D4 `last_name_field` |
| `field.advanced.lastNameFullwidth` | — | onoff |  | R | · | D4 `last_name_fullwidth` |
| `field.advanced.nameField` | — | onoff |  | desktop | · | D4 `name_field` |
| `field.advanced.nameFieldOnly` | — | onoff |  | desktop | · | D4 `name_field_only` |
| `field.advanced.nameFullwidth` | — | onoff |  | R | · | D4 `name_fullwidth` |
| `field.advanced.placeholder.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | D4 `placeholder_color` |
| `field.advanced.placeholder.font.font` | `letterSpacing` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `lineHeight` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `size` | length |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `field.advanced.placeholder.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `module.advanced.layout` | — | enum | `left_right`, `right_left`, `top_bottom`, `bottom_top` | desktop | · | D4 `layout` |
| `module.advanced.showLabels` | — | onoff |  | desktop | · | D4 `show_labels` |
| `radio.advanced.emailFullwidth` | — | onoff |  | R | · |  |
| `radio.advanced.firstNameField` | — | onoff |  | desktop | · |  |
| `radio.advanced.firstNameFullwidth` | — | onoff |  | R | · |  |
| `radio.advanced.focus.background` | `backgroundColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.background` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_background_color (color-alpha) |
| `radio.advanced.focus.border` | `radius` | radius |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_radii_fields_focus (border-radius) |
| `radio.advanced.focus.border` | `styles` | object |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.border` | `styles.all.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_all_fields_focus (color-alpha) |
| `radio.advanced.focus.border` | `styles.all.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_all_fields_focus (select) |
| `radio.advanced.focus.border` | `styles.all.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_all_fields_focus (range) |
| `radio.advanced.focus.border` | `styles.bottom.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_bottom_fields_focus (color-alpha) |
| `radio.advanced.focus.border` | `styles.bottom.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_bottom_fields_focus (select) |
| `radio.advanced.focus.border` | `styles.bottom.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_bottom_fields_focus (range) |
| `radio.advanced.focus.border` | `styles.left.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_left_fields_focus (color-alpha) |
| `radio.advanced.focus.border` | `styles.left.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_left_fields_focus (select) |
| `radio.advanced.focus.border` | `styles.left.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_left_fields_focus (range) |
| `radio.advanced.focus.border` | `styles.right.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_right_fields_focus (color-alpha) |
| `radio.advanced.focus.border` | `styles.right.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_right_fields_focus (select) |
| `radio.advanced.focus.border` | `styles.right.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_right_fields_focus (range) |
| `radio.advanced.focus.border` | `styles.top.color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 border_color_top_fields_focus (color-alpha) |
| `radio.advanced.focus.border` | `styles.top.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky, focus, checked, active | typed from Divi 4 border_style_top_fields_focus (select) |
| `radio.advanced.focus.border` | `styles.top.width` | length | units: em, rem, px, cm, mm, in, pt, pc, ex, vh, vw | R | hover, sticky, focus, checked, active | typed from Divi 4 border_width_top_fields_focus (range) |
| `radio.advanced.focus.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active | typed from Divi 4 form_field_focus_text_color (color-alpha) |
| `radio.advanced.focus.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.focus.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `radio.advanced.focusUseBorder` | — | onoff |  | desktop | · | typed from Divi 4 use_focus_border_color (yes_no_button) |
| `radio.advanced.ipAddress` | — | onoff |  | desktop | · |  |
| `radio.advanced.lastNameField` | — | onoff |  | desktop | · |  |
| `radio.advanced.lastNameFullwidth` | — | onoff |  | R | · |  |
| `radio.advanced.nameField` | — | onoff |  | desktop | · |  |
| `radio.advanced.nameFieldOnly` | — | onoff |  | desktop | · |  |
| `radio.advanced.nameFullwidth` | — | onoff |  | R | · |  |
| `radio.advanced.placeholder.font.font` | `color` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `letterSpacing` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `lineHeight` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `size` | length |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `textColor` | color |  | R | hover, sticky, focus, checked, active |  |
| `radio.advanced.placeholder.font.font` | `variationSettings` | object |  | R | hover, sticky, focus, checked, active | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `success.advanced.action` | — | enum | `message`, `redirect` | desktop | · | D4 `success_action` |
| `success.advanced.message` | — | text |  | desktop | · | D4 `success_message` |
| `success.advanced.redirectQuery` | — | json |  | desktop | · | D4 `success_redirect_query` |
| `success.advanced.redirectUrl` | — | url |  | desktop | · | D4 `success_redirect_url` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.emailService` | [Email service](../design-families.md#email-service) |
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
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `newsletterButton` | text |  | R | hover, sticky | D4 `custom_css_newsletter_button` |
| `css` | `newsletterDescription` | text |  | R | hover, sticky | D4 `custom_css_newsletter_description` |
| `css` | `newsletterFields` | text |  | R | hover, sticky | D4 `custom_css_newsletter_fields` |
| `css` | `newsletterForm` | text |  | R | hover, sticky | D4 `custom_css_newsletter_form` |
| `css` | `newsletterTitle` | text |  | R | hover, sticky | D4 `custom_css_newsletter_title` |
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
<summary>Render defaults (27): what Divi uses when an attribute is unset — don't repeat these</summary>

- `button.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `button.innerContent` — desktop `{"linkUrl":"#","text":"Subscribe"}`
- `content.decoration.bodyFont.body.font` — desktop `{"size":"14px"}`
- `content.decoration.bodyFont.link.font` — desktop `{"size":"14px"}`
- `content.decoration.bodyFont.ol.font` — desktop `{"size":"14px"}`
- `content.decoration.bodyFont.quote.font` — desktop `{"size":"14px"}`
- `content.decoration.bodyFont.ul.font` — desktop `{"size":"14px"}`
- `customFields.advanced.enable` — desktop `"off"`
- `field.advanced.emailFullwidth` — desktop `"on"`
- `field.advanced.firstNameField` — desktop `"on"`
- `field.advanced.firstNameFullwidth` — desktop `"on"`
- `field.advanced.focusUseBorder` — desktop `"off"`
- `field.advanced.ipAddress` — desktop `"on"`
- `field.advanced.lastNameField` — desktop `"on"`
- `field.advanced.lastNameFullwidth` — desktop `"on"`
- `field.advanced.nameField` — desktop `"off"`
- `field.advanced.nameFieldOnly` — desktop `"on"`
- `field.advanced.nameFullwidth` — desktop `"on"`
- `module.advanced.showLabels` — desktop `"off"`
- `module.advanced.spamProtection` — desktop `{"enabled":"off"}`
- `module.advanced.text.text` — desktop `{"color":"dark"}`
- `module.decoration.background` — desktop `{"color":"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})$","enableColor":"on"}`
- `module.meta.adminLabel` — desktop `"Email Optin"`
- `resultMessage.decoration.font.font` — desktop `{"lineHeight":"1em","size":"26px"}`
- `success.advanced.action` — desktop `"message"`
- `success.advanced.message` — desktop `"Success!"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h2"}`

</details>
