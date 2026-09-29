# Slide — divi/slide

A single slide inside a Slider or Fullwidth Slider with its own background and content.

- **Block:** `divi/slide` (Divi 4: `et_pb_slide`)
- **Category:** child-module · **scope:** core
- **Goes inside:** `divi/fullwidth-slider`, `divi/slider`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`, `slideButton` (Slide Button), `slideContainer` (Slide Description Container), `slideDescription` (Slide Description), `slideImage` (Slide Image), `slideTitle` (Slide Title)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/slider {"builderVersion":"5.13.1"} --><!-- wp:divi/slide {"title":{"innerContent":{"desktop":{"value":"Spring tune-up"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eBook before May 1.\u003c/p\u003e"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Book now","linkUrl":"/contact/"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/slider --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/slide` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Spring tune-up"
      }
    }
  },
  "content": {
    "innerContent": {
      "desktop": {
        "value": "<p>Book before May 1.</p>"
      }
    }
  },
  "button": {
    "innerContent": {
      "desktop": {
        "value": {
          "text": "Book now",
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
| `button.innerContent` | `linkUrl` | url |  | desktop | · | D4 `button_link`, `button_url` |
| `button.innerContent` | `rel` | json |  | desktop | · | D4 `button_rel` |
| `button.innerContent` | `text` | text |  | R | hover | D4 `button_text` |
| `content.innerContent` | — | html |  | R | hover | D4 `content` |
| `image.innerContent` | `alt` | text |  | desktop | · | D4 `alt`, `image_alt` |
| `image.innerContent` | `src` | image |  | R | hover, sticky | D4 `image` |
| `title.innerContent` | — | text |  | R | hover | D4 `heading` |
| `video.innerContent` | — | url |  | R | hover, sticky | D4 `video_url` |

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
| `content.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `content.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `contentOverlay.decoration.background` | [Background](../design-families.md#background) |
| `contentOverlay.decoration.border` | [Border](../design-families.md#border) |
| `dotNav.decoration.background` | [Background](../design-families.md#background) |
| `image.decoration.border` | [Border](../design-families.md#border) |
| `image.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `image.decoration.filters` | [Filters](../design-families.md#filters) |
| `image.decoration.fit` | [Fit](../design-families.md#fit) |
| `image.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.disabledOn` | [Disabled on](../design-families.md#disabled-on) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.interactions` | [Interactions](../design-families.md#interactions) |
| `module.decoration.layout` | [Layout](../design-families.md#layout) |
| `module.decoration.overflow` | [Overflow](../design-families.md#overflow) |
| `module.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `module.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `module.decoration.transform` | [Transform](../design-families.md#transform) |
| `module.decoration.transition` | [Transition](../design-families.md#transition) |
| `module.decoration.zIndex` | [Z-index](../design-families.md#z-index) |
| `slideOverlay.decoration.background` | [Background](../design-families.md#background) |
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `arrows.advanced.color` | — | color |  | R | hover, sticky | D4 `arrows_custom_color` |
| `contentOverlay.advanced.use` | — | onoff |  | desktop | · | D4 `use_text_overlay` |
| `contentOverlay.advanced.useTextOverlay` | — | onoff |  | R | hover, sticky |  |
| `dotNav.advanced.color` | `color` | color |  | R | hover, sticky |  |
| `image.advanced.alignment` | — | enum | `bottom`, `center` | R | hover | D4 `alignment` |
| `slideOverlay.advanced.use` | — | onoff |  | desktop | · | D4 `use_bg_overlay` |
| `slideOverlay.advanced.useBackgroundOverlay` | — | onoff |  | R | hover, sticky |  |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.html` | [Html](../design-families.md#html) |
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
| `css` | `slideButton` | text |  | R | hover, sticky | D4 `custom_css_slide_button` |
| `css` | `slideContainer` | text |  | R | hover, sticky | D4 `custom_css_slide_container` |
| `css` | `slideDescription` | text |  | R | hover, sticky | D4 `custom_css_slide_description` |
| `css` | `slideImage` | text |  | R | hover, sticky | D4 `custom_css_slide_image` |
| `css` | `slideTitle` | text |  | R | hover, sticky | D4 `custom_css_slide_title` |
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

- `button.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `contentOverlay.decoration.border` — desktop `{"radius":{"bottomLeft":"3px","bottomRight":"3px","sync":"on","topLeft":"3px","topRight":"3px"}}`
- `image.advanced.alignment` — desktop `"center"`
- `module.advanced.text.text` — desktop `{"color":"dark"}`
- `module.decoration.background` — desktop `{"color":"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})$"}`
- `module.meta.adminLabel` — desktop `""`

</details>
