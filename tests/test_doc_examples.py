import unittest

from _paths import SKILL
from check_doc_examples import check


class DocExamplesTest(unittest.TestCase):
    def test_all_divi_blocks_validate(self):
        self.assertEqual(check(SKILL), [])


if __name__ == "__main__":
    unittest.main()
