# Maintainer tools (not shipped with the skill)

All commands run from the repo root against the LocalWP site `divi-test.local`.

| Purpose | Command |
|---|---|
| WP-CLI on the local site | `research/tools/wp-local.sh <args>` |
| 1. Dump Divi's field registry | `research/tools/wp-local.sh --require="$PWD/research/tools/force-all-modules.php" eval-file research/tools/dump-divi-schema.php "$PWD/research/divi-schema"` |
| 2. Compile the validator schema | `python3 research/tools/build_schema.py research/divi-schema research/tools/extras.json Skill/divi-page-builder/scripts/schema` |
| 3. Generate the module docs | `python3 research/tools/generate_docs.py research/divi-schema Skill/divi-page-builder --notes research/tools/notes` |
| 4. Check every doc/recipe example | `python3 research/tools/check_doc_examples.py Skill/divi-page-builder` |
| Tests | `python3 -m unittest discover -s tests -v` |

After a Divi update: install the new Divi on the local site, then run steps 1–4, then the tests.
