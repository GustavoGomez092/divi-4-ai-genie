"""Tests that touch a live WordPress site or read Elegant Themes credentials must be opt-in
(PP_LIVE_TESTS=1). This checks the gating statically: nothing here calls the live site."""
import os
import unittest
from unittest import mock

import _paths


def _skip_reason(obj):
    return getattr(obj, "__unittest_skip_why__", "") if getattr(obj, "__unittest_skip__", False) else ""


class LiveGatingTest(unittest.TestCase):
    def test_live_flag_reads_env(self):
        with mock.patch.dict(os.environ, {"PP_LIVE_TESTS": "1"}):
            self.assertTrue(_paths.live_tests_enabled())
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_paths.live_tests_enabled())

    @unittest.skipIf(os.environ.get("PP_LIVE_TESTS") == "1", "live tests enabled; gating not in effect")
    def test_live_tests_skip_with_reason(self):
        import test_divi_judge
        import test_preview
        import test_publish
        import test_tokens_fidelity
        gated = [test_publish.PublishLiveTest, test_tokens_fidelity.TokensFidelityTest,
                 test_divi_judge.DiviJudgeTest, test_preview.PreviewTest.test_page11_builder_css_matches_live,
                 test_preview.PreviewTest.test_no_credentials_in_output]
        for obj in gated:
            with self.subTest(obj.__qualname__):
                self.assertIn("PP_LIVE_TESTS=1", _skip_reason(obj))

    @unittest.skipIf(os.environ.get("PP_LIVE_TESTS") == "1", "live tests enabled; gating not in effect")
    def test_preview_does_not_read_et_credentials_from_local_site(self):
        import test_preview
        with mock.patch("subprocess.run", side_effect=AssertionError("wp-local.sh must not run")):
            self.assertEqual(test_preview._et_env(), {})


if __name__ == "__main__":
    unittest.main()
