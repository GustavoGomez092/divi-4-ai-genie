# Fullwidth Slider — divi/fullwidth-slider

Edge-to-edge rotating banner of slides combining headlines, buttons, and background media.

- **Block:** `divi/fullwidth-slider` (Divi 4: `et_pb_fullwidth_slider`)
- **Category:** fullwidth-module · **scope:** core
- **Goes inside:** `divi/section`
- **Children:** `divi/slide`
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h2`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `freeForm`, `mainElement`, `slideActiveController` (Slide Active Controller), `slideArrows` (Slide Arrows), `slideButton` (Slide Button), `slideControllers` (Slide Controllers), `slideDescription` (Slide Description), `slideImage` (Slide Image), `slideTitle` (Slide Title)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"advanced":{"type":{"desktop":{"value":"fullwidth"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/fullwidth-slider {"builderVersion":"5.13.1"} --><!-- wp:divi/slide {"title":{"innerContent":{"desktop":{"value":"Spring tune-up"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eBook before May 1.\u003c/p\u003e"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Book now","linkUrl":"/contact/"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/fullwidth-slider --><!-- /wp:divi/section -->
```

The `divi/fullwidth-slider` block's attributes, formatted for reading only (write them escaped and on one line, as above):

```json
{
  "builderVersion": "5.13.1"
}
```

**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written `"title":{"innerContent":{"desktop":{"value":{"text":"…"}}}}`. **R** = responsive (a value per breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides `value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); the full value model: [value-formats.md](../value-formats.md).

## Content

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `button.innerContent` | `linkTarget` | enum | `on`, `off` | desktop | · | D4 `url_new_window` |
| `button.innerContent` | `linkUrl` | url |  | desktop | · | D4 `button_url` |
| `button.innerContent` | `text` | text |  | R | hover, sticky | D4 `button_text` |
| `children.button.innerContent` | `rel` | json |  | desktop | · | D4 `button_rel` |

## Design

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `button.decoration.background` | [Background](../design-families.md#background) |
| `button.decoration.border` | [Border](../design-families.md#border) |
| `button.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
| `button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.background` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.border` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.boxShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.button` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.font` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textEffects` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.font.textShadow` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.sizing` | [Button](../design-families.md#button) |
| `button.decoration.button.decoration.spacing` | [Button](../design-families.md#button) |
| `button.decoration.button.innerContent` | [Button](../design-families.md#button) |
| `button.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `button.decoration.font.font`, not here |
| `button.decoration.font.font` | [Font](../design-families.md#font) |
| `button.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `button.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `button.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `button.decoration.spacing` | [Spacing](../design-families.md#spacing) |
| `children.button.decoration.button` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.background` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.border` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.boxShadow` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.button` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.font.font` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.font.textEffects` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.font.textShadow` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.sizing` | [Button](../design-families.md#button) |
| `children.button.decoration.button.decoration.spacing` | [Button](../design-families.md#button) |
| `children.button.decoration.button.innerContent` | [Button](../design-families.md#button) |
| `children.contentOverlay.decoration.background` | [Background](../design-families.md#background) |
| `children.contentOverlay.decoration.border` | [Border](../design-families.md#border) |
| `children.decoration.background` | [Background](../design-families.md#background) |
| `children.decoration.border` | [Border](../design-families.md#border) |
| `children.module.decoration.background` | [Background](../design-families.md#background) |
| `children.slideOverlay.decoration.background` | [Background](../design-families.md#background) |
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
| `content.decoration.sizing` | [Sizing](../design-families.md#sizing) |
| `dotNav.decoration.background` | [Background](../design-families.md#background) |
| `image.decoration.border` | [Border](../design-families.md#border) |
| `image.decoration.boxShadow` | [Box shadow](../design-families.md#box-shadow) |
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
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `arrows.advanced.color` | — | color |  | R | hover, sticky | D4 `arrows_custom_color` |
| `arrows.advanced.show` | — | onoff |  | R | hover | D4 `show_arrows` |
| `children.advanced.button` | — | object |  | R | hover, sticky | parent-level defaults for child elements; shape not dumped |
| `children.advanced.content` | — | object |  | R | hover, sticky | parent-level defaults for child elements; shape not dumped |
| `children.advanced.contentOverlay` | — | object |  | R | hover, sticky | parent-level defaults for child elements; shape not dumped |
| `children.advanced.slideOverlay` | — | object |  | R | hover, sticky | parent-level defaults for child elements; shape not dumped |
| `children.button.advanced.showOnMobile` | — | onoff |  | desktop | · | D4 `show_cta_on_mobile` |
| `children.content.advanced.showOnMobile` | — | onoff |  | desktop | · | D4 `show_content_on_mobile` |
| `children.contentOverlay.advanced.use` | — | onoff |  | desktop | · | D4 `use_text_overlay` |
| `children.slideOverlay.advanced.use` | — | onoff |  | desktop | · | D4 `use_bg_overlay` |
| `image.advanced.showOnMobile` | — | onoff |  | desktop | · | D4 `show_image_video_mobile` |
| `module.advanced.auto` | — | onoff |  | desktop | · | D4 `auto` |
| `module.advanced.autoIgnoreHover` | — | onoff |  | desktop | · | D4 `auto_ignore_hover` |
| `module.advanced.autoSpeed` | — | text |  | desktop | · | D4 `auto_speed` |
| `pagination.advanced.show` | — | onoff |  | R | hover | D4 `show_pagination` |

Shared families (in the linked family, the table whose heading ends like the attribute lists its keys):

| attribute | family |
|---|---|
| `module.advanced.html` | [Html](../design-families.md#html) |
| `module.advanced.htmlAttributes` | [CSS ID & classes](../design-families.md#id-classes) |
| `module.advanced.link` | [Link](../design-families.md#link) |
| `module.advanced.loop` | [Loop](../design-families.md#loop) |
| `module.advanced.text` | [Text](../design-families.md#text) |
| `module.advanced.text.text` | [Text](../design-families.md#text) — **renders nothing on Divi 5.13.1** — its `orientation` (each slide's default wins): set `orientation` on each `divi/slide` |
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
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `slideActiveController` | text |  | R | hover, sticky | D4 `custom_css_slide_active_controller` |
| `css` | `slideArrows` | text |  | R | hover, sticky | D4 `custom_css_slide_arrows` |
| `css` | `slideButton` | text |  | R | hover, sticky | D4 `custom_css_slide_button` |
| `css` | `slideControllers` | text |  | R | hover, sticky | D4 `custom_css_slide_controllers` |
| `css` | `slideDescription` | text |  | R | hover, sticky | D4 `custom_css_slide_description` |
| `css` | `slideImage` | text |  | R | hover, sticky | D4 `custom_css_slide_image` |
| `css` | `slideTitle` | text |  | R | hover, sticky | D4 `custom_css_slide_title` |
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

- `arrows.advanced.show` — desktop `"on"`
- `button.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `children.button.advanced.showOnMobile` — desktop `"on"`
- `children.content.advanced.showOnMobile` — desktop `"on"`
- `module.advanced.autoSpeed` — desktop `"7000"`
- `module.meta.adminLabel` — desktop `"Fullwidth Slider"`
- `pagination.advanced.show` — desktop `"on"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h2"}`

</details>
