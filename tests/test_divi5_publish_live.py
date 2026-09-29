"""publish.py against the local Divi 5 site (divi-5-test.local): the stub + /batch/v1 builder-meta sequence over
REST with an Application Password, the rendered layout, the existing-draft and publish --content paths, and block
image upload. Opt-in: PP_LIVE_TESTS=1 and the site running (@live5_only). Every page is titled "D5TEST ..." and
deleted afterwards, as are the uploaded media and the throwaway Application Password.
"""
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest
import urllib.request
import zlib
from pathlib import Path

from _paths import FIXTURES5, SCRIPTS, SITE5_URL, live5_only, wp5

sys.path.insert(0, str(SCRIPTS))
import divi5_blocks  # noqa: E402

FIXTURE = FIXTURES5 / "converted" / "handwritten-landing.html"
IMAGE_URL = "https://client.example/wp-content/uploads/2026/09/plumber.jpg"
APP_NAME = "d5-publish-live-test"


def _png() -> bytes:
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"\x00\xff\x80\x00\xff\x80\x00\x00\xff\x80\x00\xff\x80"))
            + chunk(b"IEND", b""))


def _body_classes(html: str) -> list:
    m = re.search(r"<body\b[^>]*\bclass=\"([^\"]*)\"", html)
    return m.group(1).split() if m else []


@live5_only
class Divi5PublishLiveTest(unittest.TestCase):
    def wp(self, *args):
        out = wp5(*args)
        if out.returncode != 0:
            self.fail(f"wp {args[:3]} failed: {out.stderr[-300:]}")
        return out.stdout.strip()

    def setUp(self):
        self.admin = self.wp("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        self.password = self.wp("user", "application-password", "create", self.admin, APP_NAME, "--porcelain")
        self.pages, self.media = [], []
        fd, self.keys = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        Path(self.keys).write_text(json.dumps({"keys": []}))

    def tearDown(self):
        for pid in self.pages + self.media:
            wp5("post", "delete", pid, "--force", f"--user={self.admin}")
        uuids = wp5("user", "application-password", "list", self.admin, f"--name={APP_NAME}", "--field=uuid")
        for uuid in uuids.stdout.split():
            wp5("user", "application-password", "delete", self.admin, uuid)
        os.unlink(self.keys)

    def publish_py(self, *args):
        env = dict(os.environ, WP_APP_PASSWORD=self.password, DIVI_KEYS_FILE=self.keys)
        proc = subprocess.run([sys.executable, str(SCRIPTS / "publish.py"), *map(str, args), "--site", SITE5_URL,
                               "--user", self.admin], capture_output=True, text=True, env=env, timeout=300)
        self.assertNotIn(self.password, proc.stdout + proc.stderr)
        return proc

    def draft(self, page, *extra):
        proc = self.publish_py("draft", page, "--title", "D5TEST publish.py", *extra)
        if proc.returncode == 0:
            out = json.loads(proc.stdout)
            if out["id"] not in self.pages:
                self.pages.append(out["id"])
            self.media.extend(u["id"] for u in out["uploaded"])
        return proc

    def stored(self, pid):
        return self.wp("post", "get", pid, "--field=post_content")

    def meta(self, pid):
        return self.wp("post", "meta", "get", pid, "_et_pb_use_builder")

    def front_end(self, pid):
        link = self.wp("post", "list", "--post_type=page", f"--post__in={pid}", "--post_status=publish",
                       "--field=url")
        with urllib.request.urlopen(link, timeout=120) as resp:
            return resp.read().decode("utf-8", "replace")

    def test_draft_sets_builder_meta_and_renders_builder_layout(self):
        source = FIXTURE.read_text(encoding="utf-8")
        canonical = "".join(divi5_blocks.render_block(n) for n in divi5_blocks.parse(source).nodes)
        proc = self.draft(FIXTURE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        pid = json.loads(proc.stdout)["id"]
        self.assertEqual(self.wp("post", "get", pid, "--field=post_status"), "draft")
        self.assertEqual(self.meta(pid), "on")
        self.assertEqual(self.stored(pid), canonical.rstrip("\n"))

        # the builder layout, as a visitor sees it once the page is published
        self.wp("post", "update", pid, "--post_status=publish", f"--user={self.admin}")
        html = self.front_end(pid)
        classes = _body_classes(html)
        self.assertIn("et_pb_pagebuilder_layout", classes)
        self.assertIn("et_no_sidebar", classes)
        self.assertNotIn("entry-title", html)
        self.assertIn("Emergency", html)  # the fixture's hero heading rendered

        # publish --content on the live page: its meta is read from the front end (REST can't show it)
        edited = source.replace("Emergency", "Urgent", 1)
        page = Path(tempfile.mkdtemp()) / "edited.html"
        page.write_text(edited, encoding="utf-8")
        proc = self.publish_py("publish", "--page-id", pid, "--content", page, "--yes")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["status"], "publish")
        self.assertEqual(self.meta(pid), "on")
        self.assertIn("Urgent", self.stored(pid))

    def test_existing_draft_without_readable_meta_goes_through_stub_and_batch(self):
        proc = self.draft(FIXTURE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        pid = json.loads(proc.stdout)["id"]
        self.wp("post", "meta", "delete", pid, "_et_pb_use_builder", f"--user={self.admin}")
        proc = self.draft(FIXTURE, "--page-id", pid)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["id"], pid)
        self.assertEqual(self.meta(pid), "on")
        self.assertEqual(self.wp("post", "get", pid, "--field=post_status"), "draft")
        self.assertNotIn("[et_pb_section]", self.stored(pid))

    def test_local_block_image_is_uploaded_and_rewritten(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "d5test-hero.png").write_bytes(_png())
        page = tmp / "page.html"
        with open(page, "w", encoding="utf-8", newline="") as fh:
            fh.write(FIXTURE.read_text(encoding="utf-8").replace(IMAGE_URL, "./d5test-hero.png"))
        proc = self.draft(page)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        (up,) = out["uploaded"]
        stored = self.stored(out["id"])
        self.assertNotIn("./d5test-hero.png", stored)
        self.assertIn('{"src":"' + up["url"] + '"}', stored)
        self.assertEqual(self.wp("post", "meta", "get", up["id"], "_wp_attachment_image_alt"),
                         "Plumber repairing a burst pipe")
        self.wp("post", "update", out["id"], "--post_status=publish", f"--user={self.admin}")
        html = self.front_end(out["id"])
        img = re.search(r"<img[^>]*d5test-hero[^>]*>", html)
        self.assertIsNotNone(img, "uploaded image not rendered")
        self.assertIn(f"wp-image-{up['id']}", img.group(0))  # Divi found the attachment from the URL alone


if __name__ == "__main__":
    unittest.main()
