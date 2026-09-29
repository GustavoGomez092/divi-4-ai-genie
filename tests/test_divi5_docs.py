"""Generated Divi 5 module references and design-family tables (research/tools/divi5/generate_docs5.py)."""
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import SCHEMA5_RAW, SKILL, TOOLS5
from check_doc_examples import check, count_blocks
from divi5_schema import load_schema5
from validate import validate_source

sys.path.insert(0, str(TOOLS5))
import generate_docs5 as gd  # noqa: E402

SCHEMA5 = load_schema5()
REF5 = SKILL / "reference" / "divi5"
MODULES5 = REF5 / "modules"
NOTES5 = TOOLS5 / "notes"
IN_SCOPE = [n for n in SCHEMA5.names() if SCHEMA5.in_scope(n)]


def short(name):
    return name[5:]


class GeneratedDocsTest(unittest.TestCase):
    def test_generation_is_deterministic_and_matches_committed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / "reference" / "divi5").mkdir(parents=True)
            shutil.copy(REF5 / "design-families.md", skill / "reference" / "divi5" / "design-families.md")
            self.assertEqual(gd.main(SCHEMA5_RAW, skill, NOTES5), 0)
            out = skill / "reference" / "divi5"
            generated = sorted(p.name for p in (out / "modules").glob("*.md"))
            committed = sorted(p.name for p in MODULES5.glob("*.md"))
            self.assertEqual(generated, committed)
            for name in generated:
                self.assertEqual((out / "modules" / name).read_text(), (MODULES5 / name).read_text(), name)
            self.assertEqual((out / "design-families.md").read_text(), (REF5 / "design-families.md").read_text())

    def test_every_in_scope_module_has_a_page_and_nothing_else_does(self):
        pages = {p.stem for p in MODULES5.glob("*.md")} - {"README"}
        self.assertEqual(pages, {short(n) for n in IN_SCOPE})
        self.assertIn("section", pages)       # structure blocks are included
        self.assertIn("row-inner", pages)
        self.assertNotIn("shop", pages)       # woocommerce is out of scope

    def test_readme_lists_every_page(self):
        readme = (MODULES5 / "README.md").read_text()
        for n in IN_SCOPE:
            self.assertIn(f"]({short(n)}.md)", readme, n)

    def test_coverage_reports_zero_gaps(self):
        pages = {short(n): (MODULES5 / f"{short(n)}.md").read_text() for n in IN_SCOPE}
        families = (REF5 / "design-families.md").read_text()
        self.assertEqual(gd.coverage_gaps(SCHEMA5, pages, families), [])

    def test_coverage_catches_an_attr_dropped_from_a_page(self):
        pages = {short(n): (MODULES5 / f"{short(n)}.md").read_text() for n in IN_SCOPE}
        families = (REF5 / "design-families.md").read_text()
        # an inline attr: its row disappears from the page
        pages["blurb"] = "\n".join(l for l in pages["blurb"].splitlines() if "`imageIcon.advanced.placement`" not in l)
        # a family attr: the link to its family disappears from the page
        pages["button"] = pages["button"].replace("design-families.md#z-index", "design-families.md#nowhere")
        gaps = gd.coverage_gaps(SCHEMA5, pages, families)
        self.assertIn(("blurb", "imageIcon.advanced.placement"), gaps)
        self.assertIn(("button", "module.decoration.zIndex"), gaps)

    def test_coverage_catches_a_family_table_missing_from_design_families(self):
        pages = {"blurb": (MODULES5 / "blurb.md").read_text()}
        families = (REF5 / "design-families.md").read_text()
        broken = families.replace('<a id="fit"></a>', "")
        self.assertIn(("blurb", "imageIcon.decoration.fit"), gd.coverage_gaps(SCHEMA5, pages, broken))

    def _main_with(self, **patches):
        import contextlib
        import io
        saved = {k: getattr(gd, k) for k in patches}
        try:
            for k, v in patches.items():
                setattr(gd, k, v)
            with tempfile.TemporaryDirectory() as tmp:
                skill = Path(tmp)
                (skill / "reference" / "divi5").mkdir(parents=True)
                shutil.copy(REF5 / "design-families.md", skill / "reference" / "divi5" / "design-families.md")
                err = io.StringIO()
                with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                    rc = gd.main(SCHEMA5_RAW, skill, NOTES5)
                return rc, err.getvalue(), (skill / "reference" / "divi5" / "modules").exists()
        finally:
            for k, v in saved.items():
                setattr(gd, k, v)

    def test_main_fails_when_an_example_does_not_validate(self):
        bad = dict(gd.SAMPLES, text={"content": {"innerContent": {"tablet": {"value": "<p>x</p>"}}},
                                     "notAnAttr": {"desktop": {"value": "x"}}})
        rc, err, wrote = self._main_with(SAMPLES=bad)
        self.assertEqual(rc, 1)
        self.assertIn("divi/text", err)
        self.assertFalse(wrote)

    def test_main_fails_when_a_page_drops_an_attribute(self):
        real = gd.render_module

        def dropping(short, *a, **k):
            page = real(short, *a, **k)
            return "\n".join(l for l in page.splitlines() if not l.startswith("| `imageIcon.advanced.color` |"))
        rc, err, wrote = self._main_with(render_module=dropping)
        self.assertEqual(rc, 1)
        self.assertIn("imageIcon.advanced.color", err)
        self.assertFalse(wrote)

    def test_minimal_examples_validate_without_findings(self):
        for n in IN_SCOPE:
            src = gd.minimal_example(short(n), SCHEMA5)
            findings = [(f.level, f.code, f.attr) for f in validate_source(src, fragment=True)]
            self.assertEqual(findings, [], f"{n}: {src}")
            self.assertIn(f"wp:{n} ", src)

    def test_module_page_anatomy(self):
        blurb = (MODULES5 / "blurb.md").read_text()
        for needle in ("# Blurb — divi/blurb", "et_pb_blurb", "## Minimal valid example", "```divi5\n",
                       "## Content", "`title.innerContent`", "## Design", "design-families.md#font",
                       "`title.decoration.font.font`", "## Advanced", "`imageIcon.advanced.placement`",
                       "<details>", "Render defaults", "blurbTitle", "divi/column"):
            self.assertIn(needle, blurb)

    def test_pages_carry_hand_notes(self):
        for note in NOTES5.glob("*.md"):
            if note.stem == "README":
                continue
            page = (MODULES5 / f"{note.stem}.md").read_text()
            self.assertIn("## Gotchas", page)
            self.assertIn(note.read_text().strip().splitlines()[0], page)

    def test_design_families_prose_and_markers(self):
        text = (REF5 / "design-families.md").read_text()
        head, rest = text.split("<!-- BEGIN GENERATED -->", 1)
        self.assertIn("<!-- END GENERATED -->", rest)
        self.assertIn("$variable", head)   # the hand-written prose explains $variable values
        used = {spec["family"] for n in IN_SCOPE for spec in SCHEMA5.module(n).attrs.values() if "family" in spec}
        for fam in used:
            self.assertIn(f'<a id="{fam}"></a>', rest, fam)


class Divi5DocExamplesTest(unittest.TestCase):
    def test_skill_examples_validate(self):
        self.assertEqual(check(SKILL), [])

    def test_divi5_examples_are_counted(self):
        self.assertGreaterEqual(count_blocks(SKILL, "divi5"), len(IN_SCOPE))

    def _check(self, rel, fence, block):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / rel
            md.parent.mkdir(parents=True, exist_ok=True)
            md.write_text(f"# T\n\n```{fence}\n{block}\n```\n")
            return [code for _p, _i, errs in check(Path(tmp)) for code, *_ in errs]

    GOOD = gd.minimal_example("text", SCHEMA5)
    BAD = GOOD.replace('"builderVersion"', '"notAnAttr":{"desktop":{"value":"x"}},"builderVersion"', 1)

    def test_bad_divi5_fence_fails(self):
        self.assertNotEqual(self.BAD, self.GOOD)
        self.assertEqual(self._check("reference/divi5/x.md", "divi5", self.GOOD), [])
        self.assertTrue(self._check("reference/divi5/x.md", "divi5", self.BAD))

    def test_html_fence_with_blocks_is_checked_under_divi5_dirs_only(self):
        self.assertTrue(self._check("reference/divi5/x.md", "html", self.BAD))
        self.assertTrue(self._check("recipes/divi5/sections/x.md", "html", self.BAD))
        self.assertEqual(self._check("reference/x.md", "html", self.BAD), [])

    def test_html_fence_without_blocks_is_ignored(self):
        self.assertEqual(self._check("reference/divi5/x.md", "html", "<p>not a block</p>"), [])

    def test_divi5_page_recipes_need_an_h1(self):
        self.assertEqual(self._check("recipes/divi5/pages/x.md", "divi5", self.GOOD), ["W_NO_H1"])
        self.assertEqual(self._check("recipes/divi5/sections/x.md", "divi5", self.GOOD), [])

    def test_glued_divi5_closing_fence_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "g.md").write_text("# T\n\n```divi5\n" + self.GOOD + "```\n")
            fails = check(Path(tmp))
        self.assertEqual([(str(p), label) for p, label, _ in fails], [("g.md", "fence-mismatch")])


if __name__ == "__main__":
    unittest.main()
