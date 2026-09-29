"""Divi 5 tokens from public HTML/CSS (tokens5_from_html.py) and the extract_tokens.py Divi 5 dispatch/merge."""
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from _paths import FIXTURES, FIXTURES5, SCRIPTS, d5_fixtures
from divi5_schema import load_schema5
from extract_tokens import build_tokens5, main
from test_divi5_validate_values import V, block, page, text_attrs
from tokens5_from_html import stylesheet_links, tokens5_from_html
from validate import validate_source

HTML5 = FIXTURES5 / "html"
TRACE_HTML = (HTML5 / "r6-tokens-trace.html").read_text()
TRACE_CONTENT = (HTML5 / "r6-tokens-trace.content.txt").read_text()
PLAIN_HTML = (HTML5 / "r6-plain.html").read_text()
HOME_HTML = (HTML5 / "r6-home.html").read_text()
HOME_CSS = (HTML5 / "r6-home.et-divi-dynamic.css").read_text()
HOME_CSS_URL = "http://divi-5-test.local/wp-content/et-cache/home/et-divi-dynamic.css?ver=1790664715"
AI_LAYOUT = FIXTURES5 / "divi-ai" / "layout.html"
D4_SHORTCODE = FIXTURES / "valid" / "handwritten-landing.txt"
SITE = "http://divi-5-test.local"
TRACE_URL = SITE + "/r6-tokens-trace/"
TOKEN_CODES = {"W5_UNKNOWN_PRESET", "W5_UNKNOWN_VARIABLE", "W_OFF_PALETTE_COLOR", "W_OFF_BRAND_FONT",
               "W_OFF_SCALE_SPACING"}


def trace_tokens():
    return build_tokens5([{"id": 23, "url": TRACE_URL, "raw": TRACE_CONTENT}],
                         {TRACE_URL: tokens5_from_html(TRACE_HTML), SITE + "/": tokens5_from_html(PLAIN_HTML)},
                         SITE, load_schema5())


class CustomizerTest(unittest.TestCase):
    def test_five_customizer_colors_with_ids(self):
        c = tokens5_from_html(TRACE_HTML)["colors"]["customizer"]
        self.assertEqual({k: (v["id"], v["value"]) for k, v in c.items()}, {
            "primary": ("gcid-primary-color", "#7C3AED"), "secondary": ("gcid-secondary-color", "#2ea3f2"),
            "heading": ("gcid-heading-color", "#666666"), "body": ("gcid-body-color", "#666666"),
            "link": ("gcid-link-color", "#2ea3f2")})

    def test_overridden_flags_a_non_default_customizer_color(self):
        c = tokens5_from_html(TRACE_HTML)["colors"]["customizer"]
        self.assertTrue(c["primary"]["overridden"])
        self.assertFalse(c["heading"]["overridden"])

    def test_customizer_fonts_from_et_global(self):
        f = tokens5_from_html(TRACE_HTML)["fonts"]
        self.assertEqual(f["customizer"]["heading_font"],
                         {"id": "--et_global_heading_font", "value": "Open Sans", "weight": "500"})
        self.assertEqual(f["customizer"]["body_font"]["value"], "Open Sans")
        self.assertEqual(f["customizer"]["body_size"], "14px")
        self.assertEqual(f["customizer"]["body_line_height"], "1.7em")
        self.assertIn("Open Sans", f["loaded"])

    def test_loaded_fonts_include_inlined_font_faces(self):
        html = "<style>@font-face{font-family:'Poppins';src:url(x.woff2)}</style>"
        self.assertEqual(tokens5_from_html(html)["fonts"]["loaded"], ["Poppins"])

    def test_icon_fonts_are_not_loaded_brand_fonts(self):
        html = ("<style>@font-face{font-family:ETmodules;src:url(m.woff)}"
                "@font-face{font-family:FontAwesome;src:url(f.woff)}</style>")
        self.assertEqual(tokens5_from_html(html)["fonts"]["loaded"], [])

    def test_divi_version(self):
        self.assertEqual(tokens5_from_html(TRACE_HTML)["site"]["divi_version"], "5.13.1")


class GlobalColorsTest(unittest.TestCase):
    def test_user_global_color_used_on_the_page(self):
        g = tokens5_from_html(TRACE_HTML)["colors"]["global"]
        self.assertEqual(g["gcid-r6navy0001"]["value"], "#0B2A3C")
        self.assertEqual(g["gcid-r6orange001"]["value"], "#F97316")

    def test_customizer_ids_are_not_user_global_colors(self):
        self.assertNotIn("gcid-primary-color", tokens5_from_html(TRACE_HTML)["colors"]["global"])

    def test_derived_color_is_resolved_and_keeps_its_base(self):
        d = tokens5_from_html(TRACE_HTML)["colors"]["global"]["gcid-r6orangelt1"]
        self.assertEqual(d["value"], "#fdcdab")
        self.assertEqual(d["base"], "gcid-r6orange001")
        self.assertTrue(d["raw"].startswith("hsl(from var(--gcid-r6orange001)"))

    def test_derived_color_with_opacity_and_negative_saturation(self):
        html = ("<style>:root{--gcid-a: #F97316;--gcid-b: hsl(from var(--gcid-a) calc(h + 0) "
                "max(0, calc(s - 100)) calc(l - 10) / 0.5);--gcid-c: var(--gcid-a);}</style>")
        g = tokens5_from_html(html)["colors"]["global"]
        self.assertEqual(g["gcid-b"]["value"], "rgba(110,110,110,0.5)")
        self.assertEqual(g["gcid-c"]["value"], "#F97316")

    def test_unresolvable_derived_color_keeps_raw_with_null_value(self):
        html = "<style>:root{--gcid-b: hsl(from var(--gcid-missing) calc(h + 0) calc(s + 0) calc(l + 30));}</style>"
        g = tokens5_from_html(html)["colors"]["global"]["gcid-b"]
        self.assertIsNone(g["value"])
        self.assertEqual(g["base"], "gcid-missing")


class VariablesTest(unittest.TestCase):
    def test_number_variable(self):
        v = tokens5_from_html(TRACE_HTML)["variables"]
        self.assertEqual(v["gvid-r6radius01"], {"value": "12px", "kind": "numbers"})
        self.assertEqual(v["gvid-r6secpad01"], {"value": "clamp(48px, 8vw, 96px)", "kind": "numbers"})

    def test_font_and_image_variables(self):
        v = tokens5_from_html(PLAIN_HTML)["variables"]
        self.assertEqual(v["gvid-r6font0001"], {"value": "Poppins", "kind": "fonts"})
        self.assertEqual(v["gvid-r6image001"], {"value": "https://example.com/r6-hero.jpg", "kind": "images"})

    def test_page_without_references_leaks_all_active_variables(self):
        self.assertIn("gvid-r6unusedn1", tokens5_from_html(PLAIN_HTML)["variables"])
        self.assertNotIn("gvid-r6unusedn1", tokens5_from_html(TRACE_HTML)["variables"])

    def test_customizer_fonts_in_the_numeric_block_are_not_variables(self):
        self.assertFalse([k for k in tokens5_from_html(PLAIN_HTML)["variables"] if not k.startswith("gvid-")])

    def test_gradient_variable_kind(self):
        html = "<style>:root{--gvid-g1: linear-gradient(90deg,#fff 0%,#000 100%);}</style>"
        self.assertEqual(tokens5_from_html(html)["variables"]["gvid-g1"]["kind"], "gradients")


class CssParsingTest(unittest.TestCase):
    def test_unterminated_rule_at_eof_keeps_its_last_character(self):
        g = tokens5_from_html("<style>:root{--gcid-a: #fff</style>")["colors"]["global"]
        self.assertEqual(g["gcid-a"]["value"], "#fff")

    def test_semicolon_inside_url_does_not_split_the_declaration(self):
        html = "<style>:root{--gvid-img: url(data:image/png;base64,iVBORw0KGgo=);--gvid-n: 4px;}</style>"
        v = tokens5_from_html(html)["variables"]
        self.assertEqual(v["gvid-img"], {"value": "data:image/png;base64,iVBORw0KGgo=", "kind": "images"})
        self.assertEqual(v["gvid-n"], {"value": "4px", "kind": "numbers"})

    def test_semicolon_inside_a_quoted_url_or_string(self):
        html = ("<style>:root{--gvid-img: url(\"data:image/svg+xml;utf8,<svg/>\");"
                "--gvid-f: 'A;B Sans';--gvid-n: 2px}</style>")
        v = tokens5_from_html(html)["variables"]
        self.assertEqual(v["gvid-img"]["value"], "data:image/svg+xml;utf8,<svg/>")
        self.assertEqual(v["gvid-f"], {"value": "A;B Sans", "kind": "fonts"})
        self.assertEqual(v["gvid-n"]["value"], "2px")


class PresetCssTest(unittest.TestCase):
    def test_module_preset_declarations(self):
        p = tokens5_from_html(TRACE_HTML)["presets_css"]["r6btnpreset1"]
        self.assertEqual((p["kind"], p["module"]), ("module", "divi/button"))
        self.assertIn(".preset--module--divi-button--r6btnpreset1", p["selector"])
        self.assertEqual(p["declarations"]["background-color"], "var(--gcid-r6orange001)")
        self.assertEqual(p["declarations"]["color"], "#ffffff")
        self.assertEqual(p["declarations"]["border-top-left-radius"], "var(--gvid-r6radius01)")
        self.assertNotIn("font-size", p["declarations"])  # the :after rule stays in rules only
        self.assertTrue(any(r["selector"].endswith(":after") for r in p["rules"]))

    def test_group_preset_declarations(self):
        p = tokens5_from_html(TRACE_HTML)["presets_css"]["r6fontpreset1"]
        self.assertEqual((p["kind"], p["module"], p["group_name"]), ("group", "divi/heading", "divi/font"))
        self.assertEqual(p["declarations"], {"font-family": "var(--gvid-r6font0001)", "font-weight": "700",
                                             "color": "var(--gcid-r6navy0001)", "font-size": "52px"})

    def test_wrapper_class_media_rules_and_default_presets(self):
        html = ("<style>.preset--module--divi-row-inner--abc_wrapper{margin:0}"
                ".preset--module--divi-row-inner--abc{padding:4px}"
                "@media only screen and (max-width:767px){.preset--module--divi-row-inner--abc{padding:1px}}"
                ".preset--module--divi-button--default{color:#111111}</style>")
        t = tokens5_from_html(html)
        p = t["presets_css"]["abc"]
        self.assertEqual(p["module"], "divi/row-inner")
        self.assertEqual(p["declarations"], {"padding": "4px"})
        self.assertIn({"selector": ".preset--module--divi-row-inner--abc", "declarations": {"padding": "1px"},
                       "media": "only screen and (max-width:767px)"}, p["rules"])
        self.assertNotIn("default", t["presets_css"])
        self.assertEqual(t["preset_defaults"]["divi/button"]["declarations"], {"color": "#111111"})


class StylesheetsTest(unittest.TestCase):
    def test_same_origin_et_cache_links_only(self):
        self.assertEqual(stylesheet_links(HOME_HTML, SITE + "/"), [HOME_CSS_URL])

    def test_linked_css_is_read_when_given(self):
        self.assertEqual(tokens5_from_html(HOME_HTML)["colors"]["customizer"], {})
        c = tokens5_from_html(HOME_HTML, {HOME_CSS_URL: HOME_CSS})["colors"]["customizer"]
        self.assertEqual(c["primary"]["value"], "#7C3AED")


class MergeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = trace_tokens()

    def test_site(self):
        s = self.t["site"]
        self.assertEqual((s["url"], s["divi_version"], s["divi_major"], s["content_format"]),
                         (SITE, "5.13.1", 5, "blocks"))
        self.assertEqual(s["source_pages"], [{"id": 23, "url": TRACE_URL, "format": "blocks"}])

    def test_refs_fold_into_global_colors_and_variables(self):
        self.assertNotIn("global_refs", self.t["colors"])
        self.assertNotIn("variables_refs", self.t)
        navy = self.t["colors"]["global"]["gcid-r6navy0001"]
        self.assertEqual((navy["value"], navy["uses"]), ("#0B2A3C", 1))
        self.assertEqual(self.t["colors"]["global"]["gcid-r6orange001"]["uses"], 0)  # only reached via a preset
        pad = self.t["variables"]["gvid-r6secpad01"]
        self.assertEqual((pad["value"], pad["kind"], pad["uses"]), ("clamp(48px, 8vw, 96px)", "numbers", 2))

    def test_referenced_ids_without_a_recoverable_value(self):
        v = self.t["variables"]
        self.assertEqual((v["gvid-r6tagline1"]["value"], v["gvid-r6tagline1"]["uses"]), (None, 1))
        self.assertEqual((v["gvid-r6ctalink1"]["value"], v["gvid-r6ctalink1"]["uses"]), (None, 1))

    def test_unused_active_variable_from_the_extra_page(self):
        self.assertEqual(self.t["variables"]["gvid-r6unusedn1"], {"value": "7px", "kind": "numbers", "uses": 0})

    def test_presets_carry_their_css(self):
        btn = self.t["presets"]["divi/button"]
        self.assertEqual([(p["id"], p["uses"]) for p in btn], [("r6btnpreset1", 1)])
        self.assertEqual(btn[0]["css"]["declarations"]["background-color"], "var(--gcid-r6orange001)")
        font = self.t["group_presets"]["divi/font"][0]
        self.assertEqual((font["id"], font["module"], font["group_id"]), ("r6fontpreset1", "divi/heading",
                                                                          "designTitleText"))
        self.assertEqual(font["css"]["declarations"]["font-size"], "52px")

    def test_customizer_and_typography(self):
        self.assertEqual(self.t["colors"]["customizer"]["primary"]["value"], "#7C3AED")
        typo = self.t["typography"]
        self.assertEqual(typo["customizer"]["heading_font"]["value"], "Open Sans")
        self.assertEqual(typo["heading_font"], "Open Sans")  # no heading font in content: Customizer's
        self.assertIn("Open Sans", typo["loaded_fonts"])

    def test_palette_links_a_literal_to_its_global_color(self):
        src = page(block("text", text_attrs(module={"decoration": {"background": {"desktop": {"value": {
            "color": "#0b2a3c"}}}}})))
        t = build_tokens5([{"id": 1, "url": TRACE_URL, "raw": src}], {TRACE_URL: tokens5_from_html(TRACE_HTML)},
                          SITE, load_schema5())
        self.assertEqual([p.get("global") for p in t["colors"]["palette"] if p["hex"] == "#0b2a3c"],
                         ["gcid-r6navy0001"])

    def test_json_serializable_with_site_first(self):
        json.dumps(self.t)
        self.assertEqual(next(iter(self.t)), "site")


class ValidateAgainstOwnTokensTest(unittest.TestCase):
    def codes(self, src, tokens):
        return {f.code for f in validate_source(src, tokens=tokens)}

    def test_trace_page_is_clean_against_its_own_tokens(self):
        self.assertFalse(self.codes(TRACE_CONTENT, trace_tokens()) & TOKEN_CODES)

    def test_divi_ai_layout_is_clean_against_its_own_tokens(self):
        src = AI_LAYOUT.read_text()
        t = build_tokens5([{"id": 1, "url": TRACE_URL, "raw": src}], {TRACE_URL: tokens5_from_html(TRACE_HTML)},
                          SITE, load_schema5())
        self.assertFalse(self.codes(src, t) & TOKEN_CODES)

    def test_off_palette_color_is_still_flagged(self):
        src = page(block("text", text_attrs(module={"decoration": {"background": {"desktop": {"value": {
            "color": "#123456"}}}}})))
        self.assertIn("W_OFF_PALETTE_COLOR", self.codes(src, trace_tokens()))

    def test_global_and_customizer_values_are_on_palette(self):
        for color in ("#0B2A3C", "#fdcdab", "#7C3AED"):
            with self.subTest(color=color):
                src = page(block("text", text_attrs(module={"decoration": {"background": {"desktop": {"value": {
                    "color": color}}}}})))
                self.assertNotIn("W_OFF_PALETTE_COLOR", self.codes(src, trace_tokens()))

    def test_font_variable_and_customizer_fonts_are_on_brand(self):
        def font(family):
            return page(block("text", text_attrs(content={
                "innerContent": {"desktop": {"value": "<p>x</p>"}},
                "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": family}}}}}}})))
        for family in ("Poppins", "Open Sans"):
            with self.subTest(family=family):
                self.assertNotIn("W_OFF_BRAND_FONT", self.codes(font(family), trace_tokens()))
        self.assertIn("W_OFF_BRAND_FONT", self.codes(font("Comic Sans MS"), trace_tokens()))

    def test_validate_cli_with_extracted_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            tokens_path, page_path = Path(tmp) / "tokens.json", Path(tmp) / "page.html"
            tokens_path.write_text(json.dumps(trace_tokens()))
            page_path.write_text(TRACE_CONTENT)
            run = subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), str(page_path), "--tokens",
                                  str(tokens_path), "--json"], capture_output=True, text=True)
        found = {f["code"] for f in json.loads(run.stdout)["findings"]}
        self.assertFalse(found & TOKEN_CODES, run.stdout)


class ExtractCliTest(unittest.TestCase):
    def run_main(self, *argv):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "tokens.json"
            with mock.patch("extract_tokens._get", side_effect=AssertionError("offline run fetched a URL")), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
                rc = main([*argv, "--out", str(out)])
            self.assertEqual(rc, 0, err.getvalue())
            return json.loads(out.read_text())

    def test_offline_content_file_with_html_file(self):
        t = self.run_main("--content-file", str(AI_LAYOUT), "--url", "http://x.test",
                          "--html-file", str(HTML5 / "r6-tokens-trace.html"))
        self.assertEqual(t["site"]["divi_major"], 5)
        self.assertEqual(t["site"]["divi_version"], "5.13.1")
        self.assertTrue(t["module_styles"])
        self.assertIn("divi/button", t["presets"])

    def test_shortcode_file_is_an_alias_for_content_file(self):
        t = self.run_main("--shortcode-file", str(HTML5 / "r6-tokens-trace.content.txt"),
                          "--html-file", str(HTML5 / "r6-tokens-trace.html"))
        self.assertEqual(t["site"]["divi_major"], 5)

    def test_divi4_content_keeps_the_divi4_output(self):
        t = self.run_main("--content-file", str(D4_SHORTCODE))
        self.assertNotIn("divi_major", t["site"])
        self.assertIn("et_pb_button", t["module_styles"])


class ExtractOnlineTest(unittest.TestCase):
    def fake_get(self, url, auth=""):
        self.urls.append(url)
        if "/wp-json/wp/v2/pages/23" in url:
            return json.dumps({"id": 23, "link": TRACE_URL, "content": {"raw": TRACE_CONTENT}}).encode()
        pages = {SITE + "/wp-content/themes/Divi/style.css": "/*\nTheme Name: Divi\nVersion: 5.13.1\n*/",
                 TRACE_URL: TRACE_HTML, SITE + "/": HOME_HTML, HOME_CSS_URL: HOME_CSS}
        if url in pages:
            return pages[url].encode()
        raise OSError(f"404 {url}")

    def test_online_divi5_site(self):
        self.urls = []
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "tokens.json"
            with mock.patch("extract_tokens._get", side_effect=self.fake_get), \
                    mock.patch.dict("os.environ", {"WP_APP_PASSWORD": "pw"}), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
                rc = main(["--site", SITE, "--user", "u", "--page", "23", "--out", str(out)])
            self.assertEqual(rc, 0, err.getvalue())
            t = json.loads(out.read_text())
        self.assertEqual((t["site"]["divi_major"], t["site"]["divi_version"]), (5, "5.13.1"))
        self.assertIn(SITE + "/", self.urls)       # the home page is sampled too
        self.assertIn(HOME_CSS_URL, self.urls)     # its et-cache stylesheet is followed
        self.assertIn("gvid-r6unusedn1", t["variables"])  # leaked by the reference-free home page
        self.assertEqual(t["colors"]["global"]["gcid-r6navy0001"]["value"], "#0B2A3C")


class ExtractShortcodeOnDivi5SiteTest(unittest.TestCase):
    """A Divi 5 site whose sampled pages are all Divi 4 shortcode: Divi 5 tokens, no module styles, a warning."""

    def fake_get(self, url, auth=""):
        if "/wp-json/wp/v2/pages/23" in url:
            self.urls.append(url)
            return json.dumps({"id": 23, "link": TRACE_URL,
                               "content": {"raw": D4_SHORTCODE.read_text()}}).encode()
        return ExtractOnlineTest.fake_get(self, url, auth)

    def test_all_shortcode_pages_on_a_divi5_site(self):
        self.urls = []
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "tokens.json"
            with mock.patch("extract_tokens._get", side_effect=self.fake_get), \
                    mock.patch.dict("os.environ", {"WP_APP_PASSWORD": "pw"}), \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
                rc = main(["--site", SITE, "--user", "u", "--page", "23", "--out", str(out)])
            self.assertEqual(rc, 0, err.getvalue())
            t = json.loads(out.read_text())
        self.assertEqual((t["site"]["divi_major"], t["site"]["content_format"]), (5, "shortcode"))
        self.assertEqual(t["site"]["source_pages"], [{"id": 23, "url": TRACE_URL, "format": "shortcode"}])
        self.assertEqual((t["module_styles"], t["typography"]["scale"], t["colors"]["palette"],
                          t["section_exemplars"]), ({}, {}, [], []))
        self.assertIn(f"warning: page 23 ({TRACE_URL}) is shortcode content on a Divi 5 site: it adds no module "
                      "styles (convert it in the Visual Builder first)", err.getvalue())
        # the site-wide design data still comes from the public HTML
        self.assertEqual(t["colors"]["global"]["gcid-r6navy0001"]["value"], "#0B2A3C")
        self.assertEqual(t["presets"]["divi/button"][0]["id"], "r6btnpreset1")


class FixtureHygieneTest(unittest.TestCase):
    def test_public_html_fixtures_are_not_block_fixtures(self):
        self.assertFalse([p for p in d5_fixtures() if "html" in p.relative_to(FIXTURES5).parts[:-1]])


if __name__ == "__main__":
    unittest.main()
