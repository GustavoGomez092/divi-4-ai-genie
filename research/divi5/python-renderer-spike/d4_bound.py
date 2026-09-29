#!/usr/bin/env python3
"""Upper bound for "convert D5 back to D4, reuse divi_render": render each page's ORIGINAL Divi 4 shortcode
(the exact source Divi's own converter turned into the D5 fixture, i.e. a perfect back-conversion) with
the shipped D4 renderer, and score it against real Divi 5's render of the converted blocks."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "Skill/divi-page-builder/scripts")); sys.path.insert(0, str(ROOT / "research/tools"))
import divi_render, fidelity
SRC = {"heldout-inscope": "tests/fixtures/render/heldout-inscope.txt", "handwritten-landing": "tests/fixtures/valid/handwritten-landing.txt",
       "unicode": "tests/fixtures/valid/unicode.txt", "brand-kit": "tests/fixtures/valid/brand-kit.txt",
       "divi-ai-section": "tests/fixtures/valid/divi-ai-section.txt"}
res = {}
for name, src in SRC.items():
    r = divi_render.render_page((ROOT / src).read_text(), divi_version="4.27.9")
    (HERE / f"out/{name}-d4render.html").write_text(r.html)
    c = fidelity.compare((HERE / f"out/truth/{name}-d5.html").read_text(), r.html)
    res[name] = c
    m, s = c["markup"], c["css"]
    print(f"{name:22s} elems {m['truth_elements']}/{m['candidate_elements']} seq_eq={m['tag_class_sequence_equal']} ratio={m['tag_class_seq_ratio']}"
          f" | css truth={s['truth_decls']} cand={s['candidate_decls']} common={s['common']} miss={s['missing']} extra={s['extra']} jacc={s['ratio']}")
(HERE / "out/d4_bound.json").write_text(json.dumps(res, indent=1))
