import io
import json
import subprocess
import sys
import time
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from _paths import FIXTURES, SCRIPTS
from divi_schema import load_schema
from validate import Finding, main, validate_source

SCHEMA = load_schema()
TOKENS = json.loads((FIXTURES / "tokens-min.json").read_text())

FIXTURE = str(FIXTURES / "valid" / "handwritten-landing.txt")


def section(inner, attrs=""):
    return f'[et_pb_section {attrs}][et_pb_row][et_pb_column type="4_4"]{inner}[/et_pb_column][/et_pb_row][/et_pb_section]'


class TokensTest(unittest.TestCase):
    def codes(self, src):
        return {f.code for f in validate_source(src, SCHEMA, tokens=TOKENS) if f.level == "warning"}

    def test_off_palette_color(self):
        self.assertIn("W_OFF_PALETTE_COLOR", self.codes(section('[et_pb_blurb icon_color="#123456"][/et_pb_blurb]')))
        self.assertNotIn("W_OFF_PALETTE_COLOR", self.codes(section('[et_pb_blurb icon_color="#F97316"][/et_pb_blurb]')))

    def test_unknown_global_color(self):
        self.assertIn("W_UNKNOWN_GLOBAL_COLOR", self.codes(section('[et_pb_blurb icon_color="gcid-other"][/et_pb_blurb]')))

    def test_off_brand_font(self):
        self.assertIn("W_OFF_BRAND_FONT", self.codes(section('[et_pb_heading title_font="Comic Sans MS|400|||||||"][/et_pb_heading]')))
        self.assertNotIn("W_OFF_BRAND_FONT", self.codes(section('[et_pb_heading title_font="Montserrat|700|||||||"][/et_pb_heading]')))

    def test_off_scale_section_padding(self):
        self.assertIn("W_OFF_SCALE_SPACING", self.codes(section("", 'custom_padding="13px||13px||true|false"')))

    def test_known_preset_is_not_warned(self):
        src = section('[et_pb_button _module_preset="11111111-2222-3333-4444-555555555555"][/et_pb_button]')
        self.assertNotIn("W_UNKNOWN_PRESET", self.codes(src))


class BaselineTest(unittest.TestCase):
    def test_baseline_marks_preexisting(self):
        legacy = section('[et_pb_cta text_font_size_tablet="16px"][/et_pb_cta]')
        edited = legacy + section('[et_pb_text bogus_attr="1"]<p>new</p>[/et_pb_text]')
        fs = validate_source(edited, SCHEMA, baseline=legacy)
        stale = [f for f in fs if f.attr == "text_font_size_tablet"]
        new = [f for f in fs if f.attr == "bogus_attr"]
        self.assertTrue(stale and all(f.preexisting for f in stale))
        self.assertTrue(new and not any(f.preexisting for f in new))


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), *args], capture_output=True, text=True)

    def test_schema_load_failure_exits_2(self):
        with patch("validate.load_schema", side_effect=FileNotFoundError("schema dir missing")):
            with redirect_stdout(io.StringIO()):
                rc = main([FIXTURE])
        self.assertEqual(rc, 2)

    def test_json_warning_count_excludes_preexisting(self):
        findings = [
            Finding("warning", "W_ONE", "msg", 1, 1, "path", preexisting=False),
            Finding("warning", "W_TWO", "msg", 1, 1, "path", preexisting=True),
        ]
        with patch("validate.validate_source", return_value=findings):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([FIXTURE, "--json"])
        data = json.loads(buf.getvalue())
        self.assertEqual(data["warnings"], 1)
        self.assertEqual(rc, 0)

    def test_exit_codes_and_json(self):
        good = self.run_cli(str(FIXTURES / "valid" / "handwritten-landing.txt"), "--json")
        self.assertEqual(good.returncode, 0, good.stdout)
        self.assertEqual(json.loads(good.stdout)["errors"], 0)
        bad_path = FIXTURES / "invalid" / "unknown-attr.txt"
        bad = self.run_cli(str(bad_path))
        self.assertEqual(bad.returncode, 1)
        self.assertIn("E_UNKNOWN_ATTR", bad.stdout)
        self.assertEqual(self.run_cli("/nonexistent.txt").returncode, 2)

    def test_large_page_performance(self):
        big = (FIXTURES / "valid" / "handwritten-landing.txt").read_text() * 60   # ≈ 200 KB, 1,000+ modules
        t0 = time.time()
        validate_source(big, SCHEMA, tokens=TOKENS)
        self.assertLess(time.time() - t0, 3.0)


if __name__ == "__main__":
    unittest.main()
