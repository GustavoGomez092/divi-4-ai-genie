# Divi 5: design tokens (R6) and D4/D5 detection + legacy content (R7)

Research spikes R6 and R7 for Divi 5 support in Divi Genie. Test bed: Divi **5.13.1** on
`divi-5-test.local` (LocalWP, WordPress 7.1.2), compared with Divi **4.27.9** on `divi-test.local`.
Divi 5 server code lives under `wp-content/themes/Divi/includes/builder-5/server/`, abbreviated **`B5/`** below.

Helper scripts (research only, stdlib/WP-CLI):

- `research/tools/divi5/r6_setup.php BACKUP.json`: seeds global colors, design variables, a module preset
  and an option-group preset, plus the page `R6 tokens trace` that uses them. It backs up every option it touches first.
- `research/tools/divi5/r6_restore.php BACKUP.json`: restores those options and deletes every `R6 …` page.
- `research/tools/divi5/d5_tokens_probe.py`: shows what an outsider can recover. It reads public HTML
  (`:root` variables and preset CSS rules), optionally `content.raw` over REST (preset ids and `$variable()$`
  references), and optionally probes Divi's `divi/v1` endpoints with an Application Password (`--probe-rest`).
- `research/tools/divi5/detect_divi.py`: tells Divi 4 from Divi 5 (with the version) from outside (R7, §5).

## 0. TL;DR (R7: detection and legacy content)

- **Exact version from outside (no auth):**
  - `GET /wp-content/themes/Divi/style.css` returns a `Version:` header (5.13.1 / 4.27.9).
  - The most common `?ver=` on `/themes/Divi/` assets gives the same answer.
  - The generator meta `Divi v.X` names the *active* theme, so a child theme hides it.
  - With an Application Password, `/wp/v2/themes?status=active` gives the version (needs `edit_posts`).
- **Major version from markers:**
  - D5 only: `/includes/builder-5/` asset paths, `<style class="et-vb-global-data …">`, `et_block_section`/`et_block_module` classes, `var diviBreakpointData`.
  - D5 registers 164 `divi/v1` routes (`global-data/*`, `content-conversion`, …); D4 registers only two (`get_layout_content`, `block/layout/builder_edit_data`).
  - Body classes and headers are identical on D4 and D5.
- **Per page, from `content.raw`:**
  - `[et_pb_…]` means D4 shortcode, `<!-- wp:divi/… -->` means D5 blocks.
  - Both kinds of page coexist on upgraded sites.
  - The block `builderVersion` value is **not** the site version.
- **D4 shortcode pushed to a D5 site** is *not* converted. It renders through the bundled D4 legacy path (`et_d4_element`), and fidelity is degraded: the deferred dynamic CSS was missing, columns collapsed and icons were lost. It is converted only when opened in the D5 VB and saved. **The skill must never write D4 shortcode to a D5 site.**
- **Upgrading D4 → D5 does not convert `post_content`.** The manual "Divi 5 Migrator" (`et_d5_readiness`) batch-converts pages:
  - it wraps the result in `wp:divi/placeholder`;
  - it backs up the original to `_et_pb_divi_4_content`;
  - it sets `_et_pb_use_divi_5=on`.
  Until then, pages stay shortcode.


## 1. TL;DR (R6: tokens)

- **Divi 5 stores its global design data in four places:**

  | Data | Storage |
  |---|---|
  | Global colors | `et_divi['et_global_data']['global_colors']` |
  | The 5 Customizer colors | `et_divi[accent_color / secondary_accent_color / header_color / font_color / link_color]` |
  | Design variables | Option row `et_divi_global_variables` |
  | Module and option-group presets | Option row `et_divi_builder_global_presets_d5` |

  The D4 presets (`et_divi_builder_global_presets_ng`) are migrated into the D5 row and keep their ids.
- **Content references** all of these the same way, as a string inside the block JSON:
  `$variable({"type":"color","value":{"name":"gcid-…","settings":{}}})$` for colors, and
  `$variable({"type":"content","value":{"name":"gvid-…","settings":{}}})$` for every design variable (number, font, string,
  link, image). Inside a serialized block comment the inner quotes are written `"`.
  - Presets are referenced by id: `"modulePreset":["<id>"]` (an array, which is a stack) and
    `"groupPreset":{"<groupId>":{"presetId":["<id>"],"groupName":"divi/font"}}`.
  - The D4 form `gcid-<uuid>` + `global_colors_info` is gone; Divi's converter rewrites it to `$variable()$`.
- **The front end is far more transparent than in Divi 4.** Colors, numbers, fonts, images and gradients become CSS
  custom properties in `:root`:
  - `--gcid-*` for colors: the five Customizer colors always, and user global colors *when the page uses them*;
  - `--gvid-*` for design variables: the ones the page uses, or **all active ones** if the page uses none;
  - `--et_global_*` for the Customizer fonts, font weights and body size.
  - Module CSS refers to them with `var(--…)`.
  - **Preset CSS is emitted under its own class** (`preset--module--divi-button--<id>`,
    `preset--group--divi-heading--divi-font--<hash>--<id>`). A preset's *rendered declarations* are therefore recoverable
    from any page that uses it.
- **What is never recoverable from outside:**
  - labels (the "R6 Navy" names);
  - unused colors and variables;
  - string and link variable values, which are resolved inline;
  - preset *names*;
  - preset *attribute JSON*, as opposed to its rendered CSS;
  - the id of a module type's *default* preset (it renders as `preset--module--<module>--default`).
- **REST is a dead end for global data.** Every `divi/v1` route except `settings-data/nonces` needs an `X-ET-Nonce`.
  - With an Application Password, `/nonces` answers 200, but the nonces it returns were minted for **user 0**, before
    app-password authentication ran. Every other call then fails with `400 invalid_nonce`, even for an Administrator.
  - In any case, presets and the Customizer data are only in the VB's `app_load` payload, not in `after-app-load`.
  - Core `wp/v2` exposes none of these options.
- **Proposal:**
  - Keep the Divi 4 `tokens.json` shape where it maps.
  - Replace `colors.global` with rich objects.
  - Add `variables`, a D5 `presets` shape carrying recovered CSS, and `customizer` read from `:root`.
  - Keep `module_styles` / `section_exemplars` as D5 attribute JSON with the `$variable()$` strings **left
    verbatim**.
  - The AI references a global color, variable or preset **only when its id appears in tokens.json**; everything else is
    written inline. An unknown preset id silently strips the site's default preset (evidence in §3.5).

## 2. Where Divi 5 stores global design data (R6 Q1)

| Kind | Storage (DB) | Shape | Code |
|---|---|---|---|
| Global colors | `wp_options.et_divi` → `['et_global_data']['global_colors']` | `{"gcid-xxxx": {color, label, status: active\|inactive\|temporary, lastUpdated, folder, usedInPosts[]}}`. `color` may itself be a `$variable()$` pointing at another color, plus HSL `settings` (a nested or derived color). | `B5/Packages/GlobalData/GlobalData.php:349` `get_global_colors()`, `:667` `set_global_colors()` |
| Customizer colors (exposed as global colors) | `et_divi[accent_color]` = `gcid-primary-color`, `secondary_accent_color` = `gcid-secondary-color`, `header_color` = `gcid-heading-color`, `font_color` = `gcid-body-color`, `link_color` = `gcid-link-color` | Plain hex. Defaults are #2ea3f2 / #2ea3f2 / #666666 / #666666 / #2ea3f2. `set_global_colors()` routes these five ids back into the Customizer options. | `GlobalData.php:43-84`, `:386` |
| Customizer fonts (exposed as font variables) | `et_divi[heading_font]`, `et_divi[body_font]` | Variable ids `--et_global_heading_font` and `--et_global_body_font` (with the `--`) | `GlobalData.php:93-104`, `:431` |
| Design variables | Option row **`et_divi_global_variables`**. `et_get_option('global_variables', …, $is_product_setting=true)` stores it as `'et_' . $shortname . '_' . name`; see `epanel/custom_functions.php:225`. | `{numbers\|strings\|images\|links\|fonts\|gradients: {"gvid-xxxx": {id, label, value, order, status: active\|archived, type}}}`. `colors` exists as a key but is empty: colors live in `et_global_data`. | `GlobalData.php:821` sanitize (allowed types), `:913` get, `:1020` set (requires `edit_theme_options` + `variables_manager`) |
| Module presets + option-group presets | Option row **`et_divi_builder_global_presets_d5`** | `{module: {"divi/button": {default: "<id>", items: {"<id>": {type:"module", moduleName, id, name, created, updated, version, attrs, renderAttrs?, styleAttrs?, groupPresets?, priority?}}}}, group: {"divi/font": {default, items: {"<id>": {type:"group", groupName:"divi/font", groupId:"designTitleText", moduleName:"divi/heading", primaryAttrName:"title", id, name, attrs, …}}}}}`. `attrs` is the same attribute JSON a module carries in content. | `B5/Packages/GlobalData/GlobalPreset.php:152` option name, `:190` `get_data()`, `:236` `prepare_data()` |
| Legacy D4 presets | `et_divi_builder_global_presets_ng` (the D4 option) | D4 shape. Converted into the D5 row, **keeping their ids**, by `GlobalPreset::maybe_convert_legacy_presets()` (`GlobalPreset.php:1769`). A D5 delete also removes the D4 copy (`:1005`). | |
| Legacy D4 global colors | `et_divi['et_global_colors']` | Converted once into `et_global_data` when that is missing, **keeping the `gcid-<uuid>` ids** | `GlobalData::maybe_convert_global_colors_data()`, `GlobalData.php:542` |

**Group ids and group names.** The group id is the option group's slug on that module; the group name is the
option-group component. For example, `divi/heading` has `title.decoration.font` with
`groupSlug: "designTitleText"` and component `divi/font`.

Group names in `B5/_all_modules_metadata.php` (`presetGroup` values):

- `divi/font`, `divi/font-body`, `divi/font-header`;
- `divi/button`, `divi/border`, `divi/box-shadow`, `divi/background`;
- `divi/spacing`, `divi/sizing`, `divi/layout`, `divi/text`;
- `divi/animation`, `divi/filters`, …

### Reference syntax in content (exact)

`$variable(<json>)$`. The resolver is `B5/Packages/StyleLibrary/Utils/Utils.php:86`; the pattern
`/\$variable\((.+?)\)\$/` is on `:98`.

- `type` is `color`, `content` or `gradient`. These are the three types the VB emits (they appear literally in
  `visual-builder/build/*.js`). Numbers, fonts, strings, links and images are all written as `type:"content"`.
- `value.name` is a `gcid-…` or `gvid-…` id, or `--et_global_heading_font` / `--et_global_body_font` for the Customizer
  fonts. Dynamic content (for example `post_title`) uses the same wrapper.
- `value.settings` for colors takes `{hue, saturation, lightness, opacity}`. It renders as
  `hsl(from var(--gcid-x) calc(h + …) …)`; see `GlobalData.php:181`.

Evidence: a D4 → D5 conversion with Divi's own converter (`research/tools/divi5/convert.php`) of
`button_bg_color="gcid-8ce98ce1-…" global_colors_info="{…}" _module_preset="4f7e8a1b-…"` produced:

```
<!-- wp:divi/button {"button":{…"decoration":{…"background":{"desktop":{"value":{"color":"$variable({"type":"color","value":{"name":"gcid-8ce98ce1-4460-49e4-9cd7-b148b47c216c","settings":{}}})$"}}}}},"builderVersion":"4.27.9","modulePreset":["4f7e8a1b-1234-4c5d-9e8f-0a1b2c3d4e5f"]} -->
```

So D4 global color ids and D4 preset UUIDs **survive conversion unchanged**, and `builderVersion` keeps the source D4
version. An older D5 intermediate form `var(--gcid-…)` is migrated to `$variable()$` by
`B5/Migration/GlobalColorMigration.php`. It still renders, but it is not canonical.

## 3. Trace: DB → content → HTML/CSS → what an outsider recovers (R6 Q2 + Q3)

### 3.1 Setup

This ran through `wp-local.sh eval-file research/tools/divi5/r6_setup.php <scratch>/backup.json`. It used Divi's own
`GlobalData::set_global_colors()`, `GlobalData::set_global_variables()` and `GlobalPreset::save_data()`, and
`serialize_block_attributes()` for the page.

**Global colors:**

| Id | Value |
|---|---|
| `gcid-r6navy0001` | #0B2A3C |
| `gcid-r6orange001` | #F97316 |
| `gcid-r6orangelt1` | `$variable(gcid-r6orange001, lightness +30)$`, a nested/derived color |
| `gcid-r6unused001` | #22AA55 (unused) |

Customizer `gcid-primary-color` was also set to #7C3AED.

**Design variables:**

| Type | Id | Value |
|---|---|---|
| number | `gvid-r6radius01` | 12px |
| number | `gvid-r6secpad01` | `clamp(48px, 8vw, 96px)` |
| number (unused) | `gvid-r6unusedn1` | 7px |
| font | `gvid-r6font0001` | Poppins |
| string | `gvid-r6tagline1` | "Build faster with R6" |
| link | `gvid-r6ctalink1` | … |
| image | `gvid-r6image001` | … |

**Presets:**

- Module preset `r6btnpreset1` on `divi/button`: background uses R6 Orange, the radius uses `gvid-r6radius01`, and the
  text is white.
- Option-group preset `r6fontpreset1`: `divi/font`, group `designTitleText`, host `divi/heading`. Font family uses
  `gvid-r6font0001`, color uses R6 Navy, weight 700, size 52px.

**Page 23 `R6 tokens trace`**, a section → row → column containing:

- a section whose padding uses `gvid-r6secpad01` and whose background uses R6 Orange Light;
- a heading with `groupPreset` `r6fontpreset1`;
- a text block whose body is the string variable, colored R6 Navy;
- a button with `modulePreset` `r6btnpreset1` and its link set to the link variable.

### 3.2 DB (after setup)

`wp option get et_divi_global_variables --format=json` →
`{"numbers":{"gvid-r6radius01":{"id":"gvid-r6radius01","label":"R6 Radius","value":"12px","order":"1","status":"active","type":"numbers"},…},"fonts":{…"value":"Poppins"…},"strings":{…},"links":{…},"images":{…}}`.

`wp option get et_divi_builder_global_presets_d5` →
`{"module":{"divi/button":{"default":"","items":{"r6btnpreset1":{"type":"module",…,"attrs":{"button":{"decoration":{"background":{"desktop":{"value":{"color":"$variable({\"type\":\"color\",…gcid-r6orange001…})$"}}},…}}}}}}},"group":{"divi/font":{…"r6fontpreset1":{"type":"group","groupName":"divi/font","groupId":"designTitleText",…}}}}`.

### 3.3 Rendered HTML (`curl -sL http://divi-5-test.local/r6-tokens-trace/`, second hit)

`<style>` blocks:

- `et-vb-global-data et-vb-global-fonts`
- `et-vb-global-data et-vb-global-numeric-vars`
- `#divi-dynamic-critical-inline-(css)`
- `#et-critical-inline-css`

The last two are inlined copies of `wp-content/et-cache/23/et-divi-dynamic-23-critical.css` and
`et-core-unified-23.min.css`.

```
:root{--gcid-primary-color: #7C3AED;--gcid-secondary-color: #2ea3f2;--gcid-heading-color: #666666;--gcid-body-color: #666666;--gcid-link-color: #2ea3f2;--gcid-r6navy0001: #0B2A3C;--gcid-r6orange001: #F97316;--gcid-r6orangelt1: hsl(from var(--gcid-r6orange001) calc(h + 0) calc(s + 0) calc(l + 30));}
:root{--et_global_heading_font: 'Open Sans';--et_global_body_font: 'Open Sans';--et_global_heading_font_weight: 500;--et_global_body_font_weight: 500;--et_global_body_font_size: 14px;--et_global_body_font_height: 1.7em;}
:root{--gvid-r6radius01: 12px;--gvid-r6secpad01: clamp(48px, 8vw, 96px);--gvid-r6font0001: 'Poppins';}
body #page-container .et_pb_section .preset--module--divi-button--r6btnpreset1{background-color:var(--gcid-r6orange001);color:#ffffff!important;border-top-left-radius:var(--gvid-r6radius01);…}
.preset--group--divi-heading--divi-font--hp5h6dj--r6fontpreset1 .et_pb_heading_container h1,…{font-family:var(--gvid-r6font0001);font-weight:700;color:var(--gcid-r6navy0001)!important;font-size:52px}
.et-l--post>.et_builder_inner_content .et_pb_section.et_pb_section_0{background-color:var(--gcid-r6orangelt1)!important}
.et_pb_section_0.et_pb_section{padding-top:var(--gvid-r6secpad01);padding-bottom:var(--gvid-r6secpad01)}
.et_pb_text_0 .et_pb_text_inner{color:var(--gcid-r6navy0001)!important}
```

What the rendered page shows:

- **Markup:** `<a class="… preset--module--divi-button--r6btnpreset1" href="https://example.com/r6-start">` (the link
  variable is resolved inline) and `<p>Build faster with R6</p>` (the string variable is resolved inline).
- **Fonts:** Poppins is loaded, because the font variable is used.
- **What does not appear:** no `$variable(` survives into the HTML, and neither do the labels or the unused color, number
  or image.

**Page with no variable references.** `R6 plain`, a single `divi/text`, prints **all active** numbers, fonts and images:
`--gvid-r6unusedn1: 7px`, `--gvid-r6image001: url(https://example.com/r6-hero.jpg)`, and so on. It prints the five
Customizer `--gcid-*` colors, but *no* user global colors.

This follows from `B5/FrontEnd/FrontEnd.php:730-790`:

- `enqueue_global_numeric_and_fonts_vars()` prints every active variable unless
  `DetectFeature::get_page_global_variable_ids()` finds ids in the content (including ids reached through presets). If it
  finds ids, it prints only those.
- Colors go through `Style::get_global_colors_style($ids)` (`B5/FrontEnd/Module/Style.php:1360`). With Dynamic Assets
  that is limited to the used ids plus the Customizer colors (`DynamicAssetsListBuilder.php:309/601`). Without Dynamic
  Assets, **all** colors are printed (`FrontEnd.php:686`).

### 3.4 The Customizer in D5

`:root` always carries the five `--gcid-*-color` values and the `--et_global_*` values, **even when they are defaults**.
The override rules (`h1,…{color:var(--gcid-heading-color,#112233)}`, `body{color:var(--gcid-body-color,#333344)}`)
appear only when a value differs from its default. This was verified by setting `header_color`, `font_color` and
`heading_font` and re-fetching.

Caveat: when a value is still at its default, the `:root` value is the *option default* (#666666 for headings), while the
actual heading color comes from the base CSS (`h1{color:#333}`).

**The D4 extractor misreads D5 pages.** `tokens_from_html.py` against page 23 returned:

- `customizer.heading: "#333"` and `body_text: "#666"`, read from the base CSS;
- `link: "var(--gcid-link-color,#7C3AED)"` and `body_size: "var(--et_global_body_font_size)"`, which are unresolved
  `var()` expressions;
- `global_colors` mixing the Customizer ids with the user ids;
- `divi_version: "5.13.1"`, which is correct (from `?ver=`).

For D5 the Customizer should be read from `:root`.

### 3.5 Presets: default presets and unknown ids

**A module type's default preset renders under a `default` class.** After making `r6btnpreset1` the `divi/button`
default, a button with *no* `modulePreset` rendered class `preset--module--divi-button--default` with the same CSS.
Page 23's button, which explicitly names the default id, also rendered as `…--default`. The real default id is not
visible in public HTML.

**An unknown preset id strips the default preset's styling.** A button with `"modulePreset":["doesnotexist"]` rendered
class `preset--module--divi-button--doesnotexist` with **no** preset CSS, and it lost the default preset's styling.

### 3.6 REST: what an Application Password can read

`GET /wp-json/` lists namespace `divi/v1` with 164 routes. The design-data ones are all **POST-only writers or
VB-internal**:

- `global-data/global-colors|global-fonts|global-variables|global-preset/sync`;
- `portability/export|import`;
- `outside-vb/theme-options/get` (POST);
- `settings-data/after-app-load` (GET) and `settings-data/nonces` (GET).

Every route registered through `B5/Framework/Route/RESTRoute.php:83` gets a `rest_request_before_callbacks` filter that
requires `X-ET-Nonce` (`:139`, `wp_verify_nonce(..., '<route>--<METHOD>')`). There are two exceptions, which use
`NONCE_POLICY_WP_ONLY`:

- `settings-data/nonces` (`B5/VisualBuilder/REST/RESTRegistration.php:200-207`);
- `seo/rendered-content`, which is only registered when a supported SEO plugin is active.

Evidence with an Administrator Application Password (`d5_tokens_probe.py --probe-rest`):

```
GET  divi/v1/settings-data/nonces                          -> 200 {"nonces":{"wp_rest":{"ALL":"3f7d89b54f"},"/divi/v1/settings-data/after-app-load":{"GET":"270359695b"},…}}
GET  divi/v1/settings-data/after-app-load?et_post_id=23    -> 400 invalid_nonce   (with and without that X-ET-Nonce)
POST divi/v1/portability/export  (+ minted X-ET-Nonce)     -> 400 invalid_nonce
wp eval: wp_set_current_user(0) → wp_create_nonce('/divi/v1/settings-data/after-app-load--GET') = 270359695b
         wp_set_current_user(1) → … = 3fdb1291f2
```

Two facts close this route off:

- **The minted nonces belong to user 0.** `Nonce::add_data()` runs when the routes are registered, which is before
  WordPress authenticates the Application Password (that only happens once `REST_REQUEST` is set). The nonces are
  therefore minted for the anonymous user, and verification later runs as user 1, so it fails.
- **Presets are not in that payload anyway.** Even with a cookie session, `after-app-load` does not include
  `globalPresets` or the Customizer data. Those are `app_load` items, inlined into the VB page itself
  (`B5/VisualBuilder/SettingsData/SettingsData.php:91,131`).

Core REST exposes nothing either: `/wp/v2/settings` lists only core settings, and page `meta` is only `footnotes`.

### 3.7 Recoverability matrix

| Kind | Id visible in `content.raw`? | Value from public HTML? | Label? |
|---|---|---|---|
| User global color | yes (`$variable` color) | **yes** as `--gcid-x`, only on pages that use it (or all colors if Dynamic Assets is off) | no |
| Nested/derived color | yes | yes, as an `hsl(from var(--gcid-base) …)` expression | no |
| Customizer colors (5) | yes if referenced | **always**, from `:root` (defaults included; see the caveat in §3.4) | fixed names |
| Customizer fonts / body size / weights | yes if referenced | **always** (`--et_global_*`) | fixed |
| Number / font / image / gradient variable | yes (`$variable` content) | **yes** as `--gvid-x`: the used ones, or *all active* on a page that uses none | no |
| String / link variable | yes | only indirectly (resolved into text or `href`; you would have to line up the module's HTML with its `content.raw`) | no |
| Module preset | yes (`modulePreset` id) | **rendered CSS** under `.preset--module--<module>--<id>` on pages using it | no |
| Default module preset | no (implicit) | rendered CSS under `…--default`; the id is not shown | no |
| Option-group preset | yes (`groupPreset.<groupId>.presetId`) | rendered CSS under `.preset--group--<module>--<group>--<hash>--<id>` | no |
| Preset attribute JSON (reusable as attrs) | no | no (only the CSS) | no |
| Unused anything | no | no (except variables on a page that references none) | no |

Static CSS file generation, and cache or optimization plugins, move this CSS into `<link>` files. The same-origin
`/wp-content/et-cache/<id>/*.css` links must be followed; `d5_tokens_probe.py` does this, while the D4
`tokens_from_html.py` does not.

## 4. Proposed `tokens.json` for Divi 5 (R6 Q4)

The D4 keys stay, and `site.divi_major` selects the interpretation. The differences are:

```jsonc
{
 "site": {"url": "…", "divi_major": 5, "divi_version": "5.13.1", "content_format": "blocks",   // "shortcode" on D4
          "source_pages": [{"id": 23, "url": "…", "format": "blocks", "builder_versions": ["5.13.1"]}], "extracted_at": "…"},
 "colors": {
  "palette": [ {"hex": "#0b2a3c", "uses": 2, "roles": ["title.decoration.font.color", "…"], "global": "gcid-r6navy0001"} ],
  "global": {                       // D5: now populated. id -> {value, uses, raw?}
   "gcid-r6navy0001":  {"value": "#0B2A3C", "uses": 2},
   "gcid-r6orangelt1": {"value": null, "raw": "hsl(from var(--gcid-r6orange001) calc(h + 0) calc(s + 0) calc(l + 30))",
                        "base": "gcid-r6orange001", "uses": 1}
  },
  "customizer": {                   // D5: read from :root, always complete; ids included so the AI can reference them
   "primary":   {"id": "gcid-primary-color",   "value": "#7C3AED"},
   "secondary": {"id": "gcid-secondary-color", "value": "#2ea3f2"},
   "heading":   {"id": "gcid-heading-color",   "value": "#666666", "overridden": false},
   "body":      {"id": "gcid-body-color",      "value": "#666666", "overridden": false},
   "link":      {"id": "gcid-link-color",      "value": "#2ea3f2"},
   "heading_font": {"id": "--et_global_heading_font", "value": "Open Sans", "weight": "500"},
   "body_font":    {"id": "--et_global_body_font",    "value": "Open Sans", "weight": "500"},
   "body_size": "14px", "body_line_height": "1.7em"
  }
 },
 "variables": {                     // NEW (D5 only): id -> {value|null, uses, source}
  "numbers":   {"gvid-r6radius01": {"value": "12px", "uses": 4, "roles": ["button.decoration.border.radius"]}},
  "fonts":     {"gvid-r6font0001": {"value": "Poppins", "uses": 1}},
  "images":    {},
  "gradients": {},
  "strings":   {"gvid-r6tagline1": {"value": null, "uses": 1}},     // value not recoverable; id only
  "links":     {"gvid-r6ctalink1": {"value": null, "uses": 1}}
 },
 "presets": {                       // D5 shape (D4 keeps {slug: [{uuid, uses}]})
  "module": {"divi/button": [{"id": "r6btnpreset1", "uses": 1,
             "css": [{"selector": ".preset--module--divi-button--r6btnpreset1", "declarations": ["background-color:var(--gcid-r6orange001)", "…"]}]}]},
  "module_defaults_css": {"divi/button": [{"selector": "…--default", "declarations": ["…"]}]},   // what an un-preset module looks like
  "group":  {"divi/font": [{"id": "r6fontpreset1", "module": "divi/heading", "group_id": "designTitleText", "uses": 1,
             "css": [{"declarations": ["font-family:var(--gvid-r6font0001)", "font-weight:700", "color:var(--gcid-r6navy0001)!important", "font-size:52px"]}]}]}
 },
 "typography": { "…": "unchanged; scale entries hold D5 font objects {family, weight, size, color, lineHeight, letterSpacing} per breakpoint and may hold $variable strings" },
 "spacing": { "…": "section_padding values may be $variable strings; also record the resolved value" },
 "module_styles": {"divi/button": [{"attrs": { "…design-only D5 attribute JSON, $variable() strings verbatim…" },
                   "module_preset": ["r6btnpreset1"], "group_presets": {"designTitleText": {"presetId": ["…"], "groupName": "divi/font"}},
                   "module_class": "…", "uses": 1, "contexts": [ "…as D4…" ]}]},
 "section_exemplars": [ "…D5 block tree: {name, attrs(design-only), children}…" ]
}
```

**Where each part comes from:**

- `colors.global` and `variables.{numbers,fonts,images,gradients}`: the `:root` blocks of every sampled page, merged with
  the ids referenced in the sampled `content.raw`. Keep ids that are referenced but not seen, with `value: null`. Also
  **fetch one page that uses no variables**; that page leaks every active number, font and image variable.
- `presets.*.css`: rules whose selector names the preset class.
- `presets.*.id` and `uses`: `content.raw`.
- `module_defaults_css`: rules on `…--default` classes.
- Follow the same-origin `et-cache` `<link>` stylesheets.

**What the AI references by id, and what it writes inline:**

| Situation | Write |
|---|---|
| The color matches a `colors.global` / `customizer` entry *in the same role* the site uses it for (e.g. every button background is `gcid-r6orange001`) | `$variable({"type":"color","value":{"name":"<id>","settings":{}}})$`, never the hex. The link survives the client re-theming. |
| Accent, heading, body or link color | Customizer ids (`gcid-primary-color` …): they always exist, so they are always safe to reference |
| A number, font, image or gradient the site uses through a variable in that role (section padding, radius, display font) | `$variable({"type":"content","value":{"name":"gvid-…","settings":{}}})$` |
| Module look that matches an existing preset | `modulePreset: ["<id>"]`, or `groupPreset` with the exact `groupId`/`groupName` from tokens, **and no conflicting inline attrs** |
| A module that should just look like the site's default for its type | **Nothing.** Omit `modulePreset` and let the default preset apply. Never write an id that is not in tokens (see §3.5). |
| String / link variables | Only when the user explicitly asks for that site-wide text or URL; otherwise write it inline |
| Anything with no matching token | Inline value, following the D4 fidelity rule (say it is a guess) |
| New global colors, variables or presets | **Not possible over REST** (every writer needs `X-ET-Nonce`; §3.6). Tell the user to create them in the VB. |

**Validator additions (D5):**

- Warn on any `gcid-`/`gvid-`/preset id that is not in `tokens.json`. It renders as nothing (a variable) or strips the
  default preset (a preset).
- Error on `$variable(` payloads that are not valid JSON.
- Check `groupPreset` keys against the module's `groupSlug`s from metadata.

## 5. Remote version detection (R7 Q5)

Evidence came from `detect_divi.py` against `divi-5-test.local`, and from the saved D4 4.27.9 capture
`research/python-renderer-spike/out/truth/page11-live.html`. divi-test.local was down (HTTP 502) during the run and was
not started.

| Signal | D4 4.27.9 | D5 5.13.1 | Reliability |
|---|---|---|---|
| `GET /wp-content/themes/Divi/style.css` → `Version:` | 4.27.9 | 5.13.1 | Best unauthenticated exact version. It works with a child theme, because it reads the parent's file. |
| `?ver=` on `/themes/Divi/…` assets (e.g. `common.js?ver=`) | 4.27.9 | 5.13.1 | Good (most common value). Optimizers can strip it. |
| `<meta name="generator" content="Divi v.X">` | yes | yes | Active theme only (`epanel/custom_functions.php:907-909`). A child theme prints "Divi Child v.1.0". |
| REST `/wp/v2/themes?status=active` (Application Password, `edit_posts`) | version | version | Exact. With a child theme, read `template=Divi` and fall back to style.css. |
| `/wp-json/` routes under `/divi/v1` | 2 routes (`includes/builder/api/rest/BlockLayout.php:63,83`) | 164 routes (`global-data/*`, `settings-data/nonces`, `content-conversion`, `module-data/shortcode-module/html`) | Major-version signal. The namespace exists on both, so check the routes. |
| Asset paths `/includes/builder-5/visual-builder/build/script-library-*.js`, handles `divi-script-library-*` | absent | present | D5 marker |
| `<style class="et-vb-global-data et-vb-global-fonts|…numeric-vars">`, `:root{--gcid-…}` | absent | present | D5 marker (and the token source, §3) |
| Structure classes `et_block_section/row/module`; order class first (`et_pb_section_0 et_pb_section …`) | `et_pb_section et_pb_section_0` | order class first | D5 marker |
| `et_pb_custom.builder_images_uri` | `…/includes/builder/images` | `…/includes/builder-5/images` | Major-version signal |
| `var diviBreakpointData`, `var diviElementAnimationData` | absent | present | D5 marker |
| Body classes (`et_divi_theme et-db et_pb_pagebuilder_layout`), response headers | same | same | Useless |

**Algorithm** (implemented in `research/tools/divi5/detect_divi.py`):

1. With credentials, call `/wp/v2/themes?status=active`.
2. Read `themes/<template>/style.css` → `Version`.
3. Take the most common `/themes/Divi/` `?ver=`.
4. Use the generator meta only if its name starts with "Divi".
5. Take the major version from the first exact version found. If there is none, use the D5 HTML markers or REST routes.
6. Warn when the exact version and the markers disagree, which suggests cached or optimized HTML.

**Per page (`content.raw` alone):**

- `[et_pb_` with no `<!-- wp:divi/` means D4 shortcode.
- `<!-- wp:divi/` means D5 blocks, possibly wrapped in `wp:divi/placeholder` (Migrator output).
- `wp:divi/shortcode-module` means D5 content that carries legacy shortcode.
- `<!-- wp:divi/layout -->` around shortcode is D4's block-editor layout block.
- `builderVersion` inside blocks is **not** the site version. Converter output is stamped `5.0.0-public-alpha.18.2` or
  `5.0.0-public-beta.1`, and some blocks keep `4.27.9`, as in §2.

## 6. Legacy D4 content on a D5 site (R7 Q6)

- **Rendering without conversion.**
  - D5 bundles the D4 builder and registers D4 shortcodes lazily per tag
    (`includes/builder/class-et-builder-module-shortcode-manager.php:960-990, 1545-1565`;
    `et-pagebuilder/et-pagebuilder.php:109`).
  - Output is D4 markup tagged `et_d4_element` (`includes/builder/class-et-builder-element.php:3020`).
  - Test: `tests/fixtures/valid/handwritten-landing.txt` was pushed with `_et_pb_use_builder=on`, exactly what
    `publish.py` sends today. The content stayed shortcode, the HTML had 33 `et_d4_element`, and per-module CSS was
    emitted.
  - **But** `et-cache/<id>/et-divi-dynamic-<id>.css` (the deferred dynamic CSS) was never generated, even after clearing
    the cache and 3 more fetches.
  - Headless-Chrome screenshots showed an unstyled header/menu, 1/2 and 1/3 columns collapsed into one stack, and blurb
    icons missing. The same fixture, converted to D5 blocks and saved, rendered correctly with identical text and colors.
- **The Visual Builder.** The D4 VB is gone: `et-pagebuilder/builder-5.php:15-45` makes `et_builder_d5_enabled()` always
  true.
  - Opening a D4 page converts it in memory (`B5/VisualBuilder/SettingsData/SettingsDataCallbacks.php:893-903` →
    `Conversion::maybeConvertContent`).
  - Only **Save** persists D5 blocks, `_et_pb_use_divi_5=on` and `_et_pb_use_builder=on`
    (`B5/VisualBuilder/REST/SyncToServer/SyncToServerController.php:380-386`). No D4 backup is written on this path.
- **`divi/shortcode-module`** (`visual-builder/packages/shortcode-module/src/module/module.json`,
  `d4Shortcode: et_pb_unsupported`, category `unsupported`) is what the converter emits in two cases:
  - a registered D4 module with no D5 equivalent, typically third-party (`B5/Packages/Conversion/Conversion.php:1545-1553`);
  - a core module carrying attributes the converter doesn't know (`:1620-1628`). For example,
    `[et_pb_text my_plugin_attr="x"]` → `<!-- wp:divi/shortcode-module {"unknownAttributes":{"my_plugin_attr":"x"},"content":"[et_pb_text …]","shortcodeName":"et_pb_text"…} -->`.

  It renders through `et_module_shortcode_output` on the front end and `/divi/v1/module-data/shortcode-module/html` in
  the VB. An **unregistered** shortcode (`[dsm_typing_effect]`) was **silently dropped** by conversion.
- **Policy: never write D4 shortcode to a D5 site.** Always write native `wp:divi/*` blocks, and set `_et_pb_use_builder=on`
  plus `_et_pb_use_divi_5=on`, as a VB save does. Never author `divi/shortcode-module`. Preserve existing
  `divi/shortcode-module` and `divi/placeholder` blocks verbatim when editing.

## 7. Site-wide D4 → D5 migration (R7 Q7)

- **Nothing converts on upgrade.** `upgrader_process_complete` and `after_switch_theme` only clear caches
  (`d5-readiness/d5-readiness.php:86-94`).
- **Manual "Divi 5 Migrator".** It lives on the admin page `et_d5_readiness` and needs `manage_options`
  (`d5-readiness/server/AdminPage.php:29-38`). It batches over AJAX `wp_ajax_et_d5_readiness_convert_d4_to_d5`
  (`AJAXEndpoints/Upgrade.php:34-121`).
  - It converts global presets first (`GlobalPreset::maybe_convert_legacy_presets()`), then each post
    (`d5-readiness/server/Conversion.php:35-135`).
  - Per post (reproduced with `convert_single_post`), it:
    - writes `post_content` = `<!-- wp:divi/placeholder -->…D5 blocks…<!-- /wp:divi/placeholder -->`;
    - backs up the original to `_et_pb_divi_4_content`;
    - sets `_et_pb_use_divi_5=on` and `_et_pb_divi_5_conversion_status={"status":"success","builder_version":"5.13.1",…}`;
    - sets `et_d5_readiness_conversion_finished` after the last batch.
  - Rollback restores from `_et_pb_divi_4_content` (`AJAXEndpoints/Rollback.php:78-132`).
  - The pending list is posts with `_et_pb_use_builder=on` AND (no `_et_pb_use_divi_5` OR
    `_et_pb_has_newly_convertible_modules`) (`Conversion.php:492-560`).
- **Otherwise conversion is lazy, per page.** A page is converted when someone opens it in the VB and saves.
  Unconverted pages keep `[et_pb_…]` in `content.raw` and render through the degraded legacy path from §6.
- **Global data converts lazily too.**
  - D4 `et_global_colors` → `et_global_data` on settings init (`B5/Framework/Settings/Settings.php:221`) and on
    conversion.
  - D4 presets → `et_divi_builder_global_presets_d5` when the VB loads (`SettingsDataCallbacks.php:644`) or through the
    Migrator.
  - Ids are kept, so D4 `gcid-<uuid>` ids and preset UUIDs stay valid after upgrade. For presets this is inferred from
    the id comparison in `GlobalPreset.php:100-148`, not tested end to end.

## 8. Implications for the skill

1. **Detect before anything else.**
   - Per site: `detect_divi.py` logic (style.css version → major).
   - Per page: classify `content.raw` as `shortcode`, `blocks` or `mixed/shortcode-module`.
   - Record both in `tokens.json.site` (`divi_major`, `content_format` per source page).
2. **On D5 sites, output only `wp:divi/*` blocks.**
   - Serialize attributes the way `serialize_block_attributes()` does: `"` inside string values becomes `\u0022`, and
     `<`, `>`, `&` and `--` are escaped too.
   - Set `_et_pb_use_builder=on` and `_et_pb_use_divi_5=on` on push.
   - Use the site's `divi_version` for `builderVersion`.
3. **Editing an existing page on an upgraded site.**
   - If the page is still shortcode, do not patch the shortcode. Either regenerate the page as D5 blocks (the D4 parser
     and tokens can still read the old page as a style source), or ask the user to run the Migrator or open and save the
     page first.
   - If the page is blocks, edit the blocks and keep `divi/placeholder` / `divi/shortcode-module` verbatim.
4. **Token extraction needs a D5 branch.**
   - Read `:root` `--gcid-*` / `--gvid-*` / `--et_global_*` and the `preset--*` CSS rules.
   - Follow same-origin `et-cache` links.
   - Fetch one variable-free page, which leaks all active number, font and image variables.
   - Parse `$variable()$` and `modulePreset`/`groupPreset` from `content.raw`.
   - `tokens_from_html.py`'s D4 Customizer selectors return wrong or unresolved values on D5 (§3.4).
5. **Reference, don't copy.** Where tokens.json has a global color, variable or preset id for the role, write the
   reference (§4 table). This keeps the new page linked to the client's design system. D4 could not do this, because
   `gcid` resolution was invisible there.
6. **Never invent ids.**
   - Validate every `gcid-`/`gvid-`/preset id against tokens.json.
   - An unknown `modulePreset` id silently disables the module's default preset (§3.5).
   - Omit `modulePreset` to inherit the site default.
7. **Read-only design system.** REST cannot create or read global colors, variables or presets with an Application
   Password (§3.6). New site-wide tokens must be created by the user in the VB. The skill can only reuse what the public
   pages reveal.
8. **Preview.** The local mirror can render references only if the mirror has the same global data. Otherwise
   `var(--gcid-…)` and unknown presets render unset. Options:
   - seed the mirror from tokens.json: colors and variables are recoverable as values; presets only as CSS, which could be
     injected as a stylesheet;
   - or keep the WordPress draft preview as the authoritative check, as in D4.

## 9. Changes made to the local D5 site (and restored)

- **Options:** `et_divi[et_global_data|accent_color|header_color|font_color|heading_font]`, `et_divi_global_variables`
  and `et_divi_builder_global_presets_d5`. They were backed up to the scratchpad and restored with `r6_restore.php`.
  `font_color` and `heading_font`, set by hand for §3.4, were absent before and were removed by the same restore.
- **Pages:** 23 `R6 tokens trace` and 34 `R6 plain` were deleted. The fork's pages 13, 35 and 121 were deleted by the
  fork.
- **Application Password:** "R6 research" (user 1) was deleted.
