import unittest

from _paths import FIXTURES, d5_fixtures, d5_invalid_fixtures
from divi_format import detect_content, detect_site, major_from_version, parse_style_css_version


class DetectContentTest(unittest.TestCase):
    def test_shortcode_fixtures(self):
        for p in sorted((FIXTURES / "valid").glob("*.txt")):
            self.assertEqual(detect_content(p.read_text()), "shortcode", p.name)

    def test_block_fixtures(self):
        files = d5_fixtures()
        self.assertGreaterEqual(len(files), 37)
        for p in files:
            self.assertEqual(detect_content(p.read_text()), "blocks", p.name)

    def test_mixed_and_empty(self):
        self.assertEqual(detect_content('<!-- wp:divi/text {} /-->[et_pb_section][/et_pb_section]'), "mixed")
        self.assertEqual(detect_content("   \n"), "empty")
        self.assertEqual(detect_content("<p>plain</p>"), "empty")

    def test_d4_shortcode_inside_d5_text_is_still_blocks(self):
        # Shortcode text *inside* a block's JSON is content, not D4 structure.
        src = '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"[et_pb_x]"}}}} /-->'
        self.assertEqual(detect_content(src), "blocks")


class FixtureListTest(unittest.TestCase):
    def test_invalid_fixtures_excluded_from_d5_fixtures(self):
        valid = {p for p in d5_fixtures()}
        self.assertFalse([p for p in valid if "invalid" in p.parts])
        self.assertFalse(valid & set(d5_invalid_fixtures()))


class VersionTest(unittest.TestCase):
    def test_major(self):
        self.assertEqual(major_from_version("5.13.1"), 5)
        self.assertEqual(major_from_version("4.27.9"), 4)
        self.assertIsNone(major_from_version(""))
        self.assertIsNone(major_from_version("abc"))

    def test_style_css(self):
        css = "/*\nTheme Name: Divi\nVersion: 5.13.1\nAuthor: Elegant Themes\n*/"
        self.assertEqual(parse_style_css_version(css), "5.13.1")
        self.assertIsNone(parse_style_css_version("body{}"))

    def test_detect_site_style_css(self):
        pages = {"https://x.test/wp-content/themes/Divi/style.css": b"/*\nVersion: 5.2.0\n*/"}
        got = detect_site("https://x.test/", fetch=lambda u: pages[u])
        self.assertEqual((got["divi_version"], got["divi_major"]), ("5.2.0", 5))

    def test_detect_site_falls_back_to_assets(self):
        home = (b'<link href="https://x.test/wp-content/themes/Divi/includes/builder-5/visual-builder/'
                b'build/a.css?ver=5.1.0">')
        def fetch(u):
            if u.endswith("style.css"):
                raise OSError("404")
            return home
        got = detect_site("https://x.test", fetch=fetch)
        self.assertEqual(got["divi_major"], 5)
        self.assertEqual(got["divi_version"], "5.1.0")

    def _home_only(self, html):
        def fetch(u):
            if u.endswith("style.css"):
                raise OSError("404")
            return html
        return detect_site("https://x.test", fetch=fetch)

    def test_detect_site_d5_html_markers_without_version(self):
        for html in (b'<style class="et-vb-global-data x"></style>',
                     b'<div class="et_block_section">',
                     b"<script>var diviBreakpointData = {};</script>",
                     b"<script id='divi-script-library-foo'></script>"):
            with self.subTest(html=html):
                got = self._home_only(html)
                self.assertEqual((got["divi_version"], got["divi_major"]), (None, 5))

    def test_detect_site_generator_meta(self):
        got = self._home_only(b'<meta content="Divi v.4.27.4" name="generator" />')
        self.assertEqual((got["divi_version"], got["divi_major"]), ("4.27.4", 4))
        got = self._home_only(b'<meta content="Divi Child v.1.0" name="generator" />')
        self.assertEqual((got["divi_version"], got["divi_major"]), (None, None))
