"""The background option family (ET_Builder_Element::process_advanced_background_options and
module/helpers/Background.php): colour, gradient, image, hover and mask. A mixin of Module
(base.py), split out of options.py; it relies on self.props, self.af, self.main and self.css().
"""
from __future__ import annotations

import base64
import html

from .css import add_hover_to_selectors
from .values import hover_value

BG_POSITIONS = {"top_left": "left top", "top_center": "center top", "top_right": "right top",
                "center_left": "left center", "center_right": "right center", "bottom_left": "left bottom",
                "bottom_center": "center bottom", "bottom_right": "right bottom"}


class BackgroundOptions:
    def gradient(self, prefix: str = "background") -> str:
        p = self.props
        stops = p.get(f"{prefix}_color_gradient_stops", "") or "#2b87da 0%|#29c4a9 100%"
        typ = p.get(f"{prefix}_color_gradient_type", "") or "linear"
        direction = p.get(f"{prefix}_color_gradient_direction", "") or "180deg"
        radial = p.get(f"{prefix}_color_gradient_direction_radial", "") or "center"
        repeat = "repeating-" if p.get(f"{prefix}_color_gradient_repeat", "") == "on" else ""
        stop_css = ",".join(s.strip() for s in stops.split("|"))
        if typ == "linear":
            return f"{repeat}linear-gradient({direction},{stop_css})"
        if typ in ("radial", "circular"):
            return f"{repeat}radial-gradient(circle at {radial},{stop_css})"
        if typ == "conic":
            return f"{repeat}conic-gradient(from {direction} at {radial},{stop_css})"
        return f"{repeat}radial-gradient(ellipse at {radial},{stop_css})"

    def process_background(self, prefix: str = "background", selector: str | None = None, important=None,
                           use_color=None):
        bg = self.af.get("background")
        if not isinstance(bg, dict):
            return
        p = self.props
        css = bg.get("css") or {}
        sel = selector or css.get("main") or self.main
        # process_advanced_background_options(): any truthy css.important ('all' or true)
        imp = " !important" if (important if important is not None else bool(css.get("important"))) else ""
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
                for f, prop, d in (("size", "background-size", "cover"), ("position", "background-position", "center"),
                                   ("repeat", "background-repeat", "no-repeat")):
                    v = p.get(f"{prefix}_{f}", "") or d
                    if v != d:
                        decls.append(f"{prop}: {BG_POSITIONS.get(v, v) if f == 'position' else v};")
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
        hc = hover_value(p, f"{prefix}_color")
        if hc and (use_color is True or bg.get("use_background_color_gradient", True) != "fields_only"):
            # process_advanced_background_options(): css.hover, else add_hover_to_selectors(main);
            # a 'fields_only' colour (Bar Counters) still resets the image but prints no colour
            decl = f"background-image: initial{imp};"
            if use_color is True:
                decl += f" background-color: {hc}{imp};"
            self.css(css.get("hover") or add_hover_to_selectors(sel), decl)
        if p.get(f"{prefix}_enable_mask_style", "") == "on" and bg.get("use_background_mask"):
            self._background_mask(prefix, sel)
        if p.get(f"{prefix}_enable_pattern_style", "") == "on":
            self.ctx.count_unsupported("background_pattern")

    def _background_mask(self, prefix: str, sel: str):
        p = self.props
        mstyle = p.get(f"{prefix}_mask_style", "") or "layer-blob"
        variant = "default"
        tr = p.get(f"{prefix}_mask_transform", "")
        if tr:
            variant = ("rotated" if "rotate" in tr else "default") + ("-inverted" if "invert" in tr else "")
        svg_inner = self.ctx.theme.mask_svg(mstyle, variant, p.get(f"{prefix}_mask_aspect_ratio", "") or "landscape")
        if svg_inner is None:
            self.ctx.count_unsupported("mask:" + mstyle, 0)
            return
        color_m = p.get(f"{prefix}_mask_color", "") or "#ffffff"
        svg = (f'<svg  fill="{color_m}" viewBox="0 0 1920 1440" preserveAspectRatio="none" '
               f'xmlns="http://www.w3.org/2000/svg">{svg_inner}</svg>')
        data = base64.b64encode(svg.encode()).decode()
        self.css(f"{sel} > .et_pb_background_mask", f"background-image: url(data:image/svg+xml;base64,{data});")
        self.mask_markup = '<span class="et_pb_background_mask"></span>'
