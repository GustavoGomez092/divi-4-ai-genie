"""Render context, handler registry and what every module shares (Divi 5's Module::render).

A handler is registered per block slug (`divi/text` -> "text") with @register and returns the block's HTML.
The shared parts follow Module::render: the order class (`et_pb_text_3`, one counter per module type), the class
list (order class, module class, the module's own classnames, `et_pb_module` and `et_{flex|block|grid}_module`
for non-structure modules, CSS classes from htmlAttributes and custom attributes, then the preset classes), the
`id` attribute, and the preset class names (GlobalPresetItemUtils::generate_preset_class_name).
"""
from __future__ import annotations

import html as _html

from .css import Sheet, expand, expand_props
from .options import Element
from .values import Values, esc_attr, get

HANDLERS: dict = {}
STRUCTURE = {"section", "row", "row-inner", "column", "column-inner"}
# Modules that show the live site's posts, menus, comments or widgets: neither preview has that data.
SITE_DATA = {"blog", "portfolio", "filterable-portfolio", "fullwidth-portfolio", "post-slider", "fullwidth-post-slider",
             "post-title", "fullwidth-post-title", "post-content", "fullwidth-post-content", "post-nav", "comments",
             "sidebar", "menu", "fullwidth-menu", "search", "login", "breadcrumbs"}


def register(*slugs):
    def deco(fn):
        for s in slugs:
            HANDLERS[s] = fn
        return fn
    return deco


class Ctx:
    """Per-render state shared by all modules of one page."""

    def __init__(self, theme, tokens: dict | None = None):
        self.theme = theme
        self.tokens = tokens if isinstance(tokens, dict) else {}
        self.values = Values(self.tokens)
        self.css = Sheet()
        self.fonts: set = set()
        self.counts: dict = {}
        self.coverage: list = []
        self.unsupported: dict = {}
        self.site_data: dict = {}
        self.group_presets = known_group_presets(self.tokens)

    def order(self, slug: str) -> int:
        n = self.counts.get(slug, 0)
        self.counts[slug] = n + 1
        return n

    def meta(self, slug: str) -> dict:
        return self.theme.module(slug)


def known_group_presets(tokens: dict) -> set:
    """Option-group preset ids the site has (tokens.json group_presets, or preset entries of kind "group")."""
    ids = set()

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("id"), str) and (x.get("kind") in (None, "group")):
                ids.add(x["id"])
            for v in x.values():
                if isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(tokens.get("group_presets") or {})
    for entries in (tokens.get("presets") or {}).values() if isinstance(tokens.get("presets"), dict) else []:
        for e in entries if isinstance(entries, list) else []:
            if isinstance(e, dict) and e.get("kind") == "group" and isinstance(e.get("id"), str):
                ids.add(e["id"])
    return ids


# ------------------------------------------------------------------------------------------ presets
def kebab(name: str) -> str:
    return name.replace("/", "-").replace("_", "-").lower()


def group_host_token(group_id: str) -> str:
    """GlobalPresetItemUtils::_get_group_host_token: a 32-bit string hash in base 36."""
    h = 0
    for ch in group_id:
        h = (((h << 5) - h) + ord(ch)) & 0xFFFFFFFF
    digits, out = "0123456789abcdefghijklmnopqrstuvwxyz", ""
    while True:
        h, r = divmod(h, 36)
        out = digits[r] + out
        if not h:
            break
    return "h" + out[:6]


def preset_class(kind: str, module: str = "", group: str = "", group_id: str = "", preset_id: str = "default",
                 nested: bool = False) -> str:
    """GlobalPresetItemUtils::generate_preset_class_name."""
    if group in ("divi/id-classes", "divi/animation"):
        return ""
    if module and group:
        seg = f"--{group_host_token(group_id)}" if group_id and not group_id.startswith("module.") else ""
        return f"preset--{kind}--{kebab(module)}--{kebab(group)}{seg}--{'nested--' if nested else ''}{preset_id}"
    if module:
        return f"preset--{kind}--{kebab(module)}--{preset_id}"
    if group:
        return f"preset--{kind}--{kebab(group)}--{preset_id}"
    return f"preset--{kind}--{preset_id}"


def preset_stack(value) -> list:
    """GlobalPreset::normalize_preset_stack."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    return [i for i in value if isinstance(i, str) and i and i not in ("default", "_initial")]


def preset_classes(ctx, name: str, attrs: dict) -> list:
    """Module preset classes (every id of the modulePreset stack) and the option-group preset classes of the
    groups whose preset the site has (tokens.json): Divi adds a group preset class only when the preset exists
    with attributes, and a fresh site (the Playground preview) has none."""
    out = [preset_class("module", module=name, preset_id=i) for i in preset_stack(attrs.get("modulePreset"))]
    gp = attrs.get("groupPreset")
    if isinstance(gp, dict):
        for gid, spec in gp.items():
            if not isinstance(spec, dict):
                continue
            for pid in preset_stack(spec.get("presetId")):
                if pid in ctx.group_presets:
                    c = preset_class("group", module=name, group=spec.get("groupName") or "", group_id=gid,
                                     preset_id=pid)
                    if c:
                        out.append(c)
    return out


# ------------------------------------------------------------------------------------------ modules
class Mod:
    """One module instance: order class, metadata, attrs, and element helpers."""

    def __init__(self, ctx: Ctx, block, slug: str, order_slug: str | None = None, css_class: str | None = None):
        self.ctx, self.block, self.slug = ctx, block, slug
        self.name = block.name
        self.attrs = block.attrs if isinstance(block.attrs, dict) else {}
        order_slug = order_slug or slug.replace("-", "_")
        self.n = ctx.order(order_slug)
        self.css_class = css_class or f"et_pb_{order_slug}"
        self.order_class = f"{self.css_class}_{self.n}"
        self.oc = "." + self.order_class
        self.meta = ctx.meta(slug)

    def a(self, *path, default=None):
        return get(self.attrs, *path, default=default)

    def element(self, attr_name: str, **extra) -> Element:
        """The module.json attribute `attr_name` as an Element (selector + expanded styleProps + printed)."""
        m = get(self.meta, "module", "attributes", attr_name) or {}
        sel = expand(m["selector"], self.oc, **extra) if m.get("selector") else self.oc
        props = expand_props(m.get("styleProps") or {}, self.oc, **extra)
        if isinstance(props.get("selector"), str):
            sel = props["selector"]
        printed = get(self.meta, "printed", attr_name, "decoration") or {}
        return Element(sel, props, printed)

    def deco(self, attr_name: str = "module") -> dict:
        return get(self.attrs, attr_name, "decoration") or {}

    def layout(self, default: str = "flex") -> str:
        return get(self.attrs, "module", "decoration", "layout", "desktop", "value", "display") or default

    def html_classes(self) -> list:
        """IdClassesClassnames (module.advanced.htmlAttributes.class) and custom attributes named `class`."""
        out = []
        cls = get(self.attrs, "module", "advanced", "htmlAttributes", "desktop", "value", "class")
        if isinstance(cls, str) and cls.strip():
            out += cls.split()
        for item in get(self.attrs, "module", "decoration", "attributes", "desktop", "value", "attributes") or []:
            if isinstance(item, dict) and item.get("name") == "class" and _main_target(item) and item.get("value"):
                out += str(item["value"]).split()
        return out

    def html_attrs(self) -> str:
        """` id="…"` and custom attributes other than class, for the module's main element."""
        out = ""
        hid = get(self.attrs, "module", "advanced", "htmlAttributes", "desktop", "value", "id")
        if isinstance(hid, str) and hid.strip():
            out += f' id="{esc_attr(hid.strip())}"'
        for item in get(self.attrs, "module", "decoration", "attributes", "desktop", "value", "attributes") or []:
            if (isinstance(item, dict) and item.get("name") and item.get("name") != "class" and _main_target(item)
                    and _safe_attr_name(item["name"])):
                out += f' {item["name"]}="{esc_attr(item.get("value", ""))}"'
        return out

    def custom_attributes(self, target: str) -> list:
        """Custom attributes (module.decoration.attributes) aimed at a sub-element such as the Image module's
        `image` (AttributeUtils::separate_attributes_by_target_element), as (name, value) pairs."""
        out = []
        for item in get(self.attrs, "module", "decoration", "attributes", "desktop", "value", "attributes") or []:
            if (isinstance(item, dict) and item.get("targetElement") == target and item.get("name")
                    and _safe_attr_name(str(item["name"]))):
                out.append((str(item["name"]), item.get("value", "")))
        return out

    def classes(self, own: list, module: bool = True, has_layout: bool = True) -> str:
        """Module::render's class list; `own` is the module's module_classnames output."""
        names = [self.order_class, self.css_class, *own]
        if module:
            names.append("et_pb_module")
            if has_layout:
                names.append(f"et_{self.layout()}_module")
        names += self.html_classes()
        names += preset_classes(self.ctx, self.name, self.attrs)
        return " ".join(dict.fromkeys(n for n in names if n))


def _main_target(item: dict) -> bool:
    return (item.get("targetElement") or "main") in ("main", "")


def _safe_attr_name(name: str) -> bool:
    import re
    return bool(re.fullmatch(r"[A-Za-z_:][-A-Za-z0-9_:.]*", name)) and not name.lower().startswith("on")


def render_children(block, ctx, parent_info: dict | None = None) -> str:
    kids = block.blocks
    return "".join(render_block(c, ctx, {**(parent_info or {}), "index": i, "last": i == len(kids) - 1,
                                         "parent": block})
                   for i, c in enumerate(kids))


def render_block(block, ctx, info: dict | None = None) -> str:
    slug = block.name.split("/", 1)[1] if "/" in block.name else block.name
    handler = HANDLERS.get(slug)
    if handler is None:
        return unsupported(block, ctx, slug)
    return handler(block, ctx, info or {})


def unsupported(block, ctx, slug: str) -> str:
    """A visible placeholder, listed in the coverage report (the --exact Playground preview renders it)."""
    if slug in SITE_DATA:
        ctx.site_data[slug] = ctx.site_data.get(slug, 0) + 1
        return (f'<div class="pp-site-data" style="border:2px dashed #64748b;padding:12px;color:#475569">'
                f'Divi 5 {_html.escape(slug)}: shows the live site\'s data; check it in the WordPress draft preview.'
                f'</div>')
    ctx.unsupported[slug] = ctx.unsupported.get(slug, 0) + 1
    return (f'<div class="pp-unsupported" style="border:2px dashed #e11d48;padding:12px;color:#e11d48">'
            f'Divi 5 module not rendered by the Python preview: {_html.escape(slug)} (use --exact)</div>')
