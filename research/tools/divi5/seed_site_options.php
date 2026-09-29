<?php
// Task 14b live check: put a preview.py seed_options() JSON into a THROWAWAY Divi 5 site's options, merged the way
// the Playground mu-plugin (scripts/preview/mu-plugin/pp-preview.php, pp_preview_merge) merges it for one request,
// and put the rows back byte-for-byte afterwards. Throwaway test site only (divi-5-test.local).
//   LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH=... research/tools/wp-local.sh eval-file research/tools/divi5/seed_site_options.php MODE FILE
//   backup BACKUP.json  records each touched row's raw option_value (base64) + autoload, or null when the row is
//                       absent; refuses to overwrite an existing BACKUP.json (a failed run can't lose the original).
//   apply SEED.json     merges the seed over the stored options (update_option) and drops Divi's static CSS.
//   restore BACKUP.json writes the raw rows back with $wpdb (no re-serialization), deletes rows that were absent,
//                       drops Divi's static CSS.
//   sha                 prints {"option": sha1 of the raw row, or null} (compare before/after).
global $wpdb;
$mode  = $args[0] ?? '';
$file  = $args[1] ?? '';
$names = [ 'et_divi', 'et_divi_global_variables' ];

$raw = function ( $name ) use ( $wpdb ) {
	return $wpdb->get_row( $wpdb->prepare( "SELECT option_value, autoload FROM {$wpdb->options} WHERE option_name = %s", $name ), ARRAY_A );
};
$flush = function () use ( $names ) {
	wp_cache_delete( 'alloptions', 'options' );
	wp_cache_delete( 'notoptions', 'options' );
	foreach ( $names as $n ) {
		wp_cache_delete( $n, 'options' );
	}
	if ( class_exists( 'ET_Core_PageResource' ) ) {
		ET_Core_PageResource::remove_static_resources( 'all', 'all', true );
	}
};
$merge = function ( $stored, $values ) use ( &$merge ) {
	$stored = maybe_unserialize( $stored );
	$stored = is_array( $stored ) ? $stored : [];
	foreach ( $values as $key => $value ) {
		$stored[ $key ] = ( is_array( $value ) && $value && array_key_exists( $key, $stored ) ) ? $merge( $stored[ $key ], $value ) : $value;
	}
	return $stored;
};

if ( 'sha' === $mode ) {
	$out = [];
	foreach ( $names as $n ) {
		$row       = $raw( $n );
		$out[ $n ] = $row ? sha1( $row['autoload'] . "\0" . $row['option_value'] ) : null;
	}
	echo wp_json_encode( $out ) . "\n";
} elseif ( 'backup' === $mode && $file ) {
	if ( file_exists( $file ) ) {
		WP_CLI::error( "$file exists: restore it first" );
	}
	$out = [];
	foreach ( $names as $n ) {
		$row       = $raw( $n );
		$out[ $n ] = $row ? [ 'value' => base64_encode( $row['option_value'] ), 'autoload' => $row['autoload'] ] : null;
	}
	file_put_contents( $file, wp_json_encode( $out ) );
	WP_CLI::success( 'backed up' );
} elseif ( 'apply' === $mode && $file ) {
	$seed = json_decode( (string) file_get_contents( $file ), true );
	foreach ( $names as $n ) {
		if ( ! empty( $seed[ $n ] ) && is_array( $seed[ $n ] ) ) {
			update_option( $n, $merge( get_option( $n, [] ), $seed[ $n ] ) );
		}
	}
	$flush();
	WP_CLI::success( 'seeded' );
} elseif ( 'restore' === $mode && $file ) {
	$backup = json_decode( (string) file_get_contents( $file ), true );
	if ( ! is_array( $backup ) ) {
		WP_CLI::error( "cannot read $file" );
	}
	foreach ( $names as $n ) {
		$b = $backup[ $n ] ?? null;
		if ( null === $b ) {
			$wpdb->delete( $wpdb->options, [ 'option_name' => $n ] );
		} elseif ( $raw( $n ) ) {
			$wpdb->update( $wpdb->options, [ 'option_value' => base64_decode( $b['value'] ), 'autoload' => $b['autoload'] ], [ 'option_name' => $n ] );
		} else {
			$wpdb->insert( $wpdb->options, [ 'option_name' => $n, 'option_value' => base64_decode( $b['value'] ), 'autoload' => $b['autoload'] ] );
		}
	}
	$flush();
	WP_CLI::success( 'restored' );
} else {
	WP_CLI::error( 'usage: seed_site_options.php backup|apply|restore FILE, or sha' );
}
