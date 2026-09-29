# Fullwidth Image — divi/fullwidth-image

Edge-to-edge single image used as a wide visual break in the page flow.

- **Block:** `divi/fullwidth-image` (Divi 4: `et_pb_fullwidth_image`)
- **Category:** fullwidth-module · **scope:** core
- **Goes inside:** `divi/section`
- **Children:** none
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `image` (Image), `mainElement`

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"advanced":{"type":{"desktop":{"value":"fullwidth"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/fullwidth-image {"image":{"innerContent":{"desktop":{"value":{"src":"https://example.com/wp-content/uploads/2026/09/crew.jpg","alt":"Our crew on a job site"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/section -->
```

The `divi/fullwidth-image` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "image": {
    "innerContent": {
      "desktop": {
        "value": {
          "src": "https://example.com/wp-content/uploads/2026/09/crew.jpg",
          "alt": "Our crew on a job site"
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
| `image.innerContent` | `src` | image |  | R | hover | D4 `src` |
| `image.innerContent` | `titleText` | text |  | desktop | · | D4 `title_text` |

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
| `image.advanced.lightbox` | — | onoff |  | desktop | · | D4 `show_in_lightbox` |
| `image.advanced.overlay` | `backgroundColor` | color |  | R | sticky | D4 `hover_overlay_color` |
| `image.advanced.overlay` | `use` | onoff |  | desktop | · | D4 `use_overlay` |
| `image.advanced.overlayIcon` | `hoverIcon` | icon |  | R | sticky | D4 `hover_icon` |
| `image.advanced.overlayIcon` | `iconColor` | color |  | R | sticky | D4 `overlay_icon_color` |
| `module.advanced.spacing` | `showBottomSpace` | onoff |  | R | hover, sticky | D4 `show_bottom_space` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
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
<summary>Render defaults (4): what Divi uses when an attribute is unset — don't repeat these</summary>

- `image.advanced.lightbox` — desktop `"off"`
- `image.advanced.overlay` — desktop `{"use":"off"}`
- `image.innerContent` — desktop `{"linkTarget":"off"}`
- `module.meta.adminLabel` — desktop `"Fullwidth Image"`

</details>
