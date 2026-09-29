# Maintainer tools (not shipped with the skill)

All commands run from the repo root against the LocalWP site `divi-test.local`.

| Purpose | Command |
|---|---|
| WP-CLI on the local site | `research/tools/wp-local.sh <args>` |
| 1. Dump Divi's field registry | `research/tools/wp-local.sh --require="$PWD/research/tools/force-all-modules.php" eval-file research/tools/dump-divi-schema.php "$PWD/research/divi-schema"` |
| 2. Compile the validator schema | `python3 research/tools/build_schema.py research/divi-schema research/tools/extras.json Skill/divi-page-builder/scripts/schema` |
| 3. Generate the module docs | `python3 research/tools/generate_docs.py research/divi-schema Skill/divi-page-builder --notes research/tools/notes` |
| 4. Check every doc/recipe example | `python3 research/tools/check_doc_examples.py Skill/divi-page-builder` |
| Tests (offline) | `python3 -m unittest discover -s tests -v` |
| Tests incl. live | `PP_LIVE_TESTS=1 python3 -m unittest discover -s tests -v` |

After a Divi update: install the new Divi on the local site, then run steps 1–4, then the tests.

## Divi 5

The Divi 5 schema and docs come from the LocalWP site `divi-5-test.local` (site id `fTZ3hcgdI`).

| Purpose | Command |
|---|---|
| 1. Dump Divi 5's schema | `LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH="$HOME/Local Sites/divi-5-test/app/public" research/tools/wp-local.sh eval-file research/tools/divi5/dump-schema.php "$PWD/research/divi5-schema"` |
| 2. Compile the Divi 5 validator schema | `python3 research/tools/divi5/build_schema5.py research/divi5-schema research/tools/divi5/families5.json Skill/divi-page-builder/scripts/schema5` |
| 3. Generate the Divi 5 module docs | `python3 research/tools/divi5/generate_docs5.py research/divi5-schema Skill/divi-page-builder --notes research/tools/divi5/notes` |
| 4. Check every doc/recipe example (Divi 4 and 5) | `python3 research/tools/check_doc_examples.py Skill/divi-page-builder` |

Step 3 writes `reference/divi5/modules/*.md` and the tables between the `BEGIN GENERATED`/`END GENERATED`
markers of `reference/divi5/design-families.md` (the prose around them is hand-written). It exits 1 if a
module's minimal example has any validation finding, or if an attribute path is neither listed on its module
page nor covered by a linked family table. Hand-written gotchas go in `research/tools/divi5/notes/<name>.md`.
After a Divi 5 update: run steps 1–4, then the tests.

## Live tests (`PP_LIVE_TESTS`)

Tests that touch the local WordPress site (`wp-local.sh`, `http://divi-test.local`, creating
Application Passwords) or read the Elegant Themes credentials from its database are **opt-in**:
they are skipped unless `PP_LIVE_TESTS=1` is set, with the skip reason "live test: … set
PP_LIVE_TESTS=1 to run it". Today that covers `test_publish.PublishLiveTest`,
`test_tokens_fidelity`, `test_divi_judge`, and `test_preview`'s live-CSS comparison and credential-leak
check (without the flag `test_preview` renders from the Divi cache only and never reads ET credentials).
Gate any new live test with `@live_only` from `tests/_paths.py`; `tests/test_live_gating.py` checks
the known ones.
