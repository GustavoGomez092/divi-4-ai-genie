"""Structure elements: Section, Row, RowInner and Column (incl. column_inner and specialty columns).

Order classes are numbered per shortcode tag in document order (set_order_class), so
et_pb_column and et_pb_column_inner keep separate counters.
"""
from __future__ import annotations

from .base import Module, register
from .options import ALIGN_MARGINS
from .values import DEVICES, SIDES, hover_value, property_values, resp_enabled

ROW_SELECTOR = ", body.et_pb_pagebuilder_layout.single.et_full_width_page #page-container #et-boc .et-l %%order_class%%.et_pb_row"
# Specialty sections: an inner column's type is relative to its parent column's width.
SPECIALTY_INNER_TYPES = {"1_2": {"1_2": "1_4", "1_3": "1_6"}, "2_3": {"1_3": "2_9", "1_2": "1_3", "1_4": "1_6"},
                         "3_4": {"1_2": "3_8", "1_3": "1_4"}}


@register("et_pb_section")
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
        self.add_class("et_pb_section", self.order_class, self.hover_background_class())
        bgc_any = p.get("background_color", "") and p.get("background_color", "") != "rgba(255,255,255,0)"
        if bgc_any or p.get("background_image", "") or p.get("background_video_mp4", ""):
            self.add_class("et_pb_with_background")
        bg_parallax_css = p.get("background_image", "") and p.get("parallax", "") == "on" and p.get("parallax_method", "") == "off"
        if p.get("inner_shadow", "") == "on" and not bg_parallax_css:
            self.add_class("et_pb_inner_shadow")
        fullwidth = p.get("fullwidth", "") == "on"
        specialty = p.get("specialty", "") == "on"
        if fullwidth:
            self.add_class("et_pb_fullwidth_section")
        self.add_class("et_section_specialty" if specialty else "et_section_regular")
        for pl in ("top", "bottom"):
            if p.get(f"{pl}_divider_style", "") not in ("", "none"):
                self.ctx.count_unsupported("section_divider")
        prev = self.ctx.specialty
        self.ctx.specialty = specialty
        inner = self.content_html()
        self.ctx.specialty = prev
        mid = inner
        if specialty:
            gutter = (f" et_pb_gutters{p.get('gutter_width')}"
                      if p.get("use_custom_gutter", "") == "on" and p.get("gutter_width", "") else "")
            mid = f'<div class="et_pb_row{gutter}">\n\t\t\t\t{inner}\n\t\t\t\t</div>'
        return (f'<div class="{self.classname()}" >\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t\n\t\t\t\t{mid}\n\t\t\t\t\n\t\t\t\t\n\t\t\t</div>')


@register("et_pb_row")
class Row(Module):
    slug = "et_pb_row"

    def render(self):
        p = self.props
        self.process_additional()
        self.add_class("et_pb_row", self.order_class, self.hover_background_class())
        if p.get("make_equal", "") == "on":
            self.add_class("et_pb_equal_columns")
        if p.get("use_custom_gutter", "") == "on" and p.get("gutter_width", ""):
            g = p.get("gutter_width")
            self.add_class(f"et_pb_gutters{'1' if g == '0' else g}")
        inner = self.content_html()
        return (f'<div class="{self.classname()}">\n\t\t\t\t{inner}\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t\n\t\t\t</div>')

    PADDING_SELECTOR = "%%order_class%%.et_pb_row"

    def process_custom_margin(self):
        super().process_custom_margin()
        # Row render() re-emits the desktop padding without !important, raw values; only the
        # legacy padding_mobile=on|off (without responsive padding) moves it to min-width:981px.
        p = self.props
        values = p.get("custom_padding", "").split("|") if p.get("custom_padding", "") else []
        sides = ("top", "bottom") if len(values) == 2 else SIDES
        legacy = p.get("padding_mobile", "") in ("on", "off") and p.get("padding_mobile") != "on" \
            and not resp_enabled(p, "custom_padding")
        decl = "".join(f"padding-{s}: {x};" for s, x in zip(sides, values) if x)
        self.css(self.PADDING_SELECTOR, decl, "desktop_only" if legacy else "desktop")

    def process_max_width(self):
        # rows: width/max-width with Divi's long selector list; %%row_selector%% removed
        p = self.props
        mw = self.af.get("max_width") or {}
        css = mw.get("css") or {}
        for prop, key, dflt in (("width", "width", "80%"), ("max-width", "max_width", "1080px")):
            v = p.get(key, "")
            if v and v != dflt:
                sel = css.get(key, "%%order_class%%").replace(", %%row_selector%%", ROW_SELECTOR)
                self.css(sel, f"{prop}: {v};")
        al = p.get("module_alignment", "")
        if al:
            self.css("%%order_class%%.et_pb_row", ALIGN_MARGINS.get(al, ""))


@register("et_pb_row_inner")
class RowInner(Row):
    slug = "et_pb_row_inner"
    PADDING_SELECTOR = ".et_pb_column %%order_class%%"
    process_max_width = Module.process_max_width

    def render(self):
        self.process_additional()
        self.add_class("et_pb_row_inner", self.order_class, self.hover_background_class())
        inner = self.content_html()
        return (f'<div class="{self.classname()}">\n\t\t\t\t{inner}\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t\n\t\t\t</div>')


@register("et_pb_column", "et_pb_column_inner")
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
            typ = SPECIALTY_INNER_TYPES.get(sct, {}).get(typ, typ)
        siblings = self.parent.node.modules if self.parent else [self.node]
        is_last = siblings and siblings[-1] is self.node
        cls = ["et_pb_column", f"et_pb_column_{typ}"] + (["et_pb_column_inner"] if inner_col else []) + [self.order_class]
        if self.hover_background_class():
            cls.append(self.hover_background_class())
        if inner_col:
            pass
        elif self.ctx.specialty:
            cls.append("  " + ("et_pb_specialty_column " if p.get("specialty_columns", "") else "") +
                       " et_pb_css_mix_blend_mode_passthrough"
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
