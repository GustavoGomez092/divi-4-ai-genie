# R2: Divi 5 schema source

Spike R2 for Divi 5 support. Question: where can Divi Genie get an authoritative field schema
for Divi 5 modules (attribute paths, leaf types, breakpoints/states, children, placement), the way
`research/divi-schema/` gives it for Divi 4? Site: local Divi **5.13.1** (`divi-5-test.local`). Paths
below are relative to `wp-content/themes/Divi/includes/builder-5/` unless they start with `research/`.

## TL;DR

- **No single file holds the complete registry.** `module.json` (identical to
  `server/_all_modules_metadata.php`, and to the runtime `WP_Block_Type` attributes apart from
  WordPress's 4 core attrs) declares each module's attributes. It spells out module-specific fields
  in full: 814 field items with component, options, units and `features`. Shared **option groups**
  (font, spacing, background, border, button, …) appear only as a reference, e.g.
  `"background": {}` or `{"component":{"type":"group","name":"divi/background"}}`.
- **Divi's PHP expands the groups into leaf paths, but not into leaf types.**
  `Conversion::get_preset_attrs_mapping()` (`server/Packages/Conversion/Conversion.php:2614`) walks
  `module.json` and expands each group through `ModuleOptionsPresetAttrs::get_preset_attrs_from_group()`
  (`server/Packages/Module/Options/ModuleOptionsPresetAttrs.php:79`, 47 `*PresetAttrsMap.php`
  classes). The result lists every leaf as `attrName` + `subName`. It carries no value
  type/options/units: in Divi 5 those live only in the React group components of the JS bundles
  (`visual-builder/build/module.js`).
- **The expander alone is not complete.** It is built for presets, so it leaves out the
  non-preset leaves (`background.enableColor`, `image.enabled`, `gutter.enable/makeEqual`, …),
  the builder-only structural attrs (`column module.advanced.type`,
  `row module.advanced.columnStructure`, `section module.advanced.type`, `accordion-item …open`)
  and the block-level attrs (`locked`, `adminLabel`, …). One module
  (`divi/social-media-follow-network`) filters its map to `[]`. Against Divi's own converter output
  it covers **94.8 %** of values.
- **Chosen source is a runtime PHP dump that joins three Divi-owned sources:** the expander
  (run with and without the module filters), the runtime **D4→D5 conversion map** (17,974 D4-attr →
  D5-path entries across 67 modules), and the block-level attrs from `Conversion::getAttrMap`. With
  option groups widened across modules, this union covers **100 %** of paths in Divi-converted
  content from all 7 `tests/fixtures/valid` files (7,272 values, 529 distinct paths). It covers
  **99.99 %** of the 35-file corpus (9,582/9,583; the one miss is a converter artifact) and 100 % of
  the 12 D5 posts on the local site. It still rejects bogus paths (negative control below).
- **Leaf types need one hand-curated table.** Module-specific leaves are typed from `module.json`.
  About 20 shared option-group families (a few hundred leaves) need a curated family table, like
  Divi 4's `design-families.md`. Seed it from the JS field defs (subName → component, extracted
  below) and from the Divi 4 schema via the conversion map. That table is the only piece that cannot
  be dumped.
- Deliverables: `research/tools/divi5/dump-schema.php` writes `research/divi5-schema/`
  (index.json, groups.json, 116 × modules/<slug>.json). It is deterministic: two runs produce no
  diff. `research/tools/divi5/schema_coverage.py` reproduces the coverage numbers.

## 1. Where the attribute registry lives (Q1)

### 1.1 Static files

| file | what it holds | complete? |
|---|---|---|
| `visual-builder/packages/*/src/**/module.json` (115) | `name`, `d4Shortcode`, `category`, `childrenName`, `customCssFields`, `settings.groups`, and `attributes.<attr>` = `{type, selector, elementType, settings:{innerContent, advanced, decoration, meta}, styleProps}` | Module-specific fields are complete (component + props + features). Option groups are only referenced. |
| `server/_all_modules_metadata.php` | the same data, aggregated (3.1 MB) | Same as `module.json`. Verified: 113/115 are equal after normalising PHP's `[]`/`{}`. `shop`'s `"0".."6"` option keys become a list, and `shortcode-module` is not in the file. |
| `…/conversion-outline.json` + `server/_all_modules_conversion_outline.php` | Divi 4 → Divi 5 map: `module` (D4 attr → D5 path), `advanced` (D4 advanced-field family → D5 group attr), `css` (custom CSS slots), `valueExpansionFunctionMap`, `deprecatedMap` | Compact; the runtime expands it (§5). |
| `…/module-default-render-attributes.json`, `…/module-default-printed-style-attributes.json` | default values (§4) | n/a |
| `visual-builder/build/*.js` | the group definitions (`divi/font` → size, weight, …), written as React components that build field configs inline | The only home of group leaf types/options. Minified code, not data. |

How a field is declared in `module.json` (blurb, `attributes.imageIcon.settings.innerContent.items.useIcon`):

```json
{"attrName":"imageIcon.innerContent","subName":"useIcon","label":"Use Icon",
 "features":{"hover":false,"sticky":false,"responsive":false,"preset":"content"},
 "component":{"type":"field","name":"divi/toggle"}}
```

How an option group is declared:

- `attributes.module.settings.decoration.background: {}` means the default `divi/background`
  group, with the name taken from the key by `ModuleOptionsPresetAttrs::get_the_group_name_by_key()`
  (`ModuleOptionsPresetAttrs.php:189`).
- `…decoration.sizing: {"groupType":"group-item","item":{"component":{"type":"group","name":"divi/sizing"}}}`
  names the group explicitly.
- A group item can override or add fields through `component.props.fields`, for example blurb
  `settings.groups.designImageIcon…iconFontSize`.

`features` defaults to `{responsive:true, hover:true, sticky:true, dynamicContent:false}`; see
`module.js`: `U={responsive:!0,hover:!0,sticky:!0,dynamicContent:!1,...I}`. Across all
`module.json` field items: 814 items, `sticky:false` ×521, `hover:false` ×364,
`responsive:false` ×292, props `options` ×147, `defaultUnit` ×56, `allowedUnits` ×14, `min`/`max`.
Components: toggle 223, color-picker 152, text 129, select 104, range 65, upload 21, icon-picker 18,
richtext 14, …

### 1.2 Runtime PHP

- **Block registry.** Modules are registered lazily. In WP-CLI only `divi/layout` and
  `divi/shortcode-module` are registered by default. All of them are registered when
  `ConditionsUtility::should_register_all_d5_modules()` is true
  (`server/Framework/Utility/Conditions.php:422`: VB, REST request, test env, some AJAX actions).
  The dump sets `REQUEST_URI=/wp-json/` through `--exec`, which registers 87 `divi/*` blocks.
  `WP_Block_Type->attributes` is `module.json` `attributes` plus WordPress's `lock`, `metadata`,
  `className` and `style`, so no expansion happens at registration
  (`ModuleRegistration::register_module`, `server/Packages/ModuleLibrary/ModuleRegistration.php:202`).
  Integration modules are skipped when their plugin is missing, e.g. `GravityFormsModule.php:1588`
  (`class_exists('\GFForms')`), `ContactForm7Module.php:562`, `ImagelyGalleryModule.php:610`,
  `WooCommerce*Module.php` (`et_is_woocommerce_plugin_active()`). No plugins are active on this
  site, so 29 modules show `registered:false`: 25 WooCommerce, contact-form-7, gravity-forms,
  imagely-gallery, plus the internal `global-layout`. Their metadata still comes from the static file
  (`ModuleRegistration::get_module_settings()` falls back to it, `ModuleRegistration.php:1331`).
- **Group expander.** `Conversion::get_preset_attrs_mapping($name)`
  (`Conversion.php:2614-2851`) returns `{"<attrName>__<subName>": {attrName, subName, preset}}`
  with every group expanded, e.g. `title.decoration.font.font__size`,
  `module.decoration.background__image.url`, `module.decoration.spacing__margin`. Modules can
  change it through `divi_conversion_presets_attrs_map` (`Conversion.php:2846`):
  - blurb adds `imageIcon.decoration.sizing__iconFontSize` (`Blurb/BlurbPresetAttrsMap.php`);
  - social-media-follow-network returns `[]` (`SocialMediaFollowItem/SocialMediaFollowItemPresetAttrsMap.php:34-40`).

  The dump therefore runs it twice, with and without the filter, keeps the union, and marks each
  leaf `inPresetMap`.
- **Conversion map.** `apply_filters('divi.conversion.moduleLibrary.conversionMap', [])`, after
  `do_action('divi_visual_builder_before_d4_conversion')` (`ModuleRegistration.php:693-708`), gives
  per module `attributeMap` (D4 attr → D5 path with `*` for `<breakpoint>.<state>`),
  `optionEnableMap`, `valueExpansionFunctionMap`, `nonResponsiveAttributes` and
  `conditionalAttributeConversionFunctionMap`. It holds 17,974 entries across 67 modules. It is the
  only source of the builder-only structural attrs and of non-preset group leaves such as
  `background.enableColor`.
- **Block-level attrs** (`Conversion::getAttrMap`, `Conversion.php:1185-1206`):
  - responsive: `adminLabel.*`, `themeBuilderArea.*`, `globalColorsInfo.*`, `on.*`, `locked.*`, `open.*`;
  - plain: `builderVersion`, `modulePreset`, `globalModule`, `globalParent`, `nonconvertible`,
    `shortcodeName`;
  - `unknownAttributes.<d4name>` for anything unmapped.

  Native D5 content also carries `groupPreset.<groupId>.{presetId,groupName}`.
- **Breakpoints/states:**
  - `Breakpoint::get_default_settings_values()` (`server/Framework/Breakpoint/Breakpoint.php:72`):
    `desktop` (base), `tablet` (≤980px), `phone` (≤767px) are enabled; `phoneWide`, `tabletWide`,
    `widescreen` and `ultraWide` are off by default.
  - `ModuleUtils::states()` (`server/Packages/ModuleUtils/ModuleUtils.php:2464`): `value`, `hover`,
    `focus`, `checked`, `active`, `sticky`.

### 1.3 What the JS bundle adds (not dumped)

Group leaf *types* exist only in `visual-builder/build/module.js`, as object literals inside React
group components, e.g.
`weight:{attrName:\`${e}.font\`, groupName:…, features:{hover:!0,sticky:!0}, …}`.
The options are mostly referenced constants, not literals. A regex over
`subName:"…"` → nearby `component:{name:"divi/…"}` recovers the component for about 216 group
subNames, for example:

- `size` → range; `family` → select-font; `color` → color-picker;
- `textAlign` / `headingLevel` / `flexDirection` → button-options;
- `margin` / `padding` → divi/spacing; `radius` → border-radius;
- `image.url` → upload; `gradient` → common-css-gradient.

Some subNames are unresolved (`weight`, `justifyContent`, `gridTemplateColumns`, …). That is good
enough to seed a hand-written family table, not to generate one. It is also minified vendor
code, so nothing from it goes into the dump.

**Decision:** use the runtime PHP dump (authoritative leaf paths, Divi's own expansion) plus a small
curated `families` table for group leaf types. This mirrors Divi 4, where the dump plus
hand-written `extras.json` fed `build_schema.py`.

## 2. The dump (`research/divi5-schema/`)

```
LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH="$HOME/Local Sites/divi-5-test/app/public" \
  research/tools/wp-local.sh --exec='$_SERVER["REQUEST_URI"]="/wp-json/";' \
  eval-file research/tools/divi5/dump-schema.php "$PWD/research/divi5-schema"
```

- `index.json`: `divi_version` (5.13.1), `breakpoints`, `states`, and per module `name`, `title`,
  `category`, `d4Shortcode`, `childrenName`, `folder`, `registered`, `attr_count`, `leaf_count`,
  `has_conversion_map`.
- `groups.json`: every option group (`divi/font`, `divi/background`, …, 46 in all; font groups in
  5 variants such as `has_heading_level`) → leaf list relative to the group root (`@`), plus
  `settingKeyToGroup` (`decoration.bodyFont` → `divi/font-body`, …).
- `modules/<slug>.json` (116): `module` (metadata without UI noise), `attributes`, `settings`,
  `leaves` (expanded, union, `inPresetMap`), `defaults.render` / `defaults.printedStyle`
  (runtime-merged), `conversion` (runtime map; callables reduced to `Class::method` names),
  `conversionOutline`.

All keys are sorted, there is no timestamp, and two consecutive runs `diff -r` clean. PHP encodes an
empty `{}` as `[]`, so consumers must treat `[]` as "use the default group". Contents are field
metadata only: labels, options, selectors, defaults, maps. There is no JS, CSS or PHP source. The
total is 22 MB, the same order as the Divi 4 dump; `leaves` is 12 MB of that.

## 3. Coverage against Divi's converter (Q2)

Corpus: Divi's own converter (`research/tools/divi5/convert.php` logic, batch-run into a scratch dir)
over the 7 `tests/fixtures/valid/*.txt` files plus the 28 `tests/fixtures/render/*.txt` files. A
second corpus is the 12 `wp:divi/` posts on the local site, some of which were written in D5 format
directly (posts 23, 34, 58-60). Paths are walked as (module, attrName, breakpoint, state, subName):

```
python3 research/tools/divi5/schema_coverage.py research/divi5-schema <files…> [--source preset|union]
```

| corpus | `preset` (expander only) | `union` (proposed model) |
|---|---|---|
| valid (7 files) | 6,897/7,272 values = **94.84 %**; 490/529 distinct = 92.63 % | **7,272/7,272 = 100 %**; 529/529 = 100 % |
| valid + render (35) | 9,085/9,583 = 94.80 %; 1,441/1,487 = 96.91 % | **9,582/9,583 = 99.99 %**; 1,486/1,487 = 99.93 % |
| site posts (12) | 3,852/4,101 = 93.93 % | **4,101/4,101 = 100 %** |

What the expander misses and the union supplies (valid corpus, top items):

- `column module.advanced.type` ×86, `row module.advanced.columnStructure` ×22,
  `section module.advanced.type`, `column(-inner) …specialtyColumns/savedSpecialtyColumnType`:
  structural, conversion map only.
- `…decoration.background .enableColor / .image.enabled / .video.enabledMp4 / .enabledWebm`,
  `row …gutter .enable/.makeEqual`, `slider button.decoration.button .enable`: non-preset group
  leaves.
- `locked` on every module (block-level), `accordion-item module.advanced.open`.
- `column-inner`/`row-inner` `module.decoration.layout .display`: the converter writes it, but those
  modules declare no `layout` group. The union allows it by widening the group across modules.

The single remaining miss: `signup content.desktop.value` holds the raw D4
`[et_pb_signup_custom_field …]` shortcodes. The converter does not turn signup custom fields into
child blocks; this is a converter quirk, not a schema gap.

Negative control (blurb with bogus paths): `title.decoration.font.font .fontSize`,
`module.decoration.bogus`, `module.advanced.showTitle` (another module's field) and
`imageIcon.innerContent .iconz` are all rejected. Valid siblings (`size`, `layout.display`,
`gridColumnCount`, `useIcon`, `src`) pass.

Observed breakpoints and states in converted content: desktop 8,833, tablet 396, phone 353; states
`value` 9,518, `hover` 64 (no sticky/focus in the corpus). The converter stamps
`builderVersion: "5.0.0-public-alpha.18.2"`; native saves stamp `"5.13.1"`.

## 4. Defaults (Q4)

- **`module-default-render-attributes`** holds values the renderer merges *under* the saved attrs
  (`ModuleRegistration::generate_default_attrs`, `ModuleRegistration.php:1135`; merge order
  "defaults → presets → raw attrs"). Examples:
  - heading `title.decoration.font.font.desktop.value.headingLevel = "h1"`;
  - blurb `headingLevel "h4"`, `imageIcon.advanced.placement "top"`, and
    `imageIcon.advanced.color = $variable({"type":"color","value":{"name":"gcid-primary-color"}})$`
    (a global-colour reference);
  - button `button.decoration.button.icon.enable "on"`, `module.advanced.html.elementType "a"`;
  - most modules: `module.meta.adminLabel` = the module title.

  Omitting an attribute means these values apply.
- **`module-default-printed-style-attributes`** holds the baseline style values that Divi's static
  CSS already prints, used to avoid re-emitting them (`Module.php:167`, `$default_printed_style_attrs`
  passed to style renderers). Examples:
  - section `innerSizing maxWidth 1080px` and `layout {alignItems:center, flexDirection:column}`;
  - row `layout {flexDirection:row}`;
  - blurb `contentContainer maxWidth 550px`, `imageIcon.advanced.width {icon:96px, image:100%}`.

  Note that the Divi 5 layout default is **flex**. The converter therefore writes
  `module.decoration.layout.desktop.value.display = "block"` on every converted
  section/row/column/module to keep the Divi 4 look.
- `module.json` attributes carry no inline `default`/`defaultPrintedStyle` in 5.13.1 (0
  occurrences). Some field items carry `defaultAttr` or `props.defaultValue` (×32).

**Use:**

- Docs: show `defaults.render` as the field's default, plus the printed-style defaults as the
  baseline look (for example "flex column unless you set display").
- Validator: optionally *info*-flag values equal to a render default (redundant), and never require
  them.
- Preview renderer: needs both sets, because printed-style defaults are the CSS that exists without
  any attr.

## 5. Parent/child, placement, categories (Q3)

`category` counts: module 84, child-module 13, fullwidth-module 10, structure 7
(section, row, row-inner, column, column-inner, group, global-layout), unsupported 1
(shortcode-module, `d4Shortcode et_pb_unsupported`).

Parent → children comes from `childrenName`:

| parent | children |
|---|---|
| section | row |
| accordion | accordion-item |
| contact-form | contact-field |
| counters | counter |
| fullwidth-map, map | map-pin |
| fullwidth-slider, slider | slide |
| group-carousel | group |
| icon-list | icon-list-item |
| post-filter | post-filter-item |
| pricing-tables | pricing-table |
| social-media-follow | social-media-follow-network |
| tabs | tab |
| timeline | timeline-item |
| video-slider | video-slider-item |

Also:

- `row.childModuleName = divi/column` and `row-inner.childModuleName = divi/column-inner`.
- `row` and `column` have `nestable: true` (Divi 5 allows a row inside a column).
- `signup-custom-field` is a child-module, but the D4 converter leaves it as raw content (§3).

The remaining placement rules (fullwidth/specialty, which modules a column accepts, group) are
enforced in JS (`divi/edit-post` store: `isNestedModule`, `getParentLayoutType`) and are not
dumpable. Edges actually produced by the converter (35-file corpus):

```
ROOT > section                                  (types: regular 55, fullwidth 11, specialty 2)
section            > row > column > <module> > <child-module>
section[fullwidth] > fullwidth-{code,header,image,map,slider,…}      (no row/column)
section[specialty] > column > row-inner > column-inner > <module>    (plus plain columns)
```

The section type is `section module.advanced.type.desktop.value ∈ {"", "fullwidth", "specialty"}`
(D4 `fullwidth`/`specialty` → `module.advanced.type.*`). Column width is
`column module.advanced.type` (`"1_2"`) and row layout is `row module.advanced.columnStructure`
(`"1_2,1_2"`). Neither is declared in `module.json` settings. Native Divi 5 has its own
`module.decoration.sizing.flexType` (`column` render default `"24_24"`). Which of the two
representations the D5 builder writes for new rows is an open question for the authoring-format
spike.

Scope classification for the skill (content modules usable on normal pages):

- **Core content, in scope** (same set as Divi 4 plus Divi 5 natives):
  - modules: accordion, audio, blurb, button, circle-counter, code, contact-form, countdown-timer,
    counters, cta, divider, gallery, heading, icon, image, map, number-counter, pricing-tables,
    signup, slider, social-media-follow, tabs, team-member, testimonial, text, toggle, video,
    video-slider;
  - fullwidth-code, -header, -image, -map, -slider;
  - their children;
  - structure: section, row, column, row-inner, column-inner.
- **Divi 5-only, candidates for later:** before-after-image, charts, dropdown, group,
  group-carousel, icon-list(+item), link, lottie, svg, timeline(+item), tooltip,
  table-of-contents, canvas-portal, payment-button (needs gateway accounts).
- **Third-party integrations, out of scope** (registered only when the plugin is active):
  contact-form-7 (`WPCF7_ContactForm`), gravity-forms (`GFForms`), imagely-gallery (NextGEN).
  instagram-feed is registered but needs a connected Instagram account, so it is out of scope too.
- **WooCommerce, out of scope** (25): `divi/woocommerce-*` (folder `woocommerce/…`) plus
  `divi/shop`.
- **Theme-builder / dynamic, out of scope for page authoring:**
  - post-content, fullwidth-post-content, post-title, fullwidth-post-title, post-nav, comments,
    breadcrumbs;
  - blog, portfolio, filterable-portfolio, fullwidth-portfolio, post-slider, fullwidth-post-slider,
    post-filter(+item): loop/query-driven;
  - menu, fullwidth-menu, sidebar, search, login: site-level;
  - global-layout, layout, shortcode-module: internal.

## 6. Conversion outline / map (Q5)

`conversion-outline.json` (92 modules) has four keys:

- `module`: D4 attr → D5 path, with `*` standing for `<breakpoint>.<state>`, e.g.
  - blurb `title` → `title.innerContent.*.text`, `use_icon` → `imageIcon.innerContent.*.useIcon`;
  - button `button_url` → `button.innerContent.*.linkUrl`.
- `advanced`: D4 advanced-field family → D5 group root, e.g.
  `fonts.header → title.decoration.font`, `fonts.body → content.decoration.bodyFont.body`,
  `borders.default → module.decoration.border`, `margin_padding → module.decoration.spacing`,
  `text_shadow.default → module.advanced.text.textShadow`.
- `css`: `custom_css_<slot>` → `css.*.<slot>`.
- `valueExpansionFunctionMap`: D4 attr → converter for packed values.

At runtime (`ModuleRegistration::process_conversion_outline`, `ModuleRegistration.php:141`, with
`AdvancedOptionConversion::get*ConversionMap`) each family is expanded into concrete D4 names
(`header_font_size` → `title.decoration.font.font.*.size`,
`button_bg_color` → `button.decoration.background.*.color`,
`custom_margin` → `module.decoration.spacing.*.margin`,
`module_class` → `module.advanced.htmlAttributes.*.class`). The expanded map is what the dump stores
under `conversion.attributeMap`.

Breakpoint and state come from D4 suffixes (`Conversion::getAttrMap`, `Conversion.php:983`):

- `_tablet`/`_phone` → breakpoint, only when `<attr>_last_edited` enables responsive
  (`optionEnableMap`);
- `__hover`, `__sticky`, `__focus`, `__checked`, `__active` → state, only when `__hover_enabled` and
  similar allow it.

Packed D4 values go through named expanders: `convertFont` (the `family|weight|…` string → font
object), `convertSpacing` (`a|b|c|d` → `{top,right,bottom,left,sync…}`), `convertBorderRadii`,
`convertGradientStops`, `convertFontIcon`, `convertScroll`, `convertTransform`,
`convertDisabledOnBreakpoint`, and others (31 functions). The runtime map also has `deprecatedMap`
(3 modules) and `nonResponsiveAttributes`.

For porting Divi 4 recipes, the easy route is to run Divi's converter (`convert.php`) on the recipe
shortcode, not to re-implement the map. The map is still useful for docs: it gives a "Divi 4 name"
column per Divi 5 leaf, and it lets Divi 4 types, options and units carry over to converted leaves.

## 7. Proposed validator schema shape

A build step (`build_schema5.py`, stdlib, analogous to `build_schema.py`) compiles the raw dump plus
a curated `families5.json` into `scripts/schema5/<slug>.json`:

```jsonc
{
  "name": "divi/blurb", "d4": "et_pb_blurb", "category": "module",      // module|child-module|fullwidth-module|structure
  "scope": "core",                                                     // core|d5-extra|integration|woocommerce|theme-builder|internal
  "children": null,                                                    // childrenName, or null = none
  "parents": ["divi/column", "divi/column-inner", "divi/group"],       // inverse + structure rules
  "attrs": {                                                           // keyed by attrName (dotted), value = leaf spec or group ref
    "imageIcon.innerContent": {"value": "object", "sub": {
        "useIcon": {"type": "onoff", "bp": false, "states": ["value"]},
        "icon":    {"type": "icon", "states": ["value","hover"]},       // {unicode,type,weight}
        "src":     {"type": "image", "dynamic": "image"}}},              // syncs id/alt/titleText
    "imageIcon.advanced.placement": {"type": "enum", "options": ["top","left"], "hover": false, "sticky": false},
    "title.decoration.font":   {"family": "font", "variant": "has_heading_level"},
    "module.decoration.background": {"family": "background"},
    "module.advanced.type": {"type": "enum", "from_d4": "et_pb_column.type"}   // structural, conversion-only
  },
  "css": ["mainElement","before","after","freeForm","blurbImage","blurbTitle","blurbContent"],
  "defaults": { "title.decoration.font.font": {"desktop": {"value": {"headingLevel": "h4"}}} }
}
```

Plus a shared `families5.json`: `font`, `font-body` (body/link/ul/ol/quote sub-fonts),
`font-header` (h1–h6), `text-shadow`, `text-effects`, `background` (color, gradient{stops…},
image{…}, video{…}, pattern{…}, mask{…}, enable* flags), `border` (radius, styles.{all,top,…}.{width,style,color}),
`box-shadow`, `spacing` (margin/padding objects), `sizing`, `layout` (flex/grid, 25 leaves), `position`,
`z-index`, `overflow`, `filters`, `transform`, `transition`, `animation`, `scroll`, `sticky`,
`button` (whole button family: font/background/border/boxShadow/spacing/icon), `icon`, `fit`, `image`,
`form-field` (focus/placeholder sub-families), `id-classes`, `link`, `html`, `text`, `conditions`,
`disabled-on`, `gutter`, `dividers`, `admin-label`/`meta`.

Each family lists relative attrName → subName → `{type, options, units, bp, states}`. The leaf lists
are generated from `groups.json` plus the conversion targets; the types are hand-curated, seeded
from the JS subName→component list and from Divi 4 field types via the conversion map.

Leaf types are few:

| type | value shape |
|---|---|
| `text` | string |
| `html` | escaped HTML in `innerContent` |
| `color` | hex, rgba, or `$variable({"type":"color",…})$` |
| `length` | number + unit, or `auto` / `calc()` / `$variable(content)` |
| `number` | number |
| `enum` | one of `options` |
| `onoff` | `"on"` / `"off"` |
| `url` | URL string |
| `image` | URL, with `id` / `alt` / `titleText` siblings |
| `icon` | `{unicode, type, weight}` |
| `spacing` | `{top, right, bottom, left, syncVertical, syncHorizontal}` |
| `radius` | `{topLeft, …, sync}` |
| `gradient` | `{type, direction, stops: [{position, color}], …}` |
| `object` | opaque |

Validator checks that map onto this shape (Divi 5 counterparts of spec §4.9):

| check | level |
|---|---|
| Unknown block name; bad JSON; unbalanced `<!-- wp: -->` / `<!-- /wp: -->` | error |
| Parent/child in both directions (`children`/`parents`); section type rules (regular: row only; fullwidth: fullwidth-module only; specialty: columns + one column with row-inner) | error |
| Unknown attrName, or unknown subName under a known attrName (the union model of §3; `[]`-declared groups resolve through the family) | error |
| Breakpoint key not in `{desktop, tablet, phone}` (others: warning unless the site enables them); state not allowed by the leaf's `features` (`hover:false`, …) or `focus/checked/active` outside form fields | error |
| Value type / `options` / units, from module.json props or the family table | error |
| No `desktop` value when tablet/phone are set; `hover` value without desktop value | warning |
| `modulePreset` / `groupPreset` ids not `default` and not known on the site; `$variable(...)` ids not in the tokens | warning |
| Value equal to render default | info |

## 8. Implications for the skill

1. **Schema source:** re-run `dump-schema.php` per Divi release (fast, deterministic). Commit
   `research/divi5-schema/` like the Divi 4 dump, and compile it with a new build step. Do not
   parse the JS bundles at build time.
2. **One hand-maintained artifact:** `families5.json` (group leaf types/options/units, about 20
   families). It replaces the generated option details that Divi 4's `get_module_fields()` gave for
   free. Budget real time for it. It is the Divi 5 counterpart of `design-families.md` and should
   be generated into that doc. A coverage gate should fail the build if any leaf in the dump has no
   type.
3. **Path allow-list = union model:** expander leaves (with and without filters), plus conversion
   targets, plus block-level attrs, plus groups widened by `decoration.*`/`meta.*`/group `advanced.*`
   key. That model reached 100 % on Divi-converted and on-site content while rejecting bogus paths.
   Module-specific `advanced.*` fields must not be widened across modules.
4. **Structure docs stay hand-written** (placement is JS-side). Encode:
   - `section.module.advanced.type` (regular/fullwidth/specialty);
   - `row.module.advanced.columnStructure` plus `column.module.advanced.type`;
   - `specialtyColumns`;
   - `childrenName`;
   - Divi 5 nesting (row in column, `group`) as a later extension.

   Decide in the authoring spike whether to emit the D4-compatible `advanced.type` column widths or
   native `sizing.flexType`.
5. **Emit `layout.display: "block"`** (or document flex defaults) on structure elements when
   porting Divi 4 recipes. Divi 5's default layout is flex (printed-style defaults), and the
   converter adds `display:block` everywhere to keep Divi 4 rendering.
6. **Port recipes by converting them.** Feed the Divi 4 recipe shortcodes through Divi's converter
   (`convert.php`) and then clean up by hand: drop `builderVersion: 5.0.0-public-alpha…`, `locked`
   and redundant render-default values, and fix signup custom fields. This beats re-implementing the
   17,974-entry map.
7. **Module scope:**
   - in: the 28 core content modules + 5 fullwidth + children + structure;
   - out: WooCommerce (25), third-party integrations (4), theme-builder/loop/site modules and
     internal blocks;
   - candidates: Divi 5 extras (icon-list, group, lottie, svg, …).

   `registered:false` in the dump means "plugin missing on the dump site", not "unsupported".
8. **Global colours/variables:** render defaults already use
   `$variable({"type":"color","value":{"name":"gcid-…"}})$`. The value-format checks and the token
   extractor must accept and resolve this syntax (it replaces Divi 4's `global_colors_info` +
   `gcid-` bookkeeping).

## Files

- `research/tools/divi5/dump-schema.php`: runtime dump (writes `research/divi5-schema/`).
- `research/divi5-schema/`: `index.json`, `groups.json`, `modules/*.json` (116).
- `research/tools/divi5/schema_coverage.py`: coverage checker / prototype of the union path model
  (stdlib).
