"""Generic option groups: the ElementStyle port.

element_style() styles one element (a module's `module`, `title`, `button`, `image`… attribute) the way Divi 5's
ElementStyle::style walks its decoration groups, in its order: background, font, bodyFont/headingFont (callers),
spacing, sizing, border, boxShadow, then transition for the hovered properties. Each group is a declaration
function (a port of the StyleLibrary one) run through css.statements(), which handles breakpoints, hover,
important flags and propertySelectors from the element's module.json styleProps.

Values equal to the module's default printed style attributes (module-default-printed-style-attributes.json)
are left out: Divi's static CSS already prints them.
"""
from __future__ import annotations

import re

from .css import expand, statements
from .values import attr_value, get

POSITIONS = {"center": "center", "top_left": "left top", "top_center": "center top", "top_right": "right top",
             "center_left": "left center", "center_right": "right center", "bottom_left": "left bottom",
             "bottom_center": "center bottom", "bottom_right": "right bottom"}
BOX_SHADOW_PRESETS = {
    "preset1": {"horizontal": "0px", "vertical": "2px", "blur": "18px", "spread": "0px", "position": "outer",
                "color": "rgba(0,0,0,0.3)"},
    "preset2": {"horizontal": "6px", "vertical": "6px", "blur": "18px", "spread": "0px", "position": "outer",
                "color": "rgba(0,0,0,0.3)"},
    "preset3": {"horizontal": "0px", "vertical": "12px", "blur": "18px", "spread": "-6px", "position": "outer",
                "color": "rgba(0,0,0,0.3)"},
    "preset4": {"horizontal": "10px", "vertical": "10px", "blur": "0px", "spread": "0px", "position": "outer",
                "color": "rgba(0,0,0,0.3)"},
    "preset5": {"horizontal": "0px", "vertical": "6px", "blur": "0px", "spread": "10px", "position": "outer",
                "color": "rgba(0,0,0,0.3)"},
    "preset6": {"horizontal": "0px", "vertical": "0px", "blur": "18px", "spread": "0px", "position": "inner",
                "color": "rgba(0,0,0,0.3)"},
    "preset7": {"horizontal": "10px", "vertical": "10px", "blur": "0px", "spread": "0px", "position": "inner",
                "color": "rgba(0,0,0,0.3)"},
}
FONT_KEYS = (("family", "font-family"), ("weight", "font-weight"), ("style", "font-style"),
             ("capitalization", "text-transform"), ("color", "color"), ("size", "font-size"),
             ("letterSpacing", "letter-spacing"), ("lineHeight", "line-height"), ("textAlign", "text-align"))


class Element:
    """What element_style needs to know about one element: its selector and the styleProps of its
    module.json attribute (already expanded for the module's order class), plus per-call overrides."""

    def __init__(self, selector: str, props: dict | None = None, printed: dict | None = None):
        self.selector = selector
        self.props = props or {}
        self.printed = printed or {}

    def group(self, name: str) -> dict:
        return self.props.get(name) or {}

    def group_selector(self, name: str) -> str:
        return self.group(name).get("selector") or self.selector


# ------------------------------------------------------------------------------------------ declarations
def _gradient(ctx, g) -> str:
    stops = ",".join(f"{ctx.values.resolve(st.get('color'))} {st.get('position')}%" for st in g.get("stops") or [])
    kind = g.get("type", "linear")
    if kind == "linear":
        return f"linear-gradient({g.get('direction', '180deg')},{stops})"
    return f"radial-gradient(circle at {g.get('directionRadial', 'center')},{stops})"


def background_decls(ctx):
    def fn(v, default, bp, state, attr):
        if not isinstance(v, dict):
            return []
        out = []
        if v.get("color"):
            out.append(("background-color", v["color"]))
        img, g = v.get("image") or {}, v.get("gradient") or {}
        layers = []
        if g.get("enabled") == "on":
            layers.append(_gradient(ctx, g))
        if img.get("url"):
            out.append(("background-size", img.get("size", "cover")))
            out.append(("background-position", POSITIONS.get(img.get("position", "center"), img.get("position"))))
            out.append(("background-repeat", img.get("repeat", "no-repeat")))
            url = "url('" + img["url"] + "')"
            layers = layers + [url] if g.get("overlaysImage") == "on" or not layers else [url] + layers
            out.append(("background-image", ",".join(layers)))
        elif layers:
            out.append(("background-image", ",".join(layers)))
        return out
    return fn


def spacing_decls(v, default, bp, state, attr):
    out = []
    for kind in ("margin", "padding"):
        box = (v or {}).get(kind) or {} if isinstance(v, dict) else {}
        for side in ("top", "right", "bottom", "left"):
            if box.get(side) not in (None, ""):
                out.append((f"{kind}-{side}", box[side]))
    return out


def _custom_width(v, attr, bp, state) -> bool:
    eff = attr_value(attr, bp, state, "getAndInheritAll", v) or {}
    for k in ("width", "maxWidth", "minWidth"):
        val = v.get(k) if k in v else eff.get(k)
        if val and str(val).strip().lower() not in ("auto", "100%", "none"):
            return True
    return False


def sizing_decls(align: bool = True):
    def fn(v, default, bp, state, attr):
        if not isinstance(v, dict):
            return []
        out = []
        for key, prop in (("width", "width"), ("maxWidth", "max-width"), ("minWidth", "min-width")):
            if v.get(key) not in (None, "") and v.get(key) != default.get(key):
                out.append((prop, v[key]))
        al = v.get("alignment") if align else None
        if al == "left":
            out += [("margin-left", "0"), ("margin-right", "auto")]
        elif al == "center" and _custom_width(v, attr, bp, state):
            out += [("margin-left", "auto"), ("margin-right", "auto")]
        elif al == "right":
            out += [("margin-left", "auto"), ("margin-right", "0")]
        for key, prop in (("minHeight", "min-height"), ("height", "height"), ("maxHeight", "max-height")):
            if v.get(key) not in (None, "") and v.get(key) != default.get(key):
                out.append((prop, v[key]))
        return out
    return fn


def border_decls(v, default, bp, state, attr):
    """StyleLibrary Border::style_declaration."""
    if not isinstance(v, dict):
        return []
    out = []
    radius = v.get("radius")
    if isinstance(radius, dict):
        for k, prop in (("topLeft", "border-top-left-radius"), ("topRight", "border-top-right-radius"),
                        ("bottomRight", "border-bottom-right-radius"), ("bottomLeft", "border-bottom-left-radius")):
            if radius.get(k) not in (None, ""):
                out.append((prop, radius[k]))
    styles = v.get("styles")
    if isinstance(styles, dict) and styles:
        alls = styles.get("all") or {}
        dstyles = (default or {}).get("styles") if isinstance(default, dict) else None
        for side in ("all", "top", "right", "bottom", "left"):
            if side not in styles:
                continue
            s = styles[side] or {}
            is_all = side == "all"
            wp, cp, sp = (("border-width", "border-color", "border-style") if is_all else
                          (f"border-{side}-width", f"border-{side}-color", f"border-{side}-style"))
            width, color, style = s.get("width"), s.get("color"), s.get("style")
            if width and (is_all or width != alls.get("width")):
                out.append((wp, width))
            if color:
                if is_all or color != alls.get("color"):
                    out.append((cp, color))
            elif width and (is_all or not alls.get("color")):
                dc = get(dstyles, side, "color") if dstyles else None
                if dc is None and dstyles is not None:
                    dc = get(dstyles, "all", "color")
                out.append((cp, dc or "#333"))
            if style:
                if is_all or style != alls.get("style"):
                    out.append((sp, style))
            elif width and (is_all or not alls.get("style")):
                ds = get(dstyles, side, "style") if dstyles else None
                if ds is None and dstyles is not None:
                    ds = get(dstyles, "all", "style")
                out.append((sp, ds or "solid"))
    return out


def box_shadow_value(v: dict) -> str:
    """StyleLibrary BoxShadow::value (v already merged with its preset by normalize_box_shadow)."""
    style = v.get("style") or "none"
    if style == "none":
        return ""
    bs = {**BOX_SHADOW_PRESETS.get(style, {}), **{k: x for k, x in v.items() if isinstance(x, str) and x != ""}}
    pos = "inset " if bs.get("position") == "inner" else ""
    spread = " " + bs["spread"] if bs.get("spread") else ""
    color = " " + bs["color"] if bs.get("color") else ""
    return f"{pos}{bs.get('horizontal', '')} {bs.get('vertical', '')} {bs.get('blur', '')}{spread}{color}"


def normalize_box_shadow(attr: dict) -> dict:
    """BoxShadowStyle::normalize_attr: every breakpoint/state merged over the desktop style's preset."""
    style = get(attr, "desktop", "value", "style") or "none"
    preset = BOX_SHADOW_PRESETS.get(style, {})
    out = {}
    for bp, states in attr.items():
        if not isinstance(states, dict):
            continue
        out[bp] = {}
        for st, vals in states.items():
            if not isinstance(vals, dict):
                continue
            src = vals if (bp == "desktop" and st == "value") else (
                attr_value(attr, bp, st, "getAndInheritAll") or {})
            clean = {k: x for k, x in src.items() if isinstance(x, (dict, list)) or x not in ("", None)}
            out[bp][st] = {**preset, **clean}
    return out


def box_shadow_decls(v, default, bp, state, attr):
    if not isinstance(v, dict):
        return []
    val = box_shadow_value(v)
    return [("box-shadow", val)] if val else []


def font_family(ctx, fam: str) -> str:
    fam = ctx.values.resolve(fam)
    if fam.startswith("var("):
        return fam
    ctx.fonts.add(fam)
    cat = (ctx.theme.google_fonts().get(fam) or {}).get("category", "sans-serif")
    stack = {"serif": "Georgia,\"Times New Roman\",serif", "monospace": "monospace",
             "handwriting": "cursive", "display": "fantasy"}.get(cat, "Helvetica,Arial,Lucida,sans-serif")
    return f"'{fam}',{stack}"


def font_decls(ctx):
    def fn(v, default, bp, state, attr):
        if not isinstance(v, dict):
            return []
        out = []
        for key, prop in FONT_KEYS:
            val = v.get(key)
            if val in (None, "") or val == default.get(key):
                continue
            if key == "family":
                out.append((prop, font_family(ctx, val)))
                continue
            if key == "style":
                styles = val if isinstance(val, list) else [val]
                if "italic" in styles:
                    out.append(("font-style", "italic"))
                if "uppercase" in styles:
                    out.append(("text-transform", "uppercase"))
                if "capitalize" in styles:
                    out.append(("font-variant", "small-caps"))
                lines = [x for x in ("underline", "line-through")
                         if x in styles or (x == "line-through" and "strikethrough" in styles)]
                if lines:
                    out += [("text-decoration-line", " ".join(lines), False), ("text-decoration-style", "solid", False)]
                continue
            out.append((prop, val))
        return out
    return fn


# ------------------------------------------------------------------------------------------ groups
def _emit(ctx, attr, fn, selector, props: dict, printed: dict | None = None, hovered: list | None = None,
          important=None, **kw):
    """One group through the statement engine; `hovered` collects the properties a hover state printed."""
    imp = props.get("important", False) if important is None else important
    decls_seen: list = []

    def wrapped(v, default, bp, state, a):
        ds = fn(v, default, bp, state, a)
        ds = [(d[0], ctx.values.resolve(d[1]), *d[2:]) for d in ds]
        if state == "hover":
            decls_seen.extend(d[0] for d in ds)
        return ds

    statements(ctx, attr, wrapped, selector=selector, selectors=props.get("selectors"), important=imp,
               property_selectors=props.get("propertySelectors"), printed=printed, **kw)
    if hovered is not None:
        hovered.extend(decls_seen)


def element_style(ctx, deco: dict, el: Element, groups=None, transition: bool = True, sizing_align: bool = True,
                  overflow_selector: str | None = None) -> list:
    """ElementStyle::style for `deco` (an element's decoration attrs). Returns the hovered CSS properties."""
    deco = deco if isinstance(deco, dict) else {}
    groups = groups or ("background", "font", "spacing", "sizing", "border", "boxShadow")
    hovered: list = []
    printed = el.printed
    if "background" in groups and deco.get("background"):
        _emit(ctx, deco["background"], background_decls(ctx), el.group_selector("background"), el.group("background"),
              get(printed, "background"), hovered)
    if "font" in groups and isinstance(deco.get("font"), dict) and deco["font"].get("font"):
        fprops = el.group("font")
        _emit(ctx, deco["font"]["font"], font_decls(ctx), fprops.get("selector") or el.selector,
              {**fprops, "important": get(fprops, "important", "font") or False},
              get(printed, "font", "font"), hovered)
    if "spacing" in groups and deco.get("spacing"):
        _emit(ctx, deco["spacing"], spacing_decls, el.group_selector("spacing"), el.group("spacing"),
              get(printed, "spacing"), hovered)
    if "sizing" in groups and deco.get("sizing"):
        _emit(ctx, deco["sizing"], sizing_decls(sizing_align), el.group_selector("sizing"), el.group("sizing"),
              get(printed, "sizing"), hovered)
    if "border" in groups and deco.get("border"):
        _emit(ctx, deco["border"], border_decls, el.group_selector("border"), el.group("border"),
              get(printed, "border"), hovered)
        if overflow_selector is not None:
            overflow_for_radius(ctx, deco["border"], overflow_selector)
    if "boxShadow" in groups and deco.get("boxShadow"):
        bprops = el.group("boxShadow")
        _emit(ctx, normalize_box_shadow(deco["boxShadow"]), box_shadow_decls, el.group_selector("boxShadow"),
              bprops, get(printed, "boxShadow"), hovered)
    if transition and hovered:
        transition_style(ctx, el.selector, hovered)
    return hovered


def overflow_for_radius(ctx, border_attr: dict, selector: str):
    """Declarations::overflow_for_border_radius_style_declaration: a border radius clips the element."""
    for bp in ("desktop", "tablet", "phone"):
        v = get(border_attr, bp, "value")
        if isinstance(v, dict) and any(x not in (None, "", "0", "0px")
                                       for k, x in (v.get("radius") or {}).items() if k != "sync"):
            ctx.css.add(selector, ["overflow:hidden"], bp)
            return


def transition_style(ctx, selector: str, hovered: list):
    props = ",".join(dict.fromkeys(hovered))
    ctx.css.add(selector, [f"transition-property:{props}", "transition-duration:300ms",
                           "transition-timing-function:ease", "transition-delay:0ms"])


def custom_css(ctx, css_attr: dict, selector: str, fields: dict | None = None):
    """CssStyle::style for `css.mainElement` (the module's own element); other slots are named by coverage."""
    for bp in ("desktop", "tablet", "phone"):
        main = get(css_attr, bp, "value", "mainElement")
        if isinstance(main, str) and main.strip():
            decls = [re.sub(r"\s*:\s*", ":", d.strip(), count=1) for d in main.split(";") if d.strip()]
            ctx.css.add(selector, decls, bp)


def expand_selector(tpl: str, oc: str, **extra) -> str:
    return expand(tpl, oc, **extra)
