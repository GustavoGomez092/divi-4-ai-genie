"""The advanced button option family (ET_Builder_Element::process_advanced_button_options):
colours, borders, size, font, icon placement (:before/:after), hover reveal, responsive
re-emission and custom padding. A mixin of Module (base.py).

Quirk kept from Divi: the "is this the default?" checks use the hard-coded `button_*` field names
(`_is_field_default('button_text_size', ...)`), so a module whose button option is named e.g.
`button_one` compares against fields it doesn't have.
"""
from __future__ import annotations

from .css import add_hover_to_selectors, prefix_selectors, suffix_selectors
from .values import SIDES, any_value, four_sides, hover_value, icon_font, range_value, resp_enabled

SECTION_PREFIX = "body #page-container .et_pb_section"


class ButtonOptions:
    def process_button(self):
        btns = self.af.get("button")
        if not isinstance(btns, dict):
            return
        for opt, st in btns.items():
            self._process_one_button(opt, st if isinstance(st, dict) else {})

    def _process_one_button(self, opt: str, st: dict):
        p = self.props
        slug = self.render_slug
        css = st.get("css") or {}
        if st.get("use_alignment") and css.get("alignment"):
            for dev in ("desktop", "tablet", "phone"):
                k = f"{opt}_alignment" + ("" if dev == "desktop" else f"_{dev}")
                v = p.get(k, "")
                if v and (dev == "desktop" or resp_enabled(p, f"{opt}_alignment")):
                    self.css(css["alignment"], f"text-align: {'left' if v == 'force_left' else v};", dev)
        if p.get(f"custom_{opt}", "") != "on":
            return
        main = css.get("main") or f"{self.main} .et_pb_button"
        proc = prefix_selectors(main, SECTION_PREFIX)
        tsize = p.get(f"{opt}_text_size", "")
        dflt_size = self.field_default(f"{opt}_text_size")
        is_default_size = "button_text_size" in self.fields and tsize in ("", self.field_default("button_text_size"))
        size_proc = "20px" if is_default_size else range_value(tsize or dflt_size or "20")
        use_icon = p.get(f"{opt}_use_icon", "") or "on"
        icon = p.get(f"{opt}_icon", "")
        placement = p.get(f"{opt}_icon_placement", "") or "right"
        on_hover = p.get(f"{opt}_on_hover", "")
        default_place = ("button_icon_placement" in self.fields and
                         dict.get(p, f"{opt}_icon_placement", "") in ("", self.field_default("button_icon_placement")))
        default_on_hover = ("button_on_hover" in self.fields and
                            dict.get(p, f"{opt}_on_hover", "") in ("", self.field_default("button_on_hover")))
        pad_name = "custom_padding" if slug == "et_pb_button" else f"{opt}_custom_padding"
        pad = (p.get(pad_name, "").split("|") + [""] * 4) if p.get(pad_name, "") else [""] * 4
        left = placement == "left"

        # base rule
        decl = ""
        tc = p.get(f"{opt}_text_color", "")
        if tc:
            decl += f"color:{tc} !important;"
        bw = p.get(f"{opt}_border_width", "")
        br = p.get(f"{opt}_border_radius", "")
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
            decl += f"padding-right: {'0.7em' if left else '2em'};"
        if on_hover == "off" and not pad[3]:
            decl += f"padding-left:{'2em' if left else '0.7em'};"
        # the background goes through Background::get_background_style() with the option's
        # css.important (any truthy value, e.g. Contact Form's 'plugin_only')
        bg_imp = " !important" if css.get("important") else ""
        bgc = p.get(f"{opt}_bg_color", "")
        if bgc and p.get(f"{opt}_bg_enable_color", "on") != "off":
            decl += f"background-color:{bgc}{bg_imp};"
        if p.get(f"{opt}_bg_use_color_gradient", "") == "on":
            decl += f"background-image:{self.gradient(opt + '_bg')}{bg_imp};"
        self.css(proc, decl)

        # hover
        hdecl = ""
        for cssp, suffix in (("color", "text_color"), ("border-color", "border_color"), ("border-radius", "border_radius"),
                             ("letter-spacing", "letter_spacing"), ("font-size", "text_size"), ("border-width", "border_width")):
            hv = hover_value(p, f"{opt}_{suffix}")
            if hv:
                hdecl += f"{cssp}:{hv} !important;"
        if not default_place and on_hover != "off":
            hdecl += f"padding-right: {'0.7em' if left else '2em'};padding-left: {'2em' if left else '0.7em'};"
        hbg = hover_value(p, f"{opt}_bg_color")
        if hbg:
            hdecl += f"background-image:initial{bg_imp};background-color:{hbg}{bg_imp};"
        if hdecl:
            self.css(add_hover_to_selectors(proc), hdecl)

        pseudo = ":before" if left else ":after"
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
            self._button_icon(opt, proc, main, pseudo, icon, placement, on_hover, default_place, default_on_hover,
                              is_default_size, size_proc)

        # custom padding of a module's own button option
        if slug != "et_pb_button":
            mp = (st.get("margin_padding") or {}) if isinstance(st.get("margin_padding"), dict) else {}
            mpcss = mp.get("css") or {}
            psel = mpcss.get("main") or proc
            psel = prefix_selectors(psel, SECTION_PREFIX) if mpcss.get("main") else psel
            v = p.get(pad_name, "")
            if v:
                decl = "".join(f"padding-{s}:{x}!important;" for s, x in zip(SIDES, four_sides(v)) if x)
                self.css(psel, decl)

    def _button_icon(self, opt, proc, main, pseudo, icon, placement, on_hover, default_place, default_on_hover,
                     is_default_size, size_proc):
        p = self.props
        left = placement == "left"
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
            after += f"margin-left: {'-1.3em' if left else '-1em'}; {'right' if left else 'left'}: auto;"
        if on_hover == "off":
            after += f"margin-left: {'-1.3em' if left else '.3em'}; {'right' if left else 'left'}:auto;"
        if not default_place:
            after += "display: inline-block;"
        if icon:
            fam, w = icon_font(icon)
            after += f" font-family: {fam} !important; font-weight: {w} !important;"
        self.css(suffix_selectors(proc, pseudo), after)
        if left:
            self.css(suffix_selectors(proc, ":after"), "display: none;")
            if code:
                fam, w = icon_font(icon)
                self.css(suffix_selectors(proc, ":before"),
                         f"content: attr(data-icon); font-family: {fam} !important; font-weight: {w} !important;")
        if not (icon == "" and default_on_hover and default_place):
            h = ""
            if code:
                h += (f"margin-left:{'.3em' if code != '35' else '0'};{'right' if left else 'left'}: auto; "
                      f"margin-left: {'-1.3em' if left else '.3em'};")
            if on_hover != "off":
                h += "opacity: 1;"
            self.css(suffix_selectors(suffix_selectors(proc, ":hover"), pseudo), h)
        if icon == "" and not is_default_size:
            self.css(suffix_selectors(proc, pseudo), "font-size:1.6em;")
            self.css(f"body.et_button_custom_icon #page-container {main}{pseudo}", f"font-size:{size_proc};")
        self._button_responsive(opt, proc, pseudo, icon, code, placement, on_hover)

    def _button_responsive(self, opt, proc, pseudo, icon, code, placement, on_hover):
        """Divi re-emits the size/colour values and the hover-reveal icon rules for tablet/phone."""
        p = self.props
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
            cur_place = (any_value(p, f"{opt}_icon_placement", dev, placement, True)
                         if resp_enabled(p, f"{opt}_icon_placement") else placement)
            cur_left = cur_place == "left"
            rafter = ""
            if code:
                rafter += "line-height: inherit;font-size: inherit !important;"
            if on_hover != "off" and code:
                rafter += f"margin-left: {'-1.3em' if cur_left else '-1em'}; {'right' if cur_left else 'left'}: auto;"
            if on_hover == "off":
                rafter += f"margin-left: {'-1.3em' if cur_left else '.3em'}; {'right' if cur_left else 'left'}: auto;"
            rafter += "display: inline-block;"
            rafter += "opacity: 0;" if on_hover != "off" else "opacity: 1;"
            self.css(suffix_selectors(proc, pseudo), rafter, dev)
            if code:
                hide, show = (":after", ":before") if cur_left else (":before", ":after")
                fam, w = icon_font(icon)
                self.css(suffix_selectors(proc, hide), "display: none;", dev)
                self.css(suffix_selectors(proc, show),
                         f"content: attr(data-icon); font-family: {fam} !important; font-weight: {w} !important;", dev)
            rh = ""
            if code:
                rh += (f"margin-left:.3em;{'right' if cur_left else 'left'}: auto; "
                       f"margin-left: {'-1.3em' if cur_left else '.3em'};")
            if on_hover != "off":
                rh += "opacity: 1;"
            self.css(suffix_selectors(suffix_selectors(proc, ":hover"), pseudo), rh, dev)
