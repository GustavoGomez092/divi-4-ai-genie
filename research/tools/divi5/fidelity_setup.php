<?php
// Task 13 token fidelity: seed known Divi 5 design data + one source page, and undo it byte-for-byte.
// Based on r6_setup.php / r6_restore.php (research/divi5/tokens-and-detection.md §3).
//   wp-local.sh eval-file research/tools/divi5/fidelity_setup.php snapshot            -> {"touched": {option: md5|null}, "all": {option: md5}}
//   wp-local.sh eval-file research/tools/divi5/fidelity_setup.php setup BACKUP.json   -> JSON {page_id, url, ids}
//   wp-local.sh eval-file research/tools/divi5/fidelity_setup.php restore BACKUP.json -> JSON {deleted, touched}
// setup writes BACKUP.json (the raw wp_options rows of every option it touches: value bytes + autoload, or absent)
// before changing anything, and refuses to run when BACKUP.json already exists (an unrestored earlier run).
// restore writes those rows back verbatim (deleting options that did not exist), deletes every "D5TEST fidelity"
// page (and its et-cache directory) and marks the rest of Divi's static CSS stale. Used by tests/test_divi5_tokens_fidelity.py. Throwaway test site only.
use ET\Builder\Packages\GlobalData\GlobalData;
use ET\Builder\Packages\GlobalData\GlobalPreset;

// The design-data options setup writes. Divi also deletes its _et_builder_{da,gf}_feature_cache options when these
// change; those are caches any request rebuilds (or drops), so they are not backed up.
const D5F_OPTIONS = [ 'et_divi', 'et_divi_global_variables', 'et_divi_builder_global_presets_d5' ];
const D5F_TITLE   = 'D5TEST fidelity';

$mode = $args[0] ?? '';
$file = $args[1] ?? '';

function d5f_rows( array $names ) {
	global $wpdb;
	$out = [];
	foreach ( $names as $name ) {
		$row          = $wpdb->get_row( $wpdb->prepare( "SELECT option_value, autoload FROM {$wpdb->options} WHERE option_name = %s", $name ), ARRAY_A );
		$out[ $name ] = $row ? [ 'value_b64' => base64_encode( $row['option_value'] ), 'autoload' => $row['autoload'] ] : null;
	}
	return $out;
}

function d5f_snapshot() {
	global $wpdb;
	$touched = [];
	foreach ( d5f_rows( D5F_OPTIONS ) as $name => $row ) {
		$touched[ $name ] = $row ? md5( $row['autoload'] . "\0" . base64_decode( $row['value_b64'] ) ) : null;
	}
	$all = [];
	foreach ( $wpdb->get_results( "SELECT option_name, option_value, autoload FROM {$wpdb->options} WHERE option_name NOT LIKE '\\_transient\\_%' AND option_name NOT LIKE '\\_site\\_transient\\_%'", ARRAY_A ) as $r ) {
		$all[ $r['option_name'] ] = md5( $r['autoload'] . "\0" . $r['option_value'] );
	}
	ksort( $all );
	return [ 'touched' => $touched, 'all' => $all ];
}

function d5f_pages() {
	return array_values( array_filter(
		get_posts( [ 'post_type' => 'page', 'post_status' => 'any', 'numberposts' => -1 ] ),
		function ( $p ) { return 0 === strpos( $p->post_title, D5F_TITLE ); }
	) );
}

if ( 'snapshot' === $mode ) {
	echo wp_json_encode( d5f_snapshot() );
	return;
}

if ( 'restore' === $mode ) {
	global $wpdb;
	$backup = json_decode( (string) @file_get_contents( $file ), true );
	if ( ! is_array( $backup ) || ! isset( $backup['rows'] ) ) { WP_CLI::error( 'usage: fidelity_setup.php restore BACKUP.json' ); }
	foreach ( $backup['rows'] as $name => $row ) {
		$exists = null !== $wpdb->get_var( $wpdb->prepare( "SELECT option_id FROM {$wpdb->options} WHERE option_name = %s", $name ) );
		if ( null === $row ) {
			if ( $exists ) { $wpdb->delete( $wpdb->options, [ 'option_name' => $name ] ); }
		} elseif ( $exists ) {
			$wpdb->update( $wpdb->options, [ 'option_value' => base64_decode( $row['value_b64'] ), 'autoload' => $row['autoload'] ], [ 'option_name' => $name ] );
		} else {
			$wpdb->insert( $wpdb->options, [ 'option_name' => $name, 'option_value' => base64_decode( $row['value_b64'] ), 'autoload' => $row['autoload'] ] );
		}
	}
	wp_cache_flush();
	wp_set_current_user( 1 ); // Divi's static-CSS removal is a no-op without edit_posts
	$deleted = [];
	foreach ( d5f_pages() as $p ) {
		wp_delete_post( $p->ID, true );
		$deleted[] = $p->ID;
		if ( class_exists( 'ET_Core_PageResource' ) ) {
			ET_Core_PageResource::remove_static_resources( $p->ID, 'all', true, 'all', false, true );
		}
		$dir = WP_CONTENT_DIR . '/et-cache/' . $p->ID;
		if ( is_dir( $dir ) && ! array_diff( scandir( $dir ), [ '.', '..' ] ) ) { rmdir( $dir ); }
	}
	if ( class_exists( 'ET_Core_PageResource' ) ) { // the home page's cached :root colors named the seeded ones
		ET_Core_PageResource::remove_static_resources( 'all', 'all', true );
	}
	echo wp_json_encode( [ 'deleted' => $deleted, 'touched' => d5f_snapshot()['touched'] ] );
	return;
}

if ( 'setup' !== $mode || ! $file ) { WP_CLI::error( 'usage: fidelity_setup.php snapshot | setup BACKUP.json | restore BACKUP.json' ); }
if ( file_exists( $file ) ) { WP_CLI::error( "$file exists: restore that earlier run first" ); }
if ( false === file_put_contents( $file, wp_json_encode( [ 'rows' => d5f_rows( D5F_OPTIONS ) ] ) ) ) { WP_CLI::error( "cannot write $file" ); }
wp_set_current_user( 1 );

$now = gmdate( 'Y-m-d\TH:i:s.000\Z' );
$v   = function ( $type, $name, $settings = [] ) {
	return '$variable(' . wp_json_encode( [ 'type' => $type, 'value' => [ 'name' => $name, 'settings' => (object) $settings ] ] ) . ')$';
};

// 1. Three global colors: two plain, one derived (coral + 25 lightness).
$colors = [
	'gcid-d5fnavy0001'  => [ 'color' => '#102A43', 'label' => 'D5F Navy', 'status' => 'active', 'lastUpdated' => $now, 'folder' => '', 'usedInPosts' => [] ],
	'gcid-d5fcoral001'  => [ 'color' => '#E4572E', 'label' => 'D5F Coral', 'status' => 'active', 'lastUpdated' => $now, 'folder' => '', 'usedInPosts' => [] ],
	'gcid-d5fcorallt1'  => [ 'color' => $v( 'color', 'gcid-d5fcoral001', [ 'lightness' => 25 ] ), 'label' => 'D5F Coral Light', 'status' => 'active', 'lastUpdated' => $now, 'folder' => '', 'usedInPosts' => [] ],
];
GlobalData::set_global_colors( $colors );

// 2. A number variable and a font variable.
GlobalData::set_global_variables( [
	'numbers' => [ 'gvid-d5fradius01' => [ 'id' => 'gvid-d5fradius01', 'label' => 'D5F Radius', 'value' => '10px', 'order' => 1, 'status' => 'active', 'type' => 'numbers' ] ],
	'fonts'   => [ 'gvid-d5ffont0001' => [ 'id' => 'gvid-d5ffont0001', 'label' => 'D5F Display', 'value' => 'Montserrat', 'order' => 1, 'status' => 'active', 'type' => 'fonts' ] ],
] );

// 3. A module preset on divi/button and an option-group preset on the heading title font.
$ts      = time() * 1000;
$radius  = $v( 'content', 'gvid-d5fradius01' );
$presets = GlobalPreset::get_data();
$presets['module']['divi/button'] = [
	'default' => $presets['module']['divi/button']['default'] ?? '',
	'items'   => ( $presets['module']['divi/button']['items'] ?? [] ) + [
		'd5fbtnpreset1' => [
			'type' => 'module', 'moduleName' => 'divi/button', 'id' => 'd5fbtnpreset1', 'name' => 'D5F Primary Button',
			'created' => $ts, 'updated' => $ts, 'version' => '5.13.1',
			'attrs' => [ 'button' => [ 'decoration' => [
				'button'     => [ 'desktop' => [ 'value' => [ 'enable' => 'on' ] ] ],
				'background' => [ 'desktop' => [ 'value' => [ 'color' => $v( 'color', 'gcid-d5fcoral001' ) ] ] ],
				'border'     => [ 'desktop' => [ 'value' => [ 'radius' => [ 'sync' => 'on', 'topLeft' => $radius, 'topRight' => $radius, 'bottomRight' => $radius, 'bottomLeft' => $radius ] ] ] ],
				'font'       => [ 'font' => [ 'desktop' => [ 'value' => [ 'color' => '#ffffff' ] ] ] ],
			] ] ],
		],
	],
];
$presets['group']['divi/font'] = [
	'default' => $presets['group']['divi/font']['default'] ?? '',
	'items'   => ( $presets['group']['divi/font']['items'] ?? [] ) + [
		'd5ffontpreset1' => [
			'type' => 'group', 'groupName' => 'divi/font', 'groupId' => 'designTitleText', 'moduleName' => 'divi/heading',
			'primaryAttrName' => 'title', 'id' => 'd5ffontpreset1', 'name' => 'D5F Display Heading',
			'created' => $ts, 'updated' => $ts, 'version' => '5.13.1',
			'attrs' => [ 'title' => [ 'decoration' => [ 'font' => [ 'font' => [ 'desktop' => [ 'value' => [
				'family' => $v( 'content', 'gvid-d5ffont0001' ), 'weight' => '700',
				'color'  => $v( 'color', 'gcid-d5fnavy0001' ), 'size' => '48px',
			] ] ] ] ] ] ],
		],
	],
];
GlobalPreset::save_data( $presets );

// 4. The source page: everything above, a literal responsive h2 and a custom class on the button.
$ver   = '5.13.1';
$outer = [
	[ 'divi/section', [ 'builderVersion' => $ver, 'module' => [ 'decoration' => [
		'background' => [ 'desktop' => [ 'value' => [ 'color' => $v( 'color', 'gcid-d5fcorallt1' ) ] ] ],
		'spacing'    => [ 'desktop' => [ 'value' => [ 'padding' => [ 'top' => '72px', 'right' => '', 'bottom' => '72px', 'left' => '', 'syncVertical' => 'on', 'syncHorizontal' => 'off' ] ] ] ],
	] ] ] ],
	[ 'divi/row', [ 'builderVersion' => $ver ] ],
	[ 'divi/column', [ 'builderVersion' => $ver, 'module' => [ 'advanced' => [ 'type' => [ 'desktop' => [ 'value' => '4_4' ] ] ] ] ] ],
];
$leaf = [
	[ 'divi/heading', [ 'builderVersion' => $ver, 'title' => [ 'innerContent' => [ 'desktop' => [ 'value' => 'D5 fidelity heading' ] ] ],
		'groupPreset' => [ 'designTitleText' => [ 'presetId' => [ 'd5ffontpreset1' ], 'groupName' => 'divi/font' ] ] ] ],
	[ 'divi/heading', [ 'builderVersion' => $ver, 'title' => [
		'innerContent' => [ 'desktop' => [ 'value' => 'D5 fidelity subheading' ] ],
		'decoration'   => [ 'font' => [ 'font' => [
			'desktop' => [ 'value' => [ 'headingLevel' => 'h2', 'size' => '40px', 'weight' => '600' ] ],
			'tablet'  => [ 'value' => [ 'size' => '32px' ] ],
			'phone'   => [ 'value' => [ 'size' => '26px' ] ],
		] ] ],
	] ] ],
	[ 'divi/text', [ 'builderVersion' => $ver, 'content' => [ 'innerContent' => [ 'desktop' => [ 'value' => '<p>Fidelity body copy.</p>' ] ],
		'decoration' => [ 'bodyFont' => [ 'body' => [ 'font' => [ 'desktop' => [ 'value' => [ 'color' => $v( 'color', 'gcid-d5fnavy0001' ) ] ] ] ] ] ] ] ] ],
	[ 'divi/button', [ 'builderVersion' => $ver, 'modulePreset' => [ 'd5fbtnpreset1' ],
		'module' => [ 'advanced' => [ 'htmlAttributes' => [ 'desktop' => [ 'value' => [ 'class' => 'd5f-cta', 'id' => '' ] ] ] ] ],
		'button' => [ 'innerContent' => [ 'desktop' => [ 'value' => [ 'linkUrl' => '#start', 'text' => 'Start' ] ] ] ] ] ],
];
$ser = function ( $name, $attrs ) {
	return '<!-- wp:' . $name . ' ' . serialize_block_attributes( $attrs ) . ' -->';
};
$content = '<!-- wp:divi/placeholder -->';
foreach ( $outer as $b ) { $content .= $ser( $b[0], $b[1] ); }
foreach ( $leaf as $b ) { $content .= $ser( $b[0], $b[1] ) . '<!-- /wp:' . $b[0] . ' -->'; }
$content .= '<!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section --><!-- /wp:divi/placeholder -->';

$id = wp_insert_post( [ 'post_type' => 'page', 'post_status' => 'publish', 'post_title' => D5F_TITLE . ' source', 'post_content' => wp_slash( $content ) ], true );
if ( is_wp_error( $id ) ) { WP_CLI::error( $id->get_error_message() ); }
update_post_meta( $id, '_et_pb_use_builder', 'on' );
update_post_meta( $id, '_et_pb_page_layout', 'et_no_sidebar' );
echo wp_json_encode( [ 'page_id' => $id, 'url' => get_permalink( $id ) ] );
