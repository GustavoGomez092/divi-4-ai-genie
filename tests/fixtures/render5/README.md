# Divi 5 render fidelity fixtures (tests/test_render5_fidelity.py)

Divi 5 block pages for the Python renderer's parity corpus (`research/divi5/python-renderer/divi5_render`, parked, Task 21-R5). Their truth is
real Divi 5 rendered through Playground by `research/tools/ground_truth.py` and cached outside the repo. The
manifest lists each page's batch, whether it is tuned, the modules it uses and, for recipe pages, the tokens file
the truth is rendered with (`--tokens`).

| File | Provenance |
|---|---|
| `b1-tuned-recipes.html` | `research/divi5/python-renderer-spike/pages/tuned.html` (hero-centered + process-steps recipe examples) |
| `b1-tuned-recipes2.html` | the spike's `pages/heldout.html` (hero-background-image + service-area-list) |
| `b1-tuned-mixed.html` | the spike's `pages/heldout2.html` (Divi AI native section, converted brand-kit, unicode) |
| `b1-tuned-image-inner.html` | written for Task 21-R5b: two hand-made sections (Image variants; a specialty section with an inner row), then `tests/fixtures/divi5/converted/brand-kit.html` section 1 and `handwritten-landing.html` sections 1 and 3 |
| `b1-heldout.html` | written for Task 21-R5b before the engine existed: `tests/fixtures/divi5/divi-ai/layout.html` sections 1 and 3, then the worked examples of the Divi 5 recipes hero-split, alternating-features and trust-bar |

No Divi code, CSS or rendered output is kept here (tests/test_no_divi_assets.py).
