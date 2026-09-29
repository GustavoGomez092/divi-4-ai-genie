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
    "unitless-length.html": ("E5_UNITLESS_LENGTH", "error"),
    "gradient-disabled.html": ("E5_GRADIENT_DISABLED", "error"),
    "gradient-stop-position.html": ("E5_GRADIENT_STOP_POSITION", "error"),
    "bare-font.html": ("W5_BARE_FONT", "warning"),
    "legacy-attr.html": ("W5_LEGACY_ATTR", "warning"),
    "no-effect.html": ("W5_NO_EFFECT", "warning"),
}
VALUE_CODES = {"E5_UNKNOWN_ATTR", "E5_BAD_BREAKPOINT", "W5_BREAKPOINT_DISABLED", "E5_BAD_STATE", "E5_BAD_VALUE",
               "E5_BAD_VARIABLE", "W5_UNKNOWN_VARIABLE", "W5_UNKNOWN_PRESET", "E5_NONCANONICAL",
               "W5_SHORTCODE_BRACKETS", "W_EXTERNAL_IMAGE", "W5_NO_ALT", "W5_BUILDER_VERSION",
               "W5_HOVER_WITHOUT_DESKTOP", "E5_UNITLESS_LENGTH", "E5_GRADIENT_DISABLED", "E5_GRADIENT_STOP_POSITION",
               "W5_GRADIENT_MAYBE_DISABLED", "W5_BARE_FONT", "W5_LEGACY_ATTR", "W5_NO_EFFECT"}
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

    def test_silent_value_checks_on_valid_fixtures_find_only_the_one_legacy_attr(self):
        """Of the Task 9b checks, real Divi 5 content triggers exactly one finding: the Divi AI premade's
        nextBackgroundColor (doc-experiments.md §7), a W5_LEGACY_ATTR warning."""
        found = [(p.name, f.code, f.attr) for p in d5_fixtures()
                 for f in validate_source(p.read_text(), fragment=True)
                 if f.code in ("E5_UNITLESS_LENGTH", "E5_GRADIENT_DISABLED", "W5_GRADIENT_MAYBE_DISABLED",
                               "E5_GRADIENT_STOP_POSITION", "W5_BARE_FONT", "W5_LEGACY_ATTR")]
        self.assertEqual(found, [("layout.html", "W5_LEGACY_ATTR", "nextBackgroundColor")])


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
                [{"position": "40%", "color": var("gcid-a")}], [{"position": "4em", "color": "#fff"}], [],
                var("gvid-g", "gradient"))
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
        self.assertEqual(f[0].attr, "contnt.innerContent:desktop:value")
        self.assertIn("content", f[0].hint)

    def test_unknown_attr_reported_once_across_breakpoints(self):
        bogus = {"desktop": {"value": "x"}, "tablet": {"value": "y"}, "phone": {"value": "z"}}
        spacing = {"desktop": {"value": {"marginz": {"top": "1px"}}}, "tablet": {"value": {"marginz": {"top": "2px"}}}}
        attrs = text_attrs(contnt={"innerContent": bogus}, module={"decoration": {"spacing": spacing}})
        f = [f.attr for f in run(page(block("text", attrs))) if f.code == "E5_UNKNOWN_ATTR"]
        self.assertEqual(f, ["contnt.innerContent:desktop:value", "module.decoration.spacing.marginz:desktop:value"])

    def test_unknown_key_inside_object_value(self):
        attrs = text_attrs(module={"decoration": {"spacing": {"desktop": {"value": {"marginz": {"top": "1px"}}}}}})
        f = [f for f in run(page(block("text", attrs))) if f.code == "E5_UNKNOWN_ATTR"]
        self.assertEqual([x.attr for x in f], ["module.decoration.spacing.marginz:desktop:value"])

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
        self.assertEqual([x.attr for x in f], ["title.decoration.font.font.headingLevel:tablet:value"])

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
        self.assertEqual(f[0].attr, "module.decoration.background.color:desktop:value")
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


def module_attrs(**decoration):
    return text_attrs(module={"decoration": {k: {"desktop": {"value": v}} for k, v in decoration.items()}})


def found(src, *wanted, **kw):
    return [(f.level, f.code, f.attr) for f in run(src, **kw) if f.code in wanted]


class UnitlessLengthTest(unittest.TestCase):
    """doc-experiments.md §8: Divi prints a unitless length verbatim (padding-top:41!important), browsers drop it."""
    CODES = ("E5_UNITLESS_LENGTH", "E5_BAD_VALUE")

    def check(self, **decoration):
        return found(page(block("text", module_attrs(**decoration))), *self.CODES)

    def test_spacing_number_and_numeric_string(self):
        f = run(page(block("text", module_attrs(spacing={"padding": {"top": 41, "bottom": "42px", "left": "43"}}))))
        f = [x for x in f if x.code in self.CODES]
        self.assertEqual([(x.level, x.code, x.attr) for x in f],
                         [("error", "E5_UNITLESS_LENGTH", "module.decoration.spacing.padding.top:desktop:value"),
                          ("error", "E5_UNITLESS_LENGTH", "module.decoration.spacing.padding.left:desktop:value")])
        self.assertIn("41px", f[0].hint)

    def test_zero_is_fine(self):
        self.assertEqual(self.check(spacing={"margin": {"top": 0, "bottom": "0", "left": "0.0", "right": ""}}), [])

    def test_sizing_border_radius_and_shadow(self):
        self.assertEqual(
            self.check(sizing={"maxWidth": 720, "width": "90%"},
                       border={"styles": {"all": {"width": "2"}}, "radius": {"topLeft": 8, "topRight": "8px"}},
                       boxShadow={"horizontal": "4", "vertical": "4px", "blur": 10, "spread": "0"}),
            [("error", "E5_UNITLESS_LENGTH", "module.decoration.sizing.maxWidth:desktop:value"),
             ("error", "E5_UNITLESS_LENGTH", "module.decoration.border.styles.all.width:desktop:value"),
             ("error", "E5_UNITLESS_LENGTH", "module.decoration.border.radius.topLeft:desktop:value"),
             ("error", "E5_UNITLESS_LENGTH", "module.decoration.boxShadow.horizontal:desktop:value"),
             ("error", "E5_UNITLESS_LENGTH", "module.decoration.boxShadow.blur:desktop:value")])
        self.assertEqual(self.check(border={"radius": "8"}),
                         [("error", "E5_UNITLESS_LENGTH", "module.decoration.border.radius:desktop:value")])

    def test_position_offsets(self):
        self.assertEqual(self.check(position={"offset": {"horizontal": 10, "vertical": "10px"}}),
                         [("error", "E5_UNITLESS_LENGTH", "module.decoration.position.offset.horizontal:desktop:value")])

    def heading(self, font):
        attrs = {"builderVersion": V, "title": {"innerContent": {"desktop": {"value": "Hi"}},
                                                "decoration": {"font": {"font": {"desktop": {"value": font}}}}}}
        return found(page(block("heading", attrs)), *self.CODES)

    def test_font_size_and_letter_spacing_need_units(self):
        self.assertEqual(self.heading({"size": 40, "letterSpacing": "2", "headingLevel": "h2"}),
                         [("error", "E5_UNITLESS_LENGTH", "title.decoration.font.font.size:desktop:value"),
                          ("error", "E5_UNITLESS_LENGTH", "title.decoration.font.font.letterSpacing:desktop:value")])

    def test_unitless_allowed_where_css_takes_a_number(self):
        """lineHeight (CSS <number>), zIndex, flex grow/shrink, weights: unitless stays valid."""
        self.assertEqual(self.heading({"lineHeight": "1.5", "weight": "700", "headingLevel": "h2"}), [])
        self.assertEqual(self.heading({"lineHeight": 1.2}), [])
        self.assertEqual(self.check(zIndex="10", sizing={"flexGrow": "1", "flexShrink": 0}), [])

    def test_leaf_units_listing_empty_string_allows_unitless(self):
        from divi5_checks_values import unitless_lengths5
        self.assertEqual(unitless_lengths5("module.decoration.sizing.width", {"type": "length"}, "12"),
                         [("module.decoration.sizing.width", "12")])
        self.assertEqual(unitless_lengths5("module.decoration.sizing.width",
                                           {"type": "length", "units": ["", "px"]}, "12"), [])
        self.assertEqual(unitless_lengths5("title.decoration.font.font.lineHeight", {"type": "length"}, "12"), [])


class GradientTest(unittest.TestCase):
    """doc-experiments.md §8: a gradient without "enabled": "on", or with "0%" stop positions, renders nothing."""
    CODES = ("E5_GRADIENT_DISABLED", "E5_GRADIENT_STOP_POSITION", "E5_BAD_VALUE")
    STOPS = [{"position": 0, "color": "#1e3a8a"}, {"position": 100, "color": "#3b82f6"}]

    def bg(self, background):
        return found(page(block("text", text_attrs(module={"decoration": {"background": background}}))), *self.CODES)

    def test_missing_enabled(self):
        f = self.bg({"desktop": {"value": {"gradient": {"type": "linear", "direction": "90deg", "stops": self.STOPS}}}})
        self.assertEqual(f, [("error", "E5_GRADIENT_DISABLED", "module.decoration.background.gradient:desktop:value")])

    def test_enabled_on_and_explicit_off_are_fine(self):
        for enabled in ("on", "off"):  # Divi writes "off" with stops itself (divi-ai fixtures): a deliberate choice
            with self.subTest(enabled=enabled):
                self.assertEqual(self.bg({"desktop": {"value": {"gradient": {"enabled": enabled,
                                                                             "stops": self.STOPS}}}}), [])

    def test_state_inherits_enabled_from_desktop(self):
        bg = {"desktop": {"value": {"gradient": {"enabled": "on", "stops": self.STOPS}},
                          "hover": {"gradient": {"stops": self.STOPS[::-1]}}},
              "phone": {"value": {"gradient": {"direction": "180deg"}}}}
        self.assertEqual(self.bg(bg), [])
        bg = {"desktop": {"value": {"color": "#000"}, "hover": {"gradient": {"stops": self.STOPS}}}}
        self.assertEqual(self.bg(bg),
                         [("error", "E5_GRADIENT_DISABLED", "module.decoration.background.gradient:desktop:hover")])

    def test_phone_inherits_enabled_from_tablet(self):
        bg = {"desktop": {"value": {"color": "#000"}},
              "tablet": {"value": {"gradient": {"enabled": "on", "stops": self.STOPS}}},
              "phone": {"value": {"gradient": {"stops": self.STOPS[::-1]}}}}
        self.assertEqual(self.bg(bg), [])

    def test_hover_inherits_enabled_from_its_breakpoint_value(self):
        bg = {"desktop": {"value": {"color": "#000"}},
              "tablet": {"value": {"gradient": {"enabled": "on", "stops": self.STOPS}},
                         "hover": {"gradient": {"stops": self.STOPS[::-1]}}}}
        self.assertEqual(self.bg(bg), [])

    def test_tablet_does_not_inherit_from_phone(self):
        bg = {"desktop": {"value": {"color": "#000"}},
              "tablet": {"value": {"gradient": {"stops": self.STOPS}}},
              "phone": {"value": {"gradient": {"enabled": "on"}}}}
        self.assertEqual(self.bg(bg),
                         [("error", "E5_GRADIENT_DISABLED", "module.decoration.background.gradient:tablet:value")])

    def test_preset_may_enable_the_gradient(self):
        """A non-default modulePreset or a background group preset may supply "enabled": the finding is a warning."""
        bg = {"desktop": {"value": {"gradient": {"stops": self.STOPS}}}}
        for extra in ({"modulePreset": ["p1"]},
                      {"groupPreset": {"designBackground": {"presetId": ["g1"], "groupName": "divi/background"}}}):
            with self.subTest(extra=extra):
                attrs = text_attrs(module={"decoration": {"background": bg}}, **extra)
                f = [x for x in run(page(block("text", attrs))) if "GRADIENT" in x.code]
                self.assertEqual([(x.level, x.code, x.attr) for x in f],
                                 [("warning", "W5_GRADIENT_MAYBE_DISABLED",
                                   "module.decoration.background.gradient:desktop:value")])
                self.assertIn("unless its preset enables the gradient", f[0].message)
        for extra in ({"modulePreset": ["default"]},
                      {"groupPreset": {"designText": {"presetId": ["g1"], "groupName": "divi/font"}}}):
            with self.subTest(extra=extra):
                attrs = text_attrs(module={"decoration": {"background": bg}}, **extra)
                self.assertIn("E5_GRADIENT_DISABLED", codes(page(block("text", attrs))))

    def test_stop_position_with_unit(self):
        stops = [{"position": "0%", "color": "#1e3a8a"}, {"position": "100px", "color": "#3b82f6"}]
        f = self.bg({"desktop": {"value": {"gradient": {"enabled": "on", "stops": stops}}}})
        self.assertEqual(f, [("error", "E5_GRADIENT_STOP_POSITION",
                              "module.decoration.background.gradient.stops:desktop:value")])

    def test_plain_positions_are_fine(self):
        for stops in (self.STOPS, [{"position": "0", "color": "#fff"}, {"position": "100", "color": "#000"}]):
            self.assertEqual(self.bg({"desktop": {"value": {"gradient": {"enabled": "on", "stops": stops}}}}), [])

    def test_text_effects_gradient_has_no_enabled_flag(self):
        """textEffects gradients have no `enabled` key in Divi's schema, so they are not E5_GRADIENT_DISABLED."""
        attrs = {"builderVersion": V, "title": {"innerContent": {"desktop": {"value": "Hi"}}, "decoration": {"font": {
            "textEffects": {"desktop": {"value": {"gradient": {"type": "linear", "stops": self.STOPS}}}}}}}}
        self.assertEqual(found(page(block("heading", attrs)), *self.CODES), [])


class BareFontTest(unittest.TestCase):
    """doc-experiments.md §1: keys written directly under ….decoration.font render nothing."""

    def blurb(self, font):
        attrs = {"builderVersion": V, "title": {"innerContent": {"desktop": {"value": {"text": "Fast"}}},
                                                "decoration": {"font": font}}}
        return run(page(block("blurb", attrs)))

    def test_bare_font_warns(self):
        f = [x for x in self.blurb({"desktop": {"value": {"size": "51px", "color": "#ff0001"}}})
             if x.code == "W5_BARE_FONT"]
        self.assertEqual([(x.level, x.attr) for x in f], [("warning", "title.decoration.font:desktop:value")])
        self.assertIn("title.decoration.font.font", f[0].hint)
        self.assertIn("size", f[0].message)

    def test_toggle_open_toggle_bare_font(self):
        """doc-experiments.md §1: openToggle.decoration.font.desktop.value.color rendered no rule."""
        attrs = {"builderVersion": V, "title": {"innerContent": {"desktop": {"value": "Q"}}},
                 "openToggle": {"decoration": {"font": {"desktop": {"value": {"color": "#ff0005"}}}}}}
        f = [(x.level, x.code, x.attr) for x in run(page(block("toggle", attrs))) if x.level == "error"
             or x.code == "W5_BARE_FONT"]
        self.assertEqual(f, [("warning", "W5_BARE_FONT", "openToggle.decoration.font:desktop:value")])
        attrs["openToggle"]["decoration"]["font"] = {"font": {"desktop": {"value": {"color": "#ff0006"}}}}
        self.assertNotIn("W5_BARE_FONT", codes(page(block("toggle", attrs))))

    def test_font_font_text_shadow_and_text_effects_are_fine(self):
        f = self.blurb({"font": {"desktop": {"value": {"size": "52px"}}},
                        "textShadow": {"desktop": {"value": {"style": "preset1", "horizontal": "2px"}}},
                        "textEffects": {"desktop": {"value": {"strokeWidth": "1px"}}}})
        self.assertEqual([x.code for x in f if x.level == "error" or x.code == "W5_BARE_FONT"], [])


class LegacyAttrTest(unittest.TestCase):
    """doc-experiments.md §7: attributes only Divi's Divi 4 conversion map writes; no Divi 5 module code reads them."""

    def row(self, **attrs):
        return page().replace('<!-- wp:divi/row {', '<!-- wp:divi/row {' + canonical_json(attrs)[1:-1] + ',', 1)

    def test_row_column_attrs_warn_once_with_column_hint(self):
        src = self.row(**{"columns": {"column-1": {"spacing": {"desktop": {"value": {"padding": {"top": "10px"}}},
                                                               "phone": {"value": {"padding": {"top": "5px"}}}}}},
                          "padding1Phone": {"desktop": {"value": "10px|10px|10px|10px"}}})
        f = [x for x in run(src) if x.code == "W5_LEGACY_ATTR"]
        self.assertEqual(sorted((x.level, x.attr) for x in f),
                         [("warning", "columns.column-1.spacing"), ("warning", "padding1Phone")])
        self.assertTrue(all("divi/column" in x.hint for x in f))

    def test_non_column_legacy_attr_hint(self):
        attrs = text_attrs()
        attrs["content"]["desktop"] = {"value": "x"}  # not legacy: an unknown key
        self.assertNotIn("W5_LEGACY_ATTR", codes(page(block("text", attrs))))
        src = page().replace('<!-- wp:divi/section {', '<!-- wp:divi/section {"nextBackgroundColor":{"desktop":'
                                                         '{"value":"#ffffff"}},', 1)
        f = [x for x in run(src) if x.code == "W5_LEGACY_ATTR"]
        self.assertEqual([x.attr for x in f], ["nextBackgroundColor"])
        self.assertNotIn("divi/column", f[0].hint)

    def test_current_attrs_are_not_legacy(self):
        self.assertNotIn("W5_LEGACY_ATTR", codes(page(block("text", module_attrs(spacing={"padding": {"top": "1px"}})))))

    def test_compiled_legacy_lists_match_the_shared_predicate(self):
        """The docs generator and the validator share divi5_schema.is_legacy_attr; the compiled schema5 carries its
        result per module."""
        from _paths import SCHEMA5_RAW
        from divi5_schema import is_legacy_attr
        schema = load_schema5()
        for name in schema.names():
            raw = json.loads((SCHEMA5_RAW / "modules" / f"{name[5:]}.json").read_text())
            mod = schema.module(name)
            with self.subTest(name):
                self.assertEqual(sorted(mod.legacy), sorted(p for p in mod.attrs if is_legacy_attr(p, raw)))
        self.assertIn("padding1Phone", schema.module("row").legacy)
        self.assertNotIn("content", schema.module("accordion").legacy)  # module.json declares a `content` root

    def test_generator_uses_the_shared_predicate(self):
        import sys
        from _paths import TOOLS5
        sys.path.insert(0, str(TOOLS5))
        import generate_docs5
        import divi5_schema
        self.assertIs(generate_docs5.is_legacy_attr, divi5_schema.is_legacy_attr)
        self.assertIs(generate_docs5.is_legacy_column_attr, divi5_schema.is_legacy_column_attr)


def _d(value, **bps):
    out = {"desktop": {"value": value}}
    out.update({bp: {"value": v} for bp, v in bps.items()})
    return out


def _structure(name, ctype, children, layout=True, **advanced):
    """A structure block (section/row/column/…) around rendered children, in the layout form unless layout=False."""
    module = {}
    if ctype:
        module["advanced"] = {("columnStructure" if "row" in name else "type"): _d(ctype)}
    for k, v in advanced.items():
        module.setdefault("advanced", {})[k] = _d(v)
    if layout:
        module["decoration"] = {"layout": _d({"display": "block"})}
    attrs = {"builderVersion": V, "module": module}
    return f"<!-- wp:divi/{name} {canonical_json(attrs)} -->" + "".join(children) + f"<!-- /wp:divi/{name} -->"


def columns_page(ctype, *modules):
    """One row of three `ctype` columns (layout form); the modules go in the first column."""
    cols = [_structure("column", ctype, modules)] + [_structure("column", ctype, []) for _ in range(2)]
    row = _structure("row", ",".join([ctype] * 3), cols)
    return "<!-- wp:divi/placeholder -->" + _structure("section", None, [row]) + "<!-- /wp:divi/placeholder -->"


ICON5 = {"unicode": "&#xe03b;", "type": "divi", "weight": "400"}


def blurb_attrs(image_icon, version=V):
    attrs = {"builderVersion": version, "title": {"innerContent": _d({"text": "Fast"})},
             "imageIcon": {"innerContent": _d({"useIcon": "on", "icon": ICON5})}}
    attrs["imageIcon"].update(image_icon)
    return attrs


def no_effect(src, **kw):
    return [f for f in run(src, **kw) if f.code == "W5_NO_EFFECT"]


class NoEffectTest(unittest.TestCase):
    """doc-experiments.md §9: values Divi 5.13.1 accepts but renders nothing for (live checks, Task 9c)."""

    def test_blurb_icon_width_and_alignment_render_nothing(self):
        src = page(block("blurb", blurb_attrs({"advanced": {"width": _d({"icon": "77px"}),
                                                            "alignment": _d("left")}})))
        f = no_effect(src)
        self.assertEqual(sorted((x.level, x.attr) for x in f),
                         [("warning", "imageIcon.advanced.alignment"), ("warning", "imageIcon.advanced.width")])
        width = next(x for x in f if x.attr == "imageIcon.advanced.width")
        align = next(x for x in f if x.attr == "imageIcon.advanced.alignment")
        self.assertIn("5.13.1", width.message)
        self.assertIn("imageIcon.decoration.sizing", width.hint)
        self.assertIn("iconFontSize", width.hint)
        self.assertIn("alignSelf", align.hint)
        self.assertIn('"end"', align.hint)
        self.assertEqual(codes(src).count("W5_NO_EFFECT"), 2)   # once per attribute, not per breakpoint

    def test_blurb_sizing_placement_and_color_are_fine(self):
        src = page(block("blurb", blurb_attrs({
            "advanced": {"placement": _d("left"), "color": _d("#ff0077")},
            "decoration": {"sizing": _d({"iconFontSize": "56px", "alignSelf": "flex-start"})}})))
        self.assertEqual(no_effect(src), [])

    def test_blurb_width_works_where_divi_migrates_the_whole_page(self):
        """ComposibleOptionsMigration (5.1.1) moves them to sizing, but only when no block on the page is 5.1.1 or
        newer (MigrationUtils::content_needs_migration); live: an all-5.0.0-beta page printed 79px, a mixed one
        nothing."""
        old = "5.0.0-public-beta.1"
        attrs = blurb_attrs({"advanced": {"width": _d({"icon": "79px"})}}, version=old)
        alone = f'<!-- wp:divi/blurb {canonical_json(attrs)} /-->'
        self.assertEqual(no_effect(alone), [])
        self.assertEqual(len(no_effect(page(block("blurb", attrs)))), 1)    # the page's structure blocks are 5.13.1

    def test_slider_level_text_orientation_renders_nothing(self):
        orient = {"module": {"advanced": {"text": {"text": _d({"orientation": "center", "color": "light"})}}}}
        slide = block("slide", {"builderVersion": V, "title": {"innerContent": _d("One")}})
        for parent in ("slider", "fullwidth-slider"):
            with self.subTest(parent):
                attrs = {"builderVersion": V, **orient}
                src = page(f"<!-- wp:divi/{parent} {canonical_json(attrs)} -->{slide}<!-- /wp:divi/{parent} -->")
                f = no_effect(src)
                self.assertEqual([(x.attr, x.value) for x in f], [("module.advanced.text.text.orientation", "desktop")])
                self.assertIn("divi/slide", f[0].hint)
        slide = block("slide", {"builderVersion": V, "title": {"innerContent": _d("One")}, **orient})
        self.assertEqual(no_effect(page(f"<!-- wp:divi/slider {canonical_json({'builderVersion': V})} -->"
                                        f"{slide}<!-- /wp:divi/slider -->")), [])

    HALF_PHONE_FULL = {"sizing": _d({"flexType": "12_24"}, phone={"flexType": "24_24"}, tablet={"flexType": "24_24"})}

    def form(self, field_module):
        field = block("contact-field", {"builderVersion": V, "fieldItem": {"innerContent": _d("Name")},
                                        "module": {"decoration": field_module}})
        return (f"<!-- wp:divi/contact-form {canonical_json({'builderVersion': V})} -->{field}"
                "<!-- /wp:divi/contact-form -->")

    def test_responsive_flex_type_renders_nothing_without_the_flex_grid_css(self):
        f = no_effect(page(self.form(self.HALF_PHONE_FULL)))
        self.assertEqual([(x.attr, x.value) for x in f], [("module.decoration.sizing.flexType", "phone,tablet")])
        self.assertIn("mainElement", f[0].hint)
        group = (f"<!-- wp:divi/group {canonical_json({'builderVersion': V})} -->"
                 + block("text", text_attrs(module={"decoration": self.HALF_PHONE_FULL}))
                 + "<!-- /wp:divi/group -->")
        self.assertEqual(len(no_effect(page(group))), 1)

    def test_desktop_flex_type_is_fine(self):
        self.assertEqual(no_effect(page(self.form({"sizing": _d({"flexType": "12_24"})}))), [])

    def test_responsive_flex_type_works_when_the_page_loads_the_flex_grid_css(self):
        """DetectFeature::get_flex_grid_responsive_breakpoints loads it for pricing tables, or when a
        non-self-closing, un-hyphenated block has a flexType and no desktop display:block (live: both worked)."""
        pricing = (f"<!-- wp:divi/pricing-tables {canonical_json({'builderVersion': V})} -->"
                   + block("pricing-table", {"builderVersion": V, "title": {"innerContent": _d("Basic")}})
                   + "<!-- /wp:divi/pricing-tables -->")
        self.assertEqual(no_effect(page(self.form(self.HALF_PHONE_FULL), pricing)), [])
        flex_col = canonical_json({"builderVersion": V, "module": {"decoration": {"sizing": _d({"flexType": "24_24"})}}})
        wrap = canonical_json({"builderVersion": V, "module": LAYOUT})
        src = (f"<!-- wp:divi/section {wrap} --><!-- wp:divi/row {canonical_json({'builderVersion': V})} -->"
               f"<!-- wp:divi/column {flex_col} -->{self.form(self.HALF_PHONE_FULL)}<!-- /wp:divi/column -->"
               "<!-- /wp:divi/row --><!-- /wp:divi/section -->")
        self.assertEqual(no_effect(src), [])

    def test_flex_grid_port_and_version_order(self):
        from divi5_checks_values import flex_grid_breakpoints, version_key
        pricing = "<!-- wp:divi/pricing-tables {} --><!-- /wp:divi/pricing-tables -->"
        self.assertEqual(flex_grid_breakpoints(pricing), {"phone"})           # pricing tables: phone, always
        self.assertEqual(flex_grid_breakpoints(page(self.form(self.HALF_PHONE_FULL))), set())
        self.assertLess(version_key("5.0.0-public-beta.1"), version_key("5.0.0"))
        self.assertLess(version_key("5.0.0"), version_key("5.1.1"))
        self.assertLess(version_key("5.1.1"), version_key("5.13.1"))
        self.assertLess(version_key("4.27.9"), version_key("5.1.1"))

    def test_malformed_values_do_not_crash(self):
        for layout in ("flex", ["flex"], None):
            attrs = {"builderVersion": V, "name": {"innerContent": _d("J")},
                     "module": {"decoration": {"layout": {"desktop": {"value": layout}},
                                               "sizing": {"phone": {"value": "24_24"}}}}}
            run(columns_page("1_3", block("team-member", attrs)))

    def team(self, layout):
        attrs = {"builderVersion": V, "name": {"innerContent": _d("Jordan")}}
        if layout is not None:
            attrs["module"] = {"decoration": {"layout": _d(layout)}}
        return block("team-member", attrs)

    def test_team_member_flex_layout_renders_nothing_in_a_narrow_column(self):
        f = no_effect(columns_page("1_3", self.team({"display": "flex", "rowGap": "37px"})))
        self.assertEqual([(x.level, x.attr) for x in f], [("warning", "module.decoration.layout")])
        self.assertIn("memberImage", f[0].hint)
        self.assertEqual(len(no_effect(columns_page("1_4", self.team({"rowGap": "20px"})))), 1)

    def test_team_member_layout_is_fine_in_a_full_column_or_as_a_grid(self):
        self.assertEqual(no_effect(page(self.team({"display": "flex", "rowGap": "39px"}))), [])
        self.assertEqual(no_effect(columns_page("1_3", self.team({"display": "grid", "rowGap": "38px"}))), [])
        self.assertEqual(no_effect(columns_page("1_3", self.team(None))), [])

    def test_team_member_in_a_specialty_inner_column_uses_the_scaled_width(self):
        """Divi prints an inner 1_2 column of a 3_4 specialty column as et_pb_column_3_8 (doc-experiments.md §3)."""
        def specialty(inner_type):
            inner = _structure("column-inner", inner_type, [self.team({"rowGap": "20px"})],
                               savedSpecialtyColumnType="3_4")
            inner_row = _structure("row-inner", inner_type if inner_type == "4_4" else "1_2,1_2",
                                   [inner] + ([] if inner_type == "4_4" else [_structure("column-inner", "1_2", [])]))
            main = _structure("column", "3_4", [inner_row], specialtyColumns="3")
            side = _structure("column", "1_4", [block("text", text_attrs())])
            return _structure("section", None, [side, main], type="specialty")
        self.assertEqual(len(no_effect(specialty("1_2"))), 1)   # 3/4 * 1/2 = 3_8
        self.assertEqual(len(no_effect(specialty("4_4"))), 1)   # 3/4, also in Divi's list

    def test_valid_corpus_finds_only_what_divis_converter_writes(self):
        """Divi's own Divi 4 converter writes two of these no-ops: a slider-level orientation (it also copies it
        onto every slide, where it works) and {display: flex, flexDirection: row} on team members that sit in 1_2
        and 1_3 columns (forced to display:block there). Nothing else in the corpus renders nothing."""
        found = {(p.parent.name, f.tag, f.attr) for p in d5_fixtures()
                 for f in validate_source(p.read_text(), fragment=True) if f.code == "W5_NO_EFFECT"}
        self.assertEqual({(d, a) for d, _t, a in found}, {("converted", "module.advanced.text.text.orientation"),
                                                          ("converted", "module.decoration.layout")})
        self.assertEqual({t for _d, t, _a in found}, {"divi/slider", "divi/fullwidth-slider", "divi/team-member"})

    def test_shared_table_drives_the_docs_generator(self):
        import sys
        from _paths import TOOLS5
        sys.path.insert(0, str(TOOLS5))
        import divi5_checks_values
        import generate_docs5
        self.assertIs(generate_docs5.NO_EFFECT, divi5_checks_values.NO_EFFECT)
        for entry in divi5_checks_values.NO_EFFECT:
            self.assertTrue(entry["use"] and entry["why"] and entry["evidence"], entry["attr"])


class BuilderVersionHintTest(unittest.TestCase):
    def test_hint_distinguishes_new_and_edited_blocks(self):
        f = [x for x in run(page(block("text", text_attrs())), site_version="5.14.0") if x.code == "W5_BUILDER_VERSION"]
        self.assertTrue(f)
        self.assertIn("Blocks you create: set builderVersion to the site's Divi version.", f[0].hint)
        self.assertIn("Don't change builderVersion on existing blocks you edit", f[0].hint)


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

    def test_block_token_refs(self):
        """tokens5_from_blocks records the ids a page uses under colors.global_refs and variables_refs."""
        tokens = {"presets": {"divi/text": [{"id": "p-mod"}]}, "group_presets": {"divi/font": [{"id": "p-grp"}]},
                  "colors": {"global_refs": {"gcid-brand": {"uses": 1, "roles": []}}}}
        self.assertNotIn("W5_UNKNOWN_VARIABLE", self.found(tokens=tokens))
        tokens["colors"] = {"global_refs": {}}
        self.assertIn("W5_UNKNOWN_VARIABLE", self.found(tokens=tokens))
        tokens["variables_refs"] = {"gcid-brand": {"uses": 1}}
        self.assertNotIn("W5_UNKNOWN_VARIABLE", self.found(tokens=tokens))

    def test_malformed_tokens_do_not_crash(self):
        for tokens in ({"presets": [1, 2]}, {"presets": {"x": "y"}, "colors": [], "variables": "v", "site": None},
                       {"colors": {"global": ["gcid-a"]}}, {"colors": {"palette": 5}},
                       {"colors": {"palette": True}}, {"colors": {"palette": {"a": 1}}}, {"colors": {"palette": "x"}},
                       {"colors": {"palette": [None, 1, {"global": 3}]}}, {"site": {"url": 5, "divi_version": 5}},
                       {"colors": {"global_refs": ["x"]}, "variables_refs": 3}):
            with self.subTest(tokens=tokens):
                self.found(tokens=tokens)


if __name__ == "__main__":
    unittest.main()
