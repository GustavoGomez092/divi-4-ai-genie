<?php
/**
 * Dump the complete Divi 4 module schema (every module, every field) as JSON.
 *
 * Run with WP-CLI against a site that has Divi active:
 *   wp --require=force-all-modules.php eval-file dump-divi-schema.php <out_dir>
 *
 * force-all-modules.php must pre-register the `et_builder_should_load_all_module_data`
 * filter so Divi registers every module instead of lazy-loading them.
 */

if ( ! did_action( 'et_builder_ready' ) ) {
	do_action( 'wp' );
}

$out_dir = isset( $args[0] ) ? rtrim( $args[0], '/' ) : getcwd() . '/divi-schema';
if ( ! is_dir( "$out_dir/modules" ) ) {
	mkdir( "$out_dir/modules", 0755, true );
}

/**
 * Keep only JSON-safe values (drops closures and objects used for VB callbacks).
 */
function pp_clean( $value ) {
	if ( is_array( $value ) ) {
		$clean = array();
		foreach ( $value as $k => $v ) {
			$v = pp_clean( $v );
			if ( null !== $v ) {
				$clean[ $k ] = $v;
			}
		}
		return $clean;
	}
	if ( is_scalar( $value ) ) {
		return $value;
	}
	return null;
}

// Field keys worth keeping; everything else is VB-internal noise.
$keep_keys = array(
	'label', 'type', 'option_category', 'description', 'options', 'default', 'default_on_front',
	'default_on_child', 'tab_slug', 'toggle_slug', 'sub_toggle', 'mobile_options', 'responsive',
	'hover', 'sticky', 'show_if', 'show_if_not', 'depends_show_if', 'depends_show_if_not', 'depends_on',
	'affects', 'allowed_units', 'default_unit', 'range_settings', 'validate_unit', 'fixed_unit',
	'allow_empty', 'dynamic_content', 'composite_type', 'composite_structure', 'additional_att',
	'context', 'field_template', 'upload_button_text', 'choose_text', 'update_text', 'data_type',
	'renderer_options', 'font_weight', 'mobile_global', 'is_global_default', 'computed_affects',
	'shortcode_default', 'unitless', 'option_template', 'group_label', 'attr_suffix',
);

$modules = ET_Builder_Element::get_modules_array( 'page', true );
$index   = array();
$seen    = array();

foreach ( $modules as $m ) {
	$slug = $m['label'];
	if ( isset( $seen[ $slug ] ) ) {
		continue;
	}
	$seen[ $slug ] = true;

	$module = ET_Builder_Element::get_module( $slug, 'page' );
	$fields = ET_Builder_Element::get_module_fields( 'page', $slug );
	if ( ! is_array( $fields ) ) {
		$fields = array();
	}

	$clean_fields = array();
	foreach ( $fields as $name => $def ) {
		if ( ! is_array( $def ) ) {
			continue;
		}
		$clean_fields[ $name ] = pp_clean( array_intersect_key( $def, array_flip( $keep_keys ) ) );
	}

	$meta = array(
		'slug'                   => $slug,
		'name'                   => $module ? $module->name : $m['title'],
		'plural'                 => $module && isset( $module->plural ) ? $module->plural : null,
		'type'                   => $module && $module->type ? $module->type : 'module',
		'child_slug'             => $module && $module->child_slug ? $module->child_slug : null,
		'child_item_text'        => $module && $module->child_item_text ? $module->child_item_text : null,
		'fullwidth'              => $module ? (bool) $module->fullwidth : false,
		'is_structure'           => in_array( $slug, array( 'et_pb_section', 'et_pb_row', 'et_pb_row_inner', 'et_pb_column', 'et_pb_column_inner' ), true ),
		'main_css_element'       => $module ? $module->main_css_element : null,
		'vb_support'             => isset( $m['vb_support'] ) ? $m['vb_support'] : null,
		'advanced_fields'        => $module && is_array( $module->advanced_fields ) ? pp_clean( $module->advanced_fields ) : null,
		'custom_css_fields'      => $module && is_array( $module->custom_css_fields ) ? pp_clean( $module->custom_css_fields ) : null,
		'settings_modal_toggles' => $module && is_array( $module->settings_modal_toggles ) ? pp_clean( $module->settings_modal_toggles ) : null,
		'field_count'            => count( $clean_fields ),
	);

	file_put_contents(
		"$out_dir/modules/$slug.json",
		wp_json_encode( array( 'module' => $meta, 'fields' => $clean_fields ), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE )
	);

	$index[ $slug ] = array(
		'name'        => $meta['name'],
		'type'        => $meta['type'],
		'child_slug'  => $meta['child_slug'],
		'fullwidth'   => $meta['fullwidth'],
		'structure'   => $meta['is_structure'],
		'field_count' => $meta['field_count'],
	);
	WP_CLI::log( sprintf( '%-40s %4d fields', $slug, $meta['field_count'] ) );
}

ksort( $index );
file_put_contents(
	"$out_dir/index.json",
	wp_json_encode(
		array(
			'divi_version' => ET_BUILDER_PRODUCT_VERSION,
			'generated'    => gmdate( 'c' ),
			'modules'      => $index,
		),
		JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE
	)
);
WP_CLI::success( count( $index ) . " modules written to $out_dir" );
