# Divi 5: storage, push and serialization (spikes R1 + R3)

Verified on 2026-09-28 against `http://divi-5-test.local` (LocalWP, **Divi 5.13.1**, **WordPress 7.1.2**,
PHP 8.2, admin user `user`). "Divi is the judge": every claim below comes from running Divi/WordPress code
on that site, or from a file:line in the installed source. Paths are relative to
`wp-content/themes/Divi/` unless they start with `wp-includes/`. `S/` = `includes/builder-5/server/`.
Test pages were titled `D5 Test: …` / `D5 Probe: …` and all were deleted at the end; the temporary editor user,
Application Passwords and mu-plugins were removed and `wp-config.php` was restored byte-for-byte (the site
was shared with a concurrent spike, whose pages `R5 …` were left alone).

## TL;DR

1. **post_content is WordPress block markup** — nested `<!-- wp:divi/<module> {JSON} -->` comments. All module
   data (text, HTML, URLs, styles) lives in the JSON attributes; Divi modules have **no inner HTML** between
   the tags. Leaves are self-closing `<!-- wp:divi/text {…} /-->` when saved by the builder or by WP's
   serializer; Divi's PHP converter writes them as empty open/close pairs. Both parse identically.
2. **Wrapper:** the Visual Builder saves the whole page inside `<!-- wp:divi/placeholder -->…<!-- /wp:divi/placeholder -->`.
   The wrapper is optional for rendering (unwrapped content renders identically) but it is what Divi writes.
3. **Meta:** `_et_pb_use_builder=on` is **still required** for the page layout (no title, no sidebar,
   `et_pb_pagebuilder_layout` body class). Without it the modules still render and are styled, but inside the
   normal page template (H1 title + sidebar). The builder also writes `_et_pb_use_divi_5=on` (migration
   bookkeeping only; not read by the renderer) and `_et_pb_show_page_creation=off`.
4. **REST push regression vs Divi 4:** `POST /wp/v2/pages` with `meta:{_et_pb_use_builder:"on"}` returns 201 but
   the meta is **silently not saved** on Divi 5.13.1 (the key is registered too late in REST requests). Divi's
   own save route (`/divi/v1/sync-to-server`) is unusable with an Application Password (needs `X-ET-Nonce`,
   and the nonce endpoint hands out nonces for user 0). Working options: WP-CLI, or a 10-line mu-plugin that
   registers the meta early (verified), or ask a human to toggle the builder once.
5. **Encoding:** attribute JSON must use WordPress's `serialize_block_attributes()` escaping
   (`\u0022 \u003c \u003e \u0026 \u002d\u002d \u005c`). Any valid JSON parses (raw `<`, `&`, `\"` included),
   but for users **without `unfiltered_html`** kses re-parses the block comments and raw `<`/`"` in the JSON
   **destroy the page**; canonical escaping survives. Every PHP path (converter, migrations, kses, REST
   `content.raw`) emits the WP canonical form; the builder's JS serializer differs only in writing `\\` instead
   of `\` and adding newlines.
6. **Round trip:** `serialize_blocks(parse_blocks(x))` is **not** byte-identical for converter output (leaves
   become self-closing) or for non-canonical escaping, but it always yields the **same block tree** and is a
   **fixed point** after one pass (41/41 files). WordPress-canonical input (e.g. `v6` below) round-trips byte-exactly.
7. **REST `content.raw` is not the stored bytes on WP ≥ 7.0**: core's Block Hooks re-serialize it on every
   read. Stored `post_content` itself is byte-identical for WP-CLI and REST writes by an admin.
8. **CSS:** generated per page on first view into `wp-content/et-cache/<id>/` (`et-core-unified-<id>.min.css`,
   `…-deferred-…`, `et-divi-dynamic-<id>-critical.css`, sometimes `et-divi-dynamic-<id>.css`) and **inlined**
   as `<style id="et-core-unified-<id>-cached-inline-styles">`. A REST update marks the files `.stale` and the
   next view regenerates them. **`wp post update` without `--user` does not invalidate the cache** (stale CSS was
   served) — always pass `--user=<admin>`.
9. **D4 shortcode content** pushed as-is still renders on D5 through the legacy D4 shortcode framework
   (modules carry an extra `et_d4_element` class); nothing is converted or rewritten in the DB. The Visual
   Builder converts it on open and saves D5 blocks.
10. **All 35 D4 fixtures convert and render** (HTTP 200, no PHP errors). One real conversion loss:
    `et_pb_signup_custom_field` children are left as a D4 shortcode string inside the signup's
    `content` attribute and are **not rendered** on D5 (they do render when the D4 shortcode is pushed as-is).

## 1. What Divi 5 stores for a page (R1 Q1)

### 1.1 post_content

Block markup, one block per module, nested section → row → column → module (→ child module):

```
<!-- wp:divi/placeholder -->
<!-- wp:divi/section {"module":{"decoration":{"background":{"desktop":{"value":{"color":"#0b2a3c"}}}}},"builderVersion":"5.0.0-public-alpha.23","modulePreset":["default"]} --><!-- wp:divi/row {…} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}}},…} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Emergency Plumber in Miami"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h1",…}}}}}},…} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
<!-- /wp:divi/placeholder -->
```

(`tests/fixtures/divi5/converted/handwritten-landing.html`). Block names seen across the 35 fixtures:
46 distinct `divi/*` names (section, row, row-inner, column, column-inner, text, heading, blurb, button, …,
`slide`, `tab`, `accordion-item`, `contact-field`, `map-pin`, `counter`, `pricing-table`,
`social-media-follow-network`, `video-slider-item`). D4 structural types map to the column's
`module.advanced.type` (`"1_2"`) and the row's `module.advanced.columnStructure` (`"1_2,1_2"`).

### 1.2 Post meta

| key | who writes it | needed? | evidence |
|---|---|---|---|
| `_et_pb_use_builder` = `on` | builder save (`S/VisualBuilder/REST/SyncToServer/SyncToServerController.php:380-387`), `outside-vb/posts/set-layout` (`OutsideVbController.php:1104`) | **Yes, for layout.** `et_pb_is_pagebuilder_used()` reads only this key (`includes/builder/core.php:4216-4234`). Page 7 (no meta): body `et_right_sidebar`, `<h1 class="entry-title">`, `#sidebar` present. Page 8 (meta on): `et_pb_pagebuilder_layout et_no_sidebar`, no title, no sidebar. Modules + CSS rendered in both. | curl of both pages |
| `_et_pb_use_divi_5` = `on` | builder save (same lines), D5 readiness migrator (`d5-readiness/server/Conversion.php:118`), portability import | No for rendering. Read only by the readiness migrator / rollback / compatibility checks (`d5-readiness/server/…`), portability, WPML compat. Recommended to write anyway so the migrator skips the page. | `grep -rn _et_pb_use_divi_5` |
| `_et_pb_show_page_creation` = `off` | builder save (`SyncToServerController.php:387`) | No; suppresses the "create page" onboarding in the VB. | |
| `_et_pb_divi_4_content`, `_et_pb_divi_5_conversion_status` | readiness migrator only (`d5-readiness/server/Conversion.php:108-121`) | No (backup of the D4 content). | |
| page settings (`_et_pb_custom_css`, `_et_pb_page_gutter_width`, …) | builder save → `SavingUtility::save_page_settings()` maps D5 names to the **D4 meta keys** (`S/VisualBuilder/Saving/SavingUtility.php:1923-2200`) | Only when used. | |
| `_divi_dynamic_assets_cached_modules`, `_divi_dynamic_assets_cached_feature_used`, `_divi_dynamic_assets_canvases_used`, `et_enqueued_post_fonts` | front end, on first render | No — caches Divi writes itself. `cached_modules` has separate `blocks` / `shortcodes` lists. | `wp post meta list` after a view |

There is **no builder-version flag in meta**; versioning is per block (`builderVersion` attribute, §4.5).

### 1.3 The `divi/placeholder` wrapper

- It is a real (non-rendering) block that wraps the whole document. The builder's JS serializer ends with
  `flow([replaceEscapedQuotes, wrapPlaceholderBlock])(serialize(blocks))`
  (`S/../visual-builder/build/serialized-post.js`), i.e. every VB save is wrapped. PHP twin:
  `ModuleUtils::wrap_placeholder_block()` / `maybe_unwrap_placeholder_block()` (`S/Packages/ModuleUtils/ModuleUtils.php:2311-2352`).
- Why: VB content is parsed into a `divi/root` tree whose direct children are dropped by
  `get_comment_delimited_block_content()` unless wrapped — "only the first row gets rendered, the rest is gone"
  (`S/Migration/Utils/MigrationUtils.php:99-120`, `ensure_placeholder_wrapper()`; adds `\n` after the opener and
  before the closer). The VB wraps raw content on load for PHP/JS parity (`S/VisualBuilder/SettingsData/SettingsDataCallbacks.php:944-946`).
- The front-end parser skips it (`S/FrontEnd/BlockParser/BlockParser.php:664,691`,
  `BlockParserStore.php:249`). An empty D5 page is `<!-- wp:divi/placeholder /-->`
  (`includes/builder/feature/BlockEditorIntegration.php:787`, `MigrationUtils.php:1019`).
- The readiness migrator and portability import wrap converted D4 content (`d5-readiness/server/Conversion.php:44`,
  `core/components/Portability.php:4818`).
- **Verified:** unwrapped content (raw converter output, 35 files) and wrapped content (migrated output, 35 files;
  escape case v5/v6) all render with every module present.

### 1.4 What the builder writes on save (code path)

`POST /wp-json/divi/v1/sync-to-server` → `SyncToServerController::update()`:
1. `content.post_content` is sanitized by `SavingUtility::prepare_content_for_db()`: **returned unchanged if the
   user has `unfiltered_html`**, otherwise `parse_blocks()` → per-attribute `wp_kses_post` on string values that
   contain HTML tags → WP serializer (`SavingUtility.php:230-254, 1724-1782, 2272-2360`).
2. `wp_update_post([… 'post_content' => wp_slash($post_content) …])` (`SyncToServerController.php:230-254`),
   then the meta writes in §1.2, then `do_action('et_update_post')` / `divi_visual_builder_rest_update_post`.
3. Save verification replays Divi's `wp_insert_post_data` transforms (priority 5 `AttributeSecurity`, 6
   `HtmlSecurity`, 10 `DynamicContentFixes`; `S/Security/Security.php:78-84`) and compares
   (`SyncToServerController.php:1110-1126`).

The content itself comes from the bundled `@wordpress/blocks` serializer (§4.1). A live VB save was **not
observed** in this spike (logging into wp-admin in the browser was out of scope); the VB format below is read
from the shipped bundles.

## 2. Push tests (R1 Q2)

Tools: `research/tools/divi5/push_probe.py` (4 methods × N files, compares stored bytes, REST `content.raw`,
rendered HTML), `research/tools/divi5/render_check.sh` (publish + curl + debug.log per file).

### 2.1 WP-CLI vs REST, admin (has `unfiltered_html`)

For all 6 escape-case files (§6) and the converted fixtures:

| | WP-CLI `wp post create FILE --user=1` | REST `POST /wp/v2/pages` (App Password) |
|---|---|---|
| stored `post_content` == file bytes | yes (all) | yes (all) |
| `content.raw` from `GET ?context=edit` == file bytes | n/a | **only for WP-canonical input** (`v6`); all others come back re-serialized |
| `meta._et_pb_use_builder` | set with `wp post meta update` → works | **not saved** (see 2.3) |
| rendered heading/text HTML | identical across all 6 encodings and both methods (24/24 identical fragments) | |

WP-CLI without `--user` also stores bytes unchanged (no kses in WP-CLI), but see the cache caveat in 2.4.

### 2.2 REST `content.raw` is re-serialized by WordPress core (WP ≥ 7.0)

`WP_REST_Posts_Controller::prepare_item_for_response()` runs `insert_hooked_blocks_into_rest_response()` for
`post`/`page` (`wp-includes/rest-api/endpoints/class-wp-rest-posts-controller.php:2173-2180`), which re-parses and
re-serializes `content.raw` via Block Hooks (`wp-includes/blocks.php:1537-1552`). Observed: page 83 stored the
converter's `--><!-- /wp:divi/heading -->` bytes, but `content.raw` returned `/-->`. Consequence: **a REST
read-modify-write cycle normalizes the page to WP canonical form** (harmless — same tree — but byte-diffs vs
the stored copy are expected). Filter `rest_block_hooks_post_types` can opt a type out.

### 2.3 `_et_pb_use_builder` over REST does not stick on Divi 5.13.1

- Divi registers the meta for REST in `ET_Builder_Block_Editor_Integration::init_hooks()`
  (`includes/builder/feature/BlockEditorIntegration.php:1060-1080`), but in D5 that file is only loaded when
  `is_admin()` (`includes/builder/framework.php:49-52`) or when the D4 shortcode framework is lazily loaded
  (`includes/builder/shortcode-framework.php:250`), which in a REST request evidently happens only while rendering
  `content.rendered` — after the meta update step.
- Probe (temporary mu-plugin logging hooks): at `rest_api_init` `registered_meta_key_exists(...)=false`; the
  request's `meta` param was `{"_et_pb_use_builder":"on"}`; no `added_post_meta` fired; the **response**
  lists the key with value `""` (by then it is registered). Tried: create draft/publish with D4 content, with
  D5 content, a meta-only update, and `?context=edit` update — `wp post meta get` empty every time
  (pages 123–126).
- Same requests with a mu-plugin that calls `register_post_meta('', '_et_pb_use_builder', [show_in_rest,
  single, type string, auth_callback edit_post])` on `init`: **all six stored `on`** (pages 128–131).
- Divi's own routes (`/divi/v1/sync-to-server`, `/divi/v1/outside-vb/posts/set-layout`,
  `/divi/v1/content-conversion`) reject App-Password requests with `invalid_nonce`: `RESTRoute` checks
  `X-ET-Nonce` before the permission callback (`S/Framework/Route/RESTRoute.php:128-134`). The nonce list at
  `GET /divi/v1/settings-data/nonces` is reachable with an App Password, but its nonces are minted for user 0
  (`wp_create_nonce` as user 0 matched the returned value; `wp_verify_nonce` as user 1 = false), so they never
  verify. These routes are effectively VB-only.

### 2.4 Rendering and CSS

- Every pushed page rendered HTTP 200 with D5 module markup: order class first, e.g.
  `class="et_pb_heading_0 et_pb_heading et_pb_module et_block_module"` (D5) vs
  `class="et_pb_module et_d4_element et_pb_heading et_pb_heading_0 …"` (D4 shortcode rendered by D5).
- CSS lands in `wp-content/et-cache/<id>/` on the first front-end view and is inlined as
  `<style id="et-core-unified-<id>-cached-inline-styles">` (+ `-deferred-`); `et-divi-dynamic-<id>.css` is loaded
  via `<link rel=preload>`. Example: `.et_pb_text_0{background-color:#ff00aa;text-align:start}` for a
  minimal text block.
- **REST update:** right after `POST /wp/v2/pages/<id>` with new content each cache file gets a companion
  `*.stale` marker (files kept, not deleted — D4 deleted the directory); the next view regenerates the files,
  removes the markers and serves the new CSS (`background-color:#123456` after the edit). Mechanism:
  `ET_Core_PageResource::save_post_cb` (`core/components/PageResource.php:948, 1327-1385`).
- **WP-CLI update without `--user`:** no markers, and the next view served the **old** CSS with the new HTML.
  Cause: `remove_static_resources()` bails unless `et_core_security_check_passed('edit_posts')`
  (`core/components/PageResource.php:1404`). With `--user=1` the `.stale` markers appear as for REST.

## 3. Plain D4 shortcode on a D5 site (R1 Q3)

`tests/fixtures/valid/handwritten-landing.txt` pushed verbatim (+ `_et_pb_use_builder=on`, page 9):
rendered fully (50 `et_pb_*` elements, `et_d4_element` on every module, et-cache generated; meta
`_divi_dynamic_assets_cached_modules.shortcodes` lists the 13 D4 tags). `post_content` was unchanged (same md5)
and no D5 meta was added — **not converted on the fly, only rendered through the legacy shortcode framework**.
Conversion happens when the page is opened in the VB (`SettingsDataCallbacks.php:891-904` runs
`Conversion::maybeConvertContent()` on load) and is persisted only when the user saves, or via the D5
readiness migrator. Related: D4 shortcodes **inside** a D5 text module are executed too (§6.3).

## 4. Grammar (R3 Q4)

### 4.1 Block comments

Parsed by WordPress's `WP_Block_Parser` (Divi's `BlockParser` extends it and is installed via
`block_parser_class`, `S/Packages/ModuleLibrary/Modules.php:420-440`; it adds global-layout expansion, loop
duplication and dynamic-data substitution, but tokenizes with core's regex):

```
<!--\s+(?P<closer>/)?wp:(?P<namespace>[a-z][a-z0-9_-]*/)?(?P<name>[a-z][a-z0-9_-]*)\s+(?P<attrs>{(?:(?:[^}]+|}+(?=})|(?!}\s+/?-->).)*+)?}\s+)?(?P<void>/)?-->
```
(`wp-includes/class-wp-block-parser.php:247-253`). Note the attrs must be followed by whitespace before
`-->` / `/-->`. Divi's feature detector `SimpleBlockParser` uses a looser regex that requires exactly
`<!-- wp:` with one space (`S/FrontEnd/BlockParser/SimpleBlockParser.php:164-169`) — so emit the canonical
spacing.

Writers:

| writer | opener / leaf | between blocks | JSON escaping |
|---|---|---|---|
| WP `serialize_block()` / `get_comment_delimited_block_content()` (`wp-includes/blocks.php:1750-1769`) — used by kses, REST read, migrations (`MigrationUtils::serialize_block`, `MigrationUtils.php:657-680`) | `<!-- wp:divi/x {…} -->…<!-- /wp:divi/x -->`; **empty content ⇒ `<!-- wp:divi/x {…} /-->`**; no attrs ⇒ `<!-- wp:divi/x -->` | nothing (inner chunks kept as-is) | `serialize_block_attributes()` (below) |
| Divi PHP converter `Conversion::convertShortcodeToGbFormat()` | leaves as `<!-- wp:divi/x {…} --><!-- /wp:divi/x -->` (`S/Packages/Conversion/Conversion.php:1648`) | nothing | `serialize_block_attributes()` (`Conversion.php:1517`) |
| Visual Builder (`@wordpress/blocks` serializer bundled at `S/../visual-builder-dependencies/wordpress/blocks.min.js`) | `<!-- wp:x {…} -->\n` + content + `\n<!-- /wp:x -->`; leaves self-closing (`save:()=>null` for non-structure modules, `serialized-post.js`) | `\n\n` | `JSON.stringify` + replace `--`,`<`,`>`,`&`,`\"` (no `\`); then `replaceEscapedQuotes` fixes a trailing `\\u0022` |

### 4.2 JSON attribute escaping

WordPress 7.1 `serialize_block_attributes()` (`wp-includes/blocks.php:1705-1719`):
`wp_json_encode($attrs, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)` then `strtr` with
`\\`→`\u005c`, `--`→`\u002d\u002d`, `<`→`\u003c`, `>`→`\u003e`, `&`→`\u0026`, `\"`→`\u0022`.
Non-ASCII stays raw UTF-8 (`ü € 😀`), `/` is not escaped, control characters use JSON escapes (`\n`);
PHP's encoder still escapes U+2028/U+2029 as `\u2028`/`\u2029`. The Divi converter output confirms this
form (`unicode.html`: `content: \u0022a\u005cb\u005cc\u0022;`, `\u0026#91;VIP\u0026#93;`, `\u003cp\u003e`).

### 4.3 Where content lives

- **All module content is in attributes**: text/HTML in `…innerContent.desktop.value` (e.g.
  `content.innerContent.desktop.value = "<p>…</p>"`, `title.innerContent.desktop.value`), image `src`, link
  `linkUrl`, icon objects — see §5. `innerHTML` of every `divi/*` block is empty; the comment pairs only
  delimit child blocks.
- Exception: `divi/shortcode-module` (unconvertible D4 module) keeps the original shortcode as inner HTML
  between its tags (`Conversion.php:1646`); the VB serializer's `unsupported` category also saves `innerHTML`.
- Global modules become `<!-- wp:divi/global-layout {"globalModule":"<id>","blockName":…,"localAttrs":…} -->`
  (`Conversion.php:1592-1604`), expanded at render (`BlockParser.php:880-945`).

## 5. Attribute value model (R3 Q5)

```
<group>.<kind>.<option>…<breakpoint>.<state> = value
  group      : module | title | content | button | image | imageIcon | overlay | field | … (per module)
  kind       : innerContent | decoration | advanced | meta
  breakpoint : desktop | tablet | phone   (+ phoneWide, tabletWide, widescreen, ultraWide when enabled)
  state      : value | hover | sticky     (+ focus, checked, active for form-ish options)
```

Examples from the fixtures:
`module.decoration.spacing.desktop.value.padding.top = "96px"`,
`title.decoration.font.font.desktop.value = {"headingLevel":"h1","family":"Montserrat","weight":"700","color":"#ffffff","size":"56px"}`,
`button.decoration.background.desktop.hover.color = "#ea580c"`,
`module.decoration.spacing.desktop.hover.padding = {"top":"10px",…,"syncVertical":"off","syncHorizontal":"off"}`,
`icon.advanced.color.desktop.hover = "#fde68a"`,
`module.decoration.sticky.desktop.value = {"position":"none","limit":{…},"offset":{"surrounding":"on"},…}`.
Across the 35 fixtures: breakpoints desktop 9364 / tablet 405 / phone 357; states value 10034 / hover 68 / focus 24.

- **Breakpoints:** defaults `desktop, tablet, phone` (`S/Framework/Breakpoint/Breakpoint.php:57-63`); full list
  with widths and enable flags in `get_default_settings_values()` (`:72-150`): phone ≤767 (on), phoneWide ≤860
  (off), tablet ≤980 (on), tabletWide ≤1024 (off), desktop (base), widescreen ≥1280 (off), ultraWide ≥1440
  (off); plus disabled-on pseudo-breakpoints `desktopAbove`, `tabletOnly`. Site overrides live in option
  `et_divi_builder_breakpoints` (`:29`; empty on the test site). Base state name is `value` (`:50`).
- **States:** `ModuleUtils::states()` = `value, hover, focus, checked, active, sticky` (`ModuleUtils.php:2464-2482`).
- **No enable flags.** D4's `_last_edited="on|tablet"` / `__hover_enabled="on|hover"` / `__sticky_enabled` have no
  D5 equivalent: a breakpoint/state key is either present or absent. The converter drops tablet/phone values
  whose `_last_edited` is not `on…` and hover/focus/checked/active/sticky values whose enable flag is off
  (`Conversion::enabled()` `Conversion.php:740-755`; applied at `:1044-1110`).
- **Types seen:** hex/rgba colors (`"#1D4ED8"`, `"rgba(0,0,0,0.5)"`); **global colors as dynamic variables**
  `"$variable({\"type\":\"color\",\"value\":{\"name\":\"gcid-828accbb-…\",\"settings\":{}}})$"` (definitions in
  `et_divi['et_global_data']['global_colors']`, migrated from D4 `et_global_colors`,
  `S/Packages/GlobalData/GlobalData.php:547-561`); font objects (`family`, `weight`, `size`, `lineHeight`,
  `letterSpacing`, `color`, `headingLevel`); spacing objects with `syncVertical`/`syncHorizontal` `"on"|"off"`;
  border `{"styles":{"all":{"width","color","style"}},"radius":{…,"sync"}}`; icons
  `{"unicode":"&#xe03b;","type":"divi","weight":"400"}` (HTML entity string, JSON-escaped as `\u0026#xe03b;`);
  links `linkUrl`, `linkTarget:"on"`; images `{"src":…}` / `{"url":…}`; backgrounds
  `{"color":…,"image":{"url":…},"gradient":{"enabled":"on",…}}`; yes/no stays `"on"|"off"`; numbers are strings
  with units except map coordinates (`"lat":34.01` numbers).
- **Bookkeeping per block:** `builderVersion` (string) and `modulePreset` (array, `["default"]`); optional
  `module.meta.adminLabel`. `builderVersion` **changes rendering**: content below a migration's release version
  is migrated at render time (§6.4). A minimal block with no `builderVersion` rendered `et_block_section`
  (legacy block layout); the same content with `"builderVersion":"5.13.1"` rendered `et_flex_section` /
  `et_flex_column_24_24` (FlexboxMigration release `5.0.0-public-alpha.18.2`, `S/Migration/FlexboxMigration.php:99,296-300`).
- **HTML attributes:** after migration, CSS class/id/alt/title are "attribute rows" with random UUIDs:
  `module.decoration.attributes.desktop.value.attributes = [{"id":"<uuid4>","name":"class","value":"pp-lead","adminLabel":"CSS Class"}]`
  (image alt uses `"targetElement":"image"`), and `module.advanced.htmlAttributes` is blanked to `{"class":"","id":""}`.
  Consequence: conversion output is **not deterministic** (UUIDs differ per run; identical modulo UUIDs — verified).

## 6. Parse / serialize round trip and escaping (R3 Q6)

`research/tools/divi5/make_escape_cases.py` builds six pages with identical values encoded six ways; values:

- heading title: `H1 "dq" 'sq' <b>bold</b> a & b &amp; c -- d [br] ]] \ one \\ two A %22 %91 ü € 😀 end`
- text content: `<p>T1 "dq" 'sq' &amp; &copy; & 5 &lt; 6 -- x [et_pb_text]not a shortcode[/et_pb_text] [caption] \ back \\ dbl A %22 ü € 😀</p>\n<p>line2 <a href="https://example.com/?a=1&b=2" onclick="x()">link</a> <span style="color:#ff0000">red</span></p><script>alert(1)</script>`

| variant | encoding / layout |
|---|---|
| v1-php-canonical | `serialize_block_attributes()` escaping, open/close leaves |
| v2-js-serializer | VB escaping (`\\` not `\`) |
| v3-plain-json | plain JSON: raw `<`, `>`, `&`, `--`, `\"` |
| v4-ascii-json | plain JSON with `ü`/surrogate pairs |
| v5-vb-layout | VB escaping + `\n` layout + self-closing leaves + placeholder wrapper |
| v6-php-selfclose-wrapped | WP canonical + self-closing + wrapper |

### 6.1 Parse/serialize (`research/tools/divi5/roundtrip.php`, runs Divi's registered parser)

- All six variants parse to the **same block tree** (names + decoded attrs) — Divi accepts any valid JSON and any
  of these layouts. After `serialize_blocks()`, v1–v4 are byte-identical to each other; v5/v6 equal them apart
  from the wrapper and newlines (whitespace between blocks is kept as freeform chunks).
- Normalizations made by WP's serializer: open/close empty leaves → `/-->`; `\\` → `\`; raw `<>&"--` → `\u…`;
  `\uXXXX` for non-ASCII → raw UTF-8. Output is a fixed point (`serialize(parse(out)) === out`) for all 41 files.
- Only v6 (WP canonical) round-trips byte-exactly. Raw converter output: 35/35 differ **only** by leaf
  self-closing. Migrated fixtures: 27/35 byte-identical; the 8 others still contain converter-style leaves in
  blocks no migration touched (migrations only re-serialize when they changed something).

### 6.2 Store + render, with and without `unfiltered_html`

Admin (and single-site Editor, which also has `unfiltered_html`): stored bytes unchanged for all variants via
WP-CLI and REST; all 24 renders identical. For a user **without** `unfiltered_html` (an Editor with the cap
removed), core kses runs `wp_pre_kses_block_attributes` (`wp-includes/default-filters.php:308`) →
`filter_block_content()` (`wp-includes/blocks.php:2121`), which re-parses, runs `wp_kses` on every string
attribute (`filter_block_kses_value`, `:2192`) and re-serializes; Divi's `wp_insert_post_data` filters run for
everyone (`S/Security/Security.php:78-84`). Results (WP-CLI `--user=` and REST identical):

- v1/v2/v5/v6: structure survives, re-serialized to WP canonical; values changed: `&` → `&amp;` in **every**
  string attribute (plain-text heading, `&` in text, `?a=1&amp;b=2` in the href), `onclick` stripped,
  `<script>…</script>` tags stripped (text `alert(1)` left).
- **v3/v4 (raw `<`/`"` inside the comment JSON): page destroyed** — kses treated the comment content as HTML
  (`"`→`&quot;`, `<`→`&lt;`, block names garbled); heading and text did not render at all.

### 6.3 How values render (admin)

- Heading `title` is output as raw HTML: `<h1 class="et_pb_module_header">H1 "dq" 'sq' <b>bold</b> a & b &amp; c -- d [br] ]] \ one \\ two A %22 %91 ü € 😀 end</h1>`.
  Backslashes, `A`, `%22`, `%91` are literal — **D4's `%22/%91/%93/%92/%5c` escapes mean nothing in D5**
  (the converter decodes them: `%22`→`"`, `%92`/`%5c`→`\`, `%91`/`%93`→`&#91;`/`&#93;`, `Conversion::restoreSpecialChars()` `Conversion.php:2522-2540`).
- Text `content` goes through wpautop and **`do_shortcode`**: `[caption]` vanished and
  `[et_pb_text]not a shortcode[/et_pb_text]` rendered a D4 text module (`et_d4_element`) inside the D5 text.
  `[br]` (unregistered) stayed literal. Literal brackets in content must be written `&#91;`/`&#93;` (what the
  converter does).
- `<script>` and `onclick` render for admins (wrapped in `<p>` by wpautop).

### 6.4 Render-time migrations

Each D5→D5 migration hooks `divi_framework_portability_import_migrated_post_content` (import/conversion),
`wp` → `migrate_fe_content` (which adds a `the_content` filter), `et_builder_render_layout` (priority 8) and
`et_fb_load_raw_post_content` (e.g. `S/Migration/FlexboxMigration.php:119-122,179-199`,
`AttributeMigration.php:68-70`); `Migration::execute()` adds the shared-pipeline finalizer on the same hooks
(`S/Migration/Migration.php:364-383`). So content stored with an old `builderVersion` is upgraded in memory on
every render (not written back). Raw converter output (builderVersion `5.0.0-public-alpha.18.2`, `4.27.9` on
modules) and migrated output both rendered all modules with no PHP errors.

## 7. Converting the D4 fixtures (R3 Q7)

`research/tools/divi5/convert.php` now mirrors the VB conversion route
`POST /divi/v1/content-conversion` (`S/VisualBuilder/REST/ContentConversion/ContentConversionController.php:56-86`):
`initialize_shortcode_framework()` → `do_action('divi_visual_builder_before_d4_conversion')` →
`Conversion::maybeConvertContent($content, true, $post_id)` → `apply_filters('divi_framework_portability_import_migrated_post_content', …)`.
The route does not wrap by itself; the migration filter chain does (`ensure_placeholder_wrapper`, §1.3). Not
mirrored on purpose: the route's `sanitize_callback` `wp_kses_post()` on the D4 input (`:144-146`), which
double-encodes entities (`&amp;` → `&amp;amp;`, finding from the Divi AI spike). `… raw` as a third argument
skips the migrations (bare converter output).

What the migration step changed across the 35 fixtures (block tree shape unchanged in all files):
blurb icon `imageIcon.advanced.width/alignment` → `imageIcon.decoration.sizing.{iconFontSize,width,alignSelf}`
(33/30 blurbs), `imageIcon.innerContent.animation` → `imageIcon.decoration.animation` (40),
`module.decoration.layout.display` added to every module, `htmlAttributes.class/id` + image `alt`/`titleText`
+ icon `title` → attribute rows (§5), contact-field `fullwidth` → `module.decoration.sizing.flexType`, signup /
contact-form focus and border options moved, tabs `inactiveTab` → `tab` background, gallery layout
`block` → `grid`/`flex`; `builderVersion` bumped per migration (`5.0.0-public-alpha.23`, `5.0.0-public-beta.1`, `5.1.1`).

Results (`tests/fixtures/divi5/converted/*.html`, 35 files from `tests/fixtures/valid/*.txt` +
`tests/fixtures/render/*.txt`):
- 35/35 converted, 0 `divi/shortcode-module` fallbacks.
- 35/35 rendered HTTP 200 on the D5 site with `WP_DEBUG_LOG` on; no PHP notices/warnings/fatals from rendering
  (`render_check.sh`; the only log lines were from this spike's own probes and WP-CLI's `usort` deprecation).
  Module order-class counts matched block counts except where modules intentionally render nothing
  (`divi/gallery` with no attachments on this site) or render extra items (tab nav).
- **Conversion loss:** in `forms-tuned-signup` and `forms-heldout`, the three `[et_pb_signup_custom_field …]`
  children stay as a D4 shortcode string in `divi/signup`'s `content.desktop.value`; D5 renders none of them
  (the same D4 shortcode pushed as-is renders all three). D5 does have a `divi/signup-custom-field` block
  (`S/Packages/ModuleLibrary/SignupCustomField/`), so the skill must author those children itself.
- Gallery modules convert but render empty here because the fixture's attachment IDs don't exist on this site.

## Implications for the skill

**Parser (read side)**
- Tokenize with WordPress's block-comment regex (§4.1); accept `/-->` leaves and empty open/close pairs,
  optional `divi/placeholder` wrapper, arbitrary whitespace/newlines between blocks, and any valid JSON escaping.
  Decode with a normal JSON parser — `<`, `&`, `\`, `--` are ordinary JSON escapes.
- Treat mixed corpora as normal: converter output, migrated output and VB output coexist on real sites.
- Don't expect D4 percent escapes in D5; `&#91;`/`&#93;` inside HTML values are real content.

**Serializer (write side)**
- Emit WP canonical form byte-for-byte: `serialize_block_attributes()` escaping (including `\\`→`\u005c`),
  `<!-- wp:divi/x {json} -->` with single spaces, self-closing leaves `<!-- wp:divi/x {json} /-->`, no
  whitespace between blocks, whole page wrapped in `<!-- wp:divi/placeholder -->`…`<!-- /wp:divi/placeholder -->`.
  That form is a fixed point of every PHP path (kses, REST read, migrations), so edits diff cleanly.
- **Never** write raw `<`, `>`, `&`, `"` or `--` inside the JSON — it breaks pages for any author without
  `unfiltered_html` and is re-encoded anyway.
- Put all content in attributes (`innerContent.desktop.value`), never between the tags.
- Set `builderVersion` to the site's Divi version on every block you create (it selects flex vs legacy layout and
  which render-time migrations run) and `modulePreset: ["default"]` unless using a site preset.
- Author the post-migration attribute layout (the converted fixtures), not the raw converter layout.
- Responsive/hover: just add the `tablet`/`phone`/`hover` keys; there are no enable flags.
- Global colors: `$variable({"type":"color","value":{"name":"gcid-…","settings":{}}})$` using IDs from the
  site's `et_global_data`.
- Literal `[`/`]` in HTML text must be `&#91;`/`&#93;`, or WordPress/Divi will run it as a shortcode.
- Attribute-row `id`s are UUIDv4 — generate them; don't expect deterministic conversion output in tests
  (compare modulo UUIDs).
- For round-trip edits, compare trees, not bytes, unless the input was already canonical.

**publish.py**
- `POST /wp/v2/pages` with `content` works and stores bytes as sent for users with `unfiltered_html`
  (Administrators; Editors on single site). Expect `&`→`&amp;` in attributes and stripped scripts/handlers for
  users without it.
- **`meta._et_pb_use_builder` over REST is ignored on Divi 5.13.1.** Options, in order of preference:
  (a) WP-CLI/SSH `wp post meta update <id> _et_pb_use_builder on --user=<admin>` (also set
  `_et_pb_use_divi_5 on`); (b) a one-file mu-plugin on the client site that registers the meta on `init`
  (verified: REST then stores it); (c) document the fallback — without it the page renders fully styled but
  inside the theme's title+sidebar page template. Always read back `meta._et_pb_use_builder` after a push and
  warn when it is empty.
- Divi's own REST routes (sync-to-server, content-conversion, set-layout) are not usable with Application
  Passwords (`invalid_nonce`).
- After a REST update, CSS regenerates on the next view (`.stale` markers) — no purge needed. With WP-CLI always
  pass `--user=<admin>` or stale CSS is served.
- A GET of `content.raw` returns WP-canonical re-serialization, not stored bytes; diff against a canonicalized
  copy.
- Pushing D4 shortcode to a D5 site "works" (legacy render) but is not D5 content; don't rely on it.

## Files

- `research/tools/divi5/convert.php` — D4 → D5 via Divi's converter + migration filter (mirrors the VB route).
- `research/tools/divi5/roundtrip.php` — parse/serialize round-trip, tree equality, fixed-point check.
- `research/tools/divi5/render_check.sh` — publish, curl, count modules, list et-cache, new debug.log lines, delete.
- `research/tools/divi5/make_escape_cases.py` — the six escaping variants.
- `research/tools/divi5/push_probe.py` — WP-CLI/REST × admin/editor push, stored/REST/rendered comparison.
- `tests/fixtures/divi5/converted/*.html` — 35 converted + migrated fixtures.

## Addendum (orchestrator, 2026-09-28): setting `_et_pb_use_builder` over REST with a batch

The key is registered for REST only once Divi's D4 shortcode framework loads, which in a REST request happens
lazily when `content.rendered` renders a **D4 shortcode**. D5 block content never loads it. `/batch/v1` runs
several REST requests in **one PHP process**, so the registration survives into later requests of the same batch.
`wp/v2/pages` allows batching (`allow_batch v1`, `class-wp-rest-posts-controller.php:48`).

Verified live on divi-5-test.local (WP 7.1.2, Divi 5.13.1), Application Password (admin):
1. `POST /wp/v2/pages {title, status, content:"[et_pb_section][/et_pb_section]"}` → 201 (response already lists
   the meta keys because the stub rendered, but this request's meta step ran before that).
2. `POST /batch/v1 {"requests":[{"method":"POST","path":"/wp/v2/pages/ID","body":{"title":…}},
   {"method":"POST","path":"/wp/v2/pages/ID","body":{"content":<D5 blocks>,"meta":{"_et_pb_use_builder":"on"}}}]}`
   → 207; responses 200/200; the second echoes `_et_pb_use_builder: "on"`.
3. `wp post meta get ID _et_pb_use_builder` → `on`. Front end: `et_pb_pagebuilder_layout et_no_sidebar`, no
   `entry-title`, no `#sidebar`, no `et_d4_element`.

Control: the same batch **without** a D4 stub in the page (first request re-renders D5 content) stores nothing.
Echo probe (Task 10 fix round, 2026-09-28): stub page + the same batch with **no `meta`** in the second item →
both responses show `_et_pb_use_builder: ""` and `wp post meta get` is empty, so the second response's echo reads
the stored value (no registered default of `on`) and `"on"` there proves the write.
Cost: one extra revision holding the stub. Only needed when the meta isn't already `on` (new pages; pages
never opened in Divi). For a live page lacking the meta, prefer the stub-in-batch only on drafts/copies.
