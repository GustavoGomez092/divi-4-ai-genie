# Spike: a pure-Python Divi 5 renderer (Task 21)

Spike run on 2026-09-29 (macOS arm64, Python 3.10, Divi 5.13.1 cached, ground truth from the shipped Playground
preview). Question: is a stdlib-only renderer worth building for Divi 5 previews? Divi 4 has one
(`Skill/divi-page-builder/scripts/divi_render/`, the default Divi 4 preview since D4 spec Addendum C). Divi 5
previews currently render only in WordPress Playground: about 1 s per page in `serve`, about 5 s one-shot and
about 30 s cold, and they need Node 20+ plus about 1 GB of caches.

This spike follows the method of `research/python-renderer-spike.md` (D4): a throwaway prototype, markup and CSS
scored with `research/tools/fidelity.py`, pixels and geometry compared with that spike's `shoot.mjs` and
`compare_visual.py`, one tuned page, one held-out page, a single fixing pass, then a second held-out page that
was never tuned.

Prototype: `research/divi5/python-renderer-spike/`. Rendered HTML, truth renders and screenshots go under
`out/`, which is gitignored because it contains Divi's CSS.

## TL;DR: GO, scoped, with Playground kept as `--exact`

- **Reusing `divi_render` by converting Divi 5 back to Divi 4 does not work (measured).** Even with a perfect
  back-conversion (rendering the original D4 source that Divi's converter turned into each D5 fixture), the D4
  renderer's output matches real Divi 5 on only **23–52 % of builder CSS declarations**. Its (tag, class)
  markup ratio is **0.36–0.59**, and none of the 5 pages has an identical sequence. Divi 5 prints different selectors, longhand
  properties, new CSS variables and new classes, and the conversion map only runs D4→D5. D5-only values such as
  variables, relative colours, presets and flex layout have no D4 form.
- **A native renderer driven by Divi 5's own metadata generalizes well (measured).** The prototype has about 650
  lines, 6 modules and a generic style engine. It reads each module's `module.json` (selectors,
  `styleProps` important flags, `propertySelectors`) and `module-default-printed-style-attributes.json` from the
  cached theme at runtime.

  | Page | Role | Elements with identical class list | `.et-l` markup | Builder CSS declarations (common / real, extra) | Pixel diff 1440 / 390 | Geometry identical (1440 / 390) |
  |---|---|---|---|---|---|---|
  | `tuned` (hero-centered + process-steps recipes, tokens) | Tuned against | 63/63 | **byte-identical** | **343/343, +0** | **0.000 % / 0.061 %¹** | 51/51 / 51/51 |
  | `heldout` (hero-background-image + service-area-list), **before** fixing | Held out | 52/52 | identical ignoring `\n` inside lists | **140/156 (89.7 %), +0** | not measured | not measured |
  | `heldout`, after one fixing pass (5 special cases) | Then tuned against | 52/52 | byte-identical | 156/156, +0 | 0.000 % / 0.089 %¹ | 28/28 / 28/28 |
  | `heldout2` (Divi AI native D5 section + converted brand-kit + unicode; **never tuned**) | Held out | **49/57** | tag sequence equal, 8 class lists differ | **467/483 (96.7 %), +0** | 0.90 % / 2.61 % | 50/52 / 51/52 |

  ¹ A 1-px strip on the top edge of the builder area. The real page has the Divi header above it and the spike's
  shell has none (inferred, not investigated).

  - **Not one wrong or extra declaration on any page.** Every miss is a missing declaration.
  - The Divi 4 spike, in the same situation: held-out pages at 89.9 % with 10 wrong, and 96.0 % with 3 wrong and a 90 px layout shift.
- **Speed (measured):**
  - Builder render: **5–7 ms** in-process.
  - Command-line run including interpreter start: **0.04–0.05 s**.
  - Playground today: 4.7–5.5 s per one-shot render (measured while making the truths), about 1 s in `serve` and about 30 s cold.
- **Why GO, when the D4 spike said no:**
  - The user already chose the Python renderer as the default Divi 4 preview on weaker evidence (Addendum C).
  - Divi 5's render path is far more data-driven than Divi 4's, so a generic engine reproduces more of it, and it does so with fewer wrong guesses.
  - Without a Python path, Divi 5 is the only format whose preview needs Node, which is inconsistent with Divi 4.
- **Why scoped:**
  - The Divi 5 surface is 1.5–2× Divi 4's.
  - Divi 5 releases weekly (5.13.1 → 5.14 was already offered on 2026-09-29).
  - Presets, flex/grid layout and interactions are large, unmeasured areas.
  - The renderer should cover the ~28 module types the Divi 5 recipes use. The preview should hand anything its coverage report flags to Playground automatically.
- **Effort (inferred):** about **4–5 engineer-weeks** to reach the recipe module set with the Divi 4 acceptance bar, then about **0.5–1 day a month** of release tracking. See §6.

---

## 1. The Divi 5 render surface, and what differs from Divi 4

The Divi 5 PHP render path is under `includes/builder-5/server/` of Divi 5.13.1. Line counts come from `wc -l` on the LocalWP copy.

| Part | What it does | Lines (files) |
|---|---|---|
| `Packages/ModuleLibrary/*/*Module.php` | Per-module `render_callback`, `module_classnames`, `module_styles`, script data | **70.5k (88)**, plus WooCommerce 24.8k (25) |
| `Packages/Module/Options/*` | Option groups: `*Style.php`, `*Classnames.php`, script data (background, font, spacing, sizing, border, box shadow, button, layout, transition, sticky, scroll, interactions, …) | 33.9k (30 `*Style.php` files) |
| `Packages/StyleLibrary` | Declaration functions (font, background, border, spacing, sizing, button, transform, filters, …) and gradient/variable utils | 11.2k |
| `Packages/Module/Layout/Components` | `ModuleElements` (element render and style dispatch), `MultiView` (responsive content), `DynamicContent` (post data) | 4.3k + 4.1k + 13.7k |
| `Packages/GlobalData` | Global colours, variables, module and group presets | 8.7k |
| `FrontEnd/Assets` | Dynamic assets (which static CSS/JS files a page gets), critical CSS, static CSS files | 17.9k |
| `FrontEnd/BlockParser`, `FrontEnd/Module/Style.php`, `ModuleUtils`, `Framework/Breakpoint` | Block tree store, order indexes, style grouping, attr inheritance (`use_attr_value` getOrInheritAll) | 4.9k + 2.5k + 6.1k + 1.1k |
| `*PresetAttrsMap.php` | Preset and conversion maps (not the render path) | 79.2k |
| Metadata (`visual-builder/packages/module-library/src/components/*/`) | For 90 modules: `module.json` (attribute → element selector, `styleProps`), `module-default-render-attributes.json`, `module-default-printed-style-attributes.json` | data |

Scale of the Divi 5 render code:
- About 162 declaration functions.
- 116 `Style::add` call sites.
- 386 module-level `declarationFunction` overrides.
- The D4 spike counted about 245 `set_style`, 184 `generate_styles` and 77 responsive-CSS call sites.
- Overall the surface is **about 1.5–2× Divi 4's**, which was 38.5k lines of module PHP, 24.3k of `EL`, 10.5k of helpers and 8.2k of fields.

**What differs from Divi 4:**

1. **Style generation is declarative.**
   - Each element's selector, the properties it marks important and its per-property selectors live in `module.json`.
   - The values the static CSS already covers ("default printed") live in JSON next to it.
   - Module PHP mostly calls `$elements->style(['attrName' => …])` and lets `ElementStyle` walk the option groups.
   - Divi 4 carried much of this as imperative code inside `EL` and the module `render()` methods.
   - **This is why a generic engine gets further on Divi 5:** the prototype reads this metadata unchanged.
2. **Different output everywhere.** These were measured, in `out/d4_bound.json`:
   - Class order: the order class comes first (`et_pb_text_0 et_pb_text …`).
   - New classes: `et_block_section`/`et_block_row`/`et_flex_module`/`et_block_module`, `et_block_row_4col`, `preset--module--divi-<name>--<id>` (plus a `_wrapper` variant on buttons).
   - A renamed header class: `et_pb_module_header` instead of `et_pb_module_heading`.
   - No `et_pb_gutters3` on the inner content.
   - Longhand declarations: `border-*-radius` and `transition-property/duration/timing-function/delay`.
   - New defaults: `--et-pb-icon-self-align:center` on every column, and `text-align:start` on every Text module.
   - Different selector shapes:
     - Section background: `.et-l--post>.et_builder_inner_content .et_pb_section.et_pb_section_N`.
     - Button: `body #page-container .et_pb_section .et_pb_button_N`.
     - Accordion children, blurb icons and similar elements also change shape.
   - Rules that share declarations are grouped across modules.
3. **New value semantics:**
   - Design variables print as `var(--gcid-…)` and `var(--gvid-…)`.
   - Colour variables with settings print as relative colours, for example `hsl(from #0B2A3C calc(h + 0) calc(s + 0) calc(l + 0) / 0.85)`. That needs the site's global colour **values** at render time.
   - Module presets and option-group presets add classes, and their attrs are stored site-wide.
   - Flex and grid layout (`module.decoration.layout`) is a whole new option family.
4. **The page shell:**
   - Divi 5 always writes static CSS files, and its dynamic assets pick a per-page CSS/JS subset.
   - It prints `et-vb-global-data` `:root` styles (fonts, number variables).
   - Variable Google Fonts get their own `css2?family=…:ital,wght@0,100..900;1,100..900` link.
   - The spike's first pixel runs had a **16.4 % diff at 390 px** only because the prototype emitted no font link, so Montserrat fell back to Helvetica and the H1 wrapped onto three lines. Using Divi's `style-static.min.css` for the rest of the shell was enough for 0.000 % on the pages tested. One element in `heldout2` is 2 px wider, which is probably static CSS rather than dynamic CSS (not investigated).

## 2. Approaches considered

| Approach | Verdict | Evidence |
|---|---|---|
| **A. Convert D5 attrs back to D4 and reuse `divi_render`** | **Rejected** | Measured upper bound below. Even with a perfect back-conversion, the output is a Divi 4 page, not a Divi 5 one. A post-pass that rewrites classes and selectors would be a new CSS engine anyway. The conversion map (17,974 D4→D5 entries, `research/divi5/schema.md`) is one-way and lossy in reverse: variables, relative colours, presets, flex layout and D5-only options have no D4 shortcode form. |
| **B. Native D5 renderer driven by the theme's metadata** (block walk + templates copied from `render_callback` output + generic `ElementStyle` port reading `module.json`) | **Prototyped: GO** | §4 |
| C. Run Divi's own style engine from the Visual Builder JS bundles (19 MB, minified) in Node | Rejected | Needs Node, which removes the main benefit over Playground. The bundles are React/VB-coupled and not a stable API. |
| D. php-wasm running Divi 5's `server/` without WordPress | Rejected | Also needs Node. Divi's render path calls WordPress throughout (`WP_Block`, hooks, options, `wpautop`), so it would become a WordPress stub, which is what Playground already is. |
| E. Status quo: Playground only | The fallback, and `--exact` | Exact by construction, and already shipped (`research/divi5/playground.md`), but it needs Node and 1 s to 30 s per render. |

**Upper bound for A (`d4_bound.py`).** Each page's original Divi 4 shortcode was rendered with the shipped
`divi_render` on Divi 4.27.9. Its tuned D4 fixtures are exact, so this is "perfect back-conversion plus a perfect D4
renderer". It was scored against real Divi 5.13.1 rendering the converted blocks:

| Page | Elements (D5 / D4) | Tag/class ratio | Builder CSS (D5 decls / common / missing / extra) | Jaccard |
|---|---|---|---|---|
| heldout-inscope | 127 / 129 | 0.594 | 490 / 189 / 301 / 265 | 0.25 |
| handwritten-landing | 89 / 91 | 0.478 | 104 / 45 / 59 / 37 | 0.32 |
| unicode | 11 / 11 | 0.364 | 3 / 0 / 3 / 0 | 0.00 |
| brand-kit | 87 / 90 | 0.452 | 265 / 168 / 97 / 61 | 0.52 |
| divi-ai-section | 39 / 42 | 0.568 | 296 / 91 / 205 / 105 | 0.23 |

## 3. What was built (`research/divi5/python-renderer-spike/`)

| File | Role |
|---|---|
| `d5render.py` (~650 lines) | Stdlib-only renderer. Parsing reuses `Skill/.../divi5_blocks.py` unchanged. Module handlers: section, row, column, text, heading, button (plus `divi/placeholder`); anything else renders as a red placeholder and is counted. Generic groups: background (colour, hover, gradient, image), spacing, sizing (width/max-width/heights, module alignment), font (`font`, `bodyFont.body`, `bodyFont.link`, `headingFont.hN`, including the `style` list → text-decoration), border (longhand radius, width/colour/style), overflow-for-radius, transition (hovered properties), button (`:after`, alignment wrapper). `$variable()$` → `var(--id)`, or `hsl(from …)` for colour variables with settings. Page shell: Divi 5 `style-static.min.css`, the stock customizer and global-data styles, token `:root` variables, and Google Fonts (css plus css2 for variable fonts). Its coverage report lists the attribute keys it never reads, down to the keys inside each value. |
| `truth.py` | Ground truth: `preview.py render` (Playground, Divi 5.13.1, `--tokens` when given) → `out/truth/<name>-d5.html` |
| `evaluate.py` | `fidelity.compare` (markup sequence, `.et-l` bytes, builder-CSS declaration sets), identical class lists, coverage, and the median of 20 warm renders |
| `d4_bound.py` | Approach A's upper bound (§2) |
| `pages/` | `tuned.html`, `heldout.html` and `heldout2.html` (block markup built from recipe worked examples and fixtures), plus an out-of-scope copy of `converted/heldout-inscope.html` |
| `out/` (gitignored) | Truth renders, Python renders, `*-eval.json`, `d4_bound.json`, screenshots and side-by-sides (`shots/sbs-*.png`), and the renderer snapshots `d5render.before-heldout*.py` |

Pixels and geometry were measured with `research/python-renderer-spike/shoot.mjs` (headless Chrome, the builder-area
`.et-l` bounding box, 1440 and 390 px, geometry and computed style for every `et_pb_` element) and
`compare_visual.py` (Pillow; a pixel differs when a channel differs by more than 16), both unchanged.

## 4. Fidelity results (all measured)

Truth is real Divi 5.13.1 via `preview.py render`, with `--tokens recipes/divi5/sample-tokens.json` for the recipe
pages so the global colours and variables are seeded. Playground's builder markup and CSS are byte- and
declaration-identical to the live `divi-5-test.local` (`research/divi5/playground.md` §3, §6), so the local site
was not used separately. Numbers are in the TL;DR table. The order of events:

1. **Tuned page.** The prototype was written against the `tuned` truth. Its first scored run was already
   byte-identical (`.et-l` 4,396 bytes) with 343/343 declarations.
2. **`heldout`**, whose truth was not looked at before scoring, was scored **untuned**:
   - The class sequence was identical (52/52).
   - CSS 140/156 (89.7 %) with **0 extra**.
   - The only markup byte difference was `wpautop`'s `\n` between list tags.
   - The 16 missing declarations came from 3 features:
     - a background image with a gradient overlay;
     - colour variables with an `opacity` setting, which print `hsl(from <value> … / 0.85)`;
     - the Text module's link font, with its `style: ["underline"]` list becoming `text-decoration-line/-style`.
3. **One fixing pass** covered 5 special cases in one short session (well under the D4 spike's 20 minutes; agent
   time, not engineer time): background image and gradient, relative-colour variables, the font style list, the
   link font, and list newlines. After it, `heldout` was byte-identical with 156/156.
4. **`heldout2` was written after the fixing pass and never tuned.** It deliberately uses content the recipes do
   not produce:
   - section 3 of the **native Divi 5 Divi AI layout** (`tests/fixtures/divi5/divi-ai/layout.html`, builderVersion 5.0.0-public-beta.1, presets on every element);
   - two sections of the converted `brand-kit`;
   - the converted `unicode` page.

   Results: 96.7 % of declarations (467/483), 0 extra, and 49/57 identical class lists. The misses:
   - **Reported by the coverage report:**
     - `module.decoration.boxShadow` on 3 columns (3 declarations).
     - `css.mainElement` custom CSS (1 declaration).
     - `module.advanced.htmlAttributes.class`/`id` and `module.decoration.attributes` (the `pp-lead` and `ai_ignore_all` classes).
     - `module.advanced.gutter.makeEqual` (`et_pb_equal_columns`). This is the one visible layout miss: a 34 px shorter column at 1440.
   - **Silent:**
     - **The Button module prints its padding on `:hover` as well** (`… .et_pb_button_N, … .et_pb_button_N:hover{padding-*:…!important}`): 12 declarations, invisible. This is a Divi special case, and the coverage report cannot catch it, because the attribute is "read".
     - Preset classes on rows and columns: the prototype adds preset classes only to modules. That is a prototype omission.
5. **Out of scope:** the converted `heldout-inscope`, where 9 of its module types are unsupported, gives 132/490 declarations (26.9 %) with +12 extra. The coverage report lists all 9 unsupported types, with 21 ignored keys.

**Coverage report.** On the final prototype: 0 ignored keys on `tuned`/`heldout`, and 43 key paths
on `heldout2` (18 distinct), which name every reported miss above. On the D4 spike, "read" did not mean "honoured
correctly", and the same is true here: the button `:hover` padding was read and still wrong. The first version's
report was also too coarse. It marked all of `module.decoration.background` as handled, so the untuned `heldout`
report named the link font but not the background image. Key-level granularity (the current version) fixes that.

**Visual.** In the side-by-sides (`out/shots/sbs-{tuned,heldout,heldout2}-{1440,390}.png`) the tuned and held-out
pages cannot be told apart. `heldout2` differs where equal columns and box shadow are missing (0.90 % / 2.61 %).

## 5. Speed (measured)

| | Python prototype | Playground (shipped preview) |
|---|---|---|
| Builder render, in-process, warm (median of 20) | **4.4–6.1 ms** across runs (tuned: 28 modules, 343 declarations) | — |
| Full page, in-process (including reading the 0.8 MB static CSS) | 6.8 ms | — |
| Command-line one-shot (Python start + render + write 0.8 MB) | **0.04–0.05 s** | **4.7–5.5 s** (7 truth renders today); 0.85–1.2 s per `serve` re-render; ~30 s cold (`playground.md` §4) |
| Requirements | Python 3.8+, and the cached Divi 5 theme (module.json metadata, static CSS, fonts, JS) | Node 20+, ~1–1.2 GB (npm + WordPress + site caches), the cached Divi 5 theme |

The prototype's output uses `file://` URLs for theme fonts and images, like the D4 spike's first version. A real
build must reuse `divi_render/assets.py`'s `data:` embedding or `/__divi/` route, because browsers block `file://`
over HTTP.

## 6. Effort estimate (inferred from building this)

Scope (a) mirrors Divi 4 Tasks 23–28: the **~28 module types the Divi 5 recipes emit**:
- section, row, column (plus inner row and column), text, heading, button, image, blurb, cta, divider;
- number-counter, accordion (plus item), toggle, code, video, testimonial, team-member, gallery;
- fullwidth-header, slider (plus slide), tabs (plus tab), pricing-tables (plus table), contact-form (plus field), map (plus pin).

The acceptance bar is the Divi 4 one: every module has a tuned fixture that must match exactly, and each batch
records a held-out page before any fixes. Site-data modules (blog, portfolio, post-*, menu, …) and WooCommerce
render as fallback blocks, as on Divi 4.

| Work | Estimate |
|---|---|
| Engine core: metadata loader (module.json + default printed/render attrs, read from the cached theme at runtime), order classes incl. inner/fullwidth, attr inheritance (desktop → tablet → phone, hover/sticky), generic `ElementStyle` for ~20 option groups (adds box shadow, filters, transform, position, z-index, text shadow, disabledOn, layout basics, mask/pattern), style grouping not needed | 5–7 days |
| Variables (incl. relative colours), module and option-group presets from `tokens.json` (classes, merged attrs, preset CSS the preview already seeds), preset classes on structure | 2–3 days |
| ~22 more modules at 2–4 h each (templates from `render_callback`, the module's own `module_styles` special cases) | 5–7 days |
| Page shell: dynamic-assets file list for used modules or the static CSS fallback, global-data styles, the Google Fonts css/css2 builder, `divi-script-library` JS and its JSON data, asset embedding shared with `divi_render/assets.py` | 2–3 days |
| Harness and integration: D5 truth corpus (`ground_truth.py --divi 5.x`), `tests/test_render5_fidelity.py`, `preview.py` routing (Python default, `--exact`, auto-escalation), serve mode, doctor, docs | 3–4 days |
| **Total** | **17–24 days ≈ 4–5 engineer-weeks** (Divi 4's comparable estimate: 3–4) |

Near-exact parity for all ~90 modules, plus flex/grid layout, interactions, loop/dynamic content and sticky/scroll
effects, stays out of reach at reasonable cost, as on Divi 4. Months of work, and still never complete.

**Maintenance:**
- Divi 5 ships weekly.
- Selector, important-flag and default changes arrive for free, because the metadata is read from the cached theme at runtime.
- Changes to `render_callback` templates and hard-coded special cases only surface in a parity run, so a D5 corpus run against Playground truth is needed for every new cached Divi 5 version.
- Expect **about 0.5–1 day a month**, more around big 5.x feature releases. This is inferred.

## 7. Recommendation

**GO, scoped.** Build a Divi 5 Python renderer as the **default Divi 5 preview for the module set the Divi 5
recipes emit**, keep the Playground preview as `--exact`, and escalate to Playground automatically when the coverage
report lists anything the Python renderer does not honour (if Node is available; otherwise show a banner, as on
Divi 4).

**Reasons:**
1. **The measured generalization is better than Divi 4's.** Untuned held-out pages scored 89.7 % and 96.7 % of
   declarations with **zero wrong or extra declarations**. Divi 4 scored 89.9 % (10 wrong) and 96.0 % (3 wrong) with a 90 px shift.
   After one short pass the first held-out page was exact to the byte. The second, which includes native Divi AI
   output, had one visible miss, and the coverage report flagged it.
2. **The metadata is the lever.** Divi 5 keeps selectors, important flags and printed defaults as JSON in the theme.
   The prototype reads them unchanged, so the engine inherits much of each release without code changes. Divi 4's
   equivalent needed a research dump (`dump-divi-schema.php`).
3. **Consistency with the Divi 4 decision.** The user chose a Python default for Divi 4 because it needs no Node and
   renders in tens of milliseconds, 200× faster than Playground. Today Divi 5 users need Node 20+ and about 1 GB of caches just to see a preview.
4. **The route back to exact is cheap and already built.** Playground is shipped and exact, the harness is
   D5-aware (`fidelity.py`, `ground_truth.py`), and auto-escalation keeps unsupported features from being silently shown wrong.

**Conditions and risks to accept:**
- **Weekly releases.** Budget the per-version parity run (Task 21-R5e below). If the D5 corpus stops passing on a new Divi version, the preview falls back to Playground for that version until fixed. This rule must be in `preview.py`.
- **Silent special cases exist,** such as the button's `:hover` padding copy. They are fewer than on Divi 4 but not zero, and only a parity run finds them.
- **Presets.**
  - Real Divi 5 sites put presets on most elements (the Divi AI layout does).
  - Preset rendering is only as good as `tokens.json`'s recovered preset data.
  - Playground has the same limitation today, because its seeding covers global colours, variables and preset CSS.
- **Flex/grid layout, interactions, sticky/scroll and loop content were not measured.** The recipes emit
  `display: block` structure, so skill-authored pages avoid flex. Pages fetched from sites for `page_edit` may not,
  and those escalate to `--exact`.
- **A gate:** if the first engine batch (Task 21-R5b) misses the held-out bar (95 % of declarations or more, no
  layout shift, every other miss named by coverage), stop and keep Playground as the only Divi 5 preview.
- **The prototype's gaps,** none of which change the verdict:
  - It covers 6 modules only.
  - The shell uses static CSS, not Divi 5's dynamic assets.
  - There is no JS, and theme assets are `file://` URLs.
  - Pixel diffs cover the builder area only.
  - The held-out pages were chosen by the person who wrote the renderer. `heldout2` mitigates this with native Divi AI and converted content the renderer had never seen.

## 8. Draft spec addendum and tasks (for the controller; the spec and plan files are not edited here)

### Draft for `docs/superpowers/specs/2026-09-28-divi5-support-design.md`

> ## Addendum A: Python renderer for Divi 5 previews (decided 2026-09-29)
>
> **Evidence:** `research/divi5/python-renderer-spike.md`, measured against real Divi 5.13.1 (Playground truth).
> - **Reusing the Divi 4 renderer through a D5→D4 conversion was rejected.** A perfect back-conversion still matches only 23–52 % of Divi 5's builder CSS declarations.
> - **A native renderer driven by the theme's `module.json` metadata** gave, for 6 modules:
>   - byte-identical markup and 343/343 declarations on the tuned page, with a 0.000 % pixel diff at 1440 px;
>   - untuned held-out pages at 89.7 % and 96.7 % of declarations with 0 wrong;
>   - 5–7 ms per render, against 1–5 s in Playground.
>
> **Decision:**
> - `preview.py render|serve` renders Divi 5 block pages with a stdlib Python renderer (`scripts/divi5_render/`) by default.
> - `--exact` keeps the Playground preview.
> - When the coverage report lists an unsupported module or option on a page, `preview.py` renders that page in Playground automatically if Node 20+ is available. Otherwise it shows the Divi 4-style banner naming what is missing.
> - When the page's Divi version has not passed the Divi 5 parity corpus, the Playground path is used for that version.
>
> **Scope:** the ~28 module types the Divi 5 recipes emit. Site-data and WooCommerce modules render fallback blocks.
> Flex/grid layout, interactions, sticky/scroll and loop content are unsupported and escalate.
>
> **Acceptance:**
> - Every module has a tuned D5 fixture whose builder markup (tag and class sequence) and builder-CSS declaration set match Playground truth exactly.
> - Each batch records a held-out page's pre-fix numbers in `research/divi5/render-fidelity.md`.
> - Batch 1 must reach 95 % or more of declarations with no layout shift, with every other miss named by coverage. Otherwise the work stops and Playground stays the only Divi 5 preview.
>
> **Unchanged:** Divi assets are never committed. The WordPress draft is still the authoritative visual check. The
> `.seed.css`/options seeding stays for the Playground path. The Python path reads the same `tokens.json` (global
> colours, variables, presets).

§4.8's sentence "The default (non-`--exact`) path on Divi 5 is Playground until the Python-renderer spike says
otherwise" would point to this addendum.

### Draft tasks for `docs/superpowers/plans/2026-09-28-divi5-support.md`

These go before Task 22 (final verification), named 21-R5a … 21-R5f so the existing numbers stay as they are.

- **Task 21-R5a: Divi 5 render fidelity harness.**
  - A Divi 5 truth corpus via `ground_truth.py` with `--divi 5.x` (and `--tokens` for recipe pages).
  - A tuned/held-out split per batch.
  - `tests/test_render5_fidelity.py`: exact on tuned, numbers recorded on held-out, skipped without Node or a cached Divi 5.
  - A `research/divi5/render-fidelity.md` template.
  - Reuses `fidelity.py`, which is already D5-aware.
- **Task 21-R5b: `scripts/divi5_render/` engine and structural modules.**
  - Port the spike to a package:
    - `meta` (module.json and default JSON from the cached theme);
    - `values` (variables, relative colours);
    - `css` (sheet, media queries, hover/sticky);
    - `options` (generic ElementStyle groups);
    - `structure` (section, row, column, and their inner versions);
    - `modules/basic` (text, heading, button, image);
    - `page` (shell, fonts, assets shared with `divi_render/assets.py`);
    - `coverage` (key-level).
  - Presets and group presets from `tokens.json`, with preset classes on every element.
  - The button `:hover` padding copy.
  - **Gate:** the batch's held-out page must reach 95 % or more of declarations, with no layout shift and every other miss named by coverage.
- **Task 21-R5c: content and conversion modules.** blurb, cta, divider, number-counter, accordion (plus item), toggle, code, video, testimonial, team-member, gallery (fallback when it needs media data), fullwidth-header. One tuned fixture per module and a held-out page.
- **Task 21-R5d: interactive and form modules.** slider (plus slide), tabs (plus tab), pricing-tables (plus table), contact-form (plus field), map (plus pin), signup, and the JSON that `divi-script-library` needs. Site-data and WooCommerce modules become fallback blocks.
- **Task 21-R5e: `preview.py` integration.**
  - Divi 5 pages render in Python by default in `render` and `serve`, with the Divi 4 serve behaviour (re-render per request, mtime reload, `/__divi/`).
  - `--exact` means Playground.
  - Auto-escalation to Playground on coverage misses, or a banner when Node is missing.
  - The per-Divi-version parity check: a recorded pass file per cached 5.x version, and Playground when it is absent.
  - `doctor` reports which Divi 5 path will be used.
  - Tests.
- **Task 21-R5f: documentation.** The `preview.md` §8 rewrite (Python default, `--exact`, escalation, fidelity numbers), SKILL.md/README one-liners, and a regeneration/parity checklist for new Divi 5 versions.

## 9. Verified or inferred

**Verified by running:**
- Every fidelity, pixel, geometry and timing number in the TL;DR, §2, §4 and §5.
- The D5→D4 upper bound.
- The font-link lesson (16.4 % diff to 0.061 % at 390 px).
- Coverage behaviour, including the coarse-report miss and the silent button `:hover` padding.
- Playground one-shot render times today.

**Inferred, not measured:**
- The line-count comparison with Divi 4, which uses the D4 spike's counts.
- The effort and maintenance estimates.
- That the remaining modules follow the same metadata-driven pattern.
- The cause of the 1-px strip at 390 px.
- The 2 px button width difference in `heldout2`.
- The shell's behaviour on pages that need dynamic-asset CSS the static stylesheet does not have.

**Caveats:**
- One Divi version (5.13.1), stock site settings, the sample tokens.
- Builder-area pixels only.
- No local-site pages were created. Playground truth is identical to live per `playground.md`, so none were needed and none were left behind.

## Reproduce

```
cd research/divi5/python-renderer-spike
T=../../../Skill/divi-page-builder/recipes/divi5/sample-tokens.json
python3 truth.py tuned=pages/tuned.html heldout=pages/heldout.html --tokens $T   # real Divi 5 via Playground
python3 truth.py heldout2=pages/heldout2.html
python3 evaluate.py tuned --tokens $T; python3 evaluate.py heldout --tokens $T; python3 evaluate.py heldout2
python3 d4_bound.py            # approach A upper bound (needs truths for the 5 converted fixtures: truth.py NAME=../../../tests/fixtures/divi5/converted/NAME.html)
node ../../python-renderer-spike/shoot.mjs out/shots tuned-py "file://$PWD/out/tuned-py.html"   # and -truth; then compare_visual.py
python3 d5render.py pages/tuned.html -o out/tuned-cli.html --tokens $T --coverage out/tuned-cov.json
```
