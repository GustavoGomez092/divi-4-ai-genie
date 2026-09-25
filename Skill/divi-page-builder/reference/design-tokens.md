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
  (`tokens_from_html.py`, this task). See §5.2 of
  [`research/tools/notes/customizer-css.md`](../../../research/tools/notes/customizer-css.md) for
  exactly which selectors carry which value, and why Global Colors in particular are **not**
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
export WP_APP_PASSWORD='xxxx xxxx xxxx xxxx xxxx xxxx'   # never pass it as a flag or commit it
python3 Skill/divi-page-builder/scripts/extract_tokens.py \
  --site https://client.example --user editor --page 12 --page 34 \
  --out tokens.json
```

- `--page` may repeat; pass every page you want the extractor to learn module styles from (a
  homepage plus a couple of representative interior pages is usually enough).
- The password is read **only** from the `WP_APP_PASSWORD` environment variable and is never
  written to argv, logs, or `tokens.json`.
- Each page's *public* URL (from the REST response) is fetched too, unauthenticated, purely to read
  its rendered CSS/HTML for the Customizer/global-color/font/version side of the tokens. If that
  fetch fails, extraction still proceeds with a warning on stderr — you just don't get the
  Customizer-derived tokens.

**Offline** (no network access; parses a shortcode file you already have — useful for testing, or
when you only have an export of the page content and no live site to fetch CSS from):

```bash
python3 Skill/divi-page-builder/scripts/extract_tokens.py \
  --shortcode-file page.txt --url https://client.example/page/ --out tokens.json
```

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
(shortcode) with `tests/fixtures/html/customized-page.html` (the same page's rendered output, with
non-default Customizer values set) — see `tests/test_tokens_from_html.py`.

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
- **Global Colors are effectively invisible from public HTML** (§1, and
  `research/tools/notes/customizer-css.md`): an unused Global Color leaves zero trace, and a used
  one is indistinguishable from a hardcoded hex value once rendered. `colors.global` should be
  expected to be `{}` in the common case.
- **Child-theme/plugin CSS is not captured at all** (§1). If a client's site relies on such CSS for
  part of its look, `tokens.json` will not reflect it.
