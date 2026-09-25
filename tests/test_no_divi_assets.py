"""Guard: no licensed Divi assets in the repository.

Fails if any git-tracked file contains the id of an inlined copy of Divi's stylesheet (the markers a
saved Divi page carries) or is a .zip (a Divi build). The markers are assembled at runtime so this
file does not match itself; nothing else in the tree may spell them out literally.
"""
import subprocess
import unittest

from _paths import ROOT

MARKERS = ("divi-style-css" + "-inlined", "divi-dynamic-critical" + "-inline-css")


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True)
    return [p for p in out.stdout.decode("utf-8").split("\0") if p]


class NoDiviAssetsTest(unittest.TestCase):
    def test_no_tracked_zip(self):
        self.assertEqual([p for p in tracked_files() if p.lower().endswith(".zip")], [])

    def test_no_tracked_file_contains_divi_stylesheet_markers(self):
        hits = []
        for rel in tracked_files():
            path = ROOT / rel
            if not path.is_file():
                continue  # deleted in the working tree but not yet committed
            data = path.read_bytes()
            hits += [f"{rel}: {m}" for m in MARKERS if m.encode() in data]
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
