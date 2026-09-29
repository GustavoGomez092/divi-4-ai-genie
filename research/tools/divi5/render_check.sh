#!/bin/bash
# Render-check Divi 5 block files on the local D5 site (divi-5-test.local).
# For each file: create a published "D5 Test:" page (+ _et_pb_use_builder=on), curl the
# front end, report HTTP status, Divi module count, et-cache files, new debug.log lines,
# then delete the page (unless KEEP=1).
#   research/tools/divi5/render_check.sh tests/fixtures/divi5/converted/*.html
# Needs WP_DEBUG_LOG enabled on the site to catch PHP notices/warnings.
set -uo pipefail
export LOCAL_SITE_ID="${LOCAL_SITE_ID:-fTZ3hcgdI}"
export LOCAL_SITE_PATH="${LOCAL_SITE_PATH:-$HOME/Local Sites/divi-5-test/app/public}"
HERE="$(cd "$(dirname "$0")" && pwd)"
W() { "$HERE/../wp-local.sh" "$@" 2>/dev/null; }
LOG="$LOCAL_SITE_PATH/wp-content/debug.log"
OUT="${OUT:-$(mktemp -d)}"
printf '%-42s %4s %6s %6s %6s %5s %s\n' file http blocks mods d4elem cache log_lines
for f in "$@"; do
  n=$(basename "$f"); n="${n%.*}"
  before=$( [ -f "$LOG" ] && wc -l < "$LOG" || echo 0 )
  id=$(W post create "$f" --post_type=page --post_status=publish --post_title="D5 Test: $n" --porcelain --user=1)
  W post meta update "$id" _et_pb_use_builder on >/dev/null
  url=$(W post get "$id" --field=url)
  code=$(curl -s -o "$OUT/$n.html" -w '%{http_code}' "$url")
  blocks=$(grep -o '<!-- wp:divi/[a-z0-9-]*' "$f" | grep -vc 'divi/placeholder')
  mods=$(grep -o 'class="et_pb_[a-z_]*_[0-9]\+ ' "$OUT/$n.html" | wc -l | tr -d ' ')
  d4=$(grep -o 'class="[^"]*et_d4_element' "$OUT/$n.html" | wc -l | tr -d ' ')
  cache=$(ls "$LOCAL_SITE_PATH/wp-content/et-cache/$id/" 2>/dev/null | wc -l | tr -d ' ')
  after=$( [ -f "$LOG" ] && wc -l < "$LOG" || echo 0 )
  printf '%-42s %4s %6s %6s %6s %5s %s\n' "$n" "$code" "$blocks" "$mods" "$d4" "$cache" "$((after-before))"
  if [ "$((after-before))" -gt 0 ]; then tail -n "$((after-before))" "$LOG" | cut -c1-300 | sed 's/^/    /' | sort | uniq -c | head -5; fi
  grep -o 'Fatal error\|Warning</b>\|Notice</b>\|Parse error' "$OUT/$n.html" | sort | uniq -c | sed 's/^/    html: /'
  if [ "${KEEP:-0}" != 1 ]; then W post delete "$id" --force >/dev/null; else echo "    kept page $id $url"; fi
done
echo "rendered HTML in $OUT"
