import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from validate import validate_source

SCHEMA = load_schema()
V = '_builder_version="4.27.9"'


def codes(src, level="error"):
    # snippets, not whole pages: fragment=True keeps the page-level W_NO_H1 out of these structure tests
    return [f.code for f in validate_source(src, SCHEMA, fragment=True) if f.level == level]


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

    def test_fullwidth_child_path_is_the_childs_own_path(self):
        src = '[et_pb_section fullwidth="on"][et_pb_text]<p>x</p>[/et_pb_text][/et_pb_section]'
        (f,) = [f for f in validate_source(src, SCHEMA) if f.code == "E_FULLWIDTH_CHILD"]
        self.assertEqual(f.path, "et_pb_section[0] > et_pb_text[0]")

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
        errors = codes(src)
        self.assertIn("E_COLUMN_TYPE", errors)
        self.assertNotIn("E_COLUMN_SUM", errors)

    def test_child_outside_parent(self):
        self.assertIn("E_CHILD_PLACEMENT", codes(page('[et_pb_tab title="x"]<p>x</p>[/et_pb_tab]')))

    def test_parent_with_wrong_child(self):
        errors = codes(page('[et_pb_tabs][et_pb_slide][/et_pb_slide][/et_pb_tabs]'))
        self.assertIn("E_BAD_CHILD", errors)
        self.assertEqual(errors, ["E_BAD_CHILD"])

    def test_top_level_child_module_is_not_also_child_placement(self):
        errors = codes('[et_pb_tab title="x"]<p>x</p>[/et_pb_tab]')
        self.assertIn("E_TOP_LEVEL", errors)
        self.assertNotIn("E_CHILD_PLACEMENT", errors)

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
