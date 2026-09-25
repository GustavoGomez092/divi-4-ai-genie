<?php
/**
 * Headless Divi 4 renderer (prototype).
 *
 * Renders an arbitrary Divi shortcode string through the *real* Divi theme running on a
 * WordPress install, WITHOUT creating a post, WITHOUT an HTTP request and WITHOUT a browser.
 * Output is one self-contained HTML document (all local CSS/JS inlined, local image URLs
 * made absolute or embedded) that you can open straight from disk.
 *
 * How it works (see ../divi-render-engine.md for the source references):
 *   1. A fake WP_Post (ID FAKE_ID) is primed into the object cache together with its
 *      post meta (`_et_pb_use_builder=on`, page layout, static-css off ...). Nothing
 *      touches wp_posts; meta writes for FAKE_ID are short-circuited.
 *   2. `wp()` runs the main query for `page_id=FAKE_ID`; `posts_pre_query` hands back the
 *      fake post, so is_singular()/is_page() are true and the 'wp' action fires, which is
 *      where Divi boots its module framework (framework.php `et_builder_modules_load_hook`).
 *   3. The theme's page template is included under output buffering, so get_header(),
 *      the_content (shortcodes -> ET_Builder_Element::_render), wp_head and wp_footer
 *      all run exactly like a front-end request.
 *   4. Builder CSS is forced inline (static-css-file off for the fake post), critical CSS
 *      and dynamic CSS are disabled so the full style-static.min.css is used, which
 *      removes every deferred/async stylesheet (the "unstyled first view" problem).
 *   5. The captured HTML is post-processed: every <link rel=stylesheet|preload> and
 *      <script src> that points at this site is replaced by its file contents read
 *      from disk; url(...) inside inlined CSS is made absolute.
 *
 * Usage (WP-CLI against the mirror site):
 *   wp eval-file render.php <shortcode-file> <out.html> [layout=et_no_sidebar|et_full_width_page]
 *        [title="Preview"] [settings=client-settings.json] [meta=page-meta.json] [embed-images] [no-js]
 *   (WP-CLI rejects unknown --flags on eval-file, hence bare name=value options.)
 *
 *   settings=   JSON bundle produced by export-settings.php on the CLIENT site. Its options
 *               (et_divi incl. customizer + global colors, global presets, theme mods) and
 *               Additional CSS are applied in memory only (pre_option_* filters).
 *
 * Read-only with respect to the DB and theme files. It does write/refresh the site-wide
 * et-cache/global customizer file only if Divi decides to (same as any front-end hit).
 */

if ( ! defined( 'ABSPATH' ) ) {
	fwrite( STDERR, "Run with: wp eval-file render.php <shortcode-file> <out.html>\n" );
	exit( 1 );
}

// ---------------------------------------------------------------------------------------------
// Arguments.
// ---------------------------------------------------------------------------------------------
$positional = array();
$opts       = array(
	'layout'       => 'et_no_sidebar',
	'title'        => 'Divi Render Preview',
	'embed-images' => false,
	'no-js'        => false,
);
foreach ( (array) $args as $a ) {
	// WP-CLI rejects unknown --flags for eval-file, so options are passed as bare `name=value`
	// (or bare `name` for booleans); a leading `--` is tolerated for direct PHP use.
	if ( preg_match( '/^(?:--)?(layout|title|settings|meta|embed-images|no-js)(?:=(.*))?$/', $a, $m ) ) {
		$opts[ $m[1] ] = isset( $m[2] ) ? $m[2] : true;
	} else {
		$positional[] = $a;
	}
}
if ( count( $positional ) < 2 ) {
	WP_CLI::error( 'Usage: wp eval-file render.php <shortcode-file> <out.html> [layout=..] [title=..] [settings=bundle.json] [meta=page-meta.json] [embed-images] [no-js]' );
}
list( $sc_file, $out_file ) = $positional;
$shortcode = file_get_contents( $sc_file );
if ( false === $shortcode || '' === trim( $shortcode ) ) {
	WP_CLI::error( "Cannot read shortcode from $sc_file" );
}

const DIVI_RENDER_FAKE_ID = 990000001;

// ---------------------------------------------------------------------------------------------
// 0. Optional client site-settings bundle (JSON from export-settings.php), applied IN MEMORY.
//    Every option is served through pre_option_* filters and every write to it is vetoed,
//    so the mirror site's DB is never modified.
// ---------------------------------------------------------------------------------------------
if ( ! empty( $opts['settings'] ) ) {
	$bundle = json_decode( file_get_contents( $opts['settings'] ), true );
	if ( ! is_array( $bundle ) ) {
		WP_CLI::error( 'Cannot parse settings bundle ' . $opts['settings'] );
	}
	$options = isset( $bundle['options'] ) ? $bundle['options'] : array();
	foreach ( $options as $name => $value ) {
		if ( 'et_divi' === $name ) {
			// Merge over local et_divi so local migration flags stay set (prevents Divi migrations
			// from firing and trying to write). Client values win.
			$local = get_option( 'et_divi', array() );
			$value = array_merge( is_array( $local ) ? $local : array(), $value );
		}
		if ( 'et_divi_builder_global_presets_ng' === $name ) {
			// Divi stores presets as nested stdClass objects and its normaliser reads them with
			// ->property access (global-presets/Settings.php _normalize_global_presets()).
			$value = json_decode( wp_json_encode( empty( $value ) ? new stdClass() : $value ) );
		}
		add_filter( "pre_option_{$name}", function () use ( $value ) { return $value; }, 999 );
		add_filter( "pre_update_option_{$name}", function ( $new, $old ) { return $old; }, 999, 2 );
	}
	if ( isset( $bundle['custom_css'] ) ) {
		$client_css = $bundle['custom_css'];
		add_filter( 'wp_get_custom_css', function () use ( $client_css ) { return $client_css; }, 1 );
	}
	// Drop caches that were filled while WordPress booted with the local values.
	unset( $GLOBALS['et_theme_options'] );
	if ( class_exists( 'ET_Builder_Global_Presets_Settings' ) ) {
		$rp = new ReflectionProperty( 'ET_Builder_Global_Presets_Settings', '_instance' );
		$rp->setAccessible( true );
		$rp->setValue( null, null );
	}
	WP_CLI::log( 'Applied settings bundle: ' . implode( ', ', array_keys( $options ) ) . ( isset( $bundle['custom_css'] ) ? ', custom_css' : '' ) );
}

// ---------------------------------------------------------------------------------------------
// 1. Fake post + meta, primed into the object cache (never written to the DB).
// ---------------------------------------------------------------------------------------------
$now       = current_time( 'mysql' );
$fake_post = new WP_Post(
	(object) array(
		'ID'                => DIVI_RENDER_FAKE_ID,
		'post_author'       => 1,
		'post_date'         => $now,
		'post_date_gmt'     => get_gmt_from_date( $now ),
		'post_content'      => $shortcode,
		'post_title'        => $opts['title'],
		'post_excerpt'      => '',
		'post_status'       => 'publish',
		'comment_status'    => 'closed',
		'ping_status'       => 'closed',
		'post_password'     => '',
		'post_name'         => 'divi-render-preview',
		'post_modified'     => $now,
		'post_modified_gmt' => get_gmt_from_date( $now ),
		'post_parent'       => 0,
		'guid'              => home_url( '/?page_id=' . DIVI_RENDER_FAKE_ID ),
		'menu_order'        => 0,
		'post_type'         => 'page',
		'post_mime_type'    => '',
		'comment_count'     => 0,
		'filter'            => 'raw',
	)
);
wp_cache_set( DIVI_RENDER_FAKE_ID, $fake_post, 'posts' );
$fake_meta = array(
	'_et_pb_use_builder'         => array( 'on' ),
	'_et_pb_built_for_post_type' => array( 'page' ),
	'_et_pb_page_layout'         => array( $opts['layout'] ),
	'_wp_page_template'          => array( 'default' ),
);
// Optional page-level meta the pusher will also write (e.g. _et_pb_custom_css, _et_pb_page_layout,
// _et_pb_light_text_color ...), as a flat JSON object {"meta_key": "value"}.
if ( ! empty( $opts['meta'] ) ) {
	foreach ( (array) json_decode( file_get_contents( $opts['meta'] ), true ) as $k => $v ) {
		$fake_meta[ $k ] = array( is_scalar( $v ) ? (string) $v : maybe_serialize( $v ) );
	}
}
$fake_meta['_et_pb_static_css_file'] = array( 'off' ); // Forces builder CSS inline (class-et-builder-element.php:1626).
wp_cache_set( DIVI_RENDER_FAKE_ID, $fake_meta, 'post_meta' );

// Short-circuit every meta write for the fake post (fonts cache, dynamic-assets cache, feature cache...).
$block_meta_write = function ( $check, $object_id ) {
	return ( (int) $object_id === DIVI_RENDER_FAKE_ID ) ? true : $check;
};
add_filter( 'update_post_metadata', $block_meta_write, 1, 2 );
add_filter( 'add_post_metadata', $block_meta_write, 1, 2 );
add_filter( 'delete_post_metadata', $block_meta_write, 1, 2 );

// ---------------------------------------------------------------------------------------------
// 2. Make Divi behave like its own preview endpoint (functions.php:10107 et_pb_preview_page_disable_dynamic_assets).
// ---------------------------------------------------------------------------------------------
add_filter( 'et_builder_should_load_all_module_data', '__return_true' );
add_filter( 'et_builder_critical_css_enabled', '__return_false' );
add_filter( 'et_builder_post_feature_cache_enabled', '__return_false' );
// Dynamic CSS/JS off => the complete style-static.min.css is used and nothing is written to
// et-cache/<id>/ (in CLI Divi already refuses to generate dynamic assets; this makes it explicit).
add_filter( 'et_disable_js_on_demand', '__return_true' );
add_filter( 'et_use_dynamic_css', '__return_false' );
add_filter( 'et_should_generate_dynamic_assets', '__return_false' );
// Never let the customizer/unified page resource try to write static files for the fake post.
add_filter( 'et_core_page_resource_force_write', '__return_false', 999 );
show_admin_bar( false );

// Hand the fake post to the main query.
add_filter(
	'posts_pre_query',
	function ( $posts, $q ) use ( $fake_post ) {
		if ( $q->is_main_query() && (int) $q->get( 'page_id' ) === DIVI_RENDER_FAKE_ID ) {
			$q->found_posts   = 1;
			$q->max_num_pages = 1;
			return array( $fake_post );
		}
		return $posts;
	},
	10,
	2
);

// ---------------------------------------------------------------------------------------------
// 3. Run the front-end request.
// ---------------------------------------------------------------------------------------------
$_SERVER['REQUEST_URI']    = '/?page_id=' . DIVI_RENDER_FAKE_ID;
$_SERVER['REQUEST_METHOD'] = 'GET';
$_SERVER['HTTP_HOST']      = wp_parse_url( home_url(), PHP_URL_HOST );
$_SERVER['SERVER_NAME']    = $_SERVER['HTTP_HOST'];
$_GET['page_id']           = DIVI_RENDER_FAKE_ID;

wp( array( 'page_id' => DIVI_RENDER_FAKE_ID ) );

if ( ! is_singular() || get_queried_object_id() !== DIVI_RENDER_FAKE_ID ) {
	WP_CLI::error( 'Main query did not resolve to the fake page (is_singular=' . var_export( is_singular(), true ) . ')' );
}

remove_action( 'template_redirect', 'redirect_canonical' );
remove_action( 'template_redirect', 'wp_redirect_admin_locations', 1000 );

ob_start();
do_action( 'template_redirect' );
$template = get_page_template();
if ( ! $template ) {
	$template = get_index_template();
}
$template = apply_filters( 'template_include', $template );
include $template;
$html = ob_get_clean();

// Let shutdown hooks (fonts cache etc.) run harmlessly: meta writes are blocked above.

// ---------------------------------------------------------------------------------------------
// 4. Inline local assets so the file is self-contained.
// ---------------------------------------------------------------------------------------------
$site_url  = untrailingslashit( site_url() );
$home_url  = untrailingslashit( home_url() );
$abspath   = untrailingslashit( ABSPATH );
$content_u = untrailingslashit( content_url() );
$content_d = untrailingslashit( WP_CONTENT_DIR );

$url_to_path = function ( $url ) use ( $site_url, $home_url, $abspath, $content_u, $content_d ) {
	$url = html_entity_decode( $url );
	$url = preg_replace( '/[?#].*$/', '', $url );
	if ( 0 === strpos( $url, '//' ) ) {
		$url = 'http:' . $url;
	}
	foreach ( array( $content_u => $content_d, $site_url => $abspath, $home_url => $abspath ) as $u => $d ) {
		$u_noscheme = preg_replace( '#^https?:#', '', $u );
		$url_ns     = preg_replace( '#^https?:#', '', $url );
		if ( 0 === strpos( $url_ns, $u_noscheme . '/' ) ) {
			$p = $d . substr( $url_ns, strlen( $u_noscheme ) );
			return is_readable( $p ) ? $p : null;
		}
	}
	return null;
};

$absolutize_css_urls = function ( $css, $base_url ) {
	return preg_replace_callback(
		'/url\(\s*([\'"]?)(?!data:|https?:|\/\/|#)([^\'")]+)\1\s*\)/i',
		function ( $m ) use ( $base_url ) {
			$rel = $m[2];
			if ( '/' === $rel[0] ) {
				$parts = wp_parse_url( $base_url );
				return 'url(' . $m[1] . $parts['scheme'] . '://' . $parts['host'] . ( isset( $parts['port'] ) ? ':' . $parts['port'] : '' ) . $rel . $m[1] . ')';
			}
			return 'url(' . $m[1] . trailingslashit( dirname( $base_url ) ) . $rel . $m[1] . ')';
		},
		$css
	);
};

$stats = array( 'css_inlined' => 0, 'css_remote' => 0, 'js_inlined' => 0, 'js_remote' => 0, 'img_embedded' => 0 );

// Stylesheets (rel=stylesheet and Divi's rel=preload as=style deferred links).
$html = preg_replace_callback(
	'/<link\b[^>]*>/i',
	function ( $m ) use ( $url_to_path, $absolutize_css_urls, &$stats ) {
		$tag = $m[0];
		if ( ! preg_match( '/rel=[\'"](stylesheet|preload)[\'"]/i', $tag, $rel ) ) {
			return $tag;
		}
		if ( 'preload' === strtolower( $rel[1] ) && ! preg_match( '/as=[\'"]style[\'"]/i', $tag ) ) {
			return $tag;
		}
		if ( ! preg_match( '/href=[\'"]([^\'"]+)[\'"]/i', $tag, $h ) ) {
			return $tag;
		}
		$href = html_entity_decode( $h[1] );
		$path = $url_to_path( $href );
		if ( ! $path ) {
			$stats['css_remote']++;
			// Remote (e.g. Google Fonts): normalise preload into a plain stylesheet link.
			return '<link rel="stylesheet" href="' . esc_attr( $href ) . '" />';
		}
		$stats['css_inlined']++;
		$id    = preg_match( '/id=[\'"]([^\'"]+)[\'"]/i', $tag, $i ) ? ' id="' . esc_attr( $i[1] ) . '-inlined"' : '';
		$media = preg_match( '/media=[\'"]([^\'"]+)[\'"]/i', $tag, $md ) ? ' media="' . esc_attr( $md[1] ) . '"' : '';
		return '<style' . $id . $media . ">\n" . $absolutize_css_urls( file_get_contents( $path ), preg_replace( '/[?#].*$/', '', $href ) ) . "\n</style>";
	},
	$html
);

// Scripts.
$html = preg_replace_callback(
	'/<script\b([^>]*)\bsrc=[\'"]([^\'"]+)[\'"]([^>]*)>\s*<\/script>/i',
	function ( $m ) use ( $url_to_path, $opts, &$stats ) {
		if ( $opts['no-js'] ) {
			return '';
		}
		$path = $url_to_path( $m[2] );
		if ( ! $path ) {
			$stats['js_remote']++;
			return $m[0];
		}
		$stats['js_inlined']++;
		$js = str_ireplace( '</script', '<\/script', file_get_contents( $path ) );
		return '<script' . preg_replace( '/\s+(id|defer|async)=[\'"][^\'"]*[\'"]/i', '', $m[1] . $m[3] ) . ">\n" . $js . "\n</script>";
	},
	$html
);

// Optionally embed local images as data: URIs (otherwise they stay absolute URLs to the mirror site).
if ( $opts['embed-images'] ) {
	$html = preg_replace_callback(
		'#(["\'(])(' . preg_quote( $content_u, '#' ) . '/uploads/[^"\')\s]+\.(?:png|jpe?g|gif|webp|svg))#i',
		function ( $m ) use ( $url_to_path, &$stats ) {
			$p = $url_to_path( $m[2] );
			if ( ! $p || filesize( $p ) > 3 * 1024 * 1024 ) {
				return $m[0];
			}
			$stats['img_embedded']++;
			$mime = wp_check_filetype( $p )['type'];
			return $m[1] . 'data:' . $mime . ';base64,' . base64_encode( file_get_contents( $p ) );
		},
		$html
	);
}

// Forced-inline builder CSS and the builder Google Fonts link are printed in wp_footer
// (class-et-builder-element.php setup_advanced_styles_manager: output location 'footer').
// On a production hit with a static CSS file they sit at the end of <head>. Left in the footer,
// every module first paints with the base theme styles and then *transitions* (Divi sets
// `transition: all 300ms` on buttons etc.) to its real styles - in a background tab those
// transitions never finish. Move them to the end of <head> to match production ordering.
$moved = '';
$html  = preg_replace_callback(
	'#<style[^>]*id=["\']et-builder-module-design-[^"\']*["\'][^>]*>.*?</style>|<link[^>]*id=["\']et-builder-googlefonts[^"\']*["\'][^>]*>#is',
	function ( $m ) use ( &$moved ) {
		$moved .= $m[0] . "\n";
		return '';
	},
	$html
);
// Google Fonts links were normalised above (id dropped), so move any that ended up in <body> by URL.
$body_pos = stripos( $html, '<body' );
if ( false !== $body_pos ) {
	$head_part = substr( $html, 0, $body_pos );
	$body_part = preg_replace_callback(
		'#<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*" />#i',
		function ( $m ) use ( &$moved ) {
			$moved = $m[0] . "\n" . $moved;
			return '';
		},
		substr( $html, $body_pos )
	);
	$html = $head_part . $body_part;
}
$html = preg_replace( '#</head>#i', $moved . '</head>', $html, 1 );

file_put_contents( $out_file, $html );

// ---------------------------------------------------------------------------------------------
// 5. Report.
// ---------------------------------------------------------------------------------------------
$builder_css_bytes = 0;
if ( preg_match_all( '/<style[^>]*id=[\'"]et-(?:builder-module-design|core-unified)[^\'"]*[\'"][^>]*>(.*?)<\/style>/is', $html, $mm ) ) {
	foreach ( $mm[1] as $b ) {
		$builder_css_bytes += strlen( $b );
	}
}
WP_CLI::success(
	sprintf(
		'Wrote %s (%s KB). sections=%d modules=%d builder-css=%d B, css inlined=%d remote=%d, js inlined=%d remote=%d, images embedded=%d',
		$out_file,
		number_format( strlen( $html ) / 1024, 1 ),
		preg_match_all( '/class="et_pb_section et_pb_section_\d+/', $html ),
		preg_match_all( '/class="et_pb_module /', $html ),
		$builder_css_bytes,
		$stats['css_inlined'],
		$stats['css_remote'],
		$stats['js_inlined'],
		$stats['js_remote'],
		$stats['img_embedded']
	)
);
