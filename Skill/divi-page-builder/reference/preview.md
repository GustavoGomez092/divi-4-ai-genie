# Preview

There are two previews. **`scripts/preview.py` is the default**: a pure-Python (stdlib only)
re-implementation of Divi's front-end rendering, no Node/PHP/WordPress required. **`--exact`**
hands the same command to `scripts/preview/preview.mjs`, which runs the *real* Divi theme inside
WordPress Playground (WebAssembly PHP + SQLite) — verified byte-for-byte against a
live page (repo only: `research/playground-spike.md`).

## 1. The two previews

| | `python3 scripts/preview.py` (default) | `--exact` (`node scripts/preview/preview.mjs`) |
|---|---|---|
| What renders it | A Python re-implementation of Divi's PHP output: markup templates plus a CSS engine driven by the compact schema | The real Divi 4 theme, running as real PHP |
| Requirements | Python only (stdlib) | Node ≥ 20, `unzip`/`tar`, ~1–1.2 GB disk |
| Speed | Instant (no boot) | ~3 s after the first boot; ~25–30 s cold (one-time `npx` install) |
| Portable output | Yes — `render` inlines fonts/images as `data:` URIs so the file works from `file://` with no network | Yes — same inlining, same guarantee |
| Coverage | Every module in [§3](#3-supported-modules) exactly; everything else is a labelled placeholder | Everything — it's the real theme |
| Site data (posts, menus, media, comments, widgets) | Placeholder blocks; not from any real site | A fresh Playground WordPress has none either — still not real site data |

Both commands accept the same page, `--out`/`--pages`, `--divi`/`--tokens` and `--port`. Adding
`--exact` to a `render` or `serve` invocation forwards it, unchanged, to `preview.mjs` — see
[§6](#6-commands).

## 2. When to use `--exact`

- **A page uses a module the coverage report lists as unsupported.** Every `render`/`serve` call
  prints a coverage summary; unsupported modules and features say `use --exact` right in the
  line. (Content that instead says "needs the live site's data" is not fixed by `--exact` — see
  [§5](#5-limits).)
- **Before sharing a draft for an important page.** The Python renderer is tuned and measured
  against real Divi (see [§4](#4-fidelity)), but it's still a re-implementation; `--exact` is
  proof, not an estimate.
- **Whenever the Python preview looks wrong.** If markup or styling looks off and you're not sure
  why, `--exact` rules out a renderer bug in one command.

## 3. Supported modules

<!-- BEGIN GENERATED MODULES (repo only: research/tools/gen_preview_module_table.py) -->
| Module | Tag |
|---|---|
| Accordion | `et_pb_accordion` |
| Accordion | `et_pb_accordion_item` |
| Audio | `et_pb_audio` |
| Blurb | `et_pb_blurb` |
| Button | `et_pb_button` |
| Circle Counter | `et_pb_circle_counter` |
| Code | `et_pb_code` |
| Column | `et_pb_column` |
| Column | `et_pb_column_inner` |
| Field | `et_pb_contact_field` |
| Contact Form | `et_pb_contact_form` |
| Countdown Timer | `et_pb_countdown_timer` |
| Bar Counter | `et_pb_counter` |
| Bar Counters | `et_pb_counters` |
| Call To Action | `et_pb_cta` |
| Divider | `et_pb_divider` |
| Fullwidth Code | `et_pb_fullwidth_code` |
| Fullwidth Header | `et_pb_fullwidth_header` |
| Fullwidth Image | `et_pb_fullwidth_image` |
| Fullwidth Map | `et_pb_fullwidth_map` |
| Fullwidth Slider | `et_pb_fullwidth_slider` |
| Gallery | `et_pb_gallery` |
| Heading | `et_pb_heading` |
| Icon | `et_pb_icon` |
| Image | `et_pb_image` |
| Map | `et_pb_map` |
| Pin | `et_pb_map_pin` |
| Number Counter | `et_pb_number_counter` |
| Pricing Table | `et_pb_pricing_table` |
| Pricing Tables | `et_pb_pricing_tables` |
| Row | `et_pb_row` |
| Row | `et_pb_row_inner` |
| Section | `et_pb_section` |
| Email Optin | `et_pb_signup` |
| Custom Field | `et_pb_signup_custom_field` |
| Slide | `et_pb_slide` |
| Slider | `et_pb_slider` |
| Social Media Follow | `et_pb_social_media_follow` |
| Social Network | `et_pb_social_media_follow_network` |
| Tab | `et_pb_tab` |
| Tabs | `et_pb_tabs` |
| Person | `et_pb_team_member` |
| Testimonial | `et_pb_testimonial` |
| Text | `et_pb_text` |
| Toggle | `et_pb_toggle` |
| Video | `et_pb_video` |
| Video Slider | `et_pb_video_slider` |
| Video | `et_pb_video_slider_item` |
<!-- END GENERATED MODULES -->

This table is generated from `divi_render.SUPPORTED_MODULES` (the handler registry every
`@register(...)` call in `scripts/divi_render/` populates); `tests/test_preview_docs.py` fails if
it drifts from the registry.

**Not in this table, and why:**

- **`et_pb_search`, `et_pb_login`** — not ported to Python; render as a red placeholder. Use
  `--exact`.
- **YouTube/Vimeo embeds inside `et_pb_video`** — the module itself is supported, but the actual
  oEmbed fetch needs the network; the Python preview prints the iframe oEmbed would return and
  counts it as `video_oembed` in the coverage report. `--exact` shows the real embed when it has
  network access.
- **`et_pb_blog`, `et_pb_portfolio`, `et_pb_filterable_portfolio`, `et_pb_fullwidth_portfolio`,
  `et_pb_post_slider`, `et_pb_fullwidth_post_slider`, `et_pb_post_title`,
  `et_pb_fullwidth_post_title`, `et_pb_post_content`, `et_pb_fullwidth_post_content`,
  `et_pb_post_nav`, `et_pb_comments`, `et_pb_sidebar`, `et_pb_menu`, `et_pb_fullwidth_menu`, and
  gallery attachments from the media library** — these show the *live site's* posts, projects,
  menus, comments or widgets. Neither preview has that: a fresh Playground WordPress has no
  posts, menus or media either, so `--exact` can't help. The coverage report lists these under
  "needs the live site's data" (not "use `--exact`"); check the WordPress draft preview instead.

## 4. Fidelity

The project's fidelity harness (repo only: `research/render-fidelity.md`, `research/tools/fidelity.py`)
measures the Python renderer against real Divi (Playground truth): the **markup ratio** (a difflib ratio over `(tag, class list)`
in the `.et-l` block; 1.0 = identical) and the **CSS ratio** (Jaccard similarity of builder CSS
`(media, selector, declaration)` triples; 1.0 = no missing/extra declarations). **Tuned**
fixtures must be exact (both ratios 1.0). **Held-out** fixtures are measured *before* any fix, as
the honest read of how the renderer generalizes to combinations it wasn't tuned on.

| Stage | Fixture | Tuned | Markup | CSS |
|---|---|---|---|---|
| T24 | `heldout2-inscope.txt` (pre-fix) | no | 0.9574 | 0.9469 |
| T24 | `heldout2-inscope.txt` (post-fix) | yes | 1.0000 | 1.0000 |
| T25 | `content-heldout.txt` (pre-fix) | no | 1.0000 | 0.9550 |
| T25 | `content-heldout.txt` (post-fix) | yes | 1.0000 | 1.0000 |
| T26 | `interactive-heldout.txt` (pre-fix) | no | 1.0000 | 1.0000 |
| T26 | `interactive-heldout.txt` (post-fix) | yes | 1.0000 | 1.0000 |
| T27 | `forms-heldout.txt` (pre-fix) | no | 0.9975 | 1.0000 |
| T27 | `forms-heldout.txt` (post-fix) | yes | 1.0000 | 1.0000 |

`heldout-outofscope.txt` deliberately mixes in modules that weren't supported yet at each stage;
its ratio rises as those modules land (T24 0.20/0.19 → T27 0.99/0.77) but isn't held to 0.9 until
every module on it is supported. It's included in `render-fidelity.md`, not above, because it
doesn't compare tuned vs. held-out for a single feature set.

**Be honest about what this does and doesn't prove:**

- Every pre-fix held-out row above passed or came within one element/declaration of exact. That's
  strong evidence the renderer generalizes well within the module families it's tuned on — but it
  is not a guarantee. An unseen *combination* of options (a module family paired with an option
  combination no fixture exercises) can still render slightly differently than real Divi.
- The fidelity harness only counts selectors that carry an order class as a plain CSS
  class (e.g. `.x_0`). Rules scoped by an *attribute selector*, such as the slider's
  `.et_pb_slider[data-active-slide="et_pb_slide_0"] .et-pb-slider-arrows …`, have their order
  class inside quotes and are never counted — a CSS ratio of 1.0 does not verify them. They were
  ported from Divi's `SliderItem.php` but are unchecked by this measurement. If a page leans on
  `[data-active-slide]` styling, verify it with `--exact`.

## 5. Limits

- **Stock Divi settings only.** There is no client settings bundle: the client's Customizer
  values, global presets and global colors are **not** applied in either preview (Addendum A).
  Anything a page doesn't set directly on the module falls back to Divi's own defaults, not the
  client's.
- **The header and footer are stubs**, not the client's real site: a static logo/menu shell and a
  static footer, with no real WordPress menus and no Theme Builder header/footer layouts (there's
  no WordPress underneath the Python preview to have them). `--exact`'s Playground WordPress is
  also a fresh site, so its header/menu differ from the client's for the same reason (about
  0.02–0.04% of pixels in the spike, all in the header nav band) — this is not something either
  preview fixes; the WordPress draft preview is the only one with the real header and footer.
- **Web fonts and remote images need network to look right,** in both previews. Google Fonts and
  any remote image referenced by URL only render correctly with network access; without it the
  page still renders, just with fallback fonts and missing images.
- **One Elegant Themes download per Divi version.** `fetch-divi` (and an uncached `render`/
  `serve`) needs `ET_USERNAME`/`ET_API_KEY` (an Elegant Themes account's API key) the *first*
  time a given Divi version is used; after that it's cached and fully offline for that version.
  Credentials are read only from the environment, used only in request URLs, and every error
  message redacts them before printing — never logged or written to disk. The API rate-limits at
  about 15 calls per 5 minutes; a cached version never calls it, so this only affects fetching new
  versions.

## 6. Commands

### `render` — one standalone HTML file

```bash
python3 scripts/preview.py render drafts/landing-page.txt --out landing-page.html
python3 scripts/preview.py render drafts/landing-page.txt --out landing-page.html --exact
```

Renders one page, inlines Divi's CSS, icon fonts and theme images as `data:` URIs (so the file
still works opened straight from disk, with no server and no network), writes it and prints the
coverage summary. Default `--out`: `<page name>.html` in the current directory.

### `serve` — a live, reloadable preview server

```bash
python3 scripts/preview.py serve --pages ./drafts --port 8765
python3 scripts/preview.py serve --pages ./drafts --exact
```

Serves `http://127.0.0.1:PORT/<name>` for every `./drafts/<name>.txt`, re-rendered on each
request; editing the `.txt` file and reloading the page shows the change immediately (the page
polls `/__mtime/<name>` and reloads itself). Divi's fonts/images/JS are served from `/__divi/…`
instead of embedded. Pages with unsupported modules or site-data content show a banner naming
which preview (or which check) can show them. `Ctrl-C` stops the server.

### Local images

Both commands recognize local image references the same way `publish.py draft` does: any image
attribute (`src`, `background_image`, anything ending `_image`, etc. — `local_media.py`) whose
value is `./relative`, `../relative` or `file:///abs/path`, resolved against the page file's own
directory. `render` embeds each one it finds on disk as a `data:` URI, so the standalone HTML
stays portable even when `--out` writes somewhere else; a reference whose file is missing gets a
one-line warning on stderr (naming the attribute and path) and is left as-is — it never fails the
render. `serve` instead rewrites each local reference to a `/__local/<page>/<token>` route and
serves the file from there, confined to exactly the local files that page's own attributes
reference (an unknown page, an unknown token, or a `..` attempt all just miss the allowlist and
404 — nothing outside it is ever served). Either way, previewing a page never uploads anything or
talks to WordPress; that only happens when you run `publish.py draft`.

### `doctor` — environment check

```bash
python3 scripts/preview.py doctor
```

```
python: 3.11.6 (/usr/bin/python3)
cache dir: /Users/you/.cache/divi-page-builder
cached Divi versions: 4.27.3, 4.27.9
jQuery: CDN (no cached WordPress copy)
node: /usr/local/bin/node v24.1.0 (only needed for --exact)
```

Reports Python, the cache dir, cached Divi versions, where jQuery will come from, and whether
Node is present — Node is only needed for `--exact`.

### `fetch-divi` — warm the cache

```bash
ET_USERNAME=you@example.com ET_API_KEY=your-api-key python3 scripts/preview.py fetch-divi 4.27.9
python3 scripts/preview.py fetch-divi latest
```

The only command that talks to Elegant Themes. Downloads and unpacks the requested version (or
the account's latest) into the cache and exits.

### Version selection

Preview on the client's own Divi version so what you see matches what they'll get. Resolution
order, first match wins: `--divi VERSION` → `--tokens tokens.json` (reads `site.divi_version`,
the file `extract_tokens.py` produces) → the newest version already cached → `latest` from
Elegant Themes (needs credentials and network — the fallback of last resort). A tokens file whose
`site.divi_version` is empty (`""`, the version wasn't detected) counts as not giving one: both
previews fall through to the newest cached version, else `latest`, and print a one-line note. A
tokens file with no `site.divi_version` key at all is refused (exit 2): it isn't an
`extract_tokens.py` output, so pass `--divi VERSION` instead.

### Caching

```
$PP_CACHE_DIR (default ~/.cache/divi-page-builder; %LOCALAPPDATA%\divi-page-builder on Windows)
  divi/Divi-<version>/Divi/    unpacked Divi theme (+ the downloaded zip) — shared by both previews
  wordpress/<version>/…        WordPress core, only used by --exact
  sites/wp<wp>-divi<divi>/…    one persistent Playground site per pair, only used by --exact
```

Nothing under `PP_CACHE_DIR` is ever committed to a repo — it's licensed Elegant Themes code and
generated WordPress installs, not source.

Two more environment variables exist but are **internal/test-only**, not part of the normal
workflow:

- `PP_DIVI_CACHE`: overrides just the Divi cache directory, independent of `PP_CACHE_DIR`. Used
  by tests to point at an isolated, pre-seeded Divi cache without touching a real `PP_CACHE_DIR`.
- `PP_ET_ENDPOINT`: overrides the Elegant Themes API base URL. Used by tests to exercise
  `fetch_divi.py`'s error paths (and their credential redaction) against a local stand-in server.
  Never set this for real Divi downloads.

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A `render`ed file's icons are missing/broken when opened over `file://` | An old/manual build referenced fonts by a relative or `file://` path instead of embedding them. | `preview.py render` always embeds icon fonts (and all local assets) as `data:` URIs in standalone output — it never emits a `file://` URL. If you see this, you're not looking at `preview.py`'s own output; `serve` instead maps assets under `/__divi/…`, which needs the server running. |
| `--exact` fails with `preview: … --exact needs Node 20+ …` and exits `2` | Node isn't installed, isn't on `PATH`, or is older than 20 (the message then starts `found Node v18…`). | Install Node ≥ 20 from https://nodejs.org/, or drop `--exact` to use the Python preview. `doctor` reports the Node version it finds and flags one that's too old. |
| `render`/`serve`/`fetch-divi` fails with "Divi is not cached for this version: set ET_USERNAME and ET_API_KEY" | The requested Divi version isn't cached and no credentials are set. | Set `ET_USERNAME`/`ET_API_KEY` (Elegant Themes account → API), or use a version that's already cached (`doctor` lists them). |
| A download fails with `HTTP 429` / "rate-limited" | Elegant Themes' rate limit (~15 calls / 5 min). | Wait a few minutes. A cached version never calls the API, so this only affects fetching a *new* version. |
| `serve` returns a `500` page with a Python traceback | The `.txt` page failed to render (bad encoding, a renderer bug). | The traceback is printed on the page itself and to stderr; the server keeps running and other pages keep serving. Fix the page (or file a bug) and reload — no restart needed. |
| The coverage summary says "use `--exact`" for a module | The Python renderer doesn't implement that module (see [§3](#3-supported-modules)). | Add `--exact` to see it rendered by real Divi. |
| The coverage summary says "needs the live site's data" / "check the WordPress draft preview" | The module shows the client's own posts, menus, media, comments or widgets — neither preview has a real site behind it. | Publish a draft (`scripts/publish.py draft`) and check it there; `--exact` won't help (see [§3](#3-supported-modules)). |
| Fonts/images look wrong or missing in either preview | No network access, so Google Fonts and remote content images can't be fetched. | Expected without network — the page still renders with fallback fonts and no image. Reconnect and re-render/reload to see them. |

### `--exact` (Playground)

These apply specifically when `--exact` runs `scripts/preview/preview.mjs` on WordPress
Playground:

| Symptom | Cause | Fix |
|---|---|---|
| First boot after `npx` installs the CLI takes ~25–30 s | Cold `npx` install of the pinned `@wp-playground/cli` package (mostly PHP WebAssembly builds, ~600 MB). | One-time cost. Subsequent boots are ~3 s. |
| `render`/`serve` boot fails offline with `fetch failed` | A blueprint or CLI flag tried to resolve a WordPress version against `api.wordpress.org`. | Shouldn't happen — `preview.mjs` downloads WordPress itself once and boots with `install-from-existing-files-if-needed` specifically to avoid this. If you see it, the WordPress version isn't cached yet and there's no network. |
| A boot redirects to `wp-admin/admin.php?page=et_onboarding` | Divi 4.27's onboarding screen fires on `after_switch_theme`, which the blueprint's `activateTheme` step triggers on every boot. | Already handled: the mu-plugin unhooks `et_onboarding_trigger_redirect` during preview requests. If you see this, the mu-plugin mount may be missing or stale — re-run fresh. |
| Rendered fonts look slightly different from the live site | Divi's "inline Google Fonts" mode fetches font CSS server-side with a non-browser user agent, which can return TTF instead of the WOFF2 a browser gets. | Already handled: the mu-plugin turns that option off for preview requests. If you still see a difference, check network access — without it, fonts fall back to system fonts entirely. |
| `npx` seems to hang for ~70 s before failing | `npx` tried to revalidate the pinned CLI version against the npm registry while offline. | Already handled: `preview.mjs` always passes `--prefer-offline`. If you invoke the Playground CLI directly (not through `preview.mjs`), add it yourself. |
| A stray Playground server keeps a port busy after Ctrl-C or a crash | `serve`'s child process wasn't cleaned up. | `preview.mjs` kills the whole process group on `SIGINT`/`SIGTERM`/exit; if one is still running, find it with `lsof -i :9400` (or your `--port`) and kill it manually. |
| Credentials show up somewhere they shouldn't | This would be a bug. | `ET_USERNAME`/`ET_API_KEY` are read only from `process.env`, used only in request URLs, and every error message that could echo a URL redacts them first. File an issue if you find a counterexample. |

**Order: local preview first, WordPress draft second.** The user approves the local preview before anything
is pushed; only then does the WordPress draft preview (`scripts/publish.py draft`) serve as the final check
for anything neither preview can show: client Customizer settings, global colors/presets, the
real site header/menu, plugins, a child theme, and any content that needs the live site's data.
Use `preview.py` for fast, portable, offline-capable iteration on a layout's own builder markup
and styling; use `--exact` to confirm a specific module or feature against real Divi; use a draft
on the client's own site to confirm the final, fully-dressed page.
