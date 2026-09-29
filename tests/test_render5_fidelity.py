"""Fidelity of the Divi 5 Python renderer (research/divi5/python-renderer/divi5_render) against real Divi 5 (Task 21-R5a).

Iterates tests/fixtures/render5/manifest.json. Ground truth is real Divi 5 rendered through Playground
(research/tools/ground_truth.py with the manifest's Divi 5 version, and `--tokens` for recipe pages; cached
outside the repo because it holds Divi's licensed CSS). The whole class is skipped when that Divi 5 isn't cached
or the truth can't be produced (no Node/Playground and no cached truth).

- tuned fixtures: the .et-l tag/class sequence and the builder CSS declaration sets must be equal, and the
  coverage report must list nothing (every attribute value on a tuned page is honoured).
- held-out fixtures (tuned: false): the numbers are recorded, opt-in, in research/divi5/render-fidelity.md with
  RENDER5_FIDELITY_RECORD=1 and a stage label in RENDER5_FIDELITY_STAGE (rows keyed by fixture and stage, like
  the Divi 4 table). Every module the page uses must be supported or listed by the coverage report. The Addendum A
  bar for the batch-1 held-out page (95 % or more of the builder CSS declarations, nothing wrong) is its own test,
  an expected failure since the gate missed (see research/divi5/render-fidelity.md).
"""
import datetime
import json
import os
import re
import unittest
from pathlib import Path

from _paths import RENDERER5, FIXTURES, ROOT  # noqa: F401  (puts scripts + research/tools on sys.path)
import sys as _sys
_sys.path.insert(0, str(RENDERER5))  # the parked renderer, only for these tests

import fetch_divi
import fidelity
import ground_truth

RENDER5 = FIXTURES / "render5"
MANIFEST = RENDER5 / "manifest.json"
METRICS = ROOT / "research" / "divi5" / "render-fidelity.md"
MIN_HELDOUT_DECLS = 0.95
RECORD = os.environ.get("RENDER5_FIDELITY_RECORD") == "1"
STAGE = os.environ.get("RENDER5_FIDELITY_STAGE", "").strip()
TABLE_HEADER = ("| Fixture | Stage | Modules | Tuned | Markup ratio | Identical class lists | Builder CSS (common/truth) "
                "| Declarations | Extra | Coverage-ignored | Date |")
TABLE_RULE = "|---|---|---|---|---|---|---|---|---|---|---|"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text())


def identical_class_lists(truth_html: str, html: str):
    a, b = fidelity._seq(fidelity._et_l(truth_html)), fidelity._seq(fidelity._et_l(html))
    return sum(1 for x, y in zip(a, b) if x == y), len(a)


def metrics(truth_html: str, html: str, cov: dict) -> dict:
    r = fidelity.compare(truth_html, html)
    same, total = identical_class_lists(truth_html, html)
    css = r["css"]
    return {"markup_ratio": r["markup"]["tag_class_seq_ratio"], "same_classes": same, "elements": total,
            "common": css["common"], "truth": css["truth_decls"], "extra": css["extra"],
            "decl_pct": css["common"] / css["truth_decls"] if css["truth_decls"] else 1.0,
            "ignored": len(cov.get("ignored", [])), "unsupported": dict(cov.get("unsupported_modules", {})),
            "compare": r}


def record_metrics(fixture: str, modules, tuned: bool, m: dict, stage, path=METRICS):
    """Upserts one row per (fixture, stage); a new stage always adds a row (tests/test_render_fidelity.py)."""
    if not stage or not str(stage).strip():
        raise ValueError("a stage label is required to record metrics (set RENDER5_FIDELITY_STAGE)")
    stage = " ".join(str(stage).replace("|", "/").split())
    row = (f"| {fixture} | {stage} | {', '.join(modules)} | {'yes' if tuned else 'no'} | {m['markup_ratio']:.4f} "
           f"| {m['same_classes']}/{m['elements']} | {m['common']}/{m['truth']} | {100 * m['decl_pct']:.1f} % "
           f"| {m['extra']} | {m['ignored']} | {datetime.date.today().isoformat()} |")
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


class RecordMetrics5Test(unittest.TestCase):
    M = {"markup_ratio": 1.0, "same_classes": 3, "elements": 4, "common": 95, "truth": 100, "extra": 0,
         "decl_pct": 0.95, "ignored": 2}

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "m.md"
        self.path.write_text("# Render fidelity\n\nIntro.\n")

    def tearDown(self):
        self._tmp.cleanup()

    def test_rows_are_keyed_by_fixture_and_stage(self):
        record_metrics("a.html", ["text"], False, self.M, "R5b held-out pre-fix", path=self.path)
        record_metrics("a.html", ["text"], True, {**self.M, "common": 100, "decl_pct": 1.0}, "R5b post-fix",
                       path=self.path)
        record_metrics("a.html", ["text"], False, {**self.M, "common": 96, "decl_pct": 0.96}, "R5b held-out pre-fix",
                       path=self.path)
        text = self.path.read_text()
        self.assertEqual(text.count(TABLE_HEADER), 1)
        self.assertIn("| a.html | R5b held-out pre-fix | text | no | 1.0000 | 3/4 | 96/100 | 96.0 % | 0 | 2 |", text)
        self.assertIn("| a.html | R5b post-fix | text | yes | 1.0000 | 3/4 | 100/100 | 100.0 % | 0 | 2 |", text)
        self.assertLess(text.index("pre-fix"), text.index("post-fix"))

    def test_a_stage_is_required(self):
        for stage in ("", "  ", None):
            with self.assertRaises(ValueError):
                record_metrics("a.html", ["text"], False, self.M, stage, path=self.path)


class RenderFidelity5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        man = load_manifest()
        cls.version = man["divi"]
        if fetch_divi.theme_dir(cls.version) is None:
            raise unittest.SkipTest(f"Divi {cls.version} is not cached (python3 scripts/preview.py fetch-divi "
                                    f"{cls.version})")
        try:
            import divi5_render
        except ImportError as e:  # pragma: no cover
            raise unittest.SkipTest(f"divi5_render unavailable: {e}")
        cls.r = divi5_render
        cls.fixtures = man["fixtures"]
        cls.truth, cls.tokens = {}, {}
        for fx in cls.fixtures:
            tok = ROOT / fx["tokens"] if fx.get("tokens") else None
            path = ground_truth.ensure_truth(RENDER5 / fx["file"], cls.version, tokens=tok)
            if path is None:
                raise unittest.SkipTest(f"real-Divi 5 ground truth unavailable for {fx['file']} (Node/Playground)")
            cls.truth[fx["file"]] = path.read_text(encoding="utf-8", errors="replace")
            cls.tokens[fx["file"]] = json.loads(tok.read_text()) if tok else None

    def render(self, fx):
        return self.r.render_page((RENDER5 / fx["file"]).read_text(encoding="utf-8"), divi_version=self.version,
                                  tokens=self.tokens[fx["file"]])

    def test_manifest_has_a_tuned_and_a_heldout_page_per_batch(self):
        batches = {}
        for fx in self.fixtures:
            batches.setdefault(fx["batch"], set()).add(fx["tuned"])
        self.assertIn(1, batches)
        for batch, kinds in batches.items():
            self.assertIn(True, kinds, f"batch {batch} has no tuned fixture")

    def test_tuned_fixtures_match_real_divi(self):
        for fx in (f for f in self.fixtures if f["tuned"]):
            with self.subTest(fixture=fx["file"]):
                res = self.render(fx)
                m = metrics(self.truth[fx["file"]], res.html, res.coverage)
                r = m["compare"]
                detail = json.dumps({"markup": r["markup"], "css": r["css"], "missing": r["missing_examples"],
                                     "extra": r["extra_examples"], "ignored": res.coverage["ignored"]}, indent=1)
                self.assertGreater(r["css"]["truth_decls"], 0, detail)  # guards against a vacuous pass
                self.assertGreater(r["markup"]["truth_elements"], 0, detail)
                self.assertTrue(r["markup"]["tag_class_sequence_equal"], detail)
                self.assertEqual(r["css"]["missing"], 0, detail)
                self.assertEqual(r["css"]["extra"], 0, detail)
                self.assertEqual(res.coverage["ignored"], [], detail)
                self.assertEqual(res.coverage["unsupported_modules"], {}, detail)

    def test_heldout_fixtures_render_and_record_metrics(self):
        if RECORD and not STAGE:
            self.fail("RENDER5_FIDELITY_RECORD=1 needs RENDER5_FIDELITY_STAGE, a label for the rows it records "
                      "(e.g. RENDER5_FIDELITY_STAGE='R5c held-out pre-fix')")
        for fx in (f for f in self.fixtures if not f["tuned"]):
            with self.subTest(fixture=fx["file"]):
                res = self.render(fx)
                m = metrics(self.truth[fx["file"]], res.html, res.coverage)
                if RECORD:
                    record_metrics(Path(fx["file"]).name, fx["modules"], False, m, stage=STAGE)
                missing = [x for x in fx["modules"] if x not in self.r.SUPPORTED_MODULES
                           and x not in res.coverage["unsupported_modules"] and x not in res.coverage["needs_site_data"]]
                self.assertEqual(missing, [])

    @unittest.expectedFailure
    def test_batch1_heldout_meets_the_addendum_a_bar(self):
        """The binding gate of Task 21-R5b, on the pre-fix engine. It missed (research/divi5/render-fidelity.md:
        94.3 % of the declarations, a layout shift from the unported disabledOn, 2 extra declarations the coverage
        report does not name), so this is an expected failure (NO-GO, engine parked: see research/divi5/render-fidelity.md and
        research/divi5/python-renderer/README.md); Playground stays the only Divi 5 preview. An unexpected success means the engine changed; re-measure and update the record."""
        for fx in (f for f in self.fixtures if not f["tuned"] and f["batch"] == 1):
            res = self.render(fx)
            m = metrics(self.truth[fx["file"]], res.html, res.coverage)
            self.assertGreaterEqual(m["decl_pct"], MIN_HELDOUT_DECLS, json.dumps(m["compare"], indent=1))
            self.assertEqual(m["extra"], 0)


if __name__ == "__main__":
    unittest.main()
