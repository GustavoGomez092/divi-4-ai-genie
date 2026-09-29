# Testimonial — divi/testimonial

Customer quote block with author name, title, and optional photo for social proof.

- **Block:** `divi/testimonial` (Divi 4: `et_pb_testimonial`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`, `testimonialAuthor` (Testimonial Author), `testimonialDescription` (Testimonial Description), `testimonialMeta` (Testimonial Meta), `testimonialPortrait` (Testimonial Portrait)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/testimonial {"author":{"innerContent":{"desktop":{"value":"Ravi N."}}},"jobTitle":{"innerContent":{"desktop":{"value":"Office manager"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eThey fixed our pipes without closing the office for a day.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/testimonial` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "author": {
    "innerContent": {
      "desktop": {
        "value": "Ravi N."
      }
    }
  },
  "jobTitle": {
    "innerContent": {
      "desktop": {
        "value": "Office manager"
      }
    }
  },
  "content": {
    "innerContent": {
      "desktop": {
        "value": "<p>They fixed our pipes without closing the office for a day.</p>"
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
| `author.innerContent` | — | text |  | R | hover | D4 `author` |
| `company.innerContent` | `linkTarget` | enum | `off`, `on` | desktop | · | D4 `url_new_window` |
| `company.innerContent` | `linkUrl` | url |  | desktop | · | D4 `url` |
| `company.innerContent` | `text` | text |  | R | hover | D4 `company_name` |
| `content.innerContent` | — | html |  | R | hover | D4 `content` |
| `jobTitle.innerContent` | — | text |  | R | hover | D4 `job_title` |
| `portrait.innerContent` | `src` | image |  | R | hover |  |
| `portrait.innerContent` | `url` | image |  | R | hover | D4 `portrait_url` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `author.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `author.decoration.font.font`, not here |
| `author.decoration.font.font` | [Font](../design-families.md#font) |
| `author.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `author.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `company.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `company.decoration.font.font`, not here |
| `company.decoration.font.font` | [Font](../design-families.md#font) |
| `company.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `company.decoration.font.textShadow` | [Font](../design-families.md#font) |
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
| `image.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `jobTitle.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `jobTitle.decoration.font.font`, not here |
| `jobTitle.decoration.font.font` | [Font](../design-families.md#font) |
| `jobTitle.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `jobTitle.decoration.font.textShadow` | [Font](../design-families.md#font) |
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
| `portrait.decoration.border` | [Border](../design-families.md#border) |
| `portrait.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `portrait.decoration.filters` | [Filters](../design-families.md#filters) |
| `portrait.decoration.fit` | [Fit](../design-families.md#fit) |
| `portrait.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `quoteIcon.decoration.background` | [Background](../design-families.md#background) |
| `quoteIcon.decoration.icon` | [Icon](../design-families.md#icon) |

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
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `testimonialAuthor` | text |  | R | hover, sticky | D4 `custom_css_testimonial_author` |
| `css` | `testimonialDescription` | text |  | R | hover, sticky | D4 `custom_css_testimonial_description` |
| `css` | `testimonialMeta` | text |  | R | hover, sticky | D4 `custom_css_testimonial_meta` |
| `css` | `testimonialPortrait` | text |  | R | hover, sticky | D4 `custom_css_testimonial_portrait` |
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

- `company.innerContent` — desktop `{"linkTarget":"off"}`
- `module.advanced.text.text` — desktop `{"color":"light"}`
- `module.decoration.background` — desktop `{"color":"#f5f5f5"}`
- `module.meta.adminLabel` — desktop `"Testimonial"`
- `quoteIcon.decoration.icon` — desktop `{"show":"on","useSize":"off"}`

</details>
