"""Tests for scripts/local_media.py: the local-image detection shared by publish.py (upload) and
preview.py (render/serve), so what the preview shows is exactly what `draft` would upload.
"""
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from _paths import SCRIPTS  # noqa: F401  (puts Skill scripts on sys.path)

sys.path.insert(0, str(SCRIPTS))

import local_media  # noqa: E402
from divi_shortcode import parse  # noqa: E402

PAGE = ('[et_pb_section background_image="./img/bg.jpg" _builder_version="4.27.9"]'
        '[et_pb_row][et_pb_column type="4_4"]'
        '[et_pb_image src="./img/a.png" alt="A"][/et_pb_image]'
        '[et_pb_image src="file://__FILE_URI__" alt="B"][/et_pb_image]'
        '[et_pb_image src="https://example.com/remote.jpg" alt="remote"][/et_pb_image]'
        '[et_pb_image src="./img/missing.jpg" alt="missing"][/et_pb_image]'
        '[/et_pb_column][/et_pb_row][/et_pb_section]')


class IterLocalImagesTest(unittest.TestCase):
    def test_finds_local_refs_including_background_image_and_skips_remote(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "img").mkdir()
            (base / "img" / "bg.jpg").write_bytes(b"bg")
            (base / "img" / "a.png").write_bytes(b"a")
            abs_file = base / "img" / "b.gif"
            abs_file.write_bytes(b"b")
            source = PAGE.replace("__FILE_URI__", str(abs_file))
            doc = parse(source)
            found = list(local_media.iter_local_images(doc, base))
        attrs_and_paths = sorted((attr, str(path)) for _node, attr, path in found)
        self.assertEqual(attrs_and_paths, sorted([
            ("background_image", str((base / "img" / "bg.jpg").resolve())),
            ("src", str((base / "img" / "a.png").resolve())),
            ("src", str(abs_file)),
            ("src", str((base / "img" / "missing.jpg").resolve())),
        ]))
        # remote https:// url is never treated as local
        self.assertNotIn("remote.jpg", " ".join(p for _a, p in attrs_and_paths))


class DataUriTest(unittest.TestCase):
    def test_data_uri_mime_by_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            for ext, mime in (("jpg", "image/jpeg"), ("jpeg", "image/jpeg"), ("png", "image/png"),
                              ("gif", "image/gif"), ("webp", "image/webp"), ("svg", "image/svg+xml")):
                f = Path(tmp) / f"x.{ext}"
                f.write_bytes(b"\x00\x01")
                uri = local_media.data_uri(f)
                self.assertTrue(uri.startswith(f"data:{mime};base64,"), uri)

    def test_data_uri_none_for_unsupported_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "x.bmp"
            f.write_bytes(b"\x00")
            self.assertIsNone(local_media.data_uri(f))


class EmbedLocalImagesTest(unittest.TestCase):
    def test_embeds_relative_and_file_uri_as_data_uris(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "img").mkdir()
            (base / "img" / "a.png").write_bytes(b"\x89PNG\r\n")
            abs_file = base / "img" / "b.jpg"
            abs_file.write_bytes(b"\xff\xd8\xff")
            source = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
                      f'[et_pb_image src="./img/a.png"][/et_pb_image]'
                      f'[et_pb_image src="file://{abs_file}"][/et_pb_image]'
                      '[/et_pb_column][/et_pb_row][/et_pb_section]')
            out = local_media.embed_local_images(source, base)
        self.assertIn("data:image/png;base64,", out)
        self.assertIn("data:image/jpeg;base64,", out)
        self.assertNotIn("./img/a.png", out)
        self.assertNotIn("file://", out)

    def test_missing_file_warns_without_failing(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
                      '[et_pb_image src="./img/missing.png"][/et_pb_image]'
                      '[/et_pb_column][/et_pb_row][/et_pb_section]')
            err = io.StringIO()
            with redirect_stderr(err):
                out = local_media.embed_local_images(source, base)
        self.assertIn("./img/missing.png", out)  # left as-is
        warning = err.getvalue()
        self.assertIn("src", warning)
        self.assertIn(str((base / "img" / "missing.png").resolve()), warning)
        self.assertEqual(len(warning.strip().splitlines()), 1)

    def test_background_image_is_embedded(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "img").mkdir()
            (base / "img" / "bg.jpg").write_bytes(b"\xff\xd8\xff")
            source = ('[et_pb_section background_image="./img/bg.jpg"][et_pb_row][et_pb_column type="4_4"]'
                      '[/et_pb_column][/et_pb_row][/et_pb_section]')
            out = local_media.embed_local_images(source, base)
        self.assertIn('background_image="data:image/jpeg;base64,', out)


class RouteTokenTest(unittest.TestCase):
    def test_rewrite_for_serve_builds_allowlist_and_rewrites_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "img").mkdir()
            (base / "img" / "a.png").write_bytes(b"a")
            source = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"]'
                      '[et_pb_image src="./img/a.png"][/et_pb_image]'
                      '[et_pb_image src="./img/missing.png"][/et_pb_image]'
                      '[/et_pb_column][/et_pb_row][/et_pb_section]')
            rewritten, allowed = local_media.rewrite_for_serve(source, base, "/__local/mypage/")
        self.assertEqual(len(allowed), 1)
        (token, path), = allowed.items()
        self.assertEqual(path, (base / "img" / "a.png").resolve())
        self.assertIn(f"/__local/mypage/{token}", rewritten)
        self.assertIn("./img/missing.png", rewritten)  # missing file left untouched

    def test_token_is_urlsafe_and_stable(self):
        p = Path("/tmp/some file (1).jpg")
        t1 = local_media.route_token(p)
        t2 = local_media.route_token(p)
        self.assertEqual(t1, t2)
        self.assertRegex(t1, r"^[A-Za-z0-9_-]+$")


class IterLocalImages5Test(unittest.TestCase):
    """The Divi 5 (block) branch: image leaves are the schema5 leaves typed `image` (image.innerContent src,
    blurb imageIcon.innerContent src, background image.url, ...)."""
    SOURCE = ('<!-- wp:divi/placeholder -->'
              '<!-- wp:divi/section {"module":{"decoration":{"background":{"desktop":{"value":'
              '{"image":{"url":"./img/bg.jpg"}}}}}},"builderVersion":"5.13.1"} -->'
              '<!-- wp:divi/row {"builderVersion":"5.13.1"} --><!-- wp:divi/column {"builderVersion":"5.13.1"} -->'
              '<!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"./img/a.png","alt":"A"}}}},'
              '"builderVersion":"5.0.0-public-beta.1"} /-->'
              '<!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://example.com/r.jpg"}}}},'
              '"builderVersion":"5.13.1"} /-->'
              '<!-- wp:divi/blurb {"imageIcon":{"innerContent":{"desktop":{"value":{"src":"file://__FILE__"}}}},'
              '"builderVersion":"5.13.1"} /-->'
              '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"./img/not-an-image-leaf.png"}}},'
              '"builderVersion":"5.13.1"} /-->'
              '<!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section --><!-- /wp:divi/placeholder -->')

    def _doc(self, base):
        from divi5_blocks import parse as parse5
        return parse5(self.SOURCE.replace("__FILE__", str(base / "b.gif")))

    def test_finds_image_leaves_by_schema_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            found = list(local_media.iter_local_images(self._doc(base), base))
        got = sorted((block.name, ref.attr, ref.breakpoint, ref.state, ref.sub, str(path))
                     for block, ref, path in found)
        self.assertEqual(got, sorted([
            ("divi/section", "module.decoration.background", "desktop", "value", "image.url",
             str((base / "img" / "bg.jpg").resolve())),
            ("divi/image", "image.innerContent", "desktop", "value", "src", str((base / "img" / "a.png").resolve())),
            ("divi/blurb", "imageIcon.innerContent", "desktop", "value", "src", str(base / "b.gif")),
        ]))

    def test_set_image5_rewrites_only_that_leaf_and_keeps_builder_version(self):
        from divi5_blocks import serialize as serialize5
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            doc = self._doc(base)
            for block, ref, _path in list(local_media.iter_local_images(doc, base)):
                if block.name == "divi/image":
                    local_media.set_image5(block, ref, "https://site.test/wp-content/uploads/a.png")
            out = serialize5(doc)
        self.assertIn('{"image":{"innerContent":{"desktop":{"value":{"src":"https://site.test/wp-content/uploads/a.png",'
                      '"alt":"A"}}}},"builderVersion":"5.0.0-public-beta.1"}', out)
        self.assertNotIn('"id"', out)
        # every other block keeps its exact source bytes
        self.assertIn('"url":"./img/bg.jpg"', out)
        self.assertIn('"src":"file://', out)
        self.assertEqual(out.replace("https://site.test/wp-content/uploads/a.png", "./img/a.png"),
                         self.SOURCE.replace("__FILE__", str(base / "b.gif")))

    def test_upload_alt_prefers_sibling_alt(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            found = {b.name: (b, r) for b, r, _p in local_media.iter_local_images(self._doc(base), base)}
        self.assertEqual(local_media.image_alt5(*found["divi/image"]), "A")
        self.assertEqual(local_media.image_alt5(*found["divi/blurb"]), "")


if __name__ == "__main__":
    unittest.main()
