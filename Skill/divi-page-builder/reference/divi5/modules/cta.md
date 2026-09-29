# Call To Action — divi/cta

Eye-catching block combining a headline, body text, and button to push a single conversion goal.

- **Block:** `divi/cta` (Divi 4: `et_pb_cta`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h2`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `button` (Promo Button), `description` (Promo Description), `freeForm`, `mainElement`, `title` (Promo Title)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/cta {"title":{"innerContent":{"desktop":{"value":"Need a plumber today?"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eSame-day service across Miami-Dade.\u003c/p\u003e"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Book a visit","linkUrl":"/contact/"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/cta` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Need a plumber today?"
      }
    }
  },
  "content": {
    "innerContent": {
      "desktop": {
        "value": "<p>Same-day service across Miami-Dade.</p>"
      }
    }
  },
  "button": {
    "innerContent": {
      "desktop": {
        "value": {
          "text": "Book a visit",
          "linkUrl": "/contact/"
        }
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
| `button.innerContent` | `linkTarget` | enum | `off`, `on` | desktop | · | D4 `url_new_window` |
| `button.innerContent` | `linkUrl` | url |  | desktop | · | D4 `button_url` |
| `button.innerContent` | `rel` | json |  | desktop | · | D4 `button_rel` |
| `button.innerContent` | `text` | text |  | R | hover | D4 `button_text` |
| `content.innerContent` | — | html |  | R | hover | D4 `content` |
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
| `content.decoration.inlineFont` | [Inline fonts](../design-families.md#inline-font) |
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
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
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
| `css` | `after` | text |  | R | hover, sticky | D4 `custom_css_after` |
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `button` | text |  | R | hover, sticky | D4 `custom_css_promo_button` |
| `css` | `description` | text |  | R | hover, sticky | D4 `custom_css_promo_description` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `title` | text |  | R | hover, sticky | D4 `custom_css_promo_title` |
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
<summary>Render defaults (5): what Divi uses when an attribute is unset — don't repeat these</summary>

- `button.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `module.advanced.text.text` — desktop `{"color":"dark","orientation":"center"}`
- `module.decoration.background` — desktop `{"color":"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})$"}`
- `module.meta.adminLabel` — desktop `"Call To Action"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h2"}`

</details>
