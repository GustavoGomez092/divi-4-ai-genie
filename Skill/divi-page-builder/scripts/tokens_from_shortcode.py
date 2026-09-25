"""Derive design tokens from Divi page shortcode: style bundles per module, typography scale, palette,
spacing, shapes, presets and design-only section skeletons."""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from typing import List

from divi_checks_values import COLOR_TYPES, normalize_color
from divi_shortcode import Node

STRUCTURAL_ATTRS = {"column_structure", "type", "fullwidth", "specialty", "specialty_columns",
                    "saved_specialty_column_type", "admin_label"}
LEVEL_FIELDS = ("title_level", "header_level", "toggle_level")
BOOKKEEPING = {"_builder_version", "_module_preset", "global_colors_info", "locked", "collapsed", "fb_built",
               "template_type", "_dynamic_attributes", "hover_enabled"}


def is_design_attr(mod, name: str) -> bool:
    if name in BOOKKEEPING or name.startswith("custom_css_") or name in ("module_class", "module_id"):
        return False
    res = mod.resolve(name)
    if res is None or res.kind in ("global", "extra"):
        return False
    if res.kind in ("state_toggle", "bg_enable"):
        return True
    field = res.field or {}
    return field.get("tab") == "advanced" or field.get("toggle") == "background"


def _luminance(color: str):
    c = normalize_color(color)
    m = re.fullmatch(r"#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})?", c)
    if not m:
        m2 = re.fullmatch(r"rgba?\((\d+),(\d+),(\d+)(?:,[\d.]+)?\)", c)
        if not m2:
            return None
        r, g, b = (int(x) for x in m2.groups()[:3])
    else:
        r, g, b = (int(x, 16) for x in m.groups()[:3])
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255


def _section_context(section: Node, index: int):
    color = section.value("background_color")
    image = section.value("background_image")
    lum = _luminance(color) if color else None
    tone = "dark" if lum is not None and lum < 0.5 else "light" if lum is not None else ("image" if image else "default")
    return {"section_index": index, "section_label": section.value("admin_label"), "section_tone": tone,
            "section_background": {"color": color, "image": bool(image)}}


def _skeleton(node: Node, schema):
    mod = schema.module(node.tag)
    attrs = {k: node.value(k) for k in node.attrs
             if k in STRUCTURAL_ATTRS or (mod is not None and is_design_attr(mod, k))}
    return {"tag": node.tag, "attrs": attrs, "children": [_skeleton(c, schema) for c in node.modules]}


def tokens_from_documents(docs: List, schema) -> dict:
    styles = defaultdict(dict)
    presets = defaultdict(Counter)
    palette = defaultdict(lambda: {"uses": 0, "roles": set()})
    levels = defaultdict(Counter)
    body_fonts = Counter()
    section_padding, row_width, row_max = Counter(), Counter(), Counter()
    radii, shadows = Counter(), Counter()
    exemplars = []

    for doc in docs:
        parents = {}
        for node, _path, parent in doc.walk():
            parents[id(node)] = parent
        section_index = -1
        for node, _path, parent in doc.walk():
            mod = schema.module(node.tag)
            if mod is None:
                continue
            if node.tag == "et_pb_section":
                section_index += 1
                exemplars.append(_skeleton(node, schema))
                if node.value("custom_padding"):
                    section_padding[node.value("custom_padding")] += 1
            if node.tag == "et_pb_row":
                if node.value("width"):
                    row_width[node.value("width")] += 1
                if node.value("max_width"):
                    row_max[node.value("max_width")] += 1
            design = {k: node.value(k) for k in node.attrs if is_design_attr(mod, k)}
            preset = node.value("_module_preset") or "default"
            if preset != "default":
                presets[node.tag][preset] += 1
            key = json.dumps([sorted(design.items()), preset, node.value("module_class")])
            section, column, cur = None, None, parent
            while cur is not None:
                if cur.tag in ("et_pb_column", "et_pb_column_inner") and column is None:
                    column = cur
                if cur.tag == "et_pb_section":
                    section = cur
                cur = parents.get(id(cur))
            ctx = _section_context(section, section_index) if section is not None else {}
            ctx["column_type"] = column.value("type") if column is not None else ""
            entry = styles[node.tag].setdefault(key, {
                "uses": 0, "attrs": dict(sorted(design.items())), "preset": preset,
                "module_class": node.value("module_class"), "module_id": node.value("module_id"),
                "custom_css": {k: node.value(k) for k in node.attrs if k.startswith("custom_css_")}, "contexts": []})
            entry["uses"] += 1
            entry["contexts"].append(ctx)
            for name, value in design.items():
                res = mod.resolve(name)
                ftype = (res.field or {}).get("type") if res else None
                if ftype in COLOR_TYPES and value and not value.startswith("gcid-"):
                    p = palette[normalize_color(value)]
                    p["uses"] += 1
                    p["roles"].add(name)
                if "border_radii" in name or name.endswith("_border_radius"):
                    radii[value] += 1
                if name == "box_shadow_style" and value not in ("", "none"):
                    shadows[json.dumps({k: v for k, v in design.items() if k.startswith("box_shadow_")}, sort_keys=True)] += 1
            for lf in LEVEL_FIELDS:
                if lf in mod.fields:
                    prefix = lf[: -len("_level")]
                    level = node.value(lf) or mod.fields[lf].get("default", "") or ("h1" if node.tag == "et_pb_heading" else "")
                    font = node.value(f"{prefix}_font")
                    if level and font:
                        levels[level][json.dumps({
                            "font": font, "size": node.value(f"{prefix}_font_size"),
                            "size_tablet": node.value(f"{prefix}_font_size_tablet"),
                            "size_phone": node.value(f"{prefix}_font_size_phone"),
                            "line_height": node.value(f"{prefix}_line_height"),
                            "letter_spacing": node.value(f"{prefix}_letter_spacing"),
                            "color": node.value(f"{prefix}_text_color")}, sort_keys=True)] += 1
            if node.tag == "et_pb_text" and node.value("text_font"):
                body_fonts[node.value("text_font").split("|")[0]] += 1

    scale = {lvl: json.loads(c.most_common(1)[0][0]) for lvl, c in sorted(levels.items())}
    heading_fonts = Counter(v["font"].split("|")[0] for v in scale.values() if v["font"])
    return {
        "colors": {"palette": sorted(({"hex": h, "uses": v["uses"], "roles": sorted(v["roles"])} for h, v in palette.items()),
                                     key=lambda p: -p["uses"])},
        "typography": {"heading_font": heading_fonts.most_common(1)[0][0] if heading_fonts else "",
                       "body_font": body_fonts.most_common(1)[0][0] if body_fonts else "", "scale": scale},
        "spacing": {"section_padding": [[v, c] for v, c in section_padding.most_common()],
                    "row": {"width": [[v, c] for v, c in row_width.most_common()],
                            "max_width": [[v, c] for v, c in row_max.most_common()]}},
        "shapes": {"radii": [[v, c] for v, c in radii.most_common()],
                   "shadows": [[json.loads(v), c] for v, c in shadows.most_common()]},
        "presets": {slug: [{"uuid": u, "uses": c} for u, c in cnt.most_common()] for slug, cnt in presets.items()},
        "module_styles": {slug: sorted(entries.values(), key=lambda e: -e["uses"]) for slug, entries in styles.items()},
        "section_exemplars": exemplars,
    }
