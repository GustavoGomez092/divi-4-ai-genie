# Table of Contents — divi/table-of-contents

Automatically generated list of links to headings on the current page.

- **Block:** `divi/table-of-contents` (Divi 4: `et_pb_table_of_contents`)
- **Category:** module · **scope:** d5-extra
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h2`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `emptyState` (Empty State), `freeForm`, `link` (Link), `list` (List), `mainElement`, `marker` (Marker), `title` (Title)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/table-of-contents {"title":{"innerContent":{"desktop":{"value":"On this page"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/table-of-contents` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "On this page"
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
| `emptyState.innerContent` | — | text |  | R | hover, sticky |  |
| `list.innerContent` | `includeOwnTitle` | onoff |  | desktop | · |  |
| `list.innerContent` | `includedHeadings` | json |  | desktop | · |  |
| `title.innerContent` | — | text |  | R | hover, sticky |  |
| `title.innerContent` | `text` | text |  | R | hover, sticky |  |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `emptyState.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `emptyState.decoration.font.font`, not here |
| `emptyState.decoration.font.font` | [Font](../design-families.md#font) |
| `emptyState.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `emptyState.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `list.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `list.decoration.font.font`, not here |
| `list.decoration.font.font` | [Font](../design-families.md#font) |
| `list.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `list.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `list1.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `list1.decoration.font.font`, not here |
| `list1.decoration.font.font` | [Font](../design-families.md#font) |
| `list1.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `list1.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `list2.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `list2.decoration.font.font`, not here |
| `list2.decoration.font.font` | [Font](../design-families.md#font) |
| `list2.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `list2.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `list3.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `list3.decoration.font.font`, not here |
| `list3.decoration.font.font` | [Font](../design-families.md#font) |
| `list3.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `list3.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `list4.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `list4.decoration.font.font`, not here |
| `list4.decoration.font.font` | [Font](../design-families.md#font) |
| `list4.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `list4.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `list5.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `list5.decoration.font.font`, not here |
| `list5.decoration.font.font` | [Font](../design-families.md#font) |
| `list5.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `list5.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `list6.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `list6.decoration.font.font`, not here |
| `list6.decoration.font.font` | [Font](../design-families.md#font) |
| `list6.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `list6.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `marker.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `marker.decoration.font.font`, not here |
| `marker.decoration.font.font` | [Font](../design-families.md#font) |
| `marker.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `marker.decoration.font.textShadow` | [Font](../design-families.md#font) |
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

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `list.advanced.interaction` | `scrollOffsetPx` | length |  | desktop | · |  |
| `list.advanced.interaction` | `smoothScroll` | onoff |  | desktop | · |  |
| `list.advanced.layout` | `markerStyle` | text |  | desktop | · |  |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.link` | [Link](../design-families.md#link) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `css` | `after` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `before` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `emptyState` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `freeForm` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `link` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `list` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `mainElement` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `marker` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `title` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
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

- `emptyState.innerContent` — desktop `"No headings found in this post."`
- `list.advanced.interaction` — desktop `{"scrollOffsetPx":"0","smoothScroll":"on"}`
- `list.advanced.layout` — desktop `{"markerStyle":"ordered"}`
- `module.meta.adminLabel` — desktop `"Table of Contents"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h2"}`
- `title.innerContent` — desktop `"Table of Contents"`

</details>
