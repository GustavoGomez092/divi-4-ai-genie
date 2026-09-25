import json
import subprocess
import unittest

from _paths import FIXTURES, TOOLS, WP_LOCAL
from divi_shortcode import parse

# The five escape sequences unescape_attr_value() decodes (class-et-builder-element.php:2294).
ESCAPE_TOKENS = ("%22", "%91", "%93", "%92", "%5c")


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
    FILES = ["handwritten-landing.txt", "unicode.txt", "divi-ai-section.txt", "divi-ai-layout.txt", "faq-jsonld.txt"]

    def test_parse_agrees_with_divi(self):
        mismatches = []
        content_mismatches = []
        compared_per_file = {}
        escape_present = set()
        escape_compared = set()

        for name in self.FILES:
            path = FIXTURES / "valid" / name
            ours = [n for n, _, _ in parse(path.read_text()).walk()]
            theirs = list(flatten_divi(divi_parse(path)))
            self.assertEqual([n.tag for n in ours], [t["type"] for t in theirs], f"{name}: tree shape differs")

            file_compared = 0
            for n, t in zip(ours, theirs):
                # Attributes equal to their schema default are stripped from Divi's
                # builder-data output ($is_include_attr gate,
                # class-et-builder-element.php:3944-3993), so an attr missing from
                # t["attrs"] tells us nothing about our unescaping -- it's simply not
                # judgeable this way. Only compare (and count as compared) attrs Divi
                # actually returned.
                for attr, raw in n.attrs.items():
                    for tok in ESCAPE_TOKENS:
                        if tok in raw:
                            escape_present.add(tok)
                    if attr in t["attrs"]:
                        file_compared += 1
                        for tok in ESCAPE_TOKENS:
                            if tok in raw:
                                escape_compared.add(tok)
                        if t["attrs"][attr] != n.value(attr):
                            mismatches.append((name, n.tag, attr, n.value(attr), t["attrs"][attr]))

                # Leaf modules (no child modules on either side): compare text content too.
                if not n.modules and not t["children"]:
                    theirs_content = t["content"]
                    if theirs_content != n.content:
                        content_mismatches.append((name, n.tag, n.content, theirs_content))

            compared_per_file[name] = file_compared

        total_compared = sum(compared_per_file.values())
        print(f"divi judge: compared {total_compared} attribute values "
              f"across {len(self.FILES)} fixtures: {compared_per_file}")

        uncovered = escape_present - escape_compared
        self.assertEqual(uncovered, set(),
                          "escape classes present in fixture attribute values but never actually "
                          "compared (only seen in attrs Divi stripped as defaults): "
                          f"{sorted(uncovered)}")
        self.assertGreater(total_compared, 0, "no attributes were compared at all")

        self.assertEqual(mismatches, [], json.dumps(mismatches[:10], ensure_ascii=False, indent=1))
        self.assertEqual(content_mismatches, [], json.dumps(content_mismatches[:10], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    unittest.main()
