import json
import unittest

from _paths import FIXTURES
from divi_checks_values import COLOR_RE
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
        src = SRC.replace(
            'button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default"',
            'button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="aaaa-bbbb"', 1)
        t = tokens_from_documents([parse(src)], SCHEMA)
        self.assertEqual(t["presets"]["et_pb_button"], [{"uuid": "aaaa-bbbb", "uses": 1}])

    def test_duplicate_module_preset_last_wins(self):
        src = '[et_pb_button button_text="Click" button_url="#" _module_preset="x" _module_preset="y"][/et_pb_button]'
        t = tokens_from_documents([parse(src)], SCHEMA)
        self.assertEqual(t["presets"]["et_pb_button"], [{"uuid": "y", "uses": 1}])

    def test_state_toggle_and_last_edited_are_not_colors(self):
        # button_bg_color is used nowhere else in SRC, so any leaked non-hex "color" would be
        # obvious; also assert the __hover_enabled / _last_edited style-carrier values never
        # land in the palette even though they resolve through a color field.
        hexes = {p["hex"] for p in self.t["colors"]["palette"]}
        self.assertNotIn("on|hover", hexes)
        self.assertNotIn("on|phone", hexes)
        for h in hexes:
            self.assertTrue(COLOR_RE.match(h), h)

    def test_background_field_color_captured_in_palette(self):
        src = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
               '[et_pb_button button_text="Buy" button_url="#" button_bg_color="#123abc"][/et_pb_button]'
               '[/et_pb_column][/et_pb_row][/et_pb_section]')
        t = tokens_from_documents([parse(src)], SCHEMA)
        hexes = {p["hex"]: p for p in t["colors"]["palette"]}
        self.assertIn("#123abc", hexes)
        self.assertIn("button_bg_color", hexes["#123abc"]["roles"])

    def test_media_urls_excluded_from_tokens(self):
        src = ('[et_pb_section background_image="https://x/secret.jpg"][et_pb_row]'
               '[et_pb_column type="4_4"][et_pb_text]<p>hi</p>[/et_pb_text]'
               '[/et_pb_column][/et_pb_row][/et_pb_section]')
        t = tokens_from_documents([parse(src)], SCHEMA)
        self.assertNotIn("secret.jpg", json.dumps(t))
        self.assertEqual(t["section_exemplars"][0]["media"], ["background_image"])

    def test_palette_hexes_are_valid_on_real_layout(self):
        doc = parse((FIXTURES / "valid" / "divi-ai-layout.txt").read_text())
        t = tokens_from_documents([doc], SCHEMA)
        for p in t["colors"]["palette"]:
            self.assertTrue(COLOR_RE.match(p["hex"]), p["hex"])


if __name__ == "__main__":
    unittest.main()
