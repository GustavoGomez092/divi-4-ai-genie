"""Render context, the Module base class and the node -> handler dispatch.

Module handlers register themselves with @register(tag, ...); render_node() instantiates the
handler for a shortcode node (Unsupported when none is registered), renders it and records which
of its attributes were never read (the coverage report).
"""
from __future__ import annotations

from typing import Optional

from divi_shortcode import Node, Text

from .assets import Theme
from .background import BackgroundOptions
from .buttons import ButtonOptions
from .css import StyleSheet, add_hover_to_order_class, add_hover_to_selectors
from .data import module_def
from .formfield import FormFieldOptions
from .options import DesignOptions
from .values import (DEVICES, Props, hover_enabled, hover_value, icon_css_content, icon_font, multiply_unit,
                     property_values, range_value, resp_enabled)

# Attributes that never affect output (bookkeeping), excluded from the coverage report.
META_ATTRS = {"_builder_version", "_module_preset", "hover_enabled", "locked", "global_colors_info",
              "fb_built", "admin_label", "collapsed", "template_type", "sticky_enabled",
              "_dynamic_attributes", "theme_builder_area", "saved_specialty_column_type",
              "column_structure", "specialty_columns"}
# Modules whose ET_Global_Settings keys use another module's namespace ($this->global_settings_slug;
# class-et-builder-element.php uses it instead of $this->slug). These are every override in Divi
# 4.27.9 (grep of the whole theme): FullwidthPortfolio.php:12, FullwidthPostSlider.php:17,
# PostSlider.php:23.
GLOBAL_SETTINGS_SLUG = {"et_pb_fullwidth_portfolio": "et_pb_portfolio",
                        "et_pb_fullwidth_post_slider": "et_pb_fullwidth_slider",
                        "et_pb_post_slider": "et_pb_slider"}
HANDLERS: dict = {}
FALLBACK: list = []   # [Unsupported], set by modules/fallback.py


def register(*tags):
    def deco(cls):
        for t in tags:
            HANDLERS[t] = cls
        return cls
    return deco


class Ctx:
    """Per-render state shared by all modules of one page."""

    def __init__(self, theme: Theme):
        self.theme = theme
        self.counters: dict = {}
        self.styles = StyleSheet()
        self.fonts: set = set()
        self.coverage: list = []
        self.unsupported: dict = {}   # not rendered by the Python preview (the --exact preview renders it)
        self.site_data: dict = {}     # needs the live site's posts/menus/media/...: neither preview has them
        # parent state visible to children while they render
        self.specialty = False
        self.specialty_col_type = ""
        self.slider = None
        self.slide_num = 0
        self.accordion = None
        self.social_follow = None
        self.bar_counters = None
        self.tabs = None
        self.pricing = None
        self.video_slider = None
        self.half_width_counter = 0       # $et_pb_half_width_counter (form fields)
        self.contact_form_num = None      # $et_pb_contact_form_num (the last contact form rendered)
        self.letter_spacing_fix: dict = {}  # slug -> {prefixed selector: same}

    def next_index(self, slug: str) -> int:
        n = self.counters.get(slug, 0)
        self.counters[slug] = n + 1
        return n

    def count_unsupported(self, key: str, n: int = 1):
        self.unsupported[key] = self.unsupported.get(key, 0) + n

    def count_site_data(self, key: str, n: int = 1):
        self.site_data[key] = self.site_data.get(key, 0) + n


class Module(DesignOptions, BackgroundOptions, ButtonOptions, FormFieldOptions):
    """One shortcode node: props (schema defaults + attrs), order class, CSS classes."""
    slug = ""
    mask_markup = ""
    box_shadow_overlay = False
    # render() calls video_background(), which adds et_pb_section_video_on_hover (Icon doesn't)
    has_video_background = True

    def __init__(self, node: Node, ctx: Ctx, parent=None):
        self.node, self.ctx, self.parent = node, ctx, parent
        self.render_slug = node.tag
        mdef = module_def(self.slug or node.tag)
        self.af = mdef.advanced_fields
        self.main = mdef.main_css
        self.fields = mdef.fields
        self.defaults = mdef.defaults
        self._mdef = mdef
        self.attrs = {k: node.value(k) for k in node.attrs}
        self.props = Props({**self.defaults, **self.attrs})
        self._clear_global_defaults(ctx.theme.global_settings())
        self.props.read.clear()
        self.index = ctx.next_index(self.render_slug)
        self.order_class = f"{self.render_slug}_{self.index}"
        self.classes: list = []

    def _clear_global_defaults(self, globals_: dict):
        """ET_Builder_Element::_maybe_remove_global_default_values_from_props(): on the front end a
        prop equal to its ET_Global_Settings default (e.g. the gallery's overlay colour) is emptied,
        so it prints no CSS; text_orientation is always printed. Keys are namespaced by the
        module's global settings slug (GLOBAL_SETTINGS_SLUG), as in PHP."""
        slug = GLOBAL_SETTINGS_SLUG.get(self.node.tag, self.node.tag)
        for k in list(self.props):
            g = globals_.get(f"{slug}-{k}")
            if g and k != "text_orientation" and dict.get(self.props, k) == g:
                dict.__setitem__(self.props, k, "")

    # -- utilities
    def field_default(self, name: str) -> str:
        return self._mdef.field_default(name)

    def css(self, selector, decl, device="desktop"):
        self.ctx.styles.add(self.order_class, selector, decl, device)

    def add_class(self, *cls):
        for c in cls:
            if c:
                self.classes.append(c)

    def classname(self) -> str:
        seen, out = set(), []
        for c in self.classes:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return " ".join(out)

    def content_html(self) -> str:
        return render_children(self.node, self.ctx, self)

    def raw_content(self) -> str:
        return "".join(c.value for c in self.node.children if isinstance(c, Text))

    def text_orientation_class(self) -> str:
        out = ""
        for dev in DEVICES:
            v = self.props.get("text_orientation") if dev == "desktop" else (
                self.props.get(f"text_orientation_{dev}") if resp_enabled(self.props, "text_orientation") else "")
            if v:
                v = "justified" if v == "justify" else v
                out += f" et_pb_text_align_{v}" + ("" if dev == "desktop" else f"-{dev}")
        return out

    def hover_background_class(self) -> str:
        """video_background(): any element whose background has hover enabled gets this class."""
        if not self.has_video_background:
            return ""
        return "et_pb_section_video_on_hover" if hover_enabled(self.props, "background") else ""

    def bg_layout_class(self) -> str:
        return f"et_pb_bg_layout_{self.props.get('background_layout')}"

    def generate_styles(self, base, selector, prop, important=False, typ="", hover=True, responsive=True,
                        hover_loc="order_class", skip_default=False, hover_sel=None):
        """ET_Builder_Element::generate_styles(): responsive values plus the hover value (on
        `hover_sel` when given, i.e. the PHP `hover_selector` argument)."""
        p = self.props
        imp = " !important" if important else ""
        if responsive:
            vals = property_values(p, base)
            if skip_default and vals["desktop"] == self.field_default(base):
                vals["desktop"] = ""
            for dev in DEVICES:
                v = vals[dev]
                if v:
                    if typ == "range":
                        v = range_value(v)
                    self.css(selector, f"{prop}:{v}{imp}", dev)
        if hover:
            hv = hover_value(p, base)
            if hv:
                hs = hover_sel or (add_hover_to_order_class(selector) if hover_loc == "order_class"
                                   else add_hover_to_selectors(selector))
                self.css(hs, f"{prop}:{hv}{imp}")

    def responsive_css(self, values: dict, selector: str):
        """ResponsiveOptions::generate_responsive_css() with per-device {property: value} dicts;
        empty values (and devices left with none) are skipped."""
        for dev in DEVICES:
            decl = "".join(f"{k}: {x};" for k, x in (values.get(dev) or {}).items() if k and x != "")
            if decl:
                self.css(selector, decl, dev)

    def icon_style(self, base: str, selector: str, content: bool = False):
        """generate_styles() with utility_arg icon_font_family(_and_content) (StyleProcessor::
        process_extended_icon): the icon font, weight and, optionally, the glyph as `content`."""
        icon = self.props.get(base, "")
        if not icon:
            return
        fam, w = icon_font(icon)
        decl = f"font-family: {fam} !important; font-weight: {w} !important;"
        if content:
            decl += f" content: {icon_css_content(icon)} !important;"
        self.css(selector, decl)

    def overlay_icon_size(self, selector: str, fmt: str):
        """StyleProcessor::process_overlay_icon_font_size() for `icon_font_size`: `fmt` with
        {0} = size and {1} = half the size, per device, plus the hover value on the
        :hover-suffixed selector (Video play icon, Testimonial quote icon)."""
        vals = property_values(self.props, "icon_font_size")
        for dev in DEVICES:
            if vals[dev]:
                self.css(selector, fmt.format(vals[dev], multiply_unit(vals[dev], 0.5, 0)), dev)
        hv = hover_value(self.props, "icon_font_size")
        if hv:
            self.css(add_hover_to_selectors(selector), fmt.format(hv, multiply_unit(hv, 0.5, 0)))

    def process_additional(self):
        """process_additional_options(): the generic design-option engine."""
        self.process_fonts()
        self.process_text_shadow()
        self.process_text_orientation()
        self.process_background()
        self.process_borders()
        self.process_height()
        self.process_overflow()
        self.process_custom_margin()
        self.process_max_width()
        self.process_button()
        self.process_form_field()
        self.process_box_shadow()
        self.process_form_field_spacing()
        self.process_transitions()

    def render(self) -> str:
        return ""


# ----------------------------------------------------------------------------- markup helpers
def module_wrap(m: Module, inner: str, extra_attrs: str = "", tag: str = "div") -> str:
    return (f'<{tag} class="{m.classname()}"{extra_attrs}>\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t\n\t\t\t\t{m.mask_markup}\n'
            f'\t\t\t\t{inner}\n\t\t\t</{tag}>')


def base_classes(m: Module, slug: Optional[str] = None):
    pre = [c for c in m.classes if c == "et_pb_with_border"]
    m.classes = pre + ["et_pb_module", slug or m.node.tag, m.order_class]
    m.add_class(m.hover_background_class())
    mc = m.props.get("module_class", "")
    if mc:
        m.classes += mc.split()
    anim = m.props.get("animation_style", "")
    if anim and anim != "none":
        m.classes.append("et_animated")
    if any(k.endswith("__hover_enabled") and v == "on" for k, v in m.attrs.items()):
        m.classes.append("et_hover_enabled")


def bg_layout_classes(m: Module, text_color: bool = False) -> list:
    """BackgroundLayout::get_background_layout_class(): the layout class per device, plus the
    et_pb_text_color_dark* classes when `text_color` (Audio)."""
    vals = property_values(m.props, "background_layout")
    out = [f"et_pb_bg_layout_{vals['desktop']}"]
    out += [f"et_pb_bg_layout_{vals[d]}_{d}" for d in ("tablet", "phone") if vals[d]]
    if text_color:
        out += [f"et_pb_text_color_dark{'' if d == 'desktop' else '_' + d}" for d in DEVICES if vals[d] == "light"]
    return out


# ----------------------------------------------------------------------------- dispatch
def render_node(node: Node, ctx: Ctx, parent=None) -> str:
    cls = HANDLERS.get(node.tag) or FALLBACK[0]
    m = cls(node, ctx, parent)
    out = m.render()
    ignored = sorted(k for k, v in m.attrs.items()
                     if k not in META_ATTRS and k not in m.props.read and v != m.defaults.get(k, None))
    ctx.coverage.append({"module": m.order_class, "tag": node.tag, "supported": cls is not FALLBACK[0],
                         "attrs": len([k for k in m.attrs if k not in META_ATTRS]), "ignored": ignored})
    return out


def render_children(node: Node, ctx: Ctx, parent) -> str:
    return "".join(render_node(c, ctx, parent) for c in node.children if isinstance(c, Node))
