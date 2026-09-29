# Divi 4 AI Genie (now with Divi 5)

Divi 4 AI Genie is an AI skill that builds and edits **Divi 4 and Divi 5** pages in your client's own
style. It detects which Divi the site runs, reads the site's fonts, colors and spacing (on Divi 5, its
global colors, design variables and presets too), writes the page in Divi's native format (shortcode
on Divi 4, `wp:divi/*` blocks on Divi 5), checks it for errors and shows you a local preview. Only after you approve does it save a WordPress draft,
and it never publishes without your OK.

Ask for it by name ("use Divi Genie to…", "Divi 5 AI Genie…") or just describe a Divi page task; either way
the agent picks it up.

It's a skill, not a plugin: you install it into an AI coding agent (Claude Code, claude.ai, or any
agent that can read a `SKILL.md` file), and the agent uses it to write, check and push Divi
pages for you, in a terminal, next to your other tools.

## Table of contents

- [What it is](#what-it-is)
- [Requirements](#requirements)
- [Install](#install)
- [Connect your sites (keys.json)](#connect-your-sites-keysjson)
- [Using it](#using-it)
- [Command reference](#command-reference)
- [Safety](#safety)
- [What's in the box](#whats-in-the-box)
- [Limitations](#limitations)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

## What it is

There are no fill-in-the-blank templates. Every section is composed field-by-field from documented
module attributes, styled from the target site's own extracted design tokens, and validated against
Divi's real module schema before anything is written or shown.

**What it's for:**
- **Divi 4** sites, authored as raw `et_pb_*` shortcode (the exact `post_content` Divi's own
  builder stores).
- **Divi 5** sites, authored as `<!-- wp:divi/… -->` blocks in WordPress's canonical JSON (again
  exactly what Divi 5 stores), with their own module reference, recipes and validator. Colors,
  spacing and presets are *referenced* from the site's design system (global colors, design
  variables, presets) by id rather than copied. It never writes Divi 4 shortcode on a Divi 5 site,
  or blocks on a Divi 4 site; `publish.py` refuses either mismatch.

**What it's not for:**
- **Theme Builder** templates (global headers/footers/archive layouts).
- **WooCommerce** product page layouts.

### The end-to-end workflow

1. **Intake** — the AI gets the content brief, the site URL, and whether this is a new page or an
   edit, and detects whether the site runs Divi 4 or Divi 5 (everything after follows that
   version's reference and recipes). For an edit, it fetches the page's current content first.
2. **Tokens** — it reuses an existing `tokens.json` for the site, or extracts one from the site's
   own live pages (colors, fonts, spacing, per-module styles).
3. **Outline approval** — it maps your brief onto a set of section recipes and shows you the
   planned outline before writing anything. **You approve the outline before it writes a single
   module.**
4. **Compose** — it writes each section's shortcode (Divi 4) or blocks (Divi 5), pulling every color, font, spacing value and
   button style from `tokens.json` rather than inventing one.
5. **Validate** — it checks the page against Divi's module schema (structure, attributes, value
   formats, heading outline) until there are zero blocking errors.
6. **Local preview** — it renders the page to a local HTML file or a live-reload server and gives
   you the link. **Nothing has touched the site yet.** It waits for you to approve what you see.
7. **WordPress draft** — only after you approve the local preview does it upload images and save a
   real WordPress **draft**, and hands you its `preview_url` so you can check it with the site's
   actual theme, plugins and Customizer settings.
8. **Publish, only with approval** — the page goes live only after you explicitly approve that
   draft and the AI runs the publish step with your confirmation.

## Requirements

| Requirement | Notes |
|---|---|
| **Python 3.10+** | Standard library only — no `pip install` for anything the skill ships. |
| **Node 20+** | Needed for every **Divi 5** preview (Divi 5 pages always render on the real Divi 5 theme in WordPress Playground), and for `--exact` on Divi 4. The default Divi 4 preview doesn't need it. |
| **A Divi 4 or Divi 5 site with the REST API reachable** | The standard WordPress REST API (`/wp-json/wp/v2/...`), enabled by default. Divi 5 support was built and tested against Divi 5.13.1. |
| **An Elegant Themes account** (username + API key) | Lets the previewer download a real copy of Divi once; after that it's cached and works offline for that version. The API key is in your Elegant Themes Members Area → **Account → API Key**. Put it in `keys.json`'s `elegant_themes` section (below), or env `ET_USERNAME`/`ET_API_KEY`. |

## Install

### Claude Code

Skills load at session start, so add the folder once, then start (or restart) Claude Code.

**Personal skill** (available in every project):

```bash
ln -s /path/to/divi-4-ai-genie/Skill/divi-page-builder ~/.claude/skills/divi-page-builder
```

(or copy the folder instead of symlinking it, if you'd rather not track the source repo's location).

**Project-level skill** (available only in one project):

```bash
mkdir -p .claude/skills
cp -r /path/to/divi-4-ai-genie/Skill/divi-page-builder .claude/skills/divi-page-builder
```

### claude.ai

1. Zip the `Skill/divi-page-builder` folder (zip the folder itself, not just its contents).
2. In claude.ai: **Settings → Capabilities → Skills**, and upload the zip.

Two caveats specific to claude.ai's sandboxed environment:
- The sandbox may block outbound connections to your WordPress sites or to Elegant Themes, which
  would prevent token extraction, preview downloads, and publishing from working there.
- `keys.json` (your site credentials, see below) lives on **your machine**, not in claude.ai —
  plan on running the parts of the workflow that touch real credentials somewhere that can read
  that file.

### Other agents

Point any other agent capable of reading instructions and running Python/Node at
`Skill/divi-page-builder/SKILL.md` — it's the entry point and links to every other reference file
the skill needs.

### First-run check

Once the skill is installed, verify the local environment before using it for real:

```bash
cd Skill/divi-page-builder
python3 scripts/preview.py doctor
```

This reports the Python interpreter, the cache directory, which Divi versions are already cached,
whether Node is present (needed for `--exact` and for Divi 5 pages), and whether Elegant Themes credentials are
available and where from (`env`, `keys.json`, or `none`). Then warm the cache with a real Divi
download, with your Elegant Themes credentials in `keys.json`'s `elegant_themes` section (see
[Connect your sites](#connect-your-sites-keysjson) below):

```bash
python3 scripts/preview.py fetch-divi latest     # Divi 4
python3 scripts/preview.py fetch-divi latest5    # Divi 5 (about 35 MB), if you work on Divi 5 sites
```

Or, without a `keys.json`, env vars work the same way (and always take priority over the file):

```bash
ET_USERNAME=you@example.com ET_API_KEY=your-api-key python3 scripts/preview.py fetch-divi latest
```

After the first download of a given Divi version, that version is cached and previews work fully
offline.

## Connect your sites (keys.json)

The skill authenticates to WordPress with an **Application Password**, never your account's login
password.

### 1. Create an Application Password

On the client's WordPress site: **Users → Profile → Application Passwords**, give it a name, click
**Add Application Password**, and copy the generated password immediately — WordPress shows it
to you exactly once.

### 2. Create `keys.json`

```json
{
  "elegant_themes": {
    "username": "you@example.com",
    "api_key": "your-elegant-themes-api-key"
  },
  "keys": [
    {
      "name": "Client A",
      "site": "https://client.com",
      "user": "seo-bot",
      "key": "xxxx xxxx xxxx xxxx xxxx xxxx"
    }
  ]
}
```

Both top-level sections are optional; a file may hold either one or both.

Every `keys` entry needs `name`, `site`, `user` and `key`, each a non-empty string; other keys in
an entry are allowed and ignored. Entry names must be unique, case-insensitively (JSON Schema on
its own can't express that uniqueness rule, so `wp_keys.py` enforces it itself and refuses a
duplicate).

`elegant_themes`, if present, needs `username` and `api_key`, each a non-empty string — find your
API key in the Elegant Themes Members Area → **Account → API Key**. It's used to download Divi
for the local preview (`fetch-divi`, and `render`/`serve`/`doctor` whenever a version isn't
already cached). Env vars `ET_USERNAME`/`ET_API_KEY` always override this section when both are
set; leave the section out entirely to rely on the env vars only.

<details>
<summary>JSON Schema (draft 2020-12)</summary>

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "divi-page-builder keys.json",
  "type": "object",
  "properties": {
    "elegant_themes": {
      "type": "object",
      "required": ["username", "api_key"],
      "properties": {
        "username": { "type": "string", "minLength": 1 },
        "api_key": { "type": "string", "minLength": 1 }
      },
      "additionalProperties": true
    },
    "keys": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "site", "user", "key"],
        "properties": {
          "name": { "type": "string", "minLength": 1 },
          "site": { "type": "string", "format": "uri", "minLength": 1 },
          "user": { "type": "string", "minLength": 1 },
          "key": { "type": "string", "minLength": 1 }
        },
        "additionalProperties": true
      }
    }
  },
  "additionalProperties": true
}
```

Note: `name` values must also be unique case-insensitively across the array — not expressible in
JSON Schema, so it's enforced in code (`scripts/wp_keys.py`), which raises an error naming both
conflicting entries if it finds a duplicate.

</details>

### 3. Where the file lives

Resolved in this order, first match wins:

1. `--keys PATH` passed to a script.
2. The `DIVI_KEYS_FILE` environment variable.
3. The default: `~/.config/divi-page-builder/keys.json`.

Whichever path you use: `chmod 600` it, and never commit it or put it inside this skill or any
repo — it belongs only on the machine that runs the scripts. If it's readable by other users on a
POSIX system, the scripts print a warning (`keys.json is readable by other users; run chmod 600
<path>`) rather than silently proceeding. This repo's `.gitignore` already excludes any file named
`keys.json`.

### 4. Using it

List what's configured (never prints a key value or the Elegant Themes api_key):

```bash
python3 scripts/publish.py keys
```

This prints `{"keys": [...], "elegant_themes": {"username": "...", "configured": true}}` (or
`{"configured": false}` when the file has no `elegant_themes` section).

Select a site by name (case-insensitive):

```bash
python3 scripts/publish.py draft page.txt --key "Client A" --title "…"
```

Or match by `--site` (normalized scheme+host, trailing slash ignored), adding `--user` only if
more than one entry matches the same site:

```bash
python3 scripts/publish.py draft page.txt --site https://client.com --user seo-bot --title "…"
```

### Env fallback

With no `keys.json` at all, `--site`/`--user` plus the environment variable `WP_APP_PASSWORD`
still work exactly as before, for backward compatibility:

```bash
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
python3 scripts/publish.py draft page.txt --site https://client.com --user seo-bot --title "…"
```

### Revoking a key

Revoke it on the site itself: **Users → Profile → Application Passwords**, then delete the
corresponding entry from your `keys.json`.

## Using it

Example prompts you can give the AI once the skill is installed. Name the `keys.json` entry to use,
and, for a new site, an existing page built with Divi whose design the new page should match:

- *"Using my keys at ~/.config/divi-page-builder/keys.json, build a new landing page on 'Client A'
  called 'Custom Deck Building in Phoenix', matching the design of page 42. Here's the content: …"*
- *"Build a new landing page for our emergency plumbing service in Miami, matching client.com's
  existing style."*
- *"Edit the About page on client.com — update the second paragraph to mention our new 24/7
  hotline."*
- *"Add a testimonials section to the homepage, right after the hero."*
- *"Divi 5 AI Genie: build a PPC landing page for 'Client B' (a Divi 5 site) in its global colors and
  presets."* (The version is detected either way; naming it just makes the request explicit.)
- *"Restyle the pricing section on client.com to match its current brand tokens — it looks like it
  drifted off-brand."*

What the AI asks you for, and when:

1. It shows you a **section outline** before writing any shortcode or blocks, and waits for a yes.
2. It gives you a **local preview link** (a file path or a `http://127.0.0.1:PORT/...` URL) and
   stops — nothing has touched the site yet. It applies any changes you ask for and re-shows the
   preview until you approve it.
3. Only after that approval does it save a WordPress draft and give you the draft's `preview_url`
   so you can check it in the site's real theme.
4. It publishes only after you explicitly approve that draft.

## Command reference

Run any script with `--help` (and any subcommand with its own `--help`) for the full flag list —
this table covers the common path. Every script detects the page format (Divi 4 shortcode or Divi 5
blocks) and handles both.

| Script | Key subcommands / flags | Purpose |
|---|---|---|
| `scripts/divi_format.py` | `site URL`, `content PAGE` | Which Divi a site runs (`{divi_version, divi_major, evidence}`, from public files only), and whether a page file is `shortcode`, `blocks`, `mixed` or `empty`. |
| `scripts/extract_tokens.py` | `--key NAME` / `--site URL --user USER` (env `WP_APP_PASSWORD`), `--page ID` (repeatable), `--shortcode-file FILE --url URL` (offline), `--out FILE` | Extract a site's design tokens (colors, fonts, spacing, module styles; on Divi 5 also the global colors, design variables and preset ids) into `tokens.json`, from live REST pages or an offline page file. |
| `scripts/validate.py` | `PAGE`, `--tokens FILE`, `--baseline FILE`, `--site-url URL`, `--fragment`, `--json` | Validate a page against Divi's module schema (the Divi 4 or Divi 5 one, by format): structure, heading outline, attributes, value formats, and (with `--tokens`) off-brand values. `--baseline` only fails on *new* errors versus an original page. |
| `scripts/page_edit.py` | `PAGE outline` / `extract PATH` / `replace PATH FILE` / `insert-after PATH FILE` / `insert-before PATH FILE` / `set-attr PATH NAME VALUE` / `delete PATH`, `--out FILE` | Surgical edits to one node of a page by path (e.g. `et_pb_section[1] > et_pb_row[0] > et_pb_column[2]`); everything outside the targeted node stays byte-identical. |
| `scripts/preview.py` | `render PAGE [--out FILE]`, `serve [--pages DIR] [--port N]`, `doctor`, `fetch-divi VERSION`; `render`/`serve`/`doctor`/`fetch-divi` all take `--keys PATH`, and `render`/`serve` also take `--tokens FILE`, `--divi VER`, `--no-js`, `--exact` | Default (pure-Python, stdlib-only) local preview: one standalone HTML file, or a live-reload server. `--exact` hands off to the Node preview for full fidelity, passing it the same resolved Elegant Themes credentials. |
| `scripts/preview/preview.mjs` | `serve [--pages DIR] [--port N]`, `render LAYOUT.txt [--out FILE]`, `fetch-divi VER\|latest`, `doctor`; both take `--divi VER` / `--tokens FILE` | The real Divi theme running on WordPress Playground (Node 20+, WebAssembly PHP). Invoked automatically by `preview.py ... --exact` on Divi 4 and for every Divi 5 page (seeded with the site's global colors, variables and preset CSS from `--tokens`). |
| `scripts/publish.py` | `keys`, `fetch --page-id ID --out FILE`, `media FILE --alt TEXT`, `draft PAGE --title T [--page-id ID] [--baseline F] [--tokens F] [--page-fields JSON]`, `publish --page-id ID --yes [--content F] [--status publish]` | Push to WordPress over REST: list configured sites, fetch a page's current content, upload one image, save a draft (validates + uploads local images first; on Divi 5 also sets the builder meta a plain REST save can't), and publish (requires `--yes`). |

## Safety

- **Drafts first, always.** `publish.py draft` only ever creates or updates a page with
  `status: draft`, whether the page is new or already exists.
- **Publish needs explicit approval.** `publish.py publish` refuses (exit 1, no HTTP call) unless
  `--yes` is passed, and the AI only passes it after you've reviewed the draft's `preview_url`.
- **Private and scheduled pages keep their visibility.** `publish --page-id ID` reads the page
  first; for a `private` or `future` (scheduled) page it sends only `content`/`meta` unless you
  pass `--status publish` to deliberately make it public.
- **Edits are validated against the page's current content.** `--baseline` (or, with `--page-id`,
  the page's live `content.raw`) means only *new* errors block an update — pre-existing issues on
  a legacy page don't stop your edit.
- **Credentials are never printed.** `publish.py keys` lists `name`/`site`/`user` only, never the
  password; HTTP error messages include only the method/path and WordPress's own error code —
  never a password or a URL containing one.
- **The right format for the site.** `publish.py draft`/`publish` detect the site's Divi version and
  refuse Divi 4 shortcode on a Divi 5 site (it would render through a degraded legacy path) and
  Divi 5 blocks on a Divi 4 site.
- **The local preview never uploads anything or talks to WordPress.** `preview.py render`/`serve`
  only reads local files (the page, `tokens.json`, local images) and a cached Divi copy — nothing
  is sent to the client's site until `publish.py draft` runs, and that only happens after you
  approve the local preview.

## What's in the box

```
Skill/divi-page-builder/          the product: install this folder as the skill
├── SKILL.md                      entry point: workflow, hard rules, script + reference index
├── reference/                    what every script and shortcode rule means
│   ├── page-format.md            shortcode grammar, escaping, what's stored where
│   ├── structure.md              section/row/column layouts, parent/child modules
│   ├── value-formats.md          colors, fonts, spacing, icons, responsive/hover/sticky values
│   ├── icons.md                  icon name → font_icon/button_icon value
│   ├── design-families.md        background, font, border, shadow, spacing, animation…
│   ├── design-tokens.md          extracting and applying a site's own style
│   ├── publishing.md             uploading images, drafts, editing a live page, keys.json
│   ├── preview.md                local preview setup, fidelity, and limits
│   ├── modules/                  one file per Divi module (64 modules), every field documented
│   └── divi5/                    the Divi 5 counterparts: page-format, structure, value-formats,
│                                  design-families, and modules/ (64 blocks, every attribute path)
├── recipes/
│   ├── README.md                 how a recipe maps tokens to fields, and the recipe index
│   ├── sections/                 19 single-section patterns (hero, CTA, FAQ, pricing, …)
│   ├── pages/                    4 full-page compositions (service landing, PPC, local SEO, …)
│   ├── edits/                    4 edit patterns (change copy, insert/replace a section, restyle)
│   └── divi5/                    the same 27 recipes as Divi 5 blocks, with their own README/index
└── scripts/                      divi_format.py, validate.py, extract_tokens.py, page_edit.py,
                                   preview.py, preview/preview.mjs, publish.py, wp_keys.py, and
                                   their internals (schema/ for Divi 4, schema5/ for Divi 5)

research/                         maintainer tooling: schema extraction, doc generation, fidelity
                                   harness against real Divi (see research/tools/README.md)
tests/                            the test suite (unittest), plus fixtures for valid/invalid pages,
                                   render fidelity, and doc examples
```

## Limitations

- **On Divi 4, the preview uses stock Divi defaults, not the client's Customizer settings or global
  presets.** Neither the default preview nor `--exact` applies the client's Customizer values,
  Global Colors, or global presets — a page that leans on those will look more generic in preview
  than it does live. The WordPress draft preview is the only one that reflects them.
- **Modules that need live site data render as placeholders in both previews.** Anything that
  shows the site's actual posts, projects, menus, comments, media-library galleries or widgets
  (blog/portfolio modules, post navigation, comments, menus, sidebars) has no real content to
  render outside the live site — check the WordPress draft preview for these instead.
- **The schema is Divi 4.27.x.** Module fields and behavior were extracted from a Divi 4.27
  install; a materially different Divi 4 version could have fields this skill doesn't know about
  yet.
- **The Divi 5 schema is Divi 5.13.1.** Divi 5 is still moving; a newer release can add attributes
  (the validator then reports them as unknown) until the schema is regenerated (see
  [Development](#development)). The Divi 5 preview seeds the site's global colors, design variables
  and preset CSS from `tokens.json`, but not its Customizer settings; check the draft's
  `preview_url` for those.
- **Divi 4 content on a Divi 5 site isn't converted.** `publish.py` refuses a shortcode page for a
  Divi 5 site, and token extraction learns nothing from one; convert the page in Divi 5's Visual
  Builder first, then the skill edits its blocks.

## Development

Run the offline test suite from the repo root:

```bash
python3 -m unittest discover -s tests
```

Some tests touch a real local WordPress site (WP-CLI, Application Password creation, a live Divi
install) or the Elegant Themes API and are opt-in:

```bash
PP_LIVE_TESTS=1 python3 -m unittest discover -s tests
```

The Divi 5 live tests (`test_divi5_publish_live`, `test_divi5_tokens_fidelity`, `test_divi5_judge`)
run against a second LocalWP site, `divi-5-test.local` (Divi 5.13.1, site id `fTZ3hcgdI`), with the
same `PP_LIVE_TESTS=1`. They also need that site started: when `http://divi-5-test.local` doesn't
answer they are skipped, so the Divi 4 site alone still gives a clean live run.

Check every `divi` and `divi5` fenced code example in the skill's docs and recipes actually validates:

```bash
python3 research/tools/check_doc_examples.py Skill/divi-page-builder
```

Regenerate the module reference docs after a Divi schema update:

```bash
python3 research/tools/generate_docs.py research/divi-schema Skill/divi-page-builder --notes research/tools/notes
```

(This is one step of a larger after-a-Divi-update sequence — dump the field registry, compile the
validator schema, generate docs, then check examples and run tests — see
`research/tools/README.md` for the full command list.)

After a Divi 5 update, the same sequence runs against `divi-5-test.local`:

```bash
LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH="$HOME/Local Sites/divi-5-test/app/public" \
  research/tools/wp-local.sh --exec='$_SERVER["REQUEST_URI"]="/wp-json/";' \
  eval-file research/tools/divi5/dump-schema.php "$PWD/research/divi5-schema"
python3 research/tools/divi5/build_schema5.py research/divi5-schema research/tools/divi5/families5.json Skill/divi-page-builder/scripts/schema5
python3 research/tools/divi5/generate_docs5.py research/divi5-schema Skill/divi-page-builder --notes research/tools/divi5/notes
python3 research/tools/check_doc_examples.py Skill/divi-page-builder
```

The check covers the `divi` (Divi 4) and `divi5` fenced examples alike.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `render`/`serve`/`fetch-divi` fails: "Divi is not cached for this version: set ET_USERNAME and ET_API_KEY" | The requested Divi version isn't cached yet and no credentials are set. | Add an `elegant_themes` section to `keys.json` (see [Connect your sites](#connect-your-sites-keysjson)), pass `--keys PATH`, set `ET_USERNAME`/`ET_API_KEY` (an Elegant Themes account's API key), or use a version already cached (`preview.py doctor` lists them and reports where its credentials come from). |
| `--exact` fails: "`--exact` needs Node 20+" | Node isn't installed, isn't on `PATH`, or is older than 20. | Install Node ≥ 20 from nodejs.org, or drop `--exact` to use the default Python preview. |
| A download fails with `HTTP 429` / "rate-limited" | Elegant Themes' API rate limit (~15 calls per 5 minutes). | Wait a few minutes; a cached Divi version never calls the API again. |
| Coverage summary says "use `--exact`" for a module | The Python renderer doesn't implement that module yet. | Re-render with `--exact` to see it via the real Divi theme. |
| Coverage summary says "needs the live site's data" | The module shows the client's real posts, menus, media or widgets — neither preview has a real site behind it. | Push a draft (`publish.py draft`) and check it there. |
| `401 Unauthorized` from `publish.py`/`extract_tokens.py` | Wrong username/Application Password, or Application Passwords disabled on that site. | Re-check the Application Password (not the account login password); confirm `wp_is_application_passwords_available()` isn't disabled. |
| `403 Forbidden`, `rest_cannot_edit` | Credentials are valid but that WordPress user lacks `edit_post`/`publish_pages` capability on the target page. | Use an Editor/Administrator account, or grant the missing capability. |
| `draft --page-id` refuses with an error about a live page | The target page is currently `publish`, `future`, or `private` — forcing it back to `draft` would take it offline. | Create a review copy without `--page-id`, get approval, then apply the edit with `publish --page-id ID --content edited.txt --yes` instead. |
| `preview: Divi 5 block pages render on the real Divi 5 theme …`, exit 2 | Node 20+ is missing: Divi 5 pages have no Python preview. | Install Node ≥ 20 (and `fetch-divi latest5` once). |
| `publish.py` refuses: "this is Divi 4 shortcode; the site runs Divi 5" (or the reverse) | The page file's format doesn't match the site's Divi version. | Write the page in the site's format (`python3 scripts/divi_format.py site URL` tells which). |
| `keys.json is readable by other users; run chmod 600 <path>` | The file's permissions allow other local users to read it. | `chmod 600 ~/.config/divi-page-builder/keys.json` (or wherever your `--keys`/`DIVI_KEYS_FILE` points). |
