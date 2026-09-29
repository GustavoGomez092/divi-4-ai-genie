# Divi 5 Support Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Divi Genie build, validate, preview, edit and publish **Divi 5** pages as well as it does Divi 4 pages, from the same skill. Test it to the same standard: Divi as judge, generated docs with coverage gates, live REST publishing, measured preview fidelity and fresh-agent tests.

**Architecture:** One skill that detects the version (`divi_format.py`). Divi 4 code stays byte-for-byte unchanged. Divi 5 gets parallel modules:
- `divi5_blocks.py` parses and serializes blocks;
- `divi5_schema.py` reads the compiled `schema5/`;
- `divi5_checks_*.py` hold the Divi 5 validator checks;
- `tokens5_*` extract design tokens;
- recipes and references live under `reference/divi5/` and `recipes/divi5/`.

The shared CLIs (`validate.py`, `publish.py`, `page_edit.py`, `extract_tokens.py`, `preview.py`) dispatch on content format or site version. Maintainer tools (schema dump, family curation, doc generator, converter, judge harness) live in `research/tools/divi5/`.

**Tech Stack:**
- Python 3.9+ standard library only for shipped scripts, with `unittest`.
- PHP via WP-CLI on the LocalWP site `divi-5-test.local` (Divi 5.13.1, WordPress 7.1.2). Use `research/tools/wp-local.sh` with `LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH="$HOME/Local Sites/divi-5-test/app/public"`.
- Node ≥ 20 and WordPress Playground for the exact preview.

**Spec:** `docs/superpowers/specs/2026-09-28-divi5-support-design.md`. Read it first, together with the research it cites in `research/divi5/*.md`. The Divi 4 spec and plan (`docs/superpowers/specs/2026-09-24-…`, `docs/superpowers/plans/2026-09-24-…`) describe the patterns every Divi 5 counterpart mirrors.

## Global Constraints

- **Dependencies:** shipped scripts (`Skill/divi-page-builder/scripts/*.py`) use the Python 3.9+ standard library only. No pip installs.
- **Divi 4 is untouched:** every existing test must still pass unchanged. Don't edit Divi 4 modules (`divi_shortcode.py`, `divi_schema.py`, `divi_checks_*.py`, `schema/`, `tokens_from_*.py`, `divi_render/`) except to add a dispatch hook. Where a shared CLI changes, the Divi 4 path must be identical in behaviour and output.
- **Canonical Divi 5 serialization** is WordPress's `serialize_block_attributes()` (`wp-includes/blocks.php:1705`): `wp_json_encode(attrs, JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)` then `strtr` with `\\`→`\u005c`, `--`→`\u002d\u002d`, `<`→`\u003c`, `>`→`\u003e`, `&`→`\u0026`, `\"`→`\u0022`. Blocks are `<!-- wp:divi/<name> {json} -->…<!-- /wp:divi/<name> -->`, self-closing `<!-- wp:divi/<name> {json} /-->` when there is no inner content, with no whitespace between blocks and the page wrapped in `<!-- wp:divi/placeholder -->…<!-- /wp:divi/placeholder -->`.
- **Layout form for new content** (spec §3.1):
  - structure blocks carry `module.decoration.layout.desktop.value.display = "block"`;
  - rows carry `module.advanced.columnStructure.desktop.value`;
  - columns carry `module.advanced.type.desktop.value` (e.g. `"1_2"`).
- **`builderVersion`:** every block the skill creates gets `builderVersion` = the site's Divi version (`tokens.json → site.divi_version`), defaulting to `schema5/_meta.json → divi_version`.
- **Module scope:** everything in `research/divi5-schema/` except `scope` ∈ {woocommerce, integration, theme-builder, internal}. The compiled schema records each module's `scope`.
- **Credentials:** never print or write credentials (Application Passwords, ET username/api_key). Live tests create throwaway Application Passwords on `divi-5-test.local` and delete them in `tearDown`.
- **Divi assets:** never commit Divi's code, CSS, JS, zips or rendered pages containing its CSS. Caches live in `PP_CACHE_DIR` (default `~/.cache/divi-page-builder`).
- **Live tests:**
  - gate them with `@live5_only` (Task 1), which needs `PP_LIVE_TESTS=1` and skips with a clear reason when `divi-5-test.local` is unreachable;
  - they touch only `divi-5-test.local`, create objects titled `D5TEST …` and delete them;
  - `wp` writes pass `--user=<admin>`.
- **Python HTTPS on this machine:** the system python.org 3.10 has no CA bundle, so run HTTPS tests/tools with `SSL_CERT_FILE=/etc/ssl/cert.pem`. The local sites are `http://`.
- **Test command (offline):** `python3 -m unittest discover -s tests`. **With live:** `PP_LIVE_TESTS=1 python3 -m unittest discover -s tests`.
- **Commit style:** `<area>: <summary>` (e.g. `divi5: block parser …`), ending with the `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` line.

## Review Focus

1. **Non-canonical but valid input** (Visual Builder output with `\n\n` between blocks and `\\` escapes, converter output with empty open/close pairs, pages without the placeholder wrapper) must parse, validate and round-trip byte-exactly. Only edited blocks may change. Tests in Tasks 2 and 15.
2. **PHP JSON quirks in canonical output:** PHP decodes `{}` to an empty array and re-encodes it as `[]`, and turns `{"0":…,"1":…}` into a list. U+2028/U+2029 are escaped by `json_encode`. Our canonical writer must equal WordPress's round-trip output, not Python's naive `json.dumps`. Tests in Task 2, with the live judge in Task 7.
3. **A Divi 4 page on a Divi 5 site, or Divi 5 content on a Divi 4 site:** validator, `publish.py` and `page_edit.py` must refuse with a clear message, not silently do the wrong thing. Tests in Tasks 4, 10 and 15.
4. **Unknown preset, `gcid` or `gvid` ids:** an unknown `modulePreset` silently drops the site's default preset styling, so the validator must warn, and tokens must carry every id the site reveals. Tests in Tasks 6 and 11.
5. **REST publish where the builder meta doesn't stick:** after `draft` the tool must read back `_et_pb_use_builder` and fail loudly if it isn't `on`, never report success. Test in Task 10.

## File Structure

| Path | Responsibility | Task |
|---|---|---|
| `tests/_paths.py` (modify) | Divi 5 paths, `WP_LOCAL5` env, `live5_only` | 1 |
| `scripts/divi_format.py` | content-format and site-version detection | 1 |
| `scripts/divi5_blocks.py` | block parse/serialize, canonical JSON, paths, attr get/set, `$variable()$` | 2 |
| `research/tools/divi5/families5.json` | curated value types for shared option groups | 3 |
| `research/tools/divi5/build_schema5.py` | dump + families → `scripts/schema5/` with coverage gate | 3 |
| `scripts/schema5/*.json` | compiled Divi 5 schema (generated) | 3 |
| `scripts/divi5_schema.py` | load schema5 and resolve attribute paths to leaf specs | 3 |
| `scripts/divi5_checks_structure.py` | nesting, section types, columns, headings | 4 |
| `scripts/validate.py` (modify) | format dispatch | 4 |
| `scripts/divi5_checks_values.py` | attribute paths, breakpoints/states, value types, escaping, presets/variables, images | 5 |
| `scripts/divi5_checks_tokens.py` | off-token colors/fonts/spacing | 6 |
| `research/tools/divi5/judge.php`, `tests/test_divi5_judge.py` | Divi as judge | 7 |
| `research/tools/divi5/generate_docs5.py`, `reference/divi5/modules/*`, `reference/divi5/design-families.md` | generated docs + coverage | 8 |
| `reference/divi5/{page-format,structure,value-formats}.md` | hand-written references | 9 |
| `scripts/publish.py`, `scripts/local_media.py` (modify), `reference/publishing.md` (modify) | Divi 5 publishing | 10 |
| `scripts/tokens5_from_blocks.py` | tokens from block content | 11 |
| `scripts/tokens5_from_html.py`, `scripts/extract_tokens.py` (modify), `reference/design-tokens.md` (modify) | tokens from public HTML/CSS; dispatch | 12 |
| `tests/test_divi5_tokens_fidelity.py`, `research/tools/divi5/fidelity_setup.php` | live token fidelity | 13 |
| `scripts/preview/*` (modify), `scripts/preview.py` (modify), `reference/preview.md` (modify) | Playground preview for Divi 5 | 14 |
| `scripts/page_edit.py` (modify), `recipes/divi5/edits/*` | block edits | 15 |
| `recipes/divi5/sections/*.md`, `recipes/divi5/pages/*.md`, `recipes/divi5/sample-tokens.json` | Divi 5 worked examples | 16–18 |
| `SKILL.md`, `README.md` (modify) | skill entry and docs | 19 |
| `research/skill-tests/divi5-*` | fresh-agent test | 20 |
| `research/divi5/python-renderer-spike.md` | measured renderer decision | 21 |

All script paths are relative to `Skill/divi-page-builder/`.

---

### Task 1: Divi 5 test harness and format detection

**Files:**
- Modify: `tests/_paths.py`
- Create: `Skill/divi-page-builder/scripts/divi_format.py`
- Test: `tests/test_divi_format.py`, `tests/test_live_gating.py` (extend known list)

**Interfaces:**
- Produces:
  - `_paths.FIXTURES5 = FIXTURES / "divi5"`, `_paths.SCHEMA5_RAW = ROOT / "research" / "divi5-schema"`, `_paths.TOOLS5 = TOOLS / "divi5"`;
  - `_paths.wp5(*args, timeout=120) -> subprocess.CompletedProcess`, which runs `wp-local.sh` with `LOCAL_SITE_ID=fTZ3hcgdI` and `LOCAL_SITE_PATH=$HOME/Local Sites/divi-5-test/app/public`;
  - `_paths.live5_only`, a decorator that skips unless `PP_LIVE_TESTS=1` and `http://divi-5-test.local/` answers;
  - `_paths.d5_fixtures() -> list[Path]`, all `tests/fixtures/divi5/**/*.html` sorted;
  - `divi_format.detect_content(text: str) -> str`, one of `"shortcode" | "blocks" | "mixed" | "empty"`;
  - `divi_format.major_from_version(v: str) -> int | None`;
  - `divi_format.parse_style_css_version(css_text: str) -> str | None`;
  - `divi_format.detect_site(url: str, fetch=None) -> dict`, returning `{"divi_version": str|None, "divi_major": int|None, "evidence": str}`. `fetch(url)->bytes` is injectable for tests.

- [ ] **Step 1: Write the failing tests** (`tests/test_divi_format.py`)

```python
import unittest

from _paths import FIXTURES, d5_fixtures
from divi_format import detect_content, detect_site, major_from_version, parse_style_css_version


class DetectContentTest(unittest.TestCase):
    def test_shortcode_fixtures(self):
        for p in sorted((FIXTURES / "valid").glob("*.txt")):
            self.assertEqual(detect_content(p.read_text()), "shortcode", p.name)

    def test_block_fixtures(self):
        files = d5_fixtures()
        self.assertGreaterEqual(len(files), 37)
        for p in files:
            self.assertEqual(detect_content(p.read_text()), "blocks", p.name)

    def test_mixed_and_empty(self):
        self.assertEqual(detect_content('<!-- wp:divi/text {} /-->[et_pb_section][/et_pb_section]'), "mixed")
        self.assertEqual(detect_content("   \n"), "empty")
        self.assertEqual(detect_content("<p>plain</p>"), "empty")

    def test_d4_shortcode_inside_d5_text_is_still_blocks(self):
        # Shortcode text *inside* a block's JSON is content, not D4 structure.
        src = '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"[et_pb_x]"}}}} /-->'
        self.assertEqual(detect_content(src), "blocks")


class VersionTest(unittest.TestCase):
    def test_major(self):
        self.assertEqual(major_from_version("5.13.1"), 5)
        self.assertEqual(major_from_version("4.27.9"), 4)
        self.assertIsNone(major_from_version(""))
        self.assertIsNone(major_from_version("abc"))

    def test_style_css(self):
        css = "/*\nTheme Name: Divi\nVersion: 5.13.1\nAuthor: Elegant Themes\n*/"
        self.assertEqual(parse_style_css_version(css), "5.13.1")
        self.assertIsNone(parse_style_css_version("body{}"))

    def test_detect_site_style_css(self):
        pages = {"https://x.test/wp-content/themes/Divi/style.css": b"/*\nVersion: 5.2.0\n*/"}
        got = detect_site("https://x.test/", fetch=lambda u: pages[u])
        self.assertEqual((got["divi_version"], got["divi_major"]), ("5.2.0", 5))

    def test_detect_site_falls_back_to_assets(self):
        home = (b'<link href="https://x.test/wp-content/themes/Divi/includes/builder-5/visual-builder/'
                b'build/a.css?ver=5.1.0">')
        def fetch(u):
            if u.endswith("style.css"):
                raise OSError("404")
            return home
        got = detect_site("https://x.test", fetch=fetch)
        self.assertEqual(got["divi_major"], 5)
        self.assertEqual(got["divi_version"], "5.1.0")
```

- [ ] **Step 2: Run to verify they fail**

Run: `python3 -m unittest tests.test_divi_format -v` (from repo root, `cd tests` is not needed because `discover`-style imports work via `_paths`; run as `python3 -m unittest discover -s tests -p test_divi_format.py -v`).
Expected: ImportError, because `divi_format` and `d5_fixtures` don't exist yet.

- [ ] **Step 3: Implement `_paths.py` additions**

```python
FIXTURES5 = FIXTURES / "divi5"
SCHEMA5_RAW = ROOT / "research" / "divi5-schema"
TOOLS5 = TOOLS / "divi5"
LOCAL5_ENV = {"LOCAL_SITE_ID": "fTZ3hcgdI",
              "LOCAL_SITE_PATH": str(Path.home() / "Local Sites" / "divi-5-test" / "app" / "public")}
SITE5_URL = "http://divi-5-test.local"


def d5_fixtures():
    return sorted(FIXTURES5.rglob("*.html"))


def wp5(*args, timeout=120):
    import subprocess
    env = dict(os.environ, **LOCAL5_ENV)
    return subprocess.run([str(WP_LOCAL), *map(str, args)], capture_output=True, text=True, env=env,
                          timeout=timeout)


def _site5_up() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen(SITE5_URL + "/", timeout=5)
        return True
    except Exception:
        return False


LIVE5_SKIP_REASON = ("live test: touches the local Divi 5 site (divi-5-test.local via wp-local.sh); "
                     "set PP_LIVE_TESTS=1 and start the site to run it")


def live5_only(obj):
    return unittest.skipUnless(live_tests_enabled() and _site5_up(), LIVE5_SKIP_REASON)(obj)
```

- [ ] **Step 4: Implement `divi_format.py`**

```python
#!/usr/bin/env python3
"""Tell Divi 4 shortcode from Divi 5 block content, and find a site's Divi version.

  python3 divi_format.py content PAGE      -> shortcode | blocks | mixed | empty
  python3 divi_format.py site URL          -> JSON {divi_version, divi_major, evidence}
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from typing import Callable, Optional

_BLOCK_OPEN = re.compile(r"<!--\s+wp:divi/[a-z0-9-]+")
_JSON_BLOCK = re.compile(r"<!--\s+/?wp:[^>]*?-->", re.S)
_SHORTCODE = re.compile(r"\[et_pb_[a-z0-9_]+[\s\]/]")
_VERSION = re.compile(r"^\s*Version:\s*([0-9][0-9.]*)", re.M)
_ASSET_VER = re.compile(r"/themes/Divi/[^\"'?\s]*\?ver=([0-9]+\.[0-9][0-9.]*)")


def detect_content(text: str) -> str:
    has_blocks = bool(_BLOCK_OPEN.search(text))
    outside = _JSON_BLOCK.sub(" ", text) if has_blocks else text
    has_shortcode = bool(_SHORTCODE.search(outside))
    if has_blocks and has_shortcode:
        return "mixed"
    if has_blocks:
        return "blocks"
    if has_shortcode:
        return "shortcode"
    return "empty"


def major_from_version(v: Optional[str]) -> Optional[int]:
    m = re.match(r"^\s*(\d+)\.", v or "")
    return int(m.group(1)) if m else None


def parse_style_css_version(css_text: str) -> Optional[str]:
    m = _VERSION.search(css_text[:4000])
    return m.group(1) if m else None


def _default_fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "divi-page-builder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def detect_site(url: str, fetch: Optional[Callable[[str], bytes]] = None) -> dict:
    fetch = fetch or _default_fetch
    base = url.rstrip("/")
    try:
        v = parse_style_css_version(fetch(base + "/wp-content/themes/Divi/style.css").decode("utf-8", "replace"))
        if v:
            return {"divi_version": v, "divi_major": major_from_version(v), "evidence": "style.css"}
    except Exception:
        pass
    try:
        html = fetch(base + "/").decode("utf-8", "replace")
    except Exception as exc:
        return {"divi_version": None, "divi_major": None, "evidence": f"unreachable: {exc}"}
    versions = _ASSET_VER.findall(html)
    v = max(versions, key=lambda s: tuple(int(x) for x in s.split(".") if x.isdigit())) if versions else None
    major = major_from_version(v)
    if "/includes/builder-5/" in html:
        major = 5
    return {"divi_version": v, "divi_major": major, "evidence": "assets" if (v or major) else "none"}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] not in ("content", "site"):
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "content":
        with open(argv[1], encoding="utf-8") as fh:
            print(detect_content(fh.read()))
    else:
        print(json.dumps(detect_site(argv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Note: the detection logic of `research/tools/divi5/detect_divi.py` (R7) is the reference. Read it and carry over any additional marker it uses that this version lacks, adding a test for it.

- [ ] **Step 5: Run tests, confirm they pass, and run the whole suite** (`python3 -m unittest discover -s tests`). Expected: all pass, the D4 suite unchanged.

- [ ] **Step 6: Commit** `divi5: test harness paths, live5 gate, divi_format detection`

---

### Task 2: `divi5_blocks.py`: parse, canonical serialize, paths, attribute access

**Files:**
- Create: `Skill/divi-page-builder/scripts/divi5_blocks.py`
- Test: `tests/test_divi5_blocks.py`

**Interfaces:**
- Consumes: `_paths.d5_fixtures()`.
- Produces:
  - `Problem(code, message, offset)` (same fields as `divi_shortcode.Problem`);
  - `Block` dataclass: `name` (e.g. `"divi/text"`), `attrs: dict`, `raw_json: str` (exact source text of the JSON, `""` if none), `children: list[Block | Freeform]`, `start`, `open_end`, `close_start: int | None`, `end`, `self_closing: bool`, `dirty: bool = False`;
  - `Freeform(value, start, end)`, text between blocks, kept verbatim;
  - `Document(source, nodes, problems)` with `.line_col(offset)`, `.walk()` yielding `(block, path, parent)` where path looks like `placeholder[0] > section[2] > row[0] > column[1] > blurb[0]` (names shown without `divi/`), `.find(path) -> Block | None`, and `.sections() -> list[Block]` (sections under the placeholder, or top-level if there's no placeholder);
  - `parse(source) -> Document`;
  - `serialize(doc_or_nodes) -> str`, byte-exact for unmodified blocks (source spans reused); a block with `dirty=True` or `start == -1` is emitted canonically;
  - `canonical_json(attrs) -> str`, byte-identical to WordPress `serialize_block_attributes()` after PHP's decode/encode;
  - `render_block(block) -> str`, the canonical text of one block and its children;
  - `new_block(name, attrs=None, children=None) -> Block` (name gets a `divi/` prefix if missing);
  - `get_attr(block, dotted: str, breakpoint="desktop", state="value", default=None)`;
  - `set_attr(block, dotted, value, breakpoint="desktop", state="value")`, which sets `dirty=True`;
  - `iter_leaves(attrs) -> Iterator[(path: str, breakpoint: str | None, state: str | None, value)]`, where `path` is the dotted attrName path before the breakpoint level (e.g. `title.decoration.font.font`) and `value` is the object/scalar under the state. Breakpoints are {desktop, tablet, phone, phoneWide, tabletWide, widescreen, ultraWide}; states are {value, hover, sticky, focus, checked, active, disabled}. Non-responsive attributes (`builderVersion`, `modulePreset`, `groupPreset`, `locked`…) yield `(key, None, None, value)`;
  - `variable_refs(value) -> list[dict]`, which parses every `$variable({...})$` inside a string into its JSON object;
  - `wrap_placeholder(blocks) -> list[Block]`.

- [ ] **Step 1: Write the failing tests**

```python
import json
import unittest

from _paths import d5_fixtures
from divi5_blocks import (Block, Freeform, canonical_json, get_attr, iter_leaves, new_block, parse,
                          render_block, serialize, set_attr, variable_refs, wrap_placeholder)

SIMPLE = ('<!-- wp:divi/placeholder --><!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":'
          '{"value":"Hero"}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":'
          '{"columnStructure":{"desktop":{"value":"1_2,1_2"}}}}} --><!-- wp:divi/column {"module":{"advanced":'
          '{"type":{"desktop":{"value":"1_2"}}}}} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":'
          '{"value":"\\u003cp\\u003eHi\\u003c/p\\u003e"}}}} /--><!-- /wp:divi/column --><!-- wp:divi/column '
          '{"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}}}} --><!-- wp:divi/image {"image":'
          '{"innerContent":{"desktop":{"value":{"src":"https://x.test/a.jpg"}}}}} /--><!-- /wp:divi/column -->'
          '<!-- /wp:divi/row --><!-- /wp:divi/section --><!-- /wp:divi/placeholder -->')


class ParseTest(unittest.TestCase):
    def test_roundtrip_all_fixtures(self):
        for p in d5_fixtures():
            src = p.read_text()
            doc = parse(src)
            self.assertEqual(doc.problems, [], p.name)
            self.assertEqual(serialize(doc), src, p.name)

    def test_tree_shape_and_paths(self):
        doc = parse(SIMPLE)
        (section,) = doc.sections()
        self.assertEqual(section.name, "divi/section")
        text = doc.find("placeholder[0] > section[0] > row[0] > column[0] > text[0]")
        self.assertEqual(get_attr(text, "content.innerContent"), "<p>Hi</p>")
        self.assertEqual([p for _, p, _ in doc.walk()][-1],
                         "placeholder[0] > section[0] > row[0] > column[1] > image[0]")

    def test_visual_builder_style_whitespace_and_escapes(self):
        vb = ('<!-- wp:divi/placeholder -->\n<!-- wp:divi/section {"a":"x\\\\y"} -->\n\n'
              '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"a\\u0026b"}}}} /-->\n'
              '<!-- /wp:divi/section -->\n<!-- /wp:divi/placeholder -->')
        doc = parse(vb)
        self.assertEqual(doc.problems, [])
        self.assertEqual(serialize(doc), vb)
        text = doc.find("placeholder[0] > section[0] > text[0]")
        self.assertEqual(get_attr(text, "content.innerContent"), "a&b")
        self.assertTrue(any(isinstance(c, Freeform) for c in doc.nodes[0].children))

    def test_empty_open_close_pair_accepted(self):
        src = '<!-- wp:divi/divider {"x":1} --><!-- /wp:divi/divider -->'
        doc = parse(src)
        self.assertEqual(doc.problems, [])
        self.assertEqual(serialize(doc), src)

    def test_problems(self):
        self.assertEqual(parse('<!-- wp:divi/section {"a": } -->x<!-- /wp:divi/section -->').problems[0].code,
                         "E5_BAD_JSON")
        self.assertEqual(parse('<!-- wp:divi/section {} -->').problems[0].code, "E5_UNCLOSED")
        self.assertEqual(parse('<!-- /wp:divi/row -->').problems[0].code, "E5_STRAY_CLOSE")
        self.assertEqual(parse('<!-- wp:divi/section --><!-- /wp:divi/row -->').problems[0].code,
                         "E5_MISNESTED")


class CanonicalTest(unittest.TestCase):
    def test_wordpress_escapes(self):
        got = canonical_json({"t": 'a<b>&"c"--d\\e/é😀'})
        self.assertEqual(got, '{"t":"a\\u003cb\\u003e\\u0026\\u0022c\\u0022\\u002d\\u002dd\\u005ce/é😀"}')

    def test_php_empty_object_becomes_array(self):
        self.assertEqual(canonical_json({"a": {}, "b": []}), '{"a":[],"b":[]}')

    def test_php_sequential_numeric_keys_become_list(self):
        self.assertEqual(canonical_json({"s": {"0": "x", "1": "y"}}), '{"s":["x","y"]}')
        self.assertEqual(canonical_json({"s": {"1": "x"}}), '{"s":{"1":"x"}}')

    def test_line_separators_escaped(self):
        self.assertEqual(canonical_json({"t": "a b "}), '{"t":"a\\u2028b\\u2029"}')

    def test_floats_and_bools(self):
        self.assertEqual(canonical_json({"a": 1.0, "b": 0.5, "c": True, "d": None}),
                         '{"a":1.0,"b":0.5,"c":true,"d":null}')

    def test_new_block_is_canonical_and_self_closing(self):
        b = new_block("text", {"content": {"innerContent": {"desktop": {"value": "<p>x</p>"}}}})
        self.assertEqual(render_block(b),
                         '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":'
                         '"\\u003cp\\u003ex\\u003c/p\\u003e"}}}} /-->')
        sec = new_block("section", {}, [b])
        self.assertTrue(render_block(sec).startswith("<!-- wp:divi/section -->"))

    def test_canonical_is_fixed_point_on_fixtures(self):
        # Re-rendering every block canonically, then parsing that again, yields identical attrs.
        for p in d5_fixtures():
            doc = parse(p.read_text())
            canon = "".join(render_block(n) for n in doc.nodes if isinstance(n, Block))
            again = parse(canon)
            self.assertEqual(again.problems, [], p.name)
            self.assertEqual(serialize(again), canon, p.name)


class AttrTest(unittest.TestCase):
    def test_set_attr_only_changes_that_block(self):
        doc = parse(SIMPLE)
        text = doc.find("placeholder[0] > section[0] > row[0] > column[0] > text[0]")
        set_attr(text, "content.innerContent", "<p>Bye</p>")
        set_attr(text, "content.decoration.bodyFont.body.font", {"size": "18px"}, breakpoint="tablet")
        out = serialize(doc)
        before, after = SIMPLE.split("<!-- wp:divi/text")[0], SIMPLE.split("<!-- /wp:divi/column -->", 1)[1]
        self.assertTrue(out.startswith(before))
        self.assertTrue(out.endswith(after))
        self.assertIn("Bye", out)
        self.assertEqual(get_attr(parse(out).find("placeholder[0] > section[0] > row[0] > column[0] > text[0]"),
                                  "content.decoration.bodyFont.body.font", breakpoint="tablet"), {"size": "18px"})

    def test_iter_leaves(self):
        attrs = {"title": {"decoration": {"font": {"font": {"desktop": {"value": {"size": "5px"}, "hover": {"x": 1}},
                                                             "tablet": {"value": {"size": "4px"}}}}}},
                 "builderVersion": "5.13.1", "modulePreset": ["default"]}
        got = sorted((p, bp or "", st or "") for p, bp, st, _ in iter_leaves(attrs))
        self.assertEqual(got, [("builderVersion", "", ""), ("modulePreset", "", ""),
                               ("title.decoration.font.font", "desktop", "hover"),
                               ("title.decoration.font.font", "desktop", "value"),
                               ("title.decoration.font.font", "tablet", "value")])

    def test_variable_refs(self):
        v = 'x $variable({"type":"color","value":{"name":"gcid-abc","settings":{}}})$ y'
        self.assertEqual(variable_refs(v), [{"type": "color", "value": {"name": "gcid-abc", "settings": {}}}])
        self.assertEqual(variable_refs("#fff"), [])

    def test_wrap_placeholder(self):
        (ph,) = wrap_placeholder([new_block("section")])
        self.assertEqual(ph.name, "divi/placeholder")
        self.assertEqual(render_block(ph), "<!-- wp:divi/placeholder --><!-- wp:divi/section /-->"
                                           "<!-- /wp:divi/placeholder -->")
```

Note on the last assertion: a structure block with no children is self-closing in canonical form (WordPress's `get_comment_delimited_block_content()` emits `/-->` when the inner content is empty). This matches the storage research §3. Check the table in `research/divi5/storage-and-serialization.md` before implementing.

- [ ] **Step 2: Run to verify they fail.** `python3 -m unittest discover -s tests -p test_divi5_blocks.py -v` → ImportError.

- [ ] **Step 3: Implement `divi5_blocks.py`.** Required behaviour:
  - **Tokenizer:** WordPress's block delimiter regex, from `WP_Block_Parser::next_token` in `wp-includes/class-wp-block-parser.php`, restricted to any namespace:
    `<!--\s+(?P<closer>/)?wp:(?P<ns>[a-z][a-z0-9_-]*/)?(?P<name>[a-z][a-z0-9_-]*)\s+(?P<attrs>{(?:(?:[^}]+|}+(?=})|(?!}\s+/?-->).)*)?}\s+)?(?P<void>/)?-->`, compiled with `re.S`. Non-`divi/` blocks (e.g. `core/*`) are parsed and kept, and the validator flags them. A missing namespace means `core/`.
  - **Structure:** build the tree with a stack. Report a close with an empty stack as `E5_STRAY_CLOSE`, a close name that doesn't match the top of the stack as `E5_MISNESTED`, blocks left open at EOF as `E5_UNCLOSED`, and `json.loads` failures as `E5_BAD_JSON`. Keep the block with `attrs={}` after a JSON failure.
  - **Text:** text between delimiters becomes a `Freeform` child of the current block, or top level, kept verbatim.
  - **`serialize`:** for each node, if it isn't dirty and has a source span, emit `source[start:open_end]`, then its children recursively, then `source[close_start:end]`. That way a dirty descendant re-renders only itself. Emit a dirty or new block with `render_block`.
  - **`canonical_json`:** first `_phpify(obj)`, which recursively turns an empty dict into `[]` and a dict whose keys are exactly `"0".."n-1"` in order into a list. Then `json.dumps(ensure_ascii=False, separators=(",", ":"))`. Then replace ` `/` ` characters with their `\\u2028`/`\\u2029` escapes. Then a single left-to-right pass equivalent to PHP `strtr` with the six pairs from Global Constraints. Implement it with `re.sub(r'\\\\|--|<|>|&|\\"', repl, s)`: the alternation order matches `strtr`'s leftmost-longest behaviour because all keys are one or two characters and the regex scans left to right.
  - **`render_block`:** `<!-- wp:{name_without_core} {json} -->` + children + `<!-- /wp:… -->`. With no children (or only empty freeform) use `<!-- wp:{name} {json} /-->`. When attrs is empty, leave out the JSON and its space: `<!-- wp:divi/section -->`.
  - **`get_attr`/`set_attr`:** dotted path down to the attrName leaf, then `[breakpoint][state]`. For non-responsive top-level keys (`builderVersion`, `modulePreset`, `groupPreset`, `locked`), pass `breakpoint=None` to get or set the raw key. `set_attr` creates intermediate dicts as needed.
  - **`iter_leaves`:** walk the dict. When a dict's keys are all breakpoint names and each value is a dict whose keys are all state names, yield one leaf per (breakpoint, state) with the dotted path so far. Otherwise recurse. Scalars and lists at top level are non-responsive leaves.
  - **`variable_refs`:** find `$variable(` and read to the matching `)$` with a brace counter that respects JSON strings, then `json.loads` the inside.

- [ ] **Step 4: Run tests** until they pass, then run the full suite.

- [ ] **Step 5: Performance guard.** Add `test_parse_large_fast`: parse the largest fixture 20× in under 2 s total.

- [ ] **Step 6: Commit** `divi5: block parser/serializer with WordPress-canonical JSON and attribute access`

---

### Task 3: Divi 5 schema: families, compile with coverage gate, resolver

**Files:**
- Create: `research/tools/divi5/families5.json`, `research/tools/divi5/build_schema5.py`, `Skill/divi-page-builder/scripts/divi5_schema.py`, generated `Skill/divi-page-builder/scripts/schema5/*.json`
- Test: `tests/test_divi5_schema.py`

**Read first:** `research/divi5/schema.md` in full (particularly §3 on the union path model, §7 on the proposed shape and leaf types, and §8), `research/divi5-schema/index.json`, `groups.json`, one `modules/blurb.json`, and `research/tools/divi5/schema_coverage.py`. That script already implements the union model that reached 100% coverage, so port its logic rather than reinventing it.

**Interfaces:**
- Consumes: `divi5_blocks.parse`, `iter_leaves`, `variable_refs`.
- Produces:
  - `scripts/schema5/<short>.json` (short = module name without `divi/`), each holding `{"name","d4","category","scope","children":[...]|null,"parents":[...],"attrs":{<attrName path>: <leaf spec or {"family": name, "prefix": ...}>},"css":[...],"defaults":{...}}`;
  - `scripts/schema5/families5.json`, copied from the research source with leaf specs `{type, options?, units?, bp: bool, states: [..]}`;
  - `scripts/schema5/_meta.json`: `{"divi_version","breakpoints_default":["desktop","tablet","phone"],"breakpoints_all":[...],"states":[...],"scopes_in":["core","d5-extra"],"generated_by":"build_schema5.py"}`;
  - `divi5_schema.load_schema5(directory=None) -> Schema5`;
  - `Schema5.module(name) -> ModuleSchema5 | None` (accepts `divi/text` or `text`);
  - `Schema5.in_scope(name) -> bool`;
  - `ModuleSchema5.resolve(path: str, breakpoint: str | None, state: str | None) -> Resolution5`, where `Resolution5` is a dataclass of `status` ("ok" | "unknown_attr" | "bad_breakpoint" | "bad_state" | "nonresponsive"), `leaf: dict | None` (the type spec), `attr_path`, `sub_path` (the path inside the value object when the leaf is an object-valued family attr) and `family: str | None`;
  - `ModuleSchema5.children`, `.parents`, `.category`, `.scope`, `.d4`;
  - `leaf_types()`, the set of leaf type names defined in `families5.json`.

- [ ] **Step 1: Write the failing tests**

```python
import json
import unittest

from _paths import SCRIPTS, d5_fixtures
from divi5_blocks import iter_leaves, parse
from divi5_schema import load_schema5

LEAF_TYPES = {"text", "html", "color", "length", "number", "enum", "onoff", "url", "image", "icon",
              "spacing", "radius", "gradient", "object", "font-family", "font-weight", "json"}


class Schema5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema5()

    def test_meta_and_scope(self):
        meta = json.loads((SCRIPTS / "schema5" / "_meta.json").read_text())
        self.assertTrue(meta["divi_version"].startswith("5."))
        self.assertTrue(self.schema.in_scope("divi/blurb"))
        self.assertTrue(self.schema.in_scope("section"))
        self.assertFalse(self.schema.in_scope("divi/cart-products"))      # woocommerce
        self.assertFalse(self.schema.in_scope("divi/contact-form-7"))     # integration
        self.assertIsNone(self.schema.module("divi/nope"))

    def test_every_fixture_path_resolves(self):
        misses = []
        for p in d5_fixtures():
            for block, path, _ in parse(p.read_text()).walk():
                mod = self.schema.module(block.name)
                if mod is None:
                    continue  # placeholder/internal handled by the validator
                for attr, bp, st, _ in iter_leaves(block.attrs):
                    r = mod.resolve(attr, bp, st)
                    if r.status not in ("ok", "nonresponsive"):
                        misses.append((p.name, block.name, attr, bp, st, r.status))
        # Known converter quirk: signup custom fields stay as a D4 shortcode string (schema.md §Q2).
        misses = [m for m in misses if "signup" not in m[1]]
        self.assertEqual(misses, [])

    def test_bogus_paths_rejected(self):
        blurb = self.schema.module("divi/blurb")
        for attr in ("title.decoration.fontz.font", "module.decoration.bogus", "imageIcon.innerContent.nope",
                     "titlex.innerContent"):
            self.assertEqual(blurb.resolve(attr, "desktop", "value").status, "unknown_attr", attr)

    def test_breakpoints_and_states(self):
        blurb = self.schema.module("divi/blurb")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "tablet", "value").status, "ok")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "desktop", "hover").status, "ok")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "mobile", "value").status, "bad_breakpoint")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "desktop", "pressed").status, "bad_state")

    def test_every_leaf_typed(self):
        for name in self.schema.names():
            mod = self.schema.module(name)
            for attr, spec in mod.attrs.items():
                leaf = self.schema.leaf_spec(spec)
                for sub, s in leaf.items():
                    self.assertIn(s["type"], LEAF_TYPES, f"{name} {attr} {sub}")

    def test_structure_relations(self):
        self.assertIn("divi/row", self.schema.module("section").children or [])
        self.assertIn("divi/accordion-item", self.schema.module("accordion").children)
        self.assertEqual(self.schema.module("blurb").d4, "et_pb_blurb")
        self.assertEqual(self.schema.module("section").category, "structure")

    def test_build_is_deterministic(self):
        import subprocess, sys, tempfile
        from _paths import ROOT, SCHEMA5_RAW, TOOLS5
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, str(TOOLS5 / "build_schema5.py"), str(SCHEMA5_RAW),
                            str(TOOLS5 / "families5.json"), tmp], check=True, capture_output=True)
            for f in sorted((SCRIPTS / "schema5").glob("*.json")):
                self.assertEqual((SCRIPTS / "schema5" / f.name).read_text(), open(f"{tmp}/{f.name}").read(), f.name)
```

Adjust `LEAF_TYPES` to exactly the type set you define in `families5.json`, and keep the list in the test and in `families5.json["_types"]` identical. The test reads the set from `schema.leaf_types()` rather than hard-coding it if you prefer. The point is that no leaf has an undefined type.

- [ ] **Step 2: Run to verify they fail.**

- [ ] **Step 3: Curate `families5.json`.**
  - **Start from `groups.json`:** for each shared option group it lists the leaf sub-paths. Assign every leaf a `type` from the leaf-type table in `schema.md` §7, plus `options` (enum values), `units` and `states`.
  - **Where types come from:**
    - Divi 4 field types via the conversion map (`modules/*.json` conversion entries map each D4 attr to a D5 path, and the D4 field's `type`/`options`/`allowed_units` are in `research/divi-schema/modules/*.json`);
    - the leaf names themselves (`color` → `color`, `size`/`letterSpacing`/`lineHeight` → `length`, `family` → `font-family`, `weight` → `font-weight`, `sync*`/`enabled`/`use*` → `onoff`, `style` → `enum`);
    - the render defaults in `research/divi5-schema` (value shapes).
  - **Where options come from:** D4 option lists via the conversion map, then the value corpus (every distinct value across fixtures) to confirm.
  - Record each family's source in a `"_notes"` key.
  - Budget real time for this; it is the one hand-maintained artifact.

- [ ] **Step 4: Write `build_schema5.py DUMP_DIR FAMILIES OUT_DIR`.**
  - Port the union path model from `schema_coverage.py`.
  - Write one JSON per module with `sort_keys=True, indent=1`, a trailing newline, and `ensure_ascii=False`.
  - Copy the families and write `_meta.json`.
  - Compute `scope` from the dump plus a fixed list (WooCommerce = the module list in `schema.md` Q3; integration = contact-form-7, gravity-forms, imagely-gallery, instagram-feed; theme-builder and internal per `schema.md`).
  - Compute parents as the inverse of `children` plus structure rules:
    - section → row, row-inner, fullwidth modules;
    - row → column;
    - column → modules, row-inner (specialty);
    - row-inner → column-inner;
    - column-inner → modules;
    - group → modules (per `schema.md`).
  - **Coverage gate:** exit 1 and list offenders if any attr path of an in-scope module has a leaf without a type in `families5.json`.

- [ ] **Step 5: Write `divi5_schema.py`.**
  - Load lazily from `Path(__file__).parent / "schema5"` and cache.
  - `resolve()`:
    1. exact attr path match;
    2. otherwise the longest attr prefix that maps to a family whose leaf table contains the remainder (object-valued attrs: the remainder is `sub_path` inside the value);
    3. `nonresponsive` for top-level bookkeeping keys (`builderVersion`, `modulePreset`, `groupPreset`, `locked`, `_*`).
  - Check the breakpoint against `_meta.breakpoints_all` (the validator distinguishes the default set) and the state against the leaf's `states`.

- [ ] **Step 6: Run the build, then the tests; iterate on `families5.json` until green.** Then run the full suite.

- [ ] **Step 7: Commit** `divi5: curated families, schema build with coverage gate, schema5 resolver`

---

### Task 4: Validator: format dispatch, Divi 5 structure and headings

**Files:**
- Create: `Skill/divi-page-builder/scripts/divi5_checks_structure.py`
- Modify: `Skill/divi-page-builder/scripts/validate.py`
- Create fixtures: `tests/fixtures/divi5/invalid/*.html` (one per error class)
- Test: `tests/test_divi5_validate_structure.py`

**Interfaces:**
- Consumes: `divi5_blocks.parse/Document/Block`, `divi5_schema.load_schema5`, `divi_format.detect_content`, `validate.Finding/Reporter`.
- Produces:
  - `divi5_checks_structure.check_structure5(doc, schema5, report) -> None`;
  - `check_headings5(doc, schema5, report, fragment=False) -> None`;
  - `validate.validate_source(source, schema=None, tokens=None, site_url=None, baseline=None, fragment=False) -> list[Finding]`, which dispatches on `detect_content(source)`. With `"blocks"` it runs the D5 checks and loads `load_schema5()` itself. With `"mixed"` it reports `E5_MIXED_FORMAT`. `"shortcode"`/`"empty"` take the existing path, with `schema` defaulting to `load_schema()`. The existing positional signature stays compatible (callers pass the D4 schema positionally).
  - `Reporter` gets a `line_col` source that works for both document types (both expose `.line_col`), and uses `node.name` for D5 tags.
- Error codes (D5 prefix `E5_`/`W5_`):

| Code | Level | Condition |
|---|---|---|
| `E5_MIXED_FORMAT` | error | shortcode and blocks mixed |
| `E5_BAD_JSON`, `E5_UNCLOSED`, `E5_STRAY_CLOSE`, `E5_MISNESTED` | error | from the parser |
| `E5_UNKNOWN_BLOCK` | error | name not in schema5 and not `divi/placeholder` |
| `W5_OUT_OF_SCOPE` | warning | known but scope not in `scopes_in` |
| `E5_NOT_DIVI` | error | a non-`divi/` block, or non-whitespace freeform text outside blocks |
| `W5_NO_PLACEHOLDER` | warning | top-level blocks not wrapped in `divi/placeholder` (whole pages only; skipped with `--fragment`) |
| `E5_BAD_PARENT` | error | child not allowed in parent (both directions: `children` lists and structure rules) |
| `E5_TOPLEVEL` | error | a non-section at top level (inside the placeholder) |
| `E5_SECTION_TYPE` | error | `module.advanced.type` not in {regular, fullwidth, specialty}; content wrong for the type (regular → rows only; fullwidth → fullwidth modules only; specialty → columns with at most one inner-row column per the D4 rules) |
| `E5_COLUMNS` | error | a row's `columnStructure` doesn't match its columns' `type` sequence (same fraction rules as D4 `_check_columns`) |
| `E5_MULTIPLE_H1`, `W_NO_H1`, `W_HEADING_SKIP` | error / warning / warning | same semantics and messages as D4 (`check_headings`), with levels read from `headingLevel` leaves of font attrs (`…decoration.font.font.desktop.value.headingLevel`, and the module default from schema5 `defaults`) and from `<h1>`–`<h6>` tags inside HTML `innerContent` values |

- [ ] **Step 1: Write the invalid fixtures.** Write each as the smallest page that isolates its error, built from a valid converted fixture section. Add a `tests/fixtures/divi5/invalid/README.md` table: file → expected code.
- [ ] **Step 2: Write the failing tests.**

```python
import unittest

from _paths import FIXTURES5, d5_fixtures
from validate import validate_source

EXPECT = {
    "mixed.html": "E5_MIXED_FORMAT", "bad-json.html": "E5_BAD_JSON", "unclosed.html": "E5_UNCLOSED",
    "unknown-block.html": "E5_UNKNOWN_BLOCK", "text-in-section.html": "E5_BAD_PARENT",
    "row-at-top.html": "E5_TOPLEVEL", "fullwidth-with-row.html": "E5_SECTION_TYPE",
    "columns-mismatch.html": "E5_COLUMNS", "two-h1.html": "E5_MULTIPLE_H1", "freeform.html": "E5_NOT_DIVI",
}


def codes(src, **kw):
    return [f.code for f in validate_source(src, **kw) if f.level == "error"]


class Structure5Test(unittest.TestCase):
    def test_valid_fixtures_have_no_structure_errors(self):
        for p in d5_fixtures():
            if "invalid" in p.parts:
                continue
            errs = [f for f in validate_source(p.read_text()) if f.level == "error" and f.code.startswith("E5_")
                    and f.code in {"E5_BAD_PARENT", "E5_TOPLEVEL", "E5_SECTION_TYPE", "E5_COLUMNS",
                                   "E5_UNKNOWN_BLOCK", "E5_BAD_JSON", "E5_MISNESTED", "E5_UNCLOSED"}]
            self.assertEqual(errs, [], p.name)

    def test_each_invalid_fixture(self):
        for name, code in EXPECT.items():
            src = (FIXTURES5 / "invalid" / name).read_text()
            self.assertIn(code, codes(src), name)

    def test_d4_path_unchanged(self):
        from _paths import FIXTURES
        from divi_schema import load_schema
        src = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()
        self.assertEqual([f.code for f in validate_source(src, load_schema())],
                         [f.code for f in validate_source(src)])

    def test_heading_rules(self):
        src = (FIXTURES5 / "invalid" / "two-h1.html").read_text()
        f = [f for f in validate_source(src) if f.code == "E5_MULTIPLE_H1"][0]
        self.assertIn(">", f.path)
        self.assertGreater(f.line, 0)
```

`d5_fixtures()` globs `**/*.html`, which includes `invalid/`. The filter above skips them. Also update `tests/test_divi_format.py::test_block_fixtures` to skip `invalid` (mixed.html is not "blocks").

- [ ] **Step 3: Implement** `divi5_checks_structure.py`, following `divi_checks_structure.py`'s structure closely: reuse its `fraction()` and column-sequence logic by importing them, and write D5-specific walkers. Add the dispatch in `validate.py`. `main()` doesn't change; it simply stops calling `load_schema()` itself when the content is blocks.
- [ ] **Step 4: Run** the new tests and the full suite (D4 validate tests must be unchanged).
- [ ] **Step 5: Commit** `divi5: validator dispatch, structure and heading checks`

---

### Task 5: Validator: attribute paths, value types, escaping, presets and variables

**Files:**
- Create: `Skill/divi-page-builder/scripts/divi5_checks_values.py`; more `tests/fixtures/divi5/invalid/*.html`
- Modify: `validate.py` (call `check_attributes5`)
- Test: `tests/test_divi5_validate_values.py`

**Interfaces:**
- Consumes: `divi5_schema.Resolution5`, `divi5_blocks.iter_leaves/variable_refs`, `families5` leaf types.
- Produces:
  - `check_attributes5(doc, schema5, report, known_presets=frozenset(), known_vars=frozenset(), site_host=None, site_version=None) -> None`;
  - `value_problems5(leaf_spec: dict, value) -> list[str]`, the messages for one leaf value (unit-testable).
- Codes:

| Code | Level | Condition |
|---|---|---|
| `E5_UNKNOWN_ATTR` | error | resolve → `unknown_attr` |
| `E5_BAD_BREAKPOINT` | error | a breakpoint that isn't a Divi breakpoint |
| `W5_BREAKPOINT_DISABLED` | warning | phoneWide/tabletWide/widescreen/ultraWide (off by default) |
| `E5_BAD_STATE` | error | state not allowed on the leaf |
| `E5_BAD_VALUE` | error | the type check fails. Types: `color` = hex / rgb(a) / hsl(a) / `transparent` / a `$variable({"type":"color"…})$`; `length` = number + unit in `units` or `auto` / `calc(...)` / a `$variable` content ref / `""`; `enum` ∈ options; `onoff` ∈ {on, off}; `number`; `url`; `icon` = `{unicode,type,weight}`; `spacing` keys ⊆ {top,right,bottom,left,syncVertical,syncHorizontal} with length values; `radius`; `gradient` stops list; `image` = object with `src`/`url`; `html`/`text` strings |
| `E5_BAD_VARIABLE` | error | a malformed `$variable(...)$` (bad JSON, missing `type` or `value.name`) |
| `W5_UNKNOWN_VARIABLE` | warning | a `gcid-`/`gvid-` name not in `known_vars`, only when tokens are given. **Exception:** the 5 Customizer ids `gcid-primary-color`, `gcid-secondary-color`, `gcid-heading-color`, `gcid-body-color`, `gcid-link-color` (check `tokens-and-detection.md` §2 for the exact list) are always known |
| `W5_UNKNOWN_PRESET` | warning | a `modulePreset` entry that isn't `default` and isn't in `known_presets`, or a `groupPreset` presetId likewise. Message: "an unknown preset id makes Divi drop the module's default preset styling; omit modulePreset or use ["default"]" |
| `E5_NONCANONICAL` | error | the block's `raw_json` contains a raw `<`, `>`, `&` or `--` outside escapes, or a raw `\"` quote form that isn't `"` inside string values. Hint: "write the JSON in WordPress canonical form (validate.py never rewrites; page_edit/publish do)". Check the raw text, not the decoded value |
| `W5_SHORTCODE_BRACKETS` | warning | an HTML `innerContent` value containing `[` + letter (WordPress would run it as a shortcode) — hint `&#91;` / `&#93;` |
| `W_EXTERNAL_IMAGE` | warning | an image `src`/`url` whose host isn't `site_host`, and isn't a relative or local file (same code and semantics as D4) |
| `W5_NO_ALT` | warning | an image module without `alt` |
| `W5_BUILDER_VERSION` | warning | `builderVersion` missing, or different from `site_version` when given |
| `W5_HOVER_WITHOUT_DESKTOP` | warning | a hover/sticky state or tablet/phone breakpoint present without `desktop.value` for the same leaf |

- [ ] **Step 1: Write the new invalid fixtures** (unknown-attr, bad-breakpoint, bad-state, bad-color, bad-unit, bad-enum, bad-variable, noncanonical-lt, unknown-preset, shortcode-brackets) and extend the fixture README.
- [ ] **Step 2: Write the failing tests.** For each fixture assert its code. Add `value_problems5` unit tests for each leaf type (valid and invalid examples, including `$variable` in color and length). **Valid-corpus test:** every `d5_fixtures()` file outside `invalid/` has 0 errors from `validate_source` (the whole validator), except the documented signup quirk. If a fixture legitimately fails because of converter output, fix `families5.json`, not the fixture.
- [ ] **Step 3: Implement.** Pass `known_presets`/`known_vars`/`site_version` from tokens in `validate_source` (tokens D5 shape: Task 11/12; until then, read `tokens.get("presets")` ids, `tokens.get("colors",{}).get("global")` keys and `tokens.get("variables")` keys defensively).
- [ ] **Step 4: Run** the new and full suites.
- [ ] **Step 5: Commit** `divi5: attribute, value, escaping, preset and variable checks`

---

### Task 6: Validator: tokens checks, baseline, JSON output, performance

**Files:**
- Create: `Skill/divi-page-builder/scripts/divi5_checks_tokens.py`
- Modify: `validate.py`
- Test: `tests/test_divi5_validate_tokens.py`

**Interfaces:**
- Produces: `check_tokens5(doc, schema5, tokens, report)`. It emits `W_OFF_PALETTE_COLOR`, `W_OFF_TOKEN_FONT` and `W_OFF_TOKEN_SPACING`, the same codes as D4's `check_tokens` (read `divi_checks_tokens.py` for the exact codes and messages and reuse its `_palette`/`_fonts` helpers by import). It checks only literal values; `$variable` refs are never off-palette.

**Behaviour:** `--baseline` and `--fragment` work for blocks exactly as for shortcode. The `mark_preexisting` key `(code, tag, attr, value)` uses `tag = block.name` and `attr = dotted path + ":" + breakpoint + ":" + state`. `--json` output has the same shape.

- [ ] **Step 1: Write the failing tests.**
  1. A page with one literal off-palette color against `tests/fixtures/tokens-min.json` gives one `W_OFF_PALETTE_COLOR`. The same color written as a `$variable` gives none.
  2. Baseline: validating a fixture against itself as baseline marks every finding preexisting, so exit 0. Adding one new error makes exactly one non-preexisting finding.
  3. CLI `validate.py page.html --json` returns exit 0 for a valid fixture and 1 for `invalid/unknown-attr.html`, with the JSON `findings[0].code == "E5_UNKNOWN_ATTR"`.
  4. Performance: validating the largest fixture takes under 1.5 s (mirror the D4 perf test).
- [ ] **Step 2: Run to verify they fail.**
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** the new and full suites.
- [ ] **Step 5: Commit** `divi5: token checks, baseline/fragment/json parity, perf guard`

---

### Task 7: Divi as judge (live)

**Files:**
- Create: `research/tools/divi5/judge.php`, `tests/test_divi5_judge.py`
- Create: `tests/fixtures/divi5/escape-cases.html` (a canonical page built by `research/tools/divi5/make_escape_cases.py` from R3, with every tricky character class)

**What it proves:**
1. For every valid D5 fixture, WordPress's `parse_blocks()` (as run by Divi) yields the same tree (names, nesting) and the same decoded attrs as `divi5_blocks.parse`.
2. For every block, `serialize_block_attributes(parsed attrs)` in PHP equals our `canonical_json(attrs)` byte for byte. This is the authority for Review Focus #2.
3. Divi renders every valid fixture without PHP warnings, producing one `.et_pb_section` per section block. Use `research/tools/divi5/render_check.sh` or `do_blocks()` in `judge.php`.
4. For each invalid fixture where Divi can have an opinion (bad JSON, unknown block), record Divi's behaviour in the test docstring. Our verdict must be at least as strict.

`judge.php FILE` prints JSON: `{"blocks":[{"name","attrs","canonical","children":[…]}], "render":{"sections":N,"php_notices":[…]}}`. Run it with `wp5("eval-file", TOOLS5/"judge.php", path)`.

- [ ] **Step 1: Write `judge.php`.** Use `parse_blocks` and `serialize_block_attributes`. Render with `do_blocks` inside an output buffer while capturing `set_error_handler` notices, and use the Divi front-end context: for rendering, create a draft page via `wp_insert_post` with `--user`, `get_the_content`/`apply_filters('the_content')` in a simulated query, then delete it. If simpler, use R1's `render_check.sh` approach (a temporary publish plus curl) and delete afterwards.
- [ ] **Step 2: Write `tests/test_divi5_judge.py`** (`@live5_only`) with three tests (tree/attrs, canonical bytes, render). Compare recursively, with a precise diff message on failure.
- [ ] **Step 3: Run with** `PP_LIVE_TESTS=1`. Every mismatch in canonical bytes is a bug in `canonical_json`: fix it in Task 2's module and add an offline unit test reproducing the case.
- [ ] **Step 4: Add the escape-cases fixture to the offline round-trip corpus** (it is canonical, so the offline tests cover it).
- [ ] **Step 5: Commit** `divi5: Divi-as-judge harness (parse, canonical JSON, render)`

---

### Task 8: Generated module docs and design families with coverage check

**Files:**
- Create: `research/tools/divi5/generate_docs5.py`, `research/tools/divi5/notes/` (hand notes, may start empty)
- Generated: `Skill/divi-page-builder/reference/divi5/modules/<short>.md` (in-scope modules), `reference/divi5/modules/README.md`, and the generated tables inside `reference/divi5/design-families.md` (between `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->` markers; the prose outside them is hand-written)
- Modify: `research/tools/check_doc_examples.py` to also validate ```` ```html ```` / ```` ```divi5 ```` code blocks under `reference/divi5/` and `recipes/divi5/` through `validate_source` (fragment mode for snippets)
- Test: `tests/test_divi5_docs.py`

**Read first:** `research/tools/generate_docs.py` and one generated D4 page (`reference/modules/et_pb_blurb.md`) with `reference/design-families.md`. Mirror their layout, tone and table columns.

**Module page contents:**
- **Header:** title, `divi/<name>` (D4 equivalent `et_pb_*`), category, scope, allowed parents, allowed children, CSS slots.
- **Minimal valid example:** a canonical page fragment built with `new_block` and validated at generation time. Generation fails if it doesn't validate.
- **Content group:** `innerContent` attrs with their types.
- **Design group:** module-specific decoration attrs in full, plus a table of the families this module uses with their attrName paths (e.g. `title.decoration.font` → font family), linking to `../design-families.md#<family>`.
- **Advanced group:** `advanced.*` fields.
- **Render defaults:** a collapsed list from schema5 `defaults`.
- **Gotchas:** merged from `notes/<short>.md`.

**Coverage check:** generation exits 1 if any attr path in the module's schema5 is neither listed on its page nor covered by a linked family table.

- [ ] **Step 1: Write the failing tests.**
  1. After running the generator into a temp dir, the output equals the committed `reference/divi5` files (deterministic).
  2. Every in-scope module has a page.
  3. `check_doc_examples.py Skill/divi-page-builder` passes (all D4 and D5 examples validate).
  4. The coverage function reports zero gaps.
  5. The README lists every page.
- [ ] **Step 2: Run to verify they fail.**
- [ ] **Step 3: Implement the generator** and write the hand-written prose of `design-families.md`: how attrName paths, breakpoints and states nest; how to read a family table; the `$variable` note.
- [ ] **Step 4: Generate, run the tests, iterate.**
- [ ] **Step 5: Update `research/tools/README.md`** with the Divi 5 regeneration commands:
  1. dump: `LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH=… research/tools/wp-local.sh eval-file research/tools/divi5/dump-schema.php "$PWD/research/divi5-schema"`;
  2. build: `python3 research/tools/divi5/build_schema5.py research/divi5-schema research/tools/divi5/families5.json Skill/divi-page-builder/scripts/schema5`;
  3. docs: `python3 research/tools/divi5/generate_docs5.py research/divi5-schema Skill/divi-page-builder --notes research/tools/divi5/notes`;
  4. check examples.
- [ ] **Step 6: Commit** `divi5: generated module references and design-family tables with coverage check`

---

### Task 9: Hand-written Divi 5 references

**Files:**
- Create: `Skill/divi-page-builder/reference/divi5/page-format.md`, `structure.md`, `value-formats.md`
- Test: extend `tests/test_divi5_docs.py` so every code example validates (via `check_doc_examples`) and every file mentioned in `SKILL.md`'s Divi 5 index exists (the latter is enforced in Task 19)

**Content (every claim backed by `research/divi5/*.md`; cite the experiment, like the D4 references do):**
- **`page-format.md`:**
  - block grammar;
  - placeholder;
  - canonical JSON escaping and why (non-`unfiltered_html` authors);
  - "all content lives in the JSON";
  - `builderVersion` rules;
  - required meta (`_et_pb_use_builder`), and why REST needs `publish.py` (the batch sequence);
  - where things are stored (post_content, meta, the options `et_divi`, `et_divi_global_variables`, `et_divi_builder_global_presets_d5`);
  - what never to do (raw `<`/`&`/`"` in JSON, text between tags, Divi 4 shortcode on Divi 5);
  - how Divi 4 pages on Divi 5 sites behave;
  - `&#91;`/`&#93;` in text;
  - `content.raw` is canonicalized on WordPress ≥ 7.0.
- **`structure.md`:**
  - section types (`module.advanced.type`);
  - `columnStructure` values with the column `type` sequences (a table of every legal structure, reusing the D4 list);
  - the specialty section rules;
  - row-inner/column-inner;
  - parent → child pairs from schema5;
  - `display:"block"` on structure elements (the spec's layout-form decision) with the exact JSON snippet;
  - module index classes (`et_pb_text_0`) and how they relate to custom CSS.
- **`value-formats.md`:**
  - the value model (attrName → group → breakpoint → state) with a full example;
  - enabled breakpoints;
  - hover/sticky (presence = enabled);
  - one section per leaf type from `families5.json` (grammar, valid example, common mistake);
  - `$variable()` color and content refs;
  - `modulePreset` and `groupPreset`;
  - icons (`{unicode,type,weight}`; point to `reference/icons.md`, and confirm the unicode values match D4's `&#xf0a9;` → `"unicode":"&#xf0a9;"` or whatever the converter produces: check the fixtures);
  - images (`src`, `id`, `alt`, `titleText`);
  - links;
  - spacing and radius objects with the sync flags.

- [ ] **Step 1: Write the three files.** Every JSON snippet is canonical and validated: use fenced ```` ```divi5 ```` blocks containing complete fragments, which `check_doc_examples.py` (Task 8) validates with `--fragment`.
- [ ] **Step 2: Run** `python3 research/tools/check_doc_examples.py Skill/divi-page-builder` and the test suite.
- [ ] **Step 3: Commit** `divi5: page-format, structure and value-format references`

---

### Task 10: Publishing Divi 5 pages (`publish.py`, `local_media.py`, `publishing.md`)

**Files:**
- Modify: `Skill/divi-page-builder/scripts/publish.py`, `Skill/divi-page-builder/scripts/local_media.py`, `Skill/divi-page-builder/reference/publishing.md`
- Test: extend `tests/test_publish.py` (offline, with a fake `WordPress`) and add `tests/test_divi5_publish_live.py` (`@live5_only`)

**Behaviour:**
1. **Format and version checks.** `draft` and `publish` detect the content format. Before writing they need the site's major version: `divi_format.detect_site(wp.base)` (cached per run), or `tokens.json → site.divi_major` when `--tokens` is given.
   - Shortcode content to a Divi 5 site → refuse (exit 1): "this is Divi 4 shortcode; the site runs Divi 5 — write Divi 5 blocks (reference/divi5/page-format.md)".
   - Blocks to a Divi 4 site → refuse similarly.
   - Unknown version → proceed with a warning.
2. **Validation** uses `validate_source` (format-aware) with tokens and baseline, exactly as for D4.
3. **Local images in blocks.** `local_media.iter_local_images` gains a blocks branch: image leaves are the `src`/`url` keys of `image` values and background `image.url`; decide by schema5 leaf type `image` or `url` under image families. Upload each and rewrite the value; set `id` and `alt` siblings when the leaf is an image object. Re-serialize only changed blocks (`set_attr` sets `dirty`).
4. **Divi 5 draft sequence**, when the site is Divi 5:
   1. For a new page: `POST /wp/v2/pages {title, slug?, status:"draft", content:"[et_pb_section][/et_pb_section]", …page_fields}`.
   2. `POST /batch/v1 {"requests":[{"method":"POST","path":"/wp/v2/pages/ID","body":{"title":TITLE}},{"method":"POST","path":"/wp/v2/pages/ID","body":{"content":CONTENT,"meta":{"_et_pb_use_builder":"on"}}}]}`. Expect 207 with two 200s.
   3. `GET /wp/v2/pages/ID?context=edit` and require `meta._et_pb_use_builder == "on"`. Otherwise exit 2: "WordPress did not store _et_pb_use_builder=on; the page will render inside the theme's title+sidebar template. See reference/publishing.md → Divi 5 builder meta."
   4. **Existing page** (`--page-id`): if its meta is already `on`, a normal content update. If it's off: when the page is a draft, use the same stub+batch; if it's live, refuse with the explanation (spec §3.6).
5. **`publish --content`** on Divi 5: same checks; send content only, since meta is already on for pages created by `draft`. The status rules stay unchanged from D4.
6. **`fetch`:** print a note to stderr when the content is blocks: `content.raw` is WordPress's canonical re-serialization on WP ≥ 7.0 (use it as the baseline as-is).

- [ ] **Step 1: Write offline tests with a fake transport.** Mirror the existing `test_publish.py` fakes and read it first. Cover:
  - refusal matrix (D4 content → D5 site; D5 → D4);
  - the exact request sequence and bodies for a new D5 draft;
  - read-back failure → exit 2 and message;
  - existing live page with meta off → refusal;
  - local image upload rewrites a block's `image.innerContent.desktop.value.src` and sets `id`;
  - Divi 4 behaviour byte-identical (the existing tests unchanged).
- [ ] **Step 2: Run to verify they fail.**
- [ ] **Step 3: Implement.** Keep D4 code paths unchanged: add a `_divi5_draft(wp, a, content)` function, called only when the site is Divi 5.
- [ ] **Step 4: Live test** `tests/test_divi5_publish_live.py`:
  1. Create an Application Password for the admin via `wp5` and delete it in `tearDown`.
  2. Run `publish.py draft <fixture> --site http://divi-5-test.local --user <admin>` with `WP_APP_PASSWORD` in env.
  3. Assert exit 0, a stored meta `on`, and stored content equal to the canonical content.
  4. Temporarily publish via `wp5 post update ID --post_status=publish --user=<admin>`, curl the permalink, and assert `et_pb_pagebuilder_layout` and `et_no_sidebar` with no `entry-title`.
  5. Delete the page.
  6. Also test the image upload path with a small local PNG fixture.
- [ ] **Step 5: `publishing.md`:** add a "Divi 5" section covering detection, the refusal rules, why the builder meta needs the batch (with evidence), canonical `content.raw`, CSS regeneration, and a curl version of the sequence for manual use.
- [ ] **Step 6: Run** the offline suite, then the live one with `PP_LIVE_TESTS=1`.
- [ ] **Step 7: Commit** `divi5: publish.py drafts over REST with builder-meta batch, block image upload, publishing docs`

---

### Task 11: Tokens from Divi 5 block content

**Files:**
- Create: `Skill/divi-page-builder/scripts/tokens5_from_blocks.py`
- Test: `tests/test_divi5_tokens_blocks.py`

**Read first:** `research/divi5/tokens-and-detection.md` §4 (the proposed D5 tokens shape) and `tokens_from_shortcode.py` (the D4 counterpart; mirror its output sections).

**Interfaces:**
- Produces: `tokens5_from_documents(docs: list[Document], schema5) -> dict`, the partial tokens, with these keys:
  - `colors.palette`: literal colors with uses and roles;
  - `colors.global_refs`: the `gcid` ids used and where;
  - `variables_refs`: the `gvid` ids used;
  - `typography`: per heading level the font values (literal or `$variable`), sizes with tablet/phone, from `…decoration.font.font` / `headingLevel`; body font from text modules' `bodyFont`;
  - `spacing`: section padding frequencies, row widths/max-widths, gutters;
  - `shapes`: radii, shadows;
  - `presets`: `{module_name: [{"id","uses"}]}` from `modulePreset`, and `group_presets` from `groupPreset`;
  - `module_styles`: per module name, distinct design-only attr subtrees (design = the `decoration` and `advanced` groups minus content-ish leaves, decided by the schema5 leaf types `text`/`html`/`url`/`image` → content) with use count, preset ids, `module.advanced.htmlAttributes` classes/ids and context (section background dark/light plus color/image, position, admin label, column type);
  - `section_exemplars`: design-only skeletons of each section (text, links and images removed).

  `$variable()` strings are kept verbatim everywhere.

- [ ] **Step 1: Write the failing tests** on the converted fixtures:
  1. `module_styles` for `divi/blurb` exists with counts that sum to the number of blurbs.
  2. No `innerContent` text appears anywhere in `section_exemplars` (assert a known headline string from `divi-ai/layout.html` is absent).
  3. Presets list the `modulePreset` ids present in `divi-ai-layout.html`'s converted fixture with their counts.
  4. The typography scale reads the `h2` from a heading module.
  5. A `$variable` color stays a `$variable` string in module_styles and its id appears in `colors.global_refs`.
- [ ] **Step 2: Run to verify they fail. Step 3: Implement. Step 4: Run** the new and full suites.
- [ ] **Step 5: Commit** `divi5: tokens from block content`

---

### Task 12: Tokens from public HTML/CSS on Divi 5, `extract_tokens.py` dispatch, `design-tokens.md`

**Files:**
- Create: `Skill/divi-page-builder/scripts/tokens5_from_html.py`
- Modify: `Skill/divi-page-builder/scripts/extract_tokens.py`, `Skill/divi-page-builder/reference/design-tokens.md`
- Create: `tests/fixtures/divi5/html/*.html`, captured public pages of the local D5 site made by `research/tools/divi5/d5_tokens_probe.py` or curl. **They must not contain Divi's licensed CSS files:** strip the `<style>`/`<link>` contents down to the `:root` custom-property blocks and `preset--*` rules the tests need, or generate synthetic pages. Put a README note on provenance.
- Test: `tests/test_divi5_tokens_html.py`

**Interfaces:**
- Produces: `tokens5_from_html(html: str, css_by_url: dict | None = None) -> dict`, with:
  - `colors.global`: `{gcid: {"value": resolved hex/rgba}}` from `--gcid-*`;
  - `colors.customizer`: the 5 Customizer colors with ids;
  - `variables`: `{gvid: {"value": ..., "kind": number|font|image|…}}` from `--gvid-*`;
  - `fonts.customizer`: from `--et_global_*`;
  - `presets_css`: `{preset_id: {"module": name, "selector": ..., "declarations": {...}}}` from `.preset--module--<m>--<id>` and group preset classes;
  - `site.divi_version`: from asset `?ver=` or style.css when present in the html.
- `extract_tokens.py`: after fetching, detect the major version (`detect_site`, plus the content format of the fetched pages). On Divi 5, merge `tokens5_from_documents` with `tokens5_from_html` into the final `tokens.json`:
  - `site`: `{url, divi_version, divi_major: 5, content_format, source_pages}`;
  - `colors`: `{global, customizer, palette}`;
  - `variables`;
  - `typography`;
  - `spacing`;
  - `shapes`;
  - `presets`: per module `[{id, uses, css}]` (CSS joined from `presets_css`);
  - `group_presets`;
  - `module_styles`;
  - `section_exemplars`.

  Follow same-origin `et-cache` CSS links (R6 §8.4), and fetch one extra page with no variables when needed. Keep it simple: also fetch the site home page, since it often prints all active variables. The offline mode `--shortcode-file` becomes `--content-file` (keep the old flag as an alias), accepting blocks.

- [ ] **Step 1: Write the failing tests** on the fixture HTML:
  1. The 5 Customizer colors are extracted with correct values.
  2. A user `gcid` color used on the page is extracted.
  3. A number `gvid` variable is extracted.
  4. A preset's declarations are recovered.
  5. An offline end-to-end run of `extract_tokens.py --content-file tests/fixtures/divi5/divi-ai/layout.html --url http://x.test --html-file <fixture html> --out tmp.json` (add a hidden `--html-file` option for offline tests if needed) produces `site.divi_major == 5` and non-empty `module_styles`.
  6. The D4 extract tests are unchanged.
- [ ] **Step 2: Run to verify they fail. Step 3: Implement. Step 4: Run** the new and full suites.
- [ ] **Step 5: `design-tokens.md`:** add a Divi 5 section covering what's extracted, reference-versus-literal rules (spec §3.5), the read-only design system, unknown preset ids, and how `validate.py --tokens` uses the ids.
- [ ] **Step 6: Commit** `divi5: tokens from public HTML/CSS, extract_tokens dispatch, design-tokens docs`

---

### Task 13: Token fidelity end to end (live)

**Files:**
- Create: `research/tools/divi5/fidelity_setup.php` (based on R6's `r6_setup.php`/`r6_restore.php`), `tests/test_divi5_tokens_fidelity.py` (`@live5_only`)

**What it proves:** run `extract_tokens.py` over REST against the local Divi 5 site, set up with known design data:
- 3 global colors;
- a font variable and a number variable;
- a module preset on a button;
- an option-group preset on a heading font;
- a page using them all, plus literal responsive heading sizes and a custom class.

The extracted tokens must reproduce each known value exactly (colors resolved, variable values, preset CSS declarations, typography scale including tablet/phone). Then compose a tiny page from the tokens only (a heading + button using the recovered ids), validate it with `--tokens` (0 errors, 0 unknown-id warnings), push it with `publish.py draft`, and assert the rendered CSS for the button equals the original preset-styled button's CSS (compare the computed declarations in the `preset--` rule and the module's printed CSS). Restore the site in `tearDownClass` and delete the pages and Application Password.

- [ ] **Step 1: Write the setup/restore PHP. Step 2: Write the test. Step 3: Run** with `PP_LIVE_TESTS=1`; fix extraction bugs in Tasks 11/12 modules with offline regression tests for each.
- [ ] **Step 4: Commit** `divi5: live token fidelity test`

---

### Task 14: Divi 5 preview (Playground)

**Files:**
- Modify: `Skill/divi-page-builder/scripts/preview/preview.mjs`, `blueprint.json`, `mu-plugin/pp-preview.php`, `fetch-divi.mjs` (as `research/divi5/playground.md` requires), `Skill/divi-page-builder/scripts/preview.py`, `Skill/divi-page-builder/reference/preview.md`
- Test: extend `tests/test_preview_cli.py` (offline dispatch) and `tests/test_preview.py` (`@live5_only` render parity)

**Read first:** `research/divi5/playground.md` (GO/NO-GO, required changes, numbers) and `research/divi5/playground-prototype/`. This task ports that prototype into the shipped preview.

**Behaviour:**
- `preview.py render|serve` detects the format of each page.
  - **Shortcode:** today's paths are unchanged (the Python renderer default, `--exact` Playground).
  - **Blocks:** always use Playground with the Divi version from `--tokens`/`--divi`, defaulting to the newest cached 5.x, else latest.
- `render` for blocks writes the standalone HTML like `--exact` does today.
- `serve` for blocks keeps one Playground instance warm and re-renders on save, the way the D4 `--exact` serve works (if it doesn't, implement a warm Playground server in `preview.mjs serve` and document the timings).
- `doctor` reports Node and whether a 5.x Divi is cached.
- Local `./` images in blocks are inlined (data URIs, via `local_media.embed_local_images`'s blocks branch from Task 10).
- **Stock settings** apply: `var(--gcid-*)`/`--gvid-*` references render unset unless tokens are given. Seed them: when `--tokens` has `colors.global`/`variables`, inject a `:root{--gcid-…:…;--gvid-…:…}` style and the `presets[].css` rules into the rendered page. This is the tokens-seeding option from R6 §8.8; state its limits in `preview.md`.
- `fetch-divi 5.x` works through `fetch_divi.py` (the version regex accepts 5.x). Check the zip layout of Divi 5 downloads.

- [ ] **Step 1: Write offline tests:**
  1. A blocks page routes to the Playground command line with the correct Divi version (mock `run_exact` like the existing CLI tests do).
  2. Token seeding CSS is generated from a sample tokens dict (a pure function `seed_css(tokens) -> str`).
  3. `doctor` output mentions Divi 5 cache status.
- [ ] **Step 2: Implement the prototype port;** the offline tests pass.
- [ ] **Step 3: Live parity test** (`@live5_only`, needs Node and cached Divi 5): render 3 fixtures (`divi-ai/layout.html`, `converted/heldout-inscope.html`, `converted/content-heldout.html`) in Playground and on `divi-5-test.local`. Compare builder markup (tag/class sequence) and builder CSS declaration sets with `research/tools/fidelity.py`, asserting the thresholds the spike measured (identical markup; CSS declarations ≥ the spike's figure). Record the numbers in `research/divi5/playground.md`.
- [ ] **Step 4: `preview.md`:** Divi 5 section covering requirements (Node ≥ 20), timings, token seeding, and limits (client presets and variables only via tokens seeding; the WordPress draft stays the authoritative check).
- [ ] **Step 5: Run** the offline and live suites. **Commit** `divi5: Playground preview for block pages with token seeding`

---

### Task 15: `page_edit.py` for blocks and the Divi 5 edit recipes

**Files:**
- Modify: `Skill/divi-page-builder/scripts/page_edit.py`
- Create: `Skill/divi-page-builder/recipes/divi5/edits/{change-copy,insert-section,replace-section,restyle-to-tokens}.md`
- Test: `tests/test_divi5_page_edit.py`

**Behaviour:** the same CLI verbs (`outline`, `extract`, `replace`, `insert-after`, `insert-before`, `set-attr`, `delete`) work on block documents. Read `page_edit.py` and `tests/test_page_edit.py` and keep the argument shapes.
- **Paths:** use the `divi5_blocks` path syntax (`placeholder[0] > section[1] > …`). Accept the short form without `placeholder[0] >`.
- **`set-attr PATH ATTR VALUE [--breakpoint tablet] [--state hover]`:** VALUE is JSON if it parses as JSON, otherwise a string. The edited block is re-rendered canonically; every other byte is preserved.
- **`replace`/`insert-*`:** take a file of canonical block markup. Validate it parses, and splice the text at the block span boundaries.
- **Refusals:** `page_edit` refuses shortcode content when `--site-major 5` is given, or when the tokens say Divi 5 (Review Focus #3).
- **`outline`:** section → row → column → module with admin labels and heading text.

- [ ] **Step 1: Write the failing tests.**
  1. For each verb on `converted/heldout-inscope.html`, bytes outside the edited block are unchanged (compare prefix and suffix).
  2. The result validates with 0 new errors (`--baseline` original).
  3. `set-attr` with a hover state produces canonical JSON.
  4. Non-canonical VB-style input (Review Focus #1): editing one block leaves the `\n\n` separators and the other blocks' `\\` escapes intact.
  5. The D4 page_edit tests are unchanged.
- [ ] **Step 2: Implement. Step 3: Write the 4 edit recipes** with worked commands on a fixture (examples validated).
- [ ] **Step 4: Run** the suites. **Commit** `divi5: page_edit for block pages and D5 edit recipes`

---

### Task 16: Divi 5 recipe foundation and hero recipes

**Files:**
- Create: `recipes/divi5/README.md`, `recipes/divi5/sample-tokens.json` (the D5 counterpart of `recipes/sample-tokens.json`, produced by running `extract_tokens.py` offline on a Divi 5 fixture page plus fixture HTML, then curated), `research/tools/divi5/port_recipe.py`, `recipes/divi5/sections/{hero-split,hero-centered,hero-background-image,hero-fullwidth-header}.md`
- Test: extend `tests/test_divi5_docs.py` (all recipe examples validate with `--tokens recipes/divi5/sample-tokens.json`; each D4 recipe has a D5 counterpart once Tasks 16–18 are done, with the list asserted in Task 18)

**Porting method (spec §3.8):** `port_recipe.py recipes/sections/<name>.md` does the following:
1. Extracts the D4 worked example.
2. Converts it with `convert.php` through `wp5`.
3. Cleans it: sets `builderVersion` to the schema version, drops `locked`, drops values equal to render defaults, replaces the D4 sample-token colors/fonts with the D5 sample tokens' `$variable` refs where the D5 sample tokens have ids for those roles, and regenerates attribute-row UUIDs deterministically (uuid5 of the recipe name and index).
4. Validates it.
5. Writes a draft `recipes/divi5/sections/<name>.md`.

**Each D5 recipe file** covers:
- a one-line pointer to the shared recipe (`../../sections/<name>.md`) for purpose, SEO notes and variations;
- the **D5 structure tree**;
- the **D5 field mapping** (token path → attr path);
- the D5-specific responsive rules;
- the complete worked example (canonical, validated);
- a checklist.

Then a human-quality pass: read the ported example, fix awkward output, and keep only the attrs a person would set.

**Live check:** push each worked example to `divi-5-test.local` as a draft via `publish.py draft` and take one screenshot each (Playground preview or the site with Chrome/`shoot.mjs`). Look at it; fix visible problems. Delete the drafts. Screenshots are not committed.

- [ ] **Step 1: Write the test additions. Step 2: Write `port_recipe.py`** and the README (how D5 recipes map tokens to attrs, when to write `$variable` vs literal, choosing `module_styles` by context, exemplars).
- [ ] **Step 3: Port the 4 hero recipes;** validate, push, screenshot, fix.
- [ ] **Step 4: Run** the tests. **Commit** `divi5: recipe foundation, D5 sample tokens, hero recipes`

### Task 17: Divi 5 content-section recipes

**Files:** `recipes/divi5/sections/{services-grid,alternating-features,process-steps,stats-counters,service-area-list,tabs,video,gallery}.md`

Same method and checks as Task 16 (port, clean, human pass, validate, live push and screenshot, delete). **Commit** `divi5: content-section recipes`

### Task 18: Divi 5 social-proof, conversion and page recipes

**Files:** `recipes/divi5/sections/{testimonials,pricing,faq,cta-band,contact,team,trust-bar}.md`, `recipes/divi5/pages/{service-landing,local-seo-location,ppc-lead-gen,product-feature}.md`

- **Section recipes:** same method as Task 16. The FAQ keeps the `FAQPage` JSON-LD in a code module; check its JSON survives canonical escaping and renders in a `<script type="application/ld+json">`. Contact has **no signup custom fields**: the converter quirk means the ported contact form must be checked by rendering it.
- **Page recipes:** section order and rhythm for Divi 5, reusing the section recipes, plus a full-page worked example for `service-landing` that validates as a whole page (one H1).
- **Test:** every file in `recipes/sections/` has a counterpart in `recipes/divi5/sections/`, and every file in `recipes/pages/` one in `recipes/divi5/pages/`.

**Commit** `divi5: social-proof, conversion and page recipes`

---

### Task 19: `SKILL.md`, README and index completeness

**Files:**
- Modify: `Skill/divi-page-builder/SKILL.md`, `README.md`, `tests/test_skill_index.py`

**Changes to `SKILL.md`** (keep it short; progressive disclosure):
- **Frontmatter `description`:** add Divi 5 triggers ("Divi 5 page", `wp:divi/` blocks, "Divi 5 AI Genie"). Keep the existing triggers ("Divi Genie", "Divi 4 AI Genie").
- **Title/intro:** "Divi 4 and Divi 5". Update the **Not for** line (Divi 5 is now supported).
- **Workflow step 1:** "Which Divi?", from `tokens.json → site.divi_major`, or `python3 scripts/divi_format.py site URL`. Divi 5 → read `reference/divi5/*` and `recipes/divi5/*`; Divi 4 → today's files.
- **Hard rules, Divi 5 additions:**
  - write only `wp:divi/*` blocks in canonical JSON;
  - never Divi 4 shortcode on a Divi 5 site;
  - `builderVersion` = the site's version;
  - reference `gcid`/`gvid`/preset ids only from `tokens.json`, and omit `modulePreset` for the site default;
  - `&#91;`/`&#93;` for literal brackets in text;
  - drafts only via `publish.py`, which sets the builder meta.
- **Scripts table:** add `divi_format.py`, and note that the others are version-aware.
- **Reference index:** a Divi 5 sub-table (page-format, structure, value-formats, design-families, modules/README, recipes/divi5/README + each D5 recipe).

**README.md:** Divi 5 support in the feature list, requirements (Node for Divi 5 preview), the regeneration commands, and live tests for Divi 5.

**`test_skill_index.py`:** extend it so every file in `reference/divi5` and `recipes/divi5` is indexed, and every index entry exists.

- [ ] Steps: update the tests first (they fail), edit the docs, run the suites, **commit** `divi5: SKILL.md, README and index coverage for Divi 5`

---

### Task 20: Test the skill on fresh agents (Divi 5)

**Files:**
- Create: `research/skill-tests/divi5-brief-01.md`, `research/skill-tests/divi5-results.md`

Mirror D4 Task 21 (`research/skill-tests/results.md`) and read how it was run.
1. **Brief:** a realistic Divi 5 brief: a service landing page for "Octavio Lawn and Landscape", with services and FAQ, from `recipes/divi5/sample-tokens.json`.
2. **Baseline:** a fresh subagent with only the brief and tokens, and no skill. It writes a Divi 5 page. Record the validator results and a Playground render screenshot.
3. **With skill:** a fresh subagent with the brief, the tokens and the skill directory (instructed to follow `SKILL.md`). Record the validator results, the preview, a draft pushed to `divi-5-test.local` (then deleted), and a screenshot.
4. **Compare:** errors, warnings, structure quality and visuals. For every stumble in the with-skill run, fix the docs, then re-run until the with-skill run is clean (0 errors, sensible warnings) and the page looks right.
5. **Write up** the results.

**Commit** `divi5: fresh-agent skill test and doc fixes`

---

### Task 21: Python renderer spike for Divi 5 (measured decision)

**Files:**
- Create: `research/divi5/python-renderer-spike.md` (and a throwaway prototype in `research/divi5/python-renderer-spike/`, gitignored outputs)

Mirror `research/python-renderer-spike.md` (D4).
1. Estimate the D5 front-end render surface: the PHP StyleLibrary/ModuleLibrary render path, and how much differs from D4. Can the existing `divi_render` package be reused by converting D5 attrs back to D4 through the conversion map?
2. Prototype the cheapest credible path for 3 modules (section/row/column/text/heading/button).
3. Measure markup and CSS parity against real Divi 5 (Playground ground truth) on one tuned and one held-out page.
4. Recommend GO or NO-GO with numbers and an effort estimate.
5. **If GO:** append an addendum to the spec and new tasks to this plan (don't implement them in this task). **If NO-GO:** Playground stays the Divi 5 preview, and `preview.md` already says so.

**Commit** `research: Divi 5 Python renderer spike and decision`

---

### Task 22: Final verification

- [ ] Run the full offline suite: `python3 -m unittest discover -s tests`. All pass.
- [ ] Run the live suites with both local sites running: `PP_LIVE_TESTS=1 python3 -m unittest discover -s tests`. All pass; if the Divi 4 site is down, start it in Local first. Paste the summaries into `research/divi5/verification.md`.
- [ ] Regenerate schema5 and the docs, and confirm an empty `git diff`.
- [ ] `check_doc_examples.py` passes.
- [ ] Credential scan: `git grep -nE "api_key=|Basic [A-Za-z0-9+/=]{20,}"` finds nothing sensitive.
- [ ] Whole-branch review (superpowers:requesting-code-review).
- [ ] **Commit** `divi5: verification record`
