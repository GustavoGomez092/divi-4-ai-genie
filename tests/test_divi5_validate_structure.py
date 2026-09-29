"""Divi 5 validator: format dispatch, structure (E5_*) and heading checks."""
import io
import json
import unittest
from contextlib import redirect_stdout

from _paths import FIXTURES5, d5_fixtures
from divi5_blocks import canonical_json
from validate import main, validate_source

EXPECT = {
    "mixed.html": "E5_MIXED_FORMAT", "bad-json.html": "E5_BAD_JSON", "unclosed.html": "E5_UNCLOSED",
    "unknown-block.html": "E5_UNKNOWN_BLOCK", "text-in-section.html": "E5_BAD_PARENT",
    "row-at-top.html": "E5_TOPLEVEL", "fullwidth-with-row.html": "E5_SECTION_TYPE",
    "columns-mismatch.html": "E5_COLUMNS", "two-h1.html": "E5_MULTIPLE_H1", "freeform.html": "E5_NOT_DIVI",
    "specialty-no-specialty-column.html": "E5_SPECIALTY_COLUMN", "inner-row-misplaced.html": "E5_INNER_ROW_PLACEMENT",
}
STRUCTURE_CODES = {"E5_BAD_PARENT", "E5_TOPLEVEL", "E5_SECTION_TYPE", "E5_COLUMNS",
                   "E5_SPECIALTY_COLUMN", "E5_INNER_ROW_PLACEMENT",
                   "E5_UNKNOWN_BLOCK", "E5_BAD_JSON", "E5_MISNESTED", "E5_UNCLOSED"}
HEADING_CODES = {"E5_MULTIPLE_H1", "W_NO_H1", "W_HEADING_SKIP"}

LAYOUT = '"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}}'


def codes(src, **kw):
    return [f.code for f in validate_source(src, **kw) if f.level == "error"]


def heading(text, level=None):
    font = f',"decoration":{{"font":{{"font":{{"desktop":{{"value":{{"headingLevel":"{level}"}}}}}}}}}}' if level else ""
    return ('<!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"' + text + '"}}' + font + '},'
            + LAYOUT + '} /-->')


def text(html):
    return '<!-- wp:divi/text ' + canonical_json({"content": {"innerContent": {"desktop": {"value": html}}}}) + ' /-->'


# The helper blocks carry no builderVersion (a divi5_checks_values warning); structure tests look past it.
def structural(findings):
    return [f for f in findings if f.code != "W5_BUILDER_VERSION"]


def blurb(title, level=None):
    font = f',"decoration":{{"font":{{"font":{{"desktop":{{"value":{{"headingLevel":"{level}"}}}}}}}}}}' if level else ""
    return '<!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":"' + title + '"}}' + font + '}} /-->'


def column(inner, ctype="4_4", extra="", name="column"):
    return (f'<!-- wp:divi/{name} {{"module":{{"advanced":{{"type":{{"desktop":{{"value":"{ctype}"}}}}{extra}}}}}}} -->'
            f'{inner}<!-- /wp:divi/{name} -->')


def inner_col(inner, ctype="4_4"):
    return column(inner, ctype, name="column-inner")


def row(inner, structure=None, name="divi/row"):
    adv = f'{{"module":{{"advanced":{{"columnStructure":{{"desktop":{{"value":"{structure}"}}}}}}}}}} ' \
        if structure else ""
    short = name[5:]
    return f'<!-- wp:divi/{short} {adv}-->{inner}<!-- /wp:divi/{short} -->'


def section(inner, stype=None):
    adv = f'{{"module":{{"advanced":{{"type":{{"desktop":{{"value":"{stype}"}}}}}}}}}} ' if stype else ""
    return f'<!-- wp:divi/section {adv}-->{inner}<!-- /wp:divi/section -->'


def page(*sections, placeholder=True):
    body = "\n".join(sections)
    return f"<!-- wp:divi/placeholder -->\n{body}\n<!-- /wp:divi/placeholder -->" if placeholder else body


def simple(*modules):
    return page(section(row(column("".join(modules)))))


H1 = heading("Main", "h1")


class Structure5Test(unittest.TestCase):
    def test_valid_fixtures_have_no_structure_errors(self):
        for p in d5_fixtures():
            if "invalid" in p.parts:
                continue
            errs = [f for f in validate_source(p.read_text()) if f.level == "error" and f.code.startswith("E5_")
                    and f.code in STRUCTURE_CODES]
            self.assertEqual(errs, [], p.name)

    def test_valid_fixtures_have_no_d5_structure_errors_at_all(self):
        structural = STRUCTURE_CODES | {"E5_NOT_DIVI", "E5_MIXED_FORMAT", "E5_STRAY_CLOSE"}
        for p in d5_fixtures():
            got = [(f.code, f.path, f.message) for f in validate_source(p.read_text()) if f.code in structural]
            self.assertEqual(got, [], p.name)

    def test_each_invalid_fixture(self):
        for name, code in EXPECT.items():
            src = (FIXTURES5 / "invalid" / name).read_text()
            self.assertIn(code, codes(src), name)

    def test_each_invalid_fixture_has_only_its_error(self):
        for name, code in EXPECT.items():
            src = (FIXTURES5 / "invalid" / name).read_text()
            self.assertEqual(sorted(set(codes(src))), [code], name)

    def test_d4_path_unchanged(self):
        from _paths import FIXTURES
        from divi_schema import load_schema
        src = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()
        self.assertEqual([f.code for f in validate_source(src, load_schema())],
                         [f.code for f in validate_source(src)])

    def test_d4_schema_passed_positionally_is_ignored_for_blocks(self):
        from divi_schema import load_schema
        src = (FIXTURES5 / "invalid" / "two-h1.html").read_text()
        self.assertEqual([f.code for f in validate_source(src, load_schema())],
                         [f.code for f in validate_source(src)])

    def test_heading_rules(self):
        src = (FIXTURES5 / "invalid" / "two-h1.html").read_text()
        f = [f for f in validate_source(src) if f.code == "E5_MULTIPLE_H1"][0]
        self.assertIn(">", f.path)
        self.assertGreater(f.line, 0)

    def test_findings_carry_block_name_and_position(self):
        src = (FIXTURES5 / "invalid" / "two-h1.html").read_text()
        f = [f for f in validate_source(src) if f.code == "E5_MULTIPLE_H1"][0]
        self.assertEqual(f.tag, "divi/heading")
        self.assertEqual(f.line, 3)
        self.assertEqual(f.path, "placeholder[0] > section[1] > row[0] > column[0] > heading[0]")
        start = src.index("<!-- wp:divi/heading", src.index("\n", src.index("\n") + 1))
        self.assertEqual(f.col, start - src.rindex("\n", 0, start))

    def test_mixed_reports_only_mixed(self):
        src = (FIXTURES5 / "invalid" / "mixed.html").read_text()
        found = validate_source(src)
        self.assertEqual([f.code for f in found], ["E5_MIXED_FORMAT"])
        self.assertEqual(found[0].line, 4)  # the shortcode after the placeholder


class Placement5Test(unittest.TestCase):
    def test_clean_page(self):
        self.assertEqual([f.code for f in structural(validate_source(simple(H1, text("<p>x</p>"))))], [])

    def test_no_placeholder_warns_on_whole_pages_only(self):
        src = page(section(row(column(H1))), placeholder=False)
        found = structural(validate_source(src))
        self.assertEqual([(f.level, f.code) for f in found], [("warning", "W5_NO_PLACEHOLDER")])
        self.assertEqual(structural(validate_source(src, fragment=True)), [])

    def test_non_divi_block_and_top_level_text(self):
        src = page(section(row(column(H1 + "<!-- wp:paragraph --><p>x</p><!-- /wp:paragraph -->"))))
        self.assertEqual(codes(src), ["E5_NOT_DIVI"])
        self.assertEqual(codes("Hello\n" + simple(H1)), ["E5_NOT_DIVI"])

    def test_out_of_scope_block_warns(self):
        src = simple(H1, '<!-- wp:divi/woocommerce-product-price /-->')
        found = [(f.level, f.code, f.tag) for f in structural(validate_source(src))]
        self.assertEqual(found, [("warning", "W5_OUT_OF_SCOPE", "divi/woocommerce-product-price")])

    def test_child_module_outside_its_parent(self):
        src = simple(H1, '<!-- wp:divi/slide /-->')
        self.assertEqual(codes(src), ["E5_BAD_PARENT"])

    def test_wrong_child_in_parent_module(self):
        src = simple(H1, '<!-- wp:divi/accordion --><!-- wp:divi/tab /--><!-- /wp:divi/accordion -->')
        self.assertEqual(codes(src), ["E5_BAD_PARENT"])

    def test_module_nested_in_leaf_module(self):
        src = simple(H1, '<!-- wp:divi/text --><!-- wp:divi/button /--><!-- /wp:divi/text -->')
        self.assertEqual(codes(src), ["E5_BAD_PARENT"])

    def test_fullwidth_module_in_column(self):
        src = simple(H1, '<!-- wp:divi/fullwidth-code /-->')
        self.assertEqual(codes(src), ["E5_BAD_PARENT"])

    def test_nested_placeholder(self):
        src = simple(H1, '<!-- wp:divi/placeholder --><!-- /wp:divi/placeholder -->')
        self.assertEqual(codes(src), ["E5_BAD_PARENT"])

    def test_stray_close_and_misnested(self):
        self.assertEqual(codes(simple(H1) + "<!-- /wp:divi/row -->"), ["E5_STRAY_CLOSE"])
        src = page(section(row(column(H1).replace("<!-- /wp:divi/column -->", ""))))
        self.assertIn("E5_MISNESTED", codes(src))


class SectionType5Test(unittest.TestCase):
    def test_bad_section_type(self):
        f = [f for f in validate_source(page(section(row(column(H1)), stype="wide"))) if f.level == "error"]
        self.assertEqual([(f.code, f.attr, f.value) for f in f], [("E5_SECTION_TYPE", "module.advanced.type", "wide")])

    def test_regular_section_type_is_accepted(self):
        self.assertEqual(codes(page(section(row(column(H1)), stype="regular"))), [])

    def test_regular_section_rejects_columns(self):
        self.assertEqual(codes(page(section(column(H1)))), ["E5_SECTION_TYPE"])

    def test_fullwidth_section_accepts_fullwidth_modules(self):
        fw = ('<!-- wp:divi/fullwidth-header {"title":{"innerContent":{"desktop":{"value":"Hi"}}}} /-->')
        self.assertEqual(codes(page(section(fw, stype="fullwidth"))), [])
        self.assertEqual(codes(page(section(fw))), ["E5_SECTION_TYPE"])

    def specialty(self, left, right, right_extra=',"specialtyColumns":{"desktop":{"value":"2"}}'):
        return page(section(column(left, "1_3") + column(right, "2_3", right_extra), stype="specialty"))

    def test_specialty_section(self):
        inner = row(inner_col(H1, "1_2") + inner_col(text("<p>x</p>"), "1_2"), "1_2,1_2", "divi/row-inner")
        self.assertEqual(codes(self.specialty(text("<p>a</p>"), inner)), [])

    def test_specialty_rejects_rows(self):
        self.assertEqual(sorted(codes(page(section(row(column(H1)), stype="specialty")))),
                         ["E5_SECTION_TYPE", "E5_SPECIALTY_COLUMN"])

    def test_specialty_needs_exactly_one_specialty_column(self):
        # Divi 4 E_SPECIALTY_COLUMN: exactly one column carries specialtyColumns
        plain = page(section(column(text("<p>a</p>"), "1_3") + column(H1, "2_3"), stype="specialty"))
        self.assertEqual(codes(plain), ["E5_SPECIALTY_COLUMN"])
        sc = ',"specialtyColumns":{"desktop":{"value":"2"}}'
        inner = row(inner_col(text("<p>a</p>")), None, "divi/row-inner")
        two = page(section(column(inner, "1_3", sc) + column(inner, "2_3", sc), stype="specialty"))
        self.assertEqual(codes(two), ["E5_SPECIALTY_COLUMN"])

    def test_inner_row_needs_the_specialty_column(self):
        # Divi 4 E_INNER_ROW_PLACEMENT: a row-inner in a specialty-section column without specialtyColumns
        inner = row(inner_col(H1), None, "divi/row-inner")
        src = self.specialty(text("<p>a</p>"), inner, "")
        self.assertEqual(sorted(codes(src)), ["E5_INNER_ROW_PLACEMENT", "E5_SPECIALTY_COLUMN"])
        found = [f for f in validate_source(src) if f.code == "E5_INNER_ROW_PLACEMENT"]
        self.assertEqual([(f.tag, f.path) for f in found],
                         [("divi/row-inner", "placeholder[0] > section[0] > column[1] > row-inner[0]")])

    def test_specialty_column_holds_only_inner_rows(self):
        inner = row(inner_col(H1), None, "divi/row-inner")
        self.assertEqual(codes(self.specialty(text("<p>a</p>"), inner + text("<p>b</p>"))), ["E5_SECTION_TYPE"])

    def test_inner_row_outside_specialty_section(self):
        src = simple(H1, row(inner_col(text("<p>x</p>")), None, "divi/row-inner"))
        self.assertEqual(codes(src), ["E5_INNER_ROW_PLACEMENT"])


class Columns5Test(unittest.TestCase):
    def test_structure_matches(self):
        src = page(section(row(column(H1, "1_3") + column("", "2_3"), "1_3,2_3")))
        self.assertEqual(codes(src), [])

    def test_mismatch_sum_and_bad_type(self):
        mismatch = page(section(row(column(H1, "1_3") + column("", "2_3"), "2_3,1_3")))
        self.assertEqual(codes(mismatch), ["E5_COLUMNS"])
        short = page(section(row(column(H1, "1_3") + column("", "1_3"))))
        self.assertEqual(codes(short), ["E5_COLUMNS"])
        bad = page(section(row(column(H1, "7_8"))))
        f = [f for f in validate_source(bad) if f.level == "error"]
        self.assertEqual([(x.code, x.tag, x.value) for x in f], [("E5_COLUMNS", "divi/column", "7_8")])


    def test_untyped_columns_warn(self):
        bare = '<!-- wp:divi/column -->{}<!-- /wp:divi/column -->'
        src = page(section(row(bare.format(H1) + bare.format("") + bare.format(""), "1_2,1_2")))
        self.assertEqual(codes(src), [])  # no error: the widths can't be checked
        f = [x for x in validate_source(src) if x.code == "W5_UNTYPED_COLUMN"]
        self.assertEqual([(x.level, x.tag) for x in f], [("warning", "divi/column")] * 3)
        self.assertIn("columnStructure 1_2,1_2 lists 2 column(s), the row has 3", f[0].message)
        one = page(section(row(bare.format(H1))))
        f = [x for x in validate_source(one) if x.code == "W5_UNTYPED_COLUMN"]
        self.assertEqual(len(f), 1)
        self.assertNotIn("columnStructure", f[0].message)
        typed = page(section(row(column(H1, "1_2") + column("", "1_2"), "1_2,1_2")))
        self.assertNotIn("W5_UNTYPED_COLUMN", [x.code for x in validate_source(typed)])


class Headings5Test(unittest.TestCase):
    def heading_findings(self, src, **kw):
        return [(f.code, f.tag, f.value) for f in validate_source(src, **kw) if f.code in HEADING_CODES]

    def test_heading_default_level_is_h1(self):
        self.assertEqual(self.heading_findings(simple(heading("Main"), heading("Sub", "h2"))), [])

    def test_empty_heading_does_not_count(self):
        self.assertEqual(self.heading_findings(simple(heading(""), heading("Sub", "h2"))),
                         [("W_NO_H1", "", "")])

    def test_content_h1_is_another_h1(self):
        found = self.heading_findings(simple(H1, text("<h1>Again</h1>")))
        self.assertEqual(found, [("E5_MULTIPLE_H1", "divi/text", "h1")])

    def test_no_h1_and_fragment(self):
        src = simple(heading("Sub", "h2"))
        self.assertEqual([c for c, *_ in self.heading_findings(src)], ["W_NO_H1"])
        self.assertEqual(self.heading_findings(src, fragment=True), [])

    def test_skip_uses_schema_default(self):
        # divi/blurb title defaults to h4 in schema5
        found = self.heading_findings(simple(H1, blurb("B")))
        self.assertEqual(found, [("W_HEADING_SKIP", "divi/blurb", "h1>h4")])
        self.assertEqual(self.heading_findings(simple(H1, heading("S", "h2"), heading("T", "h3"), blurb("B"))), [])

    def test_container_level_is_inherited_by_children(self):
        acc = ('<!-- wp:divi/accordion {"title":{"decoration":{"font":{"font":{"desktop":{"value":'
               '{"headingLevel":"h2"}}}}}}} --><!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":'
               '{"value":"Q"}}}} /--><!-- /wp:divi/accordion -->')
        self.assertEqual(self.heading_findings(simple(H1, acc)), [])
        # without the container override, the accordion default (h5) applies: h1 -> h5 skips
        self.assertEqual([c for c, *_ in self.heading_findings(simple(H1, acc.replace('"h2"', '""')))],
                         ["W_HEADING_SKIP"])


class HeadingParity5Test(unittest.TestCase):
    def test_converted_fixtures_match_their_divi4_sources(self):
        """Each converted/*.html page has the same heading findings as the Divi 4 shortcode it came from."""
        from _paths import FIXTURES
        same = {"E_MULTIPLE_H1": "E5_MULTIPLE_H1"}
        checked = 0
        for p in sorted((FIXTURES5 / "converted").glob("*.html")):
            src4 = [c for c in FIXTURES.rglob(p.stem + ".txt") if "divi5" not in c.parts]
            if not src4:
                continue
            checked += 1
            d4 = [(same.get(f.code, f.code), f.value) for f in validate_source(src4[0].read_text())
                  if f.code in {"E_MULTIPLE_H1", "W_NO_H1", "W_HEADING_SKIP"}]
            d5 = [(f.code, f.value) for f in validate_source(p.read_text()) if f.code in HEADING_CODES]
            self.assertEqual(d5, d4, p.name)
        self.assertGreaterEqual(checked, 30)


class Cli5Test(unittest.TestCase):
    def test_cli_on_block_page(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main([str(FIXTURES5 / "invalid" / "two-h1.html"), "--json"])
        self.assertEqual(rc, 1)
        out = json.loads(buf.getvalue())
        self.assertEqual([f["code"] for f in out["findings"]], ["E5_MULTIPLE_H1"])

    def test_baseline_marks_preexisting(self):
        src = (FIXTURES5 / "invalid" / "two-h1.html").read_text()
        found = validate_source(src, baseline=src)
        self.assertTrue(found and all(f.preexisting for f in found))


if __name__ == "__main__":
    unittest.main()
