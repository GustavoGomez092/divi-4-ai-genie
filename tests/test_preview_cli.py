"""CLI tests for scripts/preview.py, the pure-Python preview (Task 24).

The render/serve tests need a cached Divi build (they never download one) and are skipped
without it. The user found in the spike that icons break when a page served over HTTP references
file:// assets; these tests pin the fix (data: URIs in standalone files, /__divi/ when serving).
"""
import contextlib
import http.client
import http.server
import io
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.parse
import zipfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from _paths import FIXTURES, SCRIPTS

import fetch_divi

PREVIEW = SCRIPTS / "preview.py"
VERSION = fetch_divi.newest_cached(major=4)  # the Python preview renders Divi 4 only
LANDING = FIXTURES / "valid" / "handwritten-landing.txt"
# et_pb_sidebar needs WordPress widgets: it always renders as the fallback in the Python preview, and
# neither preview has the site's widgets. et_pb_search isn't ported to Python but --exact renders it.
UNSUPPORTED_PAGE = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
                    '[et_pb_sidebar area="sidebar-1"][/et_pb_sidebar]'
                    '[/et_pb_column][/et_pb_row][/et_pb_section]')
OEMBED_PAGE = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
               '[et_pb_video src="https://www.youtube.com/watch?v=dQw4w9WgXcQ"][/et_pb_video]'
               '[/et_pb_column][/et_pb_row][/et_pb_section]')
EXACT_ONLY_PAGE = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
                   '[et_pb_search][/et_pb_search]'
                   '[/et_pb_column][/et_pb_row][/et_pb_section]')


def run(*args, env=None, cwd=None, timeout=120):
    return subprocess.run([sys.executable, str(PREVIEW), *map(str, args)], capture_output=True, text=True,
                          env=env, cwd=cwd, timeout=timeout)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def get(port: int, raw_path: str):
    """GET with the path sent exactly as given (no client-side '..' normalisation)."""
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    try:
        conn.putrequest("GET", raw_path, skip_accept_encoding=True)
        conn.endheaders()
        r = conn.getresponse()
        return r.status, r.read(), dict(r.getheaders())
    finally:
        conn.close()


# --- a minimal fake Elegant Themes server, for the --keys credential-flow tests below (mirrors
# tests/test_fetch_divi.py's fake-server style) --------------------------------------------------
def _et_zip_bytes(version):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("Divi/style.css", f"/*\nTheme Name: Divi\nVersion: {version}\n*/\n")
        zf.writestr("Divi/functions.php", "<?php\n")
    return buf.getvalue()


def _et_recording_handler(dl_body):
    received = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            received.append(self.path)
            if "api_downloads.php" in self.path:
                body, code, ctype = dl_body, 200, "application/zip"
            else:
                body, code, ctype = b'a:1:{s:6:"status";s:9:"available"}', 200, "text/html"
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    return Handler, received


@contextmanager
def _et_server(handler_cls):
    server = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


class DoctorAndExactTest(unittest.TestCase):
    def test_doctor_exits_zero_and_reports(self):
        r = run("doctor")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("python:", r.stdout)
        self.assertIn("cached Divi versions:", r.stdout)
        self.assertIn("node", r.stdout.lower())

    def test_doctor_reports_divi_5_cache_status(self):
        with tempfile.TemporaryDirectory() as cache:
            (Path(cache) / "Divi-4.27.9" / "Divi").mkdir(parents=True)
            (Path(cache) / "Divi-4.27.9" / "Divi" / "style.css").write_text("/* */")
            r = run("doctor", env={**os.environ, "PP_DIVI_CACHE": cache})
            self.assertIn("Divi 5 (block pages): not cached", r.stdout)
            self.assertIn("fetch-divi latest5", r.stdout)
            (Path(cache) / "Divi-5.13.1" / "Divi").mkdir(parents=True)
            (Path(cache) / "Divi-5.13.1" / "Divi" / "style.css").write_text("/* */")
            r = run("doctor", env={**os.environ, "PP_DIVI_CACHE": cache})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Divi 5 (block pages): cached 5.13.1", r.stdout)
        self.assertIn("cached Divi versions: 4.27.9, 5.13.1", r.stdout)

    def test_exact_without_node_exits_2_with_guidance(self):
        with tempfile.TemporaryDirectory() as empty:
            env = {**os.environ, "PATH": empty}
            r = run("render", LANDING, "--exact", env=env)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Node", r.stderr)

    def _fake_node(self, d, version):
        node = Path(d) / "node"
        node.write_text(f"#!/bin/sh\nif [ \"$1\" = --version ]; then echo {version}; exit 0; fi\necho ran-preview; exit 0\n")
        node.chmod(0o755)
        return {**os.environ, "PATH": d}

    def test_exact_with_old_node_exits_2_with_guidance(self):
        with tempfile.TemporaryDirectory() as d:
            r = run("render", LANDING, "--exact", env=self._fake_node(d, "v18.19.0"))
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("20", r.stderr)
        self.assertIn("v18.19.0", r.stderr)
        self.assertNotIn("ran-preview", r.stdout)

    def test_exact_with_node_20_runs_preview_mjs(self):
        with tempfile.TemporaryDirectory() as d:
            r = run("render", LANDING, "--exact", env=self._fake_node(d, "v20.11.1"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ran-preview", r.stdout)

    def test_docs_say_node_20(self):
        text = PREVIEW.read_text()
        self.assertNotIn("Node 18", text)
        self.assertNotIn("Node.js 18", text)
        self.assertIn("Node 20+", text)

    def test_usage_without_command_exits_2(self):
        self.assertEqual(run().returncode, 2)


class ExactEnvTest(unittest.TestCase):
    """The environment preview.py builds for the --exact (preview.mjs) child process: ET_* filled
    in from resolve_et_credentials, env always taking precedence over the keys file."""

    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        self.preview = preview

    def test_no_credentials_leaves_et_vars_unset(self):
        with tempfile.TemporaryDirectory() as home:
            env = {"HOME": home, "PATH": os.environ.get("PATH", "")}
            env.pop("ET_USERNAME", None)
            env.pop("ET_API_KEY", None)
            with mock.patch.dict(os.environ, env, clear=True):
                got = self.preview.exact_env(None)
        self.assertNotIn("ET_USERNAME", got)
        self.assertNotIn("ET_API_KEY", got)

    def test_keys_file_credentials_fill_the_child_env(self):
        with tempfile.TemporaryDirectory() as d:
            keys_file = Path(d) / "keys.json"
            keys_file.write_text(json.dumps({"elegant_themes": {"username": "fileuser", "api_key": "filesecret"}}))
            with mock.patch.dict(os.environ, {}, clear=True):
                os.environ["PATH"] = "/usr/bin:/bin"
                got = self.preview.exact_env(str(keys_file))
        self.assertEqual(got["ET_USERNAME"], "fileuser")
        self.assertEqual(got["ET_API_KEY"], "filesecret")

    def test_env_credentials_win_over_keys_file(self):
        with tempfile.TemporaryDirectory() as d:
            keys_file = Path(d) / "keys.json"
            keys_file.write_text(json.dumps({"elegant_themes": {"username": "fileuser", "api_key": "filesecret"}}))
            with mock.patch.dict(os.environ, {"ET_USERNAME": "envuser", "ET_API_KEY": "envsecret"}):
                got = self.preview.exact_env(str(keys_file))
        self.assertEqual(got["ET_USERNAME"], "envuser")
        self.assertEqual(got["ET_API_KEY"], "envsecret")

    def test_preserves_the_rest_of_the_current_environment(self):
        with mock.patch.dict(os.environ, {"SOME_MARKER_VAR": "yes"}):
            got = self.preview.exact_env(None)
        self.assertEqual(got.get("SOME_MARKER_VAR"), "yes")


class DoctorKeysFlagTest(unittest.TestCase):
    def test_reports_none_when_no_credentials(self):
        with tempfile.TemporaryDirectory() as home:
            env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY", "DIVI_KEYS_FILE")}
            env["HOME"] = home
            r = run("doctor", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Elegant Themes credentials: none", r.stdout)

    def test_reports_env_when_env_vars_set(self):
        env = {**os.environ, "ET_USERNAME": "someone", "ET_API_KEY": "secretvalue"}
        r = run("doctor", env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Elegant Themes credentials: env", r.stdout)
        self.assertNotIn("secretvalue", r.stdout)

    def test_reports_keys_json_when_only_file_has_it(self):
        with tempfile.TemporaryDirectory() as d:
            keys_file = Path(d) / "keys.json"
            keys_file.write_text(json.dumps({"elegant_themes": {"username": "fileuser", "api_key": "filesecret"}}))
            env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY")}
            r = run("doctor", "--keys", str(keys_file), env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Elegant Themes credentials: keys.json", r.stdout)
        self.assertNotIn("filesecret", r.stdout)


class FetchDiviAndRenderKeysFlagTest(unittest.TestCase):
    """`preview.py fetch-divi` / `render` get ET credentials from --keys when the version isn't
    cached (same fake-ET-server style as tests/test_fetch_divi.py)."""

    def test_fetch_divi_uses_keys_file_reaching_fake_server(self):
        handler, received = _et_recording_handler(_et_zip_bytes("6.0.0"))
        with _et_server(handler) as base, tempfile.TemporaryDirectory() as cache, tempfile.TemporaryDirectory() as d:
            keys_file = Path(d) / "keys.json"
            keys_file.write_text(json.dumps({"elegant_themes": {"username": "fileuser", "api_key": "filesecret"}}))
            env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY")}
            env["PP_ET_ENDPOINT"] = base
            env["PP_CACHE_DIR"] = cache
            r = run("fetch-divi", "6.0.0", "--keys", str(keys_file), env=env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(any("fileuser" in p for p in received), received)
        for stream in (r.stdout, r.stderr):
            self.assertNotIn("filesecret", stream)

    def test_render_downloads_uncached_version_via_keys_file(self):
        page = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
               '[et_pb_text]Hi[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]')
        handler, received = _et_recording_handler(_et_zip_bytes("6.0.1"))
        with _et_server(handler) as base, tempfile.TemporaryDirectory() as cache, tempfile.TemporaryDirectory() as d:
            keys_file = Path(d) / "keys.json"
            keys_file.write_text(json.dumps({"elegant_themes": {"username": "fileuser2", "api_key": "filesecret2"}}))
            page_file = Path(d) / "p.txt"
            page_file.write_text(page)
            out_file = Path(d) / "out.html"
            env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY")}
            env["PP_ET_ENDPOINT"] = base
            env["PP_CACHE_DIR"] = cache
            r = run("render", page_file, "--divi", "6.0.1", "--out", out_file, "--keys", str(keys_file), env=env)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(out_file.exists())
        self.assertTrue(any("fileuser2" in p for p in received), received)
        for stream in (r.stdout, r.stderr):
            self.assertNotIn("filesecret2", stream)


TOKENS5 = {
    "site": {"divi_version": "5.13.1", "divi_major": 5},
    "colors": {
        "global": {
            "gcid-navy": {"value": "#0B2A3C", "uses": 1},
            "gcid-unknown": {"value": None, "uses": 2},
            "gcid-light": {"value": "#fdcdab", "raw": "hsl(from var(--gcid-navy) calc(h + 0) s l)", "base": "gcid-navy",
                           "uses": 1},
            "gcid-evil": {"value": "red}</style><script>alert(1)</script>", "uses": 1},
        },
        "customizer": {"primary": {"id": "gcid-primary-color", "value": "#7C3AED", "overridden": True},
                       "link": {"id": "gcid-link-color", "value": None}},
        "palette": [{"hex": "#0b2a3c", "count": 1}],
    },
    "variables": {
        "gvid-pad": {"value": "clamp(48px, 8vw, 96px)", "kind": "numbers", "uses": 2},
        "gvid-font": {"value": "Poppins", "kind": "fonts", "uses": 0},
        "gvid-img": {"value": "https://example.com/hero.jpg", "kind": "images", "uses": 0},
        "gvid-grad": {"value": "linear-gradient(90deg, #fff 0%, #000 100%)", "kind": "gradients", "uses": 0},
        "gvid-link": {"value": None, "kind": "links", "uses": 1},
        "gvid-text": {"value": None, "kind": "strings", "uses": 1},
    },
    "presets": {"divi/button": [
        {"id": "btn1", "uses": 1, "css": {
            "selector": "body #page-container .et_pb_section .preset--module--divi-button--btn1",
            "declarations": {"background-color": "var(--gcid-navy)", "color": "#ffffff"},
            "rules": [
                {"selector": "body #page-container .et_pb_section .preset--module--divi-button--btn1",
                 "declarations": {"background-color": "var(--gcid-navy)", "color": "#ffffff"}},
                {"selector": "body #page-container .et_pb_section .preset--module--divi-button--btn1:hover",
                 "declarations": {"color": "#000000"}},
                {"selector": ".preset--module--divi-button--btn1", "declarations": {"font-size": "14px"},
                 "media": "only screen and (max-width: 980px)"},
            ]}},
        {"id": "btn2", "uses": 1, "css": None},
    ]},
    "group_presets": {"divi/font": [
        {"id": "f1", "uses": 1, "module": "divi/heading", "group_id": "designTitleText", "css": {
            "selector": ".preset--group--divi-heading--divi-font--designtitletext--f1 h2",
            "declarations": {"font-weight": "700"},
            "rules": [{"selector": ".preset--group--divi-heading--divi-font--designtitletext--f1 h2",
                       "declarations": {"font-weight": "700"}}]}},
    ]},
    "preset_defaults": {"divi/text": {
        "selector": ".preset--module--divi-text--default", "declarations": {"line-height": "1.9em"},
        "rules": [{"selector": ".preset--module--divi-text--default", "declarations": {"line-height": "1.9em"}}]}},
}


class SeedCssTest(unittest.TestCase):
    """seed_css(tokens): the recovered Divi 5 design system as CSS, so var(--gcid-*)/var(--gvid-*) and preset
    classes render with the client's values in the (otherwise stock) Playground preview."""

    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        self.css = preview.seed_css(TOKENS5)

    def root(self):
        m = re.match(r":root:root\{(.*?)\}", self.css)
        self.assertIsNotNone(m, self.css[:200])
        return m.group(1)

    def test_root_block_comes_first_and_beats_divis_own_root(self):
        self.assertTrue(self.css.startswith(":root:root{"), self.css[:80])

    def test_colors_and_customizer_colors_are_seeded(self):
        root = self.root()
        self.assertIn("--gcid-navy:#0B2A3C;", root)
        self.assertIn("--gcid-light:#fdcdab;", root)  # a derived color uses its resolved value
        self.assertIn("--gcid-primary-color:#7C3AED;", root)

    def test_null_values_and_unsafe_values_are_skipped(self):
        for name in ("gcid-unknown", "gcid-link-color", "gvid-link", "gvid-text", "gcid-evil"):
            self.assertNotIn(f"--{name}:", self.css)
        self.assertNotIn("</style", self.css)
        self.assertNotIn("<script", self.css)

    def test_values_that_could_break_out_of_a_declaration_are_skipped(self):
        import preview
        bad = {"a;color:red": "semicolon", "a\\9": "backslash", "a\nb": "newline", "red'": "unbalanced quote",
               'x"': "unbalanced double quote", "a}b": "brace"}
        tokens = {"colors": {"global": {f"gcid-bad{i}": {"value": v} for i, v in enumerate(bad)}},
                  "variables": {"gvid-font": {"value": "Po'ppins", "kind": "fonts"},
                                "gvid-img": {"value": 'https://x.test/a".jpg', "kind": "images"}},
                  "presets": {"divi/text": [{"id": "p", "css": {"rules": [
                      {"selector": ".preset--module--divi-text--p", "declarations": {
                          "font-family": "'Open Sans', sans-serif", "color": "red;x:y", "margin": "0\\;"}},
                      {"selector": '.a[data-x="1"', "declarations": {"color": "blue"}},
                      {"selector": ".preset--module--divi-text--p", "declarations": {"color": "green"},
                       "media": "screen;x"}]}}]}}
        css = preview.seed_css(tokens)
        self.assertNotIn("gcid-bad", css)
        self.assertNotIn("gvid-font", css)
        self.assertNotIn("gvid-img", css)
        self.assertEqual(css, ".preset--module--divi-text--p{font-family:'Open Sans', sans-serif}")

    def test_variables_are_seeded_in_css_form(self):
        root = self.root()
        self.assertIn("--gvid-pad:clamp(48px, 8vw, 96px);", root)
        self.assertIn("--gvid-font:'Poppins';", root)
        self.assertIn("--gvid-img:url(\"https://example.com/hero.jpg\");", root)
        self.assertIn("--gvid-grad:linear-gradient(90deg, #fff 0%, #000 100%);", root)

    def test_preset_rules_are_emitted_with_media(self):
        css = self.css
        self.assertIn("body #page-container .et_pb_section .preset--module--divi-button--btn1{"
                      "background-color:var(--gcid-navy);color:#ffffff}", css)
        self.assertIn("body #page-container .et_pb_section .preset--module--divi-button--btn1:hover{color:#000000}", css)
        self.assertIn("@media only screen and (max-width: 980px){.preset--module--divi-button--btn1{font-size:14px}}", css)
        self.assertIn(".preset--group--divi-heading--divi-font--designtitletext--f1 h2{font-weight:700}", css)
        self.assertIn(".preset--module--divi-text--default{line-height:1.9em}", css)
        self.assertLess(css.index(":root:root"), css.index(".preset--"))

    def test_nothing_to_seed_is_empty(self):
        import preview
        self.assertEqual(preview.seed_css({}), "")
        self.assertEqual(preview.seed_css({"site": {"divi_version": "4.27.9"}, "colors": {"palette": []}}), "")


class SeedOptionsTest(unittest.TestCase):
    """seed_options(tokens): the recovered Divi 5 design system as the WordPress options Divi reads it from, so
    the Playground preview resolves $variable() refs to number/font/string/link/image variables and global colors
    the way the live site does (seed_css alone can't: Divi resolves a gvid ref to '' unless the variable exists
    in et_divi_global_variables)."""

    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        self.preview = preview
        self.opts = preview.seed_options(TOKENS5)

    def test_option_names(self):
        self.assertEqual(sorted(self.opts), ["et_divi", "et_divi_global_variables"])

    def test_global_colors_go_to_et_global_data_active_and_labelled_by_id(self):
        colors = self.opts["et_divi"]["et_global_data"]["global_colors"]
        self.assertEqual(sorted(colors), ["gcid-light", "gcid-navy"])  # null and unsafe skipped
        navy = colors["gcid-navy"]
        self.assertEqual((navy["color"], navy["label"], navy["status"]), ("#0B2A3C", "gcid-navy", "active"))
        self.assertEqual((navy["folder"], navy["usedInPosts"]), ("", []))
        self.assertIn("lastUpdated", navy)
        self.assertEqual(colors["gcid-light"]["color"], "#fdcdab")  # a derived color uses its resolved value

    def test_customizer_colors_go_to_their_customizer_options(self):
        et_divi = self.opts["et_divi"]
        self.assertEqual(et_divi["accent_color"], "#7C3AED")
        self.assertNotIn("link_color", et_divi)  # value null
        tokens = {"colors": {"customizer": {
            "primary": {"id": "gcid-primary-color", "value": "#111111"},
            "secondary": {"id": "gcid-secondary-color", "value": "#222222"},
            "heading": {"id": "gcid-heading-color", "value": "#333333"},
            "body": {"id": "gcid-body-color", "value": "#444444"},
            "link": {"id": "gcid-link-color", "value": "#555555"}},
            "global": {"gcid-body-color": {"value": "#666666"}}}}  # a Customizer id listed as a global color
        et_divi = self.preview.seed_options(tokens)["et_divi"]
        self.assertEqual({k: et_divi[k] for k in ("accent_color", "secondary_accent_color", "header_color",
                                                   "link_color")},
                         {"accent_color": "#111111", "secondary_accent_color": "#222222",
                          "header_color": "#333333", "link_color": "#555555"})
        self.assertIn(et_divi["font_color"], ("#444444", "#666666"))
        self.assertNotIn("et_global_data", et_divi)  # never stored as a plain global color

    def test_variables_go_to_their_kinds_bucket(self):
        v = self.opts["et_divi_global_variables"]
        self.assertEqual(sorted(v), ["fonts", "gradients", "images", "numbers"])
        self.assertEqual(v["numbers"]["gvid-pad"], {"id": "gvid-pad", "label": "gvid-pad",
                                                    "value": "clamp(48px, 8vw, 96px)", "order": 1,
                                                    "status": "active", "type": "numbers"})
        self.assertEqual(v["fonts"]["gvid-font"]["value"], "Poppins")  # the stored form, not CSS-quoted
        self.assertEqual(v["images"]["gvid-img"]["value"], "https://example.com/hero.jpg")  # not url("…")
        self.assertEqual(v["gradients"]["gvid-grad"]["value"], "linear-gradient(90deg, #fff 0%, #000 100%)")
        for bucket, items in v.items():
            for gvid, item in items.items():
                self.assertEqual((item["id"], item["type"], item["status"]), (gvid, bucket, "active"))

    def test_string_and_link_variables_are_seeded_too(self):
        tokens = {"variables": {"gvid-tag": {"value": "Fast, friendly plumbers", "kind": "strings"},
                                "gvid-cta": {"value": "https://example.com/start", "kind": "links"},
                                "gvid-nul": {"value": None, "kind": "strings"}}}
        v = self.preview.seed_options(tokens)["et_divi_global_variables"]
        self.assertEqual(v["strings"]["gvid-tag"]["value"], "Fast, friendly plumbers")
        self.assertEqual(v["links"]["gvid-cta"]["value"], "https://example.com/start")
        self.assertNotIn("gvid-nul", v["strings"])

    def test_values_are_sanitized_like_seed_css(self):
        bad = ["a;color:red", "a\\9", "a\nb", "red'", 'x"', "a}b", "<b>", "/* x */", "calc(1px"]
        tokens = {"colors": {"global": {f"gcid-bad{i}": {"value": b} for i, b in enumerate(bad)},
                             "customizer": {"primary": {"id": "gcid-primary-color", "value": "red;x:y"}}},
                  "variables": dict({f"gvid-bad{i}": {"value": b, "kind": "numbers"} for i, b in enumerate(bad)},
                                    **{"gvid-font": {"value": "Po'ppins", "kind": "fonts"},
                                       "gvid-img": {"value": 'https://x.test/a".jpg', "kind": "images"},
                                       "gvid-str": {"value": "it's", "kind": "strings"}})}
        self.assertEqual(self.preview.seed_options(tokens), {})

    def test_bad_ids_and_unknown_kinds_are_skipped(self):
        tokens = {"colors": {"global": {"navy": {"value": "#000"}, "gcid-x y": {"value": "#000"}},
                             "customizer": {"primary": {"id": "gcid-evil-color", "value": "#000"}}},
                  "variables": {"gvid-a": {"value": "1px", "kind": "colors"}, "gvid-b": {"value": "1px"},
                                "pad": {"value": "1px", "kind": "numbers"}}}
        self.assertEqual(self.preview.seed_options(tokens), {})

    def test_nothing_to_seed_is_empty(self):
        self.assertEqual(self.preview.seed_options({}), {})
        self.assertEqual(self.preview.seed_options([]), {})
        self.assertEqual(self.preview.seed_options({"site": {"divi_version": "4.27.9"},
                                                    "colors": {"palette": []}}), {})

    def test_sample_tokens_seed_the_recipe_variables(self):
        sample = json.loads((SCRIPTS.parent / "recipes" / "divi5" / "sample-tokens.json").read_text())
        opts = self.preview.seed_options(sample)
        numbers = opts["et_divi_global_variables"]["numbers"]
        self.assertEqual(numbers["gvid-r6secpad01"]["value"], "clamp(48px, 8vw, 96px)")
        self.assertEqual(numbers["gvid-r6radius01"]["value"], "12px")
        self.assertEqual(opts["et_divi"]["et_global_data"]["global_colors"]["gcid-r6navy0001"]["color"], "#0B2A3C")
        self.assertEqual(opts["et_divi"]["accent_color"], "#F97316")


BLOCK_PAGE = ('<!-- wp:divi/placeholder --><!-- wp:divi/section {"builderVersion":"5.13.1"} -->'
              '<!-- wp:divi/row {"builderVersion":"5.13.1"} --><!-- wp:divi/column {"builderVersion":"5.13.1"} -->'
              '<!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"./img/a.png"}}}},'
              '"builderVersion":"5.13.1"} /-->'
              '<!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section --><!-- /wp:divi/placeholder -->')

# A stand-in `node`: reports its version, logs its argv plus the staged page / seed sidecar it was handed to
# $FAKE_NODE_LOG, writes --out, and for `serve` prints the ready URLs the way preview.mjs does, then waits.
FAKE_NODE = r"""#!/bin/sh
if [ "$1" = --version ]; then echo v20.11.1; exit 0; fi
log="$FAKE_NODE_LOG"
echo "ARGS $*" >> "$log"
out=""; pages=""; port=""; prev=""
for a in "$@"; do
  case "$prev" in --out) out="$a";; --pages) pages="$a";; --port) port="$a";; esac
  case "$a" in *.txt) echo "PAGE $(cat "$a")" >> "$log"; s="${a%.txt}.seed.css"
    [ -f "$s" ] && echo "SEED $(cat "$s")" >> "$log"; o="${a%.txt}.seed.json"
    [ -f "$o" ] && echo "OPTS $(cat "$o")" >> "$log";; esac
  prev="$a"
done
if [ "$2" = render ]; then echo "<html>fake</html>" > "$out"; exit 0; fi
if [ "$2" = serve ]; then
  echo "PID $$" >> "$log"
  for f in "$pages"/*.txt; do n=$(basename "$f" .txt); echo "http://127.0.0.1:$port/?pp_preview=$n"; done
  exec sleep 60
fi
exit 0
"""


class BlocksRoutingTest(unittest.TestCase):
    """A Divi 5 block page always goes to Playground (preview.mjs) with a Divi 5 version, local images inlined
    and the tokens seed as a sidecar; the Python renderer is never used for it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.cache = d / "cache"
        for v in ("4.27.10", "5.13.1"):
            (self.cache / f"Divi-{v}" / "Divi").mkdir(parents=True)
            (self.cache / f"Divi-{v}" / "Divi" / "style.css").write_text(f"/*\nVersion: {v}\n*/")
        self.bin = d / "bin"
        self.bin.mkdir()
        node = self.bin / "node"
        node.write_text(FAKE_NODE)
        node.chmod(0o755)
        self.log = d / "node.log"
        self.pages = d / "pages"
        (self.pages / "img").mkdir(parents=True)
        (self.pages / "img" / "a.png").write_bytes(b"\x89PNG\r\n")
        self.page = self.pages / "home.html"
        self.page.write_text(BLOCK_PAGE)
        self.env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY")}
        self.env.update(PATH=f"{self.bin}:/bin:/usr/bin", PP_DIVI_CACHE=str(self.cache), FAKE_NODE_LOG=str(self.log))

    def tearDown(self):
        self.tmp.cleanup()

    def logged(self):
        return self.log.read_text() if self.log.exists() else ""

    def test_render_routes_to_playground_with_newest_cached_5x(self):
        out = Path(self.tmp.name) / "o.html"
        r = run("render", self.page, "--out", out, env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        args = self.logged().splitlines()[0].split()
        self.assertEqual(args[1:3], [str(SCRIPTS / "preview" / "preview.mjs"), "render"])
        self.assertTrue(args[3].endswith("/home.txt"), args)
        self.assertEqual(args[args.index("--out") + 1], str(out.resolve()))
        self.assertEqual(args[args.index("--divi") + 1], "5.13.1")
        self.assertNotIn("--tokens", args)
        self.assertTrue(out.exists())

    def test_render_inlines_local_images_in_the_staged_page(self):
        r = run("render", self.page, "--out", Path(self.tmp.name) / "o.html", env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        page = next(l for l in self.logged().splitlines() if l.startswith("PAGE "))
        self.assertIn('"src":"data:image/png;base64,', page)
        self.assertNotIn("./img/a.png", page)
        self.assertEqual(self.page.read_text(), BLOCK_PAGE)  # the source page is untouched

    def test_render_with_exact_takes_the_same_route(self):
        r = run("render", self.page, "--out", Path(self.tmp.name) / "o.html", "--exact", env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("--divi 5.13.1", self.logged())

    def test_tokens_pick_the_version_and_seed_the_page(self):
        tokens = Path(self.tmp.name) / "tokens.json"
        tokens.write_text(json.dumps(dict(TOKENS5, site={"divi_version": "5.9.0", "divi_major": 5})))
        r = run("render", self.page, "--out", Path(self.tmp.name) / "o.html", "--tokens", tokens, env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        log = self.logged()
        self.assertIn("--divi 5.9.0", log)
        seed = log[log.index("SEED "):]
        self.assertIn("--gcid-navy:#0B2A3C", seed)
        self.assertIn("preset--module--divi-button--btn1", seed)

    def test_no_seed_sidecar_without_tokens(self):
        run("render", self.page, "--out", Path(self.tmp.name) / "o.html", env=self.env)
        self.assertNotIn("SEED ", self.logged())
        self.assertNotIn("OPTS ", self.logged())

    def test_tokens_seed_the_site_options_sidecar(self):
        tokens = Path(self.tmp.name) / "tokens.json"
        tokens.write_text(json.dumps(TOKENS5))
        r = run("render", self.page, "--out", Path(self.tmp.name) / "o.html", "--tokens", tokens, env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        line = next(l for l in self.logged().splitlines() if l.startswith("OPTS "))
        sys.path.insert(0, str(SCRIPTS))
        import preview
        self.assertEqual(json.loads(line[5:]), preview.seed_options(TOKENS5))
        self.assertIn("design variables", r.stdout)

    def test_tokens_with_nothing_for_the_options_write_no_options_sidecar(self):
        tokens = Path(self.tmp.name) / "tokens.json"
        tokens.write_text(json.dumps({"site": {"divi_version": "5.13.1"}, "presets": TOKENS5["presets"]}))
        r = run("render", self.page, "--out", Path(self.tmp.name) / "o.html", "--tokens", tokens, env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("SEED ", self.logged())
        self.assertNotIn("OPTS ", self.logged())

    def test_a_divi_4_version_for_a_block_page_is_refused(self):
        r = run("render", self.page, "--divi", "4.27.10", "--out", Path(self.tmp.name) / "o.html", env=self.env)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Divi 5", r.stderr)
        self.assertEqual(self.logged(), "")

    def test_default_out_never_overwrites_an_html_source_page(self):
        r = run("render", self.page, env=self.env, cwd=self.pages)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.page.read_text(), BLOCK_PAGE)
        args = self.logged().splitlines()[0].split()
        self.assertEqual(args[args.index("--out") + 1], str((self.pages / "home.preview.html").resolve()))

    def test_block_page_without_node_explains(self):
        env = dict(self.env, PATH="/nonexistent")
        r = run("render", self.page, "--out", Path(self.tmp.name) / "o.html", env=env)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Node 20+", r.stderr)
        self.assertIn("Divi 5", r.stderr)

    def test_shortcode_page_with_exact_is_unchanged(self):
        r = run("render", LANDING, "--exact", "--out", Path(self.tmp.name) / "o.html", env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        args = self.logged().splitlines()[0].split()
        self.assertEqual(args[2:], ["render", str(LANDING.resolve()), "--out",
                                    str((Path(self.tmp.name) / "o.html").resolve())])


class BlocksServeTest(unittest.TestCase):
    """serve: shortcode pages stay on the Python preview; block pages are staged (images inlined, tokens seed)
    for one warm Playground and redirected to it; edits are re-staged."""

    @classmethod
    def setUpClass(cls):
        cls.t = BlocksRoutingTest("setUp")
        cls.t.setUp()
        (cls.t.pages / "landing.txt").write_text(LANDING.read_text())
        (cls.t.pages / "odd name.html").write_text(BLOCK_PAGE)
        (cls.t.pages / "rendered.html").write_text("<html><body>not a page</body></html>")
        cls.port = free_port()
        cls.proc = subprocess.Popen([sys.executable, str(PREVIEW), "serve", "--pages", str(cls.t.pages),
                                     "--port", str(cls.port)], env=cls.t.env,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.time() + 30
        while time.time() < deadline:
            try:
                socket.create_connection(("127.0.0.1", cls.port), timeout=0.5).close()
                return
            except OSError:
                if cls.proc.poll() is not None:
                    break
                time.sleep(0.1)
        cls.tearDownClass()
        raise RuntimeError("preview.py serve did not start")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:
            cls.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            cls.proc.kill()
        cls.t.tearDown()

    def wait_ready(self, path):
        deadline = time.time() + 20
        while time.time() < deadline:
            status, body, headers = get(self.port, path)
            if status != 503:
                return status, body, headers
            time.sleep(0.2)
        self.fail("Playground never became ready")

    def serve_args(self):
        line = next(l for l in self.t.logged().splitlines() if l.startswith("ARGS ") and " serve " in l)
        return line.split()

    def test_block_page_redirects_to_the_warm_playground(self):
        status, _, headers = self.wait_ready("/home")
        self.assertEqual(status, 302)
        args = self.serve_args()
        pg_port = args[args.index("--port") + 1]
        self.assertEqual(headers["Location"], f"http://127.0.0.1:{pg_port}/?pp_preview=home")
        self.assertEqual(args[args.index("--divi") + 1], "5.13.1")
        self.assertNotEqual(pg_port, str(self.port))

    def test_page_names_are_made_safe_for_playground(self):
        status, _, headers = self.wait_ready("/odd%20name")
        self.assertEqual(status, 302)
        self.assertTrue(headers["Location"].endswith("?pp_preview=odd-name"), headers["Location"])

    def test_staged_pages_inline_images_and_follow_edits(self):
        self.wait_ready("/home")
        stage = Path(self.serve_args()[self.serve_args().index("--pages") + 1])
        staged = stage / "home.txt"
        self.assertIn('"src":"data:image/png;base64,', staged.read_text())
        edited = BLOCK_PAGE.replace('"builderVersion":"5.13.1"} -->', '"builderVersion":"5.13.1","x":1} -->', 1)
        (self.t.pages / "home.html").write_text(edited)
        deadline = time.time() + 5
        while time.time() < deadline and '"x":1' not in staged.read_text():
            time.sleep(0.1)
        self.assertIn('"x":1', staged.read_text())
        (self.t.pages / "home.html").write_text(BLOCK_PAGE)

    def test_shortcode_page_is_still_rendered_by_python(self):
        status, body, headers = get(self.port, "/landing")
        self.assertEqual(status, 200)
        self.assertIn('class="et-l et-l--post"', body.decode("utf-8"))
        self.assertIn("X-Render-Ms", headers)

    def test_index_lists_both_formats_but_not_rendered_html(self):
        status, body, _ = get(self.port, "/")
        html = body.decode("utf-8")
        self.assertEqual(status, 200)
        for name in ("home", "landing", "odd name"):
            self.assertIn(f">{name}<", html)
        self.assertNotIn("rendered", html)
        self.assertEqual(get(self.port, "/rendered")[0], 404)


class PlaygroundPagesTest(unittest.TestCase):
    def test_concurrent_first_requests_start_one_playground(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        t = BlocksRoutingTest("setUp")
        t.setUp()
        self.addCleanup(t.tearDown)
        with mock.patch.dict(os.environ, t.env):
            pg = preview.PlaygroundPages(t.pages, "5.13.1", "", str(t.bin / "node"), dict(t.env))
            self.addCleanup(pg.stop)
            threads = [threading.Thread(target=pg.start) for _ in range(8)]
            for th in threads:
                th.start()
            for th in threads:
                th.join()
            deadline = time.time() + 10
            while pg.base is None and time.time() < deadline:
                time.sleep(0.05)
        self.assertIsNotNone(pg.base)
        self.assertEqual(sum(1 for l in t.logged().splitlines() if l.startswith("ARGS ") and " serve " in l), 1)


    def test_serve_stages_the_options_seed_for_every_block_page(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        t = BlocksRoutingTest("setUp")
        t.setUp()
        self.addCleanup(t.tearDown)
        (t.pages / "about.html").write_text(BLOCK_PAGE)
        opts = preview.seed_options(TOKENS5)
        pg = preview.PlaygroundPages(t.pages, "5.13.1", "", str(t.bin / "node"), dict(t.env), options=opts)
        pg.stage = Path(tempfile.mkdtemp(dir=t.tmp.name))
        pg.sync()
        for name in ("home", "about"):
            self.assertEqual(json.loads((pg.stage / f"{name}.seed.json").read_text()), opts)
        (t.pages / "about.html").unlink()
        pg.sync()
        self.assertFalse((pg.stage / "about.seed.json").exists())


class ServeStartupTest(unittest.TestCase):
    def setUp(self):
        self.t = BlocksRoutingTest("setUp")
        self.t.setUp()
        self.addCleanup(self.t.tearDown)
        self.tmpdir = Path(self.t.tmp.name) / "tmp"
        self.tmpdir.mkdir()

    def test_a_failed_start_leaves_no_playground_child_or_stage_dir(self):
        env = dict(self.t.env, TMPDIR=str(self.tmpdir))
        r = run("serve", "--pages", self.t.pages, "--port", "99999", env=env, timeout=60)
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        time.sleep(0.5)
        self.assertNotIn(" serve ", self.t.logged())
        self.assertEqual(sorted(p.name for p in self.tmpdir.iterdir()), [])

    def test_shortcode_only_serve_output_is_the_divi_4_output(self):
        # Divi 4 output must not change: no Divi 5 resolution (or its note) when there are no block pages.
        cache = Path(self.t.tmp.name) / "cache"
        pages = Path(self.t.tmp.name) / "d4pages"
        pages.mkdir()
        (pages / "landing.txt").write_text(LANDING.read_text())
        tokens = Path(self.t.tmp.name) / "tokens.json"
        tokens.write_text(json.dumps({"site": {"divi_version": ""}}))
        port = free_port()
        proc = subprocess.Popen([sys.executable, str(PREVIEW), "serve", "--pages", str(pages), "--port", str(port),
                                 "--tokens", str(tokens)], env=self.t.env, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.time() + 20
            while time.time() < deadline:
                try:
                    socket.create_connection(("127.0.0.1", port), timeout=0.5).close()
                    break
                except OSError:
                    time.sleep(0.1)
        finally:
            proc.terminate()
            out, err = proc.communicate(timeout=15)
        self.assertEqual(out, f"http://127.0.0.1:{port}/landing\n")
        self.assertEqual(err, f"note: site.divi_version is empty in {tokens}; using the newest cached Divi, 4.27.10\n"
                              "Serving (Python preview); Ctrl-C to stop.\n")
        self.assertEqual(self.t.logged(), "")  # node never ran
        del cache


class BlocksServeStopTest(unittest.TestCase):
    def test_terminating_serve_stops_the_playground_child(self):
        t = BlocksRoutingTest("setUp")
        t.setUp()
        self.addCleanup(t.tearDown)
        port = free_port()
        proc = subprocess.Popen([sys.executable, str(PREVIEW), "serve", "--pages", str(t.pages), "--port", str(port)],
                                env=t.env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.time() + 20
            while time.time() < deadline and "PID " not in t.logged():
                time.sleep(0.1)
            pid = int(t.logged().split("PID ")[1].split()[0])
            os.kill(pid, 0)  # running
        finally:
            proc.terminate()
            proc.wait(timeout=15)
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.1)
        os.kill(pid, 9)
        self.fail("the Playground child outlived serve")


class ExactArgsTest(unittest.TestCase):
    """--exact hands the parsed command to preview.mjs, so Node gets the same page/port/flags."""

    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        self.preview = preview

    def args(self, *argv):
        return self.preview.exact_args(self.preview.build_parser().parse_args(list(argv)))

    def test_serve_forwards_port_pages_and_version(self):
        with tempfile.TemporaryDirectory() as d:
            got = self.args("serve", "--pages", d, "--port=9123", "--divi", "4.27.9", "--exact", "--no-js")
            self.assertEqual(got, ["serve", "--pages", str(Path(d).resolve()), "--port", "9123", "--divi", "4.27.9"])

    def test_serve_default_port_is_forwarded_too(self):
        got = self.args("serve", "--exact")
        self.assertEqual(got[got.index("--port") + 1], "8765")
        self.assertEqual(got[got.index("--pages") + 1], str(Path(".").resolve()))

    def test_render_forwards_page_out_and_tokens(self):
        got = self.args("render", "p.txt", "--exact", "--out", "o.html", "--tokens", "t.json")
        self.assertEqual(got, ["render", str(Path("p.txt").resolve()), "--out", str(Path("o.html").resolve()),
                               "--tokens", str(Path("t.json").resolve())])


class BannerTest(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        self.preview = preview

    def test_oembed_banner_points_to_exact_and_mentions_network(self):
        html = self.preview.banner_html({"unsupported_modules": {"video_oembed": 1}, "needs_site_data": {}})
        self.assertIn("add --exact", html)
        self.assertIn("network", html)
        self.assertNotIn("draft preview", html)

    def test_site_data_banner_points_to_the_draft_preview(self):
        html = self.preview.banner_html({"unsupported_modules": {}, "needs_site_data": {"et_pb_blog": 1}})
        self.assertIn("WordPress draft preview", html)
        self.assertNotIn("add --exact", html)


class ResolveAssetTest(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))
        from divi_render.assets import resolve_asset
        self.resolve = resolve_asset
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.theme = root / "Divi"
        (self.theme / "css").mkdir(parents=True)
        (self.theme / "css" / "a.css").write_text("a{}")
        (self.theme / "functions.php").write_text("<?php")
        (root / "outside.css").write_text("secret{}")
        (self.theme / "css" / "escape.css").symlink_to(root / "outside.css")

    def tearDown(self):
        self.tmp.cleanup()

    def test_static_file_inside_theme_resolves(self):
        self.assertEqual(self.resolve(self.theme, "css/a.css"), (self.theme / "css" / "a.css").resolve())

    def test_escapes_and_non_static_files_are_refused(self):
        for rel in ("../outside.css", "css/../../outside.css", "/../outside.css", "css/escape.css",
                    "functions.php", "css", "css/missing.css"):
            with self.subTest(rel=rel):
                self.assertIsNone(self.resolve(self.theme, rel))


class VersionResolutionTest(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(SCRIPTS))
        import preview
        self.preview = preview
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = Path(self.tmp.name)
        # A cached Divi 5 must never be picked for Divi 4 shortcode (the default major).
        for v in ("4.27.3", "4.27.10", "5.13.1"):
            (self.cache / f"Divi-{v}" / "Divi").mkdir(parents=True)
            (self.cache / f"Divi-{v}" / "Divi" / "style.css").write_text("/* Version: x */")
        self.env = mock.patch.dict(os.environ, {"PP_DIVI_CACHE": str(self.cache)})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_divi_flag_wins(self):
        self.assertEqual(self.preview.resolve_divi_version("4.20.0", None), "4.20.0")

    def test_tokens_site_version_is_next(self):
        tokens = self.cache / "tokens.json"
        tokens.write_text(json.dumps({"site": {"divi_version": "4.26.1"}}))
        self.assertEqual(self.preview.resolve_divi_version(None, str(tokens)), "4.26.1")

    def test_tokens_without_version_is_an_error(self):
        tokens = self.cache / "tokens.json"
        tokens.write_text(json.dumps({"site": {}}))
        with self.assertRaises(self.preview.UsageError):
            self.preview.resolve_divi_version(None, str(tokens))

    def test_tokens_with_empty_version_falls_through_to_newest_cached(self):
        tokens = self.cache / "tokens.json"
        tokens.write_text(json.dumps({"site": {"url": "https://x.example", "divi_version": ""}}))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(self.preview.resolve_divi_version(None, str(tokens)), "4.27.10")
        note = err.getvalue().strip()
        self.assertEqual(len(note.splitlines()), 1, note)
        self.assertIn("divi_version", note)
        self.assertIn("4.27.10", note)

    def test_tokens_with_empty_version_and_no_cache_falls_through_to_latest(self):
        tokens = self.cache / "tokens.json"
        tokens.write_text(json.dumps({"site": {"divi_version": ""}}))
        with mock.patch.dict(os.environ, {"PP_DIVI_CACHE": str(self.cache / "none")}), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.preview.resolve_divi_version(None, str(tokens)), "latest")

    def test_cli_render_with_empty_token_version_does_not_exit_2(self):
        tokens = self.cache / "tokens.json"
        tokens.write_text(json.dumps({"site": {"divi_version": ""}}))
        env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY")}
        env["PP_DIVI_CACHE"] = str(self.cache)
        with tempfile.TemporaryDirectory() as d:
            r = run("render", LANDING, "--tokens", tokens, "--out", Path(d) / "x.html", env=env)
        self.assertNotIn("No site.divi_version", r.stderr)
        self.assertIn("4.27.10", r.stdout + r.stderr)

    def test_newest_cached_then_latest(self):
        self.assertEqual(self.preview.resolve_divi_version(None, None), "4.27.10")
        with mock.patch.dict(os.environ, {"PP_DIVI_CACHE": str(self.cache / "none")}):
            self.assertEqual(self.preview.resolve_divi_version(None, None), "latest")

    def test_major_5_picks_newest_cached_5x(self):
        self.assertEqual(self.preview.resolve_divi_version(None, None, major=5), "5.13.1")
        with mock.patch.dict(os.environ, {"PP_DIVI_CACHE": str(self.cache / "none")}):
            self.assertEqual(self.preview.resolve_divi_version(None, None, major=5), "latest5")

    def test_tokens_with_empty_version_falls_through_to_newest_cached_of_the_major(self):
        tokens = self.cache / "tokens.json"
        tokens.write_text(json.dumps({"site": {"divi_version": ""}}))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(self.preview.resolve_divi_version(None, str(tokens), major=5), "5.13.1")
            self.assertEqual(self.preview.resolve_divi_version(None, str(tokens), major=4), "4.27.10")

    def test_explicit_versions_still_win_for_either_major(self):
        self.assertEqual(self.preview.resolve_divi_version("4.27.3", None, major=5), "4.27.3")
        tokens = self.cache / "tokens.json"
        tokens.write_text(json.dumps({"site": {"divi_version": "5.13.1"}}))
        self.assertEqual(self.preview.resolve_divi_version(None, str(tokens), major=4), "5.13.1")

    def test_python_renderer_theme_default_is_newest_4x(self):
        from divi_render.assets import Theme
        self.assertEqual(Theme.for_version(None).version, "4.27.10")

    def test_shortcode_page_with_a_divi_5_version_is_refused_without_exact(self):
        env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY")}
        env["PP_DIVI_CACHE"] = str(self.cache)
        with tempfile.TemporaryDirectory() as d:
            r = run("render", LANDING, "--divi", "5.13.1", "--out", Path(d) / "x.html", env=env)
            self.assertFalse((Path(d) / "x.html").exists())
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Divi 4", r.stderr)
        self.assertIn("--exact", r.stderr)

    def test_uncached_version_without_credentials_fails_cleanly(self):
        env = {k: v for k, v in os.environ.items() if k not in ("ET_USERNAME", "ET_API_KEY")}
        env["PP_DIVI_CACHE"] = str(self.cache)
        with tempfile.TemporaryDirectory() as d:
            r = run("render", LANDING, "--divi", "0.0.1", "--out", Path(d) / "x.html", env=env)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("ET_USERNAME", r.stderr)


@unittest.skipUnless(VERSION, "no Divi build cached")
class RenderTest(unittest.TestCase):
    def test_standalone_render_embeds_fonts_and_has_no_file_urls(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "landing.html"
            r = run("render", LANDING, "--out", out, "--divi", VERSION, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            html = out.read_text(encoding="utf-8")
        self.assertNotIn("file://", html)
        faces = re.findall(r"@font-face\{[^}]*\}", html)
        etmodules = [f for f in faces if "ETmodules" in f]
        self.assertTrue(etmodules, "no ETmodules @font-face")
        self.assertTrue(all("url(data:font/woff" in f for f in etmodules), etmodules[0][:300])
        self.assertTrue(any("FontAwesome" in f and "url(data:font/woff2" in f for f in faces))
        self.assertIn('id="logo"', html)
        self.assertRegex(html, r'<img src="data:image/png;base64,[^"]+"[^>]*id="logo"')
        self.assertIn("coverage", r.stdout)
        self.assertIn("load from the network", r.stdout)

    def test_default_out_is_page_name_in_cwd(self):
        with tempfile.TemporaryDirectory() as d:
            r = run("render", LANDING, "--no-js", "--divi", VERSION, cwd=d)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue((Path(d) / "handwritten-landing.html").exists())

    def render_summary(self, source: str) -> str:
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "t.txt"
            page.write_text(source)
            r = run("render", page, "--divi", VERSION, "--no-js", cwd=d)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def test_coverage_summary_sends_site_data_modules_to_the_draft_preview(self):
        out = self.render_summary(UNSUPPORTED_PAGE)
        line = next(l for l in out.splitlines() if "et_pb_sidebar" in l)
        self.assertIn("needs the live site's data", line)
        self.assertIn("WordPress draft preview", line)
        self.assertNotIn("--exact", out)

    def test_coverage_summary_sends_oembed_to_exact_with_network(self):
        out = self.render_summary(OEMBED_PAGE)
        line = next(l for l in out.splitlines() if "video_oembed" in l)
        self.assertIn("--exact", line)
        self.assertIn("network", line)
        self.assertNotIn("draft preview", out)

    def test_coverage_summary_lists_unsupported_modules_for_exact(self):
        out = self.render_summary(EXACT_ONLY_PAGE)
        line = next(l for l in out.splitlines() if "et_pb_search" in l)
        self.assertIn("unsupported modules", line)
        self.assertIn("--exact", line)
        self.assertNotIn("draft preview", out)


@unittest.skipUnless(VERSION, "no Divi build cached")
class RenderLocalImagesTest(unittest.TestCase):
    """render must embed local images as data: URIs (Task: preview shows local images), using
    exactly the same local-image rule as publish.py draft (local_media.py), so the output is
    standalone even when --out lives in a different directory than the page."""

    def _page(self, d, extra_section=""):
        (Path(d) / "img").mkdir()
        (Path(d) / "img" / "a.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"0" * 20)
        abs_jpg = Path(d) / "img" / "b.jpg"
        abs_jpg.write_bytes(b"\xff\xd8\xff" + b"1" * 20)
        source = ('[et_pb_section background_image="./img/bg.jpg"]' + extra_section +
                  '[et_pb_row][et_pb_column type="4_4"]'
                  '[et_pb_image src="./img/a.png"][/et_pb_image]'
                  f'[et_pb_image src="file://{abs_jpg}"][/et_pb_image]'
                  '[/et_pb_column][/et_pb_row][/et_pb_section]')
        page = Path(d) / "page.txt"
        page.write_text(source)
        return page

    def test_render_embeds_local_and_background_images_even_with_out_elsewhere(self):
        with tempfile.TemporaryDirectory() as page_dir, tempfile.TemporaryDirectory() as out_dir:
            page = self._page(page_dir)
            (Path(page_dir) / "img" / "bg.jpg").write_bytes(b"\xff\xd8\xff" + b"2" * 20)
            out = Path(out_dir) / "elsewhere.html"
            r = run("render", page, "--out", out, "--divi", VERSION, "--no-js")
            self.assertEqual(r.returncode, 0, r.stderr)
            html = out.read_text(encoding="utf-8")
        self.assertIn("data:image/png;base64,", html)
        self.assertIn("data:image/jpeg;base64,", html)
        self.assertNotIn("./img/", html)
        self.assertNotIn("file://", html)

    def test_missing_local_image_warns_without_failing_render(self):
        with tempfile.TemporaryDirectory() as d:
            source = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
                      '[et_pb_image src="./img/missing.png"][/et_pb_image]'
                      '[/et_pb_column][/et_pb_row][/et_pb_section]')
            page = Path(d) / "page.txt"
            page.write_text(source)
            out = Path(d) / "page.html"
            r = run("render", page, "--out", out, "--divi", VERSION, "--no-js")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(out.exists())
        self.assertIn("src", r.stderr)
        self.assertIn("img/missing.png", r.stderr)


@unittest.skipUnless(VERSION, "no Divi build cached")
class ServeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        pages = Path(cls.tmp.name)
        (pages / "landing.txt").write_text(LANDING.read_text())
        (pages / "partial.txt").write_text(UNSUPPORTED_PAGE)
        (pages / "exactonly.txt").write_text(EXACT_ONLY_PAGE)
        (pages / "broken.txt").write_bytes(b"\xff\xfe[et_pb_section][/et_pb_section]")  # not UTF-8
        (pages / "img").mkdir()
        (pages / "img" / "local.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"3" * 40)
        (pages / "withimage.txt").write_text(
            '[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
            '[et_pb_image src="./img/local.png"][/et_pb_image]'
            '[/et_pb_column][/et_pb_row][/et_pb_section]')
        cls.port = free_port()
        cls.proc = subprocess.Popen([sys.executable, str(PREVIEW), "serve", "--pages", str(pages),
                                     "--port", str(cls.port), "--divi", VERSION],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                socket.create_connection(("127.0.0.1", cls.port), timeout=0.5).close()
                return
            except OSError:
                if cls.proc.poll() is not None:
                    break
                time.sleep(0.1)
        cls.tearDownClass()
        raise RuntimeError("preview.py serve did not start")

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:
            cls.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            cls.proc.kill()
        cls.tmp.cleanup()

    def test_page_is_rendered_with_assets_under_divi_route(self):
        status, body, headers = get(self.port, "/landing")
        self.assertEqual(status, 200)
        html = body.decode("utf-8")
        self.assertIn('class="et-l et-l--post"', html)
        self.assertNotIn("file://", html)
        self.assertIn("url(/__divi/core/admin/fonts/modules/all/modules.woff)", html)
        self.assertIn("/__mtime/landing", html)  # auto-reload poll

    def test_theme_font_is_served(self):
        status, body, headers = get(self.port, "/__divi/core/admin/fonts/modules/all/modules.woff")
        self.assertEqual(status, 200)
        self.assertEqual(headers.get("Content-Type"), "font/woff")
        self.assertGreater(len(body), 10000)

    def test_path_traversal_is_refused(self):
        for path in ("/__divi/../../etc/passwd", "/__divi/%2e%2e/%2e%2e/etc/passwd", "/__divi/../../x.css",
                     "/__divi/../Divi-4.27.9/Divi/style.css/../../../../../x.css", "/__divi/%2e%2e/%2e%2e/x.css",
                     "/__divi/../../../../../../etc/passwd", "/__divi/functions.php"):
            with self.subTest(path=path):
                self.assertEqual(get(self.port, path)[0], 404)

    def test_unsupported_modules_show_the_exact_banner(self):
        status, body, _ = get(self.port, "/exactonly")
        self.assertEqual(status, 200)
        self.assertIn("exact preview: add --exact", body.decode("utf-8"))
        self.assertNotIn("exact preview: add --exact", get(self.port, "/landing")[1].decode("utf-8"))

    def test_site_data_modules_show_the_draft_preview_banner(self):
        status, body, _ = get(self.port, "/partial")
        self.assertEqual(status, 200)
        html = body.decode("utf-8")
        self.assertIn("WordPress draft preview", html)
        self.assertNotIn("add --exact", html)
        self.assertNotIn("id=\"pp-preview-banner\"", get(self.port, "/landing")[1].decode("utf-8"))

    def test_render_error_returns_500_with_the_error(self):
        status, body, _ = get(self.port, "/broken")
        self.assertEqual(status, 500)
        self.assertIn("UnicodeDecodeError", body.decode("utf-8"))
        self.assertEqual(get(self.port, "/landing")[0], 200)  # the server keeps serving

    def test_index_and_missing_page(self):
        status, body, _ = get(self.port, "/")
        self.assertEqual(status, 200)
        self.assertIn("landing", body.decode("utf-8"))
        self.assertEqual(get(self.port, "/nope")[0], 404)

    def test_mtime_endpoint_changes_on_edit(self):
        before = get(self.port, "/__mtime/landing")[1]
        page = Path(self.tmp.name) / "landing.txt"
        time.sleep(0.01)
        page.write_text(page.read_text() + "\n")
        self.assertNotEqual(get(self.port, "/__mtime/landing")[1], before)

    # --- local images: served through a per-request /__local/<name>/<token> allowlist ----------
    def test_local_image_is_routed_and_served(self):
        status, body, _ = get(self.port, "/withimage")
        self.assertEqual(status, 200)
        html = body.decode("utf-8")
        self.assertNotIn("./img/local.png", html)
        self.assertNotIn("file://", html)
        m = re.search(r'src="(/__local/withimage/[A-Za-z0-9_-]+)"', html)
        self.assertIsNotNone(m, html)
        status2, body2, headers2 = get(self.port, m.group(1))
        self.assertEqual(status2, 200)
        self.assertEqual(body2, (Path(self.tmp.name) / "img" / "local.png").read_bytes())
        self.assertEqual(headers2.get("Content-Type"), "image/png")

    def test_local_image_route_confinement(self):
        get(self.port, "/withimage")  # populate the allowlist for this page
        for path in ("/__local/withimage/" + "0" * 32,  # not an allowed token
                     "/__local/withimage/../../../../etc/passwd",
                     "/__local/withimage/%2e%2e/%2e%2e/etc/passwd",
                     "/__local/../../../../etc/passwd/x",
                     "/__local/otherpage/" + "0" * 32):  # a page that was never rendered
            with self.subTest(path=path):
                self.assertEqual(get(self.port, path)[0], 404)

    def test_local_image_route_is_scoped_to_its_own_page(self):
        status, body, _ = get(self.port, "/withimage")
        token = re.search(r'/__local/withimage/([A-Za-z0-9_-]+)', body.decode("utf-8")).group(1)
        get(self.port, "/landing")  # render a different page so its own (empty) allowlist exists
        self.assertEqual(get(self.port, f"/__local/landing/{token}")[0], 404)


if __name__ == "__main__":
    unittest.main()
