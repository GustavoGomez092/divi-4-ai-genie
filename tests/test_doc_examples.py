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


if __name__ == "__main__":
    unittest.main()
