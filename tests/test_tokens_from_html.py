import json
import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from extract_tokens import build_tokens
from tokens_from_html import tokens_from_html

HTML = (FIXTURES / "html" / "customized-page.html").read_text()


class TokensFromHtmlTest(unittest.TestCase):
    def test_customizer_values(self):
        c = tokens_from_html(HTML)["customizer"]
        self.assertEqual(c.get("accent"), "#ff00aa")
        self.assertEqual(c.get("body_text"), "#333344")
        self.assertEqual(c.get("heading"), "#112233")
        self.assertEqual(c.get("link"), "#0055ff")

    def test_customizer_fonts_size_and_width(self):
        c = tokens_from_html(HTML)["customizer"]
        self.assertEqual(c.get("body_font"), "Lato")
        self.assertEqual(c.get("heading_font"), "Montserrat")
        self.assertEqual(c.get("body_size"), "17px")
        self.assertEqual(c.get("content_width"), "1200px")

    def test_fonts_and_version(self):
        t = tokens_from_html(HTML)
        self.assertIn("Montserrat", t["fonts"])
        self.assertIn("Lato", t["fonts"])
        self.assertEqual(t["divi_version"], "4.27.9")

    def test_global_colors(self):
        # research/tools/notes/customizer-css.md ("Global colors (gcid-*)"): Divi 4.27.9 does not
        # emit a `--gcid-*` CSS custom property, and emits nothing at all for a global color that
        # isn't referenced by any module on the rendered page (this fixture's page never assigns
        # gcid-planprobe to a module attribute). When used, a global color is resolved to a plain
        # hex value before CSS is generated, indistinguishable from a hardcoded color -- so public
        # HTML alone can never recover a gcid->hex mapping. The original brief assertion
        # (global_colors["gcid-planprobe"] == "#123456") is dropped per that finding; this asserts
        # the parser doesn't fabricate an entry that isn't actually there.
        self.assertEqual(tokens_from_html(HTML)["global_colors"], {})

    def test_build_tokens_merges_sources(self):
        raw = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()
        t = build_tokens([{"id": 1, "url": "https://client.example/p/", "raw": raw}],
                         {"https://client.example/p/": HTML}, "https://client.example", load_schema())
        self.assertEqual(t["site"]["url"], "https://client.example")
        self.assertEqual(t["site"]["divi_version"], "4.27.9")
        self.assertEqual(t["colors"]["customizer"]["accent"], "#ff00aa")
        self.assertIn("et_pb_button", t["module_styles"])
        json.dumps(t)  # must be JSON-serializable


if __name__ == "__main__":
    unittest.main()
