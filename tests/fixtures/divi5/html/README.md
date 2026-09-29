# Divi 5 public-page fixtures (tokens5_from_html)

Minimal public HTML of pages on the local Divi 5.13.1 test site (`http://divi-5-test.local`), used by
`tests/test_divi5_tokens_html.py`. These are **not** block fixtures: `_paths.d5_fixtures()` skips this directory.

## Provenance

Captured on 2026-09-28 with `curl` (second hit, so Divi's CSS cache was warm) after seeding the site with
`research/tools/divi5/r6_setup.php` (R6 global colors, design variables, a module preset `r6btnpreset1` and a
`divi/font` group preset `r6fontpreset1`) plus one extra page, "R6 plain", holding a single `divi/text` with no
variable reference. The site's options were restored with `r6_restore.php` and both pages deleted right after.

| File | Source |
|---|---|
| `r6-tokens-trace.html` | page "R6 tokens trace" (uses the colors, variables and both presets) |
| `r6-tokens-trace.content.txt` | that page's `post_content` (`wp post get --field=post_content`), verbatim |
| `r6-plain.html` | page "R6 plain": a page with no references, so Divi prints every active variable |
| `r6-home.html` | the site home page, whose `:root` colors live in a linked `et-cache` stylesheet |
| `r6-home.et-divi-dynamic.css` | the `:root{--gcid-…}` rule of that linked stylesheet |

## What was kept (and what was not)

Divi's licensed CSS is **not** included. Each page was cut down, by script, to:

- the `<style class="et-vb-global-data …">` blocks (only `:root` custom properties: `--et_global_*`, `--gvid-*`);
- the `:root{--gcid-…}` rule, and the page's own module/preset rules that reference `--gcid-`/`--gvid-` or a
  `preset--*` class, copied into a neutral `<style id="fixture-page-inline-css">` block;
- the Google Fonts `<link>`, the Divi generator meta and one `themes/Divi/…?ver=5.13.1` script tag (the version
  signal), and the home page's `et-cache` `<link>`;
- minimal markup: the section/row/column/module wrappers with their order and preset classes.

Everything else (Divi's base, dynamic and critical stylesheets, WordPress block CSS, scripts, header, footer) was
dropped.
