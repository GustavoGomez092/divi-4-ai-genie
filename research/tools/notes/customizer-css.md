# Customizer / global-color CSS output (Divi 4.27.9)

Discovery for Task 12 Step 1. Local site: `divi-test.local` (LocalWP), reached through
`research/tools/wp-local.sh`. Method: back up `et_divi`, set non-default values (accent, font
colors, body/heading fonts, body font size, content width, one global color), publish a page
titled `Plan Test: tokens html` built from `tests/fixtures/valid/handwritten-landing.txt`, curl it
twice (first hit builds Divi's CSS cache) following redirects (`curl -sL`, required — WP 301s
`?page_id=N` to the pretty-permalink URL, so a plain `curl -s` captures an empty 301 body), save the
third-party HTML to `tests/fixtures/html/customized-page.html`, delete the page, and restore
`et_divi`. Divi version under test: 4.27.9 (confirmed by `<meta content="Divi v.4.27.9"
name="generator"/>` and by `?ver=4.27.9` on `themes/Divi/style.min.css`).

## `<style id>` blocks present on a Divi 4 front-end page

In document order:
`global-styles-inline-css`, `divi-style-inline-inline-css`, `divi-dynamic-critical-inline-css`,
`et-critical-inline-css`, `wp-block-archives-inline-css`, `wp-block-categories-inline-css`,
`wp-block-heading-inline-css`, `wp-block-group-inline-css`, `wp-block-library-inline-css`.

Customizer overrides land in **`et-critical-inline-css`** (colors, content width) and
**`divi-dynamic-critical-inline-css`** (the body-font-size rule, mixed in with other selectors).
`divi-style-inline-inline-css` carries Divi's own base/reset rules (e.g. a bare `body{...}` with
hardcoded `font-size:14px;color:#666;font-family:Open Sans,Arial,sans-serif}`) — these come
*before* the Customizer rules in the document, and because both sets of rules use plain,
equal-specificity selectors (`body`, `h1`, `a`, …), **the browser (and our parser) must take the
*last* matching declaration, not the first** — the base rule for the same selector+property always
appears earlier in source order than the Customizer's override.

One block (`divi-dynamic-critical-inline-css`) opens with a `/*# sourceURL=... */` CSS comment
directly followed by its first real selector on the next line, e.g.
`/*# sourceURL=divi-dynamic-critical-inline-css */\n\nbody, .et_pb_column_1_2 ...`. A naive
selector-splitter that doesn't strip CSS comments first will glue that comment onto the `body`
token and silently fail to match it. **The parser must strip `/* ... */` comments from the
concatenated CSS before splitting rules.**

## Exact selectors observed for each Customizer value (last match wins)

| Token | Selector (exact, as one comma-item) | Property | Observed value |
|---|---|---|---|
| `body_text` (Font Color) | `body` | `color` | `#333344` |
| `heading` (Header Color) | `h1` (one item of `h1,h2,h3,h4,h5,h6{color:#112233}`) | `color` | `#112233` |
| `link` (Link Color) | `a` | `color` | `#0055ff` |
| `accent` (Accent Color) | `.et_pb_counter_amount` (one item of an 8-selector list incl. `.et_quote_content`, `.et_pb_post_slider.et_pb_bg_layout_dark`, …) | `background-color` | `#ff00aa` |
| `body_font` (Body Font) | `body` (one item of `body,input,textarea,select{font-family:'Lato',...}`) | `font-family` | `'Lato',Helvetica,Arial,Lucida,sans-serif` → first family `Lato` |
| `heading_font` (Heading Font) | `h1` (one item of `h1,h2,h3,h4,h5,h6{font-family:'Montserrat',...}`) | `font-family` | `'Montserrat',Helvetica,Arial,Lucida,sans-serif` → first family `Montserrat` |
| `body_size` (Body Font Size) | `body` (one item of a long selector list ending `...,body .et_pb_bg_layout_light .et_pb_post p,body .et_pb_bg_layout_dark .et_pb_post p{font-size:17px}`) | `font-size` | `17px` |
| `content_width` (Website Content Width) | `.et_pb_fullwidth_section .et_pb_title_container` (one item of `.container,.et_pb_row,.et_pb_slider .et_pb_container,.et_pb_fullwidth_section .et_pb_title_container,.et_pb_fullwidth_section .et_pb_title_featured_container,.et_pb_fullwidth_header:not(.et_pb_fullscreen) .et_pb_fullwidth_header_container{max-width:1200px}`) | `max-width` | `1200px` |

Notes on why the brief's starting-guess selectors needed adjusting:
- `.container` and `.et_pb_row` alone (the brief's guesses for `content_width`) each have an
  *earlier*, unrelated rule with the same selector and the same property
  (`.container{width:80%;max-width:1080px;...}` and a separate `.et_pb_row{max-width:1080px}`),
  which is Divi's default row-width CSS, not the Customizer's content-width override. Any exact
  single-selector guess here would collide with that default. `.et_pb_fullwidth_section
  .et_pb_title_container` is the compound selector-list item that only ever appears attached to
  the 1200px override, so it's unambiguous.
- `#top-menu li.current-menu-item>a` (the brief's fallback accent guess) does exist in the CSS but
  wasn't needed — `.et_pb_counter_amount` / `background-color` (the primary guess) matched
  correctly once "last match wins" was used, so the fallback is kept only as a defensive `or`.
- The brief's generator-meta regex assumed attribute order `name="generator" content="..."`; Divi
  4.27.9 actually emits `<meta content="Divi v.4.27.9" name="generator"/>` (content first, no
  space before the self-closing slash). The parser matches on `content="Divi v\.([\d.]+)"` alone
  (order-independent) and falls back to `themes/Divi/...?ver=([\d.]+)` (also confirmed present:
  `4.27.9` on `style.min.css`).

## Global colors (`gcid-*`)

**Not output by Divi 4.27.9 as a `--gcid-*` CSS custom property, and not output at all when the
global color is never referenced by a module on the page being rendered.**

We set `et_global_data.global_colors["gcid-planprobe"] = {"color": "#123456", "active": "yes"}` on
the site, but the test page's shortcode (`handwritten-landing.txt`) never assigns any module
attribute the value `"gcid-planprobe"`. Result: the strings `gcid-planprobe`, `planprobe`, and
`123456` all have **zero occurrences** anywhere in the captured HTML/CSS. There is no site-wide
`:root{--gcid-...}` block, no inline JSON registry, no trace at all — a global color that isn't
used on the rendered page leaves no signature in that page's public output.

Reading Divi's own source
(`includes/builder/class-et-builder-element.php`, `ET_Builder_Element::process_global_colors()`)
confirms the mechanism: at render time, for any prop whose *value* contains the literal substring
`gcid-XXXXXXXXX` (this is how a module's shortcode attribute looks when an editor assigns it a
Global Color — e.g. `button_bg_color="gcid-56f36a672"`), Divi does a plain string replace of that
substring with the resolved hex from `et_builder_get_all_global_colors()`, then generates CSS from
the now-fully-resolved value. So even when a global color *is* used by a module, the public CSS
never contains `gcid-` or a CSS variable — it contains the *plain resolved hex value*, byte-for-byte
indistinguishable from a hardcoded color assigned directly by the page author. There's no signal in
the front-end HTML that says "this hex came from a global color."

**Parser implication:** `tokens_from_html.py`'s `global_colors` dict is populated defensively by a
regex over `--gcid-[\w-]+:` CSS custom properties, in case a different Divi build/version emits
them, but on real Divi 4.27.9 output it will be empty. Global colors that *are* used are only
recoverable from the **shortcode** side (Task 11 already excludes `gcid-` values from the color
palette on purpose, since they're not resolvable without the site's private
`et_global_data` option) — public HTML alone cannot map a gcid to its hex value or vice versa.
`tests/test_tokens_from_html.py`'s `test_global_colors` assertion (expecting
`global_colors["gcid-planprobe"] == "#123456"`) was dropped per this finding; see the comment in
that test file citing this note.

## Fonts / Google Fonts

`<link rel='stylesheet' id='et-builder-googlefonts-cached-css'
href='https://fonts.googleapis.com/css?family=Montserrat:100,200,300,...|Lato:100,100italic,...&#038;subset=latin,latin-ext&#038;display=swap' ... />`
— both `Montserrat` (heading font) and `Lato` (body font) appear as `family=` values, `|`-joined,
each with a `:weights` suffix to strip. The existing regex in the brief's starter code
(`fonts\.googleapis\.com/css2?\?...`, splitting on `|` and `:`) handles this correctly as written;
no change needed.

## Restore verification

Pre-task md5 of `wp option get et_divi --format=json`: `083f759d82c93aa19d180ca14059ebdc`
(matches the value the controller recorded). After the experiment, `wp option update et_divi
--format=json < backup` did **not** restore byte-identically — the only diff was
`"builder_custom_defaults":{}` (original) vs `"builder_custom_defaults":[]` (after naive restore).
Cause: WP-CLI's JSON reader decodes with PHP's `json_decode($raw, true)` (associative arrays only),
so an originally-empty PHP `stdClass` (which `json_encode`s as `{}`) round-trips as an empty PHP
array (which `json_encode`s as `[]`) — `json_decode`/`json_encode` can't tell an empty object from
an empty array once decoded associatively, and PHP has no way to mark an empty array as "please
encode me as `{}`". Fix used: `wp eval` with `json_decode($raw, false)` (keep JSON objects as
`stdClass`, so `{}` stays `{}`) then a **shallow** `(array)` cast so the top level is array-indexable
again (Divi's code does `$o["accent_color"] = ...`) while nested values (including the empty
`stdClass` for `builder_custom_defaults`) keep their original type. Re-checked: restored option's
md5 is `083f759d82c93aa19d180ca14059ebdc`, byte-identical to the pre-task backup.
