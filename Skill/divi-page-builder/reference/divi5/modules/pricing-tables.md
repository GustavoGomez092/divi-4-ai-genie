# Pricing Tables — divi/pricing-tables

Side-by-side pricing plans with features, prices, and call-to-action buttons.

- **Block:** `divi/pricing-tables` (Divi 4: `et_pb_pricing_tables`)
- **Category:** module · **scope:** core
- **Goes inside:** `divi/column`, `divi/column-inner`, `divi/group`
- **Children:** `divi/pricing-table`
- **Headings:** `title.decoration.font.font` → `headingLevel` defaults to `h2`.
- **CSS slots** (keys of the `css` attribute's value): `after`, `before`, `currency` (Currency), `featuredTable` (Featured Table), `freeForm`, `frequency` (Frequency), `mainElement`, `price` (Price), `pricingButton` (Pricing Button), `pricingContent` (Pricing Content), `pricingHeading` (Pricing Heading), `pricingItem` (Pricing Item), `pricingItemExcluded` (Excluded Item), `pricingSubtitle` (Pricing Subtitle), `pricingTitle` (Pricing Title), `pricingTop` (Pricing Top)

## Minimal valid example

A complete section, in canonical block markup (validated when this page was generated):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/pricing-tables {"builderVersion":"5.13.1"} --><!-- wp:divi/pricing-table {"title":{"innerContent":{"desktop":{"value":"Basic"}}},"price":{"innerContent":{"desktop":{"value":"99"}}},"currencyFrequency":{"innerContent":{"desktop":{"value":{"currency":"$","per":"mo"}}}},"content":{"innerContent":{"desktop":{"value":"+Design consult\n+Permit handling\n-3D renderings"}}},"button":{"innerContent":{"desktop":{"value":{"text":"Choose","linkUrl":"/contact/"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/pricing-tables --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The `divi/pricing-tables` block's attributes, formatted for reading only (write them escaped and on one line, as above):

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
| `currencyFrequency.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `currencyFrequency.decoration.font.font`, not here |
| `currencyFrequency.decoration.font.font` | [Font](../design-families.md#font) |
| `currencyFrequency.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `currencyFrequency.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `excluded.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `excluded.decoration.font.font`, not here |
| `excluded.decoration.font.font` | [Font](../design-families.md#font) |
| `excluded.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `excluded.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `featuredContent.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `featuredContent.decoration.font.font`, not here |
| `featuredContent.decoration.font.font` | [Font](../design-families.md#font) |
| `featuredContent.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `featuredContent.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `featuredCurrencyFrequency.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `featuredCurrencyFrequency.decoration.font.font`, not here |
| `featuredCurrencyFrequency.decoration.font.font` | [Font](../design-families.md#font) |
| `featuredCurrencyFrequency.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `featuredCurrencyFrequency.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `featuredExcluded.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `featuredExcluded.decoration.font.font`, not here |
| `featuredExcluded.decoration.font.font` | [Font](../design-families.md#font) |
| `featuredExcluded.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `featuredExcluded.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `featuredPrice.decoration.background` | [Background](../design-families.md#background) |
| `featuredPrice.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `featuredPrice.decoration.font.font`, not here |
| `featuredPrice.decoration.font.font` | [Font](../design-families.md#font) |
| `featuredPrice.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `featuredPrice.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `featuredSubtitle.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `featuredSubtitle.decoration.font.font`, not here |
| `featuredSubtitle.decoration.font.font` | [Font](../design-families.md#font) |
| `featuredSubtitle.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `featuredSubtitle.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `featuredTable.decoration.background` | [Background](../design-families.md#background) |
| `featuredTitle.decoration.background` | [Background](../design-families.md#background) |
| `featuredTitle.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `featuredTitle.decoration.font.font`, not here |
| `featuredTitle.decoration.font.font` | [Font](../design-families.md#font) |
| `featuredTitle.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `featuredTitle.decoration.font.textShadow` | [Font](../design-families.md#font) |
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
| `price.decoration.background` | [Background](../design-families.md#background) |
| `price.decoration.border` | [Border](../design-families.md#border) |
| `price.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `price.decoration.font.font`, not here |
| `price.decoration.font.font` | [Font](../design-families.md#font) |
| `price.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `price.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `subtitle.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `subtitle.decoration.font.font`, not here |
| `subtitle.decoration.font.font` | [Font](../design-families.md#font) |
| `subtitle.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `subtitle.decoration.font.textShadow` | [Font](../design-families.md#font) |
| `title.decoration.background` | [Background](../design-families.md#background) |
| `title.decoration.font` | [Font](../design-families.md#font) — container only: write keys under `title.decoration.font.font`, not here |
| `title.decoration.font.font` | [Font](../design-families.md#font) |
| `title.decoration.font.textEffects` | [Font](../design-families.md#font) |
| `title.decoration.font.textShadow` | [Font](../design-families.md#font) |

## Advanced

Module-specific:

| attribute | key | type | values | R | states | notes |
|---|---|---|---|---|---|---|
| `content.advanced.bulletColor` | — | color |  | R | hover, sticky | D4 `bullet_color` |
| `content.advanced.showBullet` | — | onoff |  | R | hover | D4 `show_bullet` |
| `featuredContent.advanced.bulletColor` | — | color |  | R | hover, sticky | D4 `featured_table_bullet_color` |
| `featuredTable.advanced.showDropShadow` | — | onoff |  | R | · | D4 `show_featured_drop_shadow` |

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
| `content` | — | html |  | R | hover, sticky | D4 `content` |
| `css` | `after` | text |  | R | hover, sticky | D4 `custom_css_after` |
| `css` | `before` | text |  | R | hover, sticky | D4 `custom_css_before` |
| `css` | `currency` | text |  | R | hover, sticky | D4 `custom_css_currency` |
| `css` | `featuredTable` | text |  | R | hover, sticky | D4 `custom_css_featured_table` |
| `css` | `freeForm` | text |  | R | hover, sticky | D4 `custom_css_free_form` |
| `css` | `frequency` | text |  | R | hover, sticky | D4 `custom_css_frequency` |
| `css` | `mainElement` | text |  | R | hover, sticky | D4 `custom_css_main_element` |
| `css` | `price` | text |  | R | hover, sticky | D4 `custom_css_price` |
| `css` | `pricingButton` | text |  | R | hover, sticky | D4 `custom_css_pricing_button` |
| `css` | `pricingContent` | text |  | R | hover, sticky | D4 `custom_css_pricing_content` |
| `css` | `pricingHeading` | text |  | R | hover, sticky | D4 `custom_css_pricing_heading` |
| `css` | `pricingItem` | text |  | R | hover, sticky | D4 `custom_css_pricing_item` |
| `css` | `pricingItemExcluded` | text |  | R | hover, sticky | D4 `custom_css_pricing_item_excluded` |
| `css` | `pricingSubtitle` | text |  | R | hover, sticky | D4 `custom_css_pricing_subtitle` |
| `css` | `pricingTitle` | text |  | R | hover, sticky | D4 `custom_css_pricing_title` |
| `css` | `pricingTop` | text |  | R | hover, sticky | D4 `custom_css_pricing_top` |
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
<summary>Render defaults (5): what Divi uses when an attribute is unset — don't repeat these</summary>

- `button.decoration.button` — desktop `{"icon":{"enable":"on"}}`
- `content.advanced.showBullet` — desktop `"on"`
- `featuredTable.advanced.showDropShadow` — desktop `"on"`
- `module.meta.adminLabel` — desktop `"Pricing Tables"`
- `title.decoration.font.font` — desktop `{"headingLevel":"h2"}`

</details>
