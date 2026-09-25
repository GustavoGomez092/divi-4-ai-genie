"""The generic design-option engine (ET_Builder_Element::process_additional_options), driven by
each module's `advanced_fields`: fonts, text shadow, borders, box shadow, overflow, custom
margin/padding, width/max-width and hover transitions. The background family is in background.py,
the button family in buttons.py.

A mixin of Module (base.py): it relies on self.props, self.af, self.main, self.attrs, self.css()
and self.field_default().
"""
from __future__ import annotations

import re

from .css import add_hover_to_order_class, add_hover_to_selectors
from .values import (BOX_SHADOW_PRESETS, DEVICES, SIDES, TEXT_SHADOW_PRESETS, any_value, four_sides, hover_value,
                     range_value, resp_enabled)

WEBSAFE_FONTS = {"Georgia": "serif", "Times New Roman": "serif", "Arial": "sans-serif",
                 "Trebuchet": "sans-serif", "Verdana": "sans-serif"}
FONT_STACKS = {"sans-serif": "Helvetica, Arial, Lucida, sans-serif", "serif": 'Georgia, "Times New Roman", serif',
               "cursive": "cursive"}
ALIGN_MARGINS = {"left": "margin-left: 0px !important; margin-right: auto !important;",
                 "center": "margin-left: auto !important; margin-right: auto !important;",
                 "right": "margin-left: auto !important; margin-right: 0px !important;"}
# Modules whose border radius doesn't add overflow:hidden, and that never get et_pb_with_border.
NO_RADIUS_OVERFLOW = ("et_pb_social_media_follow", "et_pb_social_media_follow_network", "et_pb_menu",
                      "et_pb_fullwidth_menu")  # process_advanced_borders_options() $no_overflow_module
NO_WITH_BORDER_CLASS = ("et_pb_accordion", "et_pb_accordion_item", "et_pb_pricing_table", "et_pb_tabs", "et_pb_toggle")


def overlay_selector(sel: str) -> str:
    """BoxShadow::get_overlay_selector(): 'X' -> 'X>.box-shadow-overlay, X.et-box-shadow-no-overlay'."""
    parts = (x.strip() for x in sel.split(","))
    return ", ".join(f"{x}>.box-shadow-overlay, {x}.et-box-shadow-no-overlay" for x in parts)


class DesignOptions:
    # Module-specific hover transition map (get_transition_fields_css_props overrides):
    # {option: {css property: selector}}.
    TRANSITIONS: dict = {}

    # fonts --------------------------------------------------------------------------------
    def font_decl(self, value: str, important: bool, default: str | None = None) -> str:
        """et_builder_set_element_font(): 'Name|weight|italic|caps|underline|smallcaps|strike|color|style'."""
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
        gf = self.ctx.theme.google_fonts()
        if name in WEBSAFE_FONTS:
            typ = WEBSAFE_FONTS[name]
        elif name in gf:
            typ = gf[name]["category"]
            self.ctx.fonts.add(name)
        else:
            typ = None
        stack = FONT_STACKS.get(typ, typ) if typ else "sans-serif"
        ms = "'Trebuchet MS', " if name == "Trebuchet" else ""
        return f"font-family: '{name}', {ms}{stack}{' !important' if important else ''};"

    def process_fonts(self):
        fonts = self.af.get("fonts") or {}
        if not isinstance(fonts, dict):
            return
        for opt, st in fonts.items():
            if isinstance(st, dict):
                self._process_font(opt, st)
        # process_advanced_fonts_options() ends by re-emitting every selector on the module class's
        # letter-spacing fix list, with the current order class; the list lives on the (shared)
        # module instance, so it carries over to later modules of the same type on the page
        for sel in self.ctx.letter_spacing_fix.get(self.render_slug, {}).values():
            self.css(sel, "font-variant-ligatures: no-common-ligatures;")

    def _letter_spacing_fix(self, selector: str, prefixes, style: str, default: str):
        """maybe_push_element_to_letter_spacing_fix_list(): the key is the prefixed selector; the
        "value" is the whole declaration minus 'letter-spacing' and non-alphanumerics, read with
        intval(), so a style that starts with another property counts as the default."""
        if "letter-spacing" not in style.strip() or not selector:
            return
        fix = self.ctx.letter_spacing_fix.setdefault(self.render_slug, {})
        value = re.sub(r"[^a-zA-Z0-9]", "", style.replace("letter-spacing", ""))

        def intval(v):
            m = re.match(r"\s*[+-]?\d+", v)
            return int(m.group(0)) if m else 0
        is_default = (intval(default) == 0 and intval(value) == 0) or value == default
        for prefix in prefixes:
            key = ",".join(prefix + part for part in selector.split(","))
            if not is_default:
                fix[key] = key
            else:
                fix.pop(key, None)

    def _process_font(self, opt: str, st: dict):
        p = self.props
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
        tcfg = st.get("text_color") if isinstance(st.get("text_color"), dict) else {}
        old_ref = tcfg.get("old_option_ref", "") if tcfg else ""
        dflt_color = tcfg.get("default", "") if old_ref and p.get(old_ref, "") else ""
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
        # the font's own text shadow ({opt}_text_shadow_*)
        tss = p.get(f"{opt}_text_shadow_style", "")
        if tss and tss != "none":
            h, v_, b_ = TEXT_SHADOW_PRESETS.get(tss, ("0em", "0.1em", "0.1em"))
            h = p.get(f"{opt}_text_shadow_horizontal_length", "") or h
            v_ = p.get(f"{opt}_text_shadow_vertical_length", "") or v_
            b_ = p.get(f"{opt}_text_shadow_blur_strength", "") or b_
            col = p.get(f"{opt}_text_shadow_color", "") or "rgba(0,0,0,0.4)"
            tmain = css.get("text_shadow") or css.get("main") or self.main
            self.css(tmain if isinstance(tmain, list) else [tmain], f"text-shadow: {h} {v_} {b_} {col};")
        main = css.get("main") or self.main
        ls_default = self.field_default(f"{opt}_letter_spacing")
        for state, s in (("default", style), ("hover", hover_style)):
            if not s.strip():
                continue
            for sel in (main if isinstance(main, list) else [main]):
                if state == "hover":  # process_advanced_fonts_options(): css.hover or add_hover_to_selectors()
                    sel = css.get("hover") or add_hover_to_selectors(sel)
                self.css(sel, s)
                self._letter_spacing_fix(sel, ("body.safari ", "body.iphone ", "body.uiwebview "), s.strip(), ls_default)
        self._process_font_responsive(opt, css, imp)

    def _process_font_responsive(self, opt: str, css: dict, imp):
        p = self.props
        for mob in ("font", "font_size", "text_color", "line_height", "letter_spacing", "text_align"):
            for dev in ("tablet", "phone"):
                v = p.get(f"{opt}_{mob}_{dev}", "")
                if v == "" or not resp_enabled(p, f"{opt}_{mob}"):
                    continue
                prop = "color" if mob == "text_color" else mob.replace("_", "-")
                important = " !important" if mob == "text_color" else imp("size" if prop == "font-size" else prop)
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
                if mob == "letter_spacing":  # tablet -> body.uiwebview, phone -> body.iphone
                    self._letter_spacing_fix(sel, ("body.uiwebview " if dev == "tablet" else "body.iphone ",), decl,
                                             self.field_default(f"{opt}_letter_spacing"))

    def process_text_shadow(self):
        p = self.props
        styl = p.get("text_shadow_style", "")
        if styl and styl != "none":
            h, v, b = TEXT_SHADOW_PRESETS.get(styl, ("0em", "0.1em", "0.1em"))
            h = p.get("text_shadow_horizontal_length", "") or h
            v = p.get("text_shadow_vertical_length", "") or v
            b = p.get("text_shadow_blur_strength", "") or b
            color = p.get("text_shadow_color", "") or "rgba(0,0,0,0.4)"
            txt = self.af.get("text") if isinstance(self.af.get("text"), dict) else {}
            sel = (txt.get("css") or {}).get("text_shadow") or self.main
            self.css(sel, f"text-shadow: {h} {v} {b} {color};")

    def process_text_orientation(self):
        """process_advanced_text_options(): modules whose `text` options name a text_orientation
        selector get text-align rules (desktop only when it differs from the field default)."""
        txt = self.af.get("text")
        css = txt.get("css") if isinstance(txt, dict) else None
        if not isinstance(css, dict) or not css.get("text_orientation"):
            return
        p = self.props
        dflt = self.field_default("text_orientation")

        def align(v):  # et_pb_get_alignment()
            return {"force_left": "left", "justified": "justify"}.get(v, v)
        desktop = align(p.get("text_orientation", ""))
        vals = {"desktop": desktop if desktop != dflt else ""}
        for dev in ("tablet", "phone"):
            vals[dev] = align(any_value(p, f"text_orientation_{dev}", dev, dflt))
        for dev in DEVICES:
            if vals[dev]:
                self.css(css["text_orientation"], f"text-align: {vals[dev]};", dev)

    # borders ------------------------------------------------------------------------------
    def process_borders(self):
        borders = self.af.get("borders")
        if borders is None:
            borders = {"default": {}}
        if not isinstance(borders, dict):
            return
        for bname, b in borders.items():
            if b is False or not isinstance(b, (dict, list)):
                continue
            self._process_border(bname, b if isinstance(b, dict) else {})
        if self.render_slug not in NO_WITH_BORDER_CLASS:
            for k, v in self.attrs.items():
                if v and k.startswith("border_") and not k.startswith("border_radii") and k.count("_") > 1:
                    self.add_class("et_pb_with_border")
                    break

    def _process_border(self, bname: str, b: dict):
        p = self.props
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
            if self.render_slug not in NO_RADIUS_OVERFLOW:
                d += " overflow: hidden;"
            self.css(radii_sel, d, dev)
        # styles
        defaults = b.get("defaults", {}).get("border_styles", {}) if isinstance(b.get("defaults"), dict) else {}
        for dev in DEVICES:
            decl = ""
            for prop in ("width", "style", "color"):
                v = p.get(f"border_{prop}_all{suf}", "")
                if dev != "desktop":
                    v = any_value(p, f"border_{prop}_all{suf}", dev) if resp_enabled(p, f"border_{prop}_all{suf}") else ""
                if v and v != defaults.get(prop, ""):
                    decl += f"border-{prop}: {v};"
            for edge in SIDES:
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

    # box shadow ---------------------------------------------------------------------------
    def box_shadow_value(self, suf: str = "", hover=False) -> str:
        p = self.props
        style = p.get(f"box_shadow_style{suf}", "")
        if not style or style == "none":
            return ""
        h, v, b, s, pos = BOX_SHADOW_PRESETS.get(style, ("0", "0", "0", "0", "outer"))

        def g(name, d):
            val = dict.get(p, f"box_shadow_{name}{suf}", "") or d
            p.read.add(f"box_shadow_{name}{suf}")
            if hover:
                hv = hover_value(p, f"box_shadow_{name}{suf}")
                if hv:
                    val = hv
            return val
        pos = "inset" if g("position", pos) == "inner" else ""
        return (f"box-shadow: {pos} {g('horizontal', h)} {g('vertical', v)} {g('blur', b)} {g('spread', s)} "
                f"{g('color', 'rgba(0,0,0,0.3)')};")

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
            if any(self.props.get(k, "") != v for k, v in (css.get("show_if") or {}).items()):
                continue
            if any(self.props.get(k, "") == v for k, v in (css.get("show_if_not") or {}).items()):
                continue
            val = self.box_shadow_value(suf)
            if not val:
                continue
            if css.get("important"):
                val = val.rstrip(";") + " !important;"
            sel = css.get("main", "%%order_class%%")
            overlay = css.get("overlay")
            # process_box_shadow(): an inset shadow on an `overlay: inset` option (or any shadow
            # with `overlay: always`) goes on the overlay element (BoxShadow::get_overlay_selector())
            def on_overlay(s, v):
                return overlay_selector(s) if ("inset" in v and overlay == "inset") or overlay == "always" else s
            self.css(on_overlay(sel, val), val)
            hv = self.box_shadow_value(suf, hover=True)
            if hv and hv != self.box_shadow_value(suf):
                hsel = css.get("hover") or (add_hover_to_order_class(sel) if name == "default"
                                            else add_hover_to_selectors(sel))
                self.css(on_overlay(hsel, hv), hv)
            if "inset" in val and overlay == "inset":
                self.box_shadow_overlay = True

    def process_overflow(self):
        if not self.af.get("overflow"):
            return
        decl = ""
        for axis in ("overflow-x", "overflow-y"):
            v = self.props.get(axis, "")
            if v:
                decl += f"{axis}: {v};"
        self.css(self.main, decl)

    # margin / padding ---------------------------------------------------------------------
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
            imp = " !important" if (imp_cfg == "all" or (isinstance(imp_cfg, list) and kind in imp_cfg)) else ""
            sel = css.get(prop) or css.get("main") or self.main
            for dev in DEVICES:
                if dev == "desktop":
                    v = p.get(kind, "")
                else:
                    if not resp_enabled(p, kind):
                        continue
                    # process_advanced_custom_margin_options(): each breakpoint uses its own raw
                    # value; an empty phone value does not inherit the tablet one.
                    v = p.get(f"{kind}_{dev}", "")
                if not v:
                    continue
                decl = "".join(f"{prop}-{side}: {range_value(val) if val != 'auto' else 'auto'}{imp};"
                               for side, val in zip(SIDES, four_sides(v)) if val != "")
                if decl:
                    self.css(sel, decl, dev)
            hv = hover_value(p, kind)
            if hv:
                decl = "".join(f"{prop}-{s}: {x}{imp};" for s, x in zip(SIDES, four_sides(hv)) if x)
                if decl:
                    self.css(add_hover_to_order_class(sel), decl)

    # sizing -------------------------------------------------------------------------------
    def process_max_width(self):
        """process_max_width_options(): width/max-width on css.<key> or css.main or the order
        class (not main_css); with responsive editing on, the desktop value moves into a
        min-width:981px query."""
        mw = self.af.get("max_width")
        if not isinstance(mw, (dict, list)):
            return
        mw = mw if isinstance(mw, dict) else {}
        css = mw.get("css") or {}
        p = self.props
        imp = " !important" if "important" in css else ""
        opts = mw.get("options") or {}
        for prop, key in (("width", "width"), ("max-width", "max_width")):
            if mw.get(f"use_{key}", True) is False:
                continue
            dflt = (opts.get(key) or {}).get("default", "") or self.field_default(key)
            sel = css.get(key) or css.get("main") or "%%order_class%%"
            responsive = resp_enabled(p, key)
            for dev in DEVICES:
                v = any_value(p, key, dev) if dev != "desktop" else p.get(key, "")
                if dev != "desktop" and not responsive:
                    continue
                if not v or v == dflt or v in ("auto", "none") and dev == "desktop":
                    continue
                self.css(sel, f"{prop}: {v}{imp};", "desktop_only" if dev == "desktop" and responsive else dev)
        # module alignment (only meaningful with a width)
        al = p.get("module_alignment", "")
        if al and (p.get("max_width", "") or p.get("width", "")) and mw.get("use_module_alignment", True) is not False:
            self.css(css.get("module_alignment") or css.get("main") or "%%order_class%%.et_pb_module",
                     ALIGN_MARGINS.get(al, ""))

    # hover transitions --------------------------------------------------------------------
    def _box_shadow_transition_selector(self, key: str) -> str:
        """get_transition_box_shadow_fields_css_props(): the option's css.main (default: the order
        class), plus the overlay selectors when its overlay is `inset` or `always`."""
        bs = self.af.get("box_shadow") if isinstance(self.af.get("box_shadow"), dict) else {}
        opt = next((n for n in bs if n != "default" and key.endswith(f"_{n}")), "default")
        css = (bs.get(opt) or {}).get("css") or {} if isinstance(bs.get(opt), dict) else {}
        sel = css.get("main", "%%order_class%%")
        if css.get("overlay") in ("inset", "always"):
            sel += ", " + overlay_selector(sel)
        return sel

    def process_transitions(self):
        """process_hover_transitions(): one transition rule over the selectors of hover-enabled props."""
        p = self.props
        # attrs plus values a child inherited from its parent (e.g. a slide's background hover)
        src = {**self.attrs, **getattr(self, "inherited_attrs", {})}
        hovered = [k[:-len("__hover_enabled")] for k in src if k.endswith("__hover_enabled") and src[k].startswith("on")]
        fonts = self.af.get("fonts") if isinstance(self.af.get("fonts"), dict) else {}
        btns = self.af.get("button") if isinstance(self.af.get("button"), dict) else {}
        bg_main = ((self.af.get("background") or {}).get("css") or {}).get("main") or self.main \
            if isinstance(self.af.get("background"), dict) else self.main
        tmap = {"background": {"background-color": bg_main, "background-image": bg_main}, **self.TRANSITIONS}
        props, sels = [], []
        for k in hovered:
            if k in tmap:  # get_transition_fields_css_props(): explicit css props + selectors
                if k == "background":
                    if not (hover_value(p, "background_color") or hover_value(p, "background_image")):
                        continue
                elif not p.get(f"{k}__hover", ""):
                    continue
                for cssp, tsel in tmap[k].items():
                    props.append(cssp)
                    sels.append(tsel)
                continue
            sel = self.main
            if k.startswith("box_shadow"):
                prop = "box-shadow"
                sel = self._box_shadow_transition_selector(k)
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
                if isinstance(st, dict) and k.startswith(opt + "_") and self.render_slug != "et_pb_button":
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
