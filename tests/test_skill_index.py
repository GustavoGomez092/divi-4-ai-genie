import re
import unittest

from _paths import SKILL

# Two-level index: SKILL.md names these index pages, and each of them links every file it indexes (one hop).
# The generated module pages are reached through their module README the same way.
INDEX_PAGES = ("recipes/README.md", "recipes/divi5/README.md",
               "reference/modules/README.md", "reference/divi5/modules/README.md")

# Files an AI needs for any page of that Divi version: named in SKILL.md itself, never behind an index page.
CORE_DIVI4 = ("reference/page-format.md", "reference/structure.md", "reference/value-formats.md",
              "reference/modules/README.md", "reference/design-tokens.md", "reference/publishing.md",
              "reference/preview.md", "recipes/README.md")
CORE_DIVI5 = ("reference/divi5/page-format.md", "reference/divi5/structure.md", "reference/divi5/value-formats.md",
              "reference/divi5/design-families.md", "reference/divi5/modules/README.md", "recipes/divi5/README.md")

SCRIPTS = ("scripts/divi_format.py", "scripts/validate.py", "scripts/extract_tokens.py", "scripts/page_edit.py",
           "scripts/preview.py", "scripts/preview/preview.mjs", "scripts/publish.py")

LINK = re.compile(r"\]\(([^)\s]+)\)")
SKILL_PATH = re.compile(r"`((?:reference|recipes|scripts)/[^`\s<]+\.(?:md|py|mjs|json))`")  # `<slug>` = a pattern


def _linked_files(index_rel):
    """Skill-relative paths of every local file an index page links to."""
    page = SKILL / index_rel
    out = set()
    for link in LINK.findall(page.read_text()):
        if link.startswith(("http://", "https://", "#")):
            continue
        target = (page.parent / link.partition("#")[0]).resolve()
        if target.is_file() and SKILL.resolve() in target.parents:
            out.add(target.relative_to(SKILL.resolve()).as_posix())
    return out


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
        """Every .md in the skill is named in SKILL.md, or linked from an index page that SKILL.md names."""
        reachable = set(SKILL_PATH.findall(self.text))
        for page in INDEX_PAGES:
            reachable |= _linked_files(page)
        files = sorted(p.relative_to(SKILL).as_posix() for p in SKILL.rglob("*.md") if p.name != "SKILL.md")
        self.assertTrue([f for f in files if f.startswith(("reference/divi5/", "recipes/divi5/"))])
        missing = [f for f in files if f not in reachable]
        self.assertEqual(missing, [])

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
