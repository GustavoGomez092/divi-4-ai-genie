<?php
// Undo r6_setup.php: restore every option it touched from BACKUP.json and delete the R6 pages.
//   LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH=... research/tools/wp-local.sh eval-file research/tools/divi5/r6_restore.php BACKUP.json
$backup = json_decode( file_get_contents( $args[0] ?? '' ), true );
if ( ! is_array( $backup ) ) { WP_CLI::error( 'usage: r6_restore.php BACKUP.json' ); }

$et_divi = get_option( 'et_divi' );
foreach ( [ 'et_global_data', 'header_color', 'accent_color', 'font_color', 'heading_font' ] as $key ) { // font_color, heading_font: set by hand for §3.4; absent before
	$value = $backup[ "et_divi.$key" ] ?? null;
	if ( null === $value ) { unset( $et_divi[ $key ] ); } else { $et_divi[ $key ] = $value; }
}
update_option( 'et_divi', $et_divi );
foreach ( [ 'et_divi_global_variables', 'et_divi_builder_global_presets_d5' ] as $opt ) {
	if ( null === $backup[ $opt ] ) { delete_option( $opt ); } else { update_option( $opt, $backup[ $opt ] ); }
}
foreach ( get_posts( [ 'post_type' => 'page', 'post_status' => 'any', 'numberposts' => -1 ] ) as $p ) {
	if ( 0 === strpos( $p->post_title, 'R6 ' ) ) { wp_delete_post( $p->ID, true ); WP_CLI::log( "deleted page {$p->ID} {$p->post_title}" ); }
}
if ( class_exists( 'ET_Core_PageResource' ) ) { ET_Core_PageResource::remove_static_resources( 'all', 'all', true ); }
WP_CLI::success( 'restored' );
