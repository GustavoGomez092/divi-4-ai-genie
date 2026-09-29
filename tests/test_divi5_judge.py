"""Divi as judge (live): WordPress 7.1 + Divi 5.13.1 check our Divi 5 parser, canonical JSON and fixtures.

research/tools/divi5/judge.php runs on the local Divi 5 site (divi-5-test.local). For one file it prints what
parse_blocks() returns (Divi registers ET\\Builder\\FrontEnd\\BlockParser\\BlockParser as the block parser),
serialize_block_attributes() of every block's decoded attrs, and a front-end render of the file as a draft page.
The tests compare that, block by block, with divi5_blocks:

1. tree and attrs: same blocks (names, nesting), same inner HTML chunks, same decoded attrs;
2. canonical bytes: serialize_block_attributes(attrs) == canonical_json(attrs), byte for byte, on every fixture
   block and on a synthetic block of floats, big ints, {} / "0".."n" keys and control characters;
3. render: no PHP errors/warnings/notices, one `.et_pb_section` per divi/section block;
4. invalid fixtures where Divi has an opinion: our validator is at least as strict.

Needs PP_LIVE_TESTS=1 and the site running; skips with a message otherwise.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES5, SITE5_URL, TOOLS5, d5_fixtures, live5_only, wp5
from divi5_blocks import Block, Freeform, _phpify, canonical_json, parse
from validate import validate_source

MARK = "D5JUDGE:"
JUDGE_TITLE = "D5TEST judge"  # judge.php's draft pages are titled "D5TEST judge <file>"
DIVI_PARSER = "ET\\Builder\\FrontEnd\\BlockParser\\BlockParser"
_CACHE = {}
_ADMIN = []


def _admin_id():
    if not _ADMIN:
        out = wp5("user", "list", "--role=administrator", "--field=ID", "--orderby=ID")
        ids = out.stdout.split()
        if out.returncode != 0 or not ids:
            raise unittest.SkipTest(f"local Divi 5 site unavailable (wp user list failed): {out.stderr[-300:]}")
        _ADMIN.append(ids[0])
    return _ADMIN[0]


def judge_pages():
    """IDs of pages left by judge.php (normally none: it deletes its page, but not after a fatal or a kill)."""
    out = wp5(f"--user={_admin_id()}", "post", "list", "--post_type=page", "--post_status=any", "--nopaging",
              "--fields=ID,post_title", "--format=json")
    if out.returncode != 0:
        raise AssertionError(f"wp post list failed: {out.stderr[-300:]}")
    return [str(p["ID"]) for p in json.loads(out.stdout[out.stdout.index("["):])
            if p["post_title"].startswith(JUDGE_TITLE)]


def sweep_judge_pages():
    ids = judge_pages()
    if ids:
        out = wp5(f"--user={_admin_id()}", "post", "delete", *ids, "--force")
        if out.returncode != 0:
            raise AssertionError(f"could not delete leftover judge pages {ids}: {out.stderr[-300:]}")
    return ids


def warm_site():
    """Deleting a page makes Divi flush its static CSS cache; view the home page once so the next live5_only
    probe (and anyone else) does not pay the slow regeneration."""
    import urllib.error
    import urllib.request
    try:
        urllib.request.urlopen(SITE5_URL + "/", timeout=60).read()
    except urllib.error.HTTPError:
        pass
    except Exception as e:  # never fail the run on the courtesy request
        print(f"warm-up of {SITE5_URL} failed: {e}")


def _class_cleanup():
    sweep_judge_pages()
    warm_site()


def judge(path, parse_only=False):
    """judge.php's JSON for one file (cached: each rendering call creates and deletes a draft page)."""
    key = (str(path), parse_only)
    if key not in _CACHE:
        extra = ["parse-only"] if parse_only else []
        out = wp5(f"--user={_admin_id()}", "eval-file", TOOLS5 / "judge.php", path, *extra, timeout=300)
        lines = [ln for ln in out.stdout.splitlines() if ln.startswith(MARK)]
        if out.returncode != 0 or len(lines) != 1:
            raise AssertionError(f"judge.php failed on {path.name} (exit {out.returncode}):\n"
                                 f"{out.stdout[-800:]}\n{out.stderr[-800:]}")
        _CACHE[key] = json.loads(lines[0][len(MARK):])
    return _CACHE[key]


def _block_shape(b: Block) -> dict:
    inner = [None if isinstance(c, Block) else c.value for c in b.children]
    return {"name": b.name, "attrs": _phpify(b.attrs), "canonical": canonical_json(b.attrs), "inner": inner,
            "children": [_block_shape(c) for c in b.blocks]}


def ours_source(src: str) -> list:
    """Our parse in judge.php's shape. Top-level text is a freeform node, as parse_blocks() makes it; text inside a
    block is its `inner` list (WordPress innerContent: HTML chunks, None where a child block sits). Attrs go through
    _phpify because PHP arrays cannot tell {} from [] or {"0":…} from a list; the canonical test checks bytes."""
    doc = parse(src)
    assert doc.problems == [], doc.problems
    return [{"name": None, "html": n.value} if isinstance(n, Freeform) else _block_shape(n) for n in doc.nodes]


def ours(path) -> list:
    return ours_source(path.read_text(encoding="utf-8"))


def _label(node, idx):
    return f"{node['name'] or 'freeform'}[{idx}]"


def diff_value(a, b, where):
    """First difference between two decoded JSON values, or None. Types are strict (true != 1) except int/float,
    which compare numerically: PHP json_encode() writes 1.0 as 1 on the way out of judge.php."""
    num = (int, float)
    if isinstance(a, num) and isinstance(b, num) and not isinstance(a, bool) and not isinstance(b, bool):
        return None if a == b else f"{where}: ours {a!r} vs Divi {b!r}"
    if type(a) is not type(b):
        return f"{where}: ours {type(a).__name__} {a!r:.80} vs Divi {type(b).__name__} {b!r:.80}"
    if isinstance(a, dict):
        if list(a) != list(b):
            return f"{where}: keys ours {list(a)} vs Divi {list(b)}"
        for k in a:
            d = diff_value(a[k], b[k], f"{where}.{k}")
            if d:
                return d
        return None
    if isinstance(a, list):
        if len(a) != len(b):
            return f"{where}: length ours {len(a)} vs Divi {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = diff_value(x, y, f"{where}[{i}]")
            if d:
                return d
        return None
    return None if a == b else f"{where}: ours {a!r:.200} vs Divi {b!r:.200}"


def diff_trees(mine, theirs, path, out, counts):
    """Append one message per differing node to `out`; count compared blocks in counts['blocks']."""
    if [n["name"] for n in mine] != [n["name"] for n in theirs]:
        out.append(f"{path or 'top'}: children ours {[n['name'] for n in mine]} vs Divi "
                   f"{[n['name'] for n in theirs]}")
        return
    for i, (m, t) in enumerate(zip(mine, theirs)):
        here = f"{path} > {_label(m, i)}" if path else _label(m, i)
        if m["name"] is None:
            if m["html"] != t["html"]:
                out.append(f"{here}: freeform ours {m['html']!r:.120} vs Divi {t['html']!r:.120}")
            continue
        counts["blocks"] += 1
        d = diff_value(m["attrs"], t["attrs"], "attrs")
        if d:
            out.append(f"{here}: {d}")
        # WP_Block_Parser::proceed() (and Divi's copy of it) appends an empty "" chunk when a nested block closes
        # right after its last child; it adds nothing to innerHTML, so it is dropped before comparing.
        their_inner = [c for c in t["inner"] if c != ""]
        if m["inner"] != their_inner:
            out.append(f"{here}: innerContent ours {m['inner']!r:.200} vs Divi {their_inner!r:.200}")
        diff_trees(m["children"], t["children"], here, out, counts)


def walk_pairs(mine, theirs, path=""):
    for i, (m, t) in enumerate(zip(mine, theirs)):
        if m["name"] is None:
            continue
        here = f"{path} > {_label(m, i)}" if path else _label(m, i)
        yield here, m, t
        yield from walk_pairs(m["children"], t["children"], here)


def flat(nodes):
    for n in nodes:
        if n["name"] is not None:
            yield n
            yield from flat(n["children"])


def first_diff(a: str, b: str) -> str:
    i = next((k for k, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return f"@{i}: ours …{a[max(0, i - 40):i + 60]!r} vs Divi …{b[max(0, i - 40):i + 60]!r}"


def rel(p):
    return str(p.relative_to(FIXTURES5))


@live5_only
class DiviJudge5Test(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls):
        _admin_id()  # SkipTest here if WP-CLI cannot reach the site
        sweep_judge_pages()
        cls.addClassCleanup(_class_cleanup)
        cls.fixtures = d5_fixtures()
        assert any(p.name == "escape-cases.html" for p in cls.fixtures)

    def test_tree_and_attrs_agree_with_divi(self):
        problems, per_file, total = [], {}, 0
        for p in self.fixtures:
            if judge(p)["parser"] != DIVI_PARSER:
                problems.append(f"{rel(p)}: parsed by {judge(p)['parser']}, not Divi's {DIVI_PARSER}")
            counts = {"blocks": 0}
            out = []
            diff_trees(ours(p), judge(p)["blocks"], "", out, counts)
            problems += [f"{rel(p)}: {m}" for m in out]
            per_file[rel(p)] = counts["blocks"]
            total += counts["blocks"]
        print(f"\ndivi5 judge (tree/attrs): {total} blocks compared in {len(self.fixtures)} fixtures, "
              f"{len(problems)} differences")
        self.assertGreater(total, 500)
        self.assertEqual(problems, [], "\n".join(problems[:20]))

    def test_canonical_json_matches_serialize_block_attributes(self):
        problems, total, expected, escaped = [], 0, 0, set()
        for p in self.fixtures:
            expected += sum(1 for _ in flat(ours(p)))
            for where, m, t in walk_pairs(ours(p), judge(p)["blocks"]):
                total += 1
                escaped.update(re.findall(r"\\u(?:005c|0022|002d|003c|003e|0026|2028|2029)", t["canonical"]))
                if m["canonical"] != t["canonical"]:
                    problems.append(f"{rel(p)}: {where}: {first_diff(m['canonical'], t['canonical'])}")
        print(f"\ndivi5 judge (canonical): {total - len(problems)}/{total} blocks byte-identical; "
              f"WP escapes seen: {sorted(escaped)}")
        self.assertEqual(total, expected, "walk_pairs compared fewer blocks than we parsed (trees differ?)")
        # escape-cases.html must make WordPress use every serialize_block_attributes() escape at least once.
        self.assertEqual(escaped, {"\\u005c", "\\u0022", "\\u002d", "\\u003c", "\\u003e", "\\u0026",
                                   "\\u2028", "\\u2029"})
        self.assertEqual(problems, [], "\n".join(problems[:20]))

    def test_divi_renders_every_fixture(self):
        problems, sections = [], 0
        for p in self.fixtures:
            want = sum(1 for b, _, _ in parse(p.read_text(encoding="utf-8")).walk() if b.name == "divi/section")
            render = judge(p)["render"]
            sections += render["sections"]
            if render["cleanup_warnings"]:
                problems.append(f"{rel(p)}: cleanup {render['cleanup_warnings']}")
            if not render["stored_identical"]:
                problems.append(f"{rel(p)}: WordPress changed the bytes on wp_insert_post")
            if render["php_notices"]:
                problems.append(f"{rel(p)}: PHP {render['php_notices'][:3]}")
            if render["sections"] != want:
                problems.append(f"{rel(p)}: {render['sections']} .et_pb_section elements for {want} divi/section")
            if render["modules"] == 0:
                problems.append(f"{rel(p)}: rendered no et_pb_ modules")
        print(f"\ndivi5 judge (render): {len(self.fixtures)} fixtures, {sections} sections rendered")
        self.assertEqual(problems, [], "\n".join(problems[:20]))


    def test_canonical_json_matches_php_on_synthetic_values(self):
        """Values the fixtures barely use (floats, big ints, {} and "0".."n" keys, controls), in plain json.dumps
        form: PHP json_decode()s them and serialize_block_attributes() must equal canonical_json()."""
        values = {
            "floats": [1.0, 0.5, 0.1, -0.0, 100.0, 1e15, 1e16, 1e17, 1e20, 1e-4, 1e-5, 2.5e-7, 123e-20, 123456.789,
                       0.30000000000000004, 12345678901234567.0, 1234567890123456.7, 1.7976931348623157e308,
                       5e-324, 34.01, -1.5e-10],
            "ints": [0, -1, 9223372036854775807, -9223372036854775808, 9223372036854775808, -9223372036854775809],
            "empty": {}, "emptyList": [], "nested": {"a": {"b": {}}, "c": [{}, {"0": 1}]},
            "seq": {"0": "x", "1": "y"}, "notSeq": {"1": "x"}, "backwards": {"1": "x", "0": "y"}, "lead0": {"01": "x"},
            "bools": [True, False, None],
            "strings": ["ctl\x01\x1f\x7f\b\f\n\r\t", "a\u2028b\u2029c", "---", "\\\\", '\\"', "\\-", "</x>&",
                        "\u00fc\u20ac\U0001f600", "/path/"],
        }
        src = f'<!-- wp:divi/text {json.dumps(values)} /-->'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.html"
            path.write_text(src, encoding="utf-8")
            (theirs,) = judge(path, parse_only=True)["blocks"]
        (mine,) = ours_source(src)
        self.assertIsNone(diff_value(mine["attrs"], theirs["attrs"], "attrs"))
        self.assertEqual(mine["canonical"], theirs["canonical"], first_diff(mine["canonical"], theirs["canonical"]))

    def test_invalid_fixtures_we_are_at_least_as_strict_as_divi(self):
        """What Divi 5.13.1 does with invalid input (recorded 2026-09-28), and our verdict on it:

        - bad-json.html (trailing comma in divi/text's JSON): parse_blocks() keeps the block with attrs null;
          the page renders with no PHP notice, but the text module silently renders nothing (4 modules, not 5).
          We: E5_BAD_JSON (error).
        - unknown-block.html (divi/fancy-text): parsed as a block with its attrs; renders nothing for it, no
          notice (4 modules). We: E5_UNKNOWN_BLOCK (error).
        - unclosed.html (no closing placeholder): the parser closes the open blocks at end of document and all 5
          modules render. Divi tolerates it; we: E5_UNCLOSED (error), since the next edit may nest wrongly.
        - noncanonical-lt.html (raw < > in the JSON): parses and renders all 5 modules for an administrator. We:
          E5_NONCANONICAL (error), because kses mangles raw < in comments for users without unfiltered_html.
        """
        cases = {"bad-json.html": ("E5_BAD_JSON", 4), "unknown-block.html": ("E5_UNKNOWN_BLOCK", 4),
                 "unclosed.html": ("E5_UNCLOSED", 5), "noncanonical-lt.html": ("E5_NONCANONICAL", 5)}
        for name, (code, modules) in cases.items():
            path = FIXTURES5 / "invalid" / name
            result = judge(path)
            self.assertEqual(result["render"]["php_notices"], [], name)
            self.assertEqual(result["render"]["modules"], modules, name)
            errors = [f.code for f in validate_source(path.read_text(encoding="utf-8")) if f.level == "error"]
            self.assertIn(code, errors, name)
        unknown = list(flat(judge(FIXTURES5 / "invalid" / "unknown-block.html")["blocks"]))
        self.assertIn("divi/fancy-text", [t["name"] for t in unknown])
        bad = list(flat(judge(FIXTURES5 / "invalid" / "bad-json.html")["blocks"]))
        self.assertEqual([t["attrs"] for t in bad if t["name"] == "divi/text"], [None])


    def test_judge_uses_divis_parser_and_sweep_removes_leftover_pages(self):
        """A disabled Divi would degrade the judge to core WordPress; a killed judge.php would leave its page."""
        self.assertEqual(judge(self.fixtures[0], parse_only=True)["parser"], DIVI_PARSER)
        out = wp5(f"--user={_admin_id()}", "post", "create", "--post_type=page", "--post_status=draft",
                  f"--post_title={JUDGE_TITLE} leftover-probe", "--porcelain")
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        leftover = out.stdout.strip().splitlines()[-1]
        self.assertIn(leftover, judge_pages())
        self.assertIn(leftover, sweep_judge_pages())
        self.assertEqual(judge_pages(), [])


if __name__ == "__main__":
    unittest.main()
