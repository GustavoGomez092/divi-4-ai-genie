<?php
/**
 * Divi as judge: WordPress/Divi's own view of one Divi 5 block file, as one JSON line.
 *
 *   research/tools/wp-local.sh --user=<admin ID> eval-file research/tools/divi5/judge.php FILE [parse-only]
 *   (with LOCAL_SITE_ID / LOCAL_SITE_PATH of the Divi 5 site; tests/test_divi5_judge.py runs it via wp5())
 *
 * Prints one line "D5JUDGE:{json}" with
 *   parser  the registered block parser class (Divi 5: ET\Builder\FrontEnd\BlockParser\BlockParser)
 *   blocks  parse_blocks(FILE): [{"name","attrs","canonical","inner","children"}] where canonical is
 *           serialize_block_attributes(attrs) and inner is the block's innerContent (HTML chunks, null where a
 *           child block sits); top-level HTML between blocks is {"name":null,"html"}.
 *   render  FILE stored as a draft page "D5TEST judge <file>" (+ _et_pb_use_builder=on) and rendered through the
 *           front-end path (a singular WP_Query for it, do_action('wp'), the_content) with every PHP error, warning,
 *           notice and deprecation captured: {"sections","modules","php_notices","stored_identical","bytes"}.
 *           sections counts elements with class et_pb_section, modules the elements with an et_pb_*_N order
 *           class. The page (and its et-cache directory) is deleted before exiting. parse-only: render is null.
 *
 * Needs a --user with unfiltered_html, or kses rewrites the stored content (research/divi5 §6.2).
 */
if ( empty( $args[0] ) || ! is_readable( $args[0] ) ) {
	WP_CLI::error( 'usage: wp --user=<admin> eval-file judge.php FILE' );
}
if ( ! current_user_can( 'unfiltered_html' ) ) {
	WP_CLI::error( 'judge.php needs --user=<an administrator> (unfiltered_html), or kses rewrites the content' );
}
$d5j_file    = $args[0];
$d5j_content = file_get_contents( $d5j_file );

function d5j_tree( array $blocks ) {
	$out = array();
	foreach ( $blocks as $b ) {
		if ( null === $b['blockName'] ) {
			$out[] = array(
				'name' => null,
				'html' => $b['innerHTML'],
			);
			continue;
		}
		$out[] = array(
			'name'      => $b['blockName'],
			'attrs'     => $b['attrs'],
			'canonical' => serialize_block_attributes( $b['attrs'] ),
			'inner'     => $b['innerContent'],
			'children'  => d5j_tree( $b['innerBlocks'] ),
		);
	}
	return $out;
}

function d5j_count_classes( $html ) {
	$sections = 0;
	$modules  = 0;
	preg_match_all( '/\sclass="([^"]*)"/', $html, $m );
	foreach ( $m[1] as $class_attr ) {
		$classes = preg_split( '/\s+/', trim( $class_attr ) );
		if ( in_array( 'et_pb_section', $classes, true ) ) {
			++$sections;
		}
		if ( preg_grep( '/^et_pb_[a-z_]+_\d+$/', $classes ) ) {
			++$modules;
		}
	}
	return array( $sections, $modules );
}

function d5j_render( $file, $content ) {
	global $wp_query, $wp_the_query, $wp;
	$notices = array();
	$id      = wp_insert_post(
		array(
			'post_type'    => 'page',
			'post_status'  => 'draft',
			'post_title'   => 'D5TEST judge ' . basename( $file ),
			'post_content' => wp_slash( $content ),
		),
		true
	);
	if ( is_wp_error( $id ) ) {
		WP_CLI::error( 'wp_insert_post: ' . $id->get_error_message() );
	}
	$html = '';
	try {
		update_post_meta( $id, '_et_pb_use_builder', 'on' );
		$stored = get_post_field( 'post_content', $id, 'raw' );

		$old_level = error_reporting( E_ALL );
		set_error_handler(
			function ( $errno, $errstr, $errfile, $errline ) use ( &$notices ) {
				$notices[] = sprintf( '%d %s (%s:%d)', $errno, $errstr, basename( $errfile ), $errline );
				return true;
			}
		);
		ob_start();
		try {
			$wp_query     = new WP_Query(
				array(
					'page_id'     => $id,
					'post_type'   => 'page',
					'post_status' => 'any',
				)
			);
			$wp_the_query = $wp_query;
			$wp_query->the_post();
			do_action( 'wp', $wp );
			echo apply_filters( 'the_content', get_the_content() ); // phpcs:ignore WordPress.Security.EscapeOutput
		} catch ( Throwable $e ) {
			$notices[] = get_class( $e ) . ': ' . $e->getMessage() . ' (' . basename( $e->getFile() ) . ':' . $e->getLine() . ')';
		}
		$html = ob_get_clean();
		restore_error_handler();
		error_reporting( $old_level );
		wp_reset_postdata();
	} finally {
		wp_delete_post( $id, true );
		$cache = WP_CONTENT_DIR . '/et-cache/' . $id;
		if ( is_dir( $cache ) ) {
			foreach ( glob( $cache . '/{,.}*', GLOB_BRACE ) as $f ) {
				if ( is_file( $f ) ) {
					unlink( $f );
				}
			}
			rmdir( $cache );
		}
	}
	list( $sections, $modules ) = d5j_count_classes( $html );
	return array(
		'sections'         => $sections,
		'modules'          => $modules,
		'php_notices'      => array_values( array_unique( $notices ) ),
		'stored_identical' => $stored === $content,
		'bytes'            => strlen( $html ),
	);
}

$d5j_result = array(
	'parser' => apply_filters( 'block_parser_class', 'WP_Block_Parser' ),
	'blocks' => d5j_tree( parse_blocks( $d5j_content ) ),
);
$d5j_result['render'] = ( isset( $args[1] ) && 'parse-only' === $args[1] ) ? null : d5j_render( $d5j_file, $d5j_content );

$d5j_json = wp_json_encode( $d5j_result, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
if ( false === $d5j_json ) {
	WP_CLI::error( 'json_encode failed: ' . json_last_error_msg() );
}
echo "\nD5JUDGE:" . $d5j_json . "\n";
