# Hero — divi/fullwidth-header

Edge-to-edge hero banner with headline, subhead, buttons, and background media; typically the first thing on a page.

- **Block:** `divi/fullwidth-header` (Divi 4: `et_pb_fullwidth_header`)
- **Category:** fullwidth-module · **scope:** core
- **Goes inside:** `divi/section`
- **Children:** none
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h1`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `button1` (Button One), `button2` (Button Two), `content` (Body), `freeForm`, `headerContainer` (Header Container), `headerImage` (Header Image), `logo` (Logo), `mainElement`, `scrollButton` (Scroll Down Button), `subtitle` (Subtitle), `title` (Title)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"advanced":{"type":{"desktop":{"value":"fullwidth"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/fullwidth-header {"title":{"innerContent":{"desktop":{"value":"Emergency plumbing in Miami"}}},"subhead":{"innerContent":{"desktop":{"value":"Licensed, insured, on call 24/7"}}},"buttonOne":{"innerContent":{"desktop":{"value":{"text":"Call now","linkUrl":"tel:+13055550100"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/section -->
```

The `divi/fullwidth-header` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Emergency plumbing in Miami"
      }
    }
  },
  "subhead": {
    "innerContent": {
      "desktop": {
        "value": "Licensed, insured, on call 24/7"
      }
    }
  },
  "buttonOne": {
    "innerContent": {
      "desktop": {
        "value": {
          "text": "Call now",
          "linkUrl": "tel:+13055550100"
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
| `buttonOne.innerContent` | `linkUrl` | url |  | desktop | · | D4 `button_one_url` |
| `buttonOne.innerContent` | `rel` | json |  | desktop | · | D4 `button_one_rel` |
| `buttonOne.innerContent` | `text` | text |  | R | hover | D4 `button_one_text` |
| `buttonTwo.innerContent` | `linkUrl` | url |  | desktop | · | D4 `button_two_url` |
| `buttonTwo.innerContent` | `rel` | json |  | desktop | · | D4 `button_two_rel` |
| `buttonTwo.innerContent` | `text` | text |  | R | hover | D4 `button_two_text` |
| `content.innerContent` | — | html |  | R | hover | D4 `content` |
| `image.innerContent` | `alt` | text |  | desktop | · | D4 `image_alt_text` |
| `image.innerContent` | `src` | image |  | R | hover, sticky | D4 `header_image_url` |
| `image.innerContent` | `title` | text |  | desktop | · | D4 `image_title` |
| `logo.innerContent` | `alt` | text |  | desktop | · | D4 `logo_alt_text` |
| `logo.innerContent` | `src` | image |  | R | hover, sticky | D4 `logo_image_url` |
| `logo.innerContent` | `title` | text |  | desktop | · | D4 `logo_title` |
| `subhead.innerContent` | — | text |  | R | hover | D4 `subhead` |
| `title.innerContent` | — | text |  | R | hover | D4 `title` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `buttonOne.decoration.background` | [Background](../design-families.md#background) |
| `buttonOne.decoration.border` | [Border](../design-families.md#border) |
| `buttonOne.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `buttonOne.decoration.button` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.background` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.border` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.boxShadow` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.button` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.font.font` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.font.textEffects` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.font.textShadow` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.sizing` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.decoration.spacing` | [Button](../design-families.md#button) |
| `buttonOne.decoration.button.innerContent` | [Button](../design-families.md#button) |
| `buttonOne.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `buttonOne.decoration.font.font`, not here |
| `buttonOne.decoration.font.font` | [Font](../design-families.md#font) |
| `buttonOne.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `buttonOne.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `buttonOne.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `buttonOne.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `buttonTwo.decoration.background` | [Background](../design-families.md#background) |
| `buttonTwo.decoration.border` | [Border](../design-families.md#border) |
| `buttonTwo.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `buttonTwo.decoration.button` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.background` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.border` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.boxShadow` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.button` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.font.font` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.font.textEffects` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.font.textShadow` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.sizing` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.decoration.spacing` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.button.innerContent` | [Button](../design-families.md#button) |
| `buttonTwo.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `buttonTwo.decoration.font.font`, not here |
| `buttonTwo.decoration.font.font` | [Font](../design-families.md#font) |
| `buttonTwo.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `buttonTwo.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `buttonTwo.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `buttonTwo.decoration.spacing` | [Spacing](../design-families.md#spacing) |
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
| `image.decoration.border` | [Border](../design-families.md#border) |
| `image.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `image.decoration.filters` | [Filters](../design-families.md#filters) |
| `image.decoration.fit` | [Fit](../design-families.md#fit) |
| `image.decoration.sizing` | [Sizing](../design-families.md#sizing) |
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
| `overlay.decoration.background` | [Background](../design-families.md#background) |
| `scrollDown.decoration.icon` | [Icon](../design-families.md#icon) |
| `subhead.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `subhead.decoration.font.font`, not here |
| `subhead.decoration.font.font` | [Font](../design-families.md#font) |
| `subhead.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `subhead.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `content.advanced.maxWidth` | — | length |  | R | · | D4 `content_max_width` |
| `content.advanced.orientation` | — | text |  | desktop | · | D4 `content_orientation` |
| `image.advanced.orientation` | — | text |  | desktop | · | D4 `image_orientation` |
| `module.advanced.headerFullscreen` | — | onoff |  | desktop | · | D4 `header_fullscreen` |

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
| `css` | `button1` | text |  | R | hover, sticky | D4 `custom_css_button_1` |
| `css` | `button2` | text |  | R | hover, sticky | D4 `custom_css_button_2` |
| `css` | `content` | text |  | R | hover, sticky | D4 `custom_css_content` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `headerContainer` | text |  | R | hover, sticky | D4 `custom_css_header_container` |
| `css` | `headerImage` | text |  | R | hover, sticky | D4 `custom_css_header_image` |
| `css` | `logo` | text |  | R | hover, sticky | D4 `custom_css_logo` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `scrollButton` | text |  | R | hover, sticky | D4 `custom_css_scroll_button` |
| `css` | `subtitle` | text |  | R | hover, sticky | D4 `custom_css_subtitle` |
| `css` | `title` | text |  | R | hover, sticky | D4 `custom_css_title` |
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
<summary>Render defaults (12): what Divi uses when an attribute is unset — don't repeat these</summary>

- `buttonOne.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `buttonTwo.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `content.advanced.maxWidth` — desktop `"100%"`
- `content.advanced.orientation` — desktop `"center"`
- `image.advanced.orientation` — desktop `"center"`
- `module.advanced.headerFullscreen` — desktop `"off"`
- `module.advanced.html` — desktop `{"elementType":"section"}`
- `module.advanced.text.text` — desktop `{"color":"dark","orientation":"left"}`
- `module.decoration.background` — desktop `{"color":"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})$"}`
- `module.meta.adminLabel` — desktop `"Hero"`
- `scrollDown.decoration.icon` — desktop `{"show":"off","size":"50px","type":"divi","unicode":"&#x3b;","weight":"400"}`
- `title.decoration.font.font` — desktop `{"headingLevel":"h1"}`

</details>
