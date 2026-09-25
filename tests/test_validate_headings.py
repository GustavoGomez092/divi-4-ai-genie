"""Page-level heading structure: E_MULTIPLE_H1, W_NO_H1, W_HEADING_SKIP."""
import unittest

from _paths import FIXTURES
from divi_schema import load_schema
from validate import validate_source

SCHEMA = load_schema()
HEADING_CODES = {"E_MULTIPLE_H1", "W_NO_H1", "W_HEADING_SKIP"}


def page(*modules, fullwidth=()):
    body = "".join(modules)
    out = f'[et_pb_section][et_pb_row][et_pb_column type="4_4"]{body}[/et_pb_column][/et_pb_row][/et_pb_section]'
    if fullwidth:
        out = f'[et_pb_section fullwidth="on"]{"".join(fullwidth)}[/et_pb_section]' + out
    return out


def heading_findings(src, **kw):
    return [(f.code, f.tag, f.attr, f.value) for f in validate_source(src, SCHEMA, **kw) if f.code in HEADING_CODES]


def codes(src, **kw):
    return [c for c, *_ in heading_findings(src, **kw)]


H1 = '[et_pb_heading title="Main" title_level="h1"][/et_pb_heading]'
H2 = '[et_pb_heading title="Sub" title_level="h2"][/et_pb_heading]'


class HeadingStructureTest(unittest.TestCase):
    def test_single_h1_then_h2_is_clean(self):
        self.assertEqual(codes(page(H1, H2)), [])

    def test_heading_module_default_level_is_h1(self):
        self.assertEqual(codes(page('[et_pb_heading title="Main"][/et_pb_heading]', H2)), [])

    def test_two_h1_is_an_error_at_the_second(self):
        found = heading_findings(page(H1, '[et_pb_text]<h1>Another</h1>[/et_pb_text]'))
        self.assertEqual(found, [("E_MULTIPLE_H1", "et_pb_text", "content", "h1")])
        errors = [f for f in validate_source(page(H1, H1), SCHEMA) if f.code == "E_MULTIPLE_H1"]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].level, "error")

    def test_no_h1_is_a_warning(self):
        found = [f for f in validate_source(page(H2), SCHEMA) if f.code in HEADING_CODES]
        self.assertEqual([(f.level, f.code) for f in found], [("warning", "W_NO_H1")])

    def test_fragment_skips_no_h1_only(self):
        self.assertEqual(codes(page(H2), fragment=True), [])
        self.assertEqual(codes(page(H1, H1), fragment=True), ["E_MULTIPLE_H1"])
        skip = page(H2, '[et_pb_blurb title="B" header_level="h4"]<p>x</p>[/et_pb_blurb]')
        self.assertEqual(codes(skip, fragment=True), ["W_HEADING_SKIP"])

    def test_skip_going_deeper_warns_going_up_does_not(self):
        found = heading_findings(page(H1, '[et_pb_blurb title="B" header_level="h3"]<p>x</p>[/et_pb_blurb]'))
        self.assertEqual(found, [("W_HEADING_SKIP", "et_pb_blurb", "header_level", "h1>h3")])
        self.assertEqual(codes(page(H1, H2, '[et_pb_blurb title="B" header_level="h3"][/et_pb_blurb]', H2)), [])

    def test_blurb_default_header_level_h4_counts(self):
        # et_pb_blurb's header_level defaults to h4: h1 -> h4 skips
        self.assertEqual(codes(page(H1, '[et_pb_blurb title="B"][/et_pb_blurb]')), ["W_HEADING_SKIP"])

    def test_module_without_its_title_text_renders_no_heading(self):
        self.assertEqual(codes(page(H1, '[et_pb_blurb header_level="h4"]<p>no title</p>[/et_pb_blurb]')), [])

    def test_content_headings_in_document_order(self):
        text = '[et_pb_text]<h2>A</h2><p>x</p><h3>B</h3><h5>C</h5>[/et_pb_text]'
        self.assertEqual(heading_findings(page(H1, text)),
                         [("W_HEADING_SKIP", "et_pb_text", "content", "h3>h5")])

    def test_accordion_items_inherit_the_accordions_toggle_level(self):
        acc = ('[et_pb_accordion toggle_level="h3"][et_pb_accordion_item title="Q1"]<p>a</p>[/et_pb_accordion_item]'
               '[et_pb_accordion_item title="Q2"]<p>b</p>[/et_pb_accordion_item][/et_pb_accordion]')
        self.assertEqual(codes(page(H1, H2, acc)), [])
        default_acc = acc.replace(' toggle_level="h3"', "")  # accordion default h5: h2 -> h5 skips
        self.assertEqual(heading_findings(page(H1, H2, default_acc)),
                         [("W_HEADING_SKIP", "et_pb_accordion_item", "toggle_level", "h2>h5")])

    def test_fullwidth_header_title_defaults_to_h1(self):
        fw = '[et_pb_fullwidth_header title="Hero"][/et_pb_fullwidth_header]'
        self.assertEqual(codes(page(H2, fullwidth=[fw])), [])
        self.assertEqual(codes(page(H1, fullwidth=[fw])), ["E_MULTIPLE_H1"])
        fw2 = '[et_pb_fullwidth_header title="Hero" title_level="h2"][/et_pb_fullwidth_header]'
        self.assertEqual(codes(page(H2, fullwidth=[fw2])), ["W_NO_H1"])

    def test_slides_inherit_the_sliders_header_level(self):
        slider = ('[et_pb_slider header_level="h2"][et_pb_slide heading="One"][/et_pb_slide]'
                  '[et_pb_slide heading="Two" header_level="h4"][/et_pb_slide][/et_pb_slider]')
        self.assertEqual(heading_findings(page(H1, slider)),
                         [("W_HEADING_SKIP", "et_pb_slide", "header_level", "h2>h4")])

    def test_heading_skip_respects_baseline(self):
        original = page(H1, '[et_pb_blurb title="B" header_level="h3"][/et_pb_blurb]')
        edited = original.replace('title="Main"', 'title="New main"')
        found = [f for f in validate_source(edited, SCHEMA, baseline=original) if f.code in HEADING_CODES]
        self.assertEqual([(f.code, f.preexisting) for f in found], [("W_HEADING_SKIP", True)])
        worse = page(H1, H1, '[et_pb_blurb title="B" header_level="h3"][/et_pb_blurb]')
        found = [f for f in validate_source(worse, SCHEMA, baseline=original) if f.code in HEADING_CODES]
        self.assertIn(("E_MULTIPLE_H1", False), [(f.code, f.preexisting) for f in found])

    def test_every_schema_heading_level_field_is_covered(self):
        from divi_checks_structure import HEADING_CONTAINERS, HEADING_FIELDS
        covered = {(slug, attr) for slug, rules in HEADING_FIELDS.items() for attr, *_ in rules}
        covered |= set(HEADING_CONTAINERS.items())
        in_schema = set()
        for slug in SCHEMA.slugs:
            for name, field in SCHEMA.module(slug).fields.items():
                if name.endswith("_level") and set(field.get("options") or ()) == {f"h{i}" for i in range(1, 7)}:
                    in_schema.add((slug, name))
        self.assertEqual(in_schema - covered, set())
        self.assertEqual(covered - in_schema, set())

    def test_valid_fixtures_have_no_heading_errors(self):
        for path in sorted((FIXTURES / "valid").glob("*.txt")):
            with self.subTest(path.name):
                errors = [c for c in codes(path.read_text()) if c.startswith("E_")]
                self.assertEqual(errors, [])

    def test_handwritten_landing_heading_outline_is_clean(self):
        self.assertEqual(codes((FIXTURES / "valid" / "handwritten-landing.txt").read_text()), [])


if __name__ == "__main__":
    unittest.main()
