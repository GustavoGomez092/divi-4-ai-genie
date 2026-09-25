"""Basic modules: Heading, Text, Button, Image, Divider (templates from each module's render())."""
from __future__ import annotations

from ..base import Module, base_classes, module_wrap, register
from ..values import (DEVICES, SIDES, decode_icon, esc, esc_url, four_sides, hover_value, module_content, new_window,
                      property_values, resp_enabled)

BUTTON_RELS = ("bookmark", "external", "nofollow", "noreferrer", "noopener")


@register("et_pb_heading")
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


@register("et_pb_text")
class Text(Module):
    slug = "et_pb_text"
    TRANSITIONS = {"quote_border_weight": {"border-width": "%%order_class%% blockquote"},
                   "quote_border_color": {"border-color": "%%order_class%% blockquote"}}

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
        return module_wrap(self, f'<div class="et_pb_text_inner">{module_content(self.node)}</div>')


@register("et_pb_button")
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
            rels = [r for r, on in zip(BUTTON_RELS, p.get("button_rel").split("|")) if on == "on"]
            rel = f' rel="{" ".join(rels)}"' if rels else ""
        btn = f'<a class="{cls}" href="{esc_url(url)}"{target}{rel}{data_icon}>{text}</a>'
        self.css("%%order_class%%, %%order_class%%:after", "transition: all 300ms ease 0ms;")
        return (f'<div class="et_pb_button_module_wrapper {self.order_class}_wrapper {" ".join(al)} et_pb_module ">\n'
                f'\t\t\t\t{btn}\n\t\t\t</div>')

    def process_custom_margin(self):
        p = self.props
        for kind, prop in (("custom_margin", "margin"), ("custom_padding", "padding")):
            sel = ("%%order_class%%_wrapper" if prop == "margin" else
                   "%%order_class%%_wrapper %%order_class%%, %%order_class%%_wrapper %%order_class%%:hover")
            for dev in DEVICES:
                v = p.get(kind, "") if dev == "desktop" else (p.get(f"{kind}_{dev}", "") if resp_enabled(p, kind) else "")
                if not v:
                    continue
                self.css(sel, "".join(f"{prop}-{s}: {x} !important;" for s, x in zip(SIDES, four_sides(v)) if x), dev)
            hv = hover_value(p, kind)
            if hv:
                decl = "".join(f"{prop}-{s}: {x} !important;" for s, x in zip(SIDES, four_sides(hv)) if x)
                self.css("%%order_class%%_wrapper %%order_class%%:hover", decl)


@register("et_pb_image")
class Image(Module):
    slug = "et_pb_image"
    ALIGN_MARGINS = {"left": "margin-left: 0;", "center": "", "right": "margin-right: 0;"}

    def render(self):
        p = self.props
        self.process_additional()
        if p.get("force_fullwidth", "") == "on":
            self.css("%%order_class%%", "width: 100%; max-width: 100% !important;")
            self.css("%%order_class%% .et_pb_image_wrap, %%order_class%% img", "width: 100%;")
        al = property_values(p, "align")
        align = p.get("align", "") or "left"
        self.css("%%order_class%%", f"text-align: {align}; {self.ALIGN_MARGINS.get(align, '')}")
        for dev in ("tablet", "phone"):
            if al[dev]:
                self.css("%%order_class%%", f"text-align: {al[dev]}; {self.ALIGN_MARGINS.get(al[dev], '')}", dev)
        if p.get("force_fullwidth", "") != "on":
            # only height or max-height set, no width: the image keeps its natural width
            w, h, mh = (property_values(p, k) for k in ("width", "height", "max_height"))
            for dev in DEVICES:
                if (w[dev] == "auto" and h[dev] != "auto") or mh[dev] != "none":
                    self.css("%%order_class%% .et_pb_image_wrap img", "width: auto;", dev)
        base_classes(self)
        if p.get("animation_style", "") not in ("", "none"):
            self.add_class("et-waypoint")
        if p.get("show_bottom_space", "") != "on":
            self.add_class("et_pb_image_sticky")
        space = property_values(p, "show_bottom_space")
        for dev in ("tablet", "phone"):
            if space[dev] == "on":
                self.add_class(f"et_pb_image_bottom_space_{dev}")
            elif space[dev] == "off":
                self.add_class(f"et_pb_image_sticky_{dev}")
        has_bs = self.box_shadow_value() != ""
        overlay_div = '<div class="box-shadow-overlay"></div>' if has_bs else ""
        wrap_cls = "has-box-shadow-overlay" if has_bs else ""
        title = f' title="{esc(p.get("title_text", ""))}"'
        img = f'<img decoding="async" src="{esc_url(p.get("src"))}" alt="{esc(p.get("alt", ""))}"{title} />'
        out = f'<span class="et_pb_image_wrap {wrap_cls}">{overlay_div}{img}</span>'
        if p.get("url", ""):
            out = f'<a href="{esc_url(p.get("url"))}"{new_window(p)}>{out}</a>'
        return module_wrap(self, out)


@register("et_pb_divider")
class Divider(Module):
    slug = "et_pb_divider"
    TRANSITIONS = {"color": {"border": "%%order_class%%:before"}, "divider_weight": {"border": "%%order_class%%:before"}}

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        show = p.get("show_divider", "") != "off"
        if show:
            p.get("divider_position", "")
            self.add_class(f"et_pb_divider_position_{dict.get(p, 'divider_position', '') if 'divider_position' in self.attrs else ''}")
            self.generate_styles("color", "%%order_class%%:before", "border-top-color")
            self.generate_styles("divider_weight", "%%order_class%%:before", "border-top-width", typ="range")
            st = p.get("divider_style", "")
            if st and st != "solid":
                self.css("%%order_class%%:before", f"border-top-style: {st};")
        self.add_class("et_pb_space")
        if not show:
            self.classes.remove("et_pb_divider")
            self.add_class("et_pb_divider_hidden")
        for dev in DEVICES:
            v = p.get("height", "") if dev == "desktop" else (p.get(f"height_{dev}", "") if resp_enabled(p, "height") else "")
            if v and v != "auto":
                self.css("%%order_class%%", f"height: {v};", dev)
        v = p.get("max_height", "")
        if v and v != "none":
            self.css("%%order_class%%", f"max-height: {v};")
        return f'<div class="{self.classname()}"><div class="et_pb_divider_internal"></div></div>'
