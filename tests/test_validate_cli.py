import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from _paths import FIXTURES
from validate import Finding, main

FIXTURE = str(FIXTURES / "valid" / "handwritten-landing.txt")


class CliTest(unittest.TestCase):
    def test_schema_load_failure_exits_2(self):
        with patch("validate.load_schema", side_effect=FileNotFoundError("schema dir missing")):
            with redirect_stdout(io.StringIO()):
                rc = main([FIXTURE])
        self.assertEqual(rc, 2)

    def test_json_warning_count_excludes_preexisting(self):
        findings = [
            Finding("warning", "W_ONE", "msg", 1, 1, "path", preexisting=False),
            Finding("warning", "W_TWO", "msg", 1, 1, "path", preexisting=True),
        ]
        with patch("validate.validate_source", return_value=findings):
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([FIXTURE, "--json"])
        data = json.loads(buf.getvalue())
        self.assertEqual(data["warnings"], 1)
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
