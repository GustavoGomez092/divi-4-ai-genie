import unittest

from _paths import FIXTURES
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
        # et_pb_blurb has no "title_color"-like attribute at all (Divi calls it
        # header_text_color), so that typo has no close real match; use a typo of
        # a real attribute (icon_color) that difflib's 0.75 cutoff actually catches.
        fs = [f for f in validate_source(wrap('[et_pb_blurb icon_colour="#fff"][/et_pb_blurb]'), SCHEMA)
              if f.code == "E_UNKNOWN_ATTR"]
        self.assertEqual(len(fs), 1)
        self.assertIn("did you mean", fs[0].hint)

    def test_illegal_suffix(self):
        fs = found('[et_pb_blurb use_icon__hover="on"][/et_pb_blurb]')
        self.assertIn(("error", "E_UNKNOWN_ATTR", "use_icon__hover"), fs)
        self.assertNotIn(("warning", "W_HOVER_DISABLED", "use_icon__hover"), fs)

    def test_raw_bracket_and_positional(self):
        fs = found('[et_pb_heading title="Save [now]" stray][/et_pb_heading]')
        self.assertIn(("error", "E_RAW_BRACKET", "title"), fs)
        self.assertIn(("error", "E_POSITIONAL_ATTR", ""), fs)

    def test_wp_blanks_lt(self):
        self.assertIn(("error", "E_ATTR_LT", "title"), found('[et_pb_heading title="a < b"][/et_pb_heading]'))

    def test_single_quoted_value_warns(self):
        self.assertIn(("warning", "W_ATTR_QUOTING", "title"), found("[et_pb_heading title='x'][/et_pb_heading]"))

    def test_raw_quote(self):
        self.assertIn(("error", "E_RAW_QUOTE", "title"),
                      found('[et_pb_heading title=\'He said "hi"\'][/et_pb_heading]'))

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

    def test_border_radius_units(self):
        self.assertIn(("error", "E_VALUE_FORMAT", "border_radii"),
                      found('[et_pb_blurb border_radii="on|10deg|10deg|10deg|10deg"][/et_pb_blurb]'))
        self.assertEqual(found('[et_pb_blurb border_radii="on|10px|10px|10px|10px"][/et_pb_blurb]', "error"), [])

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

    def test_divi_ai_fixtures_only_have_known_stale_errors(self):
        from _paths import FIXTURES
        from test_divi_schema import KNOWN_STALE
        for path in (FIXTURES / "valid").glob("divi-ai-*.txt"):
            errors = [f for f in validate_source(path.read_text(), SCHEMA) if f.level == "error"]
            self.assertTrue(all(f.code == "E_UNKNOWN_ATTR" for f in errors), [(f.code, f.attr) for f in errors])
            self.assertTrue({(f.tag, f.attr) for f in errors} <= KNOWN_STALE)


if __name__ == "__main__":
    unittest.main()
