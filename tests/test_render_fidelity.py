"""Fidelity of the pure-Python renderer (scripts/divi_render) against real Divi (Task 24).

Iterates tests/fixtures/render/manifest.json. Ground truth is real Divi rendered through
Playground (research/tools/ground_truth.py, cached outside the repo); the whole class is skipped
when no Divi build is cached or Node/Playground can't produce the truth.

- tuned fixtures: the .et-l tag/class sequence and the builder CSS declaration sets must be equal.
- held-out fixtures (tuned: false): must render without crashing; their metrics are recorded in
  research/render-fidelity.md. When every listed module is supported they must also reach a
  tag/class sequence ratio >= 0.9; while some aren't, each unsupported module must instead be
  listed in the coverage report (the fallback contract), because a placeholder can't match.
"""
import datetime
import json
import re
import unittest
from pathlib import Path

from _paths import FIXTURES, ROOT  # noqa: F401  (puts scripts + research/tools on sys.path)

import divi_render
import fetch_divi
import fidelity
import ground_truth

RENDER_FIXTURES = FIXTURES / "render"
MANIFEST = RENDER_FIXTURES / "manifest.json"
METRICS = ROOT / "research" / "render-fidelity.md"
MIN_HELDOUT_RATIO = 0.9
TABLE_HEADER = "| Fixture | Modules | Tuned | Markup ratio | CSS ratio | Date |"


def load_manifest():
    return json.loads(MANIFEST.read_text())["fixtures"]


def record_metrics(fixture: str, modules, tuned: bool, markup_ratio: float, css_ratio: float, path=METRICS):
    """Upserts one row per (fixture, tuned, date) into the metrics table so progress stays visible."""
    today = datetime.date.today().isoformat()
    short = ", ".join(m.replace("et_pb_", "") for m in modules)
    row = f"| {fixture} | {short} | {'yes' if tuned else 'no'} | {markup_ratio:.4f} | {css_ratio:.4f} | {today} |"
    text = path.read_text() if path.exists() else ""
    if TABLE_HEADER not in text:
        text = text.rstrip("\n") + ("\n\n" if text else "") + TABLE_HEADER + "\n|---|---|---|---|---|---|\n"
    key = re.compile(r"^\| %s \| [^|]* \| %s \| [^|]* \| [^|]* \| %s \|$"
                     % (re.escape(fixture), "yes" if tuned else "no", today), re.M)
    if key.search(text):
        text = key.sub(row.replace("\\", "\\\\"), text)
    else:
        lines = text.split("\n")
        start = lines.index(TABLE_HEADER)
        end = start + 2
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        lines.insert(end, row)
        text = "\n".join(lines)
    path.write_text(text if text.endswith("\n") else text + "\n")


class RecordMetricsTest(unittest.TestCase):
    def test_rows_are_upserted_per_fixture_and_day(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "m.md"
            p.write_text("# Render fidelity\n\nIntro.\n")
            record_metrics("a.txt", ["et_pb_text"], False, 0.5, 0.25, p)
            record_metrics("a.txt", ["et_pb_text"], False, 0.75, 0.5, p)
            record_metrics("b.txt", ["et_pb_blurb"], False, 1.0, 1.0, p)
            text = p.read_text()
        self.assertEqual(text.count(TABLE_HEADER), 1)
        self.assertEqual(text.count("| a.txt |"), 1)
        self.assertIn("| a.txt | text | no | 0.7500 | 0.5000 |", text)
        self.assertLess(text.index("| a.txt |"), text.index("| b.txt |"))
        self.assertTrue(text.startswith("# Render fidelity\n\nIntro.\n"))


class RenderFidelityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.version = fetch_divi.newest_cached()
        if cls.version is None:
            raise unittest.SkipTest("no Divi build cached (python3 scripts/preview.py fetch-divi VER)")
        cls.fixtures = load_manifest()
        cls.truth = {}
        for fx in cls.fixtures:
            path = ground_truth.ensure_truth(RENDER_FIXTURES / fx["file"], cls.version)
            if path is None:
                raise unittest.SkipTest(f"real-Divi ground truth unavailable for {fx['file']} (Node/Playground)")
            cls.truth[fx["file"]] = path.read_text(encoding="utf-8", errors="replace")

    def render(self, fx):
        source = (RENDER_FIXTURES / fx["file"]).read_text(encoding="utf-8")
        return divi_render.render_page(source, divi_version=self.version, with_js=False)

    def test_manifest_lists_the_task_fixtures(self):
        names = {Path(fx["file"]).name: fx["tuned"] for fx in self.fixtures}
        self.assertEqual(names.get("divi-ai-layout.txt"), True)
        self.assertEqual(names.get("handwritten-landing.txt"), True)
        self.assertEqual(names.get("heldout-outofscope.txt"), False)

    def test_tuned_fixtures_match_real_divi(self):
        for fx in (f for f in self.fixtures if f["tuned"]):
            with self.subTest(fixture=fx["file"]):
                r = fidelity.compare(self.truth[fx["file"]], self.render(fx).html)
                detail = json.dumps({"markup": r["markup"], "css": r["css"], "missing": r["missing_examples"],
                                     "extra": r["extra_examples"]}, indent=1)
                self.assertTrue(r["markup"]["tag_class_sequence_equal"], detail)
                self.assertEqual(r["css"]["missing"], 0, detail)
                self.assertEqual(r["css"]["extra"], 0, detail)

    def test_heldout_fixtures_render_and_record_metrics(self):
        for fx in (f for f in self.fixtures if not f["tuned"]):
            with self.subTest(fixture=fx["file"]):
                result = self.render(fx)
                r = fidelity.compare(self.truth[fx["file"]], result.html)
                record_metrics(Path(fx["file"]).name, fx["modules"], False,
                               r["markup"]["tag_class_seq_ratio"], r["css"]["ratio"])
                unsupported = [m for m in fx["modules"] if m not in divi_render.SUPPORTED_MODULES]
                if unsupported:
                    listed = result.coverage["unsupported_modules"]
                    self.assertEqual([m for m in unsupported if m not in listed], [])
                else:
                    self.assertGreaterEqual(r["markup"]["tag_class_seq_ratio"], MIN_HELDOUT_RATIO, json.dumps(r, indent=1))


if __name__ == "__main__":
    unittest.main()
