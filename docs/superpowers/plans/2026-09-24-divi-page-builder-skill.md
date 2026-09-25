# Divi Page Builder Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a skill (`Skill/divi-page-builder/`) that teaches any AI to write Divi 4 pages as native shortcode, check them with an offline validator, extract a site's design tokens, preview pages locally, and prepare them for publishing over REST.

**Architecture:**
- **Shared foundations.** Two stdlib-only Python modules underpin everything:
  - `divi_shortcode.py` parses and serializes Divi shortcode, round-tripping it exactly;
  - `divi_schema.py` resolves attribute names against a compact schema compiled from Divi's own field registry.
- **What's built on them:**
  - the validator;
  - the token extractor;
  - the edit helper;
  - the doc generator, which writes 64 module reference pages plus design-family tables from the same registry dump, with a coverage check that every field is documented.
- **Hand-written content:** reference docs, recipes and `SKILL.md`, each verified against the local Divi site.
- **Local preview:** a port of the proven headless-render prototype.

**Tech Stack:**
- Python 3.9+ standard library only for shipped scripts, with `unittest` for tests.
- PHP via WP-CLI on the LocalWP site `divi-test.local` (Divi 4.27.9) for the schema dump, the Divi-as-judge harness and preview rendering.
- `curl` for the REST experiments.

**Spec:** `docs/superpowers/specs/2026-09-24-divi-page-builder-skill-design.md`. Read it first; this plan argues from it.

**Execution order (amended 2026-09-24):** Tasks 1–14, then **Task 22**, then Tasks 15–21. Task 14 was rewritten for the WordPress Playground preview, and Task 22 (`publish.py`) was added, after the user widened the scope to end-to-end (spec Addendum B).

## Global Constraints

- **Dependencies:** shipped scripts (`Skill/divi-page-builder/scripts/*.py`) use the Python 3.9+ standard library only. No pip installs.
- **Portability:** scripts must run from any working directory. They locate siblings with `Path(__file__).resolve().parent`.
- **Divi version:** Divi 4 only. The schema is generated from Divi **4.27.9** at `~/Local Sites/divi-test/app/public/wp-content/themes/Divi`.
- **Read-only theme:** never modify files under the Divi theme directory or WordPress core.
- **Local site:** `divi-test.local` is a throwaway test site. Test pages must be titled `Plan Test: …` and deleted at the end of the task that creates them. Never touch page 11 ("Probe: Divi AI Emergency Plumber"); it's the reference render.
- **Secrets:** never print Application Passwords or the Elegant Themes API key, and never write them to files. Pass them through environment variables.
- **Escaping inside attribute values** (Divi `functions.php:2056-2089`):
  - `"` → `%22`, `[` → `%91`, `]` → `%93`;
  - `\` → `%92` only for `custom_css_*` and for `checkbox_options`, `radio_options`, `select_options`, `conditional_logic_rules`.
- **Hover/sticky enable rule:** hover is enabled when `X__hover_enabled` starts with `on`; sticky likewise with `X__sticky_enabled`. `background_color` and `background_image` use the group key `background` (`HoverOptions.php:68-78`, `StickyOptions.php:104-112`).
- **Preview:** real Divi in WordPress Playground (Task 14, spec Addendum B) with stock Divi settings. There is no client settings bundle (spec Addendum A). The preview scripts are Node `.mjs` (Node ≥ 20), so the Python-stdlib rule applies to `.py` scripts only.
- **Divi licensing:** Divi zips, unpacked themes and Playground caches live in the user cache (`PP_CACHE_DIR`) and never enter the repo. Elegant Themes credentials come only from `ET_USERNAME`/`ET_API_KEY` and are never printed. Never call the Elegant Themes API when the version is cached (rate limit).
- **Publishing safety:** `publish.py` validates before saving, saves drafts only, and publishes only with an explicit `--yes` given after the user approves.
- **Commits:** one commit per task minimum. Message style: `<area>: <what>` (e.g. `validator: structure checks`).
- **Running tests:** `python3 -m unittest discover -s tests -v`, from the repo root.

## Review Focus

These five cases are the most likely to bite real users; each has a pinned test in its owning task.

1. **Editing a legacy client page** (old `_builder_version`, stale attributes Divi ignores, no `column_structure` on multi-column rows). The expected behavior is that `--baseline` marks pre-existing problems as non-blocking and a row without `column_structure` validates from its column types. Tests are in Task 6 (`test_baseline_marks_preexisting`) and Task 4 (`test_row_without_column_structure_uses_column_types`).
2. **Non-English copy and typographic characters** (Spanish accents, smart quotes, `&`, emoji) inside attribute values and content. Expected: exact round-trip, and escaping touches only `"`, `[`, `]`. Tests are in Task 2 (`test_unicode_roundtrip_and_escape`) and Task 7 (Divi-judge fixture `unicode.txt`).
3. **Third-party shortcodes inside Divi text** (e.g. `[contact-form-7 id="5"]` inside `[et_pb_text]`). Expected: treated as content and never flagged. Tests are in Task 2 (`test_third_party_shortcode_is_text`) and Task 5 (`test_third_party_shortcode_not_flagged`).
4. **CRLF line endings and whitespace between tags**, for example content pasted from Windows or Google Docs. Expected: byte-exact round-trip and correct line/column numbers in findings. Test is in Task 2 (`test_crlf_roundtrip_and_line_col`).
5. **Large pages** (about 200 KB and 1,000+ modules). Expected: validation finishes in under 3 s. Test is in Task 6 (`test_large_page_performance`).

---

## File Structure

```
Skill/divi-page-builder/
  SKILL.md                                  Task 20
  reference/page-format.md                  Task 9
  reference/structure.md                    Task 9
  reference/value-formats.md                Task 9
  reference/design-families.md              Task 8 (generated tables) + Task 9 (prose)
  reference/modules/*.md, README.md         Task 8 (generated)
  reference/publishing.md                   Task 10
  reference/design-tokens.md                Task 12
  reference/preview.md                      Task 14
  recipes/README.md, sample-tokens.json     Task 15
  recipes/sections/*.md                     Tasks 16-18
  recipes/pages/*.md, recipes/edits/*.md    Task 19
  scripts/divi_shortcode.py                 Task 2   parse/serialize/escape/find/replace
  scripts/divi_schema.py                    Task 3   compact schema loader + attribute resolver
  scripts/schema/*.json                     Task 3   (generated)
  scripts/divi_checks_structure.py          Task 4
  scripts/divi_checks_values.py             Task 5
  scripts/divi_checks_tokens.py             Task 6
  scripts/validate.py                       Tasks 4-6  CLI + Finding model + orchestration
  scripts/tokens_from_shortcode.py          Task 11
  scripts/tokens_from_html.py               Task 12
  scripts/extract_tokens.py                 Task 12  CLI (REST + public URL)
  scripts/page_edit.py                      Task 19  CLI for surgical edits
  scripts/preview/preview.mjs, fetch-divi.mjs, mu-plugin/, blueprint.json   Task 14 (Playground)
  scripts/publish.py                        Task 22  fetch/media/draft/publish over REST
research/tools/
  wp-local.sh                               Task 1   WP-CLI wrapper for LocalWP
  force-all-modules.php, dump-divi-schema.php   (exist)
  build_schema.py, extras.json              Task 3
  divi_parse.php                            Task 7   Divi-as-judge
  generate_docs.py                          Task 8
  check_doc_examples.py                     Task 9
  push_local.sh                             Task 15  push a page to divi-test via REST
  notes/*.md                                Tasks 8-19 (hand-written gotchas)
tests/
  _paths.py                                 Task 1
  fixtures/valid/*.txt, fixtures/invalid/*.txt, fixtures/html/*.html
  test_*.py                                 each task
```

---

### Task 1: Test harness, LocalWP wrapper, fixtures, schema-dump check

**Files:**
- Create: `research/tools/wp-local.sh`
- Create: `tests/_paths.py`, `tests/test_schema_dump.py`
- Create: `tests/fixtures/valid/divi-ai-layout.txt`, `tests/fixtures/valid/divi-ai-section.txt`, `tests/fixtures/valid/divi-ai-layout-skeleton.txt`
- Create: `research/tools/README.md`

**Interfaces:**
- Produces:
  - `tests/_paths.py` exporting `ROOT`, `SKILL`, `SCRIPTS`, `TOOLS`, `FIXTURES`, `RAW_SCHEMA` (all `pathlib.Path`), and putting `SCRIPTS` and `TOOLS` on `sys.path`;
  - `research/tools/wp-local.sh <wp-cli args…>`.

- [ ] **Step 1: Create the WP-CLI wrapper**

`research/tools/wp-local.sh`:
```bash
#!/bin/bash
# Run WP-CLI against a LocalWP site without Local's site shell.
#   research/tools/wp-local.sh option get siteurl
# Override LOCAL_SITE_ID / LOCAL_SITE_PATH / LOCAL_PHP for other LocalWP sites.
set -euo pipefail
SITE_ID="${LOCAL_SITE_ID:-VHfw9zcDi}"
SITE_PATH="${LOCAL_SITE_PATH:-$HOME/Local Sites/divi-test/app/public}"
LS="$HOME/Library/Application Support/Local"
PHP_BIN="${LOCAL_PHP:-$(ls -d "$LS"/lightning-services/php-8.2.29*/bin/darwin-arm64/bin/php | head -1)}"
SOCK="$LS/run/$SITE_ID/mysql/mysqld.sock"
WPCLI="/Applications/Local.app/Contents/Resources/extraResources/bin/wp-cli/wp-cli.phar"
exec "$PHP_BIN" -d mysqli.default_socket="$SOCK" -d pdo_mysql.default_socket="$SOCK" \
  -d memory_limit=512M "$WPCLI" --path="$SITE_PATH" "$@"
```
Run: `chmod +x research/tools/wp-local.sh && research/tools/wp-local.sh option get siteurl`
Expected: `http://divi-test.local`

- [ ] **Step 2: Create the test path helper**

`tests/_paths.py`:
```python
"""Shared paths for tests; importing this puts the skill scripts and tools on sys.path."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "Skill" / "divi-page-builder"
SCRIPTS = SKILL / "scripts"
TOOLS = ROOT / "research" / "tools"
FIXTURES = ROOT / "tests" / "fixtures"
RAW_SCHEMA = ROOT / "research" / "divi-schema"
WP_LOCAL = TOOLS / "wp-local.sh"

for p in (SCRIPTS, TOOLS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
```

- [ ] **Step 3: Extract the captured Divi AI pages into fixtures**

Run:
```bash
mkdir -p tests/fixtures/valid tests/fixtures/invalid tests/fixtures/html
python3 - <<'EOF'
import json
from pathlib import Path
src = Path("research/divi-ai-api")
out = Path("tests/fixtures/valid")
pairs = {"20-layout-3-images.json": "divi-ai-layout.txt",
         "10-section-3-images.json": "divi-ai-section.txt",
         "20-layout-1-shortcode.json": "divi-ai-layout-skeleton.txt"}
for s, d in pairs.items():
    (out / d).write_text(json.loads((src / s).read_text())["response"]["content"])
    print(d, (out / d).stat().st_size)
EOF
```
Expected: three files, roughly 100 KB, 16 KB and 100 KB.

- [ ] **Step 4: Write the failing schema-dump test**

`tests/test_schema_dump.py`:
```python
import json
import unittest

from _paths import RAW_SCHEMA


class SchemaDumpTest(unittest.TestCase):
    def fields(self, slug):
        return json.loads((RAW_SCHEMA / "modules" / f"{slug}.json").read_text())["fields"]

    def test_index_has_64_modules(self):
        index = json.loads((RAW_SCHEMA / "index.json").read_text())
        self.assertEqual(len(index["modules"]), 64)
        self.assertEqual(index["divi_version"], "4.27.9")

    def test_option_templates_expanded(self):
        f = self.fields("et_pb_blurb")
        for name in ("border_radii", "border_width_all", "box_shadow_style", "header_text_shadow_style"):
            self.assertIn(name, f, name)

    def test_composite_controls_flattened(self):
        f = self.fields("et_pb_blurb")
        self.assertEqual(f["transform_scale"]["composite_of"], "transform_styles")
        self.assertEqual(f["scroll_fade_enable"]["composite_of"], "scroll_effects")

    def test_no_placeholder_field_names(self):
        for path in (RAW_SCHEMA / "modules").glob("*.json"):
            names = json.loads(path.read_text())["fields"]
            self.assertFalse([n for n in names if n.startswith("%t")], path.name)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Run the test**

Run: `python3 -m unittest tests/test_schema_dump.py -v`
Expected: PASS. The v2 dump (commit `65c84e0`) already expands templates and composites. If it fails, re-run the dump:
```bash
research/tools/wp-local.sh --require="$PWD/research/tools/force-all-modules.php" \
  eval-file research/tools/dump-divi-schema.php "$PWD/research/divi-schema"
```

- [ ] **Step 6: Document the maintainer commands**

`research/tools/README.md`:
````markdown
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
````

- [ ] **Step 7: Commit**

```bash
git add research/tools/wp-local.sh research/tools/README.md tests/
git commit -m "tests: harness, LocalWP wrapper, Divi AI fixtures, schema dump checks"
```

---

### Task 2: `divi_shortcode.py`: parse, serialize, escape, find, replace

**Files:**
- Create: `Skill/divi-page-builder/scripts/divi_shortcode.py`
- Test: `tests/test_divi_shortcode.py`

**Interfaces:**
- Produces:
  - `Problem(code: str, message: str, offset: int)`
  - `Text(value: str, start: int, end: int)`
  - `Node(tag, attrs: dict[str,str] /*raw, still escaped*/, start, open_end, close_start, end, raw_open, raw_close, self_closing, children: list[Node|Text], orig_attrs, quoting: dict[str,str], duplicate_attrs: list[str], positional: list[str])`, with properties `.content -> str` and `.modules -> list[Node]` and method `.value(attr) -> str` (unescaped)
  - `Document(source, nodes, problems)`, with `.line_col(offset) -> (line, col)`, `.walk() -> Iterator[(Node, path: str, parent: Node|None)]`, `.find(path) -> Node|None` and `.sections() -> list[Node]`
  - `parse(source: str) -> Document`
  - `parse_attrs(text) -> (attrs, quoting, duplicates, positional)`
  - `build_open_tag(node) -> str`, which rebuilds `[tag a="v" …]` from `node.attrs`
  - `serialize(doc_or_nodes) -> str` and `serialize_node(node) -> str`
  - `new_node(tag, attrs=None, content="", children=None) -> Node`, which escapes plain values
  - `escape_attr_value(value, attr="") -> str` and `unescape_attr_value(value) -> str`
  - `wp_blanks_value(raw_value) -> bool`
  - `replace_span(source, start, end, replacement) -> str`
  - Path syntax: `et_pb_section[2] > et_pb_row[0] > et_pb_column[1] > et_pb_blurb[0]`, where the index counts siblings **of the same tag**.

- [ ] **Step 1: Write the failing tests**

`tests/test_divi_shortcode.py`:
```python
import time
import unittest

from _paths import FIXTURES
from divi_shortcode import (Node, Text, escape_attr_value, new_node, parse, parse_attrs,
                            replace_span, serialize, unescape_attr_value, wp_blanks_value)

SIMPLE = ('[et_pb_section admin_label="Hero"][et_pb_row column_structure="1_2,1_2"]'
          '[et_pb_column type="1_2"][et_pb_text text_font_size="18px"]<p>Hi</p>[/et_pb_text][/et_pb_column]'
          '[et_pb_column type="1_2"][et_pb_image src="https://x.test/a.jpg"][/et_pb_image][/et_pb_column]'
          '[/et_pb_row][/et_pb_section]')


class ParseTest(unittest.TestCase):
    def test_roundtrip_captured_pages(self):
        for path in sorted((FIXTURES / "valid").glob("*.txt")):
            src = path.read_text()
            doc = parse(src)
            self.assertEqual(doc.problems, [], path.name)
            self.assertEqual(serialize(doc), src, path.name)

    def test_tree_shape(self):
        doc = parse(SIMPLE)
        (section,) = doc.sections()
        row = section.modules[0]
        self.assertEqual(row.attrs["column_structure"], "1_2,1_2")
        text = row.modules[0].modules[0]
        self.assertEqual(text.tag, "et_pb_text")
        self.assertEqual(text.content, "<p>Hi</p>")
        self.assertEqual([p for _, p, _ in doc.walk()][-1],
                         "et_pb_section[0] > et_pb_row[0] > et_pb_column[1] > et_pb_image[0]")

    def test_walk_yields_parent(self):
        doc = parse(SIMPLE)
        parents = {p: (par.tag if par else None) for _, p, par in doc.walk()}
        self.assertIsNone(parents["et_pb_section[0]"])
        self.assertEqual(parents["et_pb_section[0] > et_pb_row[0]"], "et_pb_section")

    def test_find(self):
        doc = parse(SIMPLE)
        node = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]")
        self.assertEqual(node.tag, "et_pb_text")
        self.assertIsNone(doc.find("et_pb_section[3]"))

    def test_attr_grammar(self):
        attrs, quoting, dups, positional = parse_attrs(' a="1" b=\'2\' c=3 D="4" a="5" loose')
        self.assertEqual(attrs, {"a": "5", "b": "2", "c": "3", "d": "4"})
        self.assertEqual(quoting, {"a": '"', "b": "'", "c": "", "d": '"'})
        self.assertEqual(dups, ["a"])
        self.assertEqual(positional, ["loose"])

    def test_self_closing_without_closer(self):
        doc = parse('[et_pb_column type="4_4"][et_pb_divider][et_pb_text]<p>x</p>[/et_pb_text][/et_pb_column]')
        col = doc.nodes[0]
        self.assertEqual([m.tag for m in col.modules], ["et_pb_divider", "et_pb_text"])
        self.assertTrue(col.modules[0].self_closing)

    def test_unclosed_and_stray(self):
        doc = parse('[et_pb_section][et_pb_row][/et_pb_section][/et_pb_row]')
        codes = [p.code for p in doc.problems]
        self.assertIn("E_UNCLOSED", codes)
        self.assertIn("E_STRAY_CLOSE", codes)

    def test_third_party_shortcode_is_text(self):
        src = '[et_pb_text]<p>[contact-form-7 id="5" title="Form"]</p>[/et_pb_text]'
        doc = parse(src)
        self.assertEqual(len(doc.nodes), 1)
        self.assertEqual(doc.nodes[0].content, '<p>[contact-form-7 id="5" title="Form"]</p>')
        self.assertEqual(serialize(doc), src)

    def test_crlf_roundtrip_and_line_col(self):
        src = SIMPLE.replace("][", "]\r\n[")
        doc = parse(src)
        self.assertEqual(serialize(doc), src)
        text = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]")
        self.assertEqual(doc.line_col(text.start), (4, 1))

    def test_unicode_roundtrip_and_escape(self):
        title = 'Odontología en Miami — “sonrisa” "real" [VIP] & más 😀'
        esc = escape_attr_value(title)
        self.assertEqual(esc, 'Odontología en Miami — “sonrisa” %22real%22 %91VIP%93 & más 😀')
        self.assertEqual(unescape_attr_value(esc), title)
        src = f'[et_pb_heading title="{esc}"][/et_pb_heading]'
        doc = parse(src)
        self.assertEqual(serialize(doc), src)
        self.assertEqual(doc.nodes[0].value("title"), title)

    def test_backslash_escaped_only_for_css_and_json_attrs(self):
        self.assertEqual(escape_attr_value("a\\b", "custom_css_main_element"), "a%92b")
        self.assertEqual(escape_attr_value("a\\b", "select_options"), "a%92b")
        self.assertEqual(escape_attr_value("a\\b", "title"), "a\\b")

    def test_edit_attr_rebuilds_only_that_tag(self):
        doc = parse(SIMPLE)
        text = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]")
        text.attrs["text_font_size"] = "20px"
        out = serialize(doc)
        self.assertEqual(out, SIMPLE.replace('text_font_size="18px"', 'text_font_size="20px"'))

    def test_new_node_escapes_and_closes(self):
        node = new_node("et_pb_heading", {"title": 'Say "hi"'})
        self.assertEqual(serialize([node]), '[et_pb_heading title="Say %22hi%22"][/et_pb_heading]')
        text = new_node("et_pb_text", {}, content="<p>x</p>")
        self.assertEqual(serialize([text]), "[et_pb_text]<p>x</p>[/et_pb_text]")

    def test_replace_span(self):
        doc = parse(SIMPLE)
        img = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[1] > et_pb_image[0]")
        out = replace_span(SIMPLE, img.start, img.end, "[et_pb_divider][/et_pb_divider]")
        self.assertIn("[et_pb_divider][/et_pb_divider][/et_pb_column]", out)
        with self.assertRaises(ValueError):
            replace_span(SIMPLE, 10, 5, "")

    def test_wp_blanks_value(self):
        self.assertFalse(wp_blanks_value("plain"))
        self.assertFalse(wp_blanks_value("<b>bold</b> text"))
        self.assertTrue(wp_blanks_value("a < b"))

    def test_large_input_is_fast(self):
        big = (FIXTURES / "valid" / "divi-ai-layout.txt").read_text() * 2
        t0 = time.time()
        self.assertEqual(serialize(parse(big)), big)
        self.assertLess(time.time() - t0, 2.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_divi_shortcode.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'divi_shortcode'`

- [ ] **Step 3: Implement `divi_shortcode.py`**

`Skill/divi-page-builder/scripts/divi_shortcode.py`:
```python
"""Parse, edit and serialize Divi 4 page content (nested [et_pb_*] shortcodes).

Stdlib only. For well-formed input, serialize(parse(s)) == s byte-for-byte.
Attribute values in Node.attrs are kept exactly as written (still escaped);
use Node.value(name) for the unescaped value.
"""
from __future__ import annotations

import bisect
import re
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Tuple, Union

TAG_RE = re.compile(r"\[(/?)(et_pb_[A-Za-z0-9_]+)((?:[^\]\"']|\"[^\"]*\"|'[^']*')*)\]")
# WordPress get_shortcode_atts_regex(), in the same alternation order.
ATTR_RE = re.compile(
    r'([\w-]+)\s*=\s*"([^"]*)"(?:\s|$)'
    r"|([\w-]+)\s*=\s*'([^']*)'(?:\s|$)"
    r"|([\w-]+)\s*=\s*([^\s'\"]+)(?:\s|$)"
    r'|"([^"]*)"(?:\s|$)'
    r"|'([^']*)'(?:\s|$)"
    r"|(\S+)(?:\s|$)"
)
# Attributes whose backslashes Divi encodes as %92 (functions.php:2063-2067).
BACKSLASH_ATTRS = ("checkbox_options", "radio_options", "select_options", "conditional_logic_rules")
_WP_LT_OK = re.compile(r"^[^<]*(?:<[^>]*>[^<]*)*$")
_PATH_PART = re.compile(r"^(et_pb_\w+)\[(\d+)\]$")


@dataclass
class Problem:
    code: str
    message: str
    offset: int


@dataclass
class Text:
    value: str
    start: int = -1
    end: int = -1


@dataclass
class Node:
    tag: str
    attrs: dict
    start: int = -1
    open_end: int = -1
    close_start: Optional[int] = None
    end: int = -1
    raw_open: str = ""
    raw_close: str = ""
    self_closing: bool = False
    children: list = field(default_factory=list)
    orig_attrs: dict = field(default_factory=dict)
    quoting: dict = field(default_factory=dict)
    duplicate_attrs: list = field(default_factory=list)
    positional: list = field(default_factory=list)

    @property
    def content(self) -> str:
        return "".join(c.value if isinstance(c, Text) else serialize_node(c) for c in self.children)

    @property
    def modules(self) -> List["Node"]:
        return [c for c in self.children if isinstance(c, Node)]

    def value(self, attr: str, default: str = "") -> str:
        return unescape_attr_value(self.attrs.get(attr, default))


@dataclass
class Document:
    source: str
    nodes: list
    problems: List[Problem]
    _line_starts: List[int] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._line_starts = [0] + [m.end() for m in re.finditer(r"\n", self.source)]

    def line_col(self, offset: int) -> Tuple[int, int]:
        i = bisect.bisect_right(self._line_starts, max(offset, 0)) - 1
        return i + 1, offset - self._line_starts[i] + 1

    def walk(self) -> Iterator[Tuple[Node, str, Optional[Node]]]:
        def rec(children, prefix, parent):
            counts = {}
            for child in children:
                if isinstance(child, Node):
                    idx = counts.get(child.tag, 0)
                    counts[child.tag] = idx + 1
                    path = f"{prefix} > {child.tag}[{idx}]" if prefix else f"{child.tag}[{idx}]"
                    yield child, path, parent
                    yield from rec(child.children, path, child)
        yield from rec(self.nodes, "", None)

    def find(self, path: str) -> Optional[Node]:
        children = self.nodes
        node = None
        for part in (p.strip() for p in path.split(">")):
            m = _PATH_PART.match(part)
            if not m:
                raise ValueError(f"bad path segment {part!r}")
            same = [c for c in children if isinstance(c, Node) and c.tag == m.group(1)]
            idx = int(m.group(2))
            if idx >= len(same):
                return None
            node = same[idx]
            children = node.children
        return node

    def sections(self) -> List[Node]:
        return [n for n in self.nodes if isinstance(n, Node) and n.tag == "et_pb_section"]


def parse_attrs(text: str):
    """WordPress shortcode_parse_atts(): returns (attrs, quoting, duplicates, positional)."""
    attrs, quoting, dups, positional = {}, {}, [], []
    text = re.sub("[\u00a0\u200b]+", " ", text)
    for m in ATTR_RE.finditer(text):
        if m.group(1) is not None:
            name, value, q = m.group(1), m.group(2), '"'
        elif m.group(3) is not None:
            name, value, q = m.group(3), m.group(4), "'"
        elif m.group(5) is not None:
            name, value, q = m.group(5), m.group(6), ""
        else:
            positional.append(next(g for g in m.groups()[6:] if g is not None))
            continue
        name = name.lower()
        if name in attrs:
            dups.append(name)
        attrs[name] = value
        quoting[name] = q
    return attrs, quoting, dups, positional


def parse(source: str) -> Document:
    problems: List[Problem] = []
    matches = list(TAG_RE.finditer(source))
    closers: dict = {}
    for m in matches:
        if m.group(1):
            closers.setdefault(m.group(2), []).append(m.start())

    roots: list = []
    stack: List[Node] = []
    pos = 0

    def container() -> list:
        return stack[-1].children if stack else roots

    def emit_text(upto: int) -> None:
        nonlocal pos
        if upto > pos:
            container().append(Text(source[pos:upto], pos, upto))
        pos = upto

    def has_closer_after(tag: str, offset: int) -> bool:
        positions = closers.get(tag, [])
        return bisect.bisect_left(positions, offset) < len(positions)

    for m in matches:
        emit_text(m.start())
        slash, tag, attr_text = m.group(1), m.group(2), m.group(3)
        if slash:
            if any(n.tag == tag for n in stack):
                while stack[-1].tag != tag:
                    orphan = stack.pop()
                    problems.append(Problem("E_UNCLOSED", f"[{orphan.tag}] is never closed (found [/{tag}] first)", orphan.start))
                    orphan.close_start = orphan.end = m.start()
                node = stack.pop()
                node.close_start, node.end, node.raw_close = m.start(), m.end(), m.group(0)
            else:
                problems.append(Problem("E_STRAY_CLOSE", f"[/{tag}] has no matching opening tag", m.start()))
                container().append(Text(m.group(0), m.start(), m.end()))
            pos = m.end()
            continue
        stripped = attr_text.rstrip()
        self_closing = stripped.endswith("/")
        if self_closing:
            attr_text = stripped[:-1]
        attrs, quoting, dups, positional = parse_attrs(attr_text)
        node = Node(tag=tag, attrs=attrs, start=m.start(), open_end=m.end(), raw_open=m.group(0),
                    orig_attrs=dict(attrs), quoting=quoting, duplicate_attrs=dups, positional=positional)
        container().append(node)
        if self_closing or not has_closer_after(tag, m.end()):
            node.self_closing = True
            node.end = m.end()
        else:
            stack.append(node)
        pos = m.end()
    emit_text(len(source))
    while stack:
        orphan = stack.pop()
        problems.append(Problem("E_UNCLOSED", f"[{orphan.tag}] is never closed", orphan.start))
        orphan.end = len(source)
    return Document(source, roots, problems)


def build_open_tag(node: Node) -> str:
    return "[" + " ".join([node.tag] + [f'{k}="{v}"' for k, v in node.attrs.items()]) + "]"


def serialize_node(node: Node) -> str:
    if node.raw_open and node.attrs == node.orig_attrs:
        opening = node.raw_open
        if node.self_closing and not node.children:
            return opening
    else:
        opening = build_open_tag(node)
    inner = "".join(c.value if isinstance(c, Text) else serialize_node(c) for c in node.children)
    return opening + inner + (node.raw_close or f"[/{node.tag}]")


def serialize(doc_or_nodes: Union[Document, list]) -> str:
    nodes = doc_or_nodes.nodes if isinstance(doc_or_nodes, Document) else doc_or_nodes
    return "".join(c.value if isinstance(c, Text) else serialize_node(c) for c in nodes)


def new_node(tag: str, attrs: Optional[dict] = None, content: str = "", children: Optional[list] = None) -> Node:
    """Build a node from plain (unescaped) attribute values."""
    escaped = {k: escape_attr_value(str(v), k) for k, v in (attrs or {}).items()}
    kids = ([Text(content)] if content else []) + list(children or [])
    return Node(tag=tag, attrs=escaped, children=kids)


def escape_attr_value(value: str, attr: str = "") -> str:
    out = value.replace('"', "%22").replace("[", "%91").replace("]", "%93")
    if attr.startswith("custom_css_") or attr in BACKSLASH_ATTRS:
        out = out.replace("\\", "%92")
    return out


def unescape_attr_value(value: str) -> str:
    for enc, dec in (("%22", '"'), ("%91", "["), ("%93", "]"), ("%92", "\\"), ("%5c", "\\"), ("%5C", "\\")):
        value = value.replace(enc, dec)
    return value


def wp_blanks_value(raw_value: str) -> bool:
    """WordPress empties a shortcode attribute containing '<' unless every '<' opens a complete tag."""
    return "<" in raw_value and not _WP_LT_OK.match(raw_value)


def replace_span(source: str, start: int, end: int, replacement: str) -> str:
    if not 0 <= start <= end <= len(source):
        raise ValueError(f"invalid span {start}:{end} for source of length {len(source)}")
    return source[:start] + replacement + source[end:]
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 -m unittest tests/test_divi_shortcode.py -v`
Expected: all PASS. If `test_crlf_roundtrip_and_line_col` reports another line number, print `doc.line_col(text.start)` together with `src.count("\n", 0, text.start)`. The expected line is that newline count plus 1; fix `line_col`, not the test.

- [ ] **Step 5: Commit**

```bash
git add Skill/divi-page-builder/scripts/divi_shortcode.py tests/test_divi_shortcode.py
git commit -m "scripts: divi_shortcode parser/serializer with exact round-trip"
```

---

### Task 3: Compact schema, `divi_schema.py` resolver, calibration

**Files:**
- Create: `research/tools/build_schema.py`, `research/tools/extras.json`
- Create: `Skill/divi-page-builder/scripts/divi_schema.py`
- Create (generated): `Skill/divi-page-builder/scripts/schema/*.json`, `Skill/divi-page-builder/scripts/schema/_meta.json`
- Test: `tests/test_divi_schema.py`

**Interfaces:**
- Consumes: `divi_shortcode.parse`, `Document.walk` (Task 2).
- Produces:
  - `Resolution(kind: str, base: str, field: dict|None)`, where `kind` is one of `field`, `global`, `extra`, `responsive`, `hover`, `sticky`, `state_toggle`, `bg_enable`
  - `ModuleSchema` with `.slug`, `.name`, `.kind` (`module`/`child`/`structure`), `.fullwidth`, `.child`, `.parents`, `.fields`, `.extras`, `.resolve(attr) -> Resolution|None` and `.attribute_names() -> list[str]`
  - `Schema` with `.divi_version`, `.slugs`, `.global_attrs`, `.column_structures: dict[str, list[str]]` (keys `et_pb_row`, `et_pb_row_inner`), `.column_types: set[str]` and `.module(slug) -> ModuleSchema|None`
  - `load_schema(directory=None) -> Schema`
- Compact field dict keys: `type`, `tab` (`general`/`advanced`/`custom_css`), `toggle`, `label`, `options` (list of legal values), `units`, `default_unit`, `default`, `default_on_front`, `responsive`, `hover`, `sticky` (bools, present only when true), `composite_of`.

- [ ] **Step 1: Write the curated extras file**

Every entry must be backed by evidence: a captured page or a Divi source reference.

`research/tools/extras.json`:
```json
{
  "global": {
    "global_colors_info": {"type": "global_colors_info", "why": "Global color bookkeeping; JSON escaped with %22/%91/%93 (seen on every module in Divi AI output)"},
    "locked": {"type": "yes_no_button", "options": ["on", "off"], "why": "Builder lock state (Divi AI output)"},
    "collapsed": {"type": "yes_no_button", "options": ["on", "off"], "why": "Builder collapsed state (Divi AI output)"},
    "fb_built": {"type": "text", "why": "Added to sections saved by the Visual Builder (functions.php:2093)"},
    "template_type": {"type": "text", "why": "Divi Library template marker (Divi AI output)"}
  },
  "modules": {
    "et_pb_accordion_item": {
      "open": {"type": "yes_no_button", "options": ["on", "off"], "why": "Initial open state; missing from the registry, used by Divi AI output"}
    }
  },
  "aliases": {"et_pb_column_inner": "et_pb_column"}
}
```

- [ ] **Step 2: Write the failing tests**

`tests/test_divi_schema.py`:
```python
import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from divi_shortcode import parse

# Attributes in the Divi AI fixtures that Divi's registry doesn't define for that module.
# Divi silently ignores them; they are template leftovers.
KNOWN_STALE = {
    ("et_pb_slide", "sticky_transition"),
    ("et_pb_accordion", "quote_icon_color"),
    ("et_pb_cta", "text_font_size_tablet"),
    ("et_pb_cta", "text_font_size_phone"),
    ("et_pb_cta", "text_font_size_last_edited"),
}


class SchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema()

    def test_meta(self):
        self.assertEqual(self.schema.divi_version, "4.27.9")
        self.assertEqual(len(self.schema.slugs), 64)
        self.assertIn("1_3,2_3", self.schema.column_structures["et_pb_row"])
        self.assertEqual(self.schema.column_structures["et_pb_row_inner"],
                         ["4_4", "1_2,1_2", "1_3,1_3,1_3", "1_4,1_4,1_4,1_4"])
        self.assertIn("1_5", self.schema.column_types)

    def test_kinds_and_relations(self):
        s = self.schema
        self.assertEqual(s.module("et_pb_section").kind, "structure")
        self.assertEqual(s.module("et_pb_column_inner").kind, "structure")
        self.assertEqual(s.module("et_pb_tab").kind, "child")
        self.assertEqual(s.module("et_pb_tabs").child, "et_pb_tab")
        self.assertEqual(sorted(s.module("et_pb_slide").parents), ["et_pb_fullwidth_slider", "et_pb_slider"])
        self.assertTrue(s.module("et_pb_fullwidth_header").fullwidth)
        self.assertIsNone(s.module("et_pb_nope"))

    def test_resolution_kinds(self):
        blurb = self.schema.module("et_pb_blurb")
        cases = {
            "title": "field",
            "title_tablet": "responsive",
            "title_last_edited": "responsive",
            "header_text_color__hover": "hover",
            "header_text_color__hover_enabled": "state_toggle",
            "background__hover_enabled": "state_toggle",
            "global_colors_info": "global",
            "transform_scale": "field",
            "background_enable_color": "field",
        }
        for attr, kind in cases.items():
            res = blurb.resolve(attr)
            self.assertIsNotNone(res, attr)
            self.assertEqual(res.kind, kind, attr)
        self.assertIsNone(blurb.resolve("title_colour"))
        self.assertIsNone(blurb.resolve("use_icon__hover"))  # use_icon has no hover support
        self.assertEqual(self.schema.module("et_pb_button").resolve("button_bg_enable_color").kind, "bg_enable")
        self.assertEqual(self.schema.module("et_pb_accordion_item").resolve("open").kind, "extra")

    def test_calibration_against_real_pages(self):
        unresolved = set()
        for path in (FIXTURES / "valid").glob("divi-ai-*.txt"):
            for node, _, _ in parse(path.read_text()).walk():
                mod = self.schema.module(node.tag)
                self.assertIsNotNone(mod, node.tag)
                for attr in node.attrs:
                    if mod.resolve(attr) is None:
                        unresolved.add((node.tag, attr))
        self.assertEqual(unresolved, KNOWN_STALE)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_divi_schema.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'divi_schema'`

- [ ] **Step 4: Implement the compiler**

`research/tools/build_schema.py`:
```python
#!/usr/bin/env python3
"""Compile the raw Divi schema dump into the compact schema used by the skill's scripts.

Usage: build_schema.py <raw_schema_dir> <extras.json> <out_dir>
"""
import json
import sys
from pathlib import Path

RESP_SUFFIXES = ("_tablet", "_phone", "_last_edited")
STRUCTURE = {"et_pb_section", "et_pb_row", "et_pb_row_inner", "et_pb_column", "et_pb_column_inner"}


def option_values(field: dict):
    opts = field.get("options")
    if isinstance(opts, list):
        return [str(o) for o in opts]
    if not isinstance(opts, dict) or not opts:
        return None
    if field.get("type") == "select_with_option_groups":
        return [str(k) for group in opts.values() if isinstance(group, dict) for k in group]
    return [str(k) for k in opts]


def compact_field(name: str, d: dict, raw: dict) -> dict:
    out = {"type": d.get("type", ""), "tab": d.get("tab_slug") or "general", "toggle": d.get("toggle_slug") or ""}
    if d.get("label"):
        out["label"] = d["label"]
    values = option_values(d)
    if values is not None:
        out["options"] = values
    if d.get("allowed_units"):
        out["units"] = list(d["allowed_units"])
    if d.get("default_unit"):
        out["default_unit"] = str(d["default_unit"])
    for key in ("default", "default_on_front"):
        if isinstance(d.get(key), (str, int, float)):
            out[key] = str(d[key])
    if d.get("mobile_options") or d.get("responsive") or f"{name}_tablet" in raw:
        out["responsive"] = True
    if d.get("hover"):
        out["hover"] = True
    if d.get("sticky"):
        out["sticky"] = True
    if d.get("composite_of"):
        out["composite_of"] = d["composite_of"]
    return out


def is_derived(name: str, raw: dict) -> bool:
    """A skip entry that only exists as a responsive variant of another field."""
    return any(name.endswith(s) and name[: -len(s)] in raw for s in RESP_SUFFIXES) and raw[name].get("type") == "skip"


def main(raw_dir: str, extras_path: str, out_dir: str) -> None:
    raw_dir, out = Path(raw_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    extras = json.loads(Path(extras_path).read_text())
    index = json.loads((raw_dir / "index.json").read_text())
    raw = {p.stem: json.loads(p.read_text()) for p in (raw_dir / "modules").glob("*.json")}
    parents: dict = {}
    for slug, data in raw.items():
        child = data["module"].get("child_slug")
        if child:
            parents.setdefault(child, []).append(slug)

    for slug, data in sorted(raw.items()):
        fields = data["fields"]
        kind = "structure" if slug in STRUCTURE else ("child" if slug in parents or data["module"].get("type") == "child" else "module")
        compact = {
            "slug": slug,
            "name": data["module"]["name"],
            "kind": kind,
            "fullwidth": bool(data["module"].get("fullwidth")),
            "child": data["module"].get("child_slug"),
            "parents": sorted(parents.get(slug, [])),
            "fields": {n: compact_field(n, d, fields) for n, d in fields.items() if not is_derived(n, fields)},
            "extras": extras["modules"].get(slug, {}),
        }
        (out / f"{slug}.json").write_text(json.dumps(compact, indent=1, sort_keys=True))

    meta = {
        "divi_version": index["divi_version"],
        "modules": sorted(raw) + sorted(extras["aliases"]),
        "aliases": extras["aliases"],
        "global_attrs": extras["global"],
        "column_structures": {
            "et_pb_row": option_values(raw["et_pb_row"]["fields"]["column_structure"]),
            "et_pb_row_inner": option_values(raw["et_pb_row_inner"]["fields"]["column_structure"]),
        },
    }
    (out / "_meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True))
    print(f"wrote {len(raw)} modules + _meta.json to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
```

- [ ] **Step 5: Implement the resolver**

`Skill/divi-page-builder/scripts/divi_schema.py`:
```python
"""Load the compact Divi schema and resolve attribute names to field definitions (stdlib only)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

SCHEMA_DIR = Path(__file__).resolve().parent / "schema"
RESP_SUFFIXES = ("_tablet", "_phone", "_last_edited")
# (suffix, state flag on the base field, is the *_enabled toggle)
STATE_SUFFIXES = (("__hover_enabled", "hover", True), ("__sticky_enabled", "sticky", True),
                  ("__hover", "hover", False), ("__sticky", "sticky", False))
BG_ENABLE_RE = re.compile(r"^(?P<prefix>.+)_enable_(?:color|image|video_mp4|video_webm|pattern_style|mask_style)$")


@dataclass(frozen=True)
class Resolution:
    kind: str
    base: str
    field: Optional[dict]


class ModuleSchema:
    def __init__(self, data: dict, global_attrs: Dict[str, dict]):
        self.slug: str = data["slug"]
        self.name: str = data["name"]
        self.kind: str = data["kind"]
        self.fullwidth: bool = data.get("fullwidth", False)
        self.child: Optional[str] = data.get("child")
        self.parents: List[str] = data.get("parents", [])
        self.fields: Dict[str, dict] = data["fields"]
        self.extras: Dict[str, dict] = data.get("extras", {})
        self._global = global_attrs
        self._groups: Dict[tuple, bool] = {}

    def attribute_names(self) -> List[str]:
        return sorted(set(self.fields) | set(self.extras) | set(self._global))

    def _has_state_group(self, prefix: str, state: str) -> bool:
        key = (prefix, state)
        if key not in self._groups:
            self._groups[key] = any(n.startswith(prefix + "_") and f.get(state) for n, f in self.fields.items())
        return self._groups[key]

    def resolve(self, attr: str) -> Optional[Resolution]:
        if attr in self.fields:
            return Resolution("field", attr, self.fields[attr])
        if attr in self.extras:
            return Resolution("extra", attr, self.extras[attr])
        if attr in self._global:
            return Resolution("global", attr, self._global[attr])
        for suffix, state, is_toggle in STATE_SUFFIXES:
            if attr.endswith(suffix):
                base = attr[: -len(suffix)]
                f = self.fields.get(base)
                if f is not None and f.get(state):
                    return Resolution("state_toggle" if is_toggle else state, base, f)
                if is_toggle and self._has_state_group(base, state):
                    return Resolution("state_toggle", base, None)
                return None
        for suffix in RESP_SUFFIXES:
            if attr.endswith(suffix):
                inner = self.resolve(attr[: -len(suffix)])
                if inner is not None and (inner.kind == "bg_enable" or (inner.field or {}).get("responsive")):
                    return Resolution("responsive", inner.base, inner.field)
                return None
        m = BG_ENABLE_RE.match(attr)
        if m and any(f"{m['prefix']}_{s}" in self.fields for s in ("color", "use_color_gradient")):
            return Resolution("bg_enable", attr, {"type": "yes_no_button", "options": ["on", "off"]})
        return None


class Schema:
    def __init__(self, directory: Path):
        meta = json.loads((directory / "_meta.json").read_text())
        self.directory = directory
        self.divi_version: str = meta["divi_version"]
        self.global_attrs: Dict[str, dict] = meta["global_attrs"]
        self.column_structures: Dict[str, List[str]] = meta["column_structures"]
        self.column_types = {t for lst in self.column_structures.values() for s in lst for t in s.split(",")}
        self._aliases: Dict[str, str] = meta["aliases"]
        self.slugs: List[str] = [s for s in meta["modules"] if s not in self._aliases]
        self._known = set(meta["modules"])
        self._cache: Dict[str, ModuleSchema] = {}

    def module(self, slug: str) -> Optional[ModuleSchema]:
        if slug not in self._known:
            return None
        real = self._aliases.get(slug, slug)
        if real not in self._cache:
            data = json.loads((self.directory / f"{real}.json").read_text())
            self._cache[real] = ModuleSchema(data, self.global_attrs)
        return self._cache[real]


def load_schema(directory: Optional[Path] = None) -> Schema:
    return Schema(Path(directory) if directory else SCHEMA_DIR)
```

Note on `STATE_SUFFIXES` ordering: `__hover_enabled` must be checked before `__hover`. The tuple order handles this.

- [ ] **Step 6: Build the compact schema and run the tests**

Run:
```bash
python3 research/tools/build_schema.py research/divi-schema research/tools/extras.json Skill/divi-page-builder/scripts/schema
python3 -m unittest tests/test_divi_schema.py -v
```
Expected: `wrote 64 modules + _meta.json …`, then all PASS.

If `test_calibration_against_real_pages` fails, handle each difference individually:
- **An attribute is unresolved but not in `KNOWN_STALE`:** grep the Divi source for it (`grep -rn "'<attr>'" "$DIVI/includes/builder"`). If Divi really reads it for that module, add it to `extras.json` with a `why` that cites the file and line. Otherwise add it to `KNOWN_STALE` with a comment.
- **A `KNOWN_STALE` entry now resolves:** remove it from the set.

- [ ] **Step 7: Commit**

```bash
git add research/tools/build_schema.py research/tools/extras.json Skill/divi-page-builder/scripts/divi_schema.py Skill/divi-page-builder/scripts/schema tests/test_divi_schema.py
git commit -m "scripts: compact Divi schema + attribute resolver calibrated on real pages"
```

---

### Task 4: Validator core and structure checks

**Files:**
- Create: `Skill/divi-page-builder/scripts/validate.py` (Finding model, `validate_source`, CLI)
- Create: `Skill/divi-page-builder/scripts/divi_checks_structure.py`
- Create: `tests/fixtures/valid/handwritten-landing.txt`
- Test: `tests/test_validate_structure.py`

**Interfaces:**
- Consumes: `parse`, `Document`, `Node`, `Text` (Task 2); `Schema`, `ModuleSchema` (Task 3).
- Produces:
  - `validate.Finding(level, code, message, line, col, path, tag="", attr="", value="", hint="", preexisting=False)`, a dataclass;
  - `validate.validate_source(source: str, schema: Schema, tokens: dict|None = None, site_url: str|None = None, baseline: str|None = None) -> list[Finding]`;
  - `validate.Reporter(doc)`, callable as `report(level, code, message, node=None, path="", offset=None, attr="", value="", hint="")`, with a `.findings` list;
  - `divi_checks_structure.check_structure(doc, schema, report) -> None`.

- [ ] **Step 1: Write the known-good hand-written fixture**

`tests/fixtures/valid/handwritten-landing.txt` has one section per structural pattern:
- a regular 1/2 + 1/2 hero;
- a three-blurb row;
- an accordion;
- a specialty section;
- a fullwidth header.

```
[et_pb_section admin_label="Hero" _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" custom_padding="96px||96px||true|false" custom_padding_tablet="64px||64px||true|false" custom_padding_phone="48px||48px||true|false" custom_padding_last_edited="on|phone"][et_pb_row column_structure="1_2,1_2" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Emergency Plumber in Miami" title_level="h1" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#ffffff" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#cbd5e1" text_font_size="18px"]<p>Licensed, insured plumbers at your door in 60 minutes.</p>[/et_pb_text][et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_text_color="#ffffff" button_bg_color="#f97316" button_border_radius="6px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover"][/et_pb_button][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://client.example/wp-content/uploads/2026/09/plumber.jpg" alt="Plumber repairing a burst pipe" _builder_version="4.27.9" _module_preset="default"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section][et_pb_section admin_label="Services" _builder_version="4.27.9" _module_preset="default"][et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb title="Burst Pipes" use_icon="on" font_icon="&#xe03b;||divi||400" icon_color="#f97316" header_level="h3" _builder_version="4.27.9" _module_preset="default"]<p>Fast shut-off and repair.</p>[/et_pb_blurb][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb title="Water Heaters" use_icon="on" font_icon="&#xe03b;||divi||400" icon_color="#f97316" header_level="h3" _builder_version="4.27.9" _module_preset="default"]<p>Same-day repair or replacement.</p>[/et_pb_blurb][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb title="Drain Clogs" use_icon="on" font_icon="&#xe03b;||divi||400" icon_color="#f97316" header_level="h3" _builder_version="4.27.9" _module_preset="default"]<p>Camera inspection and hydro-jetting.</p>[/et_pb_blurb][/et_pb_column][/et_pb_row][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_accordion _builder_version="4.27.9" _module_preset="default"][et_pb_accordion_item title="How fast can you arrive?" open="on" _builder_version="4.27.9" _module_preset="default"]<p>Within 60 minutes anywhere in Miami-Dade.</p>[/et_pb_accordion_item][et_pb_accordion_item title="Are you licensed?" open="off" _builder_version="4.27.9" _module_preset="default"]<p>Yes, licensed and insured.</p>[/et_pb_accordion_item][/et_pb_accordion][/et_pb_column][/et_pb_row][/et_pb_section][et_pb_section specialty="on" admin_label="Specialty" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Sidebar note.</p>[/et_pb_text][/et_pb_column][et_pb_column type="3_4" specialty_columns="3" _builder_version="4.27.9" _module_preset="default"][et_pb_row_inner column_structure="1_2,1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_column_inner type="1_2" saved_specialty_column_type="3_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Left.</p>[/et_pb_text][/et_pb_column_inner][et_pb_column_inner type="1_2" saved_specialty_column_type="3_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Right.</p>[/et_pb_text][/et_pb_column_inner][/et_pb_row_inner][/et_pb_column][/et_pb_section][et_pb_section fullwidth="on" admin_label="Closing" _builder_version="4.27.9" _module_preset="default"][et_pb_fullwidth_header title="Need a plumber now?" subhead="We answer 24/7" button_one_text="Call now" button_one_url="tel:+13055550100" text_orientation="center" _builder_version="4.27.9" _module_preset="default"]<p>Licensed and insured.</p>[/et_pb_fullwidth_header][/et_pb_section]
```
Use Write to create the file as a single line, exactly as shown.

- [ ] **Step 2: Write the failing tests**

`tests/test_validate_structure.py`:
```python
import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from validate import validate_source

SCHEMA = load_schema()
V = '_builder_version="4.27.9"'


def codes(src, level="error"):
    return [f.code for f in validate_source(src, SCHEMA) if f.level == level]


def page(inner):
    return f'[et_pb_section {V}][et_pb_row {V}][et_pb_column type="4_4" {V}]{inner}[/et_pb_column][/et_pb_row][/et_pb_section]'


class StructureTest(unittest.TestCase):
    def test_handwritten_fixture_is_clean(self):
        src = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()
        errors = [f for f in validate_source(src, SCHEMA) if f.level == "error"]
        self.assertEqual(errors, [])

    def test_text_outside_section(self):
        self.assertIn("E_TEXT_OUTSIDE_SECTION", codes("hello " + page("")))

    def test_module_at_top_level(self):
        self.assertIn("E_TOP_LEVEL", codes("[et_pb_text]<p>x</p>[/et_pb_text]"))

    def test_unknown_tag(self):
        self.assertIn("E_UNKNOWN_TAG", codes(page("[et_pb_fancy_widget][/et_pb_fancy_widget]")))

    def test_parse_problems_reported(self):
        self.assertIn("E_UNCLOSED", codes('[et_pb_section][et_pb_row][/et_pb_section][/et_pb_row]'))

    def test_regular_section_needs_rows(self):
        self.assertIn("E_SECTION_CHILD", codes(f'[et_pb_section {V}][et_pb_text]<p>x</p>[/et_pb_text][/et_pb_section]'))

    def test_fullwidth_section_rejects_regular_modules(self):
        self.assertIn("E_FULLWIDTH_CHILD", codes('[et_pb_section fullwidth="on"][et_pb_text]<p>x</p>[/et_pb_text][/et_pb_section]'))

    def test_fullwidth_module_in_column(self):
        self.assertIn("E_FULLWIDTH_IN_COLUMN", codes(page('[et_pb_fullwidth_header title="x"][/et_pb_fullwidth_header]')))

    def test_column_types_must_match_structure(self):
        src = ('[et_pb_section][et_pb_row column_structure="1_2,1_2"][et_pb_column type="1_3"][/et_pb_column]'
               '[et_pb_column type="2_3"][/et_pb_column][/et_pb_row][/et_pb_section]')
        self.assertIn("W_COLUMN_STRUCTURE_MISMATCH", codes(src, "warning"))

    def test_column_sum_must_be_one(self):
        src = '[et_pb_section][et_pb_row][et_pb_column type="1_2"][/et_pb_column][/et_pb_row][/et_pb_section]'
        self.assertIn("E_COLUMN_SUM", codes(src))

    def test_row_without_column_structure_uses_column_types(self):
        src = ('[et_pb_section][et_pb_row][et_pb_column type="1_3"][/et_pb_column]'
               '[et_pb_column type="2_3"][/et_pb_column][/et_pb_row][/et_pb_section]')
        self.assertEqual(codes(src), [])
        self.assertEqual(codes(src, "warning"), [])

    def test_bad_column_type(self):
        src = '[et_pb_section][et_pb_row][et_pb_column type="7_8"][/et_pb_column][/et_pb_row][/et_pb_section]'
        self.assertIn("E_COLUMN_TYPE", codes(src))

    def test_child_outside_parent(self):
        self.assertIn("E_CHILD_PLACEMENT", codes(page('[et_pb_tab title="x"]<p>x</p>[/et_pb_tab]')))

    def test_parent_with_wrong_child(self):
        self.assertIn("E_BAD_CHILD", codes(page('[et_pb_tabs][et_pb_slide][/et_pb_slide][/et_pb_tabs]')))

    def test_nested_leaf_modules(self):
        self.assertIn("E_NESTED_MODULE", codes(page('[et_pb_text][et_pb_button][/et_pb_button][/et_pb_text]')))

    def test_inner_row_outside_specialty(self):
        self.assertIn("E_INNER_ROW_PLACEMENT", codes(page('[et_pb_row_inner][et_pb_column_inner type="4_4"][/et_pb_column_inner][/et_pb_row_inner]')))

    def test_specialty_needs_one_specialty_column(self):
        src = ('[et_pb_section specialty="on"][et_pb_column type="1_2"][/et_pb_column]'
               '[et_pb_column type="1_2"][/et_pb_column][/et_pb_section]')
        self.assertIn("E_SPECIALTY_COLUMN", codes(src))

    def test_findings_have_location_and_path(self):
        (f,) = [f for f in validate_source(page("[et_pb_fancy][/et_pb_fancy]"), SCHEMA) if f.code == "E_UNKNOWN_TAG"]
        self.assertEqual(f.line, 1)
        self.assertGreater(f.col, 1)
        self.assertTrue(f.path.endswith("et_pb_fancy[0]"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_validate_structure.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'validate'`

- [ ] **Step 4: Implement the structure checks**

`Skill/divi-page-builder/scripts/divi_checks_structure.py`:
```python
"""Structural rules for Divi 4 pages: section → row → column → module, specialty and fullwidth sections,
parent/child module pairs."""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Optional

from divi_shortcode import Node, Text

COLUMN_FOR_ROW = {"et_pb_row": "et_pb_column", "et_pb_row_inner": "et_pb_column_inner"}


def fraction(col_type: str) -> Optional[Fraction]:
    m = re.fullmatch(r"(\d+)_(\d+)", col_type or "")
    return Fraction(int(m.group(1)), int(m.group(2))) if m and int(m.group(2)) else None


def _stray_text(node, path, report):
    for child in node.children:
        if isinstance(child, Text) and child.value.strip():
            report("error", "E_STRAY_TEXT", f"Text directly inside [{node.tag}] is not rendered",
                   offset=child.start, path=path, hint="Put copy inside a text module.")


def _check_columns(node, path, cols, expected, report, schema, structure_attr_present):
    types = [c.attrs.get("type", "") for c in cols]
    for c, t in zip(cols, types):
        if t not in schema.column_types:
            report("error", "E_COLUMN_TYPE", f"Column type '{t}' is not a Divi column type", node=c,
                   path=path, attr="type", value=t, hint="Use types such as 4_4, 1_2, 1_3, 2_3, 1_4, 3_4, 1_5, 2_5, 3_5, 1_6.")
    fracs = [fraction(t) for t in types]
    if cols and all(fracs) and sum(fracs) != 1:
        report("error", "E_COLUMN_SUM", f"Column widths {','.join(types)} do not add up to one full row",
               node=node, path=path, hint="Column fractions in a row must sum to 1.")
    if structure_attr_present and expected is not None and types != expected:
        report("warning", "W_COLUMN_STRUCTURE_MISMATCH",
               f"Columns are {','.join(types)} but column_structure says {','.join(expected)}",
               node=node, path=path, attr="column_structure",
               hint="Divi renders by column type; make column_structure match so the builder shows the same layout.")


def check_structure(doc, schema, report) -> None:
    for problem in doc.problems:
        report("error", problem.code, problem.message, offset=problem.offset, path="(parser)")

    for child in doc.nodes:
        if isinstance(child, Text) and child.value.strip():
            report("error", "E_TEXT_OUTSIDE_SECTION", "Content outside any [et_pb_section] is not part of the layout",
                   offset=child.start, path="(top level)", hint="Wrap it in section → row → column → text module.")
        elif isinstance(child, Node) and child.tag != "et_pb_section":
            report("error", "E_TOP_LEVEL", f"[{child.tag}] must be inside a section", node=child, path="(top level)")

    for node, path, parent in doc.walk():
        mod = schema.module(node.tag)
        if mod is None:
            report("error", "E_UNKNOWN_TAG", f"Unknown Divi module [{node.tag}]", node=node, path=path,
                   hint="Valid slugs are listed in reference/modules/README.md.")
            continue
        kids = node.modules
        tag = node.tag

        if mod.kind == "child" and (parent is None or parent.tag not in mod.parents):
            report("error", "E_CHILD_PLACEMENT", f"[{tag}] must be a direct child of {' or '.join(mod.parents)}",
                   node=node, path=path)

        if tag == "et_pb_section":
            _stray_text(node, path, report)
            if node.value("fullwidth") == "on":
                for c in kids:
                    m = schema.module(c.tag)
                    if m is not None and not m.fullwidth:
                        report("error", "E_FULLWIDTH_CHILD", f"Fullwidth sections accept only fullwidth modules, not [{c.tag}]",
                               node=c, path=path)
            elif node.value("specialty") == "on":
                cols = [c for c in kids if c.tag == "et_pb_column"]
                for c in kids:
                    if c.tag != "et_pb_column":
                        report("error", "E_SECTION_CHILD", f"Specialty sections contain columns, not [{c.tag}]", node=c, path=path)
                _check_columns(node, path, cols, None, report, schema, False)
                special = [c for c in cols if c.value("specialty_columns")]
                if len(special) != 1:
                    report("error", "E_SPECIALTY_COLUMN", "A specialty section needs exactly one column with specialty_columns",
                           node=node, path=path, hint='Set specialty_columns="2|3|4" on the column that holds inner rows.')
                for c in cols:
                    for g in c.modules:
                        if any(c is s for s in special) and g.tag != "et_pb_row_inner":
                            report("error", "E_SPECIALTY_CONTENT", f"The specialty column holds only [et_pb_row_inner], not [{g.tag}]",
                                   node=g, path=path)
            else:
                for c in kids:
                    if c.tag != "et_pb_row":
                        report("error", "E_SECTION_CHILD", f"Regular sections contain only [et_pb_row], not [{c.tag}]",
                               node=c, path=path)
        elif tag in COLUMN_FOR_ROW:
            _stray_text(node, path, report)
            col_tag = COLUMN_FOR_ROW[tag]
            cols = [c for c in kids if c.tag == col_tag]
            for c in kids:
                if c.tag != col_tag:
                    report("error", "E_ROW_CHILD", f"[{tag}] contains only [{col_tag}], not [{c.tag}]", node=c, path=path)
            present = "column_structure" in node.attrs
            structure = node.value("column_structure", "4_4")
            if present and structure not in schema.column_structures[tag]:
                report("error", "E_COLUMN_STRUCTURE", f"'{structure}' is not a legal column_structure for [{tag}]",
                       node=node, path=path, attr="column_structure", value=structure,
                       hint="Legal values: " + ", ".join(schema.column_structures[tag]))
            _check_columns(node, path, cols, structure.split(",") if present else None, report, schema, present)
        elif tag in ("et_pb_column", "et_pb_column_inner"):
            _stray_text(node, path, report)
            in_specialty = parent is not None and parent.tag == "et_pb_section" and parent.value("specialty") == "on"
            for c in kids:
                m = schema.module(c.tag)
                if c.tag == "et_pb_row_inner":
                    if not (in_specialty and node.value("specialty_columns")):
                        report("error", "E_INNER_ROW_PLACEMENT", "[et_pb_row_inner] is only allowed in a specialty section's specialty column",
                               node=c, path=path)
                elif m is None or m.kind == "child":
                    continue  # reported at the child itself
                elif m.kind == "structure":
                    report("error", "E_COLUMN_CHILD", f"[{c.tag}] cannot be inside a column", node=c, path=path)
                elif m.fullwidth:
                    report("error", "E_FULLWIDTH_IN_COLUMN", f"[{c.tag}] only works in a fullwidth section",
                           node=c, path=path, hint='Put it in [et_pb_section fullwidth="on"].')
        elif mod.child:
            _stray_text(node, path, report)
            for c in kids:
                if c.tag != mod.child:
                    report("error", "E_BAD_CHILD", f"[{tag}] can only contain [{mod.child}], not [{c.tag}]", node=c, path=path)
        else:
            for c in kids:
                report("error", "E_NESTED_MODULE", f"[{c.tag}] cannot be nested inside [{tag}]", node=c, path=path)
```

- [ ] **Step 5: Implement the validator core and CLI skeleton**

`Skill/divi-page-builder/scripts/validate.py`:
```python
#!/usr/bin/env python3
"""Validate Divi 4 page shortcode against Divi's module schema.

Usage: validate.py PAGE [--tokens tokens.json] [--baseline ORIGINAL] [--site-url URL] [--json]
Exit status: 0 = no blocking errors, 1 = errors found, 2 = usage or I/O problem.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_checks_structure import check_structure  # noqa: E402
from divi_schema import Schema, load_schema  # noqa: E402
from divi_shortcode import Document, parse  # noqa: E402


@dataclass
class Finding:
    level: str
    code: str
    message: str
    line: int
    col: int
    path: str
    tag: str = ""
    attr: str = ""
    value: str = ""
    hint: str = ""
    preexisting: bool = False


class Reporter:
    def __init__(self, doc: Document):
        self.doc = doc
        self.findings: List[Finding] = []

    def __call__(self, level, code, message, node=None, path="", offset=None, attr="", value="", hint=""):
        pos = offset if offset is not None else (node.start if node is not None else 0)
        line, col = self.doc.line_col(pos)
        self.findings.append(Finding(level, code, message, line, col, path,
                                     tag=node.tag if node is not None else "", attr=attr, value=value, hint=hint))


def validate_source(source: str, schema: Schema, tokens: Optional[dict] = None,
                    site_url: Optional[str] = None, baseline: Optional[str] = None) -> List[Finding]:
    doc = parse(source)
    report = Reporter(doc)
    check_structure(doc, schema, report)
    return report.findings


def _format(f: Finding, filename: str) -> str:
    out = f"{filename}:{f.line}:{f.col} {f.level} {f.code} {f.path}\n  {f.message}"
    if f.hint:
        out += f"\n  hint: {f.hint}"
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--tokens")
    ap.add_argument("--baseline")
    ap.add_argument("--site-url")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        source = Path(args.page).read_text(encoding="utf-8")
        tokens = json.loads(Path(args.tokens).read_text()) if args.tokens else None
        baseline = Path(args.baseline).read_text(encoding="utf-8") if args.baseline else None
    except (OSError, ValueError) as exc:
        print(f"validate.py: {exc}", file=sys.stderr)
        return 2
    findings = validate_source(source, load_schema(), tokens=tokens, site_url=args.site_url, baseline=baseline)
    blocking = [f for f in findings if f.level == "error" and not f.preexisting]
    if args.json:
        print(json.dumps({"file": args.page, "errors": len(blocking),
                          "warnings": sum(f.level == "warning" for f in findings),
                          "findings": [asdict(f) for f in findings]}, indent=1))
    else:
        for f in findings:
            if not f.preexisting:
                print(_format(f, args.page))
        pre = [f for f in findings if f.preexisting]
        if pre:
            print(f"\n{len(pre)} pre-existing finding(s) also present in the baseline (not blocking):")
            for f in pre:
                print(_format(f, args.page))
        warnings = sum(f.level == "warning" and not f.preexisting for f in findings)
        print(f"\nSummary: {len(blocking)} error(s), {warnings} warning(s), {len(pre)} pre-existing")
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python3 -m unittest tests/test_validate_structure.py -v`
Expected: all PASS. If `test_handwritten_fixture_is_clean` fails, read each finding. Fix the **fixture** only when the finding is correct per the schema (e.g. a misspelled attribute); otherwise fix the check.

- [ ] **Step 7: Commit**

```bash
git add Skill/divi-page-builder/scripts/validate.py Skill/divi-page-builder/scripts/divi_checks_structure.py tests/fixtures/valid/handwritten-landing.txt tests/test_validate_structure.py
git commit -m "validator: finding model, CLI skeleton, structure checks"
```

---

### Task 5: Validator attribute and value checks

**Files:**
- Create: `Skill/divi-page-builder/scripts/divi_checks_values.py`
- Modify: `Skill/divi-page-builder/scripts/validate.py` (call `check_attributes` in `validate_source`)
- Test: `tests/test_validate_values.py`

**Interfaces:**
- Consumes: `ModuleSchema.resolve` / `Resolution` (Task 3); `Node.value`, `wp_blanks_value`, `unescape_attr_value` (Task 2); the `Reporter` call signature (Task 4).
- Produces:
  - `divi_checks_values.check_attributes(doc, schema, report, known_presets: set[str] = frozenset(), site_host: str|None = None) -> None`;
  - `divi_checks_values.value_problems(resolution, attr, value) -> list[tuple[level, code, message, hint]]`;
  - `COLOR_RE`;
  - `normalize_color(value) -> str`, which Task 6 reuses.

- [ ] **Step 1: Write the failing tests**

`tests/test_validate_values.py`:
```python
import unittest

from divi_schema import load_schema
from validate import validate_source

SCHEMA = load_schema()


def wrap(module):
    return f'[et_pb_section][et_pb_row][et_pb_column type="4_4"]{module}[/et_pb_column][/et_pb_row][/et_pb_section]'


def found(module, level=None):
    return [(f.level, f.code, f.attr) for f in validate_source(wrap(module), SCHEMA)
            if level is None or f.level == level]


class AttributeTest(unittest.TestCase):
    def test_unknown_attribute_with_suggestion(self):
        fs = [f for f in validate_source(wrap('[et_pb_blurb title_colour="#fff"][/et_pb_blurb]'), SCHEMA)
              if f.code == "E_UNKNOWN_ATTR"]
        self.assertEqual(len(fs), 1)
        self.assertIn("did you mean", fs[0].hint)

    def test_illegal_suffix(self):
        self.assertIn(("error", "E_UNKNOWN_ATTR", "use_icon__hover"),
                      found('[et_pb_blurb use_icon__hover="on"][/et_pb_blurb]'))

    def test_raw_bracket_and_positional(self):
        fs = found('[et_pb_heading title="Save [now]" stray][/et_pb_heading]')
        self.assertIn(("error", "E_RAW_BRACKET", "title"), fs)
        self.assertIn(("error", "E_POSITIONAL_ATTR", ""), fs)

    def test_wp_blanks_lt(self):
        self.assertIn(("error", "E_ATTR_LT", "title"), found('[et_pb_heading title="a < b"][/et_pb_heading]'))

    def test_single_quoted_value_warns(self):
        self.assertIn(("warning", "W_ATTR_QUOTING", "title"), found("[et_pb_heading title='x'][/et_pb_heading]"))

    def test_select_and_yes_no(self):
        self.assertIn(("error", "E_BAD_OPTION", "title_level"), found('[et_pb_heading title_level="h7"][/et_pb_heading]'))
        self.assertIn(("error", "E_BAD_OPTION", "use_icon"), found('[et_pb_blurb use_icon="yes"][/et_pb_blurb]'))

    def test_units(self):
        self.assertEqual(found('[et_pb_heading title_font_size="48px"][/et_pb_heading]', "error"), [])
        self.assertIn(("error", "E_BAD_UNIT", "title_font_size"), found('[et_pb_heading title_font_size="48parsecs"][/et_pb_heading]'))
        self.assertEqual(found('[et_pb_blurb max_width="none" min_height="auto"][/et_pb_blurb]', "error"), [])

    def test_colors(self):
        for ok in ("#fff", "#0E7C86", "rgba(0,0,0,0.5)", "RGBA(255,255,255,0)", "transparent", "gcid-36fd78a7"):
            self.assertEqual(found(f'[et_pb_blurb icon_color="{ok}"][/et_pb_blurb]', "error"), [], ok)
        self.assertIn(("error", "E_VALUE_FORMAT", "icon_color"), found('[et_pb_blurb icon_color="blue-ish"][/et_pb_blurb]'))

    def test_font_string(self):
        self.assertEqual(found('[et_pb_heading title_font="Montserrat|700|||||||"][/et_pb_heading]', "error"), [])
        self.assertIn(("error", "E_VALUE_FORMAT", "title_font"), found('[et_pb_heading title_font="A|700|||||||||||"][/et_pb_heading]'))
        self.assertIn(("warning", "W_FONT_WEIGHT", "title_font"), found('[et_pb_heading title_font="Poppins|Poppins_weight|||||||"][/et_pb_heading]'))

    def test_spacing_string(self):
        self.assertEqual(found('[et_pb_blurb custom_margin="10px|auto||5%|false|false"][/et_pb_blurb]', "error"), [])
        self.assertIn(("error", "E_VALUE_FORMAT", "custom_margin"), found('[et_pb_blurb custom_margin="10px|20px|30px|40px|x|y|z"][/et_pb_blurb]'))

    def test_icon(self):
        for ok in ("&#xf0a9;||fa||900", "&#xe03b;||divi||400", "%%43%%"):
            self.assertEqual(found(f'[et_pb_blurb font_icon="{ok}"][/et_pb_blurb]', "error"), [], ok)
        self.assertIn(("error", "E_VALUE_FORMAT", "font_icon"), found('[et_pb_blurb font_icon="arrow"][/et_pb_blurb]'))

    def test_last_edited_and_state_toggle_formats(self):
        self.assertIn(("error", "E_VALUE_FORMAT", "title_font_size_last_edited"),
                      found('[et_pb_heading title_font_size_last_edited="yes"][/et_pb_heading]'))
        self.assertIn(("error", "E_VALUE_FORMAT", "title_text_color__hover_enabled"),
                      found('[et_pb_heading title_text_color__hover_enabled="true"][/et_pb_heading]'))

    def test_state_consistency_warnings(self):
        fs = found('[et_pb_heading title_text_color__hover="#000" title_font_size_tablet="30px"][/et_pb_heading]', "warning")
        self.assertIn(("warning", "W_HOVER_DISABLED", "title_text_color__hover"), fs)
        self.assertIn(("warning", "W_RESPONSIVE_DISABLED", "title_font_size_tablet"), fs)
        bg = found('[et_pb_blurb background_color__hover="#000" background__hover_enabled="on|hover"][/et_pb_blurb]', "warning")
        self.assertNotIn(("warning", "W_HOVER_DISABLED", "background_color__hover"), bg)

    def test_presets_and_external_images(self):
        fs = [(f.level, f.code) for f in validate_source(
            wrap('[et_pb_image _module_preset="5138c454-be54-4233-bd3b-f8e6a8747976" src="https://images.unsplash.com/x.jpg"][/et_pb_image]'),
            SCHEMA, site_url="https://client.example")]
        self.assertIn(("warning", "W_UNKNOWN_PRESET"), fs)
        self.assertIn(("warning", "W_EXTERNAL_IMAGE"), fs)

    def test_global_colors_info_must_be_json(self):
        self.assertIn(("error", "E_VALUE_FORMAT", "global_colors_info"),
                      found('[et_pb_text global_colors_info="{%22a%22:"][/et_pb_text]'))

    def test_third_party_shortcode_not_flagged(self):
        self.assertEqual(found('[et_pb_text]<p>[contact-form-7 id="5"]</p>[/et_pb_text]'), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_validate_values.py -v`
Expected: FAIL. The `E_UNKNOWN_ATTR` and value codes are never reported, because `check_attributes` doesn't exist yet.

- [ ] **Step 3: Implement the attribute and value checks**

`Skill/divi-page-builder/scripts/divi_checks_values.py`:
```python
"""Attribute-name and attribute-value rules for Divi 4 modules."""
from __future__ import annotations

import difflib
import json
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from divi_shortcode import wp_blanks_value

COLOR_RE = re.compile(r"^(#[0-9a-fA-F]{3,4}|#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8}|(?i:rgba?|hsla?)\([^)]*\)|transparent|gcid-[\w-]+|var\(--[\w-]+\))$")
NUMBER_UNIT_RE = re.compile(r"^(-?(?:\d+\.?\d*|\.\d+))([a-z%]*)$", re.I)
CSS_KEYWORDS = {"auto", "none", "inherit", "initial", "unset", "normal"}
GENERIC_UNITS = {"%", "em", "rem", "px", "cm", "mm", "in", "pt", "pc", "ex", "vh", "vw", "deg", "ms", "s", ""}
ICON_RE = re.compile(r"^(&#x[0-9a-fA-F]+;|&amp;#x[0-9a-fA-F]+;|[^|]*)\|\|(divi|fa)\|\|(\d{3})?$|^%%\d+%%$")
LAST_EDITED_RE = re.compile(r"^(on|off)\|(desktop|tablet|phone|hover|sticky)$")
STATE_TOGGLE_RE = re.compile(r"^(on|off)(\|\w+)?$")
SELECT_TYPES = {"select", "select_animation", "select-pattern", "select-mask", "text_align", "align", "position",
                "divider", "select_with_option_groups", "select_box_shadow", "presets_shadow", "yes_no_button"}
COLOR_TYPES = {"color", "color-alpha"}
LINE_STYLES = {"", "solid", "double", "dotted", "dashed", "wavy"}
IMAGE_ATTRS = ("src", "image", "background_image", "logo", "image_url", "portrait_url", "logo_image_url")

Problem = Tuple[str, str, str, str]  # (level, code, message, hint)


def normalize_color(value: str) -> str:
    v = value.strip().lower().replace(" ", "")
    if re.fullmatch(r"#[0-9a-f]{3}", v):
        v = "#" + "".join(c * 2 for c in v[1:])
    return v


def _length_ok(part: str, units) -> bool:
    if part == "" or part.lower() in CSS_KEYWORDS or part.startswith(("calc(", "var(", "clamp(", "min(", "max(")):
        return True
    m = NUMBER_UNIT_RE.match(part)
    return bool(m) and (m.group(2).lower() in (units or GENERIC_UNITS) or m.group(2) == "")


def value_problems(res, attr: str, value: str) -> List[Problem]:
    if value == "":
        return []
    if attr.endswith("_last_edited"):
        return [] if LAST_EDITED_RE.match(value) else [(
            "error", "E_VALUE_FORMAT", f"{attr} must look like 'on|phone' or 'off|desktop'", "")]
    if res.kind == "state_toggle":
        return [] if STATE_TOGGLE_RE.match(value) else [(
            "error", "E_VALUE_FORMAT", f"{attr} must be 'on|hover' / 'on|sticky' or 'off|desktop'", "")]
    field = res.field or {}
    ftype = field.get("type", "")
    if ftype == "global_colors_info":
        try:
            json.loads(value)
            return []
        except ValueError:
            return [("error", "E_VALUE_FORMAT", "global_colors_info must be JSON (escape \" as %22, [ as %91, ] as %93)", "")]
    options = field.get("options")
    if ftype in SELECT_TYPES and options:
        if value not in options:
            shown = ", ".join(options[:12]) + (" …" if len(options) > 12 else "")
            return [("error", "E_BAD_OPTION", f"'{value}' is not an option for {attr}", f"Options: {shown}")]
        return []
    if ftype == "multiple_buttons" and options:
        bad = [p for p in value.split("|") if p and p not in options]
        return [("error", "E_BAD_OPTION", f"{bad} not in options for {attr}", "Options: " + ", ".join(options))] if bad else []
    if ftype == "multiple_checkboxes" and options:
        parts = value.split("|")
        if len(parts) != len(options) or any(p not in ("on", "off", "") for p in parts):
            return [("error", "E_VALUE_FORMAT", f"{attr} needs {len(options)} on/off flags joined by '|' ({'|'.join(options)})", "")]
        return []
    if ftype == "range":
        if _length_ok(value, [u.lower() for u in field.get("units", [])] or None):
            return []
        m = NUMBER_UNIT_RE.match(value)
        code = "E_BAD_UNIT" if m else "E_VALUE_FORMAT"
        return [("error", code, f"'{value}' is not a valid length for {attr}",
                 "Allowed units: " + ", ".join(field.get("units", sorted(GENERIC_UNITS - {''}))))]
    if ftype in COLOR_TYPES:
        return [] if COLOR_RE.match(value.strip()) else [(
            "error", "E_VALUE_FORMAT", f"'{value}' is not a color", "Use #hex, rgba(), or a gcid- global color id.")]
    if ftype == "font":
        parts = value.split("|")
        if len(parts) > 9:
            return [("error", "E_VALUE_FORMAT", f"Font string has {len(parts)} parts; Divi uses 9",
                     "Family|weight|italic|uppercase|underline|smallcaps|strikethrough|line_color|line_style")]
        out: List[Problem] = []
        parts += [""] * (9 - len(parts))
        if parts[1] not in ("", "on", "off") and not re.fullmatch(r"[1-9]00", parts[1]):
            out.append(("warning", "W_FONT_WEIGHT", f"Font weight '{parts[1]}' is not 100–900", "Use 100…900, or leave empty."))
        if any(p not in ("", "on", "off") for p in parts[2:7]):
            out.append(("error", "E_VALUE_FORMAT", "Font style flags (parts 3–7) must be on, off or empty", ""))
        if parts[7] and not COLOR_RE.match(parts[7]):
            out.append(("error", "E_VALUE_FORMAT", "Font line color (part 8) must be a color", ""))
        if parts[8] not in LINE_STYLES:
            out.append(("error", "E_VALUE_FORMAT", f"Font line style must be one of {sorted(LINE_STYLES - {''})}", ""))
        return out
    if ftype in ("custom_margin", "custom_padding"):
        parts = value.split("|")
        units = [u.lower() for u in field.get("units", [])] or None
        if len(parts) > 6 or not all(_length_ok(p, units) for p in parts[:4]) or any(p not in ("", "true", "false") for p in parts[4:6]):
            return [("error", "E_VALUE_FORMAT", f"'{value}' is not a Divi spacing value",
                     "top|right|bottom|left|linked_top_bottom|linked_left_right, e.g. 80px||80px||true|false")]
        return []
    if ftype == "border-radius":
        parts = value.split("|")
        if len(parts) != 5 or parts[0] not in ("", "on", "off") or not all(_length_ok(p, None) for p in parts[1:]):
            return [("error", "E_VALUE_FORMAT", f"'{value}' is not a Divi border radius", "on|top-left|top-right|bottom-right|bottom-left")]
        return []
    if ftype == "select_icon":
        return [] if ICON_RE.match(value) else [(
            "error", "E_VALUE_FORMAT", f"'{value}' is not a Divi icon value", "e.g. &#xf0a9;||fa||900 or &#xe03b;||divi||400")]
    return []


def check_attributes(doc, schema, report, known_presets=frozenset(), site_host: Optional[str] = None) -> None:
    for node, path, _parent in doc.walk():
        mod = schema.module(node.tag)
        if mod is None:
            continue
        for name in node.duplicate_attrs:
            report("warning", "W_DUPLICATE_ATTR", f"'{name}' is set more than once; the last value wins", node=node, path=path, attr=name)
        for token in node.positional:
            report("error", "E_POSITIONAL_ATTR", f"Stray token {token!r} in the [{node.tag}] tag", node=node, path=path,
                   hint='Attributes must be name="value".')
        for name, raw in node.attrs.items():
            if node.quoting.get(name, '"') != '"':
                report("warning", "W_ATTR_QUOTING", f"{name} is not double-quoted", node=node, path=path, attr=name,
                       hint="Divi always writes name=\"value\".")
            if "[" in raw or "]" in raw:
                report("error", "E_RAW_BRACKET", f"{name} contains a raw [ or ]", node=node, path=path, attr=name, value=raw,
                       hint="Write [ as %91 and ] as %93.")
            if wp_blanks_value(raw):
                report("error", "E_ATTR_LT", f"WordPress will empty {name}: it contains a '<' that is not a complete tag",
                       node=node, path=path, attr=name, value=raw, hint="Rephrase without '<', or use &lt; in HTML content.")
            res = mod.resolve(name)
            if res is None:
                close = difflib.get_close_matches(name, mod.attribute_names(), n=1, cutoff=0.75)
                report("error", "E_UNKNOWN_ATTR", f"[{node.tag}] has no attribute '{name}'", node=node, path=path, attr=name,
                       value=raw, hint=f"did you mean '{close[0]}'?" if close else f"See reference/modules/{mod.slug}.md.")
                continue
            for level, code, message, hint in value_problems(res, name, node.value(name)):
                report(level, code, message, node=node, path=path, attr=name, value=raw, hint=hint)
            if site_host and name in IMAGE_ATTRS or site_host and name.endswith("_image") and node.value(name).startswith("http"):
                host = urlparse(node.value(name)).hostname
                if host and host != site_host:
                    report("warning", "W_EXTERNAL_IMAGE", f"{name} points to {host}, not the site", node=node, path=path,
                           attr=name, hint="Upload the image to the site's Media Library and use that URL.")
        for name in node.attrs:
            for state in ("hover", "sticky"):
                suffix = f"__{state}"
                if name.endswith(suffix):
                    base = name[: -len(suffix)]
                    key = "background" if base in ("background_color", "background_image") else base
                    if not node.value(f"{key}__{state}_enabled").startswith("on"):
                        report("warning", f"W_{state.upper()}_DISABLED",
                               f"{name} is ignored until {key}__{state}_enabled starts with 'on'", node=node, path=path, attr=name)
            for suffix in ("_tablet", "_phone"):
                if name.endswith(suffix) and mod.resolve(name) is not None:
                    base = name[: -len(suffix)]
                    if not node.value(f"{base}_last_edited").startswith("on"):
                        report("warning", "W_RESPONSIVE_DISABLED", f"{name} is ignored until {base}_last_edited starts with 'on'",
                               node=node, path=path, attr=name, hint=f'Add {base}_last_edited="on|phone".')
        preset = node.value("_module_preset")
        if preset and preset != "default" and preset not in known_presets:
            report("warning", "W_UNKNOWN_PRESET", f"_module_preset {preset} is not a preset known on this site",
                   node=node, path=path, attr="_module_preset",
                   hint="Use a preset UUID listed in tokens.json, or 'default' with inline styles.")
```

In `validate.py`, extend `validate_source`:
```python
from urllib.parse import urlparse
from divi_checks_values import check_attributes  # noqa: E402
# inside validate_source, after check_structure(...):
    known = {p["uuid"] for lst in (tokens or {}).get("presets", {}).values() for p in lst}
    host = urlparse(site_url or (tokens or {}).get("site", {}).get("url", "")).hostname
    check_attributes(doc, schema, report, known_presets=known, site_host=host)
```

- [ ] **Step 4: Run all validator tests**

Run: `python3 -m unittest tests/test_validate_values.py tests/test_validate_structure.py -v`
Expected: all PASS. Two likely failures:
- `test_units` fails for `max_width="none"`: check that `max_width`'s compact type is `range`, and that `none` is in `CSS_KEYWORDS`.
- `test_icon` fails: print `SCHEMA.module('et_pb_blurb').fields['font_icon']` to see the type. The check expects `select_icon`.

- [ ] **Step 5: Pin the Divi AI fixtures' error set**

Append this to `tests/test_validate_values.py`, inside `AttributeTest`:
```python
    def test_divi_ai_fixtures_only_have_known_stale_errors(self):
        from _paths import FIXTURES
        from test_divi_schema import KNOWN_STALE
        for path in (FIXTURES / "valid").glob("divi-ai-*.txt"):
            errors = [f for f in validate_source(path.read_text(), SCHEMA) if f.level == "error"]
            self.assertTrue(all(f.code == "E_UNKNOWN_ATTR" for f in errors), [(f.code, f.attr) for f in errors])
            self.assertTrue({(f.tag, f.attr) for f in errors} <= KNOWN_STALE)
```
Run: `python3 -m unittest tests/test_validate_values.py -v`
Expected: PASS. If another error code appears, decide which of two cases it is:
- **A validator bug:** fix the check.
- **A real defect in Divi AI's output:** record it in `research/tools/notes/divi-ai-defects.md` and add it to an explicit allow-list in this test, with a comment.

- [ ] **Step 6: Commit**

```bash
git add Skill/divi-page-builder/scripts/divi_checks_values.py Skill/divi-page-builder/scripts/validate.py tests/test_validate_values.py research/tools/notes 2>/dev/null
git commit -m "validator: attribute names, value formats, hover/responsive/preset/image checks"
```

---

### Task 6: Validator tokens checks, baseline mode, JSON output, performance

**Files:**
- Create: `Skill/divi-page-builder/scripts/divi_checks_tokens.py`
- Modify: `Skill/divi-page-builder/scripts/validate.py`
- Create: `tests/fixtures/tokens-min.json`
- Test: `tests/test_validate_cli.py`

**Interfaces:**
- Consumes: `normalize_color`, `COLOR_TYPES` (Task 5); the tokens schema from spec §4.10.
- Produces:
  - `divi_checks_tokens.check_tokens(doc, schema, tokens: dict, report) -> None`;
  - `validate.mark_preexisting(findings, baseline_findings) -> None`, which mutates `preexisting`.
- The minimal tokens keys this task relies on are `colors.global` (gcid → hex), `colors.customizer` (name → hex), `colors.palette` (list of `{hex, uses, roles}`), `typography.heading_font`, `typography.body_font`, `module_styles.*[].attrs`, `spacing.section_padding` (list of `[value, count]`), `presets` (slug → list of `{uuid, uses}`) and `site.url`.

- [ ] **Step 1: Write the minimal tokens fixture**

`tests/fixtures/tokens-min.json`:
```json
{
  "site": {"url": "https://client.example", "divi_version": "4.27.9", "source_pages": []},
  "colors": {
    "global": {"gcid-brand": "#0e7c86"},
    "customizer": {"accent": "#2ea3f2"},
    "palette": [{"hex": "#0b2a3c", "uses": 5, "roles": ["background_color"]},
                {"hex": "#ffffff", "uses": 9, "roles": ["title_text_color"]},
                {"hex": "#f97316", "uses": 4, "roles": ["button_bg_color"]}]
  },
  "typography": {"heading_font": "Montserrat", "body_font": "Lato", "scale": {}},
  "spacing": {"section_padding": [["96px||96px||true|false", 3]]},
  "presets": {"et_pb_button": [{"uuid": "11111111-2222-3333-4444-555555555555", "uses": 2}]},
  "module_styles": {},
  "section_exemplars": []
}
```

- [ ] **Step 2: Write the failing tests**

`tests/test_validate_cli.py`:
```python
import json
import subprocess
import sys
import time
import unittest

from _paths import FIXTURES, SCRIPTS
from divi_schema import load_schema
from validate import validate_source

SCHEMA = load_schema()
TOKENS = json.loads((FIXTURES / "tokens-min.json").read_text())


def section(inner, attrs=""):
    return f'[et_pb_section {attrs}][et_pb_row][et_pb_column type="4_4"]{inner}[/et_pb_column][/et_pb_row][/et_pb_section]'


class TokensTest(unittest.TestCase):
    def codes(self, src):
        return {f.code for f in validate_source(src, SCHEMA, tokens=TOKENS) if f.level == "warning"}

    def test_off_palette_color(self):
        self.assertIn("W_OFF_PALETTE_COLOR", self.codes(section('[et_pb_blurb icon_color="#123456"][/et_pb_blurb]')))
        self.assertNotIn("W_OFF_PALETTE_COLOR", self.codes(section('[et_pb_blurb icon_color="#F97316"][/et_pb_blurb]')))

    def test_unknown_global_color(self):
        self.assertIn("W_UNKNOWN_GLOBAL_COLOR", self.codes(section('[et_pb_blurb icon_color="gcid-other"][/et_pb_blurb]')))

    def test_off_brand_font(self):
        self.assertIn("W_OFF_BRAND_FONT", self.codes(section('[et_pb_heading title_font="Comic Sans MS|400|||||||"][/et_pb_heading]')))
        self.assertNotIn("W_OFF_BRAND_FONT", self.codes(section('[et_pb_heading title_font="Montserrat|700|||||||"][/et_pb_heading]')))

    def test_off_scale_section_padding(self):
        self.assertIn("W_OFF_SCALE_SPACING", self.codes(section("", 'custom_padding="13px||13px||true|false"')))

    def test_known_preset_is_not_warned(self):
        src = section('[et_pb_button _module_preset="11111111-2222-3333-4444-555555555555"][/et_pb_button]')
        self.assertNotIn("W_UNKNOWN_PRESET", self.codes(src))


class BaselineTest(unittest.TestCase):
    def test_baseline_marks_preexisting(self):
        legacy = section('[et_pb_cta text_font_size_tablet="16px"][/et_pb_cta]')
        edited = legacy + section('[et_pb_text bogus_attr="1"]<p>new</p>[/et_pb_text]')
        fs = validate_source(edited, SCHEMA, baseline=legacy)
        stale = [f for f in fs if f.attr == "text_font_size_tablet"]
        new = [f for f in fs if f.attr == "bogus_attr"]
        self.assertTrue(stale and all(f.preexisting for f in stale))
        self.assertTrue(new and not any(f.preexisting for f in new))


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), *args], capture_output=True, text=True)

    def test_exit_codes_and_json(self):
        good = self.run_cli(str(FIXTURES / "valid" / "handwritten-landing.txt"), "--json")
        self.assertEqual(good.returncode, 0, good.stdout)
        self.assertEqual(json.loads(good.stdout)["errors"], 0)
        bad_path = FIXTURES / "invalid" / "unknown-attr.txt"
        bad_path.write_text(section('[et_pb_text colour="red"]<p>x</p>[/et_pb_text]'))
        bad = self.run_cli(str(bad_path))
        self.assertEqual(bad.returncode, 1)
        self.assertIn("E_UNKNOWN_ATTR", bad.stdout)
        self.assertEqual(self.run_cli("/nonexistent.txt").returncode, 2)

    def test_large_page_performance(self):
        big = (FIXTURES / "valid" / "handwritten-landing.txt").read_text() * 60   # ≈ 200 KB, 1,000+ modules
        t0 = time.time()
        validate_source(big, SCHEMA, tokens=TOKENS)
        self.assertLess(time.time() - t0, 3.0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_validate_cli.py -v`
Expected: FAIL on the `TokensTest` and `BaselineTest` assertions.

- [ ] **Step 4: Implement the token checks**

`Skill/divi-page-builder/scripts/divi_checks_tokens.py`:
```python
"""Warn when a page uses colors, fonts or section spacing that are not part of the site's design tokens."""
from __future__ import annotations

from divi_checks_values import COLOR_TYPES, normalize_color


def _palette(tokens: dict) -> set:
    colors = tokens.get("colors", {})
    values = list(colors.get("global", {}).values()) + list(colors.get("customizer", {}).values())
    values += [p["hex"] for p in colors.get("palette", [])]
    return {normalize_color(v) for v in values if v}


def _fonts(tokens: dict) -> set:
    typo = tokens.get("typography", {})
    fonts = {typo.get("heading_font", ""), typo.get("body_font", "")}
    for level in typo.get("scale", {}).values():
        fonts.add((level.get("font") or "").split("|")[0])
    for entries in tokens.get("module_styles", {}).values():
        for entry in entries:
            for name, value in entry.get("attrs", {}).items():
                if name.endswith("_font"):
                    fonts.add(value.split("|")[0])
    return {f.lower() for f in fonts if f}


def check_tokens(doc, schema, tokens: dict, report) -> None:
    palette, fonts = _palette(tokens), _fonts(tokens)
    gcids = set(tokens.get("colors", {}).get("global", {}))
    paddings = {v for v, _ in tokens.get("spacing", {}).get("section_padding", [])}
    for node, path, _parent in doc.walk():
        mod = schema.module(node.tag)
        if mod is None:
            continue
        for name in node.attrs:
            res = mod.resolve(name)
            if res is None or not res.field:
                continue
            value = node.value(name)
            if not value:
                continue
            ftype = res.field.get("type")
            if ftype in COLOR_TYPES:
                color = normalize_color(value)
                if color.startswith("gcid-"):
                    if color not in gcids:
                        report("warning", "W_UNKNOWN_GLOBAL_COLOR", f"{name} uses global color {value}, which the site does not define",
                               node=node, path=path, attr=name, value=value)
                elif palette and color not in palette and color not in ("transparent", "rgba(0,0,0,0)", "rgba(255,255,255,0)"):
                    report("warning", "W_OFF_PALETTE_COLOR", f"{name}={value} is not in the site's palette",
                           node=node, path=path, attr=name, value=value, hint="Use a color from tokens.json colors.")
            elif ftype == "font" and fonts:
                family = value.split("|")[0]
                if family and family.lower() not in fonts:
                    report("warning", "W_OFF_BRAND_FONT", f"{name} uses '{family}', which the site does not use",
                           node=node, path=path, attr=name, value=value)
        if node.tag == "et_pb_section" and paddings and "custom_padding" in node.attrs:
            value = node.value("custom_padding")
            if value and value not in paddings:
                report("warning", "W_OFF_SCALE_SPACING", f"Section padding {value} is not one the site uses",
                       node=node, path=path, attr="custom_padding", value=value,
                       hint="Reuse a value from tokens.json spacing.section_padding.")
```

In `validate.py`, add token checks and baseline marking:
```python
from collections import Counter
from divi_checks_tokens import check_tokens  # noqa: E402


def mark_preexisting(findings, baseline_findings) -> None:
    pool = Counter((f.code, f.tag, f.attr, f.value) for f in baseline_findings)
    for f in findings:
        key = (f.code, f.tag, f.attr, f.value)
        if pool[key] > 0:
            pool[key] -= 1
            f.preexisting = True

# validate_source becomes:
def validate_source(source, schema, tokens=None, site_url=None, baseline=None):
    doc = parse(source)
    report = Reporter(doc)
    check_structure(doc, schema, report)
    known = {p["uuid"] for lst in (tokens or {}).get("presets", {}).values() for p in lst}
    host = urlparse(site_url or (tokens or {}).get("site", {}).get("url", "")).hostname
    check_attributes(doc, schema, report, known_presets=known, site_host=host)
    if tokens:
        check_tokens(doc, schema, tokens, report)
    if baseline is not None:
        mark_preexisting(report.findings, validate_source(baseline, schema, tokens=tokens, site_url=site_url))
    return report.findings
```

- [ ] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add Skill/divi-page-builder/scripts/divi_checks_tokens.py Skill/divi-page-builder/scripts/validate.py tests/fixtures/tokens-min.json tests/fixtures/invalid tests/test_validate_cli.py
git commit -m "validator: token checks, baseline mode for edits, JSON output, perf test"
```

---

### Task 7: Divi as judge: compare our parse with Divi's own parser

**Files:**
- Create: `research/tools/divi_parse.php`
- Create: `tests/fixtures/valid/unicode.txt`
- Test: `tests/test_divi_judge.py`

**Interfaces:**
- Consumes: `parse`, `Node.value`, `Document.walk` (Task 2); `research/tools/wp-local.sh` (Task 1).
- Produces:
  - `research/tools/divi_parse.php <file>`, which prints Divi's parse as JSON: `[{type, attrs, content, children}]`;
  - `research/tools/notes/escaping.md`, recording any value normalization Divi applies. Task 9's `page-format.md` consumes it.

- [ ] **Step 1: Write the judge script**

`research/tools/divi_parse.php`:
```php
<?php
/**
 * Print Divi's own parse of a shortcode file as JSON.
 *   research/tools/wp-local.sh --require=research/tools/force-all-modules.php eval-file research/tools/divi_parse.php <file>
 */
if ( ! did_action( 'et_builder_ready' ) ) {
	do_action( 'wp' );
}
$tree     = et_fb_process_shortcode( file_get_contents( $args[0] ) );
$simplify = function ( $items ) use ( &$simplify ) {
	$out = array();
	foreach ( (array) $items as $item ) {
		$content = isset( $item['content'] ) ? $item['content'] : '';
		$out[]   = array(
			'type'     => isset( $item['type'] ) ? $item['type'] : '',
			'attrs'    => isset( $item['attrs'] ) ? $item['attrs'] : array(),
			'content'  => is_array( $content ) ? '' : (string) $content,
			'children' => is_array( $content ) ? $simplify( $content ) : array(),
		);
	}
	return $out;
};
echo wp_json_encode( $simplify( $tree ), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
```

- [ ] **Step 2: Write the unicode fixture**

`tests/fixtures/valid/unicode.txt` (one line):
```
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Odontología en Miami — “sonrisa” %22real%22 %91VIP%93 & más 😀" title_level="h1" _builder_version="4.27.9" _module_preset="default"][/et_pb_heading][et_pb_text custom_css_main_element="content: %22a%92b%22;" _builder_version="4.27.9" _module_preset="default"]<p>Precio: $99 &amp; “garantía” — sin sorpresas.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

- [ ] **Step 3: Write the judge test**

It is skipped when the local site isn't reachable.

`tests/test_divi_judge.py`:
```python
import json
import subprocess
import unittest

from _paths import FIXTURES, TOOLS, WP_LOCAL
from divi_shortcode import parse


def divi_parse(path):
    out = subprocess.run([str(WP_LOCAL), f"--require={TOOLS / 'force-all-modules.php'}", "eval-file",
                          str(TOOLS / "divi_parse.php"), str(path)], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise unittest.SkipTest(f"local Divi site unavailable: {out.stderr[-300:]}")
    return json.loads(out.stdout[out.stdout.index("["):])


def flatten_divi(items):
    for item in items:
        yield item
        yield from flatten_divi(item["children"])


class DiviJudgeTest(unittest.TestCase):
    FILES = ["handwritten-landing.txt", "unicode.txt", "divi-ai-section.txt", "divi-ai-layout.txt"]

    def test_parse_agrees_with_divi(self):
        mismatches = []
        for name in self.FILES:
            path = FIXTURES / "valid" / name
            ours = [n for n, _, _ in parse(path.read_text()).walk()]
            theirs = list(flatten_divi(divi_parse(path)))
            self.assertEqual([n.tag for n in ours], [t["type"] for t in theirs], f"{name}: tree shape differs")
            for n, t in zip(ours, theirs):
                for attr in n.attrs:
                    if attr in t["attrs"] and t["attrs"][attr] != n.value(attr):
                        mismatches.append((name, n.tag, attr, n.value(attr), t["attrs"][attr]))
        self.assertEqual(mismatches, [], json.dumps(mismatches[:10], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run it, and turn every mismatch into a rule**

Run: `python3 -m unittest tests/test_divi_judge.py -v`
Expected: PASS, or a list of `(file, tag, attr, ours, divi)` mismatches. For each **class** of mismatch:
1. Find the Divi code responsible. Start with `includes/builder/functions.php:11542` (`%91` → `&#91;` for decoded content fields) and `class-et-builder-element.php:2284-2294`.
2. Record the rule, with a file:line reference, in `research/tools/notes/escaping.md`, as a row in `| attribute(s) | we read | Divi reads | why | source |`.
3. If the difference is a *Divi-side display normalization* (Divi changes the value, but writing the escaped form is still correct), normalize it in the test comparison with a helper `divi_normalize(attr, value)` that cites the source line.
4. If our `unescape_attr_value` is wrong, fix it in `divi_shortcode.py` and add a unit test in `tests/test_divi_shortcode.py`.

Re-run until the test passes.

- [ ] **Step 5: Commit**

```bash
git add research/tools/divi_parse.php research/tools/notes/escaping.md tests/fixtures/valid/unicode.txt tests/test_divi_judge.py Skill/divi-page-builder/scripts/divi_shortcode.py tests/test_divi_shortcode.py
git commit -m "tests: Divi-as-judge parse agreement + escaping notes"
```

---

### Task 8: Doc generator: module pages, family tables, coverage check

**Files:**
- Create: `research/tools/generate_docs.py`
- Create (generated): `Skill/divi-page-builder/reference/modules/*.md`, `Skill/divi-page-builder/reference/modules/README.md`
- Create: `Skill/divi-page-builder/reference/design-families.md` (skeleton with generated markers)
- Create: `research/tools/notes/et_pb_blurb.md` (the first gotchas note)
- Test: `tests/test_generate_docs.py`

**Interfaces:**
- Consumes: the raw schema (`research/divi-schema`), `load_schema`, `validate_source` (to check examples).
- Produces:
  - `generate_docs.classify(raw_modules: dict) -> tuple[dict, dict]`, returning `(placement, families)`:
    - `placement[slug][field] = ("module", toggle)` or `("family", family_id, prefix)`;
    - `families[family_id] = {"canonical": {canon_name: field_def}, "instances": int}`;
  - `generate_docs.render_module(slug, raw, placement, families, version) -> str`;
  - `generate_docs.minimal_example(slug, schema) -> str`, which returns a validator-clean page that contains the module;
  - `generate_docs.main(raw_dir, skill_dir, notes_dir) -> int`, returning 0 (or 1 on a coverage failure).
- Markers in `design-families.md`: `<!-- BEGIN GENERATED FAMILIES -->` … `<!-- END GENERATED FAMILIES -->`.

- [ ] **Step 1: Write the failing tests**

`tests/test_generate_docs.py`:
```python
import json
import tempfile
import unittest
from pathlib import Path

from _paths import RAW_SCHEMA
from divi_schema import load_schema
from generate_docs import classify, main, minimal_example
from validate import validate_source

RAW = {p.stem: json.loads(p.read_text()) for p in (RAW_SCHEMA / "modules").glob("*.json")}
SCHEMA = load_schema()


class GenerateDocsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.placement, cls.families = classify(RAW)

    def test_every_non_skip_field_is_placed(self):
        for slug, data in RAW.items():
            for name, f in data["fields"].items():
                if f.get("type") != "skip":
                    self.assertIn(name, self.placement[slug], f"{slug}.{name}")

    def test_font_family_uses_prefixes(self):
        self.assertEqual(self.placement["et_pb_blurb"]["header_font"][:3], ("family", "font", "header"))
        self.assertIn("{p}_font_size", self.families["font"]["canonical"])

    def test_module_specific_fields_stay_on_module(self):
        self.assertEqual(self.placement["et_pb_blurb"]["use_icon"][0], "module")
        self.assertEqual(self.placement["et_pb_blurb"]["custom_css_blurb_image"][0], "module")

    def test_minimal_examples_validate(self):
        for slug in SCHEMA.slugs:
            src = minimal_example(slug, SCHEMA)
            errors = [(f.code, f.attr) for f in validate_source(src, SCHEMA) if f.level == "error"]
            self.assertEqual(errors, [], f"{slug}: {src}")

    def test_main_writes_pages_and_passes_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / "reference").mkdir()
            (skill / "reference" / "design-families.md").write_text(
                "# Design families\n<!-- BEGIN GENERATED FAMILIES -->\n<!-- END GENERATED FAMILIES -->\n")
            self.assertEqual(main(RAW_SCHEMA, skill, None), 0)
            pages = list((skill / "reference" / "modules").glob("et_pb_*.md"))
            self.assertEqual(len(pages), 64)
            blurb = (skill / "reference" / "modules" / "et_pb_blurb.md").read_text()
            for needle in ("# Blurb — et_pb_blurb", "## Minimal valid example", "| use_icon |", "design-families.md#font"):
                self.assertIn(needle, blurb)
            fam = (skill / "reference" / "design-families.md").read_text()
            self.assertIn("## Font", fam)
            self.assertIn("{p}_font_size", fam)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_generate_docs.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'generate_docs'`

- [ ] **Step 3: Implement the generator**

`research/tools/generate_docs.py`:
```python
#!/usr/bin/env python3
"""Generate reference/modules/*.md and the design-family tables from the raw Divi schema dump.

Usage: generate_docs.py <raw_schema_dir> <skill_dir> [--notes <notes_dir>]
Exit 1 if any non-skip field would be left undocumented.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Skill" / "divi-page-builder" / "scripts"))
from divi_schema import load_schema  # noqa: E402
from validate import validate_source  # noqa: E402

FAMILY_TOGGLES = {
    "background": "background", "margin_padding": "spacing", "border": "border", "box_shadow": "box-shadow",
    "filters": "filters", "transform": "transform", "animation": "animation", "position_fields": "position",
    "scroll_effects": "scroll-effects", "visibility": "visibility", "hover_transitions": "transitions",
    "conditions": "display-conditions", "classes": "css-id-and-classes", "custom_css": "custom-css",
    "width": "sizing", "text": "text", "attributes": "attributes",
}
FAMILY_TITLES = {"font": "Font", "button": "Button", "background": "Background", "spacing": "Spacing",
                 "border": "Border", "box-shadow": "Box shadow", "filters": "Filters", "transform": "Transform",
                 "animation": "Animation", "position": "Position", "scroll-effects": "Scroll effects",
                 "visibility": "Visibility", "transitions": "Transitions", "display-conditions": "Display conditions",
                 "css-id-and-classes": "CSS ID & classes", "custom-css": "Custom CSS", "sizing": "Sizing",
                 "text": "Text", "attributes": "Attributes"}
MEMBERSHIP = 0.5          # canonical field must appear in ≥50% of a family's instances
TAB_TITLES = {"general": "Content tab", "advanced": "Design tab", "custom_css": "Advanced tab"}


def _real_fields(data):
    return {n: f for n, f in data["fields"].items() if f.get("type") != "skip"}


def _font_prefixes(fields):
    return {n[: -len("_font")]: f.get("toggle_slug") for n, f in fields.items() if f.get("type") == "font" and n.endswith("_font")}


def _button_prefixes(data):
    adv = data["module"].get("advanced_fields") or {}
    return list((adv.get("button") or {}).keys())


def _candidate(slug, data, name, f):
    toggle = f.get("toggle_slug") or ""
    for p, t in _font_prefixes(data["fields"]).items():
        if toggle == t and name.startswith(p + "_"):
            return ("font", p, "{p}" + name[len(p):])
    for p in _button_prefixes(data):
        if toggle == p and p in name:
            return ("button", p, name.replace(p, "{p}", 1))
    if toggle in FAMILY_TOGGLES:
        return (FAMILY_TOGGLES[toggle], "", name)
    return None


def classify(raw):
    counts = defaultdict(Counter)
    instances = defaultdict(set)
    candidates = {}
    for slug, data in raw.items():
        for name, f in _real_fields(data).items():
            cand = _candidate(slug, data, name, f)
            candidates[(slug, name)] = cand
            if cand:
                fam, prefix, canon = cand
                counts[fam][canon] += 1
                instances[fam].add((slug, prefix))
    families = {}
    for fam, counter in counts.items():
        n = len(instances[fam])
        families[fam] = {"canonical": {}, "instances": n}
        for canon, c in counter.items():
            if c >= MEMBERSHIP * n:
                families[fam]["canonical"][canon] = None
    placement = {}
    for slug, data in raw.items():
        placement[slug] = {}
        for name, f in _real_fields(data).items():
            cand = candidates[(slug, name)]
            if cand and cand[2] in families[cand[0]]["canonical"]:
                placement[slug][name] = ("family", cand[0], cand[1])
                if families[cand[0]]["canonical"][cand[2]] is None:
                    families[cand[0]]["canonical"][cand[2]] = f
            else:
                placement[slug][name] = ("module", f.get("toggle_slug") or "")
    return placement, families


def _flags(f):
    return " ".join(x for x, k in (("R", "mobile_options"), ("H", "hover"), ("S", "sticky")) if f.get(k)) or "·"


def _values(f):
    opts = f.get("options")
    if isinstance(opts, dict) and opts:
        keys = [str(k) for k in opts][:15]
        return ", ".join(f"`{k}`" for k in keys) + (" …" if len(opts) > 15 else "")
    if isinstance(opts, list) and opts:
        return ", ".join(f"`{o}`" for o in opts[:15])
    if f.get("allowed_units"):
        return "length: " + ", ".join(f.get("allowed_units")[:6]) + ("…" if len(f["allowed_units"]) > 6 else "")
    return {"color-alpha": "color", "font": "font string", "custom_margin": "spacing string",
            "custom_padding": "spacing string", "select_icon": "icon string", "upload": "URL",
            "tiny_mce": "HTML (between the tags)", "border-radius": "radius string"}.get(f.get("type"), "")


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def _field_row(name, f):
    default = f.get("default", f.get("default_on_front", ""))
    return f"| {_cell(name)} | {_cell(f.get('type', ''))} | {_cell(_values(f))} | {_cell(default)} | {_flags(f)} | {_cell(f.get('label', ''))} |"


HEADER = "| attribute | type | values | default | R H S | label |\n|---|---|---|---|---|---|"


def minimal_example(slug, schema):
    mod = schema.module(slug)
    base = '_builder_version="%s" _module_preset="default"' % schema.divi_version
    def content_for(tag):
        m = schema.module(tag)
        return "<p>Example text.</p>" if m and m.fields.get("content", {}).get("type") == "tiny_mce" else ""

    content = content_for(slug)

    def leaf(tag):
        return f"[{tag} {base}]{content_for(tag)}[/{tag}]"

    def in_column(inner):
        return (f"[et_pb_section {base}][et_pb_row {base}][et_pb_column type=\"4_4\" {base}]"
                f"{inner}[/et_pb_column][/et_pb_row][/et_pb_section]")

    if slug == "et_pb_section":
        return in_column("")
    if slug in ("et_pb_row", "et_pb_column"):
        return in_column("")
    if slug in ("et_pb_row_inner", "et_pb_column_inner"):
        return (f"[et_pb_section specialty=\"on\" {base}][et_pb_column type=\"1_4\" {base}][/et_pb_column]"
                f"[et_pb_column type=\"3_4\" specialty_columns=\"3\" {base}][et_pb_row_inner {base}]"
                f"[et_pb_column_inner type=\"4_4\" saved_specialty_column_type=\"3_4\" {base}][/et_pb_column_inner]"
                f"[/et_pb_row_inner][/et_pb_column][/et_pb_section]")
    if mod.kind == "child":
        parent = schema.module(mod.parents[0])
        inner = f"[{mod.parents[0]} {base}]{leaf(slug)}[/{mod.parents[0]}]"
        return f"[et_pb_section fullwidth=\"on\" {base}]{inner}[/et_pb_section]" if parent.fullwidth else in_column(inner)
    body = f"[{slug} {base}]{leaf(mod.child) if mod.child else content}[/{slug}]"
    return f"[et_pb_section fullwidth=\"on\" {base}]{body}[/et_pb_section]" if mod.fullwidth else in_column(body)


def render_module(slug, raw, placement, families, schema, notes_dir):
    data = raw[slug]
    meta = data["module"]
    mod = schema.module(slug)
    fields = _real_fields(data)
    lines = [f"# {meta['name']} — {slug}", ""]
    rel = "structure element" if mod.kind == "structure" else mod.kind
    parents = ", ".join(f"`{p}`" for p in mod.parents) or ("fullwidth section" if mod.fullwidth else "column" if mod.kind == "module" else "—")
    lines += [f"- **Kind:** {rel}", f"- **Goes inside:** {parents}",
              f"- **Children:** {'`' + mod.child + '`' if mod.child else 'none'}",
              f"- **CSS selector:** `{meta.get('main_css_element') or ''}`", "",
              "## Minimal valid example", "", "```divi", minimal_example(slug, schema), "```", ""]
    by_tab = defaultdict(lambda: defaultdict(list))
    fam_use = defaultdict(set)
    for name, f in fields.items():
        place = placement[slug][name]
        if place[0] == "module":
            by_tab[f.get("tab_slug") or "general"][place[1]].append((name, f))
        else:
            fam_use[place[1]].add(place[2])
    toggles = meta.get("settings_modal_toggles") or {}
    for tab in ("general", "advanced", "custom_css"):
        if not by_tab.get(tab):
            continue
        lines += [f"## {TAB_TITLES[tab]}", ""]
        labels = (toggles.get(tab) or {}).get("toggles") or {}
        for toggle, rows in by_tab[tab].items():
            label = labels.get(toggle)
            title = label.get("title") if isinstance(label, dict) else label
            lines += [f"### {title or toggle or 'Other'} — `{toggle or '-'}`", "", HEADER]
            lines += [_field_row(n, f) for n, f in sorted(rows)]
            lines.append("")
    if fam_use:
        lines += ["## Shared design families", "", "| family | prefix(es) | reference |", "|---|---|---|"]
        for fam in sorted(fam_use):
            prefixes = ", ".join(f"`{p}_`" for p in sorted(fam_use[fam]) if p) or "(none)"
            lines.append(f"| {FAMILY_TITLES.get(fam, fam)} | {prefixes} | [design-families.md#{fam}](../design-families.md#{fam}) |")
        lines.append("")
    note = notes_dir / f"{slug}.md" if notes_dir else None
    if note and note.exists():
        lines += ["## Gotchas", "", note.read_text().strip(), ""]
    lines += ["R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). "
              "See [value-formats.md](../value-formats.md)."]
    return "\n".join(lines) + "\n"


def render_families(families):
    out = []
    for fam in sorted(families, key=lambda k: FAMILY_TITLES.get(k, k)):
        canon = {k: v for k, v in families[fam]["canonical"].items() if v}
        out += [f"## {FAMILY_TITLES.get(fam, fam)}", f'<a id="{fam}"></a>', "",
                f"Used by {families[fam]['instances']} module/prefix combinations. `{{p}}` = the prefix listed on each module page.", "",
                HEADER]
        out += [_field_row(n, f) for n, f in sorted(canon.items())]
        out.append("")
    return "\n".join(out)


def main(raw_dir, skill_dir, notes_dir):
    raw_dir, skill_dir = Path(raw_dir), Path(skill_dir)
    notes_dir = Path(notes_dir) if notes_dir else None
    raw = {p.stem: json.loads(p.read_text()) for p in (raw_dir / "modules").glob("*.json")}
    schema = load_schema()
    placement, families = classify(raw)
    missing = [(s, n) for s, d in raw.items() for n in _real_fields(d) if n not in placement[s]]
    if missing:
        print("UNDOCUMENTED FIELDS:", missing[:20], file=sys.stderr)
        return 1
    out = skill_dir / "reference" / "modules"
    out.mkdir(parents=True, exist_ok=True)
    rows = ["# Module index", "", "| slug | name | kind | goes inside | children | fields |", "|---|---|---|---|---|---|"]
    for slug in sorted(raw):
        example = minimal_example(slug, schema)
        errors = [f for f in validate_source(example, schema) if f.level == "error"]
        if errors:
            print(f"{slug}: example fails validation: {[(e.code, e.attr) for e in errors]}", file=sys.stderr)
            return 1
        (out / f"{slug}.md").write_text(render_module(slug, raw, placement, families, schema, notes_dir))
        mod = schema.module(slug)
        rows.append(f"| [{slug}]({slug}.md) | {raw[slug]['module']['name']} | {mod.kind} | "
                    f"{', '.join(mod.parents) or ('fullwidth section' if mod.fullwidth else 'column')} | {mod.child or ''} | {len(_real_fields(raw[slug]))} |")
    (out / "README.md").write_text("\n".join(rows) + "\n")
    fam_path = skill_dir / "reference" / "design-families.md"
    text = fam_path.read_text()
    begin, end = "<!-- BEGIN GENERATED FAMILIES -->", "<!-- END GENERATED FAMILIES -->"
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    fam_path.write_text(head + begin + "\n" + render_families(families) + "\n" + end + tail)
    print(f"wrote {len(raw)} module pages, {len(families)} families")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_dir")
    ap.add_argument("skill_dir")
    ap.add_argument("--notes")
    a = ap.parse_args()
    sys.exit(main(a.raw_dir, a.skill_dir, a.notes))
```

- [ ] **Step 4: Create the `design-families.md` skeleton and the first note**

`Skill/divi-page-builder/reference/design-families.md`:
```markdown
# Design families

Most Divi modules share the same groups of design options. Each group is documented once here.
Field names use `{p}` for a module-specific prefix. For example, the Font family's `{p}_font_size` becomes
`header_font_size`, `body_font_size` or `button_font_size` depending on the module; each module page lists its prefixes.

Columns: **R** responsive (`_tablet`/`_phone` + `_last_edited`), **H** hover (`__hover` + `__hover_enabled`),
**S** sticky (`__sticky` + `__sticky_enabled`). Value grammars are in [value-formats.md](value-formats.md).

<!-- BEGIN GENERATED FAMILIES -->
<!-- END GENERATED FAMILIES -->
```

`research/tools/notes/et_pb_blurb.md`:
```markdown
- `use_icon="on"` shows `font_icon`; `use_icon="off"` shows `image`. Set only the one you use.
- The title's heading level is `header_level` (default `h4`); in a services grid use `h3` under an `h2` section heading.
- `icon_placement="top"|"left"` changes the layout; `left` suits compact feature lists.
```

- [ ] **Step 5: Run the generator and the tests**

Run:
```bash
python3 research/tools/generate_docs.py research/divi-schema Skill/divi-page-builder --notes research/tools/notes
python3 -m unittest tests/test_generate_docs.py -v
```
Expected: `wrote 64 module pages, N families`, then all PASS.

If a minimal example fails validation, the error names the module and the attribute. Fix `minimal_example` for that module kind. Never weaken the validator to make an example pass.

- [ ] **Step 6: Spot-check three pages by reading them**

Open `reference/modules/et_pb_blurb.md`, `et_pb_section.md` and `et_pb_fullwidth_header.md`, and confirm:
- the tables render;
- the toggle titles are human-readable;
- the family links resolve to anchors in `design-families.md`.

Fix the formatting in `render_module` if needed and re-run.

- [ ] **Step 7: Commit**

```bash
git add research/tools/generate_docs.py research/tools/notes Skill/divi-page-builder/reference tests/test_generate_docs.py
git commit -m "docs: generated module reference pages + design family tables with coverage check"
```

---

### Task 9: Hand-written references: page format, structure, value formats

**Files:**
- Create: `Skill/divi-page-builder/reference/page-format.md`, `reference/structure.md`, `reference/value-formats.md`
- Modify: `Skill/divi-page-builder/reference/design-families.md` (prose above the generated block only)
- Create: `research/tools/check_doc_examples.py`
- Test: `tests/test_doc_examples.py`

**Interfaces:**
- Consumes: `research/tools/notes/escaping.md` (Task 7), `validate_source` (Tasks 4-6), and the local site via `wp-local.sh`.
- Produces:
  - the convention that **every fenced code block tagged `divi`** in `reference/` and `recipes/` must be a complete page that passes the validator with 0 errors;
  - blocks tagged `divi-fragment` are exempt, for partial snippets;
  - `check_doc_examples.py <skill_dir>`, which prints failures and exits 1.

- [ ] **Step 1: Write the example checker and its test**

`research/tools/check_doc_examples.py`:
```python
#!/usr/bin/env python3
"""Validate every ```divi fenced block in the skill's Markdown. Usage: check_doc_examples.py <skill_dir>"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Skill" / "divi-page-builder" / "scripts"))
from divi_schema import load_schema  # noqa: E402
from validate import validate_source  # noqa: E402

BLOCK_RE = re.compile(r"^```divi\n(.*?)^```", re.S | re.M)


def check(skill_dir: Path):
    schema = load_schema()
    failures = []
    for md in sorted(skill_dir.rglob("*.md")):
        for i, m in enumerate(BLOCK_RE.finditer(md.read_text())):
            errors = [f for f in validate_source(m.group(1).strip(), schema) if f.level == "error"]
            if errors:
                failures.append((md.relative_to(skill_dir), i, [(e.code, e.attr, e.message) for e in errors[:5]]))
    return failures


if __name__ == "__main__":
    fails = check(Path(sys.argv[1]))
    for path, i, errs in fails:
        print(f"{path} block {i}: {errs}")
    print(f"{len(fails)} failing block(s)")
    sys.exit(1 if fails else 0)
```

`tests/test_doc_examples.py`:
```python
import unittest

from _paths import SKILL
from check_doc_examples import check


class DocExamplesTest(unittest.TestCase):
    def test_all_divi_blocks_validate(self):
        self.assertEqual(check(SKILL), [])


if __name__ == "__main__":
    unittest.main()
```
Run: `python3 -m unittest tests/test_doc_examples.py -v`
Expected: PASS (the generated module pages' examples are valid).

- [ ] **Step 2: Run the experiments these docs depend on**

Record each result in `research/tools/notes/doc-experiments.md`: the command, what you observed, and the conclusion. The experiments are:
1. **Custom CSS newlines.** Run `grep -n "||" "$DIVI/includes/builder/class-et-builder-element.php" | grep -i "custom_css\|\\\\n"` and find how multi-line `custom_css_*` values are stored. The expected answer is that newlines are saved as `||`; confirm it from the code, citing the file and line.
2. **The `<` rule.** Create a page with `wp-local.sh post create` containing `[et_pb_heading title="a < b"]`. `curl` it and confirm the heading renders empty, which confirms `E_ATTR_LT`. Delete the page.
3. **Global colors.** Run `grep -rn "gcid-" "$DIVI/includes/builder" --include=*.php | head` and document:
   - how `gcid-…` values in attributes resolve to colors;
   - how `global_colors_info` is shaped (`{"gcid-x":["attr",…]}`, escaped).
4. **Section types.** Confirm the `fullwidth="on"` and `specialty="on"` rules by rendering `tests/fixtures/valid/handwritten-landing.txt` as a `Plan Test:` page and checking the HTML for `et_pb_fullwidth_section` and `et_section_specialty`. Delete the page.
5. **Legal specialty layouts.** Run `grep -o "specialty[^,]*columns[^}]*" "$DIVI/includes/builder/frontend-builder/build/bundle.js" | head` and record the column arrangements and the `specialty_columns` value for each.

- [ ] **Step 3: Write `reference/page-format.md`**

Required sections, in order:
1. *What Divi stores*: `post_content` is a shortcode string, answered directly as "not JSON, not serialized PHP". Explain where JSON appears (builder transit, portability export `{"context":"et_builder","data":{…}}`) and where serialized PHP appears (the `et_divi` and `et_divi_builder_global_presets_ng` options).
2. *Grammar*: tags, `name="value"` always double-quoted, enclosing vs self-closing, and inner content as HTML for text-bearing modules. Include a ```divi example.
3. *Escaping*: a table built from `research/tools/notes/escaping.md` and experiment 1: `"`, `[`, `]`, `\`, `<`, and newlines in `custom_css_*`. Give a correct and an incorrect example for each.
4. *Bookkeeping attributes*: `_builder_version` (use the site's Divi version from `tokens.json`), `_module_preset` (`default` unless reusing a site preset), `global_colors_info`, `admin_label`, `fb_built`, `locked`, `collapsed`.
5. *Post meta*: `_et_pb_use_builder=on` (required), `_et_pb_page_layout`, `_et_pb_old_content`, `_et_pb_built_for_post_type`.
6. *What never to write*: preset UUIDs that aren't in `tokens.json`, Divi 5 block markup, and `<!-- wp:… -->` comments.

- [ ] **Step 4: Write `reference/structure.md`**

Required sections:
1. The nesting diagram (section → row → column → module).
2. Regular, fullwidth and specialty sections, each with a ```divi example; use experiment 5 for specialty.
3. A table of every `column_structure` value for `et_pb_row` (20 values) and `et_pb_row_inner` (4 values), with the matching column `type` list.
4. Parent → child pairs, generated from the schema: `python3 -c "from divi_schema import load_schema; s=load_schema(); print([(x, s.module(x).child) for x in s.slugs if s.module(x).child])"` run with `PYTHONPATH=Skill/divi-page-builder/scripts`. Paste the table.
5. Fullwidth-only modules (the `fullwidth: true` list).
6. Module numbering (`et_pb_text_0`, `_1`, …): assigned at render time and never stored, so custom CSS should target `module_class` instead.
7. Every structural validator code (`E_SECTION_CHILD` … `W_COLUMN_STRUCTURE_MISMATCH`), with a one-line fix for each.

- [ ] **Step 5: Write `reference/value-formats.md`**

One `##` per format, each with grammar, a valid example, a common mistake and which field types use it:
- colors (hex, rgba, `gcid-`, `global_colors_info`, using experiment 3);
- lengths and units, with keywords;
- the 9-part font string, with a table of the parts;
- spacing (6 parts);
- border radius (5 parts);
- yes/no;
- selects;
- `multiple_buttons`;
- `multiple_checkboxes` (positional);
- icons (`&#x…;||fa||900`, `||divi||400`, legacy `%%N%%`);
- uploads and URLs;
- gradient stops;
- box-shadow presets;
- animation;
- transform (composite sub-attributes such as `transform_scale`);
- scroll effects;
- display conditions;
- **responsive** (`_tablet`, `_phone`, `_last_edited="on|phone"`);
- **hover** (`__hover` + `__hover_enabled="on|hover"`, with the background group key);
- **sticky**.

Every value example must pass `validate.py` inside a complete ```divi block, or use ```divi-fragment.

- [ ] **Step 6: Add the family prose to `design-families.md`**

Above the generated block, add a short `##` per family: when to use it, and one ```divi-fragment example. Don't touch the content between the markers.

- [ ] **Step 7: Verify and commit**

Run:
```bash
python3 research/tools/generate_docs.py research/divi-schema Skill/divi-page-builder --notes research/tools/notes
python3 research/tools/check_doc_examples.py Skill/divi-page-builder
python3 -m unittest discover -s tests -v
```
Expected: `0 failing block(s)`, and all tests PASS.

```bash
git add Skill/divi-page-builder/reference research/tools/check_doc_examples.py research/tools/notes tests/test_doc_examples.py
git commit -m "docs: page format, structure, value formats references (experiment-backed)"
```

---

### Task 10: Publishing: verify the REST flow live, then write `publishing.md`

**Files:**
- Create: `Skill/divi-page-builder/reference/publishing.md`
- Create: `research/tools/notes/rest-experiments.md`

**Interfaces:**
- Consumes: `wp-local.sh` and `tests/fixtures/valid/handwritten-landing.txt`.
- Produces: the documented request sequence that Task 15's `push_local.sh` and the future connection phase implement.

- [ ] **Step 1: Create a test Application Password on the local site**

```bash
research/tools/wp-local.sh eval 'var_dump( wp_is_application_passwords_available() );'
ADMIN=$(research/tools/wp-local.sh user list --role=administrator --field=user_login | head -1)
export WP_USER="$ADMIN"
export WP_APP_PASSWORD="$(research/tools/wp-local.sh user application-password create "$ADMIN" plan-test --porcelain)"
```
Expected: `bool(true)`, and the password stored in the environment only. If the result is `false` because the site is plain HTTP, run `research/tools/wp-local.sh config set WP_ENVIRONMENT_TYPE local --type=constant` (LocalWP normally sets it) and retry.

- [ ] **Step 2: Create a draft over REST and read it back**

```bash
SITE=http://divi-test.local
python3 - <<'EOF' > /tmp/pp-body.json
import json; print(json.dumps({"title": "Plan Test: REST create", "status": "draft",
  "content": open("tests/fixtures/valid/handwritten-landing.txt").read(), "meta": {"_et_pb_use_builder": "on"}}))
EOF
curl -s -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' -d @/tmp/pp-body.json "$SITE/wp-json/wp/v2/pages" > /tmp/pp-created.json
ID=$(python3 -c "import json;print(json.load(open('/tmp/pp-created.json'))['id'])")
curl -s -u "$WP_USER:$WP_APP_PASSWORD" "$SITE/wp-json/wp/v2/pages/$ID?context=edit" > /tmp/pp-read.json
python3 - <<EOF
import json
sent = open("tests/fixtures/valid/handwritten-landing.txt").read()
got = json.load(open("/tmp/pp-read.json"))
print("roundtrip identical:", got["content"]["raw"] == sent, "| meta:", got["meta"].get("_et_pb_use_builder"), "| link:", got["link"])
EOF
```
Expected: `roundtrip identical: True | meta: on`. If the round-trip isn't identical, diff the strings with `difflib.unified_diff` and record exactly which characters WordPress changed in `rest-experiments.md`. That finding goes into `publishing.md` and `page-format.md`.

- [ ] **Step 3: Settle the three open questions**

Record each answer in `research/tools/notes/rest-experiments.md`.
1. **CSS cache.** `curl "$SITE/?page_id=$ID&preview=true"` won't work without a cookie, so publish temporarily instead: `curl -X POST -u … -d '{"status":"publish"}' …/pages/$ID`. Then `curl` the page once, and `ls ~/Local\ Sites/divi-test/app/public/wp-content/et-cache/$ID/`. Next, update the content over REST (change one heading), and check whether the `et-cache/$ID` files were deleted or changed and whether the new `curl` shows the new CSS.
2. **Layout without a sidebar.** Check the body class of the published page (`curl … | grep -o 'et_[a-z_]*sidebar'`). Then try:
   - `{"template": "page-template-blank.php"}`;
   - `research/tools/wp-local.sh post meta update $ID _et_pb_page_layout et_no_sidebar`;
   - and whether `_et_pb_page_layout` in the REST `meta` is rejected.

   Record which method produces `et_no_sidebar` or `et_full_width_page`.
3. **Entities.** Send `tests/fixtures/valid/unicode.txt` through the same create flow and compare `content.raw` with the file.

- [ ] **Step 4: Clean up**

```bash
curl -s -X DELETE -u "$WP_USER:$WP_APP_PASSWORD" "$SITE/wp-json/wp/v2/pages/$ID?force=true" > /dev/null
research/tools/wp-local.sh user application-password delete "$WP_USER" "$(research/tools/wp-local.sh user application-password list "$WP_USER" --name=plan-test --field=uuid)"
unset WP_APP_PASSWORD
```
Expected: no `Plan Test:` pages remain (`research/tools/wp-local.sh post list --post_type=page --s="Plan Test" --format=count` prints `0`).

- [ ] **Step 5: Write `reference/publishing.md`**

Required sections, all based on the recorded experiments:
1. **Auth.** Application Passwords (Users → Profile), Basic auth, HTTPS required on live sites, the environment variables `WP_USER` and `WP_APP_PASSWORD`, and never pasting secrets into chat or files.
2. **Upload images.** `POST /wp/v2/media` with `Content-Disposition: attachment; filename="x.jpg"` and a binary body, then set `alt_text` with `POST /wp/v2/media/<id>`. Use `source_url` in the shortcode.
3. **Create a draft.** The exact request body, with `meta._et_pb_use_builder`, plus the layout method found in Step 3.
4. **Preview.** `link` + `&preview=true`, visible to logged-in users. The WordPress draft is the authoritative visual check.
5. **Publish.**
6. **Edit an existing page.** `GET ?context=edit` → save `original.txt` → edit → `validate.py --baseline original.txt` → `POST` the update.
7. **CSS cache behavior,** from experiment 1.
8. **Troubleshooting** for 401, 403 (`rest_cannot_edit`), and content altered on save (list the characters found in Step 2/3).

Include complete `curl` examples. Passwords appear only as `$WP_APP_PASSWORD`.

- [ ] **Step 6: Commit**

```bash
git add Skill/divi-page-builder/reference/publishing.md research/tools/notes/rest-experiments.md
git commit -m "docs: publishing over REST, verified live (create/read/update/cache/layout)"
```

---

### Task 11: Tokens from shortcode

**Files:**
- Create: `Skill/divi-page-builder/scripts/tokens_from_shortcode.py`
- Test: `tests/test_tokens_from_shortcode.py`

**Interfaces:**
- Consumes: `parse`, `Document.walk`, `Node.value` (Task 2); `load_schema` / `ModuleSchema.resolve` (Task 3); `normalize_color`, `COLOR_TYPES` (Task 5).
- Produces:
  - `is_design_attr(mod, name) -> bool`;
  - `tokens_from_documents(docs: list[Document], schema) -> dict`, which returns the keys `colors.palette`, `typography`, `spacing`, `shapes`, `presets`, `module_styles` and `section_exemplars` from spec §4.10. `module_styles[slug]` is a list of `{uses, attrs, preset, module_class, module_id, custom_css, contexts: [{section_index, section_label, section_tone, section_background, column_type}]}`, sorted by `uses` descending.

- [ ] **Step 1: Write the failing tests**

`tests/test_tokens_from_shortcode.py`:
```python
import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from divi_shortcode import parse
from tokens_from_shortcode import is_design_attr, tokens_from_documents

SCHEMA = load_schema()
SRC = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()


class TokensFromShortcodeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = tokens_from_documents([parse(SRC)], SCHEMA)

    def test_design_vs_content(self):
        heading = SCHEMA.module("et_pb_heading")
        self.assertTrue(is_design_attr(heading, "title_font"))
        self.assertTrue(is_design_attr(heading, "title_font_size_tablet"))
        self.assertFalse(is_design_attr(heading, "title"))
        self.assertTrue(is_design_attr(SCHEMA.module("et_pb_section"), "background_color"))
        self.assertFalse(is_design_attr(SCHEMA.module("et_pb_button"), "button_url"))

    def test_button_style_captured_with_context(self):
        (btn,) = self.t["module_styles"]["et_pb_button"]
        self.assertEqual(btn["uses"], 1)
        self.assertEqual(btn["attrs"]["button_bg_color"], "#f97316")
        self.assertNotIn("button_text", btn["attrs"])
        ctx = btn["contexts"][0]
        self.assertEqual(ctx["section_label"], "Hero")
        self.assertEqual(ctx["section_tone"], "dark")
        self.assertEqual(ctx["column_type"], "1_2")

    def test_identical_styles_are_grouped(self):
        blurbs = self.t["module_styles"]["et_pb_blurb"]
        self.assertEqual(len(blurbs), 1)
        self.assertEqual(blurbs[0]["uses"], 3)

    def test_typography_scale(self):
        h1 = self.t["typography"]["scale"]["h1"]
        self.assertEqual(h1["font"], "Montserrat|700|||||||")
        self.assertEqual(h1["size"], "56px")
        self.assertEqual(h1["size_tablet"], "42px")
        self.assertEqual(self.t["typography"]["heading_font"], "Montserrat")
        self.assertEqual(self.t["typography"]["body_font"], "Lato")

    def test_palette_spacing_presets(self):
        hexes = {p["hex"] for p in self.t["colors"]["palette"]}
        self.assertTrue({"#0b2a3c", "#f97316", "#ffffff"} <= hexes)
        self.assertIn(["96px||96px||true|false", 1], self.t["spacing"]["section_padding"])
        self.assertEqual(self.t["presets"], {})

    def test_section_exemplars_strip_content(self):
        hero = self.t["section_exemplars"][0]
        self.assertEqual(hero["tag"], "et_pb_section")
        self.assertEqual(hero["attrs"]["admin_label"], "Hero")
        flat = repr(hero)
        self.assertNotIn("Emergency Plumber in Miami", flat)
        self.assertNotIn("plumber.jpg", flat)
        self.assertIn("title_font_size", flat)

    def test_presets_counted(self):
        src = SRC.replace('[et_pb_button button_text', '[et_pb_button _module_preset="aaaa-bbbb" button_text', 1)
        t = tokens_from_documents([parse(src)], SCHEMA)
        self.assertEqual(t["presets"]["et_pb_button"], [{"uuid": "aaaa-bbbb", "uses": 1}])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_tokens_from_shortcode.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tokens_from_shortcode'`

- [ ] **Step 3: Implement**

`Skill/divi-page-builder/scripts/tokens_from_shortcode.py`:
```python
"""Derive design tokens from Divi page shortcode: style bundles per module, typography scale, palette,
spacing, shapes, presets and design-only section skeletons."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from typing import List

from divi_checks_values import COLOR_TYPES, normalize_color
from divi_shortcode import Node

STRUCTURAL_ATTRS = {"column_structure", "type", "fullwidth", "specialty", "specialty_columns",
                    "saved_specialty_column_type", "admin_label"}
LEVEL_FIELDS = ("title_level", "header_level", "toggle_level")
BOOKKEEPING = {"_builder_version", "_module_preset", "global_colors_info", "locked", "collapsed", "fb_built",
               "template_type", "_dynamic_attributes", "hover_enabled"}


def is_design_attr(mod, name: str) -> bool:
    if name in BOOKKEEPING or name.startswith("custom_css_") or name in ("module_class", "module_id"):
        return False
    res = mod.resolve(name)
    if res is None or res.kind in ("global", "extra"):
        return False
    if res.kind in ("state_toggle", "bg_enable"):
        return True
    field = res.field or {}
    return field.get("tab") == "advanced" or field.get("toggle") == "background"


def _luminance(color: str):
    c = normalize_color(color)
    m = re.fullmatch(r"#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})?", c)
    if not m:
        m2 = re.fullmatch(r"rgba?\((\d+),(\d+),(\d+)(?:,[\d.]+)?\)", c)
        if not m2:
            return None
        r, g, b = (int(x) for x in m2.groups()[:3])
    else:
        r, g, b = (int(x, 16) for x in m.groups()[:3])
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _section_context(section: Node, index: int):
    color = section.value("background_color")
    image = section.value("background_image")
    lum = _luminance(color) if color else None
    tone = "dark" if lum is not None and lum < 0.5 else "light" if lum is not None else ("image" if image else "default")
    return {"section_index": index, "section_label": section.value("admin_label"), "section_tone": tone,
            "section_background": {"color": color, "image": bool(image)}}


def _skeleton(node: Node, schema):
    mod = schema.module(node.tag)
    attrs = {k: node.value(k) for k in node.attrs
             if k in STRUCTURAL_ATTRS or (mod is not None and is_design_attr(mod, k))}
    return {"tag": node.tag, "attrs": attrs, "children": [_skeleton(c, schema) for c in node.modules]}


def tokens_from_documents(docs: List, schema) -> dict:
    styles = defaultdict(dict)
    presets = defaultdict(Counter)
    palette = defaultdict(lambda: {"uses": 0, "roles": set()})
    levels = defaultdict(Counter)
    body_fonts = Counter()
    section_padding, row_width, row_max = Counter(), Counter(), Counter()
    radii, shadows = Counter(), Counter()
    exemplars = []

    for doc in docs:
        parents = {}
        for node, _path, parent in doc.walk():
            parents[id(node)] = parent
        section_index = -1
        for node, _path, parent in doc.walk():
            mod = schema.module(node.tag)
            if mod is None:
                continue
            if node.tag == "et_pb_section":
                section_index += 1
                exemplars.append(_skeleton(node, schema))
                if node.value("custom_padding"):
                    section_padding[node.value("custom_padding")] += 1
            if node.tag == "et_pb_row":
                if node.value("width"):
                    row_width[node.value("width")] += 1
                if node.value("max_width"):
                    row_max[node.value("max_width")] += 1
            design = {k: node.value(k) for k in node.attrs if is_design_attr(mod, k)}
            preset = node.value("_module_preset") or "default"
            if preset != "default":
                presets[node.tag][preset] += 1
            key = json.dumps([sorted(design.items()), preset, node.value("module_class")])
            section, column, cur = None, None, parent
            while cur is not None:
                if cur.tag in ("et_pb_column", "et_pb_column_inner") and column is None:
                    column = cur
                if cur.tag == "et_pb_section":
                    section = cur
                cur = parents.get(id(cur))
            ctx = _section_context(section, section_index) if section is not None else {}
            ctx["column_type"] = column.value("type") if column is not None else ""
            entry = styles[node.tag].setdefault(key, {
                "uses": 0, "attrs": dict(sorted(design.items())), "preset": preset,
                "module_class": node.value("module_class"), "module_id": node.value("module_id"),
                "custom_css": {k: node.value(k) for k in node.attrs if k.startswith("custom_css_")}, "contexts": []})
            entry["uses"] += 1
            entry["contexts"].append(ctx)
            for name, value in design.items():
                res = mod.resolve(name)
                ftype = (res.field or {}).get("type") if res else None
                if ftype in COLOR_TYPES and value and not value.startswith("gcid-"):
                    p = palette[normalize_color(value)]
                    p["uses"] += 1
                    p["roles"].add(name)
                if "border_radii" in name or name.endswith("_border_radius"):
                    radii[value] += 1
                if name == "box_shadow_style" and value not in ("", "none"):
                    shadows[json.dumps({k: v for k, v in design.items() if k.startswith("box_shadow_")}, sort_keys=True)] += 1
            for lf in LEVEL_FIELDS:
                if lf in mod.fields:
                    prefix = lf[: -len("_level")]
                    level = node.value(lf) or mod.fields[lf].get("default", "") or ("h1" if node.tag == "et_pb_heading" else "")
                    font = node.value(f"{prefix}_font")
                    if level and font:
                        levels[level][json.dumps({
                            "font": font, "size": node.value(f"{prefix}_font_size"),
                            "size_tablet": node.value(f"{prefix}_font_size_tablet"),
                            "size_phone": node.value(f"{prefix}_font_size_phone"),
                            "line_height": node.value(f"{prefix}_line_height"),
                            "letter_spacing": node.value(f"{prefix}_letter_spacing"),
                            "color": node.value(f"{prefix}_text_color")}, sort_keys=True)] += 1
            if node.tag == "et_pb_text" and node.value("text_font"):
                body_fonts[node.value("text_font").split("|")[0]] += 1

    scale = {lvl: json.loads(c.most_common(1)[0][0]) for lvl, c in sorted(levels.items())}
    heading_fonts = Counter(v["font"].split("|")[0] for v in scale.values() if v["font"])
    return {
        "colors": {"palette": sorted(({"hex": h, "uses": v["uses"], "roles": sorted(v["roles"])} for h, v in palette.items()),
                                     key=lambda p: -p["uses"])},
        "typography": {"heading_font": heading_fonts.most_common(1)[0][0] if heading_fonts else "",
                       "body_font": body_fonts.most_common(1)[0][0] if body_fonts else "", "scale": scale},
        "spacing": {"section_padding": [[v, c] for v, c in section_padding.most_common()],
                    "row": {"width": [[v, c] for v, c in row_width.most_common()],
                            "max_width": [[v, c] for v, c in row_max.most_common()]}},
        "shapes": {"radii": [[v, c] for v, c in radii.most_common()],
                   "shadows": [[json.loads(v), c] for v, c in shadows.most_common()]},
        "presets": {slug: [{"uuid": u, "uses": c} for u, c in cnt.most_common()] for slug, cnt in presets.items()},
        "module_styles": {slug: sorted(entries.values(), key=lambda e: -e["uses"]) for slug, entries in styles.items()},
        "section_exemplars": exemplars,
    }
```

- [ ] **Step 4: Run the tests**

Run: `python3 -m unittest tests/test_tokens_from_shortcode.py -v`
Expected: all PASS. If `test_design_vs_content` fails for `background_color`, print `SCHEMA.module('et_pb_section').fields['background_color']` and adjust `is_design_attr` to match the real `tab`/`toggle` values.

- [ ] **Step 5: Commit**

```bash
git add Skill/divi-page-builder/scripts/tokens_from_shortcode.py tests/test_tokens_from_shortcode.py
git commit -m "tokens: style bundles with context, typography scale, palette, spacing, presets, exemplars"
```

---

### Task 12: Tokens from public HTML, `extract_tokens.py` CLI, `design-tokens.md`

**Files:**
- Create: `Skill/divi-page-builder/scripts/tokens_from_html.py`, `Skill/divi-page-builder/scripts/extract_tokens.py`
- Create: `tests/fixtures/html/customized-page.html` (captured in Step 1)
- Create: `Skill/divi-page-builder/reference/design-tokens.md`
- Test: `tests/test_tokens_from_html.py`

**Interfaces:**
- Consumes: `tokens_from_documents` (Task 11), `parse`, `load_schema`.
- Produces:
  - `tokens_from_html.tokens_from_html(html: str) -> {"divi_version": str, "global_colors": {gcid: value}, "fonts": [family], "customizer": {accent, link, body_text, heading, body_font, heading_font, body_size, content_width}}`;
  - `extract_tokens.build_tokens(sources: list[dict(id, url, raw)], html_by_url: dict, site_url: str, schema) -> dict`, the full `tokens.json` per spec §4.10 plus `site`;
  - CLI flags `--site/--user/--page…/--out` and `--shortcode-file/--url/--out`.

- [ ] **Step 1: Discover Divi's Customizer and global-color CSS output (live)**

Set non-default values on the local site, capture a page, then restore the originals.
```bash
W=research/tools/wp-local.sh
$W option get et_divi --format=json > /tmp/et_divi.backup.json
$W eval '$o=get_option("et_divi"); $o["accent_color"]="#ff00aa"; $o["font_color"]="#333344"; $o["header_color"]="#112233"; $o["link_color"]="#0055ff"; $o["body_font"]="Lato"; $o["heading_font"]="Montserrat"; $o["body_font_size"]=17; $o["content_width"]=1200; $o["et_global_data"]["global_colors"]["gcid-planprobe"]=array("color"=>"#123456","active"=>"yes"); update_option("et_divi",$o); echo "ok";'
ID=$($W post create tests/fixtures/valid/handwritten-landing.txt --post_type=page --post_status=publish --post_title="Plan Test: tokens html" --porcelain)
$W post meta update $ID _et_pb_use_builder on
curl -s "http://divi-test.local/?page_id=$ID" > /dev/null   # first hit builds the CSS cache
curl -s "http://divi-test.local/?page_id=$ID" > tests/fixtures/html/customized-page.html
$W post delete $ID --force
$W option update et_divi --format=json < /tmp/et_divi.backup.json
python3 - <<'EOF'
import re
h = open("tests/fixtures/html/customized-page.html").read()
print("style ids:", re.findall(r'<style[^>]*id=["\']([^"\']+)', h))
for needle in ("#ff00aa", "#333344", "#112233", "#0055ff", "gcid-planprobe", "#123456", "1200px", "17px"):
    i = h.find(needle); print(needle, i, h[max(0, i-160):i+40].replace("\n", " ") if i >= 0 else "")
print(re.findall(r'<meta name="generator" content="([^"]+)"', h))
EOF
```
Record the following in `research/tools/notes/customizer-css.md`:
- which `<style id>` holds each value;
- the exact CSS selectors (for example `body{color:#333344}` and `h1,h2,…{color:#112233}`);
- how `gcid-planprobe` appears (a CSS custom property, or inlined as a hex value);
- the generator meta.

The parser in Step 3 targets these observed selectors. If a value doesn't appear anywhere, record "not output by Divi 4.27.9" and leave that token empty.

- [ ] **Step 2: Write the failing tests against the captured fixture**

`tests/test_tokens_from_html.py`:
```python
import json
import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from extract_tokens import build_tokens
from tokens_from_html import tokens_from_html

HTML = (FIXTURES / "html" / "customized-page.html").read_text()


class TokensFromHtmlTest(unittest.TestCase):
    def test_customizer_values(self):
        c = tokens_from_html(HTML)["customizer"]
        self.assertEqual(c.get("accent"), "#ff00aa")
        self.assertEqual(c.get("body_text"), "#333344")
        self.assertEqual(c.get("heading"), "#112233")
        self.assertEqual(c.get("link"), "#0055ff")

    def test_fonts_and_version(self):
        t = tokens_from_html(HTML)
        self.assertIn("Montserrat", t["fonts"])
        self.assertIn("Lato", t["fonts"])
        self.assertEqual(t["divi_version"], "4.27.9")

    def test_global_colors(self):
        self.assertEqual(tokens_from_html(HTML)["global_colors"].get("gcid-planprobe"), "#123456")

    def test_build_tokens_merges_sources(self):
        raw = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()
        t = build_tokens([{"id": 1, "url": "https://client.example/p/", "raw": raw}],
                         {"https://client.example/p/": HTML}, "https://client.example", load_schema())
        self.assertEqual(t["site"]["url"], "https://client.example")
        self.assertEqual(t["site"]["divi_version"], "4.27.9")
        self.assertEqual(t["colors"]["customizer"]["accent"], "#ff00aa")
        self.assertIn("et_pb_button", t["module_styles"])
        json.dumps(t)  # must be JSON-serializable


if __name__ == "__main__":
    unittest.main()
```
If Step 1 recorded a value as "not output", delete the matching assertion and note why in a comment that cites `customizer-css.md`.

Run: `python3 -m unittest tests/test_tokens_from_html.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tokens_from_html'`

- [ ] **Step 3: Implement the HTML parser**

`Skill/divi-page-builder/scripts/tokens_from_html.py`:
```python
"""Read site-wide Divi styling from a public page's HTML: Customizer CSS, global colors, fonts, Divi version."""
from __future__ import annotations

import re
from urllib.parse import parse_qs, unquote, urlparse

RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
DECL_RE = re.compile(r"([\w-]+)\s*:\s*([^;]+)")


def _rules(css: str):
    for m in RULE_RE.finditer(css):
        selectors = [s.strip() for s in m.group(1).split(",")]
        decls = {k.strip().lower(): v.strip().replace("!important", "").strip() for k, v in DECL_RE.findall(m.group(2))}
        yield selectors, decls


def _first(css: str, selector: str, prop: str) -> str:
    for selectors, decls in _rules(css):
        if selector in selectors and prop in decls:
            return decls[prop]
    return ""


def tokens_from_html(html: str) -> dict:
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", html, re.S))
    fonts = []
    for href in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"']+)", html):
        for fam in parse_qs(unquote(href.replace("&#038;", "&"))).get("family", []):
            for part in fam.split("|"):
                name = part.split(":")[0].replace("+", " ").strip()
                if name and name not in fonts:
                    fonts.append(name)
    version = ""
    m = re.search(r'<meta name="generator" content="Divi v\.([\d.]+)"', html) or \
        re.search(r"themes/Divi/[^\"']*\?ver=([\d.]+)", html)
    if m:
        version = m.group(1)
    global_colors = {k: v.strip() for k, v in re.findall(r"--(gcid-[\w-]+)\s*:\s*([^;}]+)", css)}
    customizer = {
        # Selectors below are the ones recorded in research/tools/notes/customizer-css.md (Task 12 Step 1).
        "body_text": _first(css, "body", "color"),
        "heading": _first(css, "h1", "color"),
        "link": _first(css, "a", "color"),
        "accent": _first(css, ".et_pb_counter_amount", "background-color") or _first(css, "#top-menu li.current-menu-item>a", "color"),
        "body_font": _first(css, "body", "font-family").split(",")[0].strip("'\" "),
        "heading_font": _first(css, "h1", "font-family").split(",")[0].strip("'\" "),
        "body_size": _first(css, "body", "font-size"),
        "content_width": _first(css, ".container", "max-width") or _first(css, ".et_pb_row", "max-width"),
    }
    return {"divi_version": version, "global_colors": global_colors, "fonts": fonts,
            "customizer": {k: v for k, v in customizer.items() if v}}
```
After Step 1, replace each `_first(css, "<selector>", "<prop>")` with the exact selector recorded in `customizer-css.md`, **before** running the tests. The selectors above are starting guesses.

- [ ] **Step 4: Implement the CLI**

`Skill/divi-page-builder/scripts/extract_tokens.py`:
```python
#!/usr/bin/env python3
"""Extract a Divi site's design tokens into tokens.json.

Online:  extract_tokens.py --site https://client.com --user USER --page 12 [--page 34] --out tokens.json
         (password from env WP_APP_PASSWORD, an Application Password)
Offline: extract_tokens.py --shortcode-file page.txt --url https://client.com/page/ --out tokens.json
"""
from __future__ import annotations

import argparse
import base64
import datetime
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_schema import load_schema  # noqa: E402
from divi_shortcode import parse  # noqa: E402
from tokens_from_html import tokens_from_html  # noqa: E402
from tokens_from_shortcode import tokens_from_documents  # noqa: E402


def _get(url: str, auth: str = "") -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "divi-page-builder/1.0"})
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_page(site: str, user: str, password: str, page_id: int) -> dict:
    data = json.loads(_get(f"{site.rstrip('/')}/wp-json/wp/v2/pages/{page_id}?context=edit", f"{user}:{password}"))
    return {"id": page_id, "url": data["link"], "raw": data["content"]["raw"]}


def build_tokens(sources, html_by_url, site_url, schema) -> dict:
    tokens = tokens_from_documents([parse(s["raw"]) for s in sources], schema)
    html_parts = [tokens_from_html(h) for h in html_by_url.values() if h]
    customizer, global_colors, fonts, version = {}, {}, [], ""
    for part in html_parts:
        customizer.update({k: v for k, v in part["customizer"].items() if k not in customizer})
        global_colors.update(part["global_colors"])
        fonts += [f for f in part["fonts"] if f not in fonts]
        version = version or part["divi_version"]
    tokens["colors"]["global"] = global_colors
    tokens["colors"]["customizer"] = customizer
    tokens["typography"]["loaded_fonts"] = fonts
    if not tokens["typography"]["heading_font"]:
        tokens["typography"]["heading_font"] = customizer.get("heading_font", "")
    if not tokens["typography"]["body_font"]:
        tokens["typography"]["body_font"] = customizer.get("body_font", "")
    tokens["site"] = {"url": site_url, "divi_version": version,
                      "source_pages": [{"id": s["id"], "url": s["url"]} for s in sources],
                      "extracted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    return dict(sorted(tokens.items(), key=lambda kv: kv[0] != "site"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site")
    ap.add_argument("--user")
    ap.add_argument("--page", type=int, action="append", default=[])
    ap.add_argument("--shortcode-file")
    ap.add_argument("--url")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    try:
        if a.shortcode_file:
            sources = [{"id": 0, "url": a.url or "", "raw": Path(a.shortcode_file).read_text(encoding="utf-8")}]
            site = a.url or ""
        else:
            password = os.environ.get("WP_APP_PASSWORD", "")
            if not (a.site and a.user and a.page and password):
                ap.error("online mode needs --site, --user, --page and env WP_APP_PASSWORD")
            sources = [fetch_page(a.site, a.user, password, pid) for pid in a.page]
            site = a.site
        html = {}
        for s in sources:
            if s["url"]:
                try:
                    html[s["url"]] = _get(s["url"]).decode("utf-8", "replace")
                except OSError as exc:
                    print(f"warning: could not fetch {s['url']}: {exc}", file=sys.stderr)
    except OSError as exc:
        print(f"extract_tokens.py: {exc}", file=sys.stderr)
        return 2
    tokens = build_tokens(sources, html, site, load_schema())
    Path(a.out).write_text(json.dumps(tokens, indent=1, ensure_ascii=False))
    ms = tokens["module_styles"]
    print(f"wrote {a.out}: {sum(len(v) for v in ms.values())} style bundles across {len(ms)} modules, "
          f"{len(tokens['colors']['palette'])} palette colors, {len(tokens['section_exemplars'])} section exemplars, "
          f"{sum(len(v) for v in tokens['presets'].values())} presets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run the tests and the offline CLI**

Run:
```bash
python3 -m unittest tests/test_tokens_from_html.py tests/test_tokens_from_shortcode.py -v
python3 Skill/divi-page-builder/scripts/extract_tokens.py --shortcode-file tests/fixtures/valid/handwritten-landing.txt --out /tmp/t.json && head -c 600 /tmp/t.json
```
Expected: all PASS; `wrote /tmp/t.json: …` followed by JSON that starts with `"site"`.

- [ ] **Step 6: Write `reference/design-tokens.md`**

Required sections:
1. Where a Divi site's style lives: inline attributes, global presets (which can't be read; reuse UUIDs from `presets`), Customizer and global colors (from the public CSS), and child theme or plugin CSS (not captured).
2. How to run the extractor, in both modes.
3. What each `tokens.json` key means, with a short excerpt from `/tmp/t.json`.
4. **How to use the tokens when composing:**
   - pick `module_styles[slug]` entries by `contexts.section_tone` and position;
   - copy `attrs` verbatim;
   - keep `preset` and `module_class`;
   - follow `section_exemplars` for padding, row widths and column habits;
   - use `typography.scale` for each heading level.
5. The fidelity rule: the result must reproduce anything existing components do. When no matching style exists, say so to the user rather than inventing one.
6. Limits: preset contents are unknown; Customizer values the site never overrides don't appear in the tokens.

- [ ] **Step 7: Commit**

```bash
git add Skill/divi-page-builder/scripts/tokens_from_html.py Skill/divi-page-builder/scripts/extract_tokens.py tests/fixtures/html tests/test_tokens_from_html.py Skill/divi-page-builder/reference/design-tokens.md research/tools/notes/customizer-css.md
git commit -m "tokens: public-CSS side, extract_tokens CLI (REST/offline), design-tokens reference"
```

---

### Task 13: Token fidelity, end to end, on the local site

**Files:**
- Create: `tests/fixtures/valid/brand-kit.txt`
- Create: `Skill/divi-page-builder/recipes/sample-tokens.json` (generated here, used by Tasks 15-19)
- Test: `tests/test_tokens_fidelity.py`

**Interfaces:**
- Consumes: `extract_tokens.py` (Task 12), `wp-local.sh`, and the Application Password flow (Task 10).
- Produces: `recipes/sample-tokens.json`, a realistic tokens file for a fictional brand, which the recipes reference.

- [ ] **Step 1: Author the brand-kit page**

`tests/fixtures/valid/brand-kit.txt` is a 5-section page for the fictional brand "Miami Rapid Plumbing". Palette: `#0b2a3c` navy, `#f97316` orange, `#ffffff`, `#f1f5f9`, `#475569`. Fonts: Montserrat headings, Lato body. It must include:
- (a) the hero from `handwritten-landing.txt`;
- (b) a light section with an H2 (`title_font_size="40px"`, tablet `32px`, phone `28px`) and 3 blurbs;
- (c) a button that uses `_module_preset="11111111-2222-3333-4444-555555555555"`;
- (d) a text module with `module_class="pp-lead"`;
- (e) a stats row with two `et_pb_number_counter`s on `#f1f5f9`.

It must pass `validate.py` with 0 errors, and it's the source for `sample-tokens.json`.

- [ ] **Step 2: Write the end-to-end test**

It runs against the local site and is skipped when the site is unavailable.

`tests/test_tokens_fidelity.py`:
```python
import json
import os
import subprocess
import sys
import unittest

from _paths import FIXTURES, SCRIPTS, WP_LOCAL

PAGE = FIXTURES / "valid" / "brand-kit.txt"


def wp(*args):
    out = subprocess.run([str(WP_LOCAL), *args], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise unittest.SkipTest(f"local site unavailable: {out.stderr[-200:]}")
    return out.stdout.strip()


class TokensFidelityTest(unittest.TestCase):
    def test_round_trip_through_wordpress(self):
        user = wp("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        password = wp("user", "application-password", "create", user, "fidelity-test", "--porcelain")
        page_id = wp("post", "create", str(PAGE), "--post_type=page", "--post_status=publish",
                     "--post_title=Plan Test: fidelity", "--porcelain")
        wp("post", "meta", "update", page_id, "_et_pb_use_builder", "on")
        out = FIXTURES / "html" / "fidelity-tokens.json"
        try:
            env = dict(os.environ, WP_APP_PASSWORD=password)
            run = subprocess.run([sys.executable, str(SCRIPTS / "extract_tokens.py"), "--site", "http://divi-test.local",
                                  "--user", user, "--page", page_id, "--out", str(out)], env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            t = json.loads(out.read_text())
        finally:
            wp("post", "delete", page_id, "--force")
            uuid = wp("user", "application-password", "list", user, "--name=fidelity-test", "--field=uuid")
            wp("user", "application-password", "delete", user, uuid)
        self.assertEqual(t["presets"]["et_pb_button"][0]["uuid"], "11111111-2222-3333-4444-555555555555")
        self.assertTrue(any(e["module_class"] == "pp-lead" for e in t["module_styles"]["et_pb_text"]))
        self.assertEqual(t["typography"]["scale"]["h2"]["size_tablet"], "32px")
        self.assertTrue({"#0b2a3c", "#f97316", "#f1f5f9"} <= {p["hex"] for p in t["colors"]["palette"]})
        tones = {c["section_tone"] for e in t["module_styles"]["et_pb_button"] for c in e["contexts"]}
        self.assertIn("dark", tones)
        self.assertEqual(len(t["section_exemplars"]), 5)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run it**

Run: `python3 -m unittest tests/test_tokens_fidelity.py -v`
Expected: PASS. Afterwards, `research/tools/wp-local.sh post list --post_type=page --s="Plan Test" --format=count` prints `0`.

- [ ] **Step 4: Produce `recipes/sample-tokens.json`**

```bash
mkdir -p Skill/divi-page-builder/recipes
cp tests/fixtures/html/fidelity-tokens.json Skill/divi-page-builder/recipes/sample-tokens.json
python3 - <<'EOF'
import json
p = "Skill/divi-page-builder/recipes/sample-tokens.json"
t = json.load(open(p))
t["site"]["url"] = "https://miamirapidplumbing.example"
t["site"]["source_pages"] = [{"id": 101, "url": "https://miamirapidplumbing.example/"}]
json.dump(t, open(p, "w"), indent=1)
EOF
```

- [ ] **Step 5: Sanity run on a real client page (needs the user)**

Ask the user for one live client page ID and a WordPress user with an Application Password on that site, where the user sets `WP_APP_PASSWORD` in their own shell (for example via `! export WP_APP_PASSWORD=…`). Then run:
```bash
python3 Skill/divi-page-builder/scripts/extract_tokens.py --site https://CLIENT --user USER --page ID --out /tmp/client-tokens.json
```
Check the printed summary and open `/tmp/client-tokens.json`:
- the palette colors match what the live page shows;
- `typography.scale` has the page's heading sizes;
- the `presets` list is non-empty if the site uses presets.

Record the findings, not the tokens file (it's client data), in `research/tools/notes/client-sanity-run.md`. If the user declines, record "skipped: no client credentials" there.

- [ ] **Step 6: Commit**

```bash
git add research/tools/notes/client-sanity-run.md tests/fixtures/valid/brand-kit.txt tests/test_tokens_fidelity.py Skill/divi-page-builder/recipes/sample-tokens.json
git commit -m "tokens: end-to-end fidelity test via REST + sample tokens for recipes"
```

---

### Task 14: Portable preview on WordPress Playground (amended 2026-09-24)

> Amended after the Playground spike (`research/playground-spike.md`: GO). This replaces the LocalWP-mirror preview. The user decided the skill must preview without a WordPress install, and still without client settings (spec Addendum A/B).

**Files:**
- Create: `Skill/divi-page-builder/scripts/preview/preview.mjs`, `fetch-divi.mjs`, `mu-plugin/pp-preview.php`, `blueprint.json`, `.gitignore`. Start from `research/playground-prototype/` and adapt.
- Create: `Skill/divi-page-builder/reference/preview.md`
- Test: `tests/test_preview.py`

**Interfaces:**
- Consumes: `tokens.json → site.divi_version` (Task 12); fixtures `handwritten-landing.txt`, `brand-kit.txt` (Task 13), `unicode.txt`, `divi-ai-layout.txt`; `divi_shortcode.parse` (for section counts in tests).
- Produces the CLI (Node ≥ 20; tested on 24.1):
  - `node scripts/preview/preview.mjs serve [--pages DIR] [--divi VER | --tokens tokens.json] [--port 9400]` serves `http://127.0.0.1:PORT/?pp_preview=<name>` for each `DIR/<name>.txt`, re-reading the file on every request.
  - `node scripts/preview/preview.mjs render <page.txt> [--out page.html] [--divi VER | --tokens tokens.json]` writes one self-contained HTML file.
  - `node scripts/preview/preview.mjs fetch-divi <VER|latest>` warms the cache. It's the only command that needs Elegant Themes credentials.
  - `node scripts/preview/preview.mjs doctor` prints the Node version (fails if < 20), npx/unzip/tar availability, the cache dir, and cached Divi and WordPress versions. It exits 0 when usable, 1 when not.
- Env:
  - `ET_USERNAME`/`ET_API_KEY`: used only to fetch an uncached Divi version, and never printed or written.
  - `PP_CACHE_DIR`: default `~/.cache/divi-page-builder` (Windows: `%LOCALAPPDATA%\divi-page-builder`).
  - `PP_PLAYGROUND_CLI`: default pinned `@wp-playground/cli@3.1.55`.
  - `PP_WP_VERSION`: default `7.1.2`.
- Divi version resolution: `--divi`, then `--tokens` (`site.divi_version`), then the newest cached version, then `latest` (network). **Never call the Elegant Themes API when the resolved version is already cached.** The API rate-limits at about 15 calls per 5 minutes.

- [ ] **Step 1: Read the spike, then copy the prototype**

Read `research/playground-spike.md` in full, especially §1 (the Elegant Themes endpoint and its errors), §3 (the mu-plugin design), §5 (practicalities and quirks) and "Recommendation".
```bash
mkdir -p Skill/divi-page-builder/scripts/preview/mu-plugin
cp research/playground-prototype/{preview.mjs,fetch-divi.mjs,blueprint.json,.gitignore} Skill/divi-page-builder/scripts/preview/
cp research/playground-prototype/mu-plugin/pp-preview.php Skill/divi-page-builder/scripts/preview/mu-plugin/
```

- [ ] **Step 2: Adapt the prototype into the shipped command**

1. Add the `fetch-divi <VER|latest>` subcommand to `preview.mjs` (call `ensureDivi` from `fetch-divi.mjs`), and add `doctor`.
2. Add `--tokens <file>`, which reads `site.divi_version`, following the resolution order above.
3. Rename the cache root from `post-pusher` to `divi-page-builder` everywhere (both `.mjs` files and the `.gitignore` comment).
4. Keep the pinned CLI version, `--prefer-offline`, the WordPress self-download, the PHP pin inside the blueprint, the onboarding-redirect guard and the inline-Google-Fonts-off setting. These are the spike's documented quirk workarounds, and each needs a one-line comment saying why.
5. Don't add a settings bundle (spec Addendum A: no client settings). Remove any `settings` references the prototype carries.
6. Audit for secrets: `command grep -n "api_key\|ET_API_KEY\|ET_USERNAME\|console" Skill/divi-page-builder/scripts/preview/*.mjs`. Credentials may only be read from `process.env` and placed in the request URL; no log line may contain them. A failed download must print a redacted URL.
7. Confirm with `node --check Skill/divi-page-builder/scripts/preview/preview.mjs && node --check Skill/divi-page-builder/scripts/preview/fetch-divi.mjs`.

- [ ] **Step 3: Write the tests**

They skip cleanly when Node, the cache or credentials are unavailable.

`tests/test_preview.py`:
```python
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SKILL, WP_LOCAL
from divi_shortcode import parse

PREVIEW = SKILL / "scripts" / "preview" / "preview.mjs"
VERSION = "4.27.9"


def _et_env():
    """Elegant Themes credentials from the local test site's DB, passed only via the child env (never printed)."""
    out = subprocess.run([str(WP_LOCAL), "option", "get", "et_automatic_updates_options", "--format=json"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        return {}
    import json
    data = json.loads(out.stdout[out.stdout.index("{"):])
    return {"ET_USERNAME": data.get("username", ""), "ET_API_KEY": data.get("api_key", "")}


def node(*args, timeout=600):
    if shutil.which("node") is None:
        raise unittest.SkipTest("node not installed")
    env = dict(os.environ, **_et_env())
    return subprocess.run(["node", str(PREVIEW), *args], capture_output=True, text=True, timeout=timeout, env=env)


class PreviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        warm = node("fetch-divi", VERSION)
        if warm.returncode != 0:
            raise unittest.SkipTest(f"Divi {VERSION} not cached and not fetchable: {warm.stderr[-300:]}")

    def render(self, path, *extra):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out.html"
            proc = node("render", str(path), "--out", str(out), "--divi", VERSION, *extra)
            self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
            return out.read_text(), proc.stdout + proc.stderr

    def test_doctor(self):
        proc = node("doctor")
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn(VERSION, proc.stdout)

    def test_fixtures_render_every_section(self):
        for name in ("handwritten-landing.txt", "brand-kit.txt", "unicode.txt"):
            path = FIXTURES / "valid" / name
            html, _ = self.render(path)
            self.assertIn('class="et-l', html, name)
            sections = len(parse(path.read_text()).sections())
            self.assertEqual(len(re.findall(r'class="[^"]*\bet_pb_section\b', html)), sections, name)

    def test_tokens_select_divi_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "o.html"
            proc = node("render", str(FIXTURES / "valid" / "handwritten-landing.txt"), "--out", str(out),
                        "--tokens", str(FIXTURES / "tokens-min.json"))
            self.assertEqual(proc.returncode, 0, proc.stderr[-500:])
            self.assertIn(VERSION, proc.stdout + proc.stderr)

    def test_page11_builder_css_matches_live(self):
        live = subprocess.run(["curl", "-s", "http://divi-test.local/probe-divi-ai-emergency-plumber/"],
                              capture_output=True, text=True).stdout
        if "et_pb_section" not in live:
            self.skipTest("page 11 not reachable")
        html, _ = self.render(FIXTURES / "valid" / "divi-ai-layout.txt")
        decl = re.compile(r"\.et_pb_[a-z_]+_\d+[^{]*\{[^}]*\}")
        self.assertEqual(sorted(set(decl.findall(html))), sorted(set(decl.findall(live))))

    def test_no_credentials_in_output(self):
        env = _et_env()
        _, logs = self.render(FIXTURES / "valid" / "handwritten-landing.txt")
        for secret in env.values():
            if secret:
                self.assertNotIn(secret, logs)


if __name__ == "__main__":
    unittest.main()
```
Run: `python3 -m unittest discover -s tests -p 'test_preview.py' -v`
Expected: all PASS. The first run takes about 30 s because it installs the CLI and WordPress.

If `test_page11_builder_css_matches_live` differs, compare with the spike's `research/playground-prototype/compare.py` method. The spike measured 2,064 of 2,064 matching declarations; differences usually mean an inline-Google-Fonts or onboarding setting was lost during adaptation.

- [ ] **Step 4: Write `reference/preview.md`**

Required sections:
1. **What it is:** real Divi running in WebAssembly WordPress (Playground). No WordPress install; nothing is written to any site.
2. **Requirements:** Node ≥ 20 (tested on 24.1) with npx; `unzip` or `tar`; about 1–1.2 GB of disk; Elegant Themes credentials only the first time a Divi version is used. Run `doctor` to check.
3. **Commands:** `serve`, `render`, `fetch-divi` and `doctor`, each with an example.
4. **Version selection:** preview on the client's Divi version (`--tokens tokens.json`), and the resolution order.
5. **Caching and offline:** what's cached where; it works offline after the first run; the Elegant Themes rate limit.
6. **Fidelity and limits (must be explicit):**
   - builder markup and CSS are identical to real Divi (the spike's numbers);
   - it uses **stock Divi settings**, so client Customizer values, global presets and global colors are **not** applied;
   - the site header and menu are the preview site's, not the client's;
   - animations need JS;
   - fonts and images need network to *look* right.

   The WordPress draft preview is the authoritative visual check.
7. **Troubleshooting:** the spike's quirks and their symptoms.

- [ ] **Step 5: Commit**

```bash
git add Skill/divi-page-builder/scripts/preview Skill/divi-page-builder/reference/preview.md tests/test_preview.py research/playground-spike.md research/playground-prototype
git commit -m "preview: portable Divi preview on WordPress Playground (serve/render/fetch-divi/doctor)"
```
Before committing, confirm `git status --porcelain | command grep -i "\.zip\|/Divi/"` prints nothing. No Divi files or caches may enter the repo.

---

### Task 15: Recipe foundation: README, template, local push helper

**Files:**
- Create: `Skill/divi-page-builder/recipes/README.md`
- Create: `research/tools/push_local.sh`
- Create: `research/tools/notes/recipe-template.md`

**Interfaces:**
- Consumes: `recipes/sample-tokens.json` (Task 13), `check_doc_examples.py` (Task 9) and the REST flow (Task 10).
- Produces:
  - the recipe format that every recipe in Tasks 16-19 follows exactly;
  - `research/tools/push_local.sh <file.txt> "<title>"`, which prints the page ID and URL of a published `Plan Test:` page on `divi-test.local`.

- [ ] **Step 1: Write the local push helper**

`research/tools/push_local.sh`:
```bash
#!/bin/bash
# Publish a shortcode file as a "Plan Test:" page on divi-test.local for visual checks; prints "<id> <url>".
#   research/tools/push_local.sh recipe-example.txt "Hero split"
# Delete afterwards with: research/tools/wp-local.sh post delete <id> --force
set -euo pipefail
W="$(cd "$(dirname "$0")" && pwd)/wp-local.sh"
ID=$("$W" post create "$1" --post_type=page --post_status=publish --post_title="Plan Test: $2" --porcelain)
"$W" post meta update "$ID" _et_pb_use_builder on >/dev/null
"$W" post meta update "$ID" _et_pb_page_layout et_no_sidebar >/dev/null
URL=$("$W" post get "$ID" --field=url)
curl -s "$URL" > /dev/null   # warm Divi's CSS cache
echo "$ID $URL"
```

- [ ] **Step 2: Write the recipe template**

`research/tools/notes/recipe-template.md` defines every section recipe as exactly these parts, in order:
````markdown
# <Recipe name>

**Use for:** <one line> · **SEO:** <heading level rules, alt text, links>

## Structure
```text
section (<purpose>)
└─ row column_structure="…"
   ├─ column 1_2: heading (h1) · text · button
   └─ column 1_2: image
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[section_tone=dark].attrs.background_color` | `colors.palette[0].hex` |
| heading `title_font` | `typography.scale.h1.font` | `typography.heading_font` + `|700|||||||` |
| … | … | … |

## Required fields · Optional fields
Two short lists; each field links to its module page.

## Responsive rules
Which values need `_tablet`/`_phone`, and why.

## Variations
2–3 bullets, each saying which attributes change.

## Worked example (sample-tokens.json)
```divi
<complete page containing this section, 0 validator errors>
```

## Checklist
- [ ] validator 0 errors with `--tokens`
- [ ] exactly one H1 on the page
- [ ] every image has alt text and a Media Library URL
````

- [ ] **Step 3: Write `recipes/README.md`**

Required content:
1. What a recipe is: a *pattern expressed as fields*, not a template to fill in.
2. How to read a token mapping. Show how to pick a `module_styles` entry by `contexts.section_tone`, and how to copy `attrs` verbatim, including `preset` and `module_class`.
3. How to use `section_exemplars`: match padding, row width and column habits.
4. An index table of every recipe in `sections/`, `pages/` and `edits/`, with a one-line use-case each (grows through Tasks 16-19).
5. The verification loop every recipe went through:
   - `validate.py --tokens recipes/sample-tokens.json`;
   - `push_local.sh`;
   - a screenshot.

- [ ] **Step 4: Verify and commit**

Run: `chmod +x research/tools/push_local.sh && python3 research/tools/check_doc_examples.py Skill/divi-page-builder`
Expected: `0 failing block(s)`

```bash
git add Skill/divi-page-builder/recipes/README.md research/tools/push_local.sh research/tools/notes/recipe-template.md
git commit -m "recipes: format, README, local push helper"
```

---

### Task 16: Hero recipes (4 variants)

**Files:**
- Create: `Skill/divi-page-builder/recipes/sections/hero-split.md`, `hero-centered.md`, `hero-background-image.md`, `hero-fullwidth-header.md`
- Modify: `Skill/divi-page-builder/recipes/README.md` (index rows)

**Interfaces:**
- Consumes: the recipe template (Task 15), `sample-tokens.json`, module pages (Task 8) and value formats (Task 9).
- Produces: four recipes that follow the template exactly.

- [ ] **Step 1: Write `hero-split.md`, using this worked example as the anchor**

Every attribute must come from `sample-tokens.json`. If the sample tokens contain different values from those shown, use the sample tokens.
```divi
[et_pb_section admin_label="Hero" _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" custom_padding="96px||96px||true|false" custom_padding_tablet="64px||64px||true|false" custom_padding_phone="48px||48px||true|false" custom_padding_last_edited="on|phone"][et_pb_row column_structure="1_2,1_2" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Eyebrow" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|600||on|||||" text_text_color="#f97316" text_font_size="14px" text_letter_spacing="2px"]<p>24/7 Emergency Plumbing</p>[/et_pb_text][et_pb_heading title="Emergency Plumber in Miami" title_level="h1" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#ffffff" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone" title_line_height="1.1em"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#cbd5e1" text_font_size="18px" text_line_height="1.7em"]<p>Licensed, insured plumbers at your door in 60 minutes, day or night, anywhere in Miami-Dade.</p>[/et_pb_text][et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_text_color="#ffffff" button_bg_color="#f97316" button_border_width="0px" button_border_radius="6px" button_font="Montserrat|600|||||||" button_text_size="16px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover"][/et_pb_button][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/plumber-at-work.jpg" alt="Licensed plumber repairing a burst pipe under a Miami kitchen sink" _builder_version="4.27.9" _module_preset="default" border_radii="on|12px|12px|12px|12px" box_shadow_style="preset1"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

- [ ] **Step 2: Write the other three hero recipes**

- **`hero-centered.md`:** one `4_4` column, `text_orientation="center"` on text modules, button `button_alignment="center"`, max-width text via `max_width="720px"` + `module_alignment="center"`.
- **`hero-background-image.md`:** section `background_image`, `background_size="cover"`, `background_position="center"`, a dark overlay through `background_color_gradient_stops` + `use_background_color_gradient="on"` + `background_color_gradient_overlays_image="on"`, and light text.
- **`hero-fullwidth-header.md`:** `[et_pb_section fullwidth="on"][et_pb_fullwidth_header …]`, with `title`, `subhead`, `button_one_*`, `button_two_*`, `header_fullscreen`, `text_orientation` and the title heading level field (look it up in `reference/modules/et_pb_fullwidth_header.md`).

- [ ] **Step 3: Verify each recipe**

For each recipe:
```bash
python3 research/tools/check_doc_examples.py Skill/divi-page-builder
python3 - <<'EOF' > /tmp/recipe.txt
import re,sys; t=open("Skill/divi-page-builder/recipes/sections/hero-split.md").read(); print(re.search(r"```divi\n(.*?)```", t, re.S).group(1).strip())
EOF
python3 Skill/divi-page-builder/scripts/validate.py /tmp/recipe.txt --tokens Skill/divi-page-builder/recipes/sample-tokens.json
research/tools/push_local.sh /tmp/recipe.txt "hero-split"
```
Expected: 0 errors and no `W_OFF_PALETTE_COLOR`/`W_OFF_BRAND_FONT` warnings. Open the printed URL with the Chrome tools and screenshot it at 1440 px and 390 px wide. Confirm three things:
- the layout matches the Structure section;
- the text is readable on its background;
- nothing overflows on phone.

Delete the page: `research/tools/wp-local.sh post delete <id> --force`.

- [ ] **Step 4: Add the index rows and commit**

```bash
git add Skill/divi-page-builder/recipes
git commit -m "recipes: hero (split, centered, background image, fullwidth header)"
```

---

### Task 17: Content-section recipes

**Files:**
- Create in `Skill/divi-page-builder/recipes/sections/`: `trust-bar.md`, `services-grid.md`, `alternating-features.md`, `stats-counters.md`, `process-steps.md`, `tabs.md`, `service-area-list.md`
- Modify: `recipes/README.md` (index rows)

**Interfaces:** same as Task 16.

- [ ] **Step 1: Write each recipe with the template and these required specifics**

- **`trust-bar.md`:** a `1_5`×5 or `1_4`×4 row of `et_pb_image` logos with `alt` = the company name, a grayscale filter (`filter_saturate="0%"`) with hover color (`filter_saturate__hover="100%"`, `filter_saturate__hover_enabled="on|hover"`), and a compact section padding from tokens.
- **`services-grid.md`:** an H2 heading row, then `1_3`×3 (or `1_4`×4) `et_pb_blurb`s with `use_icon="on"`, `header_level="h3"`, `icon_color` from tokens, and an optional `url` on each blurb linking to the service page. The internal-linking SEO note goes here.
- **`alternating-features.md`:** rows alternating `1_2,1_2` image/text then text/image. Use `custom_css`-free ordering; on phone, keep the image first via row ordering, explained with the reason.
- **`stats-counters.md`:** `et_pb_number_counter` × 3–4 with `number`, `title`, `percent_sign="off"`, and number font from `typography.scale`.
- **`process-steps.md`:** numbered steps as blurbs, or text modules with a number eyebrow; `1_4`×4 or a stacked `4_4`.
- **`tabs.md`:** `et_pb_tabs` with `et_pb_tab` children, plus the tab title/active color fields from its module page.
- **`service-area-list.md`:** an H2 plus a `1_3`×3 `et_pb_text` with `<ul>` lists of cities (local SEO), and a note to link each city to its location page when one exists.

- [ ] **Step 2: Verify each recipe exactly as in Task 16, Step 3**

This means validating with `--tokens`, pushing, screenshotting at 1440 and 390, checking and deleting.

- [ ] **Step 3: Commit**

```bash
git add Skill/divi-page-builder/recipes
git commit -m "recipes: trust bar, services grid, features, stats, process, tabs, service areas"
```

---

### Task 18: Social-proof and conversion recipes

**Files:**
- Create in `Skill/divi-page-builder/recipes/sections/`: `testimonials.md`, `pricing.md`, `faq.md`, `cta-band.md`, `contact.md`, `team.md`, `gallery.md`, `video.md`
- Modify: `recipes/README.md` (index rows)

**Interfaces:** same as Task 16.

- [ ] **Step 1: Write each recipe with the template and these required specifics**

- **`testimonials.md`:** a grid variant (`et_pb_testimonial` × 3 in `1_3` columns, `portrait_url` optional, `quote_icon` on/off) and a slider variant (`et_pb_slider` with `et_pb_slide`s carrying the quote in content). Include the review-honesty note: never invent testimonials; use only ones provided in the brief.
- **`pricing.md`:** `et_pb_pricing_tables` with `et_pb_pricing_table` children, `featured="on"` on one, and a currency/price/frequency field table from the module page.
- **`faq.md`:** `et_pb_accordion` with `et_pb_accordion_item` (first one `open="on"`) **plus** an `et_pb_code` module containing `<script type="application/ld+json">` FAQPage JSON-LD built from the same questions. Document that the JSON-LD's quotes and brackets must be escaped inside the code module's content (inner content, not an attribute; verify with the validator and the Divi judge), and that the questions must match word for word.
- **`cta-band.md`:** a full-width colored section with `et_pb_cta` (or heading + text + button), a contrasting button from `module_styles.et_pb_button[section_tone=dark]`.
- **`contact.md`:** `et_pb_contact_form` with `et_pb_contact_field` children (name, email, phone, message), `email` set from the brief, plus an optional `et_pb_map` with `et_pb_map_pin`. Include the note that map modules need a Google Maps API key configured on the site.
- **`team.md`:** `et_pb_team_member` × 3–4 with `name`, `position`, `image_url` and alt text.
- **`gallery.md`:** `et_pb_gallery` with `gallery_ids` from Media Library uploads, and `fullwidth`/`posts_number` options.
- **`video.md`:** `et_pb_video` with `src` (YouTube/Vimeo URL) and `image_src` overlay, plus a lazy-load note.

- [ ] **Step 2: Verify each recipe exactly as in Task 16, Step 3**

For `faq.md`, also:
- run `python3 -m unittest tests/test_divi_judge.py` after adding the FAQ example as `tests/fixtures/valid/faq-jsonld.txt` to `DiviJudgeTest.FILES`;
- confirm the rendered page contains valid JSON-LD with `python3 -c "import json,re,sys; …"` over the `curl`ed HTML.

- [ ] **Step 3: Commit**

```bash
git add Skill/divi-page-builder/recipes tests/fixtures/valid/faq-jsonld.txt tests/test_divi_judge.py
git commit -m "recipes: testimonials, pricing, FAQ + JSON-LD, CTA, contact, team, gallery, video"
```

---

### Task 19: Page assemblies, edit recipes, `page_edit.py`

**Files:**
- Create: `Skill/divi-page-builder/scripts/page_edit.py`
- Create: `Skill/divi-page-builder/recipes/pages/service-landing.md`, `local-seo-location.md`, `ppc-lead-gen.md`, `product-feature.md`
- Create: `Skill/divi-page-builder/recipes/edits/change-copy.md`, `insert-section.md`, `replace-section.md`, `restyle-to-tokens.md`
- Test: `tests/test_page_edit.py`

**Interfaces:**
- Consumes: `parse`, `Document.find`, `replace_span`, `serialize`, `escape_attr_value` (Task 2).
- Produces the CLI `page_edit.py PAGE <command>`, which writes to stdout (or `--out FILE`). Commands:
  - `outline`: one line per node, `<path>  admin_label=…  (N chars)`;
  - `extract PATH`;
  - `replace PATH FILE`;
  - `insert-after PATH FILE`;
  - `insert-before PATH FILE`;
  - `set-attr PATH NAME VALUE`, where VALUE is plain text that gets escaped;
  - `delete PATH`.

  Every mutating command leaves all bytes outside the target span unchanged.

- [ ] **Step 1: Write the failing tests**

`tests/test_page_edit.py`:
```python
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS

PAGE = FIXTURES / "valid" / "handwritten-landing.txt"
SRC = PAGE.read_text()


def run(*args):
    out = subprocess.run([sys.executable, str(SCRIPTS / "page_edit.py"), str(PAGE), *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return out.stdout


class PageEditTest(unittest.TestCase):
    def test_outline_lists_sections(self):
        out = run("outline")
        self.assertIn("et_pb_section[0]  admin_label=Hero", out)
        self.assertIn("et_pb_section[3]  admin_label=Closing", out)

    def test_set_attr_changes_only_that_attribute(self):
        out = run("set-attr", "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_heading[0]", "title", 'Miami "24/7" Plumber')
        self.assertEqual(out, SRC.replace('title="Emergency Plumber in Miami"', 'title="Miami %2224/7%22 Plumber"', 1))

    def test_insert_after_section_is_surgical(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write('[et_pb_section admin_label="New"][et_pb_row][et_pb_column type="4_4"][/et_pb_column][/et_pb_row][/et_pb_section]')
        out = run("insert-after", "et_pb_section[1]", f.name)
        Path(f.name).unlink()
        head_end = SRC.index('[et_pb_section specialty="on"')
        self.assertEqual(out[:head_end], SRC[:head_end])
        self.assertTrue(out.endswith(SRC[head_end:]))
        self.assertIn('admin_label="New"', out[head_end - 1:head_end + 120])

    def test_replace_and_delete(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("[et_pb_text]<p>Replaced</p>[/et_pb_text]")
        path = "et_pb_section[2] > et_pb_column[0] > et_pb_text[0]"
        out = run("replace", path, f.name)
        Path(f.name).unlink()
        self.assertIn("<p>Replaced</p>", out)
        self.assertNotIn("<p>Sidebar note.</p>", out)
        self.assertNotIn("admin_label=\"Closing\"", run("delete", "et_pb_section[3]"))

    def test_bad_path_fails_cleanly(self):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "page_edit.py"), str(PAGE), "extract", "et_pb_section[9]"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("no node at", proc.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 -m unittest tests/test_page_edit.py -v`
Expected: FAIL (`page_edit.py` doesn't exist).

- [ ] **Step 3: Implement `page_edit.py`**

`Skill/divi-page-builder/scripts/page_edit.py`:
```python
#!/usr/bin/env python3
"""Surgical edits to a Divi page: everything outside the targeted node stays byte-identical.

Usage: page_edit.py PAGE outline
       page_edit.py PAGE extract PATH
       page_edit.py PAGE replace PATH FILE | insert-after PATH FILE | insert-before PATH FILE
       page_edit.py PAGE set-attr PATH NAME VALUE      (VALUE is plain text; it is escaped for you)
       page_edit.py PAGE delete PATH
Options: --out FILE (default: stdout). PATH looks like: et_pb_section[1] > et_pb_row[0] > et_pb_column[2] > et_pb_blurb[0]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_shortcode import build_open_tag, escape_attr_value, parse, replace_span  # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("command", choices=["outline", "extract", "replace", "insert-after", "insert-before", "set-attr", "delete"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    src = Path(a.page).read_text(encoding="utf-8")
    doc = parse(src)
    if a.command == "outline":
        lines = [f"{path}  admin_label={n.value('admin_label')}  ({n.end - n.start} chars)" for n, path, _ in doc.walk()]
        result = "\n".join(lines) + "\n"
    else:
        if not a.args:
            ap.error("PATH is required")
        node = doc.find(a.args[0])
        if node is None:
            print(f"page_edit.py: no node at {a.args[0]}", file=sys.stderr)
            return 2
        if a.command == "extract":
            result = src[node.start:node.end]
        elif a.command == "delete":
            result = replace_span(src, node.start, node.end, "")
        elif a.command == "set-attr":
            if len(a.args) != 3:
                ap.error("set-attr needs PATH NAME VALUE")
            node.attrs[a.args[1]] = escape_attr_value(a.args[2], a.args[1])
            result = replace_span(src, node.start, node.open_end, build_open_tag(node))
        else:
            if len(a.args) != 2:
                ap.error(f"{a.command} needs PATH FILE")
            snippet = Path(a.args[1]).read_text(encoding="utf-8").strip()
            if a.command == "replace":
                result = replace_span(src, node.start, node.end, snippet)
            elif a.command == "insert-after":
                result = replace_span(src, node.end, node.end, snippet)
            else:
                result = replace_span(src, node.start, node.start, snippet)
    if a.out:
        Path(a.out).write_text(result, encoding="utf-8")
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
Note: `set-attr` rebuilds **only the opening tag**, so attribute order in that one tag is preserved, with a new attribute appended at the end.

- [ ] **Step 4: Run the tests**

Run: `python3 -m unittest tests/test_page_edit.py -v`
Expected: all PASS.

- [ ] **Step 5: Write the page assemblies**

Each assembly lists:
- the ordered sections, linking to the section recipes;
- the rhythm: alternate `section_tone` using `section_exemplars`, and the padding scale;
- H1/H2 placement;
- internal links;
- one complete ```divi example page, built from recipe examples, that passes the validator with `--tokens`.

The four assemblies:
- **`service-landing.md`:** hero-split → trust-bar → services-grid → alternating-features → stats → testimonials → faq → cta-band.
- **`local-seo-location.md`:** hero-centered (city in the H1) → services-grid → service-area-list → testimonials (local) → faq (local questions + JSON-LD) → contact (map) → cta-band.
- **`ppc-lead-gen.md`:** hero-split with the form in the right column (`et_pb_contact_form`) → trust-bar → process-steps → testimonials → cta-band. No navigation-heavy sections; one conversion goal.
- **`product-feature.md`:** hero-background-image → alternating-features → tabs → pricing → faq → cta-band.

Push each assembly with `push_local.sh`, screenshot it at 1440 and 390, check it, and delete it.

- [ ] **Step 6: Write the edit recipes**

Each one covers when to use it, the exact `page_edit.py` + `validate.py --baseline` command sequence, and a worked example on `tests/fixtures/valid/handwritten-landing.txt` showing the `diff -u` output (only the intended lines change):
- **`change-copy.md`:** `outline` → `set-attr` for attribute copy (titles, button text); `extract` → edit the inner HTML → `replace` for body copy.
- **`insert-section.md`:** compose the new section from a recipe, `insert-after` the anchor section, then validate with `--baseline original.txt`.
- **`replace-section.md`:** `extract` the old section, write the new one reusing its `admin_label` and design attributes from `section_exemplars`, then `replace`.
- **`restyle-to-tokens.md`:** run `validate.py --tokens` to list off-palette and off-brand warnings, then fix each with `set-attr` using the token values.

- [ ] **Step 7: Verify and commit**

Run:
```bash
python3 research/tools/check_doc_examples.py Skill/divi-page-builder
python3 -m unittest discover -s tests -v
```
Expected: `0 failing block(s)`, all PASS.

```bash
git add Skill/divi-page-builder/scripts/page_edit.py Skill/divi-page-builder/recipes tests/test_page_edit.py
git commit -m "recipes: page assemblies + edit recipes; page_edit.py surgical edit CLI"
```

---

### Task 20: `SKILL.md` and index completeness

**Files:**
- Create: `Skill/divi-page-builder/SKILL.md`
- Test: `tests/test_skill_index.py`

**Interfaces:**
- Consumes: every reference, recipe and script from Tasks 2-19.
- Produces: the skill entry point.

- [ ] **Step 1: Write the failing index test**

`tests/test_skill_index.py`:
```python
import re
import unittest

from _paths import SKILL


class SkillIndexTest(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text()

    def test_frontmatter(self):
        m = re.match(r"^---\nname: divi-page-builder\ndescription: (Use when .+)\n---\n", self.text)
        self.assertIsNotNone(m)
        self.assertLessEqual(len(m.group(1)), 500)

    def test_every_reference_and_recipe_is_indexed(self):
        files = [p.relative_to(SKILL).as_posix() for p in SKILL.rglob("*.md")
                 if p.name != "SKILL.md" and "reference/modules/et_pb_" not in p.as_posix()]
        missing = [f for f in files if f not in self.text]
        self.assertEqual(missing, [])

    def test_scripts_are_documented(self):
        for script in ("scripts/validate.py", "scripts/extract_tokens.py", "scripts/page_edit.py", "scripts/preview/preview.mjs", "scripts/publish.py"):
            self.assertIn(script, self.text)

    def test_short_enough(self):
        self.assertLess(len(self.text.split()), 1200)


if __name__ == "__main__":
    unittest.main()
```
Run: `python3 -m unittest tests/test_skill_index.py -v`
Expected: FAIL (`SKILL.md` doesn't exist).

- [ ] **Step 2: Write `SKILL.md`**

`Skill/divi-page-builder/SKILL.md`. After writing it, fill in the index with every file the test lists:
````markdown
---
name: divi-page-builder
description: Use when creating a new Divi 4 page or section, editing an existing Divi page's copy, sections or styling, or matching new content to a Divi site's existing design. Authors Divi's native shortcode (post_content) directly, validates it, previews it, and prepares it for publishing.
---

# Divi Page Builder

Write Divi 4 pages as raw shortcode (the exact `post_content` Divi stores), styled with the target site's own design tokens, and validated before anything is pushed. There are no templates: every section is composed from documented fields.

**Not for:** Divi 5 sites (block format), Theme Builder templates, WooCommerce product layouts.

## Workflow
1. **Intake:** get the content brief, the site URL, and whether this is a new page or an edit. For an edit, fetch the current page (`reference/publishing.md` → "Edit an existing page") and save it as `original.txt`.
2. **Tokens:** reuse the site's `tokens.json` if you have one; otherwise run `python3 scripts/extract_tokens.py --site URL --user USER --page ID --out tokens.json` with the password in `WP_APP_PASSWORD`. See `reference/design-tokens.md`.
3. **Plan:** map the brief to recipes (`recipes/README.md`, `recipes/pages/`). Show the user the section outline and get a yes before writing.
4. **Compose:** for each section, follow its recipe. Look up every module in `reference/modules/<slug>.md`, and take every color, font, spacing and button style from `tokens.json`.
5. **Validate:** `python3 scripts/validate.py page.txt --tokens tokens.json` (add `--baseline original.txt` for edits). Repeat until there are 0 errors; read every warning.
6. **Preview:** `node scripts/preview/preview.mjs render page.txt --tokens tokens.json --out preview.html` (or `serve` for live reload), then open it (`reference/preview.md`). Client Customizer and preset styling looks generic there.
7. **Publish:** `python3 scripts/publish.py draft page.txt --site URL --user USER --title "…"` uploads local images and saves a **draft** (it validates first). Share the printed `preview_url`; after the user approves, run `publish.py publish --page-id ID --yes` (`reference/publishing.md`). The WordPress draft is the authoritative visual check.

## Hard rules
- **Never invent attributes.** An attribute not on the module's page (or in its linked design families) does not exist; `validate.py` reports it as `E_UNKNOWN_ATTR`.
- **Styles:** use inline attributes, or `_module_preset` UUIDs listed in `tokens.json`. Never use preset UUIDs from anywhere else.
- **Escaping inside attribute values:** `"` → `%22`, `[` → `%91`, `]` → `%93` (`reference/page-format.md`).
- **Headings:** exactly one H1 per page, and no skipped heading levels.
- **Images:** upload to the site's Media Library and use that URL. Never hotlink. Always write `alt`.
- **Edits:** use `scripts/page_edit.py`. Everything you weren't asked to change stays byte-identical.
- **Testimonials, reviews, prices and stats:** only as provided in the brief. Never invent them.
- **Always push as a draft first.**

## Scripts
| script | purpose |
|---|---|
| `scripts/validate.py` | structure, attributes, value formats, tokens; `--baseline` for edits; `--json` |
| `scripts/extract_tokens.py` | site design tokens via REST (Application Password) + public CSS |
| `scripts/page_edit.py` | outline / extract / replace / insert / set-attr / delete, surgically |
| `scripts/preview/preview.mjs` | real-Divi preview in WordPress Playground: `serve`, `render`, `fetch-divi`, `doctor` |
| `scripts/publish.py` | `fetch` / `media` / `draft` / `publish` over REST with an Application Password |

## Reference index
| file | read it when |
|---|---|
| `reference/page-format.md` | writing any shortcode: grammar, escaping, what's stored where |
| `reference/structure.md` | choosing section, row and column layouts; parent/child modules |
| `reference/value-formats.md` | writing colors, fonts, spacing, icons, responsive/hover/sticky values |
| `reference/design-families.md` | styling: background, font, border, shadow, spacing, animation… |
| `reference/modules/README.md` | finding a module; each `reference/modules/<slug>.md` lists all of its fields |
| `reference/design-tokens.md` | extracting and applying a site's styles |
| `reference/publishing.md` | uploading images, creating drafts, editing live pages |
| `reference/preview.md` | local preview setup and limits |
| `recipes/README.md` | how recipes map tokens to fields |
| … one row per recipe file in recipes/sections, recipes/pages, recipes/edits … |
````
The last table row is an instruction to you, not text for the file. Replace it with one row per recipe file, e.g. `| \`recipes/sections/hero-split.md\` | two-column hero with H1, copy, CTA and image |`.

- [ ] **Step 3: Run the index test and the full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add Skill/divi-page-builder/SKILL.md tests/test_skill_index.py
git commit -m "skill: SKILL.md entry point with workflow, hard rules, full index"
```

---

### Task 21: Test the skill on fresh agents (baseline vs with-skill)

**Files:**
- Create: `research/skill-tests/brief-01-dental.md`
- Create: `research/skill-tests/results.md`
- Modify: whichever skill docs the runs show are unclear

**Interfaces:**
- Consumes: the whole skill, `recipes/sample-tokens.json`, `validate.py` and `push_local.sh`.

- [ ] **Step 1: Invoke the skill-writing skill**

Invoke `superpowers:writing-skills` and follow its testing guidance for this task.

- [ ] **Step 2: Write the test brief**

`research/skill-tests/brief-01-dental.md`:
```markdown
Site: Miami Rapid Plumbing's sister brand uses the same Divi design (use recipes/sample-tokens.json as its tokens).
Build a new landing page: "Emergency Water Heater Repair in Miami".
Content (use verbatim where given):
- H1: Emergency Water Heater Repair in Miami
- Intro: "No hot water? Our licensed technicians repair and replace tank and tankless water heaters the same day, 24/7."
- Services: Tank repair; Tankless repair; Same-day replacement; Annual maintenance
- Stats: 25+ years in business; 60-minute response; 4.9★ from 1,200 reviews
- FAQ: "How fast can you get here?" → "Within 60 minutes anywhere in Miami-Dade." / "Do you repair tankless heaters?" → "Yes, all major brands."
- Phone CTA: (305) 555-0100
Output: the page shortcode in a file named page.txt.
```

- [ ] **Step 3: Run the baseline (without the skill)**

Dispatch a fresh general-purpose subagent with the brief, `sample-tokens.json` and `SKILL.md` withheld, and the instruction "Produce Divi 4 page shortcode for this brief". Then run:
```bash
python3 Skill/divi-page-builder/scripts/validate.py <baseline page.txt> --tokens Skill/divi-page-builder/recipes/sample-tokens.json --json
```
Record in `results.md`:
- the error and warning counts by code;
- whether it has exactly one H1;
- whether it used the site's fonts and colors.

- [ ] **Step 4: Run with the skill**

Dispatch a fresh subagent with the brief and the instruction "Use the skill at Skill/divi-page-builder/SKILL.md", with file access to the skill. It should render the page with `scripts/preview/preview.mjs` and save a draft on `divi-test.local` with `scripts/publish.py` (give it a temporary Application Password via env, created as in Task 10 and deleted afterwards). Validate the same way, then screenshot the draft at 1440 and 390. Record the same metrics, plus:
- every point where the agent hesitated, guessed, or read the wrong file (from its transcript);
- visual problems seen in the screenshots.

Delete the page.

- [ ] **Step 5: Fix the docs where the agent stumbled, then re-run Step 4**

For each stumble, change the smallest doc that would have prevented it (SKILL.md wording, a recipe's token mapping, a module note in `research/tools/notes/` followed by regenerating the docs). Re-run Step 4 with a fresh agent.

**Success:**
- 0 validator errors;
- 0 `W_OFF_PALETTE_COLOR`/`W_OFF_BRAND_FONT` warnings;
- exactly one H1;
- the screenshot shows the sample brand's navy/orange, Montserrat/Lato look, and no phone overflow.

Record both runs in `results.md`.

- [ ] **Step 6: Final verification and commit**

Run:
```bash
python3 -m unittest discover -s tests -v
python3 research/tools/check_doc_examples.py Skill/divi-page-builder
research/tools/wp-local.sh post list --post_type=page --s="Plan Test" --format=count
```
Expected: all PASS, `0 failing block(s)`, and `0` leftover test pages.

```bash
git add research/skill-tests Skill/divi-page-builder research/tools/notes
git commit -m "skill: tested on fresh agents (baseline vs with-skill), docs fixed where agents stumbled"
```

---

### Task 22: `publish.py`: fetch, media, draft, publish over REST (added 2026-09-24)

> Added after the user widened the scope: the skill must also send pages to the target site (spec Addendum B). **Execution order:** run this task right after Task 14, before Task 15, because Tasks 20 and 21 depend on it.

**Files:**
- Create: `Skill/divi-page-builder/scripts/publish.py`
- Modify: `Skill/divi-page-builder/reference/publishing.md` (Task 10), adding a "Using publish.py" section at the top
- Test: `tests/test_publish.py`

**Interfaces:**
- Consumes:
  - `validate_source`, `load_schema` (Tasks 4-6);
  - `parse`, `serialize` (Task 2);
  - `divi_checks_values.IMAGE_ATTRS` (Task 5);
  - the REST facts recorded in `research/tools/notes/rest-experiments.md` (Task 10).
- Produces the CLI. The password always comes from env `WP_APP_PASSWORD`. Every command prints one JSON object on stdout.
  - `publish.py fetch --site URL --user USER --page-id ID --out FILE` writes `content.raw`, printing `{"id", "link", "out"}`.
  - `publish.py media --site URL --user USER FILE --alt TEXT` uploads one file, printing `{"id", "url"}`.
  - `publish.py draft PAGE --site URL --user USER --title TITLE [--slug S] [--page-id ID] [--tokens tokens.json] [--page-fields JSON]`:
    - validates first, and refuses on errors (exit 1, with no HTTP calls);
    - uploads local images (image attributes whose value starts with `file://`, `./` or `../`, resolved relative to PAGE's folder, with alt text from the module's `alt`/`title_text`) and rewrites them to Media Library URLs;
    - creates a draft, or updates `--page-id` and keeps it a draft;
    - prints `{"id", "status", "link", "preview_url", "edit_url", "uploaded": [...]}`.
  - `publish.py publish --site URL --user USER --page-id ID --yes` prints `{"id", "status", "link"}`. Without `--yes` it exits 1 and makes no HTTP call.
- Exit codes: 0 ok · 1 validation errors or refused · 2 usage, HTTP or I/O error.

- [ ] **Step 1: Write the failing tests**

They run against a fake WordPress REST server, plus a live check against `divi-test.local`.

`tests/test_publish.py`:
```python
import base64
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from _paths import FIXTURES, SCRIPTS, WP_LOCAL

PASSWORD = "abcd EFGH ijkl MNOP qrst UVWX"
GOOD = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()


class FakeWP(BaseHTTPRequestHandler):
    calls = []

    def log_message(self, *args):
        pass

    def _reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _record(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        FakeWP.calls.append({"method": self.command, "path": self.path, "headers": dict(self.headers), "body": body})
        expected = "Basic " + base64.b64encode(f"editor:{PASSWORD}".encode()).decode()
        return self.headers.get("Authorization") == expected, body

    def do_GET(self):
        ok, _ = self._record()
        if not ok:
            return self._reply(401, {"code": "rest_not_logged_in", "message": "You are not currently logged in."})
        if self.path.startswith("/wp-json/wp/v2/pages/101"):
            return self._reply(200, {"id": 101, "link": "http://fake/?page_id=101", "content": {"raw": GOOD}})
        self._reply(404, {"code": "rest_no_route", "message": "No route"})

    def do_POST(self):
        ok, body = self._record()
        if not ok:
            return self._reply(401, {"code": "rest_not_logged_in", "message": "You are not currently logged in."})
        port = self.server.server_address[1]
        if self.path == "/wp-json/wp/v2/media":
            return self._reply(201, {"id": 55, "source_url": f"http://127.0.0.1:{port}/wp-content/uploads/hero.jpg"})
        if self.path == "/wp-json/wp/v2/media/55":
            return self._reply(200, {"id": 55})
        if self.path == "/wp-json/wp/v2/pages":
            return self._reply(201, {"id": 101, "status": "draft", "link": f"http://127.0.0.1:{port}/?page_id=101"})
        if self.path == "/wp-json/wp/v2/pages/101":
            status = json.loads(body or b"{}").get("status", "draft")
            return self._reply(200, {"id": 101, "status": status, "link": f"http://127.0.0.1:{port}/?page_id=101"})
        self._reply(404, {"code": "rest_no_route", "message": "No route"})


class PublishFakeServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeWP)
        cls.site = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        FakeWP.calls.clear()

    def run_cli(self, *args, password=PASSWORD):
        env = dict(os.environ, WP_APP_PASSWORD=password)
        return subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), *args], capture_output=True, text=True, env=env)

    def test_draft_uploads_local_images_and_creates_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "hero.jpg").write_bytes(b"\xff\xd8\xff fake jpeg")
            page = Path(tmp) / "page.txt"
            page.write_text(GOOD.replace("https://client.example/wp-content/uploads/2026/09/plumber.jpg", "./hero.jpg"))
            proc = self.run_cli("draft", str(page), "--site", self.site, "--user", "editor", "--title", "Test Page")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["id"], 101)
        self.assertEqual(out["status"], "draft")
        self.assertIn("preview=true", out["preview_url"])
        self.assertEqual(len(out["uploaded"]), 1)
        media, alt, create = FakeWP.calls
        self.assertEqual(media["path"], "/wp-json/wp/v2/media")
        self.assertIn('filename="hero.jpg"', media["headers"]["Content-Disposition"])
        self.assertEqual(json.loads(alt["body"])["alt_text"], "Plumber repairing a burst pipe")
        sent = json.loads(create["body"])
        self.assertEqual(sent["status"], "draft")
        self.assertEqual(sent["meta"], {"_et_pb_use_builder": "on"})
        self.assertIn("/wp-content/uploads/hero.jpg", sent["content"])
        self.assertNotIn("./hero.jpg", sent["content"])

    def test_draft_update_keeps_draft(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T", "--page-id", "101")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        (call,) = FakeWP.calls
        self.assertEqual(call["path"], "/wp-json/wp/v2/pages/101")
        self.assertEqual(json.loads(call["body"])["status"], "draft")

    def test_draft_refuses_invalid_page(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write('[et_pb_section][et_pb_row][et_pb_column type="4_4"][et_pb_text colour="red"]x[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]')
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("E_UNKNOWN_ATTR", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_publish_requires_yes(self):
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(FakeWP.calls, [])
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["status"], "publish")

    def test_fetch_writes_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "original.txt"
            proc = self.run_cli("fetch", "--site", self.site, "--user", "editor", "--page-id", "101", "--out", str(out))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(out.read_text(), GOOD)

    def test_http_error_exit_2_without_leaking_password(self):
        proc = self.run_cli("fetch", "--site", self.site, "--user", "editor", "--page-id", "101", "--out", "/tmp/x.txt",
                            password="wrong pass")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("rest_not_logged_in", proc.stderr)
        for stream in (proc.stdout, proc.stderr):
            self.assertNotIn("wrong pass", stream)
            self.assertNotIn(PASSWORD, stream)

    def test_missing_password_is_usage_error(self):
        proc = self.run_cli("fetch", "--site", self.site, "--user", "editor", "--page-id", "101", "--out", "/tmp/x.txt",
                            password="")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("WP_APP_PASSWORD", proc.stderr)


class PublishLiveTest(unittest.TestCase):
    """Round-trip against divi-test.local; skipped when the local site is unavailable."""

    def wp(self, *args):
        out = subprocess.run([str(WP_LOCAL), *args], capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            raise unittest.SkipTest(f"local site unavailable: {out.stderr[-200:]}")
        return out.stdout.strip()

    def test_draft_roundtrip_on_local_site(self):
        user = self.wp("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        password = self.wp("user", "application-password", "create", user, "publish-test", "--porcelain")
        page_id = None
        try:
            env = dict(os.environ, WP_APP_PASSWORD=password)
            proc = subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), "draft", str(FIXTURES / "valid" / "handwritten-landing.txt"),
                                   "--site", "http://divi-test.local", "--user", user, "--title", "Plan Test: publish.py"],
                                  capture_output=True, text=True, env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            page_id = json.loads(proc.stdout)["id"]
            self.assertEqual(self.wp("post", "get", str(page_id), "--field=post_status"), "draft")
            self.assertEqual(self.wp("post", "meta", "get", str(page_id), "_et_pb_use_builder"), "on")
            self.assertEqual(self.wp("post", "get", str(page_id), "--field=post_content"), GOOD.strip())
        finally:
            if page_id:
                self.wp("post", "delete", str(page_id), "--force")
            uuid = self.wp("user", "application-password", "list", user, "--name=publish-test", "--field=uuid")
            self.wp("user", "application-password", "delete", user, uuid)


if __name__ == "__main__":
    unittest.main()
```
Run: `python3 -m unittest discover -s tests -p 'test_publish.py' -v`
Expected: FAIL (`publish.py` doesn't exist).

- [ ] **Step 2: Implement `publish.py`**

`Skill/divi-page-builder/scripts/publish.py`:
```python
#!/usr/bin/env python3
"""Send Divi pages to WordPress over the REST API, authenticated with an Application Password.

  publish.py fetch   --site URL --user USER --page-id ID --out FILE
  publish.py media   --site URL --user USER FILE --alt TEXT
  publish.py draft   PAGE --site URL --user USER --title TITLE [--slug S] [--page-id ID] [--tokens tokens.json] [--page-fields JSON]
  publish.py publish --site URL --user USER --page-id ID --yes

The password is read from env WP_APP_PASSWORD and never printed. `draft` validates the page first and
refuses on errors; image attributes pointing at local files (file://, ./, ../) are uploaded to the
Media Library and rewritten. Pages are saved as drafts; `publish` requires --yes (after user approval).
Exit status: 0 ok, 1 validation errors or refused, 2 usage/HTTP/I-O error.
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from divi_checks_values import IMAGE_ATTRS  # noqa: E402
from divi_schema import load_schema  # noqa: E402
from divi_shortcode import escape_attr_value, parse, serialize  # noqa: E402
from validate import validate_source  # noqa: E402

LOCAL_PREFIXES = ("file://", "./", "../")


class PublishError(Exception):
    pass


class WordPress:
    def __init__(self, site: str, user: str, password: str):
        self.base = site.rstrip("/") + "/wp-json/wp/v2"
        self.site = site.rstrip("/")
        self._auth = "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()

    def request(self, method: str, path: str, json_body=None, data: bytes = None, headers=None) -> dict:
        hdrs = {"Authorization": self._auth, "Accept": "application/json", "User-Agent": "divi-page-builder/1.0"}
        if json_body is not None:
            data = json.dumps(json_body).encode()
            hdrs["Content-Type"] = "application/json"
        hdrs.update(headers or {})
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read() or b"{}")
        except urllib.error.HTTPError as exc:
            try:
                err = json.loads(exc.read())
                detail = f"{err.get('code', '')}: {err.get('message', '')}"
            except ValueError:
                detail = exc.reason
            raise PublishError(f"HTTP {exc.code} on {method} {path} — {detail}") from None
        except urllib.error.URLError as exc:
            raise PublishError(f"cannot reach {self.site}: {exc.reason}") from None


def upload_media(wp: WordPress, path: Path, alt: str) -> dict:
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    media = wp.request("POST", "/media", data=path.read_bytes(),
                       headers={"Content-Type": ctype, "Content-Disposition": f'attachment; filename="{path.name}"'})
    if alt:
        wp.request("POST", f"/media/{media['id']}", json_body={"alt_text": alt})
    return {"id": media["id"], "url": media["source_url"], "file": str(path)}


def _local_path(value: str, base_dir: Path):
    if value.startswith("file://"):
        return Path(unquote(urlparse(value).path))
    if value.startswith(("./", "../")):
        return (base_dir / value).resolve()
    return None


def upload_local_images(wp: WordPress, source: str, base_dir: Path):
    doc = parse(source)
    uploaded, cache = [], {}
    for node, _path, _parent in doc.walk():
        for attr in list(node.attrs):
            if attr not in IMAGE_ATTRS and not attr.endswith("_image"):
                continue
            local = _local_path(node.value(attr), base_dir)
            if local is None:
                continue
            if not local.is_file():
                raise PublishError(f"{node.tag} {attr}: local image not found: {local}")
            if local not in cache:
                alt = node.value("alt") or node.value("title_text") or local.stem.replace("-", " ")
                cache[local] = upload_media(wp, local, alt)
                uploaded.append(cache[local])
            node.attrs[attr] = escape_attr_value(cache[local]["url"], attr)
    return serialize(doc), uploaded


def _preview_url(link: str) -> str:
    return link + ("&" if "?" in link else "?") + "preview=true"


def _print(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def cmd_fetch(wp, a):
    page = wp.request("GET", f"/pages/{a.page_id}?context=edit")
    Path(a.out).write_text(page["content"]["raw"], encoding="utf-8")
    _print({"id": page["id"], "link": page.get("link", ""), "out": a.out})
    return 0


def cmd_media(wp, a):
    _print(upload_media(wp, Path(a.file), a.alt))
    return 0


def cmd_draft(wp, a):
    page_path = Path(a.page)
    source = page_path.read_text(encoding="utf-8")
    tokens = json.loads(Path(a.tokens).read_text()) if a.tokens else None
    errors = [f for f in validate_source(source, load_schema(), tokens=tokens) if f.level == "error"]
    if errors:
        for f in errors:
            print(f"{a.page}:{f.line}:{f.col} {f.code} {f.path}: {f.message}", file=sys.stderr)
        print(f"refusing to save: {len(errors)} validation error(s); run scripts/validate.py for details", file=sys.stderr)
        return 1
    content, uploaded = upload_local_images(wp, source, page_path.resolve().parent)
    body = {"title": a.title, "content": content, "status": "draft", "meta": {"_et_pb_use_builder": "on"}}
    if a.slug:
        body["slug"] = a.slug
    body.update(json.loads(a.page_fields) if a.page_fields else {})
    page = wp.request("POST", f"/pages/{a.page_id}" if a.page_id else "/pages", json_body=body)
    _print({"id": page["id"], "status": page.get("status", "draft"), "link": page.get("link", ""),
            "preview_url": _preview_url(page.get("link", "")),
            "edit_url": f"{wp.site}/wp-admin/post.php?post={page['id']}&action=edit", "uploaded": uploaded})
    return 0


def cmd_publish(wp, a):
    if not a.yes:
        print("refusing to publish without --yes (publish only after the user approves the draft)", file=sys.stderr)
        return 1
    page = wp.request("POST", f"/pages/{a.page_id}", json_body={"status": "publish"})
    _print({"id": page["id"], "status": page.get("status", ""), "link": page.get("link", "")})
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--site", required=True)
    common.add_argument("--user", required=True)
    p = sub.add_parser("fetch", parents=[common])
    p.add_argument("--page-id", type=int, required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("media", parents=[common])
    p.add_argument("file")
    p.add_argument("--alt", required=True)
    p = sub.add_parser("draft", parents=[common])
    p.add_argument("page")
    p.add_argument("--title", required=True)
    p.add_argument("--slug")
    p.add_argument("--page-id", type=int)
    p.add_argument("--tokens")
    p.add_argument("--page-fields", help="extra JSON fields for the page, e.g. a template (see reference/publishing.md)")
    p = sub.add_parser("publish", parents=[common])
    p.add_argument("--page-id", type=int, required=True)
    p.add_argument("--yes", action="store_true")
    a = ap.parse_args(argv)
    password = os.environ.get("WP_APP_PASSWORD", "")
    if not password:
        print("publish.py: set WP_APP_PASSWORD to a WordPress Application Password", file=sys.stderr)
        return 2
    wp = WordPress(a.site, a.user, password)
    try:
        return {"fetch": cmd_fetch, "media": cmd_media, "draft": cmd_draft, "publish": cmd_publish}[a.command](wp, a)
    except (PublishError, OSError, ValueError, KeyError) as exc:
        print(f"publish.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 3: Run the tests**

Run: `python3 -m unittest discover -s tests -p 'test_publish.py' -v`
Expected: all PASS. `PublishLiveTest` runs against `divi-test.local`, or is skipped if the site is down.

If the live test shows that WordPress altered `post_content` (for example by stripping characters), don't loosen the assertion. Record the difference in `research/tools/notes/rest-experiments.md`, and make the smallest correct fix: either in `publish.py`, if the content must be sent differently, or in `reference/page-format.md`, if authors must avoid a construct.

- [ ] **Step 4: Document it in `reference/publishing.md`**

Add a "Using publish.py" section at the top:
- one example per command;
- the draft-first rule;
- `--yes` only after the user approves the draft;
- how local images are referenced (`./images/hero.jpg`) and uploaded;
- `--page-fields` for the layout field found in Task 10 (e.g. a template);
- exit codes.

Keep the raw `curl` flow below it as the reference for how it works.

- [ ] **Step 5: Commit**

```bash
git add Skill/divi-page-builder/scripts/publish.py Skill/divi-page-builder/reference/publishing.md tests/test_publish.py
git commit -m "publish: fetch/media/draft/publish over REST with validation-first drafts"
```

