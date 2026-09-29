# Design tokens

`tokens.json` is what lets this skill author a *new* page that looks like it belongs on a
*specific* client's site: the exact colors, fonts, spacing and per-module styles that site already
uses, extracted from the pages the client already has. This document explains where that style
actually lives, how to extract it, what each key in the file means, and how to use it when writing
a page.

## 1. Where a Divi site's style actually lives

Divi spreads a site's visual identity across four places, only some of which are readable from the
outside:

- **Inline module attributes** — the great majority of styling. Every color, font, size, spacing
  and shadow an editor sets on a specific module (`button_bg_color="#f97316"`,
  `title_font="Montserrat|700|||||||"`, …) is stored directly in that module's shortcode
  attributes, on the page's content. This is fully readable: `tokens_from_shortcode.py` (Task 11)
  parses it into `module_styles`, `colors.palette`, `typography.scale`, `spacing` and `shapes`.
- **Global presets** (`_module_preset="<uuid>"`, referenced from a module) — a *named, reusable
  bundle of style attributes* the client (or Divi itself) defined once and applied to many modules.
  **The preset's actual contents are private** — they live in a site option (`et_pb_role_settings`
  / global-presets storage) that isn't exposed through a public page or the REST content field, so
  a page that uses a preset only shows you the preset's UUID, not what it sets. `tokens.json`
  records which UUIDs are seen and how often (`presets`), but never their contents. **Reuse the
  UUID as-is** on a new module of the same type when you want that preset's look; never invent
  attribute values to "reproduce" a preset you can't read.
- **Customizer settings and global colors** — sitewide defaults (accent color, link color, heading
  color, body/heading fonts, body font size, site content width, and any Global Colors the client
  defined) that apply to *every* page, not just ones a module attribute overrides. These aren't in
  the page content at all; they only show up in the **public page's rendered CSS**
  (`tokens_from_html.py`, this task). The selectors `tokens_from_html.py` reads for each value are listed in its own docstring (the
  discovery notes behind them are repo only: `research/tools/notes/customizer-css.md`). This is also
  why Global Colors in particular are **not**
  recoverable this way in general (Divi 4.27.9 resolves a Global Color to a plain hex value before
  emitting CSS — there's no `--gcid-*` variable and no signal left behind once resolved, and an
  *unused* Global Color leaves no trace at all).
- **Child-theme or plugin CSS** — any hand-written CSS a developer added outside Divi's own
  Customizer/builder system (a child theme's `style.css`, a "Custom CSS" plugin, additional
  `<style>`/`<link>` tags emitted by other plugins). **This skill does not capture it.** It's not
  attributable to any single page or module, there's no reliable way to tell it apart from
  third-party plugin styling, and reading it would mean fetching and parsing arbitrary stylesheets
  with no schema. If a site's look depends on such CSS, tokens extracted here will miss it — see
  the fidelity rule in §5.

## 2. Running the extractor

`extract_tokens.py` has two modes.

**Online** (reads live pages from the client's WordPress REST API, using an Application Password —
never a regular account password):

```bash
python3 scripts/extract_tokens.py --key "Client A" --page 12 --page 34 --out tokens.json
```

- `--key "NAME"` resolves the site/user/password from `keys.json` (`publish.py keys` lists what's
  configured; see `reference/publishing.md` → "Credentials: keys.json"). Without a `keys.json`
  entry, `--site URL --user USER` plus env `WP_APP_PASSWORD` still work exactly as before.
- `--page` may repeat; pass every page you want the extractor to learn module styles from (a
  homepage plus a couple of representative interior pages is usually enough).
- A key value is read only from `keys.json` or the `WP_APP_PASSWORD` environment variable and is
  never written to argv, logs, or `tokens.json`.
- Each page's *public* URL (from the REST response) is fetched too, unauthenticated, purely to read
  its rendered CSS/HTML for the Customizer/global-color/font/version side of the tokens. If that
  fetch fails, extraction still proceeds with a warning on stderr — you just don't get the
  Customizer-derived tokens.

**Offline** (no credentials and no REST call; parses a content file you already have — useful for testing, or
when you only have an export of the page content). Without `--url` it makes no network access at all; with `--url`
it still fetches that public URL for its CSS (on Divi 5 also the site's home page and their same-origin `et-cache`
stylesheets, §7.2):

```bash
python3 scripts/extract_tokens.py \
  --content-file page.txt --url https://client.example/page/ --out tokens.json
```

`--content-file` takes Divi 4 shortcode or Divi 5 blocks (`--shortcode-file` is the old name and still works).
The rest of this section, and §3–§6, describe the Divi 4 output; Divi 5 sites are covered in §7.

`--url` is optional in offline mode. If given, the extractor will still try to fetch that URL's
HTML (for Customizer/fonts/version); if omitted, `tokens.json` will have `colors.customizer`,
`colors.global` and `typography.loaded_fonts` all empty, and `site.divi_version` `""` — everything
the shortcode itself carries (palette, typography scale, spacing, shapes, presets, module_styles,
section_exemplars) is still produced.

Either mode prints a one-line summary and writes `tokens.json`:

```
wrote tokens.json: 16 style bundles across 13 modules, 5 palette colors, 4 section exemplars, 0 presets
```

## 3. What each key means

Top-level keys: `site`, `colors`, `typography`, `spacing`, `shapes`, `presets`, `module_styles`,
`section_exemplars`. Excerpt below is from combining `tests/fixtures/valid/handwritten-landing.txt`
(shortcode) with a rendered page carrying non-default Customizer values.

```json
{
 "site": {
  "url": "https://client.example",
  "divi_version": "4.27.9",
  "source_pages": [{"id": 1, "url": "https://client.example/p/"}],
  "extracted_at": "2026-09-25T03:57:00+00:00"
 },
 "colors": {
  "palette": [
   {"hex": "#f97316", "uses": 4, "roles": ["button_bg_color", "icon_color"]},
   {"hex": "#0b2a3c", "uses": 1, "roles": ["background_color"]}
  ],
  "global": {},
  "customizer": {
   "body_text": "#333344", "heading": "#112233", "link": "#0055ff", "accent": "#ff00aa",
   "body_font": "Lato", "heading_font": "Montserrat", "body_size": "17px", "content_width": "1200px"
  }
 }
}
```

- `site` — where these tokens came from and when: the site URL, the Divi version the public HTML
  reported (from `<meta ... content="Divi v.X">` or a `themes/Divi/...?ver=X` asset URL), each
  source page's id/URL, and an ISO-8601 UTC extraction timestamp. Use `site.divi_version` when
  writing `_builder_version="..."` on new modules, so the new markup matches what the site's Divi
  install actually renders.
- `colors.palette` — every distinct hex color found on real design attributes across the sampled
  pages (not content text/URLs), how many times each was used, and which attribute names
  (`roles`) used it, sorted by use count descending. This is the client's *actual* palette, built
  from evidence, not guessed from a screenshot.
- `colors.global` — Global Colors recovered from the public HTML as `{gcid: hex}`. In practice this
  is almost always `{}` (see §1 and `customizer-css.md`); don't rely on it being populated.
- `colors.customizer` — sitewide Customizer overrides actually detected in the rendered CSS: only
  keys the site *overrode from Divi's defaults* appear (see §6). Possible keys: `accent`, `link`,
  `body_text`, `heading`, `body_font`, `heading_font`, `body_size`, `content_width`.
- `typography.heading_font` / `typography.body_font` — the most common font seen in the shortcode
  data (heading levels' fonts / `et_pb_text` fonts), falling back to the Customizer's heading/body
  font when the shortcode itself never sets one explicitly.
- `typography.scale` — per heading level (`h1`…`h6`, or whatever levels the pages actually use) the
  most common `{font, size, size_tablet, size_phone, line_height, letter_spacing, color}`
  combination seen for that level. This is the client's real heading scale — use it instead of
  guessing font sizes for headings on a new page.
- `typography.loaded_fonts` — every Google Font family name the public page(s) actually load
  (from the `fonts.googleapis.com` `<link>`), in first-seen order. A font used inline
  (`title_font="SomeFont|700|..."`) that isn't in this list may not actually be loading on the
  live site — worth flagging rather than reusing blind.
- `spacing.section_padding` / `spacing.row.width` / `spacing.row.max_width` — `[value, count]`
  pairs (most common first) for `et_pb_section`'s `custom_padding` and `et_pb_row`'s `width` /
  `max_width`. These are the section/row rhythms the client's pages actually use.
- `shapes.radii` / `shapes.shadows` — same `[value, count]` shape for border radii and box-shadow
  bundles seen anywhere in the sampled pages.
- `presets` — `{module_slug: [{uuid, uses}, ...]}`, how often each Global Preset UUID was seen on
  each module type. **Contents unknown** — see §1.
- `module_styles` — `{module_slug: [bundle, ...]}`, sorted by `uses` descending. Each bundle:
  `attrs` (the exact design attributes as they appeared — colors, fonts, spacing, borders, etc.,
  content and bookkeeping stripped out), `media` (which of those attrs are upload/image fields —
  names only, never URLs), `preset` (the `_module_preset` UUID or `"default"`), `module_class` /
  `module_id` (if the client uses either as a CSS hook), `custom_css` (any `custom_css_*`
  attributes), `uses` (how many times this exact bundle occurred), and `contexts` (see next).
- `module_styles[slug][i].contexts` — one entry per occurrence of that exact style bundle:
  `section_index`, `section_label` (the section's `admin_label`, if the client named it),
  `section_tone` (`dark`/`light`/`image`/`default`, from the section's background luminance),
  `section_background` (`{color, image: bool}`), `column_type` (e.g. `1_2`, `1_3`). This tells you
  *where on the page* a given style is normally used, which is the key to composing correctly (§4).
- `section_exemplars` — one design-only skeleton per `et_pb_section` seen: `tag`, `attrs`
  (structural + design attrs only — no text, no image URLs), `media` (upload attr names), and
  `children` (same shape, recursively). This is a real section's shape with the content stripped
  out — a template for how the client actually composes sections, rows and columns.

## 4. Using the tokens when composing a page

1. **Pick styles by context, not just by module type.** For a given module slug, look at
   `module_styles[slug]` and choose the bundle whose `contexts` best match where you're placing the
   new module — same `section_tone` (a light-background section shouldn't reuse a bundle built for
   dark sections), similar `section_label`/position, and matching `column_type` for column-scoped
   modules like buttons or blurbs.
2. **Copy `attrs` verbatim.** Don't rephrase or "clean up" a chosen bundle's `attrs` — copy the
   exact key/value pairs onto the new module's shortcode attributes so it renders identically to
   the client's existing usage.
3. **Keep `preset` and `module_class` as-is.** If the bundle has a non-`"default"` `preset`, set
   `_module_preset` to that same UUID on the new module (don't invent attribute values to imitate
   it — see §1). If it has a `module_class`, keep it, since it may be targeted by the site's own
   CSS.
4. **Follow `section_exemplars` for structure.** When building a new section, match an exemplar's
   padding, its row's `width`/`max_width`, and its column-count/type habits, rather than picking
   arbitrary structural values.
5. **Use `typography.scale` for every heading level** you place — pull the level's recorded
   `font`/`size`/`size_tablet`/`size_phone`/`line_height`/`letter_spacing`/`color` rather than
   guessing a heading style.

## 5. The fidelity rule

The point of `tokens.json` is that a page built from it should be indistinguishable, style-wise,
from a page the client's own team built — it must **reproduce what the site's existing components
already do**, not invent a plausible-looking new style. When you need a style and there's no
matching entry in `module_styles`, no matching `section_exemplars` shape, and no relevant
`colors`/`typography`/`spacing`/`shapes` token — **say so to the user** ("this site has no existing
example of X; here's my best guess, please confirm") instead of silently fabricating a color, font
size, or spacing value that merely looks plausible. A confident-looking invention is worse than an
honest gap, because it's indistinguishable from real data until someone notices the page doesn't
actually match the rest of the site.

## 6. Limits

- **Preset contents are unknown.** `presets` only ever tells you a UUID and how often it's used —
  never what attributes it sets. Treat a preset as an opaque token to reuse, not a style to
  reconstruct.
- **Customizer values the site never overrides don't appear.** `colors.customizer` only contains
  keys the extractor could actually detect a non-default value for in the rendered CSS; a site
  running with Divi's stock defaults for, say, the accent color, will simply have no `"accent"` key
  — that is not the same as "the accent color is Divi's default `#2ea3f2`", it means *this
  extraction found no override*, and code that consumes `tokens.json` should not assume a missing
  key means any particular color.
- **Customizer CSS is read from inline `<style>` blocks only.** `tokens_from_html.py` never follows
  `<link rel="stylesheet">` files. If a cache/optimization plugin (WP Rocket, Autoptimize, LiteSpeed,
  …) or Divi's own static CSS file generation (Theme Options → Builder → Advanced → Static CSS File
  Generation) moves the Customizer CSS into an external stylesheet, `colors.customizer` (and the
  Customizer fonts/sizes) can come back empty or partial. Then either re-run in offline mode against
  a copy of the page served *without* that optimization (most cache plugins skip logged-in users or
  have a bypass query string; ask the site owner which): `publish.py fetch --page-id ID --out page.txt`,
  then `extract_tokens.py --shortcode-file page.txt --url <that unoptimized URL> --out customizer.json`
  and copy its `colors.customizer` (plus `typography.heading_font`/`body_font`) into your
  `tokens.json` (online mode ignores `--url` and fetches each page's own public link); or fill
  `colors.customizer` in by hand from the site's Divi Theme Customizer values (keys: `accent`, `body_text`, `heading`,
  `link`, `body_font`, `heading_font`, `body_size`, `content_width`).
- **Global Colors are effectively invisible from public HTML** (§1): an unused Global Color leaves zero trace, and a used
  one is indistinguishable from a hardcoded hex value once rendered. `colors.global` should be
  expected to be `{}` in the common case. The shortcode's own `global_colors_info` bookkeeping
  attribute isn't a usable fallback either
  (Divi's `_prepare_global_colors_info()`,
  `includes/builder/class-et-builder-element.php:13391-13431`): a true global-color entry maps a
  `gcid-<uuid>` to a list of *attribute names* that use it, never to a hex, and an inline/"smart"
  color entry is keyed by the hex itself — a value already captured plainly in `colors.palette`.
  Neither shape ever yields a new gcid→hex pair, so `colors.global` only fills in if a Divi build
  actually emits `--gcid-*` CSS custom properties; until then, reuse colors from `colors.palette`
  instead of expecting a gcid to resolve to anything.
- **Child-theme/plugin CSS is not captured at all** (§1). If a client's site relies on such CSS for
  part of its look, `tokens.json` will not reflect it.

## 7. Divi 5 sites

Divi 5 keeps the same idea (learn the site's look from its own pages), but its design system is far more visible
from outside, and it can be *referenced* by id instead of copied. The research behind this section is
`research/divi5/tokens-and-detection.md` (repo only).

### 7.1 Detection

`extract_tokens.py` decides the format before anything else:

- **Online**, it asks `divi_format.detect_site`: the `Version:` header of `/wp-content/themes/Divi/style.css`,
  else the most common `?ver=` on `/themes/Divi/` assets, else Divi 5 HTML markers.
- **Every page's content** is classified with `detect_content` (`shortcode`, `blocks`, `mixed`).
- A site that reports Divi 5, or any page holding `<!-- wp:divi/… -->` blocks, gets the Divi 5 extractor. Anything
  else gets the Divi 4 extractor, whose output is unchanged (§2–§6).
- A Divi 4 shortcode page sampled on a Divi 5 site is listed in `site.source_pages` with `format: "shortcode"` and
  a warning; it adds no module styles. Sample block pages, or have the page converted in the Visual Builder first.
- Online, a Divi 5 site whose sampled pages are **all** shortcode still gets Divi 5 tokens (`divi_major: 5`,
  `content_format: "shortcode"`, the site-wide colors, variables and preset CSS from the public HTML) but an empty
  `module_styles` (and no scale, palette or section exemplars from content): sample block pages, or migrate the
  pages to Divi 5 first. (Offline there is no site detection, so a shortcode `--content-file` gets the Divi 4
  extractor.)

### 7.2 Where the style lives, and what is recovered

| Data | Stored in (site options) | Recovered from content (`tokens5_from_blocks.py`) | Recovered from public HTML/CSS (`tokens5_from_html.py`) |
|---|---|---|---|
| Global colors (`gcid-…`) | `et_divi[et_global_data]` | ids a page references, with use counts and roles | values from `:root{--gcid-…}`: only colors the page uses (all of them when Dynamic Assets is off). A derived color (`hsl(from var(--gcid-base) …)`) is resolved to a hex/rgba value |
| The 5 Customizer colors | `et_divi[accent_color]` … | ids if referenced | **always**, from `:root` (defaults included) |
| Customizer fonts, weights, body size | `et_divi[heading_font]` … | — | **always**, from `:root{--et_global_…}` |
| Design variables (`gvid-…`) | `et_divi_global_variables` | ids a page references (every kind) | number, font, image and gradient values from `:root{--gvid-…}`: the ones the page uses, or **all active ones** on a page that uses none |
| String and link variables | same | ids only | never (resolved inline into text / `href`) |
| Module presets | `et_divi_builder_global_presets_d5` | ids (`modulePreset`) and use counts | the **rendered CSS** under `.preset--module--<module>--<id>` |
| Option-group presets | same | ids, group name, host module, group id | the rendered CSS under `.preset--group--<module>--<group>--<hash>--<id>` |
| A module type's default preset | same | — (implicit) | its CSS under `…--default`; its real id never appears |
| Labels (color names, preset names), preset attribute JSON, unused anything | options | no | no |

Online, the extractor fetches each sampled page's public URL **and the site's home page** (a page that references no
variable prints every active number/font/image variable), and follows each page's same-origin
`/wp-content/et-cache/…css` stylesheets, where static CSS generation or a cache plugin moves this CSS. Offline,
`--content-file` plus `--url` fetches that URL and the site's home page the same way.

### 7.3 `tokens.json` on Divi 5

Top-level keys: `site`, `colors`, `variables`, `typography`, `spacing`, `shapes`, `presets`, `group_presets`,
`preset_defaults`, `module_styles`, `section_exemplars`. A trimmed real extraction from the local Divi 5 test site:

```json
{
 "site": {"url": "http://divi-5-test.local", "divi_version": "5.13.1", "divi_major": 5, "content_format": "blocks",
          "source_pages": [{"id": 658, "url": "http://divi-5-test.local/r6-tokens-trace/", "format": "blocks"}],
          "extracted_at": "2026-09-29T07:00:24+00:00"},
 "colors": {
  "global": {
   "gcid-r6navy0001": {"value": "#0B2A3C", "uses": 1, "roles": ["content.decoration.bodyFont.body.font.color"]},
   "gcid-r6orange001": {"value": "#F97316", "uses": 0},
   "gcid-r6orangelt1": {"value": "#fdcdab", "raw": "hsl(from var(--gcid-r6orange001) calc(h + 0) calc(s + 0) calc(l + 30))",
                        "base": "gcid-r6orange001", "uses": 1, "roles": ["module.decoration.background.color"]}
  },
  "customizer": {
   "primary": {"id": "gcid-primary-color", "value": "#7C3AED", "overridden": true},
   "heading": {"id": "gcid-heading-color", "value": "#666666", "overridden": false}
  },
  "palette": []
 },
 "variables": {
  "gvid-r6secpad01": {"value": "clamp(48px, 8vw, 96px)", "kind": "numbers", "uses": 2,
                      "roles": ["module.decoration.spacing.padding"]},
  "gvid-r6font0001": {"value": "Poppins", "kind": "fonts", "uses": 0},
  "gvid-r6image001": {"value": "https://example.com/r6-hero.jpg", "kind": "images", "uses": 0},
  "gvid-r6ctalink1": {"value": null, "kind": "links", "uses": 1, "roles": ["button.innerContent.linkUrl"]}
 },
 "typography": {
  "heading_font": "Open Sans", "body_font": "Open Sans", "scale": {},
  "customizer": {"heading_font": {"id": "--et_global_heading_font", "value": "Open Sans", "weight": "500"},
                 "body_size": "14px", "body_line_height": "1.7em"},
  "loaded_fonts": ["Open Sans", "Poppins"]
 },
 "presets": {
  "divi/button": [{"id": "r6btnpreset1", "uses": 1, "css": {
   "selector": "body #page-container .et_pb_section .preset--module--divi-button--r6btnpreset1",
   "declarations": {"background-color": "var(--gcid-r6orange001)", "color": "#ffffff",
                    "border-top-left-radius": "var(--gvid-r6radius01)"},
   "rules": ["… every rule naming the class, with its selector, declarations and media query …"]}}]
 },
 "group_presets": {
  "divi/font": [{"id": "r6fontpreset1", "uses": 1, "module": "divi/heading", "group_id": "designTitleText",
                 "css": {"declarations": {"font-family": "var(--gvid-r6font0001)", "font-weight": "700",
                                          "color": "var(--gcid-r6navy0001)", "font-size": "52px"}}}]
 }
}
```

- `site.divi_major` is `5`; `site.divi_version` is the version for `builderVersion` on every block you write.
  `site.content_format` is the sampled pages' format (`blocks`, or `mixed` when they differ); each source page
  carries its own `format`.
- `colors.global` — `{gcid: {value, uses, roles?, raw?, base?}}`. It merges the `:root` values with the ids the
  sampled content references. A referenced id whose value the public HTML never showed has `"value": null`: it is
  still a real id, safe to reference. `uses: 0` means the value was seen (a preset or another page uses it) but the
  sampled content never references it directly. `raw`/`base` describe a derived color.
- `colors.customizer` — the five Customizer colors `{role: {id, value, overridden}}` (`primary`, `secondary`,
  `heading`, `body`, `link`). `overridden: false` means Divi's default; at the default, the rendered heading color
  actually comes from Divi's base CSS, not this value.
- `colors.palette` — literal colors in the content, as on Divi 4, plus `global: "<gcid>"` when a literal equals a
  known global or Customizer color (a hint that the site meant that color).
- `variables` — `{gvid: {value, kind, uses, roles?}}`, `kind` being `numbers`, `fonts`, `images`, `gradients`,
  `strings` or `links`. String and link values are always `null`.
- `typography` — the Divi 4 keys, computed from Divi 5 font objects (`scale` entries and `body` may hold
  `$variable()$` strings), plus `customizer` (heading/body fonts with their `--et_global_…` ids and weights, body
  size and line height) and `loaded_fonts` (Google Font links and inlined `@font-face` families, icon fonts left
  out). `heading_font`/`body_font` fall back to the Customizer fonts when the content sets none.
- `spacing`, `shapes` — Divi 5 value objects with counts: `section_padding` `[{top, right, bottom, left}, n]`,
  `row.width`/`row.max_width`, `gutters`, `gaps`, `radii`, `shadows`. Values may be `$variable()$` strings.
- `presets` — `{module: [{id, uses, css}]}`. `group_presets` — `{group name: [{id, uses, module, group_id, css}]}`.
  `css` is the preset's recovered CSS, `null` when no sampled page rendered it. `css.declarations` is the merged
  base rule (no pseudo-elements, no media query); `css.rules` lists every rule. A preset seen only in the HTML (not
  in the sampled content) is listed with `uses: 0` and, for a group preset, `group_id: null`.
- `preset_defaults` — `{module: css}`: what an un-preset module of that type looks like (its `…--default` CSS).
- `module_styles` — `{module: [bundle]}`, bundles holding `attrs` (design-only Divi 5 attribute JSON, `$variable()$`
  strings verbatim), `module_preset`, `group_presets`, `html_attributes`, `custom_css_slots` (which custom CSS slots
  are filled, never the CSS text), `media`, `uses` and `contexts` (as on Divi 4, capped at 5).
- `section_exemplars` — one design-only `{name, attrs, media, children}` tree per section.

### 7.4 References versus literals

When `tokens.json` has an id for the role, write the **reference**, not the value. The page then stays linked to the
client's design system, and it follows a later re-theme. Otherwise write the value inline.

| Situation | Write |
|---|---|
| The color is a `colors.global` entry used in that role (its `roles`), or a palette entry with `global` | `$variable({"type":"color","value":{"name":"<gcid>","settings":{}}})$`, not the hex |
| Accent, secondary, heading, body or link color | the Customizer ids (`gcid-primary-color` …): they always exist |
| A number, font, image or gradient the site uses through a variable in that role (section padding, radius, display font) | `$variable({"type":"content","value":{"name":"<gvid>","settings":{}}})$` |
| A module that should look like an existing preset | `"modulePreset": ["<id>"]`, or `"groupPreset": {"<group_id>": {"presetId": ["<id>"], "groupName": "<group name>"}}` with the exact ids from tokens, and no inline attrs fighting it |
| A module that should just look like the site's default for its type | nothing: omit `modulePreset` (or write `["default"]`) and the default preset applies |
| String and link variables | only when the user asks for that site-wide text or URL |
| Anything with no matching token | the inline value, under the fidelity rule (§5): say it is a guess |

These strings go inside the block's attribute JSON as ordinary strings; the serializer escapes the inner quotes.
Use only ids that appear in `tokens.json` — never invent one, and never guess a label.

### 7.5 The design system is read-only

Divi 5 global colors, variables and presets cannot be created or read over REST with an Application Password (every
`divi/v1` writer needs a Visual Builder nonce). The skill can only **reuse** what the sampled public pages reveal.
If a page needs a new site-wide color, variable or preset, write the value inline and tell the user to create the
token in the Visual Builder; a later extraction will then pick it up.

### 7.6 Unknown preset ids

An unknown `modulePreset` id is not harmless: Divi renders the module with that id's (empty) preset class **and drops
the module type's default preset styling**. An unknown `gcid-`/`gvid-` id renders as nothing. So:

- only reference preset, color and variable ids that are in `tokens.json`;
- to inherit the site default, omit `modulePreset`;
- `presets[...]` entries with `css: null` are still real ids (the content uses them); their look is just unknown.

### 7.7 How `validate.py --tokens` uses the ids

`validate.py PAGE --tokens tokens.json` on block content reads:

- **Known presets**: every `id` under `presets` and `group_presets`. Any other `modulePreset`/`groupPreset` id is
  `W5_UNKNOWN_PRESET`.
- **Known variables**: the keys of `colors.global` and `variables` (plus palette `global` links). The five Customizer
  color ids are always known. Any other `gcid-`/`gvid-` reference is `W5_UNKNOWN_VARIABLE`.
- **Palette**: `colors.global` and `colors.customizer` values plus `colors.palette` hexes. A literal color outside it is
  `W_OFF_PALETTE_COLOR`; a `$variable()$` reference never is.
- **Fonts**: `typography` heading/body/scale fonts, the Customizer fonts, font variables and every literal
  `family` in `module_styles`. Any other literal family is `W_OFF_BRAND_FONT`.
- **Section padding**: `spacing.section_padding` top/bottom pairs (`W_OFF_SCALE_SPACING`); a variable is never off-scale.
- `site.divi_version` is checked against each block's `builderVersion` (`W5_BUILDER_VERSION`), and `site.url` names
  the site's own host for image URLs.

A page validated against tokens extracted from itself produces none of these warnings.

### 7.8 Limits (Divi 5)

- Values of colors and variables the sampled pages never print are unknown (`value: null`); sample more pages that
  use them. Labels and preset names are never recoverable.
- A preset's attribute JSON is never recoverable, only its rendered CSS: reuse the preset by id, don't rebuild it
  from `css`.
- The id behind a module type's default preset never appears; `preset_defaults` shows only its CSS.
- CSS from cache or optimization plugins that combine stylesheets into non-`et-cache` files is not followed; child-theme
  and plugin CSS is not captured (§1).
