"""The document shell around the builder markup: what WordPress and Divi 5 print around a page.

- Divi 5's static stylesheet (style-static.min.css) from the cached theme, through divi_render.assets.Theme's
  delivery modes (data: URIs for standalone files, /__divi/ URLs when served; never file://);
- the stock Theme Customizer CSS and the `et-vb-global-data` font variables Divi prints on a stock site;
- the Google Fonts the page uses: one `css?family=` link for static fonts and one `css2?family=` link per
  variable font (a wght axis), as Divi 5 prints them (the spike's 390 px H1 wrapped without them);
- the client's design system from tokens.json exactly as the Playground preview seeds it (preview.seed_css:
  global colours and variables as `:root:root{…}`, plus the recovered preset rules), so both previews show the
  same presets.
"""
from __future__ import annotations

from .values import esc_attr

STOCK_CUSTOMIZER_CSS = ("@media only screen and (min-width:1350px){.et_block_row{padding:27px 0}"
                        ".et_pb_section{padding:54px 0}.single.et_pb_pagebuilder_layout.et_full_width_page "
                        ".et_post_meta_wrapper{padding-top:81px}.et_pb_fullwidth_section{padding:0}}")
GLOBAL_FONTS_CSS = (":root{--et_global_heading_font: 'Open Sans';--et_global_body_font: 'Open Sans';"
                    "--et_global_heading_font_weight: 500;--et_global_body_font_weight: 500;"
                    "--et_global_body_font_size: 14px;--et_global_body_font_height: 1.7em;}"
                    "body{line-height:var(--et_global_body_font_height);font-size:var(--et_global_body_font_size);}")
BODY_CLASSES = ("page-template-default page et_pb_button_helper_class et_fixed_nav et_show_nav "
                "et_primary_nav_dropdown_animation_fade et_secondary_nav_dropdown_animation_fade et_header_style_left "
                "et_pb_footer_columns4 et_cover_background et_pb_gutter et_pb_gutters3 et_pb_pagebuilder_layout "
                "et_no_sidebar et_divi_theme et-db")
OPEN_SANS = ("<link rel='stylesheet' id='et-divi-open-sans-css' href='https://fonts.googleapis.com/css?family=Open+Sans:"
             "300italic,400italic,600italic,700italic,800italic,400,300,600,700,800&#038;subset=latin,latin-ext"
             "&#038;display=swap' media='all' />")


def google_fonts_links(ctx) -> str:
    gf = ctx.theme.google_fonts()
    fams = sorted(f for f in ctx.fonts if f in gf)
    static = [f for f in fams if not gf[f].get("axes")]
    out = ""
    if static:
        out += ("<link rel='stylesheet' id='et-builder-googlefonts-css' href='https://fonts.googleapis.com/css?family="
                + "|".join(f.replace(" ", "+") + ":" + ",".join(gf[f]["variants"]) for f in static)
                + "&#038;subset=latin,latin-ext&#038;display=swap' media='all' />")
    for f in fams:
        axes = {a["tag"]: a for a in gf[f].get("axes") or []}
        if "wght" in axes:
            r = f"{axes['wght']['start']}..{axes['wght']['end']}"
            spec = f"ital,wght@0,{r};1,{r}" if "italic" in gf[f]["variants"] else f"wght@{r}"
            out += (f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family={f.replace(' ', '+')}:"
                    f"{spec}&#038;subset=latin%2Clatin-ext&#038;display=swap' media='all' />")
    return out


def token_css(tokens: dict) -> str:
    """preview.seed_css(tokens): the same seed the Playground preview adds as <style id="pp-token-seed">."""
    if not tokens:
        return ""
    from preview import seed_css  # the skill's preview.py (stdlib only); imported lazily, it imports this package
    return seed_css(tokens).replace("</style", "<\\/style")


def document(ctx, builder_html: str, builder_css: str, title: str = "Preview") -> str:
    theme = ctx.theme
    seed = token_css(ctx.tokens)
    etl = (f'<div class="et-l et-l--post">\n\t\t\t<div class="et_builder_inner_content">\n\t\t{builder_html}\n\n'
           f'\t\t</div>\n\t</div>')
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0" />
<title>{esc_attr(title)}</title>
{OPEN_SANS}
<style id="pp-divi5-static-css" media="all">{theme.static_css()}</style>
<style id="et-divi-customizer-global-cached-inline-styles">{STOCK_CUSTOMIZER_CSS}</style>
{google_fonts_links(ctx)}
<style class="et-vb-global-data et-vb-global-fonts">{GLOBAL_FONTS_CSS}</style>
<style id="et-builder-module-design-python5-inline-styles">{builder_css}</style>
{f'<style id="pp-token-seed">{seed}</style>' if seed else ''}
</head>
<body class="{BODY_CLASSES}">
<div id="page-container"><div id="et-main-area"><div id="main-content"><article class="page type-page"><div class="entry-content">
{etl}
</div></article></div></div></div>
</body>
</html>
"""
