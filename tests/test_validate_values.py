import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from validate import validate_source

SCHEMA = load_schema()


def wrap(module):
    return f'[et_pb_section][et_pb_row][et_pb_column type="4_4"]{module}[/et_pb_column][/et_pb_row][/et_pb_section]'


def found(module, level=None):
    # one module wrapped in a section: a fragment, so the page-level W_NO_H1 stays out of these tests
    return [(f.level, f.code, f.attr) for f in validate_source(wrap(module), SCHEMA, fragment=True)
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

    def test_email_provider_list_accepts_site_specific_account_list_pairs(self):
        # The schema can only list '0|none' and the manage actions: the real values are
        # '<account>|<list id>' pairs from the live site's connected provider accounts.
        self.assertEqual(found('[et_pb_signup mailchimp_list="Studio|a1b2c3d4"][/et_pb_signup]', "error"), [])
        self.assertEqual(found('[et_pb_signup aweber_list="0|none"][/et_pb_signup]', "error"), [])
        self.assertIn(("error", "E_BAD_OPTION", "mailchimp_list"), found('[et_pb_signup mailchimp_list="a1b2c3d4"][/et_pb_signup]'))
        self.assertIn(("error", "E_BAD_OPTION", "mailchimp_list"), found('[et_pb_signup mailchimp_list="manage|oops"][/et_pb_signup]'))
        self.assertEqual(found('[et_pb_signup convertkit_list="Main|98765"][/et_pb_signup]', "error"), [])

    def test_spam_provider_list_is_not_an_email_list(self):
        # recaptcha_list (Signup and Contact Form spam protection) only holds '0|none' or a manage
        # action; the account|list exemption is for email provider lists only.
        for tag in ("et_pb_signup", "et_pb_contact_form"):
            with self.subTest(tag=tag):
                self.assertIn(("error", "E_BAD_OPTION", "recaptcha_list"),
                              found(f'[{tag} recaptcha_list="totally|bogus"][/{tag}]'))
                self.assertEqual(found(f'[{tag} recaptcha_list="0|none"][/{tag}]', "error"), [])

    def test_units(self):
        self.assertEqual(found('[et_pb_heading title_font_size="48px"][/et_pb_heading]', "error"), [])
        self.assertIn(("error", "E_BAD_UNIT", "title_font_size"), found('[et_pb_heading title_font_size="48parsecs"][/et_pb_heading]'))
        self.assertEqual(found('[et_pb_blurb max_width="none" min_height="auto"][/et_pb_blurb]', "error"), [])

    def test_colors(self):
        for ok in ("#fff", "#0E7C86", "rgba(0,0,0,0.5)", "RGBA(255,255,255,0)", "transparent", "gcid-36fd78a7"):
            self.assertEqual(found(f'[et_pb_blurb icon_color="{ok}"][/et_pb_blurb]', "error"), [], ok)
        self.assertIn(("error", "E_VALUE_FORMAT", "icon_color"), found('[et_pb_blurb icon_color="blue-ish"][/et_pb_blurb]'))

    def test_background_field_color_format(self):
        self.assertEqual(found('[et_pb_button button_bg_color="#f97316"][/et_pb_button]', "error"), [])
        self.assertIn(("error", "E_VALUE_FORMAT", "button_bg_color"), found('[et_pb_button button_bg_color="not-a-color"][/et_pb_button]'))

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

    def external_images(self, module):
        return [f.attr for f in validate_source(wrap(module), SCHEMA, site_url="https://client.example")
                if f.code == "W_EXTERNAL_IMAGE"]

    def test_external_image_is_module_aware_video_src_is_not_an_image(self):
        self.assertEqual(self.external_images('[et_pb_video src="https://www.youtube.com/watch?v=dQw4w9WgXcQ"][/et_pb_video]'), [])
        self.assertEqual(self.external_images(
            '[et_pb_video_slider][et_pb_video_slider_item src="https://vimeo.com/1"][/et_pb_video_slider_item][/et_pb_video_slider]'), [])
        self.assertEqual(self.external_images('[et_pb_audio audio="https://cdn.example/a.mp3"][/et_pb_audio]'), [])

    def test_external_image_still_warns_on_image_fields(self):
        self.assertEqual(self.external_images('[et_pb_image src="https://images.unsplash.com/x.jpg"][/et_pb_image]'), ["src"])
        # the video's poster image IS an image field
        self.assertEqual(self.external_images(
            '[et_pb_video src="https://www.youtube.com/watch?v=1" image_src="https://img.example/p.jpg"][/et_pb_video]'),
            ["image_src"])
        self.assertEqual(self.external_images('[et_pb_blurb image="https://img.example/b.png"][/et_pb_blurb]'), ["image"])
        self.assertEqual(self.external_images(
            '[et_pb_text background_image="https://img.example/bg.jpg"]<p>x</p>[/et_pb_text]'), ["background_image"])
        self.assertEqual(self.external_images(
            '[et_pb_image src="https://client.example/wp-content/uploads/x.jpg"][/et_pb_image]'), [])

    def test_image_field_detection_uses_the_schema_data_type(self):
        from divi_checks_values import is_image_field
        video = SCHEMA.module("et_pb_video")
        self.assertFalse(is_image_field(video.resolve("src")))
        self.assertTrue(is_image_field(video.resolve("image_src")))
        self.assertTrue(is_image_field(SCHEMA.module("et_pb_image").resolve("src_tablet")))
        self.assertFalse(is_image_field(SCHEMA.module("et_pb_section").resolve("background_video_mp4")))

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
