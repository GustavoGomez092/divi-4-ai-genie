import re
import unittest

from _paths import SKILL


class SkillIndexTest(unittest.TestCase):
    def setUp(self):
        self.text = (SKILL / "SKILL.md").read_text()

    def test_frontmatter(self):
        m = re.match(r"^---\nname: divi-page-builder\ndescription: (Use when .+)\n---\n", self.text)
        self.assertIsNotNone(m)
        self.assertLessEqual(len(m.group(1)), 500)

    def test_every_reference_and_recipe_is_indexed(self):
        files = [p.relative_to(SKILL).as_posix() for p in SKILL.rglob("*.md")
                 if p.name != "SKILL.md" and "reference/modules/et_pb_" not in p.as_posix()]
        missing = [f for f in files if f not in self.text]
        self.assertEqual(missing, [])

    def test_scripts_are_documented(self):
        for script in ("scripts/validate.py", "scripts/extract_tokens.py", "scripts/page_edit.py", "scripts/preview.py", "scripts/preview/preview.mjs", "scripts/publish.py"):
            self.assertIn(script, self.text)

    def test_short_enough(self):
        self.assertLess(len(self.text.split()), 1200)


if __name__ == "__main__":
    unittest.main()
