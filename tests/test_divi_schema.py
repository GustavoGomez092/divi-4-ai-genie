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
