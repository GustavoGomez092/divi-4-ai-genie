# R5 spike: does WordPress Playground run Divi 5?

Run on 2026-09-28 (macOS arm64, Node 24.1.0, Playground CLI 3.1.55, WordPress 7.1.2, Divi 5.13.1).

The question: can the `--exact` preview (`Skill/divi-page-builder/scripts/preview/`, WordPress Playground plus the real theme; see `research/playground-spike.md`) render **Divi 5** pages faithfully, and what has to change to support Divi 4 and Divi 5 side by side?

- Prototype: `research/divi5/playground-prototype/`. It is a copy of the shipped preview. Every Divi 5 change is in `mu-plugin/pp-preview.php`.
- Comparison tool: `compare_d5.py`.

## TL;DR: GO

- **Divi 5.13.1 activates and renders Divi 5 block content inside Playground (verified).**
  - Runs on PHP 8.2.33 and 8.3.33 (wasm) with SQLite.
  - No fatals, warnings, notices or deprecations with WP_DEBUG on, and `debug.log` stays clean.
  - The blueprint (`activateTheme Divi`), the mounts and `preview.mjs` are **unchanged**.
  - Divi 5 content goes through **the same injection path** as Divi 4: the fake page's `post_content` holds the block markup, and Divi 5 renders it from `the_content`.
- **The unmodified Divi 4 mu-plugin already gives exact builder markup and CSS**, but it has three Divi 5 bugs. The prototype fixes all three, and **none of the fixes changes Divi 4 output**:
  1. **Stale CSS in `serve` mode.** Divi 5 ignores `_et_pb_static_css_file` and always caches per-post CSS in `et-cache/<id>/`. Every preview shares one fake ID, so page b, or an edited page, was served page a's CSS.
  2. **Broken icon fonts in the self-contained file.** Divi 5 references the icon fonts by protocol-relative URL inside inline `<style>` blocks, which the `inline=1` step didn't embed.
  3. **An extra font request.** Divi 5's cold render requests a variable Open Sans that a warm live page doesn't. This re-wrapped a heading at 390 px.
- **Fidelity after the fixes (verified).** Three pages converted with Divi's own D4→D5 converter, rendered in Playground and on the real Divi 5 site (`divi-5-test.local`):
  - Builder markup: the tag/class sequence is identical on all three. `.et-l` is byte-identical on 2 of the 3; the third differs only in an audio element's post ID.
  - Builder CSS: **2,480/2,480, 490/490 and 161/161** declarations identical.
  - Pixel diff of the builder area against a frozen warm live snapshot:
    - 390 px: **0.000 %** on all three pages.
    - 1440 px: **0.0007–0.002 %**, all of it the site's header search icon overlapping the top of the builder area. That is site content, not rendering.
- **Timings (verified):**

  | Run | Time |
  |---|---|
  | Warm one-shot `render` | **4.6–5.2 s** |
  | `serve` re-render | **0.85–0.94 s**, up to 1.2 s on larger pages |
  | First boot of a new (WP, Divi 5) site | 8.5 s |
  | Fully cold (empty npm and WP caches, Divi already cached) | **29.3 s** |

  These match Divi 4. Peak PHP memory is 96–129 MB of Playground's 256 MB.
- **Not verified:**
  - Downloading Divi 5 from Elegant Themes. The API was timing out today and was deliberately not called; the cache was seeded from the LocalWP copy. (Checked in Task 14, §6: `divi_5=on` returns the Divi 5 line and a 5.13.1 download has the Divi 4 zip layout.)
  - The Visual Builder. The front end doesn't need it.
- **Hazard created by this spike (resolved in Task 14, see §6).** With `Divi-5.13.1` in the user cache, "newest cached" resolved to **5.13.1** in `preview.mjs`, `preview.py`, `divi_render/assets.py` and `tests/test_render_fidelity.py` / `test_render_fallbacks.py`, so a Divi 4 run without `--divi` or `--tokens` picked Divi 5. Version resolution is now major-aware everywhere (shortcode → newest cached 4.x, blocks → newest cached 5.x).

---

## 1. Setup

- **Divi 5 cache.** `~/.cache/divi-page-builder/divi/Divi-5.13.1/Divi` was rsynced from `~/Local Sites/divi-5-test/.../themes/Divi`: 132 MB, 3,360 files. `.DS_Store` was excluded.
  - Both `fetch-divi.mjs` and `fetch_divi.py` treat a version as cached when `Divi-<v>/Divi/style.css` exists. The zip is optional: neither Divi 4 cache dir has one either.
  - No zip was created. A `zip -9` of the unpacked theme is **34.6 MB**, versus 17.6 MB for 4.27.9. That is the expected download size (an estimate).
- **Divi 5 content.** Three Divi 4 fixtures were converted with `research/tools/divi5/convert.php`, which calls Divi's `Conversion::maybeConvertContent`:

  | Fixture | Divi 4 size | Divi 5 size | Sections | Modules |
  |---|---|---|---|---|
  | `tests/fixtures/valid/divi-ai-layout.txt` | 102 KB | 123 KB | 8 | heading, blurb, button, text, accordion, slider, image, number-counter, divider, cta |
  | `tests/fixtures/render/heldout-inscope.txt` | 10.8 KB | 20.9 KB | 5 | incl. fullwidth-header, toggle |
  | `tests/fixtures/render/content-heldout.txt` | 5.1 KB | 10.9 KB | 2 | audio, video, gallery, code, fullwidth-code/image, icon, social-follow, team-member, testimonial |

- **Reference pages.** One LocalWP page per fixture: "R5 divi-ai-layout" (ID 10), "R5 heldout-inscope" (ID 11) and "R5 content-heldout" (ID 12).
  - Content: `<!-- wp:divi/placeholder -->…<!-- /wp:divi/placeholder -->`, the wrapper the Visual Builder saves.
  - Meta, as `SyncToServerController` sets it: `_et_pb_use_builder=on`, `_et_pb_use_divi_5=on`, `_et_pb_page_layout=et_no_sidebar`, `_et_pb_built_for_post_type=page`.
  - The stored `post_content` round-tripped byte-identical through `wp post create`, so kses didn't alter the block JSON.
  - **All three pages and their et-cache dirs were deleted afterwards.**

## 2. Q1: activation, what breaks, what the mu-plugin needs

| Area | Result (verified) |
|---|---|
| Activation (`activateTheme Divi` blueprint step) | Works. `X-PP-Env: php=8.2.33 wp=7.1.2 divi=5.13.1`. |
| PHP 8.2 / 8.3 | Both render identically (490/490 declarations on heldout-inscope with PHP 8.3). No warnings, notices or deprecations in the HTML or `debug.log`. |
| Onboarding / Divi 5 migration screens | Nothing on the front end. The existing unhook of `et_onboarding_trigger_redirect` covers the `after_switch_theme` redirect. `d5-readiness` and migration are admin-only, and `wp-admin/*` redirects to the login page as usual. |
| REST / VB bootstrapping | The `divi/v1` REST namespace loads. The Visual Builder wasn't exercised: it isn't needed for a front-end preview. |
| Memory / time | Peak 96–129 MB, against `memory_limit=256M`. Divi 4.27.9 on the same layout: 102 MB. PHP time 1.0–1.8 s per render. |
| Theme mount size | 132 MB and 3,360 files, mounted rather than copied. Warm boot is 3.0–3.7 s, versus 2.8–3.4 s for Divi 4. |
| Playground quirks from the Divi 4 spike | Unchanged. The first request after boot still gets a 302 (harmless). The pinned CLI and `preferredVersions.php` are still needed. |
| Content injection | Same path. The fake `WP_Post`'s `post_content` is the block markup and Divi 5 renders it from `the_content`. The `divi/placeholder` wrapper is optional: wrapped and unwrapped renders are identical. `_et_pb_use_divi_5` is not needed for rendering. |

### Where Divi 5 puts its CSS (answer: in files, and that works in Playground)

- **Static CSS files are always on in Divi 5.** `core/functions.php:2448` `et_core_is_static_css_enabled()` returns `true` for every front-end request outside the Visual Builder or preview ("temporarily … force Static CSS to be on"). The `_et_pb_static_css_file=off` meta that the Divi 4 plugin relies on is therefore ignored.
- **Files written per post** (all work in Playground; they land in the host-mounted site dir):
  - `wp-content/et-cache/<id>/et-core-unified-<id>.min.css`
  - `et-core-unified-deferred-<id>.min.css` (critical CSS is on by default)
  - `et-divi-dynamic-<id>.css`
  - `et-divi-dynamic-<id>-critical.css`
- **First request:** the builder CSS is printed inline as `et-core-unified-<id>-cached-inline-styles[-2]` and `…-deferred-…-2` in the footer, and the files are written.
- **Later requests:** critical CSS goes inline in `<head>` (`et-critical-inline-css`), and the deferred CSS and Dynamic CSS become `<link rel=preload>` to the files.
- **Divi's preview-mode filters were renamed** in Divi 5 (`divi_frontend_assets_dynamic_assets_utils_*`, `divi_frontend_assets_critical_css_should_generate_critical_css`). The Divi 4 names in the plugin are inert on Divi 5, so Divi 5 runs its **live** Dynamic CSS pipeline. That turned out to be exactly what fidelity needs (see the `d5=preview` row below).

### mu-plugin changes (prototype `mu-plugin/pp-preview.php`)

All of these are inert or skipped on Divi 4.

1. **Purge `et-cache/<fake id>/` at the start of every preview request** (`muplugins_loaded`).
   - Without it, `StaticCSS::setup_styles_manager()` finds the existing file and reuses it.
   - Measured in `serve` with the unmodified plugin: page b's CSS had **334 extra declarations** from page a and was **missing 169 of its own**. An edited page shares the same fake ID and file, so it is affected the same way (inferred). These counts use the first, all-`<style>` metric.
   - The one-shot `render` hid this, because every boot re-activates the theme and Divi clears its cache.
   - With the purge: a → b → a → b → a → edit a → all identical to live (490/490, 161/161, 2,480/2,480).
2. **Embed icon fonts referenced by absolute or protocol-relative URL inside `<style>` blocks** (`inline=1`).
   - Divi 5's Dynamic CSS declares ETmodules and Font Awesome as `url(//127.0.0.1:9400/wp-content/themes/Divi/core/admin/fonts/…)` inside `divi-dynamic-critical-inline-(css)`.
   - Opened from disk, that resolves to `file://127.0.0.1:9400/…`, so blurb icons fell back to text: the icon box went from 48 to 54 px wide and headings re-wrapped.
   - The new pass uses a `strpos` walk, not a single `/<style>(.*?)<\/style>/s`. That regex hit `pcre.backtrack_limit` on megabyte-sized inlined CSS, and `preg_replace_callback()` returned NULL: an **empty page**, seen once.
3. **Drop "Open Sans" from builder Google Fonts URLs when the theme already enqueues Open Sans** (`style_loader_src`, gated on `ET_BUILDER_5_DIR`).
   - A warm live page prints builder fonts from post meta (`et_builder_preprint_font`), and Divi 5 filters Open Sans out there (`includes/builder/functions.php:4265`).
   - The cold path (`et_builder_print_font`, footer) does not filter it. The preview is always cold, because meta writes for the fake ID are blocked.
   - The variable Open Sans (`wdth` axis) then overrode the theme's static Open Sans and re-wrapped a 390 px heading (+22 px).
   - Divi 4.27.9 has no such filter, hence the gate.

Also kept for experiments: `&d5=preview` (Divi's preview mode under the Divi 5 filter names), `&fonts=inline` (leave Divi's inline Google Fonts option alone), and an HTML comment with `php_ms`, `peak_mem_mb` and `memory_limit`.

**Tried and rejected:**

| Attempt | Why it was rejected |
|---|---|
| Force the builder CSS inline via `divi_frontend_assets_static_css_module_style_manager` (setting `forced_inline` and the footer location) | Declarations stayed identical, but it **dropped the theme-customizer part of the unified resource** (the `@media (min-width:1350px) .et_pb_section{padding:54px 0}` rules). Section padding became 57.6 px instead of 54 px, for an 8.5–16 % pixel diff at 1440. |
| `d5=preview` (Divi's own preview mode) | Builder CSS was still identical, but the layout differed from live: a slider 423 px tall instead of 464 px, and a row losing its 108 px auto margin. Pixel diff 3.3 % (390) and 4.3 % (1440) on divi-ai-layout. The full static theme stylesheet cascades differently from Dynamic CSS. |

**Divi 4 regression check.** Tested with the prototype on 4.27.9, heldout-inscope and content-heldout:
- `render` output is byte-identical to the shipped Skill preview, apart from WordPress's random `wp_block_styles_on_demand_placeholder:<hex>` token and the new trailing instrumentation comment.
- `fidelity.py`: 454/454 and 110/110 declarations, identical sequences.

## 3. Q2: fidelity

**Method:**
- **Markup:** the balanced `.et-l` block, compared as a (tag, class) sequence. Reused from `research/tools/fidelity.py`.
- **Builder CSS:** (media, selector, declaration) triples of order-classed rules, same method as before. `compare_d5.py` widens the builder-CSS source to Divi 5's style ids:
  - `et-critical-inline-css`
  - `et-core-unified[-deferred]-<id>[-cached-inline-styles[-N]]`
  - flattened `et-core-unified*.css` files

  `fidelity.py` as shipped finds **0** builder declarations on Divi 5 pages: its regex only knows `et-builder-module-design-*`.
- **Live side:** each page was fetched warm, and its local stylesheets were inlined (`compare_d5.py flatten`).
- **Pixels:** `research/python-renderer-spike/shoot.mjs` (headless Chrome, builder-area `.et-l` bounding box, widths 1440 and 390) and `compare_visual.py` (Pillow; a pixel differs when a channel delta is > 16).
  - The preview side is the self-contained `render` file opened via `file://`.
  - The live side is a **frozen warm snapshot**: the flattened HTML with protocol-relative site URLs made absolute, loading fonts and images from `divi-5-test.local`.
  - Shooting the live URL directly was not reproducible. Another agent was using the same LocalWP site and clearing `et-cache` (`.cache-cleared-at` 19:16), so successive live loads alternated between cold and warm output. Two shots of the live URL differed by up to **14.3 % (390) and 2.4 % (1440)**. Two shots of the frozen snapshot differ by **0.000 %**, and two Playground renders also differ by 0.000 %.

**Final prototype vs live Divi 5.13.1:**

| Page | Elements | Tag/class sequence | `.et-l` bytes (live / preview) | Builder CSS decls (live / preview / common) | Pixel diff 1440 | Pixel diff 390 |
|---|---|---|---|---|---|---|
| divi-ai-layout | 347 | identical | 33,851 / 33,851, byte-identical | 2,480 / 2,480 / 2,480 | 0.0007 % | **0.000 %** |
| heldout-inscope | 127 | identical | 8,282 / 8,282, byte-identical | 490 / 490 / 490 | 0.0017 % | **0.000 %** |
| content-heldout | 82 | identical | 5,874 / 5,881 (`audio-12-1` vs `audio-990000001-1`) | 161 / 161 / 161 | 0.002 % | **0.000 %** |

- **The 1440 diff** is a 17×14 px box at the top right of the builder area: the site header's search icon. The fixed header is 130 px tall on live, because its fallback menu lists the other agent's test pages, and 80 px in Playground.
- **Geometry and computed style** are identical for every visible element. The only differing geometry rows are hidden (`display:none`) slides, whose y offset is measured from the header.

**How each fix moved the numbers (pixel diff, 1440 / 390):**

| Variant | divi-ai-layout | heldout-inscope | content-heldout |
|---|---|---|---|
| Unmodified Divi 4 mu-plugin (fresh boot per render) | 0.12 / 0.29 % | 0.62 / 14.58 % | 0.41 / 5.40 % |
| + et-cache purge + `<style>` font embedding | 0.0007 / 0.000 % | 0.58 / 14.58 % | 0.002 / 0.000 % |
| + Open Sans builder-font filter (**final**) | **0.0007 / 0.000 %** | **0.0017 / 0.000 %** | **0.002 / 0.000 %** |
| `d5=preview` (Divi preview mode), for comparison | 4.32 / 3.32 % | 1.00 / 14.98 % | 0.002 / 0.000 % |

Markup and builder-CSS declarations were identical in every variant. The one exception was stale `serve` output before the purge.

**Divi 4 shortcode rendered by the Divi 5 theme** (for context; not a target): the unconverted `heldout-inscope.txt`, rendered through Divi 5's shortcode compatibility layer, differs from the converted-blocks page. Tag/class ratio 0.599; CSS: 192 common, 298 missing, 262 extra. The preview must therefore be given the same format the site will store.

## 4. Q3: timings (Divi 5.13.1, this Mac)

| Measure | Result |
|---|---|
| Warm one-shot `render` (boot + render + write + stop), heldout-inscope | **4.6–4.7 s** over 3 runs. Boot about 3.0–3.3 s, render 1.4–1.5 s. |
| Same, divi-ai-layout (123 KB of blocks) | 4.9–5.2 s (render 1.7–1.9 s) |
| `serve`, subsequent renders | 0.85–0.94 s (10 samples, content-heldout); 0.9–1.2 s for heldout-inscope. First render after boot: 1.4 s. |
| First boot of a new `wp7.1.2-divi5.13.1` site (`--fresh`, WordPress install into SQLite) | 8.5 s total (ready at 5.7 s, render 2.6 s) |
| **Fully cold** (empty `PP_CACHE_DIR` except Divi, empty npm cache) | **29.3 s**: WordPress download 2.8 s, `npx` CLI install + boot + install about 23 s, render 2.65 s. An earlier identical attempt aborted after 86 s during downloads; the retry succeeded (not diagnosed). |
| Divi 5 download | **Not measured** (Elegant Themes API down today). About 35 MB, so about 2× the Divi 4 zip. |
| Output size (`render`, self-contained) | 1.7–1.9 MB, versus 3.0–3.2 MB for Divi 4. Dynamic CSS/JS ships only the features used. |
| Disk | Divi 5 unpacked 132 MB (Divi 4: 67 MB). Site 129 MB. npm cache 814 MB. WordPress 114 MB. |

## 5. Q4: supporting Divi 4 and Divi 5 (version-driven)

**Unchanged:**
- `blueprint.json`.
- The Playground CLI flags and mounts.
- The fake-page technique.
- The `?pp_preview=<name>` URL.
- The page-file mechanism: the file's content is used as `post_content` whether it is shortcode or blocks.

**Required changes (minimal):**

1. **`mu-plugin/pp-preview.php`:** add the three changes in §2: the et-cache purge, font embedding for `<style>` blocks, and the Divi 5-gated Open Sans filter. The prototype has them; Divi 4 output is unchanged.
   - Better than the purge for `serve`: a **unique fake ID per request** (e.g. `990000000 + counter`) plus garbage collection of old `et-cache/99…` dirs.
   - Why: in `serve` (non-inline) mode the page links `et-cache/<id>/et-divi-dynamic-<id>.css`, which the browser fetches *after* the response. A second preview request in between (two tabs) would purge it: a possible flash of missing late CSS. `render` (`inline=1`) is unaffected.
2. **Version resolution must be major-aware** (`preview.mjs` `resolveDiviVersion`/`newestCached`, `fetch_divi.newest_cached`, `preview.py resolve_divi_version`, `divi_render/assets.py`):
   - Today "newest cached" returns 5.13.1, so Divi 4 shortcode would silently render on Divi 5.
   - Resolve from `tokens.json → site.divi_version` first (unchanged).
   - Otherwise pick the newest cached version **of the major that matches the content**: `<!-- wp:divi/` means 5, `[et_pb_` means 4.
   - `--divi latest` needs a line: `latest4` / `latest5`, or infer it from the content.
3. **`fetch-divi.mjs` / `fetch_divi.py`, `latest` for Divi 5 (unverified):**
   - Divi's `et_core_maybe_add_divi5_api_parameter()` (`core/functions.php:2545`) adds `divi_5=on` to update requests. Presumably `check_theme_updates` needs `divi_5=on` (and maybe `installed_themes[Divi]=5.0.0`) to return the Divi 5 line.
   - A specific version should use the same `api_downloads.php?…&version=5.13.1` endpoint: `ElegantThemes::get_download_url()` is unchanged in 5.13.1.
   - Verify when the API is up. It rate-limits at about 15 calls per 5 minutes.
4. **Tooling:**
   - `research/tools/fidelity.py` `_BUILDER_STYLE` must accept Divi 5 style ids (use the regex in `compare_d5.py`).
   - `ground_truth.py` works as-is with an explicit `--divi 5.13.1`, since truth is keyed by version.
   - `tests/test_render_fidelity.py` / `test_render_fallbacks.py` should pin a 4.x version instead of `newest_cached()`.
5. **Optional:**
   - Accept `.html` page files for block markup (only `.txt` is listed today; block content in `.txt` works).
   - The Divi 4 head-move regex (`et-builder-module-design-*`) never matches on Divi 5. Harmless: on a first-load Divi 5 page the builder CSS sits in the footer, and pixels are identical.

## 6. Shipped (Task 14, 2026-09-29)

The prototype was ported into `Skill/divi-page-builder/scripts/preview/` and `preview.py`:

- **Version selection is major-aware** everywhere (`fetch_divi.newest_cached(major=)`, `fetch-divi.mjs`
  `newestCached`/`resolveDiviVersion`, `divi_render/assets.py`, the render-fidelity tests): shortcode → newest cached
  4.x, blocks → newest cached 5.x, explicit `--divi`/`--tokens` win. The Divi 5.13.1 cache is back in place
  (`~/.cache/divi-page-builder/divi/Divi-5.13.1`) and the Divi 4 suites pick 4.27.9.
- **mu-plugin:** the three fixes, each gated on the mounted theme's `style.css` major being 5. `serve` requests get a
  fake id per page name (`990000002 + crc32(name) % 999998`) and that id's `et-cache` dir is purged per request;
  `inline=1` renders keep `990000001`. The seeding sidecar `<name>.seed.css` is injected at the end of `<head>`.
  The seed sidecar is read and injected only on Divi 5. The prototype's experiments (`d5=preview`, `fonts=inline`,
  the timing comment) were not shipped.
- **Divi 4 regression:** `render` of heldout-inscope, content-heldout and divi-ai-layout on 4.27.9 with the shipped
  preview vs the pre-change one: byte-identical apart from WordPress's random `wp_block_styles_on_demand_placeholder`
  token (3.10/3.26/3.15 MB). `serve` (non-inline) of two of them: identical after the same normalization.
- **Elegant Themes API (2 calls):** `check_theme_updates` with `divi_5=on` and `installed_themes[Divi]=5.0.0` answered
  `new_version` **5.14**. `api_downloads.php?…&version=5.13.1` returned a **32.7 MB** zip with the Divi 4 layout
  (top-level `Divi/`, 3,360 entries, `style.css` Version 5.13.1).

**Live parity** (`tests/test_preview.py` `Divi5PreviewParityTest`, `preview.py render` vs the same block content
published on divi-5-test.local as "D5TEST preview …" pages, fetched after a warm-up view and flattened; pages deleted after):

| Fixture | Elements | Tag/class sequence | `.et-l` bytes (live / preview) | Builder CSS decls (live / preview / common) | `render` wall time |
|---|---|---|---|---|---|
| `divi5/divi-ai/layout.html` | 231 | identical | 24,859 / 24,859, byte-identical | 2,099 / 2,099 / 2,099 | 7.1 s |
| `divi5/converted/heldout-inscope.html` | 127 | identical | 8,282 / 8,282, byte-identical | 490 / 490 / 490 | 8.7 s |
| `divi5/converted/content-heldout.html` | 82 | identical | 5,875 / 5,881 (audio post id) | 161 / 161 / 161 | 6.8 s |

(`divi-ai/layout.html` is a different conversion of that layout than the spike's 123 KB one, hence 2,099 not 2,480.)

**`serve`** (one warm Playground behind `preview.py serve`): a → b → a → a edited to divi-ai's content, each flattened
response vs its live page: identical sequences and 0 missing / 0 extra declarations at every step. The per-name fake
ids left three `et-cache` dirs (990000001 and two per-page ids) and no rows in the Playground site's options.

**Timings on 2026-09-29** were taken with the machine at load average 6–7 (another long-running process at 85 % CPU):
`render` 6.8–8.7 s end to end, `serve` reloads 1.6–3.5 s, first page after `serve` starts about 7 s. The research
prototype measured the same 1.6–3.5 s (up to 6.9 s) on the same pages in the same conditions, so the port adds no
cost; the unloaded figures in §4 stand.

## Implications for the skill

- **`--exact` works for Divi 5 with the same architecture.** There is no new runtime dependency, no WordPress install for users, stock Divi settings, and Divi stays in `PP_CACHE_DIR`. Fidelity is at the Divi 4 level or better (exact builder markup and CSS, and pixel-identical builder area at 390 px).
- **Ship the mu-plugin changes together with the major-aware version resolver.** The resolver is the real risk. Once any Divi 5 version is in a user's cache, Divi 4 previews and the fidelity tests would silently switch to Divi 5. **This machine is already in that state.**
- **The preview must receive the format the target site stores.** Divi 5 blocks for a Divi 5 site; Divi 4 shortcode for a Divi 4 site. Shortcode fed to Divi 5 renders, but not like converted blocks.
- **Divi 5 needs about 2× the download and cache** (about 35 MB zip, 132 MB unpacked). Warm and `serve` timings are the same as Divi 4.
- **Open items:**
  - The Divi 5 download through the Elegant Themes API: resolved in Task 14 (§6). `latest5` sends `divi_5=on` (answered 5.14 on 2026-09-29) and a per-version 5.13.1 download works, with the Divi 4 zip layout. A 5.14 download itself is not yet verified.
  - The Visual Builder inside Playground (not needed).
  - Theme Builder templates and client settings (out of scope, as for Divi 4).

## Verified vs inferred

**Verified by running:**
- Activation and rendering on PHP 8.2 and 8.3, with no PHP errors.
- Every fidelity and pixel number above, and the `serve` staleness plus its fix.
- The Divi 4 non-regression.
- All timings except the Divi 5 download.
- Memory.
- The `divi/v1` REST namespace.

**Inferred:**
- The Divi 5 download size (from a local `zip -9`).
- ET API behaviour for the Divi 5 line.
- The two-tab race in `serve` mode (from reading the code; not reproduced).
- Linux and Windows behaviour (as for Divi 4).

## Files

- `research/divi5/playground-prototype/`: `preview.mjs` (adds only `--query`), `fetch-divi.mjs` and `blueprint.json` (unchanged copies), `mu-plugin/pp-preview.php` (Divi 4 + Divi 5), `compare_d5.py` (flatten + Divi 5-aware fidelity), and `.gitignore` (no Divi code, rendered HTML, screenshots or caches).
- Artefacts outside the repo (they contain Divi's licensed CSS):
  - The session scratchpad `r5/`: `d5/` (converted content), `live/` (warm live snapshots), `out/` (renders) and `shots/` (screenshots and geometry).
  - `~/.cache/divi-page-builder/divi/Divi-5.13.1/` and `sites/wp7.1.2-divi5.13.1/`.
