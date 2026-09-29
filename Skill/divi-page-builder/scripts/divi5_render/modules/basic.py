"""Text, Heading, Button and Image (TextModule, HeadingModule, ButtonModule, ImageModule).

Templates are the render_callback output; styles are the generic element style per module.json attribute plus
each module_styles special case:
- Text: `text-align:start` (the text orientation default), body/link/heading fonts on `.et_pb_text_inner`;
- Button: the module's spacing on the wrapper, its padding copied onto `…:hover` (the silent special case the
  spike found), the alignment rules and the icon's `:after` size;
- Image: alignment, force fullwidth, the image wrap's border/box shadow and the radius overflow.
"""
from __future__ import annotations

import re

from .. import coverage
from ..base import Mod, register
from ..css import expand
from ..options import (Element, border_decls, custom_css, element_style, font_decls, overflow_for_radius,
                       _emit)
from ..values import esc_attr, esc_url, get, merge

MODULE_DECO = {k: k for k in ("background", "spacing", "sizing", "border", "boxShadow", "layout")}


def handled_module(extra: dict | None = None) -> dict:
    h = {f"module.decoration.{k}": fam for k, fam in MODULE_DECO.items()}
    h.update({"modulePreset": "*", "groupPreset": "*", "module.advanced.htmlAttributes": "htmlAttributes",
              "module.decoration.attributes": "*", "css": "css", "module.advanced.text": "*"})
    h.update(extra or {})
    return h


def render_attrs(m: Mod) -> dict:
    """The block attrs over the module's default render attributes (what classnames functions see)."""
    return merge(get(m.meta, "defaults") or {}, m.attrs)


def text_classes(ra: dict) -> list:
    """TextClassnames::text_options_classnames (background layout; orientation off for these modules)."""
    out = []
    for bp, states in (get(ra, "module", "advanced", "text", "text") or {}).items():
        for st, v in (states or {}).items():
            color = (v or {}).get("color") if isinstance(v, dict) else None
            if color in ("dark", "light"):
                out.append(f"et_pb_bg_layout_{color}{'' if bp == 'desktop' else '_' + bp}"
                           f"{'' if st == 'value' else '_' + st}")
    return out


def wpautop(text: str) -> str:
    """Enough of WordPress's wpautop for module content: paragraphs, and a newline after block-level closers."""
    text = text.strip()
    if not text:
        return ""
    if not text.startswith("<"):
        text = f"<p>{text}</p>"
    text = re.sub(r"(</(?:p|li|ul|ol|h[1-6]|blockquote)>|<(?:ul|ol)>)\s*", "\\1\n", text)
    return text


# ------------------------------------------------------------------------------------------ text
BODY_FONT_PARTS = {"body": "", "link": " a", "ul": " ul li", "ol": " ol li", "quote": " blockquote"}


@register("text")
def r_text(b, ctx, info):
    m = Mod(ctx, b, "text")
    ra = render_attrs(m)
    element_style(ctx, m.deco(), m.element("module"), overflow_selector=m.oc)
    ctx.css.add(m.oc, ["text-align:start"])
    content = m.element("content")
    sel = content.selector
    cprops = get(m.meta, "module", "attributes", "content", "styleProps") or {}
    handled = {"content.innerContent": "*"}
    for part in ("body", "link"):
        attr = m.a("content", "decoration", "bodyFont", part, "font")
        if attr:
            _emit(ctx, attr, font_decls(ctx), sel + BODY_FONT_PARTS[part], {},
                  get(content.printed, "bodyFont", part, "font"),
                  important=get(cprops, "bodyFont", "important", part, "font") or False)
        handled[f"content.decoration.bodyFont.{part}.font"] = "font"
    for h in ("h1", "h2", "h3", "h4", "h5", "h6"):
        attr = m.a("content", "decoration", "headingFont", h, "font")
        if attr:
            _emit(ctx, attr, font_decls(ctx), f"{sel} {h}", {}, get(content.printed, "headingFont", h, "font"),
                  important=get(cprops, "headingFont", "important", h, "font") or False)
        handled[f"content.decoration.headingFont.{h}.font"] = "font"
    custom_css(ctx, m.a("css") or {}, m.oc)
    coverage.check(ctx, "text", m.attrs, handled_module(handled))
    body = wpautop(m.a("content", "innerContent", "desktop", "value") or "")
    return (f'<div class="{m.classes(text_classes(ra))}"{m.html_attrs()}>'
            f'<div class="et_pb_text_inner">{body}</div></div>')


# ------------------------------------------------------------------------------------------ heading
@register("heading")
def r_heading(b, ctx, info):
    m = Mod(ctx, b, "heading")
    ra = render_attrs(m)
    element_style(ctx, m.deco(), m.element("module"), overflow_selector=m.oc)
    title = m.element("title")
    font_attr = m.a("title", "decoration", "font", "font")
    if font_attr:
        tprops = title.group("font")
        _emit(ctx, font_attr, font_decls(ctx), title.selector, {}, get(title.printed, "font", "font"),
              important=get(tprops, "important", "font") or False)
    custom_css(ctx, m.a("css") or {}, m.oc)
    coverage.check(ctx, "heading", m.attrs,
                   handled_module({"title.innerContent": "*", "title.decoration.font.font": "font"}))
    level = get(ra, "title", "decoration", "font", "font", "desktop", "value", "headingLevel") or "h1"
    if level not in ("h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span"):
        level = "h1"
    text = m.a("title", "innerContent", "desktop", "value") or ""
    return (f'<div class="{m.classes(text_classes(ra))}"{m.html_attrs()}><div class="et_pb_heading_container">'
            f'<{level} class="et_pb_module_header">{text}</{level}></div></div>')


# ------------------------------------------------------------------------------------------ button
def supported_groups(m: Mod, attr_name: str, deco: dict) -> dict:
    """ButtonModule::_sanitize_button_decoration_attrs: only the decoration groups module.json declares for the
    element, minus the `<group>Group` fields its button component marks `render: false` (the Button's own
    spacing and box shadow: Divi prints nothing for them)."""
    settings = get(m.meta, "module", "attributes", attr_name, "settings", "decoration") or {}
    fields = get(settings, "button", "component", "props", "fields") or {}
    excluded = {k[:-5] for k, v in fields.items() if k.endswith("Group") and isinstance(v, dict) and v.get("render") is False}
    return {k: v for k, v in deco.items() if k in settings and k not in excluded}


ALIGN_MARGINS = {"center": ("auto", "auto"), "left": ("0", "auto"), "right": ("auto", "0")}


@register("button")
def r_button(b, ctx, info):
    m = Mod(ctx, b, "button")
    ra = render_attrs(m)
    wrap = f"{m.oc}_wrapper"
    mod_el = m.element("module", wrapperSelector=wrap)
    # ButtonModule::module_styles: the module padding also goes on `wrapper button:hover` (a special case the
    # module.json styleProps don't carry).
    sp = dict(mod_el.props.get("spacing") or {})
    sp["propertySelectors"] = {"desktop": {"value": {"margin": wrap,
                                                     "padding": f"{wrap} {m.oc}, {wrap} {m.oc}:hover"}}}
    sp["important"] = True
    mod_el.props["spacing"] = sp
    element_style(ctx, m.deco(), mod_el, overflow_selector=m.oc)
    al = m.a("module", "advanced", "alignment", "desktop", "value")
    if al in ALIGN_MARGINS:
        ctx.css.add(wrap, [f"text-align:{al}"])
        ml, mr = ALIGN_MARGINS[al]
        ctx.css.add(f"{wrap} {m.oc}", [f"text-align:{al}", f"margin-left:{ml}", f"margin-right:{mr}"])
    bmeta = get(m.meta, "module", "attributes", "button") or {}
    bsel = expand(bmeta.get("selector", "{{selector}}"), m.oc)
    bprops = m.element("button").props
    bdeco = supported_groups(m, "button", m.deco("button"))
    bel = Element(bsel, {k: v for k, v in bprops.items() if k != "selector"})
    bel.props.setdefault("sizing", {})["important"] = {"desktop": {"value": {"max-width": True}}}
    element_style(ctx, bdeco, bel, groups=("background", "font", "spacing", "sizing", "border", "boxShadow"))
    if get(bdeco, "button", "desktop", "value", "enable") == "on":
        ctx.css.add(f"{bsel}:after", ["font-size:1.6em"])
    custom_css(ctx, m.a("css") or {}, m.oc)
    coverage.check(ctx, "button", m.attrs, handled_module({
        "button.innerContent": "*", "button.decoration.background": "background",
        "button.decoration.font.font": "font", "button.decoration.border": "border",
        "button.decoration.spacing": "spacing", "button.decoration.boxShadow": "boxShadow",
        "button.decoration.sizing": "sizing", "button.decoration.button": "button",
        "module.advanced.alignment": "*"}))
    inner = m.a("button", "innerContent", "desktop", "value") or {}
    link = inner.get("linkUrl") or ""
    text = inner.get("text")
    text = esc_attr(text) if text else esc_url(link)
    target = ' target="_blank"' if inner.get("linkTarget") == "on" else ""
    rel = inner.get("rel")
    rel_attr = f' rel="{esc_attr(" ".join(rel))}"' if isinstance(rel, list) and rel else ""
    if not text and not link:
        return ""
    presets = [c for c in m.classes([]).split() if c.startswith("preset--")]
    wk = " ".join(["et_pb_module", "et_pb_button_module_wrapper", f"{m.order_class}_wrapper",
                   *(p + "_wrapper" for p in presets)])
    kl = m.classes(text_classes(ra))
    return (f'<div class="{wk}"><a class="{kl}"{m.html_attrs()} href="{esc_url(link)}"{target}{rel_attr}>'
            f'{text}</a></div>')


# ------------------------------------------------------------------------------------------ image
@register("image")
def r_image(b, ctx, info):
    m = Mod(ctx, b, "image")
    ra = render_attrs(m)
    oc = m.oc
    element_style(ctx, m.deco(), m.element("module"), overflow_selector=oc)
    adv_spacing = m.a("module", "advanced", "spacing") or {}
    if adv_spacing:
        _emit(ctx, adv_spacing, _margin_padding, oc, {},
              important={"desktop": {"value": {"margin": True}}})
    align = m.a("module", "advanced", "align")
    if align:
        _emit(ctx, align, _image_align, f"{oc}.et_pb_image", {})
    sizing = m.a("module", "advanced", "sizing") or {}
    if sizing:
        _emit(ctx, sizing, _image_sizing, oc, {"important": {"desktop": {"value": {"margin-left": True,
                                                                                    "margin-right": True}}}})
        _emit(ctx, sizing, _fullwidth_module, oc, {})
        _emit(ctx, sizing, _fullwidth_image, f"{oc} img, {oc} .et_pb_image_wrap", {})
    img_deco = m.deco("image")
    if img_deco.get("border"):
        _emit(ctx, img_deco["border"], border_decls, f"{oc} .et_pb_image_wrap", {})
        overflow_for_radius(ctx, img_deco["border"], f"{oc} .et_pb_image_wrap")
        _emit(ctx, img_deco["border"], _radius_inherit, f"{oc} .et_pb_image_wrap img", {})
    if img_deco.get("boxShadow"):
        from ..options import box_shadow_decls, normalize_box_shadow
        _emit(ctx, normalize_box_shadow(img_deco["boxShadow"]), box_shadow_decls, f"{oc} .et_pb_image_wrap", {})
    custom_css(ctx, m.a("css") or {}, oc)
    coverage.check(ctx, "image", m.attrs, handled_module({
        "image.innerContent": "*", "image.advanced.lightbox": "*", "module.advanced.align": "*",
        "module.advanced.sizing": "imageSizing", "module.advanced.spacing": "*",
        "image.decoration.border": "border", "image.decoration.boxShadow": "boxShadow"}), targets=("main", "image"))
    ic = m.a("image", "innerContent", "desktop", "value") or {}
    src = ic.get("src") or ""
    show_bottom = get(ra, "module", "advanced", "spacing", "desktop", "value", "showBottomSpace") or "on"
    own = []
    for bp in ("tablet", "phone"):
        if get(ra, "module", "advanced", "spacing", bp, "value", "showBottomSpace") == "on":
            own.append(f"et_pb_image_bottom_space_{bp}")
    if show_bottom == "off":
        own.append("et_pb_image_sticky")
    for bp in ("tablet", "phone"):
        if get(ra, "module", "advanced", "spacing", bp, "value", "showBottomSpace") == "off":
            own.append(f"et_pb_image_sticky_{bp}")
    lightbox = get(ra, "image", "advanced", "lightbox", "desktop", "value") == "on"
    url = ic.get("linkUrl") or ""
    use_overlay = get(ra, "image", "advanced", "overlay", "desktop", "value", "use") == "on"
    if use_overlay and (lightbox or url):
        own.append("et_pb_has_overlay")
    if not src:
        return f'<div class="{m.classes(own)}"{m.html_attrs()}></div>'
    img_attrs = {"src": esc_url(src)}
    if ic.get("alt"):
        img_attrs["alt"] = esc_attr(ic["alt"])
    if ic.get("titleText"):
        img_attrs["title"] = esc_attr(ic["titleText"])
    for name, value in m.custom_attributes("image"):
        img_attrs[name] = esc_attr(value)
    img = "<img decoding=\"async\"" + "".join(f' {k}="{v}"' for k, v in img_attrs.items()) + " />"
    wrap =f'<span class="et_pb_image_wrap">{img}</span>'
    if lightbox:
        title = f' title="{esc_attr(ic["alt"])}"' if ic.get("alt") else ""
        body = f'<a href="{esc_url(src)}"{title} class="et_pb_lightbox_image">{wrap}</a>'
    elif url:
        target = ' target="_blank"' if ic.get("linkTarget") == "on" else ""
        rel = ic.get("rel")
        rel_attr = f' rel="{esc_attr(" ".join(rel))}"' if isinstance(rel, list) and rel else ""
        body = f'<a href="{esc_url(url)}"{target}{rel_attr}>{wrap}</a>'
    else:
        body = wrap
    return f'<div class="{m.classes(own)}"{m.html_attrs()}>{body}</div>'


def _margin_padding(v, default, bp, state, attr):
    out = []
    for kind in ("margin", "padding"):
        box = (v.get(kind) or {}) if isinstance(v, dict) else {}
        for side in ("top", "right", "bottom", "left"):
            if box.get(side) not in (None, ""):
                out.append((f"{kind}-{side}", box[side]))
    return out


def _image_align(v, default, bp, state, attr):
    ml, mr = {"left": ("0", "auto"), "center": ("auto", "auto"), "right": ("auto", "0")}.get(v, ("0", "auto"))
    ai = {"left": "flex-start", "center": "center", "right": "flex-end"}.get(v, "flex-start")
    return [("text-align", v if v in ("left", "center", "right") else "left"), ("margin-left", ml),
            ("margin-right", mr), ("align-items", ai)] if v else []


def _image_sizing(v, default, bp, state, attr):
    if not isinstance(v, dict):
        return []
    out = []
    for key, prop in (("width", "width"), ("maxWidth", "max-width"), ("minHeight", "min-height"),
                      ("height", "height"), ("maxHeight", "max-height")):
        if v.get(key) not in (None, ""):
            out.append((prop, v[key]))
    al = v.get("alignment")
    if al in ALIGN_MARGINS:
        ml, mr = ALIGN_MARGINS[al]
        out += [("margin-left", ml), ("margin-right", mr)]
    return out


def _radius_inherit(v, default, bp, state, attr):
    """ImageModule::image_border_radius_inherit_style_declaration."""
    if not isinstance(v, dict):
        return []
    for side in ("all", "top", "right", "bottom", "left"):
        w = get(v, "styles", side, "width")
        try:
            if w not in (None, "") and float(re.match(r"-?[\d.]*", str(w)).group(0) or 0) != 0:
                return []
        except ValueError:
            pass
    radius = v.get("radius")
    if not isinstance(radius, dict):
        return []
    for k, x in radius.items():
        if k == "sync" or x in (None, ""):
            continue
        try:
            if float(re.match(r"-?[\d.]*", str(x)).group(0) or 0) != 0:
                return [("border-radius", "inherit")]
        except ValueError:
            return [("border-radius", "inherit")]
    return []


def _fullwidth_module(v, default, bp, state, attr):
    return [("width", "100%")] if isinstance(v, dict) and v.get("forceFullwidth") == "on" else []


def _fullwidth_image(v, default, bp, state, attr):
    if isinstance(v, dict) and v.get("forceFullwidth") == "on":
        return [("width", "100%"), ("max-width", "100%", True)]
    return []
