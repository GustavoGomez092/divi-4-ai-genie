#!/usr/bin/env python3
"""Score d5render.py output against real Divi 5 (Playground truth) with research/tools/fidelity.py.
  evaluate.py NAME [--tokens FILE] [--show N]   (pages/NAME.html vs out/truth/NAME-d5.html)"""
import argparse, json, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/tools")); sys.path.insert(0, str(HERE))
import fidelity, d5render
ap = argparse.ArgumentParser(); ap.add_argument("name"); ap.add_argument("--page"); ap.add_argument("--tokens"); ap.add_argument("--show", type=int, default=15)
a = ap.parse_args()
page = Path(a.page) if a.page else HERE / "pages" / f"{a.name}.html"
tokens = json.loads(Path(a.tokens).read_text()) if a.tokens else {}
src = page.read_text()
html, cov = d5render.render_page(src, tokens)
times = []
for _ in range(20):
    t0 = time.perf_counter(); d5render.render_page(src, tokens, static_css=""); times.append((time.perf_counter() - t0) * 1000)
(HERE / "out" / f"{a.name}-py.html").write_text(html)
truth = (HERE / "out/truth" / f"{a.name}-d5.html").read_text()
c = fidelity.compare(truth, html)
sa = fidelity._seq(fidelity._et_l(truth)); sb = fidelity._seq(fidelity._et_l(html))
same_cls = sum(1 for x, y in zip(sa, sb) if x == y) if len(sa) == len(sb) else None
c["markup"]["identical_class_lists"] = same_cls
c["coverage"] = cov
c["render_ms_median_warm"] = round(sorted(times)[len(times) // 2], 2)
(HERE / "out" / f"{a.name}-eval.json").write_text(json.dumps(c, indent=1))
m, s = c["markup"], c["css"]
print(f"{a.name}: elements {m['truth_elements']}/{m['candidate_elements']} identical_class_lists={same_cls} seq_equal={m['tag_class_sequence_equal']} "
      f"ratio={m['tag_class_seq_ratio']} et_l_identical={m['et_l_identical']} bytes={m['et_l_bytes']}")
print(f"  css: truth={s['truth_decls']} cand={s['candidate_decls']} common={s['common']} ({100*s['common']/max(1,s['truth_decls']):.1f}%) missing={s['missing']} extra={s['extra']}")
print(f"  coverage: {cov['attr_leaves']} leaves, {cov['ignored_leaves']} ignored; unsupported={cov['unsupported']}; render {c['render_ms_median_warm']} ms (median of 20, builder only)")
da = fidelity._decls(fidelity._builder_css(truth)); db = fidelity._decls(fidelity._builder_css(html))
for d in sorted(da - db)[:a.show]: print("  -", d[:200])
for d in sorted(db - da)[:a.show]: print("  +", d[:200])
if not m["tag_class_sequence_equal"]:
    for i, (x, y) in enumerate(zip(sa, sb)):
        if x != y: print("  markup@", i, x, "|", y)
