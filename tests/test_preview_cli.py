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
VERSION = fetch_divi.newest_cached()
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
