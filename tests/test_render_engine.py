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


class ContactFieldMarkupTest(unittest.TestCase):
    """Task 27 fix round: ContactFormItem::render() input markup (ids, names, required markers,
    option labels). Expected strings are what real Divi printed on Playground for
    forms-tuned-contact-form.txt (whitespace between tags collapsed)."""

    def field(self, shortcode: str):
        from divi_render.modules.forms import ContactField
        node = next(n for n in parse(shortcode).nodes if isinstance(n, Node))
        return ContactField(node, Ctx(StubTheme({})))

    def html(self, shortcode: str, fid: str, num: int = 0, count: int = 0) -> str:
        import re
        f = self.field(shortcode)
        out = f.input_html(f.props.get("field_type"), fid, f.props.get("field_title"), num, count)
        return re.sub(r">\s+<", "><", out)

    def test_text_input(self):
        self.assertEqual(
            self.html('[et_pb_contact_field field_id="Name" field_title="Full name" allowed_symbols="letters" '
                      'min_length="2" max_length="40"][/et_pb_contact_field]', "name"),
            '<input type="text" id="et_pb_contact_name_0" class="input" value="" name="et_pb_contact_name_0" '
            'data-required_mark="required" data-field_type="input" data-original_id="name" placeholder="Full name" '
            'pattern="[A-Za-z\\s\\-]{2,40}" title="Only letters allowed.Minimum length: 2 characters. Maximum length: '
            '40 characters." maxlength="40">')

    def test_textarea_not_required(self):
        self.assertEqual(
            self.html('[et_pb_contact_field field_id="Message" field_title="Tell us about the project" field_type="text" '
                      'required_mark="off"][/et_pb_contact_field]', "message"),
            '<textarea name="et_pb_contact_message_0" id="et_pb_contact_message_0" class="et_pb_contact_message input" '
            'data-required_mark="not_required" data-field_type="text" data-original_id="message" '
            'placeholder="Tell us about the project"></textarea>')

    def test_checkbox_group(self):
        self.assertEqual(
            self.html('[et_pb_contact_field field_id="Contact" field_title="Contact me by" field_type="checkbox" '
                      'checkbox_options="%91{%22value%22:%22Email%22,%22checked%22:1,%22dragID%22:0},'
                      '{%22value%22:%22Phone%22,%22checked%22:0,%22dragID%22:1}%93"][/et_pb_contact_field]',
                      "contact", count=3),
            '<input class="et_pb_checkbox_handle" type="hidden" name="et_pb_contact_contact_0" data-required_mark="required" '
            'data-field_type="checkbox" data-original_id="contact"><span class="et_pb_contact_field_options_wrapper">'
            '<span class="et_pb_contact_field_options_title">Contact me by</span><span class="et_pb_contact_field_options_list">'
            '<span class="et_pb_contact_field_checkbox"><input type="checkbox" id="et_pb_contact_contact_3_0" class="input" '
            'value="Email" checked="checked" data-id="0"><label for="et_pb_contact_contact_3_0"><i></i>Email</label></span>'
            '<span class="et_pb_contact_field_checkbox"><input type="checkbox" id="et_pb_contact_contact_3_1" class="input" '
            'value="Phone" data-id="1"><label for="et_pb_contact_contact_3_1"><i></i>Phone</label></span></span></span>')

    def test_select(self):
        self.assertEqual(
            self.html('[et_pb_contact_field field_id="Service" field_title="Service" field_type="select" '
                      'select_options="%91{%22value%22:%22Design%22,%22checked%22:0,%22dragID%22:0},'
                      '{%22value%22:%22Build%22,%22checked%22:0,%22dragID%22:1}%93"][/et_pb_contact_field]', "service"),
            '<select id="et_pb_contact_service_0" class="et_pb_contact_select input" name="et_pb_contact_service_0" '
            'data-required_mark="required" data-field_type="select" data-original_id="service"><option value="">Service'
            '</option><option value="Design">Design</option><option value="Build">Build</option></select>')

    def test_option_text_is_stripped_of_tags(self):
        # wp_strip_all_tags() on every option value and label (ContactFormItem.php render())
        opts = ('%91{%22value%22:%22<b>Email</b> me <script>x()</script>%22,%22checked%22:0,%22dragID%22:0}%93')
        for ftype in ("checkbox", "radio", "select"):
            with self.subTest(ftype=ftype):
                out = self.html(f'[et_pb_contact_field field_id="Pick" field_title="Pick" field_type="{ftype}" '
                                f'{ftype}_options="{opts}"][/et_pb_contact_field]', "pick")
                self.assertIn('value="Email me"', out)
                self.assertIn("Email me</", out)
                self.assertNotIn("<b>", out)
                self.assertNotIn("script", out)
