# Page format

## What Divi stores

A Divi 4 page's `post_content` is **a plain string of nested WordPress shortcode tags** —
`[et_pb_section]...[/et_pb_section]` and friends. It is **not JSON, not serialized PHP, and not
Gutenberg block markup**. `wp post get <id> --field=post_content` on a real Divi page returns
exactly the text you'd type into a `.php` template and pass to `do_shortcode()` — nothing more.

JSON and serialized PHP both exist *around* Divi content, just never inside `post_content` itself:

- **JSON** appears in two places that never touch `post_content`:
  - **Builder transit** — when the Visual Builder edits a page, it converts the shortcode tree to
    a JSON module tree in the browser (this is exactly what
    `et_fb_process_shortcode()`/`render_as_builder_data()` produce; see
    `research/tools/notes/escaping.md`) and converts it back to shortcode on save. An AI authoring
    a page never needs to produce this JSON — write shortcode directly.
  - **Portability export** — Divi's Import/Export tool (and the `et_core_portability_*` REST
    endpoints) wrap one or more pages' shortcode as `{"context":"et_builder","data":{"<post
    id>":"<shortcode string>", ...}}`, i.e. a JSON envelope whose values are the same shortcode
    strings, not a structured representation of them.
- **Serialized PHP** appears in two `wp_options` rows, never in a page's `post_content`:
  - `et_divi` — the theme's Customizer settings (colors, typography, layout defaults), stored as a
    PHP-serialized array.
  - `et_divi_builder_global_presets_ng` — the site's Global Presets (the definitions that
    `_module_preset` UUIDs point at), also PHP-serialized.

When authoring a page: write `post_content` as shortcode text, full stop. Presets and Customizer
settings are read, never written, by a hand-authored page.

## Grammar

- A **tag** is `[et_pb_<name> attr="value" ...]`. Slugs always start with `et_pb_`.
- Every attribute is written `name="value"` — **always double-quoted**. (The Visual Builder never
  emits single-quoted or bare/unquoted attributes; `validate.py` warns with `W_ATTR_QUOTING` on
  anything else, and a raw `"` inside a non-double-quoted attribute is `E_RAW_QUOTE`.)
- A tag is either **enclosing** — `[et_pb_text ...]...[/et_pb_text]` — or **self-closing** —
  `[et_pb_image ...][/et_pb_image]` or `[et_pb_image .../]`. Divi's own output always writes a
  matching closing tag even for modules with no content (see the minimal example below); either
  form parses the same.
- For a module whose `content` field is `tiny_mce` (a text-bearing module: `et_pb_text`,
  `et_pb_blurb`, `et_pb_cta`, `et_pb_accordion_item`, slides, and similar), everything between the
  open and close tags is **raw HTML**, not shortcode-escaped text — write `<p>`, `<strong>`, links,
  etc. directly. It is not re-escaped the way attribute values are (see Escaping below).
- Containers nest: `et_pb_section` → `et_pb_row` → `et_pb_column` → module. See
  [structure.md](structure.md) for the exact rules.

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Licensed, insured plumbers at your door in 60 minutes.</p>[/et_pb_text][et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" alt="Plumber" _builder_version="4.27.9" _module_preset="default"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Escaping

Attribute values are escaped **once**, uniformly, regardless of which attribute they're on (with
one URL-attribute caveat below). Content between a text-bearing module's tags is **not** escaped
this way — see the last row.

| character | write as | why | correct | incorrect |
|---|---|---|---|---|
| `"` (double quote) | `%22` | a raw `"` inside a double-quoted attribute value terminates the attribute early (WordPress's attribute regex stops at the first unescaped `"`), producing stray tokens (`E_POSITIONAL_ATTR`) instead of one attribute. | `title="Say %22hi%22"` | `title="Say "hi""` |
| `[` | `%91` | a raw `[` inside an attribute value can be misread as the start of a nested shortcode tag by WordPress's tag matcher. `validate.py` flags any raw `[`/`]` in an attribute as `E_RAW_BRACKET`. | `title="Save %9120%%93 today"` (decodes to `Save [20%] today`) | `title="Save [20%] today"` |
| `]` | `%93` | same reason as `[` — a raw `]` can be misread as closing a shortcode tag early. | (see above) | (see above) |
| `\` (backslash) | `%92` (general attributes and `checkbox_options`/`radio_options`/`select_options`/`conditional_logic_rules`) | Divi's own Visual Builder templates decode `%92` back to `\` for display (`class-et-builder-element.php:11596`,`:11653`); a raw backslash round-trips fine on the front end but doesn't match what the Visual Builder itself writes, so a page you hand-author with a literal `\` will look "dirty" the moment someone opens it in the builder and it re-saves. | `custom_css_main_element="content: %22%922014%22;"` | `custom_css_main_element="content: \"\2014\";"` |
| `<` | avoid entirely; use `&lt;` inside HTML content, or rephrase attribute text | WordPress empties (or worse — see below) any shortcode attribute value containing a `<` that isn't part of a complete `<tag>...</tag>` pair. `validate.py` flags this as `E_ATTR_LT`. **Confirmed against the real site** (`research/tools/notes/doc-experiments.md`, experiment 2): a bare `<` in `et_pb_heading`'s `title` didn't just blank that title — `wptexturize()` (which runs before Divi's own shortcode parsing on every page load) desynced its quote tracking at the `<`, and the rest of the shortcode string, including the closing tags for the section/row/column that held it, was dumped onto the page as literal unrendered text. | `title="Revenue less than 5%"` | `title="Revenue < 5%"` |
| newline, inside `custom_css_*` only | `\|\|` (two pipes) | the Visual Builder's custom-CSS textareas store each line joined by `\|\|` and turn it back into `\n` only for display (`class-et-builder-element.php:24209/24223/24237`, confirmed in experiment 1). A raw newline inside a shortcode attribute value is unusual but not itself flagged by the parser; `\|\|` is simply what real Divi output always uses for multi-line CSS. | `custom_css_main_element="color: red;\|\|font-weight: bold;"` (two rules) | `custom_css_main_element="color: red;\nfont-weight: bold;"` (a literal `\n`, which the builder will show as one line containing the two characters `\`+`n`) |
| — content between a text-bearing module's tags | write raw HTML, not escaped | unlike attributes, a leaf module's inner content is returned to the front end byte-for-byte when the module's `vb_support` is `'on'` (true for every ordinary text module) — Divi runs `html_entity_decode()` on it only when `vb_support` is **not** `'on'` and the content has no line breaks (`research/tools/notes/escaping.md`, "Content" section). Don't pre-encode `&amp;`, `&lt;`, etc. unless you actually want that literal entity to survive; it will not be decoded away for you on a normal text module. | `[et_pb_text ...]<p>Terms &amp; conditions apply.</p>[/et_pb_text]` | `[et_pb_text ...]<p>Terms %26amp%3B conditions apply.</p>[/et_pb_text]` (attribute-style escaping doesn't apply to content, so this renders literally) |

Caveat (documented in `research/tools/notes/escaping.md`, not exercised by any of this skill's own
examples): for **URL-type attributes only** (`url`, `button_link`, `button_url`, `image_src`,
`redirect_url`), Divi's own decoder skips the general `%22`/`%92`/`%5c` replace and leaves those
three sequences as **literal text** in the Visual Builder's JSON — only `%91`/`%93` inside the
query string get decoded there. Avoid encoding `"`, `\` inside a URL attribute at all; a real URL
shouldn't need them unescaped anyway.

## Bookkeeping attributes

These are written on (almost) every module tag, but describe the module's editing state rather
than its design — the validator accepts them on every module (they're `type: "skip"` in the schema
or defined as always-legal `global_attrs`) and mostly doesn't check their *values*:

- **`_builder_version="4.27.9"`** — the Divi version that saved this markup. Always set it to the
  site's actual Divi version (from `tokens.json`'s `site.divi_version`, or the schema's own
  `divi_version` — `4.27.9` for this site). Divi uses this to decide which legacy-vs-current CSS
  generation path to run for that one module; an unrelated/future version number is not rejected
  by the parser but is a lie about what actually built the page.
- **`_module_preset="default"`** — which of the site's Global Presets style this module inherits.
  Use `"default"` unless you are deliberately reusing one of the site's real presets. If you set it
  to something else, that value must be a preset UUID that actually exists in the site's
  `tokens.json` `presets` map, or `validate.py` warns `W_UNKNOWN_PRESET` (not blocking, but a
  preset id the site doesn't recognize is very unlikely to render the way you intended — not
  independently verified against the real site for this task, so treat it as a strong hint to
  double-check, not a confirmed rendering outcome).
- **`global_colors_info`** — JSON bookkeeping (escaped the same way as any other attribute:
  `%91`→`[`, `%93`→`]`, `%22`→`"`) mapping a color id to the list of attribute names on *this
  module* that use it, e.g. `global_colors_info="{%22gcid-…%22:%91%22background_color%22%93}"`.
  See [value-formats.md](value-formats.md#colors) for the two real shapes this takes. Omit it (or
  set `"{}"` ) unless you are actually using a `gcid-` global color; it isn't required for plain
  hex/rgba colors.
- **`admin_label`** — the module's display name in the builder's layer tree. Purely cosmetic; give
  modules a meaningful one (`admin_label="Hero"`) so a human opening the Visual Builder later can
  navigate the page.
- **`fb_built`** — added automatically to sections the Visual Builder itself has saved
  (`includes/builder/functions.php:2093`). Safe to omit when hand-authoring; don't invent a value
  for it.
- **`locked="on"|"off"`** and **`collapsed="on"|"off"`** — pure Visual Builder UI state (is this
  module locked from editing / collapsed in the layer tree). Neither affects rendering; omit both
  unless you specifically want the page to open pre-collapsed or pre-locked in the builder.

## Post meta

`post_content` alone is not enough to make a page render through the Divi Builder — WordPress
needs to be told to run the builder's `the_content` filters on it. Confirmed on the real site
(`research/tools/notes/doc-experiments.md`, experiment 2): a page with correct Divi shortcode in
`post_content` but without `_et_pb_use_builder` set rendered as plain unprocessed shortcode text.
Required/relevant post meta (set with `wp post meta update <id> <key> <value>`, not inside
`post_content`):

| meta key | required? | value | purpose |
|---|---|---|---|
| `_et_pb_use_builder` | **required** | `on` | tells WordPress's `the_content` filter chain to run the Divi Builder's rendering instead of the classic editor's (`wpautop`-only) path. Without it, `post_content` is treated as plain text/HTML and shortcode is not recognized as Divi module output. |
| `_et_pb_page_layout` | optional | `et_full_width_page`, `et_right_sidebar`, `et_left_sidebar`, `et_no_sidebar` | the theme's outer page template. Pages built entirely from fullwidth/specialty sections almost always want `et_full_width_page` so the theme doesn't reserve sidebar space next to full-bleed sections. |
| `_et_pb_old_content` | optional | the page's pre-builder HTML | Divi's own "restore previous content" safety net when a human first enables the builder on an existing page in the WP admin. Not something a hand-authored page needs to set. |
| `_et_pb_built_for_post_type` | optional (Divi defaults it to `page`) | the post type (`page`, `post`, ...) | used by Divi's own admin UI to remember which post type this builder content was made for; harmless to leave unset for a `page`. |

## What never to write

- **Preset UUIDs that aren't in `tokens.json`.** `_module_preset="<uuid>"` for a preset the site
  doesn't actually have isn't a parse error (`validate.py` only warns `W_UNKNOWN_PRESET`), which
  is worse than an obvious break — the page can look fine in isolation while quietly not using the
  style you intended. Always use `"default"` unless you've confirmed the UUID is real.
- **Divi 5 block markup.** Divi 5 (the React/block-based rewrite) uses a completely different
  on-disk format (block comments and a JSON `computed_style`); none of it is valid inside a Divi 4
  `post_content` string, and this skill's validator, module schema, and every reference here are
  Divi 4 (`et_pb_*` shortcode) only.
- **`<!-- wp:… -->` Gutenberg block comments.** Divi 4 pages are shortcode, not blocks; mixing in
  block comments doesn't extend a Divi page, it just becomes inert (or actively broken, if it
  wraps content that was meant to be inside a section) text sitting next to the shortcode tree.
