#!/usr/bin/env python3
"""Throwaway spike (Task 21): a stdlib-only Divi 5 renderer for six modules
(section, row, column, text, heading, button). Block markup in, full HTML page out.

  python3 d5render.py PAGE.html -o OUT.html [--tokens tokens.json] [--coverage cov.json]

Design (native, not D5->D4): walk the parsed blocks (the Skill's divi5_blocks parser), give each block its
order class, print the markup template copied from the module's render_callback output, and run a small
generic style engine over each element's decoration groups. The engine is driven by the theme's own
module.json (element selectors + styleProps: important flags, propertySelectors) and
module-default-printed-style-attributes.json (values the static CSS already prints), both read at runtime
from the cached Divi 5 theme. Declaration functions are ports of the StyleLibrary ones this page family
needs: background colour, spacing, sizing, font, border radius/width, button, transition.
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "Skill/divi-page-builder/scripts"))
import divi5_blocks as B  # noqa: E402

THEME = Path.home() / ".cache/divi-page-builder/divi/Divi-5.13.1/Divi"
COMPONENTS = THEME / "includes/builder-5/visual-builder/packages/module-library/src/components"
MEDIA = {"desktop": "", "tablet": "@media only screen and (max-width:980px)",
         "phone": "@media only screen and (max-width:767px)"}
SUPPORTED = {"section", "row", "column", "text", "heading", "button", "placeholder"}

_VAR = re.compile(r'\$variable\((\{.*?\})\)\$')


GLOBAL_COLORS: dict = {}


def resolve(v):
    """$variable({...})$ -> var(--id); a colour variable with settings (opacity/hue/saturation/lightness) -> the
    relative-colour hsl(from <resolved value> ...) Divi prints, which needs the site's global colour values."""
    if not isinstance(v, str) or "$variable(" not in v:
        return v

    def rep(m):
        try:
            d = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        val = d.get("value") or {}
        name, st = val.get("name", ""), val.get("settings") or {}
        if d.get("type") == "color" and st and name in GLOBAL_COLORS:
            h, s_, l_ = (st.get(k, 0) or 0 for k in ("hue", "saturation", "lightness"))
            op = st.get("opacity")
            alpha = f" / {op / 100:g}" if op not in (None, 100) else ""
            return f"hsl(from {GLOBAL_COLORS[name]} calc(h + {h}) calc(s + {s_}) calc(l + {l_}){alpha})"
        return f"var(--{name})"
    return _VAR.sub(rep, v)


def meta(slug: str) -> dict:
    j = json.loads((COMPONENTS / slug / "module.json").read_text())
    d = json.loads((COMPONENTS / slug / "module-default-printed-style-attributes.json").read_text())
    d.pop("_comment", None)
    return {"module": j, "printed": d}


def get(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return default
        d = d[p]
    return d


class Sheet:
    """(media, selector, [declarations]) in insertion order; minified output."""

    def __init__(self):
        self.rules = []

    def add(self, sel: str, decls: list, bp: str = "desktop"):
        decls = [d for d in decls if d]
        if decls:
            self.rules.append((MEDIA[bp], sel, decls))

    def text(self) -> str:
        out, by_media = [], {}
        for media, sel, decls in self.rules:
            by_media.setdefault(media, []).append(f"{sel}{{{';'.join(decls)}}}")
        out.append("".join(by_media.pop("", [])))
        for media in (MEDIA["tablet"], MEDIA["phone"]):
            if media in by_media:
                out.append(f"{media}{{{''.join(by_media[media])}}}")
        return "".join(out)


class Ctx:
    def __init__(self):
        self.counts: dict = {}
        self.css = Sheet()
        self.fonts: set = set()
        self.meta: dict = {}
        self.coverage: list = []
        self.unsupported: dict = {}
        self.gfonts = {i["family"]: i for i in json.loads((THEME / "core/json-data/google-fonts.json").read_text())["items"]}

    def order(self, slug: str) -> int:
        n = self.counts.get(slug, 0)
        self.counts[slug] = n + 1
        return n

    def m(self, slug):
        if slug not in self.meta:
            self.meta[slug] = meta(slug)
        return self.meta[slug]


def imp(flag, prop, bp="desktop"):
    """styleProps important: True, or {bp: {value: {prop: True}}}."""
    if flag is True:
        return True
    return bool(get(flag, bp, "value", prop)) if isinstance(flag, dict) else False


def decl(prop, val, important=False):
    if val in (None, ""):
        return ""
    return f"{prop}:{resolve(val)}{'!important' if important else ''}"


def states(attr):
    """(breakpoint, state, value) for a responsive attr {bp: {state: value}}."""
    for bp in ("desktop", "tablet", "phone"):
        for st in ("value", "hover"):
            v = get(attr, bp, st)
            if v is not None:
                yield bp, st, v


def sel_state(sel: str, st: str) -> str:
    return sel if st == "value" else ",".join(s.strip() + ":hover" for s in sel.split(","))


# ------------------------------------------------------------------------------------------------ groups
POSITIONS = {"center": "center", "top_left": "left top", "top_center": "center top", "top_right": "right top",
             "center_left": "left center", "center_right": "right center", "bottom_left": "left bottom",
             "bottom_center": "center bottom", "bottom_right": "right bottom"}


def gradient_css(g):
    stops = ",".join(f"{resolve(st.get('color'))} {st.get('position')}%" for st in g.get("stops") or [])
    kind = g.get("type", "linear")
    if kind == "linear":
        return f"linear-gradient({g.get('direction', '180deg')},{stops})"
    return f"radial-gradient(circle at {g.get('directionRadial', 'center')},{stops})"


def g_background(ctx, attr, sel, props, hovered):
    for bp, st, v in states(attr):
        if not isinstance(v, dict):
            continue
        important = imp(get(props, "important"), "background-color", bp)
        if v.get("color"):
            s = get(props, "propertySelectors", bp, "value", "background-color") or sel
            ctx.css.add(sel_state(s, st), [decl("background-color", v["color"], important)], bp)
            if st == "hover":
                hovered.append("background-color")
        img, g = v.get("image") or {}, v.get("gradient") or {}
        layers = []
        if g.get("enabled") == "on":
            layers.append(gradient_css(g))
        if img.get("url"):
            ds = []
            if img.get("size", "cover") not in ("",):
                ds.append(decl("background-size", img.get("size", "cover"), important))
            ds.append(decl("background-position", POSITIONS.get(img.get("position", "center"), img.get("position")), important))
            ds.append(decl("background-repeat", img.get("repeat", "no-repeat"), important))
            url = "url('" + img["url"] + "')"
            layers = layers + [url] if g.get("overlaysImage") == "on" or not layers else [url] + layers
            ds.append(decl("background-image", ",".join(layers), important))
            ctx.css.add(sel_state(sel, st), ds, bp)
        elif layers:
            ctx.css.add(sel_state(sel, st), [decl("background-image", ",".join(layers), important)], bp)


def g_spacing(ctx, attr, sel, props, hovered):
    important = get(props, "important")
    for bp, st, v in states(attr):
        for kind in ("padding", "margin"):
            box = (v or {}).get(kind) or {}
            ds = []
            for side in ("top", "right", "bottom", "left"):
                if box.get(side) not in (None, ""):
                    prop = f"{kind}-{side}"
                    ds.append(decl(prop, box[side], imp(important, prop, bp)))
            if ds:
                s = get(props, "propertySelectors", bp, "value", kind) or sel
                ctx.css.add(sel_state(s, st), ds, bp)


def g_sizing(ctx, attr, sel, props, hovered, printed=None, module_align=True):
    important = get(props, "important")
    psel = get(props, "propertySelectors", "desktop", "value") or {}
    for bp, st, v in states(attr):
        if not isinstance(v, dict):
            continue
        pv = get(printed or {}, bp, st) or {}
        for key, prop in (("width", "width"), ("maxWidth", "max-width"), ("minHeight", "min-height"),
                          ("height", "height"), ("maxHeight", "max-height")):
            if v.get(key) not in (None, "") and v.get(key) != pv.get(key):
                ctx.css.add(sel_state(psel.get(prop, sel), st), [decl(prop, v[key], imp(important, prop, bp))], bp)
        al = v.get("alignment")
        if al and module_align:
            ml, mr = {"center": ("auto", "auto"), "left": ("0", "auto"), "right": ("auto", "0")}[al]
            ctx.css.add(sel_state(psel.get("margin-left", sel), st),
                        [decl("margin-left", ml, imp(important, "margin-left", bp)),
                         decl("margin-right", mr, imp(important, "margin-right", bp))], bp)


FONT_KEYS = (("family", "font-family"), ("weight", "font-weight"), ("style", "font-style"),
             ("capitalization", "text-transform"), ("color", "color"), ("size", "font-size"),
             ("letterSpacing", "letter-spacing"), ("lineHeight", "line-height"), ("textAlign", "text-align"))


def font_family(ctx, fam):
    fam = resolve(fam)
    if fam.startswith("var("):
        return fam
    ctx.fonts.add(fam)
    cat = (ctx.gfonts.get(fam) or {}).get("category", "sans-serif")
    stack = {"serif": "Georgia,\"Times New Roman\",serif", "monospace": "monospace",
             "handwriting": "cursive", "display": "fantasy"}.get(cat, "Helvetica,Arial,Lucida,sans-serif")
    return f"'{fam}',{stack}"


def g_font(ctx, attr, sel, important, hovered, printed=None):
    for bp, st, v in states(attr):
        if not isinstance(v, dict):
            continue
        pv = get(printed or {}, bp, st) or {}
        ds = []
        for key, prop in FONT_KEYS:
            val = v.get(key)
            if val in (None, "") or val == pv.get(key):
                continue
            if key == "family":
                val = font_family(ctx, val)
            if key == "style":
                styles = val if isinstance(val, list) else [val]
                ds += [decl("font-style", "italic") if "italic" in styles else "",
                       decl("text-transform", "uppercase") if "uppercase" in styles else "",
                       decl("font-variant", "small-caps") if "capitalize" in styles else ""]
                lines = [x for x in ("underline", "line-through") if x in styles or (x == "line-through" and "strikethrough" in styles)]
                if lines:
                    ds += [decl("text-decoration-line", " ".join(lines)), decl("text-decoration-style", "solid")]
                continue
            ds.append(decl(prop, val, imp(important, prop, bp)))
            if st == "hover":
                hovered.append(prop)
        ctx.css.add(sel_state(sel, st), ds, bp)


def g_border(ctx, attr, sel, hovered, overflow_sel=None):
    has_radius = False
    for bp, st, v in states(attr):
        if not isinstance(v, dict):
            continue
        ds = []
        r = v.get("radius") or {}
        for k, prop in (("topLeft", "border-top-left-radius"), ("topRight", "border-top-right-radius"),
                        ("bottomRight", "border-bottom-right-radius"), ("bottomLeft", "border-bottom-left-radius")):
            if r.get(k) not in (None, ""):
                ds.append(decl(prop, r[k]))
                has_radius = True
        alls = get(v, "styles", "all") or {}
        if alls:
            ds += [decl("border-width", alls.get("width")), decl("border-color", alls.get("color") or "#333"),
                   decl("border-style", alls.get("style") or "solid")]
        ctx.css.add(sel_state(sel, st), ds, bp)
    if has_radius and overflow_sel:
        ctx.css.add(overflow_sel, ["overflow:hidden"])


def g_transition(ctx, sel, hovered):
    if hovered:
        props = ",".join(dict.fromkeys(hovered))
        ctx.css.add(sel, [f"transition-property:{props}", "transition-duration:300ms",
                          "transition-timing-function:ease", "transition-delay:0ms"])


def element_style(ctx, deco: dict, sel: str, props: dict, printed: dict, overflow=True, align=True):
    """ElementStyle::style for the groups this spike supports. Returns the groups it did not handle."""
    hovered: list = []
    done = set()
    if "background" in deco:
        g_background(ctx, deco["background"], sel, get(props, "background") or {}, hovered); done.add("background")
    if "sizing" in deco:
        g_sizing(ctx, deco["sizing"], sel, get(props, "sizing") or {}, hovered, get(printed, "sizing"), align); done.add("sizing")
    if "spacing" in deco:
        sp = dict(get(props, "spacing") or {})
        g_spacing(ctx, deco["spacing"], sp.get("selector", sel).replace("{{selector}}", sel), sp, hovered); done.add("spacing")
    if "border" in deco:
        g_border(ctx, deco["border"], sel, hovered, sel if overflow else None); done.add("border")
    if "font" in deco and isinstance(deco["font"], dict) and "font" in deco["font"]:
        g_font(ctx, deco["font"]["font"], sel, get(props, "font", "important", "font") or {}, hovered,
               get(printed, "font", "font")); done.add("font")
    g_transition(ctx, sel, hovered)
    return [k for k in deco if k not in done and k not in ("layout",)]


def expand(sel_tpl: str, oc: str, **extra) -> str:
    s = sel_tpl.replace("{{selector}}", oc).replace("{{baseSelector}}", oc).replace("{{selectorPrefix}}", "")
    s = s.replace("{{nestedModuleNameSelector}}", "")
    for k, v in extra.items():
        s = s.replace("{{" + k + "}}", v)
    return re.sub(r"\s*,\s*", ",", s)


def expand_props(props: dict, oc: str, **extra) -> dict:
    return json.loads(expand(json.dumps(props), oc, **extra)) if props else {}


# ------------------------------------------------------------------------------------------------ modules
def cls(*names) -> str:
    return " ".join(n for n in names if n)


def layout_kind(attrs, default="flex"):
    return get(attrs, "module", "decoration", "layout", "desktop", "value", "display") or default


def wpautop(text: str) -> str:
    # Enough for paragraph content: Divi runs wpautop on text content, which leaves "</p>\n".
    text = text.strip()
    if not text:
        return ""
    if not text.startswith("<"):
        text = f"<p>{text}</p>"
    text = re.sub(r"(</(?:p|li|ul|ol|h[1-6]|blockquote)>|<(?:ul|ol)>)\s*", "\\1\n", text)
    return re.sub(r"\n(?=</(?:ul|ol)>$)", "\n", text)


def presets(attrs, slug):
    ids = attrs.get("modulePreset") or []
    if isinstance(ids, str):
        ids = [ids]
    return [f"preset--module--divi-{slug}--{i}" for i in ids if i and i != "default"]


SUBKEYS = {
    "background": {"color", "image.url", "image.size", "image.position", "image.repeat", "gradient.enabled",
                   "gradient.direction", "gradient.stops", "gradient.overlaysImage", "gradient.type"},
    "sizing": {"width", "maxWidth", "minHeight", "height", "maxHeight", "alignment"},
    "spacing": {f"{k}.{s}" for k in ("padding", "margin") for s in ("top", "right", "bottom", "left", "syncVertical",
                                                                    "syncHorizontal")},
    "border": {f"radius.{k}" for k in ("sync", "topLeft", "topRight", "bottomRight", "bottomLeft")}
              | {"styles.all.width", "styles.all.color", "styles.all.style"},
    "font": {"family", "weight", "style", "capitalization", "color", "size", "letterSpacing", "lineHeight",
             "textAlign", "headingLevel"},
    "layout": {"display"},
    "button": {"enable"},
}


def _flat(v, prefix=""):
    if isinstance(v, dict) and v:
        for k, x in v.items():
            yield from _flat(x, f"{prefix}.{k}" if prefix else k)
    else:
        yield prefix


def unhandled(ctx, slug, attrs, handled_paths):
    """Coverage: attribute leaves (down to the keys inside each value) this spike never reads."""
    ignored, n = [], 0
    for path, bp, st, v in B.iter_leaves(attrs):
        if path in ("builderVersion",) or path.startswith("module.meta"):
            continue
        group = path.rsplit(".", 1)[-1]
        whole = any(path == h or path.startswith(h + ".") for h in handled_paths)
        for sub in (_flat(v) if isinstance(v, dict) and not whole else [""]):
            n += 1
            full = f"{path}.{sub}" if sub else path
            if whole:
                continue
            fam = group if group in SUBKEYS else ("font" if path.endswith(".font") else None)
            if fam and path in handled_paths_family(handled_paths) and (sub in SUBKEYS[fam] or sub.split(".")[0] + ".*" in SUBKEYS[fam]):
                continue
            ignored.append(full)
    ctx.coverage.append({"module": slug, "attrs": n, "ignored": sorted(set(ignored))})


def handled_paths_family(handled_paths):
    return {h[:-2] for h in handled_paths if h.endswith(".~")}


MOD_HANDLED = ["module.decoration.background.*", "module.decoration.sizing", "module.decoration.spacing",
               "module.decoration.border", "module.decoration.layout.display", "modulePreset"]


def handled_list(extra):
    base = ["module.decoration.background.~", "module.decoration.sizing.~", "module.decoration.spacing.~",
            "module.decoration.border.~", "module.decoration.layout.~", "modulePreset", "module.advanced.columnStructure",
            "module.advanced.type"]
    return base + extra


def render(block, ctx, siblings_info=None) -> str:
    slug = block.name.split("/", 1)[1]
    if slug == "placeholder":
        return "".join(render(c, ctx) for c in block.blocks)
    if slug not in SUPPORTED:
        ctx.unsupported[slug] = ctx.unsupported.get(slug, 0) + 1
        return (f'<div class="pp-unsupported" style="border:2px dashed #e11d48;padding:12px;color:#e11d48">'
                f'Divi 5 module not rendered by the Python spike: {htmllib.escape(slug)}</div>')
    return globals()[f"r_{slug}"](block, ctx, siblings_info or {})


def r_section(b, ctx, info):
    n = ctx.order("section"); oc = f".et_pb_section_{n}"
    m = ctx.m("section"); a = b.attrs
    deco = get(a, "module", "decoration") or {}
    props = get(m, "module", "attributes", "module", "styleProps") or {}
    # SectionModule: background colour selector is prefixed for post content.
    bgsel = f".et-l--post>.et_builder_inner_content .et_pb_section{oc}"
    props = expand_props(props, oc)
    props.setdefault("background", {})["propertySelectors"] = {"desktop": {"value": {"background-color": bgsel}}}
    element_style(ctx, deco, oc, props, get(m, "printed", "module", "decoration") or {})
    unhandled(ctx, "section", a, handled_list([]))
    kids = b.blocks
    inner = "".join(render(c, ctx) for c in kids)
    return f'<div class="{cls(oc[1:], "et_pb_section", "et_section_regular", "et_" + layout_kind(a) + "_section")}">{inner}</div>'


def r_row(b, ctx, info):
    n = ctx.order("row"); oc = f".et_pb_row_{n}"
    m = ctx.m("row"); a = b.attrs
    deco = get(a, "module", "decoration") or {}
    props = expand_props(get(m, "module", "attributes", "module", "styleProps") or {}, oc)
    element_style(ctx, deco, oc, props, get(m, "printed", "module", "decoration") or {})
    unhandled(ctx, "row", a, handled_list([]))
    cols = b.blocks
    ncols = len(cols)
    extra = [f"et_pb_row_{ncols}col"] if ncols >= 4 else []
    lk = layout_kind(a)
    inner = "".join(render(c, ctx, {"last": i == ncols - 1}) for i, c in enumerate(cols))
    kl = cls(oc[1:], "et_pb_row", *extra, f"et_{lk}_row", *(f"et_{lk}_row_{ncols}col" for _ in [0] if ncols >= 4))
    return f'<div class="{kl}">{inner}</div>'


def r_column(b, ctx, info):
    n = ctx.order("column"); oc = f".et_pb_column_{n}"
    m = ctx.m("column"); a = b.attrs
    deco = get(a, "module", "decoration") or {}
    props = expand_props(get(m, "module", "attributes", "module", "styleProps") or {}, oc)
    ctype = get(a, "module", "advanced", "type", "desktop", "value") or "4_4"
    ctx.css.add(oc, ["--et-pb-icon-self-align:center"])
    element_style(ctx, deco, oc, props, get(m, "printed", "module", "decoration") or {})
    unhandled(ctx, "column", a, handled_list([]))
    inner = "".join(render(c, ctx) for c in b.blocks)
    kl = cls(oc[1:], "et_pb_column", f"et_pb_column_{ctype}", "et-last-child" if info.get("last") else "",
             f"et_{layout_kind(a)}_column", "et_pb_css_mix_blend_mode_passthrough")
    return f'<div class="{kl}">{inner}</div>'


def module_common(b, ctx, slug):
    n = ctx.order(slug); oc = f".et_pb_{slug}_{n}"
    m = ctx.m(slug); a = b.attrs
    deco = get(a, "module", "decoration") or {}
    props = expand_props(get(m, "module", "attributes", "module", "styleProps") or {}, oc)
    return n, oc, m, a, deco, props


def r_text(b, ctx, info):
    n, oc, m, a, deco, props = module_common(b, ctx, "text")
    element_style(ctx, deco, oc, props, get(m, "printed", "module", "decoration") or {})
    ctx.css.add(oc, ["text-align:start"])  # TextStyle: module.advanced.text orientation default
    cprops = get(m, "module", "attributes", "content", "styleProps") or {}
    body = get(a, "content", "decoration", "bodyFont", "body", "font")
    if body:
        g_font(ctx, body, f"{oc} .et_pb_text_inner", get(cprops, "bodyFont", "important", "body", "font") or {}, [])
    link = get(a, "content", "decoration", "bodyFont", "link", "font")
    if link:
        g_font(ctx, link, f"{oc} .et_pb_text_inner a", get(cprops, "bodyFont", "important", "link", "font") or {}, [])
    for h in ("h1", "h2", "h3", "h4", "h5", "h6"):
        hf = get(a, "content", "decoration", "headingFont", h, "font")
        if hf:
            g_font(ctx, hf, f"{oc} .et_pb_text_inner {h}", get(cprops, "headingFont", "important", h, "font") or {}, [])
    unhandled(ctx, "text", a, handled_list(["content.innerContent", "content.decoration.bodyFont.body.font.~", "content.decoration.bodyFont.link.font.~"] + [f"content.decoration.headingFont.{h}.font.~" for h in ("h1", "h2", "h3", "h4", "h5", "h6")] + ["content.innerContent"]))
    content = wpautop(get(a, "content", "innerContent", "desktop", "value") or "")
    kl = cls(oc[1:], "et_pb_text", "et_pb_bg_layout_light", "et_pb_module", f"et_{layout_kind(a)}_module", *presets(a, "text"))
    return f'<div class="{kl}"><div class="et_pb_text_inner">{content}</div></div>'


def r_heading(b, ctx, info):
    n, oc, m, a, deco, props = module_common(b, ctx, "heading")
    element_style(ctx, deco, oc, props, get(m, "printed", "module", "decoration") or {})
    tmeta = get(m, "module", "attributes", "title") or {}
    tsel = expand(tmeta.get("selector", ""), oc)
    font = get(a, "title", "decoration", "font", "font") or {}
    g_font(ctx, font, tsel, get(tmeta, "styleProps", "font", "important", "font") or {}, [],
           get(m, "printed", "title", "decoration", "font", "font"))
    level = get(font, "desktop", "value", "headingLevel") or "h1"
    unhandled(ctx, "heading", a, handled_list(["title.innerContent", "title.decoration.font.font.~"]))
    title = get(a, "title", "innerContent", "desktop", "value") or ""
    kl = cls(oc[1:], "et_pb_heading", "et_pb_module", f"et_{layout_kind(a)}_module", *presets(a, "heading"))
    return (f'<div class="{kl}"><div class="et_pb_heading_container"><{level} class="et_pb_module_header">'
            f'{title}</{level}></div></div>')


def r_button(b, ctx, info):
    n, oc, m, a, deco, props = module_common(b, ctx, "button")
    wrap = f"{oc}_wrapper"
    props = expand_props(get(m, "module", "attributes", "module", "styleProps") or {}, oc, wrapperSelector=wrap)
    element_style(ctx, deco, oc, props, {})
    al = get(a, "module", "advanced", "alignment", "desktop", "value")
    if al:
        ctx.css.add(wrap, [f"text-align:{al}"])
        ml, mr = {"center": ("auto", "auto"), "left": ("0", "auto"), "right": ("auto", "0")}[al]
        ctx.css.add(f"{wrap} {oc}", [f"text-align:{al}", f"margin-left:{ml}", f"margin-right:{mr}"])
    bmeta = get(m, "module", "attributes", "button") or {}
    bsel = expand(bmeta.get("selector", ""), oc)
    bdeco = get(a, "button", "decoration") or {}
    hovered: list = []
    if "background" in bdeco:
        g_background(ctx, bdeco["background"], bsel, {}, hovered)
    if "font" in bdeco:
        g_font(ctx, get(bdeco, "font", "font") or {}, bsel, get(bmeta, "styleProps", "font", "important", "font") or {}, hovered)
    if "border" in bdeco:
        g_border(ctx, bdeco["border"], bsel, hovered)
    g_transition(ctx, bsel, hovered)
    if get(bdeco, "button", "desktop", "value", "enable") == "on":
        ctx.css.add(f"{bsel}:after", ["font-size:1.6em"])
    unhandled(ctx, "button", a, handled_list(["button.innerContent", "button.decoration.background.~",
                                              "button.decoration.font.font.~", "button.decoration.border.~",
                                              "button.decoration.button.~", "module.advanced.alignment"]))
    inner = get(a, "button", "innerContent", "desktop", "value") or {}
    pre = presets(a, "button")
    wk = cls("et_pb_module", "et_pb_button_module_wrapper", wrap[1:], *(p + "_wrapper" for p in pre))
    kl = cls(oc[1:], "et_pb_button", "et_pb_bg_layout_light", "et_pb_module", f"et_{layout_kind(a)}_module", *pre)
    href = htmllib.escape(inner.get("linkUrl") or "#", quote=True)
    return f'<div class="{wk}"><a class="{kl}" href="{href}">{inner.get("text", "")}</a></div>'


# ------------------------------------------------------------------------------------------------ page
STOCK_CUSTOMIZER_CSS = ("@media only screen and (min-width:1350px){.et_block_row{padding:27px 0}.et_pb_section{padding:54px 0}"
                        ".single.et_pb_pagebuilder_layout.et_full_width_page .et_post_meta_wrapper{padding-top:81px}"
                        ".et_pb_fullwidth_section{padding:0}}")
GLOBAL_FONTS_CSS = (":root{--et_global_heading_font: 'Open Sans';--et_global_body_font: 'Open Sans';--et_global_heading_font_weight: 500;"
                    "--et_global_body_font_weight: 500;--et_global_body_font_size: 14px;--et_global_body_font_height: 1.7em;}"
                    "body{line-height:var(--et_global_body_font_height);font-size:var(--et_global_body_font_size);}")


def token_root_css(tokens: dict) -> str:
    out = []
    for gid, e in ((tokens.get("colors") or {}).get("global") or {}).items():
        v = e.get("value") if isinstance(e, dict) else e
        if v:
            out.append(f"--{gid}:{v};")
    for e in ((tokens.get("colors") or {}).get("customizer") or {}).values():
        if isinstance(e, dict) and e.get("id") and e.get("value"):
            out.append(f"--{e['id']}:{e['value']};")
    for gid, e in (tokens.get("variables") or {}).items():
        v = e.get("value") if isinstance(e, dict) else None
        if isinstance(v, str) and v:
            out.append(f"--{gid}:{v};")
    return ":root{" + "".join(out) + "}" if out else ""


def page_shell(builder: str, css: str, ctx: Ctx, tokens: dict, static_css: str) -> str:
    # Static fonts: one css?family= link; variable fonts (axes): one css2 link each (wght range), as Divi 5 prints.
    fams = sorted(f for f in ctx.fonts if f in ctx.gfonts)
    static = [f for f in fams if not ctx.gfonts[f].get("axes")]
    gf = ("<link rel='stylesheet' href='https://fonts.googleapis.com/css?family="
          + "|".join(f.replace(" ", "+") + ":" + ",".join(ctx.gfonts[f]["variants"]) for f in static)
          + "&#038;subset=latin,latin-ext&#038;display=swap' />") if static else ""
    for f in fams:
        axes = {a["tag"]: a for a in ctx.gfonts[f].get("axes") or []}
        if "wght" in axes:
            r = f"{axes['wght']['start']}..{axes['wght']['end']}"
            spec = f"ital,wght@0,{r};1,{r}" if "italic" in ctx.gfonts[f]["variants"] else f"wght@{r}"
            gf += (f"<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family={f.replace(' ', '+')}:{spec}"
                   f"&#038;subset=latin%2Clatin-ext&#038;display=swap' />")
    etl = (f'<div class="et-l et-l--post">\n\t\t\t<div class="et_builder_inner_content">\n\t\t{builder}\n\n\t\t</div>\n\t</div>')
    return f"""<!DOCTYPE html>
<html lang="en-US"><head><meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0" />
<link rel='stylesheet' href='https://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800&#038;subset=latin,latin-ext&#038;display=swap' />
<style id="pp-divi5-static-css">{static_css}</style>
<style id="pp-divi5-customizer">{STOCK_CUSTOMIZER_CSS}</style>
{gf}
<style class="et-vb-global-data et-vb-global-fonts">{GLOBAL_FONTS_CSS}</style>
<style id="pp-token-root">{token_root_css(tokens)}</style>
<style id="et-builder-module-design-python5-inline-styles">{css}</style>
</head>
<body class="page-template-default page et_pb_button_helper_class et_fixed_nav et_show_nav et_primary_nav_dropdown_animation_fade et_secondary_nav_dropdown_animation_fade et_header_style_left et_pb_footer_columns4 et_cover_background et_pb_gutter et_pb_gutters3 et_pb_pagebuilder_layout et_no_sidebar et_divi_theme et-db">
<div id="page-container"><div id="et-main-area"><div id="main-content"><article class="page type-page"><div class="entry-content">
{etl}
</div></article></div></div></div>
</body></html>
"""


def render_page(source: str, tokens: dict | None = None, static_css: str | None = None):
    t0 = time.perf_counter()
    ctx = Ctx()
    GLOBAL_COLORS.clear()
    GLOBAL_COLORS.update({k: e.get("value") for k, e in (((tokens or {}).get("colors") or {}).get("global") or {}).items()
                          if isinstance(e, dict) and e.get("value")})
    doc = B.parse(source)
    builder = "".join(render(nd, ctx) for nd in doc.nodes if isinstance(nd, B.Block))
    css = ctx.css.text()
    t_render = time.perf_counter() - t0
    if static_css is None:
        static_css = (THEME / "style-static.min.css").read_text()
        static_css = re.sub(r"url\((['\"]?)(?!data:|https?:|//)([^)'\"]+)\1\)",
                            lambda m: f"url({m.group(1)}file://{THEME}/{m.group(2).lstrip('./')}{m.group(1)})", static_css)
    html = page_shell(builder, css, ctx, tokens or {}, static_css)
    tot = sum(c["attrs"] for c in ctx.coverage)
    ign = sum(len(c["ignored"]) for c in ctx.coverage)
    cov = {"render_ms": round(t_render * 1000, 2), "modules": len(ctx.coverage), "unsupported": ctx.unsupported,
           "attr_leaves": tot, "ignored_leaves": ign,
           "ignored": sorted({f"{c['module']}:{p}" for c in ctx.coverage for p in c["ignored"]})}
    return html, cov


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--tokens")
    ap.add_argument("--coverage")
    a = ap.parse_args()
    tokens = json.loads(Path(a.tokens).read_text()) if a.tokens else {}
    html, cov = render_page(Path(a.page).read_text(), tokens)
    Path(a.out).write_text(html)
    if a.coverage:
        Path(a.coverage).write_text(json.dumps(cov, indent=1))
    print(json.dumps({k: v for k, v in cov.items() if k != "ignored"}), f"ignored={len(cov['ignored'])}")


if __name__ == "__main__":
    main()
