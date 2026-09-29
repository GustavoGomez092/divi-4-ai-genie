# Chart — divi/charts

Interactive bar, line, pie, and other charts built from customizable data tables.

- **Block:** `divi/charts` (Divi 4: `et_pb_charts`)
- **Category:** module · **scope:** d5-extra
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `chartCanvas` (Chart Canvas), `freeForm`, `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/charts {"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/charts` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "builderVersion": "5.13.1"
}
```

**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written `"title":{"innerContent":{"desktop":{"value":{"text":"…"}}}}`. **R** = responsive (a value per breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides `value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); the full value model: [value-formats.md](../value-formats.md).

## Content

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `chart.innerContent` | `data` | json |  | desktop | hover, sticky |  |
| `chart.innerContent` | `legendTitle` | text |  | desktop | · |  |
| `chart.innerContent` | `subtitle` | text |  | desktop | · |  |
| `chart.innerContent` | `title` | text |  | desktop | · |  |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
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
| `chart.advanced.config` | `showLegend` | onoff |  | desktop | · |  |
| `chart.advanced.config` | `showLegendTitle` | onoff |  | desktop | · |  |
| `chart.advanced.config` | `showSubtitle` | onoff |  | desktop | · |  |
| `chart.advanced.config` | `showTitle` | onoff |  | desktop | · |  |
| `chart.advanced.config` | `showTooltip` | onoff |  | desktop | · |  |
| `chart.advanced.config` | `type` | enum | `area`, `bar`, `bubble`, `doughnut`, `line`, `pie`, `polarArea`, `radar`, `scatter` | R | hover, sticky |  |
| `chart.advanced.legend` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `capitalization` | enum | `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps`, `none` | R | hover, sticky | JS button-options {uppercase,capitalize,lowercase,smallCaps,allSmallCaps}; D4 all_caps converts through convertAllCaps; none = unset |
| `chart.advanced.legend.font` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `columnCount` | number |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `columnGap` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `family` | font-family |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `hyphens` | text |  | R | hover, sticky | JS divi/toggle-like control; CSS hyphens value not pinned |
| `chart.advanced.legend.font` | `letterSpacing` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `lineColor` | color |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `lineHeight` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `lineStyle` | enum | `solid`, `double`, `dotted`, `dashed`, `wavy` | R | hover, sticky |  |
| `chart.advanced.legend.font` | `lineThickness` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `opticalSizing` | enum | `auto`, `none` | R | hover, sticky |  |
| `chart.advanced.legend.font` | `size` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `style` | enum | list of: `italic`, `underline`, `overline`, `strikethrough`, `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps` | R | hover, sticky | list of styles; JS options {italic,underline,overline,strikethrough} (+ Ju capitalization keys, which the same Ju constant holds) |
| `chart.advanced.legend.font` | `textAlign` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |
| `chart.advanced.legend.font` | `textWrap` | text |  | R | hover, sticky | JS button-options with a computed option list (y); CSS text-wrap keyword |
| `chart.advanced.legend.font` | `underlineOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `variationSettings` | object |  | R | hover, sticky | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `chart.advanced.legend.font` | `weight` | font-weight |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `weightFineTune` | number |  | R | hover, sticky |  |
| `chart.advanced.legend.font` | `writingMode` | enum | `horizontal-tb`, `vertical-rl`, `vertical-lr` | R | hover, sticky |  |
| `chart.advanced.legend.layout` | `align` | text |  | R | hover, sticky |  |
| `chart.advanced.legend.layout` | `position` | enum | `top`, `left`, `bottom`, `right`, `chartArea` | R | hover, sticky |  |
| `chart.advanced.legend.markers` | `boxHeight` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.markers` | `boxWidth` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.markers` | `padding` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.markers` | `pointStyle` | text |  | R | hover, sticky | JS select circle/cross/star/triangle/...; list not pinned |
| `chart.advanced.legend.markers` | `usePointStyle` | onoff |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `fillType` | enum | `none`, `gradient`, `image`, `transparent` | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `gradient` | object |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `gradient.direction` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `gradient.directionRadial` | text |  | R | hover, sticky | D4 options center/top left/top/.../left; D5 may store other position keywords |
| `chart.advanced.legend.textEffects` | `gradient.length` | text |  | R | hover, sticky | D4 background_color_gradient_unit (a unit select) converts here; corpus has "100%" and "%" |
| `chart.advanced.legend.textEffects` | `gradient.repeat` | onoff |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `gradient.stops` | gradient |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `gradient.type` | enum | `linear`, `circular`, `elliptical`, `conic`, `radial` | R | hover, sticky | D4 linear/circular/elliptical/conic; radial kept for native D5 content |
| `chart.advanced.legend.textEffects` | `imageFill.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `imageFill.height` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `imageFill.horizontalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `imageFill.position` | text |  | R | hover, sticky | CSS background-position keywords after convertBackgroundPosition (corpus center, center top) |
| `chart.advanced.legend.textEffects` | `imageFill.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `imageFill.size` | enum | `cover`, `contain`, `initial`, `stretch`, `custom` | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `imageFill.url` | image |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `imageFill.verticalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `imageFill.width` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `strokeColor` | color |  | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `strokePosition` | enum | `stroke-fill`, `fill-stroke` | R | hover, sticky |  |
| `chart.advanced.legend.textEffects` | `strokeWidth` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textShadow` | `blur` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textShadow` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.legend.textShadow` | `horizontal` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.textShadow` | `style` | text |  | R | · | none or a Divi preset name (preset1..presetN); D4 presets_shadow/select_box_shadow, corpus none/preset1-6; number of presets not pinned |
| `chart.advanced.legend.textShadow` | `vertical` | length |  | R | hover, sticky |  |
| `chart.advanced.legend.title` | `color` | color |  | desktop | hover, sticky |  |
| `chart.advanced.subtitle.font` | `capitalization` | enum | `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps`, `none` | R | hover, sticky | JS button-options {uppercase,capitalize,lowercase,smallCaps,allSmallCaps}; D4 all_caps converts through convertAllCaps; none = unset |
| `chart.advanced.subtitle.font` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `columnCount` | number |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `columnGap` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `family` | font-family |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `hyphens` | text |  | R | hover, sticky | JS divi/toggle-like control; CSS hyphens value not pinned |
| `chart.advanced.subtitle.font` | `letterSpacing` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `lineColor` | color |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `lineHeight` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `lineStyle` | enum | `solid`, `double`, `dotted`, `dashed`, `wavy` | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `lineThickness` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `opticalSizing` | enum | `auto`, `none` | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `size` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `style` | enum | list of: `italic`, `underline`, `overline`, `strikethrough`, `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps` | R | hover, sticky | list of styles; JS options {italic,underline,overline,strikethrough} (+ Ju capitalization keys, which the same Ju constant holds) |
| `chart.advanced.subtitle.font` | `textAlign` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |
| `chart.advanced.subtitle.font` | `textWrap` | text |  | R | hover, sticky | JS button-options with a computed option list (y); CSS text-wrap keyword |
| `chart.advanced.subtitle.font` | `underlineOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `variationSettings` | object |  | R | hover, sticky | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `chart.advanced.subtitle.font` | `weight` | font-weight |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `weightFineTune` | number |  | R | hover, sticky |  |
| `chart.advanced.subtitle.font` | `writingMode` | enum | `horizontal-tb`, `vertical-rl`, `vertical-lr` | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `fillType` | enum | `none`, `gradient`, `image`, `transparent` | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `gradient` | object |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `gradient.direction` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `gradient.directionRadial` | text |  | R | hover, sticky | D4 options center/top left/top/.../left; D5 may store other position keywords |
| `chart.advanced.subtitle.textEffects` | `gradient.length` | text |  | R | hover, sticky | D4 background_color_gradient_unit (a unit select) converts here; corpus has "100%" and "%" |
| `chart.advanced.subtitle.textEffects` | `gradient.repeat` | onoff |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `gradient.stops` | gradient |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `gradient.type` | enum | `linear`, `circular`, `elliptical`, `conic`, `radial` | R | hover, sticky | D4 linear/circular/elliptical/conic; radial kept for native D5 content |
| `chart.advanced.subtitle.textEffects` | `imageFill.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `imageFill.height` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `imageFill.horizontalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `imageFill.position` | text |  | R | hover, sticky | CSS background-position keywords after convertBackgroundPosition (corpus center, center top) |
| `chart.advanced.subtitle.textEffects` | `imageFill.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `imageFill.size` | enum | `cover`, `contain`, `initial`, `stretch`, `custom` | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `imageFill.url` | image |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `imageFill.verticalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `imageFill.width` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `strokeColor` | color |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `strokePosition` | enum | `stroke-fill`, `fill-stroke` | R | hover, sticky |  |
| `chart.advanced.subtitle.textEffects` | `strokeWidth` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textShadow` | `blur` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textShadow` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textShadow` | `horizontal` | length |  | R | hover, sticky |  |
| `chart.advanced.subtitle.textShadow` | `style` | text |  | R | · | none or a Divi preset name (preset1..presetN); D4 presets_shadow/select_box_shadow, corpus none/preset1-6; number of presets not pinned |
| `chart.advanced.subtitle.textShadow` | `vertical` | length |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `capitalization` | enum | `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps`, `none` | R | hover, sticky | JS button-options {uppercase,capitalize,lowercase,smallCaps,allSmallCaps}; D4 all_caps converts through convertAllCaps; none = unset |
| `chart.advanced.title.font` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `columnCount` | number |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `columnGap` | length |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `family` | font-family |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `hyphens` | text |  | R | hover, sticky | JS divi/toggle-like control; CSS hyphens value not pinned |
| `chart.advanced.title.font` | `letterSpacing` | length |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `lineColor` | color |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `lineHeight` | length |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `lineStyle` | enum | `solid`, `double`, `dotted`, `dashed`, `wavy` | R | hover, sticky |  |
| `chart.advanced.title.font` | `lineThickness` | length |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `opticalSizing` | enum | `auto`, `none` | R | hover, sticky |  |
| `chart.advanced.title.font` | `size` | length |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `style` | enum | list of: `italic`, `underline`, `overline`, `strikethrough`, `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps` | R | hover, sticky | list of styles; JS options {italic,underline,overline,strikethrough} (+ Ju capitalization keys, which the same Ju constant holds) |
| `chart.advanced.title.font` | `textAlign` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |
| `chart.advanced.title.font` | `textWrap` | text |  | R | hover, sticky | JS button-options with a computed option list (y); CSS text-wrap keyword |
| `chart.advanced.title.font` | `underlineOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `variationSettings` | object |  | R | hover, sticky | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `chart.advanced.title.font` | `weight` | font-weight |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `weightFineTune` | number |  | R | hover, sticky |  |
| `chart.advanced.title.font` | `writingMode` | enum | `horizontal-tb`, `vertical-rl`, `vertical-lr` | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `fillType` | enum | `none`, `gradient`, `image`, `transparent` | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `gradient` | object |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `gradient.direction` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `gradient.directionRadial` | text |  | R | hover, sticky | D4 options center/top left/top/.../left; D5 may store other position keywords |
| `chart.advanced.title.textEffects` | `gradient.length` | text |  | R | hover, sticky | D4 background_color_gradient_unit (a unit select) converts here; corpus has "100%" and "%" |
| `chart.advanced.title.textEffects` | `gradient.repeat` | onoff |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `gradient.stops` | gradient |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `gradient.type` | enum | `linear`, `circular`, `elliptical`, `conic`, `radial` | R | hover, sticky | D4 linear/circular/elliptical/conic; radial kept for native D5 content |
| `chart.advanced.title.textEffects` | `imageFill.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `imageFill.height` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `imageFill.horizontalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `imageFill.position` | text |  | R | hover, sticky | CSS background-position keywords after convertBackgroundPosition (corpus center, center top) |
| `chart.advanced.title.textEffects` | `imageFill.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `imageFill.size` | enum | `cover`, `contain`, `initial`, `stretch`, `custom` | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `imageFill.url` | image |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `imageFill.verticalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `imageFill.width` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `strokeColor` | color |  | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `strokePosition` | enum | `stroke-fill`, `fill-stroke` | R | hover, sticky |  |
| `chart.advanced.title.textEffects` | `strokeWidth` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textShadow` | `blur` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textShadow` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.title.textShadow` | `horizontal` | length |  | R | hover, sticky |  |
| `chart.advanced.title.textShadow` | `style` | text |  | R | · | none or a Divi preset name (preset1..presetN); D4 presets_shadow/select_box_shadow, corpus none/preset1-6; number of presets not pinned |
| `chart.advanced.title.textShadow` | `vertical` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.box` | `backgroundColor` | color |  | R | hover, sticky |  |
| `chart.advanced.tooltip.box` | `borderColor` | color |  | R | hover, sticky |  |
| `chart.advanced.tooltip.box` | `borderWidth` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.box` | `cornerRadius` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.box` | `padding` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.colorBoxes` | `boxHeight` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.colorBoxes` | `boxWidth` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.colorBoxes` | `displayColors` | onoff |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `capitalization` | enum | `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps`, `none` | R | hover, sticky | JS button-options {uppercase,capitalize,lowercase,smallCaps,allSmallCaps}; D4 all_caps converts through convertAllCaps; none = unset |
| `chart.advanced.tooltip.font` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `columnCount` | number |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `columnGap` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `family` | font-family |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `hyphens` | text |  | R | hover, sticky | JS divi/toggle-like control; CSS hyphens value not pinned |
| `chart.advanced.tooltip.font` | `letterSpacing` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `lineColor` | color |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `lineHeight` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `lineStyle` | enum | `solid`, `double`, `dotted`, `dashed`, `wavy` | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `lineThickness` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `opticalSizing` | enum | `auto`, `none` | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `size` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `style` | enum | list of: `italic`, `underline`, `overline`, `strikethrough`, `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps` | R | hover, sticky | list of styles; JS options {italic,underline,overline,strikethrough} (+ Ju capitalization keys, which the same Ju constant holds) |
| `chart.advanced.tooltip.font` | `textAlign` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |
| `chart.advanced.tooltip.font` | `textWrap` | text |  | R | hover, sticky | JS button-options with a computed option list (y); CSS text-wrap keyword |
| `chart.advanced.tooltip.font` | `underlineOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `variationSettings` | object |  | R | hover, sticky | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `chart.advanced.tooltip.font` | `weight` | font-weight |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `weightFineTune` | number |  | R | hover, sticky |  |
| `chart.advanced.tooltip.font` | `writingMode` | enum | `horizontal-tb`, `vertical-rl`, `vertical-lr` | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `fillType` | enum | `none`, `gradient`, `image`, `transparent` | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `gradient` | object |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `gradient.direction` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `gradient.directionRadial` | text |  | R | hover, sticky | D4 options center/top left/top/.../left; D5 may store other position keywords |
| `chart.advanced.tooltip.textEffects` | `gradient.length` | text |  | R | hover, sticky | D4 background_color_gradient_unit (a unit select) converts here; corpus has "100%" and "%" |
| `chart.advanced.tooltip.textEffects` | `gradient.repeat` | onoff |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `gradient.stops` | gradient |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `gradient.type` | enum | `linear`, `circular`, `elliptical`, `conic`, `radial` | R | hover, sticky | D4 linear/circular/elliptical/conic; radial kept for native D5 content |
| `chart.advanced.tooltip.textEffects` | `imageFill.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `imageFill.height` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `imageFill.horizontalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `imageFill.position` | text |  | R | hover, sticky | CSS background-position keywords after convertBackgroundPosition (corpus center, center top) |
| `chart.advanced.tooltip.textEffects` | `imageFill.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `imageFill.size` | enum | `cover`, `contain`, `initial`, `stretch`, `custom` | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `imageFill.url` | image |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `imageFill.verticalOffset` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `imageFill.width` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `strokeColor` | color |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `strokePosition` | enum | `stroke-fill`, `fill-stroke` | R | hover, sticky |  |
| `chart.advanced.tooltip.textEffects` | `strokeWidth` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textShadow` | `blur` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textShadow` | `color` | color |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textShadow` | `horizontal` | length |  | R | hover, sticky |  |
| `chart.advanced.tooltip.textShadow` | `style` | text |  | R | · | none or a Divi preset name (preset1..presetN); D4 presets_shadow/select_box_shadow, corpus none/preset1-6; number of presets not pinned |
| `chart.advanced.tooltip.textShadow` | `vertical` | length |  | R | hover, sticky |  |

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
| `css` | `chartCanvas` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
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
<summary>Render defaults (8): what Divi uses when an attribute is unset — don't repeat these</summary>

- `chart.advanced.config` — desktop `{"showLegend":"on","showLegendTitle":"off","showSubtitle":"on","showTitle":"on","showTooltip":"on","type":"line"}`
- `chart.advanced.legend.layout` — desktop `{"align":"center","position":"top"}`
- `chart.advanced.legend.markers` — desktop `{"boxHeight":"12px","boxWidth":"40px","padding":"10px","pointStyle":"circle","usePointStyle":"off"}`
- `chart.advanced.subtitle.font` — desktop `{"textAlign":"center"}`
- `chart.advanced.title.font` — desktop `{"textAlign":"center"}`
- `chart.advanced.tooltip.box` — desktop `{"backgroundColor":"rgba(0, 0, 0, 0.8)","borderColor":"rgba(0, 0, 0, 0)","borderWidth":"0px","cornerRadius":"6px","padding":"6px"}`
- `chart.advanced.tooltip.colorBoxes` — desktop `{"boxHeight":"12px","boxWidth":"12px","displayColors":"on"}`
- `module.meta.adminLabel` — desktop `"Chart"`

</details>
