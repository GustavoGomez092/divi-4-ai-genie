#!/bin/bash
# Re-run the whole spike evaluation. Ground truth (real Divi) is produced with the render prototype:
#   WP=research/tools/wp-local.sh research/render-prototype/run.sh <page.txt> out/truth/<name>-real.html
# and live page 11 is fetched with curl into out/truth/page11-live.html.
set -u
cd "$(dirname "$0")"
D="$PWD/out"
declare -a PAGES=(
  "page11:../../tests/fixtures/valid/divi-ai-layout.txt"
  "landing:../../tests/fixtures/valid/handwritten-landing.txt"
  "heldout-inscope:pages/heldout-inscope.txt"
  "heldout2-inscope:pages/heldout2-inscope.txt"
  "heldout-outofscope:pages/heldout-outofscope.txt"
)
for spec in "${PAGES[@]}"; do
  k=${spec%%:*}; src=${spec#*:}
  python3 divi_render.py "$src" -o "out/$k-py.html" --coverage "out/$k-coverage.json" > "out/$k-render.json"
  python3 evaluate.py "out/truth/$k-real.html" "out/$k-py.html" --show 50 --json "out/$k-eval.json" > /dev/null
  for n in "$k-real:truth/$k-real" "$k-py:$k-py"; do
    perl -e 'alarm 150; exec @ARGV' node shoot.mjs out/shots "${n%%:*}" "file://$D/${n#*:}.html" --wait 4000 > /dev/null
  done
  python3 compare_visual.py out/shots "$k-real" "$k-py" --side-by-side "out/sbs-$k.png" > "out/$k-visual.json"
done
perl -e 'alarm 150; exec @ARGV' node shoot.mjs out/shots page11-live "http://divi-test.local/probe-divi-ai-emergency-plumber/" --wait 4000 > /dev/null
python3 compare_visual.py out/shots page11-live page11-py > out/page11-live-visual.json
python3 - <<'EOF'
import json
rows = []
for k in ["page11", "landing", "heldout-inscope", "heldout2-inscope", "heldout-outofscope"]:
    e = json.load(open(f"out/{k}-eval.json")); v = json.load(open(f"out/{k}-visual.json"))
    r = json.load(open(f"out/{k}-render.json"))
    rows.append({"page": k, "render_ms": round(r["render_s"] * 1000, 1), "attr_coverage_pct": r["attr_coverage_pct"],
                 "elements": f'{e["markup"]["elements_with_identical_class_list"]}/{e["markup"]["truth_elements"]}',
                 "byte_identical": e["markup"]["byte_identical"],
                 "css": f'{e["css"]["common"]}/{e["css"]["truth_decls"]} (+{e["css"]["extra_or_wrong"]} extra)',
                 "px_1440": v["1440"]["diff_pct"], "px_390": v["390"]["diff_pct"],
                 "geo_1440": f'{v["1440"]["geometry_identical_elements"]}/{v["1440"]["elements"][0]}'})
lv = json.load(open("out/page11-live-visual.json"))
rows.append({"page": "page11 vs LIVE", "px_1440": lv["1440"]["diff_pct"], "px_390": lv["390"]["diff_pct"],
             "geo_1440": f'{lv["1440"]["geometry_identical_elements"]}/{lv["1440"]["elements"][0]}'})
json.dump(rows, open("out/summary.json", "w"), indent=1)
for r in rows: print(r)
EOF
