---
name: divi-page-builder
description: Use when the user says "Divi Genie", "Divi 4 AI Genie" or "Divi 5 AI Genie", or when creating a new Divi 4 or Divi 5 page, landing page or section, editing an existing Divi page's copy, sections or styling, matching new content to a Divi site's existing design, or when Divi et_pb_ shortcode, wp:divi/ block markup or post_content must be written, checked, previewed or pushed to WordPress.
---

# Divi Page Builder (Divi 4 and Divi 5 AI Genie)

Write Divi pages as the exact `post_content` Divi stores (raw shortcode on Divi 4, `wp:divi/*` blocks on Divi 5), styled with the target site's own design tokens, and validated before anything is pushed. There are no templates: every section is composed from documented fields.

**Not for:** Theme Builder templates, WooCommerce product layouts.

## Workflow
1. **Which Divi?** Read `site.divi_major` in the site's `tokens.json`, or run `python3 scripts/divi_format.py site URL`. **Divi 5:** use the Divi 5 files of the reference index (`reference/divi5/`, `recipes/divi5/`) at every step below. **Divi 4:** the Divi 4 files. The scripts take either format.
2. **Intake:** get the content brief, the site URL, and whether this is a new page or an edit. For an edit, fetch the current page (`reference/publishing.md` → "6. Edit an existing page") and save it as `original.txt`.
3. **Tokens:** reuse the site's `tokens.json` if you have one; otherwise run `python3 scripts/extract_tokens.py --key "NAME" --page ID --out tokens.json` (`publish.py keys` lists the available sites; or `--site URL --user USER` with the password in `WP_APP_PASSWORD`). See `reference/design-tokens.md` (§7 for Divi 5).
4. **Plan:** map the brief to recipes through the recipe index (`recipes/README.md`; Divi 5: `recipes/divi5/README.md`). Show the user the section outline and get a yes before writing.
5. **Compose:** for each section, follow its recipe. Look up every module in `reference/modules/<slug>.md` (Divi 5: its page, linked from `reference/divi5/modules/README.md`), and take every color, font, spacing and button style from `tokens.json`.
6. **Validate:** `python3 scripts/validate.py page.txt --tokens tokens.json` (add `--baseline original.txt` for edits). Repeat until there are 0 errors; read every warning, including the heading-outline ones. For a single section, add `--fragment`.
7. **Preview, then stop for approval:** put `page.txt` in its own folder and run `python3 scripts/preview.py serve --pages DIR --tokens tokens.json` (it keeps running; local `./` images show without uploading anything). Give the user the printed `http://127.0.0.1:PORT/<name>` link. If a server can't stay running, use `render page.txt --tokens tokens.json --out preview.html` and give them the file path instead. Divi 4: if the coverage report lists unsupported modules, or something looks off, add `--exact` (real Divi in Playground; needs Node 20+); Customizer and preset styling looks generic. Divi 5 pages always render on real Divi 5 in Playground (Node 20+) with the site's global colors, variables and presets from `--tokens`. See `reference/preview.md`. **Then end your turn and wait for the user's reply.** Apply their changes, re-validate, and repeat until they approve the preview.
8. **Publish, only after the user approves the local preview:** `python3 scripts/publish.py draft page.txt --key "NAME" --title "…"` (or `--site URL --user USER` with `WP_APP_PASSWORD`) uploads local images and saves a **draft** (it validates first). Share the printed `preview_url` so the user can check the page with the site's real theme settings. After they approve that, run `publish.py publish --page-id ID --yes` (`reference/publishing.md`).

## Hard rules
- **Nothing touches the site before the user approves the local preview.** Don't run `publish.py media`, `draft` or `publish` (no image upload, no draft) until the user has replied approving the step-7 preview. An approved outline is not an approved page, and your own screenshots are not approval.
- **Never invent attributes.** An attribute not on the module's page (or in its linked design families) does not exist; `validate.py` reports it as `E_UNKNOWN_ATTR` (`E5_UNKNOWN_ATTR`).
- **Headings:** exactly one H1 per page, and no skipped heading levels. `validate.py` enforces this (`E_MULTIPLE_H1`, `W_NO_H1`, `W_HEADING_SKIP`).
- **Images:** upload to the site's Media Library and use that URL. Never hotlink. Always write `alt`.
- **Edits:** use `scripts/page_edit.py`. Everything you weren't asked to change stays byte-identical.
- **Testimonials, reviews, prices and stats:** only as provided in the brief. Never invent them.
- **Always push as a draft first.**
- **Never print or write credentials.** They come from `keys.json` (outside the repo, `chmod 600`) or env `WP_APP_PASSWORD`; `ET_USERNAME` / `ET_API_KEY` come from env or keys.json's `elegant_themes` section, env winning.

**Divi 4 only**
- **Styles:** use inline attributes, or `_module_preset` UUIDs listed in `tokens.json`. Never use preset UUIDs from anywhere else.
- **Escaping inside attribute values:** `"` → `%22`, `[` → `%91`, `]` → `%93` (`reference/page-format.md`).

**Divi 5 only**
- **Write only `wp:divi/*` blocks, in canonical JSON** (build them with `scripts/divi5_blocks.py`). Never write Divi 4 shortcode on a Divi 5 site.
- **`builderVersion`:** the site's `site.divi_version` on every block you create; leave it unchanged on blocks you edit.
- **Ids:** reference `gcid-…`/`gvid-…` variables and preset ids only from `tokens.json`. Omit `modulePreset` to get the site's default preset.
- **Literal brackets in text:** `&#91;` and `&#93;`.
- **Nothing Divi silently ignores:** fix every validator finding for a value `reference/divi5/page-format.md` lists as ignored (`E5_UNITLESS_LENGTH`, `E5_GRADIENT_DISABLED`, `W5_BARE_FONT`, `W5_LEGACY_ATTR`, `W5_NO_EFFECT`…).
- **Drafts only via `publish.py`:** it sets the builder meta (`_et_pb_use_builder`) a plain REST save can't.

## Scripts
All scripts detect the page format and handle Divi 4 and Divi 5.

| script | purpose |
|---|---|
| `scripts/divi_format.py` | `site URL` → the site's Divi version; `content PAGE` → shortcode, blocks or mixed |
| `scripts/validate.py` | structure, heading outline, attributes, value formats, tokens; `--baseline` for edits; `--fragment`; `--json` |
| `scripts/extract_tokens.py` | site design tokens via REST (Application Password) + public CSS |
| `scripts/page_edit.py` | outline / extract / replace / insert-after / insert-before / set-attr / delete, surgically |
| `scripts/preview.py` | local preview: `render`, `serve` (live reload), `doctor`, `fetch-divi`; `--exact` hands Divi 4 off to Playground |
| `scripts/preview/preview.mjs` | real-Divi preview in WordPress Playground (Node 20+): Divi 4 `--exact`, every Divi 5 page |
| `scripts/publish.py` | `fetch` / `media` / `draft` / `publish` / `keys` over REST with an Application Password |

## Reference index
| Divi 4 | Divi 5 | read it when |
|---|---|---|
| `reference/page-format.md` | `reference/divi5/page-format.md` | writing any page: grammar, escaping, what's stored where |
| `reference/structure.md` | `reference/divi5/structure.md` | choosing section, row and column layouts; parent/child modules |
| `reference/value-formats.md` | `reference/divi5/value-formats.md` | writing colors, fonts, spacing, icons, responsive/hover/sticky values |
| `reference/design-families.md` | `reference/divi5/design-families.md` | styling: background, font, border, shadow, spacing, animation… |
| `reference/modules/README.md` | `reference/divi5/modules/README.md` | finding a module; it links one page per module listing all of its fields |
| `reference/icons.md` | | picking an icon: name → exact `font_icon`/`button_icon` value |
| `recipes/README.md` | `recipes/divi5/README.md` | planning and composing: how recipes map tokens to fields, and the **recipe index** of every section, page and edit recipe (`sections/`, `pages/`, `edits/`) with when to use each |

Both versions:

| file | read it when |
|---|---|
| `reference/design-tokens.md` | extracting and applying a site's styles |
| `reference/publishing.md` | uploading images, creating drafts, editing live pages |
| `reference/preview.md` | local preview setup and limits |
