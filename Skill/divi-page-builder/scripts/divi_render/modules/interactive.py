"""Interactive modules: Accordion + Accordion Item, Toggle, Slider / Fullwidth Slider + Slide, Tabs + Tab."""
from __future__ import annotations

from ..base import Module, base_classes, module_wrap, register
from ..values import (DEVICES, esc, esc_url, hover_value, icon_css_content, icon_font, module_content,
                      property_values)

HEADING_LEVELS = ["h5", "h1", "h2", "h3", "h4", "h6"]


def toggle_transitions(icon: str, closed: str, opened: str) -> dict:
    """Accordion/Toggle get_transition_fields_css_props()."""
    title = "%%order_class%% .et_pb_toggle .et_pb_toggle_title"
    return {"icon_color": {"color": icon},
            "icon_font_size": {"font-size": icon, "margin-top": icon, "right": icon},
            "toggle_text_color": {"color": title}, "toggle_font_size": {"font-size": title},
            "toggle_letter_spacing": {"letter-spacing": title}, "toggle_line_height": {"line-height": title},
            "toggle_text_shadow_style": {"text-shadow": title},
            "closed_toggle_text_color": {"color": f"{closed} .et_pb_toggle_title"},
            "closed_toggle_background_color": {"background-color": closed},
            "open_toggle_text_color": {"color": f"{opened} .et_pb_toggle_title"},
            "open_toggle_background_color": {"background-color": opened}}


def toggle_markup(classes, lvl, title, content) -> str:
    return (f'<div class="{" ".join(classes)}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n'
            f'\t\t\t\t<{lvl} class="et_pb_toggle_title">{title}</{lvl}>\n'
            f'\t\t\t\t<div class="et_pb_toggle_content clearfix">{content}</div>\n\t\t\t</div>')


@register("et_pb_accordion")
class Accordion(Module):
    slug = "et_pb_accordion"
    TRANSITIONS = toggle_transitions("%%order_class%% .et_pb_toggle .et_pb_toggle_title:before",
                                     "%%order_class%%.et_pb_accordion .et_pb_toggle_close",
                                     "%%order_class%%.et_pb_accordion .et_pb_toggle_open")

    def render(self):
        p = self.props
        self.process_additional()
        self.generate_styles("open_toggle_background_color", "%%order_class%% .et_pb_toggle_open", "background-color")
        self.generate_styles("closed_toggle_background_color", "%%order_class%% .et_pb_toggle_close", "background-color")
        for state, key in (("open", "open"), ("close", "closed")):
            sel = ", ".join(f"%%order_class%%.et_pb_accordion .et_pb_toggle_{state} {h}.et_pb_toggle_title" for h in HEADING_LEVELS)
            self.generate_styles(f"{key}_toggle_text_color", sel, "color", important=True)
        if p.get("use_icon_font_size", "") == "on":
            self.generate_styles("icon_font_size", "%%order_class%% .et_pb_toggle_title:before", "font-size", typ="range", hover_loc="suffix")
        self.generate_styles("icon_color", "%%order_class%% .et_pb_toggle_title:before", "color", hover_loc="suffix", skip_default=True)
        icon = p.get("toggle_icon", "")
        if icon:
            fam, w = icon_font(icon)
            self.css("%%order_class%% .et_pb_toggle_title:before",
                     f"font-family: {fam} !important; font-weight: {w} !important; content: {icon_css_content(icon)} !important;")
        base_classes(self)
        self.add_class(self.text_orientation_class() if dict.get(p, "text_orientation") else "")
        prev = self.ctx.accordion
        self.ctx.accordion = self
        inner = self.content_html()
        self.ctx.accordion = prev
        return module_wrap(self, inner)


@register("et_pb_accordion_item")
class AccordionItem(Module):
    slug = "et_pb_accordion_item"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self, "et_pb_accordion_item")
        self.classes = ["et_pb_toggle", "et_pb_module", "et_pb_accordion_item", self.order_class]
        acc = self.ctx.accordion
        p.get("open", "")  # honoured below through the siblings' values (first open item wins)
        siblings = acc.node.modules if acc else [self.node]
        first_open = next((i for i, s in enumerate(siblings) if s.value("open") == "on"), 0)
        idx = next(i for i, s in enumerate(siblings) if s is self.node)
        self.add_class(" et_pb_toggle_open" if idx == first_open else " et_pb_toggle_close")
        lvl = (acc.props.get("toggle_level", "") if acc else "") or "h5"
        return toggle_markup(self.classes, lvl, p.get("title"), module_content(self.node))


@register("et_pb_toggle")
class Toggle(Module):
    slug = "et_pb_toggle"
    TRANSITIONS = toggle_transitions("%%order_class%% .et_pb_toggle_title:before",
                                     "%%order_class%%.et_pb_toggle_close", "%%order_class%%.et_pb_toggle_open")

    def render(self):
        p = self.props
        self.process_additional()
        for state in ("open", "close"):
            key = "open" if state == "open" else "closed"
            self.generate_styles(f"{key}_toggle_background_color", f"%%order_class%%.et_pb_toggle.et_pb_toggle_{state}",
                                 "background-color", hover_loc="suffix")
            self.generate_styles(f"{key}_toggle_text_color",
                                 ", ".join(f"%%order_class%%.et_pb_toggle.et_pb_toggle_{state} {h}.et_pb_toggle_title" for h in HEADING_LEVELS),
                                 "color", important=True, hover_loc="suffix")
        self.generate_styles("open_icon_color", "%%order_class%%.et_pb_toggle_open .et_pb_toggle_title:before", "color", skip_default=True)
        self.generate_styles("icon_color", "%%order_class%%.et_pb_toggle_close .et_pb_toggle_title:before", "color", skip_default=True)
        base_classes(self)
        self.classes = ["et_pb_module", "et_pb_toggle", self.order_class, "et_pb_toggle_item",
                        "et_pb_toggle_open" if p.get("open", "") == "on" else "et_pb_toggle_close"]
        lvl = p.get("toggle_level", "") or "h5"
        return toggle_markup(self.classes, lvl, p.get("title"), module_content(self.node))


@register("et_pb_slider")
class Slider(Module):
    slug = "et_pb_slider"
    # generate_responsive_hover_style() with et_pb_slider_options() selectors (no prefix)
    ARROWS = "%%order_class%% .et-pb-slider-arrows .et-pb-arrow-prev, %%order_class%% .et-pb-slider-arrows .et-pb-arrow-next"
    DOTS = "%%order_class%% .et-pb-controllers a, %%order_class%% .et-pb-controllers .et-pb-active-control"
    TRANSITIONS = {"dot_nav_custom_color": {"background-color": DOTS}, "arrows_custom_color": {"all": ARROWS}}

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        self.slider_classes()
        for attr, sel, prop in (("arrows_custom_color", self.ARROWS, "color"), ("dot_nav_custom_color", self.DOTS, "background-color")):
            vals = property_values(p, attr)
            for dev in DEVICES:
                if vals[dev]:
                    self.css(sel, f"{prop}: {vals[dev]};", dev)
        # before_render(): the slides inherit the slider's settings ($et_pb_slider)
        self.ctx.slider = self
        self.ctx.slide_num = 0
        inner = self.content_html()
        self.ctx.slider = None
        return (f'<div class="{self.classname()}">\n\t\t\t\t<div class="et_pb_slides">\n\t\t\t\t\t{inner}\n\t\t\t\t</div>\n'
                f'\t\t\t\t\n\t\t\t</div>\n\t\t\t')

    def slider_classes(self):
        p = self.props
        self.add_class("et_pb_slider_fullwidth_off")
        if p.get("show_arrows", "") == "off":
            self.add_class("et_pb_slider_no_arrows")
        if p.get("show_pagination", "") == "off":
            self.add_class("et_pb_slider_no_pagination")
        if p.get("auto", "") == "on":
            self.add_class("et_slider_auto", f"et_slider_speed_{p.get('auto_speed', '') or '7000'}")

    def process_background(self, *a, **kw):
        pass  # the slider's background is applied to its slides (fields_only)


@register("et_pb_fullwidth_slider")
class FullwidthSlider(Slider):
    """FullwidthSlider.php: Slider's render() without video_background() (so no
    et_pb_section_video_on_hover), the render slug swapped for et_pb_slider and no
    et_pb_slider_fullwidth_off; the slides are the same Slide module."""
    slug = "et_pb_fullwidth_slider"
    has_video_background = False

    def slider_classes(self):
        p = self.props
        self.classes = [c for c in self.classes if c != self.render_slug]
        self.add_class("et_pb_slider")
        if p.get("show_arrows", "") == "off":
            self.add_class("et_pb_slider_no_arrows")
        if p.get("show_pagination", "") == "off":
            self.add_class("et_pb_slider_no_pagination")
        if p.get("parallax", "") == "on":
            self.add_class("et_pb_slider_parallax")
        if p.get("auto", "") == "on":
            self.add_class("et_slider_auto", f"et_slider_speed_{p.get('auto_speed', '')}")
        if p.get("auto_ignore_hover", "") == "on":
            self.add_class("et_slider_auto_ignore_hover")
        if p.get("show_image_video_mobile", "") == "on":
            self.add_class("et_pb_slider_show_image")


# Slider/FullwidthSlider before_render(): the $et_pb_slider settings a slide inherits
SLIDER_INHERIT = {"background_last_edited", "background__hover_enabled", "header_level", "use_bg_overlay",
                  "use_text_overlay"} | {f"{b}{d}" for b in ("bg_overlay_color", "text_overlay_color", "text_border_radius",
                                                             "arrows_custom_color", "dot_nav_custom_color")
                                         for d in ("", "_tablet", "_phone")}
SLIDER_INHERIT_PREFIXES = ("background_", "use_background_color_gradient", "parallax")


@register("et_pb_slide")
class Slide(Module):
    slug = "et_pb_slide"

    def inherit(self, sl):
        """SliderItem::maybe_inherit_values(): a slide value that is empty or its default takes the
        slider's value unless that is empty or the slide's default; background_enable_color* is
        never inherited ('off' only when the slide itself says so)."""
        p = self.props
        self.inherited_attrs = {}
        for k in list(sl.props):
            if not (k in SLIDER_INHERIT or k.startswith(SLIDER_INHERIT_PREFIXES)):
                continue
            if k.startswith("background_enable_color"):
                dict.__setitem__(p, k, "off" if self.attrs.get(k) == "off" else "on")
                continue
            dflt = self.field_default(k) or ""
            if dict.get(p, k, "") not in ("", dflt):
                continue
            v = sl.props.get(k, "")
            if v in ("", dflt):
                continue
            dict.__setitem__(p, k, v)
            self.inherited_attrs[k] = v

    def render(self):
        p = self.props
        sl = self.ctx.slider
        if sl:
            self.inherit(sl)
        self.process_additional()
        self.ctx.slide_num += 1
        base_classes(self)
        self.classes = ["et_pb_slide", self.order_class]
        self.add_class(self.hover_background_class())
        self.add_class(f"et_pb_bg_layout_{p.get('background_layout', '') or 'dark'}")
        image = p.get("image", "")
        if image:
            self.add_class("et_pb_slide_with_image")
        align = p.get("alignment", "") or "center"
        if align != "bottom":
            self.add_class(f"et_pb_media_alignment_{align}")
        if self.ctx.slide_num == 1:
            self.add_class("et-pb-active-slide")
        # arrows / dots colours per active slide: $et_pb_slider has no 'order_class', so the
        # prefix is always .et_pb_slider (SliderItem.php render())
        prefix = f'.et_pb_slider[data-active-slide="{self.order_class}"]'
        ac = p.get("arrows_custom_color", "")
        if ac:
            self.css(f"{prefix} .et-pb-slider-arrows .et-pb-arrow-prev, {prefix} .et-pb-slider-arrows .et-pb-arrow-next", f"color: {ac};")
        dc = p.get("dot_nav_custom_color", "")
        if dc:
            self.css(f"{prefix} .et-pb-controllers a, {prefix} .et-pb-controllers .et-pb-active-control", f"background-color: {dc};")
        lvl = p.get("header_level", "") or "h2"
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
        img = (f'<div class="et_pb_slide_image"><img decoding="async" src="{esc_url(image)}" '
               f'alt="{esc(p.get("image_alt", ""))}" /></div>' if image else "")
        return (f'<div class="{" ".join(self.classes)}" data-slide-id="{self.order_class}">\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t<div class="et_pb_container clearfix">\n\t\t\t\t\t<div class="et_pb_slider_container_inner">\n'
                f'\t\t\t\t\t\t{img}\n\t\t\t\t\t\t<div class="et_pb_slide_description">\n\t\t\t\t\t\t\t{title}{body}\n\t\t\t\t\t\t\t{btn}\n'
                f'\t\t\t\t\t\t</div>\n\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t</div>\n\t\t\t')

    def process_background(self, *a, **kw):
        p = self.props
        color = p.get("background_color", "")
        if color and p.get("background_enable_color", "on") != "off":  # render(): set_style on the order class
            self.css("%%order_class%%", f"background-color: {color};")
        super().process_background(selector=".et_pb_slider %%order_class%%")

    def process_fonts(self):
        pass  # the parent slider's fonts cover the slides; per-slide fonts not ported yet


@register("et_pb_tabs")
class Tabs(Module):
    slug = "et_pb_tabs"
    TRANSITIONS = {"inactive_tab_background_color": {"background-color": "%%order_class%% .et_pb_tabs_controls li"},
                   "active_tab_background_color": {"background-color": "%%order_class%% .et_pb_tabs_controls li"},
                   "active_tab_text_color": {"color": "%%order_class%% .et_pb_tabs_controls li a"}}

    def render(self):
        self.process_additional()
        self.generate_styles("inactive_tab_background_color", "%%order_class%% .et_pb_tabs_controls li",
                             "background-color", hover_loc="suffix")
        self.generate_styles("active_tab_background_color", "%%order_class%% .et_pb_tabs_controls li.et_pb_tab_active",
                             "background-color", hover_loc="suffix")
        self.generate_styles("active_tab_text_color", "%%order_class%%.et_pb_tabs .et_pb_tabs_controls li.et_pb_tab_active a",
                             "color", important=True, hover=False)
        hv = hover_value(self.props, "active_tab_text_color")
        if hv:  # render(): an explicit hover_selector
            self.css("%%order_class%% .et_pb_tabs_controls li.et_pb_tab_active:hover a", f"color: {hv} !important;")
        # the children collect their titles and order classes ($et_pb_tab_titles / $et_pb_tab_classes)
        prev = self.ctx.tabs
        self.ctx.tabs = []
        inner = self.content_html()
        titles, self.ctx.tabs = self.ctx.tabs, prev
        nav = "".join(f'<li class="{cls}{" et_pb_tab_active" if i == 0 else ""}"><a href="#">{title}</a></li>'
                      for i, (title, cls) in enumerate(titles))
        base_classes(self)
        self.add_class(self.text_orientation_class().strip())
        return (f'<div class="{self.classname()} ">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t<ul class="et_pb_tabs_controls clearfix">\n\t\t\t\t\t{nav}\n\t\t\t\t</ul>\n'
                f'\t\t\t\t<div class="et_pb_all_tabs">\n\t\t\t\t\t{inner}\n\t\t\t\t</div>\n\t\t\t</div>')

    def process_box_shadow(self):
        """Tabs::process_box_shadow(): an inset shadow goes on `.et-pb-active-slide`."""
        if "inset" in self.box_shadow_value():
            self.af = {**self.af, "box_shadow": {"default": {"css": {"main": "%%order_class%% .et-pb-active-slide"}}}}
        super().process_box_shadow()


@register("et_pb_tab")
class Tab(Module):
    slug = "et_pb_tab"

    def render(self):
        p = self.props
        self.process_additional()
        titles = self.ctx.tabs if self.ctx.tabs is not None else []
        titles.append((p.get("title", "") or "Tab", self.order_class))
        base_classes(self)
        self.classes = [c for c in self.classes if c != "et_pb_module"]
        self.add_class("clearfix", self.text_orientation_class().strip())
        if len(titles) == 1:
            self.add_class("et_pb_active_content")
        return (f'<div class="{self.classname()}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t<div class="et_pb_tab_content">{module_content(self.node)}</div>\n\t\t\t</div>')
