# Group Carousel — divi/group-carousel

Horizontally scrollable carousel of grouped content blocks for slide-based storytelling.

- **Block:** `divi/group-carousel` (no Divi 4 equivalent)
- **Category:** module · **scope:** d5-extra
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** `divi/group`
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `carouselActiveSlide` (Carousel Active Slide), `carouselArrows` (Carousel Arrows), `carouselContainer` (Carousel Container), `carouselDots` (Carousel Dots), `carouselSlide` (Carousel Slide), `carouselTrack` (Carousel Track), `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/group-carousel {"builderVersion":"5.13.1"} --><!-- wp:divi/group {"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eLicensed, insured plumbers at your door in 60 minutes.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/group --><!-- /wp:divi/group-carousel --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/group-carousel` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "builderVersion": "5.13.1"
}
```

**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written `"title":{"innerContent":{"desktop":{"value":{"text":"…"}}}}`. **R** = responsive (a value per breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides `value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); the full value model: [value-formats.md](../value-formats.md).

## Content

None on this block.

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `activeGroups.decoration.background` | [Background](../design-families.md#background) |
| `activeGroups.decoration.border` | [Border](../design-families.md#border) |
| `activeGroups.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `activeGroups.decoration.filters` | [Filters](../design-families.md#filters) |
| `activeGroups.decoration.layout` | [Layout](../design-families.md#layout) |
| `activeGroups.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `activeGroups.decoration.transform` | [Transform](../design-families.md#transform) |
| `arrows.decoration.background` | [Background](../design-families.md#background) |
| `arrows.decoration.border` | [Border](../design-families.md#border) |
| `arrows.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `arrows.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `children.decoration.background` | [Background](../design-families.md#background) |
| `children.decoration.border` | [Border](../design-families.md#border) |
| `children.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `children.decoration.filters` | [Filters](../design-families.md#filters) |
| `children.decoration.layout` | [Layout](../design-families.md#layout) |
| `children.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `children.decoration.transform` | [Transform](../design-families.md#transform) |
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
| `arrows.advanced.color` | — | color |  | R | hover, sticky |  |
| `arrows.advanced.leftIcon` | — | icon |  | R | hover, sticky |  |
| `arrows.advanced.position` | — | enum | `center`, `inside`, `outside` | R | hover, sticky |  |
| `arrows.advanced.rightIcon` | — | icon |  | R | hover, sticky |  |
| `arrows.advanced.show` | — | onoff |  | R | hover, sticky |  |
| `arrows.advanced.showArrows` | — | onoff |  | R | hover, sticky |  |
| `arrows.advanced.size` | — | length |  | R | hover, sticky |  |
| `dotNav.advanced.alignment` | — | enum | `center`, `left`, `right` | R | hover, sticky |  |
| `dotNav.advanced.color` | — | color |  | R | hover, sticky |  |
| `dotNav.advanced.position` | — | enum | `above`, `below`, `overlay` | R | hover, sticky |  |
| `dotNav.advanced.show` | — | onoff |  | R | hover, sticky |  |
| `dotNav.advanced.showDots` | — | onoff |  | R | hover, sticky |  |
| `dotNav.advanced.size` | — | length |  | R | hover, sticky |  |
| `module.advanced.auto` | — | onoff |  | R | hover, sticky |  |
| `module.advanced.autoSpeed` | — | number |  | R | hover, sticky |  |
| `module.advanced.centerMode` | — | onoff |  | R | hover, sticky |  |
| `module.advanced.pauseOnHover` | — | onoff |  | R | hover, sticky |  |
| `module.advanced.slidesToScroll` | — | number |  | R | hover, sticky |  |
| `module.advanced.slidesToShow` | — | number |  | R | hover, sticky |  |
| `module.advanced.speed` | — | length |  | R | hover, sticky |  |
| `module.advanced.transitionSpeed` | — | length |  | R | hover, sticky |  |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.link` | [Link](../design-families.md#link) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `css` | `after` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `before` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `carouselActiveSlide` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `carouselArrows` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `carouselContainer` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `carouselDots` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `carouselSlide` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `carouselTrack` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
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
| `module.meta.adminLabel` | [Admin label](../design-families.md#admin-label) |
| `module.meta.meta.forceVisible` | [Meta](../design-families.md#meta) |
| `module.meta.meta.tocListHeading` | [Meta](../design-families.md#meta) |

<details>
<summary>Render defaults (10): what Divi uses when an attribute is unset — don't repeat these</summary>

- `arrows.advanced.leftIcon` — desktop `{"target":"off","type":"divi","unicode":"&#x34;","weight":"400"}`
- `arrows.advanced.rightIcon` — desktop `{"target":"off","type":"divi","unicode":"&#x35;","weight":"400"}`
- `arrows.advanced.showArrows` — desktop `"on"`
- `dotNav.advanced.showDots` — desktop `"on"`
- `module.advanced.auto` — desktop `"off"`
- `module.advanced.centerMode` — desktop `"off"`
- `module.advanced.pauseOnHover` — desktop `"on"`
- `module.advanced.slidesToScroll` — desktop `"1"`
- `module.advanced.slidesToShow` — desktop `"1"`
- `module.meta.adminLabel` — desktop `"Carousel"`

</details>
