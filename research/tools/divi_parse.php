<?php
/**
 * Print Divi's own parse of a shortcode file as JSON.
 *   research/tools/wp-local.sh --require=research/tools/force-all-modules.php eval-file research/tools/divi_parse.php <file>
 */
if ( ! did_action( 'et_builder_ready' ) ) {
	do_action( 'wp' );
}
// render_as_builder_data() bails with '' unless $_POST['action'] is set or this
// filter returns true (class-et-builder-element.php:3756-3758); force it on for CLI use.
add_filter( 'et_builder_module_force_render', '__return_true' );
$tree     = et_fb_process_shortcode( file_get_contents( $args[0] ) );
$simplify = function ( $items ) use ( &$simplify ) {
	$out = array();
	foreach ( (array) $items as $item ) {
		$content = isset( $item['content'] ) ? $item['content'] : '';
		$out[]   = array(
			'type'     => isset( $item['type'] ) ? $item['type'] : '',
			'attrs'    => isset( $item['attrs'] ) ? $item['attrs'] : array(),
			'content'  => is_array( $content ) ? '' : (string) $content,
			'children' => is_array( $content ) ? $simplify( $content ) : array(),
		);
	}
	return $out;
};
echo wp_json_encode( $simplify( $tree ), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE );
