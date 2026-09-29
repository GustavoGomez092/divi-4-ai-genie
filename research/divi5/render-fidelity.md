# Render fidelity: the Divi 5 Python renderer against real Divi 5

The Divi 5 Python renderer (`Skill/divi-page-builder/scripts/divi5_render/`, spec Addendum A, tasks 21-R5a…f) is
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

(Rows are added by `RENDER5_FIDELITY_RECORD=1`; the batch-1 held-out pre-fix row comes first.)
