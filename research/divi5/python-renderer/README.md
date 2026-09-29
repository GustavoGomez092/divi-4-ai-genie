# Divi 5 Python renderer (parked)

**Status: parked at its batch-1 gate (NO-GO, 2026-09-29).** Playground is the only Divi 5 preview in the shipped
skill. This package (`divi5_render/`) was moved out of `Skill/divi-page-builder/scripts/` and nothing in the skill
imports it.

**Numbers:** the batch-1 held-out page (`tests/fixtures/render5/b1-heldout.html`), pre-fix, matched 94.3 %
(982/1041) of the builder CSS declarations against the 95 % bar, with 2 extra declarations that coverage did not
name and a layout shift from the fourth section (disabledOn not ported). Details: `research/divi5/render-fidelity.md`.

**Tests keep it alive:** `tests/test_render5_engine.py` and `tests/test_render5_fidelity.py` put this directory on
`sys.path` themselves (`RENDERER5` in `tests/_paths.py`); it is not on the path for the skill's scripts. The gate
test is an expected failure.

**Licensing:** the renderer reads Divi's own files (module.json, defaults, CSS) from the local Divi cache at
runtime (`scripts/preview.py fetch-divi`). Nothing licensed is committed.

**How to resume**
1. Choose a NEW held-out page and measure it before looking at any diffs (the old one is now tuned-on).
2. Port: `disabledOn`, image filters, blockquote font, section dividers, background-image default size/position.
3. Re-run the gate (95 % of declarations, no layout shift, every other miss named by coverage).
4. If it passes, continue with Tasks 21-R5c..f from `docs/superpowers/plans/2026-09-28-divi5-support.md`
   (currently marked cancelled; reinstate them).
