<?php
/**
 * Export the site-level inputs a Divi 4 render depends on, as a JSON "settings bundle"
 * for render.php --settings=... . READ-ONLY: only get_option() / wp_get_custom_css().
 *
 * Run on the CLIENT site (or reimplement the same reads over whatever API the pusher uses):
 *   wp eval-file export-settings.php client-settings.json
 *
 * Secrets are stripped (API keys, license/credentials, SEO/integration code). Integration
 * code (divi_integration_head/body) is excluded by default because it is usually tracking
 * scripts; pass --with-integration to keep it.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit( 1 );
}

$out_file         = isset( $args[0] ) ? $args[0] : 'client-settings.json';
$with_integration = in_array( '--with-integration', (array) $args, true );

global $shortname;
$theme_opt_name = 'et_' . ( $shortname ? $shortname : 'divi' ); // et_divi (Divi) / et_extra (Extra).

$et_opts = get_option( $theme_opt_name, array() );
$dropped = array();
foreach ( (array) $et_opts as $k => $v ) {
	$secret      = preg_match( '/api|key|secret|token|pass|license|credential|username|email_provider|_seo_/i', $k );
	$integration = ! $with_integration && preg_match( '/^divi_integration_|^divi_468_/', $k );
	if ( $secret || $integration ) {
		unset( $et_opts[ $k ] );
		$dropped[] = $k;
	}
}

$stylesheet = get_stylesheet();
$bundle     = array(
	'generated'  => gmdate( 'c' ),
	'source'     => home_url(),
	'meta'       => array(
		'divi_version'    => defined( 'ET_CORE_VERSION' ) ? ET_CORE_VERSION : null,
		'wp_version'      => get_bloginfo( 'version' ),
		'template'        => get_template(),
		'stylesheet'      => $stylesheet, // != template means a child theme: its files must exist on the mirror too.
		'active_plugins'  => get_option( 'active_plugins', array() ),
		'dropped_keys'    => $dropped,
		// Theme Builder templates are posts (et_template / et_header_layout / et_body_layout /
		// et_footer_layout); they are NOT covered by this bundle. Export them with Divi's
		// Theme Builder portability if the client uses a global header/footer.
		'theme_builder_templates' => (int) wp_count_posts( 'et_template' )->publish,
	),
	'options'    => array(
		// ePanel theme options + Theme Customizer settings + global colors (key et_global_colors)
		// all live in this one array (epanel/custom_functions.php et_get_option()).
		$theme_opt_name                          => $et_opts,
		// Global presets (includes/builder/feature/global-presets/Settings.php GLOBAL_PRESETS_OPTION).
		'et_divi_builder_global_presets_ng'      => get_option( 'et_divi_builder_global_presets_ng', new stdClass() ),
		// Customizer theme mods (logo, menus, header image...).
		"theme_mods_{$stylesheet}"               => get_option( "theme_mods_{$stylesheet}", array() ),
		// Builder settings (e.g. Divi Builder plugin performance options).
		'et_pb_builder_options'                  => get_option( 'et_pb_builder_options', array() ),
		'blogname'                               => get_option( 'blogname' ),
	),
	// Appearance > Customize > Additional CSS (a custom_css post, not an option).
	'custom_css' => wp_get_custom_css( $stylesheet ),
);

file_put_contents( $out_file, wp_json_encode( $bundle, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES ) );
WP_CLI::success( "Wrote $out_file (" . count( $et_opts ) . " {$theme_opt_name} keys kept, " . count( $dropped ) . ' dropped)' );
