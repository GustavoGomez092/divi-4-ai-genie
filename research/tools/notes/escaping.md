# Attribute value escaping: our parser vs. Divi's own parser

Method: run Divi's `et_fb_process_shortcode()` (the same function the Visual
Builder uses to turn shortcode text into its JSON module tree) on our test
fixtures via `research/tools/divi_parse.php`, and diff every attribute value
against `divi_shortcode.Node.value()` for the same node. See
`tests/test_divi_judge.py`.

## Result

`test_parse_agrees_with_divi` passes with **zero mismatches** across all four
required fixtures (`handwritten-landing.txt`, `unicode.txt`,
`divi-ai-section.txt`, `divi-ai-layout.txt`), including tree shape and every
attribute value (plain text, unicode, emoji, `custom_css_*` with embedded
quotes/backslashes, and `global_colors_info` JSON blobs containing `%91`/`%93`).
No change to `unescape_attr_value` was needed.

The table below documents *why* they agree — Divi's own code takes a more
roundabout path than a straight decode table, and it's worth recording so a
future change to `unescape_attr_value` doesn't accidentally break parity.

| attribute(s) | we read (`unescape_attr_value`) | Divi reads (`et_fb_process_shortcode` output) | why | source |
|---|---|---|---|---|
| general text attrs (`title`, `content`, any non-icon/non-URL field) | `%22`→`"`, `%91`→`[`, `%93`→`]`, `%92`→`\`, `%5c`→`\` | same literal characters | Divi's module property setup first re-encodes `%91`/`%93` to the HTML entities `&#91;`/`&#93;` (`_decode_double_quotes`, general branch), but when `render_as_builder_data()` builds the VB JSON `attrs`, it runs every string value through `html_entity_decode()`, which turns `&#91;`/`&#93;` straight back into literal `[`/`]`. Net effect equals a direct one-shot decode, which is what our function does. | `includes/builder/class-et-builder-element.php:2270-2295` (`_decode_double_quotes`, encodes to `&#91;`/`&#93;`); `includes/builder/class-et-builder-element.php:3996` (`html_entity_decode($value)` reverses it) |
| `content__hover`, `content_tablet`, `content_phone`, `raw_content__hover`, `raw_content_tablet`, `raw_content_phone` | same decode table as above | same literal characters (verified with a manual `content_tablet="a %91b%93 c"` case → `"a [b] c"`) | `et_fb_process_shortcode()` itself pre-decodes these "decoded content fields" to `&#91;`/`&#93;` before the module even runs, then the same `html_entity_decode()` step above (line 3996) undoes it, again netting to a literal-bracket decode. | `includes/builder/functions.php:11542` (encode to `&#91;`/`&#93;`); `includes/builder/class-et-builder-element.php:3996` (decode back) |
| `global_colors_info` | `%91`→`[`, `%93`→`]`, `%22`→`"` | same literal characters | No HTML-entity round trip here — Divi does a direct `str_replace` in the builder-data attrs loop. Same end result as our generic decode. | `includes/builder/class-et-builder-element.php:4003` |
| `url`, `button_link`, `button_url`, `image_src`, `redirect_url` — **only** for `%91`/`%93` in the query string | `%22`→`"`, `%91`→`[`, `%93`→`]`, `%92`→`\`, `%5c`→`\` (same table, no special-casing by attribute name) | `%91`/`%93` in the query string decode to literal `[`/`]` (verified with `button_url="https://example.com/?x=%91y%93"` → `https://example.com/?x=[y]`) | For URL fields, `_decode_double_quotes` skips the generic `%22`/`%92`/`%5c` replace entirely and only HTML-entity-encodes `%91`/`%93` inside the parsed query string, then `esc_url_raw()`s the whole URL. The same `html_entity_decode()` at line 3996 later turns those entities back into literal brackets, matching our table for this subset. | `includes/builder/class-et-builder-element.php:2276-2288` (URL-only `%91`/`%93`→entity, query only); `includes/builder/class-et-builder-element.php:3996` (decode back) |
| `url`, `button_link`, `button_url`, `image_src`, `redirect_url` — `%22`, `%92`, `%5c` **anywhere in the value** | `%22`→`"`, `%92`→`\`, `%5c`→`\` (decoded, same as any other attribute) | **left untouched** — literal `%22`/`%92`/`%5c` text (verified with `button_url="https://example.com/?x=%22quoted%22"` → unchanged `%22...%22` in Divi's output) | Caveat, not exercised by any required fixture (none embed `%22`/`%92`/`%5c` in a URL-type attribute value). Because the URL branch of `_decode_double_quotes` never runs the general `str_replace(array('%22','%92','%91','%93','%5c'), ...)` — it only touches `%91`/`%93` in the query string — and `html_entity_decode()` at line 3996 has no effect on plain `%XX` percent sequences (only on `&#NN;`-style HTML entities), Divi's VB JSON keeps `%22`/`%92`/`%5c` as literal text for URL attributes. Our `unescape_attr_value()` intentionally applies one uniform decode table to every attribute (per `class-et-builder-element.php:2294`, which is the rule for the general non-URL case), so `Node.value()` on a URL attribute containing `%22`/`%92`/`%5c` will disagree with what the Visual Builder shows for that one attribute. This is a real, if obscure, corner case: authors should avoid encoding literal quotes/backslashes inside `button_url`/`url`/etc. — those characters aren't valid unescaped in a URL anyway. No code change made; documented for Task 9 (`page-format.md`) to flag if it ever becomes relevant to authored content. | `includes/builder/class-et-builder-element.php:2270-2295` (general branch skipped for URL keys), `:2276-2288` (URL-only branch) |

## Operational note: making `et_fb_process_shortcode()` runnable from WP-CLI

`ET_Builder_Element::render_as_builder_data()` bails out early and returns `''`
unless `$_POST['action']` is set or the `et_builder_module_force_render` filter
returns true — neither is true during a plain `wp eval-file` run, so every
module in the tree silently comes back empty. `research/tools/divi_parse.php`
adds `add_filter( 'et_builder_module_force_render', '__return_true' );` before
calling `et_fb_process_shortcode()` to force real rendering.

Source: `includes/builder/class-et-builder-element.php:3756-3758`.
