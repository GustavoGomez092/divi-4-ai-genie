# Number Counter — divi/number-counter

Large animated number that counts up to a target value to emphasize a statistic.

- **Block:** `divi/number-counter` (Divi 4: `et_pb_number_counter`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h3`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`, `numberCounterTitle` (Number Counter Title), `percent` (Percent)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/number-counter {"title":{"innerContent":{"desktop":{"value":"Jobs completed"}}},"number":{"innerContent":{"desktop":{"value":"9500"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/number-counter` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "title": {
    "innerContent": {
      "desktop": {
        "value": "Jobs completed"
      }
    }
  },
  "number": {
    "innerContent": {
      "desktop": {
        "value": "9500"
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
| `number.innerContent` | — | text |  | R | hover | D4 `number` |
| `title.innerContent` | — | text |  | R | hover | D4 `title` |

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
| `number.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `number.decoration.font.font`, not here |
| `number.decoration.font.font` | [Font](../design-families.md#font) |
| `number.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `number.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `number.advanced.enablePercentSign` | — | onoff |  | R | hover | D4 `percent_sign` |

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
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `numberCounterTitle` | text |  | R | hover, sticky | D4 `custom_css_number_counter_title` |
| `css` | `percent` | text |  | R | hover, sticky | D4 `custom_css_percent` |
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

Legacy, from Divi's Divi 4 conversion map only. They appear only in Divi's conversion outlines: no Divi 5 module code reads them. The validator warns `W5_LEGACY_ATTR` on them (a warning, so that converted pages still validate). Don't write them.

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `content` | — | html |  | R | hover, sticky | **legacy (D4 conversion) — don't author**; D4 `content` |

<details>
<summary>Render defaults (6): what Divi uses when an attribute is unset — don't repeat these</summary>

- `module.advanced.text.text` — desktop `{"color":"light","orientation":"center"}`
- `module.meta.adminLabel` — desktop `"Number Counter"`
- `number.advanced.enablePercentSign` — desktop `"on"`
- `number.decoration.font.font` — desktop `{"color":"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-primary-color\",\"settings\":{}}})$"}`
- `number.innerContent` — desktop `"0"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h3"}`

</details>

## Gotchas

- `number.innerContent` is free text, and Divi 5 keeps it verbatim: the count-up animates the number it finds in it, then prints your text unchanged. `"25+"` counts 0 → 25 and ends on `25+`; `"1,200+"` counts with the comma (`1,038`, `1,198`) and ends on `1,200+`; `"98%"` with `enablePercentSign` `"off"` ends on `98%`. So a trailing suffix (`+`, `%`, `★`) is safe; it appears only when the count stops (Divi 5.13.1's `module-library-script-number-counter.js`, checked on a live Divi 5.13.1 page).
- **Don't start with a non-number.** Divi `parseFloat`s the text after removing commas: `"$49"` shows `NaN` for the whole count-up (about 1.8 s) before `$49`. Put a currency sign or other prefix in the title, or use a `divi/text`/`divi/heading` block for that stat.
- Every character after the last `.` counts as a decimal place: `"4.9"` counts `0.0` … `4.9`, but `"4.9★"` counts `0.00` … `4.89` and then jumps to `4.9★`. For a rating, write `"4.9"` and put the star in the title (`"★ from 1,200 reviews"`), or accept the extra digit while it counts.
- Text such as `"24/7"` counts 0 → 24 and then prints `24/7`: a count-up that means nothing. Keep a counter for a real quantity, and put `24/7` in text.
- `number.advanced.enablePercentSign` defaults to `"on"` and adds a `%` after the number: set `"off"` on every counter that isn't a percentage.
