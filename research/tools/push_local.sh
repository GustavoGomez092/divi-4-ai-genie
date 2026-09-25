#!/bin/bash
# Publish a shortcode file as a "Plan Test:" page on divi-test.local for visual checks; prints "<id> <url>".
#   research/tools/push_local.sh recipe-example.txt "Hero split"
#
# Next step in the recipe verification loop — screenshot the result at desktop + mobile:
#   node research/python-renderer-spike/shoot.mjs <outdir> <name> <url> --width 1440,390
#
# Delete afterwards with: research/tools/wp-local.sh post delete <id> --force
#
# No _et_pb_page_layout meta update here (earlier drafts of this script set it to
# et_no_sidebar): it is not a registered REST meta field, and reference/publishing.md documents
# that setting it — even directly via WP-CLI, as this script would — makes no observable
# difference on a builder-active page. Divi's own et_divi_sidebar_class() already forces the
# et_no_sidebar body class for any page with _et_pb_use_builder=on (Task 10 finding), so the
# line was harmless but dead weight; dropped rather than kept for cargo-cult parity.
set -euo pipefail
W="$(cd "$(dirname "$0")" && pwd)/wp-local.sh"
ID=$("$W" post create "$1" --post_type=page --post_status=publish --post_title="Plan Test: $2" --porcelain)
"$W" post meta update "$ID" _et_pb_use_builder on >/dev/null
URL=$("$W" post get "$ID" --field=url)
curl -s "$URL" > /dev/null   # warm Divi's CSS cache
echo "$ID $URL"
