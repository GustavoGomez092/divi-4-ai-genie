# Timeline — divi/timeline

Vertical sequence of events with dates, headings, and descriptions for company history or roadmaps.

- **Block:** `divi/timeline` (Divi 4: `et_pb_timeline`)
- **Category:** module · **scope:** d5-extra
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** `divi/timeline-item`
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `card` (Card), `connector` (Connector), `content` (Content), `date` (Date), `freeForm`, `item` (Item), `mainElement`, `marker` (Marker), `spacer` (Spacer), `title` (Title), `track` (Track)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/timeline {"builderVersion":"5.13.1"} --><!-- wp:divi/timeline-item {"title":{"innerContent":{"desktop":{"value":"Founded"}}},"date":{"innerContent":{"desktop":{"value":"2009"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eTwo plumbers and one van.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/timeline --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/timeline` block's attributes, formatted for reading only (write them escaped and on one line, as above):

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
| `card.decoration.background` | [Background](../design-families.md#background) |
| `card.decoration.border` | [Border](../design-families.md#border) |
| `card.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `card.decoration.layout` | [Layout](../design-families.md#layout) |
| `card.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `card.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `cardEven.decoration.background` | [Background](../design-families.md#background) |
| `cardEven.decoration.border` | [Border](../design-families.md#border) |
| `cardEven.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `cardEven.decoration.layout` | [Layout](../design-families.md#layout) |
| `cardEven.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `cardEven.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `connector.decoration.background` | [Background](../design-families.md#background) |
| `connector.decoration.border` | [Border](../design-families.md#border) |
| `connector.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `connector.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `connector.decoration.spacing` | [Spacing](../design-families.md#spacing) |
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
| `contentEven.decoration.bodyFont.body.font` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.body.list` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.body.textEffects` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.body.textShadow` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.dropCap.font` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.dropCap.textShadow` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.link.font` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.link.textEffects` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.link.textShadow` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ol.font` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ol.list` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ol.textEffects` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ol.textShadow` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.quote.border` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.quote.font` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.quote.textEffects` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.quote.textShadow` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ul.font` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ul.list` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ul.textEffects` | [Body font](../design-families.md#font-body) |
| `contentEven.decoration.bodyFont.ul.textShadow` | [Body font](../design-families.md#font-body) |
| `date.decoration.font` | [Font](../design-families.md#font) |
| `date.decoration.font.font` | [Font](../design-families.md#font) |
| `date.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `date.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `dateEven.decoration.font` | [Font](../design-families.md#font) |
| `dateEven.decoration.font.font` | [Font](../design-families.md#font) |
| `dateEven.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `dateEven.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `item.decoration.background` | [Background](../design-families.md#background) |
| `item.decoration.border` | [Border](../design-families.md#border) |
| `item.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `item.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `item.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `itemEven.decoration.background` | [Background](../design-families.md#background) |
| `itemEven.decoration.border` | [Border](../design-families.md#border) |
| `itemEven.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `itemEven.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `itemEven.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `marker.decoration.background` | [Background](../design-families.md#background) |
| `marker.decoration.border` | [Border](../design-families.md#border) |
| `marker.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `marker.decoration.icon` | [Icon](../design-families.md#icon) |
| `marker.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `marker.decoration.spacing` | [Spacing](../design-families.md#spacing) |
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
| `spacer.decoration.background` | [Background](../design-families.md#background) |
| `spacer.decoration.border` | [Border](../design-families.md#border) |
| `spacer.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `spacer.decoration.layout` | [Layout](../design-families.md#layout) |
| `spacer.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `spacer.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `spacerEven.decoration.background` | [Background](../design-families.md#background) |
| `spacerEven.decoration.border` | [Border](../design-families.md#border) |
| `spacerEven.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `spacerEven.decoration.layout` | [Layout](../design-families.md#layout) |
| `spacerEven.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `spacerEven.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `title.decoration.font` | [Font](../design-families.md#font) |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `titleEven.decoration.font` | [Font](../design-families.md#font) |
| `titleEven.decoration.font.font` | [Font](../design-families.md#font) |
| `titleEven.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `titleEven.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `track.decoration.background` | [Background](../design-families.md#background) |
| `track.decoration.border` | [Border](../design-families.md#border) |
| `track.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `track.decoration.layout` | [Layout](../design-families.md#layout) |
| `track.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `track.decoration.spacing` | [Spacing](../design-families.md#spacing) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `children.advanced.spacer` | — | object |  | R | hover, sticky | parent-level defaults for child elements; shape not dumped |
| `children.spacer.advanced.displayElementsOnSpacer` | — | onoff |  | desktop | · |  |
| `marker.advanced` | `position` | enum | `center`, `end`, `start` | desktop | · |  |
| `marker.advanced.position` | `position` | text |  | R | hover, sticky |  |
| `module.advanced.timeline` | `alignContent` | text |  | R | · |  |
| `module.advanced.timeline` | `alignItems` | text |  | R | · |  |
| `module.advanced.timeline` | `collapseEmptyColumns` | onoff |  | R | · |  |
| `module.advanced.timeline` | `columnGap` | length |  | R | · |  |
| `module.advanced.timeline` | `direction` | enum | `horizontal`, `vertical` | R | · |  |
| `module.advanced.timeline` | `display` | enum | `block`, `flex`, `grid` | R | · |  |
| `module.advanced.timeline` | `flexDirection` | enum | `row`, `row-reverse`, `column`, `column-reverse` | R | · |  |
| `module.advanced.timeline` | `flexWrap` | text |  | R | · |  |
| `module.advanced.timeline` | `gridAutoColumns` | text |  | R | · |  |
| `module.advanced.timeline` | `gridAutoFlow` | enum | `row`, `column` | R | · |  |
| `module.advanced.timeline` | `gridAutoRows` | text |  | R | · |  |
| `module.advanced.timeline` | `gridColumnCount` | number |  | R | · |  |
| `module.advanced.timeline` | `gridColumnMinWidth` | length |  | R | · |  |
| `module.advanced.timeline` | `gridColumnWidth` | length |  | R | · |  |
| `module.advanced.timeline` | `gridColumnWidths` | enum | `equal`, `equalMinimum`, `equalFixed`, `auto`, `manual` | R | · |  |
| `module.advanced.timeline` | `gridDensity` | enum | `dense`, `auto` | R | · |  |
| `module.advanced.timeline` | `gridJustifyItems` | enum | `start`, `center`, `end`, `stretch`, `baseline` | R | · |  |
| `module.advanced.timeline` | `gridOffsetRules` | json |  | R | · | JS divi/grid-offset-rules |
| `module.advanced.timeline` | `gridRowCount` | text |  | R | · | range with default auto |
| `module.advanced.timeline` | `gridRowHeight` | length |  | R | · |  |
| `module.advanced.timeline` | `gridRowHeights` | enum | `auto`, `equal`, `minimum`, `fixed`, `manual` | R | · |  |
| `module.advanced.timeline` | `gridRowMinHeight` | length |  | R | · |  |
| `module.advanced.timeline` | `gridTemplateColumns` | text |  | R | · |  |
| `module.advanced.timeline` | `gridTemplateRows` | text |  | R | · |  |
| `module.advanced.timeline` | `justifyContent` | text |  | R | · |  |
| `module.advanced.timeline` | `position` | enum | `alternating`, `bottom`, `top`, `left`, `right` | R | · |  |
| `module.advanced.timeline` | `rowGap` | length |  | R | · |  |
| `module.advanced.timeline` | `startFrom` | enum | `bottom`, `top`, `left`, `right` | R | · |  |

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
| `css` | `card` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `connector` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `content` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `date` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `freeForm` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `item` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `mainElement` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `marker` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `spacer` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `title` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
| `css` | `track` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
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
<summary>Render defaults (2): what Divi uses when an attribute is unset — don't repeat these</summary>

- `module.advanced.timeline` — desktop `{"direction":"vertical","position":"right"}`
- `module.meta.adminLabel` — desktop `"Timeline"`

</details>
