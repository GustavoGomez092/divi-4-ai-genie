# Render fidelity: the Divi 5 Python renderer against real Divi 5

**Outcome (2026-09-29): NO-GO.** Batch-1 held-out gate missed (94.3 % = 982/1041 declarations vs 95 %, 2 unnamed extras, layout shift from unported disabledOn). Renderer parked in `research/divi5/python-renderer/`; Playground stays the only Divi 5 preview.

The Divi 5 Python renderer (`research/divi5/python-renderer/divi5_render/`, parked, spec Addendum A, tasks 21-R5a…f) is
checked by `tests/test_render5_fidelity.py` against real Divi 5, rendered through Playground by
`research/tools/ground_truth.py` (the manifest's Divi 5 version, `--tokens` for recipe pages; cached outside the
repo because it holds Divi's licensed CSS), for every fixture in `tests/fixtures/render5/manifest.json`.
`research/tools/fidelity.py` (Divi 5-aware since Task 14) measures:

- **Markup ratio:** the difflib ratio over the `(tag, class list)` sequence of the `.et-l` block (1.0 = identical).
- **Identical class lists:** elements whose tag and class list match the truth at the same position.
- **Builder CSS (common/truth):** the truth's builder declarations, as `(media, selector, declaration)` triples of
  rules naming an order class, that the Python render also prints. **Declarations** is that as a percentage: the
  Addendum A bar (95 %) is on this number.
- **Extra:** declarations the Python render prints that the truth does not (a wrong or invented rule).
- **Coverage-ignored:** attribute values the coverage report lists as not honoured.

Recording is opt-in:
`RENDER5_FIDELITY_RECORD=1 RENDER5_FIDELITY_STAGE='R5c held-out pre-fix' python3 -m unittest tests.test_render5_fidelity`
(run from `tests/`, or with `discover -s tests -p 'test_render5_fidelity.py'`). The stage label is required. Rows
are keyed by fixture and stage: a new stage adds a row, the same stage updates its row. Without the flag the test
only checks.

**Procedure per batch (as on Divi 4):** tuned fixtures (`tuned: true`) must match exactly (sequence equal, 0
missing, 0 extra, nothing coverage-ignored). The batch's held-out page (`tuned: false`) is chosen and its truth
rendered before the batch's tuning starts, and it is measured **once, before any fix** (the pre-fix row, the honest
number for how the renderer generalizes). Fixes found on it then make it a tuned page (a post-fix row).

**Layout shift** is checked with the Divi 4 spike's tools (headless Chrome over CDP, Node 22+; Pillow):
`node research/python-renderer-spike/shoot.mjs OUTDIR NAME file://PAGE.html` for the truth and the Python render,
then `python3 research/python-renderer-spike/compare_visual.py OUTDIR TRUTH-NAME PY-NAME` (geometry of every
`.et-l [class*=et_pb_]` element and a pixel diff of the builder area at 1440 and 390 px). Outputs go outside the
repo (they contain Divi's CSS and rendering).

## Batch 1 (Task 21-R5b: engine, structure, text, heading, button, image)

Divi 5.13.1. Fixtures in `tests/fixtures/render5/` (provenance in its README):

| Fixture | Role | Content |
|---|---|---|
| `b1-tuned-recipes.html` | tuned (tokens) | the spike's tuned page: hero-centered + process-steps recipe examples |
| `b1-tuned-recipes2.html` | tuned (tokens) | the spike's first held-out page: hero-background-image + service-area-list |
| `b1-tuned-mixed.html` | tuned | the spike's second held-out page: Divi AI native section, converted brand-kit, unicode |
| `b1-tuned-image-inner.html` | tuned | new: Image variants (link, lightbox, force fullwidth, radius + box shadow, responsive align, presets), a specialty section with inner row/columns, converted brand-kit + handwritten-landing image/specialty sections |
| `b1-heldout.html` | **held out** (tokens) | new, never rendered by the engine before its pre-fix row: native Divi AI layout sections 1 and 3 (image, button, heading, text, presets on every element) + the hero-split, alternating-features and trust-bar recipe examples |

**Gate (spec Addendum A, binding):** the batch-1 held-out page must reach 95 % or more of the builder CSS
declarations, show no layout shift, and every other miss must be named by the coverage report.

## Measurements

| Fixture | Stage | Modules | Tuned | Markup ratio | Identical class lists | Builder CSS (common/truth) | Declarations | Extra | Coverage-ignored | Date |
|---|---|---|---|---|---|---|---|---|---|---|
| b1-heldout.html | R5b held-out pre-fix | button, column, heading, image, row, section, text | no | 0.9902 | 19/154 | 982/1041 | 94.3 % | 2 | 12 | 2026-09-29 |

### Batch 1 gate: GATE_FAILED (measured 2026-09-29)

The four tuned fixtures match exactly (sequence equal, `.et-l` byte-identical, 0 missing, 0 extra, nothing
coverage-ignored). The held-out page's truth was rendered before the engine was written, and its diffs were first
looked at after the pre-fix row above was recorded. No fix was made after it (the gate is on the pre-fix numbers).

| Gate criterion | Result | Verdict |
|---|---|---|
| ≥ 95 % of the builder CSS declarations | **982/1041 = 94.3 %** (59 missing, 2 extra) | missed by 7 declarations |
| No layout shift | **shift:** section 4 ("Alternating Features") is 177 px taller at 1440 px and 280 px taller at 390 px, and everything below it moves; sections 1–3 are geometry-identical (every order-classed element) at both widths | missed |
| Every other miss named by coverage | the 59 missing are all named; the **2 extra are not** | missed |

What the misses are (after recording):

| Miss | Declarations | Named by coverage | Visible |
|---|---|---|---|
| Image `module.decoration.filters` (saturate 0 %, 100 % on hover, and its filter transition) on the 5 trust-bar logos | 30 missing | yes (`image:module.decoration.filters.saturate`) | colour instead of grey logos |
| Text `content.decoration.bodyFont.quote` (blockquote font and border colour) on 5 Divi AI texts | 20 missing | yes (`text:content.decoration.bodyFont.quote.*`) | no (the texts have no blockquote) |
| Section bottom divider (`module.advanced.dividers.bottom`), its rules and its `et_pb_bottom_inside_divider` element plus the section's `section_has_divider et_pb_bottom_divider` classes | 6 missing, 1 element, 1 class list | yes (`section:module.advanced.dividers.bottom.*`) | the divider shape is missing (no geometry change) |
| Row `module.decoration.disabledOn` (the recipe's mobile/desktop row variants) | 3 missing | yes (`row:module.decoration.disabledOn`) | **the layout shift:** both row variants show |
| A section background image without `size`/`position` gets `background-size:cover` and `background-position:center` (the spike's defaults); Divi prints neither | 2 extra | **no** (a silent engine bug: `image.url` is honoured) | none at these sizes (static CSS has the same defaults) |

Every unported feature above is an existing option family (filters, dividers, disabledOn, the quote font); none is a
flaw in the metadata-driven approach, and the byte-identical tuned pages (including the spike's two held-out
pages and a new image/specialty page) stand. But the binding bar is the pre-fix held-out number, so batch 1 stops
here: `tests/test_render5_fidelity.py::test_batch1_heldout_meets_the_addendum_a_bar` is an expected failure, and
per Addendum A Playground stays the only Divi 5 preview unless the controller decides otherwise.

Coverage on the held-out page: 890 attribute values, 33 not honoured (12 distinct keys), 0 unsupported modules.
Speed (median of 20 warm renders, Divi 5.13.1): builder 1.0–2.3 ms on the tuned pages and 5.3 ms on the held-out
page (75 modules, 1041 declarations); a CLI one-shot including Python start and data: URI embedding, 0.07 s.
