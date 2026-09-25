import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS

PAGE = FIXTURES / "valid" / "handwritten-landing.txt"
SRC = PAGE.read_text()


def run(*args):
    out = subprocess.run([sys.executable, str(SCRIPTS / "page_edit.py"), str(PAGE), *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise AssertionError(out.stderr)
    return out.stdout


class PageEditTest(unittest.TestCase):
    def test_outline_lists_sections(self):
        out = run("outline")
        self.assertIn("et_pb_section[0]  admin_label=Hero", out)
        self.assertIn("et_pb_section[3]  admin_label=Closing", out)

    def test_set_attr_changes_only_that_attribute(self):
        out = run("set-attr", "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_heading[0]", "title", 'Miami "24/7" Plumber')
        self.assertEqual(out, SRC.replace('title="Emergency Plumber in Miami"', 'title="Miami %2224/7%22 Plumber"', 1))

    def test_insert_after_section_is_surgical(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write('[et_pb_section admin_label="New"][et_pb_row][et_pb_column type="4_4"][/et_pb_column][/et_pb_row][/et_pb_section]')
        out = run("insert-after", "et_pb_section[1]", f.name)
        Path(f.name).unlink()
        head_end = SRC.index('[et_pb_section specialty="on"')
        self.assertEqual(out[:head_end], SRC[:head_end])
        self.assertTrue(out.endswith(SRC[head_end:]))
        self.assertIn('admin_label="New"', out[head_end - 1:head_end + 120])

    def test_replace_and_delete(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("[et_pb_text]<p>Replaced</p>[/et_pb_text]")
        path = "et_pb_section[2] > et_pb_column[0] > et_pb_text[0]"
        out = run("replace", path, f.name)
        Path(f.name).unlink()
        self.assertIn("<p>Replaced</p>", out)
        self.assertNotIn("<p>Sidebar note.</p>", out)
        self.assertNotIn("admin_label=\"Closing\"", run("delete", "et_pb_section[3]"))

    def test_bad_path_fails_cleanly(self):
        proc = subprocess.run([sys.executable, str(SCRIPTS / "page_edit.py"), str(PAGE), "extract", "et_pb_section[9]"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("no node at", proc.stderr)


if __name__ == "__main__":
    unittest.main()
