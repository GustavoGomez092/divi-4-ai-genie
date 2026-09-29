"""Divi 5 validator: token checks, baseline/fragment/JSON parity and the performance guard."""
import contextlib
import io
import json
import tempfile
import time
import unittest
from pathlib import Path

from _paths import FIXTURES, FIXTURES5, d5_fixtures
from test_divi5_validate_values import V, block, page, text_attrs, var
from validate import main, validate_source

TOKENS = json.loads((FIXTURES / "tokens-min.json").read_text())


def bg(color):
    return text_attrs(module={"decoration": {"background": {"desktop": {"value": {"color": color}}}}})


def codes(src, **kw):
    return [f.code for f in validate_source(src, tokens=TOKENS, **kw)]


class TokenChecksTest(unittest.TestCase):
    def test_literal_off_palette_color(self):
        found = [f for f in validate_source(page(block("text", bg("#123456"))), tokens=TOKENS)
                 if f.code == "W_OFF_PALETTE_COLOR"]
        self.assertEqual(len(found), 1)
        self.assertEqual((found[0].tag, found[0].attr, found[0].level),
                         ("divi/text", "module.decoration.background.color:desktop:value", "warning"))

    def test_palette_and_variable_colors_are_fine(self):
        for color in ("#0b2a3c", "#0B2A3C", "transparent", var("gcid-brand")):
            with self.subTest(color=color):
                self.assertNotIn("W_OFF_PALETTE_COLOR", codes(page(block("text", bg(color)))))

    def test_off_brand_font(self):
        def font(family):
            return text_attrs(content={"innerContent": {"desktop": {"value": "<p>x</p>"}},
                                       "decoration": {"bodyFont": {"body": {"font": {"desktop": {
                                           "value": {"family": family}}}}}}})
        self.assertIn("W_OFF_BRAND_FONT", codes(page(block("text", font("Comic Sans MS")))))
        self.assertNotIn("W_OFF_BRAND_FONT", codes(page(block("text", font("montserrat")))))
        self.assertNotIn("W_OFF_BRAND_FONT", codes(page(block("text", font(var("gvid-font", "content"))))))

    def test_off_scale_section_padding(self):
        def section(top, bottom):
            wrap = {"builderVersion": V, "module": {"decoration": {"spacing": {"desktop": {"value": {
                "padding": {"top": top, "bottom": bottom}}}}}}}
            return (f"<!-- wp:divi/section {json.dumps(wrap)} --><!-- /wp:divi/section -->")
        self.assertIn("W_OFF_SCALE_SPACING", codes(section("10px", "10px")))
        self.assertNotIn("W_OFF_SCALE_SPACING", codes(section("96px", "96px")))

    def test_variable_section_padding_is_fine(self):
        ref = var("gvid-spacing", "content")
        wrap = {"builderVersion": V, "module": {"decoration": {"spacing": {"desktop": {"value": {
            "padding": {"top": ref, "bottom": ref}}}}}}}
        src = f"<!-- wp:divi/section {json.dumps(wrap)} --><!-- /wp:divi/section -->"
        self.assertNotIn("W_OFF_SCALE_SPACING", codes(src))

    def test_no_tokens_no_findings(self):
        self.assertNotIn("W_OFF_PALETTE_COLOR",
                         [f.code for f in validate_source(page(block("text", bg("#123456"))))])

    def test_odd_tokens_shape_is_tolerated(self):
        for t in ({"colors": [], "typography": "x", "spacing": []}, {"colors": {"palette": None}}):
            validate_source(page(block("text", bg("#123456"))), tokens=t)


class BaselineTest(unittest.TestCase):
    def test_self_baseline_is_all_preexisting(self):
        src = (FIXTURES5 / "invalid" / "unknown-attr.html").read_text()
        found = validate_source(src, baseline=src, tokens=TOKENS)
        self.assertTrue(found)
        self.assertTrue(all(f.preexisting for f in found))

    def test_new_error_is_not_preexisting(self):
        old = page(block("text", bg("#0b2a3c")))
        bad = text_attrs(bogus={"desktop": {"value": "x"}})
        new = page(block("text", bg("#0b2a3c")), block("text", bad))
        fresh = [f for f in validate_source(new, baseline=old, tokens=TOKENS) if not f.preexisting and f.level == "error"]
        self.assertEqual([(f.code, f.attr) for f in fresh], [("E5_UNKNOWN_ATTR", "bogus:desktop:value")])

    def test_off_palette_survives_a_line_shift(self):
        old = page(block("text", bg("#123456")))
        new = page(block("text", text_attrs("<p>more</p>")), block("text", bg("#123456")))
        found = [f for f in validate_source(new, baseline=old, tokens=TOKENS) if f.code == "W_OFF_PALETTE_COLOR"]
        self.assertTrue(found and all(f.preexisting for f in found))

    def test_fragment_skips_page_level_checks(self):
        full = {f.code for f in validate_source(page(block("text", text_attrs())))}
        frag = {f.code for f in validate_source(page(block("text", text_attrs())), fragment=True)}
        self.assertIn("W_NO_H1", full)
        self.assertNotIn("W_NO_H1", frag)


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main([str(a) for a in args])
        return rc, buf.getvalue()

    def test_json_valid_fixture(self):
        rc, out = self.run_cli(d5_fixtures()[0], "--json")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["errors"], 0)

    def test_json_invalid_fixture(self):
        rc, out = self.run_cli(FIXTURES5 / "invalid" / "unknown-attr.html", "--json")
        data = json.loads(out)
        self.assertEqual(rc, 1)
        self.assertEqual(data["findings"][0]["code"], "E5_UNKNOWN_ATTR")
        self.assertEqual(set(data["findings"][0]), {"level", "code", "message", "line", "col", "path", "tag", "attr",
                                                    "value", "hint", "preexisting"})

    def test_baseline_flag(self):
        path = FIXTURES5 / "invalid" / "unknown-attr.html"
        rc, out = self.run_cli(path, "--baseline", path, "--json")
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["errors"], 0)
        self.assertTrue(all(f["preexisting"] for f in data["findings"]))

    def test_tokens_flag(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "p.html"
            p.write_text(page(block("text", bg("#123456"))))
            rc, out = self.run_cli(p, "--tokens", FIXTURES / "tokens-min.json", "--json", "--fragment")
        self.assertIn("W_OFF_PALETTE_COLOR", [f["code"] for f in json.loads(out)["findings"]])


class PerformanceTest(unittest.TestCase):
    def test_largest_fixture_under_budget(self):
        big = max(d5_fixtures(), key=lambda p: p.stat().st_size)
        src = big.read_text()
        validate_source(src, tokens=TOKENS)  # warm the schema cache
        t0 = time.time()
        validate_source(src, tokens=TOKENS)
        self.assertLess(time.time() - t0, 1.5, big.name)


if __name__ == "__main__":
    unittest.main()
