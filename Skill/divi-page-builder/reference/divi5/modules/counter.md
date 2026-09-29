# Bar Counter — divi/counter

A single labeled progress bar inside a Bar Counters module.

- **Block:** `divi/counter` (Divi 4: `et_pb_counter`)
- **Category:** child-module · **scope:** core
- **Goes inside:** `divi/counters`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `counterAmount` (Counter Amount), `counterContainer` (Counter Container), `counterTitle` (Counter Title), `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/counters {"builderVersion":"5.13.1"} --><!-- wp:divi/counter {"title":{"innerContent":{"desktop":{"value":"Kitchens"}}},"barProgress":{"innerContent":{"desktop":{"value":"80"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/counters --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/counter` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Kitchens"
      }
    }
  },
  "barProgress": {
    "innerContent": {
      "desktop": {
        "value": "80"
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
| `barProgress.innerContent` | — | text |  | R | hover | D4 `percent` |
| `title.innerContent` | — | text |  | R | hover | D4 `content` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `barCounter.decoration.background` | [Background](../design-families.md#background) |
| `barCounter.decoration.border` | [Border](../design-families.md#border) |
| `barCounter.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `barCounter.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `barProgress.decoration.background` | [Background](../design-families.md#background) |
| `barProgress.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `barProgress.decoration.font.font`, not here |
| `barProgress.decoration.font.font` | [Font](../design-families.md#font) |
| `barProgress.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `barProgress.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.interactions` | [Interactions](../design-families.md#interactions) |
| `module.decoration.layout` | [Layout](../design-families.md#layout) |
| `module.decoration.overflow` | [Overflow](../design-families.md#overflow) |
| `module.decoration.position` | [Position](../design-families.md#position) |
| `module.decoration.scroll` | [Scroll](../design-families.md#scroll) |
| `module.decoration.spacing` | [Spacing](../design-families.md#spacing) |
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
| `css` | `counterAmount` | text |  | R | hover, sticky | D4 `custom_css_counter_amount` |
| `css` | `counterContainer` | text |  | R | hover, sticky | D4 `custom_css_counter_container` |
| `css` | `counterTitle` | text |  | R | hover, sticky | D4 `custom_css_counter_title` |
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

<details>
<summary>Render defaults (3): what Divi uses when an attribute is unset — don't repeat these</summary>

- `barProgress.innerContent` — desktop `"50"`
- `module.advanced.html` — desktop `{"elementType":"li"}`
- `module.meta.adminLabel` — desktop `"Bar Counter"`

</details>
