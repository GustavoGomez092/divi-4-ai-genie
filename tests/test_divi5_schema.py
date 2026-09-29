import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCHEMA5_RAW, SCRIPTS, TOOLS5, d5_fixtures
from divi5_blocks import iter_leaves, parse, variable_refs
from divi5_schema import load_schema5

LEAF_TYPES = {"text", "html", "color", "length", "number", "enum", "onoff", "url", "image", "icon",
              "spacing", "radius", "gradient", "object", "font-family", "font-weight", "json"}


def _signup_quirk(block_name, attr):
    # Known converter quirk: signup custom fields stay as a D4 shortcode string (schema.md §Q2).
    return "signup" in block_name and attr.startswith("content")


class Schema5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = load_schema5()

    def test_meta_and_scope(self):
        meta = json.loads((SCRIPTS / "schema5" / "_meta.json").read_text())
        self.assertTrue(meta["divi_version"].startswith("5."))
        self.assertEqual(meta["breakpoints_default"], ["desktop", "tablet", "phone"])
        self.assertEqual(meta["scopes_in"], ["core", "d5-extra"])
        self.assertEqual(meta["generated_by"], "build_schema5.py")
        self.assertTrue(self.schema.in_scope("divi/blurb"))
        self.assertTrue(self.schema.in_scope("section"))
        self.assertTrue(self.schema.in_scope("divi/icon-list"))                   # d5-extra
        self.assertFalse(self.schema.in_scope("divi/cart-products"))              # woocommerce (no such block)
        self.assertFalse(self.schema.in_scope("divi/woocommerce-cart-products"))  # woocommerce
        self.assertFalse(self.schema.in_scope("divi/contact-form-7"))             # integration
        self.assertFalse(self.schema.in_scope("divi/blog"))                       # theme-builder
        self.assertIsNone(self.schema.module("divi/nope"))
        self.assertEqual(self.schema.module("divi/woocommerce-cart-products").scope, "woocommerce")
        self.assertEqual(self.schema.module("shortcode-module").scope, "internal")

    def test_every_fixture_path_resolves(self):
        misses = []
        for p in d5_fixtures():
            for block, path, _ in parse(p.read_text()).walk():
                mod = self.schema.module(block.name)
                if mod is None:
                    continue  # placeholder/internal handled by the validator
                for attr, bp, st, _ in iter_leaves(block.attrs):
                    r = mod.resolve(attr, bp, st)
                    if r.status not in ("ok", "nonresponsive"):
                        misses.append((p.name, block.name, attr, bp, st, r.status))
        misses = [m for m in misses if not _signup_quirk(m[1], m[2])]
        self.assertEqual(misses, [])

    def test_every_fixture_value_leaf_resolves(self):
        """Descend into object values: every sub-key of every fixture value maps to a typed leaf."""
        misses = []
        for p in d5_fixtures():
            for block, path, _ in parse(p.read_text()).walk():
                mod = self.schema.module(block.name)
                if mod is None:
                    continue
                for attr, bp, st, value in iter_leaves(block.attrs):
                    if bp is None:
                        continue
                    for r, _v in mod.walk_value(attr, bp, st, value):
                        if r.status != "ok":
                            misses.append((p.name, block.name, attr, r.sub_path, bp, st, r.status))
                        else:
                            self.assertIn(r.leaf["type"], LEAF_TYPES)
        misses = [m for m in misses if not _signup_quirk(m[1], m[2])]
        self.assertEqual(misses, [])

    def test_fixture_values_fit_enum_and_onoff(self):
        """Enum options are not narrower than what Divi itself writes (corpus = converter + Divi AI + VB)."""
        bad = []
        for p in d5_fixtures():
            for block, path, _ in parse(p.read_text()).walk():
                mod = self.schema.module(block.name)
                if mod is None:
                    continue
                for attr, bp, st, value in iter_leaves(block.attrs):
                    if bp is None:
                        continue
                    for r, v in mod.walk_value(attr, bp, st, value):
                        if r.status != "ok" or v in ("", None) or variable_refs(v):
                            continue
                        t = r.leaf["type"]
                        vals = v if isinstance(v, list) and r.leaf.get("multiple") else [v]
                        if t == "enum" and not all(x in r.leaf["options"] for x in vals):
                            bad.append((p.name, block.name, attr, r.sub_path, v))
                        if t == "onoff" and v not in ("on", "off"):
                            bad.append((p.name, block.name, attr, r.sub_path, v))
        bad = [m for m in bad if not _signup_quirk(m[1], m[2])]
        self.assertEqual(bad, [])

    def test_bogus_paths_rejected(self):
        blurb = self.schema.module("divi/blurb")
        for attr in ("title.decoration.fontz.font", "module.decoration.bogus", "imageIcon.innerContent.nope",
                     "titlex.innerContent", "module.advanced.showTitle", "title.decoration.font.font.fontSize"):
            self.assertEqual(blurb.resolve(attr, "desktop", "value").status, "unknown_attr", attr)
        bad = list(blurb.walk_value("module.decoration.spacing", "desktop", "value", {"marginz": "1px"}))
        self.assertEqual([r.status for r, _ in bad], ["unknown_attr"])

    def test_breakpoints_and_states(self):
        blurb = self.schema.module("divi/blurb")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "tablet", "value").status, "ok")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "desktop", "hover").status, "ok")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "phoneWide", "value").status, "ok")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "mobile", "value").status, "bad_breakpoint")
        self.assertEqual(blurb.resolve("title.decoration.font.font", "desktop", "pressed").status, "bad_state")
        # useIcon is declared hover:false / sticky:false in module.json
        self.assertEqual(blurb.resolve("imageIcon.innerContent.useIcon", "desktop", "hover").status, "bad_state")
        # a known responsive attribute given without a breakpoint wrapper
        self.assertEqual(blurb.resolve("imageIcon.advanced.placement", None, None).status, "bad_breakpoint")

    def test_resolution_fields(self):
        blurb = self.schema.module("blurb")
        r = blurb.resolve("title.decoration.font.font.size", "desktop", "value")
        self.assertEqual((r.status, r.attr_path, r.sub_path, r.family),
                         ("ok", "title.decoration.font.font", "size", "font"))
        self.assertEqual(r.leaf["type"], "length")
        r = blurb.resolve("imageIcon.advanced.placement", "desktop", "value")
        self.assertEqual((r.status, r.attr_path, r.sub_path, r.family), ("ok", "imageIcon.advanced.placement",
                                                                         None, None))
        self.assertEqual(r.leaf["type"], "enum")
        self.assertIn("top", r.leaf["options"])
        r = blurb.resolve("imageIcon.innerContent.useIcon", "desktop", "value")
        self.assertEqual((r.attr_path, r.sub_path, r.leaf["type"]), ("imageIcon.innerContent", "useIcon", "onoff"))
        r = blurb.resolve("module.decoration.background.color", "desktop", "hover")
        self.assertEqual((r.status, r.family, r.leaf["type"]), ("ok", "background", "color"))
        for key, bp, st in (("builderVersion", None, None), ("modulePreset", None, None),
                            ("groupPreset.designTitleText.presetId", None, None), ("_private", None, None)):
            self.assertEqual(blurb.resolve(key, bp, st).status, "nonresponsive", key)

    def test_walk_value_types(self):
        blurb = self.schema.module("blurb")
        got = {r.sub_path: r.leaf["type"] for r, _ in blurb.walk_value(
            "module.decoration.spacing", "desktop", "value",
            {"padding": {"top": "10px", "syncVertical": "on"}, "margin": {"bottom": "20px"}})}
        self.assertEqual(got, {"padding": "spacing", "margin": "spacing"})
        got = {r.sub_path: r.leaf["type"] for r, _ in blurb.walk_value(
            "title.decoration.font.font", "desktop", "value", {"family": "Lato", "weight": "700", "size": "20px"})}
        self.assertEqual(got, {"family": "font-family", "weight": "font-weight", "size": "length"})

    def test_every_leaf_typed(self):
        self.assertEqual(self.schema.leaf_types(), LEAF_TYPES)
        self.assertGreater(len(self.schema.names()), 100)
        for name in self.schema.names():
            mod = self.schema.module(name)
            for attr, spec in mod.attrs.items():
                leaf = self.schema.leaf_spec(spec)
                self.assertTrue(leaf, f"{name} {attr}")
                for sub, s in leaf.items():
                    self.assertIn(s["type"], LEAF_TYPES, f"{name} {attr} {sub}")
                    self.assertIsInstance(s["bp"], bool, f"{name} {attr} {sub}")
                    self.assertIn("value", s["states"], f"{name} {attr} {sub}")
                    if s["type"] == "enum":
                        self.assertTrue(s.get("options"), f"{name} {attr} {sub}")

    def test_structure_relations(self):
        self.assertIn("divi/row", self.schema.module("section").children or [])
        self.assertIn("divi/accordion-item", self.schema.module("accordion").children)
        self.assertEqual(self.schema.module("blurb").d4, "et_pb_blurb")
        self.assertEqual(self.schema.module("section").category, "structure")
        self.assertEqual(self.schema.module("row").children, ["divi/column"])
        self.assertIn("divi/section", self.schema.module("row").parents)
        self.assertIn("divi/column", self.schema.module("blurb").parents)
        self.assertIn("divi/column-inner", self.schema.module("blurb").parents)
        self.assertEqual(self.schema.module("accordion-item").parents, ["divi/accordion"])
        self.assertEqual(self.schema.module("section").parents, [])
        self.assertIn("divi/section", self.schema.module("fullwidth-header").parents)
        self.assertNotIn("divi/column", self.schema.module("fullwidth-header").parents)
        self.assertIn("divi/row-inner", self.schema.module("column").children)
        self.assertIsNone(self.schema.module("blurb").children)

    def test_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, str(TOOLS5 / "build_schema5.py"), str(SCHEMA5_RAW),
                            str(TOOLS5 / "families5.json"), tmp], check=True, capture_output=True)
            committed = sorted(f.name for f in (SCRIPTS / "schema5").glob("*.json"))
            self.assertEqual(committed, sorted(f.name for f in Path(tmp).glob("*.json")))
            for name in committed:
                self.assertEqual((SCRIPTS / "schema5" / name).read_text(), (Path(tmp) / name).read_text(), name)

    def test_coverage_gate_fails_on_untyped_leaf(self):
        fam = json.loads((TOOLS5 / "families5.json").read_text())
        del fam["fragments"]["background"]["color"]  # families.background -> fragment background
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "families5.json"
            bad.write_text(json.dumps(fam))
            out = Path(tmp) / "out"
            proc = subprocess.run([sys.executable, str(TOOLS5 / "build_schema5.py"), str(SCHEMA5_RAW), str(bad),
                                   str(out)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("decoration.background", proc.stdout + proc.stderr)
            self.assertIn("color", proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
