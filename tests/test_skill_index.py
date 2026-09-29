import re
import unittest

from _paths import SKILL

# Two-level index: SKILL.md names these index pages, and each of them links every file it indexes (one hop).
# The generated module pages are reached through their module README the same way. Reachability is checked per
# version: a Divi 4 file must be reachable from a Divi 4 index page, a Divi 5 file (under a `divi5/` directory)
# from a Divi 5 one, so the Divi 5 recipe README's "Divi 4 original" links can't stand in for the Divi 4 index.
INDEX_DIVI4 = ("recipes/README.md", "reference/modules/README.md")
INDEX_DIVI5 = ("recipes/divi5/README.md", "reference/divi5/modules/README.md")
INDEX_PAGES = INDEX_DIVI4 + INDEX_DIVI5

# Files an AI needs for any page of that Divi version: named in SKILL.md itself, never behind an index page.
CORE_DIVI4 = ("reference/page-format.md", "reference/structure.md", "reference/value-formats.md",
              "reference/modules/README.md", "reference/design-tokens.md", "reference/publishing.md",
              "reference/preview.md", "recipes/README.md")
CORE_DIVI5 = ("reference/divi5/page-format.md", "reference/divi5/structure.md", "reference/divi5/value-formats.md",
              "reference/divi5/design-families.md", "reference/divi5/modules/README.md", "recipes/divi5/README.md")

SCRIPTS = ("scripts/divi_format.py", "scripts/divi5_blocks.py", "scripts/validate.py", "scripts/extract_tokens.py", "scripts/page_edit.py",
           "scripts/preview.py", "scripts/preview/preview.mjs", "scripts/publish.py")

LINK = re.compile(r"\]\(([^)\s]+)\)")
SKILL_PATH = re.compile(r"`((?:reference|recipes|scripts)/[^`\s<]+\.(?:md|py|mjs|json))`")  # `<slug>` = a pattern


def _linked_files(index_rel, text=None):
    """Skill-relative paths of every local file an index page links to (`text` overrides the page's content)."""
    page = SKILL / index_rel
    out = set()
    for link in LINK.findall(page.read_text() if text is None else text):
        if link.startswith(("http://", "https://", "#")):
            continue
        target = (page.parent / link.partition("#")[0]).resolve()
        if target.is_file() and SKILL.resolve() in target.parents:
            out.add(target.relative_to(SKILL.resolve()).as_posix())
    return out


def _is_divi5(rel):
    return "divi5/" in rel


def unindexed(skill_text, overrides=None):
    """Skill .md files not named in SKILL.md and not linked from an index page of their own Divi version.
    `overrides` maps an index page to replacement text (used to prove the check can fail)."""
    overrides = overrides or {}
    named = set(SKILL_PATH.findall(skill_text))
    linked4, linked5 = set(), set()
    for pages, linked in ((INDEX_DIVI4, linked4), (INDEX_DIVI5, linked5)):
        for page in pages:
            linked |= _linked_files(page, overrides.get(page))
    files = sorted(p.relative_to(SKILL).as_posix() for p in SKILL.rglob("*.md") if p.name != "SKILL.md")
    return [f for f in files if f not in named and f not in (linked5 if _is_divi5(f) else linked4)]


class SkillIndexTest(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text()

    def test_frontmatter(self):
        m = re.match(r"^---\nname: divi-page-builder\ndescription: (Use when .+)\n---\n", self.text)
        self.assertIsNotNone(m)
        self.assertLessEqual(len(m.group(1)), 500)
        for trigger in ("Divi Genie", "Divi 4 AI Genie", "Divi 5 AI Genie", "Divi 5", "wp:divi/"):
            self.assertIn(trigger, m.group(1))

    def test_index_pages_are_named_in_skill_md(self):
        for page in INDEX_PAGES:
            self.assertIn(f"`{page}`", self.text, page)

    def test_every_skill_file_is_indexed(self):
        """Every .md in the skill is named in SKILL.md, or linked from an index page of its version that SKILL.md
        names."""
        files = [p.relative_to(SKILL).as_posix() for p in SKILL.rglob("*.md")]
        self.assertTrue([f for f in files if _is_divi5(f)])
        self.assertEqual(unindexed(self.text), [])

    def test_the_index_check_catches_a_missing_divi4_recipe_row(self):
        """Mutation: drop one recipe's row from recipes/README.md's index (in memory). recipes/divi5/README.md still
        links that Divi 4 recipe as a "Divi 4 original", which must not count."""
        readme = (SKILL / "recipes/README.md").read_text()
        row = next(line for line in readme.splitlines() if "](sections/faq.md)" in line)
        self.assertIn("../sections/faq.md", (SKILL / "recipes/divi5/README.md").read_text())
        mutated = readme.replace(row + "\n", "")
        self.assertEqual(unindexed(self.text, {"recipes/README.md": mutated}), ["recipes/sections/faq.md"])

    def test_the_index_check_catches_a_missing_divi5_recipe_row(self):
        readme = (SKILL / "recipes/divi5/README.md").read_text()
        row = next(line for line in readme.splitlines() if "](sections/faq.md)" in line)
        mutated = readme.replace(row + "\n", "")
        self.assertEqual(unindexed(self.text, {"recipes/divi5/README.md": mutated}), ["recipes/divi5/sections/faq.md"])

    def test_every_index_entry_exists(self):
        named = SKILL_PATH.findall(self.text)
        self.assertTrue(named)
        self.assertEqual([rel for rel in named if not (SKILL / rel).exists()], [])
        for page in INDEX_PAGES:
            base = (SKILL / page).parent
            broken = [link for link in LINK.findall((SKILL / page).read_text())
                      if not link.startswith(("http://", "https://", "#"))
                      and not (base / link.partition("#")[0]).exists()]
            self.assertEqual(broken, [], page)

    def test_core_files_are_one_hop_from_skill_md(self):
        for rel in CORE_DIVI4 + CORE_DIVI5:
            self.assertIn(f"`{rel}`", self.text, rel)

    def test_scripts_are_documented(self):
        for script in SCRIPTS:
            self.assertIn(script, self.text)

    def test_divi5_hard_rules(self):
        rules = self.text.split("## Hard rules", 1)[1].split("\n## ", 1)[0]
        for phrase in ("wp:divi/", "builderVersion", "tokens.json", "modulePreset", "&#91;", "&#93;",
                       "publish.py", "shortcode on a Divi 5 site"):
            self.assertIn(phrase, rules, phrase)

    def test_workflow_starts_with_which_divi(self):
        workflow = self.text.split("## Workflow", 1)[1].split("\n## ", 1)[0]
        first = workflow.strip().splitlines()[0]
        self.assertIn("Which Divi?", first)
        self.assertIn("site.divi_major", first)
        self.assertIn("divi_format.py site URL", first)

    def test_short_enough(self):
        self.assertLess(len(self.text.split()), 1200)


if __name__ == "__main__":
    unittest.main()
