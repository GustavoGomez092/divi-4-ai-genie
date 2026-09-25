# Spike: Divi 4 preview on WordPress Playground

Spike run on 2026-09-24 (macOS arm64, Node 24.1.0, npm 11.6.2). Question: can a portable, one-command local preview render Divi 4 pages with real Divi code inside WordPress Playground, with no MySQL and no LocalWP, and fetch Divi automatically from the user's Elegant Themes account?

Prototype: `research/playground-prototype/`. Background: `research/divi-render-engine.md`, which describes the fake-page render technique reused here.

## TL;DR: GO

- **Divi download works (verified).** Divi's own rollback endpoint returns a specific version zip given username + API key. 4.27.9 and 4.27.3 both downloaded (17.6 / 16.8 MB, about 2 s each). The 4.27.9 zip is file-for-file identical to the LocalWP install (`diff -rq`: no differences).
- **Divi runs on Playground's SQLite (verified).** Playground CLI 3.1.55, PHP 8.2.33 (WebAssembly), WordPress 7.1.2 (the same version as the local site). Divi activates and renders with no fatals, warnings or notices while WP_DEBUG is on.
- **Rendering works (verified).** A mu-plugin serves `http://127.0.0.1:9400/?pp_preview=<name>` from `<pages>/<name>.txt` using the render.php fake-page technique. Editing the file and reloading re-renders it. `render` mode writes a self-contained HTML file.
- **Fidelity matches LocalWP (verified), compared with live page 11:**
  - The `.et-l` builder markup is **byte-identical** (31,755 chars).
  - Builder CSS: **2,064 / 2,064** declarations identical, counted as (media, selector, declaration) triples after exploding grouped selectors, with 0 missing and 0 extra.
  - Pixel diff of the self-contained file, opened from disk after the server was stopped, against the live page:
    - Desktop: **0.023 %** of pixels differ, all in the header nav. That band lists the site's own pages, so it is site content, not rendering.
    - Phone: **0.041 %**, the header nav plus the number-counter animation.
  - Rendering Divi 4.27.3 and 4.27.9 gives identical output for this layout.
- **Timings (verified):**
  - Warm one-shot render: **about 4.2–5 s** end to end. Boot is 2.8–3.4 s and the first render 1.5 s.
  - `serve` mode: **about 1.0 s per render**.
  - Cold first run: **about 25–30 s**, most of it the npm install of the CLI.
  - **Works fully offline after the first run.** Verified with outbound network blocked by `sandbox-exec`.
- **Requirements:** Node (24.x tested) and npm/npx, plus `unzip` or bsdtar `tar`. Elegant Themes credentials are needed only the first time a Divi version is fetched. There is no PHP, MySQL, Docker or LocalWP dependency.

---

## 1. Divi download (Elegant Themes API)

**Source.** The code is `core/components/api/ElegantThemes.php`:
- `get_download_url()` is used by `core/components/VersionRollback.php:315`.
- Theme update checks are in `core/components/Updates.php:666-740` (`check_themes_updates`, `maybe_add_automatic_updates_data`).
- The product name is `$themename` = `Divi` (`functions.php:8781`).
- Divi itself reads the credentials from the option `et_automatic_updates_options` (`username`, `api_key`).

| Call | Request (credentials redacted) | Response |
|---|---|---|
| Version available? | `GET https://www.elegantthemes.com/api/api.php?api_update=1&action=check_version_status&product=Divi&version=4.27.9&username=<ET_USERNAME>&api_key=<API_KEY>` | PHP-serialized `a:1:{s:6:"status";s:9:"available";}`. Other values are `not_available` (e.g. 9.9.9) and `blacklisted` (2.3.6). **It does not validate credentials**: a bad key still returns `available`. |
| Download specific version | `GET https://www.elegantthemes.com/api/api_downloads.php?api_update=1&theme=Divi&version=4.27.9&username=<ET_USERNAME>&api_key=<API_KEY>` | `200 application/zip`, no Content-Disposition, top-level dir `Divi/`. 4.27.9 = 18,442,749 B; 4.27.3 = 17,650,955 B. About 0.6–1.9 s. |
| Download latest | Same URL **without** `version` | The 4.27.9 zip, byte-identical to `version=4.27.9` (`cmp`). |
| Latest version number | `POST https://www.elegantthemes.com/api/api.php` with `action=check_theme_updates&installed_themes[Divi]=4.0.0&class_version=1.2&automatic_updates=on&username=…&api_key=…` | Serialized array: `['Divi']['new_version']="4.27.9"`, `['Divi']['package']` (the download URL above with credentials embedded), plus `et_account_data.et_username_status="active"`. |

**Error behaviour (verified):**
- Bad API key: `200 text/html` with body `API key is not valid`.
- Bad username: `200 text/html` with body `Subscription is not active`.
- Nonexistent version on `api_downloads`: `403 application/xml` `<Error><Code>AccessDenied</Code>…` (S3).
- **Rate limit:** after about 15 API calls in about 5 minutes, every endpoint returned `429` with an HTML page. The fetcher reports this as "rate-limited, retry later". A shipped tool must cache aggressively and never call the API on warm runs. `preview.mjs` defaults to the newest *cached* version for this reason.
- **Gotcha:** the "latest" lookup picks the upgrade line from `installed_themes[Divi]`. `0` returned **2.3.6** (blacklisted) and `4.0.0` returned 4.27.9. Divi 5 is only offered when a `divi_5` parameter is sent (`et_core_maybe_add_divi5_api_parameter`), and we never send it.
- Credentials travel in the query string over HTTPS. This is Divi's own protocol. The fetcher keeps the credentials in memory only and redacts them from every error message, and no URL is ever logged.

Implemented in `playground-prototype/fetch-divi.mjs`: `ET_USERNAME=… ET_API_KEY=… node fetch-divi.mjs 4.27.3`. It checks the version status, downloads the zip, verifies the `PK` magic, unpacks with `unzip` or bsdtar, and checks `style.css` `Version:` against the request. It uses Node's `fetch`. Python's `urllib` failed on this Mac with `CERTIFICATE_VERIFY_FAILED` (the python.org build ships no CA bundle), which is another reason to stay on Node.

## 2. Divi on Playground

**CLI tested:** `npx @wp-playground/cli@3.1.55`. It provides `start`, `server`, `run-blueprint`, `build-snapshot` and `php`, with the flags `--php` (5.2, 7.4, 8.0–8.5), `--wp`, `--mount`, `--mount-before-install`, `--wordpress-install-mode`, `--blueprint`, `--define-bool` and `--port`. npm prints `EBADENGINE` warnings (the packages declare `node >=24.18`, `npm >=11.16`), but everything ran on Node 24.1.0.

**Result (verified):**
- The unpacked theme is mounted at `/wordpress/wp-content/themes/Divi`, and the blueprint step `activateTheme` activates it.
- The response header from the mu-plugin reads `X-PP-Env: php=8.2.33 wp=7.1.2 divi=4.27.9 theme=Divi wp_debug=1`.
- No fatals. With WP_DEBUG and WP_DEBUG_DISPLAY on, the rendered page contains no `Warning`, `Notice`, `Deprecated` or `Fatal` text.
- In one run that accidentally used PHP 8.5, `debug.log` had a single `PHP Deprecated: Automatic conversion of false to array … Divi/epanel/custom_functions.php:296`, which is harmless.
- The `divi/v1` REST namespace loads. Admin redirects to login as normal.
- SQLite is the only DB, handled by Playground's bundled `sqlite-database-integration`. Divi's options, transients and et-cache all work.

**Playground quirks found and handled:**

| Quirk | Handling |
|---|---|
| A blueprint without `preferredVersions` silently overrides `--php`: PHP 8.5.10 ran despite `--php=8.2`. A blueprint with `preferredVersions.wp: "latest"` overrides `--wp` in the same way. | `preview.mjs` generates the blueprint per run with `preferredVersions.php` set. |
| `--wp=7.1.2`, or a release URL, **always** calls `api.wordpress.org/core/version-check` before using the cached zip, so boot fails offline with `fetch failed`. | `preview.mjs` downloads WordPress itself and boots with `--mount-before-install=<site>:/wordpress --wordpress-install-mode=install-from-existing-files-if-needed`. |
| `npx -y pkg@x.y.z` waits about 70 s for the npm registry to time out when offline. | `npx --prefer-offline` (safe because the version is pinned). |
| Re-running `activateTheme` on a persisted site triggers Divi 4.27's onboarding: the first front-end request is answered with a 302 to `wp-admin/admin.php?page=et_onboarding&content=disabled`, from `onboarding/functions.php` on `after_switch_theme`. | The mu-plugin unhooks `et_onboarding_trigger_redirect` during preview requests. |
| The first request after every boot gets a `302` to the same URL (source not traced; the Playground server). | Harmless: browsers and `fetch` follow it. `curl` users need `-L`. |
| The blueprint step `setSiteOptions` → `blogname` never took effect: the value stayed "My WordPress Website" in the SQLite DB. | Dropped from the blueprint. Only the `<title>` suffix is affected. The real fix is the settings-bundle filter below. |

## 3. Rendering inside Playground

**Chosen design: a mu-plugin over HTTP** (`mu-plugin/pp-preview.php`, about 250 lines, mounted at `/wordpress/wp-content/mu-plugins`). On `?pp_preview=<name>` it does the following:
- Reads `/pp-pages/<name>.txt`. The pages directory is mounted from the host, so every request sees the current file. An optional `<name>.meta.json` supplies page meta.
- Primes a fake `WP_Post` (ID 990000001) and its meta in the object cache.
- Uses the `request` filter to point the main query at it, and `posts_pre_query` to return it.
- Applies the same Divi preview-mode filters as render.php and sets `_et_pb_static_css_file=off`.
- Uses an output buffer to move the forced-inline builder CSS and font link from the footer to the end of `<head>`.
- Blocks meta writes for the fake ID and sets `nocache_headers()`.
- Turns off Divi's **inline Google Fonts** option (`et_builder_google_fonts_is_enabled`, `google_fonts_inline` → false).
  - Why: on an uncached render Divi fetches the fonts CSS server-side with non-browser user agents and gets TTF files instead of the WOFF2 files a browser gets. That caused glyph-level diffs in 0.11 % of pixels and a network call per render.
  - With the option off, the preview emits the same `<link>` a warmed-up live page serves.
- With `&inline=1`, it inlines local CSS and JS and embeds local web fonts (woff, woff2, ttf) as `data:` URIs, as in render.php step 4. The resulting file works after the server is gone.

**Why not WP-CLI or `runPHP`:** the `php` subcommand and `run-blueprint` boot a fresh WordPress for every invocation (about 3 s or more). The HTTP route keeps one warm server, gives a real URL that a browser or AI can reload, and serves theme assets naturally. It is also simpler than render.php, because the request is real: no `$_SERVER` faking, no manual `wp()`, no template include. Nothing is written to the DB for the fake ID, checked in SQLite: 0 rows in `wp_posts` and `wp_postmeta` for 990000001.

**Wrapper:** `preview.mjs` (Node, no dependencies).

```
node preview.mjs serve  [--pages DIR] [--divi 4.27.3] [--port 9400] [--php 8.2] [--wp 7.1.2] [--fresh]
   -> prints http://127.0.0.1:9400/?pp_preview=<name> for each DIR/*.txt; Ctrl-C stops (process group killed)
node preview.mjs render layout.txt --out layout.html [--divi …]
   -> boots, renders with inline=1, writes a self-contained file, stops the server, exits
```

Cache layout (`PP_CACHE_DIR`, default `~/.cache/post-pusher`; `%LOCALAPPDATA%\post-pusher` on Windows):
- `divi/Divi-<v>/Divi` plus the zip
- `wordpress/<v>/wordpress` (pristine core)
- `sites/wp<v>-divi<v>/wordpress`: a persistent site per (WP, Divi) pair. The SQLite DB lives inside it, so later boots skip the install, and Divi options never cross versions.

## 4. Fidelity (all run)

`compare.py <live.html> <preview.html>` checks:
- `.et-l` equality, using balanced-div extraction.
- The builder CSS set: every `<style>` block, grouped selectors exploded, `(media, selector, decl)` triples, selectors containing a module *order class* (`.et_pb_text_3`, but not `.et_pb_column_1_3`).
- Body classes.

The live page's `et-core-unified-deferred-11.min.css` and dynamic CSS are appended as `<style>` blocks. Live `divi-dynamic-critical-inline-css` is excluded because it is theme base CSS that sits in `style-static.min.css` in the preview.

| Comparison | Result |
|---|---|
| Playground `serve` vs live page 11: `.et-l` | **Identical**, 31,755 chars |
| Builder CSS declarations | **2,064 live / 2,064 preview, 2,064 common, 0 / 0 diff** |
| Body classes | Only `page-id-11` vs `page-id-990000001` |
| Same, offline boot (network blocked) | Identical (same numbers) |
| Divi 4.27.3 vs 4.27.9 render of this layout | Identical markup and CSS (2,968 / 2,968 with inlined static CSS) |
| First pass, before the Google Fonts fix: headless Chrome 1440×7655 | 0.114 % of pixels differ. Crops showed glyph anti-aliasing only (TTF vs WOFF2), not layout. |
| After the fix, `serve` URL vs live, 1440×7655 / 390×15310 | 0.044 % / 0.007 %. Bands: header nav (site pages) and number counters (animation). |
| **`render` file opened via `file://` with the server stopped**, vs live | **0.023 % / 0.041 %**. Desktop: header nav band only. Phone: header plus counters. |

The header nav differs because Divi's fallback menu lists the *site's* pages. Live has "Home, Probe: …, Sample Page, Uncategorized" and the fresh Playground site has "Sample Page, Uncategorized". Logo, header height and every builder pixel are identical.

## 5. Practicalities

| Measure | Result (verified on this Mac) |
|---|---|
| Divi download + unpack | 1.8–1.9 s (17 MB zip, 64–67 MB unpacked) |
| WordPress 7.1.2 download + unpack | 3.0 s (37 MB zip, 114 MB unpacked) |
| First boot of a new (WP, Divi) site (install into SQLite) | about 5.4 s |
| **Cold first run** (empty npm cache and Playground cache, Divi already cached) | **25.3 s** total, mostly `npx` installing the CLI. Add about 2 s for the Divi download. |
| **Warm boot** (site persisted) | **2.8–3.4 s**, online or offline |
| First render after boot | 1.5–1.6 s |
| Subsequent renders (`serve`, 10 samples) | min 1.02 s, median 1.03 s, max 1.17 s. render.php on native PHP took 0.4 s. |
| **Warm one-shot `render`** (boot + render + write + shutdown) | **4.2–5.1 s** |
| Offline after first run | **Yes.** `sandbox-exec` denied all outbound traffic except localhost, and both `render` and `serve` worked with identical fidelity. The preview's Google Fonts and Unsplash images are loaded by the browser, so they need network to *look* right, but not to render. |
| Disk | npx install of the CLI: 578 MB, mostly 8 PHP wasm builds of about 60 MB each; a fresh npm cache totalled 806 MB. WordPress: 114 MB. Each site: 131 MB (a full WP copy plus the DB). Each Divi version: about 85 MB (unpacked plus zip). A typical footprint is about 1–1.2 GB. |

**Requirements:** Node ≥ 20 for global `fetch`; tested on 24.1, and the CLI's packages declare ≥ 24.18. npm/npx. `unzip` (macOS/Linux) or bsdtar `tar` (macOS, Windows 10+). Elegant Themes credentials, only for versions not yet cached.

**Platform notes (inferred, not run):**
- Linux: should work as-is (`unzip` is usually present).
- Windows: `preview.mjs` uses `npx.cmd`, `taskkill /T` and `tar.exe`. Mounts pass Windows paths to the CLI, which Playground documents as supported, but this is unverified.
- The offline test used macOS `sandbox-exec`.

## Verified vs inferred

Verified by running:
- ET endpoints, sizes, errors and the rate limit.
- Divi activation, and no PHP errors under WP_DEBUG on PHP 8.2.
- The mu-plugin render, re-render on edit, the 404 for a missing file, and a malformed shortcode rendering an empty `.et-l` without a fatal.
- The fidelity numbers and pixel diffs.
- The 4.27.3 render.
- Offline boot and render.
- The timings above.
- Process cleanup: no stray servers after `render` or SIGTERM.

Inferred:
- Linux and Windows behaviour.
- The settings bundle (render.php `settings=`) inside the mu-plugin. It isn't ported yet, but it is the same `pre_option_*` filters, so it should transfer directly.
- Theme Builder templates. Untested, as in the previous spike.
- Node 20/22. Only Node 24.1 was run.

## Recommendation: GO

Ship `scripts/preview` as the default preview path. LocalWP or a mirror site becomes optional, needed only for clients with a child theme, plugins or Theme Builder templates. Proposed shape:

```
scripts/preview serve  [--pages DIR] [--divi VERSION] [--settings bundle.json] [--port 9400]
scripts/preview render <layout.txt> [--out file.html] [--screenshot file.png] [--divi VERSION] [--settings bundle.json]
scripts/preview fetch-divi <VERSION|latest>          # pre-warm the cache (the only command that needs ET creds)
scripts/preview doctor                                # node/npx/unzip present, cache sizes, cached Divi/WP versions
```

- **Env:** `ET_USERNAME` / `ET_API_KEY` (never logged; only needed by `fetch-divi` or the first use of a version), `PP_CACHE_DIR`, `PP_DIVI_VERSION`, `PP_WP_VERSION`, `PP_PLAYGROUND_CLI` (pinned CLI spec).
- **Version selection:** `--divi` should default to the client's `meta.divi_version` from their settings bundle, so a 4.27.3 client previews on 4.27.3. Otherwise use the newest cached version, and only then "latest". Never hit the ET API on a warm run: it rate-limits.
- **To add before shipping:**
  - Port the `settings=` bundle (customizer, presets, global colors, custom CSS) from render.php into the mu-plugin, e.g. `/pp-pages/<name>.settings.json` or a per-run `--settings`.
  - Add a `--screenshot` option (headless Chrome, as in `compare.sh`).
  - Reduce disk use by hard-linking or mounting WordPress core read-only instead of copying it per site.
  - Pin the CLI version and smoke-test it on upgrade: the preferredVersions and offline quirks above are CLI-version specific.
  - Keep all Divi files in the user cache, never in the repo (licensing). `playground-prototype/.gitignore` guards this.

## Files

- `research/playground-prototype/preview.mjs`: one-command `serve` / `render`.
- `research/playground-prototype/fetch-divi.mjs`: Elegant Themes download and cache (usable standalone).
- `research/playground-prototype/mu-plugin/pp-preview.php`: the in-Playground renderer.
- `research/playground-prototype/blueprint.json`: `activateTheme Divi`. `preferredVersions` is injected per run.
- `research/playground-prototype/compare.py`: markup and CSS fidelity check against a live page.
- `research/playground-prototype/.gitignore`.

Spike artefacts, outside the repo, under the session scratchpad: `divi-cache/` (Divi 4.27.9 and 4.27.3), `ppcache/` (WordPress plus two sites), `shots/` (screenshots and diffs), `live-flat.html`, and rendered outputs.
