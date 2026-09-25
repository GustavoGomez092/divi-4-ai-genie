import json
import tempfile
import unittest
from pathlib import Path

from _paths import RAW_SCHEMA
from divi_schema import load_schema
from generate_docs import _field_row, classify, main, minimal_example
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

    def test_conditional_default_renders_readably(self):
        # body_link_text_shadow_blur_strength's raw "default" is
        # ["body_link_text_shadow_style", {"none": "0em", "preset1": "0.1em", ...}] -- a default that
        # depends on another field's value, not a literal default. Dumping the raw Python repr into the
        # table (e.g. "['body_link_text_shadow_style', {'none': '0em', ...}]") reads as broken data.
        f = RAW["et_pb_blurb"]["fields"]["body_link_text_shadow_blur_strength"]
        row = _field_row("body_link_text_shadow_blur_strength", f)
        self.assertNotIn("preset1", row)
        self.assertIn("depends on `body_link_text_shadow_style`", row)

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
