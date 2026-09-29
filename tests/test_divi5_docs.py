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
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp)
            (skill / "reference" / "divi5").mkdir(parents=True)
            shutil.copy(REF5 / "design-families.md", skill / "reference" / "divi5" / "design-families.md")
            with contextlib.redirect_stdout(io.StringIO()):
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

    def test_bare_font_attr_is_marked_as_a_container(self):
        # Divi 5.13.1 styles text only from ….decoration.font.font (FontStyle.php); keys written directly under
        # ….decoration.font render nothing (live check on blurb, heading and toggle, task 9 report).
        blurb = (MODULES5 / "blurb.md").read_text()
        bare = [l for l in blurb.splitlines() if l.startswith("| `title.decoration.font` |")]
        self.assertEqual(len(bare), 1)
        self.assertIn("`title.decoration.font.font`", bare[0])
        fonts = [l for l in blurb.splitlines() if l.startswith("| `title.decoration.font.font` |")]
        self.assertNotIn("don't write", fonts[0])
        families = (REF5 / "design-families.md").read_text()
        section = families.split('<a id="font"></a>', 1)[1].split("\n## ", 1)[0]
        bare_table = section.split("### `….decoration.font`\n", 1)[1].split("### ", 1)[0]
        self.assertIn("….decoration.font.font", bare_table.split("| key |", 1)[0])

    def test_icon_notes_explain_the_divi4_string_conversion(self):
        for page in ("blurb", "button"):
            text = (MODULES5 / f"{page}.md").read_text()
            self.assertIn("||", text, page)
            self.assertIn("value-formats.md#icons", text, page)

    def test_legacy_conversion_attrs_are_tagged(self):
        row = (MODULES5 / "row.md").read_text()
        lines = row.splitlines()
        legacy = [l for l in lines if l.startswith(("| `customCssMain1` |", "| `padding1Phone` |",
                                                     "| `columns.column-1.spacing` |"))]
        self.assertTrue(legacy)
        for l in legacy:
            self.assertIn("legacy (D4 conversion)", l)
        self.assertIn("Legacy", row.split("## Meta and block-level attributes", 1)[1])
        for keep in ("| `css` |", "| `adminLabel` |", "| `locked` |"):
            for l in (l for l in lines if l.startswith(keep)):
                self.assertNotIn("legacy", l)
        for name in ("padding1Phone", "padding2Tablet", "padding3LastEdited", "customCssMain1"):
            rows = [l for l in lines if l.startswith(f"| `{name}` |")]
            self.assertTrue(rows, name)
            self.assertIn("style each column on its own `divi/column` block", rows[0], name)
        section = (MODULES5 / "section.md").read_text()
        self.assertTrue(any(l.startswith("| `columnsPadding` |") and "legacy (D4 conversion)" in l
                            for l in section.splitlines()))
        text = (MODULES5 / "text.md").read_text()
        self.assertNotIn("legacy (D4 conversion)", text)

    def test_design_families_prose_and_markers(self):
        text = (REF5 / "design-families.md").read_text()
        head, rest = text.split("<!-- BEGIN GENERATED -->", 1)
        self.assertIn("<!-- END GENERATED -->", rest)
        self.assertIn("$variable", head)   # the hand-written prose explains $variable values
        used = {spec["family"] for n in IN_SCOPE for spec in SCHEMA5.module(n).attrs.values() if "family" in spec}
        for fam in used:
            self.assertIn(f'<a id="{fam}"></a>', rest, fam)


HAND_WRITTEN = ("page-format.md", "structure.md", "value-formats.md")
BLOCK5 = re.compile(r"^```divi5\n(.*?)^```", re.S | re.M)
LINK = re.compile(r"\]\(([^)\s]+)\)")


def _slug(heading: str) -> str:
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def _anchors(path: Path) -> set:
    text = path.read_text()
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    return {_slug(h) for h in re.findall(r"^#+ (.*)$", prose, re.M)} | set(re.findall(r'<a id="([^"]+)"', text))


class HandWrittenReferencesTest(unittest.TestCase):
    """reference/divi5/{page-format,structure,value-formats}.md (Task 9)."""

    def test_examples_validate_without_any_finding(self):
        for name in HAND_WRITTEN:
            blocks = BLOCK5.findall((REF5 / name).read_text())
            self.assertTrue(blocks, name)
            for i, src in enumerate(blocks):
                findings = [(f.level, f.code, f.attr) for f in validate_source(src.strip(), fragment=True)]
                self.assertEqual(findings, [], f"{name} block {i}")

    def test_examples_carry_the_schema_builder_version(self):
        version = SCHEMA5.meta["divi_version"]
        for name in HAND_WRITTEN:
            for src in BLOCK5.findall((REF5 / name).read_text()):
                self.assertIn(f'"builderVersion":"{version}"', src, name)
                self.assertNotIn('"builderVersion":"', src.replace(f'"builderVersion":"{version}"', ""), name)

    def test_relative_links_and_anchors_resolve(self):
        pages = [REF5 / n for n in HAND_WRITTEN] + [REF5 / "design-families.md"] + sorted(MODULES5.glob("*.md"))
        broken = []
        for page in pages:
            for link in LINK.findall(page.read_text()):
                if link.startswith(("http://", "https://")):
                    continue
                target, _, anchor = link.partition("#")
                path = (page.parent / target).resolve() if target else page
                if not path.exists():
                    broken.append((page.name, link))
                elif anchor and path.suffix == ".md" and anchor not in _anchors(path):
                    broken.append((page.name, link))
        self.assertEqual(broken, [])

    def test_escaping_table_shows_the_escapes(self):
        # Regression: an earlier write decoded the \\uXXXX sequences, so the table said `"` -> `"`.
        B = chr(92)
        text = (REF5 / "page-format.md").read_text()
        table = text.split("## Canonical JSON escaping, and why", 1)[1].split("\n\n|", 1)[1].split("\n\n", 1)[0]
        rows = [r for r in ("|" + table).splitlines() if r.startswith("| `")]
        self.assertGreaterEqual(len(rows), 7)
        for code in ("0022", "003c", "003e", "0026", "002d" + B + "u002d", "005c"):
            self.assertIn(f"`{B}u{code}`", table, code)
        for row in rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            self.assertNotEqual(cells[0], cells[1], row)
        values = (REF5 / "value-formats.md").read_text()
        for escape in ("0022", "003c", "0026#xf095;"):
            self.assertIn(f"`{B}u{escape}`", values, escape)
        for name in HAND_WRITTEN + ("design-families.md",):
            prose = BLOCK5.sub("", (REF5 / name).read_text())
            stray = [hex(ord(c)) for c in prose if 0xE000 <= ord(c) <= 0xF8FF or ord(c) in (0x2028, 0x2029)]
            self.assertEqual(stray, [], name)

    def test_cited_validator_codes_exist(self):
        scripts = SKILL / "scripts"
        source = "".join(p.read_text() for p in scripts.glob("*.py"))
        for name in HAND_WRITTEN:
            for code in set(re.findall(r"`([EW]5?_[A-Z0-9_]{3,})`", (REF5 / name).read_text())):
                self.assertTrue(f'"{code}"' in source, f"{name} cites {code}, which no validator script reports")

    def test_skill_index_lists_the_divi5_references(self):
        index = (SKILL / "SKILL.md").read_text()
        for rel in re.findall(r"`(reference/divi5/[^`]+)`", index):
            self.assertTrue((SKILL / rel).exists(), rel)
        for name in HAND_WRITTEN:
            self.assertIn(f"reference/divi5/{name}", index)


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
