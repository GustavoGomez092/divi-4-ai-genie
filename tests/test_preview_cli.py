"""CLI tests for scripts/preview.py, the pure-Python preview (Task 24).

The render/serve tests need a cached Divi build (they never download one) and are skipped
without it. The user found in the spike that icons break when a page served over HTTP references
file:// assets; these tests pin the fix (data: URIs in standalone files, /__divi/ when serving).
"""
import http.client
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from _paths import FIXTURES, SCRIPTS

import fetch_divi

PREVIEW = SCRIPTS / "preview.py"
VERSION = fetch_divi.newest_cached()
LANDING = FIXTURES / "valid" / "handwritten-landing.txt"
# et_pb_sidebar needs WordPress widgets: it always renders as the fallback in the Python preview.
UNSUPPORTED_PAGE = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
                    '[et_pb_sidebar area="sidebar-1"][/et_pb_sidebar]'
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


class DoctorAndExactTest(unittest.TestCase):
    def test_doctor_exits_zero_and_reports(self):
        r = run("doctor")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("python:", r.stdout)
        self.assertIn("cached Divi versions:", r.stdout)
        self.assertIn("node", r.stdout.lower())

    def test_exact_without_node_exits_2_with_guidance(self):
        with tempfile.TemporaryDirectory() as empty:
            env = {**os.environ, "PATH": empty}
            r = run("render", LANDING, "--exact", env=env)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("Node", r.stderr)

    def test_usage_without_command_exits_2(self):
        self.assertEqual(run().returncode, 2)


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
        for v in ("4.27.3", "4.27.10"):
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

    def test_newest_cached_then_latest(self):
        self.assertEqual(self.preview.resolve_divi_version(None, None), "4.27.10")
        with mock.patch.dict(os.environ, {"PP_DIVI_CACHE": str(self.cache / "none")}):
            self.assertEqual(self.preview.resolve_divi_version(None, None), "latest")

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

    def test_coverage_summary_lists_unsupported_modules(self):
        with tempfile.TemporaryDirectory() as d:
            page = Path(d) / "t.txt"
            page.write_text(UNSUPPORTED_PAGE)
            r = run("render", page, "--divi", VERSION, "--no-js", cwd=d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("et_pb_sidebar", r.stdout)
        self.assertIn("--exact", r.stdout)


@unittest.skipUnless(VERSION, "no Divi build cached")
class ServeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        pages = Path(cls.tmp.name)
        (pages / "landing.txt").write_text(LANDING.read_text())
        (pages / "partial.txt").write_text(UNSUPPORTED_PAGE)
        (pages / "broken.txt").write_bytes(b"\xff\xfe[et_pb_section][/et_pb_section]")  # not UTF-8
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
        status, body, _ = get(self.port, "/partial")
        self.assertEqual(status, 200)
        self.assertIn("exact preview: add --exact", body.decode("utf-8"))
        self.assertNotIn("exact preview: add --exact", get(self.port, "/landing")[1].decode("utf-8"))

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


if __name__ == "__main__":
    unittest.main()
