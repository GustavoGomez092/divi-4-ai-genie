"""Divi 5 validator: attribute paths, value types, escaping, presets and variables (divi5_checks_values)."""
import json
import unittest

from _paths import FIXTURES5, d5_fixtures
from divi5_blocks import canonical_json, parse
from divi5_checks_values import check_attributes5, value_problems5
from divi5_schema import load_schema5
from validate import Reporter, validate_source

INVALID = FIXTURES5 / "invalid"
# fixture -> (code, level); error fixtures must produce exactly that one error code.
EXPECT = {
    "unknown-attr.html": ("E5_UNKNOWN_ATTR", "error"),
    "bad-breakpoint.html": ("E5_BAD_BREAKPOINT", "error"),
    "bad-state.html": ("E5_BAD_STATE", "error"),
    "bad-color.html": ("E5_BAD_VALUE", "error"),
    "bad-unit.html": ("E5_BAD_VALUE", "error"),
    "bad-enum.html": ("E5_BAD_VALUE", "error"),
    "bad-variable.html": ("E5_BAD_VARIABLE", "error"),
    "noncanonical-lt.html": ("E5_NONCANONICAL", "error"),
    "unknown-preset.html": ("W5_UNKNOWN_PRESET", "warning"),
    "shortcode-brackets.html": ("W5_SHORTCODE_BRACKETS", "warning"),
}
VALUE_CODES = {"E5_UNKNOWN_ATTR", "E5_BAD_BREAKPOINT", "W5_BREAKPOINT_DISABLED", "E5_BAD_STATE", "E5_BAD_VALUE",
               "E5_BAD_VARIABLE", "W5_UNKNOWN_VARIABLE", "W5_UNKNOWN_PRESET", "E5_NONCANONICAL",
               "W5_SHORTCODE_BRACKETS", "W_EXTERNAL_IMAGE", "W5_NO_ALT", "W5_BUILDER_VERSION",
               "W5_HOVER_WITHOUT_DESKTOP"}
LAYOUT = {"decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}}
V = "5.13.1"


def _signup_quirk(f):
    # Known converter quirk: signup custom fields stay as a D4 shortcode string (research/divi5/schema.md).
    return "signup" in f.tag and f.attr.startswith("content")


# Heading findings of converted pages are the Divi 4 source pages' own (two h1s there too); HeadingParity5Test in
# test_divi5_validate_structure.py pins them to the Divi 4 validator's findings. They are content, not schema, errors.
PAGE_CONTENT_CODES = {"E5_MULTIPLE_H1"}


def var(name, vtype="color", settings=None):
    return "$variable(" + json.dumps({"type": vtype, "value": {"name": name, "settings": settings or {}}},
                                     separators=(",", ":")) + ")$"


def block(name, attrs, raw=None):
    return f"<!-- wp:divi/{name} {raw if raw is not None else canonical_json(attrs)} /-->"


def page(*modules):
    col = canonical_json({"module": {"advanced": {"type": {"desktop": {"value": "4_4"}}}, **LAYOUT},
                          "builderVersion": V})
    wrap = canonical_json({"builderVersion": V, "module": LAYOUT})
    return ("<!-- wp:divi/placeholder -->"
            f"<!-- wp:divi/section {wrap} --><!-- wp:divi/row {wrap} --><!-- wp:divi/column {col} -->"
            + "".join(modules) +
            "<!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section --><!-- /wp:divi/placeholder -->")


def text_attrs(html="<p>Hello</p>", **extra):
    attrs = {"builderVersion": V, "content": {"innerContent": {"desktop": {"value": html}}}}
    attrs.update(extra)
    return attrs


def run(src, **kw):
    """Findings of check_attributes5 alone (not the structure checks)."""
    doc = parse(src)
    report = Reporter(doc)
    check_attributes5(doc, load_schema5(), report, **kw)
    return report.findings


def codes(src, **kw):
    return [f.code for f in run(src, **kw)]


class InvalidFixturesTest(unittest.TestCase):
    def test_each_fixture_reports_its_code(self):
        for name, (code, level) in EXPECT.items():
            with self.subTest(name):
                findings = validate_source((INVALID / name).read_text(), fragment=True)
                self.assertIn(code, [f.code for f in findings if f.level == level])
                errors = {f.code for f in findings if f.level == "error"}
                self.assertEqual(errors, {code} if level == "error" else set())

    def test_readme_lists_every_fixture(self):
        readme = (INVALID / "README.md").read_text()
        for name, (code, _level) in EXPECT.items():
            self.assertIn(f"| `{name}` | `{code}` |", readme)


class ValidCorpusTest(unittest.TestCase):
    def test_valid_fixtures_have_no_errors(self):
        """The whole validator (structure + headings + values) finds no error in real Divi 5 content."""
        bad = []
        for p in d5_fixtures():
            for f in validate_source(p.read_text(), fragment=True):
                if f.level == "error" and not _signup_quirk(f) and f.code not in PAGE_CONTENT_CODES:
                    bad.append((p.name, f.code, f.tag, f.attr, f.value[:80], f.message))
        self.assertEqual(bad, [])


class ValueProblemsTest(unittest.TestCase):
    def ok(self, leaf, *values):
        for v in values:
            self.assertEqual(value_problems5(leaf, v), [], f"{leaf['type']} {v!r}")

    def bad(self, leaf, *values):
        for v in values:
            self.assertNotEqual(value_problems5(leaf, v), [], f"{leaf['type']} {v!r}")

    def test_color(self):
        leaf = {"type": "color"}
        self.ok(leaf, "#fff", "#FFFA", "#0f172a", "#0F172A80", "rgb(0,0,0)", "RGBA(255,255,255,0)",
                "rgba(0, 0, 0, 0.12)", "hsl(210 50% 40%)", "hsla(210,50%,40%,.5)", "transparent", "",
                "hsl(from var(--gcid-x) calc(h + 0) calc(s + 0) calc(l + 30))", "var(--gcid-primary-color)",
                var("gcid-primary-color"), var("gcid-828accbb-1ed2", settings={"opacity": 50, "lightness": 30}))
        self.bad(leaf, "#12345", "#ggg", "red", "12", "rgb(0,0,0", "gcid-primary-color", 12, None, {"color": "#fff"},
                 var("gvid-x", "content"), "#fff " + var("gcid-a"))

    def test_length(self):
        leaf = {"type": "length"}
        self.ok(leaf, "10px", "-12px", "1.4em", "100%", "0", "0px", "auto", "none", "600ms", "0deg", "",
                "calc(100% - 20px)", "clamp(48px, 8vw, 96px)", "min(10px, 2vw)", "var(--gvid-x)",
                var("gvid-r6radius01", "content"), 0)
        self.bad(leaf, "10pz", "px", "ten", "10 px", True, [], var("gcid-a", "color"))
        units = {"type": "length", "units": ["px", "em"]}
        self.ok(units, "10px", "2em", "0", "auto")
        self.bad(units, "10%", "3vw")

    def test_length_parity_with_divi4(self):
        """Divi 5 writes lineHeight/letterSpacing/sizes verbatim into CSS (Font.php); like Divi 4's _length_ok, a
        unitless number and the CSS keywords are fine, plus the intrinsic sizing keywords."""
        for leaf in ({"type": "length"}, {"type": "length", "units": ["px", "em"]}):
            self.ok(leaf, "1.5", "12", "-2", 12, 1.7, "normal", "unset", "Normal", "inherit", "initial",
                    "fit-content", "min-content", "max-content")
        self.bad({"type": "length"}, "wide", "1.5.2", "fit-contents")

    def test_number(self):
        leaf = {"type": "number"}
        self.ok(leaf, 2, -118.2437, "2", "0.4", "-3", "", var("gvid-n", "content"))
        self.bad(leaf, "two", "2px", True, None, [1])

    def test_enum(self):
        leaf = {"type": "enum", "options": ["h1", "h2"]}
        self.ok(leaf, "h1", "")
        self.bad(leaf, "h7", "H1", 1, ["h1"])
        multi = {"type": "enum", "options": ["a", "b"], "multiple": True}
        self.ok(multi, ["a", "b"], "a", [])
        self.bad(multi, ["a", "c"])

    def test_onoff(self):
        leaf = {"type": "onoff"}
        self.ok(leaf, "on", "off", "")
        self.bad(leaf, "yes", True, "ON")

    def test_url_and_image(self):
        for t in ("url", "image"):
            leaf = {"type": t}
            self.ok(leaf, "https://example.com/a.jpg", "/wp-content/uploads/a.jpg", "#book", "mailto:a@b.c",
                    "tel:+13055550100", "", var("gvid-link", "content"))
            self.bad(leaf, 12, {"src": "a.jpg"}, "https://exa mple.com/a b.jpg", "a\nb")

    def test_icon(self):
        leaf = {"type": "icon"}
        self.ok(leaf, {"unicode": "&#xf0a9;", "type": "fa", "weight": "900"},
                {"unicode": "&#xe03b;", "type": "divi", "weight": "400"})
        self.bad(leaf, "&#xf0a9;||fa||900", {"unicode": "&#xf0a9;", "type": "fa"},
                 {"unicode": "&#xf0a9;", "type": "fontawesome", "weight": "900"},
                 {"unicode": "&#xf0a9;", "type": "fa", "weight": "900", "size": "2"})

    def test_spacing(self):
        leaf = {"type": "spacing"}
        self.ok(leaf, {"top": "", "right": "", "bottom": "10px", "left": "", "syncVertical": "off",
                       "syncHorizontal": "off"}, {"top": "12px"}, {"left": var("gvid-pad", "content")})
        self.bad(leaf, {"top": "12pz"}, {"middle": "1px"}, {"syncVertical": "yes"}, "10px")

    def test_radius(self):
        leaf = {"type": "radius"}
        self.ok(leaf, {"sync": "on", "topLeft": "6px", "topRight": "6px", "bottomRight": "6px", "bottomLeft": "6px"},
                "8px", {"topLeft": ""})
        self.bad(leaf, {"top": "6px"}, {"topLeft": "6pz"}, {"sync": "maybe"})

    def test_gradient(self):
        leaf = {"type": "gradient"}
        self.ok(leaf, [{"position": 0, "color": "#2b87da"}, {"position": "100", "color": "rgba(0,0,0,0.4)"}],
                [{"position": "40%", "color": var("gcid-a")}], [], var("gvid-g", "gradient"))
        self.bad(leaf, [{"position": 0, "color": "nope"}], [{"position": "x", "color": "#fff"}],
                 [{"color": "#fff"}], "linear-gradient(#fff,#000)", {"stops": []})

    def test_text_html_and_fonts(self):
        self.ok({"type": "text"}, "hello", "", var("gvid-s", "content"))
        self.bad({"type": "text"}, 12, ["a"], {"a": 1})
        self.ok({"type": "html"}, "<p>x</p>", "")
        self.bad({"type": "html"}, None, 3)
        self.ok({"type": "font-family"}, "Montserrat", "Open Sans", var("gvid-font", "content"),
                var("--et_global_heading_font", "content"))
        self.bad({"type": "font-family"}, 12, ["Lato"])
        self.ok({"type": "font-weight"}, "700", 400, "normal", "bold", "Montserrat_weight", "Open Sans_weight", "",
                "variable", "750", 750, "1", "1000", 1000)
        self.bad({"type": "font-weight"}, "heavy", "0", "1001", 1001, 0, True, "Variable")

    def test_object_and_json(self):
        self.ok({"type": "object"}, {"x": "0deg"}, [], "")
        self.bad({"type": "object"}, 12, "x")
        self.ok({"type": "json"}, {"a": 1}, [1, 2], "x", 3, None)

    def test_malformed_variable_left_to_bad_variable(self):
        """A malformed $variable is E5_BAD_VARIABLE's job, not a value-type problem."""
        self.assertEqual(value_problems5({"type": "color"}, '$variable({"type":"color","value":{}})$'), [])


class CheckAttributesTest(unittest.TestCase):
    def test_unknown_attr_hint(self):
        f = [f for f in run(page(block("text", text_attrs(contnt={"innerContent": {"desktop": {"value": "x"}}}))))
             if f.code == "E5_UNKNOWN_ATTR"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].attr, "contnt.innerContent")
        self.assertIn("content", f[0].hint)

    def test_unknown_attr_reported_once_across_breakpoints(self):
        bogus = {"desktop": {"value": "x"}, "tablet": {"value": "y"}, "phone": {"value": "z"}}
        spacing = {"desktop": {"value": {"marginz": {"top": "1px"}}}, "tablet": {"value": {"marginz": {"top": "2px"}}}}
        attrs = text_attrs(contnt={"innerContent": bogus}, module={"decoration": {"spacing": spacing}})
        f = [f.attr for f in run(page(block("text", attrs))) if f.code == "E5_UNKNOWN_ATTR"]
        self.assertEqual(f, ["contnt.innerContent", "module.decoration.spacing.marginz"])

    def test_unknown_key_inside_object_value(self):
        attrs = text_attrs(module={"decoration": {"spacing": {"desktop": {"value": {"marginz": {"top": "1px"}}}}}})
        f = [f for f in run(page(block("text", attrs))) if f.code == "E5_UNKNOWN_ATTR"]
        self.assertEqual([x.attr for x in f], ["module.decoration.spacing.marginz"])

    def test_missing_breakpoint_wrapper(self):
        attrs = text_attrs()
        attrs["content"]["innerContent"] = "<p>bare</p>"
        self.assertIn("E5_BAD_BREAKPOINT", codes(page(block("text", attrs))))

    def test_attribute_beside_a_breakpoint_is_not_a_breakpoint(self):
        """{"innerContent": {...}, "desktop": {...}} (the signup converter quirk) is an attribute object with a stray
        desktop key, not a breakpoint map with a breakpoint called innerContent."""
        attrs = text_attrs()
        attrs["content"]["desktop"] = {"value": "x"}
        f = [(f.code, f.attr) for f in run(page(block("text", attrs))) if f.level == "error"]
        self.assertEqual(f, [("E5_UNKNOWN_ATTR", "content.desktop.value")])

    def body_font(self, value):
        font = {"desktop": {"value": value}}
        return page(block("text", text_attrs(content={"innerContent": {"desktop": {"value": "<p>x</p>"}},
                                                      "decoration": {"bodyFont": {"body": {"font": font}}}})))

    def test_variable_font_weight(self):
        """Divi 5.13 variable fonts: weight "variable" with weightFineTune or variationSettings (Font.php:340-360)."""
        for value in ({"weight": "variable", "weightFineTune": "650"},
                      {"weight": "variable", "variationSettings": {"wght": 650}},
                      {"family": "Inter", "weight": "variable", "variationSettings": {"wght": 650, "opsz": "14"},
                       "opticalSizing": "auto"}):
            with self.subTest(value=value):
                self.assertEqual([(f.code, f.attr) for f in run(self.body_font(value)) if f.level == "error"], [])

    def test_font_weight_off_the_hundreds_warns(self):
        found = [(f.level, f.code, f.value) for f in run(self.body_font({"weight": "750"}))
                 if f.code in ("W_FONT_WEIGHT", "E5_BAD_VALUE")]
        self.assertEqual(found, [("warning", "W_FONT_WEIGHT", "750")])
        for weight in ("700", "variable", "Montserrat_weight", "bold"):
            self.assertNotIn("W_FONT_WEIGHT", codes(self.body_font({"weight": weight})))

    def test_bp_false_leaf_on_tablet(self):
        font = {"desktop": {"value": {"headingLevel": "h2"}}, "tablet": {"value": {"headingLevel": "h3"}}}
        attrs = {"builderVersion": V, "title": {"innerContent": {"desktop": {"value": "Hi"}},
                                                "decoration": {"font": {"font": font}}}}
        f = [f for f in run(page(block("heading", attrs))) if f.code == "E5_BAD_BREAKPOINT"]
        self.assertEqual([x.attr for x in f], ["title.decoration.font.font.headingLevel"])

    def test_disabled_breakpoints_warn(self):
        attrs = text_attrs()
        attrs["content"]["innerContent"]["widescreen"] = {"value": "<p>Wide</p>"}
        c = codes(page(block("text", attrs)))
        self.assertIn("W5_BREAKPOINT_DISABLED", c)
        self.assertNotIn("E5_BAD_BREAKPOINT", c)

    def test_disabled_on_pseudo_breakpoints_ok(self):
        attrs = text_attrs(module={"decoration": {"disabledOn": {"tabletOnly": {"value": "on"}}}})
        c = codes(page(block("text", attrs)))
        self.assertNotIn("E5_BAD_BREAKPOINT", c)
        self.assertNotIn("W5_HOVER_WITHOUT_DESKTOP", c)

    def test_bad_value_reports_leaf(self):
        attrs = text_attrs(module={"decoration": {"background": {"desktop": {"value": {"color": "bluish"}}}}})
        f = [f for f in run(page(block("text", attrs))) if f.code == "E5_BAD_VALUE"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0].attr, "module.decoration.background.color")
        self.assertEqual(f[0].value, "bluish")

    def test_bad_variable_anywhere(self):
        html = '<p>$variable({"type":"content","value":{"name":"post_title"})$</p>'  # missing a brace
        self.assertIn("E5_BAD_VARIABLE", codes(page(block("text", text_attrs(html)))))
        no_type = '$variable({"value":{"name":"gcid-a"}})$'
        attrs = text_attrs(module={"decoration": {"background": {"desktop": {"value": {"color": no_type}}}}})
        c = codes(page(block("text", attrs)))
        self.assertIn("E5_BAD_VARIABLE", c)
        self.assertNotIn("E5_BAD_VALUE", c)

    def test_unknown_variable_only_with_tokens(self):
        attrs = text_attrs(module={"decoration": {"background": {"desktop": {"value": {"color": var("gcid-nope")}}}}})
        src = page(block("text", attrs))
        self.assertNotIn("W5_UNKNOWN_VARIABLE", codes(src))
        self.assertIn("W5_UNKNOWN_VARIABLE", codes(src, known_vars=frozenset({"gcid-other"})))
        self.assertNotIn("W5_UNKNOWN_VARIABLE", codes(src, known_vars=frozenset({"gcid-nope"})))

    def test_customizer_colors_always_known(self):
        for cid in ("gcid-primary-color", "gcid-secondary-color", "gcid-heading-color", "gcid-body-color",
                    "gcid-link-color"):
            attrs = text_attrs(module={"decoration": {"background": {"desktop": {"value": {"color": var(cid)}}}}})
            self.assertNotIn("W5_UNKNOWN_VARIABLE", codes(page(block("text", attrs)), known_vars=frozenset()))

    def test_unknown_presets(self):
        attrs = text_attrs(modulePreset=["default", "abc"],
                           groupPreset={"designText": {"presetId": ["grp1"], "groupName": "divi/font"}})
        f = [f for f in run(page(block("text", attrs))) if f.code == "W5_UNKNOWN_PRESET"]
        self.assertEqual(sorted(x.value for x in f), ["abc", "grp1"])
        self.assertIn('use ["default"]', f[0].message)
        self.assertNotIn("W5_UNKNOWN_PRESET", codes(page(block("text", attrs)),
                                                    known_presets=frozenset({"abc", "grp1"})))

    def test_noncanonical_forms(self):
        good = canonical_json(text_attrs("<p>a -- b & c</p>"))
        self.assertNotIn("E5_NONCANONICAL", codes(page(block("text", None, good))))
        for raw in (good.replace("\\u002d\\u002d", "--"), good.replace("\\u0026", "&"),
                    good.replace("\\u003e", ">"), good.replace("\\u003c", "<"),
                    canonical_json(text_attrs('<p class="x">y</p>')).replace("\\u0022", '\\"')):
            with self.subTest(raw=raw):
                self.assertIn("E5_NONCANONICAL", codes(page(block("text", None, raw))))
        vb_backslash = canonical_json(text_attrs("a\\b")).replace("\\u005c", "\\\\")
        self.assertNotIn("E5_NONCANONICAL", codes(page(block("text", None, vb_backslash))))

    def test_shortcode_brackets(self):
        self.assertIn("W5_SHORTCODE_BRACKETS", codes(page(block("text", text_attrs("<p>[contact-form]</p>")))))
        self.assertNotIn("W5_SHORTCODE_BRACKETS", codes(page(block("text", text_attrs("<p>&#91;x&#93; [1]</p>")))))

    def image(self, src, alt=None, attributes=None):
        inner = {"src": src}
        if alt is not None:
            inner["alt"] = alt
        attrs = {"builderVersion": V, "image": {"innerContent": {"desktop": {"value": inner}}}}
        if attributes:
            attrs["module"] = {"decoration": {"attributes": {"desktop": {"value": {"attributes": attributes}}}}}
        return page(block("image", attrs))

    def test_external_image(self):
        src = self.image("https://cdn.example.org/a.jpg", alt="A")
        self.assertIn("W_EXTERNAL_IMAGE", codes(src, site_host="client.example"))
        self.assertNotIn("W_EXTERNAL_IMAGE", codes(src))
        self.assertNotIn("W_EXTERNAL_IMAGE", codes(self.image("https://client.example/a.jpg", alt="A"),
                                                   site_host="client.example"))
        self.assertNotIn("W_EXTERNAL_IMAGE", codes(self.image("/wp-content/uploads/a.jpg", alt="A"),
                                                   site_host="client.example"))
        self.assertNotIn("W_EXTERNAL_IMAGE", codes(self.image("images/a.jpg", alt="A"), site_host="client.example"))

    def test_image_alt(self):
        self.assertIn("W5_NO_ALT", codes(self.image("/a.jpg")))
        self.assertIn("W5_NO_ALT", codes(self.image("/a.jpg", alt=" ")))
        self.assertNotIn("W5_NO_ALT", codes(self.image("/a.jpg", alt="A plumber")))
        attr = [{"id": "1", "name": "alt", "value": "Plumber", "adminLabel": "Image Alt", "targetElement": "image"}]
        self.assertNotIn("W5_NO_ALT", codes(self.image("/a.jpg", attributes=attr)))

    def test_builder_version(self):
        attrs = text_attrs()
        del attrs["builderVersion"]
        self.assertIn("W5_BUILDER_VERSION", codes(page(block("text", attrs))))
        src = page(block("text", text_attrs()))
        self.assertNotIn("W5_BUILDER_VERSION", codes(src))
        self.assertNotIn("W5_BUILDER_VERSION", codes(src, site_version=V))
        self.assertIn("W5_BUILDER_VERSION", codes(src, site_version="5.14.0"))

    def test_hover_without_desktop(self):
        bg = {"desktop": {"hover": {"color": "#fff"}}}
        self.assertIn("W5_HOVER_WITHOUT_DESKTOP",
                      codes(page(block("text", text_attrs(module={"decoration": {"background": bg}})))))
        bg = {"tablet": {"value": {"color": "#fff"}}}
        self.assertIn("W5_HOVER_WITHOUT_DESKTOP",
                      codes(page(block("text", text_attrs(module={"decoration": {"background": bg}})))))
        bg = {"desktop": {"value": {"color": "#000"}, "hover": {"color": "#fff"}},
              "phone": {"value": {"color": "#111"}}}
        self.assertNotIn("W5_HOVER_WITHOUT_DESKTOP",
                         codes(page(block("text", text_attrs(module={"decoration": {"background": bg}})))))


class TokensWiringTest(unittest.TestCase):
    SRC = page(block("text", text_attrs(
        modulePreset=["p-mod"], groupPreset={"designText": {"presetId": ["p-grp"], "groupName": "divi/font"}},
        module={"decoration": {"background": {"desktop": {"value": {"color": var("gcid-brand")}}}}})),
        block("image", {"builderVersion": V, "image": {"innerContent": {"desktop": {"value": {
            "src": "https://cdn.example.org/a.jpg", "alt": "A"}}}}}))

    def found(self, **kw):
        return [f.code for f in validate_source(self.SRC, fragment=True, **kw)]

    def test_without_tokens(self):
        c = self.found()
        self.assertIn("W5_UNKNOWN_PRESET", c)
        self.assertNotIn("W5_UNKNOWN_VARIABLE", c)
        self.assertNotIn("W_EXTERNAL_IMAGE", c)
        self.assertNotIn("W5_BUILDER_VERSION", c)

    def test_d4_shaped_tokens(self):
        tokens = {"site": {"url": "https://client.example", "divi_version": "5.14.0"},
                  "presets": {"divi/text": [{"uuid": "p-mod"}], "divi/font": [{"id": "p-grp"}]},
                  "colors": {"global": {"gcid-brand": {"value": "#123456"}}}}
        c = self.found(tokens=tokens)
        self.assertNotIn("W5_UNKNOWN_PRESET", c)
        self.assertNotIn("W5_UNKNOWN_VARIABLE", c)
        self.assertIn("W_EXTERNAL_IMAGE", c)
        self.assertIn("W5_BUILDER_VERSION", c)

    def test_d5_shaped_tokens(self):
        tokens = {"site": {"divi_version": V},
                  "presets": {"module": {"divi/text": [{"id": "p-mod"}]},
                              "group": {"divi/font": [{"id": "p-grp", "group_id": "designText"}]}},
                  "variables": {"numbers": {"gvid-r": {"value": "12px"}}}}
        c = self.found(tokens=tokens, site_url="https://cdn.example.org")
        self.assertNotIn("W5_UNKNOWN_PRESET", c)
        self.assertIn("W5_UNKNOWN_VARIABLE", c)  # gcid-brand is not in these tokens
        self.assertNotIn("W_EXTERNAL_IMAGE", c)
        self.assertNotIn("W5_BUILDER_VERSION", c)

    def test_group_presets_key(self):
        tokens = {"presets": {"divi/text": [{"id": "p-mod"}]}, "group_presets": {"divi/font": [{"id": "p-grp"}]},
                  "variables": {"gcid-brand": {}}}
        c = self.found(tokens=tokens)
        self.assertNotIn("W5_UNKNOWN_PRESET", c)
        self.assertNotIn("W5_UNKNOWN_VARIABLE", c)

    def test_malformed_tokens_do_not_crash(self):
        for tokens in ({"presets": [1, 2]}, {"presets": {"x": "y"}, "colors": [], "variables": "v", "site": None},
                       {"colors": {"global": ["gcid-a"]}}, {"colors": {"palette": 5}},
                       {"colors": {"palette": True}}, {"colors": {"palette": {"a": 1}}}, {"colors": {"palette": "x"}},
                       {"colors": {"palette": [None, 1, {"global": 3}]}}, {"site": {"url": 5, "divi_version": 5}}):
            with self.subTest(tokens=tokens):
                self.found(tokens=tokens)


if __name__ == "__main__":
    unittest.main()
