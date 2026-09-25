import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from _paths import FIXTURES, SCRIPTS, WP_LOCAL, live_only

PAGE = FIXTURES / "valid" / "brand-kit.txt"


def wp(*args):
    out = subprocess.run([str(WP_LOCAL), *args], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise unittest.SkipTest(f"local site unavailable: {out.stderr[-200:]}")
    return out.stdout.strip()


@live_only
class TokensFidelityTest(unittest.TestCase):
    def test_round_trip_through_wordpress(self):
        user = wp("user", "list", "--role=administrator", "--field=user_login").splitlines()[0]
        password = wp("user", "application-password", "create", user, "fidelity-test", "--porcelain")
        page_id = wp("post", "create", str(PAGE), "--post_type=page", "--post_status=publish",
                     "--post_title=Plan Test: fidelity", "--porcelain")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "fidelity-tokens.json"  # never write into the source tree
        try:
            wp("post", "meta", "update", page_id, "_et_pb_use_builder", "on")
            env = dict(os.environ, WP_APP_PASSWORD=password)
            run = subprocess.run([sys.executable, str(SCRIPTS / "extract_tokens.py"), "--site", "http://divi-test.local",
                                  "--user", user, "--page", page_id, "--out", str(out)], env=env, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            t = json.loads(out.read_text())
        finally:
            wp("post", "delete", page_id, "--force")
            uuid = wp("user", "application-password", "list", user, "--name=fidelity-test", "--field=uuid")
            wp("user", "application-password", "delete", user, uuid)
        self.assertEqual(t["presets"]["et_pb_button"][0]["uuid"], "11111111-2222-3333-4444-555555555555")
        self.assertTrue(any(e["module_class"] == "pp-lead" for e in t["module_styles"]["et_pb_text"]))
        self.assertEqual(t["typography"]["scale"]["h2"]["size_tablet"], "32px")
        self.assertTrue({"#0b2a3c", "#f97316", "#f1f5f9"} <= {p["hex"] for p in t["colors"]["palette"]})
        tones = {c["section_tone"] for e in t["module_styles"]["et_pb_button"] for c in e["contexts"]}
        self.assertIn("dark", tones)
        self.assertEqual(len(t["section_exemplars"]), 5)


if __name__ == "__main__":
    unittest.main()
