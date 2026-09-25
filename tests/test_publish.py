import base64
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from _paths import FIXTURES, SCRIPTS, WP_LOCAL

PASSWORD = "abcd EFGH ijkl MNOP qrst UVWX"
GOOD = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()


class FakeWP(BaseHTTPRequestHandler):
    calls = []

    def log_message(self, *args):
        pass

    def _reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _record(self):
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""
        FakeWP.calls.append({"method": self.command, "path": self.path, "headers": dict(self.headers), "body": body})
        expected = "Basic " + base64.b64encode(f"editor:{PASSWORD}".encode()).decode()
        return self.headers.get("Authorization") == expected, body

    def do_GET(self):
        ok, _ = self._record()
        if not ok:
            return self._reply(401, {"code": "rest_not_logged_in", "message": "You are not currently logged in."})
        if self.path.startswith("/wp-json/wp/v2/pages/101"):
            return self._reply(200, {"id": 101, "link": "http://fake/?page_id=101", "content": {"raw": GOOD}})
        self._reply(404, {"code": "rest_no_route", "message": "No route"})

    def do_POST(self):
        ok, body = self._record()
        if not ok:
            return self._reply(401, {"code": "rest_not_logged_in", "message": "You are not currently logged in."})
        port = self.server.server_address[1]
        if self.path == "/wp-json/wp/v2/media":
            return self._reply(201, {"id": 55, "source_url": f"http://127.0.0.1:{port}/wp-content/uploads/hero.jpg"})
        if self.path == "/wp-json/wp/v2/media/55":
            return self._reply(200, {"id": 55})
        if self.path == "/wp-json/wp/v2/pages":
            return self._reply(201, {"id": 101, "status": "draft", "link": f"http://127.0.0.1:{port}/?page_id=101"})
        if self.path == "/wp-json/wp/v2/pages/101":
            status = json.loads(body or b"{}").get("status", "draft")
            return self._reply(200, {"id": 101, "status": status, "link": f"http://127.0.0.1:{port}/?page_id=101"})
        self._reply(404, {"code": "rest_no_route", "message": "No route"})


class PublishFakeServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeWP)
        cls.site = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        FakeWP.calls.clear()

    def run_cli(self, *args, password=PASSWORD):
        env = dict(os.environ, WP_APP_PASSWORD=password)
        return subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), *args], capture_output=True, text=True, env=env)

    def test_draft_uploads_local_images_and_creates_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "hero.jpg").write_bytes(b"\xff\xd8\xff fake jpeg")
            page = Path(tmp) / "page.txt"
            page.write_text(GOOD.replace("https://client.example/wp-content/uploads/2026/09/plumber.jpg", "./hero.jpg"))
            proc = self.run_cli("draft", str(page), "--site", self.site, "--user", "editor", "--title", "Test Page")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertEqual(out["id"], 101)
        self.assertEqual(out["status"], "draft")
        self.assertIn("preview=true", out["preview_url"])
        self.assertEqual(len(out["uploaded"]), 1)
        media, alt, create = FakeWP.calls
        self.assertEqual(media["path"], "/wp-json/wp/v2/media")
        self.assertIn('filename="hero.jpg"', media["headers"]["Content-Disposition"])
        self.assertEqual(json.loads(alt["body"])["alt_text"], "Plumber repairing a burst pipe")
        sent = json.loads(create["body"])
        self.assertEqual(sent["status"], "draft")
        self.assertEqual(sent["meta"], {"_et_pb_use_builder": "on"})
        self.assertIn("/wp-content/uploads/hero.jpg", sent["content"])
        self.assertNotIn("./hero.jpg", sent["content"])

    def test_draft_update_keeps_draft(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T", "--page-id", "101")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        (call,) = FakeWP.calls
        self.assertEqual(call["path"], "/wp-json/wp/v2/pages/101")
        self.assertEqual(json.loads(call["body"])["status"], "draft")

    def test_draft_refuses_invalid_page(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write('[et_pb_section][et_pb_row][et_pb_column type="4_4"][et_pb_text colour="red"]x[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]')
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("E_UNKNOWN_ATTR", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_publish_requires_yes(self):
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101")
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(FakeWP.calls, [])
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["status"], "publish")

    def test_fetch_writes_raw(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "original.txt"
            proc = self.run_cli("fetch", "--site", self.site, "--user", "editor", "--page-id", "101", "--out", str(out))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(out.read_text(), GOOD)

    def test_http_error_exit_2_without_leaking_password(self):
        proc = self.run_cli("fetch", "--site", self.site, "--user", "editor", "--page-id", "101", "--out", "/tmp/x.txt",
                            password="wrong pass")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("rest_not_logged_in", proc.stderr)
        for stream in (proc.stdout, proc.stderr):
            self.assertNotIn("wrong pass", stream)
            self.assertNotIn(PASSWORD, stream)

    def test_missing_password_is_usage_error(self):
        proc = self.run_cli("fetch", "--site", self.site, "--user", "editor", "--page-id", "101", "--out", "/tmp/x.txt",
                            password="")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("WP_APP_PASSWORD", proc.stderr)


class PublishLiveTest(unittest.TestCase):
    """Round-trip against divi-test.local; skipped when the local site is unavailable."""

    def wp(self, *args):
        out = subprocess.run([str(WP_LOCAL), *args], capture_output=True, text=True, timeout=120)
        if out.returncode != 0:
            raise unittest.SkipTest(f"local site unavailable: {out.stderr[-200:]}")
        return out.stdout.strip()

    def test_draft_roundtrip_on_local_site(self):
        user = self.wp("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        password = self.wp("user", "application-password", "create", user, "publish-test", "--porcelain")
        page_id = None
        try:
            env = dict(os.environ, WP_APP_PASSWORD=password)
            proc = subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), "draft", str(FIXTURES / "valid" / "handwritten-landing.txt"),
                                   "--site", "http://divi-test.local", "--user", user, "--title", "Plan Test: publish.py"],
                                  capture_output=True, text=True, env=env)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            page_id = json.loads(proc.stdout)["id"]
            self.assertEqual(self.wp("post", "get", str(page_id), "--field=post_status"), "draft")
            self.assertEqual(self.wp("post", "meta", "get", str(page_id), "_et_pb_use_builder"), "on")
            self.assertEqual(self.wp("post", "get", str(page_id), "--field=post_content"), GOOD.strip())
        finally:
            if page_id:
                self.wp("post", "delete", str(page_id), "--force")
            uuid = self.wp("user", "application-password", "list", user, "--name=publish-test", "--field=uuid")
            self.wp("user", "application-password", "delete", user, uuid)


if __name__ == "__main__":
    unittest.main()
