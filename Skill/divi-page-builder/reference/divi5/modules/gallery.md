# Gallery — divi/gallery

Grid or slider of images displayed in a clickable thumbnail layout.

- **Block:** `divi/gallery` (Divi 4: `et_pb_gallery`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** none
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h3`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `galleryItem` (Gallery Item), `galleryItemCaption` (Gallery Item Caption), `galleryItemTitle` (Gallery Item Title), `galleryPagination` (Gallery Pagination), `galleryPaginationActive` (Pagination Active Page), `mainElement`, `overlay` (Overlay), `overlayIcon` (Overlay Icon)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/gallery {"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/gallery` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "builderVersion": "5.13.1"
}
```

**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written `"title":{"innerContent":{"desktop":{"value":{"text":"…"}}}}`. **R** = responsive (a value per breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides `value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); the full value model: [value-formats.md](../value-formats.md).

## Content

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `overlay.innerContent` | `icon` | icon |  | R | sticky | D4 `hover_icon` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `caption.decoration.font` | [Font](../design-families.md#font) |
| `caption.decoration.font.font` | [Font](../design-families.md#font) |
| `caption.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `caption.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `galleryGrid.decoration.layout` | [Layout](../design-families.md#layout) |
| `image.decoration.border` | [Border](../design-families.md#border) |
| `image.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `image.decoration.filters` | [Filters](../design-families.md#filters) |
| `image.decoration.fit` | [Fit](../design-families.md#fit) |
| `image.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `item.decoration.border` | [Border](../design-families.md#border) |
| `module.decoration.animation` | [Animation](../design-families.md#animation) |
| `module.decoration.attributes` | [Attributes](../design-families.md#attributes) |
| `module.decoration.background` | [Background](../design-families.md#background) |
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
| `pagination.decoration.font` | [Font](../design-families.md#font) |
| `pagination.decoration.font.font` | [Font](../design-families.md#font) |
| `pagination.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `pagination.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `title.decoration.font` | [Font](../design-families.md#font) |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `galleryGrid.advanced.flexType` | — | text |  | R | hover, sticky |  |
| `image.advanced.galleryCaptions` | — | text |  | desktop | · | D4 `gallery_captions` |
| `image.advanced.galleryIds` | — | text |  | desktop | · | D4 `gallery_ids` |
| `image.advanced.galleryOrderby` | — | enum | `default`, `rand` | desktop | · | D4 `gallery_orderby` |
| `image.advanced.orientation` | — | enum | `landscape`, `portrait` | desktop | · | D4 `orientation` |
| `module.advanced.auto` | — | onoff |  | desktop | · | D4 `auto` |
| `module.advanced.autoSpeed` | — | text |  | desktop | · | D4 `auto_speed` |
| `module.advanced.fullwidth` | — | enum | `off`, `on` | desktop | · | D4 `fullwidth` |
| `module.advanced.postsNumber` | — | text |  | desktop | · | D4 `posts_number` |
| `module.advanced.showTitleAndCaption` | — | onoff |  | R | hover | D4 `show_title_and_caption` |
| `overlay.advanced.hoverOverlayColor` | — | color |  | R | sticky | D4 `hover_overlay_color` |
| `overlay.advanced.zoomIconColor` | — | color |  | R | sticky | D4 `zoom_icon_color` |
| `pagination.advanced.showPagination` | — | onoff |  | R | hover | D4 `show_pagination` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.elements.structure` | [Elements](../design-families.md#elements) |
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.link` | [Link](../design-families.md#link) |
| `module.advanced.text` | [Text](../design-families.md#text) |
| `module.advanced.text.text` | [Text](../design-families.md#text) |
| `module.advanced.text.textShadow` | [Text](../design-families.md#text) |

## Meta and block-level attributes

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `adminLabel` | — | text |  | desktop | · |  |
| `content` | — | html |  | R | hover, sticky | D4 `content` |
| `css` | `after` | text |  | R | hover, sticky | D4 `custom_css_after` |
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `galleryItem` | text |  | R | hover, sticky | D4 `custom_css_gallery_item` |
| `css` | `galleryItemCaption` | text |  | R | hover, sticky | D4 `custom_css_gallery_item_caption` |
| `css` | `galleryItemTitle` | text |  | R | hover, sticky | D4 `custom_css_gallery_item_title` |
| `css` | `galleryPagination` | text |  | R | hover, sticky | D4 `custom_css_gallery_pagination` |
| `css` | `galleryPaginationActive` | text |  | R | hover, sticky | D4 `custom_css_gallery_pagination_active` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `overlay` | text |  | R | hover, sticky | D4 `custom_css_overlay` |
| `css` | `overlayIcon` | text |  | R | hover, sticky | D4 `custom_css_overlay_icon` |
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
<summary>Render defaults (11): what Divi uses when an attribute is unset — don't repeat these</summary>

- `galleryGrid.decoration.layout` — desktop `{"display":"grid","gridColumnCount":"4"}`
- `image.advanced.galleryOrderby` — desktop `"default"`
- `image.advanced.orientation` — desktop `"landscape"`
- `module.advanced.autoSpeed` — desktop `"7000"`
- `module.advanced.fullwidth` — desktop `"off"`
- `module.advanced.postsNumber` — desktop `"4"`
- `module.advanced.showTitleAndCaption` — desktop `"on"`
- `module.advanced.text.text` — desktop `{"color":"light"}`
- `module.meta.adminLabel` — desktop `"Gallery"`
- `pagination.advanced.showPagination` — desktop `"on"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h3"}`

</details>
