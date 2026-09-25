"""Tests for research/tools/fidelity.py (ported from research/python-renderer-spike/evaluate.py)
and research/tools/ground_truth.py (Playground ground-truth cache, Task 14)."""
import shutil
import unittest
from pathlib import Path

from _paths import FIXTURES, TOOLS  # noqa: F401  (puts research/tools on sys.path)

import fidelity
import ground_truth

VERSION = "4.27.9"


def _html(text_class="et_pb_text_0", color="red", extra_css=""):
    return (
        '<html><body>'
        '<div class="et-l et-l--post">'
        '<div class="et_pb_section et_pb_section_0">'
        f'<div class="et_pb_text {text_class}"><p>Hello</p></div>'
        '</div></div>'
        '<style id="et-builder-module-design-990000001-cached-inline-styles">'
        f'.et_pb_text_0{{color:{color};}}{extra_css}'
        '</style>'
        '</body></html>'
    )


class CompareTest(unittest.TestCase):
    def test_identical_html_is_a_perfect_match(self):
        html = _html()
        result = fidelity.compare(html, html)
        self.assertTrue(result["markup"]["tag_class_sequence_equal"])
        self.assertEqual(result["markup"]["tag_class_seq_ratio"], 1.0)
        self.assertEqual(result["css"]["missing"], 0)
        self.assertEqual(result["css"]["extra"], 0)

    def test_one_changed_class_breaks_sequence_equality(self):
        truth = _html(text_class="et_pb_text_0")
        candidate = _html(text_class="et_pb_text_0 et_pb_text_0--mod")
        result = fidelity.compare(truth, candidate)
        self.assertFalse(result["markup"]["tag_class_sequence_equal"])
        self.assertLess(result["markup"]["tag_class_seq_ratio"], 1.0)

    def test_dropped_css_declaration_is_reported_as_missing(self):
        truth = _html(extra_css=".et_pb_text_0{font-size:14px;}")
        candidate = _html(extra_css="")
        result = fidelity.compare(truth, candidate)
        self.assertEqual(result["css"]["missing"], 1)
        self.assertTrue(any("font-size:14px" in ex for ex in result["missing_examples"]))

    def test_deferred_builder_css_is_read(self):
        # Playground/real Divi pages without critical CSS print all builder CSS in the *deferred* style.
        truth = _html().replace("module-design-990000001", "module-design-deferred-990000001")
        result = fidelity.compare(truth, _html())
        self.assertEqual(result["css"]["truth_decls"], 1)
        self.assertEqual(result["css"]["missing"], 0)
        self.assertEqual(result["css"]["extra"], 0)

    def test_split_builder_css_is_combined(self):
        # Critical-CSS pages split builder CSS between the inline and the deferred style.
        truth = _html(extra_css="") + (
            '<style id="et-builder-module-design-deferred-990000001-cached-inline-styles">'
            '.et_pb_text_0{font-size:14px;}</style>')
        result = fidelity.compare(truth, _html(extra_css=".et_pb_text_0{font-size:14px;}"))
        self.assertEqual(result["css"]["truth_decls"], 2)
        self.assertEqual(result["css"]["missing"], 0)

    def test_per_request_form_values_do_not_affect_the_comparison(self):
        # Divi prints a fresh nonce and random captcha digits on every contact form render; the
        # markup comparison reads tags and classes only, so two renders stay identical.
        def form(nonce, a, b):
            return ('<div class="et-l et-l--post"><div class="et_pb_contact"><form class="et_pb_contact_form clearfix">'
                    f'<p class="clearfix"><span class="et_pb_contact_captcha_question">{a} + {b}</span> = '
                    f'<input type="text" class="input et_pb_contact_captcha" data-first_digit="{a}" data-second_digit="{b}">'
                    f'</p><input type="hidden" id="_wpnonce-et-pb-contact-form-submitted-0" value="{nonce}" />'
                    '</form></div></div>')
        result = fidelity.compare(form("92b852bfe5", 4, 9), form("0000000000", 1, 1))
        self.assertTrue(result["markup"]["tag_class_sequence_equal"])
        self.assertEqual(result["markup"]["tag_class_seq_ratio"], 1.0)


@unittest.skipUnless(shutil.which("node"), "node not installed")
class GroundTruthTest(unittest.TestCase):
    FIXTURE = FIXTURES / "valid" / "handwritten-landing.txt"

    @classmethod
    def setUpClass(cls):
        cls.truth = ground_truth.ensure_truth(cls.FIXTURE, VERSION)
        if cls.truth is None:
            raise unittest.SkipTest(f"Divi {VERSION} not cached / Playground unavailable")

    def test_truth_path_layout(self):
        path = ground_truth.truth_path(self.FIXTURE, VERSION)
        self.assertEqual(path.name, "handwritten-landing.html")
        self.assertEqual(path.parent.name, VERSION)

    def test_ensure_truth_renders_real_divi_markup(self):
        self.assertTrue(self.truth.exists())
        self.assertIn('class="et-l', self.truth.read_text(encoding="utf-8", errors="replace"))


if __name__ == "__main__":
    unittest.main()
