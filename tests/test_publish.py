import base64
import json
import os
import shutil
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
    # Divi version detection (divi_format.detect_site) fetches the theme's style.css and the home page without
    # auth; those fetches go to `probes`, never to `calls`, so the REST request sequences stay exact.
    probes = []
    divi_version = "4.27.9"   # None: style.css is a 404
    home_html = None          # None: the home page is a 404
    page_meta = None          # None: GET /pages/101 has no "meta" (the D4 fake's response, unchanged)
    page_link = None          # None: "http://fake/?page_id=101"
    page_html = None          # front-end HTML served for /?page_id=101 (None: 404)
    page_title = None         # title.raw in GET /pages/101 (None: no "title", the D4 fake's response)
    batch_echo = "on"         # _et_pb_use_builder echoed by the batch's second response (None: key absent)
    batch_statuses = (200, 200)
    batch_http_error = False  # the whole /batch/v1 request fails (400)
    readback_meta = None      # meta a GET shows after a batch content write (None: like the real site, no key)

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

    def _text(self, code, text):
        data = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=UTF-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _probe(self):
        FakeWP.probes.append(self.path)
        if self.path == "/wp-content/themes/Divi/style.css" and FakeWP.divi_version:
            return self._text(200, f"/*\nTheme Name: Divi\nVersion: {FakeWP.divi_version}\n*/\n")
        if self.path == "/" and FakeWP.home_html is not None:
            return self._text(200, FakeWP.home_html)
        if self.path == "/?page_id=101" and FakeWP.page_html is not None:
            return self._text(200, FakeWP.page_html)
        return self._text(404, "not found")

    def do_GET(self):
        if not self.path.startswith("/wp-json/"):
            return self._probe()
        ok, _ = self._record()
        if not ok:
            return self._reply(401, {"code": "rest_not_logged_in", "message": "You are not currently logged in."})
        if self.path.startswith("/wp-json/wp/v2/pages/101"):
            page = {"id": 101, "status": FakeWP.page_status,
                    "link": FakeWP.page_link or "http://fake/?page_id=101", "content": {"raw": FakeWP.page_raw}}
            if FakeWP.page_meta is not None:
                page["meta"] = FakeWP.page_meta
            if FakeWP.page_title is not None:
                page["title"] = {"raw": FakeWP.page_title, "rendered": FakeWP.page_title}
            return self._reply(200, page)
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
        if self.path == "/wp-json/batch/v1":
            if FakeWP.batch_http_error:
                return self._reply(400, {"code": "rest_invalid_param", "message": "Invalid parameter(s): requests"})
            responses = []
            for req, code in zip(json.loads(body)["requests"], FakeWP.batch_statuses):
                meta = {"footnotes": ""}
                if "meta" in req["body"] and FakeWP.batch_echo is not None:
                    meta["_et_pb_use_builder"] = FakeWP.batch_echo
                if "content" in req["body"]:
                    FakeWP.page_raw = req["body"]["content"]
                    if FakeWP.readback_meta is not None:
                        FakeWP.page_meta = FakeWP.readback_meta
                    elif FakeWP.page_meta is not None:
                        # like the real site: a GET of Divi 5 content can't show the (unregistered) key
                        FakeWP.page_meta = {"footnotes": ""}
                rbody = ({"id": 101, "status": "draft", "meta": meta} if code == 200
                         else {"code": "rest_invalid_param", "message": "Invalid parameter(s): content"})
                responses.append({"body": rbody, "status": code, "headers": {}})
            return self._reply(207, {"responses": responses})
        self._reply(404, {"code": "rest_no_route", "message": "No route"})


def _reset_fake():
    FakeWP.calls.clear()
    FakeWP.probes.clear()
    FakeWP.page_status = "draft"
    FakeWP.page_raw = GOOD
    FakeWP.auth_user = "editor"
    FakeWP.auth_password = PASSWORD
    FakeWP.divi_version = "4.27.9"
    FakeWP.home_html = None
    FakeWP.page_meta = None
    FakeWP.page_link = None
    FakeWP.page_html = None
    FakeWP.batch_echo = "on"
    FakeWP.batch_statuses = (200, 200)
    FakeWP.batch_http_error = False
    FakeWP.readback_meta = None
    FakeWP.page_title = None


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
        _reset_fake()

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
        ], "elegant_themes": {"configured": False}})
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
        self.assertEqual(json.loads(proc.stdout), {"keys": [], "elegant_themes": {"configured": False}})
        self.assertIn(".config/divi-page-builder/keys.json", proc.stderr)

    def test_keys_command_shows_elegant_themes_username_when_configured(self):
        keys_file = self._write_keys([])
        et_secret = "et-api-key-value-should-not-leak"
        data = json.loads(Path(keys_file).read_text())
        data["elegant_themes"] = {"username": "you@example.com", "api_key": et_secret}
        Path(keys_file).write_text(json.dumps(data))
        proc = self.run_cli("keys", "--keys", keys_file, password=None)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {
            "keys": [],
            "elegant_themes": {"username": "you@example.com", "configured": True},
        })
        for stream in (proc.stdout, proc.stderr):
            self.assertNotIn(et_secret, stream)

    def test_keys_command_elegant_themes_only_file(self):
        # A keys.json with only "elegant_themes" (no "keys" list at all) is valid.
        keys_file = Path(tempfile.NamedTemporaryFile(suffix=".json", delete=False).name)
        self.addCleanup(os.unlink, keys_file)
        et_secret = "another-et-secret"
        keys_file.write_text(json.dumps({"elegant_themes": {"username": "solo@example.com", "api_key": et_secret}}))
        proc = self.run_cli("keys", "--keys", str(keys_file), password=None)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), {
            "keys": [],
            "elegant_themes": {"username": "solo@example.com", "configured": True},
        })
        self.assertNotIn(et_secret, proc.stdout + proc.stderr)

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


D5 = (FIXTURES / "divi5" / "converted" / "handwritten-landing.html").read_text(encoding="utf-8")
D5_IMAGE_URL = "https://client.example/wp-content/uploads/2026/09/plumber.jpg"
STUB = "[et_pb_section][/et_pb_section]"
META_MSG = ("WordPress did not store _et_pb_use_builder=on; the page will render inside the theme's title+sidebar "
            "template. See reference/publishing.md → Divi 5 builder meta.")


class Divi5PublishFakeServerTest(unittest.TestCase):
    """publish.py against a fake Divi 5 site: the refusal matrix, the stub + /batch/v1 builder-meta sequence with
    its read-back, block image upload, and publish --content on Divi 5."""

    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), FakeWP)
        cls.site = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        fd, cls.empty_keys_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        Path(cls.empty_keys_path).write_text(json.dumps({"keys": []}))

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        os.unlink(cls.empty_keys_path)

    def setUp(self):
        _reset_fake()
        FakeWP.divi_version = "5.13.1"
        FakeWP.page_raw = D5
        FakeWP.page_title = "Existing Title"
        self.cwd = Path(tempfile.mkdtemp()).resolve()  # where a backup lands when no page file is given
        self.addCleanup(shutil.rmtree, self.cwd, True)

    def run_cli(self, *args):
        env = dict(os.environ, WP_APP_PASSWORD=PASSWORD, DIVI_KEYS_FILE=self.empty_keys_path)
        return subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), *args], capture_output=True, text=True,
                              env=env, cwd=self.cwd)

    def backups(self, where):
        return sorted(Path(where).glob("page-101-before-stub-*.txt"))

    def _file(self, text, name="page.html"):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        path = Path(d) / name
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        return path

    def draft(self, text, *extra):
        return self.run_cli("draft", str(self._file(text)), "--site", self.site, "--user", "editor",
                            "--title", "D5 Page", *extra)

    def publish(self, text, *extra):
        return self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                            "--content", str(self._file(text)), "--yes", *extra)

    def rest(self):
        return [(c["method"], c["path"]) for c in FakeWP.calls]

    def body(self, i):
        return json.loads(FakeWP.calls[i]["body"])

    # --- refusal matrix -------------------------------------------------------------------------
    def test_shortcode_draft_to_divi5_site_is_refused(self):
        proc = self.draft(GOOD)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("this is Divi 4 shortcode; the site runs Divi 5 — write Divi 5 blocks "
                      "(reference/divi5/page-format.md)", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_shortcode_publish_to_divi5_site_is_refused(self):
        proc = self.publish(GOOD)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("this is Divi 4 shortcode; the site runs Divi 5", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_blocks_draft_to_divi4_site_is_refused(self):
        FakeWP.divi_version = "4.27.9"
        proc = self.draft(D5)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("this is Divi 5 block content; the site runs Divi 4 — write Divi 4 shortcode "
                      "(reference/page-format.md)", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_blocks_publish_to_divi4_site_is_refused(self):
        FakeWP.divi_version = "4.27.9"
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("the site runs Divi 4", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    def test_tokens_divi_major_is_used_instead_of_detection(self):
        tokens = self._file(json.dumps({"site": {"url": self.site, "divi_major": 4, "divi_version": "4.27.9"}}),
                            "tokens.json")
        proc = self.draft(D5, "--tokens", str(tokens))
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("the site runs Divi 4", proc.stderr)
        self.assertEqual(FakeWP.probes, [])
        self.assertEqual(FakeWP.calls, [])

    def test_unknown_site_version_proceeds_with_warning(self):
        FakeWP.divi_version = None
        proc = self.draft(D5)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("could not detect the site's Divi version", proc.stderr)
        self.assertEqual([m for m, _ in self.rest()], ["POST", "POST", "GET"])  # still the Divi 5 sequence

    def test_unknown_site_version_shortcode_keeps_divi4_request(self):
        _reset_fake()
        FakeWP.divi_version = None
        proc = self.draft(GOOD)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("could not detect the site's Divi version", proc.stderr)
        (create,) = FakeWP.calls
        self.assertEqual(json.loads(create["body"]),
                         {"title": "D5 Page", "content": GOOD, "status": "draft", "meta": {"_et_pb_use_builder": "on"}})

    def test_block_parse_problems_are_refused_before_any_request(self):
        broken = D5.replace("<!-- /wp:divi/placeholder -->", "")
        proc = self.draft(broken)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("E5_UNCLOSED", proc.stderr)
        self.assertEqual(FakeWP.calls, [])
        bad_json = D5.replace('{"module":{"meta"', '{"module":{"meta"::', 1)
        proc = self.publish(bad_json)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn("E5_BAD_JSON", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    # --- new draft: stub, batch, read-back ------------------------------------------------------
    def test_new_draft_request_sequence(self):
        proc = self.draft(D5, "--slug", "d5-page", "--page-fields", '{"template":"page-template-blank.php"}')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.rest(), [("POST", "/wp-json/wp/v2/pages"), ("POST", "/wp-json/batch/v1"),
                                       ("GET", "/wp-json/wp/v2/pages/101?context=edit")])
        self.assertEqual(self.body(0), {"title": "D5 Page", "slug": "d5-page", "status": "draft", "content": STUB,
                                        "template": "page-template-blank.php"})
        self.assertEqual(self.body(1), {"requests": [
            {"method": "POST", "path": "/wp/v2/pages/101", "body": {"title": "D5 Page"}},
            {"method": "POST", "path": "/wp/v2/pages/101",
             "body": {"content": D5, "meta": {"_et_pb_use_builder": "on"}}}]})
        out = json.loads(proc.stdout)
        self.assertEqual(out["id"], 101)
        self.assertEqual(out["status"], "draft")
        self.assertIn("preview=true", out["preview_url"])
        self.assertEqual(out["uploaded"], [])

    def test_content_is_sent_byte_exact_including_crlf(self):
        crlf = D5.replace("\n", "\r\n")
        proc = self.draft(crlf)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.body(1)["requests"][1]["body"]["content"], crlf)

    def test_meta_not_stored_exits_2_with_message(self):
        FakeWP.batch_echo = None  # the batch's content update ran, but the meta key was not registered
        proc = self.draft(D5)
        self.assertEqual(proc.returncode, 2)
        self.assertIn(META_MSG, proc.stderr)
        self.assertIn("101", proc.stderr)

    def test_batch_echo_off_exits_2(self):
        FakeWP.batch_echo = ""
        proc = self.draft(D5)
        self.assertEqual(proc.returncode, 2)
        self.assertIn(META_MSG, proc.stderr)

    def test_get_read_back_showing_off_exits_2_even_when_the_echo_said_on(self):
        FakeWP.readback_meta = {"_et_pb_use_builder": ""}
        proc = self.draft(D5)
        self.assertEqual(proc.returncode, 2)
        self.assertIn(META_MSG, proc.stderr)

    def test_failed_batch_item_exits_2_and_names_the_stub_page(self):
        FakeWP.batch_statuses = (200, 400)
        proc = self.draft(D5)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("rest_invalid_param", proc.stderr)
        self.assertIn("--page-id 101", proc.stderr)

    def test_failed_batch_request_exits_2_and_names_the_stub_page(self):
        FakeWP.batch_http_error = True
        proc = self.draft(D5)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("HTTP 400 on POST /batch/v1", proc.stderr)
        self.assertIn("--page-id 101", proc.stderr)

    def test_divi4_site_shortcode_draft_is_the_unchanged_divi4_request(self):
        _reset_fake()
        proc = self.draft(GOOD)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr, "")
        (create,) = FakeWP.calls
        self.assertEqual(create["path"], "/wp-json/wp/v2/pages")
        self.assertEqual(json.loads(create["body"]),
                         {"title": "D5 Page", "content": GOOD, "status": "draft", "meta": {"_et_pb_use_builder": "on"}})
        self.assertEqual(FakeWP.probes, ["/wp-content/themes/Divi/style.css"])

    # --- existing page ---------------------------------------------------------------------------
    def test_existing_draft_with_meta_on_is_a_plain_update(self):
        FakeWP.page_meta = {"_et_pb_use_builder": "on"}
        proc = self.draft(D5, "--page-id", "101")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.rest(), [("GET", "/wp-json/wp/v2/pages/101?context=edit"),
                                       ("POST", "/wp-json/wp/v2/pages/101")])
        self.assertEqual(self.body(1), {"title": "D5 Page", "content": D5, "status": "draft"})

    def test_existing_draft_without_meta_uses_stub_and_batch(self):
        for meta in (None, {"_et_pb_use_builder": ""}, {"footnotes": ""}):
            with self.subTest(meta=meta):
                _reset_fake()
                FakeWP.divi_version, FakeWP.page_raw, FakeWP.page_meta = "5.13.1", D5, meta
                proc = self.draft(D5, "--page-id", "101")
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self.assertEqual(self.rest(), [("GET", "/wp-json/wp/v2/pages/101?context=edit"),
                                               ("POST", "/wp-json/wp/v2/pages/101"), ("POST", "/wp-json/batch/v1"),
                                               ("GET", "/wp-json/wp/v2/pages/101?context=edit")])
                self.assertEqual(self.body(1), {"content": STUB, "status": "draft"})
                self.assertEqual(self.body(2)["requests"][1]["body"], {"content": D5,
                                                                       "meta": {"_et_pb_use_builder": "on"}})

    def test_existing_live_page_is_still_refused_by_draft(self):
        FakeWP.page_status = "publish"
        proc = self.draft(D5, "--page-id", "101")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("offline", proc.stderr)
        self.assertFalse(any(c["method"] == "POST" for c in FakeWP.calls))

    # --- publish --content on Divi 5 --------------------------------------------------------------
    def test_publish_content_meta_on_sends_content_and_status_only(self):
        FakeWP.page_meta = {"_et_pb_use_builder": "on"}
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.rest(), [("GET", "/wp-json/wp/v2/pages/101?context=edit"),
                                       ("POST", "/wp-json/wp/v2/pages/101")])
        self.assertEqual(self.body(1), {"content": D5, "status": "publish"})

    def test_publish_content_keeps_private_page_private(self):
        FakeWP.page_status = "private"
        FakeWP.page_meta = {"_et_pb_use_builder": "on"}
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.body(1), {"content": D5})

    def test_publish_content_refuses_live_page_with_meta_off(self):
        FakeWP.page_status = "publish"
        FakeWP.page_meta = {"_et_pb_use_builder": ""}
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("_et_pb_use_builder", proc.stderr)
        self.assertIn("live", proc.stderr)
        self.assertEqual([m for m, _ in self.rest()], ["GET"])

    def _live_page_html(self, classes):
        FakeWP.page_link = f"{self.site}/?page_id=101"
        FakeWP.page_html = f'<!DOCTYPE html><html><head></head><body class="{classes}"><p>x</p></body></html>'

    def test_publish_content_live_page_meta_read_from_front_end(self):
        FakeWP.page_status = "publish"
        self._live_page_html("page-template-default page page-id-101 et_pb_pagebuilder_layout et_no_sidebar")
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("/?page_id=101", FakeWP.probes)
        self.assertEqual(self.body(1), {"content": D5, "status": "publish"})

    def test_publish_content_live_page_front_end_without_builder_layout_is_refused(self):
        FakeWP.page_status = "publish"
        self._live_page_html("page-template-default page page-id-101 et_right_sidebar")
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("_et_pb_use_builder", proc.stderr)
        self.assertEqual([m for m, _ in self.rest()], ["GET"])

    def test_publish_content_live_non_divi_page_with_unknown_meta_is_refused(self):
        FakeWP.page_status = "private"
        FakeWP.page_raw = "<!-- wp:paragraph --><p>Classic page</p><!-- /wp:paragraph -->"
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("_et_pb_use_builder", proc.stderr)
        self.assertEqual([m for m, _ in self.rest()], ["GET"])

    def test_publish_content_divi5_page_with_unknown_meta_proceeds_with_note(self):
        FakeWP.page_status = "private"   # front end not readable, REST cannot show the key
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("could not read _et_pb_use_builder", proc.stderr)
        self.assertEqual(self.body(1), {"content": D5})

    STUB_THEN_PUBLISH = [("GET", "/wp-json/wp/v2/pages/101?context=edit"), ("POST", "/wp-json/wp/v2/pages/101"),
                         ("POST", "/wp-json/batch/v1"), ("GET", "/wp-json/wp/v2/pages/101?context=edit"),
                         ("POST", "/wp-json/wp/v2/pages/101")]

    def _assert_stub_then_publish(self, content):
        self.assertEqual(self.rest(), self.STUB_THEN_PUBLISH)
        self.assertEqual(self.body(1), {"content": STUB})
        self.assertEqual(self.body(2), {"requests": [
            {"method": "POST", "path": "/wp/v2/pages/101", "body": {"title": "Existing Title"}},
            {"method": "POST", "path": "/wp/v2/pages/101",
             "body": {"content": content, "meta": {"_et_pb_use_builder": "on"}}}]})
        self.assertEqual(self.body(4), {"status": "publish"})

    def test_publish_content_draft_with_unknown_meta_sets_it_before_publishing(self):
        for meta in (None, {"_et_pb_use_builder": ""}):
            with self.subTest(meta=meta):
                _reset_fake()
                FakeWP.divi_version, FakeWP.page_raw, FakeWP.page_title, FakeWP.page_meta = \
                    "5.13.1", D5, "Existing Title", meta
                edited = D5.replace("Emergency", "Urgent", 1)
                proc = self.publish(edited)
                self.assertEqual(proc.returncode, 0, proc.stderr)
                self._assert_stub_then_publish(edited)
                self.assertEqual(json.loads(proc.stdout)["status"], "publish")

    def test_publish_without_content_draft_with_unknown_meta_resends_current_content_with_meta(self):
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self._assert_stub_then_publish(D5)

    def test_publish_meta_not_stored_exits_2_and_the_page_stays_a_draft(self):
        FakeWP.batch_echo = None
        for args in ((), ("--content", str(self._file(D5)))):
            with self.subTest(args=args):
                FakeWP.calls.clear()
                FakeWP.page_raw, FakeWP.page_meta = D5, None
                proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                                    "--yes", *args)
                self.assertEqual(proc.returncode, 2)
                self.assertIn(META_MSG, proc.stderr)
                self.assertEqual(self.rest(), self.STUB_THEN_PUBLISH[:4])  # the status change is never sent
                self.assertIn("not published", proc.stderr)

    def test_publish_backstop_exits_2_when_the_published_page_lacks_the_builder_layout(self):
        FakeWP.page_meta = {"_et_pb_use_builder": "on"}
        FakeWP.page_html = ('<html><body class="page-template-default page page-id-101 et_right_sidebar">'
                            '</body></html>')
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("et_pb_pagebuilder_layout", proc.stderr)
        self.assertIn("101", proc.stderr)
        self.assertIn("/?page_id=101", FakeWP.probes)

    def test_publish_backstop_on_an_already_live_page_does_not_say_now_published(self):
        FakeWP.page_status = "publish"
        FakeWP.page_meta = {"_et_pb_use_builder": "on"}
        FakeWP.page_html = '<html><body class="page page-id-101 et_right_sidebar"></body></html>'
        proc = self.publish(D5)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("page 101 is published, but", proc.stderr)
        self.assertNotIn("now published", proc.stderr)

    # --- the stub: backups, recovery hints, never published -------------------------------------
    def test_publish_without_content_batch_failure_backs_up_the_page_and_names_the_recovery(self):
        original = D5.replace("\n", "\r\n")
        FakeWP.page_raw = original
        FakeWP.batch_statuses = (200, 400)
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
        self.assertEqual(proc.returncode, 2)
        (backup,) = self.backups(self.cwd)
        self.assertEqual(backup.read_bytes(), original.encode("utf-8"))
        self.assertIn(str(backup), proc.stderr)
        self.assertIn(f"publish.py publish --page-id 101 --content {backup} --yes", proc.stderr)
        self.assertIn(f"publish.py draft {backup} --page-id 101", proc.stderr)
        self.assertFalse(any(json.loads(c["body"]).get("status") == "publish" for c in FakeWP.calls
                             if c["method"] == "POST" and c["path"] == "/wp-json/wp/v2/pages/101"))

    def test_publish_without_content_on_a_stubbed_page_is_refused(self):
        for raw in (STUB, STUB + "\n", "  " + STUB + "\r\n"):
            with self.subTest(raw=raw):
                FakeWP.calls.clear()
                FakeWP.page_raw, FakeWP.page_meta = raw, {"_et_pb_use_builder": ""}
                proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
                self.assertEqual(proc.returncode, 1, proc.stderr)
                self.assertIn("stub", proc.stderr)
                self.assertIn("--content", proc.stderr)
                self.assertEqual([m for m, _ in self.rest()], ["GET"])
                self.assertEqual(self.backups(self.cwd), [])

    def test_publish_content_on_a_stubbed_page_goes_through_stub_batch_and_verify(self):
        FakeWP.page_raw, FakeWP.page_meta = STUB, {"_et_pb_use_builder": ""}
        page = self._file(D5)
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                            "--content", str(page), "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self._assert_stub_then_publish(D5)
        self.assertEqual(self.backups(page.parent), [])  # the page held only the stub: nothing to back up

    def test_draft_existing_page_is_backed_up_next_to_the_page_file_before_the_stub(self):
        page = self._file(D5)
        FakeWP.batch_statuses = (200, 400)
        proc = self.run_cli("draft", str(page), "--site", self.site, "--user", "editor", "--title", "T",
                            "--page-id", "101")
        self.assertEqual(proc.returncode, 2)
        (backup,) = self.backups(page.parent)
        self.assertEqual(backup.read_text(encoding="utf-8"), D5)
        self.assertIn(str(backup), proc.stderr)
        self.assertIn(f"publish.py draft {page} --page-id 101", proc.stderr)

    def test_meta_not_stored_hint_names_the_retry_command(self):
        FakeWP.batch_echo = None
        page = self._file(D5)
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101",
                            "--content", str(page), "--yes")
        self.assertEqual(proc.returncode, 2)
        self.assertIn(f"publish.py publish --page-id 101 --content {page} --yes", proc.stderr)

    def test_publish_backstop_passes_when_the_published_page_has_the_builder_layout(self):
        FakeWP.page_html = ('<html><body class="page-template-default page page-id-101 et_pb_pagebuilder_layout '
                            'et_no_sidebar"></body></html>')
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("/?page_id=101", FakeWP.probes)

    def test_publish_without_content_divi4_page_is_unchanged(self):
        FakeWP.page_raw = GOOD
        proc = self.run_cli("publish", "--site", self.site, "--user", "editor", "--page-id", "101", "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.rest(), [("GET", "/wp-json/wp/v2/pages/101?context=edit"),
                                       ("POST", "/wp-json/wp/v2/pages/101")])
        self.assertEqual(self.body(1), {"status": "publish"})
        self.assertEqual(FakeWP.probes, [])

    # --- local images in blocks -------------------------------------------------------------------
    def test_draft_uploads_local_block_image_and_rewrites_src(self):
        page = self._file(D5.replace(D5_IMAGE_URL, "./hero.png"))
        (page.parent / "hero.png").write_bytes(b"\x89PNG\r\n\x1a\n fake")
        proc = self.run_cli("draft", str(page), "--site", self.site, "--user", "editor", "--title", "D5 Page")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual([p for _, p in self.rest()][:2], ["/wp-json/wp/v2/media", "/wp-json/wp/v2/media/55"])
        self.assertEqual(self.body(1), {"alt_text": "Plumber repairing a burst pipe"})
        sent = self.body(3)["requests"][1]["body"]["content"]
        uploaded = f"{self.site}/wp-content/uploads/hero.jpg"
        self.assertIn('{"image":{"innerContent":{"desktop":{"value":{"src":"' + uploaded + '"}}}},'
                      '"builderVersion":"5.0.0-public-beta.1"', sent)
        self.assertNotIn("./hero.png", sent)
        # only the image block was re-serialized: everything else is byte-identical
        self.assertEqual(sent.replace(uploaded, D5_IMAGE_URL), D5)
        self.assertEqual(len(json.loads(proc.stdout)["uploaded"]), 1)

    def test_missing_local_block_image_uploads_nothing(self):
        proc = self.draft(D5.replace(D5_IMAGE_URL, "./missing.png"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("local image not found", proc.stderr)
        self.assertEqual(FakeWP.calls, [])

    # --- fetch ------------------------------------------------------------------------------------
    def test_fetch_blocks_notes_canonical_raw_and_writes_bytes_exactly(self):
        FakeWP.page_raw = D5.replace("\n", "\r\n")
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        out = Path(tmp) / "original.html"
        proc = self.run_cli("fetch", "--site", self.site, "--user", "editor", "--page-id", "101", "--out", str(out))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(out.read_bytes(), D5.replace("\n", "\r\n").encode("utf-8"))
        self.assertIn("canonical re-serialization", proc.stderr)


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
