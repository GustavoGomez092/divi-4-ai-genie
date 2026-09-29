"""Tests for the stdlib port of scripts/preview/fetch-divi.mjs.

Uses a fake HTTP server (PP_ET_ENDPOINT) so no real network access or credentials are needed.
"""
import http.server
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
import urllib.parse
import zipfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from _paths import SCRIPTS  # noqa: F401  (puts Skill scripts on sys.path)

FETCH_MJS = SCRIPTS / "preview" / "fetch-divi.mjs"

import fetch_divi
from fetch_divi import FetchError

AVAILABLE = b'a:1:{s:6:"status";s:9:"available"}'


def _zip_bytes(version):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("Divi/style.css", f"/*\nTheme Name: Divi\nVersion: {version}\n*/\n")
        zf.writestr("Divi/functions.php", "<?php\n")
    return buf.getvalue()


def _make_handler(status_body=AVAILABLE, dl_status=200, dl_body=b"", dl_ctype="application/zip"):
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if "api_downloads.php" in self.path:
                body, code, ctype = dl_body, dl_status, dl_ctype
            else:
                body, code, ctype = status_body, 200, "text/html"
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    return Handler


@contextmanager
def _server(handler_cls):
    server = http.server.HTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def _seed_cached(cache_dir, version, content_version=None):
    theme = Path(cache_dir) / f"Divi-{version}" / "Divi"
    theme.mkdir(parents=True)
    (theme / "style.css").write_text(f"/*\nVersion: {content_version or version}\n*/\n")
    return theme


class CacheLayoutTest(unittest.TestCase):
    def test_theme_dir_none_when_not_cached(self):
        with tempfile.TemporaryDirectory() as cache:
            self.assertIsNone(fetch_divi.theme_dir("9.9.9", cache))

    def test_theme_dir_returns_path_when_cached(self):
        with tempfile.TemporaryDirectory() as cache:
            theme = _seed_cached(cache, "4.27.9")
            self.assertEqual(fetch_divi.theme_dir("4.27.9", cache), theme)

    def test_newest_cached_orders_versions_numerically(self):
        with tempfile.TemporaryDirectory() as cache:
            _seed_cached(cache, "4.27.9")
            _seed_cached(cache, "4.27.10")
            _seed_cached(cache, "4.9.0")
            self.assertEqual(fetch_divi.newest_cached(cache), "4.27.10")

    def test_list_cached_is_public_and_sorted(self):
        with tempfile.TemporaryDirectory() as cache:
            _seed_cached(cache, "4.27.10")
            _seed_cached(cache, "4.9.0")
            (Path(cache) / "Divi-5.0.0").mkdir()  # no style.css: not a usable build
            self.assertEqual(fetch_divi.list_cached(cache), ["4.9.0", "4.27.10"])
        with tempfile.TemporaryDirectory() as cache, \
                mock.patch.dict(os.environ, {"PP_DIVI_CACHE": cache}):
            _seed_cached(cache, "4.1.0")
            self.assertEqual(fetch_divi.list_cached(), ["4.1.0"])

    def test_newest_cached_none_when_empty(self):
        with tempfile.TemporaryDirectory() as cache:
            self.assertIsNone(fetch_divi.newest_cached(cache))

    def test_cache_root_honours_env_override(self):
        with mock.patch.dict(os.environ, {"PP_CACHE_DIR": "/tmp/pp-test-cache-root"}, clear=False):
            self.assertEqual(fetch_divi.cache_root(), Path("/tmp/pp-test-cache-root"))


class EnsureDiviTest(unittest.TestCase):
    def test_cached_version_returns_without_any_http_call(self):
        with tempfile.TemporaryDirectory() as cache:
            theme = _seed_cached(cache, "4.27.9")
            # No ET_* creds, and PP_ET_ENDPOINT points at an address that refuses connections: any
            # attempt to reach the network would raise, proving the cached path never calls out.
            with mock.patch.dict(os.environ, {"PP_ET_ENDPOINT": "http://127.0.0.1:1/"}, clear=True):
                result = fetch_divi.ensure_divi("4.27.9", cache)
            self.assertEqual(result, theme)

    def test_uncached_version_downloads_and_unpacks(self):
        handler = _make_handler(dl_body=_zip_bytes("1.2.3"))
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache:
            env = {"ET_USERNAME": "someone", "ET_API_KEY": "secretkey", "PP_ET_ENDPOINT": base}
            with mock.patch.dict(os.environ, env, clear=True):
                result = fetch_divi.ensure_divi("1.2.3", cache)
            self.assertEqual(result, Path(cache) / "Divi-1.2.3" / "Divi")
            self.assertTrue((result / "style.css").exists())
            self.assertIn("Version: 1.2.3", (result / "style.css").read_text())

    def test_text_error_body_raises_fetcherror_without_credentials(self):
        handler = _make_handler(dl_status=200, dl_body=b"API key is not valid", dl_ctype="text/html")
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache:
            env = {"ET_USERNAME": "someone", "ET_API_KEY": "secretkey", "PP_ET_ENDPOINT": base}
            with mock.patch.dict(os.environ, env, clear=True):
                with self.assertRaises(FetchError) as ctx:
                    fetch_divi.ensure_divi("1.2.3", cache)
            msg = str(ctx.exception)
            self.assertNotIn("someone", msg)
            self.assertNotIn("secretkey", msg)

    def test_403_and_429_raise_distinct_messages(self):
        for status in (403, 429):
            handler = _make_handler(dl_status=status, dl_body=b"denied", dl_ctype="text/xml")
            with _server(handler) as base, tempfile.TemporaryDirectory() as cache:
                env = {"ET_USERNAME": "someone", "ET_API_KEY": "secretkey", "PP_ET_ENDPOINT": base}
                with mock.patch.dict(os.environ, env, clear=True):
                    with self.assertRaises(FetchError) as ctx:
                        fetch_divi.ensure_divi("1.2.3", cache)
                self.assertIn(str(status), str(ctx.exception))

    def test_403_message_differs_from_429_message(self):
        messages = {}
        for status in (403, 429):
            handler = _make_handler(dl_status=status, dl_body=b"denied", dl_ctype="text/xml")
            with _server(handler) as base, tempfile.TemporaryDirectory() as cache:
                env = {"ET_USERNAME": "someone", "ET_API_KEY": "secretkey", "PP_ET_ENDPOINT": base}
                with mock.patch.dict(os.environ, env, clear=True):
                    with self.assertRaises(FetchError) as ctx:
                        fetch_divi.ensure_divi("1.2.3", cache)
                messages[status] = str(ctx.exception)
        self.assertNotEqual(messages[403], messages[429])

    def test_missing_credentials_raise_fetcherror(self):
        with tempfile.TemporaryDirectory() as cache:
            with mock.patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(FetchError):
                    fetch_divi.ensure_divi("1.2.3", cache)


class RedactionTest(unittest.TestCase):
    """Security regression: never redact by string-matching credentials in an already-encoded URL.
    An email-style username or a key containing '+'/'/' must not leak, raw or percent-encoded."""

    def test_special_character_credentials_never_leak(self):
        username, api_key = "someone@example.com", "abc+def/123"
        handler = _make_handler(status_body=b'a:1:{s:6:"status";s:13:"not_available"}')
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache:
            env = {"ET_USERNAME": username, "ET_API_KEY": api_key, "PP_ET_ENDPOINT": base}
            with mock.patch.dict(os.environ, env, clear=True):
                with self.assertRaises(FetchError) as ctx:
                    fetch_divi.ensure_divi("9.9.9", cache)
        msg = str(ctx.exception)
        self.assertNotIn(username, msg)
        self.assertNotIn(api_key, msg)
        self.assertNotIn(urllib.parse.quote(username, safe=""), msg)
        self.assertNotIn(urllib.parse.quote(api_key, safe=""), msg)
        self.assertNotIn(urllib.parse.quote_plus(username), msg)
        self.assertNotIn(urllib.parse.quote_plus(api_key), msg)
        # The placeholder appears (percent-encoded, like the rest of the query string) - proof the
        # redaction path actually engaged rather than, say, the URL being omitted entirely.
        self.assertIn(urllib.parse.quote("<ET_USERNAME>", safe=""), msg)
        self.assertIn(urllib.parse.quote("<API_KEY>", safe=""), msg)

# A credential that straddles the 160-byte snippet boundary: truncating before redacting would
# leave a partial key ("SECRETKEY1") that no longer matches the full key and so escapes redaction.
STRADDLE_KEY = "SECRETKEY1234567890"
STRADDLE_BODY = (b"x" * 150) + STRADDLE_KEY.encode() + b" is not valid"


class SnippetRedactionTest(unittest.TestCase):
    def test_python_redacts_before_truncating(self):
        handler = _make_handler(dl_status=200, dl_body=STRADDLE_BODY, dl_ctype="text/html")
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache:
            env = {"ET_USERNAME": "someone", "ET_API_KEY": STRADDLE_KEY, "PP_ET_ENDPOINT": base}
            with mock.patch.dict(os.environ, env, clear=True):
                with self.assertRaises(FetchError) as ctx:
                    fetch_divi.ensure_divi("1.2.3", cache)
        msg = str(ctx.exception)
        self.assertNotIn(STRADDLE_KEY[:6], msg)
        self.assertIn("<API_KEY>", msg)

    @unittest.skipUnless(shutil.which("node"), "node not installed")
    def test_node_redacts_before_truncating(self):
        handler = _make_handler(dl_status=200, dl_body=STRADDLE_BODY, dl_ctype="text/html")
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache:
            script = (f"import({FETCH_MJS.as_uri()!r}).then(m => m.ensureDivi('1.2.3', {cache!r}, () => {{}}))"
                      ".catch(e => { console.error(e.message); process.exit(1); });")
            env = dict(os.environ, ET_USERNAME="someone", ET_API_KEY=STRADDLE_KEY, PP_ET_ENDPOINT=base)
            proc = subprocess.run(["node", "--input-type=module", "-e", script],
                                  capture_output=True, text=True, timeout=30, env=env)
        out = proc.stdout + proc.stderr
        self.assertIn("download failed", out)
        self.assertNotIn(STRADDLE_KEY[:6], out)
        self.assertIn("<API_KEY>", out)


class KeysFileCredentialsTest(unittest.TestCase):
    """Elegant Themes credentials from a keys.json `elegant_themes` section (via --keys / keys_path),
    used when ET_USERNAME/ET_API_KEY aren't set. Mirrors the existing fake-ET-server test style."""

    def _write_keys_file(self, tmp, et):
        path = Path(tmp) / "keys.json"
        path.write_text(json.dumps({"elegant_themes": et}))
        return path

    def _recording_handler(self, dl_body):
        received = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                received.append(self.path)
                if "api_downloads.php" in self.path:
                    body, code, ctype = dl_body, 200, "application/zip"
                else:
                    body, code, ctype = AVAILABLE, 200, "text/html"
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_a):
                pass

        return Handler, received

    def test_ensure_divi_uses_keys_file_credentials_reaching_fake_server(self):
        handler, received = self._recording_handler(_zip_bytes("2.0.0"))
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache, \
                tempfile.TemporaryDirectory() as keysdir:
            keys_file = self._write_keys_file(keysdir, {"username": "fileuser", "api_key": "filesecretkey"})
            with mock.patch.dict(os.environ, {"PP_ET_ENDPOINT": base}, clear=True):
                result = fetch_divi.ensure_divi("2.0.0", cache, keys_path=keys_file)
            self.assertEqual(result, Path(cache) / "Divi-2.0.0" / "Divi")
        self.assertTrue(received, "fake server never received a request")
        self.assertTrue(any("fileuser" in p for p in received), received)

    def test_no_credentials_error_mentions_keys_json(self):
        with tempfile.TemporaryDirectory() as cache:
            with mock.patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(FetchError) as ctx:
                    fetch_divi.ensure_divi("1.2.3", cache, keys_path=None)
        msg = str(ctx.exception)
        self.assertIn("ET_USERNAME", msg)
        self.assertIn("elegant_themes", msg)

    def test_cli_keys_flag_with_no_env_reaches_server_without_leaking(self):
        handler, received = self._recording_handler(_zip_bytes("2.0.1"))
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache, \
                tempfile.TemporaryDirectory() as keysdir:
            keys_file = self._write_keys_file(keysdir, {"username": "fileuser2", "api_key": "sup3r-secret-key"})
            env = {"PP_ET_ENDPOINT": base, "PP_CACHE_DIR": cache}
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
                rc = fetch_divi.main(["--keys", str(keys_file), "2.0.1"])
        self.assertEqual(rc, 0, err.getvalue())
        self.assertTrue(any("fileuser2" in p for p in received), received)
        for stream in (out.getvalue(), err.getvalue()):
            self.assertNotIn("sup3r-secret-key", stream)
            self.assertNotIn(urllib.parse.quote("sup3r-secret-key", safe=""), stream)

    def test_cli_keys_flag_error_response_does_not_leak(self):
        handler = _make_handler(dl_status=200, dl_body=b"API key is not valid", dl_ctype="text/html")
        with _server(handler) as base, tempfile.TemporaryDirectory() as cache, \
                tempfile.TemporaryDirectory() as keysdir:
            keys_file = self._write_keys_file(keysdir, {"username": "fileuser3", "api_key": "another-secret-99"})
            env = {"PP_ET_ENDPOINT": base, "PP_CACHE_DIR": cache}
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.dict(os.environ, env, clear=True), \
                    mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
                rc = fetch_divi.main(["--keys", str(keys_file), "1.2.3"])
        self.assertEqual(rc, 1)
        for stream in (out.getvalue(), err.getvalue()):
            self.assertNotIn("another-secret-99", stream)
            self.assertNotIn(urllib.parse.quote("another-secret-99", safe=""), stream)
            self.assertNotIn("fileuser3", stream)

    def test_cli_keys_flag_missing_path_is_clean_error(self):
        with tempfile.TemporaryDirectory() as cache, tempfile.TemporaryDirectory() as keysdir:
            missing = str(Path(keysdir) / "nope.json")
            env = {"PP_CACHE_DIR": cache}
            err = io.StringIO()
            with mock.patch.dict(os.environ, env, clear=True), mock.patch("sys.stderr", err):
                rc = fetch_divi.main(["--keys", missing, "1.2.3"])
        self.assertEqual(rc, 1)
        self.assertIn(missing, err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())


class VersionArgTest(unittest.TestCase):
    def test_rejects_non_version_arguments_before_any_network_call(self):
        calls = []

        class Counting(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                calls.append(self.path)
                self.send_response(500)
                self.end_headers()

            def log_message(self, *_a):
                pass

        for bad in ("--help", "-v", "4.x", "../4.27.9", "4.27.9; rm", ""):
            with self.subTest(bad=bad), _server(Counting) as base, tempfile.TemporaryDirectory() as cache:
                env = {"ET_USERNAME": "someone", "ET_API_KEY": "secretkey", "PP_ET_ENDPOINT": base,
                       "PP_CACHE_DIR": cache}
                err = io.StringIO()
                with mock.patch.dict(os.environ, env, clear=True), mock.patch("sys.stderr", err):
                    self.assertEqual(fetch_divi.main([bad]), 2)
                self.assertIn("latest", err.getvalue())
        self.assertEqual(calls, [])

    def test_accepts_latest_and_dotted_versions(self):
        for good in ("latest", "4.27.9", "4.27", "10.0.1.2"):
            self.assertTrue(fetch_divi.valid_version_arg(good), good)


def _latest_handler(received, version="5.13.1"):
    """A fake check_theme_updates endpoint (POST api.php) recording each form body it gets."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            received.append(urllib.parse.parse_qs(self.rfile.read(n).decode()))
            body = ('a:1:{s:4:"Divi";a:2:{s:11:"new_version";s:%d:"%s";s:7:"package";s:3:"zip";}}'
                    % (len(version), version)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    return Handler


class MajorAwareCacheTest(unittest.TestCase):
    """Version selection is per Divi major: a cached Divi 5 must never be picked for Divi 4 content."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cache = self.tmp.name
        for v in ("4.27.3", "4.27.10", "5.0.0", "5.13.1"):
            _seed_cached(self.cache, v)

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_cached_filters_by_major(self):
        self.assertEqual(fetch_divi.list_cached(self.cache, major=4), ["4.27.3", "4.27.10"])
        self.assertEqual(fetch_divi.list_cached(self.cache, major=5), ["5.0.0", "5.13.1"])
        self.assertEqual(fetch_divi.list_cached(self.cache, major=6), [])

    def test_newest_cached_of_major_4_ignores_a_newer_5(self):
        self.assertEqual(fetch_divi.newest_cached(self.cache, major=4), "4.27.10")
        self.assertEqual(fetch_divi.newest_cached(self.cache, major=5), "5.13.1")

    def test_latest_aliases_are_valid_version_args(self):
        for good in ("latest4", "latest5"):
            self.assertTrue(fetch_divi.valid_version_arg(good), good)
        self.assertFalse(fetch_divi.valid_version_arg("latest6"))

    def test_latest_major_of_alias(self):
        self.assertEqual(fetch_divi.latest_major("latest"), 4)
        self.assertEqual(fetch_divi.latest_major("latest4"), 4)
        self.assertEqual(fetch_divi.latest_major("latest5"), 5)
        self.assertIsNone(fetch_divi.latest_major("5.13.1"))


class LatestVersionTest(unittest.TestCase):
    """`latest` asks for the Divi 4 line exactly as before; `latest5` adds divi_5=on (what Divi 5's own
    updater sends, et_core_maybe_add_divi5_api_parameter) and reports an installed 5.0.0."""

    def _latest(self, major):
        received = []
        with _server(_latest_handler(received)) as base:
            env = {"ET_USERNAME": "someone", "ET_API_KEY": "secretkey", "PP_ET_ENDPOINT": base}
            with mock.patch.dict(os.environ, env, clear=True):
                got = fetch_divi.latest_version(major=major) if major else fetch_divi.latest_version()
        return got, received[0]

    def test_default_latest_asks_for_divi_4_without_divi_5(self):
        got, form = self._latest(None)
        self.assertEqual(got, "5.13.1")  # whatever the server answers
        self.assertEqual(form["installed_themes[Divi]"], ["4.0.0"])
        self.assertNotIn("divi_5", form)

    def test_latest_5_sends_divi_5_on(self):
        _got, form = self._latest(5)
        self.assertEqual(form["divi_5"], ["on"])
        self.assertEqual(form["installed_themes[Divi]"], ["5.0.0"])

    def test_ensure_divi_latest5_resolves_through_the_divi_5_line(self):
        received = []
        with _server(_latest_handler(received)) as base, tempfile.TemporaryDirectory() as cache:
            _seed_cached(cache, "5.13.1")
            env = {"ET_USERNAME": "someone", "ET_API_KEY": "secretkey", "PP_ET_ENDPOINT": base}
            with mock.patch.dict(os.environ, env, clear=True):
                got = fetch_divi.ensure_divi("latest5", cache)
        self.assertEqual(got, Path(cache) / "Divi-5.13.1" / "Divi")
        self.assertEqual(received[0]["divi_5"], ["on"])


@unittest.skipUnless(shutil.which("node"), "node not installed")
class NodeMajorAwareTest(unittest.TestCase):
    """fetch-divi.mjs: the same per-major selection preview.mjs uses (listCachedDivi/newestCached/contentMajor/
    resolveDiviVersion) and latest5 -> divi_5=on."""

    def node(self, expr, env=None):
        script = f"import({FETCH_MJS.as_uri()!r}).then(async m => console.log(JSON.stringify(await ({expr}))));"
        proc = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True,
                              timeout=30, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout), proc.stderr

    def test_newest_cached_per_major(self):
        with tempfile.TemporaryDirectory() as cache:
            for v in ("4.27.3", "4.27.10", "5.13.1"):
                _seed_cached(cache, v)
            got, _ = self.node(f"[m.newestCached({cache!r}, 4), m.newestCached({cache!r}, 5), "
                               f"m.listCachedDivi({cache!r})]")
        self.assertEqual(got, ["4.27.10", "5.13.1", ["4.27.3", "4.27.10", "5.13.1"]])

    def test_content_major(self):
        got, _ = self.node("[m.contentMajor('<!-- wp:divi/placeholder --><!-- /wp:divi/placeholder -->'), "
                           "m.contentMajor('[et_pb_section][/et_pb_section]'), m.contentMajor('')]")
        self.assertEqual(got, [5, 4, 4])

    def test_resolve_divi_version_is_major_aware(self):
        with tempfile.TemporaryDirectory() as cache:
            for v in ("4.27.10", "5.13.1"):
                _seed_cached(cache, v)
            tokens = Path(cache) / "t.json"
            tokens.write_text(json.dumps({"site": {"divi_version": ""}}))
            got, err = self.node(
                f"[m.resolveDiviVersion({{}}, {cache!r}, 4), m.resolveDiviVersion({{}}, {cache!r}, 5), "
                f"m.resolveDiviVersion({{divi: '4.20.0'}}, {cache!r}, 5), "
                f"m.resolveDiviVersion({{tokens: {str(tokens)!r}}}, {cache!r}, 5), "
                f"m.resolveDiviVersion({{}}, {str(Path(cache) / 'none')!r}, 5), "
                f"m.resolveDiviVersion({{}}, {str(Path(cache) / 'none')!r}, 4)]")
        self.assertEqual(got, ["4.27.10", "5.13.1", "4.20.0", "5.13.1", "latest5", "latest"])
        self.assertIn("5.13.1", err)  # the empty-version note

    def test_latest5_sends_divi_5_on(self):
        received = []
        with _server(_latest_handler(received)) as base:
            env = {"PATH": os.environ["PATH"], "ET_USERNAME": "someone", "ET_API_KEY": "secretkey",
                   "PP_ET_ENDPOINT": base}
            got, _ = self.node("m.latestVersion(5)", env=env)
            got4, _ = self.node("m.latestVersion()", env=env)
        self.assertEqual(got, "5.13.1")
        self.assertEqual(received[0]["divi_5"], ["on"])
        self.assertEqual(received[0]["installed_themes[Divi]"], ["5.0.0"])
        self.assertNotIn("divi_5", received[1])
        self.assertEqual(received[1]["installed_themes[Divi]"], ["4.0.0"])


@unittest.skipUnless(shutil.which("node"), "node not installed")
class PlaygroundEnvTest(unittest.TestCase):
    def test_secrets_are_stripped_from_the_playground_environment(self):
        script = (f"import({FETCH_MJS.as_uri()!r}).then(m => console.log(JSON.stringify(m.playgroundEnv({{"
                  "PATH: '/bin', HOME: '/h', ET_USERNAME: 'u', ET_API_KEY: 'k', WP_APP_PASSWORD: 'p'}))));")
        proc = subprocess.run(["node", "--input-type=module", "-e", script], capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"PATH": "/bin", "HOME": "/h"})

    def test_preview_mjs_spawns_playground_with_scrubbed_env(self):
        text = (SCRIPTS / "preview" / "preview.mjs").read_text()
        spawn_line = next(line for line in text.splitlines() if "spawn(win ? 'npx.cmd' : 'npx'" in line)
        self.assertIn("env: playgroundEnv()", spawn_line)


if __name__ == "__main__":
    unittest.main()
