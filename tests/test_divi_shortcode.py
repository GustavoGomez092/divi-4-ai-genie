import time
import unittest

from _paths import FIXTURES
from divi_shortcode import (Node, Text, escape_attr_value, new_node, parse, parse_attrs,
                            replace_span, serialize, unescape_attr_value, wp_blanks_value)

SIMPLE = ('[et_pb_section admin_label="Hero"][et_pb_row column_structure="1_2,1_2"]'
          '[et_pb_column type="1_2"][et_pb_text text_font_size="18px"]<p>Hi</p>[/et_pb_text][/et_pb_column]'
          '[et_pb_column type="1_2"][et_pb_image src="https://x.test/a.jpg"][/et_pb_image][/et_pb_column]'
          '[/et_pb_row][/et_pb_section]')


class ParseTest(unittest.TestCase):
    def test_roundtrip_captured_pages(self):
        for path in sorted((FIXTURES / "valid").glob("*.txt")):
            src = path.read_text()
            doc = parse(src)
            self.assertEqual(doc.problems, [], path.name)
            self.assertEqual(serialize(doc), src, path.name)

    def test_tree_shape(self):
        doc = parse(SIMPLE)
        (section,) = doc.sections()
        row = section.modules[0]
        self.assertEqual(row.attrs["column_structure"], "1_2,1_2")
        text = row.modules[0].modules[0]
        self.assertEqual(text.tag, "et_pb_text")
        self.assertEqual(text.content, "<p>Hi</p>")
        self.assertEqual([p for _, p, _ in doc.walk()][-1],
                         "et_pb_section[0] > et_pb_row[0] > et_pb_column[1] > et_pb_image[0]")

    def test_walk_yields_parent(self):
        doc = parse(SIMPLE)
        parents = {p: (par.tag if par else None) for _, p, par in doc.walk()}
        self.assertIsNone(parents["et_pb_section[0]"])
        self.assertEqual(parents["et_pb_section[0] > et_pb_row[0]"], "et_pb_section")

    def test_find(self):
        doc = parse(SIMPLE)
        node = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]")
        self.assertEqual(node.tag, "et_pb_text")
        self.assertIsNone(doc.find("et_pb_section[3]"))

    def test_attr_grammar(self):
        attrs, quoting, dups, positional = parse_attrs(' a="1" b=\'2\' c=3 D="4" a="5" loose')
        self.assertEqual(attrs, {"a": "5", "b": "2", "c": "3", "d": "4"})
        self.assertEqual(quoting, {"a": '"', "b": "'", "c": "", "d": '"'})
        self.assertEqual(dups, ["a"])
        self.assertEqual(positional, ["loose"])

    def test_self_closing_without_closer(self):
        doc = parse('[et_pb_column type="4_4"][et_pb_divider][et_pb_text]<p>x</p>[/et_pb_text][/et_pb_column]')
        col = doc.nodes[0]
        self.assertEqual([m.tag for m in col.modules], ["et_pb_divider", "et_pb_text"])
        self.assertTrue(col.modules[0].self_closing)

    def test_unclosed_and_stray(self):
        doc = parse('[et_pb_section][et_pb_row][/et_pb_section][/et_pb_row]')
        codes = [p.code for p in doc.problems]
        self.assertIn("E_UNCLOSED", codes)
        self.assertIn("E_STRAY_CLOSE", codes)

    def test_third_party_shortcode_is_text(self):
        src = '[et_pb_text]<p>[contact-form-7 id="5" title="Form"]</p>[/et_pb_text]'
        doc = parse(src)
        self.assertEqual(len(doc.nodes), 1)
        self.assertEqual(doc.nodes[0].content, '<p>[contact-form-7 id="5" title="Form"]</p>')
        self.assertEqual(serialize(doc), src)

    def test_crlf_roundtrip_and_line_col(self):
        src = SIMPLE.replace("][", "]\r\n[")
        doc = parse(src)
        self.assertEqual(serialize(doc), src)
        text = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]")
        self.assertEqual(doc.line_col(text.start), (4, 1))

    def test_unicode_roundtrip_and_escape(self):
        title = 'Odontología en Miami — “sonrisa” "real" [VIP] & más 😀'
        esc = escape_attr_value(title)
        self.assertEqual(esc, 'Odontología en Miami — “sonrisa” %22real%22 %91VIP%93 & más 😀')
        self.assertEqual(unescape_attr_value(esc), title)
        src = f'[et_pb_heading title="{esc}"][/et_pb_heading]'
        doc = parse(src)
        self.assertEqual(serialize(doc), src)
        self.assertEqual(doc.nodes[0].value("title"), title)

    def test_backslash_escaped_only_for_css_and_json_attrs(self):
        self.assertEqual(escape_attr_value("a\\b", "custom_css_main_element"), "a%92b")
        self.assertEqual(escape_attr_value("a\\b", "select_options"), "a%92b")
        self.assertEqual(escape_attr_value("a\\b", "title"), "a\\b")

    def test_edit_attr_rebuilds_only_that_tag(self):
        doc = parse(SIMPLE)
        text = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]")
        text.attrs["text_font_size"] = "20px"
        out = serialize(doc)
        self.assertEqual(out, SIMPLE.replace('text_font_size="18px"', 'text_font_size="20px"'))

    def test_new_node_escapes_and_closes(self):
        node = new_node("et_pb_heading", {"title": 'Say "hi"'})
        self.assertEqual(serialize([node]), '[et_pb_heading title="Say %22hi%22"][/et_pb_heading]')
        text = new_node("et_pb_text", {}, content="<p>x</p>")
        self.assertEqual(serialize([text]), "[et_pb_text]<p>x</p>[/et_pb_text]")

    def test_replace_span(self):
        doc = parse(SIMPLE)
        img = doc.find("et_pb_section[0] > et_pb_row[0] > et_pb_column[1] > et_pb_image[0]")
        out = replace_span(SIMPLE, img.start, img.end, "[et_pb_divider][/et_pb_divider]")
        self.assertIn("[et_pb_divider][/et_pb_divider][/et_pb_column]", out)
        with self.assertRaises(ValueError):
            replace_span(SIMPLE, 10, 5, "")

    def test_wp_blanks_value(self):
        self.assertFalse(wp_blanks_value("plain"))
        self.assertFalse(wp_blanks_value("<b>bold</b> text"))
        self.assertTrue(wp_blanks_value("a < b"))

    def test_large_input_is_fast(self):
        big = (FIXTURES / "valid" / "divi-ai-layout.txt").read_text() * 2
        t0 = time.time()
        self.assertEqual(serialize(parse(big)), big)
        self.assertLess(time.time() - t0, 2.0)


if __name__ == "__main__":
    unittest.main()
