"""Tests for the stdlib port of scripts/preview/fetch-divi.mjs.

Uses a fake HTTP server (PP_ET_ENDPOINT) so no real network access or credentials are needed.
"""
import http.server
import io
import os
import tempfile
import threading
import unittest
import urllib.parse
import zipfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from _paths import SCRIPTS  # noqa: F401  (puts Skill scripts on sys.path)

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


if __name__ == "__main__":
    unittest.main()
