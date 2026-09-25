# Spike: a pure-Python Divi 4 renderer (no WordPress, PHP or Node)

Spike run on 2026-09-24 (macOS arm64, Python 3.10, Divi 4.27.9 on `divi-test.local`). Question: how close can a renderer and preview server written only with the Python standard library get to real Divi 4 output? The answer is compared with the WordPress Playground approach already proven in `research/playground-spike.md`.

Prototype: `research/python-renderer-spike/`. Background: `research/divi-render-engine.md`.

## TL;DR: not worth it as the main preview. Keep Playground.

- **Fidelity is high on the pages it was tuned against (verified):**
  - **Page 11, compared with the live page:**
    - The `.et-l` builder markup is byte-identical (31,755 chars).
    - Builder CSS: 2,063 of 2,063 declarations match, with 0 extra.
    - All 302 builder elements have identical geometry and computed style.
    - The builder area shows 0.000 % pixel difference at 1440 px and at 390 px.
  - **`handwritten-landing.txt`:** the same result. The markup is identical when whitespace is ignored, CSS is 82/82 and the pixel difference is 0.000 %.
- **Fidelity on pages it has never seen is lower (verified).** I wrote held-out test pages that use only the supported modules but pick options in new combinations:
  - First page, untuned: 89.9 % of Divi's CSS declarations matched (408/454, 10 wrong or extra), and 127 of 129 elements had the right class list.
  - I then spent about 20 minutes on one fixing pass. A second new page reached 96.0 % (214/223, 3 wrong) and 90/94 elements.
  - Visually, that second page looks right to a person but is not exact. A missing section class (`et_pb_inner_shadow`) and a divider spacing difference push later content down by 90 px. The pixel difference is 17 %, and only 20 of 72 elements keep identical geometry.
- **Modules it does not support fall back to a visible placeholder (verified).** On a page with 11 unsupported module types, 8 of 43 CSS declarations matched and 11 of 141 elements. The coverage report correctly lists every missing module and ignored attribute.
- **Speed (verified):**
  - Rendering page 11 in-process takes 34 ms warm and 48–52 ms cold.
  - The command-line tool runs in 0.10–0.12 s end to end.
  - In the preview server a page request takes about 55 ms, and an edit shows up in the browser 50–750 ms later (it polls for changes once a second).
  - Playground takes about 1.0 s per render in serve mode and about 4–5 s for a one-shot render.
- **Why not:**
  - Every new combination of modules and options turns up new special cases that are hard-coded in Divi's PHP. Each takes about 5–15 minutes to fix, but only after real Divi output exposes it, so you still need the PHP runtime to produce reference output.
  - Some modules need WordPress data: blog, portfolio, post slider, menus, and the 25 WooCommerce modules. These cannot be rendered without WordPress at all.
  - The Python path still needs Divi's own files at runtime: the static CSS, icon fonts, JS, mask SVGs and font list. So it does not remove the need for a Divi download (Elegant Themes credentials) or live-site access, which is the main thing it would save over Playground.
  - Playground is already exact and already fast enough for an edit-and-reload loop.

---

## 1. What was built

| File | Role | Size |
|---|---|---|
| `divi_render.py` | Standard-library-only renderer: shortcode in, full HTML page out, plus a coverage report | ~1,960 lines |
| `serve.py` | Standard-library `http.server`. Serves `/<name>` from `<pages>/<name>.txt` and re-renders on every request. Serves `/__divi/<path>` (theme fonts, images and JS; no PHP files, path traversal blocked) and `/__mtime/<name>` for auto-reload. | ~100 lines |
| `evaluate.py` | Evaluation: markup (tag and class sequence of `.et-l`, identical class lists, byte and whitespace-normalised identity) and builder CSS as (media, selector, declaration) sets. It uses the same method as `playground-prototype/compare.py`. | ~150 lines |
| `shoot.mjs` | Evaluation only. Drives headless Chrome through the DevTools protocol (Node's built-in WebSocket). Captures the builder-area PNG at 1440 and 390 px, plus a geometry and computed-style record for every `.et-l [class*=et_pb_]` element. It waits for fonts and images. | ~80 lines |
| `compare_visual.py` | Evaluation only. Pillow pixel diff of the builder-area crops, a geometry and style comparison, and side-by-side PNGs. | ~55 lines |
| `evaluate_all.sh` | Re-runs everything and writes `out/summary.json` | |
| `pages/heldout-*.txt` | Held-out test pages, written without looking at their real Divi output | |

`out/` holds the numbers (`*-eval*.json`, `*-visual.json`, `*-coverage.json`, `summary.json`) and small side-by-side screenshots (`sbs-*.png`: real Divi on the left, Python on the right). The full-size screenshots, the reference HTML (`out/truth/`) and the rendered HTML are covered by `.gitignore`. `out/divi_render.before-heldout.py` is a snapshot of the renderer before the tuning pass, also ignored.

### How it works

1. **Parsing** reuses `Skill/divi-page-builder/scripts/divi_shortcode.py`, imported and unchanged.
2. **Module settings and defaults** come from the repo's schema dump, `research/divi-schema/modules/<slug>.json`, which is made from Divi by `research/tools/dump-divi-schema.php`. It supplies three things:
   - `fields`: defaults, with `default_on_front` taking precedence over `default`, as in PHP `get_default_props()`.
   - `advanced_fields`: the CSS selectors and "important" flags for fonts, background, borders, box shadow, margin/padding, max-width, button, text and overflow.
   - `main_css_element` for each module.
   **This dump is why the approach works as well as it does.** Most of Divi's CSS output is driven by configuration rather than hand-written code, so a generic engine plus the dump reproduces it.
3. **A generic CSS engine** ports `process_additional_options` from `EL`, which is `includes/builder/class-et-builder-element.php`:
   - Fonts: `et_builder_set_element_font`, the font stack, size, colour, letter spacing, line height, alignment, text shadow, `_last_edited`-gated tablet and phone values, and hover.
   - Background: colour, linear, radial and conic gradients, image with position, size and repeat, hover colour, and mask SVGs.
   - Borders: radius, all-sides and per-side width, style and colour, responsive values, and the `et_pb_with_border` rule.
   - Box shadow: presets merged with overrides, plus hover.
   - Custom margin and padding, including responsive inheritance and hover.
   - Width, max-width and module alignment.
   - Buttons: roughly the first third of `process_advanced_button_options`, meaning the icon, `:after` and `:before` rules, hover, responsive values, and the rule that applies default checks against the hard-coded `button_*` field names.
   - Hover transitions: `transition` on the combined selectors of the hover-enabled options.
   - Overflow.
   - The minified output format.
4. **Module handlers** copy the `render()` output templates, whitespace included. There are 19: section, row, row_inner, column, column_inner, heading, text, button, image, blurb, accordion, accordion_item, toggle, number_counter, divider, cta, slider, slide and fullwidth_header. Each also carries its module-specific `set_style` and `generate_styles` calls, such as the blurb icon, image alignment, accordion and toggle states, divider line, slider arrows and dots, and slide background inheritance. Order classes are counted per module type in document order, as in `set_order_class`.
5. **Page shell:**
   - Divi's `style-static.min.css` is read at runtime from `--divi-path`, with `url()`s made absolute, or fetched from a live site with `--theme-css-url`.
   - Stock customizer CSS.
   - A Google Fonts `<link>` built from `core/json-data/google-fonts.json`.
   - Divi's front-end JS read from the theme, plus jQuery from the local WordPress install or a CDN.
   - A stub of the default Divi header and footer. There is no WordPress, so there are no real menus or Theme Builder layouts.
   - Theme assets have two delivery modes. `serve.py` serves fonts, images and JS over HTTP from `/__divi/<path>`. A standalone file inlines the icon and web fonts (woff2 and woff) and the logo as `data:` URIs, which adds about 0.6 MB and brings page 11 to 2.07 MB. `--no-embed-fonts` switches back to `file://` URLs. See "Theme assets" below.
6. **Coverage:** props are held in a dict that records which keys were read. For each module, any attribute that was set, is not bookkeeping and was never read is reported as ignored. Unsupported modules render as a visible dashed placeholder and are counted.

## 2. Fidelity results (all verified by running)

Reference output ("truth"):
- For page 11: the live page at `http://divi-test.local/probe-divi-ai-emergency-plumber/`, plus the render prototype's output. The render prototype was verified identical to live in the earlier spike, and its CSS is inline, which makes counting declarations straightforward.
- For every other page: `research/render-prototype/run.sh`, meaning real Divi 4.27.9 on the local site.

Pixel diffs are taken over the **builder area only** (the `.et-l` bounding box). The Python page has a stub header and footer, so full-page diffs are not comparable. Screenshots are taken after fonts and images have loaded and after a 4 s settle.

### Side by side with the Playground spike (page 11)

| Check (page 11) | Playground spike | Python renderer |
|---|---|---|
| `.et-l` markup | Byte-identical (31,755 chars) | **Byte-identical** (31,755 chars, also against live) |
| Builder CSS declarations | 2,064 / 2,064, 0 missing, 0 extra | **2,063 / 2,063**, 0 missing, 0 extra¹ |
| Element geometry and computed style | Identical (earlier LocalWP check, 302 elements) | **302 / 302 identical** at 1440 and 390 px, against the real render and against live |
| Pixel diff | 0.023 % desktop / 0.041 % phone, **full page** against live (header nav plus counter animation) | **0.000 % / 0.000 %, builder area** against live and against the real render |
| Page shell (header, footer, menus, Theme Builder) | The real site's (it is WordPress) | Stub only |
| Unseen pages | Exact by construction (real Divi code) | **89.9 % → 96.0 %** of CSS declarations, 95.7–98.4 % of elements (see below) |
| Unsupported modules | None (all 64 plus WooCommerce run) | Placeholder, listed in the coverage report |

### Theme assets: a problem found during review, now fixed and verified

- **The problem:** the first standalone output referenced theme files by `file://` URL: the ETmodules and FontAwesome woff2/woff/ttf fonts, and `images/logo.png`. When that HTML is opened over `http://`, Chrome blocks every one of them ("Not allowed to load local resource"), so all blurb and accordion icons render as empty boxes. The user hit this when viewing `page11-py.html` through an HTTP server.
- **My screenshots were not affected.** `shoot.mjs` opened the Python pages from `file://`, where `file://` sub-resources are allowed. An earlier bug did affect them: unquoted paths containing a space (`Local Sites`) broke the icon fonts, giving icon boxes 23 px wide instead of 32 px and 48 of 302 elements with the wrong geometry. That was fixed before the numbers above were taken.
- **Effect of the blocked-font case, reproduced:** the `--no-embed-fonts` page served over `http://127.0.0.1` differs by 0.11 % at 1440 px and 0.29 % at 390 px, with 254/302 elements having identical geometry (all 48 differences are icon glyph boxes).
- **After the fix:** the standalone file served over HTTP and `serve.py` (fonts through `/__divi/`) both measure **0.000 % / 0.000 % with 302/302 elements identical** against the real render. Any preview a browser opens needs to get Divi's assets over HTTP or as `data:` URIs.

¹ The counts differ by one because of the reference used. The Playground spike counted against the live page's unified and deferred CSS files. This spike counts against the inline builder `<style>` from the render prototype.

### All pages

| Page | Role | Elements with identical class list | Markup identity | Builder CSS declarations (common / real, extra) | Pixel diff 1440 / 390 | Geometry identical (1440) |
|---|---|---|---|---|---|---|
| `divi-ai-layout.txt` (page 11, 8 sections, 15 module types) | Tuned against | 359/359 | byte-identical | 2,063/2,063, +0 | 0.000 % / 0.000 % | 302/302 |
| `handwritten-landing.txt` (specialty section, fullwidth header, responsive, hover) | Tuned against | 91/91 | identical ignoring whitespace² | 82/82, +0 | 0.000 % / 0.000 % | 74/74 |
| `heldout-inscope.txt`, **before** tuning | Held out | 127/129 | no | **408/454 (89.9 %), +10** | not measured | not measured |
| `heldout-inscope.txt`, after one ~20 min fixing pass | Then tuned against | 129/129 | tag and class sequence identical | 454/454, +0 | 0.000 % / 0.000 % | 90/90 (84/90 in one earlier run³) |
| `heldout2-inscope.txt` (written after the fixing pass, never tuned) | Held out | **90/94** | no | **214/223 (96.0 %), +3** | 17.6 % / 17.0 % | 20/72 |
| `heldout-outofscope.txt` (tabs, testimonial, pricing, contact form, social, countdown, circle and bar counters, icon, section divider, transforms, animation, filters) | Out of scope | 11/141 | no | 8/43 (18.6 %), +0 | 26.5 % / 27.7 % | 3/97 |

² The only differences are newlines that Divi inserts between block tags in Text content.
³ The slider on this page auto-rotates every 5 s, so which slide is showing when the screenshot is taken differs between runs.

Side-by-side images:
- `out/sbs-page11-{1440,390}.png` and `out/sbs-landing-*.png`: the two are indistinguishable.
- `out/sbs-heldout2-inscope-1440.png`: looks right, but everything below the hero is shifted by 90 px. The hero section is missing its inner shadow class and the image is missing its sticky class.
- `out/sbs-heldout-outofscope-1440.png`: red placeholders, and the animated heading is invisible because it lacks Divi's animation data.

### What the held-out pages exposed

Each of these is a small special case. Fixing one takes 5–15 minutes, but only once real Divi output has shown that it exists.
- A gradient type is spelled differently: `circular` becomes `radial-gradient(circle at …)`.
- Background images are escaped with `esc_html` inside `url()`. Only non-default size, position and repeat values are printed, without `!important`, even on sections, where the image itself gets `!important`. `top_center` is printed as `center top`.
- Hover transitions go on the selector of the option being hovered (the link colour, or the button's `css.main`), not on the module's main selector.
- The Heading font's text shadow is controlled by its own `{font}_text_shadow_*` options.
- The standalone Toggle module uses a different selector family from accordion items.
- Buttons: `_is_field_default('button_text_size', …)` is called with the hard-coded name `button_*`. So on the fullwidth header's `button_one`, the default 20 px size is printed, and icon placement is treated as non-default. The responsive icon rules for a left-placed icon (`:before`/`:after` swaps in media queries) also had to be added.
- `use_background_color="off"` on the CTA cancels its default `#7EBEC5` background.
- Image alignment `center` prints only `text-align`.
- When a column has a border, Divi inserts `et_pb_column_<type>` at position 1 of its class list, after `et_pb_with_border`.
- The slide title is wrapped in `<a>` when `button_link` is not `#`.
- The divider's `height` option.
- Still open on `heldout2`: the section's `et_pb_inner_shadow` class, the image's `et_pb_image_sticky` class when `show_bottom_space` is off, the column's `et_pb_section_video_on_hover` class and hover background image when a hover background is set, `et_pb_divider_hidden` removing `et_pb_divider` from the class list, and an extra desktop-only padding copy for rows with a box-shadow hover.

Rather than new families of features, these are the long tail of special cases inside families already covered. That long tail is what makes exact parity expensive.

## 3. Timings (verified)

| | Python renderer | Playground spike |
|---|---|---|
| Render page 11, in-process, warm | **34 ms** median of 20 | — |
| Command-line one-shot (process start, render, write 2.07 MB file with fonts inlined) | **0.10–0.12 s** | 4.2–5 s |
| Server request for page 11 (render plus 1.4 MB response, fonts through `/__divi/`) | **~55 ms** (first request 80 ms) | ~1.0 s |
| Edit to visible change in the browser (1 s mtime poll, measured through the DevTools protocol, 5 samples) | **53–745 ms** (mean ~400 ms) | ~1 s plus manual reload |
| Cold start | none (standard library only) | 25–30 s (npm install) |
| Dependencies | Python 3.8+. At runtime it still needs a Divi 4 copy for CSS, fonts, JS, masks and the font list, or a live-site URL for the CSS. | Node and npm, plus a Divi zip (Elegant Themes credentials the first time) |

## 4. Coverage report summary (verified)

`divi_render.py … --coverage cov.json` reports, per module type, the number of attributes set and any attribute that was never read. For unsupported modules and features it also gives a count.
- **Page 11: 97.9 %** of 2,445 attributes were read. The 52 ignored ones are mostly harmless:
  - Legacy gradient start and end values (Divi also uses `_stops`).
  - `box_shadow_*` values while the style is `none`.
  - `background_mask_style` while the mask is off.
  - `custom_padding__hover` without the enable flag.
  - `quote_icon_color` on accordion.
- **Landing page: 96.9 %.**
- **`heldout2`: 95.1 %.** It correctly flags `inner_shadow`, `show_bottom_space` and the hover background, which are exactly the misses that cost pixels.
- **Out-of-scope page: 26.6 %,** with all 11 unsupported module types listed.

Limitation: "read" is not the same as "honoured correctly". The first held-out page showed 100 % coverage and still had 10 % of its CSS wrong. The report is good at catching unsupported modules and options, and cannot catch quirks.

## 5. Effort estimate (inferred from building this)

This spike took about one working session:
- About 2,000 lines of Python: a generic engine plus 19 module handlers.
- One fixing pass of about 20 minutes, which cleared 12 distinct special cases.

The generic engine reaches most of the CSS because the schema dump already contains the selectors and defaults. The cost is in module `render()` code and in special cases that are hard-coded in PHP.

**(a) "Looks right" for the ~30 modules used on landing pages and the main option families.** Target: 95 % or more of declarations on unseen pages, no layout shifts, and the rest reported by the coverage report. About **3–4 engineer-weeks**:
- About 11 more modules at 2–4 hours each: tabs, testimonial, pricing tables, contact form, social follow, icon, circle and bar counters, countdown, team member, video, code and gallery (gallery needs attachment data). About 4–6 days.
- Missing option families, about 6–10 days in total:
  - Section dividers (SVG builder in `module/field/Divider.php`, ~1 day).
  - Transform, filters, position and z-index, height and min/max height (~2 days).
  - Animations, sticky, scroll effects and motion (~3 days). Divi's JS needs JSON data that PHP prints, such as `et_animation_data` and `et_pb_sticky_elements`.
  - Background video, parallax and patterns (~1–2 days).
- Site settings (~4–6 days):
  - Global presets merged under module attributes (~0.5 day).
  - Global colours (~0.5 day).
  - Customizer-derived module defaults (`ET_Global_Settings`) and the customizer CSS (~2k lines in `functions.php`, 3–5 days).
- Hardening against a corpus of 50–100 pages rendered by Playground, tuning until unseen pages stop surfacing new special cases (5+ days). The harness for this exists now: `evaluate.py`, `shoot.mjs` and `compare_visual.py`.

**(b) Near-exact parity for all 64 modules and ~9k fields.** At least **3–6 engineer-months**, and still not complete:
- The surface to port is large:
  - Module PHP: 38.5k lines in 60 files.
  - WooCommerce modules: another 15.9k lines.
  - Helpers: 10.5k lines. Field classes: 8.2k lines.
  - `EL`: 24.3k lines.
  - There are about 245 `set_style`, 184 `generate_styles` and 77 responsive-CSS call sites, and 29 attribute migrations.
  - This spike covers roughly 15 % of that surface.
- Some modules can never be exact without WordPress, because their output is WordPress data: Blog, Portfolio, Filterable Portfolio, Post Slider, Post Title, Post Content, Posts Navigation, Comments, Menu and Fullwidth Menu, Search, Login, Sidebar, and all 25 WooCommerce modules. At best they get realistic placeholders.
- Contact form, signup and map rely on server-side nonces, captcha and API keys.

**The hard parts, in rough order:**
1. Special cases coded per module and per option: named-default checks, class insertions, dropped defaults. The divider's `divider_position` default is not applied on the front end, for example.
2. The button engine alone is about 950 lines of branching.
3. Responsive, hover and sticky combinations. Hover changes selectors and transitions, and sticky needs `et_pb_sticky_elements` JSON plus the sticky JS.
4. JS-driven modules and features need PHP-printed JSON: animations, sticky, motion and scroll effects, counters, sliders, video, maps and countdown.
5. Option defaults derived from the customizer and global presets.
6. Section dividers, masks and patterns.
7. Divi's static CSS, icon fonts and JS are still needed at runtime, which is a licensing and distribution question.
8. The whitespace and escaping rules of `wptexturize` and `esc_url`/`esc_html`, and shortcode content formatting.

**Maintenance:**
- Divi 4 releases arrive roughly monthly (4.27.x).
- The `advanced_fields` dump regenerates automatically with the existing `research/tools` pipeline, which covers selector and default changes.
- Changes to module `render()` code and to the special cases have to be found by diffing against real output for every release. Expect about 1–3 days per release once the port covers the ~30 modules.
- Divi 5 is a different engine (block-based, with a new style system), so none of this carries over.

## 6. Recommendation

**Use Playground, or `render.php` on a local mirror, as the preview. Do not build the Python renderer into the skill.**
- Playground is exact by construction, runs every module including WooCommerce and the ones that depend on WordPress data, applies client settings bundles, and already re-renders in about 1 s.
- The Python renderer's advantages are real: 34 ms renders and no Node or WordPress. But it:
  - still needs Divi's files at runtime, so it still needs Elegant Themes credentials or a live-site URL;
  - misses special cases silently on content it has not seen;
  - needs Playground or LocalWP anyway to produce reference output for its own tuning and regression tests.
- Keep the spike's **evaluation harness** (`evaluate.py`, `shoot.mjs`, `compare_visual.py`). It works just as well for regression-testing Playground previews against live pages.
- **Hybrid, only if a no-Node environment becomes a hard requirement:**
  - Ship the Python renderer as a clearly labelled "approximate preview".
  - Limit it to the ~20 modules that AI-generated landing pages use.
  - Always show its coverage report, plus a banner for unsupported modules or options.
  - Run CI against a corpus rendered by Playground.
  - Budget for (a) above, and accept that the result will occasionally be visibly wrong.

## 7. Verified or inferred

- **Verified by running:**
  - Every number in §2, §3 and §4.
  - Byte identity with live page 11.
  - Icon fonts: blocked over HTTP with `file://` URLs, and fixed with `data:` URIs and the `/__divi/` route.
  - Pixel, geometry and style identity for page 11 and the landing page.
  - The held-out results before and after tuning, and the out-of-scope result.
  - Server behaviour: re-renders on every request, `/__divi/` refuses PHP and path traversal, and edit-to-reload latency.
- **Inferred, not measured:**
  - The effort and maintenance estimates in §5.
  - The claim that the remaining modules follow the same patterns.
  - The per-release cost.
  - That customizer and preset support would take the time estimated.
  - The Divi 5 statement (not examined in this spike).
- **Caveats:**
  - Only one Divi version (4.27.9) and stock site settings were tested. The global presets referenced on page 11 do not exist on the test site, so page 11 renders with default presets.
  - Pixel diffs cover the builder area only.
  - The held-out pages were written by the same person who wrote the renderer. Real AI-authored pages, like page 11, use a narrower set of options, which makes the held-out numbers pessimistic for typical AI output. Hand-built sites would be less favourable.

## Reproduce

```
cd research/python-renderer-spike
python3 divi_render.py ../../tests/fixtures/valid/divi-ai-layout.txt -o out/page11-py.html --coverage out/page11-coverage.json
python3 serve.py --pages <dir with name.txt files> --port 8791   # http://127.0.0.1:8791/<name>
# Reference output (real Divi):
WP=../tools/wp-local.sh ../render-prototype/run.sh pages/heldout2-inscope.txt out/truth/heldout2-inscope-real.html
python3 evaluate.py out/truth/page11-real.html out/page11-py.html --show 20
./evaluate_all.sh    # renders, evaluates, screenshots and pixel-diffs all pages -> out/summary.json
```
