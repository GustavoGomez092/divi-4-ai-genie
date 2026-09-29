# Fullwidth Map — divi/fullwidth-map

Edge-to-edge Google Map for use as a contact-page hero or location showcase.

- **Block:** `divi/fullwidth-map` (Divi 4: `et_pb_fullwidth_map`)
- **Category:** fullwidth-module · **scope:** core
- **Goes inside:** `divi/section`
- **Children:** `divi/map-pin`
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"advanced":{"type":{"desktop":{"value":"fullwidth"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/fullwidth-map {"map":{"innerContent":{"desktop":{"value":{"address":"Miami, FL","lat":25.7617,"lng":-80.1918,"zoom":11}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/map-pin {"title":{"innerContent":{"desktop":{"value":"Downtown office"}}},"pin":{"innerContent":{"desktop":{"value":{"lat":25.7617,"lng":-80.1918}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/fullwidth-map --><!-- /wp:divi/section -->
```

The `divi/fullwidth-map` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "map": {
    "innerContent": {
      "desktop": {
        "value": {
          "address": "Miami, FL",
          "lat": 25.7617,
          "lng": -80.1918,
          "zoom": 11
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
| `map.innerContent` | — | object |  | R | hover, sticky |  |
| `map.innerContent` | `address` | text |  | desktop | · | D4 `address` |
| `map.innerContent` | `lat` | number |  | R | hover, sticky | D4 `address_lat` |
| `map.innerContent` | `lng` | number |  | R | hover, sticky | D4 `address_lng` |
| `map.innerContent` | `zoom` | number |  | R | hover, sticky | D4 `zoom_level` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `map.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
| `module.decoration.border` | [Border](../design-families.md#border) |
| `module.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.disabledOn` | [Disabled on](../design-families.md#disabled-on) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.interactions` | [Interactions](../design-families.md#interactions) |
| `module.decoration.overflow` | [Overflow](../design-families.md#overflow) |
| `module.decoration.position` | [Position](../design-families.md#position) |
| `module.decoration.scroll` | [Scroll](../design-families.md#scroll) |
| `module.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `module.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `module.decoration.sticky` | [Sticky](../design-families.md#sticky) |
| `module.decoration.transform` | [Transform](../design-families.md#transform) |
| `module.decoration.transition` | [Transition](../design-families.md#transition) |
| `module.decoration.zIndex` | [Z-index](../design-families.md#z-index) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `map.advanced.googleAPIKey` | — | text |  | R | hover, sticky | D4 `google_api_key` |
| `map.advanced.grayscaleFilter` | `amount` | text |  | desktop | · | D4 `grayscale_filter_amount` |
| `map.advanced.mobileDragging` | — | onoff |  | R | hover | D4 `mobile_dragging` |
| `map.advanced.mouseWheel` | — | onoff |  | R | hover | D4 `mouse_wheel` |

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
| `googleMapsScriptNotice` | — | text |  | desktop | · | D4 `google_maps_script_notice` |
| `locked` | — | onoff |  | desktop | · |  |
| `mapCenterMap` | — | object |  | desktop | · | D4 `map_center_map` |
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

- `map.advanced.mobileDragging` — desktop `"on"`
- `map.advanced.mouseWheel` — desktop `"on"`
- `map.innerContent` — desktop `{"address":"","lat":0,"lng":0,"zoom":18}`
- `module.decoration.sizing` — desktop `{"maxHeight":"none","maxWidth":"none","minHeight":"auto","width":"auto"}`
- `module.meta.adminLabel` — desktop `"Fullwidth Map"`

</details>
