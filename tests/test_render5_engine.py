"""Offline checks of the Divi 5 Python renderer's engine (research/divi5/python-renderer/divi5_render, Task 21-R5b).

The parity with real Divi 5 is tests/test_render5_fidelity.py; these pin the documented behaviour that needs
no Playground: variables and relative colours, preset class names (checked against a live Divi 5 page),
selector states, key-level coverage, placeholders for unsupported and site-data modules, and the page shell.
Tests that read module metadata need a cached Divi 5 and are skipped without one.
"""
import json
import re
import unittest

from _paths import RENDERER5, FIXTURES5, ROOT  # noqa: F401  (puts scripts on sys.path)
import sys as _sys
_sys.path.insert(0, str(RENDERER5))  # the parked renderer, only for these tests

import fetch_divi
from divi5_render import base, css, values

V = "5.13.1"


def block(name, attrs, inner=""):
    a = json.dumps(attrs, separators=(",", ":"))
    return f"<!-- wp:divi/{name} {a} -->{inner}<!-- /wp:divi/{name} -->" if inner or name in (
        "section", "row", "column", "row-inner", "column-inner") else f"<!-- wp:divi/{name} {a} /-->"


def page(*modules):
    blk = {"module": {"decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}}, "builderVersion": V}
    col = {"module": {"advanced": {"type": {"desktop": {"value": "4_4"}}},
                      "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}}, "builderVersion": V}
    return block("section", blk, block("row", blk, block("column", col, "".join(modules))))


class ValuesTest(unittest.TestCase):
    def test_variables_print_as_css_custom_properties(self):
        v = values.Values({})
        ref = '$variable({"type":"content","value":{"name":"gvid-pad","settings":{}}})$'
        self.assertEqual(v.resolve(f"{ref} 10px"), "var(--gvid-pad) 10px")

    def test_colour_with_settings_is_a_relative_colour_of_the_site_value(self):
        v = values.Values({"colors": {"global": {"gcid-navy": {"value": "#0B2A3C"}}}})
        ref = '$variable({"type":"color","value":{"name":"gcid-navy","settings":{"opacity":85}}})$'
        self.assertEqual(v.resolve(ref), "hsl(from #0B2A3C calc(h + 0) calc(s + 0) calc(l + 0) / 0.85)")
        # unknown colour value: the plain variable
        self.assertEqual(values.Values({}).resolve(ref), "var(--gcid-navy)")

    def test_attr_value_inherits_desktop_to_tablet_to_phone(self):
        attr = {"desktop": {"value": {"a": 1, "b": 2}}, "tablet": {"value": {"b": 3}}}
        self.assertEqual(values.attr_value(attr, "phone", "value", "getAndInheritAll"), {"a": 1, "b": 3})
        self.assertEqual(values.attr_value(attr, "tablet", "hover", "getOrInheritAll"), {"a": 1, "b": 3})
        self.assertIsNone(values.attr_value(attr, "tablet", "hover", "get"))

    def test_esc_url_encodes_ampersands_like_wordpress(self):
        self.assertEqual(values.esc_url("https://x.test/a.jpg?w=1&q=2"), "https://x.test/a.jpg?w=1&#038;q=2")


class SelectorTest(unittest.TestCase):
    def test_hover_goes_before_a_pseudo_element(self):
        self.assertEqual(css.hover_selector(".a .b, .c:after"), ".a .b:hover, .c:hover:after")
        self.assertEqual(css.hover_selector(".a:hover"), ".a:hover")

    def test_statements_split_declarations_over_property_selectors(self):
        class C:
            sheet = css.Sheet()
        ctx = C()
        ctx.css = ctx.sheet
        attr = {"desktop": {"value": {"padding": {"top": "1px"}, "margin": {"top": "2px"}}},
                "tablet": {"value": {"padding": {"top": "3px"}}}}
        from divi5_render.options import spacing_decls
        css.statements(ctx, attr, spacing_decls, selector=".w", important=True,
                       property_selectors={"desktop": {"value": {"padding": ".w .b, .w .b:hover"}}})
        text = ctx.css.text()
        self.assertIn(".w{margin-top:2px!important}", text)
        self.assertIn(".w .b,.w .b:hover{padding-top:1px!important}", text)
        self.assertIn("@media only screen and (max-width:980px){.w .b,.w .b:hover{padding-top:3px!important}}", text)


class PresetClassTest(unittest.TestCase):
    def test_group_preset_class_matches_a_live_divi5_page(self):
        # tests/fixtures/divi5/html/r6-tokens-trace.html (live Divi 5.13.1) prints exactly this class for
        # groupPreset {"designTitleText": {"presetId": ["r6fontpreset1"], "groupName": "divi/font"}} on a heading.
        live = (FIXTURES5 / "html" / "r6-tokens-trace.html").read_text()
        cls = base.preset_class("group", module="divi/heading", group="divi/font", group_id="designTitleText",
                                preset_id="r6fontpreset1")
        self.assertEqual(cls, "preset--group--divi-heading--divi-font--hp5h6dj--r6fontpreset1")
        self.assertIn(cls, live)

    def test_module_preset_stack_drops_default_ids(self):
        self.assertEqual(base.preset_stack(["default", "", "_initial", "abc", "def"]), ["abc", "def"])
        self.assertEqual(base.preset_stack("default"), [])
        self.assertEqual(base.preset_class("module", module="divi/button", preset_id="abc"),
                         "preset--module--divi-button--abc")

    def test_group_presets_known_from_tokens(self):
        self.assertEqual(base.known_group_presets({"group_presets": {"divi/font": [{"id": "g1", "uses": 2}]},
                                                   "presets": {"divi/button": [{"id": "m1"}]}}), {"g1"})


@unittest.skipIf(fetch_divi.theme_dir(V) is None, f"Divi {V} is not cached")
class RenderTest(unittest.TestCase):
    def render(self, src, tokens=None):
        import divi5_render
        r = divi5_render.render_page(src, divi_version=V, tokens=tokens)
        etl = r.html.split('<div class="et-l et-l--post">', 1)[1]
        return r, etl

    def test_unsupported_and_site_data_modules_render_placeholders_and_are_reported(self):
        r, etl = self.render(page(block("blurb", {"builderVersion": V}), block("blog", {"builderVersion": V})))
        self.assertIn("pp-unsupported", etl)
        self.assertIn("pp-site-data", etl)
        self.assertEqual(r.coverage["unsupported_modules"], {"blurb": 1})
        self.assertEqual(r.coverage["needs_site_data"], {"blog": 1})

    def test_coverage_names_unhonoured_keys_inside_a_value(self):
        text = block("text", {"content": {"innerContent": {"desktop": {"value": "<p>x</p>"}}},
                              "module": {"decoration": {
                                  "background": {"desktop": {"value": {"color": "#fff", "video": {"mp4": "a.mp4"}}}},
                                  "filters": {"desktop": {"value": {"saturate": "0%"}}},
                                  "spacing": {"desktop": {"value": {"padding": {"top": "4px"}}}},
                                  "sizing": {"desktop": {"sticky": {"width": "50%"}}}}},
                              "builderVersion": V})
        r, _ = self.render(page(text))
        ign = r.coverage["ignored"]
        self.assertIn("text:module.decoration.background.video.mp4", ign)
        self.assertIn("text:module.decoration.filters.saturate", ign)
        self.assertIn("text:module.decoration.sizing.width@sticky", ign)
        self.assertNotIn("text:module.decoration.background.color", ign)
        self.assertNotIn("text:module.decoration.spacing.padding.top", ign)

    def test_group_preset_class_only_for_presets_the_site_has(self):
        head = block("heading", {"title": {"innerContent": {"desktop": {"value": "Hi"}}},
                                 "groupPreset": {"designTitleText": {"presetId": ["r6fontpreset1"],
                                                                     "groupName": "divi/font"}},
                                 "modulePreset": ["default"], "builderVersion": V})
        _, etl = self.render(page(head))
        self.assertNotIn("preset--group", etl)  # a fresh site (the Playground truth) prints none either
        _, etl = self.render(page(head), {"group_presets": {"divi/font": [{"id": "r6fontpreset1"}]}})
        self.assertIn("preset--group--divi-heading--divi-font--hp5h6dj--r6fontpreset1", etl)

    def test_button_padding_is_copied_onto_hover(self):
        btn = block("button", {"button": {"innerContent": {"desktop": {"value": {"text": "Go", "linkUrl": "#"}}}},
                               "module": {"decoration": {"spacing": {"desktop": {"value": {"padding": {"top": "9px"}}}}}},
                               "builderVersion": V})
        r, _ = self.render(page(btn))
        builder_css = re.search(r'<style id="et-builder-module-design-python5-inline-styles">(.*?)</style>',
                                r.html, re.S).group(1)
        self.assertIn(".et_pb_button_0_wrapper .et_pb_button_0,.et_pb_button_0_wrapper .et_pb_button_0:hover"
                      "{padding-top:9px!important}", builder_css)

    def test_shell_embeds_theme_assets_without_file_urls_and_seeds_tokens(self):
        import divi5_render
        tokens = json.loads((ROOT / "Skill/divi-page-builder/recipes/divi5/sample-tokens.json").read_text())
        r = divi5_render.render_page(page(block("text", {"builderVersion": V})), divi_version=V, tokens=tokens,
                                     embed_assets=True)
        self.assertNotIn("file://", r.html)
        self.assertIn('<style id="pp-token-seed">:root:root{--gcid-r6navy0001:#0B2A3C;', r.html)
        self.assertIn(".preset--module--divi-button--r6btnpreset1", r.html)
        self.assertIn("et_block_section", r.html)  # a Divi 5 page for fidelity.py
