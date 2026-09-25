"""Fidelity of the pure-Python renderer (scripts/divi_render) against real Divi (Task 24).

Iterates tests/fixtures/render/manifest.json. Ground truth is real Divi rendered through
Playground (research/tools/ground_truth.py, cached outside the repo); the whole class is skipped
when no Divi build is cached or Node/Playground can't produce the truth.

- tuned fixtures: the .et-l tag/class sequence and the builder CSS declaration sets must be equal.
- held-out fixtures (tuned: false): must render without crashing. With RENDER_FIDELITY_RECORD=1
  their metrics are recorded in research/render-fidelity.md (opt-in, so ordinary test runs never
  touch the working tree) under the stage label in RENDER_FIDELITY_STAGE (required; rows are keyed
  by fixture and stage). When every listed module is supported they must also reach a
  tag/class sequence ratio >= 0.9; while some aren't, each unsupported module must instead be
  listed in the coverage report (the fallback contract: `unsupported_modules`, or
  `needs_site_data` for modules that show the site's posts, menus, comments or widgets), because
  a placeholder can't match.
"""
import datetime
import json
import os
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
RECORD = os.environ.get("RENDER_FIDELITY_RECORD") == "1"
STAGE = os.environ.get("RENDER_FIDELITY_STAGE", "").strip()
TABLE_HEADER = "| Fixture | Stage | Modules | Tuned | Markup ratio | CSS ratio | Date |"
TABLE_RULE = "|---|---|---|---|---|---|---|"


def load_manifest():
    return json.loads(MANIFEST.read_text())["fixtures"]


def record_metrics(fixture: str, modules, tuned: bool, markup_ratio: float, css_ratio: float, stage,
                   path=METRICS):
    """Upserts one row per (fixture, stage) into the metrics table. The stage is a free-text label
    naming when the row was measured ("T25 held-out pre-fix", "T25 re-measure"...): a new stage
    always adds a row, so later tasks never overwrite earlier history; recording the same stage
    again updates its row."""
    if not stage or not str(stage).strip():
        raise ValueError("a stage label is required to record metrics (set RENDER_FIDELITY_STAGE)")
    stage = " ".join(str(stage).replace("|", "/").split())
    today = datetime.date.today().isoformat()
    short = ", ".join(m.replace("et_pb_", "") for m in modules)
    row = (f"| {fixture} | {stage} | {short} | {'yes' if tuned else 'no'} | {markup_ratio:.4f} | {css_ratio:.4f} "
           f"| {today} |")
    text = path.read_text() if path.exists() else ""
    if TABLE_HEADER not in text:
        text = text.rstrip("\n") + ("\n\n" if text else "") + TABLE_HEADER + "\n" + TABLE_RULE + "\n"
    key = re.compile(r"^\| %s \| %s \| .*$" % (re.escape(fixture), re.escape(stage)), re.M)
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
    def record(self, p, fixture, stage, markup, css=1.0, tuned=False):
        record_metrics(fixture, ["et_pb_text"], tuned, markup, css, stage=stage, path=p)

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "m.md"
        self.path.write_text("# Render fidelity\n\nIntro.\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_different_stages_for_one_fixture_keep_separate_rows(self):
        self.record(self.path, "a.txt", "T24 held-out pre-fix", 0.5)
        self.record(self.path, "a.txt", "T25 re-measure", 0.75)
        text = self.path.read_text()
        self.assertEqual(text.count(TABLE_HEADER), 1)
        self.assertEqual(text.count("| a.txt |"), 2)
        self.assertIn("| a.txt | T24 held-out pre-fix | text | no | 0.5000 |", text)
        self.assertIn("| a.txt | T25 re-measure | text | no | 0.7500 |", text)
        self.assertLess(text.index("T24 held-out pre-fix"), text.index("T25 re-measure"))
        self.assertTrue(text.startswith("# Render fidelity\n\nIntro.\n"))

    def test_same_stage_twice_updates_its_row(self):
        self.record(self.path, "a.txt", "T25 held-out post-fix", 0.5)
        self.record(self.path, "b.txt", "T25 held-out post-fix", 0.9)
        self.record(self.path, "a.txt", "T25 held-out post-fix", 1.0, tuned=True)
        text = self.path.read_text()
        self.assertEqual(text.count("| a.txt |"), 1)
        self.assertIn("| a.txt | T25 held-out post-fix | text | yes | 1.0000 |", text)
        self.assertLess(text.index("| a.txt |"), text.index("| b.txt |"))

    def test_a_stage_is_required(self):
        for stage in ("", "  ", None):
            with self.assertRaises(ValueError):
                self.record(self.path, "a.txt", stage, 0.5)


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
                # guard against vacuous passes (e.g. the builder CSS not being found at all)
                self.assertGreater(r["css"]["truth_decls"], 0, detail)
                self.assertGreater(r["css"]["common"] + r["css"]["extra"], 0, detail)
                self.assertGreater(r["markup"]["truth_elements"], 0, detail)
                self.assertTrue(r["markup"]["tag_class_sequence_equal"], detail)
                self.assertEqual(r["css"]["missing"], 0, detail)
                self.assertEqual(r["css"]["extra"], 0, detail)

    def test_heldout_fixtures_render_and_record_metrics(self):
        if RECORD and not STAGE:
            self.fail("RENDER_FIDELITY_RECORD=1 needs RENDER_FIDELITY_STAGE, a label for the rows it "
                      "records (e.g. RENDER_FIDELITY_STAGE='T26 held-out pre-fix'); rows are keyed by "
                      "(fixture, stage), so a new stage never overwrites an earlier one")
        for fx in (f for f in self.fixtures if not f["tuned"]):
            with self.subTest(fixture=fx["file"]):
                result = self.render(fx)
                r = fidelity.compare(self.truth[fx["file"]], result.html)
                if RECORD:
                    record_metrics(Path(fx["file"]).name, fx["modules"], False,
                                   r["markup"]["tag_class_seq_ratio"], r["css"]["ratio"], stage=STAGE)
                unsupported = [m for m in fx["modules"] if m not in divi_render.SUPPORTED_MODULES]
                if unsupported:
                    listed = {**result.coverage["unsupported_modules"], **result.coverage["needs_site_data"]}
                    self.assertEqual([m for m in unsupported if m not in listed], [])
                else:
                    self.assertGreaterEqual(r["markup"]["tag_class_seq_ratio"], MIN_HELDOUT_RATIO, json.dumps(r, indent=1))


if __name__ == "__main__":
    unittest.main()
