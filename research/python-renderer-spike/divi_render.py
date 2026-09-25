#!/usr/bin/env python3
"""SPIKE: pure-Python (stdlib only) Divi 4 shortcode -> HTML preview renderer.

    python3 divi_render.py page.txt -o out.html [--divi-path DIR | --theme-css-url URL]
                                                [--no-js] [--coverage cov.json]

Throwaway feasibility prototype. It re-implements a subset of Divi 4.27's PHP renderer:
markup templates for the ~20 most common modules (copied from the module render()
methods) and a generic CSS engine driven by the `advanced_fields` configs that
research/divi-schema dumps from Divi (fonts, background, borders, box shadow,
margin/padding, max-width, button), plus the module-specific `set_style` calls.

Divi's own static CSS / JS / font list / mask SVGs are read at runtime from a local Divi
install (--divi-path) or the static CSS from a live site (--theme-css-url); nothing from
Divi is copied into this directory.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "Skill" / "divi-page-builder" / "scripts"))
from divi_shortcode import Node, Text, parse  # noqa: E402

DUMP_DIR = REPO / "research" / "divi-schema" / "modules"
DEFAULT_DIVI = Path.home() / "Local Sites/divi-test/app/public/wp-content/themes/Divi"

DEVICES = ("desktop", "tablet", "phone")
MEDIA = {"desktop": "", "tablet": "@media only screen and (max-width:980px)",
         "phone": "@media only screen and (max-width:767px)"}
# Attributes that never affect output (bookkeeping), excluded from the coverage report.
META_ATTRS = {"_builder_version", "_module_preset", "hover_enabled", "locked", "global_colors_info",
              "fb_built", "admin_label", "collapsed", "template_type", "sticky_enabled",
              "_dynamic_attributes", "theme_builder_area", "saved_specialty_column_type",
              "column_structure", "specialty_columns"}


# ----------------------------------------------------------------------------- data
class DiviData:
    """Everything read from Divi at runtime (theme dir) + the repo's schema dump."""

    def __init__(self, divi_path: Path | None, theme_css_url: str | None):
        self.divi_path = divi_path
        self.theme_css_url = theme_css_url
        self._modules: dict = {}
        self._gfonts = None
        self._static_css = None
        self.asset_base = None  # e.g. "/__divi/" when served by serve.py
        self.embed_fonts = True  # standalone output: inline woff/woff2 + logo as data: URIs

    def data_uri(self, rel: str) -> str | None:
        p = (self.divi_path / rel) if self.divi_path else None
        if not p or not p.is_file():
            return None
        mime = {".woff2": "font/woff2", ".woff": "font/woff", ".png": "image/png", ".svg": "image/svg+xml"}.get(p.suffix, "application/octet-stream")
        return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"

    def module(self, slug: str) -> dict | None:
        if slug not in self._modules:
            p = DUMP_DIR / f"{slug}.json"
            self._modules[slug] = json.loads(p.read_text()) if p.exists() else None
        return self._modules[slug]

    def google_fonts(self) -> dict:
        if self._gfonts is None:
            self._gfonts = {}
            p = self.divi_path / "core/json-data/google-fonts.json" if self.divi_path else None
            if p and p.exists():
                for it in json.loads(p.read_text())["items"]:
                    self._gfonts[it["family"]] = it
        return self._gfonts

    def static_css(self) -> str:
        if self._static_css is None:
            css = ""
            if self.theme_css_url:
                with urllib.request.urlopen(self.theme_css_url, timeout=30) as r:
                    css = r.read().decode("utf-8", "replace")
                base = self.theme_css_url.rsplit("/", 1)[0] + "/"
            elif self.divi_path and (self.divi_path / "style-static.min.css").exists():
                css = (self.divi_path / "style-static.min.css").read_text(encoding="utf-8", errors="replace")
                base = self.asset_base or ("file://" + urllib.parse.quote(str(self.divi_path)) + "/")
            else:
                base = ""
            # make relative url() absolute (fonts/images live next to style.css). Standalone files
            # (no asset_base, local theme) get the icon/web fonts inlined as data: URIs: browsers refuse
            # file:// sub-resources when the HTML itself is served over http(s).
            def fix(m):
                q, rel = m.group(1), m.group(2)
                clean = rel.split("?")[0].split("#")[0]
                if self.embed_fonts and not self.asset_base and not self.theme_css_url and self.divi_path \
                        and clean.endswith((".woff2", ".woff")):
                    uri = self.data_uri(clean)
                    if uri:
                        return f"url({uri})"
                return f"url({q}{base}{rel}{q})"
            css = re.sub(r"url\((['\"]?)(?!data:|https?:|/|#)([^)'\"]+)\1\)", fix, css)
            self._static_css = css
        return self._static_css

    def mask_svg(self, style: str, variant: str, ratio: str = "landscape") -> str | None:
        if not self.divi_path:
            return None
        p = self.divi_path / f"includes/builder/feature/background-masks/mask/{style}.php"
        if not p.exists():
            return None
        src = p.read_text()
        m = re.search(r"'%s'\s*=>\s*array\((.*?)\)," % re.escape(variant), src, re.S)
        if not m:
            return None
        m2 = re.search(r"'%s'\s*=>\s*'([^']*)'" % ratio, m.group(1))
        return m2.group(1) if m2 else None

    def read_js(self, rel: str) -> str:
        p = self.divi_path / rel if self.divi_path else None
        return p.read_text(encoding="utf-8", errors="replace") if p and p.exists() else ""


# ----------------------------------------------------------------------------- helpers
def to_css_decimal(v: float) -> str:
    s = ("%.6f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def range_value(val: str, option_type: str = "") -> str:
    """et_builder_process_range_value()."""
    val = val.strip()
    if option_type == "line_height" and val in ("normal", "inherit", "initial"):
        return val
    m = re.match(r"^(-?[\d.]+)(.*)$", val)
    if not m:
        return val
    try:
        num = float(m.group(1))
    except ValueError:
        return val
    unit = m.group(2)
    if unit == "":
        unit = "em" if option_type == "line_height" and num <= 3 else "px"
    return to_css_decimal(num) + unit


def minify_decl(d: str) -> str:
    d = re.sub(r"\s+", " ", d).strip().rstrip(";").strip()
    d = re.sub(r"\s*!important", "!important", d)
    d = re.sub(r"\s*,\s*", ",", d)
    d = re.sub(r"^([-\w]+)\s*:\s*", r"\1:", d)
    return d


def minify_sel(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*,\s*", ",", s)
    s = re.sub(r"\s*>\s*", ">", s)
    return s


def split_decls(decl: str) -> list:
    out, depth, cur = [], 0, ""
    for ch in decl:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            if cur.strip():
                out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [minify_decl(x) for x in out if minify_decl(x)]


def add_hover_to_order_class(sel: str) -> str:
    parts = [p.strip() for p in sel.split(",")]
    return ", ".join(re.sub(r"(.*%%order_class%%[^\s:]*)(.*)", r"\1:hover\2", p, count=1) for p in parts)


def add_hover_to_selectors(sel: str) -> str:
    parts = [p.strip() for p in sel.split(",")]
    return ", ".join(re.sub(r"(.+\s)*([^:]+?)((::?[-a-z()\[\]]+)+)?$", r"\1\2:hover\3", p, count=1, flags=re.I)
                     for p in parts)


def suffix_selectors(sel: str, suffix: str) -> str:
    return ", ".join(p.strip() + suffix for p in sel.split(","))


def prefix_selectors(sel: str, prefix: str) -> str:
    return ", ".join(f"{prefix} {p.strip()}" for p in sel.split(","))


def new_window(p) -> str:
    return ' target="_blank"' if p.get("url_new_window", "") == "on" else ""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def esc_url(s: str) -> str:
    """WordPress esc_url(): keeps the URL, encodes & as &#038;."""
    s = s.strip().replace("&amp;", "&").replace("&", "&#038;")
    return s.replace('"', "%22").replace("'", "&#039;")


def decode_icon(v: str) -> str:
    """'&#xe03b;||divi||400' -> the private-use glyph."""
    code = v.split("|")[0]
    m = re.match(r"&#x([0-9a-fA-F]+);?", code)
    if m:
        return chr(int(m.group(1), 16))
    m = re.match(r"%%(\d+)%%", code)   # legacy numeric icon index -> not resolved in spike
    return "" if m else html.unescape(code)


def icon_font(v: str) -> tuple:
    parts = v.split("|")
    fam = parts[2] if len(parts) > 2 else ""
    weight = parts[4] if len(parts) > 4 and parts[4] else "400"
    return ("FontAwesome" if fam == "fa" else "ETmodules"), weight


def icon_css_content(v: str) -> str:
    code = v.split("|")[0]
    m = re.match(r"&#x([0-9a-fA-F]+);?", code)
    return ('"\\%s"' % m.group(1).lower()) if m else '""'


def wpautop(text: str) -> str:
    """Tiny subset of WordPress wpautop() for module content."""
    t = text.strip("\n")
    if not t:
        return ""
    if re.search(r"<(p|div|h[1-6]|ul|ol|blockquote|table|figure)\b", t):
        return t
    paras = [p.strip() for p in re.split(r"\n\s*\n", t) if p.strip()]
    return "".join(f"<p>{p.replace(chr(10), '<br />' + chr(10))}</p>\n" for p in paras).rstrip("\n")


def wptexturize(s: str) -> str:
    """Subset of WordPress wptexturize() (runs on the_content): apostrophes + straight quotes in text."""
    parts = re.split(r"(<[^>]*>)", s)
    for i, part in enumerate(parts):
        if part.startswith("<"):
            continue
        part = re.sub(r"(?<=\w)'(?=\w)", "&#8217;", part)
        part = re.sub(r"(^|\s)'", r"\1&#8216;", part)
        part = re.sub(r"'", "&#8217;", part)
        part = re.sub(r'(^|\s|>)"', r"\1&#8220;", part)
        part = re.sub(r'"', "&#8221;", part)
        part = part.replace(" -- ", " &#8212; ").replace("...", "&#8230;")
        parts[i] = part
    return "".join(parts)


def module_content(node) -> str:
    """Module body as Divi outputs it: builder pages skip wpautop; wptexturize still runs."""
    return wptexturize(node.content.strip("\n"))


# ----------------------------------------------------------------------------- props
class Props(dict):
    """Module props (defaults + attrs) that records which keys were read (coverage)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.read = set()

    def __getitem__(self, k):
        self.read.add(k)
        return super().get(k, "")

    def get(self, k, d=""):
        self.read.add(k)
        return super().get(k, d)


def resp_enabled(p: Props, name: str) -> bool:
    return p.get(f"{name}_last_edited", "").startswith("on")


def any_value(p: Props, name: str, device: str = "desktop", default: str = "", force: bool = False) -> str:
    """ResponsiveOptions::get_any_value()."""
    base = re.sub(r"_(tablet|phone)$", "", name)
    key = base if device == "desktop" else f"{base}_{device}"
    cur = dict.get(p, key, "") if key in p else ""
    p.read.add(key)
    if device == "desktop":
        prev = default
    else:
        desktop = dict.get(p, base, "") or default
        prev = desktop if device == "tablet" else (dict.get(p, f"{base}_tablet", "") or desktop)
    if force:
        return cur or prev
    return "" if cur == prev else cur


def property_values(p: Props, name: str, default: str = "", force: bool = False) -> dict:
    vals = {d: default for d in DEVICES}
    vals["desktop"] = any_value(p, name, "desktop", default, force)
    if resp_enabled(p, name):
        vals["tablet"] = any_value(p, name, "tablet", default, force)
        vals["phone"] = any_value(p, name, "phone", default, force)
    else:
        vals["tablet"] = vals["phone"] = ""
    return vals


def hover_value(p: Props, name: str, default=None):
    if p.get(f"{name}__hover_enabled", "").startswith("on"):
        v = p.get(f"{name}__hover", "")
        return v if v != "" else default
    return default


# ----------------------------------------------------------------------------- context
class Ctx:
    def __init__(self, data: DiviData):
        self.data = data
        self.counters: dict = {}
        self.styles = {d: {} for d in DEVICES}  # device -> {selector: [decls]}
        self.fonts: set = set()
        self.coverage: list = []
        self.unsupported: dict = {}
        self.specialty = False
        self.specialty_col_type = ""
        self.slider = None

    def next_index(self, slug: str) -> int:
        n = self.counters.get(slug, 0)
        self.counters[slug] = n + 1
        return n

    def style(self, order_class: str, selector, decl: str, device: str = "desktop"):
        if not decl or not decl.strip():
            return
        sels = selector if isinstance(selector, list) else [selector]
        for sel in sels:
            s = minify_sel(sel.replace("%%order_class%%", "." + order_class))
            bucket = self.styles[device].setdefault(s, [])
            for d in split_decls(decl):
                bucket.append(d)

    def css_text(self) -> str:
        out = []
        for dev in DEVICES:
            rules = []
            for sel, decls in self.styles[dev].items():
                seen, uniq = set(), []
                for d in decls:
                    if d not in seen or True:
                        uniq.append(d)
                    seen.add(d)
                rules.append(f"{sel}{{{';'.join(uniq)}}}")
            if not rules:
                continue
            body = "\n".join(rules)
            out.append(f"{MEDIA[dev]}{{{body}\n}}" if MEDIA[dev] else body)
        return "\n".join(out)


# ----------------------------------------------------------------------------- module base
class Module:
    slug = ""
    render_slug = None

    def __init__(self, node: Node, ctx: Ctx, parent=None):
        self.node, self.ctx, self.parent = node, ctx, parent
        rs = self.render_slug or node.tag
        self.dump = ctx.data.module(self.slug or node.tag) or {"module": {"advanced_fields": {}, "main_css_element": "%%order_class%%"}, "fields": {}}
        self.af = self.dump["module"].get("advanced_fields") or {}
        self.main = self.dump["module"].get("main_css_element") or "%%order_class%%"
        self.fields = self.dump.get("fields", {})
        defaults = {}
        for k, f in self.fields.items():
            if "default_on_front" in f:
                defaults[k] = f["default_on_front"]
            elif "default" in f and isinstance(f["default"], str):
                defaults[k] = f["default"]
        self.defaults = defaults
        attrs = {k: node.value(k) for k in node.attrs}
        self.attrs = attrs
        self.props = Props({**defaults, **attrs})
        self.props.read.clear()
        self.index = ctx.next_index(rs)
        self.order_class = f"{rs}_{self.index}"
        self.classes: list = []

    # -- utilities
    def field_default(self, name: str) -> str:
        d = self.fields.get(name, {}).get("default", "")
        return d if isinstance(d, str) else ""

    def css(self, selector, decl, device="desktop"):
        self.ctx.style(self.order_class, selector, decl, device)

    def add_class(self, *cls):
        for c in cls:
            if c:
                self.classes.append(c)

    def classname(self) -> str:
        seen, out = set(), []
        for c in self.classes:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return " ".join(out)

    def content_html(self) -> str:
        return render_children(self.node, self.ctx, self)

    def raw_content(self) -> str:
        return "".join(c.value for c in self.node.children if isinstance(c, Text))

    def text_orientation_class(self) -> str:
        out = ""
        for dev in DEVICES:
            v = self.props.get("text_orientation") if dev == "desktop" else (
                self.props.get(f"text_orientation_{dev}") if resp_enabled(self.props, "text_orientation") else "")
            if v:
                v = "justified" if v == "justify" else v
                out += f" et_pb_text_align_{v}" + ("" if dev == "desktop" else f"-{dev}")
        return out

    def bg_layout_class(self) -> str:
        return f"et_pb_bg_layout_{self.props.get('background_layout')}"

    def generate_styles(self, base, selector, prop, important=False, typ="", hover=True, responsive=True,
                        hover_loc="order_class", skip_default=False):
        p = self.props
        if responsive:
            vals = property_values(p, base)
            if skip_default and vals["desktop"] == self.field_default(base):
                vals["desktop"] = ""
            for dev in DEVICES:
                v = vals[dev]
                if v:
                    if typ == "range":
                        v = range_value(v)
                    self.css(selector, f"{prop}:{v}{' !important' if important else ''}", dev)
        if hover:
            hv = hover_value(p, base)
            if hv:
                hs = add_hover_to_order_class(selector) if hover_loc == "order_class" else add_hover_to_selectors(selector)
                self.css(hs, f"{prop}:{hv}{' !important' if important else ''}")

    # -- the generic advanced-fields engine (process_additional_options) ------------------
    def process_additional(self):
        if self.af is False:
            return
        self.process_fonts()
        self.process_text_shadow()
        self.process_background()
        self.process_borders()
        self.process_overflow()
        self.process_custom_margin()
        self.process_max_width()
        self.process_button()
        self.process_box_shadow()
        self.process_transitions()

    # fonts ------------------------------------------------------------------------------
    def font_decl(self, value: str, important: bool, default: str | None = None) -> str:
        if value == "":
            return ""
        vals = [x.strip() for x in value.split("|")]
        vals += [""] * (9 - len(vals))
        dvals = (default or "||||||||").split("|") + [""] * 9
        if vals[1] == "on":
            vals[1] = "700"
        imp = " !important" if important else ""
        st = ""
        name = vals[0]
        if name and name != dvals[0] and name != "Default":
            st += self.font_family(name, important) + " "
        weight = vals[1]

        def fs(prop, is_default, is_value, prop_default, prop_value):
            if is_value and not is_default:
                return f"{prop}: {prop_value}{imp}; "
            if not is_value and is_default:
                return f"{prop}: {prop_default}{imp}; "
            return ""
        dweight = dvals[1]
        st += fs("font-weight", dweight != "" and (weight == "" or dweight == weight), weight != "", "normal", weight)
        st += fs("font-style", dvals[2] == "on", vals[2] == "on", "normal", "italic")
        st += fs("text-transform", dvals[3] == "on", vals[3] == "on", "none", "uppercase")
        st += fs("text-decoration", dvals[4] == "on", vals[4] == "on", "none", "underline")
        st += fs("font-variant", dvals[5] == "on", vals[5] == "on", "none", "small-caps")
        st += fs("text-decoration", dvals[6] == "on", vals[6] == "on", "none", "line-through")
        st += fs("text-decoration-style", dvals[8] != "", vals[8] != "", "solid", vals[8])
        st += fs("-webkit-text-decoration-color", dvals[7] != "", vals[7] != "", "", vals[7])
        st += fs("text-decoration-color", dvals[7] != "", vals[7] != "", "", vals[7])
        return st.rstrip()

    def font_family(self, name: str, important: bool = False) -> str:
        websafe = {"Georgia": "serif", "Times New Roman": "serif", "Arial": "sans-serif",
                   "Trebuchet": "sans-serif", "Verdana": "sans-serif"}
        gf = self.ctx.data.google_fonts()
        if name in websafe:
            typ = websafe[name]
        elif name in gf:
            typ = gf[name]["category"]
            self.ctx.fonts.add(name)
        else:
            typ = None
        stack = {"sans-serif": "Helvetica, Arial, Lucida, sans-serif",
                 "serif": 'Georgia, "Times New Roman", serif', "cursive": "cursive"}.get(typ, typ) if typ else "sans-serif"
        ms = "'Trebuchet MS', " if name == "Trebuchet" else ""
        return f"font-family: '{name}', {ms}{stack}{' !important' if important else ''};"

    def process_fonts(self):
        fonts = self.af.get("fonts") or {}
        if not isinstance(fonts, dict):
            return
        p = self.props
        for opt, st in fonts.items():
            if not isinstance(st, dict):
                continue
            css = st.get("css") or {}
            imp_set = css.get("important")
            use_global_imp = imp_set == "all"
            imp_opts = imp_set if isinstance(imp_set, list) else []
            style, hover_style = "", ""

            def imp(k):
                return " !important" if (k in imp_opts or use_global_imp) else ""
            # font
            fv = p.get(f"{opt}_font", "")
            fdef = self.field_default(f"{opt}_font") or None
            if fv != "":
                style += self.font_decl(fv, imp("font") != "", fdef)
                style += " " if style and not style.endswith(" ") else ""
            # size
            sv = p.get(f"{opt}_font_size", "")
            size_val = ""
            if sv.strip() not in ("", "px", self.field_default(f"{opt}_font_size")):
                size_val = range_value(sv)
                style += f"font-size: {size_val}{imp('size')}; "
            hsz = hover_value(p, f"{opt}_font_size", "")
            if hsz and hsz not in ("px", size_val):
                hover_style += f"font-size: {range_value(hsz)}{imp('size')}; "
            # color
            color_sel = css.get("color", "")
            tc = p.get(f"{opt}_text_color", "")
            old_ref = (st.get("text_color") or {}).get("old_option_ref", "") if isinstance(st.get("text_color"), dict) else ""
            dflt_color = (st.get("text_color") or {}).get("default", "") if old_ref and p.get(old_ref, "") else ""
            if tc and not st.get("hide_text_color") and tc != dflt_color:
                if color_sel:
                    self.css(color_sel, f"color: {tc} !important;")
                else:
                    style += f"color: {tc} !important; "
            htc = hover_value(p, f"{opt}_text_color", "")
            if htc and not st.get("hide_text_color"):
                if color_sel:
                    self.css(css.get("color_hover") or add_hover_to_selectors(color_sel), f"color: {htc} !important;")
                else:
                    hover_style += f"color: {htc} !important; "
            # letter spacing
            ls = p.get(f"{opt}_letter_spacing", "")
            if ls.strip() not in ("", "px", self.field_default(f"{opt}_letter_spacing")):
                lsv = range_value(ls)
                style += f"letter-spacing: {lsv}{imp('letter-spacing')}; "
                if css.get("letter_spacing"):
                    self.css(css["letter_spacing"], f"letter-spacing: {lsv}{imp('letter-spacing')};")
            # line height
            lh = p.get(f"{opt}_line_height", "")
            if lh.strip() not in ("", "px", self.field_default(f"{opt}_line_height")):
                lhv = range_value(lh, "line_height")
                style += f"line-height: {lhv}{imp('line-height')}; "
                if css.get("line_height"):
                    self.css(css["line_height"], f"line-height: {lhv}{imp('line-height')};")
            hlh = hover_value(p, f"{opt}_line_height", "")
            if hlh:
                hover_style += f"line-height: {range_value(hlh, 'line_height')}{imp('line-height')}; "
            # text align
            ta = p.get(f"{opt}_text_align", "")
            if ta and not st.get("hide_text_align"):
                ta = {"justified": "justify", "force_left": "left"}.get(ta, ta)
                if css.get("text_align"):
                    self.css(css["text_align"], f"text-align: {ta}{imp('text-align')};")
                else:
                    style += f"text-align: {ta}{imp('text-align')}; "
            tss = p.get(f"{opt}_text_shadow_style", "")
            if tss and tss != "none":
                presets = {"preset1": ("0em", "0.1em", "0.1em"), "preset2": ("0.08em", "0.08em", "0.08em"),
                           "preset3": ("0em", "0em", "0.3em"), "preset4": ("0em", "0.08em", "0em"),
                           "preset5": ("0.08em", "0.08em", "0em")}
                h, v_, b_ = presets.get(tss, ("0em", "0.1em", "0.1em"))
                h = p.get(f"{opt}_text_shadow_horizontal_length", "") or h
                v_ = p.get(f"{opt}_text_shadow_vertical_length", "") or v_
                b_ = p.get(f"{opt}_text_shadow_blur_strength", "") or b_
                col = p.get(f"{opt}_text_shadow_color", "") or "rgba(0,0,0,0.4)"
                tmain = css.get("text_shadow") or css.get("main") or self.main
                self.css(tmain if isinstance(tmain, list) else [tmain], f"text-shadow: {h} {v_} {b_} {col};")
            main = css.get("main") or self.main
            for state, s in (("default", style), ("hover", hover_style)):
                if not s.strip():
                    continue
                sels = main if isinstance(main, list) else [main]
                for sel in sels:
                    if state == "hover":
                        sel = css.get("hover") or add_hover_to_order_class(sel)
                    self.css(sel, s)
            # responsive
            for mob in ("font", "font_size", "text_color", "line_height", "letter_spacing", "text_align"):
                for dev in ("tablet", "phone"):
                    name = f"{opt}_{mob}_{dev}"
                    v = p.get(name, "")
                    if v == "" or not resp_enabled(p, f"{opt}_{mob}"):
                        continue
                    prop = "color" if mob == "text_color" else mob.replace("_", "-")
                    important = imp("size" if prop == "font-size" else prop)
                    if mob == "text_color":
                        important = " !important"
                    if css.get(f"{mob}_{dev}"):
                        sel = css[f"{mob}_{dev}"]
                    elif mob == "text_color" and css.get("color"):
                        sel = css["color"]
                    elif css.get(mob) or css.get("main"):
                        sel = css.get(mob) or css["main"]
                    else:
                        sel = self.main
                    if mob in ("font_size", "line_height", "letter_spacing"):
                        v = range_value(v)
                    if mob == "font":
                        decl = self.font_decl(v, important != "", self.field_default(f"{opt}_font") or None)
                    elif mob == "text_align":
                        decl = f"text-align: {v}{important};"
                    else:
                        decl = f"{prop}: {v}{important};"
                    self.css(sel, decl, dev)

    def process_text_shadow(self):
        p = self.props
        styl = p.get("text_shadow_style", "")
        if styl and styl != "none":
            presets = {"preset1": ("0em", "0.1em", "0.1em"), "preset2": ("0.08em", "0.08em", "0.08em"),
                       "preset3": ("0em", "0em", "0.3em"), "preset4": ("0em", "0.08em", "0em"),
                       "preset5": ("0.08em", "0.08em", "0em")}
            h, v, b = presets.get(styl, ("0em", "0.1em", "0.1em"))
            h = p.get("text_shadow_horizontal_length", "") or h
            v = p.get("text_shadow_vertical_length", "") or v
            b = p.get("text_shadow_blur_strength", "") or b
            color = p.get("text_shadow_color", "") or "rgba(0,0,0,0.4)"
            txt = self.af.get("text") if isinstance(self.af.get("text"), dict) else {}
            sel = (txt.get("css") or {}).get("text_shadow") or self.main
            self.css(sel, f"text-shadow: {h} {v} {b} {color};")

    # background -----------------------------------------------------------------------
    def gradient(self, prefix: str = "background") -> str:
        p = self.props
        stops = p.get(f"{prefix}_color_gradient_stops", "") or "#2b87da 0%|#29c4a9 100%"
        typ = p.get(f"{prefix}_color_gradient_type", "") or "linear"
        direction = p.get(f"{prefix}_color_gradient_direction", "") or "180deg"
        radial = p.get(f"{prefix}_color_gradient_direction_radial", "") or "center"
        repeat = p.get(f"{prefix}_color_gradient_repeat", "") == "on"
        stop_css = ",".join(s.strip() for s in stops.split("|"))
        fn = ("repeating-" if repeat else "") + f"{typ}-gradient"
        if typ == "linear":
            return f"{fn}({direction},{stop_css})"
        rfn = ("repeating-" if repeat else "") + "radial-gradient"
        if typ in ("radial", "circular"):
            return f"{rfn}(circle at {radial},{stop_css})"
        if typ == "conic":
            return f"{'repeating-' if repeat else ''}conic-gradient(from {direction} at {radial},{stop_css})"
        return f"{rfn}(ellipse at {radial},{stop_css})"

    def process_background(self, prefix: str = "background", selector: str | None = None, important=None,
                           use_color=None):
        bg = self.af.get("background")
        if not isinstance(bg, dict):
            return
        p = self.props
        css = bg.get("css") or {}
        sel = selector or css.get("main") or self.main
        imp = " !important" if (important if important is not None else css.get("important") == "all") else ""
        use_color = bg.get("use_background_color", True) if use_color is None else use_color
        decls = []
        images = []
        if p.get(f"use_{prefix}_color_gradient", "") == "on" and p.get(f"{prefix}_enable_color_gradient", "on") != "off":
            images.append(("gradient", self.gradient(prefix)))
        img = p.get(f"{prefix}_image", "")
        if img and p.get(f"{prefix}_enable_image", "on") != "off" and p.get("parallax", "off") != "on":
            images.append(("image", f"url({html.escape(img, quote=False)})"))
        if images:
            if len(images) == 2 and p.get(f"{prefix}_color_gradient_overlays_image", "") != "on":
                images.reverse()
            decls.append(f"background-image: {', '.join(v for _, v in images)}{imp};")
            if img:
                posmap = {"top_left": "left top", "top_center": "center top", "top_right": "right top",
                          "center_left": "left center", "center_right": "right center", "bottom_left": "left bottom",
                          "bottom_center": "center bottom", "bottom_right": "right bottom"}
                for f, prop, d in (("size", "background-size", "cover"), ("position", "background-position", "center"),
                                   ("repeat", "background-repeat", "no-repeat")):
                    v = p.get(f"{prefix}_{f}", "") or d
                    if v != d:
                        decls.append(f"{prop}: {posmap.get(v, v) if f == 'position' else v};")
                blend = p.get(f"{prefix}_blend", "")
                if blend and blend != "normal":
                    decls.append(f"background-blend-mode: {blend};")
        color = p.get(f"{prefix}_color", "")
        if bg.get("has_background_color_toggle") and p.get("use_background_color", "on") == "off":
            color = ""
        if use_color is True and color and p.get(f"{prefix}_enable_color", "on") != "off":
            decls.append(f"background-color: {color}{imp};")
        if decls:
            self.css(sel, " ".join(decls))
        # hover color
        hc = hover_value(p, f"{prefix}_color")
        if use_color is True and hc:
            self.css(add_hover_to_order_class(sel), f"background-image: initial; background-color: {hc}{imp};")
        # mask
        if p.get(f"{prefix}_enable_mask_style", "") == "on" and bg.get("use_background_mask"):
            mstyle = p.get(f"{prefix}_mask_style", "") or "layer-blob"
            variant = "default"
            if p.get(f"{prefix}_mask_transform", ""):
                tr = p.get(f"{prefix}_mask_transform", "")
                variant = ("rotated" if "rotate" in tr else "default") + ("-inverted" if "invert" in tr else "")
            svg_inner = self.ctx.data.mask_svg(mstyle, variant, p.get(f"{prefix}_mask_aspect_ratio", "") or "landscape")
            if svg_inner is not None:
                color_m = p.get(f"{prefix}_mask_color", "") or "#ffffff"
                svg = (f'<svg  fill="{color_m}" viewBox="0 0 1920 1440" preserveAspectRatio="none" '
                       f'xmlns="http://www.w3.org/2000/svg">{svg_inner}</svg>')
                data = base64.b64encode(svg.encode()).decode()
                self.css(f"{sel} > .et_pb_background_mask", f"background-image: url(data:image/svg+xml;base64,{data});")
                self.mask_markup = '<span class="et_pb_background_mask"></span>'
            else:
                self.ctx.unsupported.setdefault("mask:" + mstyle, 0)
        if p.get(f"{prefix}_enable_pattern_style", "") == "on":
            self.ctx.unsupported["background_pattern"] = self.ctx.unsupported.get("background_pattern", 0) + 1

    mask_markup = ""

    # borders --------------------------------------------------------------------------
    def process_borders(self):
        p = self.props
        borders = self.af.get("borders")
        if borders is None:
            borders = {"default": {}}
        if not isinstance(borders, dict):
            return
        slug = self.render_slug or self.node.tag
        for bname, b in borders.items():
            if b is False or not isinstance(b, (dict, list)):
                continue
            b = b if isinstance(b, dict) else {}
            suf = "" if bname == "default" else f"_{bname}"
            main = ((b.get("css") or {}).get("main") or {}) if isinstance(b.get("css"), dict) else {}
            radii_sel = main.get("border_radii", self.main) if isinstance(main, dict) else self.main
            styles_sel = main.get("border_styles", self.main) if isinstance(main, dict) else self.main
            # radii (desktop + responsive)
            for dev in DEVICES:
                key = f"border_radii{suf}" + ("" if dev == "desktop" else f"_{dev}")
                r = p.get(key, "")
                if not r or (dev != "desktop" and not resp_enabled(p, f"border_radii{suf}")):
                    continue
                parts = (r.split("|") + [""] * 5)[:5]
                vals = [x or "0" for x in parts[1:5]]
                if all(v in ("0", "0px", "") for v in vals):
                    continue
                d = f"border-radius: {' '.join(vals)};"
                if slug not in ("et_pb_social_media_follow", "et_pb_menu"):
                    d += " overflow: hidden;"
                self.css(radii_sel, d, dev)
            # styles
            defaults = b.get("defaults", {}).get("border_styles", {}) if isinstance(b.get("defaults"), dict) else {}
            for dev in DEVICES:
                decl = ""
                allv = {}
                for prop in ("width", "style", "color"):
                    v = p.get(f"border_{prop}_all{suf}", "")
                    if dev != "desktop":
                        v = any_value(p, f"border_{prop}_all{suf}", dev) if resp_enabled(p, f"border_{prop}_all{suf}") else ""
                    allv[prop] = v
                    if v and v != defaults.get(prop, ""):
                        decl += f"border-{prop}: {v};"
                for edge in ("top", "right", "bottom", "left"):
                    for prop in ("width", "style", "color"):
                        k = f"border_{prop}_{edge}{suf}"
                        if dev == "desktop" or not resp_enabled(p, k):
                            v = dict.get(p, k, "")
                        else:
                            v = any_value(p, k, dev, "", True)
                        p.read.add(k)
                        if v:
                            decl += f"border-{edge}-{prop}: {v};"
                if decl:
                    self.css(styles_sel, decl, dev)
        if slug not in ("et_pb_accordion", "et_pb_accordion_item", "et_pb_pricing_table", "et_pb_tabs", "et_pb_toggle"):
            for k, v in self.attrs.items():
                if v and k.startswith("border_") and not k.startswith("border_radii") and k.count("_") > 1:
                    self.add_class("et_pb_with_border")
                    break

    # box shadow ------------------------------------------------------------------------
    PRESETS = {"preset1": ("0px", "2px", "18px", "0px", "outer"), "preset2": ("6px", "6px", "18px", "0px", "outer"),
               "preset3": ("0px", "12px", "18px", "-6px", "outer"), "preset4": ("10px", "10px", "0px", "0px", "outer"),
               "preset5": ("0px", "6px", "0px", "10px", "outer"), "preset6": ("0px", "0px", "18px", "0px", "inner"),
               "preset7": ("10px", "10px", "0px", "0px", "inner")}

    def box_shadow_value(self, suf: str = "", hover=False) -> str:
        p = self.props
        style = p.get(f"box_shadow_style{suf}", "")
        if not style or style == "none":
            return ""
        h, v, b, s, pos = self.PRESETS.get(style, ("0", "0", "0", "0", "outer"))

        def g(name, d):
            val = dict.get(p, f"box_shadow_{name}{suf}", "") or d
            p.read.add(f"box_shadow_{name}{suf}")
            if hover:
                hv = hover_value(p, f"box_shadow_{name}{suf}")
                if hv:
                    val = hv
            return val
        pos = "inset" if g("position", pos) == "inner" else ""
        val = f"box-shadow: {pos} {g('horizontal', h)} {g('vertical', v)} {g('blur', b)} {g('spread', s)} {g('color', 'rgba(0,0,0,0.3)')};"
        return val

    def process_box_shadow(self):
        bs = self.af.get("box_shadow", {"default": {}})
        if not isinstance(bs, dict):
            return
        for name, st in bs.items():
            if st is False:
                continue
            st = st if isinstance(st, dict) else {}
            css = st.get("css") or {}
            suf = "" if name == "default" else f"_{name}"
            show_if = css.get("show_if") or {}
            if any(self.props.get(k, "") != v for k, v in show_if.items()):
                continue
            if any(self.props.get(k, "") == v for k, v in (css.get("show_if_not") or {}).items()):
                continue
            val = self.box_shadow_value(suf)
            if not val:
                continue
            if css.get("important"):
                val = val.rstrip(";") + " !important;"
            sel = css.get("main", "%%order_class%%")
            self.css(sel, val)
            hv = self.box_shadow_value(suf, hover=True)
            if hv and hv != self.box_shadow_value(suf):
                hsel = add_hover_to_order_class(sel) if name == "default" else add_hover_to_selectors(sel)
                self.css(css.get("hover") or hsel, hv)
            if "inset" in val and css.get("overlay") == "inset":
                self.box_shadow_overlay = True

    box_shadow_overlay = False

    def process_overflow(self):
        ov = self.af.get("overflow")
        if not ov:
            return
        decl = ""
        for axis in ("overflow-x", "overflow-y"):
            v = self.props.get(axis, "")
            if v:
                decl += f"{axis}: {v};"
        self.css(self.main, decl)

    # margin / padding ------------------------------------------------------------------
    def process_custom_margin(self):
        mp = self.af.get("margin_padding")
        if not isinstance(mp, dict):
            return
        css = mp.get("css") or {}
        imp_cfg = css.get("important")
        p = self.props
        for kind, prop in (("custom_margin", "margin"), ("custom_padding", "padding")):
            if kind == "custom_margin" and mp.get("use_margin") is False:
                continue
            imp = imp_cfg == "all" or (isinstance(imp_cfg, list) and kind in imp_cfg)
            sel = css.get(prop) or css.get("main") or self.main
            prev_vals = None
            for dev in DEVICES:
                if dev == "desktop":
                    v = p.get(kind, "")
                else:
                    if not resp_enabled(p, kind):
                        continue
                    v = p.get(f"{kind}_{dev}", "") or (p.get(f"{kind}_tablet", "") if dev == "phone" else "")
                if not v:
                    continue
                vals = (v.split("|") + [""] * 4)[:4]
                decl = ""
                for side, val in zip(("top", "right", "bottom", "left"), vals):
                    if val != "":
                        decl += f"{prop}-{side}: {range_value(val) if val != 'auto' else 'auto'}{' !important' if imp else ''};"
                if decl:
                    self.css(sel, decl, dev)
            hv = hover_value(p, kind)
            if hv:
                vals = (hv.split("|") + [""] * 4)[:4]
                decl = "".join(f"{prop}-{s}: {x}{' !important' if imp else ''};" for s, x in zip(("top", "right", "bottom", "left"), vals) if x)
                if decl:
                    self.css(add_hover_to_order_class(sel), decl)

    # sizing -------------------------------------------------------------------------------
    def process_max_width(self):
        mw = self.af.get("max_width")
        if mw is False or mw is None:
            return
        mw = mw if isinstance(mw, dict) else {}
        css = mw.get("css") or {}
        p = self.props
        imp = " !important" if css.get("important") == "all" else ""
        opts = mw.get("options") or {}
        for prop, key in (("width", "width"), ("max-width", "max_width")):
            dflt = (opts.get(key) or {}).get("default", "") or self.field_default(key)
            for dev in DEVICES:
                v = any_value(p, key, dev) if dev != "desktop" else p.get(key, "")
                if dev != "desktop" and not resp_enabled(p, key):
                    continue
                if not v or v == dflt or v in ("auto", "none") and dev == "desktop":
                    continue
                sel = css.get(key) or css.get("main") or self.main
                self.css(sel, f"{prop}: {v}{imp};", dev)
        # module alignment (only meaningful with a width)
        al = p.get("module_alignment", "")
        if al and (p.get("max_width", "") or p.get("width", "")) and mw.get("use_module_alignment", True) is not False:
            sel = css.get("module_alignment") or f"{self.main}.et_pb_module"
            decl = {"left": "margin-left: 0px !important; margin-right: auto !important;",
                    "center": "margin-left: auto !important; margin-right: auto !important;",
                    "right": "margin-left: auto !important; margin-right: 0px !important;"}.get(al, "")
            self.css(sel, decl)

    # button (advanced) -------------------------------------------------------------------
    def process_button(self):
        btns = self.af.get("button")
        if not isinstance(btns, dict):
            return
        p = self.props
        slug = self.render_slug or self.node.tag
        for opt, st in btns.items():
            st = st if isinstance(st, dict) else {}
            css = st.get("css") or {}
            if st.get("use_alignment") and css.get("alignment"):
                for dev in DEVICES:
                    k = f"{opt}_alignment" + ("" if dev == "desktop" else f"_{dev}")
                    v = p.get(k, "")
                    if v and (dev == "desktop" or resp_enabled(p, f"{opt}_alignment")):
                        self.css(css["alignment"], f"text-align: {'left' if v == 'force_left' else v};", dev)
            if p.get(f"custom_{opt}", "") != "on":
                continue
            main = css.get("main") or f"{self.main} .et_pb_button"
            proc = prefix_selectors(main, "body #page-container .et_pb_section")
            tsize = p.get(f"{opt}_text_size", "")
            dflt_size = self.field_default(f"{opt}_text_size")
            is_default_size = "button_text_size" in self.fields and tsize in ("", self.field_default("button_text_size"))
            size_proc = "20px" if is_default_size else range_value(tsize or dflt_size or "20")
            use_icon = p.get(f"{opt}_use_icon", "") or "on"
            icon = p.get(f"{opt}_icon", "")
            placement = p.get(f"{opt}_icon_placement", "") or "right"
            on_hover = p.get(f"{opt}_on_hover", "")
            default_place = "button_icon_placement" in self.fields and dict.get(p, f"{opt}_icon_placement", "") in ("", self.field_default("button_icon_placement"))
            default_on_hover = "button_on_hover" in self.fields and dict.get(p, f"{opt}_on_hover", "") in ("", self.field_default("button_on_hover"))
            pad_name = "custom_padding" if slug == "et_pb_button" else f"{opt}_custom_padding"
            pad = (p.get(pad_name, "").split("|") + [""] * 4) if p.get(pad_name, "") else [""] * 4
            bw = p.get(f"{opt}_border_width", "")
            br = p.get(f"{opt}_border_radius", "")
            decl = ""
            tc = p.get(f"{opt}_text_color", "")
            if tc:
                decl += f"color:{tc} !important;"
            if bw and bw != "px":
                decl += f"border-width:{range_value(bw)} !important;"
            bc = p.get(f"{opt}_border_color", "")
            if bc:
                decl += f"border-color:{bc};"
            if br and br != "px":
                decl += f"border-radius:{range_value(br)};"
            lsp = p.get(f"{opt}_letter_spacing", "")
            if lsp and lsp != "px" and lsp != self.field_default(f"{opt}_letter_spacing"):
                decl += f"letter-spacing:{range_value(lsp)};"
            if not is_default_size:
                decl += f"font-size:{size_proc};"
            bf = p.get(f"{opt}_font", "")
            if bf:
                decl += self.font_decl(bf, True)
            if on_hover == "off" and not pad[1]:
                decl += f"padding-right: {'0.7em' if placement == 'left' else '2em'};"
            if on_hover == "off" and not pad[3]:
                decl += f"padding-left:{'2em' if placement == 'left' else '0.7em'};"
            # button background (button_bg_* fields)
            bgc = p.get(f"{opt}_bg_color", "")
            if bgc and p.get(f"{opt}_bg_enable_color", "on") != "off":
                decl += f"background-color:{bgc};"
            if p.get(f"{opt}_bg_use_color_gradient", "") == "on":
                decl += f"background-image:{self.gradient(opt + '_bg')};"
            self.css(proc, decl)
            # hover
            hdecl = ""
            for cssp, suffix in (("color", "text_color"), ("border-color", "border_color"), ("border-radius", "border_radius"),
                                 ("letter-spacing", "letter_spacing"), ("font-size", "text_size"), ("border-width", "border_width")):
                hv = hover_value(p, f"{opt}_{suffix}")
                if hv:
                    hdecl += f"{cssp}:{hv} !important;"
            if not default_place and on_hover != "off":
                hdecl += (f"padding-right: {'0.7em' if placement == 'left' else '2em'};"
                          f"padding-left: {'2em' if placement == 'left' else '0.7em'};")
            hbg = hover_value(p, f"{opt}_bg_color")
            if hbg:
                hdecl += f"background-image:initial;background-color:{hbg};"
            if hdecl:
                self.css(add_hover_to_selectors(proc), hdecl)
            pseudo = ":before" if placement == "left" else ":after"
            if use_icon == "off":
                self.css(f"{suffix_selectors(proc, ':before')}, {suffix_selectors(proc, ':after')}", "display:none !important;")
                nd = ""
                if not pad[1]:
                    nd += "padding-right: 1em !important;"
                if not pad[3]:
                    nd += "padding-left: 1em !important;"
                if not p.get(pad_name, ""):
                    nd = "padding: 0.3em 1em !important;"
                self.css(f"{proc}, {suffix_selectors(proc, ':hover')}", nd)
            else:
                ic_color = p.get(f"{opt}_icon_color", "")
                code = icon.split("|")[0].replace("&#x", "").replace(";", "") if icon else ""
                after = ""
                if ic_color:
                    after += f"color:{ic_color};"
                if code:
                    after += "line-height: inherit;font-size: inherit !important;"
                if not (default_on_hover and default_place):
                    after += f"opacity:{'0' if on_hover != 'off' else '1'};"
                if on_hover != "off" and code:
                    after += f"margin-left: {'-1.3em' if placement == 'left' else '-1em'}; {'right' if placement == 'left' else 'left'}: auto;"
                if on_hover == "off":
                    after += f"margin-left: {'-1.3em' if placement == 'left' else '.3em'}; {'right' if placement == 'left' else 'left'}:auto;"
                if not default_place:
                    after += "display: inline-block;"
                if icon:
                    fam, w = icon_font(icon)
                    after += f" font-family: {fam} !important; font-weight: {w} !important;"
                sel_after = suffix_selectors(proc, pseudo)
                self.css(sel_after, after)
                if placement == "left":
                    self.css(suffix_selectors(proc, ":after"), "display: none;")
                    if code:
                        fam, w = icon_font(icon)
                        self.css(suffix_selectors(proc, ":before"), f"content: attr(data-icon); font-family: {fam} !important; font-weight: {w} !important;")
                if not (icon == "" and default_on_hover and default_place):
                    h = ""
                    if code:
                        h += f"margin-left:{'.3em' if code != '35' else '0'};{'right' if placement == 'left' else 'left'}: auto; margin-left: {'-1.3em' if placement == 'left' else '.3em'};"
                    if on_hover != "off":
                        h += "opacity: 1;"
                    self.css(suffix_selectors(suffix_selectors(proc, ":hover"), pseudo), h)
                if icon == "" and not is_default_size:
                    self.css(suffix_selectors(proc, pseudo), "font-size:1.6em;")
                    self.css(f"body.et_button_custom_icon #page-container {main}{pseudo}", f"font-size:{size_proc};")
                # responsive: Divi re-emits the hover-reveal rules for tablet/phone
                for dev in ("tablet", "phone"):
                    rdecl = ""
                    for cssp, suffix, imp in (("font-size", "text_size", " !important"), ("letter-spacing", "letter_spacing", ""),
                                              ("color", "text_color", " !important"), ("border-width", "border_width", " !important"),
                                              ("border-color", "border_color", ""), ("border-radius", "border_radius", "")):
                        if resp_enabled(p, f"{opt}_{suffix}"):
                            v = p.get(f"{opt}_{suffix}_{dev}", "")
                            if v:
                                rdecl += f"{cssp}:{range_value(v) if cssp not in ('color', 'border-color') else v}{imp};"
                    if rdecl:
                        self.css(proc, rdecl, dev)
                    cur_place = any_value(p, f"{opt}_icon_placement", dev, placement, True) if resp_enabled(p, f"{opt}_icon_placement") else placement
                    cur_on_hover = on_hover
                    rafter = ""
                    if code:
                        rafter += "line-height: inherit;font-size: inherit !important;"
                    if cur_on_hover != "off" and code:
                        rafter += f"margin-left: {'-1.3em' if cur_place == 'left' else '-1em'}; {'right' if cur_place == 'left' else 'left'}: auto;"
                    if cur_on_hover == "off":
                        rafter += f"margin-left: {'-1.3em' if cur_place == 'left' else '.3em'}; {'right' if cur_place == 'left' else 'left'}: auto;"
                    rafter += "display: inline-block;"
                    rafter += "opacity: 0;" if cur_on_hover != "off" else "opacity: 1;"
                    self.css(suffix_selectors(proc, pseudo), rafter, dev)
                    if code:
                        hide, show = (":after", ":before") if cur_place == "left" else (":before", ":after")
                        fam, w = icon_font(icon)
                        self.css(suffix_selectors(proc, hide), "display: none;", dev)
                        self.css(suffix_selectors(proc, show), f"content: attr(data-icon); font-family: {fam} !important; font-weight: {w} !important;", dev)
                    if not (icon == "" and default_on_hover and default_place and False):
                        rh = ""
                        if code:
                            rh += f"margin-left:.3em;{'right' if cur_place == 'left' else 'left'}: auto; margin-left: {'-1.3em' if cur_place == 'left' else '.3em'};"
                        if cur_on_hover != "off":
                            rh += "opacity: 1;"
                        self.css(suffix_selectors(suffix_selectors(proc, ":hover"), pseudo), rh, dev)
            # button custom padding
            if slug != "et_pb_button":
                mp = (st.get("margin_padding") or {}) if isinstance(st.get("margin_padding"), dict) else {}
                mpcss = mp.get("css") or {}
                psel = mpcss.get("main") or proc
                psel = prefix_selectors(psel, "body #page-container .et_pb_section") if mpcss.get("main") else psel
                v = p.get(pad_name, "")
                if v:
                    vals = (v.split("|") + [""] * 4)[:4]
                    decl = "".join(f"padding-{s}:{x}!important;" for s, x in zip(("top", "right", "bottom", "left"), vals) if x)
                    self.css(psel, decl)

    def process_transitions(self):
        """process_hover_transitions(): one transition rule over the selectors of hover-enabled props."""
        p = self.props
        hovered = [k[:-len("__hover_enabled")] for k in self.attrs if k.endswith("__hover_enabled")
                   and self.attrs[k].startswith("on")]
        fonts = self.af.get("fonts") if isinstance(self.af.get("fonts"), dict) else {}
        btns = self.af.get("button") if isinstance(self.af.get("button"), dict) else {}
        props, sels = [], []
        for k in hovered:
            sel = self.main
            if k.startswith("box_shadow"):
                prop = "box-shadow"
            elif k.endswith("bg_color") or k == "background_color":
                prop = "background-color"
            elif k.endswith("text_color"):
                prop = "color"
            elif k.startswith("custom_padding"):
                prop = "padding"
            else:
                continue
            for opt, st in fonts.items():
                if isinstance(st, dict) and k == f"{opt}_text_color":
                    css = st.get("css") or {}
                    sel = css.get("color") or css.get("main") or self.main
            for opt, st in btns.items():
                if isinstance(st, dict) and k.startswith(opt + "_") and (self.render_slug or self.node.tag) != "et_pb_button":
                    sel = (st.get("css") or {}).get("main") or sel
            props.append(prop)
            sels.append(sel if isinstance(sel, str) else ", ".join(sel))
        props = sorted(set(props), key=props.index)
        if props:
            dur = p.get("hover_transition_duration", "") or "300ms"
            curve = p.get("hover_transition_speed_curve", "") or "ease"
            delay = p.get("hover_transition_delay", "") or "0ms"
            usels = ", ".join(sorted(set(sels), key=sels.index))
            self.css(usels, "transition:" + ",".join(f"{x} {dur} {curve} {delay}" for x in props) + ";")

    # -- rendering
    def render(self) -> str:
        return ""


# ----------------------------------------------------------------------------- structure
class Section(Module):
    slug = "et_pb_section"

    def render(self):
        p = self.props
        self.process_additional()
        bgc = property_values(p, "background_color")
        for dev in DEVICES:
            if bgc[dev] and bgc[dev] != "rgba(255,255,255,0)" and p.get("background_enable_color", "on") != "off":
                self.css("%%order_class%%.et_pb_section", f"background-color: {bgc[dev]} !important;", dev)
        hbg = hover_value(p, "background_color")
        if hbg:
            self.css("%%order_class%%.et_pb_section:hover", f"background-color:{hbg} !important;")
        self.add_class("et_pb_section", self.order_class)
        bgc_any = p.get("background_color", "") and p.get("background_color", "") != "rgba(255,255,255,0)"
        if bgc_any or p.get("background_image", "") or p.get("background_video_mp4", ""):
            self.add_class("et_pb_with_background")
        fullwidth = p.get("fullwidth", "") == "on"
        specialty = p.get("specialty", "") == "on"
        if fullwidth:
            self.add_class("et_pb_fullwidth_section")
        self.add_class("et_section_specialty" if specialty else "et_section_regular")
        for pl in ("top", "bottom"):
            if p.get(f"{pl}_divider_style", "") not in ("", "none"):
                self.ctx.unsupported["section_divider"] = self.ctx.unsupported.get("section_divider", 0) + 1
        prev = self.ctx.specialty
        self.ctx.specialty = specialty
        inner = self.content_html()
        self.ctx.specialty = prev
        mid = inner
        if specialty:
            gutter = f" et_pb_gutters{p.get('gutter_width')}" if p.get("use_custom_gutter", "") == "on" and p.get("gutter_width", "") else ""
            mid = f'<div class="et_pb_row{gutter}">\n\t\t\t\t{inner}\n\t\t\t\t</div>'
        return (f'<div class="{self.classname()}" >\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t\n\t\t\t\t{mid}\n\t\t\t\t\n\t\t\t\t\n\t\t\t</div>')


class Row(Module):
    slug = "et_pb_row"

    def render(self):
        p = self.props
        self.process_additional()
        self.add_class("et_pb_row", self.order_class)
        if p.get("make_equal", "") == "on":
            self.add_class("et_pb_equal_columns")
        if p.get("use_custom_gutter", "") == "on" and p.get("gutter_width", ""):
            g = p.get("gutter_width")
            self.add_class(f"et_pb_gutters{'1' if g == '0' else g}")
        self.ctx.row_cols = [c for c in self.node.modules]
        inner = self.content_html()
        return (f'<div class="{self.classname()}">\n\t\t\t\t{inner}\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t\n\t\t\t</div>')

    def process_custom_margin(self):
        super().process_custom_margin()
        # Row render() re-emits responsive padding without !important (structure-element quirk)
        p = self.props
        if resp_enabled(p, "custom_padding") and p.get("custom_padding", ""):
            vals = (p.get("custom_padding").split("|") + [""] * 4)[:4]
            decl = "".join(f"padding-{s}: {range_value(x)};" for s, x in zip(("top", "right", "bottom", "left"), vals) if x)
            self.css("%%order_class%%.et_pb_row", decl)

    def process_max_width(self):
        # rows: width/max-width with Divi's long selector list; %%row_selector%% removed
        p = self.props
        mw = self.af.get("max_width") or {}
        css = mw.get("css") or {}
        for prop, key, dflt in (("width", "width", "80%"), ("max-width", "max_width", "1080px")):
            v = p.get(key, "")
            if v and v != dflt:
                sel = css.get(key, "%%order_class%%").replace(", %%row_selector%%",
                                                                ", body.et_pb_pagebuilder_layout.single.et_full_width_page #page-container #et-boc .et-l %%order_class%%.et_pb_row")
                self.css(sel, f"{prop}: {v};")
        al = p.get("module_alignment", "")
        if al:
            decl = {"left": "margin-left: 0px !important; margin-right: auto !important;",
                    "center": "margin-left: auto !important; margin-right: auto !important;",
                    "right": "margin-left: auto !important; margin-right: 0px !important;"}.get(al, "")
            self.css("%%order_class%%.et_pb_row", decl)


class RowInner(Row):
    slug = "et_pb_row_inner"
    process_max_width = Module.process_max_width

    def render(self):
        self.process_additional()
        self.add_class("et_pb_row_inner", self.order_class)
        inner = self.content_html()
        return (f'<div class="{self.classname()}">\n\t\t\t\t{inner}\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t\n\t\t\t</div>')


class Column(Module):
    slug = "et_pb_column"

    def render(self):
        p = self.props
        inner_col = self.node.tag == "et_pb_column_inner"
        self.process_additional()
        typ = p.get("type", "") or "4_4"
        if inner_col:
            if typ == "1_1":
                typ = "4_4"
            sct = p.get("saved_specialty_column_type", "") or self.ctx.specialty_col_type
            typ = {"1_2": {"1_2": "1_4", "1_3": "1_6"}, "2_3": {"1_3": "2_9", "1_2": "1_3", "1_4": "1_6"},
                   "3_4": {"1_2": "3_8", "1_3": "1_4"}}.get(sct, {}).get(typ, typ)
        siblings = self.parent.node.modules if self.parent else [self.node]
        is_last = siblings and siblings[-1] is self.node
        cls = ["et_pb_column", f"et_pb_column_{typ}", self.order_class]
        if inner_col:
            cls = ["et_pb_column", f"et_pb_column_{typ}", "et_pb_column_inner", self.order_class]
        else:
            if self.ctx.specialty:
                cls.append("  " + ("et_pb_specialty_column " if p.get("specialty_columns", "") else "") + " et_pb_css_mix_blend_mode_passthrough"
                           if p.get("specialty_columns", "") else "   et_pb_css_mix_blend_mode_passthrough")
            else:
                cls.append(" et_pb_css_mix_blend_mode_passthrough")
        if is_last:
            cls.append("et-last-child")
        if "et_pb_with_border" in self.classes:   # add_classname('et_pb_column_' . $type, 1) lands after it
            cls = ["et_pb_with_border", cls[1], cls[0]] + cls[2:]
        self.classes = cls
        prev = self.ctx.specialty_col_type
        if not inner_col and self.ctx.specialty:
            self.ctx.specialty_col_type = typ
        inner = self.content_html()
        self.ctx.specialty_col_type = prev
        empty = " et_pb_column_empty" if not inner.strip() else ""
        return (f'<div class="{self.classname()}{empty}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t{inner}\n\t\t\t</div>')

    def classname(self):
        return " ".join(self.classes)


# ----------------------------------------------------------------------------- modules
def module_wrap(m: Module, inner: str, extra_attrs: str = "", tag: str = "div") -> str:
    return (f'<{tag} class="{m.classname()}"{extra_attrs}>\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{m.mask_markup}\n'
            f'\t\t\t\t{inner}\n\t\t\t</{tag}>')


def base_classes(m: Module, slug: str | None = None):
    pre = [c for c in m.classes if c == "et_pb_with_border"]
    m.classes = pre + ["et_pb_module", slug or m.node.tag, m.order_class]
    mc = m.props.get("module_class", "")
    if mc:
        m.classes += mc.split()
    anim = m.props.get("animation_style", "")
    if anim and anim != "none":
        m.classes.append("et_animated")
    if any(k.endswith("__hover_enabled") and v == "on" for k, v in m.attrs.items()):
        m.classes.append("et_hover_enabled")


class Heading(Module):
    slug = "et_pb_heading"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        self.add_class(f"et_pb_bg_layout_{p.get('background_layout', '')}")
        lvl = p.get("title_level", "") or "h1"
        title = f'<{lvl} class="et_pb_module_heading">{p.get("title")}</{lvl}>'
        if p.get("url", ""):
            title = f'<a href="{esc_url(p.get("url"))}"{new_window(p)}>{title}</a>'
        return module_wrap(self, f'<div class="et_pb_heading_container">{title}</div>')


class TextMod(Module):
    slug = "et_pb_text"

    def render(self):
        p = self.props
        self.process_additional()
        for kind in ("ul", "ol"):
            for attr, prop, imp in ((f"{kind}_type", "list-style-type", True), (f"{kind}_position", "list-style-position", kind == "ol"),
                                    (f"{kind}_item_indent", "padding-left", True)):
                vals = property_values(p, attr)
                for dev in DEVICES:
                    if vals[dev]:
                        self.css(f"%%order_class%% {kind}", f"{prop}: {vals[dev]}{' !important' if imp else ''};", dev)
        self.generate_styles("quote_border_weight", "%%order_class%% blockquote", "border-width", typ="range", hover_loc="suffix")
        self.generate_styles("quote_border_color", "%%order_class%% blockquote", "border-color", hover_loc="suffix")
        base_classes(self)
        self.add_class(self.text_orientation_class(), self.bg_layout_class())
        content = module_content(self.node)
        return module_wrap(self, f'<div class="et_pb_text_inner">{content}</div>')


class Button(Module):
    slug = "et_pb_button"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        url, text = p.get("button_url", "").strip(), p.get("button_text", "")
        if not url and not text:
            return ""
        al = []
        a = p.get("button_alignment", "")
        if a:
            al.append(f"et_pb_button_alignment_{a}")
        for dev in ("tablet", "phone"):
            v = p.get(f"button_alignment_{dev}", "") if resp_enabled(p, "button_alignment") else ""
            if v:
                al.append(f"et_pb_button_alignment_{dev}_{v}")
        self.classes = [c for c in self.classes if c != "et_pb_module"]
        self.add_class(self.bg_layout_class())
        cls = "et_pb_button " + self.classname().replace("et_pb_button ", "", 1)
        icon = p.get("button_icon", "")
        data_icon = f' data-icon="{esc(decode_icon(icon))}"' if icon and p.get("custom_button") == "on" else ""
        target = ' target="_blank"' if p.get("url_new_window", "") == "on" else ""
        rel = ""
        if p.get("button_rel", ""):
            rels = [r for r, on in zip(("bookmark", "external", "nofollow", "noreferrer", "noopener"), p.get("button_rel").split("|")) if on == "on"]
            rel = f' rel="{" ".join(rels)}"' if rels else ""
        btn = f'<a class="{cls}" href="{esc_url(url)}"{target}{rel}{data_icon}>{text}</a>'
        self.css("%%order_class%%, %%order_class%%:after", "transition: all 300ms ease 0ms;")
        return (f'<div class="et_pb_button_module_wrapper {self.order_class}_wrapper {" ".join(al)} et_pb_module ">\n'
                f'\t\t\t\t{btn}\n\t\t\t</div>')

    def process_custom_margin(self):
        p = self.props
        for kind, prop in (("custom_margin", "margin"), ("custom_padding", "padding")):
            sel = "%%order_class%%_wrapper" if prop == "margin" else "%%order_class%%_wrapper %%order_class%%, %%order_class%%_wrapper %%order_class%%:hover"
            for dev in DEVICES:
                v = p.get(kind, "") if dev == "desktop" else (p.get(f"{kind}_{dev}", "") if resp_enabled(p, kind) else "")
                if not v:
                    continue
                vals = (v.split("|") + [""] * 4)[:4]
                decl = "".join(f"{prop}-{s}: {x} !important;" for s, x in zip(("top", "right", "bottom", "left"), vals) if x)
                self.css(sel, decl, dev)
            hv = hover_value(p, kind)
            if hv:
                vals = (hv.split("|") + [""] * 4)[:4]
                decl = "".join(f"{prop}-{s}: {x} !important;" for s, x in zip(("top", "right", "bottom", "left"), vals) if x)
                self.css("%%order_class%%_wrapper %%order_class%%:hover", decl)


class Image(Module):
    slug = "et_pb_image"

    def render(self):
        p = self.props
        self.process_additional()
        if p.get("force_fullwidth", "") == "on":
            self.css("%%order_class%%", "width: 100%; max-width: 100% !important;")
            self.css("%%order_class%% .et_pb_image_wrap, %%order_class%% img", "width: 100%;")
        al = property_values(p, "align")
        align = p.get("align", "") or "left"
        margins = {"left": "margin-left: 0;", "center": "", "right": "margin-right: 0;"}
        self.css("%%order_class%%", f"text-align: {align}; {margins.get(align, '')}")
        for dev in ("tablet", "phone"):
            if al[dev]:
                self.css("%%order_class%%", f"text-align: {al[dev]}; {margins.get(al[dev], '')}", dev)
            self.css("%%order_class%% .et_pb_image_wrap img", "width: auto;", dev)
        base_classes(self)
        has_bs = self.box_shadow_value() != ""
        overlay_div = '<div class="box-shadow-overlay"></div>' if has_bs else ""
        wrap_cls = "has-box-shadow-overlay" if has_bs else ""
        title = f' title="{esc(p.get("title_text", ""))}"'
        img = f'<img decoding="async" src="{esc_url(p.get("src"))}" alt="{esc(p.get("alt", ""))}"{title} />'
        out = f'<span class="et_pb_image_wrap {wrap_cls}">{overlay_div}{img}</span>'
        if p.get("url", ""):
            out = f'<a href="{esc_url(p.get("url"))}"{new_window(p)}>{out}</a>'
        return module_wrap(self, out)


class Blurb(Module):
    slug = "et_pb_blurb"

    def render(self):
        p = self.props
        self.process_additional()
        use_icon = p.get("use_icon", "") == "on"
        placement = p.get("icon_placement", "") or "top"
        if placement == "top":
            al = p.get("icon_alignment", "")
            if resp_enabled(p, "icon_alignment"):
                vals = property_values(p, "icon_alignment")
                for dev in DEVICES:
                    if vals[dev]:
                        self.css("%%order_class%% .et_pb_blurb_content", f"text-align: {vals[dev]};", dev)
            elif al in ("left", "right"):
                self.css("%%order_class%% .et_pb_blurb_content", f"text-align: {al};")
                if not use_icon:
                    self.css("%%order_class%%.et_pb_blurb .et_pb_image_wrap",
                             f"margin: {'auto auto auto 0' if al == 'left' else 'auto 0 auto auto'};")
        if use_icon:
            self.generate_styles("image_icon_width", "%%order_class%% .et-pb-icon", "font-size", typ="range")
        else:
            w = p.get("image_icon_width", "")
            if w:
                self.css("%%order_class%% .et_pb_main_blurb_image .et_pb_image_wrap", f"{'width' if 'px' in w else 'max-width'}: {w};")
        cmw = property_values(p, "content_max_width")
        for dev in DEVICES:
            if cmw[dev]:
                self.css("%%order_class%% .et_pb_blurb_content", f"max-width: {cmw[dev]};", dev)
        self.generate_styles("image_icon_background_color",
                             "%%order_class%% .et_pb_main_blurb_image .et_pb_only_image_mode_wrap, %%order_class%% .et_pb_main_blurb_image .et-pb-icon",
                             "background-color")
        # image/icon custom margin & padding (advanced_fields.image_icon)
        for kind, prop in (("image_icon_custom_margin", "margin"), ("image_icon_custom_padding", "padding")):
            v = p.get(kind, "")
            if v:
                vals = (v.split("|") + [""] * 4)[:4]
                decl = "".join(f"{prop}-{s}: {x} !important;" for s, x in zip(("top", "right", "bottom", "left"), vals) if x)
                self.css("%%order_class%% .et_pb_main_blurb_image .et_pb_only_image_mode_wrap, %%order_class%% .et_pb_main_blurb_image .et-pb-icon", decl)
        anim = p.get("animation", "") or "top"
        img_classes = ["et-waypoint", f"et_pb_animation_{anim}", f"et_pb_animation_{anim}_tablet", f"et_pb_animation_{anim}_phone"]
        image = ""
        if use_icon:
            self.generate_styles("icon_color", "%%order_class%% .et-pb-icon", "color")
            img_classes.append("et-pb-icon")
            if p.get("border_radii_image", "") == "on|100%|100%|100%|100%" or p.get("use_circle", "") == "on":
                img_classes.append("et-pb-icon-circle")
            icon = p.get("font_icon", "")
            if icon:
                fam, w = icon_font(icon)
                self.css("%%order_class%% .et-pb-icon", f"font-family: {fam} !important; font-weight: {w} !important;")
            image = f'<span class="{" ".join(img_classes)}">{esc(decode_icon(icon)) if icon else ""}</span>'
            image = f'<span class="et_pb_image_wrap">{image}</span>'
        elif p.get("image", ""):
            image = f'<img decoding="async" src="{esc_url(p.get("image"))}" alt="{esc(p.get("alt", ""))}" class="{" ".join(img_classes)}" />'
            image = f'<span class="et_pb_image_wrap et_pb_only_image_mode_wrap">{image}</span>'
        if image:
            if p.get("url", ""):
                image = f'<a href="{esc_url(p.get("url"))}">{image}</a>'
            image = f'<div class="et_pb_main_blurb_image">{image}</div>'
        base_classes(self)
        self.add_class(self.text_orientation_class(), f" et_pb_blurb_position_{placement}", self.bg_layout_class())
        lvl = p.get("header_level", "") or "h4"
        tt = f'<a href="{esc_url(p.get("url"))}">{p.get("title")}</a>' if p.get("url", "") else f'<span>{p.get("title")}</span>'
        title = f'<{lvl} class="et_pb_module_header">{tt}</{lvl}>' if p.get("title", "") else ""
        content = module_content(self.node)
        inner = (f'<div class="et_pb_blurb_content">\n\t\t\t\t\t{image}\n\t\t\t\t\t<div class="et_pb_blurb_container">\n'
                 f'\t\t\t\t\t\t{title}\n\t\t\t\t\t\t<div class="et_pb_blurb_description">{content}</div>\n'
                 f'\t\t\t\t\t</div>\n\t\t\t\t</div>')
        return module_wrap(self, inner)


class Accordion(Module):
    slug = "et_pb_accordion"

    def render(self):
        p = self.props
        self.process_additional()
        self.generate_styles("open_toggle_background_color", "%%order_class%% .et_pb_toggle_open", "background-color")
        self.generate_styles("closed_toggle_background_color", "%%order_class%% .et_pb_toggle_close", "background-color")
        hl = ["h5", "h1", "h2", "h3", "h4", "h6"]
        self.generate_styles("open_toggle_text_color", ", ".join(f"%%order_class%%.et_pb_accordion .et_pb_toggle_open {h}.et_pb_toggle_title" for h in hl), "color", important=True)
        self.generate_styles("closed_toggle_text_color", ", ".join(f"%%order_class%%.et_pb_accordion .et_pb_toggle_close {h}.et_pb_toggle_title" for h in hl), "color", important=True)
        if p.get("use_icon_font_size", "") == "on":
            self.generate_styles("icon_font_size", "%%order_class%% .et_pb_toggle_title:before", "font-size", typ="range", hover_loc="suffix")
        self.generate_styles("icon_color", "%%order_class%% .et_pb_toggle_title:before", "color", hover_loc="suffix", skip_default=True)
        icon = p.get("toggle_icon", "")
        if icon:
            fam, w = icon_font(icon)
            self.css("%%order_class%% .et_pb_toggle_title:before", f"font-family: {fam} !important; font-weight: {w} !important; content: {icon_css_content(icon)} !important;")
        base_classes(self)
        self.add_class(self.text_orientation_class() if dict.get(p, "text_orientation") else "")
        self.ctx.accordion = self
        self.ctx.acc_first_open = None
        inner = self.content_html()
        return module_wrap(self, inner)


class AccordionItem(Module):
    slug = "et_pb_accordion_item"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self, "et_pb_accordion_item")
        self.classes = ["et_pb_toggle", "et_pb_module", "et_pb_accordion_item", self.order_class]
        acc = getattr(self.ctx, "accordion", None)
        siblings = acc.node.modules if acc else [self.node]
        any_open = next((i for i, s in enumerate(siblings) if s.value("open") == "on"), 0)
        idx = next(i for i, s in enumerate(siblings) if s is self.node)
        self.add_class(" et_pb_toggle_open" if idx == any_open else " et_pb_toggle_close")
        lvl = (acc.props.get("toggle_level", "") if acc else "") or "h5"
        content = module_content(self.node)
        return (f'<div class="{" ".join(self.classes)}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t<{lvl} class="et_pb_toggle_title">{p.get("title")}</{lvl}>\n'
                f'\t\t\t\t<div class="et_pb_toggle_content clearfix">{content}</div>\n\t\t\t</div>')


class Toggle(AccordionItem):
    slug = "et_pb_toggle"

    def render(self):
        p = self.props
        self.process_additional()
        hl = ["h5", "h1", "h2", "h3", "h4", "h6"]
        for state in ("open", "close"):
            key = "open" if state == "open" else "closed"
            self.generate_styles(f"{key}_toggle_background_color", f"%%order_class%%.et_pb_toggle.et_pb_toggle_{state}",
                                 "background-color", hover_loc="suffix")
            self.generate_styles(f"{key}_toggle_text_color",
                                 ", ".join(f"%%order_class%%.et_pb_toggle.et_pb_toggle_{state} {h}.et_pb_toggle_title" for h in hl),
                                 "color", important=True, hover_loc="suffix")
        self.generate_styles("open_icon_color", "%%order_class%%.et_pb_toggle_open .et_pb_toggle_title:before", "color", skip_default=True)
        self.generate_styles("icon_color", "%%order_class%%.et_pb_toggle_close .et_pb_toggle_title:before", "color", skip_default=True)
        base_classes(self)
        self.classes = ["et_pb_module", "et_pb_toggle", self.order_class, "et_pb_toggle_item",
                        "et_pb_toggle_open" if p.get("open", "") == "on" else "et_pb_toggle_close"]
        lvl = p.get("toggle_level", "") or "h5"
        content = module_content(self.node)
        return (f'<div class="{" ".join(self.classes)}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t<{lvl} class="et_pb_toggle_title">{p.get("title")}</{lvl}>\n'
                f'\t\t\t\t<div class="et_pb_toggle_content clearfix">{content}</div>\n\t\t\t</div>')


class NumberCounter(Module):
    slug = "et_pb_number_counter"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        self.add_class(self.text_orientation_class(), self.bg_layout_class())
        if p.get("title", ""):
            self.add_class("et_pb_with_title")
        lvl = p.get("title_level", "") or "h3"
        title = f'<{lvl} class="title">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        sign = "%" if p.get("percent_sign", "") == "on" else ""
        sep = p.get("number_separator", "") if p.get("use_number_separator", "") == "on" else ""
        return (f'<div class="{self.classname()}" data-number-value="{esc(p.get("number"))}" data-number-separator="{sep}">\n'
                f'\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t<div class="percent" ><p><span class="percent-value"></span><span class="percent-sign">{sign}</span></p></div>\n'
                f'\t\t\t\t{title}\n\t\t\t</div>')


class Divider(Module):
    slug = "et_pb_divider"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        show = p.get("show_divider", "") != "off"
        pos = p.get("divider_position", "") if show else ""
        self.add_class(f"et_pb_divider_position_{dict.get(p, 'divider_position', '') if 'divider_position' in self.attrs else ''}")
        if show:
            self.generate_styles("color", "%%order_class%%:before", "border-top-color")
            self.generate_styles("divider_weight", "%%order_class%%:before", "border-top-width", typ="range")
            st = p.get("divider_style", "")
            if st and st != "solid":
                self.css("%%order_class%%:before", f"border-top-style: {st};")
        self.add_class("et_pb_space")
        if not show:
            self.add_class("et_pb_divider_hidden")
        for dev in DEVICES:
            v = p.get("height", "") if dev == "desktop" else (p.get(f"height_{dev}", "") if resp_enabled(p, "height") else "")
            if v and v != "auto":
                self.css("%%order_class%%", f"height: {v};", dev)
        for dev in DEVICES:
            v = p.get("max_height", "") if dev == "desktop" else ""
            if v and v != "none":
                self.css("%%order_class%%", f"max-height: {v};", dev)
        return f'<div class="{self.classname()}"><div class="et_pb_divider_internal"></div></div>'


class Cta(Module):
    slug = "et_pb_cta"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        self.classes = [c for c in self.classes if c != "et_pb_cta"] + ["et_pb_promo"]
        self.add_class(self.text_orientation_class(), self.bg_layout_class())
        if p.get("use_background_color", "on") == "off":
            self.add_class("et_pb_no_bg")
        lvl = p.get("header_level", "") or "h2"
        title = f'<{lvl} class="et_pb_module_header">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        content = module_content(self.node)
        btn = ""
        if p.get("button_text", "") or p.get("button_url", ""):
            btn = (f'<div class="et_pb_button_wrapper"><a class="et_pb_button et_pb_promo_button" href="{esc_url(p.get("button_url"))}">'
                   f'{p.get("button_text")}</a></div>')
        inner = (f'<div class="et_pb_promo_description">{title}<div>{content}</div></div>\n\t\t\t\t{btn}')
        return module_wrap(self, inner)


class Slider(Module):
    slug = "et_pb_slider"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        self.add_class("et_pb_slider_fullwidth_off")
        if p.get("show_arrows", "") == "off":
            self.add_class("et_pb_slider_no_arrows")
        if p.get("show_pagination", "") == "off":
            self.add_class("et_pb_slider_no_pagination")
        if p.get("auto", "") == "on":
            self.add_class("et_slider_auto", f"et_slider_speed_{p.get('auto_speed', '') or '7000'}")
        arrows = ".et_pb_slider %%order_class%% .et-pb-slider-arrows .et-pb-arrow-prev, .et_pb_slider %%order_class%% .et-pb-slider-arrows .et-pb-arrow-next"
        dots = ".et_pb_slider %%order_class%% .et-pb-controllers a, .et_pb_slider %%order_class%% .et-pb-controllers .et-pb-active-control"
        # Divi: generate_responsive_hover_style with et_pb_slider_options() selectors (no prefix)
        arrows = "%%order_class%% .et-pb-slider-arrows .et-pb-arrow-prev, %%order_class%% .et-pb-slider-arrows .et-pb-arrow-next"
        dots = "%%order_class%% .et-pb-controllers a, %%order_class%% .et-pb-controllers .et-pb-active-control"
        for attr, sel, prop in (("arrows_custom_color", arrows, "color"), ("dot_nav_custom_color", dots, "background-color")):
            vals = property_values(p, attr)
            for dev in DEVICES:
                if vals[dev]:
                    self.css(sel, f"{prop}: {vals[dev]};", dev)
        self.ctx.slider = self
        self.ctx.slide_num = 0
        inner = self.content_html()
        self.ctx.slider = None
        return (f'<div class="{self.classname()}">\n\t\t\t\t<div class="et_pb_slides">\n\t\t\t\t\t{inner}\n\t\t\t\t</div>\n'
                f'\t\t\t\t\n\t\t\t</div>\n\t\t\t')

    def process_background(self, *a, **kw):
        pass  # slider background is applied to the slides (fields_only)


class Slide(Module):
    slug = "et_pb_slide"

    def render(self):
        p = self.props
        sl = self.ctx.slider
        # children inherit the parent's values for unset (default) fields
        if sl:
            for k, v in sl.attrs.items():
                if k not in self.attrs and k in self.fields and k.startswith("background_"):
                    self.props[k] = v
                    dict.__setitem__(self.props, k, v)
        self.process_additional()
        self.ctx.slide_num = getattr(self.ctx, "slide_num", 0) + 1
        base_classes(self)
        self.classes = ["et_pb_slide", self.order_class]
        self.add_class(self.bg_layout_class_slide())
        if p.get("image", ""):
            self.add_class("et_pb_slide_with_image")
        self.add_class(f"et_pb_media_alignment_{p.get('image_alignment', '') or 'center'}")
        if self.ctx.slide_num == 1:
            self.add_class("et-pb-active-slide")
        # arrows / dots colors per active slide
        if sl:
            prefix = f'.{sl.order_class.rsplit("_", 1)[0]}[data-active-slide="{self.order_class}"]'
            ac = sl.props.get("arrows_custom_color", "")
            if ac:
                self.css(f"{prefix} .et-pb-slider-arrows .et-pb-arrow-prev, {prefix} .et-pb-slider-arrows .et-pb-arrow-next", f"color: {ac};")
            dc = sl.props.get("dot_nav_custom_color", "")
            if dc:
                self.css(f"{prefix} .et-pb-controllers a, {prefix} .et-pb-controllers .et-pb-active-control", f"background-color: {dc};")
        lvl = (sl.props.get("header_level", "") if sl else "") or "h2"
        heading = p.get("heading", "")
        if heading and (p.get("button_link", "") or "#") != "#":
            heading = f'<a href="{esc_url(p.get("button_link"))}">{heading}</a>'
        title = f'<{lvl} class="et_pb_slide_title">{heading}</{lvl}>' if heading else ""
        content = module_content(self.node)
        body = f'<div class="et_pb_slide_content">{content}</div>' if content else ""
        btn = ""
        if p.get("button_text", ""):
            btn = (f'<div class="et_pb_button_wrapper"><a class="et_pb_button et_pb_more_button" href="{esc(p.get("button_link") or "#")}">'
                   f'{p.get("button_text")}</a></div>')
        return (f'<div class="{" ".join(self.classes)}" data-slide-id="{self.order_class}">\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t<div class="et_pb_container clearfix">\n\t\t\t\t\t<div class="et_pb_slider_container_inner">\n'
                f'\t\t\t\t\t\t\n\t\t\t\t\t\t<div class="et_pb_slide_description">\n\t\t\t\t\t\t\t{title}{body}\n\t\t\t\t\t\t\t{btn}\n'
                f'\t\t\t\t\t\t</div>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t</div>\n\t\t\t')

    def bg_layout_class_slide(self):
        return f"et_pb_bg_layout_{self.props.get('background_layout', '') or 'dark'}"

    def process_background(self, *a, **kw):
        bg = self.af.get("background") or {}
        p = self.props
        color = p.get("background_color", "")
        if color and p.get("background_enable_color", "on") != "off":
            self.css(["%%order_class%%", ".et_pb_slider %%order_class%%"], f"background-color: {color};")
        if p.get("use_background_color_gradient", "") == "on" or p.get("background_image", ""):
            super().process_background(selector=".et_pb_slider %%order_class%%")

    def process_fonts(self):
        pass  # parent slider fonts cover the slides; per-slide fonts not in spike scope


class FullwidthHeader(Module):
    slug = "et_pb_fullwidth_header"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        self.add_class(self.text_orientation_class().strip(), self.bg_layout_class())
        if p.get("header_fullscreen", "") == "on":
            self.add_class("et_pb_fullscreen")
        lvl = p.get("title_level", "") or "h1"
        orient = p.get("content_orientation", "") or "center"
        align = p.get("text_orientation", "") or "left"
        title = f'<{lvl} class="et_pb_module_header">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        sub = f'<span class="et_pb_fullwidth_header_subhead">{p.get("subhead")}</span>' if p.get("subhead", "") else ""
        content = module_content(self.node)
        body = f'<div class="et_pb_header_content_wrapper">{content}</div>' if content else ""
        btns = ""
        for n in ("one", "two"):
            if p.get(f"button_{n}_text", ""):
                btns += (f'<a class="et_pb_button et_pb_more_button et_pb_button_{n}" href="{esc_url(p.get(f"button_{n}_url"))}">'
                         f'{p.get(f"button_{n}_text")}</a>')
        inner = (f'<div class="et_pb_fullwidth_header_container {align}">\n\t\t\t\t\t<div class="header-content-container {orient}">\n'
                 f'\t\t\t\t\t<div class="header-content">\n\t\t\t\t\t\t\n\t\t\t\t\t\t{title}\n\t\t\t\t\t\t{sub}\n'
                 f'\t\t\t\t\t\t{body}\n\t\t\t\t\t\t{btns}\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t\t\n\t\t\t\t</div>\n'
                 f'\t\t\t\t<div class="et_pb_fullwidth_header_overlay"></div>\n\t\t\t\t<div class="et_pb_fullwidth_header_scroll"></div>')
        return module_wrap(self, inner, tag="section")


class Unsupported(Module):
    def render(self):
        self.ctx.unsupported[self.node.tag] = self.ctx.unsupported.get(self.node.tag, 0) + 1
        base_classes(self)
        inner = render_children(self.node, self.ctx, self) if self.node.modules else esc(self.node.content[:200])
        return (f'<div class="{self.classname()} pp-unsupported" style="outline:2px dashed #e11d48;padding:12px;'
                f'font:12px/1.4 monospace;color:#e11d48">[{self.node.tag} not supported by the Python preview]{inner}</div>')


HANDLERS = {
    "et_pb_section": Section, "et_pb_row": Row, "et_pb_row_inner": RowInner,
    "et_pb_column": Column, "et_pb_column_inner": Column,
    "et_pb_heading": Heading, "et_pb_text": TextMod, "et_pb_button": Button, "et_pb_image": Image,
    "et_pb_blurb": Blurb, "et_pb_accordion": Accordion, "et_pb_accordion_item": AccordionItem,
    "et_pb_toggle": Toggle, "et_pb_number_counter": NumberCounter, "et_pb_divider": Divider,
    "et_pb_cta": Cta, "et_pb_slider": Slider, "et_pb_slide": Slide, "et_pb_fullwidth_header": FullwidthHeader,
}


def render_node(node: Node, ctx: Ctx, parent=None) -> str:
    cls = HANDLERS.get(node.tag, Unsupported)
    m = cls(node, ctx, parent)
    if cls is Column and node.tag == "et_pb_column_inner":
        m.render_slug = "et_pb_column_inner"
    out = m.render()
    ignored = sorted(k for k, v in m.attrs.items()
                     if k not in META_ATTRS and k not in m.props.read and v != m.defaults.get(k, None))
    ctx.coverage.append({"module": m.order_class, "tag": node.tag, "supported": cls is not Unsupported,
                         "attrs": len([k for k in m.attrs if k not in META_ATTRS]), "ignored": ignored})
    return out


def render_children(node: Node, ctx: Ctx, parent) -> str:
    return "".join(render_node(c, ctx, parent) for c in node.children if isinstance(c, Node))


# column_inner uses its own counter
_orig_init = Column.__init__


def _col_init(self, node, ctx, parent=None):
    self.render_slug = node.tag
    _orig_init(self, node, ctx, parent)


Column.__init__ = _col_init


# ----------------------------------------------------------------------------- page shell
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
DIVI_JS = ["js/scripts.min.js", "includes/builder/feature/dynamic-assets/assets/js/jquery.fitvids.js",
           "includes/builder/feature/dynamic-assets/assets/js/jquery.mobile.js",
           "includes/builder/feature/dynamic-assets/assets/js/easypiechart.js", "core/admin/js/common.js"]


def google_fonts_link(ctx: Ctx) -> str:
    gf = ctx.data.google_fonts()
    fams = []
    for f in sorted(ctx.fonts):
        if f in gf:
            fams.append(f.replace(" ", "+") + ":" + ",".join(gf[f]["variants"]))
    if not fams:
        return ""
    return (f"<link rel='stylesheet' id='et-builder-googlefonts-cached-css' href='https://fonts.googleapis.com/css?family="
            f"{'|'.join(fams)}&#038;subset=latin,latin-ext&#038;display=swap' media='all' />")


def render_page(source: str, data: DiviData, title: str = "Preview", with_js: bool = True,
                jquery: str | None = None, reload_js: str = "") -> tuple:
    t0 = time.perf_counter()
    doc = parse(source)
    ctx = Ctx(data)
    builder = "".join(render_node(n, ctx) for n in doc.nodes if isinstance(n, Node))
    etl = (f'<div class="et-l et-l--post">\n\t\t\t<div class="et_builder_inner_content et_pb_gutters3">\n\t\t'
           f'{builder}\t\t</div>\n\t</div>')
    builder_css = ctx.css_text()
    t_render = time.perf_counter() - t0
    if data.asset_base:
        logo = data.asset_base + "images/logo.png"
    elif data.divi_path and data.embed_fonts:
        logo = data.data_uri("images/logo.png") or ""
    else:
        logo = ("file://" + urllib.parse.quote(str(data.divi_path)) + "/images/logo.png") if data.divi_path else ""
    header = HEADER.format(logo=logo, site="Preview", menu='<li><a href="#">Home</a></li><li><a href="#">Sample Page</a></li>')
    js = ""
    if with_js:
        jq = ""
        if jquery and os.path.exists(jquery):
            jq = f"<script>{Path(jquery).read_text(encoding='utf-8', errors='replace')}</script>"
        elif jquery:
            jq = f'<script src="{jquery}"></script>'
        scripts = "".join(f"<script>{data.read_js(r)}</script>\n" for r in DIVI_JS if data.read_js(r))
        js = f"{jq}\n<script>{JS_GLOBALS}</script>\n{scripts}"
    page = f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0" />
<title>{esc(title)}</title>
<script type="text/javascript">document.documentElement.className = 'js';</script>
<link rel='stylesheet' id='et-divi-open-sans-css' href='https://fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800&#038;subset=latin,latin-ext&#038;display=swap' media='all' />
<style id="divi-style-css-inlined" media="all">{data.static_css()}</style>
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
{js}{reload_js}
</body>
</html>
"""
    stats = {"render_s": round(t_render, 4), "total_s": round(time.perf_counter() - t0, 4),
             "modules": len(ctx.coverage), "builder_css_bytes": len(builder_css),
             "parse_problems": [p.message for p in doc.problems]}
    return page, ctx, stats


def coverage_report(ctx: Ctx) -> dict:
    by_tag: dict = {}
    for c in ctx.coverage:
        t = by_tag.setdefault(c["tag"], {"count": 0, "supported": c["supported"], "attrs": 0, "ignored": {}})
        t["count"] += 1
        t["attrs"] += c["attrs"]
        for a in c["ignored"]:
            t["ignored"][a] = t["ignored"].get(a, 0) + 1
    total = sum(c["attrs"] for c in ctx.coverage)
    ign = sum(len(c["ignored"]) for c in ctx.coverage)
    return {"modules": len(ctx.coverage), "unsupported_modules": {k: v for k, v in ctx.unsupported.items()},
            "attrs_total": total, "attrs_ignored": ign,
            "attr_coverage_pct": round(100 * (total - ign) / total, 1) if total else 100.0,
            "by_tag": by_tag}


def find_jquery(divi_path: Path | None) -> str | None:
    if divi_path:
        p = divi_path.parent.parent.parent / "wp-includes/js/jquery/jquery.min.js"
        if p.exists():
            return str(p)
    return "https://code.jquery.com/jquery-3.7.1.min.js"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--divi-path", default=str(DEFAULT_DIVI))
    ap.add_argument("--theme-css-url")
    ap.add_argument("--no-js", action="store_true")
    ap.add_argument("--no-embed-fonts", action="store_true", help="reference fonts via file:// instead of data: URIs")
    ap.add_argument("--coverage")
    a = ap.parse_args(argv)
    divi = Path(a.divi_path).expanduser() if a.divi_path else None
    data = DiviData(divi if divi and divi.exists() else None, a.theme_css_url)
    data.embed_fonts = not a.no_embed_fonts
    page, ctx, stats = render_page(Path(a.source).read_text(encoding="utf-8"), data,
                                   title=Path(a.source).stem, with_js=not a.no_js, jquery=find_jquery(data.divi_path))
    Path(a.out).write_text(page, encoding="utf-8")
    cov = coverage_report(ctx)
    if a.coverage:
        Path(a.coverage).write_text(json.dumps(cov, indent=1))
    print(json.dumps({**stats, "attr_coverage_pct": cov["attr_coverage_pct"], "unsupported": cov["unsupported_modules"],
                      "out": a.out, "bytes": len(page)}))


if __name__ == "__main__":
    main()
