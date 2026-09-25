#!/bin/bash
# Run WP-CLI against a LocalWP site without Local's site shell.
#   research/tools/wp-local.sh option get siteurl
# Override LOCAL_SITE_ID / LOCAL_SITE_PATH / LOCAL_PHP for other LocalWP sites.
set -euo pipefail
SITE_ID="${LOCAL_SITE_ID:-VHfw9zcDi}"
SITE_PATH="${LOCAL_SITE_PATH:-$HOME/Local Sites/divi-test/app/public}"
LS="$HOME/Library/Application Support/Local"
PHP_BIN="${LOCAL_PHP:-$(ls -d "$LS"/lightning-services/php-8.2.29*/bin/darwin-arm64/bin/php | head -1)}"
SOCK="$LS/run/$SITE_ID/mysql/mysqld.sock"
WPCLI="/Applications/Local.app/Contents/Resources/extraResources/bin/wp-cli/wp-cli.phar"
exec "$PHP_BIN" -d mysqli.default_socket="$SOCK" -d pdo_mysql.default_socket="$SOCK" \
  -d memory_limit=512M "$WPCLI" --path="$SITE_PATH" "$@"
