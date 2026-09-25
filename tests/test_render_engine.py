"""Unit tests of the Python renderer's design-option engine that don't need real Divi (Task 25)."""
import unittest

from _paths import FIXTURES  # noqa: F401  (puts scripts on sys.path)

from divi_render.base import GLOBAL_SETTINGS_SLUG, Ctx, Module
from divi_shortcode import Node, parse


class StubTheme:
    """Only what Module.__init__ needs: ET_Global_Settings values."""

    def __init__(self, settings: dict):
        self.settings = settings

    def global_settings(self) -> dict:
        return self.settings


def module_for(shortcode: str, settings: dict) -> Module:
    node = next(n for n in parse(shortcode).nodes if isinstance(n, Node))
    return Module(node, Ctx(StubTheme(settings)))


class GlobalDefaultsTest(unittest.TestCase):
    def test_own_slug_namespace_clears_a_prop_equal_to_its_global_default(self):
        m = module_for('[et_pb_gallery hover_overlay_color="rgba(255,255,255,0.9)"][/et_pb_gallery]',
                       {"et_pb_gallery-hover_overlay_color": "rgba(255,255,255,0.9)"})
        self.assertEqual(dict.get(m.props, "hover_overlay_color"), "")

    def test_a_different_value_is_kept(self):
        m = module_for('[et_pb_gallery hover_overlay_color="#000000"][/et_pb_gallery]',
                       {"et_pb_gallery-hover_overlay_color": "rgba(255,255,255,0.9)"})
        self.assertEqual(dict.get(m.props, "hover_overlay_color"), "#000000")

    def test_global_settings_slug_override_resolves_to_the_parent_namespace(self):
        # PostSlider.php: $this->global_settings_slug = 'et_pb_slider'
        self.assertEqual(GLOBAL_SETTINGS_SLUG["et_pb_post_slider"], "et_pb_slider")
        settings = {"et_pb_slider-header_font_size": "46", "et_pb_post_slider-header_font_size": "99"}
        m = module_for('[et_pb_post_slider header_font_size="46"][/et_pb_post_slider]', settings)
        self.assertEqual(dict.get(m.props, "header_font_size"), "")
        m = module_for('[et_pb_post_slider header_font_size="99"][/et_pb_post_slider]', settings)
        self.assertEqual(dict.get(m.props, "header_font_size"), "99")

    def test_every_divi_override_is_mapped(self):
        # FullwidthPortfolio.php:12, FullwidthPostSlider.php:17, PostSlider.php:23 (Divi 4.27.9)
        self.assertEqual(GLOBAL_SETTINGS_SLUG, {"et_pb_fullwidth_portfolio": "et_pb_portfolio",
                                                "et_pb_fullwidth_post_slider": "et_pb_fullwidth_slider",
                                                "et_pb_post_slider": "et_pb_slider"})

    def test_text_orientation_is_always_printed(self):
        m = module_for('[et_pb_text text_orientation="left"][/et_pb_text]', {"et_pb_text-text_orientation": "left"})
        self.assertEqual(dict.get(m.props, "text_orientation"), "left")


if __name__ == "__main__":
    unittest.main()


class DataModuleHelpersTest(unittest.TestCase):
    """Task 26: server-side values of the countdown timer and pricing table items."""

    def test_countdown_end_timestamp_reads_the_date_as_utc(self):
        from divi_render.modules.counters import end_timestamp
        # the value real Divi printed on Playground for date_time="2020-03-31 23:59"
        # (interactive-tuned-countdown.txt); it depends only on the date, never on "now"
        self.assertEqual(end_timestamp("2020-03-31 23:59"), 1585699140)
        self.assertEqual(end_timestamp("2019-12-31 00:00"), 1577750400)
        self.assertEqual(end_timestamp("not a date"), 0)

    def test_pricing_items_mark_minus_and_en_dash_lines_unavailable(self):
        from divi_render.modules.pricing import pricing_items
        self.assertEqual(
            pricing_items("+Design\n-Renderings\n&#8211;Weekends\n\nPermits"),
            '<li><span>Design</span></li><li class="et_pb_not_available"><span>Renderings</span></li>'
            '<li class="et_pb_not_available"><span>Weekends</span></li><li><span>Permits</span></li>')


class FormHelpersTest(unittest.TestCase):
    """Task 27: attribute values of the form modules. The fidelity harness compares tags, classes
    and CSS only, so these pin values real Divi printed on Playground (forms-*.txt fixtures)."""

    def props(self, **attrs):
        from divi_render.values import Props
        return Props(attrs)

    def test_input_pattern_title_and_maxlength(self):
        from divi_render.modules.forms import field_pattern
        self.assertEqual(field_pattern(self.props(allowed_symbols="letters", min_length="2", max_length="40")),
                         (' pattern="[A-Za-z\\s\\-]{2,40}"',
                          ' title="Only letters allowed.Minimum length: 2 characters. Maximum length: 40 characters."',
                          ' maxlength="40"'))
        self.assertEqual(field_pattern(self.props(allowed_symbols="numbers", max_length="5")),
                         (' pattern="[0-9\\s\\-]{0,5}"', ' title="Only numbers allowed.Maximum length: 5 characters."', ""))
        self.assertEqual(field_pattern(self.props(min_length="4")),
                         (' pattern=".{4,}"', ' title="Minimum length: 4 characters. "', ""))
        self.assertEqual(field_pattern(self.props(allowed_symbols="all")), ("", "", ""))

    def test_conditional_logic_rules_become_data_attributes(self):
        from divi_render.modules.forms import conditional_attrs
        rules = '[{"field":"zip","condition":"is not empty","value":""},{"field":"reason","condition":"is","value":"Estimate"}]'
        self.assertEqual(
            conditional_attrs(self.props(conditional_logic="on", conditional_logic_relation="on",
                                         conditional_logic_rules=rules)),
            ' data-conditional-logic="[[&quot;zip&quot;,&quot;is not empty&quot;,&quot;&quot;],[&quot;reason&quot;,'
            '&quot;is&quot;,&quot;Estimate&quot;]]" data-conditional-relation="all"')
        self.assertTrue(conditional_attrs(self.props(conditional_logic="on", conditional_logic_relation="off",
                                                     conditional_logic_rules=rules)).endswith(' data-conditional-relation="any"'))
        self.assertEqual(conditional_attrs(self.props(conditional_logic="off", conditional_logic_rules=rules)), "")

    def test_signup_checksum_is_md5_of_the_php_serialized_attributes(self):
        import hashlib
        from divi_render.modules.forms import php_serialize
        self.assertEqual(php_serialize({"title": "Café", "x": ""}), 'a:2:{s:5:"title";s:5:"Café";s:1:"x";s:0:"";}')
        doc = parse((FIXTURES / "render" / "forms-tuned-signup.txt").read_text())
        signup = next(n for n, _, _ in doc.walk() if n.tag == "et_pb_signup")
        # the value real Divi printed for the first signup of forms-tuned-signup.txt
        self.assertEqual(hashlib.md5(php_serialize(signup.attrs).encode()).hexdigest(), "f3076ae46f36856dee3524c616f93e38")
