# Design families (Divi 5)

Most Divi 5 blocks share the same option groups: background, font, border, spacing, sizing, animation and more.
Each group ("family") is documented once here. Each module page in [modules/](modules/README.md) lists the
attribute paths that use a family and links to its table below. The value grammars of every leaf type are in
[Leaf types](#leaf-types); the full value model is in [value-formats.md](value-formats.md).

## How attribute paths nest

A block's JSON is a tree. Its first level names an **element** of the module: `module` (the whole block) or a
named part such as `title`, `content`, `button` or `imageIcon`. The second level is the **group**:
`innerContent` (the content), `decoration` (design), `advanced` (behaviour and settings) or `meta`. A family
attribute adds the family's key under that group, and sometimes a sub-table: `module.decoration.background`,
`title.decoration.font.font`, `button.decoration.button`.

Under the attribute path come the **breakpoint** and then the **state**; the value sits at the bottom:

```json
"title": {"decoration": {"font": {"font": {
  "desktop": {"value": {"size": "18px", "color": "#1b2e1c"}, "hover": {"color": "#2e7d32"}},
  "phone":   {"value": {"size": "15px"}}
}}}}
```

- **Breakpoints:** `desktop`, `tablet` and `phone` are on by default. `phoneWide`, `tabletWide`, `widescreen` and
  `ultraWide` are off unless the site enables them (the validator warns `W5_BREAKPOINT_DISABLED`). A leaf marked
  `desktop` in the **R** column takes only a `desktop` value (`E5_BAD_BREAKPOINT` otherwise).
- **States:** `value` is the normal look; `hover`, `sticky` and the form states (`focus`, `checked`, `active`) are
  only allowed where the table's **states** column lists them. There are no enable flags: writing a `hover` value
  turns hover on. Always set `desktop.value` too (`W5_HOVER_WITHOUT_DESKTOP`).
- **Only write what you change.** A key you leave out keeps Divi's default, so `{"size": "18px"}` is a complete
  font value. The module pages list the render defaults Divi applies to unset attributes.

## How to read a family table

Each family below starts with its group key (for example `decoration.font`) and a few real attribute paths
that use it. Each `### ….<suffix>` table belongs to the attribute paths that end in that suffix: the Font
family's `### ….decoration.font.font` table types `title.decoration.font.font`,
`button.decoration.font.font`, and so on.

- **key** is a key inside the value object. A dotted key is a nested object: key `icon.color` in the Button
  family is written `{"icon": {"color": "#fff"}}`. `—` means the value itself (not an object).
- **type** is a leaf type from [Leaf types](#leaf-types); **values** lists the allowed options or units.
- **R** and **states** are as above.
- **notes** carry the schema's evidence (the Divi 4 field a key converts from, the Divi JS option set).
- "Same keys as …" means the table is identical to the one linked, so it isn't repeated.

A module has only the family attributes its page lists. A family table can hold keys a given element ignores;
use the ones that match what the element shows.

This styled button uses the Button, Background, Border, Font and Spacing families:

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call now","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"#ea580c"}}},"border":{"desktop":{"value":{"radius":{"sync":"on","topLeft":"100px","topRight":"100px","bottomRight":"100px","bottomLeft":"100px"},"styles":{"all":{"width":"0px"}}}}},"font":{"font":{"desktop":{"value":{"color":"#ffffff","size":"16px","weight":"700"}},"phone":{"value":{"size":"14px"}}}},"spacing":{"desktop":{"value":{"padding":{"top":"12px","right":"24px","bottom":"12px","left":"24px","syncVertical":"on","syncHorizontal":"on"}}}}}},"module":{"advanced":{"alignment":{"desktop":{"value":"center"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

And this section uses Background and Spacing on the `module` element, with a smaller padding on phones:

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#f8fafc"}}},"spacing":{"desktop":{"value":{"padding":{"top":"80px","bottom":"80px"}}},"phone":{"value":{"padding":{"top":"40px","bottom":"40px"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Our services"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","size":"40px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## `$variable` values

Wherever a table says a leaf accepts a `$variable` reference, the value can be a site-wide global instead of a
literal. A global color is the string
`$variable({"type":"color","value":{"name":"gcid-…","settings":{}}})$`. Global numbers, fonts and images use
`"type":"content"` with a `gvid-…` name. Rules:

- Use only ids listed in the site's `tokens.json`. The Customizer colors `gcid-primary-color`,
  `gcid-secondary-color`, `gcid-heading-color`, `gcid-body-color` and `gcid-link-color` always exist. An unknown id
  renders as nothing (`W5_UNKNOWN_VARIABLE` with `--tokens`).
- The string is JSON *inside* the block JSON, so its quotes are escaped. In canonical markup every `"` inside
  it becomes `\u0022`, as in the button example above. The validator rejects a malformed reference (`E5_BAD_VARIABLE`).
- A `$variable` counts as on-brand for the token checks. Prefer one over a literal copy of the same color.

<!-- BEGIN GENERATED -->
## Leaf types
<a id="leaf-types"></a>

Every `type` in the module pages and the tables below is one of these value grammars.

| type | grammar |
|---|---|
| `color` | hex (#rgb/#rrggbb/#rrggbbaa), rgb()/rgba()/hsl()/hsla() (any case), transparent, or a $variable({"type":"color",...})$ global color reference |
| `enum` | one of options (strings); with multiple: true, a list of options |
| `font-family` | a font family name string, or a $variable({"type":"content",...})$ global font reference |
| `font-weight` | 1..1000 as a string/number (Divi writes it into CSS verbatim; off the hundreds is only a warning), normal/bold/lighter/bolder, "variable" (Divi 5.13 variable-font mode, Font.php:360), a Divi global-font weight token ("<Font>_weight", written by Divi AI), or a $variable reference |
| `gradient` | a list of gradient stops [{position: number\|string, color: color}] |
| `html` | a string of HTML; innerContent rich text/code, stored JSON-escaped (\u003c...) in the block comment |
| `icon` | an icon object {unicode, type (divi\|fa), weight} |
| `image` | an image URL string (src/url leaves); id/alt/titleText are sibling leaves, not part of this value |
| `json` | any JSON value (list, object or scalar); structure not validated |
| `length` | a CSS length: number + unit (one of units when given), a unitless number (Divi 5 writes lengths into the CSS verbatim, Font.php:689-695, so it is valid CSS only where the property takes a plain number, e.g. lineHeight; the validator reports E5_UNITLESS_LENGTH for a non-zero one on spacing sides, sizing, border widths/radii, gaps, offsets, background positions, font size, letterSpacing and shadow lengths only, and leaves other length leaves unchecked), auto/none/inherit/initial/unset/normal/fit-content/min-content/max-content, calc()/clamp()/min()/max()/var(), a $variable({"type":"content",...})$ number variable, or "" (unset) |
| `number` | a number or a numeric string (unitless), or a $variable number reference |
| `object` | a JSON object whose keys are not validated (opaque) |
| `onoff` | "on" or "off" |
| `radius` | an object with keys from topLeft, topRight, bottomRight, bottomLeft (lengths) and sync (on/off); Divi's converter may also write a single length string |
| `spacing` | an object with keys from top, right, bottom, left (lengths) and syncVertical, syncHorizontal (on/off) |
| `text` | a string (plain text, CSS text, an id, a date, a CSS value Divi passes through verbatim) |
| `url` | a URL string (absolute, relative, #anchor, mailto:, tel:) or a $variable dynamic-content reference |

## Admin label
<a id="admin-label"></a>

Group key `meta.adminLabel` · used by 63 module(s) · e.g. `module.meta.adminLabel` (accordion), `pin.meta.adminLabel` (map-pin)

> Schema notes: divi/admin-label: the layer name

### `….meta.adminLabel`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | text |  | desktop | · |  |

## Animation
<a id="animation"></a>

Group key `decoration.animation` · used by 62 module(s) · e.g. `module.decoration.animation` (accordion), `imageIcon.decoration.animation` (blurb)

> Schema notes: divi/animation (JS: all hover:false sticky:false; D4 animation_*; style/direction/repeat/speedCurve option constants JS Ca/Sa/wa/Aa = D4 lists). Durations/delays are ms lengths; intensities and startingOpacity are unitless/% numbers stored as strings.

### `….decoration.animation`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `delay` | length |  | R | · |  |
| `direction` | enum | `center`, `left`, `right`, `bottom`, `top` | R | · |  |
| `duration` | length |  | R | · |  |
| `intensity.flip` | number |  | R | · |  |
| `intensity.fold` | number |  | R | · |  |
| `intensity.roll` | number |  | R | · |  |
| `intensity.slide` | number |  | R | · |  |
| `intensity.zoom` | number |  | R | · |  |
| `repeat` | enum | `once`, `loop` | R | · |  |
| `speedCurve` | enum | `ease-in-out`, `ease`, `ease-in`, `ease-out`, `linear`, `easeInOut`, `easeIn`, `easeOut` | R | · | animation uses CSS names (JS Aa, D4); the transition group's JS options (Bv) are camelCase; both accepted |
| `startingOpacity` | length |  | R | · |  |
| `style` | enum | `none`, `fade`, `slide`, `bounce`, `zoom`, `flip`, `fold`, `roll` | R | · |  |

## Attributes
<a id="attributes"></a>

Group key `decoration.attributes` · used by 63 module(s) · e.g. `module.decoration.attributes` (accordion)

> Schema notes: custom HTML attributes: a list of {id, name, value, targetElement} objects (corpus)

### `….decoration.attributes`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | json |  | R | · |  |

## Background
<a id="background"></a>

Group key `decoration.background` · used by 63 module(s) · e.g. `module.decoration.background` (accordion), `tab.decoration.background` (tabs), `card.decoration.background` (timeline)

> Schema notes: divi/background; see fragment background

### `….decoration.background`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | object |  | R | hover, sticky |  |
| `backgroundColor` | color |  | R | hover, sticky |  |
| `color` | color |  | R | hover, sticky |  |
| `enableColor` | onoff |  | R | hover, sticky |  |
| `gradient` | object |  | R | hover, sticky |  |
| `gradient.direction` | length |  | R | hover, sticky |  |
| `gradient.directionRadial` | text |  | R | hover, sticky | D4 options center/top left/top/.../left; D5 may store other position keywords |
| `gradient.enabled` | onoff |  | R | hover, sticky |  |
| `gradient.length` | text |  | R | hover, sticky | D4 background_color_gradient_unit (a unit select) converts here; corpus has "100%" and "%" |
| `gradient.overlaysImage` | onoff |  | R | hover, sticky |  |
| `gradient.repeat` | onoff |  | R | hover, sticky |  |
| `gradient.stops` | gradient |  | R | hover, sticky |  |
| `gradient.stops[0].color` | color |  | R | hover, sticky |  |
| `gradient.stops[0].position` | text |  | R | hover, sticky |  |
| `gradient.stops[1].color` | color |  | R | hover, sticky |  |
| `gradient.stops[1].position` | text |  | R | hover, sticky |  |
| `gradient.type` | enum | `linear`, `circular`, `elliptical`, `conic`, `radial` | R | hover, sticky | D4 linear/circular/elliptical/conic; radial kept for native D5 content |
| `image.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `image.enabled` | onoff |  | R | hover, sticky |  |
| `image.height` | length |  | R | hover, sticky |  |
| `image.horizontalOffset` | length |  | R | hover, sticky |  |
| `image.parallax.enabled` | onoff |  | R | hover, sticky |  |
| `image.parallax.method` | enum | `on`, `off` | R | hover, sticky | D4 parallax_method on (true parallax) / off (CSS) |
| `image.position` | text |  | R | hover, sticky | CSS background-position keywords after convertBackgroundPosition (corpus center, center top) |
| `image.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `image.size` | enum | `cover`, `contain`, `initial`, `stretch`, `custom` | R | hover, sticky |  |
| `image.title` | text |  | R | hover, sticky |  |
| `image.url` | image |  | R | hover, sticky |  |
| `image.verticalOffset` | length |  | R | hover, sticky |  |
| `image.width` | length |  | R | hover, sticky |  |
| `mask.aspectRatio` | enum | `landscape`, `square`, `portrait` | R | hover, sticky |  |
| `mask.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `mask.color` | color |  | R | hover, sticky |  |
| `mask.enabled` | onoff |  | R | hover, sticky |  |
| `mask.height` | length |  | R | hover, sticky |  |
| `mask.horizontalOffset` | length |  | R | hover, sticky |  |
| `mask.position` | text |  | R | hover, sticky | D4 top_left..bottom_right; D5 position keywords |
| `mask.size` | enum | `stretch`, `cover`, `contain`, `custom` | R | hover, sticky |  |
| `mask.style` | text |  | R | hover, sticky | a mask shape slug (D4 select-mask: layer-blob, arch, ..., wave; corpus diagonal, diagonal-bars, caret) |
| `mask.transform` | json |  | R | hover, sticky | D4 multiple_buttons through convertSvgTransform |
| `mask.verticalOffset` | length |  | R | hover, sticky |  |
| `mask.width` | length |  | R | hover, sticky |  |
| `pattern.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `pattern.color` | color |  | R | hover, sticky |  |
| `pattern.enabled` | onoff |  | R | hover, sticky |  |
| `pattern.height` | length |  | R | hover, sticky |  |
| `pattern.horizontalOffset` | length |  | R | hover, sticky |  |
| `pattern.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `pattern.repeatOrigin` | text |  | R | hover, sticky | D4 top_left..bottom_right; corpus "left top" |
| `pattern.size` | enum | `initial`, `cover`, `contain`, `stretch`, `custom` | R | hover, sticky |  |
| `pattern.style` | text |  | R | hover, sticky | a pattern slug (D4 select-pattern: polka-dots, 3d-diamonds, ..., zig-zag) |
| `pattern.transform` | json |  | R | hover, sticky | D4 multiple_buttons through convertSvgTransform |
| `pattern.verticalOffset` | length |  | R | hover, sticky |  |
| `pattern.width` | length |  | R | hover, sticky |  |
| `video.allowPlayerPause` | onoff |  | R | hover, sticky |  |
| `video.enabledMp4` | onoff |  | R | hover, sticky |  |
| `video.enabledWebm` | onoff |  | R | hover, sticky |  |
| `video.height` | text |  | R | hover, sticky |  |
| `video.mp4` | url |  | R | hover, sticky |  |
| `video.pauseOutsideViewport` | onoff |  | R | hover, sticky |  |
| `video.webm` | url |  | R | hover, sticky |  |
| `video.width` | text |  | R | hover, sticky |  |

## Body font
<a id="font-body"></a>

Group key `decoration.bodyFont` · used by 24 module(s) · e.g. `content.decoration.bodyFont.ol.font` (accordion), `content.decoration.bodyFont.ol.list` (accordion), `content.decoration.bodyFont.ul.font` (accordion)

> Schema notes: divi/font-body: body/link/ul/ol/quote sub-fonts + dropCap; quote.border = blockquote left border (D4 quote_border_*)

### `….decoration.bodyFont.body.font`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `capitalization` | enum | `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps`, `none` | R | hover, sticky | JS button-options {uppercase,capitalize,lowercase,smallCaps,allSmallCaps}; D4 all_caps converts through convertAllCaps; none = unset |
| `color` | color |  | R | hover, sticky |  |
| `columnCount` | number |  | R | hover, sticky |  |
| `columnGap` | length |  | R | hover, sticky |  |
| `family` | font-family |  | R | hover, sticky |  |
| `hyphens` | text |  | R | hover, sticky | JS divi/toggle-like control; CSS hyphens value not pinned |
| `letterSpacing` | length |  | R | hover, sticky |  |
| `lineColor` | color |  | R | hover, sticky |  |
| `lineHeight` | length |  | R | hover, sticky |  |
| `lineStyle` | enum | `solid`, `double`, `dotted`, `dashed`, `wavy` | R | hover, sticky |  |
| `lineThickness` | length |  | R | hover, sticky |  |
| `opticalSizing` | enum | `auto`, `none` | R | hover, sticky |  |
| `size` | length |  | R | hover, sticky |  |
| `style` | enum | list of: `italic`, `underline`, `overline`, `strikethrough`, `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps` | R | hover, sticky | list of styles; JS options {italic,underline,overline,strikethrough} (+ Ju capitalization keys, which the same Ju constant holds) |
| `textAlign` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |
| `textWrap` | text |  | R | hover, sticky | JS button-options with a computed option list (y); CSS text-wrap keyword |
| `underlineOffset` | length |  | R | hover, sticky |  |
| `variationSettings` | object |  | R | hover, sticky | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `weight` | font-weight |  | R | hover, sticky |  |
| `weightFineTune` | number |  | R | hover, sticky |  |
| `writingMode` | enum | `horizontal-tb`, `vertical-rl`, `vertical-lr` | R | hover, sticky |  |

### `….decoration.bodyFont.body.list`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `paragraphSpacing` | length |  | R | hover, sticky |  |

### `….decoration.bodyFont.body.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.bodyFont.body.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.bodyFont.dropCap.font`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `capitalization` | enum | `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps`, `none` | R | hover, sticky | JS button-options {uppercase,capitalize,lowercase,smallCaps,allSmallCaps}; D4 all_caps converts through convertAllCaps; none = unset |
| `color` | color |  | R | hover, sticky |  |
| `dropCapLineSize` | number |  | R | hover, sticky |  |
| `dropCapSpacing` | length |  | R | hover, sticky |  |
| `family` | font-family |  | R | hover, sticky |  |
| `lineColor` | color |  | R | hover, sticky |  |
| `lineStyle` | enum | `solid`, `double`, `dotted`, `dashed`, `wavy` | R | hover, sticky |  |
| `lineThickness` | length |  | R | hover, sticky |  |
| `opticalSizing` | enum | `auto`, `none` | R | hover, sticky |  |
| `style` | enum | list of: `italic`, `underline`, `overline`, `strikethrough`, `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps` | R | hover, sticky | list of styles; JS options {italic,underline,overline,strikethrough} (+ Ju capitalization keys, which the same Ju constant holds) |
| `underlineOffset` | length |  | R | hover, sticky |  |
| `variationSettings` | object |  | R | hover, sticky | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `weight` | font-weight |  | R | hover, sticky |  |
| `weightFineTune` | number |  | R | hover, sticky |  |

### `….decoration.bodyFont.dropCap.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.bodyFont.link.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.bodyFont.link.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.bodyFont.link.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.bodyFont.ol.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.bodyFont.ol.list`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `itemIndent` | length |  | R | hover, sticky |  |
| `listSpacing` | length |  | R | hover, sticky |  |
| `position` | enum | `inside`, `outside` | R | hover, sticky |  |
| `type` | text |  | R | hover, sticky | CSS list-style-type keyword |

### `….decoration.bodyFont.ol.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.bodyFont.ol.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.bodyFont.quote.border`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `styles.left.color` | color |  | R | hover, sticky |  |
| `styles.left.width` | length |  | R | hover, sticky |  |

### `….decoration.bodyFont.quote.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.bodyFont.quote.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.bodyFont.quote.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.bodyFont.ul.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.bodyFont.ul.list`

Same keys as [Body font → `….decoration.bodyFont.ol.list`](#font-body).

### `….decoration.bodyFont.ul.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.bodyFont.ul.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

## Border
<a id="border"></a>

Group key `decoration.border` · used by 62 module(s) · e.g. `module.decoration.border` (accordion), `card.decoration.border` (timeline), `icon.decoration.border` (icon-list)

> Schema notes: divi/border; see fragment border

### `….decoration.border`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `radius` | radius |  | R | hover, sticky |  |
| `styles` | object |  | R | hover, sticky |  |
| `styles.all.color` | color |  | R | hover, sticky |  |
| `styles.all.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky |  |
| `styles.all.width` | length |  | R | hover, sticky |  |
| `styles.bottom.color` | color |  | R | hover, sticky |  |
| `styles.bottom.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky |  |
| `styles.bottom.width` | length |  | R | hover, sticky |  |
| `styles.left.color` | color |  | R | hover, sticky |  |
| `styles.left.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky |  |
| `styles.left.width` | length |  | R | hover, sticky |  |
| `styles.right.color` | color |  | R | hover, sticky |  |
| `styles.right.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky |  |
| `styles.right.width` | length |  | R | hover, sticky |  |
| `styles.top.color` | color |  | R | hover, sticky |  |
| `styles.top.style` | enum | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `none` | R | hover, sticky |  |
| `styles.top.width` | length |  | R | hover, sticky |  |

## Box shadow
<a id="box-shadow"></a>

Group key `decoration.boxShadow` · used by 63 module(s) · e.g. `module.decoration.boxShadow` (accordion), `card.decoration.boxShadow` (timeline), `icon.decoration.boxShadow` (icon-list)

> Schema notes: divi/box-shadow

### `….decoration.boxShadow`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `blur` | length |  | R | hover, sticky |  |
| `color` | color |  | R | hover, sticky |  |
| `horizontal` | length |  | R | hover, sticky |  |
| `position` | enum | `outer`, `inner` | R | hover, sticky |  |
| `spread` | length |  | R | hover, sticky |  |
| `style` | text |  | R | · | none or a Divi preset name (preset1..presetN); D4 presets_shadow/select_box_shadow, corpus none/preset1-6; number of presets not pinned |
| `vertical` | length |  | R | hover, sticky |  |

## Button
<a id="button"></a>

Group key `decoration.button` · used by 17 module(s) · e.g. `button.decoration.button` (button), `buttonOne.decoration.button` (fullwidth-header), `buttonTwo.decoration.button` (fullwidth-header)

> Schema notes: divi/button. Divi's expander also lists the group's own sub-attrs under the button attr itself (X.decoration.button.decoration.background, ...font.font, .innerContent); they are kept as declared by the dump.

### `….decoration.button`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `alignment` | enum | `left`, `center`, `right` | R | · |  |
| `enable` | onoff |  | R | hover, sticky |  |
| `icon.color` | color |  | R | hover, sticky |  |
| `icon.enable` | onoff |  | R | · |  |
| `icon.onHover` | onoff |  | R | hover, sticky |  |
| `icon.placement` | enum | `right`, `left` | R | hover, sticky |  |
| `icon.settings` | icon |  | R | hover | JS icon-picker hover:false preset html/style; D4 button_icon through convertButtonIcon |

### `….decoration.button.decoration.background`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `color` | color |  | R | hover, sticky |  |
| `enableColor` | onoff |  | R | hover, sticky |  |
| `gradient` | object |  | R | hover, sticky |  |
| `gradient.direction` | length |  | R | hover, sticky |  |
| `gradient.directionRadial` | text |  | R | hover, sticky | D4 options center/top left/top/.../left; D5 may store other position keywords |
| `gradient.enabled` | onoff |  | R | hover, sticky |  |
| `gradient.length` | text |  | R | hover, sticky | D4 background_color_gradient_unit (a unit select) converts here; corpus has "100%" and "%" |
| `gradient.overlaysImage` | onoff |  | R | hover, sticky |  |
| `gradient.repeat` | onoff |  | R | hover, sticky |  |
| `gradient.stops` | gradient |  | R | hover, sticky |  |
| `gradient.type` | enum | `linear`, `circular`, `elliptical`, `conic`, `radial` | R | hover, sticky | D4 linear/circular/elliptical/conic; radial kept for native D5 content |
| `image.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `image.enabled` | onoff |  | R | hover, sticky |  |
| `image.height` | length |  | R | hover, sticky |  |
| `image.horizontalOffset` | length |  | R | hover, sticky |  |
| `image.parallax.enabled` | onoff |  | R | hover, sticky |  |
| `image.parallax.method` | enum | `on`, `off` | R | hover, sticky | D4 parallax_method on (true parallax) / off (CSS) |
| `image.position` | text |  | R | hover, sticky | CSS background-position keywords after convertBackgroundPosition (corpus center, center top) |
| `image.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `image.size` | enum | `cover`, `contain`, `initial`, `stretch`, `custom` | R | hover, sticky |  |
| `image.title` | text |  | R | hover, sticky |  |
| `image.url` | image |  | R | hover, sticky |  |
| `image.verticalOffset` | length |  | R | hover, sticky |  |
| `image.width` | length |  | R | hover, sticky |  |
| `mask.aspectRatio` | enum | `landscape`, `square`, `portrait` | R | hover, sticky |  |
| `mask.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `mask.color` | color |  | R | hover, sticky |  |
| `mask.enabled` | onoff |  | R | hover, sticky |  |
| `mask.height` | length |  | R | hover, sticky |  |
| `mask.horizontalOffset` | length |  | R | hover, sticky |  |
| `mask.position` | text |  | R | hover, sticky | D4 top_left..bottom_right; D5 position keywords |
| `mask.size` | enum | `stretch`, `cover`, `contain`, `custom` | R | hover, sticky |  |
| `mask.style` | text |  | R | hover, sticky | a mask shape slug (D4 select-mask: layer-blob, arch, ..., wave; corpus diagonal, diagonal-bars, caret) |
| `mask.transform` | json |  | R | hover, sticky | D4 multiple_buttons through convertSvgTransform |
| `mask.verticalOffset` | length |  | R | hover, sticky |  |
| `mask.width` | length |  | R | hover, sticky |  |
| `pattern.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `pattern.color` | color |  | R | hover, sticky |  |
| `pattern.enabled` | onoff |  | R | hover, sticky |  |
| `pattern.height` | length |  | R | hover, sticky |  |
| `pattern.horizontalOffset` | length |  | R | hover, sticky |  |
| `pattern.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `pattern.repeatOrigin` | text |  | R | hover, sticky | D4 top_left..bottom_right; corpus "left top" |
| `pattern.size` | enum | `initial`, `cover`, `contain`, `stretch`, `custom` | R | hover, sticky |  |
| `pattern.style` | text |  | R | hover, sticky | a pattern slug (D4 select-pattern: polka-dots, 3d-diamonds, ..., zig-zag) |
| `pattern.transform` | json |  | R | hover, sticky | D4 multiple_buttons through convertSvgTransform |
| `pattern.verticalOffset` | length |  | R | hover, sticky |  |
| `pattern.width` | length |  | R | hover, sticky |  |
| `video.allowPlayerPause` | onoff |  | R | hover, sticky |  |
| `video.height` | text |  | R | hover, sticky |  |
| `video.mp4` | url |  | R | hover, sticky |  |
| `video.pauseOutsideViewport` | onoff |  | R | hover, sticky |  |
| `video.webm` | url |  | R | hover, sticky |  |
| `video.width` | text |  | R | hover, sticky |  |

### `….decoration.button.decoration.border`

Same keys as [Border → `….decoration.border`](#border).

### `….decoration.button.decoration.boxShadow`

Same keys as [Box shadow → `….decoration.boxShadow`](#box-shadow).

### `….decoration.button.decoration.button`

Same keys as [Button → `….decoration.button`](#button).

### `….decoration.button.decoration.font.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.button.decoration.font.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.button.decoration.font.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.button.decoration.sizing`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `alignSelf` | text |  | R | · |  |
| `alignment` | enum | `left`, `center`, `right` | R | · |  |
| `aspectRatio` | text |  | R | hover, sticky | JS divi/aspect-ratio: a ratio like 16/9 or auto |
| `flexGrow` | number |  | R | hover, sticky |  |
| `flexShrink` | number |  | R | hover, sticky |  |
| `flexType` | text |  | R | · | JS divi/select-column-class, e.g. 24_24, 12_24 |
| `gridAlignSelf` | text |  | desktop | · |  |
| `gridColumnEnd` | text |  | R | hover, sticky |  |
| `gridColumnSpan` | text |  | R | hover, sticky |  |
| `gridColumnStart` | text |  | R | hover, sticky |  |
| `gridJustifySelf` | enum | `start`, `center`, `end`, `stretch`, `baseline` | desktop | · |  |
| `gridRowEnd` | text |  | R | hover, sticky |  |
| `gridRowSpan` | text |  | R | hover, sticky |  |
| `gridRowStart` | text |  | R | hover, sticky |  |
| `height` | length |  | R | hover, sticky |  |
| `maxHeight` | length |  | R | hover, sticky |  |
| `maxWidth` | length |  | R | hover, sticky |  |
| `minHeight` | length |  | R | hover, sticky |  |
| `size` | length |  | R | hover, sticky |  |
| `width` | length |  | R | hover, sticky |  |

### `….decoration.button.decoration.spacing`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `margin` | spacing |  | R | hover, sticky |  |
| `padding` | spacing |  | R | hover, sticky |  |

### `….decoration.button.innerContent`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `linkTarget` | enum | `on`, `off` | desktop | · | D4 url_new_window off/on (on = new tab) |
| `linkUrl` | url |  | desktop | · |  |
| `rel` | enum | list of: `bookmark`, `external`, `nofollow`, `noreferrer`, `noopener` | desktop | · | D4 button_rel multiple_checkboxes through convertButtonRel |
| `text` | text |  | R | hover, sticky |  |

## CSS ID & classes
<a id="id-classes"></a>

Group key `advanced.htmlAttributes` · used by 46 module(s) · e.g. `module.advanced.htmlAttributes` (accordion), `column1.advanced.htmlAttributes` (section), `column2.advanced.htmlAttributes` (section)

> Schema notes: divi/id-classes (D4 module_id/module_class)

### `….advanced.htmlAttributes`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `class` | text |  | desktop | · |  |
| `id` | text |  | desktop | · |  |

## Conditions
<a id="conditions"></a>

Group key `decoration.conditions` · used by 63 module(s) · e.g. `module.decoration.conditions` (accordion)

> Schema notes: display conditions (D4 display_conditions through convert_conditions): a list of condition objects

### `….decoration.conditions`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | json |  | desktop | · |  |

## Disabled on
<a id="disabled-on"></a>

Group key `decoration.disabledOn` · used by 62 module(s) · e.g. `module.decoration.disabledOn` (accordion)

> Schema notes: divi/disabled-on (JS group wr/Ar): a responsive attr whose per-breakpoint value is "on" (disabled) or "off". Divi's converter (AdvancedOptionConversion::convertDisabledOnBreakpoint) writes the D4 items as the pseudo-breakpoints desktopAbove / tabletOnly (index.json breakpoints.disabledOnItems), which the VB migrates on edit; both forms are valid.

### `….decoration.disabledOn`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | onoff |  | R + desktopAbove, tabletOnly | · |  |

## Dividers
<a id="dividers"></a>

Group key `advanced.dividers` · used by 1 module(s) · e.g. `module.advanced.dividers.top` (section), `module.advanced.dividers.bottom` (section)

> Schema notes: section dividers (D4 {top,bottom}_divider_*): style list D4 divider options; arrangement JS Ac above/below vs D4 above_content/below_content; flip D4 multiple_buttons through dividersFlip -> list

### `….advanced.dividers.bottom`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `arrangement` | enum | `above`, `below`, `above_content`, `below_content` | R | · |  |
| `color` | color |  | R | hover, sticky |  |
| `flip` | enum | list of: `horizontal`, `vertical` | R | · |  |
| `height` | length |  | R | hover, sticky |  |
| `repeat` | text |  | R | hover, sticky |  |
| `style` | enum | `none`, `slant`, `slant2`, `arrow`, `arrow2`, `arrow3`, `ramp`, `ramp2`, `curve`, `curve2`, `mountains`, `mountains2`, `wave`, `wave2`, `waves` … (27 options; full list in scripts/schema5) | R | · |  |

### `….advanced.dividers.top`

Same keys as [Dividers → `….advanced.dividers.bottom`](#dividers).

## Elements
<a id="elements"></a>

Group key `advanced.elements` · used by 54 module(s) · e.g. `module.advanced.elements.structure` (accordion)

> Schema notes: divi/elements: structure (opaque)

### `….advanced.elements.structure`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | json |  | desktop | · |  |

## Email service
<a id="email-service"></a>

Group key `advanced.emailService` · used by 1 module(s) · e.g. `module.advanced.emailService` (signup)

> Schema notes: divi/email-service (D4 provider list; account through convertEmailServiceAccount = "<name>|<list id>" strings, corpus)

### `….advanced.emailService`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `account` | text |  | desktop | · |  |
| `provider` | text |  | desktop | · | D4 list: activecampaign, aweber, ..., mailchimp, ..., sendinblue; D5 may add providers |

## Filters
<a id="filters"></a>

Group key `decoration.filters` · used by 63 module(s) · e.g. `module.decoration.filters` (accordion), `map.decoration.filters` (fullwidth-map), `image.decoration.filters` (audio)

> Schema notes: divi/filters (JS ranges: blur px, hueRotate deg, others %; D4 filter_*). blendMode JS jc = D4 mix_blend_mode list.

### `….decoration.filters`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `backdropBlur` | length |  | R | hover, sticky |  |
| `backdropInvert` | length |  | R | hover, sticky |  |
| `backdropSepia` | length |  | R | hover, sticky |  |
| `blendMode` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | · |  |
| `blur` | length |  | R | hover, sticky |  |
| `brightness` | length |  | R | hover, sticky |  |
| `contrast` | length |  | R | hover, sticky |  |
| `hueRotate` | length |  | R | hover, sticky |  |
| `invert` | length |  | R | hover, sticky |  |
| `opacity` | length |  | R | hover, sticky |  |
| `saturate` | length |  | R | hover, sticky |  |
| `sepia` | length |  | R | hover, sticky |  |

## Fit
<a id="fit"></a>

Group key `decoration.fit` · used by 10 module(s) · e.g. `image.decoration.fit` (audio), `portrait.decoration.fit` (testimonial), `imageIcon.decoration.fit` (blurb)

> Schema notes: divi/fit (JS: objectFit literal options, objectPosition divi/object-position)

### `….decoration.fit`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `objectFit` | enum | `fill`, `contain`, `cover`, `none`, `scale-down` | R | hover |  |
| `objectPosition` | text |  | R | hover | CSS object-position |

## Font
<a id="font"></a>

Group key `decoration.font` · used by 41 module(s) · e.g. `tab.decoration.font` (tabs), `date.decoration.font` (timeline), `list.decoration.font` (table-of-contents)

> Schema notes: divi/font (all 5 variants: has_heading_level/has_list/has_paragraph/has_border). The dump also lists color/size/textAlign/headingLevel directly on the bare attr ("") for a few elements (accordion/toggle openToggle, pricing-tables featured*, gallery pagination), but Divi 5.13.1 styles text only from .font.font/.textShadow/.textEffects (FontStyle.php); bare keys render nothing (live check).

### `….decoration.font`

> **Container only: write the text styles (size, color, weight, family, headingLevel, …) under `….decoration.font.font`. Divi 5.13.1 styles text from `….font.font`, `.textShadow` and `.textEffects` only; keys written directly here render nothing (live check: a blurb and a heading title, and a toggle's `openToggle`), and the validator warns `W5_BARE_FONT`.**

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | object |  | R | hover, sticky |  |
| `color` | color |  | R | hover, sticky |  |
| `headingLevel` | enum | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | desktop | · |  |
| `size` | length |  | R | hover, sticky |  |
| `textAlign` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |

### `….decoration.font.font`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `capitalization` | enum | `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps`, `none` | R | hover, sticky | JS button-options {uppercase,capitalize,lowercase,smallCaps,allSmallCaps}; D4 all_caps converts through convertAllCaps; none = unset |
| `color` | color |  | R | hover, sticky |  |
| `columnCount` | number |  | R | hover, sticky |  |
| `columnGap` | length |  | R | hover, sticky |  |
| `family` | font-family |  | R | hover, sticky |  |
| `headingLevel` | enum | `h1`, `h2`, `h3`, `h4`, `h5`, `h6` | desktop | · | JS Ku, D4 multiple_buttons h1..h6 |
| `hyphens` | text |  | R | hover, sticky | JS divi/toggle-like control; CSS hyphens value not pinned |
| `letterSpacing` | length |  | R | hover, sticky |  |
| `lineColor` | color |  | R | hover, sticky |  |
| `lineHeight` | length |  | R | hover, sticky |  |
| `lineStyle` | enum | `solid`, `double`, `dotted`, `dashed`, `wavy` | R | hover, sticky |  |
| `lineThickness` | length |  | R | hover, sticky |  |
| `opticalSizing` | enum | `auto`, `none` | R | hover, sticky |  |
| `size` | length |  | R | hover, sticky |  |
| `style` | enum | list of: `italic`, `underline`, `overline`, `strikethrough`, `uppercase`, `capitalize`, `lowercase`, `smallCaps`, `allSmallCaps` | R | hover, sticky | list of styles; JS options {italic,underline,overline,strikethrough} (+ Ju capitalization keys, which the same Ju constant holds) |
| `textAlign` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |
| `textWrap` | text |  | R | hover, sticky | JS button-options with a computed option list (y); CSS text-wrap keyword |
| `underlineOffset` | length |  | R | hover, sticky |  |
| `variationSettings` | object |  | R | hover, sticky | variable-font axis settings; weight "variable" selects variable-weight mode (Font.php:360) |
| `weight` | font-weight |  | R | hover, sticky |  |
| `weightFineTune` | number |  | R | hover, sticky |  |
| `writingMode` | enum | `horizontal-tb`, `vertical-rl`, `vertical-lr` | R | hover, sticky |  |

### `….decoration.font.textEffects`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `fillType` | enum | `none`, `gradient`, `image`, `transparent` | R | hover, sticky |  |
| `gradient` | object |  | R | hover, sticky |  |
| `gradient.direction` | length |  | R | hover, sticky |  |
| `gradient.directionRadial` | text |  | R | hover, sticky | D4 options center/top left/top/.../left; D5 may store other position keywords |
| `gradient.length` | text |  | R | hover, sticky | D4 background_color_gradient_unit (a unit select) converts here; corpus has "100%" and "%" |
| `gradient.repeat` | onoff |  | R | hover, sticky |  |
| `gradient.stops` | gradient |  | R | hover, sticky |  |
| `gradient.type` | enum | `linear`, `circular`, `elliptical`, `conic`, `radial` | R | hover, sticky | D4 linear/circular/elliptical/conic; radial kept for native D5 content |
| `imageFill.blend` | enum | `normal`, `multiply`, `screen`, `overlay`, `darken`, `lighten`, `color-dodge`, `color-burn`, `hard-light`, `soft-light`, `difference`, `exclusion`, `hue`, `saturation`, `color` … (16 options; full list in scripts/schema5) | R | hover, sticky |  |
| `imageFill.height` | length |  | R | hover, sticky |  |
| `imageFill.horizontalOffset` | length |  | R | hover, sticky |  |
| `imageFill.position` | text |  | R | hover, sticky | CSS background-position keywords after convertBackgroundPosition (corpus center, center top) |
| `imageFill.repeat` | enum | `repeat`, `repeat-x`, `repeat-y`, `space`, `round`, `no-repeat` | R | hover, sticky |  |
| `imageFill.size` | enum | `cover`, `contain`, `initial`, `stretch`, `custom` | R | hover, sticky |  |
| `imageFill.url` | image |  | R | hover, sticky |  |
| `imageFill.verticalOffset` | length |  | R | hover, sticky |  |
| `imageFill.width` | length |  | R | hover, sticky |  |
| `strokeColor` | color |  | R | hover, sticky |  |
| `strokePosition` | enum | `stroke-fill`, `fill-stroke` | R | hover, sticky |  |
| `strokeWidth` | length |  | R | hover, sticky |  |

### `….decoration.font.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

## Gutter
<a id="gutter"></a>

Group key `advanced.gutter` · used by 3 module(s) · e.g. `module.advanced.gutter` (row)

> Schema notes: divi/gutter (row gutters; D4 use_custom_gutter/gutter_width/make_equal). width is the gutter number 1..4 (JS range min 1 max 4 unitless); alignColumns JS button-options (flex-start/center/...) -> text

### `….advanced.gutter`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `alignColumns` | text |  | R | · |  |
| `enable` | onoff |  | R | · |  |
| `makeEqual` | onoff |  | desktop | · |  |
| `width` | number |  | desktop | · |  |

## Heading fonts
<a id="font-header"></a>

Group key `decoration.headingFont` · used by 1 module(s) · e.g. `content.decoration.headingFont.h1.font` (text), `content.decoration.headingFont.h2.font` (text), `content.decoration.headingFont.h3.font` (text)

> Schema notes: divi/font-header: h1..h6 sub-fonts (D4 header_{2..6}_* fonts)

### `….decoration.headingFont.h1.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.headingFont.h1.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.headingFont.h1.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.headingFont.h2.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.headingFont.h2.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.headingFont.h2.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.headingFont.h3.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.headingFont.h3.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.headingFont.h3.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.headingFont.h4.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.headingFont.h4.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.headingFont.h4.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.headingFont.h5.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.headingFont.h5.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.headingFont.h5.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

### `….decoration.headingFont.h6.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.headingFont.h6.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.headingFont.h6.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

## Html
<a id="html"></a>

Group key `advanced.html` · used by 64 module(s) · e.g. `module.advanced.html` (accordion), `pin.advanced.html` (map-pin)

> Schema notes: divi/html (elementType select of HTML tag names, htmlBefore/After code)

### `….advanced.html`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `elementType` | text |  | desktop | · | an HTML tag name from Divi's VALID_HTML_ELEMENT_TYPES |
| `htmlAfter` | html |  | desktop | · |  |
| `htmlBefore` | html |  | desktop | · |  |

## Icon
<a id="icon"></a>

Group key `decoration.icon` · used by 15 module(s) · e.g. `radio.decoration.icon` (contact-field), `marker.decoration.icon` (timeline), `social.decoration.icon` (team-member)

> Schema notes: divi/icon; see fragment icon-group

### `….decoration.icon`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | object |  | R | hover, sticky |  |
| `color` | color |  | R | hover, sticky |  |
| `show` | onoff |  | R | hover, sticky |  |
| `size` | length |  | R | hover, sticky |  |
| `type` | enum | `divi`, `fa` | R | hover, sticky |  |
| `unicode` | text |  | R | hover, sticky |  |
| `useSize` | onoff |  | R | hover |  |
| `weight` | font-weight |  | R | hover, sticky |  |

## Inline fonts
<a id="inline-font"></a>

Group key `decoration.inlineFont` · used by 12 module(s) · e.g. `content.decoration.inlineFont` (accordion-item)

> Schema notes: fonts used inside rich text (D4 inline_fonts through convertInlineFont): a list of family names

### `….decoration.inlineFont`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `families` | json |  | desktop | · | D4 inline_fonts (comma list) through convertInlineFont |

## Interactions
<a id="interactions"></a>

Group key `decoration.interactions` · used by 62 module(s) · e.g. `module.decoration.interactions` (accordion)

> Schema notes: D5 interactions (triggers/effects list); structure not dumped

### `….decoration.interactions`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | json |  | desktop | · |  |

## Label font
<a id="font-label"></a>

Group key `decoration.labelFont` · used by 4 module(s) · e.g. `field.decoration.labelFont.font` (contact-field), `field.decoration.labelFont.textShadow` (contact-field), `field.decoration.labelFont.textEffects` (contact-field)

> Schema notes: form label font (same divi/font leaves)

### `….decoration.labelFont.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.labelFont.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.labelFont.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

## Layout
<a id="layout"></a>

Group key `decoration.layout` · used by 52 module(s) · e.g. `module.decoration.layout` (accordion), `card.decoration.layout` (timeline), `track.decoration.layout` (timeline)

> Schema notes: divi/layout (JS, D5-only; features hover:false sticky:false). display JS ly (converter writes block); flexDirection JS uy; grid options JS by/hy/vy/fy/gy. justifyContent/alignItems/alignContent/flexWrap build their options elsewhere -> text (CSS keywords). Grid templates/gaps are CSS text/lengths.

### `….decoration.layout`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `alignContent` | text |  | R | · |  |
| `alignItems` | text |  | R | · |  |
| `collapseEmptyColumns` | onoff |  | R | · |  |
| `columnGap` | length |  | R | · |  |
| `display` | enum | `block`, `flex`, `grid` | R | · |  |
| `flexDirection` | enum | `row`, `row-reverse`, `column`, `column-reverse` | R | · |  |
| `flexWrap` | text |  | R | · |  |
| `gridAutoColumns` | text |  | R | · |  |
| `gridAutoFlow` | enum | `row`, `column` | R | · |  |
| `gridAutoRows` | text |  | R | · |  |
| `gridColumnCount` | number |  | R | · |  |
| `gridColumnMinWidth` | length |  | R | · |  |
| `gridColumnWidth` | length |  | R | · |  |
| `gridColumnWidths` | enum | `equal`, `equalMinimum`, `equalFixed`, `auto`, `manual` | R | · |  |
| `gridDensity` | enum | `dense`, `auto` | R | · |  |
| `gridJustifyItems` | enum | `start`, `center`, `end`, `stretch`, `baseline` | R | · |  |
| `gridOffsetRules` | json |  | R | · | JS divi/grid-offset-rules |
| `gridRowCount` | text |  | R | · | range with default auto |
| `gridRowHeight` | length |  | R | · |  |
| `gridRowHeights` | enum | `auto`, `equal`, `minimum`, `fixed`, `manual` | R | · |  |
| `gridRowMinHeight` | length |  | R | · |  |
| `gridTemplateColumns` | text |  | R | · |  |
| `gridTemplateRows` | text |  | R | · |  |
| `justifyContent` | text |  | R | · |  |
| `rowGap` | length |  | R | · |  |

## Link
<a id="link"></a>

Group key `advanced.link` · used by 53 module(s) · e.g. `module.advanced.link` (accordion)

> Schema notes: divi/link (D4 link_option_url / link_option_url_new_window off|on; lightbox toggle)

### `….advanced.link`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `lightbox` | onoff |  | desktop | · |  |
| `target` | enum | `on`, `off` | desktop | · |  |
| `url` | url |  | desktop | · |  |

## Loop
<a id="loop"></a>

Group key `advanced.loop` · used by 58 module(s) · e.g. `module.advanced.loop` (accordion), `pin.advanced.loop` (map-pin)

> Schema notes: divi/loop query builder (JS, D5-only): selects with dynamic options (post types, taxonomies) -> text; tag inputs / meta query -> json

### `….advanced.loop`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `enable` | onoff |  | desktop | · |  |
| `excludeCurrentPost` | onoff |  | desktop | · |  |
| `excludePostWithSpecificTerms` | json |  | desktop | · |  |
| `excludeSpecificPosts` | json |  | desktop | · |  |
| `ignoreStickysPost` | onoff |  | desktop | · |  |
| `includePostWithSpecificTerms` | json |  | desktop | · |  |
| `includeSpecificPosts` | json |  | desktop | · |  |
| `metaQuery` | json |  | desktop | · |  |
| `order` | enum | `descending`, `ascending` | desktop | · |  |
| `orderBy` | text |  | desktop | · |  |
| `postOffset` | text |  | desktop | · |  |
| `postPerPage` | text |  | desktop | · |  |
| `queryType` | text |  | desktop | · |  |
| `subTypes` | json |  | desktop | · |  |

## Meta
<a id="meta"></a>

Group key `meta.meta` · used by 60 module(s) · e.g. `module.meta.meta.forceVisible` (accordion), `module.meta.meta.tocListHeading` (accordion), `pin.meta.meta.forceVisible` (map-pin)

> Schema notes: divi/meta (forceVisible toggle, tocListHeading toggle for table-of-contents)

### `….meta.meta.forceVisible`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | onoff |  | desktop | · |  |

### `….meta.meta.tocListHeading`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | onoff |  | desktop | · |  |

## Overflow
<a id="overflow"></a>

Group key `decoration.overflow` · used by 63 module(s) · e.g. `module.decoration.overflow` (accordion)

> Schema notes: divi/overflow (JS Nb default/visible/scroll/hidden/auto; D4 overflow-x/y)

### `….decoration.overflow`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `x` | enum | `default`, `visible`, `scroll`, `hidden`, `auto` | R | hover, sticky |  |
| `y` | enum | `default`, `visible`, `scroll`, `hidden`, `auto` | R | hover, sticky |  |

## Placeholder font
<a id="font-placeholder"></a>

Group key `decoration.placeholderFont` · used by 4 module(s) · e.g. `field.decoration.placeholderFont.font` (contact-field), `field.decoration.placeholderFont.textShadow` (contact-field), `field.decoration.placeholderFont.textEffects` (contact-field)

> Schema notes: form placeholder font (same divi/font leaves)

### `….decoration.placeholderFont.font`

Same keys as [Body font → `….decoration.bodyFont.body.font`](#font-body).

### `….decoration.placeholderFont.textEffects`

Same keys as [Font → `….decoration.font.textEffects`](#font).

### `….decoration.placeholderFont.textShadow`

Same keys as [Text → `….advanced.text.textShadow`](#text).

## Position
<a id="position"></a>

Group key `decoration.position` · used by 60 module(s) · e.g. `module.decoration.position` (accordion)

> Schema notes: divi/position (JS mode Mb default/relative/absolute/fixed; D4 positioning none/relative/absolute/fixed; origins are corner keywords like "top left" (corpus), D4 top_left)

### `….decoration.position`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `mode` | enum | `default`, `none`, `relative`, `absolute`, `fixed` | R | hover, sticky |  |
| `offset.horizontal` | length |  | R | hover, sticky |  |
| `offset.vertical` | length |  | R | hover, sticky |  |
| `origin.absolute` | text |  | R | hover, sticky |  |
| `origin.fixed` | text |  | R | hover, sticky |  |
| `origin.relative` | text |  | R | hover, sticky |  |

## Scroll
<a id="scroll"></a>

Group key `decoration.scroll` · used by 60 module(s) · e.g. `module.decoration.scroll` (accordion)

> Schema notes: divi/scroll (D4 scroll_* motion fields through convertScroll): each effect value is {enable, viewport {bottom,end,start,top}, offset {start,mid,end}} (AdvancedOptionConversion.php convertScroll); *.enable toggles are declared, the rest of the effect object is open; motionTriggerStart D4 middle/top/bottom

### `….decoration.scroll`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `blur` | object | object (other keys accepted) | R | · | {enable, viewport: {bottom, end, start, top}, offset: {start, mid, end}} (AdvancedOptionConversion::convertScroll); open: keys other than the declared enable are accepted untyped |
| `blur.enable` | onoff |  | R | · |  |
| `fade` | object | object (other keys accepted) | R | · | {enable, viewport: {bottom, end, start, top}, offset: {start, mid, end}} (AdvancedOptionConversion::convertScroll); open: keys other than the declared enable are accepted untyped |
| `fade.enable` | onoff |  | R | · |  |
| `gridMotion.enable` | onoff |  | R | · |  |
| `horizontalMotion` | object | object (other keys accepted) | R | · | {enable, viewport: {bottom, end, start, top}, offset: {start, mid, end}} (AdvancedOptionConversion::convertScroll); open: keys other than the declared enable are accepted untyped |
| `horizontalMotion.enable` | onoff |  | R | · |  |
| `motionTriggerStart` | enum | `middle`, `top`, `bottom` | R | · |  |
| `rotating` | object | object (other keys accepted) | R | · | {enable, viewport: {bottom, end, start, top}, offset: {start, mid, end}} (AdvancedOptionConversion::convertScroll); open: keys other than the declared enable are accepted untyped |
| `rotating.enable` | onoff |  | R | · |  |
| `scaling` | object | object (other keys accepted) | R | · | {enable, viewport: {bottom, end, start, top}, offset: {start, mid, end}} (AdvancedOptionConversion::convertScroll); open: keys other than the declared enable are accepted untyped |
| `scaling.enable` | onoff |  | R | · |  |
| `verticalMotion` | object | object (other keys accepted) | R | · | {enable, viewport: {bottom, end, start, top}, offset: {start, mid, end}} (AdvancedOptionConversion::convertScroll); open: keys other than the declared enable are accepted untyped |
| `verticalMotion.enable` | onoff |  | R | · |  |

## Sizing
<a id="sizing"></a>

Group key `decoration.sizing` · used by 61 module(s) · e.g. `module.decoration.sizing` (accordion), `card.decoration.sizing` (timeline), `item.decoration.sizing` (timeline)

> Schema notes: divi/sizing

### `….decoration.sizing`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `alignSelf` | text |  | R | · |  |
| `alignment` | enum | `left`, `center`, `right` | R | · |  |
| `aspectRatio` | text |  | R | hover, sticky | JS divi/aspect-ratio: a ratio like 16/9 or auto |
| `flexGrow` | number |  | R | hover, sticky |  |
| `flexShrink` | number |  | R | hover, sticky |  |
| `flexType` | text |  | R | · | JS divi/select-column-class, e.g. 24_24, 12_24 |
| `gridAlignSelf` | text |  | desktop | · |  |
| `gridColumnEnd` | text |  | R | hover, sticky |  |
| `gridColumnSpan` | text |  | R | hover, sticky |  |
| `gridColumnStart` | text |  | R | hover, sticky |  |
| `gridJustifySelf` | enum | `start`, `center`, `end`, `stretch`, `baseline` | desktop | · |  |
| `gridRowEnd` | text |  | R | hover, sticky |  |
| `gridRowSpan` | text |  | R | hover, sticky |  |
| `gridRowStart` | text |  | R | hover, sticky |  |
| `height` | length |  | R | hover, sticky |  |
| `iconFontSize` | length |  | R | hover, sticky | blurb BlurbPresetAttrsMap adds imageIcon.decoration.sizing iconFontSize |
| `maxHeight` | length |  | R | hover, sticky |  |
| `maxWidth` | length |  | R | hover, sticky |  |
| `minHeight` | length |  | R | hover, sticky |  |
| `size` | length |  | R | hover, sticky |  |
| `width` | length |  | R | hover, sticky |  |

## Spacing
<a id="spacing"></a>

Group key `decoration.spacing` · used by 62 module(s) · e.g. `module.decoration.spacing` (accordion), `card.decoration.spacing` (timeline), `icon.decoration.spacing` (icon-list)

> Schema notes: divi/spacing

### `….decoration.spacing`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `margin` | spacing |  | R | hover, sticky |  |
| `padding` | spacing |  | R | hover, sticky |  |

## Spam protection
<a id="spam-protection"></a>

Group key `advanced.spamProtection` · used by 2 module(s) · e.g. `module.advanced.spamProtection` (contact-form)

> Schema notes: divi/spam-protection (D4 use_spam_service/spam_provider/recaptcha_min_score)

### `….advanced.spamProtection`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `account` | text |  | desktop | · |  |
| `enabled` | onoff |  | desktop | · |  |
| `minScore` | number |  | desktop | · |  |
| `provider` | text |  | desktop | · |  |
| `secretKey` | text |  | desktop | · |  |
| `siteKey` | text |  | desktop | · |  |
| `useBasicCaptcha` | onoff |  | desktop | · |  |

## Sticky
<a id="sticky"></a>

Group key `decoration.sticky` · used by 57 module(s) · e.g. `module.decoration.sticky` (accordion)

> Schema notes: divi/sticky (JS hover:false sticky:false; limits JS Bh = D4; position JS Fh topBottom, D4 top_bottom)

### `….decoration.sticky`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `limit.bottom` | enum | `none`, `body`, `section`, `row`, `column` | R | · |  |
| `limit.top` | enum | `none`, `body`, `section`, `row`, `column` | R | · |  |
| `offset.bottom` | length |  | R | · |  |
| `offset.surrounding` | onoff |  | R | · |  |
| `offset.top` | length |  | R | · |  |
| `position` | enum | `none`, `top`, `bottom`, `topBottom`, `top_bottom` | R | · |  |
| `transition` | onoff |  | R | · |  |

## Text
<a id="text"></a>

Group key `advanced.text` · used by 48 module(s) · e.g. `module.advanced.text` (accordion), `module.advanced.text.text` (accordion), `module.advanced.text.textShadow` (accordion)

> Schema notes: divi/text: text.color = light/dark text scheme (D4 background_layout), orientation = alignment (D4 text_orientation); textShadow = divi/text-shadow

### `….advanced.text`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `orientation` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |

### `….advanced.text.text`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `color` | enum | `light`, `dark` | R | hover, sticky |  |
| `orientation` | enum | `left`, `center`, `right`, `justify`, `justified` | R | · | JS Zu() left/center/right/justify; D4 text orientation also writes justified |

### `….advanced.text.textShadow`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `blur` | length |  | R | hover, sticky |  |
| `color` | color |  | R | hover, sticky |  |
| `horizontal` | length |  | R | hover, sticky |  |
| `style` | text |  | R | · | none or a Divi preset name (preset1..presetN); D4 presets_shadow/select_box_shadow, corpus none/preset1-6; number of presets not pinned |
| `vertical` | length |  | R | hover, sticky |  |

## Transform
<a id="transform"></a>

Group key `decoration.transform` · used by 63 module(s) · e.g. `module.decoration.transform` (accordion), `children.decoration.transform` (group-carousel), `activeGroups.decoration.transform` (group-carousel)

> Schema notes: divi/transform (D4 transform_* through convertTransform): rotate {x,y,z}, scale/skew/translate {x,y,linked}, origin {x,y}; values are lengths (deg, %, px) - typed object (opaque) per axis group

### `….decoration.transform`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `origin` | object |  | R | hover, sticky |  |
| `rotate` | object |  | R | hover, sticky |  |
| `scale` | object |  | R | hover, sticky |  |
| `skew` | object |  | R | hover, sticky |  |
| `translate` | object |  | R | hover, sticky |  |

## Transition
<a id="transition"></a>

Group key `decoration.transition` · used by 63 module(s) · e.g. `module.decoration.transition` (accordion)

> Schema notes: divi/transition (JS hover:false sticky:false; ms lengths; D4 hover_transition_*)

### `….decoration.transition`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| `delay` | length |  | R | · |  |
| `duration` | length |  | R | · |  |
| `speedCurve` | enum | `ease-in-out`, `ease`, `ease-in`, `ease-out`, `linear`, `easeInOut`, `easeIn`, `easeOut` | R | · | animation uses CSS names (JS Aa, D4); the transition group's JS options (Bv) are camelCase; both accepted |

## Z-index
<a id="z-index"></a>

Group key `decoration.zIndex` · used by 63 module(s) · e.g. `module.decoration.zIndex` (accordion)

> Schema notes: D4 z_index range: an integer (string)

### `….decoration.zIndex`

| key | type | values | R | states | notes |
|---|---|---|---|---|---|
| — | number |  | R | hover, sticky |  |
<!-- END GENERATED -->
