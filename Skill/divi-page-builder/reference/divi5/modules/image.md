# Image — divi/image

Single picture with optional caption, link, and lightbox overlay.

- **Block:** `divi/image` (Divi 4: `et_pb_image`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `image` (Image), `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://example.com/wp-content/uploads/2026/09/team.jpg","alt":"Our team on a job site"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/image` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "image": {
    "innerContent": {
      "desktop": {
        "value": {
          "src": "https://example.com/wp-content/uploads/2026/09/team.jpg",
          "alt": "Our team on a job site"
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
| `image.innerContent` | `alt` | text |  | desktop | · | D4 `alt` |
| `image.innerContent` | `linkTarget` | enum | `off`, `on` | desktop | · | D4 `url_new_window` |
| `image.innerContent` | `linkUrl` | url |  | desktop | · | D4 `url` |
| `image.innerContent` | `rel` | json |  | desktop | · | link rel values (list); options not dumped |
| `image.innerContent` | `src` | image |  | R | hover | D4 `src` |
| `image.innerContent` | `titleText` | text |  | desktop | · | D4 `title_text` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `image.decoration.border` | [Border](../design-families.md#border) |
| `image.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `image.decoration.fit` | [Fit](../design-families.md#fit) |
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
| `module.decoration.conditions` | [Conditions](../design-families.md#conditions) |
| `module.decoration.disabledOn` | [Disabled on](../design-families.md#disabled-on) |
| `module.decoration.filters` | [Filters](../design-families.md#filters) |
| `module.decoration.interactions` | [Interactions](../design-families.md#interactions) |
| `module.decoration.layout` | [Layout](../design-families.md#layout) |
| `module.decoration.overflow` | [Overflow](../design-families.md#overflow) |
| `module.decoration.position` | [Position](../design-families.md#position) |
| `module.decoration.scroll` | [Scroll](../design-families.md#scroll) |
| `module.decoration.sticky` | [Sticky](../design-families.md#sticky) |
| `module.decoration.transform` | [Transform](../design-families.md#transform) |
| `module.decoration.transition` | [Transition](../design-families.md#transition) |
| `module.decoration.zIndex` | [Z-index](../design-families.md#z-index) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `image.advanced.lightbox` | — | onoff |  | desktop | · | D4 `show_in_lightbox` |
| `image.advanced.overlay` | `backgroundColor` | color |  | R | sticky | D4 `hover_overlay_color` |
| `image.advanced.overlay` | `use` | onoff |  | desktop | · | D4 `use_overlay` |
| `image.advanced.overlayIcon` | `hoverIcon` | icon |  | R | sticky | D4 `hover_icon` |
| `image.advanced.overlayIcon` | `iconColor` | color |  | R | sticky | D4 `overlay_icon_color` |
| `module.advanced.align` | — | enum | `left`, `center`, `right` | R | · | D4 `align` |
| `module.advanced.forceFullwidth` | — | onoff |  | R | hover, sticky |  |
| `module.advanced.sizing` | `alignSelf` | text |  | R | · |  |
| `module.advanced.sizing` | `alignment` | enum | `left`, `center`, `right` | R | · | D4 `module_alignment` |
| `module.advanced.sizing` | `aspectRatio` | text |  | R | hover, sticky | JS divi/aspect-ratio: a ratio like 16/9 or auto |
| `module.advanced.sizing` | `flexGrow` | number |  | R | hover, sticky |  |
| `module.advanced.sizing` | `flexShrink` | number |  | R | hover, sticky |  |
| `module.advanced.sizing` | `flexType` | text |  | R | · | JS divi/select-column-class, e.g. 24_24, 12_24 |
| `module.advanced.sizing` | `forceFullwidth` | onoff |  | R | · | D4 `force_fullwidth` |
| `module.advanced.sizing` | `gridAlignSelf` | text |  | desktop | · |  |
| `module.advanced.sizing` | `gridColumnEnd` | text |  | R | hover, sticky |  |
| `module.advanced.sizing` | `gridColumnSpan` | text |  | R | hover, sticky |  |
| `module.advanced.sizing` | `gridColumnStart` | text |  | R | hover, sticky |  |
| `module.advanced.sizing` | `gridJustifySelf` | enum | `start`, `center`, `end`, `stretch`, `baseline` | desktop | · |  |
| `module.advanced.sizing` | `gridRowEnd` | text |  | R | hover, sticky |  |
| `module.advanced.sizing` | `gridRowSpan` | text |  | R | hover, sticky |  |
| `module.advanced.sizing` | `gridRowStart` | text |  | R | hover, sticky |  |
| `module.advanced.sizing` | `height` | length |  | R | hover, sticky | D4 `height` |
| `module.advanced.sizing` | `maxHeight` | length |  | R | hover, sticky | D4 `max_height` |
| `module.advanced.sizing` | `maxWidth` | length |  | R | hover, sticky | D4 `max_width` |
| `module.advanced.sizing` | `minHeight` | length |  | R | hover, sticky | D4 `min_height` |
| `module.advanced.sizing` | `size` | length |  | R | hover, sticky |  |
| `module.advanced.sizing` | `width` | length |  | R | hover, sticky | D4 `width` |
| `module.advanced.spacing` | `margin` | spacing |  | R | hover, sticky | D4 `custom_margin` |
| `module.advanced.spacing` | `padding` | spacing |  | R | hover, sticky | D4 `custom_padding` |
| `module.advanced.spacing` | `showBottomSpace` | onoff |  | R | · | D4 `show_bottom_space` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `content` | — | html |  | R | hover, sticky | D4 `content` |
| `css` | `after` | text |  | R | hover, sticky | D4 `custom_css_after` |
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `image` | text |  | R | hover, sticky | custom CSS declarations for a CSS slot (D4 custom_css_*) |
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
| `module.meta.meta.forceVisible` | [Meta](../design-families.md#meta) |
| `module.meta.meta.tocListHeading` | [Meta](../design-families.md#meta) |

<details>
<summary>Render defaults (6): what Divi uses when an attribute is unset — don't repeat these</summary>

- `image.advanced.lightbox` — desktop `"off"`
- `image.advanced.overlay` — desktop `{"use":"off"}`
- `image.innerContent` — desktop `{"linkTarget":"off"}`
- `module.advanced.forceFullwidth` — desktop `"off"`
- `module.advanced.spacing` — desktop `{"showBottomSpace":"on"}`
- `module.meta.adminLabel` — desktop `"Image"`

</details>
