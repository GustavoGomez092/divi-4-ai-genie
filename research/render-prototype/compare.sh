#!/bin/bash
# Screenshot a live URL and a rendered preview file with headless Chrome at desktop and
# phone widths, then pixel-diff them (Python + Pillow).
# Usage: compare.sh <live-url> <preview.html> <outdir> [page-height]
set -u
LIVE="$1"; PREVIEW="$2"; OUT="$3"; H="${4:-8000}"
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE="$(mktemp -d)"
mkdir -p "$OUT"
shot() { # name width height url
  perl -e 'alarm 30; exec @ARGV' "$CH" --headless=new --disable-gpu --hide-scrollbars \
    --user-data-dir="$PROFILE" --timeout=20000 --window-size="$2,$3" \
    --screenshot="$OUT/$1.png" "$4" >/dev/null 2>&1
}
for spec in "desk 1440 $H" "phone 390 $((H * 2))"; do
  read -r name w h <<<"$spec"
  shot "live-$name" "$w" "$h" "$LIVE"
  shot "preview-$name" "$w" "$h" "file://$PREVIEW"
done
rm -rf "$PROFILE"
python3 - "$OUT" <<'EOF'
import sys
from PIL import Image, ImageChops
out = sys.argv[1]
for v in ['desk', 'phone']:
    a = Image.open(f'{out}/live-{v}.png').convert('RGB')
    b = Image.open(f'{out}/preview-{v}.png').convert('RGB')
    if a.size != b.size:
        print(v, 'SIZE MISMATCH', a.size, b.size); continue
    d = ImageChops.difference(a, b)
    mask = d.convert('L').point(lambda x: 255 if x > 16 else 0)
    px = mask.histogram()[255]
    total = a.size[0] * a.size[1]
    print(f'{v}: {a.size} differing pixels {px} ({100 * px / total:.4f}%) bbox={mask.getbbox()}')
    if px:
        mask.save(f'{out}/diff-{v}.png')
EOF
