import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

from _paths import FIXTURES
from divi_schema import load_schema
from extract_tokens import build_tokens, main
from tokens_from_html import tokens_from_html

HTML = (FIXTURES / "html" / "customized-page.html").read_text()
SHORTCODE_FILE = str(FIXTURES / "valid" / "handwritten-landing.txt")


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

    def test_build_tokens_merges_two_html_sources(self):
        # Fix round 1, item 4: customizer merge is first-non-empty-wins per key, and fonts are a
        # union in first-seen order across sources.
        raw = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()
        html_a = ('<style>body{color:#333344}a{color:#0055ff}</style>'
                  '<link rel="stylesheet" id="et-builder-googlefonts-cached-css" '
                  'href="https://fonts.googleapis.com/css?family=Montserrat:400&#038;display=swap" />')
        html_b = ('<style>body{color:#000000}h1,h2{color:#112233}'
                  '.et_pb_counter_amount{background-color:#ff00aa}</style>'
                  '<link rel="stylesheet" id="et-builder-googlefonts-cached-css" '
                  'href="https://fonts.googleapis.com/css?family=Lato:400&#038;display=swap" />')
        t = build_tokens(
            [{"id": 1, "url": "https://client.example/a/", "raw": raw},
             {"id": 2, "url": "https://client.example/b/", "raw": raw}],
            {"https://client.example/a/": html_a, "https://client.example/b/": html_b},
            "https://client.example", load_schema())
        c = t["colors"]["customizer"]
        # body_text/link only appear in A -> A's values win even though B also sets body_text.
        self.assertEqual(c["body_text"], "#333344")
        self.assertEqual(c["link"], "#0055ff")
        # heading/accent only appear in B.
        self.assertEqual(c["heading"], "#112233")
        self.assertEqual(c["accent"], "#ff00aa")
        self.assertEqual(t["typography"]["loaded_fonts"], ["Montserrat", "Lato"])

    def test_media_query_color_is_ignored_for_customizer_lookup(self):
        # Fix round 1, item 3: a breakpoint override inside @media must not win over the top-level
        # (desktop) rule just because it appears later in source order.
        html = "<style>body{color:#111111}\n@media (max-width:767px){body{color:#222222}}</style>"
        self.assertEqual(tokens_from_html(html)["customizer"].get("body_text"), "#111111")

    def test_media_query_before_desktop_rule_is_still_ignored(self):
        html = "<style>@media (max-width:767px){body{color:#222222}}\nbody{color:#111111}</style>"
        self.assertEqual(tokens_from_html(html)["customizer"].get("body_text"), "#111111")

    def test_main_returns_2_for_unwritable_out_path(self):
        rc = main(["--shortcode-file", SHORTCODE_FILE, "--out", "/nonexistent-dir-xyz/x.json"])
        self.assertEqual(rc, 2)

    def test_main_returns_2_for_malformed_rest_response(self):
        with mock.patch("extract_tokens._get", return_value=b"{}"), \
                mock.patch.dict(os.environ, {"WP_APP_PASSWORD": "super-secret-password"}):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                rc = main(["--site", "https://client.example", "--user", "editor", "--page", "1",
                           "--out", "/tmp/task12-malformed-rest.json"])
        self.assertEqual(rc, 2)
        self.assertNotIn("super-secret-password", stderr.getvalue())
        self.assertNotIn("Authorization", stderr.getvalue())

    def test_online_mode_resolves_credentials_from_keys_file(self):
        secret = "aaaa BBBB cccc DDDD eeee FFFF"
        raw = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()
        calls = []

        def fake_get(url, auth=""):
            calls.append((url, auth))
            if "wp-json" in url:
                return json.dumps({"id": 1, "link": "https://client.example/p/",
                                   "content": {"raw": raw}}).encode()
            return b""

        with tempfile.TemporaryDirectory() as tmp:
            keys_path = Path(tmp) / "keys.json"
            keys_path.write_text(json.dumps({"keys": [
                {"name": "Test Site", "site": "https://client.example", "user": "keyuser", "key": secret},
            ]}))
            out = Path(tmp) / "tokens.json"
            with mock.patch("extract_tokens._get", side_effect=fake_get), \
                    mock.patch.dict(os.environ, {"WP_APP_PASSWORD": ""}, clear=False):
                rc = main(["--key", "Test Site", "--keys", str(keys_path), "--page", "1", "--out", str(out)])
        self.assertEqual(rc, 0)
        self.assertEqual(calls[0], ("https://client.example/wp-json/wp/v2/pages/1?context=edit",
                                    f"keyuser:{secret}"))

    def test_online_mode_unknown_key_exits_2_without_leaking(self):
        secret = "aaaa BBBB cccc DDDD eeee FFFF"
        with tempfile.TemporaryDirectory() as tmp:
            keys_path = Path(tmp) / "keys.json"
            keys_path.write_text(json.dumps({"keys": [
                {"name": "Test Site", "site": "https://client.example", "user": "keyuser", "key": secret},
            ]}))
            stderr = io.StringIO()
            with redirect_stderr(stderr), mock.patch.dict(os.environ, {"WP_APP_PASSWORD": ""}, clear=False):
                rc = main(["--key", "Nope", "--keys", str(keys_path), "--page", "1",
                          "--out", str(Path(tmp) / "tokens.json")])
        self.assertEqual(rc, 2)
        self.assertIn("Test Site", stderr.getvalue())
        self.assertNotIn(secret, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
