# Blurb — divi/blurb

Compact feature card pairing an icon or image with a heading and short description.

- **Block:** `divi/blurb` (Divi 4: `et_pb_blurb`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h4`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `blurbContent` (Blurb Content), `blurbImage` (Blurb Image), `blurbTitle` (Blurb Title), `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Fast response"}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xe03b;","type":"divi","weight":"400"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eA licensed plumber at your door within the hour.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/blurb` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": {
          "text": "Fast response"
        }
      }
    }
  },
  "imageIcon": {
    "innerContent": {
      "desktop": {
        "value": {
          "useIcon": "on",
          "icon": {
            "unicode": "&#xe03b;",
            "type": "divi",
            "weight": "400"
          }
        }
      }
    }
  },
  "content": {
    "innerContent": {
      "desktop": {
        "value": "<p>A licensed plumber at your door within the hour.</p>"
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
| `content.innerContent` | — | html |  | R | hover | D4 `content` |
| `imageIcon.innerContent` | `alt` | text |  | desktop | · | D4 `alt` |
| `imageIcon.innerContent` | `animation` | enum | `top`, `left`, `right`, `bottom`, `off` | R | · | D4 `animation` |
| `imageIcon.innerContent` | `icon` | icon |  | R | hover | D4 `font_icon` |
| `imageIcon.innerContent` | `src` | image |  | R | hover | D4 `image` |
| `imageIcon.innerContent` | `useIcon` | onoff |  | desktop | · | D4 `use_icon` |
| `title.innerContent` | `target` | enum | `off`, `on` | desktop | · | D4 `url_new_window` |
| `title.innerContent` | `text` | text |  | R | hover | D4 `title` |
| `title.innerContent` | `url` | url |  | desktop | · | D4 `url` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
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
| `contentContainer.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `imageIcon.decoration.animation` | [Animation](../design-families.md#animation) |
| `imageIcon.decoration.background` | [Background](../design-families.md#background) |
| `imageIcon.decoration.border` | [Border](../design-families.md#border) |
| `imageIcon.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `imageIcon.decoration.filters` | [Filters](../design-families.md#filters) |
| `imageIcon.decoration.fit` | [Fit](../design-families.md#fit) |
| `imageIcon.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `imageIcon.decoration.spacing` | [Spacing](../design-families.md#spacing) |
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
| `title.decoration.font` | [Font](../design-families.md#font) |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `imageIcon.advanced.alignment` | — | enum | `left`, `center`, `right` | R | sticky | D4 `icon_alignment` |
| `imageIcon.advanced.color` | — | color |  | R | hover, sticky | D4 `icon_color` |
| `imageIcon.advanced.placement` | — | enum | `left`, `top` | R | · | D4 `icon_placement` |
| `imageIcon.advanced.width` | `icon` | length |  | R | hover, sticky |  |
| `imageIcon.advanced.width` | `image` | length |  | R | hover, sticky |  |

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
| `css` | `blurbContent` | text |  | R | hover, sticky | D4 `custom_css_blurb_content` |
| `css` | `blurbImage` | text |  | R | hover, sticky | D4 `custom_css_blurb_image` |
| `css` | `blurbTitle` | text |  | R | hover, sticky | D4 `custom_css_blurb_title` |
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

- `imageIcon.advanced.color` — desktop `"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})$"`
- `imageIcon.advanced.placement` — desktop `"top"`
- `imageIcon.innerContent` — desktop `{"useIcon":"off"}`
- `module.advanced.text.text` — desktop `{"color":"light"}`
- `module.meta.adminLabel` — desktop `"Blurb"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h4"}`

</details>

## Gotchas

- `title.innerContent` is an object, not a string: `{"text": "…", "url": "…", "target": "off"|"on"}` (Divi 4 `title`, `url`, `url_new_window`). Only `divi/heading` and a few others take a plain string title.
- Icon or image: in `imageIcon.innerContent`, `useIcon: "on"` shows `icon` (an icon object `{"unicode", "type", "weight"}`, see [icons.md](../../icons.md)); the default `"off"` shows the image `src` (give it an `alt`). Set only the one you use.
- The title renders as `h4` by default. In a grid of blurbs under an `h2` section heading, set `title.decoration.font.font` → `{"headingLevel": "h3"}` so the outline doesn't skip a level.
- `imageIcon.advanced.placement` is `top` (default) or `left`; `left` suits compact feature lists. The icon color is `imageIcon.advanced.color` (default: the site's primary global color).
