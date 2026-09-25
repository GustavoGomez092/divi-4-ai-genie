"""Render context, the Module base class and the node -> handler dispatch.

Module handlers register themselves with @register(tag, ...); render_node() instantiates the
handler for a shortcode node (Unsupported when none is registered), renders it and records which
of its attributes were never read (the coverage report).
"""
from __future__ import annotations

from typing import Optional

from divi_shortcode import Node, Text

from .assets import Theme
from .buttons import ButtonOptions
from .css import StyleSheet, add_hover_to_order_class, add_hover_to_selectors
from .data import module_def
from .options import DesignOptions
from .values import DEVICES, Props, hover_enabled, hover_value, property_values, range_value, resp_enabled

# Attributes that never affect output (bookkeeping), excluded from the coverage report.
META_ATTRS = {"_builder_version", "_module_preset", "hover_enabled", "locked", "global_colors_info",
              "fb_built", "admin_label", "collapsed", "template_type", "sticky_enabled",
              "_dynamic_attributes", "theme_builder_area", "saved_specialty_column_type",
              "column_structure", "specialty_columns"}
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
        self.unsupported: dict = {}
        # parent state visible to children while they render
        self.specialty = False
        self.specialty_col_type = ""
        self.slider = None
        self.slide_num = 0
        self.accordion = None

    def next_index(self, slug: str) -> int:
        n = self.counters.get(slug, 0)
        self.counters[slug] = n + 1
        return n

    def count_unsupported(self, key: str, n: int = 1):
        self.unsupported[key] = self.unsupported.get(key, 0) + n


class Module(DesignOptions, ButtonOptions):
    """One shortcode node: props (schema defaults + attrs), order class, CSS classes."""
    slug = ""
    mask_markup = ""
    box_shadow_overlay = False

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
        self.props.read.clear()
        self.index = ctx.next_index(self.render_slug)
        self.order_class = f"{self.render_slug}_{self.index}"
        self.classes: list = []

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
        return "et_pb_section_video_on_hover" if hover_enabled(self.props, "background") else ""

    def bg_layout_class(self) -> str:
        return f"et_pb_bg_layout_{self.props.get('background_layout')}"

    def generate_styles(self, base, selector, prop, important=False, typ="", hover=True, responsive=True,
                        hover_loc="order_class", skip_default=False):
        """ET_Builder_Element::generate_styles(): responsive values plus the hover value."""
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
                hs = add_hover_to_order_class(selector) if hover_loc == "order_class" else add_hover_to_selectors(selector)
                self.css(hs, f"{prop}:{hv}{imp}")

    def process_additional(self):
        """process_additional_options(): the generic design-option engine."""
        self.process_fonts()
        self.process_text_shadow()
        self.process_background()
        self.process_borders()
        self.process_overflow()
        self.process_custom_margin()
        self.process_max_width()
        self.process_button()
        self.process_box_shadow()
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
