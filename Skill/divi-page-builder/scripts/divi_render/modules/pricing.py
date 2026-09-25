"""Pricing Tables + Pricing Table (templates from PricingTables.php / PricingTablesItem.php render())."""
from __future__ import annotations

import re

from ..base import Module, base_classes, register
from ..values import decode_icon, esc, esc_url, property_values

FEATURED_CLASSES = ("", "et_pb_second_featured", "et_pb_third_featured", "et_pb_fourth_featured")
BUTTON_RELS = ("bookmark", "external", "nofollow", "noreferrer", "noopener")


def featured_class(node) -> str:
    """PricingTables::get_featured_table(): which of the first four tables is featured."""
    flags = [c.value("featured") == "on" for c in node.modules if c.tag == "et_pb_pricing_table"]
    for i, on in enumerate(flags[:4]):
        if on:
            return FEATURED_CLASSES[i]
    return "et_pb_no_featured_in_first_row"


def pricing_items(content: str) -> str:
    """et_pb_extract_items() + PricingTables::additional_render(): one <li> per non-empty line; a
    leading '-' (or an en dash) marks the item unavailable, a leading '+' is dropped."""
    out = ""
    for line in re.sub(r"<p>|</p>|<br />", "\n", content).split("\n"):
        line = line.strip()
        if line.startswith("&#8211;"):
            line = "-" + line[7:]
        if not line:
            continue
        first = line[0]
        if first in "-+":
            line = line[1:].strip()
        cls = ' class="et_pb_not_available"' if first == "-" else ""
        out += f"<li{cls}><span>{line}</span></li>"
    return out


def center_padding(m: Module, selector: str):
    """render(): body text centred on a device drops the list's left padding there."""
    for dev, v in property_values(m.props, "body_text_align").items():
        if v == "center":
            m.css(selector, "padding-left: 0;", dev)


@register("et_pb_pricing_tables")
class PricingTables(Module):
    slug = "et_pb_pricing_tables"
    _FT = "%%order_class%% .et_pb_featured_table"
    TRANSITIONS = {
        "bullet_color": {"border-color": "%%order_class%% .et_pb_pricing li span:before"},
        "featured_table_bullet_color": {"border-color": f"{_FT} .et_pb_pricing li span:before"},
        "featured_table_header_background_color": {"background-color": f"{_FT} .et_pb_pricing_heading"},
        "featured_table_header_text_color": {"color": f"{_FT} .et_pb_pricing_heading h2, {_FT} .et_pb_pricing_heading .et_pb_pricing_title"},
        "header_background_color": {"background-color": "%%order_class%% .et_pb_pricing_heading"},
        "featured_table_text_color": {"color": f"{_FT} .et_pb_pricing_content li, {_FT} .et_pb_pricing_content li span, {_FT} .et_pb_pricing_content li a"},
        "featured_table_subheader_text_color": {"color": f"{_FT} .et_pb_best_value"},
        "featured_table_price_color": {"color": f"{_FT} .et_pb_sum"},
        "featured_table_currency_frequency_text_color": {"color": f"{_FT} .et_pb_dollar_sign, {_FT} .et_pb_frequency"},
        "featured_table_excluded_text_color": {"color": f"{_FT} .et_pb_pricing li.et_pb_not_available, {_FT} .et_pb_pricing li.et_pb_not_available span, {_FT} .et_pb_pricing li.et_pb_not_available a"},
        "featured_table_price_background_color": {"background-color": f"{_FT} .et_pb_pricing_content_top"},
        "price_background_color": {"background-color": "%%order_class%% .et_pb_pricing_content_top"},
    }
    # (attr, selector, hover selector, important) for render()'s generate_styles() calls
    COLORS = (
        ("header_background_color", "%%order_class%% .et_pb_pricing_heading",
         "%%order_class%% .et_pb_pricing_table:hover .et_pb_pricing_heading", False),
        ("featured_table_header_background_color", f"{_FT} .et_pb_pricing_heading",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing_heading", True),
        ("featured_table_header_text_color", f"{_FT} .et_pb_pricing_heading h2, {_FT} .et_pb_pricing_heading .et_pb_pricing_title",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing_heading h2, "
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing_heading .et_pb_pricing_title", True),
        ("featured_table_subheader_text_color", f"{_FT} .et_pb_best_value",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_best_value", True),
        ("featured_table_price_color", f"{_FT} .et_pb_sum", "%%order_class%% .et_pb_featured_table:hover .et_pb_sum", True),
        ("featured_table_text_color", f"{_FT} .et_pb_pricing_content li",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing_content li", True),
        ("bullet_color", "%%order_class%% .et_pb_pricing li span:before", "%%order_class%% .et_pb_pricing:hover li span:before", False),
        ("featured_table_bullet_color", f"{_FT} .et_pb_pricing li span:before",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing li span:before", False),
        ("featured_table_currency_frequency_text_color", f"{_FT} .et_pb_dollar_sign, {_FT} .et_pb_frequency",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_dollar_sign, %%order_class%% .et_pb_featured_table:hover .et_pb_frequency", True),
        ("featured_table_excluded_text_color",
         f"{_FT} .et_pb_pricing li.et_pb_not_available, {_FT} .et_pb_pricing li.et_pb_not_available span, {_FT} .et_pb_pricing li.et_pb_not_available a",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing li.et_pb_not_available, "
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing li.et_pb_not_available span, "
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing li.et_pb_not_available a", True),
        ("featured_table_price_background_color", f"{_FT} .et_pb_pricing_content_top",
         "%%order_class%% .et_pb_featured_table:hover .et_pb_pricing_content_top", False),
        ("price_background_color", "%%order_class%% .et_pb_pricing_content_top",
         "%%order_class%%:hover .et_pb_pricing_content_top", False),
    )

    def render(self):
        p = self.props
        self.process_additional()
        # show_featured_drop_shadow: 'none' when off, the default shadow back on a device that turns it on
        vals = property_values(p, "show_featured_drop_shadow")
        shadow = {"desktop": "none" if p.get("show_featured_drop_shadow", "") != "on" else ""}
        prev = shadow["desktop"]
        for dev in ("tablet", "phone"):
            v, s = vals[dev], ""
            if v:
                s = "none" if v != "on" else ("0 0 12px rgba(0,0,0,0.1)" if prev != "on" else "")
                s = "" if s == prev else s
            shadow[dev] = s
            prev = s
        self.responsive_css({d: {"-moz-box-shadow": v, "-webkit-box-shadow": v, "box-shadow": v} if v else {}
                             for d, v in shadow.items()}, "%%order_class%% .et_pb_featured_table")
        self.generate_styles("featured_table_background_color", "%%order_class%% .et_pb_featured_table", "background-color",
                             hover_loc="suffix")
        for attr, sel, hsel, imp in self.COLORS:
            self.generate_styles(attr, sel, "background-color" if "background" in attr else
                                 ("border-color" if "bullet" in attr else "color"), important=imp, hover_sel=hsel)
        center_padding(self, "%%order_class%% .et_pb_pricing li")
        # before_render(): the tables inherit the button icon, rel and header level
        prev_ctx, self.ctx.pricing = self.ctx.pricing, self
        self.table_count = 0
        inner = self.content_html()
        self.ctx.pricing = prev_ctx
        base_classes(self)
        self.classes = [c for c in self.classes if c != self.render_slug]
        self.add_class("et_pb_pricing", "clearfix", f"et_pb_pricing_{self.table_count}", featured_class(self.node))
        if p.get("show_bullet", "") == "off":
            self.add_class("et_pb_pricing_no_bullet")
        return (f'<div class="{self.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t<div class="et_pb_pricing_table_wrap">\n\t\t\t\t\t{inner}\n\t\t\t\t</div>\n\t\t\t</div>')


@register("et_pb_pricing_table")
class PricingTable(Module):
    slug = "et_pb_pricing_table"
    TRANSITIONS = {"bullet_color": {"border-color": "%%order_class%% ul.et_pb_pricing li span:before"},
                   "header_background_color": {"background-color": "%%order_class%% .et_pb_pricing_heading"},
                   "price_background_color": {"background-color": "%%order_class%% .et_pb_pricing_content_top"}}

    def render(self):
        p = self.props
        parent = self.ctx.pricing
        if parent is not None:
            parent.table_count += 1
        self.process_additional()
        self.generate_styles("bullet_color", "%%order_class%% .et_pb_pricing_content ul.et_pb_pricing li span:before",
                             "border-color", hover_sel="%%order_class%% .et_pb_pricing_content ul.et_pb_pricing:hover li span:before")
        self.generate_styles("header_background_color", ".et_pb_pricing %%order_class%%.et_pb_pricing_table .et_pb_pricing_heading",
                             "background-color", important=True,
                             hover_sel=".et_pb_pricing %%order_class%%.et_pb_pricing_table:hover .et_pb_pricing_heading")
        self.generate_styles("price_background_color", "%%order_class%%.et_pb_pricing_table .et_pb_pricing_content_top",
                             "background-color",
                             hover_sel="%%order_class%%.et_pb_pricing_table:hover .et_pb_pricing_content_top")
        center_padding(self, "%%order_class%%.et_pb_pricing_table .et_pb_pricing li")
        pp = parent.props if parent is not None else {}
        # button: the table's own custom icon, else the parent's (before_render())
        icon = p.get("button_icon", "") if p.get("custom_button", "") == "on" else ""
        icon = icon or (pp.get("button_icon", "") if pp and pp.get("custom_button", "") == "on" else "")
        rel = p.get("button_rel", "")
        if rel in ("", "off|off|off|off|off") and pp and pp.get("button_rel", ""):
            rel = pp.get("button_rel", "")
        button = ""
        url, text = p.get("button_url", "").strip(), p.get("button_text", "")
        if url and text:
            data_icon = f' data-icon="{esc(decode_icon(icon))}"' if icon else ""
            target = ' target="_blank"' if p.get("url_new_window", "") == "on" else ""
            rels = [r for r, on in zip(BUTTON_RELS, rel.split("|")) if on == "on"] if rel else []
            rel_attr = f' rel="{" ".join(rels)}"' if rels else ""
            button = (f'<div class="et_pb_button_wrapper"><a class="et_pb_button et_pb_pricing_table_button" '
                      f'href="{esc_url(url)}"{target}{data_icon}{rel_attr}>{text}</a></div>')
        lvl = p.get("header_level", "")
        if not lvl and pp and pp.get("header_level", "") not in ("", "h2"):
            lvl = pp.get("header_level", "")
        lvl = lvl or "h2"
        title = f'<{lvl} class="et_pb_pricing_title">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        subtitle = f'<span class="et_pb_best_value">{p.get("subtitle")}</span>' if p.get("subtitle", "") else ""
        currency = f'<span class="et_pb_dollar_sign">{p.get("currency")}</span>' if p.get("currency", "") else ""
        per = (f'<span class="et_pb_frequency"><span class="et_pb_frequency_slash">/</span>{p.get("per")}</span>'
               if p.get("per", "") else "")
        total = f'<span class="et_pb_sum">{p.get("sum")}</span>' if p.get("sum", "") else ""
        items = pricing_items(self.raw_content())
        content = f'<ul class="et_pb_pricing">{items}</ul>' if items else ""
        base_classes(self)
        self.classes = [c for c in self.classes if c != "et_pb_module"]
        if p.get("featured", "") != "off":
            self.add_class("et_pb_featured_table")
        return (f'<div class="{self.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t<div class="et_pb_pricing_heading">\n\t\t\t\t\t{title}\n\t\t\t\t\t{subtitle}\n\t\t\t\t</div>\n'
                f'\t\t\t\t<div class="et_pb_pricing_content_top">\n\t\t\t\t\t<span class="et_pb_et_price">{currency}{total}{per}'
                f'</span>\n\t\t\t\t</div>\n\t\t\t\t<div class="et_pb_pricing_content">\n\t\t\t\t\t{content}\n\t\t\t\t</div>\n'
                f'\t\t\t\t{button}\n\t\t\t</div>')

