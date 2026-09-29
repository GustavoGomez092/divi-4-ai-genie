# Map Pin — divi/map-pin

A single map marker inside a Map or Fullwidth Map module with coordinates and tooltip content.

- **Block:** `divi/map-pin` (Divi 4: `et_pb_map_pin`)
- **Category:** child-module · **scope:** core
- **Goes inside:** `divi/fullwidth-map`, `divi/map`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/map {"map":{"innerContent":{"desktop":{"value":{"address":"Miami, FL","lat":25.7617,"lng":-80.1918,"zoom":11}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/map-pin {"title":{"innerContent":{"desktop":{"value":"Downtown office"}}},"pin":{"innerContent":{"desktop":{"value":{"lat":25.7617,"lng":-80.1918}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/map --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/map-pin` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Downtown office"
      }
    }
  },
  "pin": {
    "innerContent": {
      "desktop": {
        "value": {
          "lat": 25.7617,
          "lng": -80.1918
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
| `content.innerContent` | — | html |  | R | hover | D4 `content` |
| `pin.innerContent` | — | object |  | desktop | · |  |
| `pin.innerContent` | `address` | text |  | desktop | · | D4 `pin_address` |
| `pin.innerContent` | `lat` | number |  | R | hover, sticky | D4 `pin_address_lat` |
| `pin.innerContent` | `lng` | number |  | R | hover, sticky | D4 `pin_address_lng` |
| `pin.innerContent` | `zoom` | text |  | desktop | · | D4 `zoom_level` |
| `title.innerContent` | — | text |  | R | hover | D4 `title` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `content.decoration.inlineFont` | [Inline fonts](../design-families.md#inline-font) |

## Advanced

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `pin.advanced.html` | [Html](../design-families.md#html) |
| `pin.advanced.loop` | [Loop](../design-families.md#loop) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `css` | `after` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `before` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `freeForm` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `mainElement` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `globalColorsInfo` | — | json |  | desktop | · | D4 global_colors_info (Conversion::getAttrMap) |
| `locked` | — | onoff |  | desktop | · |  |
| `on` | — | json |  | desktop | · | block-level attr from Conversion::getAttrMap; value shape not documented |
| `open` | — | onoff |  | desktop | · |  |
| `themeBuilderArea` | — | json |  | desktop | · | theme-builder area marker (Conversion::getAttrMap) |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `pin.meta.adminLabel` | [Admin label](../design-families.md#admin-label) |
| `pin.meta.meta.forceVisible` | [Meta](../design-families.md#meta) |
| `pin.meta.meta.tocListHeading` | [Meta](../design-families.md#meta) |

<details>
<summary>Render defaults (1): what Divi uses when an attribute is unset — don't repeat these</summary>

- `pin.innerContent` — desktop `{"address":"","lat":0,"lng":0,"zoom":18}`

</details>
