"""The font option family (ET_Builder_Element::process_advanced_fonts_options): font, size,
colour, letter spacing, line height, alignment and the font's own text shadow, with responsive and
hover values, plus Divi's letter-spacing ligature fix. A mixin of Module (base.py), split out of
options.py; it relies on self.props, self.af, self.main, self.ctx, self.css() and
self.field_default().
"""
from __future__ import annotations

import re

from .css import add_hover_to_selectors
from .values import TEXT_SHADOW_PRESETS, hover_value, range_value, resp_enabled

WEBSAFE_FONTS = {"Georgia": "serif", "Times New Roman": "serif", "Arial": "sans-serif",
                 "Trebuchet": "sans-serif", "Verdana": "sans-serif"}
FONT_STACKS = {"sans-serif": "Helvetica, Arial, Lucida, sans-serif", "serif": 'Georgia, "Times New Roman", serif',
               "cursive": "cursive"}


class FontOptions:
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
