# Link — divi/link

Inline anchor wrapping another module so the whole block becomes clickable.

- **Block:** `divi/link` (Divi 4: `et_pb_link`)
- **Category:** module · **scope:** d5-extra
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `icon` (Icon), `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/link {"content":{"innerContent":{"desktop":{"value":"Read the case study"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/link` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "content": {
    "innerContent": {
      "desktop": {
        "value": "Read the case study"
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
| `content.innerContent` | — | text |  | R | hover, sticky |  |
| `icon.innerContent` | — | icon |  | R | hover, sticky |  |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `content.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `content.decoration.font.font`, not here |
| `content.decoration.font.font` | [Font](../design-families.md#font) |
| `content.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `content.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `icon.decoration.background` | [Background](../design-families.md#background) |
| `icon.decoration.border` | [Border](../design-families.md#border) |
| `icon.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `icon.decoration.spacing` | [Spacing](../design-families.md#spacing) |
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

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `icon.advanced.color` | — | color |  | R | hover, sticky |  |
| `icon.advanced.size` | — | length |  | R | hover, sticky |  |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `css` | `after` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `before` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `freeForm` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `icon` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `mainElement` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
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
<summary>Render defaults (4): what Divi uses when an attribute is unset — don't repeat these</summary>

- `module.advanced.html` — desktop `{"elementType":"a"}`
- `module.decoration.layout` — desktop `{"alignItems":"center","columnGap":"10px","flexDirection":"row","rowGap":"10px"}`
- `module.decoration.spacing` — desktop `{"margin":{"bottom":"0px"}}`
- `module.meta.adminLabel` — desktop `"Link"`

</details>
