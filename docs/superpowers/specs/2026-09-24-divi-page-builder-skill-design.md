# Divi Page Builder Skill: Design Spec

- **Date:** 2026-09-24
- **Status:** Approved; Addendum A added 2026-09-24
- **Related research:** `research/divi-ai-findings.md`, `research/divi-schema/`, `research/divi-render-engine.md`

## 1. Goal

SEO strategists and content creators produce content for **pages**, either new landing pages or edits to existing ones, on client WordPress sites built with **Divi 4**. Today a developer builds each page by hand in the Divi Builder so it matches the site's look.

This project delivers a **skill**: a set of Markdown files plus two small scripts that lets any AI author Divi page data directly, in Divi's native format. The result must be visually consistent with the target site's existing design. Pushing the result to WordPress is documented here; the push tooling is a later phase ("connection phase").

### Success criteria
1. From a content brief and a site's `tokens.json`, an AI following the skill produces a page shortcode that passes the validator with zero errors and renders on the site with the site's own fonts, colors, spacing, button styles and presets.
2. Every field of every Divi 4 module (64 modules) is documented, either on the module's page or in a shared design family it links to. A generator check enforces this.
3. Edits to existing pages change only the intended parts: the rest of the shortcode stays byte-identical.
4. The docs and the validator schema regenerate from the Divi source with two commands when Divi updates.

### Non-goals (this spec)
- Premade component or template libraries that get filled with data. That approach was explicitly rejected.
- Push tooling: an MCP server or CLI that creates pages remotely. Only the REST flow is documented here.
- Divi 5 (block-based format). All target sites run Divi 4 (4.27.3 on Interinvestments, 4.27.9 local).
- WooCommerce modules (WooCommerce is not active on the reference install, so they are not in the extracted schema).

## 2. Background findings (established by research)

- **Storage format.** A Divi 4 page is a nested **shortcode string** in `post_content`, for example `[et_pb_section …][et_pb_row …][et_pb_column type="1_2"][et_pb_text …]<p>HTML</p>[/et_pb_text]…`. It is neither JSON nor serialized PHP. The Visual Builder uses JSON only while you edit; `et_fb_ajax_save` (`includes/builder/functions.php:2330`) converts it with `et_fb_process_to_shortcode()` and saves via `wp_update_post()`. Serialized PHP appears only in site-wide options: `et_divi` (theme options) and `et_divi_builder_global_presets_ng` (global presets).
- **Required meta.** `_et_pb_use_builder=on`. It is registered for REST with an auth callback in `includes/builder/feature/BlockEditorIntegration.php:872`. Also written by the builder: `_et_pb_built_for_post_type=page`. Written separately: `_et_pb_page_layout`, which is not registered for REST.
- **The schema is extractable.** When forced to load every module (the `et_builder_should_load_all_module_data` filter), `ET_Builder_Element::get_module_fields('page', $slug)` returns each module's fully expanded field set. This is the same data the Visual Builder uses. Extracted: 64 modules and about 40k field entries, of which about 31.8k are `skip`-type suffix variants. There are 3,876 distinct field names; 367 appear in at least 90% of modules and 1,601 are unique to one module. Each field carries `mobile_options` (responsive), `hover` and `sticky` flags plus `tab_slug`/`toggle_slug` grouping. Script: `research/tools/dump-divi-schema.php`. Output: `research/divi-schema/`.
- **Pushing is proven.** A shortcode written with WP-CLI plus `_et_pb_use_builder=on` renders a fully styled page (local page 11). Per-page CSS is generated into `wp-content/et-cache/<id>/` on the first view.
- **How Divi AI works, for reference only.** It fills premade sections server-side at `ai.elegantthemes.com`. Styles are inlined on every module, so pages render correctly even when the `_module_preset` UUIDs they reference do not exist on the site.

## 3. Architecture

```
Skill/divi-page-builder/                 ← the shipped skill
├── SKILL.md
├── reference/
│   ├── page-format.md
│   ├── structure.md
│   ├── value-formats.md
│   ├── design-families.md
│   ├── publishing.md
│   ├── design-tokens.md
│   └── modules/<slug>.md       × 64 (generated)
├── recipes/
│   ├── README.md
│   ├── sections/<name>.md
│   ├── pages/<name>.md
│   └── edits/<name>.md
└── scripts/
    ├── validate.py
    ├── extract_tokens.py
    ├── divi_shortcode.py         shared parser/serializer used by both scripts
    └── schema/<slug>.json        × 64 (generated) + families.json

research/tools/                          ← maintainer-only, not shipped
├── force-all-modules.php
├── dump-divi-schema.php
├── generate_docs.py            schema → reference/modules/*.md, design-families tables, scripts/schema/*
└── notes/<slug>.md             hand-written gotchas merged into generated module pages
```

- **Language:** Python 3 standard library only, so any AI with a shell can run the scripts with no installs.
- **Progressive disclosure:** `SKILL.md` stays short (workflow, hard rules, index). References and recipes are loaded only when needed.
- **Regeneration:**
  1. `wp --require=force-all-modules.php eval-file dump-divi-schema.php <out>`
  2. `python3 generate_docs.py <schema_dir> <skill_dir>`

## 4. Components

### 4.1 `SKILL.md`
- **Triggers:** building a new Divi page or section, editing an existing Divi page, or matching a Divi site's design.
- **Workflow:** as in §5.
- **Hard rules:**
  - Never invent attributes. Every attribute must exist in the module reference.
  - Use inline design attributes, or preset UUIDs recorded in the site's tokens. Never use foreign preset UUIDs.
  - Follow the escaping rules (§4.2).
  - Upload images to the site; never hotlink.
  - Exactly one H1 per page.
  - Always push as a draft first.
- **Index:** a one-line description per reference file and recipe.

### 4.2 `reference/page-format.md`
- **Shortcode grammar:** tag names, attribute syntax (always double-quoted), self-closing versus enclosing modules, and inner content (HTML for `tiny_mce` fields).
- **Escaping inside attribute values:** `"` → `%22`, `[` → `%91`, `]` → `%93`, plus Divi's handling of `<`, `>`, `&` and newlines. Each rule is confirmed by round-tripping through `et_fb_process_shortcode`.
- **Where things are stored:**
  - `post_content`: the shortcode;
  - post meta: `_et_pb_use_builder`, `_et_pb_page_layout`, `_et_pb_old_content`, `_et_pb_built_for_post_type`;
  - options: `et_divi` (Customizer and theme options, global colors), `et_divi_builder_global_presets_ng` (presets).
- **Bookkeeping attributes:** `_builder_version`, `_module_preset`, `global_colors_info`, `admin_label`, `locked`, `collapsed`. The page says what to set on new content (for example the site's Divi version for `_builder_version`, and `_module_preset="default"` unless reusing a site preset).
- **Answering the format question directly:** JSON is used by the builder in transit and in portability exports (`{"context":"et_builder","data":{…}}`); serialized PHP appears in options only.

### 4.3 `reference/structure.md`
- **Section types:**
  - regular: rows inside;
  - `fullwidth="on"`: fullwidth modules only;
  - `specialty="on"`: columns with inner rows.
- **Rows and columns:** every legal `column_structure` value and the matching column `type` sequence. Also covers `et_pb_row_inner` and `et_pb_column_inner` and when each is allowed.
- **Parent → child pairs** (from `child_slug`): accordion→accordion_item, tabs→tab, slider→slide, fullwidth_slider→slide, pricing_tables→pricing_table, counters→counter, contact_form→contact_field, signup→signup_custom_field, social_media_follow→social_media_follow_network, map/fullwidth_map→map_pin, video_slider→video_slider_item, and any others found in the schema.
- **Module placement rules:** fullwidth-only modules, and modules that are not allowed inside specialty inner columns.
- **Module index numbering:** `et_pb_text_0`, `_1` and so on are assigned at render time, not stored. This matters for custom CSS selectors.

### 4.4 `reference/value-formats.md`
One section per value type, each with the exact grammar, a valid example, a common mistake, and which field types use it:
- colors: hex, rgba, and global color references (`gcid-…` plus the `global_colors_info` JSON);
- ranges with units;
- the 9-part font string `Family|weight|italic|uppercase|underline|smallcaps|strikethrough|line_color|line_style`;
- 6-part margin/padding `top|right|bottom|left|linked_tb|linked_lr`;
- yes/no (`on`/`off`);
- selects, multiple buttons and multiple checkboxes (`on|off|…` positional);
- icon strings `&#xf0a9;||fa||900`;
- uploads (URL);
- gradient stops;
- `border_radii` `on|tl|tr|br|bl`;
- box-shadow presets;
- animation and transform composites;
- display conditions;
- responsive suffixes `_tablet`, `_phone`, `_last_edited="on|phone"`;
- hover `__hover` plus `__hover_enabled="on|hover"`;
- sticky `__sticky` plus `__sticky_enabled`.

### 4.5 `reference/design-families.md`
Each shared option group (background, font, text, border, box shadow, spacing, sizing, filters, transform, animation, position, z-index, scroll effects, sticky, visibility, link, custom CSS, display conditions) is documented once, with every field and its type, values, defaults, units and R/H/S flags. Fields are written with a `{prefix}` placeholder, and the page explains how prefixes are formed (for example `header_`, `body_`, `button_`, `image_icon_`). The content of these tables is generated; the explanatory prose is hand-written.

### 4.6 `reference/modules/<slug>.md` (generated, × 64)
- **Header:** name, slug, type (module, child or structure), allowed parents, allowed children, main CSS selector.
- **Minimal valid example**, checked by the validator.
- **Content tab:** every field, grouped by toggle, with attribute, type, values/default, R/H/S flags and notes. Inner content is noted as "HTML between the tags".
- **Design tab:** module-specific fields in full, plus a table of the shared families this module uses with their prefixes, linking to `design-families.md`.
- **Advanced tab:** the module's `custom_css_*` slots, with families for the rest.
- **Gotchas:** merged from `research/tools/notes/<slug>.md` when that file exists.
- **Coverage check:** generation fails if any non-`skip` field is neither listed on the page nor covered by a linked family.

### 4.7 `reference/publishing.md` (documentation only in this phase)
Authentication is Basic auth with a WordPress Application Password.
1. **Media:** `POST /wp/v2/media` with the binary and `Content-Disposition`; use `id` and `source_url` in the shortcode.
2. **Create:** `POST /wp/v2/pages` with `{title, slug, status:"draft", content, meta:{_et_pb_use_builder:"on"}}`.
3. **Preview:** the returned `link` plus `&preview=true`, visible to logged-in users.
4. **Publish:** `POST /wp/v2/pages/<id>` with `{status:"publish"}`.
5. **Edit:** `GET /wp/v2/pages/<id>?context=edit` returns `content.raw`; modify it and `POST` it back.

To be settled by live tests on the local site before this file is finalized:
- whether a REST update clears the `et-cache` CSS;
- how to get a no-sidebar or full-width layout (the `template` field versus `_et_pb_page_layout`);
- whether quotes and entities survive the REST round-trip unchanged.

### 4.8 `scripts/divi_shortcode.py`
Shared, stdlib-only module:
- `parse(text) → tree` of nodes `{tag, attrs (ordered), content, children, span}`, using WordPress's shortcode attribute grammar;
- `serialize(tree)`, which round-trips byte-for-byte on unmodified input;
- escape and unescape helpers.

Both scripts use it.

### 4.9 `scripts/validate.py`
- **Usage:** `validate.py page.txt [--tokens tokens.json] [--json]`. Exits non-zero on any error.

| Check | Level |
|---|---|
| Unknown tag; unbalanced or misnested tags | error |
| Structure rules (§4.3), including column types matching `column_structure` and fullwidth or specialty constraints | error |
| Parent/child rules in both directions | error |
| Unknown attribute for the module, or an illegal suffix (e.g. `__hover` on a field without hover support) | error |
| Raw `"`, `[` or `]` inside an attribute value | error |
| Value-format violations (§4.4), select values outside options, units outside `allowed_units` | error |
| `__hover` without `__hover_enabled`; responsive values without `_last_edited` | warning |
| A `_module_preset` UUID that is not `default` and not in the tokens' known presets | warning |
| External image URLs | warning |
| With `--tokens`: colors, fonts or spacing outside the site's token set | warning |

- **Output:** a human-readable report by default, each finding with its line/column, the module path (e.g. `section[2] > row[0] > column[1] > et_pb_blurb[0]`), the attribute and a fix hint. `--json` gives machine-readable output.

### 4.10 `scripts/extract_tokens.py`
- **Usage:**
  - `extract_tokens.py --site URL --user USER --page ID [--page ID …] --out tokens.json`, with the password read from the `WP_APP_PASSWORD` environment variable;
  - offline mode: `--shortcode-file F --url PUBLIC_URL`.
- **Sources:**
  1. page shortcode via REST `?context=edit`;
  2. public page HTML and CSS: the Customizer inline stylesheet, global-color CSS variables (verified live), and Google Fonts links.
- **Output (`tokens.json`):**
  - `site`: url, Divi version, source pages;
  - `colors.global` (gcid → hex), `colors.customizer`, `colors.palette` (hex, uses, roles);
  - `typography`: heading and body fonts, plus a per-level scale (font string, size with tablet/phone, line height, letter spacing, color);
  - `spacing`: section padding frequencies, row width and max width, gutters;
  - `shapes`: radii and shadows;
  - `presets`: preset UUIDs in use, per module, with counts;
  - `module_styles`: per module slug, the distinct **design-only** attribute sets (design versus content decided by the schema), each with use count, preset UUID, `module_class`, `module_id` and `custom_css_*` usage, and **context** (the parent section's background as dark or light plus its color or image, position on the page, admin label, column width);
  - `section_exemplars`: for each existing section, a design-only skeleton (section → row → column → module tree with all design attributes; text, links and images removed). These are **style references to study, not templates to fill in.**
- **Fidelity requirement:** a new component built from `tokens.json` must be able to reproduce any styling the site's existing components use, including preset-driven styles (by reusing preset UUIDs), class-based custom CSS (by reusing classes), responsive and hover values, and theme-level defaults.

### 4.11 `recipes/`
- **`README.md`:** how a recipe maps token paths to attributes, how to choose a `module_styles` entry by context, and how to reuse `section_exemplars` spacing and layout habits.
- **`sections/*.md`:**
  - hero, in four variants: split, centered, background image with overlay, fullwidth header;
  - trust bar or logos;
  - services grid;
  - alternating features;
  - stats counters;
  - process steps;
  - testimonials (grid or slider);
  - pricing;
  - FAQ, with FAQPage JSON-LD in a code module;
  - CTA band;
  - contact (form and map);
  - team;
  - gallery;
  - video;
  - tabs;
  - service-area list.

  Each recipe covers purpose, SEO notes, structure tree, required and optional fields, token mapping, responsive rules, 2–3 variations, and a complete worked example that passes the validator (using a sample `tokens.json` shipped in `recipes/`).
- **`pages/*.md`:** section order and rhythm for four page types: service landing page, local-SEO location page, PPC/lead-gen page, product/feature page.
- **`edits/*.md`:**
  - change copy in place;
  - insert a section;
  - replace a section;
  - restyle a module to site tokens.

  Each keeps untouched content byte-identical by using `divi_shortcode.py` spans.
- **SEO rules throughout:**
  - one H1 (set through `header_level`/`title_level`);
  - no skipped heading levels;
  - alt text on every image;
  - internal links;
  - meaningful `admin_label`s.

## 5. End-to-end workflow (in `SKILL.md`)

1. **Intake:** the content brief, the target site, and whether this is a new page or an edit. For an edit, fetch `content.raw`.
2. **Tokens:** run `extract_tokens.py`, or reuse the site's cached `tokens.json`.
3. **Plan:** outline sections by mapping the brief to recipes, and confirm the outline with the user.
4. **Compose:** write the shortcode section by section, using module references, recipes and tokens.
5. **Validate:** `validate.py --tokens tokens.json`, repeating until there are 0 errors and every warning has been reviewed.
6. **Preview (optional):** render on the local mirror when available (see Addendum A). The WordPress draft is the authoritative visual check.
7. **Publish:** draft, then preview URL, then publish on approval, following `publishing.md` (tooling in the connection phase).

## 6. Testing and verification

| Component | Verification |
|---|---|
| Generator | Coverage check (every non-`skip` field accounted for); deterministic output (regeneration produces an empty diff) |
| `divi_shortcode.py` | Byte-exact round-trip on all captured pages (Divi AI outputs, page 11) |
| Validator | `unittest` suite. Valid fixtures: the captured Divi AI pages and page 11. One broken fixture per error class, each asserting its message. **Divi acts as the judge:** every fixture is also parsed by Divi's `et_fb_process_shortcode` via WP-CLI on the local site, and the validator's verdict and parsed attribute values must match Divi's |
| Token extractor | 2–3 local pages built with known styles (a preset-based button, global colors, custom classes, a responsive heading scale); the extracted tokens must reproduce them exactly. Then a sanity run on a real client page |
| Recipes | Every worked example passes the validator (a check script covers them all). Each is pushed to the local site as a draft through REST and screenshotted once, which also verifies `publishing.md` |
| The skill | Tested on fresh agents (per the skill-writing method): a fresh subagent gets a real SEO brief plus `tokens.json`, once without the skill and once with it. Compare validator results and screenshots, and fix the docs wherever the agent stumbles |

## 7. Risks and mitigations
- **Global presets can't be read through REST.** Reuse preset UUIDs by reference, and get the rendered effect from the public CSS.
- **Escaping disagreements with Divi.** The Divi-as-judge tests (§6).
- **Divi updates change fields.** Regeneration commands, plus the coverage check.
- **Customizer and global-color extraction depends on how Divi outputs CSS.** Verified live on the local site and on one client site before the extractor is finalized; if global colors aren't exposed as CSS variables, fall back to the hex values found in `global_colors_info`.

## Addendum A: Local preview (decided 2026-09-24)

Full findings are in `research/divi-render-engine.md`. The prototype is in `research/render-prototype/`.

- **Approach:** a headless render script (`render.php`, run via WP-CLI `eval-file`) on a local **mirror** WordPress running the same Divi version as the target site (LocalWP). It simulates a front-end request for a fake page held in memory, so it writes nothing to the database and nothing to `et-cache`. It outputs one standalone HTML file with CSS and JS inlined.
- **Verified fidelity on page 11:**
  - builder markup byte-identical to the live page;
  - 2,099 of 2,099 CSS declarations identical;
  - all 302 elements identical in geometry and computed style;
  - pixel diff 0.044% on desktop, all of it animations caught mid-motion.
- **Rejected alternatives:**
  - A JS/Python re-implementation: the render engine is about 185k lines of PHP.
  - `wp eval` + `the_content`: no modules get registered.
  - Divi's preview endpoint: no header or footer, and it needs a login.
  - VB AJAX: renders one module at a time.
- **Client settings: not used (decision).** The preview renders with the mirror's stock Divi settings plus everything inline on the page. There is no settings bundle and no companion plugin; client theme options, presets and global colors are not read.
  - **Consequence:** layout, structure and module-level styling are faithful. Styling that comes from the client's Customizer values or global presets looks generic in the preview. **The WordPress draft preview stays the authoritative visual check.** The skill must say this explicitly.
  - Tokens (§4.10) are unchanged: preset UUIDs are reused without knowing their contents, and Customizer and global colors come from public CSS.
- **Shipped as:**
  - `scripts/preview/render.php` and `scripts/preview/run.sh`, adapted from the prototype with the settings-bundle path removed;
  - `reference/preview.md`, covering mirror setup (a LocalWP site with the matching Divi version), running a render, opening the output, and the fidelity limits above.
- **Workflow step 6** becomes: if a mirror is available, render the page and review the HTML (optionally screenshot it); otherwise skip to the draft push.
- **Tests:**
  - render the validator's valid fixtures on the local mirror; every one must produce HTML containing `.et-l` with one `.et_pb_section` per section in the source;
  - render page 11's shortcode and compare builder CSS declarations with the live page (must be identical).

## Addendum B: End-to-end scope and a portable preview (decided 2026-09-24, mid-build)

**Decisions (user):**
1. The skill must do everything: fetch the design tokens, read the references, compose the page, validate it, preview it, **and send it to the target site**.
2. The preview must not require anyone to install or run WordPress.
3. The Divi theme for previews is fetched from the Elegant Themes account.

**Evidence:** `research/playground-spike.md` (GO).
- Divi 4.27.9 runs inside WordPress Playground (WebAssembly PHP 8.2 + SQLite).
- Rendering page 11's layout gave byte-identical builder markup, 2,064 of 2,064 identical builder CSS declarations, and a 0.02–0.04% pixel diff (site header menu and counter animation).
- The Elegant Themes endpoint `api_downloads.php?api_update=1&theme=Divi&version=V&username=…&api_key=…` returns a specific version's zip. The API rate-limits at about 15 calls per 5 minutes.
- Timings: a cold first run takes about 25 s, a warm render about 1 s while serving. It works offline after the first run.

**Changes:**
- **Preview (supersedes Addendum A's mirror approach):** `scripts/preview/preview.mjs` (Node ≥ 20) with `serve`, `render`, `fetch-divi` and `doctor`.
  - The Divi version comes from `tokens.json → site.divi_version`.
  - Divi zips and caches live in `PP_CACHE_DIR` (user cache) and never enter the repo.
  - `ET_USERNAME`/`ET_API_KEY` are env-only, never printed, and used only for uncached versions.
  - Still **stock Divi settings**; the no-client-settings decision in Addendum A stands. The WordPress draft remains the authoritative visual check.
- **Publishing:** `scripts/publish.py` with `fetch`, `media`, `draft` and `publish`, using Application Passwords from env `WP_APP_PASSWORD`.
  - `draft` validates first, uploads local images, and saves drafts only.
  - `publish` requires an explicit `--yes` after user approval.
  - This moves the "connection phase" publishing tool into this build. The MCP remains out of scope.
- **Workflow (§5), updated:**
  1. Intake.
  2. Tokens (`extract_tokens.py`).
  3. Plan.
  4. Compose.
  5. Validate (`validate.py`).
  6. Preview (`preview.mjs render|serve`).
  7. Draft (`publish.py draft`): share the `preview_url`.
  8. Publish on approval (`publish.py publish --yes`).
- **Language note:** the Python-stdlib-only rule applies to `.py` scripts. The preview is Node because the Playground runtime is a Node package.

