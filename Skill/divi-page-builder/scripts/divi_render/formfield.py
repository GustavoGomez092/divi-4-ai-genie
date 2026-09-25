"""The form-field option family (Contact Form, Contact Field, Email Optin and its custom fields):
ET_Builder_Element::process_advanced_form_field_options() for the field colours, and
ET_Builder_Module_Field_MarginPadding::process_advanced_css() for the fields' own margin and
padding. A mixin of Module (base.py); it relies on self.props, self.af, self.main and self.css().
The fields' fonts are an ordinary `fonts` option (options.py).
"""
from __future__ import annotations

from .css import add_hover_to_selectors
from .values import DEVICES, SIDES, any_value, four_sides, hover_value, property_values, range_value, resp_enabled


def _placeholders(base: str, state: str = "") -> str:
    return ", ".join(f"{base}{state}{p}" for p in ("::placeholder", "::-webkit-input-placeholder",
                                                    "::-moz-placeholder", "::-ms-input-placeholder"))


class FormFieldOptions:
    def _form_fields(self):
        ff = self.af.get("form_field")
        return [(k, v if isinstance(v, dict) else {}) for k, v in ff.items()] if isinstance(ff, dict) else []

    def _responsive_color(self, name: str, selector: str, prop: str, imp: str):
        """generate_responsive_css(get_any_value per device, type 'color')."""
        vals = property_values(self.props, name)
        for dev in DEVICES:
            if vals[dev]:
                self.css(selector, f"{prop}: {vals[dev]}{imp};", dev)

    def process_form_field(self):
        """process_advanced_form_field_options(): background and text colours, normal/hover/focus,
        on the option's css selectors (fallbacks: css.main, else `main_css .input`)."""
        for name, st in self._form_fields():
            css = st.get("css") or {}
            el = css.get("main") or f"{self.main} .input"
            hover_el = css.get("hover") or f"{el}:hover"
            focus_el = css.get("focus") or f"{el}:focus"
            focus_hover_el = css.get("focus_hover") or f"{el}:focus:hover"
            imp_list = css.get("important") if isinstance(css.get("important"), list) else []
            base = f"{self.main} .input" if "," in el else el
            use_ph = st.get("placeholder", True) is not False
            ph = {state: css.get(key) or _placeholders(base, state) for state, key in
                  (("", "placeholder"), (":hover", "placeholder_hover"), (":focus", "placeholder_focus"),
                   (":focus:hover", "placeholder_focus_hover"))}

            def with_ph(sel, state):
                return f"{sel}, {ph[state]}" if use_ph else sel

            bg_imp = " !important" if "background_color" in imp_list else ""
            self._responsive_color(f"{name}_background_color", css.get("background_color") or el,
                                   "background-color", bg_imp)
            alt_imp = " !important" if "alternating_background_color" in imp_list else ""
            self._responsive_color(f"{name}_alternating_background_color",
                                   css.get("alternating_background_color") or el, "background-color", alt_imp)
            for opt, sel, imp in ((f"{name}_background_color", css.get("background_color_hover") or hover_el, bg_imp),
                                  (f"{name}_alternating_background_color",
                                   css.get("alternating_background_color_hover") or hover_el, alt_imp)):
                hv = hover_value(self.props, opt)
                if hv:
                    self.css(sel, f"background-color:{hv}{imp};")
            fbg_imp = " !important" if "focus_background_color" in imp_list else ""
            self._responsive_color(f"{name}_focus_background_color", css.get("focus_background_color") or focus_el,
                                   "background-color", fbg_imp)
            hv = hover_value(self.props, f"{name}_focus_background_color")
            if hv:
                self.css(css.get("focus_background_color_hover") or focus_hover_el, f"background-color:{hv}{fbg_imp};")
            tc_imp = " !important" if "form_text_color" in imp_list else ""
            self._responsive_color(f"{name}_text_color", with_ph(css.get("form_text_color") or el, ""), "color", tc_imp)
            hv = hover_value(self.props, f"{name}_text_color")
            if hv:
                self.css(with_ph(css.get("form_text_color_hover") or hover_el, ":hover"), f"color:{hv}{tc_imp};")
            self._responsive_color(f"{name}_focus_text_color", with_ph(css.get("focus_text_color") or focus_el, ":focus"),
                                   "color", tc_imp)
            hv = hover_value(self.props, f"{name}_focus_text_color")
            if hv:
                self.css(with_ph(css.get("focus_text_color_hover") or focus_hover_el, ":focus:hover"),
                         f"color:{hv}{tc_imp};")

    def process_form_field_spacing(self):
        """MarginPadding::process_advanced_css() for form fields: `{name}_custom_margin/padding`
        (responsive and hover) on the option's margin_padding selectors, falling back to its
        css.main and then the module's main_css."""
        p = self.props
        for name, st in self._form_fields():
            keys = {"padding": f"{name}_custom_padding", "margin": f"{name}_custom_margin"}
            if not any(p.get(k, "") or hover_value(p, k) for k in keys.values()):
                continue
            mp = st.get("margin_padding") if isinstance(st.get("margin_padding"), dict) else {}
            opts = dict(mp.get("css") or {})
            opts["main"] = opts.get("main") or (st.get("css") or {}).get("main") or ""
            imp_cfg = opts.get("important")
            imp_list = imp_cfg if isinstance(imp_cfg, list) else []
            for prop, key in keys.items():
                if mp.get(f"use_{prop}", True) is False:
                    continue
                sel = opts.get(prop) or opts["main"] or self.main
                imp = " !important" if (imp_cfg == "all" or f"custom_{prop}" in imp_list) else ""
                for dev in DEVICES:
                    v = p.get(key, "") if dev == "desktop" else (any_value(p, f"{key}_{dev}", dev)
                                                                  if resp_enabled(p, key) else "")
                    if v:
                        self.css(sel, self._spacing_decl(v, prop, imp), dev)
                hv = hover_value(p, key)
                if hv:
                    self.css(opts.get("hover") or add_hover_to_selectors(sel), self._spacing_decl(hv, prop, " !important"))

    @staticmethod
    def _spacing_decl(value: str, prop: str, imp: str) -> str:
        """et_builder_get_element_style_css()."""
        return "".join(f"{prop}-{side}: {range_value(v.strip())}{imp};"
                       for side, v in zip(SIDES, four_sides(value)) if v.strip() != "")
