# Divi 4 Render Engine and a Local Preview Renderer

Research spike, 2026-09-24. Divi 4.27.9 on `divi-test.local` (LocalWP, WP 7.1.2, PHP 8.2).
Source paths are relative to `wp-content/themes/Divi/`. `EL` = `includes/builder/class-et-builder-element.php`.

## TL;DR

- **Recommendation: a headless render script running on a local "mirror" WordPress with the same Divi version.** It is options 4a and 4b combined: 4a supplies the runtime, and 4b turns a shortcode plus a client settings bundle into a standalone HTML file. The prototype in `research/render-prototype/` works today.
- **Verified by running it:** the prototype renders `layout.shortcode` (8 sections, 45 modules) in about 0.4 s. It needs no post, no HTTP request and no browser. It writes nothing to the database or to `et-cache`.
  - The builder markup inside `.et-l` is **byte-identical** to the live page 11.
  - The builder and customizer CSS match the live page exactly: 2,099 of 2,099 declarations.
  - In Chrome, all 302 builder elements have **identical geometry and computed styles** (same signature hash).
  - A headless-Chrome pixel diff differs on 0.044% of pixels (desktop) and 0.016% (phone). All of it is JS animation caught mid-flight: the number counters and the fading slider slide.
- **Also verified: the renderer applies a client settings bundle in memory.** It covers customizer colors and fonts, global colors, global presets and Additional CSS. The mirror DB is left unchanged (option hashes checked before and after).
- **A pure JS/Python re-implementation is not realistic.** The render engine is about 185k lines of PHP. There are 245 `set_style` and 184 `generate_styles` call sites, plus 29 attribute migrations. The CSS output depends on hundreds of option defaults.

---

## 1. Render pipeline (post_content to HTML/CSS)

### 1.1 Boot: modules are registered on the `wp` hook, lazily

| Step | Where |
|---|---|
| Builder framework is loaded when `et_builder_should_load_framework()`, which is always true in WP-CLI | `includes/builder/core.php:115-160` (CLI short-circuit at `:126`) |
| Module classes are instantiated on the `et_builder_modules_load_hook` hook. This is `wp` on the front end and `wp_loaded` in admin. **In a bare `wp eval` the `wp` action never fires, so no Divi shortcodes exist** (verified: `the_content` returned the raw `[et_pb_section…]` text wrapped in `<p>`). | `includes/builder/framework.php:903,927-928` |
| `ET_Builder_Module_Shortcode_Manager::init()` registers every module slug | `includes/builder/framework.php:873-876`, `class-et-builder-module-shortcode-manager.php:48-96` |
| Lazy mode (the default): every slug gets a `__return_empty_string` placeholder. The real class is instantiated on first use through `pre_do_shortcode_tag`. If `et_builder_should_load_all_module_data` is true, everything is registered up front. | `…shortcode-manager.php:550-558, 654-737` |
| Each module constructor calls `add_shortcode($slug, [$this,'_render'])` | `EL:1182-1201` |
| The first module constructed also sets up the style manager and hooks `set_advanced_styles` to `wp_footer`:19 | `EL:894-911` |

### 1.2 `the_content` filter chain for a builder page

| Priority | Callback | Where |
|---|---|---|
| 0 | `et_pb_the_content_prep_code_module_for_wpautop` | `includes/builder/functions.php:4921` |
| 10 | `et_pb_fix_builder_shortcodes` | `functions.php:4905` |
| 10 | `et_builder_add_builder_content_wrapper` adds `<div class="et-l et-l--post"><div class="et_builder_inner_content et_pb_gutters3">`. It **requires `is_singular()` and `_et_pb_use_builder=on`**. | `core.php:6688-6723`, wrapper markup `core.php:6585` |
| 11 | WP core `do_shortcode` runs each `[et_pb_*]` through `ET_Builder_Element::_render()` | `wp-includes/default-filters.php:209` |
| 1500 | `et_pb_content_main_query` | `framework.php:1148` |
| 9999 | `ET_Builder_Element::reset_element_indexes` (only on the main query and the outermost `the_content`) | `EL:868, 2419-2465` |

`et_builder_render_layout` is a second filter with the same wrapper and index reset (`core.php:6724`, `EL:869`). The Theme Builder uses it for header, body and footer layouts.

### 1.3 `ET_Builder_Element::_render()` (`EL:2841`)

1. `self::set_order_class($render_slug)` (`EL:2860`, impl `EL:20526`) increments a **per-slug counter**. `get_module_order_class()` (`EL:20486`) produces `{slug}_{n}`, e.g. `et_pb_text_0`, plus a Theme Builder or WP-template suffix. Counters live in `self::$_indices`, keyed by TB layout type (`EL:2373-2410`). Children of a module use a separate "inner" counter. So **order classes depend only on document order within the render**, which makes them deterministic for a given shortcode string.
2. `_maybe_add_global_presets_settings()` (`EL:2864, 4266-4298`) runs `array_merge($preset_settings, $attrs)`. The **preset is the base, and the module's own attrs override it**. A module with no `_module_preset` gets that module type's *default* preset (`global-presets/Settings.php:366`).
3. `apply_filters('et_pb_module_shortcode_attributes', …)` runs the settings migrations (`EL:2929`; there are 29 migration classes in `module/settings/migration/`).
4. `process_global_colors()` (`EL:3140, 13462`) replaces `gcid-*` values using `et_builder_get_all_global_colors(true)` (`core.php:7413`).
5. `process_additional_options()` (`EL:3143, 13513`) turns the "advanced" option groups into CSS: background, borders, button, margin/padding, filters, fonts, text, box-shadow, sizing, position, transform, transitions and so on. Each one calls `self::set_style()`.
6. `$this->render($attrs, $content, $render_slug)` is the module's own method (`EL:3441`). For example, `module/Text.php:515` calls `generate_styles()` (`EL:20112`). That method drives the `ET_Builder_Module_Helper_*` classes (`module/helpers/*`: ResponsiveOptions, HoverOptions, StickyOptions, Font, Background…) to emit desktop, tablet, phone, hover and sticky variants.
7. `et_module_process_display_conditions` and `et_module_shortcode_output` filters run (`EL:3452, 3471`).

`set_style()` (`EL:20049`) expands `%%order_class%%` into selectors and passes them to `_set_style()` (`EL:20354`). That buffers them into the static `self::$styles[$key][$media_query]`, where the key is `'post'`, or the layout ID for TB layouts (`EL:19709`). `get_style()` (`EL:19768`) serialises them, largest media query first.

### 1.4 Where the CSS ends up

| Output | Produced by | Notes |
|---|---|---|
| **Module design CSS** (`self::$styles`) | `set_advanced_styles()` on `wp_footer`:19 (`EL:1712-1745`) hands it to an `ET_Core_PageResource` (`core/components/PageResource.php`) | `setup_advanced_styles_manager()` (`EL:1615-1705`) decides the location. Normally it goes into the **`et-core-unified-<id>.min.css`** file in `wp-content/et-cache/<id>/`, which also holds the customizer CSS (priority 30) and page custom CSS. The file is written in the footer **on the first view**, while that first view gets the CSS inline in the footer (`filter_page_resource_data`, `EL:1784`). It is forced inline in the footer for previews, when `_et_pb_static_css_file=off` or `et_pb_static_css_file=off`, in safe mode, or for password-protected posts (`EL:1626`). |
| Critical CSS split (`divi_critical_css=on`) | `includes/builder/feature/CriticalCSS.php:93-107` | Styles of above-the-fold sections go to `et-core-unified-<id>.min.css`. The rest goes to `et-core-unified-deferred-<id>.min.css`, which is loaded with `rel=preload onload=` (seen on page 11). |
| Customizer / theme-options CSS | `et_divi_add_customizer_css()` on `wp` (`functions.php:5328, 7279`) | Goes into the unified resource, or into `et-cache/global/et-divi-customizer-global.min.css` when not unified. |
| Theme base CSS | `et_divi_replace_parent_stylesheet()` (`functions.php:~400-418`) and `et_divi_print_stylesheet()` (`:~422-462`) | With Dynamic CSS on, `style.min.css` (26 KB) is **printed inline** plus the per-page dynamic files. With Dynamic CSS off, the full `style-static.min.css` (825 KB) is used. |
| **Dynamic assets** (`divi_dynamic_css=on`) | `feature/dynamic-assets/class-dynamic-assets.php`: hooks `:448-462`, `initial_setup` `:468`, generate `:1028`, file write `:877-915` | Scans post content for used shortcodes and attributes (cached in post meta `_et_dynamic_cached_shortcodes` / `_attributes`). It concatenates the matching snippets from `feature/dynamic-assets/assets/css/*` (256 files) into `et-cache/<id>/et-divi-dynamic-<id>[-critical\|-late].css`. "Late" detection in `wp_footer` (`:1098`) catches modules that are only found at render time. **This is why a first view after a content change can look unstyled:** the dynamic and deferred files are generated during that request and some are loaded asynchronously. |
| Builder Google Fonts | `et_builder_enqueue_font()` / `et_builder_print_font()` on `wp_footer` (`functions.php:3461, 3636, 3756`) | On later views `et_builder_preprint_font()` (`:3786, 3842`) enqueues one cached combined URL from post meta `et_enqueued_post_fonts`. It is inlined when `google_fonts_inline` is on. |
| Page settings CSS | `et_pb_get_page_custom_css()` (`functions.php:3850`) | Built from post meta: `_et_pb_custom_css`, light/dark text colors, content background, and so on. |

---

## 2. Site-level inputs a render depends on

To reproduce a client's look you need **the same Divi version**, plus the following:

| Input | Storage | Used by |
|---|---|---|
| ePanel theme options (performance flags, `divi_color_palette`, `divi_custom_css`, sidebar default…) | option **`et_divi`** (single serialized array; `et_get_option()` in `epanel/custom_functions.php:208`) | Everything, via `et_get_option` |
| **Theme Customizer** (accent color, body/heading fonts and sizes, header and footer styles, button defaults, content width, gutter…) | also keys in **`et_divi`** | Customizer CSS (`functions.php:5328`) and `ET_Global_Settings` module defaults (`class-et-global-settings.php:32, 663-690`) |
| **Global colors** | `et_divi['et_global_colors']`, plus 4 customizer-derived colors | `core.php:7413`, `EL:13462` |
| **Global presets** | option **`et_divi_builder_global_presets_ng`** (nested **stdClass objects**) | `global-presets/Settings.php:84-90, 366` |
| Additional CSS | `custom_css` post (`theme_mods_<stylesheet>['custom_css_post_id']`) | `wp_get_custom_css` filter (`epanel/custom_functions.php:~140-190`) |
| Theme mods (logo, menus) | `theme_mods_Divi` or `theme_mods_<child>` | Header and footer chrome only |
| Theme Builder templates (global header, footer or body) | posts `et_template`, `et_header_layout`, `et_body_layout`, `et_footer_layout` | `frontend-builder/theme-builder/frontend.php` |
| Child theme `style.css` / `functions.php`, and plugins that add CSS or shortcodes | files | Anything |
| Page-level meta | `_et_pb_page_layout`, `_et_pb_custom_css`, `_et_pb_*_color`, `_et_pb_gutter_width` | Body class and page CSS |
| Media | uploads (or remote URLs) | Images |

`ET_Global_Settings` is not stored separately. It computes module defaults from `et_divi` customizer keys at `wp`:9 (`class-et-global-settings.php:764`).

**Can Divi's own portability exports cover this?** Mostly, yes:
- **"Customizer" export** (`et_divi_mods`, `functions.php:8681`) exports **all `et_divi` keys except ePanel ones, plus `wp_custom_css`** (`core/components/Portability.php:343-349`, filtered by `apply_query` at `:1786`). That includes `et_global_colors`.
- **"Theme Options" export** (`epanel`, `epanel/core_functions.php:1174-1188`) exports only ePanel option IDs.
- **Global presets:** there is no standalone "presets" export in Divi 4. A **Theme Builder export includes all global presets** (`frontend-builder/theme-builder/api.php:397-404`). A layout export includes only the presets it uses (`Portability.php:383-401`).
- Theme Builder export and import also carries the TB templates.

So Customizer + Theme Options + Theme Builder exports reproduce the look. They are manual, UI-driven and admin-only, though. Reading the three options directly (see `export-settings.php`) is simpler to automate.

---

## 3. Rendering headlessly: what works

| Approach | Result (run on divi-test.local) |
|---|---|
| `wp eval`: fake `$post` + `apply_filters('the_content', …)` | **Fails.** No modules are registered because `wp` never fired, so the output is raw shortcode text in `<p>`. `get_style()` returns an empty string. Even with modules forced, `is_singular()` is false, so the `.et-l` wrapper and the page resources are skipped. |
| **Simulated front-end request inside WP-CLI** (`render.php`) | **Works.** Prime a fake `WP_Post` and its meta in the object cache. Feed it to the main query through `posts_pre_query`. Call `wp(['page_id'=>FAKE])`, which fires `wp` and boots Divi. Then include `get_page_template()` inside an output buffer. The result is full `wp_head` + `the_content` + `wp_footer` HTML, identical to a real hit. |
| Divi preview endpoint: `POST /?et_pb_preview=true&et_pb_preview_nonce=…` with `shortcode=` (`includes/builder/template-preview.php`, routed by `functions.php:10088-10101`) | **Works over HTTP** with a logged-in `edit_posts` cookie and nonce. It turns off dynamic assets, critical CSS and the feature cache (`functions.php:10107-10127`) and outputs builder CSS inline. The builder CSS matched ours exactly (2,080 decls, 0 diff). It uses a bare template with no site header or footer, in a `.container` wrapper, so it is not page-faithful. |
| VB AJAX: `admin-ajax.php?action=et_fb_ajax_render_shortcode` (`functions.php:2189-2234`) | **Works**, but it takes the builder's *object tree* (not a shortcode string). It returns a JSON fragment: module HTML plus a `<style class="et-builder-advanced-style">` of that module's CSS. Tested: `{"success":true,"data":"<div class=\"et_pb_module et_pb_text et_pb_text_0 …\">…</div><style …>.et_pb_text_0 { font-size: 31px; background-color: #ff0000; }</style>"}`. It is useful for per-module previews only: no theme CSS, fonts or page context. |

Things that **must** be true for a faithful render (all handled in `render.php`):
- `is_singular()` must be true and the post meta must include `_et_pb_use_builder=on`. Otherwise there is no `.et-l` wrapper, no unified styles and no dynamic assets.
- The `wp` action has to fire.
- Output has to go through `wp_head` and `wp_footer`, because the customizer CSS, builder CSS and fonts are all emitted there.
- The builder CSS must be moved to `<head>`. When forced inline it lands in the footer, and modules then *transition* from the base theme styles (Divi sets `transition: all 300ms`). **This is a real bug we hit:** in a background Chrome tab the transitions froze and a button rendered at 20px instead of 14px. Moving the style block to the end of `<head>` matches production ordering and fixed it.

---

## 4. Options evaluated

| Option | Fidelity | Effort | Verdict |
|---|---|---|---|
| **a. Local mirror site + push drafts + screenshot** | Highest: the real site stack, including TB header and footer, child theme and plugins, if mirrored | Medium. Each client needs a mirror (LocalWP or Docker), a settings sync, and a draft-push path. Previews are slow (HTTP + cache warm-up + screenshot) and create posts. | Good as the runtime. Clumsy as the preview loop on its own. |
| **b. Headless render script** (on a mirror runtime) | **Verified identical** to the live render for builder content (see §5). Header and footer come from the mirror's theme options and menus. | **Low.** It works now: ~350 lines of PHP, no DB writes, 0.4 s per render. | **Recommended.** |
| c. Pure JS/Python re-implementation | Low and decaying. You would need to replicate ~185k lines of builder PHP. `EL` alone is 24.3k lines, `module/` is 81k lines across 191 files and 65 modules, and helpers are 10.5k. It has 245 `set_style` and 184 `generate_styles` call sites, 77 responsive-CSS generators, 29 attribute migrations, preset and global-color merging, and customizer-derived defaults. The theme CSS (825 KB static) could be reused, but the module CSS generation could not. The VB's own JS renderer (`frontend-builder/build/bundle.js`, 4.2 MB minified) depends on server-provided module definitions and is not extractable. | Months of work, and it breaks on every Divi release | Not feasible |
| d. Divi's own endpoints (`et_pb_preview`, `et_fb_ajax_render_shortcode`) | The builder CSS is exact, but there is no page chrome, and a login and nonce are needed | Low, over HTTP | A fallback when you can't run PHP on the mirror (e.g. a Docker mirror reached only over HTTP). **Never point these at a client's live site.** |

### How to sync client settings (for 4a/4b)

A **settings bundle** is a JSON file with these contents:
- `et_divi`, with secrets, SEO and integration code stripped.
- `et_divi_builder_global_presets_ng`.
- `theme_mods_<stylesheet>`.
- `et_pb_builder_options`.
- `custom_css`.
- Meta: Divi version, child theme, active plugins, and the Theme Builder template count.

`render-prototype/export-settings.php` produces it read-only on any WP install. The Post Pusher MCP could implement the same three `get_option` reads over its existing connection. `render.php settings=bundle.json` applies the bundle **in memory** through `pre_option_*` filters. Writes to those options are vetoed, and the presets singleton is reset. The mirror's DB is not touched (verified by option hashes before and after).

What the bundle does **not** cover: Theme Builder templates (use Divi's TB export/import on the mirror, once), child-theme files, and plugin CSS. The Divi version must match. `meta.divi_version` in the bundle lets the tool warn about a mismatch.

---

## 5. Prototype: `research/render-prototype/`

| File | Purpose |
|---|---|
| `render.php` | The headless renderer (WP-CLI `eval-file`) |
| `run.sh` | Wrapper: `WP="wp --path=/mirror" ./run.sh page.shortcode out/page.html [settings=client.json] [meta=page-meta.json] [embed-images] [no-js]` |
| `export-settings.php` | Read-only settings-bundle exporter (run on the client or source site) |
| `compare.sh` | Headless-Chrome screenshots (1440 px and 390 px) of a live URL and a preview file, plus a Pillow pixel diff |
| `sample-layout.shortcode` | Page 11's shortcode |
| `sample-settings-test.shortcode` | Probe for presets, global colors and custom CSS |
| `out/` | Rendered previews, screenshots and diffs |

**How it works:**
1. It primes a fake page (ID 990000001) and its meta into the object cache, with `_et_pb_static_css_file=off` so builder CSS is forced inline. Meta writes for that ID are short-circuited.
2. It adds the same filters Divi's own preview uses: load all modules, no critical CSS, no dynamic CSS or JS, no feature cache. The full `style-static.min.css` is used, so nothing is deferred.
3. `posts_pre_query` returns the fake post, `wp()` runs, `template_redirect` runs without canonical redirects, and `page.php` is included under output buffering.
4. It post-processes the HTML:
   - Local `<link rel=stylesheet|preload as=style>` and `<script src>` tags are inlined from disk, with CSS `url()` values made absolute.
   - The builder `<style>` and the builder Google Fonts `<link>` are moved into `<head>`.
   - `embed-images` optionally turns local uploads into `data:` URIs.

Run on the local site:

```
WP=/path/to/wp.sh ./run.sh sample-layout.shortcode out/preview.html
Success: Wrote …/out/preview.html (1,848.7 KB). sections=8 modules=45 builder-css=48662 B, css inlined=1 remote=2, js inlined=12 remote=0
```

The file is ~1.8 MB, mostly the 825 KB static CSS and inlined jQuery and Divi JS. Google Fonts stay as remote links, and images remain URLs unless `embed-images` is passed.

### Fidelity checks (all run, not inferred)

| Check | Result |
|---|---|
| HTML inside `.et-l` vs live page 11 | **Byte-identical** (31,779 chars; the class sequence of all 310 elements is equal) |
| Body classes | Identical except `page-id-*` |
| Builder + customizer CSS declarations vs live `et-core-unified-11` + `deferred` + inline critical | **2,099 / 2,099, zero diff** |
| Chrome: geometry and computed styles of all 302 `.et-l [class*=et_pb_]` elements (x, y, w, h, color, bg, font, size, padding, margin) | **Identical signature hash**, doc height 7,655 px in both, both tabs in the same visibility state |
| Headless Chrome pixel diff, 1440×7655 | 0.044% of pixels differ, in two bands: the number-counter digits (y≈3090) and the testimonial slider's fade-in opacity (y≈5100). Both are animation timing, not rendering. |
| Headless Chrome pixel diff, 390×15310 | 0.016% of pixels differ, number counters only |
| Settings bundle (accent `#ff00aa`, Roboto/Playfair fonts, global color `gcid-renderprobe`, default `et_pb_text` preset, Additional CSS) | All applied: customizer CSS has 12× `#ff00aa`, the fonts are in the Google Fonts URL, `gcid-` resolved to `#123456`, the preset produced `.et_pb_text_0,.et_pb_text_1{font-size:41px;background-color:#fef3c7}`, and the custom CSS is present. The DB options are unchanged. |
| Page meta (`meta=`) | `_et_pb_custom_css` is emitted |
| Side effects | 0 `wp_posts` or `wp_postmeta` rows for the fake ID, no `et-cache/990000001/`, and `et-cache/global` is untouched |

**Known gaps and caveats:**
- **Theme Builder:** not tested. The test site has no TB templates. The TB frontend should work unchanged because it hooks the same template path, but this is unverified.
- **Dynamic content** (`@ET-DC@…`, post title, featured image): it resolves against the fake post (title from `title=`). Anything that needs real post relationships will be empty.
- **Scripted modules:** JS-driven modules (counters, sliders, animations) need JS. It is inlined by default, but screenshots taken mid-animation will differ.
- **Remote resources:** a preview needs network access for Google Fonts and remote images.
- **Plugins and child theme:** these must also exist on the mirror when the client uses them.
- **Parallel runs:** the fake ID is constant, so object cache only, per process; parallel runs are safe.
- **Test sessions:** testing the preview and AJAX endpoints created two admin login sessions on the throwaway site. One was destroyed afterwards.

---

## 6. Recommendation

1. **Standardise on a mirror runtime**: LocalWP or Docker with WordPress plus the **exact Divi version** of each client, pinned. One mirror per Divi version is usually enough. Clients with a child theme, TB templates or style-affecting plugins need them installed too. A per-client mirror is only needed for those.
2. **Pull a settings bundle from the client** with the three `get_option` reads plus `wp_get_custom_css` (as in `export-settings.php`) through the Post Pusher connection. Cache it per client and refresh it before previews.
3. **Preview with `render.php`**: shortcode + bundle + page meta produces a standalone HTML file, then a headless-Chrome screenshot (`compare.sh` shows how). No drafts are created anywhere and the client site is never touched.
4. **Warm the live cache after the push.** Request the page once so `et-cache/<id>/` is regenerated; the unstyled-first-view effect comes from the deferred dynamic and critical files described in §1.4. Optionally compare the live screenshot against the preview with `compare.sh` as a post-push check.
5. Don't build a non-WordPress re-implementation. Use Divi's preview and AJAX endpoints only on the mirror, as a fallback when PHP can't be executed there directly.
