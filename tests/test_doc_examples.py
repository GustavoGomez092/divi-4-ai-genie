import tempfile
import unittest
from pathlib import Path

from _paths import SKILL
from check_doc_examples import check


class DocExamplesTest(unittest.TestCase):
    def test_all_divi_blocks_validate(self):
        self.assertEqual(check(SKILL), [])

    def test_glued_closing_fence_is_reported(self):
        # A closing ``` glued to the last content line (no newline before it) instead of on its
        # own line means BLOCK_RE never matches this block at all — check() must still flag the
        # file rather than silently reporting 0 blocks / 0 failures for it.
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            (skill_dir / "glued.md").write_text(
                "# Test\n\n"
                "## Worked example\n"
                "```divi\n"
                '[et_pb_section][et_pb_row][et_pb_column type="4_4"][/et_pb_column][/et_pb_row][/et_pb_section]```\n'
            )
            fails = check(skill_dir)

        self.assertEqual(len(fails), 1)
        path, label, errs = fails[0]
        self.assertEqual(str(path), "glued.md")
        self.assertEqual(label, "fence-mismatch")
        self.assertEqual(errs[0][0], "E_FENCE_MISMATCH")


    def _check_one(self, rel, block):
        with tempfile.TemporaryDirectory() as tmp:
            md = Path(tmp) / rel
            md.parent.mkdir(parents=True, exist_ok=True)
            md.write_text("# T\n\n```divi\n" + block + "\n```\n")
            return [code for _p, _i, errs in check(Path(tmp)) for code, *_ in errs]

    H2_ONLY = ('[et_pb_section][et_pb_row][et_pb_column type="4_4"][et_pb_heading title="Sub" title_level="h2"]'
               '[/et_pb_heading][/et_pb_column][/et_pb_row][/et_pb_section]')

    def test_fragments_are_not_asked_for_an_h1(self):
        self.assertEqual(self._check_one("recipes/sections/x.md", self.H2_ONLY), [])
        self.assertEqual(self._check_one("reference/x.md", self.H2_ONLY), [])

    def test_page_recipes_must_have_an_h1(self):
        self.assertEqual(self._check_one("recipes/pages/x.md", self.H2_ONLY), ["W_NO_H1"])

    def test_heading_skips_fail_any_example(self):
        skip = self.H2_ONLY.replace("[/et_pb_heading]", '[/et_pb_heading][et_pb_blurb title="B" header_level="h4"][/et_pb_blurb]')
        self.assertEqual(self._check_one("recipes/sections/x.md", skip), ["W_HEADING_SKIP"])


if __name__ == "__main__":
    unittest.main()
