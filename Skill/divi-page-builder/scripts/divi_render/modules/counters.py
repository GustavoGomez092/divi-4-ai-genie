"""Data modules: Countdown Timer, Circle Counter, Bar Counters + Bar Counter (templates from each
module's render()). The numbers are animated by Divi's JS; the server-rendered markup (what these
templates reproduce) carries them as data attributes with empty value elements."""
from __future__ import annotations

import calendar
from datetime import datetime

from ..base import Module, base_classes, bg_layout_classes, register
from ..values import DEVICES, any_value, esc, hover_enabled, hover_value, property_values, resp_enabled

COUNTDOWN_SECTIONS = (("days", "Day", "Day(s)"), ("hours", "Hrs", "Hour(s)"), ("minutes", "Min", "Minute(s)"),
                      ("seconds", "Sec", "Second(s)"))


def end_timestamp(date_time: str) -> int:
    """CountdownTimer.php: strtotime("{gmdate('M d, Y H:i:s', strtotime($date_time))} GMT+0000"),
    i.e. the date read as UTC (WordPress runs PHP in UTC; a fresh site's gmt_offset is 0). It
    doesn't depend on the current time, so the output is deterministic for any date."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d", "%m/%d/%Y %H:%M", "%m/%d/%Y"):
        try:
            return calendar.timegm(datetime.strptime(date_time.strip(), fmt).timetuple())
        except ValueError:
            continue
    return 0  # strtotime() false -> gmdate(0) -> the epoch


@register("et_pb_countdown_timer")
class CountdownTimer(Module):
    slug = "et_pb_countdown_timer"

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        if p.get("use_background_color", "") != "on":
            self.add_class("et_pb_no_bg")
        self.add_class(*bg_layout_classes(self))
        lvl = p.get("header_level", "") or "h4"
        title = f'<{lvl} class="title">{p.get("title")}</{lvl}>' if p.get("title", "") else ""
        sections = '<div class="sep section">\n\t\t\t\t\t\t<p>:</p>\n\t\t\t\t\t</div>'.join(
            f'<div class="{name} section values" data-short="{short}" data-full="{full}">\n'
            f'\t\t\t\t\t\t<p class="value"></p>\n\t\t\t\t\t\t<p class="label">{full}</p>\n\t\t\t\t\t</div>'
            for name, short, full in COUNTDOWN_SECTIONS)
        ts = end_timestamp(p.get("date_time", ""))
        return (f'<div class="{self.classname()}" data-end-timestamp="{ts}">\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n'
                f'\t\t\t\t{self.mask_markup}\n\t\t\t\t<div class="et_pb_countdown_timer_container clearfix">\n'
                f'\t\t\t\t\t{title}\n\t\t\t\t\t{sections}\n\t\t\t\t</div>\n\t\t\t</div>')


@register("et_pb_circle_counter")
class CircleCounter(Module):
    slug = "et_pb_circle_counter"
    # no get_transition_fields_css_props() override: the circle's hover colours are data attributes
    # for the JS, so they get no CSS transition
    TRANSITIONS = {"bar_bg_color": {}, "circle_color": {}, "circle_color_alpha": {}}

    def render(self):
        p = self.props
        self.process_additional()
        base_classes(self)
        self.add_class("container-width-change-notify", self.text_orientation_class().strip(), *bg_layout_classes(self))
        title = p.get("title", "")
        if title:
            self.add_class("et_pb_with_title")
            lvl = p.get("title_level", "") or "h3"
            title = f'<{lvl} class="et_pb_module_header">{title}</{lvl}>'
        number = p.get("number", "").replace("%", "")
        sign = "%" if p.get("percent_sign", "") == "on" else ""
        # render(): the circle colours and their responsive/hover variants are data attributes read
        # by the JS, in this order; the .percent div repeats data-color-hover (%19$s used twice)
        def data(attr, name, dev):
            v = hover_value(p, attr, "") if dev == "hover" else property_values(p, attr)[dev]
            return f' data-{name}{"" if dev == "desktop" else "-" + dev}="{esc(v)}"' if v else ""
        attrs = (data("circle_color", "color", "desktop") + data("circle_color_alpha", "alpha", "desktop")
                 + "".join(data(a, n, d) for a, n in (("bar_bg_color", "bar-bg-color"), ("circle_color", "color"),
                                                      ("circle_color_alpha", "alpha")) for d in ("tablet", "phone"))
                 + "".join(data(a, n, "hover") for a, n in (("bar_bg_color", "bar-bg-color"), ("circle_color", "color"),
                                                             ("circle_color_alpha", "alpha"))))
        inner_cls = " et_pb_with_background" if p.get("background_image", "") else ""
        return (f'<div class="{self.classname()}">\n\t\t\t\t<div class="et_pb_circle_counter_inner{inner_cls}" '
                f'data-number-value="{esc(number)}" data-bar-bg-color="{esc(p.get("bar_bg_color", ""))}"{attrs}>\n'
                f'\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t\t<div class="percent"{data("circle_color", "color", "hover")}><p><span class="percent-value"></span>'
                f'<span class="percent-sign">{sign}'
                f'</span></p></div>\n\t\t\t\t\t{title}\n\t\t\t\t</div>\n\t\t\t</div>')


ACCENT_COLOR = "#7EBEC5"  # et_builder_accent_color() on a stock site


@register("et_pb_counters")
class BarCounters(Module):
    slug = "et_pb_counters"
    has_video_background = False  # BarCounters.php render() never calls video_background()
    TRANSITIONS = {"background_layout": {"color": "%%order_class%% .et_pb_counter_title"},
                   "bar_bg_color": {"background-color": "%%order_class%% .et_pb_counter_amount"}}

    def render(self):
        self.process_additional()
        # render(): hover/sticky only (responsive => false)
        self.generate_styles("background_color", "%%order_class%% .et_pb_counter_container", "background-color",
                             responsive=False, hover_loc="suffix")
        self.generate_styles("bar_bg_color", "%%order_class%% .et_pb_counter_amount", "background-color", responsive=False)
        base_classes(self)
        self.add_class("et-waypoint", *bg_layout_classes(self), self.text_orientation_class().strip())
        # before_render(): the children read the parent's background, bar colour and percentages
        prev = self.ctx.bar_counters
        self.ctx.bar_counters = self
        inner = self.content_html()
        self.ctx.bar_counters = prev
        return f'<ul class="{self.classname()}">\n\t\t\t\t{inner}\n\t\t\t</ul>'


@register("et_pb_counter")
class BarCounter(Module):
    slug = "et_pb_counter"
    TRANSITIONS = {"background_layout": {"color": "%%order_class%% .et_pb_counter_title"},
                   "bar_background_color": {"background-color": "%%order_class%% .et_pb_counter_amount"}}
    CONTAINER = ".et_pb_counters %%order_class%% .et_pb_counter_container"

    def _inherit(self, parent):
        """maybe_inherit_values(): an empty background colour (and its hover/responsive values when
        the item's own toggles are off) comes from the parent Bar Counters."""
        p, pp = self.props, parent.props
        own_hover = hover_enabled(p, "background")
        own_resp = resp_enabled(p, "background")
        self.inherited_attrs = {}
        if not own_hover and hover_enabled(pp, "background"):
            dict.__setitem__(p, "background__hover_enabled", pp.get("background__hover_enabled", ""))
            self.inherited_attrs["background__hover_enabled"] = p.get("background__hover_enabled")
        if not own_resp and resp_enabled(pp, "background"):
            dict.__setitem__(p, "background_last_edited", pp.get("background_last_edited", ""))
        for field in ("background_color", "background_enable_color"):
            if not dict.get(p, field, ""):
                dict.__setitem__(p, field, pp.get(field, ""))
            if not own_hover and hover_enabled(pp, "background"):
                dict.__setitem__(p, f"{field}__hover", pp.get(f"{field}__hover", ""))
            if not own_resp and resp_enabled(pp, "background"):
                for dev in ("tablet", "phone"):
                    dict.__setitem__(p, f"{field}_{dev}", pp.get(f"{field}_{dev}", ""))

    def _has_background(self, parent) -> bool:
        p = self.props
        own_color = bool(p.get("background_color", "")) and (
            parent is not None and p.get("background_color") != parent.props.get("background_color", ""))
        return (own_color or p.get("use_background_color_gradient", "") == "on" or bool(p.get("background_image", ""))
                or any(p.get(k, "") for k in ("background_video_mp4", "background_video_webm")))

    def render(self):
        p = self.props
        parent = self.ctx.bar_counters
        if parent is not None:
            self._inherit(parent)
        self.process_additional()
        percent = p.get("percent", "")
        if not percent.strip().endswith("%"):
            percent += "%"
        # background colour: desktop, tablet and phone all resolve through
        # get_inheritance_background_value() (tablet falls back to desktop, phone to tablet)
        bg = {}
        for dev, slugs in (("desktop", ("",)), ("tablet", ("_tablet", "")), ("phone", ("_phone", "_tablet", ""))):
            bg[dev] = ""
            for s in slugs:
                enabled = (dict.get(p, f"background_enable_color{s}", "") or "on") != "off"
                val = dict.get(p, f"background_color{s}", "")
                if val and enabled:
                    bg[dev] = val
                    break
                if not enabled:
                    break
        parent_img = parent is not None and (parent.props.get("background_image", "") != ""
                                             or parent.props.get("use_background_color_gradient", "") == "on")
        if self._has_background(parent) and p.get("background_color", "") and parent_img:
            if not p.get("background_image", "") and p.get("use_background_color_gradient", "") != "on":
                self.css(".et_pb_counters %%order_class%% .et_pb_counter_container", "background-image: none !important;")
        self.responsive_css({d: {"background-color": f"{v} !important"} if v else {} for d, v in bg.items()},
                            self.CONTAINER)
        # bar colour: the item's own, else the parent's; !important unless it is the accent colour
        pvals = property_values(parent.props, "bar_bg_color") if parent is not None else {d: "" for d in DEVICES}
        bar = {"desktop": p.get("bar_background_color", "") or pvals["desktop"]}
        own_resp = resp_enabled(p, "bar_background_color")
        for dev in ("tablet", "phone"):
            v = any_value(p, f"bar_background_color_{dev}", dev) if own_resp else ""
            bar[dev] = v or pvals[dev]
        for dev, v in bar.items():
            if v and v.lower() != ACCENT_COLOR.lower():
                bar[dev] = f"{v} !important"
        self.responsive_css({d: {"background-color": v} for d, v in bar.items()}, "%%order_class%% .et_pb_counter_amount")
        self.responsive_css({d: {"color": v} for d, v in bar.items()}, "%%order_class%% .et_pb_counter_amount.overlay")
        self.generate_styles("background_color", self.CONTAINER, "background-color", responsive=False, hover_loc="suffix")
        self.generate_styles("bar_background_color", ".et_pb_counters %%order_class%% .et_pb_counter_amount",
                             "background-color", responsive=False)
        self.generate_styles("bar_background_color", ".et_pb_counters %%order_class%% .et_pb_counter_amount.overlay",
                             "color", responsive=False)
        base_classes(self)
        self.classes = [c for c in self.classes if c not in ("et_pb_module", self.render_slug)]
        self.add_class(self.text_orientation_class().strip())
        use_pct = (parent.props.get("use_percentages", "") if parent is not None else "on") == "on"
        shown = esc(percent) if use_pct else ""
        amount = (f'<span class="et_pb_counter_amount_number"><span class="et_pb_counter_amount_number_inner">{shown}'
                  f'</span></span>')
        return (f'<li class="et_pb_counter {self.classname()}">\n\t\t\t\t<span class="et_pb_counter_title">'
                f'{esc(self.raw_content().strip())}</span>\n\t\t\t\t<span class="et_pb_counter_container">\n'
                f'\t\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t\n\t\t\t\t\t{self.mask_markup}\n'
                f'\t\t\t\t\t<span class="et_pb_counter_amount" style="" data-width="{esc(percent)}">{amount}</span>\n'
                f'\t\t\t\t\t<span class="et_pb_counter_amount overlay" style="" data-width="{esc(percent)}">{amount}'
                f'</span>\n\t\t\t\t</span>\n\t\t\t</li>')
