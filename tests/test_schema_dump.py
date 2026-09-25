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
