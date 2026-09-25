#!/bin/bash
# Render a Divi shortcode file to a self-contained HTML preview using a local mirror WP+Divi site.
#   WP="wp --path=/path/to/mirror" ./run.sh page.shortcode out/page.html [settings=client.json] [meta=meta.json] [embed-images] [no-js]
# WP defaults to plain `wp` (must resolve to the mirror site; for LocalWP use its site shell or a wrapper).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WP_CMD=${WP:-wp}
[ $# -ge 2 ] || { sed -n 2,4p "$0"; exit 1; }
SC="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT_DIR="$(mkdir -p "$(dirname "$2")" && cd "$(dirname "$2")" && pwd)"
OUT="$OUT_DIR/$(basename "$2")"
shift 2
$WP_CMD eval-file "$HERE/render.php" "$SC" "$OUT" "$@"
