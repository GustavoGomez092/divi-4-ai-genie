import json
import subprocess
import unittest

from _paths import FIXTURES, TOOLS, WP_LOCAL
from divi_shortcode import parse


def divi_parse(path):
    out = subprocess.run([str(WP_LOCAL), f"--require={TOOLS / 'force-all-modules.php'}", "eval-file",
                          str(TOOLS / "divi_parse.php"), str(path)], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise unittest.SkipTest(f"local Divi site unavailable: {out.stderr[-300:]}")
    return json.loads(out.stdout[out.stdout.index("["):])


def flatten_divi(items):
    for item in items:
        yield item
        yield from flatten_divi(item["children"])


class DiviJudgeTest(unittest.TestCase):
    FILES = ["handwritten-landing.txt", "unicode.txt", "divi-ai-section.txt", "divi-ai-layout.txt"]

    def test_parse_agrees_with_divi(self):
        mismatches = []
        for name in self.FILES:
            path = FIXTURES / "valid" / name
            ours = [n for n, _, _ in parse(path.read_text()).walk()]
            theirs = list(flatten_divi(divi_parse(path)))
            self.assertEqual([n.tag for n in ours], [t["type"] for t in theirs], f"{name}: tree shape differs")
            for n, t in zip(ours, theirs):
                for attr in n.attrs:
                    if attr in t["attrs"] and t["attrs"][attr] != n.value(attr):
                        mismatches.append((name, n.tag, attr, n.value(attr), t["attrs"][attr]))
        self.assertEqual(mismatches, [], json.dumps(mismatches[:10], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    unittest.main()
