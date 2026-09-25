"""Offline fallbacks of the Python renderer for content that needs WordPress or the network
(Task 25): gallery attachment IDs and oEmbed video URLs. Real Divi can't be the reference here
(a fresh Playground site has no media and no network), so these check the documented behaviour.
"""
import re
import unittest

from _paths import FIXTURES  # noqa: F401  (puts scripts on sys.path)

import divi_render
import fetch_divi

B = '_builder_version="4.27.9" _module_preset="default"'


def page(module: str) -> str:
    return (f'[et_pb_section {B}][et_pb_row {B}][et_pb_column type="4_4" {B}]{module}'
            '[/et_pb_column][/et_pb_row][/et_pb_section]')


class FallbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.version = fetch_divi.newest_cached()
        if cls.version is None:
            raise unittest.SkipTest("no Divi build cached (python3 scripts/preview.py fetch-divi VER)")

    def render(self, module: str):
        """(builder markup only, coverage report): the page shell and Divi's static CSS mention
        the same class names, so assertions look at the .et-l block alone."""
        r = divi_render.render_page(page(module), divi_version=self.version, with_js=False)
        return r.html.split('<div class="et-l et-l--post">', 1)[1].split("<footer", 1)[0], r.coverage

    def test_gallery_without_ids_prints_no_markup_like_divi(self):
        html, cov = self.render(f'[et_pb_gallery {B}][/et_pb_gallery]')
        self.assertNotIn("et_pb_gallery", html)
        self.assertNotIn("gallery_attachments", cov["unsupported_modules"])

    def test_gallery_ids_render_placeholder_grid_items_and_are_reported(self):
        html, cov = self.render(f'[et_pb_gallery gallery_ids="11,12,13" posts_number="2" {B}][/et_pb_gallery]')
        self.assertIn("et_pb_gallery_grid", html)
        self.assertEqual(len(re.findall(r'class="et_pb_gallery_item et_pb_grid_item', html)), 3)
        self.assertIn('data-per_page="2"', html)
        self.assertIn('class="et_pb_gallery_image landscape"', html)
        self.assertIn('class="et_pb_gallery_pagination"', html)
        self.assertEqual(cov["unsupported_modules"].get("gallery_attachments"), 3)

    def test_fullwidth_gallery_ids_use_slider_markup(self):
        html, cov = self.render(f'[et_pb_gallery gallery_ids="11,12" fullwidth="on" {B}][/et_pb_gallery]')
        self.assertIn("et_pb_gallery_fullwidth", html)
        self.assertNotIn("et_pb_grid_item", html)
        self.assertNotIn("et_pb_gallery_pagination", html)

    def test_youtube_video_becomes_an_embed_iframe_and_is_reported(self):
        html, cov = self.render(f'[et_pb_video src="https://www.youtube.com/watch?v=dQw4w9WgXcQ" {B}][/et_pb_video]')
        self.assertIn('src="https://www.youtube.com/embed/dQw4w9WgXcQ?feature=oembed"', html)
        self.assertNotIn("<video", html.split('class="et_pb_video_box"')[1][:200])
        self.assertEqual(cov["unsupported_modules"].get("video_oembed"), 1)

    def test_self_hosted_video_is_a_native_player(self):
        html, cov = self.render(f'[et_pb_video src="https://example.com/a.mp4" {B}][/et_pb_video]')
        self.assertIn('<source type="video/mp4" src="https://example.com/a.mp4" />', html)
        self.assertNotIn("video_oembed", cov["unsupported_modules"])


if __name__ == "__main__":
    unittest.main()
