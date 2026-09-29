# Audio — divi/audio

Audio player with cover art for embedding podcasts, music, or voice clips.

- **Block:** `divi/audio` (Divi 4: `et_pb_audio`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h2`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `audioButtons` (Player Buttons), `audioContent` (Audio Content), `audioCoverArt` (Audio Cover Art), `audioMeta` (Audio Meta), `audioSliders` (Player Sliders), `audioSlidersCurrent` (Player Sliders Current), `audioTimer` (Player Timer), `audioTitle` (Audio Title), `before`, `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/audio {"audio":{"innerContent":{"desktop":{"value":"https://example.com/wp-content/uploads/2026/09/interview.mp3"}}},"title":{"innerContent":{"desktop":{"value":"Studio interview"}}},"artistName":{"innerContent":{"desktop":{"value":"Jordan Wells"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/audio` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "audio": {
    "innerContent": {
      "desktop": {
        "value": "https://example.com/wp-content/uploads/2026/09/interview.mp3"
      }
    }
  },
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Studio interview"
      }
    }
  },
  "artistName": {
    "innerContent": {
      "desktop": {
        "value": "Jordan Wells"
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
| `albumName.innerContent` | — | text |  | R | hover | D4 `album_name` |
| `artistName.innerContent` | — | text |  | R | hover | D4 `artist_name` |
| `audio.innerContent` | — | url |  | desktop | · | D4 `audio` |
| `image.innerContent` | `alt` | text |  | R | hover, sticky | D4 `alt` |
| `image.innerContent` | `src` | image |  | R | hover, sticky | D4 `image_url` |
| `image.innerContent` | `titleText` | text |  | R | hover, sticky | D4 `title_text` |
| `title.innerContent` | — | text |  | R | hover | D4 `title` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `caption.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `caption.decoration.font.font`, not here |
| `caption.decoration.font.font` | [Font](../design-families.md#font) |
| `caption.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `caption.decoration.font.textShadow` | [Font](../design-families.md#font) |
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
| `css` | `audioButtons` | text |  | R | hover, sticky | D4 `custom_css_audio_buttons` |
| `css` | `audioContent` | text |  | R | hover, sticky | D4 `custom_css_audio_content` |
| `css` | `audioCoverArt` | text |  | R | hover, sticky | D4 `custom_css_audio_cover_art` |
| `css` | `audioMeta` | text |  | R | hover, sticky | D4 `custom_css_audio_meta` |
| `css` | `audioSliders` | text |  | R | hover, sticky | D4 `custom_css_audio_sliders` |
| `css` | `audioSlidersCurrent` | text |  | R | hover, sticky | D4 `custom_css_audio_sliders_current` |
| `css` | `audioTimer` | text |  | R | hover, sticky | D4 `custom_css_audio_timer` |
| `css` | `audioTitle` | text |  | R | hover, sticky | D4 `custom_css_audio_title` |
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

Legacy, from Divi's Divi 4 conversion map only. The validator accepts them so that converted pages validate, but they appear only in Divi's conversion outlines: no Divi 5 module code reads them. Don't write them.

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `content` | — | html |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `content` |

<details>
<summary>Render defaults (4): what Divi uses when an attribute is unset — don't repeat these</summary>

- `module.advanced.text.text` — desktop `{"color":"dark"}`
- `module.decoration.background` — desktop `{"color":"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})$"}`
- `module.meta.adminLabel` — desktop `"Audio"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h2"}`

</details>
