"""Content modules: Blurb, Call To Action, Number Counter, Fullwidth Header."""
from __future__ import annotations

from ..base import Module, base_classes, module_wrap, register
from ..values import (DEVICES, SIDES, decode_icon, esc, esc_url, four_sides, icon_font, module_content, property_values,
                      resp_enabled)

BLURB_IMAGE_SEL = ("%%order_class%% .et_pb_main_blurb_image .et_pb_only_image_mode_wrap, "
                   "%%order_class%% .et_pb_main_blurb_image .et-pb-icon")


@register("et_pb_blurb")
class Blurb(Module):
    slug = "et_pb_blurb"
    TRANSITIONS = {
        "icon_color": {"color": "%%order_class%% .et-pb-icon"},
        "image_icon_background_color": {"background-color": "%%order_class%% .et_pb_only_image_mode_wrap, %%order_class%% .et-pb-icon"},
        "background_layout": {"color": "%%order_class%% .et_pb_module_header, %%order_class%% .et_pb_blurb_description"},
        "body_text_color": {"color": "%%order_class%% .et_pb_blurb_description"},
        "image_icon_width": {"font-size": "%%order_class%% .et_pb_image_wrap .et-pb-icon"},
        "content_max_width": {"max-width": "%%order_class%% .et_pb_blurb_content"},
    }

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
        self.generate_styles("image_icon_background_color", BLURB_IMAGE_SEL, "background-color")
        # image/icon custom margin & padding (advanced_fields.image_icon)
        for kind, prop in (("image_icon_custom_margin", "margin"), ("image_icon_custom_padding", "padding")):
            v = p.get(kind, "")
            if v:
                self.css(BLURB_IMAGE_SEL, "".join(f"{prop}-{s}: {x} !important;" for s, x in zip(SIDES, four_sides(v)) if x))
        image = self._image(use_icon)
        base_classes(self)
        self.add_class(self.text_orientation_class(), f" et_pb_blurb_position_{placement}", self.bg_layout_class())
        lvl = p.get("header_level", "") or "h4"
        tt = f'<a href="{esc_url(p.get("url"))}">{p.get("title")}</a>' if p.get("url", "") else f'<span>{p.get("title")}</span>'
        title = f'<{lvl} class="et_pb_module_header">{tt}</{lvl}>' if p.get("title", "") else ""
        inner = (f'<div class="et_pb_blurb_content">\n\t\t\t\t\t{image}\n\t\t\t\t\t<div class="et_pb_blurb_container">\n'
                 f'\t\t\t\t\t\t{title}\n\t\t\t\t\t\t<div class="et_pb_blurb_description">{module_content(self.node)}</div>\n'
                 f'\t\t\t\t\t</div>\n\t\t\t\t</div>')
        return module_wrap(self, inner)

    def _image(self, use_icon: bool) -> str:
        p = self.props
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
        return image


@register("et_pb_cta")
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
        return module_wrap(self, f'<div class="et_pb_promo_description">{title}<div>{content}</div></div>\n\t\t\t\t{btn}')


@register("et_pb_number_counter")
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


@register("et_pb_fullwidth_header")
class FullwidthHeader(Module):
    slug = "et_pb_fullwidth_header"
    _ICON = "%%order_class%%.et_pb_fullwidth_header .et_pb_fullwidth_header_scroll a .et-pb-icon"
    TRANSITIONS = {
        "scroll_down_icon_color": {"color": _ICON},
        "scroll_down_icon_size": {"font-size": _ICON},
        "background_overlay_color": {"background-color": "%%order_class%%.et_pb_fullwidth_header .et_pb_fullwidth_header_overlay"},
    }

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
        # render_element(..., 'required' => false): the wrapper prints even without content
        body = f'<div class="et_pb_header_content_wrapper">{content}</div>'
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
