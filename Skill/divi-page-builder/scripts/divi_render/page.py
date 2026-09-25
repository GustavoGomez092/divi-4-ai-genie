"""Document shell around the builder markup, and the coverage report.

The shell stands in for WordPress: Divi's static CSS and front-end JS from the cached theme, stock
customizer CSS, the Google Fonts link for the fonts the page uses, Divi's JS globals, and a stub
of the default header and footer (no real menus or Theme Builder layouts without WordPress).
"""
from __future__ import annotations

from .assets import JQUERY_CDN, Theme, find_jquery
from .base import Ctx
from .values import esc

BODY_CLASSES = ("page-template-default page wp-theme-Divi et_pb_button_helper_class et_fixed_nav et_show_nav "
                "et_primary_nav_dropdown_animation_fade et_secondary_nav_dropdown_animation_fade et_header_style_left "
                "et_pb_footer_columns4 et_cover_background et_pb_gutter et_pb_gutters3 et_pb_pagebuilder_layout "
                "et_no_sidebar et_divi_theme et-db")
# Stock customizer output for default theme settings (would come from a settings bundle).
STOCK_CUSTOMIZER_CSS = ("body,.et_pb_column_1_2 .et_quote_content blockquote cite,.et_pb_column_1_2 .et_link_content a.et_link_main_url,"
                        ".et_pb_column_1_3 .et_quote_content blockquote cite,.et_pb_column_3_8 .et_quote_content blockquote cite,"
                        ".et_pb_column_1_4 .et_quote_content blockquote cite,.et_pb_blog_grid .et_quote_content blockquote cite,"
                        ".et_pb_column_1_3 .et_link_content a.et_link_main_url,.et_pb_column_3_8 .et_link_content a.et_link_main_url,"
                        ".et_pb_column_1_4 .et_link_content a.et_link_main_url,.et_pb_blog_grid .et_link_content a.et_link_main_url,"
                        "body .et_pb_bg_layout_light .et_pb_post p,body .et_pb_bg_layout_dark .et_pb_post p{font-size:14px}"
                        ".et_pb_slide_content,.et_pb_best_value{font-size:15px}@media only screen and (min-width:1350px){"
                        ".et_pb_row{padding:27px 0}.et_pb_section{padding:54px 0}.single.et_pb_pagebuilder_layout.et_full_width_page "
                        ".et_post_meta_wrapper{padding-top:81px}.et_pb_fullwidth_section{padding:0}}")
HEADER = """<header id="main-header" data-height-onload="66">
			<div class="container clearfix et_menu_container">
				<div class="logo_container"><span class="logo_helper"></span>
					<a href="#"><img src="{logo}" width="93" height="43" alt="{site}" id="logo" data-height-percentage="54" /></a>
				</div>
				<div id="et-top-navigation" data-height="66" data-fixed-height="40">
					<nav id="top-menu-nav"><ul id="top-menu" class="nav">{menu}</ul></nav>
					<div id="et_top_search"><span id="et_search_icon"></span></div>
					<div id="et_mobile_nav_menu"><div class="mobile_nav closed"><span class="select_page">Select Page</span><span class="mobile_menu_bar mobile_menu_bar_toggle"></span></div></div>
				</div>
			</div>
		</header>"""
FOOTER = """<footer id="main-footer"><div id="footer-bottom"><div class="container clearfix">
<div id="footer-info">Designed by <a href="https://www.elegantthemes.com" title="Premium WordPress Themes">Elegant Themes</a> | Powered by <a href="https://www.wordpress.org">WordPress</a></div>
</div></div></footer>"""
JS_GLOBALS = """var DIVI = {"item_count":"%d Item","items_count":"%d Items"};
var et_builder_utils_params = {"condition":{"diviTheme":true,"extraTheme":false},"scrollLocations":["app","top"],"builderScrollLocations":{"desktop":"app","tablet":"app","phone":"app"},"onloadScrollLocation":"app","builderType":"fe"};
var et_frontend_scripts = {"builderCssContainerPrefix":"#et-boc","builderCssLayoutPrefix":"#et-boc .et-l"};
var et_pb_custom = {"ajaxurl":"","images_uri":"","builder_images_uri":"","et_frontend_nonce":"","subscription_failed":"","et_ab_log_nonce":"","fill_message":"","contact_error_message":"","invalid":"","captcha":"","prev":"Prev","previous":"Previous","next":"Next","wrong_captcha":"","wrong_checkbox":"","ignore_waypoints":"no","is_divi_theme_used":"1","widget_search_selector":".widget_search","ab_tests":[],"is_ab_testing_active":"","page_id":"0","unique_test_id":"","ab_bounce_rate":"5","is_cache_plugin_active":"no","is_shortcode_tracking":"","tinymce_uri":"","accent_color":"#7EBEC5","waypoints_options":[]};
var et_pb_box_shadow_elements = [];
var et_pb_sticky_elements = [];"""
MENU = '<li><a href="#">Home</a></li><li><a href="#">Sample Page</a></li>'


def google_fonts_link(ctx: Ctx) -> str:
    gf = ctx.theme.google_fonts()
    fams = [f.replace(" ", "+") + ":" + ",".join(gf[f]["variants"]) for f in sorted(ctx.fonts) if f in gf]
    if not fams:
        return ""
    return (f"<link rel='stylesheet' id='et-builder-googlefonts-cached-css' href='https://fonts.googleapis.com/css?family="
            f"{'|'.join(fams)}&#038;subset=latin,latin-ext&#038;display=swap' media='all' />")


def scripts_html(theme: Theme) -> str:
    jq_path = find_jquery()
    jq = (f"<script>{jq_path.read_text(encoding='utf-8', errors='replace')}</script>" if jq_path
          else f'<script src="{JQUERY_CDN}"></script>')
    scripts = "".join(f"<script>{js}</script>\n" for js in theme.scripts())
    return f"{jq}\n<script>{JS_GLOBALS}</script>\n{scripts}"


def document(ctx: Ctx, builder_html: str, builder_css: str, title: str, with_js: bool) -> str:
    theme = ctx.theme
    etl = (f'<div class="et-l et-l--post">\n\t\t\t<div class="et_builder_inner_content et_pb_gutters3">\n\t\t'
           f'{builder_html}\t\t</div>\n\t</div>')
    header = HEADER.format(logo=theme.url("images/logo.png"), site="Preview", menu=MENU)
    js = scripts_html(theme) if with_js else ""
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0" />
<title>{esc(title)}</title>
<script type="text/javascript">document.documentElement.className = 'js';</script>
<link rel='stylesheet' id='et-divi-open-sans-css' href='https://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800&#038;subset=latin,latin-ext&#038;display=swap' media='all' />
<style id="divi-style-css-inlined" media="all">{theme.static_css()}</style>
<style id="et-divi-customizer-global-cached-inline-styles">{STOCK_CUSTOMIZER_CSS}</style>
{google_fonts_link(ctx)}
<style id="et-builder-module-design-python-inline-styles">{builder_css}</style>
</head>
<body class="{BODY_CLASSES}">
	<div id="page-container">
		{header}
		<div id="et-main-area">
<div id="main-content">
				<article id="post-0" class="post-0 page type-page status-publish hentry">
					<div class="entry-content">
					{etl}
					</div>
				</article>
</div>
{FOOTER}
		</div>
	</div>
{js}
</body>
</html>
"""


def coverage_report(ctx: Ctx) -> dict:
    """Per module type: count, attributes set, attributes never read ('ignored'); plus the
    unsupported modules and features the --exact preview can show (placeholders, section
    dividers, patterns...) and, apart from them, what needs the live site's data (posts, menus,
    media, comments, widgets, oEmbed), which neither preview can show."""
    by_tag: dict = {}
    for c in ctx.coverage:
        t = by_tag.setdefault(c["tag"], {"count": 0, "supported": c["supported"], "attrs": 0, "ignored": {}})
        t["count"] += 1
        t["attrs"] += c["attrs"]
        for a in c["ignored"]:
            t["ignored"][a] = t["ignored"].get(a, 0) + 1
    total = sum(c["attrs"] for c in ctx.coverage)
    ign = sum(len(c["ignored"]) for c in ctx.coverage)
    return {"modules": len(ctx.coverage), "unsupported_modules": dict(ctx.unsupported),
            "needs_site_data": dict(ctx.site_data),
            "attrs_total": total, "attrs_ignored": ign,
            "attr_coverage_pct": round(100 * (total - ign) / total, 1) if total else 100.0,
            "by_tag": by_tag}
