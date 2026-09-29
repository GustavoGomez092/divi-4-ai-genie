"""Generated Divi 5 module references and design-family tables (research/tools/divi5/generate_docs5.py), the
hand-written references, and the Divi 5 recipes (recipes/divi5/, research/tools/divi5/port_recipe.py)."""
import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES5, SCHEMA5_RAW, SKILL, TOOLS5
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



RECIPES5 = SKILL / "recipes" / "divi5"
SAMPLE5 = RECIPES5 / "sample-tokens.json"
HEROES = ("hero-split", "hero-centered", "hero-background-image", "hero-fullwidth-header")
CONTENT_SECTIONS = ("services-grid", "alternating-features", "process-steps", "stats-counters", "service-area-list",
                    "tabs", "video", "gallery")
SECTIONS5 = HEROES + CONTENT_SECTIONS
STRUCTURE5 = ("divi/section", "divi/row", "divi/column", "divi/row-inner", "divi/column-inner")
LAYOUT_BLOCK = {"desktop": {"value": {"display": "block"}}}
import divi5_blocks as d5  # noqa: E402
import port_recipe  # noqa: E402  (research/tools/divi5, on sys.path above)


def _recipe_examples():
    """(relative path, is_page, source) of every ```divi5 example in recipes/divi5/{sections,pages}."""
    out = []
    for sub in ("sections", "pages"):
        for md in sorted((RECIPES5 / sub).glob("*.md")):
            for src in BLOCK5.findall(md.read_text()):
                out.append((md.relative_to(SKILL).as_posix(), sub == "pages", src.strip()))
    return out


def _strings(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)
    elif isinstance(node, str):
        yield node


def _worked_example(name):
    text = (RECIPES5 / "sections" / f"{name}.md").read_text()
    part = text.split("## Worked example (sample-tokens.json)", 1)[1]
    return BLOCK5.findall(part)[0].strip()


class Divi5RecipesTest(unittest.TestCase):
    """recipes/divi5/: sample tokens, the recipe files and their worked examples (Task 16 onward)."""

    @classmethod
    def setUpClass(cls):
        cls.tokens = json.loads(SAMPLE5.read_text())

    def test_sample_tokens_are_divi5_tokens_of_the_schema_version(self):
        site = self.tokens["site"]
        self.assertEqual(site["divi_major"], 5)
        self.assertEqual(site["divi_version"], SCHEMA5.meta["divi_version"])
        self.assertEqual(site["content_format"], "blocks")
        self.assertTrue(self.tokens["colors"]["global"])
        self.assertTrue(self.tokens["variables"])
        self.assertTrue(self.tokens["presets"])
        self.assertTrue(self.tokens["module_styles"])
        self.assertTrue(self.tokens["section_exemplars"])
        self.assertIn("extract_tokens.py", self.tokens["_note"])

    def test_sample_token_ids_come_from_the_fixtures(self):
        # Never invent an id: every gcid/gvid/preset id in the sample tokens is one the fixture HTML or the
        # brand-kit fixture content uses.
        fixtures = "".join(p.read_text() for p in (FIXTURES5 / "html").glob("*.html"))
        fixtures += (FIXTURES5 / "converted" / "brand-kit.html").read_text()
        ids = set(self.tokens["colors"]["global"]) | set(self.tokens["variables"])
        ids |= {p["id"] for lst in self.tokens["presets"].values() for p in lst}
        ids |= {p["id"] for lst in self.tokens.get("group_presets", {}).values() for p in lst}
        for i in ids:
            self.assertIn(i, fixtures, i)

    def test_section_recipes_have_every_part(self):
        for name in SECTIONS5:
            text = (RECIPES5 / "sections" / f"{name}.md").read_text()
            self.assertIn(f"](../../sections/{name}.md)", text, name)
            for heading in ("## Structure", "## Field mapping", "## Responsive rules",
                            "## Worked example (sample-tokens.json)", "## Checklist"):
                self.assertIn(heading, text, f"{name}: {heading}")
            self.assertTrue(_worked_example(name), name)

    def test_every_divi5_section_recipe_has_a_divi4_original(self):
        for md in (RECIPES5 / "sections").glob("*.md"):
            self.assertTrue((SKILL / "recipes" / "sections" / md.name).exists(), md.name)
            self.assertIn(f"](../../sections/{md.name})", md.read_text(), md.name)

    def test_recipe_examples_validate_against_the_sample_tokens_without_findings(self):
        examples = _recipe_examples()
        self.assertGreaterEqual(len(examples), len(HEROES))
        for rel, page, src in examples:
            findings = [(f.level, f.code, f.attr) for f in validate_source(src, tokens=self.tokens, fragment=not page)]
            self.assertEqual(findings, [], rel)

    def test_recipe_examples_use_the_layout_form_and_the_schema_version(self):
        version = SCHEMA5.meta["divi_version"]
        known = {p["id"] for lst in self.tokens["presets"].values() for p in lst}
        for rel, _page, src in _recipe_examples():
            doc = d5.parse(src)
            self.assertEqual(doc.problems, [], rel)
            for block, path, _parent in doc.walk():
                where = f"{rel}: {path}"
                self.assertEqual(block.attrs.get("builderVersion"), version, where)
                self.assertNotIn("locked", block.attrs, where)
                self.assertTrue(set(block.attrs.get("modulePreset", [])) <= known, where)
                if block.name in STRUCTURE5:
                    self.assertEqual(d5.get_attr(block, "module.decoration.layout", None, None), LAYOUT_BLOCK, where)
                if block.name in ("divi/row", "divi/row-inner"):
                    self.assertTrue(d5.get_attr(block, "module.advanced.columnStructure"), where)
                if block.name in ("divi/column", "divi/column-inner"):
                    self.assertTrue(d5.get_attr(block, "module.advanced.type"), where)

    def test_hero_examples_reference_the_sample_tokens_ids_not_their_values(self):
        # References over literals: the sample tokens hold global colors for the brand navy and orange and a
        # section-padding variable, so the heroes reference them and never repeat the literal values.
        for name in HEROES:
            src = _worked_example(name)
            refs = {r["value"]["name"] for b, _p, _x in d5.parse(src).walk() for v in _strings(b.attrs)
                    for r in d5.variable_refs(v)}
            self.assertIn("gcid-r6navy0001", refs, name)
            self.assertIn("gvid-r6secpad01", refs, name)
            for literal in ("#0b2a3c", "#f97316", "96px"):
                self.assertNotIn(literal, src.lower(), f"{name}: {literal}")

    def test_examples_keep_canonical_escapes_in_the_files(self):
        # Docs hazard: a file writer that decodes \uXXXX would leave raw quotes and tags in the JSON.
        B = chr(92)
        for name in SECTIONS5:
            src = _worked_example(name)
            self.assertIn(B + "u0022", src, name)   # the quotes inside every $variable() reference
            self.assertNotIn(B + '"', src, name)
            doc = d5.parse(src)
            self.assertEqual("".join(d5.render_block(b) for b in doc.nodes), src, name)   # canonical, byte for byte

    def test_orange_buttons_and_tabs_have_a_navy_label_and_a_legible_hover(self):
        # Contrast (Task 16 review ruling): white on the brand orange is 2.8:1 and navy on the old #ea580c hover
        # 4.2:1, both below WCAG AA; the examples put a navy label on orange and hover to the light orange.
        orange = {ORANGE_REF, ACCENT_REF}
        checked = 0
        for rel, _page, src in _recipe_examples():
            self.assertNotIn("r6btnpreset1", src, rel)            # its css is a white label on the orange
            self.assertNotIn("#ea580c", src.lower(), rel)
            for block, path, _x in d5.parse(src).walk():
                pairs = [(f"{el}.decoration.background", f"{el}.decoration.font.font")
                         for el in ("button", "buttonOne", "buttonTwo")] + \
                        [("activeTab.decoration.background", "activeTab.decoration.font.font")]
                for bg_attr, font_attr in pairs:
                    bg = d5.get_attr(block, bg_attr, None, None) or {}
                    if (bg.get("desktop", {}).get("value") or {}).get("color") not in orange:
                        continue
                    checked += 1
                    font = d5.get_attr(block, font_attr) or {}
                    self.assertEqual(font.get("color"), NAVY_REF, f"{rel}: {path} {font_attr}")
                    hover = (bg["desktop"].get("hover") or {}).get("color")
                    self.assertIn(hover, (None, ORANGE_LT_REF), f"{rel}: {path} {bg_attr} hover")
        self.assertGreaterEqual(checked, 5)

    def test_section_recipes_check_contrast(self):
        for name in SECTIONS5:
            checklist = (RECIPES5 / "sections" / f"{name}.md").read_text().split("## Checklist", 1)[1]
            self.assertIn("- [ ] contrast:", checklist, name)
            self.assertIn("](../README.md#contrast)", checklist, name)

    def test_markdown_table_rows_match_their_header(self):
        # A row with a missing or an extra cell loses text in GFM (a hero's fallback column once did).
        pipe = re.compile(r"(?<!\\)\|")
        bad = []
        for page in sorted(RECIPES5.rglob("*.md")):
            prose = re.sub(r"```.*?```", lambda m: "\n" * m.group(0).count("\n"), page.read_text(), flags=re.S)
            header = None
            for n, line in enumerate(prose.splitlines(), 1):
                if not line.startswith("|"):
                    header = None
                    continue
                cells = len(pipe.split(line.strip().strip("|")))
                if header is None:
                    header = cells
                elif cells != header:
                    bad.append((page.relative_to(RECIPES5).as_posix(), n, cells, header))
        self.assertEqual(bad, [])

    def test_readme_indexes_every_divi5_recipe_and_the_sample_tokens(self):
        readme = (RECIPES5 / "README.md").read_text()
        self.assertIn("](sample-tokens.json)", readme)
        self.assertIn("stored as `" + chr(92) + "u0022`", readme)   # docs hazard: the escape must survive
        for md in sorted(RECIPES5.rglob("*.md")):
            if md.name != "README.md":
                self.assertIn(f"]({md.relative_to(RECIPES5).as_posix()})", readme, md.name)

    def test_readme_and_recipe_links_resolve(self):
        broken = []
        for page in sorted(RECIPES5.rglob("*.md")):
            for link in LINK.findall(page.read_text()):
                if link.startswith(("http://", "https://")):
                    continue
                target, _, anchor = link.partition("#")
                path = (page.parent / target).resolve() if target else page
                if not path.exists() or (anchor and path.suffix == ".md" and anchor not in _anchors(path)):
                    broken.append((page.relative_to(RECIPES5).as_posix(), link))
        self.assertEqual(broken, [])


CONVERTED = FIXTURES5 / "converted" / "brand-kit.html"
NAVY_REF = '$variable({"type":"color","value":{"name":"gcid-r6navy0001","settings":{}}})$'
ORANGE_REF = '$variable({"type":"color","value":{"name":"gcid-r6orange001","settings":{}}})$'
ORANGE_LT_REF = '$variable({"type":"color","value":{"name":"gcid-r6orangelt1","settings":{}}})$'
ACCENT_REF = '$variable({"type":"color","value":{"name":"gcid-primary-color","settings":{}}})$'


class PortRecipeTest(unittest.TestCase):
    """research/tools/divi5/port_recipe.py, offline (the conversion step is exercised live in Task 16's report)."""

    @classmethod
    def setUpClass(cls):
        cls.tokens = json.loads(SAMPLE5.read_text())

    def test_extracts_the_divi4_worked_example(self):
        text = (SKILL / "recipes" / "sections" / "hero-split.md").read_text()
        src = port_recipe.extract_example(text)
        self.assertTrue(src.startswith("[et_pb_section"))
        self.assertTrue(src.endswith("[/et_pb_section]"))

    def _cleaned(self, source=None):
        return port_recipe.clean(source or CONVERTED.read_text(), "hero-split", self.tokens)

    def test_clean_sets_the_schema_version_and_drops_locked_and_default_presets(self):
        src = CONVERTED.read_text().replace('"modulePreset":["default"]', '"modulePreset":["default"],"locked":"off"', 1)
        sections = self._cleaned(src)
        self.assertEqual([s.name for s in sections], ["divi/section"] * 5)   # the placeholder wrapper is removed
        for s in sections:
            for block, _p, _x in d5.parse(d5.render_block(s)).walk():
                self.assertEqual(block.attrs["builderVersion"], SCHEMA5.meta["divi_version"])
                self.assertNotIn("locked", block.attrs)
                self.assertNotEqual(block.attrs.get("modulePreset"), ["default"])
                self.assertEqual(list(block.attrs)[-1], "builderVersion")

    def test_clean_keeps_known_presets_and_drops_unknown_ones(self):
        known = CONVERTED.read_text()
        cta = [b for s in self._cleaned(known) for b, _p, _x in d5.parse(d5.render_block(s)).walk()
               if b.attrs.get("modulePreset")]
        self.assertEqual([b.attrs["modulePreset"] for b in cta], [["11111111-2222-3333-4444-555555555555"]])
        unknown = known.replace("11111111-2222-3333-4444-555555555555", "99999999-2222-3333-4444-555555555555")
        self.assertFalse([b for s in self._cleaned(unknown) for b, _p, _x in d5.parse(d5.render_block(s)).walk()
                          if b.attrs.get("modulePreset")])

    def test_clean_replaces_literals_with_references_by_role(self):
        out = "".join(d5.render_block(s) for s in self._cleaned())
        doc = d5.parse(out)
        hero = doc.find("section[0]")
        self.assertEqual(d5.get_attr(hero, "module.decoration.background")["color"], NAVY_REF)
        # #ffffff has no global in the sample tokens: it stays literal
        heading = doc.find("section[0] > row[0] > column[0] > heading[0]")
        self.assertEqual(d5.get_attr(heading, "title.decoration.font.font")["color"], "#ffffff")
        self.assertNotIn("#0b2a3c", out.lower())

    def test_clean_drops_render_defaults_empty_values_and_module_layout(self):
        doc = d5.parse("".join(d5.render_block(s) for s in self._cleaned()))
        hero = doc.find("section[0]")
        padding = d5.get_attr(hero, "module.decoration.spacing")["padding"]
        self.assertNotIn("right", padding)
        self.assertEqual(padding["top"], "96px")
        heading = doc.find("section[0] > row[0] > column[0] > heading[0]")
        self.assertIsNone(d5.get_attr(heading, "module.decoration.layout"))       # modules need no layout
        self.assertEqual(d5.get_attr(heading, "title.decoration.font.font")["headingLevel"], "h1")  # kept: SEO
        column = doc.find("section[0] > row[0] > column[0]")
        self.assertEqual(d5.get_attr(column, "module.decoration.layout"), LAYOUT_BLOCK["desktop"]["value"])
        button = doc.find("section[2] > row[0] > column[0] > button[0]")
        self.assertEqual(d5.get_attr(button, "button.decoration.button"), {"enable": "on"})
        src = ('<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},'
               '"builderVersion":"5.0.0"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":'
               '{"value":"4_4"}}}}} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}}}} '
               '--><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Go","linkUrl":"/"}}},'
               '"decoration":{"button":{"desktop":{"value":{"enable":"on","icon":{"enable":"on"}}}}}},'
               '"module":{"advanced":{"html":{"desktop":{"value":{"elementType":"a"}}}}}} /--><!-- /wp:divi/column '
               '--><!-- /wp:divi/row --><!-- /wp:divi/section -->')
        doc = d5.parse("".join(d5.render_block(s) for s in port_recipe.clean(src, "x", self.tokens)))
        button = doc.find("section[0] > row[0] > column[0] > button[0]")
        self.assertEqual(d5.get_attr(button, "button.decoration.button"), {"enable": "on"})   # icon default gone
        self.assertNotIn("module", button.attrs)                                              # html default gone
        row = doc.find("section[0] > row[0]")
        self.assertEqual(d5.get_attr(row, "module.decoration.layout"), {"display": "block"})  # layout form added

    def test_clean_regenerates_attribute_row_ids_deterministically(self):
        rows = {"desktop": {"value": {"attributes": [
            {"id": "4f1c2b7e-9a53-4d2e-8f61-0c7b5e2a9d14", "name": "class", "value": "a", "adminLabel": "A"},
            {"id": "4f1c2b7e-9a53-4d2e-8f61-0c7b5e2a9d14", "name": "data-x", "value": "b", "adminLabel": "B"}]}}}
        text = d5.new_block("text", {"content": {"innerContent": {"desktop": {"value": "<p>x</p>"}}},
                                     "module": {"decoration": {"attributes": rows}}})
        col = d5.new_block("column", {"module": {"advanced": {"type": {"desktop": {"value": "4_4"}}}}}, [text])
        row = d5.new_block("row", {"module": {"advanced": {"columnStructure": {"desktop": {"value": "4_4"}}}}}, [col])
        src = d5.render_block(d5.new_block("section", {}, [row]))

        def ids(name):
            doc = d5.parse("".join(d5.render_block(s) for s in port_recipe.clean(src, name, self.tokens)))
            got = d5.get_attr(doc.find("section[0] > row[0] > column[0] > text[0]"), "module.decoration.attributes")
            return [r["id"] for r in got["attributes"]]
        first = ids("hero-split")
        self.assertEqual(first, ids("hero-split"))
        self.assertNotEqual(first, ids("hero-centered"))
        self.assertEqual(len(set(first)), 2)
        self.assertNotIn("4f1c2b7e-9a53-4d2e-8f61-0c7b5e2a9d14", first)
        import uuid
        self.assertEqual(first[0], str(uuid.uuid5(uuid.NAMESPACE_URL, "divi-genie/recipes/divi5/hero-split/0")))

    def test_main_writes_a_validated_draft_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            converted = Path(tmp) / "converted.html"
            converted.write_text(CONVERTED.read_text())
            out = Path(tmp) / "hero-split.md"
            argv = [str(SKILL / "recipes" / "sections" / "hero-split.md"), "--converted", str(converted),
                    "--out", str(out), "--tokens", str(SAMPLE5)]
            with contextlib.redirect_stdout(io.StringIO()) as so:
                self.assertEqual(port_recipe.main(argv), 0)
            self.assertIn("0 error(s)", so.getvalue())
            draft = out.read_text()
            self.assertIn("](../../sections/hero-split.md)", draft)
            for heading in ("## Structure", "## Field mapping", "## Responsive rules",
                            "## Worked example (sample-tokens.json)", "## Checklist"):
                self.assertIn(heading, draft)
            example = BLOCK5.findall(draft)[0].strip()
            self.assertEqual([f.code for f in validate_source(example, fragment=True) if f.level == "error"], [])
            with contextlib.redirect_stderr(io.StringIO()) as se:
                self.assertEqual(port_recipe.main(argv), 2)       # 2: the target exists, no --force
            self.assertIn("--force", se.getvalue())
            self.assertEqual(out.read_text(), draft)

    def test_main_fails_when_the_port_does_not_validate_but_still_writes_the_draft(self):
        bad = ('<!-- wp:divi/section {"builderVersion":"5.0.0"} --><!-- wp:divi/row {"module":{"advanced":'
               '{"columnStructure":{"desktop":{"value":"4_4"}}}}} --><!-- wp:divi/column {"module":{"advanced":'
               '{"type":{"desktop":{"value":"4_4"}}}}} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":'
               '{"value":"Hi"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2",'
               '"size":"big"}}}}}}} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->')
        with tempfile.TemporaryDirectory() as tmp:
            converted = Path(tmp) / "converted.html"
            converted.write_text(bad)
            out = Path(tmp) / "hero-split.md"
            argv = [str(SKILL / "recipes" / "sections" / "hero-split.md"), "--converted", str(converted),
                    "--out", str(out), "--tokens", str(SAMPLE5)]
            with contextlib.redirect_stdout(io.StringIO()) as so:
                self.assertEqual(port_recipe.main(argv), 1)       # 1: draft written, with validation errors
            self.assertIn("E5_BAD_VALUE", so.getvalue())
            self.assertIn("1 error(s)", so.getvalue())
            self.assertIn("E5_BAD_VALUE", out.read_text())      # the draft is written, findings in its comment


if __name__ == "__main__":
    unittest.main()
