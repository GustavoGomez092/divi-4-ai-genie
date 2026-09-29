<?php
// Convert a Divi 4 shortcode file to Divi 5 block content with Divi's own server-side converter.
//   wp eval-file convert.php IN.txt OUT.html [raw]
//
// Mirrors the Visual Builder's conversion route, POST /divi/v1/content-conversion
// (VisualBuilder/REST/ContentConversion/ContentConversionController.php::convert_content, 5.13.1):
//   1. Conversion::initialize_shortcode_framework();
//   2. do_action( 'divi_visual_builder_before_d4_conversion' );
//   3. Conversion::maybeConvertContent( $content, true, $post_id );
//   4. apply_filters( 'divi_framework_portability_import_migrated_post_content', ... )
//      = the D5->D5 migrations (AttributeMigration, FlexboxMigration, NestedModuleMigration, ...),
//      which also wrap the result in <!-- wp:divi/placeholder --> via
//      MigrationUtils::ensure_placeholder_wrapper().
// Deliberately NOT mirrored: the route's `content` sanitize_callback, wp_kses_post(), which runs on
// the D4 shortcode *before* conversion and double-encodes entities (&amp; -> &amp;amp;).
// Pass a third arg `raw` to stop after step 3 (bare converter output, no migrations/wrapper).
use ET\Builder\Packages\Conversion\Conversion;

$in       = $args[0];
$out      = $args[1];
$raw_only = isset( $args[2] ) && 'raw' === $args[2];
$content  = file_get_contents( $in );

Conversion::initialize_shortcode_framework();
do_action( 'divi_visual_builder_before_d4_conversion' );
$converted = Conversion::maybeConvertContent( $content, true, null );

if ( ! $raw_only ) {
	$converted = apply_filters( 'divi_framework_portability_import_migrated_post_content', $converted );
}

file_put_contents( $out, $converted );
WP_CLI::log( sprintf( 'in=%d bytes out=%d bytes%s', strlen( $content ), strlen( $converted ), $raw_only ? ' (raw converter output)' : '' ) );
