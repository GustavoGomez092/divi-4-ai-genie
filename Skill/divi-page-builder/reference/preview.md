# Preview on WordPress Playground

Everything on this page was verified in `research/playground-spike.md` (2026-09-24, macOS
arm64, Node 24.1.0) and confirmed again by `tests/test_preview.py` against a real Divi 4.27.9
install and a live page. `scripts/preview/preview.mjs` is the shipped tool.

> This is the **exact** preview: real Divi running in real WordPress. A future pure-Python
> renderer becomes the default, faster preview; this tool is what checks that renderer's
> output and is invoked from it as `--exact`. Nothing here changes that plan — it documents
> the tool as it ships today.

## 1. What it is

Real WordPress + the real Divi 4 theme, running in WebAssembly PHP (WordPress Playground) with
a SQLite database. There is no MySQL, no LocalWP, no Docker, and no persistent WordPress
install on the machine beyond the tool's own cache. Nothing is ever written to a client's
site: a mu-plugin renders your layout as a **fake, in-memory page** inside a disposable local
WordPress instance, and nothing is saved to any database that matters.

## 2. Requirements

- **Node ≥ 20** (tested on 24.1) with `npx` on PATH — needed for the global `fetch` API.
- **`unzip` or `tar`** (bsdtar) to unpack the Divi and WordPress zips.
- **About 1–1.2 GB of free disk**: the Playground CLI's own npm install (~600 MB, mostly PHP
  WebAssembly builds), WordPress core (~114 MB), and each cached Divi version (~85 MB).
- **Elegant Themes credentials**, only the first time a given Divi version is used. After that
  it's cached and no credentials or network access are needed for that version.

Check all of this at once:

```bash
node scripts/preview/preview.mjs doctor
```

```
node: v24.1.0
npx: found
unzip: found
tar: found
cache dir: /Users/you/.cache/divi-page-builder
cached Divi versions: 4.27.3, 4.27.9
cached WordPress versions: 7.1.2
```

Exit code `0` means usable; `1` means something required (Node < 20, or neither `unzip` nor
`tar`) is missing.

## 3. Commands

### `serve` — a live, reloadable preview server

```bash
node scripts/preview/preview.mjs serve --pages ./drafts --divi 4.27.9
```

Boots WordPress + Divi once and prints one URL per `./drafts/<name>.txt`:

```
http://127.0.0.1:9400/?pp_preview=landing-page
```

Every request re-reads the `.txt` file from disk, so editing the layout and reloading the page
shows the change immediately — no restart needed. `Ctrl-C` stops the server (and the whole
process group it spawned).

### `render` — a single self-contained HTML file

```bash
node scripts/preview/preview.mjs render drafts/landing-page.txt --out landing-page.html --divi 4.27.9
```

Boots, renders one layout, inlines local CSS/JS and local web fonts as `data:` URIs so the
file still works after the server (and the network) are gone, writes it, and shuts down. This
is what an AI agent should call to hand back a preview file. It is also the command Task 23's
Python renderer calls as its `--exact` ground truth.

### `fetch-divi` — warm the cache

```bash
ET_USERNAME=you@example.com ET_API_KEY=your-api-key node scripts/preview/preview.mjs fetch-divi 4.27.9
node scripts/preview/preview.mjs fetch-divi latest
```

The only command that talks to Elegant Themes. Downloads and unpacks the requested version
(or the account's latest) into the cache and exits. Run it once per Divi version you'll ever
need; `serve` and `render` never call the API for a version that's already cached.

### `doctor` — environment check

See §2. Also useful to see what's already cached before deciding whether a `render` will need
network access.

## 4. Version selection

Preview on the **client's own Divi version** so what you see matches what they'll get:

```bash
node scripts/preview/preview.mjs render page.txt --out page.html --tokens tokens.json
```

`tokens.json` is the file `extract_tokens.py` produces (Task 12); its `site.divi_version` is
read automatically.

Resolution order, first match wins:

1. `--divi VERSION` (explicit override)
2. `--tokens tokens.json` → `site.divi_version`
3. the newest Divi version already in the cache
4. `latest` from Elegant Themes (needs credentials and network — the fallback of last resort)

**A cached version never triggers an Elegant Themes API call.** The API rate-limits at about
15 calls per 5 minutes, so once a version is cached, every subsequent `serve`/`render` for it
is fully offline.

## 5. Caching and offline

```
$PP_CACHE_DIR (default ~/.cache/divi-page-builder; %LOCALAPPDATA%\divi-page-builder on Windows)
  divi/Divi-<version>/Divi/          unpacked Divi theme (+ the downloaded zip)
  wordpress/<version>/wordpress/     pristine WordPress core, downloaded once
  sites/wp<wp>-divi<divi>/wordpress/ one persistent site per (WordPress, Divi) pair (SQLite DB inside)
```

Nothing under `PP_CACHE_DIR` is ever committed to a repo — it's licensed Elegant Themes code
and generated WordPress installs, not source.

After the first `render` or `serve` for a given Divi + WordPress pair (which downloads Divi,
WordPress, and the Playground CLI's npm package), **everything works fully offline**: verified
in the spike with all outbound network blocked. The only things that still need network to
*look* right afterward are remote Google Fonts and remote images referenced by URL — the page
renders correctly without them, just with fallback fonts and missing images.

## 6. Fidelity and limits

- **Builder markup and CSS are identical to real Divi.** The spike measured the `.et-l`
  builder markup byte-identical (31,755 chars) and 2,064 of 2,064 builder CSS declarations
  identical against a live page, with 0 missing — because it's the same Divi PHP code
  actually running and generating the same output, not a re-implementation.
- **It uses stock Divi settings.** The client's Customizer values, global presets, and global
  colors are **not** applied — there is no client settings bundle in this tool (by design; see
  the skill's spec). A page that uses global colors or presets will preview with Divi's
  defaults for anything not set directly on the module.
- **The site header and menu are the preview site's own**, not the client's — a fresh
  Playground WordPress has no client pages, so Divi's fallback menu differs. This is the only
  visual difference the spike measured against a live page (about 0.02–0.04% of pixels, all in
  the header nav band).
- **Animations need JavaScript** — a plain screenshot or a static reading of the HTML won't
  show them; open the page in a browser (`serve`) to see them run.
- **Fonts and images need network to *look* right.** Google Fonts and remote images referenced
  by URL only render correctly with network access; the page still renders (with fallback
  fonts / no image) without it.

**The WordPress draft preview is the authoritative visual check** for anything this tool can't
show: client Customizer settings, global colors/presets, the real site header and menu, and
plugins or a child theme. Use this tool for fast, portable, offline-capable iteration on a
layout's own builder markup and styling; use a draft on the client's own site (or a LocalWP
mirror) to confirm the final, fully-dressed page.

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `fetch-divi`/`render`/`serve` fails with "Divi is not cached for this version: set ET_USERNAME and ET_API_KEY" | The requested Divi version isn't cached yet and no credentials are set. | Set `ET_USERNAME`/`ET_API_KEY` (Elegant Themes account → API), or use a version that's already cached (`doctor` lists them). |
| A download fails with "API key is not valid" or "Subscription is not active" | Bad or expired Elegant Themes credentials. | Check the credentials in the Elegant Themes account (Divi doesn't validate the *username* on the availability check, only on download). |
| A download fails with `HTTP 429` | Elegant Themes' rate limit (~15 calls / 5 min). | Wait a few minutes. Cached versions never call the API, so this only affects fetching *new* versions. |
| `render`/`serve` boot fails offline with `fetch failed` | A blueprint or CLI flag tried to resolve a WordPress version against `api.wordpress.org`. | Shouldn't happen with this tool — `preview.mjs` downloads WordPress itself once and boots with `install-from-existing-files-if-needed` specifically to avoid this. If you see it, the WordPress version isn't cached yet and there's no network. |
| First boot after `npx` installs the CLI takes ~25–30 s | Cold `npx` install of the pinned `@wp-playground/cli` package (mostly PHP WebAssembly builds, ~600 MB). | One-time cost. Subsequent boots are ~3 s. |
| A `render`/`serve` boot redirects to `wp-admin/admin.php?page=et_onboarding` | Divi 4.27's onboarding screen fires on `after_switch_theme`, which the blueprint's `activateTheme` step triggers on every boot. | Already handled: the mu-plugin unhooks `et_onboarding_trigger_redirect` during preview requests. If you see this, the mu-plugin mount may be missing or stale — re-run `render`/`serve` fresh. |
| Rendered fonts look slightly different from the live site | Divi's "inline Google Fonts" mode fetches font CSS server-side with a non-browser user agent, which can return TTF instead of the WOFF2 a browser gets. | Already handled: the mu-plugin turns that option off for preview requests, so fonts are requested the same way a live browser requests them. If you still see a difference, check network access — without it, fonts fall back to system fonts entirely. |
| `npx` seems to hang for ~70 s before failing | `npx` tried to revalidate the pinned CLI version against the npm registry while offline. | Already handled: `preview.mjs` always passes `--prefer-offline`. If you invoke the Playground CLI directly (not through `preview.mjs`), add it yourself. |
| A stray Playground server keeps a port busy after Ctrl-C or a crash | `serve`'s child process wasn't cleaned up. | `preview.mjs` kills the whole process group on `SIGINT`/`SIGTERM`/exit; if one is still running, find it with `lsof -i :9400` (or your `--port`) and kill it manually. |
| Credentials show up somewhere they shouldn't | This would be a bug. | `ET_USERNAME`/`ET_API_KEY` are read only from `process.env`, used only in request URLs, and every error message that could echo a URL redacts them first. File an issue if you find a counterexample. |
