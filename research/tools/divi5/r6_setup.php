<?php
// R6 experiment: seed realistic Divi 5 global data (colors, variables, presets) + one page that uses them.
//   LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH=... research/tools/wp-local.sh eval-file research/tools/divi5/r6_setup.php BACKUP.json
// Writes a backup of every touched option to BACKUP.json first; undo with r6_restore.php BACKUP.json.
// Throwaway test site only. All IDs are prefixed "r6" so they are easy to spot.
use ET\Builder\Packages\GlobalData\GlobalData;
use ET\Builder\Packages\GlobalData\GlobalPreset;

$backup_file = $args[0] ?? '';
if ( ! $backup_file ) { WP_CLI::error( 'usage: r6_setup.php BACKUP.json' ); }
wp_set_current_user( 1 );

$et_divi = get_option( 'et_divi' );
$backup  = [
	'et_divi.et_global_data'      => $et_divi['et_global_data'] ?? null,
	'et_divi.header_color'        => $et_divi['header_color'] ?? null,
	'et_divi.accent_color'        => $et_divi['accent_color'] ?? null,
	'et_divi_global_variables'    => get_option( 'et_divi_global_variables', null ),
	'et_divi_builder_global_presets_d5' => get_option( 'et_divi_builder_global_presets_d5', null ),
];
if ( ! file_exists( $backup_file ) ) {
	file_put_contents( $backup_file, wp_json_encode( $backup, JSON_PRETTY_PRINT ) );
}

$now = gmdate( 'Y-m-d\TH:i:s.000\Z' );

// 1. Global colors (et_divi[et_global_data][global_colors]) + one Customizer color (et_divi[accent_color]).
GlobalData::set_global_colors( [
	'gcid-r6navy0001'   => [ 'color' => '#0B2A3C', 'label' => 'R6 Navy', 'status' => 'active', 'lastUpdated' => $now, 'folder' => '', 'usedInPosts' => [] ],
	'gcid-r6orange001'  => [ 'color' => '#F97316', 'label' => 'R6 Orange', 'status' => 'active', 'lastUpdated' => $now, 'folder' => '', 'usedInPosts' => [] ],
	// Nested global color: a tint of R6 Orange via $variable() with HSL settings.
	'gcid-r6orangelt1'  => [ 'color' => '$variable({"type":"color","value":{"name":"gcid-r6orange001","settings":{"lightness":30}}})$', 'label' => 'R6 Orange Light', 'status' => 'active', 'lastUpdated' => $now, 'folder' => '', 'usedInPosts' => [] ],
	'gcid-r6unused001'  => [ 'color' => '#22AA55', 'label' => 'R6 Unused Green', 'status' => 'active', 'lastUpdated' => $now, 'folder' => '', 'usedInPosts' => [] ],
	'gcid-primary-color' => [ 'color' => '#7C3AED' ], // Customizer "accent_color", stored in et_divi.
] );

// 2. Design variables (option et_divi_global_variables).
$vars = [
	'numbers' => [
		'gvid-r6radius01' => [ 'id' => 'gvid-r6radius01', 'label' => 'R6 Radius', 'value' => '12px', 'order' => 1, 'status' => 'active', 'type' => 'numbers' ],
		'gvid-r6secpad01' => [ 'id' => 'gvid-r6secpad01', 'label' => 'R6 Section Pad', 'value' => 'clamp(48px, 8vw, 96px)', 'order' => 2, 'status' => 'active', 'type' => 'numbers' ],
		'gvid-r6unusedn1' => [ 'id' => 'gvid-r6unusedn1', 'label' => 'R6 Unused Number', 'value' => '7px', 'order' => 3, 'status' => 'active', 'type' => 'numbers' ],
	],
	'fonts'   => [
		'gvid-r6font0001' => [ 'id' => 'gvid-r6font0001', 'label' => 'R6 Display', 'value' => 'Poppins', 'order' => 3, 'status' => 'active', 'type' => 'fonts' ],
	],
	'strings' => [
		'gvid-r6tagline1' => [ 'id' => 'gvid-r6tagline1', 'label' => 'R6 Tagline', 'value' => 'Build faster with R6', 'order' => 1, 'status' => 'active', 'type' => 'strings' ],
	],
	'links'   => [
		'gvid-r6ctalink1' => [ 'id' => 'gvid-r6ctalink1', 'label' => 'R6 CTA URL', 'value' => 'https://example.com/r6-start', 'order' => 1, 'status' => 'active', 'type' => 'links' ],
	],
	'images'  => [
		'gvid-r6image001' => [ 'id' => 'gvid-r6image001', 'label' => 'R6 Hero BG', 'value' => 'https://example.com/r6-hero.jpg', 'order' => 1, 'status' => 'active', 'type' => 'images' ],
	],
];
GlobalData::set_global_variables( $vars );

// 3. Presets (option et_divi_builder_global_presets_d5).
$v = function ( $type, $name, $settings = [] ) {
	return '$variable(' . wp_json_encode( [ 'type' => $type, 'value' => [ 'name' => $name, 'settings' => (object) $settings ] ] ) . ')$';
};
$ts      = time() * 1000;
$presets = GlobalPreset::get_data();
$presets['module']['divi/button'] = [
	'default' => $presets['module']['divi/button']['default'] ?? '',
	'items'   => ( $presets['module']['divi/button']['items'] ?? [] ) + [
		'r6btnpreset1' => [
			'type' => 'module', 'moduleName' => 'divi/button', 'id' => 'r6btnpreset1', 'name' => 'R6 Primary Button',
			'created' => $ts, 'updated' => $ts, 'version' => '5.13.1',
			'attrs' => [ 'button' => [ 'decoration' => [
				'button'     => [ 'desktop' => [ 'value' => [ 'enable' => 'on' ] ] ],
				'background' => [ 'desktop' => [ 'value' => [ 'color' => $v( 'color', 'gcid-r6orange001' ) ] ] ],
				'border'     => [ 'desktop' => [ 'value' => [ 'radius' => [ 'sync' => 'on', 'topLeft' => $v( 'content', 'gvid-r6radius01' ), 'topRight' => $v( 'content', 'gvid-r6radius01' ), 'bottomRight' => $v( 'content', 'gvid-r6radius01' ), 'bottomLeft' => $v( 'content', 'gvid-r6radius01' ) ] ] ] ],
				'font'       => [ 'font' => [ 'desktop' => [ 'value' => [ 'color' => '#ffffff' ] ] ] ],
			] ] ],
		],
	],
];
$presets['group']['divi/font'] = [
	'default' => $presets['group']['divi/font']['default'] ?? '',
	'items'   => ( $presets['group']['divi/font']['items'] ?? [] ) + [
		'r6fontpreset1' => [
			'type' => 'group', 'groupName' => 'divi/font', 'groupId' => 'designTitleText', 'moduleName' => 'divi/heading',
			'primaryAttrName' => 'title', 'id' => 'r6fontpreset1', 'name' => 'R6 Display Heading',
			'created' => $ts, 'updated' => $ts, 'version' => '5.13.1',
			'attrs' => [ 'title' => [ 'decoration' => [ 'font' => [ 'font' => [ 'desktop' => [ 'value' => [
				'family' => $v( 'content', 'gvid-r6font0001' ), 'weight' => '700',
				'color'  => $v( 'color', 'gcid-r6navy0001' ), 'size' => '52px',
			] ] ] ] ] ] ],
		],
	],
];
GlobalPreset::save_data( $presets );

// 4. Page using all of the above.
$sec_bg   = $v( 'color', 'gcid-r6orangelt1' );
$sec_pad  = $v( 'content', 'gvid-r6secpad01' );
$tagline  = $v( 'content', 'gvid-r6tagline1' );
$cta_link = $v( 'content', 'gvid-r6ctalink1' );
$blocks   = [
	[ 'divi/section', [ 'builderVersion' => '5.13.1', 'module' => [ 'decoration' => [
		'spacing'    => [ 'desktop' => [ 'value' => [ 'padding' => [ 'top' => $sec_pad, 'bottom' => $sec_pad, 'right' => '', 'left' => '', 'syncVertical' => 'on', 'syncHorizontal' => 'off' ] ] ] ],
		'background' => [ 'desktop' => [ 'value' => [ 'color' => $sec_bg ] ] ],
	] ] ] ],
	[ 'divi/row', [ 'builderVersion' => '5.13.1' ] ],
	[ 'divi/column', [ 'builderVersion' => '5.13.1', 'module' => [ 'advanced' => [ 'type' => [ 'desktop' => [ 'value' => '4_4' ] ] ] ] ] ],
];
$leaf = [
	[ 'divi/heading', [ 'builderVersion' => '5.13.1', 'title' => [ 'innerContent' => [ 'desktop' => [ 'value' => 'R6 Heading via group preset' ] ] ],
		'groupPreset' => [ 'designTitleText' => [ 'presetId' => [ 'r6fontpreset1' ], 'groupName' => 'divi/font' ] ] ] ],
	[ 'divi/text', [ 'builderVersion' => '5.13.1', 'content' => [ 'innerContent' => [ 'desktop' => [ 'value' => '<p>' . $tagline . '</p>' ] ],
		'decoration' => [ 'bodyFont' => [ 'body' => [ 'font' => [ 'desktop' => [ 'value' => [ 'color' => $v( 'color', 'gcid-r6navy0001' ) ] ] ] ] ] ] ] ] ],
	[ 'divi/button', [ 'builderVersion' => '5.13.1', 'modulePreset' => [ 'r6btnpreset1' ],
		'button' => [ 'innerContent' => [ 'desktop' => [ 'value' => [ 'linkUrl' => $cta_link, 'text' => 'Start' ] ] ] ] ] ],
];
$ser = function ( $name, $attrs ) {
	// serialize_block_attributes() is what WordPress/Divi use: escapes " inside strings as " etc.
	return '<!-- wp:' . $name . ' ' . serialize_block_attributes( $attrs ) . ' -->';
};
$content = '';
foreach ( $blocks as $b ) { $content .= $ser( $b[0], $b[1] ); }
foreach ( $leaf as $b ) { $content .= $ser( $b[0], $b[1] ) . '<!-- /wp:' . $b[0] . ' -->'; }
$content .= '<!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->';

$existing = get_posts( [ 'post_type' => 'page', 'title' => 'R6 tokens trace', 'post_status' => 'any', 'numberposts' => 1 ] );
$postarr  = [ 'post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'R6 tokens trace', 'post_content' => wp_slash( $content ) ];
if ( $existing ) { $postarr['ID'] = $existing[0]->ID; }
$id = wp_insert_post( $postarr, true );
if ( is_wp_error( $id ) ) { WP_CLI::error( $id->get_error_message() ); }
update_post_meta( $id, '_et_pb_use_builder', 'on' );
update_post_meta( $id, '_et_pb_page_layout', 'et_no_sidebar' );
WP_CLI::success( "page $id " . get_permalink( $id ) );
