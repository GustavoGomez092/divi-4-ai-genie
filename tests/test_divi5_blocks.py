import time
import unittest

from _paths import d5_fixtures
from divi5_blocks import (Block, Freeform, canonical_json, get_attr, iter_leaves, new_block, parse,
                          render_block, serialize, set_attr, variable_refs, wrap_placeholder)

SIMPLE = ('<!-- wp:divi/placeholder --><!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":'
          '{"value":"Hero"}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":'
          '{"columnStructure":{"desktop":{"value":"1_2,1_2"}}}}} --><!-- wp:divi/column {"module":{"advanced":'
          '{"type":{"desktop":{"value":"1_2"}}}}} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":'
          '{"value":"\\u003cp\\u003eHi\\u003c/p\\u003e"}}}} /--><!-- /wp:divi/column --><!-- wp:divi/column '
          '{"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}}}} --><!-- wp:divi/image {"image":'
          '{"innerContent":{"desktop":{"value":{"src":"https://x.test/a.jpg"}}}}} /--><!-- /wp:divi/column -->'
          '<!-- /wp:divi/row --><!-- /wp:divi/section --><!-- /wp:divi/placeholder -->')


class ParseTest(unittest.TestCase):
    def test_roundtrip_all_fixtures(self):
        fixtures = d5_fixtures()
        self.assertGreater(len(fixtures), 30)
        for p in fixtures:
            src = p.read_text()
            doc = parse(src)
            self.assertEqual(doc.problems, [], p.name)
            self.assertEqual(serialize(doc), src, p.name)

    def test_tree_shape_and_paths(self):
        doc = parse(SIMPLE)
        (section,) = doc.sections()
        self.assertEqual(section.name, "divi/section")
        text = doc.find("placeholder[0] > section[0] > row[0] > column[0] > text[0]")
        self.assertEqual(get_attr(text, "content.innerContent"), "<p>Hi</p>")
        self.assertEqual([p for _, p, _ in doc.walk()][-1],
                         "placeholder[0] > section[0] > row[0] > column[1] > image[0]")

    def test_block_fields(self):
        doc = parse(SIMPLE)
        text = doc.find("placeholder[0] > section[0] > row[0] > column[0] > text[0]")
        self.assertTrue(text.self_closing)
        self.assertIsNone(text.close_start)
        self.assertEqual(text.open_end, text.end)
        self.assertEqual(text.raw_json, '{"content":{"innerContent":{"desktop":'
                                        '{"value":"\\u003cp\\u003eHi\\u003c/p\\u003e"}}}}')
        ph = doc.nodes[0]
        self.assertEqual(ph.raw_json, "")
        self.assertEqual(ph.attrs, {})
        self.assertEqual(SIMPLE[ph.close_start:ph.end], "<!-- /wp:divi/placeholder -->")
        self.assertFalse(ph.dirty)

    def test_walk_parent_and_find_missing(self):
        doc = parse(SIMPLE)
        rows = [(b.name, parent.name) for b, _, parent in doc.walk() if b.name == "divi/row"]
        self.assertEqual(rows, [("divi/row", "divi/section")])
        self.assertIsNone(doc.find("placeholder[0] > section[1]"))
        with self.assertRaises(ValueError):
            doc.find("placeholder[0] > bogus")

    def test_sections_without_placeholder_and_foreign_blocks(self):
        src = ('<!-- wp:divi/section /-->\n<!-- wp:paragraph --><p>x</p><!-- /wp:paragraph -->'
               '<!-- wp:divi/section {"a":1} /-->')
        doc = parse(src)
        self.assertEqual(doc.problems, [])
        self.assertEqual(len(doc.sections()), 2)
        self.assertEqual([p for _, p, _ in doc.walk()],
                         ["section[0]", "core/paragraph[0]", "section[1]"])
        self.assertEqual(doc.find("core/paragraph[0]").name, "core/paragraph")
        self.assertEqual(serialize(doc), src)

    def test_line_col(self):
        doc = parse("a\nbc<!-- wp:divi/text /-->")
        self.assertEqual(doc.line_col(4), (2, 3))

    def test_visual_builder_style_whitespace_and_escapes(self):
        vb = ('<!-- wp:divi/placeholder -->\n<!-- wp:divi/section {"a":"x\\\\y"} -->\n\n'
              '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"a\\u0026b"}}}} /-->\n'
              '<!-- /wp:divi/section -->\n<!-- /wp:divi/placeholder -->')
        doc = parse(vb)
        self.assertEqual(doc.problems, [])
        self.assertEqual(serialize(doc), vb)
        text = doc.find("placeholder[0] > section[0] > text[0]")
        self.assertEqual(get_attr(text, "content.innerContent"), "a&b")
        self.assertTrue(any(isinstance(c, Freeform) for c in doc.nodes[0].children))

    def test_empty_open_close_pair_accepted(self):
        src = '<!-- wp:divi/divider {"x":1} --><!-- /wp:divi/divider -->'
        doc = parse(src)
        self.assertEqual(doc.problems, [])
        self.assertEqual(serialize(doc), src)
        self.assertFalse(doc.nodes[0].self_closing)

    def test_problems(self):
        self.assertEqual(parse('<!-- wp:divi/section {"a": } -->x<!-- /wp:divi/section -->').problems[0].code,
                         "E5_BAD_JSON")
        self.assertEqual(parse('<!-- wp:divi/section {} -->').problems[0].code, "E5_UNCLOSED")
        self.assertEqual(parse('<!-- /wp:divi/row -->').problems[0].code, "E5_STRAY_CLOSE")
        self.assertEqual(parse('<!-- wp:divi/section --><!-- /wp:divi/row -->').problems[0].code,
                         "E5_MISNESTED")

    def test_bad_json_keeps_block_and_offset(self):
        src = 'ab<!-- wp:divi/section {"a": } -->x<!-- /wp:divi/section -->'
        doc = parse(src)
        (prob,) = doc.problems
        self.assertEqual(prob.offset, 2)
        self.assertEqual(doc.nodes[1].name, "divi/section")
        self.assertEqual(doc.nodes[1].attrs, {})
        self.assertEqual(doc.nodes[1].raw_json, '{"a": }')
        self.assertEqual(serialize(doc), src)

    def test_php_rejected_json_is_bad(self):
        # PHP json_decode() returns null for NaN and for unpaired UTF-16 surrogates.
        for raw in ('{"a":NaN}', '{"a":"\\ud800"}'):
            self.assertEqual([p.code for p in parse(f'<!-- wp:divi/text {raw} /-->').problems],
                             ["E5_BAD_JSON"], raw)

    def test_broken_input_still_serializes_verbatim(self):
        for src in ('<!-- /wp:divi/row -->x', '<!-- wp:divi/section --><!-- /wp:divi/row -->',
                    '<!-- wp:divi/section --><!-- wp:divi/row -->y<!-- /wp:divi/section -->',
                    '<!-- wp:divi/section {} -->tail'):
            self.assertEqual(serialize(parse(src)), src, src)

    def test_misnested_close_of_outer_block_closes_inner(self):
        doc = parse('<!-- wp:divi/section --><!-- wp:divi/row --><!-- /wp:divi/section -->')
        self.assertEqual([p.code for p in doc.problems], ["E5_MISNESTED"])
        self.assertEqual(doc.find("section[0] > row[0]").name, "divi/row")

    def test_malformed_comment_is_not_catastrophic(self):
        src = '<!-- wp:divi/text {"a":"' + "x" * 50000 + '"-->' + '<!-- wp:divi/text /-->'
        t = time.perf_counter()
        doc = parse(src)
        self.assertLess(time.perf_counter() - t, 1.0)
        self.assertEqual([b.name for b, _, _ in doc.walk()], ["divi/text"])

    def test_parse_large_fast(self):
        largest = max(d5_fixtures(), key=lambda p: p.stat().st_size)
        src = largest.read_text()
        t = time.perf_counter()
        for _ in range(20):
            parse(src)
        self.assertLess(time.perf_counter() - t, 2.0)


class CanonicalTest(unittest.TestCase):
    def test_wordpress_escapes(self):
        got = canonical_json({"t": 'a<b>&"c"--d\\e/é😀'})
        self.assertEqual(got, '{"t":"a\\u003cb\\u003e\\u0026\\u0022c\\u0022\\u002d\\u002dd\\u005ce/é😀"}')

    def test_strtr_is_single_pass(self):
        # Verified with PHP 8.2 serialize_block_attributes().
        got = canonical_json({"t": "---", "u": "\\\\", "v": '\\"', "w": "\\-"})
        self.assertEqual(got, '{"t":"\\u002d\\u002d-","u":"\\u005c\\u005c","v":"\\u005c\\u0022",'
                              '"w":"\\u005c-"}')

    def test_php_empty_object_becomes_array(self):
        self.assertEqual(canonical_json({"a": {}, "b": []}), '{"a":[],"b":[]}')
        self.assertEqual(canonical_json({"a": [{}, {"0": 1}], "b": {"0": {}}}), '{"a":[[],[1]],"b":[[]]}')

    def test_php_sequential_numeric_keys_become_list(self):
        self.assertEqual(canonical_json({"s": {"0": "x", "1": "y"}}), '{"s":["x","y"]}')
        self.assertEqual(canonical_json({"s": {"1": "x"}}), '{"s":{"1":"x"}}')
        self.assertEqual(canonical_json({"s": {"1": "x", "0": "y"}}), '{"s":{"1":"x","0":"y"}}')
        self.assertEqual(canonical_json({"s": {"01": "x"}}), '{"s":{"01":"x"}}')

    def test_line_separators_escaped(self):
        self.assertEqual(canonical_json({"t": "a b "}), '{"t":"a\\u2028b\\u2029"}')

    def test_control_characters(self):
        self.assertEqual(canonical_json({"t": "ctl\x01\x1f\x7f\b\f\n\r\t"}),
                         '{"t":"ctl\\u0001\\u001f\x7f\\b\\f\\n\\r\\t"}')

    def test_floats_and_bools(self):
        # PHP json_encode() without JSON_PRESERVE_ZERO_FRACTION writes 1.0 as 1 (checked on PHP 8.2).
        self.assertEqual(canonical_json({"a": 1.0, "b": 0.5, "c": True, "d": None}),
                         '{"a":1,"b":0.5,"c":true,"d":null}')

    def test_php_float_formatting(self):
        # Expected strings produced by PHP 8.2 (serialize_precision=-1) on the local Divi 5 site's PHP.
        cases = [(1e20, "1.0e+20"), (1e-5, "1.0e-5"), (1.5e300, "1.5e+300"), (0.1, "0.1"), (-0.0, "-0"),
                 (1e16, "10000000000000000"), (1e17, "1.0e+17"), (100.0, "100"), (2.5e-7, "2.5e-7"),
                 (0.0001, "0.0001"), (0.00012345, "0.00012345"), (12345678901234567.0, "12345678901234568"),
                 (1234567890123456.7, "1234567890123456.8"), (123e-20, "1.23e-18"), (-1.5e-10, "-1.5e-10"),
                 (0.30000000000000004, "0.30000000000000004"), (123456.789, "123456.789"),
                 (1.7976931348623157e308, "1.7976931348623157e+308"), (5e-324, "5.0e-324"), (34.01, "34.01")]
        for value, want in cases:
            self.assertEqual(canonical_json({"a": value}), '{"a":%s}' % want, repr(value))

    def test_php_int_overflow_becomes_float(self):
        self.assertEqual(canonical_json({"a": 9223372036854775807, "b": 9223372036854775808,
                                         "c": -9223372036854775808}),
                         '{"a":9223372036854775807,"b":9.223372036854776e+18,"c":-9223372036854775808}')

    def test_new_block_is_canonical_and_self_closing(self):
        b = new_block("text", {"content": {"innerContent": {"desktop": {"value": "<p>x</p>"}}}})
        self.assertEqual(b.name, "divi/text")
        self.assertEqual(b.start, -1)
        self.assertEqual(render_block(b),
                         '<!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":'
                         '"\\u003cp\\u003ex\\u003c/p\\u003e"}}}} /-->')
        sec = new_block("section", {}, [b])
        self.assertTrue(render_block(sec).startswith("<!-- wp:divi/section -->"))
        self.assertEqual(new_block("core/paragraph").name, "core/paragraph")
        self.assertEqual(render_block(new_block("core/paragraph", None, [Freeform("<p>x</p>", -1, -1)])),
                         "<!-- wp:paragraph --><p>x</p><!-- /wp:paragraph -->")

    def test_render_block_of_converter_leaf_self_closes(self):
        doc = parse('<!-- wp:divi/divider {"x":1} --><!-- /wp:divi/divider -->')
        self.assertEqual(render_block(doc.nodes[0]), '<!-- wp:divi/divider {"x":1} /-->')

    def test_canonical_is_fixed_point_on_fixtures(self):
        # Re-rendering every block canonically, then parsing that again, yields identical attrs.
        for p in d5_fixtures():
            doc = parse(p.read_text())
            canon = "".join(render_block(n) for n in doc.nodes if isinstance(n, Block))
            again = parse(canon)
            self.assertEqual(again.problems, [], p.name)
            self.assertEqual(serialize(again), canon, p.name)
            self.assertEqual([b.attrs for b, _, _ in again.walk()], [b.attrs for b, _, _ in doc.walk()], p.name)
            self.assertEqual("".join(render_block(n) for n in again.nodes if isinstance(n, Block)), canon)


class AttrTest(unittest.TestCase):
    def test_set_attr_only_changes_that_block(self):
        doc = parse(SIMPLE)
        text = doc.find("placeholder[0] > section[0] > row[0] > column[0] > text[0]")
        set_attr(text, "content.innerContent", "<p>Bye</p>")
        set_attr(text, "content.decoration.bodyFont.body.font", {"size": "18px"}, breakpoint="tablet")
        self.assertTrue(text.dirty)
        out = serialize(doc)
        before, after = SIMPLE.split("<!-- wp:divi/text")[0], SIMPLE.split("<!-- /wp:divi/column -->", 1)[1]
        self.assertTrue(out.startswith(before))
        self.assertTrue(out.endswith(after))
        self.assertIn("Bye", out)
        self.assertEqual(get_attr(parse(out).find("placeholder[0] > section[0] > row[0] > column[0] > text[0]"),
                                  "content.decoration.bodyFont.body.font", breakpoint="tablet"), {"size": "18px"})

    def test_dirty_parent_keeps_children_bytes(self):
        vb = ('<!-- wp:divi/section {"a":"x\\\\y"} -->\n'
              '<!-- wp:divi/text {"b":"a\\u0026b"} --><!-- /wp:divi/text -->\n<!-- /wp:divi/section -->')
        doc = parse(vb)
        set_attr(doc.nodes[0], "builderVersion", "5.13.1", breakpoint=None)
        self.assertEqual(serialize(doc),
                         '<!-- wp:divi/section {"a":"x\\u005cy","builderVersion":"5.13.1"} -->\n'
                         '<!-- wp:divi/text {"b":"a\\u0026b"} --><!-- /wp:divi/text -->\n<!-- /wp:divi/section -->')

    def test_serialize_new_block_in_parsed_tree(self):
        doc = parse(SIMPLE)
        col = doc.find("placeholder[0] > section[0] > row[0] > column[1]")
        col.children.append(new_block("divider"))
        out = serialize(doc)
        self.assertIn('"https://x.test/a.jpg"}}}}} /--><!-- wp:divi/divider /--><!-- /wp:divi/column -->', out)
        self.assertEqual(out.replace("<!-- wp:divi/divider /-->", ""), SIMPLE)

    def test_get_and_set_non_responsive(self):
        doc = parse(SIMPLE)
        sec = doc.sections()[0]
        self.assertEqual(get_attr(sec, "builderVersion", breakpoint=None), "5.13.1")
        self.assertEqual(get_attr(sec, "module.meta.adminLabel"), "Hero")
        self.assertIsNone(get_attr(sec, "module.meta.adminLabel", breakpoint="tablet"))
        self.assertEqual(get_attr(sec, "nope.x", default="d"), "d")
        set_attr(sec, "modulePreset", ["default"], breakpoint=None)
        self.assertEqual(sec.attrs["modulePreset"], ["default"])

    def test_set_attr_replaces_php_empty_array(self):
        b = parse('<!-- wp:divi/text {"module":[]} /-->').nodes[0]
        set_attr(b, "module.decoration.spacing", {"padding": {"top": "1px"}}, state="hover")
        self.assertEqual(b.attrs, {"module": {"decoration": {"spacing": {"desktop": {"hover":
                                                                                     {"padding": {"top": "1px"}}}}}}})

    def test_iter_leaves(self):
        attrs = {"title": {"decoration": {"font": {"font": {"desktop": {"value": {"size": "5px"}, "hover": {"x": 1}},
                                                             "tablet": {"value": {"size": "4px"}}}}}},
                 "builderVersion": "5.13.1", "modulePreset": ["default"]}
        got = sorted((p, bp or "", st or "") for p, bp, st, _ in iter_leaves(attrs))
        self.assertEqual(got, [("builderVersion", "", ""), ("modulePreset", "", ""),
                               ("title.decoration.font.font", "desktop", "hover"),
                               ("title.decoration.font.font", "desktop", "value"),
                               ("title.decoration.font.font", "tablet", "value")])
        values = {(p, bp, st): v for p, bp, st, v in iter_leaves(attrs)}
        self.assertEqual(values[("title.decoration.font.font", "desktop", "hover")], {"x": 1})

    def test_iter_leaves_on_fixtures_hits_breakpoint_states(self):
        doc = parse(SIMPLE)
        leaves = [(p, bp, st, v) for b, _, _ in doc.walk() for p, bp, st, v in iter_leaves(b.attrs)]
        self.assertIn(("module.advanced.columnStructure", "desktop", "value", "1_2,1_2"), leaves)
        self.assertIn(("builderVersion", None, None, "5.13.1"), leaves)

    def test_variable_refs(self):
        v = 'x $variable({"type":"color","value":{"name":"gcid-abc","settings":{}}})$ y'
        self.assertEqual(variable_refs(v), [{"type": "color", "value": {"name": "gcid-abc", "settings": {}}}])
        self.assertEqual(variable_refs("#fff"), [])

    def test_variable_refs_multiple_and_tricky_strings(self):
        v = ('$variable({"type":"content","value":{"name":"x","settings":{"before":"})$ {"}}})$'
             '-$variable({"type":"color","value":{"name":"gcid-2"}})$ $variable({broken})$')
        self.assertEqual(variable_refs(v), [
            {"type": "content", "value": {"name": "x", "settings": {"before": "})$ {"}}},
            {"type": "color", "value": {"name": "gcid-2"}}])
        self.assertEqual(variable_refs(None), [])

    def test_wrap_placeholder(self):
        (ph,) = wrap_placeholder([new_block("section")])
        self.assertEqual(ph.name, "divi/placeholder")
        self.assertEqual(render_block(ph), "<!-- wp:divi/placeholder --><!-- wp:divi/section /-->"
                                           "<!-- /wp:divi/placeholder -->")


if __name__ == "__main__":
    unittest.main()
