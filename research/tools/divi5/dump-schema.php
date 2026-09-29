<?php
/**
 * Dump the Divi 5 module schema (every module's attribute metadata) as deterministic JSON.
 *
 * Run from the repo root with WP-CLI against a site that has Divi 5 active. The --exec makes
 * Divi treat the request as a REST call, so ConditionsUtility::should_register_all_d5_modules()
 * registers every module (instead of lazy-registering them per parsed block):
 *
 *   LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH="$HOME/Local Sites/divi-5-test/app/public" \
 *     research/tools/wp-local.sh --exec='$_SERVER["REQUEST_URI"]="/wp-json/";' \
 *     eval-file research/tools/divi5/dump-schema.php "$PWD/research/divi5-schema"
 *
 * Output (all keys sorted, no timestamps, so regeneration gives an empty diff):
 *   index.json           version, breakpoints, states, module list
 *   groups.json          every option group (divi/font, divi/spacing, ...) -> its leaf subNames
 *   modules/<slug>.json  one per module (slug = block name without "divi/"):
 *     module       module.json metadata (name, d4Shortcode, category, childrenName, ...)
 *     attributes   module.json `attributes` (settings items: component name + props, features, styleProps selectors)
 *     settings     module.json `settings` (panel groups; some carry inline field definitions)
 *     leaves       Conversion::get_preset_attrs_mapping(): every attribute path with option groups expanded
 *                  ("<attrName>__<subName>" => {attrName, subName, preset})
 *     defaults     ModuleRegistration::get_default_attrs(): render defaults and default printed style attrs
 *     conversion   the runtime D4 -> D5 conversion map (attributeMap, optionEnableMap, ...), when the module has one
 *     conversionOutline  the static conversion-outline.json
 *
 * Only field metadata is written: no JS/CSS source, no callbacks (callables are reduced to their names).
 */

use ET\Builder\Framework\Breakpoint\Breakpoint;
use ET\Builder\Packages\Conversion\Conversion;
use ET\Builder\Packages\Module\Options\ModuleOptionsPresetAttrs;
use ET\Builder\Packages\ModuleLibrary\ModuleRegistration;
use ET\Builder\Packages\ModuleUtils\ModuleUtils;

$out_dir = isset( $args[0] ) ? rtrim( $args[0], '/' ) : getcwd() . '/divi5-schema';
// Without the REST-context --exec, Divi registers modules lazily and the dump would silently mark every core
// module registered:false. Refuse before touching the previous dump.
if ( ! WP_Block_Type_Registry::get_instance()->is_registered( 'divi/section' ) ) {
	WP_CLI::error( 'divi/section is not registered: run with --exec=\'$_SERVER["REQUEST_URI"]="/wp-json/";\' (see the header of this file).' );
}
if ( ! is_dir( "$out_dir/modules" ) ) {
	mkdir( "$out_dir/modules", 0755, true );
}
foreach ( glob( "$out_dir/modules/*.json" ) as $stale ) {
	unlink( $stale );
}

// Registers the conversion outlines (the `divi.conversion.moduleLibrary.conversionMap` filter).
Conversion::initialize_shortcode_framework();
do_action( 'divi_visual_builder_before_d4_conversion' );

/** Recursively sort associative arrays by key; reduce callables/objects to JSON-safe names. */
function d5_clean( $value ) {
	if ( $value instanceof Closure ) {
		return '<closure>';
	}
	if ( is_object( $value ) ) {
		return '<' . get_class( $value ) . '>';
	}
	if ( ! is_array( $value ) ) {
		return $value;
	}
	$is_list = array_keys( $value ) === range( 0, count( $value ) - 1 );
	$clean   = array();
	foreach ( $value as $k => $v ) {
		if ( is_array( $v ) && 2 === count( $v ) && isset( $v[0], $v[1] ) && is_string( $v[0] ) && is_string( $v[1] ) && is_callable( $v ) ) {
			$v = $v[0] . '::' . $v[1];
		}
		$clean[ $k ] = d5_clean( $v );
	}
	if ( ! $is_list ) {
		ksort( $clean, SORT_STRING );
	}
	return $clean;
}

function d5_write( $file, $data ) {
	$json = wp_json_encode( d5_clean( $data ), JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
	// Empty PHP arrays encode as []; keep that (it is how module.json spells "use the default group").
	file_put_contents( $file, $json . "\n" );
}

/**
 * Every attribute path of a module with its option groups expanded, via Divi's own expander
 * (Conversion::get_preset_attrs_mapping). That function is built for presets, and some modules
 * filter it (`divi_conversion_presets_attrs_map`) to add extra leaves or to drop all of them
 * (e.g. divi/social-media-follow-network returns []). So it runs twice, with and without the
 * filter, and the union is kept; `preset: false`-style information is recorded as `inPresetMap`.
 */
function d5_leaves( string $name ): array {
	global $wp_filter;
	$cache = new ReflectionProperty( Conversion::class, 'preset_attrs_maps' );
	$cache->setAccessible( true );

	$cache->setValue( null, array() );
	$filtered = Conversion::get_preset_attrs_mapping( $name );

	$saved = $wp_filter['divi_conversion_presets_attrs_map'] ?? null;
	unset( $wp_filter['divi_conversion_presets_attrs_map'] );
	$cache->setValue( null, array() );
	$unfiltered = Conversion::get_preset_attrs_mapping( $name );
	if ( null !== $saved ) {
		$wp_filter['divi_conversion_presets_attrs_map'] = $saved;
	}
	$cache->setValue( null, array() );

	$leaves = array();
	foreach ( $unfiltered + $filtered as $key => $item ) {
		$item['inPresetMap'] = isset( $filtered[ $key ] );
		$leaves[ $key ]      = $item;
	}
	return $leaves;
}

$ui_noise = array( '_comment', 'videos', 'moduleIcon', 'keywords', 'mousetrap', 'file' );

// All core modules from the generated metadata, plus any registered divi/* block not in it.
$metadata_by_name = array();
foreach ( ModuleRegistration::get_all_core_modules_metadata() as $folder => $meta ) {
	$meta['__folder']                   = $folder;
	$metadata_by_name[ $meta['name'] ] = $meta;
}
$registered = array();
foreach ( WP_Block_Type_Registry::get_instance()->get_all_registered() as $name => $block ) {
	if ( 0 !== strpos( $name, 'divi/' ) ) {
		continue;
	}
	$registered[ $name ] = true;
	if ( ! isset( $metadata_by_name[ $name ] ) ) {
		$meta = array();
		foreach ( array( 'name', 'title', 'category', 'attributes', 'd4Shortcode', 'customCssFields', 'childrenName', 'settings' ) as $prop ) {
			if ( isset( $block->$prop ) ) {
				$meta[ $prop ] = $block->$prop;
			}
		}
		$meta['name']              = $name;
		$meta['__folder']          = null;
		$metadata_by_name[ $name ] = $meta;
	}
}
ksort( $metadata_by_name );

$conversion_maps = apply_filters( 'divi.conversion.moduleLibrary.conversionMap', array() );

$index = array();
foreach ( $metadata_by_name as $name => $meta ) {
	$slug   = preg_replace( '#^divi/#', '', $name );
	$module = array_diff_key( $meta, array_flip( array_merge( $ui_noise, array( 'attributes', 'settings', '__folder' ) ) ) );
	$module['folder']     = $meta['__folder'];
	$module['registered'] = isset( $registered[ $name ] );

	$leaves = d5_leaves( $name );

	$outline = ModuleRegistration::get_module_conversion_outline( $name );
	if ( is_array( $outline ) ) {
		unset( $outline['_comment'] );
	}

	$data = array(
		'module'            => $module,
		'attributes'        => $meta['attributes'] ?? array(),
		'settings'          => $meta['settings'] ?? array(),
		'leaves'            => $leaves,
		'defaults'          => array(
			'render'       => ModuleRegistration::get_default_attrs( $name, 'default' ),
			'printedStyle' => ModuleRegistration::get_default_attrs( $name, 'defaultPrintedStyle' ),
		),
		'conversion'        => $conversion_maps[ $name ] ?? null,
		'conversionOutline' => $outline,
	);
	d5_write( "$out_dir/modules/$slug.json", $data );

	$index[ $slug ] = array(
		'name'         => $name,
		'title'        => $meta['title'] ?? null,
		'category'     => $meta['category'] ?? null,
		'd4Shortcode'  => ( isset( $meta['d4Shortcode'] ) && '' !== $meta['d4Shortcode'] ) ? $meta['d4Shortcode'] : null,
		'childrenName' => $meta['childrenName'] ?? null,
		'folder'       => $meta['__folder'],
		'registered'   => isset( $registered[ $name ] ),
		'attr_count'   => count( $meta['attributes'] ?? array() ),
		'leaf_count'   => count( $leaves ),
		'has_conversion_map' => isset( $conversion_maps[ $name ] ),
	);
	WP_CLI::log( sprintf( '%-45s %4d leaves%s', $name, count( $leaves ), isset( $registered[ $name ] ) ? '' : '  (not registered)' ) );
}

// Option groups -> leaf subNames. Group names are read from the dispatcher's `case` labels.
$src = file_get_contents( ( new ReflectionClass( ModuleOptionsPresetAttrs::class ) )->getFileName() );
preg_match_all( "/case\\s+'([^']+)':/", $src, $m );
$group_names = array_values( array_unique( array_filter( $m[1], function ( $g ) {
	return 0 === strpos( $g, 'divi/' ) || 'image' === $g;
} ) ) );
sort( $group_names );
$groups = array();
foreach ( $group_names as $group ) {
	$variants = array( 'default' => array() );
	if ( 0 === strpos( $group, 'divi/font' ) ) {
		$variants = array(
			'default'           => array(),
			'has_heading_level' => array( 'has_heading_level' => true ),
			'has_list'          => array( 'has_list' => true ),
			'has_border'        => array( 'has_border' => true ),
			'has_paragraph'     => array( 'has_paragraph' => true ),
		);
	}
	foreach ( $variants as $variant => $vargs ) {
		$map  = ModuleOptionsPresetAttrs::get_preset_attrs_from_group( $group, '@', $vargs );
		$rows = array();
		foreach ( $map as $key => $item ) {
			$rows[ substr( $key, 1 ) ] = array(
				'attrName' => substr( $item['attrName'] ?? '@', 1 ),
				'subName'  => $item['subName'] ?? null,
				'preset'   => $item['preset'] ?? null,
			);
		}
		$groups[ $group ][ $variant ] = $rows;
	}
}
$group_keys = array();
foreach ( array( 'decoration', 'advanced', 'meta' ) as $type ) {
	foreach ( array( 'animation', 'attributes', 'background', 'bodyFont', 'border', 'boxShadow', 'button', 'conditions', 'disabledOn', 'filters', 'fit', 'image', 'interactions', 'layout', 'font', 'headingFont', 'icon', 'inlineFont', 'overflow', 'position', 'scroll', 'sizing', 'spacing', 'sticky', 'transform', 'transition', 'zIndex', 'elements', 'htmlAttributes', 'gutter', 'link', 'text', 'loop', 'html', 'adminLabel', 'meta', 'textShadow', 'order', 'dividers', 'innerShadow', 'spamProtection', 'emailService' ) as $key ) {
		$g = ModuleOptionsPresetAttrs::get_the_group_name_by_key( $type, $key );
		if ( $g ) {
			$group_keys[ "$type.$key" ] = $g;
		}
	}
}
d5_write( "$out_dir/groups.json", array( 'groups' => $groups, 'settingKeyToGroup' => $group_keys ) );

d5_write(
	"$out_dir/index.json",
	array(
		'divi_version' => defined( 'ET_BUILDER_PRODUCT_VERSION' ) ? ET_BUILDER_PRODUCT_VERSION : null,
		'breakpoints'  => Breakpoint::get_default_settings_values(),
		'states'       => ModuleUtils::states(),
		'modules'      => $index,
	)
);
WP_CLI::success( count( $index ) . " modules written to $out_dir" );
