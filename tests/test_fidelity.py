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


def _d5(css_blocks, marker=True):
    """A Divi 5 page: its builder CSS sits in Divi 5 style ids (or a flattened et-cache file)."""
    return ('<html><head>'
            + ('<script src="http://x.test/wp-content/themes/Divi/includes/builder-5/visual-builder/x.js"></script>'
               if marker else '')
            + css_blocks + '</head><body><div class="et-l et-l--post"><div class="et_pb_section et_pb_section_0">'
            '<div class="et_pb_text et_pb_text_0"><p>Hi</p></div></div></div></body></html>')


class Divi5CompareTest(unittest.TestCase):
    """Divi 5 builder CSS lives under different style ids (compare_d5.py, R5): critical inline CSS, the unified
    (deferred) cached-inline styles of a first render, and et-cache files a flattened live page inlines."""

    LIVE = ('<style id="et-critical-inline-css">.et_pb_text_0{color:red}</style>'
            '<style data-href="http://x.test/wp-content/et-cache/12/et-core-unified-deferred-12.min.css">'
            '@media only screen and (max-width:980px){.et_pb_text_0{font-size:12px}}</style>')
    PREVIEW = ('<style id="et-core-unified-990000001-cached-inline-styles">.et_pb_text_0{color:red}</style>'
               '<style id="et-core-unified-deferred-990000001-cached-inline-styles-2">'
               '@media only screen and (max-width:980px){.et_pb_text_0{font-size:12px}}</style>')

    def test_divi_5_builder_css_is_found_on_both_sides(self):
        result = fidelity.compare(_d5(self.LIVE), _d5(self.PREVIEW))
        self.assertEqual(result["css"]["truth_decls"], 2)
        self.assertEqual(result["css"]["candidate_decls"], 2)
        self.assertEqual(result["css"]["common"], 2)
        self.assertTrue(result["markup"]["tag_class_sequence_equal"])
        self.assertTrue(result["markup"]["et_l_identical"])

    def test_a_missing_divi_5_declaration_is_reported(self):
        result = fidelity.compare(_d5(self.LIVE), _d5(self.PREVIEW.replace("font-size:12px", "")))
        self.assertEqual(result["css"]["missing"], 1)

    def test_divi_4_pages_keep_the_divi_4_style_ids_only(self):
        # The same Divi 5 ids on a page without Divi 5 markers are not builder CSS (Divi 4 behaviour unchanged).
        page = _d5(self.LIVE + '<style id="et-builder-module-design-990000001-cached-inline-styles">'
                   '.et_pb_text_0{margin:0}</style>', marker=False)
        self.assertEqual(fidelity.compare(page, page)["css"]["truth_decls"], 1)

    def test_flatten_inlines_same_origin_stylesheets_and_preloads(self):
        pages = {
            "http://x.test/p/": ('<link rel="stylesheet" href="http://x.test/a.css?ver=1">'
                                 '<link rel="preload" as="style" href="http://x.test/wp-content/et-cache/1/b.css">'
                                 '<link rel="preload" as="font" href="http://x.test/f.woff2">'
                                 '<link rel="stylesheet" href="https://fonts.example/c.css">'),
            "http://x.test/a.css?ver=1": ".a{color:red}",
            "http://x.test/wp-content/et-cache/1/b.css": ".b{color:blue}",
        }
        out = fidelity.flatten("http://x.test/p/", fetch=lambda u: pages[u])
        self.assertIn('<style data-href="http://x.test/a.css?ver=1">\n.a{color:red}\n</style>', out)
        self.assertIn('<style data-href="http://x.test/wp-content/et-cache/1/b.css">\n.b{color:blue}\n</style>', out)
        self.assertIn('as="font"', out)
        self.assertIn("https://fonts.example/c.css", out)


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
