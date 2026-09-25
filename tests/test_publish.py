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

from _paths import FIXTURES, SCRIPTS, WP_LOCAL, live_only

PASSWORD = "abcd EFGH ijkl MNOP qrst UVWX"
GOOD = (FIXTURES / "valid" / "handwritten-landing.txt").read_text()


class FakeWP(BaseHTTPRequestHandler):
    calls = []
    page_status = "draft"
    page_raw = GOOD
    auth_user = "editor"
    auth_password = PASSWORD

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
        expected = "Basic " + base64.b64encode(f"{FakeWP.auth_user}:{FakeWP.auth_password}".encode()).decode()
        return self.headers.get("Authorization") == expected, body

    def do_GET(self):
        ok, _ = self._record()
        if not ok:
            return self._reply(401, {"code": "rest_not_logged_in", "message": "You are not currently logged in."})
        if self.path.startswith("/wp-json/wp/v2/pages/101"):
            return self._reply(200, {"id": 101, "status": FakeWP.page_status,
                                     "link": "http://fake/?page_id=101", "content": {"raw": FakeWP.page_raw}})
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
            status = json.loads(body or b"{}").get("status", FakeWP.page_status)
            return self._reply(200, {"id": 101, "status": status, "link": f"http://127.0.0.1:{port}/?page_id=101"})
        self._reply(404, {"code": "rest_no_route", "message": "No route"})


class PublishFakeServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeWP)
        cls.site = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        # An always-present, empty keys file, used as the default DIVI_KEYS_FILE for every run_cli()
        # call below so tests never fall through to the real ~/.config/divi-page-builder/keys.json
        # (an *explicit* --keys always overrides this, and an explicit env value beats it too).
        fd, cls.empty_keys_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        Path(cls.empty_keys_path).write_text(json.dumps({"keys": []}))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        os.unlink(cls.empty_keys_path)

    def setUp(self):
        FakeWP.calls.clear()
        FakeWP.page_status = "draft"
        FakeWP.page_raw = GOOD
        FakeWP.auth_user = "editor"
        FakeWP.auth_password = PASSWORD

    def run_cli(self, *args, password=PASSWORD, keys_file=None):
        env = dict(os.environ)
        if password is None:
            env.pop("WP_APP_PASSWORD", None)
        else:
            env["WP_APP_PASSWORD"] = password
        # Explicit --keys (a CLI arg in *args) always wins over this env default, so tests that pass
        # their own --keys are unaffected; this only keeps the *implicit* default path isolated from
        # the real ~/.config/divi-page-builder/keys.json for every other test.
        env["DIVI_KEYS_FILE"] = keys_file or self.empty_keys_path
        return subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), *args], capture_output=True, text=True, env=env)

    def _write_keys(self, entries):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump({"keys": entries}, f)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

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
        get_call, post_call = FakeWP.calls
        self.assertEqual(get_call["method"], "GET")
        self.assertEqual(post_call["path"], "/wp-json/wp/v2/pages/101")
        self.assertEqual(json.loads(post_call["body"])["status"], "draft")

    def test_draft_refuses_to_unpublish_a_live_page(self):
        FakeWP.page_status = "publish"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T", "--page-id", "101")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 1)
        self.assertFalse(any(c["method"] == "POST" for c in FakeWP.calls))
        self.assertIn("101", proc.stderr)
        self.assertIn("offline", proc.stderr)
        self.assertIn("publish.py publish --page-id 101 --content", proc.stderr)

    def test_draft_allows_updating_a_pending_page(self):
        FakeWP.page_status = "pending"
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T", "--page-id", "101")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(any(c["method"] == "POST" for c in FakeWP.calls))

    def test_page_fields_cannot_set_status(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T",
                             "--page-fields", '{"status":"publish"}')
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--page-fields", proc.stderr)
        self.assertIn("status", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_page_fields_cannot_set_content_or_meta(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        for bad in ('{"content":"x"}', '{"meta":{"_et_pb_use_builder":"off"}}'):
            proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T",
                                 "--page-fields", bad)
            self.assertEqual(proc.returncode, 2, proc.stderr)
            self.assertEqual(FakeWP.calls, [])
        os.unlink(f.name)

    def test_page_fields_template_still_works(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T",
                             "--page-fields", '{"template":"page-template-blank.php"}')
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        (create,) = FakeWP.calls
        sent = json.loads(create["body"])
        self.assertEqual(sent["template"], "page-template-blank.php")

    def test_page_fields_must_be_a_json_object(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--site", self.site, "--user", "editor", "--title", "T",
                             "--page-fields", "[1,2]")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_draft_checks_all_local_images_before_uploading_any(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "hero.jpg").write_bytes(b"\xff\xd8\xff fake jpeg")
            page = Path(tmp) / "page.txt"
            source = GOOD.replace("https://client.example/wp-content/uploads/2026/09/plumber.jpg", "./hero.jpg")
            source = source.replace('admin_label="Hero" _builder_version',
                                    'admin_label="Hero" background_image="./missing.jpg" _builder_version')
            page.write_text(source)
            proc = self.run_cli("draft", str(page), "--site", self.site, "--user", "editor", "--title", "Test Page")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual([c for c in FakeWP.calls if c["path"] == "/wp-json/wp/v2/media"], [])

    def test_publish_with_content_requires_yes(self):
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                             "--content", str(FIXTURES / "valid" / "handwritten-landing.txt"))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(FakeWP.calls, [])

    def test_publish_with_content_sends_content_and_status_in_one_request(self):
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                             "--content", str(FIXTURES / "valid" / "handwritten-landing.txt"), "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        get_call, call = FakeWP.calls
        self.assertEqual(get_call["method"], "GET")
        self.assertEqual(call["method"], "POST")
        self.assertEqual(call["path"], "/wp-json/wp/v2/pages/101")
        body = json.loads(call["body"])
        self.assertEqual(body["status"], "publish")
        self.assertEqual(body["content"], GOOD)
        self.assertEqual(body["meta"], {"_et_pb_use_builder": "on"})

    # --- C1: publish must not change a page's visibility ---------------------------------------
    def _publish_content(self, *extra):
        return self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                            "--content", str(FIXTURES / "valid" / "handwritten-landing.txt"), "--yes", *extra)

    def _sent_post(self):
        posts = [c for c in FakeWP.calls if c["method"] == "POST"]
        self.assertEqual(len(posts), 1, FakeWP.calls)
        return json.loads(posts[0]["body"])

    def test_publish_content_keeps_private_page_private(self):
        FakeWP.page_status = "private"
        proc = self._publish_content()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = self._sent_post()
        self.assertNotIn("status", body)
        self.assertEqual(body["content"], GOOD)
        self.assertEqual(body["meta"], {"_et_pb_use_builder": "on"})
        self.assertEqual(json.loads(proc.stdout)["status"], "private")

    def test_publish_content_keeps_scheduled_page_scheduled(self):
        FakeWP.page_status = "future"
        proc = self._publish_content()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("status", self._sent_post())
        self.assertEqual(json.loads(proc.stdout)["status"], "future")

    def test_publish_content_keeps_published_page_published(self):
        FakeWP.page_status = "publish"
        proc = self._publish_content()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self._sent_post().get("status", "publish"), "publish")
        self.assertEqual(json.loads(proc.stdout)["status"], "publish")

    def test_publish_status_flag_explicitly_makes_private_page_public(self):
        FakeWP.page_status = "private"
        proc = self._publish_content("--status", "publish")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self._sent_post()["status"], "publish")

    def test_publish_without_content_refuses_to_change_private_visibility(self):
        FakeWP.page_status = "private"
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("--status publish", proc.stderr)
        self.assertFalse(any(c["method"] == "POST" for c in FakeWP.calls))

    # --- I1: draft/publish validate against a baseline ------------------------------------------
    LEGACY = GOOD.replace('[et_pb_text _builder_version="4.27.9"', '[et_pb_text use_border_color="on" _builder_version="4.27.9"', 1)
    NEW_ERROR = LEGACY.replace('[et_pb_button button_text=', '[et_pb_button colour="red" button_text=', 1)

    def _page_file(self, text):
        f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
        f.write(text)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_legacy_fixture_really_has_a_preexisting_unknown_attr(self):
        self.assertNotEqual(self.LEGACY, GOOD)
        self.assertNotEqual(self.NEW_ERROR, self.LEGACY)

    def test_draft_page_id_uses_current_content_as_baseline(self):
        FakeWP.page_raw = self.LEGACY
        proc = self.run_cli("draft", self._page_file(self.LEGACY), "--site", self.site, "--user", "editor",
                            "--title", "T", "--page-id", "101")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        get_call = FakeWP.calls[0]
        self.assertEqual(get_call["method"], "GET")
        self.assertIn("context=edit", get_call["path"])

    def test_draft_page_id_baseline_still_blocks_new_errors(self):
        FakeWP.page_raw = self.LEGACY
        proc = self.run_cli("draft", self._page_file(self.NEW_ERROR), "--site", self.site, "--user", "editor",
                            "--title", "T", "--page-id", "101")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("colour", proc.stderr)
        self.assertNotIn("use_border_color", proc.stderr)
        self.assertFalse(any(c["method"] == "POST" for c in FakeWP.calls))

    def test_draft_explicit_baseline_file(self):
        proc = self.run_cli("draft", self._page_file(self.LEGACY), "--site", self.site, "--user", "editor",
                            "--title", "T", "--baseline", self._page_file(self.LEGACY))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        proc = self.run_cli("draft", self._page_file(self.LEGACY), "--site", self.site, "--user", "editor",
                            "--title", "T")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("use_border_color", proc.stderr)

    def test_publish_content_uses_current_content_as_baseline(self):
        FakeWP.page_raw = self.LEGACY
        FakeWP.page_status = "publish"
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                            "--content", self._page_file(self.LEGACY), "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                            "--content", self._page_file(self.NEW_ERROR), "--yes")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("colour", proc.stderr)

    def test_publish_content_explicit_baseline_file(self):
        FakeWP.page_raw = GOOD
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                            "--content", self._page_file(self.LEGACY), "--baseline", self._page_file(self.LEGACY),
                            "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    # --- M6: Content-Disposition for non-Latin-1 filenames --------------------------------------
    def test_media_upload_non_latin1_filename(self):
        with tempfile.TemporaryDirectory() as tmp:
            img = Path(tmp) / "café-日本.jpg"
            img.write_bytes(b"\xff\xd8\xff fake jpeg")
            proc = self.run_cli("media", "--site", self.site, "--user", "editor", str(img), "--alt", "x")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        media = FakeWP.calls[0]
        disp = media["headers"]["Content-Disposition"]
        disp.encode("ascii")
        self.assertIn("filename*=UTF-8''caf%C3%A9-%E6%97%A5%E6%9C%AC.jpg", disp)
        self.assertRegex(disp, r'filename="[ -~]+\.jpg"')

    def test_publish_with_content_refuses_invalid_page(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write('[et_pb_section][et_pb_row][et_pb_column type="4_4"][et_pb_text colour="red"]x[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]')
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                             "--content", f.name, "--yes")
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 1)
        # only the read of the current page (status + baseline); nothing is written
        self.assertEqual([c["method"] for c in FakeWP.calls], ["GET"])

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

    # --- keys.json multi-site credentials ---------------------------------------------------
    def test_draft_with_key_uses_keys_file_credentials(self):
        key_user, key_password = "keyuser", "aaaa BBBB cccc DDDD eeee FFFF"
        keys_file = self._write_keys([{"name": "Test Site", "site": self.site, "user": key_user, "key": key_password}])
        FakeWP.auth_user, FakeWP.auth_password = key_user, key_password
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--key", "Test Site", "--keys", keys_file, "--title", "T",
                             password=None)
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(any(c["method"] == "POST" for c in FakeWP.calls))
        for stream in (proc.stdout, proc.stderr):
            self.assertNotIn(key_password, stream)

    def test_keys_command_lists_without_secrets(self):
        secret_a, secret_b = "aaaa BBBB cccc DDDD eeee FFFF", "zzzz YYYY xxxx WWWW vvvv UUUU"
        keys_file = self._write_keys([
            {"name": "Test Key Local site", "site": "http://divi-test.local", "user": "user", "key": secret_a},
            {"name": "Client A", "site": "https://client-a.com", "user": "seo-bot", "key": secret_b},
        ])
        proc = self.run_cli("keys", "--keys", keys_file, password=None)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"keys": [
            {"name": "Test Key Local site", "site": "http://divi-test.local", "user": "user"},
            {"name": "Client A", "site": "https://client-a.com", "user": "seo-bot"},
        ]})
        for stream in (proc.stdout, proc.stderr):
            self.assertNotIn(secret_a, stream)
            self.assertNotIn(secret_b, stream)

    def test_keys_command_default_missing_file_hint(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home)
            env.pop("DIVI_KEYS_FILE", None)
            proc = subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), "keys"],
                                  capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {"keys": []})
        self.assertIn(".config/divi-page-builder/keys.json", proc.stderr)

    def test_key_not_found_exits_2_without_leaking(self):
        secret = "supersecretkeyvalue"
        keys_file = self._write_keys([{"name": "Client A", "site": "https://client-a.com", "user": "seo-bot", "key": secret}])
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--key", "Nonexistent", "--keys", keys_file, "--title", "T",
                             password=None)
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Client A", proc.stderr)
        self.assertEqual(FakeWP.calls, [])
        for stream in (proc.stdout, proc.stderr):
            self.assertNotIn(secret, stream)

    def test_key_with_conflicting_user_is_keys_error(self):
        secret = "aaaa BBBB cccc DDDD eeee FFFF"
        keys_file = self._write_keys([{"name": "Client A", "site": "https://client-a.com", "user": "seo-bot", "key": secret}])
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write(GOOD)
        proc = self.run_cli("draft", f.name, "--key", "Client A", "--user", "someone-else",
                             "--keys", keys_file, "--title", "T", password=None)
        os.unlink(f.name)
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertEqual(FakeWP.calls, [])
        for stream in (proc.stdout, proc.stderr):
            self.assertNotIn(secret, stream)

    def test_keys_command_explicit_missing_path_exits_2(self):
        missing = str(Path(tempfile.mkdtemp()) / "nonexistent.json")
        proc = self.run_cli("keys", "--keys", missing, password=None)
        self.assertEqual(proc.returncode, 2)
        self.assertNotIn("Traceback", proc.stderr)
        self.assertIn(missing, proc.stderr)
        self.assertIn("publish.py:", proc.stderr)


@live_only
class PublishLiveTest(unittest.TestCase):
    """Round-trip against divi-test.local; opt-in with PP_LIVE_TESTS=1, and skipped when the site is unavailable."""

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
