<?php
/**
 * Plugin Name: Post Pusher Divi preview
 * Description: GET /?pp_preview=<name> renders <PP_PAGES_DIR>/<name>.txt (a Divi 4 shortcode layout or
 *              Divi 5 block markup) as a full front-end page through the real Divi theme, without creating a post.
 *
 * Same technique as research/render-prototype/render.php (repo only), but inside a real HTTP request
 * (WordPress Playground has no WP-CLI eval-file loop we want to pay for on every render):
 *   - a fake WP_Post + its meta are primed into the (per-request) object cache;
 *   - the `request` filter points the main query at page_id=FAKE and posts_pre_query returns the
 *     fake post, so is_singular()/is_page() are true and Divi boots on `wp` as for a real page;
 *   - Divi's own preview-mode filters (all modules, no critical/dynamic CSS, no feature cache);
 *   - builder CSS is forced inline (_et_pb_static_css_file=off) and moved from the footer to the
 *     end of <head> with an output buffer (matches production ordering; see divi-render-engine.md §3).
 * The file is read on every request, so editing it and reloading re-renders. Nothing is written to
 * the DB for the fake ID.
 *
 * Query args: pp_preview=<name> (required, [A-Za-z0-9_-]+), title=..., layout=et_no_sidebar|et_full_width_page|..., inline=1 (self-contained HTML)
 *
 * Divi 5 (research/divi5/playground.md, repo only). The same fake-post technique renders block markup; three
 * Divi 5-only fixes, each gated on the mounted theme being Divi 5 so Divi 4 output is unchanged:
 *   - Divi 5 always caches per-post CSS in wp-content/et-cache/<post id>/ (static CSS is forced on; the Divi 4
 *     _et_pb_static_css_file=off meta is ignored), so a reused fake ID served another page's (or the pre-edit)
 *     CSS. Each request drops that dir first, and `serve` pages (not inline=1) get their own fake ID per page
 *     name, so two tabs on different pages never purge each other's late-loaded CSS file.
 *   - inline=1 also embeds the icon fonts Divi 5 references by protocol-relative URL inside <style> blocks.
 *   - "Open Sans" is dropped from builder Google Fonts URLs when the theme already loads it (what a warm live
 *     Divi 5 page does; the preview is always a cold render).
 * Token seeding (Divi 5 only): <name>.seed.css next to the page (written by preview.py --tokens) is added as
 * <style id="pp-token-seed"> at the end of <head>.
 */

if ( ! defined( 'ABSPATH' ) || empty( $_GET['pp_preview'] ) ) {
	return;
}

$pp_name = preg_replace( '/[^A-Za-z0-9_-]/', '', (string) $_GET['pp_preview'] );

/**
 * Major version of the mounted Divi theme (read from its style.css header: the theme isn't loaded yet).
 */
function pp_preview_divi_major() {
	static $major = null;
	if ( null === $major ) {
		$css   = @file_get_contents( WP_CONTENT_DIR . '/themes/Divi/style.css', false, null, 0, 4096 );
		$major = ( $css && preg_match( '/^\s*Version:\s*(\d+)\./mi', $css, $m ) ) ? (int) $m[1] : 0;
	}
	return $major;
}

// Divi 4, and every inline=1 render: the fixed fake ID (Divi 4 output is unchanged). Divi 5 `serve`: one fake
// ID per page name (stable across reloads, so et-cache stays bounded by the number of pages).
define(
	'PP_PREVIEW_FAKE_ID',
	( pp_preview_divi_major() >= 5 && empty( $_GET['inline'] ) ) ? 990000002 + ( crc32( $pp_name ) % 999998 ) : 990000001
);

if ( pp_preview_divi_major() >= 5 ) {
	// Divi 5 finds wp-content/et-cache/<id>/*.css from an earlier render and reuses it (StaticCSS::
	// setup_styles_manager). Measured without this: page b served with page a's CSS (+334/-169 declarations).
	$pp_cache = WP_CONTENT_DIR . '/et-cache/' . PP_PREVIEW_FAKE_ID;
	if ( is_dir( $pp_cache ) ) {
		$pp_it = new RecursiveIteratorIterator( new RecursiveDirectoryIterator( $pp_cache, FilesystemIterator::SKIP_DOTS ), RecursiveIteratorIterator::CHILD_FIRST );
		foreach ( $pp_it as $pp_f ) {
			$pp_f->isDir() ? @rmdir( $pp_f->getPathname() ) : @unlink( $pp_f->getPathname() );
		}
		@rmdir( $pp_cache );
	}
}
$pp_dir  = defined( 'PP_PAGES_DIR' ) ? PP_PAGES_DIR : '/pp-pages';
$pp_file = $pp_dir . '/' . $pp_name . '.txt';

if ( '' === $pp_name || ! is_readable( $pp_file ) ) {
	status_header( 404 );
	header( 'Content-Type: text/plain; charset=utf-8' );
	echo "pp_preview: no such layout file: $pp_file\n";
	exit;
}

$pp_shortcode = file_get_contents( $pp_file );
$pp_layout    = isset( $_GET['layout'] ) ? preg_replace( '/[^a-z_]/', '', $_GET['layout'] ) : 'et_no_sidebar';
$pp_title     = isset( $_GET['title'] ) ? wp_unslash( (string) $_GET['title'] ) : 'Divi Preview';

// Page-level meta sidecar (optional): <name>.meta.json, flat {"meta_key": "value"} (e.g. _et_pb_custom_css).
$pp_meta_file = $pp_dir . '/' . $pp_name . '.meta.json';
$pp_meta_in   = is_readable( $pp_meta_file ) ? (array) json_decode( file_get_contents( $pp_meta_file ), true ) : array();
// Token-seeding sidecar (optional, Divi 5 only): <name>.seed.css, the client's recovered global colors,
// variables and preset CSS. Never read on Divi 4, so Divi 4 output can't change.
$pp_seed_file = $pp_dir . '/' . $pp_name . '.seed.css';
$pp_seed_css  = ( pp_preview_divi_major() >= 5 && is_readable( $pp_seed_file ) ) ? (string) file_get_contents( $pp_seed_file ) : '';

/**
 * Prime the fake post + meta. Called early and again on `wp` in case anything flushed the cache.
 */
function pp_preview_prime() {
	global $pp_shortcode, $pp_layout, $pp_title, $pp_meta_in;
	$now  = current_time( 'mysql' );
	$post = new WP_Post(
		(object) array(
			'ID'                => PP_PREVIEW_FAKE_ID,
			'post_author'       => 1,
			'post_date'         => $now,
			'post_date_gmt'     => get_gmt_from_date( $now ),
			'post_content'      => $pp_shortcode,
			'post_title'        => $pp_title,
			'post_excerpt'      => '',
			'post_status'       => 'publish',
			'comment_status'    => 'closed',
			'ping_status'       => 'closed',
			'post_password'     => '',
			'post_name'         => 'pp-preview',
			'post_modified'     => $now,
			'post_modified_gmt' => get_gmt_from_date( $now ),
			'post_parent'       => 0,
			'guid'              => home_url( '/?page_id=' . PP_PREVIEW_FAKE_ID ),
			'menu_order'        => 0,
			'post_type'         => 'page',
			'post_mime_type'    => '',
			'comment_count'     => 0,
			'filter'            => 'raw',
		)
	);
	wp_cache_set( PP_PREVIEW_FAKE_ID, $post, 'posts' );
	$meta = array(
		'_et_pb_use_builder'         => array( 'on' ),
		'_et_pb_built_for_post_type' => array( 'page' ),
		'_et_pb_page_layout'         => array( $pp_layout ),
		'_wp_page_template'          => array( 'default' ),
	);
	foreach ( $pp_meta_in as $k => $v ) {
		$meta[ $k ] = array( is_scalar( $v ) ? (string) $v : maybe_serialize( $v ) );
	}
	$meta['_et_pb_static_css_file'] = array( 'off' ); // builder CSS inline (class-et-builder-element.php:1626)
	wp_cache_set( PP_PREVIEW_FAKE_ID, $meta, 'post_meta' );
	return $post;
}

add_action( 'muplugins_loaded', 'pp_preview_prime', 0 );
add_action( 'wp', 'pp_preview_prime', 0 );

// Never write meta for the fake post.
$pp_block_meta_write = function ( $check, $object_id ) {
	return ( (int) $object_id === PP_PREVIEW_FAKE_ID ) ? true : $check;
};
add_filter( 'update_post_metadata', $pp_block_meta_write, 1, 2 );
add_filter( 'add_post_metadata', $pp_block_meta_write, 1, 2 );
add_filter( 'delete_post_metadata', $pp_block_meta_write, 1, 2 );

// Divi preview-mode filters (functions.php:10107 et_pb_preview_page_disable_dynamic_assets).
add_filter( 'et_builder_should_load_all_module_data', '__return_true' );
add_filter( 'et_builder_critical_css_enabled', '__return_false' );
add_filter( 'et_builder_post_feature_cache_enabled', '__return_false' );
add_filter( 'et_disable_js_on_demand', '__return_true' );
add_filter( 'et_use_dynamic_css', '__return_false' );
add_filter( 'et_should_generate_dynamic_assets', '__return_false' );
add_filter( 'et_core_page_resource_force_write', '__return_false', 999 );
add_filter( 'show_admin_bar', '__return_false' );
// The blueprint (re)activates Divi on every boot; WP then fires `after_switch_theme` on the next
// request and Divi 4.27 answers it with a 302 to wp-admin/admin.php?page=et_onboarding.
add_action(
	'after_setup_theme',
	function () {
		remove_action( 'after_switch_theme', 'et_onboarding_trigger_redirect' );
	},
	99
);
// Emit Google Fonts as <link> (what a warmed-up live page serves) instead of Divi's "inline Google
// Fonts" mode, which fetches the CSS server-side on every uncached render with non-browser user
// agents (different font files => glyph-level pixel differences, plus a network round trip).
add_filter(
	'et_builder_google_fonts_is_enabled',
	function ( $enabled, $sub_option ) {
		return 'google_fonts_inline' === $sub_option ? false : $enabled;
	},
	10,
	2
);

// Divi 5 cold/warm font asymmetry: a warmed live page prints the builder Google Fonts from post meta
// (et_builder_preprint_font), which DROPS "Open Sans" when the theme already enqueues it; the cold path
// (et_builder_print_font, footer) keeps it. The preview can never be warm (no meta writes for the fake
// ID), so apply the same filter to the builder font URLs. Measured without this: the variable
// Open Sans (wdth axis) replaced the theme's static Open Sans, re-wrapping a 390px heading (+22px).
// Divi 5 only: Divi 4's preprint path has no such filter (4.27.9 prints Open Sans both ways).
if ( pp_preview_divi_major() >= 5 ) {
	add_filter(
		'style_loader_src',
		function ( $src, $handle ) {
			if ( 0 !== strpos( $handle, 'et-builder-googlefonts' ) || ! function_exists( 'et_divi_fonts_url' ) ) {
				return $src;
			}
			$body = et_get_option( 'body_font', 'none' );
			if ( '' === et_divi_fonts_url() || ! ( 'none' === $body || '' === $body ) ) {
				return $src;
			}
			$p = wp_parse_url( $src );
			if ( empty( $p['query'] ) ) {
				return $src;
			}
			$parts = array();
			foreach ( explode( '&', str_replace( '&#038;', '&', $p['query'] ) ) as $kv ) {
				if ( 0 === strpos( $kv, 'family=' ) ) {
					// css2: one family per param; css (v1): pipe-separated list.
					$fams = array_filter(
						explode( '|', str_replace( '%7C', '|', substr( $kv, 7 ) ) ),
						function ( $f ) {
							return 0 !== strcasecmp( trim( str_replace( array( '+', '%20' ), ' ', explode( ':', $f )[0] ) ), 'Open Sans' );
						}
					);
					if ( ! $fams ) {
						continue;
					}
					$kv = 'family=' . implode( '|', $fams );
				}
				$parts[] = $kv;
			}
			if ( ! preg_grep( '/^family=/', $parts ) ) {
				return false; // nothing left to load
			}
			return $p['scheme'] . '://' . $p['host'] . ( isset( $p['port'] ) ? ':' . $p['port'] : '' ) . $p['path'] . '?' . implode( '&', $parts );
		},
		10,
		2
	);
}

// Point the main query at the fake page and hand it the fake post.
add_filter(
	'request',
	function () {
		return array( 'page_id' => PP_PREVIEW_FAKE_ID );
	},
	999
);
add_filter(
	'posts_pre_query',
	function ( $posts, $q ) {
		if ( $q->is_main_query() && (int) $q->get( 'page_id' ) === PP_PREVIEW_FAKE_ID ) {
			$q->found_posts   = 1;
			$q->max_num_pages = 1;
			return array( pp_preview_prime() );
		}
		return $posts;
	},
	10,
	2
);
add_action(
	'template_redirect',
	function () {
		remove_action( 'template_redirect', 'redirect_canonical' );
		remove_action( 'template_redirect', 'wp_redirect_admin_locations', 1000 );
		nocache_headers();
		header( 'X-PP-Preview: ' . PP_PREVIEW_FAKE_ID );
		header( sprintf( 'X-PP-Env: php=%s wp=%s divi=%s theme=%s wp_debug=%d', PHP_VERSION, get_bloginfo( 'version' ), defined( 'ET_CORE_VERSION' ) ? ET_CORE_VERSION : '?', get_template(), WP_DEBUG ) );
		// Move forced-inline builder CSS + builder Google Fonts link from the footer to the end of <head>.
		ob_start(
			function ( $html ) {
				$moved = '';
				$html  = preg_replace_callback(
					'#<style[^>]*id=["\']et-builder-module-design-[^"\']*["\'][^>]*>.*?</style>|<link[^>]*id=["\']et-builder-googlefonts[^"\']*["\'][^>]*>#is',
					function ( $m ) use ( &$moved ) {
						$moved .= $m[0] . "\n";
						return '';
					},
					$html
				);
				$html = preg_replace( '#</head>#i', $moved . '</head>', $html, 1 );
				$html = pp_preview_seed( $html );
				return empty( $_GET['inline'] ) ? $html : pp_preview_inline_assets( $html );
			}
		);
	},
	0
);

/**
 * Token seeding: the <name>.seed.css sidecar as the last <style> of <head> (its :root:root block outranks the
 * stock :root values Divi prints; preset rules precede the builder CSS, as on the live site). No sidecar, or
 * Divi 4: no-op.
 */
function pp_preview_seed( $html ) {
	global $pp_seed_css;
	$at = ( pp_preview_divi_major() < 5 || '' === trim( $pp_seed_css ) ) ? false : stripos( $html, '</head>' );
	if ( false === $at ) {
		return $html;
	}
	$style = '<style id="pp-token-seed">' . str_ireplace( '</style', '<\/style', $pp_seed_css ) . "</style>\n";
	return substr_replace( $html, $style, $at, 0 );
}

/**
 * &inline=1: make the page self-contained (same as render.php step 4) - local stylesheets
 * (incl. Divi's rel=preload as=style) and scripts are replaced by their file contents, and
 * url(...) in inlined CSS is made absolute. Fonts/images referenced by absolute URL still point
 * at this server; Google Fonts and remote images stay remote.
 */
function pp_preview_inline_assets( $html ) {
	$content_u = untrailingslashit( content_url() );
	$site_u    = untrailingslashit( site_url() );
	$url_to_path = function ( $url ) use ( $content_u, $site_u ) {
		$url = preg_replace( '/[?#].*$/', '', html_entity_decode( $url ) );
		foreach ( array( $content_u => WP_CONTENT_DIR, $site_u => untrailingslashit( ABSPATH ) ) as $u => $d ) {
			if ( 0 === strpos( $url, $u . '/' ) ) {
				$p = $d . substr( $url, strlen( $u ) );
				return is_readable( $p ) ? $p : null;
			}
		}
		return null;
	};
	$abs_css = function ( $css, $base ) use ( $url_to_path ) {
		return preg_replace_callback(
			'/url\(\s*([\'"]?)(?!data:|https?:|\/\/|#)([^\'")]+)\1\s*\)/i',
			function ( $m ) use ( $base, $url_to_path ) {
				// Web fonts (Divi's ETmodules / Font Awesome icon fonts) are embedded so the file still
				// works after the Playground server is gone. .eot/.svg fallbacks are left as URLs.
				$abs  = '/' === $m[2][0] ? $m[2] : trailingslashit( dirname( $base ) ) . $m[2];
				$path = '/' === $m[2][0] ? null : $url_to_path( $abs );
				if ( $path && preg_match( '/\.(woff2?|ttf)$/i', $path, $ext ) && filesize( $path ) < 2 * 1024 * 1024 ) {
					$mime = array( 'woff2' => 'font/woff2', 'woff' => 'font/woff', 'ttf' => 'font/ttf' )[ strtolower( $ext[1] ) ];
					return 'url(data:' . $mime . ';base64,' . base64_encode( file_get_contents( $path ) ) . ')';
				}
				if ( '/' === $m[2][0] ) {
					$p = wp_parse_url( $base );
					return 'url(' . $m[1] . $p['scheme'] . '://' . $p['host'] . ( isset( $p['port'] ) ? ':' . $p['port'] : '' ) . $m[2] . $m[1] . ')';
				}
				return 'url(' . $m[1] . trailingslashit( dirname( $base ) ) . $m[2] . $m[1] . ')';
			},
			$css
		);
	};
	$html = preg_replace_callback(
		'/<link\b[^>]*>/i',
		function ( $m ) use ( $url_to_path, $abs_css ) {
			$tag = $m[0];
			if ( ! preg_match( '/rel=[\'"](stylesheet|preload)[\'"]/i', $tag, $rel ) || ! preg_match( '/href=[\'"]([^\'"]+)[\'"]/i', $tag, $h ) ) {
				return $tag;
			}
			if ( 'preload' === strtolower( $rel[1] ) && ! preg_match( '/as=[\'"]style[\'"]/i', $tag ) ) {
				return $tag;
			}
			$href = html_entity_decode( $h[1] );
			$path = $url_to_path( $href );
			if ( ! $path ) {
				return '<link rel="stylesheet" href="' . esc_attr( $href ) . '" />';
			}
			$media = preg_match( '/media=[\'"]([^\'"]+)[\'"]/i', $tag, $md ) ? ' media="' . esc_attr( $md[1] ) . '"' : '';
			return '<style' . $media . ">\n" . $abs_css( file_get_contents( $path ), preg_replace( '/[?#].*$/', '', $href ) ) . "\n</style>";
		},
		$html
	);
	if ( pp_preview_divi_major() >= 5 ) {
		$html = pp_preview_embed_style_fonts( $html, $url_to_path );
	}
	return preg_replace_callback(
		'/<script\b([^>]*)\bsrc=[\'"]([^\'"]+)[\'"]([^>]*)>\s*<\/script>/i',
		function ( $m ) use ( $url_to_path ) {
			$path = $url_to_path( $m[2] );
			if ( ! $path ) {
				return $m[0];
			}
			$js = str_ireplace( '</script', '<\/script', file_get_contents( $path ) );
			return '<script' . preg_replace( '/\s+(id|defer|async)=[\'"][^\'"]*[\'"]/i', '', $m[1] . $m[3] ) . ">\n" . $js . "\n</script>";
		},
		$html
	);
}

/**
 * Divi 5 (inline=1): its Dynamic CSS and inline styles reference the icon fonts (ETmodules, Font Awesome) by
 * PROTOCOL-RELATIVE URL (//host/wp-content/themes/Divi/core/admin/fonts/...) inside <style> blocks. Opened
 * from disk, //127.0.0.1:9400/... resolves to file://127.0.0.1:9400/... and every icon falls back to a text
 * glyph (measured: blurb icons 48px -> 54px wide, re-wrapping headings). Embeds any local woff/woff2/ttf
 * referenced by an absolute or protocol-relative site URL in any <style> block.
 */
function pp_preview_embed_style_fonts( $html, $url_to_path ) {
	$site  = wp_parse_url( site_url() );
	$embed = function ( $css ) use ( $url_to_path, $site ) {
		return preg_replace_callback(
			'/url\(\s*([\'"]?)((?:https?:)?\/\/[^\'")\s]+\.(woff2?|ttf)(?:[?#][^\'")\s]*)?)\1\s*\)/i',
			function ( $m ) use ( $url_to_path, $site ) {
				$u    = 0 === strpos( $m[2], '//' ) ? $site['scheme'] . ':' . $m[2] : $m[2];
				$path = $url_to_path( $u );
				if ( ! $path || filesize( $path ) >= 2 * 1024 * 1024 ) {
					return $m[0];
				}
				$mime = array( 'woff2' => 'font/woff2', 'woff' => 'font/woff', 'ttf' => 'font/ttf' )[ strtolower( $m[3] ) ];
				return 'url(data:' . $mime . ';base64,' . base64_encode( file_get_contents( $path ) ) . ')';
			},
			$css
		);
	};
	// A strpos walk, not one big /<style>(.*?)<\/style>/s: that regex hits pcre.backtrack_limit on
	// megabyte-sized inlined stylesheets and preg_replace_callback() then returns NULL (an empty page).
	$out = '';
	$pos = 0;
	while ( false !== ( $open = stripos( $html, '<style', $pos ) ) ) {
		$gt    = strpos( $html, '>', $open );
		$close = false === $gt ? false : stripos( $html, '</style>', $gt );
		if ( false === $close ) {
			break;
		}
		$out .= substr( $html, $pos, $gt + 1 - $pos );
		$css  = substr( $html, $gt + 1, $close - $gt - 1 );
		$new  = false !== strpos( $css, '//' ) ? $embed( $css ) : $css;
		$out .= null === $new ? $css : $new;
		$pos  = $close;
	}
	return $out . substr( $html, $pos );
}
