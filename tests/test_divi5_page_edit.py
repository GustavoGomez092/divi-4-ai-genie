"""page_edit.py on Divi 5 block pages: every verb changes only the targeted block's span."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, FIXTURES5, SCRIPTS

import divi5_blocks
from validate import validate_source

PAGE = FIXTURES5 / "converted" / "heldout-inscope.html"
D4_PAGE = FIXTURES / "valid" / "handwritten-landing.txt"
BAD_JSON = FIXTURES5 / "invalid" / "bad-json.html"


def read_raw(path) -> str:
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


SRC = read_raw(PAGE)
HEADING = "placeholder[0] > section[0] > row[0] > column[0] > heading[0]"
BUTTON = "placeholder[0] > section[0] > row[0] > column[0] > button[0]"
SECTION1 = "placeholder[0] > section[1]"
V = "5.13.1"
NEW_SECTION = (
    '<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"New band"}}},"decoration":{"layout":'
    '{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"' + V + '"} --><!-- wp:divi/row {"module":'
    '{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":'
    '{"display":"block"}}}}},"builderVersion":"' + V + '"} --><!-- wp:divi/column {"module":{"advanced":{"type":'
    '{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},'
    '"builderVersion":"' + V + '"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":'
    '"\\u003cp\\u003eNew copy\\u003c/p\\u003e"}}},"builderVersion":"' + V + '"} /--><!-- /wp:divi/column -->'
    '<!-- /wp:divi/row --><!-- /wp:divi/section -->')

# Visual Builder style (Review Focus #1): newlines between blocks, `\\` escapes, an empty open/close pair, CRLF.
VB = ('<!-- wp:divi/placeholder -->\n'
      '<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"A\\\\B"}}}},"builderVersion":"5.1.1"}'
      ' -->\n\n<!-- wp:divi/row {"builderVersion":"5.1.1"} -->\n\n<!-- wp:divi/column {"module":{"advanced":{"type":'
      '{"desktop":{"value":"4_4"}}}},"builderVersion":"5.1.1"} -->\n\n'
      '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"C:\\\\dir \\u0026 more"}}},'
      '"builderVersion":"5.1.1"} /-->\n\n'
      '<!-- wp:divi/divider {"builderVersion":"5.1.1"} --><!-- /wp:divi/divider -->\r\n\r\n'
      '<!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Hi \\\\ there"}}},'
      '"builderVersion":"5.1.1"} /-->\n\n'
      '<!-- /wp:divi/column -->\n\n<!-- /wp:divi/row -->\n\n<!-- /wp:divi/section -->\n\n'
      '<!-- wp:divi/section {"builderVersion":"5.1.1"} -->\n\n<!-- wp:divi/row {"builderVersion":"5.1.1"} -->\n\n'
      '<!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}}},"builderVersion":"5.1.1"}'
      ' -->\n\n<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"x\\\\y"}}},"builderVersion":'
      '"5.1.1"} /-->\n\n<!-- /wp:divi/column -->\n\n<!-- /wp:divi/row -->\n\n<!-- /wp:divi/section -->\n\n'
      '<!-- /wp:divi/placeholder -->')
VB_TEXT = "section[0] > row[0] > column[0] > text[0]"


def tmp_file(test, text: str, suffix=".html") -> Path:
    f = tempfile.NamedTemporaryFile("wb", suffix=suffix, delete=False)
    f.write(text.encode("utf-8"))
    f.close()
    test.addCleanup(lambda: Path(f.name).unlink(missing_ok=True))
    return Path(f.name)


def run(page, *args):
    proc = subprocess.run([sys.executable, str(SCRIPTS / "page_edit.py"), str(page), *map(str, args)],
                          capture_output=True)
    return proc.returncode, proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")


def ok(test, page, *args) -> str:
    code, out, err = run(page, *args)
    test.assertEqual(code, 0, err)
    return out


def span(src, path):
    b = divi5_blocks.parse(src).find(path)
    return b.start, b.end


def new_errors(out, baseline):
    return [(f.code, f.path, f.message) for f in validate_source(out, baseline=baseline)
            if f.level == "error" and not f.preexisting]


class VerbsOnConvertedPage(unittest.TestCase):
    def assert_outside_unchanged(self, out, start, end):
        self.assertEqual(out[:start], SRC[:start])
        self.assertEqual(out[len(out) - (len(SRC) - end):], SRC[end:])

    def test_outline_lists_labels_and_heading_text(self):
        out = ok(self, PAGE, "outline")
        self.assertIn("placeholder[0] > section[0]  admin_label=Hero image", out)
        self.assertIn('heading[0]  admin_label=None  title="Kitchen & Bath Remodeling Done Right"', out)
        self.assertIn("placeholder[0] > section[4] > fullwidth-header[0]", out)
        self.assertEqual(len(out.splitlines()), len(list(divi5_blocks.parse(SRC).walk())))

    def test_extract_accepts_short_path(self):
        start, end = span(SRC, BUTTON)
        self.assertEqual(ok(self, PAGE, "extract", BUTTON), SRC[start:end])
        self.assertEqual(ok(self, PAGE, "extract", BUTTON.replace("placeholder[0] > ", "")), SRC[start:end])

    def test_set_attr_rewrites_only_that_block(self):
        start, end = span(SRC, HEADING)
        out = ok(self, PAGE, "set-attr", HEADING.replace("placeholder[0] > ", ""), "title.innerContent",
                 'Kitchens <& "Baths"> -- done')
        self.assert_outside_unchanged(out, start, end)
        block = divi5_blocks.parse(out).find(HEADING)
        self.assertEqual(divi5_blocks.get_attr(block, "title.innerContent"), 'Kitchens <& "Baths"> -- done')
        self.assertEqual(block.attrs["builderVersion"], "5.0.0-public-beta.1")  # existing version kept
        self.assertEqual(block.raw_json, divi5_blocks.canonical_json(block.attrs))
        self.assertEqual(new_errors(out, SRC), [])

    def test_set_attr_hover_state_is_canonical(self):
        start, end = span(SRC, BUTTON)
        out = ok(self, PAGE, "set-attr", BUTTON, "button.decoration.background", '{"color":"#111827"}',
                 "--state", "hover")
        self.assert_outside_unchanged(out, start, end)
        block = divi5_blocks.parse(out).find(BUTTON)
        self.assertEqual(divi5_blocks.get_attr(block, "button.decoration.background", state="hover"),
                         {"color": "#111827"})
        self.assertEqual(divi5_blocks.get_attr(block, "button.decoration.background"), {"color": "#fbbf24"})
        self.assertEqual(out[start:block.end], "<!-- wp:divi/button " + divi5_blocks.canonical_json(block.attrs)
                         + " /-->")
        self.assertEqual(new_errors(out, SRC), [])

    def test_set_attr_breakpoint_and_json_values(self):
        out = ok(self, PAGE, "set-attr", HEADING, "title.decoration.font.font", '{"size":"40px"}',
                 "--breakpoint", "tablet")
        block = divi5_blocks.parse(out).find(HEADING)
        self.assertEqual(divi5_blocks.get_attr(block, "title.decoration.font.font", breakpoint="tablet"),
                         {"size": "40px"})
        # a text leaf keeps VALUE as typed (numbers, true, null stay text); a quoted JSON string is decoded
        for raw, want in (("Hello", "Hello"), ("2024", "2024"), ("42", "42"), ('"42"', "42"), ("true", "true"),
                          ("null", "null"), ("#fff", "#fff"), ('{"a":1}', '{"a":1}')):
            out = ok(self, PAGE, "set-attr", HEADING, "title.innerContent", raw)
            self.assertEqual(divi5_blocks.get_attr(divi5_blocks.parse(out).find(HEADING), "title.innerContent"),
                             want)
        # url and font-family leaves too
        out = ok(self, PAGE, "set-attr", BUTTON, "button.innerContent.linkUrl", "404")
        self.assertEqual(divi5_blocks.get_attr(divi5_blocks.parse(out).find(BUTTON), "button.innerContent")["linkUrl"],
                         "404")
        out = ok(self, PAGE, "set-attr", HEADING, "title.decoration.font.font.family", "1942")
        self.assertEqual(divi5_blocks.get_attr(divi5_blocks.parse(out).find(HEADING),
                                               "title.decoration.font.font")["family"], "1942")
        # a number leaf still parses JSON
        out = ok(self, PAGE, "set-attr", HEADING, "module.decoration.zIndex", "5")
        self.assertEqual(divi5_blocks.get_attr(divi5_blocks.parse(out).find(HEADING), "module.decoration.zIndex"), 5)

    def test_set_attr_non_responsive_key(self):
        out = ok(self, PAGE, "set-attr", HEADING, "modulePreset", '["default"]')
        self.assertEqual(divi5_blocks.parse(out).find(HEADING).attrs["modulePreset"], ["default"])

    def test_set_attr_explicit_breakpoint_state_path(self):
        # a path that already names `<breakpoint>.<state>` is written as-is, even where the key is new
        out = ok(self, PAGE, "set-attr", BUTTON, "button.innerContent.desktop.value.text", "Book now")
        self.assertEqual(divi5_blocks.get_attr(divi5_blocks.parse(out).find(BUTTON), "button.innerContent"),
                         {"text": "Book now", "linkUrl": "#start", "linkTarget": "on"})
        out = ok(self, PAGE, "set-attr", BUTTON, "button.innerContent.tablet.value.text", "Book")
        self.assertEqual(divi5_blocks.get_attr(divi5_blocks.parse(out).find(BUTTON), "button.innerContent",
                                               breakpoint="tablet"), {"text": "Book"})

    def test_set_attr_inside_a_responsive_value_keeps_its_other_keys(self):
        start, end = span(SRC, "placeholder[0] > section[0]")
        before = divi5_blocks.get_attr(divi5_blocks.parse(SRC).find("placeholder[0] > section[0]"),
                                       "module.decoration.background")
        out = ok(self, PAGE, "set-attr", "section[0]", "module.decoration.background.color", "#0f172a")
        section = divi5_blocks.parse(out).find("placeholder[0] > section[0]")
        self.assertEqual(divi5_blocks.get_attr(section, "module.decoration.background"),
                         dict(before, color="#0f172a"))  # image + gradient kept
        self.assertEqual(out[:start], SRC[:start])
        self.assertEqual(out[section.open_end:], SRC[SRC.index("-->", start) + 3:])  # children + rest verbatim
        out = ok(self, PAGE, "set-attr", BUTTON, "button.decoration.background.color", "#111111", "--state", "hover")
        self.assertEqual(divi5_blocks.get_attr(divi5_blocks.parse(out).find(BUTTON), "button.decoration.background",
                                               state="hover"), {"color": "#111111"})

    def test_set_attr_usage_errors(self):
        for args in (("button.decoration", "x"),                     # a group, not one value
                     ("button.decoration.background.tablet", "x"),   # half-named slot
                     ("modulePreset", "x", "--state", "hover")):     # state on a non-responsive key
            code, out, err = run(PAGE, "set-attr", BUTTON, *args)
            self.assertEqual((code, out), (2, ""), args)
            self.assertIn("page_edit.py", err)
        self.assertIn("not a known attribute path of divi/button",
                      run(PAGE, "set-attr", BUTTON, "button.decoration", "x")[2])
        self.assertIn("reference/divi5/modules/button.md", run(PAGE, "set-attr", BUTTON, "nonsense", "x")[2])
        code, out, err = run(PAGE, "set-attr", HEADING, "title.decoration.font.font.headingLevel", "h2", "--state",
                             "hover")  # headingLevel has no hover state
        self.assertEqual((code, out), (2, ""))
        self.assertIn("bad_state", err)
        code, out, err = run(PAGE, "set-attr", BUTTON, "button.innerContent.desktop.value.text", "x", "--state",
                             "hover")  # the path already names its slot
        self.assertEqual((code, out), (2, ""))

    def test_set_attr_places_a_missing_attribute_by_schema(self):
        # Review fix: the attribute doesn't exist on the block yet; the schema splits attr / sub-path.
        divider = "section[0] > row[0] > column[1] > divider[0]"
        self.assertIsNone(divi5_blocks.get_attr(divi5_blocks.parse(SRC).find("placeholder[0] > " + divider),
                                                "module.decoration.border", breakpoint=None))
        start, end = span(SRC, "placeholder[0] > " + divider)
        out = ok(self, PAGE, "set-attr", divider, "module.decoration.border.radius", '{"topLeft":"4px"}')
        block = divi5_blocks.parse(out).find("placeholder[0] > " + divider)
        self.assertEqual(block.attrs["module"]["decoration"]["border"], {"desktop": {"value": {"radius": {"topLeft": "4px"}}}})
        self.assertEqual(out[:start], SRC[:start])
        self.assertEqual(out[block.end:], SRC[end:])
        self.assertEqual(new_errors(out, SRC), [])
        # a key deeper inside a structured leaf, at states the block has never had
        for state in ("hover", "sticky"):
            out = ok(self, PAGE, "set-attr", divider, "module.decoration.border.radius.topLeft", "4px",
                     "--state", state)
            border = divi5_blocks.parse(out).find("placeholder[0] > " + divider).attrs["module"]["decoration"]["border"]
            self.assertEqual(border, {"desktop": {state: {"radius": {"topLeft": "4px"}}}})
        out = ok(self, PAGE, "set-attr", divider, "module.decoration.background.color", "#0f172a", "--state", "hover",
                 "--breakpoint", "tablet")
        self.assertEqual(divi5_blocks.parse(out).find("placeholder[0] > " + divider).attrs["module"]["decoration"]
                         ["background"], {"tablet": {"hover": {"color": "#0f172a"}}})

    def test_set_attr_heading_level_on_a_heading_without_font(self):
        # Review fix: a freshly inserted heading with no title.decoration at all.
        bare = ('<!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"New"}}},'
                '"builderVersion":"5.13.1"} /-->')
        inserted = ok(self, PAGE, "insert-after", HEADING, tmp_file(self, bare))
        page = tmp_file(self, inserted)
        path = "section[0] > row[0] > column[0] > heading[1]"
        out = ok(self, page, "set-attr", path, "title.decoration.font.font.headingLevel", "h2")
        block = divi5_blocks.parse(out).find("placeholder[0] > " + path)
        self.assertEqual(block.attrs["title"]["decoration"], {"font": {"font": {"desktop": {"value": {"headingLevel": "h2"}}}}})
        self.assertEqual(divi5_blocks.get_attr(block, "title.decoration.font.font")["headingLevel"], "h2")

    def test_set_attr_disabled_on_pseudo_breakpoint_path(self):
        out = ok(self, PAGE, "set-attr", HEADING, "module.decoration.disabledOn.desktopAbove.value", "on")
        self.assertEqual(divi5_blocks.parse(out).find(HEADING).attrs["module"]["decoration"]["disabledOn"],
                         {"desktopAbove": {"value": "on"}})

    def test_set_attr_locked_is_not_responsive(self):
        out = ok(self, PAGE, "set-attr", HEADING, "locked", '"on"')
        self.assertEqual(divi5_blocks.parse(out).find(HEADING).attrs["locked"], "on")

    def test_replace_splices_snippet_verbatim(self):
        start, end = span(SRC, SECTION1)
        snippet = tmp_file(self, "\n" + NEW_SECTION + "\n")
        out = ok(self, PAGE, "replace", "section[1]", snippet)
        self.assertEqual(out, SRC[:start] + NEW_SECTION + SRC[end:])
        self.assertEqual(new_errors(out, SRC), [])

    def test_insert_after_and_before(self):
        start, end = span(SRC, SECTION1)
        snippet = tmp_file(self, NEW_SECTION)
        out = ok(self, PAGE, "insert-after", SECTION1, snippet)
        self.assertEqual(out, SRC[:end] + NEW_SECTION + SRC[end:])
        self.assertEqual(new_errors(out, SRC), [])
        out = ok(self, PAGE, "insert-before", SECTION1, snippet)
        self.assertEqual(out, SRC[:start] + NEW_SECTION + SRC[start:])
        self.assertEqual(new_errors(out, SRC), [])

    def test_delete(self):
        start, end = span(SRC, SECTION1)
        out = ok(self, PAGE, "delete", SECTION1)
        self.assertEqual(out, SRC[:start] + SRC[end:])
        self.assertEqual(new_errors(out, SRC), [])

    def test_out_file_keeps_crlf(self):
        crlf = SRC.replace("<!-- /wp:divi/section -->", "<!-- /wp:divi/section -->\r\n")
        page = tmp_file(self, crlf)
        out_path = page.with_suffix(".out.html")
        self.addCleanup(lambda: out_path.unlink(missing_ok=True))
        ok(self, page, "set-attr", HEADING, "title.innerContent", "New", "--out", out_path)
        result = out_path.read_bytes().decode("utf-8")
        start, end = span(crlf, HEADING)
        self.assertEqual(result[:start], crlf[:start])
        self.assertEqual(result[len(result) - (len(crlf) - end):], crlf[end:])
        self.assertEqual(result.count("\r\n"), crlf.count("\r\n"))

    def test_bad_path(self):
        code, _, err = run(PAGE, "extract", "section[9]")
        self.assertEqual(code, 2)
        self.assertIn("no node at", err)
        code, _, err = run(PAGE, "extract", "section(0)")
        self.assertEqual(code, 2)
        self.assertIn("bad path", err)


class ValidateCliBaseline(unittest.TestCase):
    """validate.py PAGE --baseline ORIGINAL reports 0 new errors after every mutating verb."""

    def test_every_mutating_verb(self):
        snippet = tmp_file(self, NEW_SECTION)
        cases = (("set-attr", HEADING, "title.innerContent", "New headline"),
                 ("set-attr", "section[0]", "module.decoration.background.color", "#0f172a"),
                 ("set-attr", BUTTON, "button.decoration.background", '{"color":"#111827"}', "--state", "hover"),
                 ("replace", SECTION1, snippet), ("insert-after", SECTION1, snippet),
                 ("insert-before", SECTION1, snippet), ("delete", SECTION1))
        for args in cases:
            with self.subTest(args=args[:2]):
                out = tmp_file(self, "")
                ok(self, PAGE, *args, "--out", out)
                proc = subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), str(out), "--baseline",
                                       str(PAGE)], capture_output=True, text=True, timeout=120)
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("Summary: 0 error(s)", proc.stdout)


class NonCanonicalInput(unittest.TestCase):
    """Review Focus #1: VB/converter output parses, and one edit leaves every other byte alone."""

    def setUp(self):
        self.page = tmp_file(self, VB)

    def test_set_attr_keeps_separators_and_other_escapes(self):
        start, end = span(VB, "placeholder[0] > " + VB_TEXT)
        out = ok(self, self.page, "set-attr", VB_TEXT, "content.innerContent", "new")
        self.assertEqual(out[:start], VB[:start])
        self.assertEqual(out[len(out) - (len(VB) - end):], VB[end:])
        self.assertIn('"A\\\\B"', out)          # the parent section's VB escape, untouched
        self.assertIn('"Hi \\\\ there"', out)   # a sibling's
        self.assertIn('"x\\\\y"', out)          # another section's
        self.assertIn("<!-- wp:divi/divider {\"builderVersion\":\"5.1.1\"} --><!-- /wp:divi/divider -->\r\n\r\n",
                      out)
        self.assertEqual(out.count("\n\n"), VB.count("\n\n"))

    def test_set_attr_on_vb_block_renders_it_canonically(self):
        heading = "section[0] > row[0] > column[0] > heading[0]"
        start, end = span(VB, "placeholder[0] > " + heading)
        out = ok(self, self.page, "set-attr", heading, "module.meta.adminLabel", "Intro")
        edited = out[start:len(out) - (len(VB) - end)]
        self.assertIn('"Hi \\u005c there"', edited)  # only the edited block is re-rendered (canonical escape)
        self.assertEqual(out.replace(edited, VB[start:end]), VB)

    def test_set_attr_on_empty_open_close_pair(self):
        divider = "section[0] > row[0] > column[0] > divider[0]"
        start, end = span(VB, "placeholder[0] > " + divider)
        out = ok(self, self.page, "set-attr", divider, "module.meta.adminLabel", "Rule")
        self.assertEqual(out[:start], VB[:start])
        self.assertEqual(out[len(out) - (len(VB) - end):], VB[end:])

    def test_insert_replace_delete_leave_neighbours(self):
        snippet = tmp_file(self, NEW_SECTION)
        start, end = span(VB, "placeholder[0] > section[1]")
        self.assertEqual(ok(self, self.page, "insert-before", "section[1]", snippet),
                         VB[:start] + NEW_SECTION + VB[start:])
        self.assertEqual(ok(self, self.page, "insert-after", "section[0]", snippet),
                         VB[:span(VB, "placeholder[0] > section[0]")[1]] + NEW_SECTION
                         + VB[span(VB, "placeholder[0] > section[0]")[1]:])
        self.assertEqual(ok(self, self.page, "replace", "section[1]", snippet), VB[:start] + NEW_SECTION + VB[end:])
        self.assertEqual(ok(self, self.page, "delete", "section[1]"), VB[:start] + VB[end:])

    def test_outline_and_extract(self):
        doc = divi5_blocks.parse(VB)
        self.assertEqual(doc.problems, [])
        out = ok(self, self.page, "outline")
        self.assertEqual([line.split("  ")[0] for line in out.splitlines()], [p for _, p, _ in doc.walk()])
        self.assertIn('title="Hi \\ there"', out)
        start, end = span(VB, "placeholder[0] > " + VB_TEXT)
        self.assertEqual(ok(self, self.page, "extract", VB_TEXT), VB[start:end])
        start, end = span(VB, "placeholder[0] > section[0]")
        self.assertEqual(ok(self, self.page, "extract", "section[0]"), VB[start:end])

    def test_set_attr_on_container_keeps_its_inner_bytes(self):
        section = divi5_blocks.parse(VB).find("placeholder[0] > section[0]")
        out = ok(self, self.page, "set-attr", "section[0]", "module.meta.adminLabel", "Renamed")
        edited = divi5_blocks.parse(out).find("placeholder[0] > section[0]")
        self.assertEqual(out[:section.start], VB[:section.start])
        self.assertEqual(out[edited.open_end:], VB[section.open_end:])  # "\n\n" separators, children, closer
        self.assertEqual(out[section.start:edited.open_end],
                         "<!-- wp:divi/section " + divi5_blocks.canonical_json(edited.attrs) + " -->")
        self.assertEqual(edited.attrs["builderVersion"], "5.1.1")

    def test_module_level_splices_keep_blank_line_separators(self):
        snippet = tmp_file(self, '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"new"}}},'
                                 '"builderVersion":"5.1.1"} /-->')
        new = read_raw(snippet)
        heading = "section[0] > row[0] > column[0] > heading[0]"
        start, end = span(VB, "placeholder[0] > " + heading)
        self.assertEqual(ok(self, self.page, "replace", heading, snippet), VB[:start] + new + VB[end:])
        self.assertEqual(ok(self, self.page, "insert-before", heading, snippet), VB[:start] + new + VB[start:])
        self.assertEqual(ok(self, self.page, "insert-after", heading, snippet), VB[:end] + new + VB[end:])
        self.assertEqual(ok(self, self.page, "delete", heading), VB[:start] + VB[end:])
        self.assertIn("\r\n\r\n\n\n<!-- /wp:divi/column -->", ok(self, self.page, "delete", heading))

    def test_no_placeholder_wrapper(self):
        inner = VB[len("<!-- wp:divi/placeholder -->\n"):-len("<!-- /wp:divi/placeholder -->")]
        page = tmp_file(self, inner)
        start, end = span(inner, VB_TEXT)
        for path in (VB_TEXT, "placeholder[0] > " + VB_TEXT):
            out = ok(self, page, "set-attr", path, "content.innerContent", "new")
            self.assertEqual(out[:start], inner[:start])
            self.assertEqual(out[len(out) - (len(inner) - end):], inner[end:])
        snippet = tmp_file(self, NEW_SECTION)
        s_start, s_end = span(inner, "section[1]")
        for path in ("section[1]", "placeholder[0] > section[1]"):
            self.assertEqual(ok(self, page, "extract", path), inner[s_start:s_end])
            self.assertEqual(ok(self, page, "delete", path), inner[:s_start] + inner[s_end:])
            self.assertEqual(ok(self, page, "replace", path, snippet), inner[:s_start] + NEW_SECTION + inner[s_end:])
            self.assertEqual(ok(self, page, "insert-before", path, snippet),
                             inner[:s_start] + NEW_SECTION + inner[s_start:])
            self.assertEqual(ok(self, page, "insert-after", path, snippet), inner[:s_end] + NEW_SECTION + inner[s_end:])
        self.assertIn("section[1]  admin_label=None", ok(self, page, "outline"))


class Refusals(unittest.TestCase):
    def test_parse_problems_refuse_mutations(self):
        for args in (("set-attr", "section[0]", "module.meta.adminLabel", "x"), ("delete", "section[0]")):
            code, out, err = run(BAD_JSON, *args)
            self.assertEqual(code, 1, err)
            self.assertEqual(out, "")
            self.assertIn("E5_BAD_JSON", err)
            self.assertIn("refusing", err)

    def test_parse_problems_still_outline_with_warning(self):
        code, out, err = run(BAD_JSON, "outline")
        self.assertEqual(code, 0, err)
        self.assertIn("placeholder[0] > section[0]", out)
        self.assertIn("warning", err)

    def test_parse_problems_extract_warns(self):
        code, out, err = run(BAD_JSON, "extract", "section[0]")
        self.assertEqual(code, 0, err)
        self.assertTrue(out.startswith("<!-- wp:divi/section"))
        self.assertIn("warning", err)
        self.assertIn("E5_BAD_JSON", err)

    def test_placeholder_snippet_refused_inside_page(self):
        code, out, err = run(PAGE, "insert-after", SECTION1,
                             tmp_file(self, "<!-- wp:divi/placeholder -->" + NEW_SECTION + "<!-- /wp:divi/placeholder -->"))
        self.assertEqual((code, out), (1, ""))
        self.assertIn("placeholder", err)

    def test_insert_at_placeholder_refused(self):
        for verb in ("insert-after", "insert-before"):
            for path in ("placeholder[0]", "divi/placeholder[0]"):
                code, out, err = run(PAGE, verb, path, tmp_file(self, NEW_SECTION))
                self.assertEqual((code, out), (1, ""), (verb, path))
                self.assertIn("outside the page's divi/placeholder", err)

    def test_mixed_page_refused(self):
        page = tmp_file(self, SRC + "[et_pb_section][/et_pb_section]")
        code, out, err = run(page, "outline")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("mixes", err)

    def test_bad_snippet_refused(self):
        for text in (NEW_SECTION[:-10], "[et_pb_text]x[/et_pb_text]", "hello " + NEW_SECTION):
            code, out, err = run(PAGE, "insert-after", SECTION1, tmp_file(self, text))
            self.assertEqual(code, 1, text)
            self.assertEqual(out, "")
            self.assertIn("page_edit.py:", err)

    def test_shortcode_refused_on_divi5_site(self):
        code, out, err = run(D4_PAGE, "set-attr", "et_pb_section[0]", "admin_label", "x", "--site-major", "5")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("Divi 5", err)
        tokens = tmp_file(self, json.dumps({"site": {"divi_version": "5.13.1"}}), ".json")
        code, _, err = run(D4_PAGE, "outline", "--tokens", tokens)
        self.assertEqual(code, 1)
        self.assertIn("Divi 5", err)

    def test_blocks_refused_on_divi4_site(self):
        code, out, err = run(PAGE, "outline", "--site-major", "4")
        self.assertEqual(code, 1)
        self.assertIn("Divi 4", err)
        tokens = tmp_file(self, json.dumps({"site": {"divi_major": 4}}), ".json")
        code, _, err = run(PAGE, "delete", SECTION1, "--tokens", tokens)
        self.assertEqual(code, 1)

    def test_matching_site_major_is_accepted(self):
        self.assertEqual(ok(self, PAGE, "outline", "--site-major", "5"), ok(self, PAGE, "outline"))
        self.assertEqual(ok(self, D4_PAGE, "outline", "--site-major", "4"), ok(self, D4_PAGE, "outline"))

    def test_block_snippet_refused_on_shortcode_page(self):
        code, out, err = run(D4_PAGE, "insert-after", "et_pb_section[0]", tmp_file(self, NEW_SECTION))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")


class BuilderVersion(unittest.TestCase):
    def test_inserted_block_without_builder_version_warns_and_is_kept_as_is(self):
        snippet = NEW_SECTION.replace(',"builderVersion":"' + V + '"} /-->', "} /-->")
        self.assertNotEqual(snippet, NEW_SECTION)
        code, out, err = run(PAGE, "insert-after", SECTION1, tmp_file(self, snippet))
        self.assertEqual(code, 0, err)
        self.assertIn(snippet, out)
        self.assertIn("builderVersion", err)
        self.assertIn("text[0]", err)

    def test_complete_snippet_is_silent(self):
        code, _, err = run(PAGE, "insert-after", SECTION1, tmp_file(self, NEW_SECTION))
        self.assertEqual((code, err), (0, ""))

    def test_set_attr_builder_version_warns(self):
        code, out, err = run(PAGE, "set-attr", HEADING, "builderVersion", V)
        self.assertEqual(code, 0, err)
        self.assertIn("builderVersion", err)
        self.assertEqual(divi5_blocks.parse(out).find(HEADING).attrs["builderVersion"], V)


if __name__ == "__main__":
    unittest.main()
