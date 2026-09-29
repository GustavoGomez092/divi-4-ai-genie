"""Offline fallbacks of the Python renderer for content that needs WordPress or the network
(Tasks 25 and 27): gallery attachment IDs, oEmbed video URLs (network) and the modules that show
the site's own data (posts, menus, comments, widgets). Real Divi can't be the reference here (a fresh
Playground site has no posts, media, menus or network), so these check the documented behaviour.

The coverage report keeps two lists apart: `unsupported_modules` (the Python preview doesn't
render it; the --exact preview does, with network for oEmbed) and `needs_site_data` (only the live
site has the data, so neither preview can show it; the WordPress draft preview is the check).
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
        cls.version = fetch_divi.newest_cached(major=4)  # the Python renderer is Divi 4 only
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
        self.assertNotIn("gallery_attachments", cov["needs_site_data"])

    def test_gallery_ids_render_placeholder_grid_items_and_are_reported(self):
        html, cov = self.render(f'[et_pb_gallery gallery_ids="11,12,13" posts_number="2" {B}][/et_pb_gallery]')
        self.assertIn("et_pb_gallery_grid", html)
        self.assertEqual(len(re.findall(r'class="et_pb_gallery_item et_pb_grid_item', html)), 3)
        self.assertIn('data-per_page="2"', html)
        self.assertIn('class="et_pb_gallery_image landscape"', html)
        self.assertIn('class="et_pb_gallery_pagination"', html)
        self.assertEqual(cov["needs_site_data"].get("gallery_attachments"), 3)
        self.assertNotIn("gallery_attachments", cov["unsupported_modules"])

    def test_fullwidth_gallery_ids_use_slider_markup(self):
        html, cov = self.render(f'[et_pb_gallery gallery_ids="11,12" fullwidth="on" {B}][/et_pb_gallery]')
        self.assertIn("et_pb_gallery_fullwidth", html)
        self.assertNotIn("et_pb_grid_item", html)
        self.assertNotIn("et_pb_gallery_pagination", html)

    def test_youtube_video_becomes_an_embed_iframe_and_is_reported(self):
        html, cov = self.render(f'[et_pb_video src="https://www.youtube.com/watch?v=dQw4w9WgXcQ" {B}][/et_pb_video]')
        self.assertIn('src="https://www.youtube.com/embed/dQw4w9WgXcQ?feature=oembed"', html)
        self.assertNotIn("<video", html.split('class="et_pb_video_box"')[1][:200])
        # oEmbed needs the network, not the site's data: the --exact preview fetches the real embed
        self.assertEqual(cov["unsupported_modules"].get("video_oembed"), 1)
        self.assertNotIn("video_oembed", cov["needs_site_data"])

    def test_self_hosted_video_is_a_native_player(self):
        html, cov = self.render(f'[et_pb_video src="https://example.com/a.mp4" {B}][/et_pb_video]')
        self.assertIn('<source type="video/mp4" src="https://example.com/a.mp4" />', html)
        self.assertNotIn("video_oembed", cov["unsupported_modules"])

    def test_site_data_modules_render_a_block_that_points_to_the_draft_preview(self):
        for tag in ("et_pb_blog", "et_pb_portfolio", "et_pb_filterable_portfolio", "et_pb_fullwidth_portfolio",
                    "et_pb_post_slider", "et_pb_fullwidth_post_slider", "et_pb_post_title",
                    "et_pb_fullwidth_post_title", "et_pb_post_content", "et_pb_fullwidth_post_content",
                    "et_pb_post_nav", "et_pb_comments", "et_pb_sidebar", "et_pb_menu", "et_pb_fullwidth_menu"):
            with self.subTest(tag=tag):
                html, cov = self.render(f'[{tag} {B}][/{tag}]')
                self.assertIn("pp-site-data", html)
                self.assertIn("WordPress draft preview", html)
                self.assertNotIn("--exact", html)
                self.assertEqual(cov["needs_site_data"], {tag: 1})
                self.assertEqual(cov["unsupported_modules"], {})
                self.assertFalse(cov["by_tag"][tag]["supported"])

    def test_modules_the_exact_preview_can_show_still_point_to_exact(self):
        for tag in ("et_pb_search", "et_pb_login"):
            with self.subTest(tag=tag):
                html, cov = self.render(f'[{tag} {B}][/{tag}]')
                self.assertIn("pp-unsupported", html)
                self.assertIn("--exact", html)
                self.assertEqual(cov["unsupported_modules"], {tag: 1})
                self.assertEqual(cov["needs_site_data"], {})


if __name__ == "__main__":
    unittest.main()
