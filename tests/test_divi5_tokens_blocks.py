"""Design tokens from Divi 5 block content (tokens5_from_blocks.py)."""
import json
import unittest
from collections import Counter, defaultdict

from _paths import FIXTURES5, d5_fixtures
from divi5_blocks import canonical_json, get_attr, parse
from divi5_schema import load_schema5
from test_divi5_validate_values import V, block, page, var
from tokens5_from_blocks import tokens5_from_documents
from validate import validate_source

SCHEMA5 = load_schema5()
CONVERTED_LAYOUT = FIXTURES5 / "converted" / "divi-ai-layout.html"
AI_LAYOUT = FIXTURES5 / "divi-ai" / "layout.html"
DIVIDER_GCID = "gcid-828accbb-1ed2-407d-95be-20ab4e191566"


def tokens(*sources):
    return tokens5_from_documents([parse(s) for s in sources], SCHEMA5)


def section(children, **attrs):
    body = {"builderVersion": V, "module": {"decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}}}
    body.update(attrs)
    col = {"builderVersion": V, "module": {"advanced": {"type": {"desktop": {"value": "1_2"}}}}}
    row = {"builderVersion": V}
    return (f"<!-- wp:divi/section {canonical_json(body)} --><!-- wp:divi/row {canonical_json(row)} -->"
            f"<!-- wp:divi/column {canonical_json(col)} -->" + "".join(children)
            + "<!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->")


def heading(font=None, text="Our Services", bare=None, **extra):
    title = {"innerContent": {"desktop": {"value": text}}}
    if font is not None:
        title["decoration"] = {"font": {"font": font}}
    if bare is not None:
        title["decoration"] = {"font": bare}
    return block("heading", {"builderVersion": V, "title": title, **extra})


def _attrs_trees(skeletons):
    for node in skeletons:
        yield node["attrs"]
        yield from _attrs_trees(node["children"])


class ConvertedLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = CONVERTED_LAYOUT.read_text()
        cls.doc = parse(cls.src)
        cls.t = tokens5_from_documents([cls.doc], SCHEMA5)

    def test_blurb_style_counts_sum_to_the_blurbs(self):
        blurbs = sum(1 for b, _p, _parent in self.doc.walk() if b.name == "divi/blurb")
        self.assertGreater(blurbs, 0)
        self.assertEqual(sum(e["uses"] for e in self.t["module_styles"]["divi/blurb"]), blurbs)

    def test_presets_list_module_preset_ids_with_counts(self):
        expected = defaultdict(Counter)
        for b, _p, _parent in self.doc.walk():
            ids = b.attrs.get("modulePreset") if isinstance(b.attrs, dict) else None
            for pid in ([ids] if isinstance(ids, str) else ids or []):
                if pid != "default":
                    expected[b.name][pid] += 1
        self.assertTrue(expected)
        got = {name: {e["id"]: e["uses"] for e in entries} for name, entries in self.t["presets"].items()}
        self.assertEqual(got, {name: dict(c) for name, c in expected.items()})

    def test_variable_color_stays_verbatim_and_is_a_global_ref(self):
        ref = var(DIVIDER_GCID)
        colors = [e["attrs"]["divider"]["advanced"]["line"]["desktop"]["value"]["color"]
                  for e in self.t["module_styles"]["divi/divider"]
                  if "line" in e["attrs"].get("divider", {}).get("advanced", {})]
        self.assertIn(ref, colors)
        self.assertEqual(self.t["colors"]["global_refs"][DIVIDER_GCID]["uses"], 1)
        self.assertIn("divider.advanced.line.color", self.t["colors"]["global_refs"][DIVIDER_GCID]["roles"])
        self.assertNotIn(ref, [p["hex"] for p in self.t["colors"]["palette"]])

    def test_typography_scale_reads_h2_from_a_heading_module(self):
        fonts = [get_attr(b, "title.decoration.font.font", None, None) for b, _p, _parent in self.doc.walk()
                 if b.name == "divi/heading"]
        h2 = [f for f in fonts if (f or {}).get("desktop", {}).get("value", {}).get("headingLevel") == "h2"]
        self.assertTrue(h2)
        scale = self.t["typography"]["scale"]["h2"]
        families = {f["desktop"]["value"].get("family") for f in h2}
        sizes = {f["desktop"]["value"].get("size") for f in h2}
        self.assertIn(scale["font"], families)
        self.assertIn(scale["size"], sizes)
        self.assertIn("size_tablet", scale)

    def test_output_is_json(self):
        json.dumps(self.t)

    def test_page_validates_clean_against_its_own_tokens(self):
        codes = {f.code for f in validate_source(self.src, tokens=self.t)}
        self.assertFalse(codes & {"W5_UNKNOWN_PRESET", "W5_UNKNOWN_VARIABLE", "W_OFF_PALETTE_COLOR",
                                  "W_OFF_BRAND_FONT", "W_OFF_SCALE_SPACING"}, codes)


class ExemplarsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = tokens(AI_LAYOUT.read_text())

    def test_no_inner_content_in_section_exemplars(self):
        flat = json.dumps(self.t["section_exemplars"])
        self.assertIn("A Better-Looking Property Starts Here", AI_LAYOUT.read_text())
        self.assertNotIn("A Better-Looking Property Starts Here", flat)
        self.assertNotIn("Residential", flat)
        self.assertNotIn("innerContent", json.dumps(list(_attrs_trees(self.t["section_exemplars"]))))
        self.assertNotIn("unsplash", flat)

    def test_exemplar_keeps_design_structure_and_media_names(self):
        hero = self.t["section_exemplars"][0]
        self.assertEqual(hero["name"], "divi/section")
        self.assertEqual(hero["attrs"]["module"]["meta"]["adminLabel"]["desktop"]["value"], "Hero")
        bg = hero["attrs"]["module"]["decoration"]["background"]["desktop"]["value"]
        self.assertEqual(bg["gradient"]["enabled"], "on")
        self.assertNotIn("url", bg.get("image", {}))
        self.assertIn("module.decoration.background.image.url", hero["media"])
        self.assertEqual(hero["children"][0]["name"], "divi/row")
        self.assertNotIn("builderVersion", hero["attrs"])

    def test_legacy_attrs_are_left_out(self):
        self.assertNotIn("nextBackgroundColor", json.dumps(self.t["section_exemplars"]))
        self.assertNotIn("nextBackgroundColor", json.dumps(self.t["module_styles"]))
        legacy = tokens((FIXTURES5 / "invalid" / "legacy-attr.html").read_text())
        self.assertNotIn("column-1", json.dumps(legacy["module_styles"]))
        self.assertNotIn("column-1", json.dumps(legacy["section_exemplars"]))


class ClassificationTest(unittest.TestCase):
    def test_content_text_leaves_dropped_design_text_leaves_kept(self):
        form = block("contact-form", {"builderVersion": V, "module": {
            "advanced": {"successMessage": {"desktop": {"value": "Thanks, we will call you back."}}},
            "decoration": {"boxShadow": {"desktop": {"value": {"style": "preset2", "color": "#00000033"}}}}}})
        t = tokens(section([form]))
        (entry,) = t["module_styles"]["divi/contact-form"]
        self.assertNotIn("Thanks", json.dumps(t))
        self.assertEqual(entry["attrs"]["module"]["decoration"]["boxShadow"]["desktop"]["value"]["style"], "preset2")
        self.assertEqual(t["shapes"]["shadows"][0][1], 1)

    def test_button_text_and_link_are_content_html_attributes_are_captured(self):
        btn = block("button", {"builderVersion": V, "modulePreset": ["btnpreset1"], "button": {
            "innerContent": {"desktop": {"value": {"text": "Book now", "linkUrl": "https://x.example/book"}}},
            "decoration": {"background": {"desktop": {"value": {"color": "#F97316"}}},
                           "border": {"desktop": {"value": {"radius": {"sync": "on", "topLeft": "8px"}}}}}},
            "module": {"advanced": {"htmlAttributes": {"desktop": {"value": {"class": "cta-main", "id": "book"}}}},
                       "meta": {"adminLabel": {"desktop": {"value": "Main CTA"}}}}})
        dark = {"module": {"decoration": {"background": {"desktop": {"value": {"color": "#0b2a3c"}}}},
                           "meta": {"adminLabel": {"desktop": {"value": "Hero"}}}}}
        t = tokens(section([btn], **dark))
        (entry,) = t["module_styles"]["divi/button"]
        flat = json.dumps(entry["attrs"])
        self.assertNotIn("Book now", flat)
        self.assertNotIn("x.example", flat)
        self.assertNotIn("cta-main", flat)
        self.assertEqual(entry["attrs"]["button"]["decoration"]["background"]["desktop"]["value"]["color"], "#F97316")
        self.assertEqual(entry["html_attributes"], {"class": "cta-main", "id": "book"})
        self.assertEqual(entry["module_preset"], ["btnpreset1"])
        ctx = entry["contexts"][0]
        self.assertEqual((ctx["section_label"], ctx["section_tone"], ctx["column_type"], ctx["admin_label"]),
                         ("Hero", "dark", "1_2", "Main CTA"))
        self.assertEqual(ctx["section_background"]["color"], "#0b2a3c")
        self.assertEqual((ctx["section_index"], ctx["index_in_parent"]), (0, 0))
        self.assertIn({"hex": "#f97316", "uses": 1, "roles": ["button.decoration.background.color"]},
                      t["colors"]["palette"])
        self.assertIn([{"sync": "on", "topLeft": "8px"}, 1], t["shapes"]["radii"])

    def test_bare_font_is_ignored(self):
        t = tokens(section([heading(bare={"desktop": {"value": {"headingLevel": "h2", "size": "53px"}}})]))
        self.assertNotIn("h2", t["typography"]["scale"])
        self.assertNotIn("53px", json.dumps(t["module_styles"]))


class FixRound1Test(unittest.TestCase):
    def test_custom_css_records_slots_never_text(self):
        css = {"desktop": {"value": {"mainElement": 'background:url(https://x/y.jpg);',
                                     "before": 'content:"Call 555-0100";'}},
               "tablet": {"value": {"after": "color:red;"}}}
        t = tokens(section([block("text", {"builderVersion": V, "css": css, "content": {
            "innerContent": {"desktop": {"value": "<p>Hi</p>"}}}})]))
        flat = json.dumps(t)
        self.assertNotIn("555-0100", flat)
        self.assertNotIn("x/y.jpg", flat)
        (entry,) = t["module_styles"]["divi/text"]
        self.assertEqual(entry["custom_css_slots"], ["after", "before", "mainElement"])
        self.assertNotIn("custom_css", entry)

    def test_exemplars_keep_admin_label_on_sections_only(self):
        btn = block("button", {"builderVersion": V, "module": {"meta": {"adminLabel": {"desktop": {
            "value": "Main CTA"}}}}})
        t = tokens(section([btn], module={"meta": {"adminLabel": {"desktop": {"value": "Hero"}}}}))
        hero = t["section_exemplars"][0]
        self.assertEqual(hero["attrs"]["module"]["meta"]["adminLabel"]["desktop"]["value"], "Hero")
        self.assertNotIn("Main CTA", json.dumps(t["section_exemplars"]))

    def test_contexts_are_capped(self):
        blurb = block("blurb", {"builderVersion": V, "title": {"decoration": {"font": {"font": {
            "desktop": {"value": {"size": "22px"}}}}}}})
        (entry,) = tokens(section([blurb] * 7))["module_styles"]["divi/blurb"]
        self.assertEqual(entry["uses"], 7)
        self.assertEqual(len(entry["contexts"]), 5)


class TypographyTest(unittest.TestCase):
    def test_default_heading_level_comes_from_the_schema(self):
        t = tokens(section([heading({"desktop": {"value": {"family": "Montserrat", "size": "56px"}},
                                     "tablet": {"value": {"size": "42px"}}}),
                            block("blurb", {"builderVersion": V, "title": {"decoration": {"font": {"font": {
                                "desktop": {"value": {"family": "Lato", "size": "22px"}}}}}}})]))
        scale = t["typography"]["scale"]
        self.assertEqual((scale["h1"]["font"], scale["h1"]["size"], scale["h1"]["size_tablet"]),
                         ("Montserrat", "56px", "42px"))
        self.assertEqual(scale["h4"]["font"], "Lato")
        self.assertIn(t["typography"]["heading_font"], ("Montserrat", "Lato"))

    def test_body_font_from_text_modules(self):
        text = block("text", {"builderVersion": V, "content": {
            "innerContent": {"desktop": {"value": "<p>Hi</p>"}},
            "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Lato", "size": "17px"}}}}}}}})
        t = tokens(section([text, text]))
        self.assertEqual(t["typography"]["body_font"], "Lato")
        self.assertEqual(t["typography"]["body"]["size"], "17px")

    def test_variable_font_kept_verbatim(self):
        ref = var("gvid-display", "content")
        t = tokens(section([heading({"desktop": {"value": {"family": ref, "headingLevel": "h2"}}})]))
        self.assertEqual(t["typography"]["scale"]["h2"]["font"], ref)
        self.assertEqual(t["variables_refs"]["gvid-display"]["kind"], "fonts")


class SpacingPresetsVariablesTest(unittest.TestCase):
    def test_section_padding_row_width_gutter_and_number_variable(self):
        ref = var("gvid-space", "content")
        pad = {"module": {"decoration": {"spacing": {"desktop": {"value": {
            "padding": {"top": ref, "right": "", "bottom": ref, "left": ""}}}}}}}
        row = {"builderVersion": V, "module": {"decoration": {"sizing": {"desktop": {"value": {
            "width": "90%", "maxWidth": "1200px"}}}}, "advanced": {"gutter": {"desktop": {"value": {
                "enable": "on", "width": "2"}}}}}}
        src = section([], **pad).replace('<!-- wp:divi/row {"builderVersion":"%s"}' % V,
                                         f"<!-- wp:divi/row {canonical_json(row)}")
        t = tokens(src)
        self.assertEqual(t["spacing"]["section_padding"],
                         [[{"top": ref, "right": "", "bottom": ref, "left": ""}, 1]])
        self.assertEqual(t["spacing"]["row"]["width"], [["90%", 1]])
        self.assertEqual(t["spacing"]["row"]["max_width"], [["1200px", 1]])
        self.assertEqual(t["spacing"]["gutters"], [[{"enable": "on", "width": "2"}, 1]])
        refs = t["variables_refs"]["gvid-space"]
        self.assertEqual((refs["uses"], refs["kind"]), (2, "numbers"))
        self.assertEqual(refs["roles"], ["module.decoration.spacing.padding"])

    def test_group_presets(self):
        h = heading({"desktop": {"value": {"size": "40px"}}}, modulePreset=["r6heading1"],
                    groupPreset={"designTitleText": {"presetId": ["r6fontpreset1"], "groupName": "divi/font"}})
        t = tokens(section([h]))
        self.assertEqual(t["presets"]["divi/heading"], [{"id": "r6heading1", "uses": 1}])
        self.assertEqual(t["group_presets"]["divi/font"],
                         [{"id": "r6fontpreset1", "uses": 1, "module": "divi/heading", "group_id": "designTitleText"}])
        (entry,) = t["module_styles"]["divi/heading"]
        self.assertEqual(entry["group_presets"],
                         {"designTitleText": {"presetId": ["r6fontpreset1"], "groupName": "divi/font"}})


class ValidatorReadsTokensTest(unittest.TestCase):
    """The validator must accept what the tokens say the site uses."""

    def test_presets_global_refs_variable_refs_and_module_fonts_are_known(self):
        ref = var("gcid-brand01")
        num = var("gvid-radius1", "content")
        blurb = block("blurb", {"builderVersion": V, "modulePreset": ["blurbpreset1"], "title": {
            "innerContent": {"desktop": {"value": "Fast"}},
            "decoration": {"font": {"font": {"desktop": {"value": {"family": "Poppins", "color": ref}}}}}},
            "module": {"decoration": {"border": {"desktop": {"value": {"radius": {"sync": "on", "topLeft": num}}}}}}})
        btn = block("button", {"builderVersion": V, "button": {
            "innerContent": {"desktop": {"value": {"text": "Go"}}},
            "decoration": {"font": {"font": {"desktop": {"value": {"family": "Karla"}}}}}}})
        src = page(blurb, btn)
        t = tokens(src)
        self.assertNotIn("Karla", json.dumps(t["typography"]))
        found = {f.code: f for f in validate_source(src, tokens=t)}
        for code in ("W5_UNKNOWN_PRESET", "W5_UNKNOWN_VARIABLE", "W_OFF_BRAND_FONT"):
            self.assertNotIn(code, found, found.get(code))


class AllFixturesTest(unittest.TestCase):
    def test_every_fixture_page_validates_clean_against_its_own_tokens(self):
        for path in d5_fixtures():
            with self.subTest(path=path.name):
                src = path.read_text()
                t = tokens(src)
                json.dumps(t)
                codes = {f.code for f in validate_source(src, tokens=t)}
                self.assertFalse(codes & {"W5_UNKNOWN_PRESET", "W5_UNKNOWN_VARIABLE", "W_OFF_PALETTE_COLOR",
                                          "W_OFF_BRAND_FONT", "W_OFF_SCALE_SPACING"}, codes)


if __name__ == "__main__":
    unittest.main()
