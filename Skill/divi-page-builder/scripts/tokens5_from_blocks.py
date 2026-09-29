"""Derive design tokens from Divi 5 block content: style bundles per module, typography scale, palette, global color
and variable references, spacing, shapes, presets and design-only section skeletons.

The Divi 5 counterpart of tokens_from_shortcode.py (same output sections; research/divi5/tokens-and-detection.md §4).
The result is partial: Task 12's merge adds what only the rendered HTML knows (colors.global/customizer values,
variables values, preset CSS, site).

What counts as design (module_styles attrs, section_exemplars):
- only attributes under a `decoration` or `advanced` group (`innerContent` and `meta` are content/bookkeeping);
- never Divi 4 conversion attrs (the schema's `legacy` list) or a bare `….decoration.font` container (Divi styles
  only `….decoration.font.font`; research/divi5/doc-experiments.md §1): authors must not be taught to reuse them;
- per typed leaf (divi5_schema walk_value): `html`, `url`, `image` and opaque `json` leaves are content; `text`
  leaves are content unless they are a property inside a design structure (a sub-key of an object attribute whose
  family is a design family) or a structural attribute (column type/structure); leaves the schema does not accept
  (unknown key, bad breakpoint/state) are dropped;
- families that hold content or behaviour rather than looks are left out whole (custom attributes, conditions,
  interactions, loop query, link, email/spam service credentials); `module.advanced.htmlAttributes` (id-classes) is
  reported separately as `html_attributes`.
`$variable(...)$` strings are kept verbatim everywhere.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from typing import Dict, Iterator, List, Optional

from divi5_blocks import Block, iter_leaves, variable_refs
from divi_checks_values import COLOR_RE, normalize_color
from tokens_from_shortcode import _luminance

DESIGN_GROUPS = frozenset({"decoration", "advanced"})
CONTENT_TYPES = frozenset({"html", "url", "image", "json"})
# Families whose values are content, behaviour or credentials, not looks.
NON_DESIGN_FAMILIES = frozenset({"attributes", "conditions", "interactions", "loop", "link", "email-service",
                                 "spam-protection", "id-classes", "admin-label", "meta"})
# Whole-value text attributes that shape the layout (the Divi 4 STRUCTURAL_ATTRS counterparts).
STRUCTURAL_TEXT = frozenset({"module.advanced.type", "module.advanced.columnStructure",
                             "module.advanced.savedSpecialtyColumnType", "module.advanced.flexType"})
# Text keys inside design structures that are still content (an image's title/alt).
CONTENT_SUBKEYS = frozenset({"title", "titleText", "alt"})
HTML_ATTRS = "module.advanced.htmlAttributes"
ADMIN_LABEL = "module.meta.adminLabel"
MAX_CONTEXTS = 5  # per module_styles entry; `uses` keeps the full count
VARIABLE_KINDS = {"length": "numbers", "number": "numbers", "spacing": "numbers", "radius": "numbers", "font-family": "fonts", "image": "images",
                  "gradient": "gradients", "url": "links", "text": "strings", "html": "strings"}
TRANSPARENT = ("transparent", "rgba(0,0,0,0)", "rgba(255,255,255,0)")


def _group(attr: str) -> Optional[str]:
    return next((seg for seg in attr.split(".") if seg in ("innerContent", "decoration", "advanced", "meta")), None)


def _ignored(mod, attr: str) -> bool:
    """Attributes Divi never reads: Divi 4 conversion leftovers and a bare font container."""
    if attr in mod.legacy or any(attr.startswith(p + ".") for p in mod.legacy):
        return True
    spec = mod.attrs.get(attr) or {}
    return spec.get("family") == "font" and not spec.get("prefix")


def _family(mod, attr: str) -> Optional[str]:
    return (mod.attrs.get(attr) or {}).get("family")


def _design_leaf(attr: str, res) -> bool:
    if res.status != "ok" or res.leaf is None:
        return False
    ltype = res.leaf.get("type")
    if ltype in CONTENT_TYPES:
        return False
    if ltype == "text":
        if res.sub_path is None:
            return attr in STRUCTURAL_TEXT
        return res.sub_path.split(".")[-1] not in CONTENT_SUBKEYS
    return True


def _set(tree: dict, keys: List[str], value) -> None:
    for k in keys[:-1]:
        tree = tree.setdefault(k, {})
    tree[keys[-1]] = value


def _leaves(block: Block, mod) -> Iterator[tuple]:
    """(attr, bp, state, value) of every responsive leaf, skipping attributes Divi never reads."""
    for attr, bp, st, value in iter_leaves(block.attrs):
        if bp is not None and not _ignored(mod, attr):
            yield attr, bp, st, value


def design_attrs(block: Block, mod) -> dict:
    """The design-only part of a block's attrs, as nested Divi 5 attribute JSON."""
    out: dict = {}
    for attr, bp, st, value in _leaves(block, mod):
        if _group(attr) not in DESIGN_GROUPS or _family(mod, attr) in NON_DESIGN_FAMILIES or attr == HTML_ATTRS:
            continue
        for res, v in mod.walk_value(attr, bp, st, value):
            if res.attr_path == attr and _design_leaf(attr, res):
                keys = attr.split(".") + [bp, st] + (res.sub_path.split(".") if res.sub_path else [])
                _set(out, keys, v)
    return out


def _media(block: Block, mod) -> List[str]:
    """Attribute paths (never values) of the image/video/url leaves a block fills in its design groups, plus its
    content images."""
    out = set()
    for attr, bp, st, value in _leaves(block, mod):
        group = _group(attr)
        if group not in DESIGN_GROUPS and group != "innerContent":
            continue
        for res, v in mod.walk_value(attr, bp, st, value):
            ltype = (res.leaf or {}).get("type")
            if v and (ltype == "image" or (ltype == "url" and group in DESIGN_GROUPS)):
                out.add(attr + (f".{res.sub_path}" if res.sub_path else ""))
    return sorted(out)


def _value(block: Block, attr: str, bp: str = "desktop", st: str = "value"):
    cur = block.attrs
    for k in attr.split(".") + [bp, st]:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _preset_list(block: Block) -> List[str]:
    ids = block.attrs.get("modulePreset")
    ids = [ids] if isinstance(ids, str) else ids if isinstance(ids, list) else []
    return [i for i in ids if isinstance(i, str) and i and i != "default"]


def _group_presets(block: Block) -> dict:
    gp = block.attrs.get("groupPreset")
    return gp if isinstance(gp, dict) else {}


def _strings(value) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)


def _is_literal_color(v) -> bool:
    return isinstance(v, str) and "$variable(" not in v and bool(COLOR_RE.match(v.strip()))


def _section_context(section: Block, index: int) -> dict:
    bg = _value(section, "module.decoration.background")
    bg = bg if isinstance(bg, dict) else {}
    color = bg.get("color") or None
    gradient = bg.get("gradient") if isinstance(bg.get("gradient"), dict) else {}
    image = bg.get("image") if isinstance(bg.get("image"), dict) else {}
    has_gradient = gradient.get("enabled") == "on"
    has_image = bool(image.get("url")) and image.get("enabled") != "off"
    lum = None
    if _is_literal_color(color):
        lum = _luminance(color)
    elif color is None and has_gradient:
        stops = [s.get("color") for s in gradient.get("stops") or [] if isinstance(s, dict)]
        values = [_luminance(c) for c in stops if _is_literal_color(c) and normalize_color(c) not in TRANSPARENT]
        values = [x for x in values if x is not None]
        lum = sum(values) / len(values) if values else None
    if lum is not None:
        tone = "dark" if lum < 0.5 else "light"
    elif isinstance(color, str) and "$variable(" in color:
        tone = "variable"
    else:
        tone = "image" if has_image else "default"
    return {"section_index": index, "section_label": _value(section, ADMIN_LABEL), "section_tone": tone,
            "section_background": {"color": color, "gradient": has_gradient, "image": has_image}}


def _skeleton(block: Block, schema5) -> dict:
    mod = schema5.module(block.name)
    attrs: dict = {}
    media: List[str] = []
    if mod is not None and isinstance(block.attrs, dict):
        attrs = design_attrs(block, mod)
        label = _value(block, ADMIN_LABEL) if block.name == "divi/section" else None
        if label:
            _set(attrs, ADMIN_LABEL.split(".") + ["desktop", "value"], label)
        if _preset_list(block):
            attrs["modulePreset"] = _preset_list(block)
        if _group_presets(block):
            attrs["groupPreset"] = _group_presets(block)
        media = _media(block, mod)
    return {"name": block.name, "attrs": attrs, "media": media,
            "children": [_skeleton(c, schema5) for c in block.blocks]}


def _css_slots(block: Block) -> List[str]:
    """Which custom CSS slots (mainElement, before, …) a block's `css` attr fills, at any breakpoint/state. Never the
    CSS itself: it can carry content (`content:"…"`) and image URLs."""
    css = block.attrs.get("css")
    slots = set()
    for bp_value in css.values() if isinstance(css, dict) else ():
        for st_value in bp_value.values() if isinstance(bp_value, dict) else ():
            if isinstance(st_value, dict):
                slots |= {k for k, v in st_value.items() if v}
    return sorted(slots)


def _font_entry(font_attr: dict) -> dict:
    def get(bp, key):
        v = font_attr.get(bp, {}).get("value") if isinstance(font_attr.get(bp), dict) else None
        return v.get(key) if isinstance(v, dict) else None
    return {"font": get("desktop", "family"), "weight": get("desktop", "weight"), "size": get("desktop", "size"),
            "size_tablet": get("tablet", "size"), "size_phone": get("phone", "size"),
            "line_height": get("desktop", "lineHeight"), "letter_spacing": get("desktop", "letterSpacing"),
            "color": get("desktop", "color")}


_STYLE_KEYS = ("family", "size", "weight", "color", "lineHeight", "letterSpacing")


def _heading_levels(block: Block, mod, schema5) -> Iterator[tuple]:
    """(level, font entry) for every `….decoration.font.font` element of a block that carries a heading level (the
    block's own, else the module default) and some font styling."""
    for attr, spec in mod.attrs.items():
        if not attr.endswith("decoration.font.font") or "headingLevel" not in schema5.leaf_spec(spec):
            continue
        font = _get(block.attrs, attr)
        if not isinstance(font, dict):
            continue
        styled = any(isinstance(s, dict) and isinstance(s.get("value"), dict)
                     and any(s["value"].get(k) for k in _STYLE_KEYS) for s in font.values())
        desktop = (font.get("desktop") or {}).get("value") if isinstance(font.get("desktop"), dict) else None
        default = ((mod.defaults.get(attr) or {}).get("desktop") or {}).get("value") or {}
        level = (desktop or {}).get("headingLevel") or default.get("headingLevel")
        if styled and level:
            yield level, _font_entry(font)


def _get(attrs, dotted: str):
    cur = attrs
    for k in dotted.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def _counted(counter: Counter) -> list:
    return [[json.loads(v), c] for v, c in counter.most_common()]


def _refs_out(refs: dict) -> dict:
    return {name: {**({"kind": r["kind"]} if "kind" in r else {}), "uses": r["uses"], "roles": sorted(r["roles"])}
            for name, r in sorted(refs.items())}


def tokens5_from_documents(docs: List, schema5) -> dict:
    styles: Dict[str, dict] = defaultdict(dict)
    presets: Dict[str, Counter] = defaultdict(Counter)
    group_presets: Dict[str, Counter] = defaultdict(Counter)
    palette = defaultdict(lambda: {"uses": 0, "roles": set()})
    global_refs = defaultdict(lambda: {"uses": 0, "roles": set()})
    var_refs = defaultdict(lambda: {"uses": 0, "roles": set()})
    levels: Dict[str, Counter] = defaultdict(Counter)
    body = Counter()
    section_padding, row_width, row_max, gutters, gaps = Counter(), Counter(), Counter(), Counter(), Counter()
    radii, shadows = Counter(), Counter()
    exemplars = []

    for doc in docs:
        parents, index_in_parent = {}, {}
        for block, _path, parent in doc.walk():
            parents[id(block)] = parent
        for holder in [None] + [b for b, _p, _x in doc.walk()]:
            kids = holder.blocks if holder is not None else [n for n in doc.nodes if isinstance(n, Block)]
            for i, kid in enumerate(kids):
                index_in_parent[id(kid)] = i
        section_index = -1
        for block, _path, parent in doc.walk():
            mod = schema5.module(block.name) if block.name.startswith("divi/") else None
            if mod is None or not isinstance(block.attrs, dict):
                continue
            if block.name == "divi/section":
                section_index += 1
                exemplars.append(_skeleton(block, schema5))
                pad = (_value(block, "module.decoration.spacing") or {}).get("padding") \
                    if isinstance(_value(block, "module.decoration.spacing"), dict) else None
                if isinstance(pad, dict) and (pad.get("top") or pad.get("bottom")):
                    section_padding[json.dumps({k: pad.get(k, "") for k in ("top", "right", "bottom", "left")})] += 1
            if block.name in ("divi/row", "divi/row-inner"):
                sizing = _value(block, "module.decoration.sizing")
                if isinstance(sizing, dict):
                    if sizing.get("width"):
                        row_width[json.dumps(sizing["width"])] += 1
                    if sizing.get("maxWidth"):
                        row_max[json.dumps(sizing["maxWidth"])] += 1
                gutter = _value(block, "module.advanced.gutter")
                if isinstance(gutter, dict) and gutter:
                    gutters[json.dumps(gutter, sort_keys=True)] += 1
                layout = _value(block, "module.decoration.layout")
                if isinstance(layout, dict) and (layout.get("columnGap") or layout.get("rowGap")):
                    gaps[json.dumps({k: layout.get(k, "") for k in ("columnGap", "rowGap")})] += 1

            for pid in _preset_list(block):
                presets[block.name][pid] += 1
            for group_id, spec in _group_presets(block).items():
                ids = spec.get("presetId") if isinstance(spec, dict) else None
                for pid in ([ids] if isinstance(ids, str) else ids if isinstance(ids, list) else []):
                    if isinstance(pid, str) and pid and pid != "default":
                        group_presets[json.dumps([spec.get("groupName"), block.name, group_id])][pid] += 1

            # Colors, variables, radii and shadows over the leaves Divi reads (global refs over every group).
            for attr, bp, st, value in _leaves(block, mod):
                design_group = _group(attr) in DESIGN_GROUPS and _family(mod, attr) not in NON_DESIGN_FAMILIES
                for res, v in mod.walk_value(attr, bp, st, value):
                    role = attr + (f".{res.sub_path}" if res.sub_path else "")
                    ltype = (res.leaf or {}).get("type")
                    for s in _strings(v):
                        for ref in variable_refs(s):
                            name = (ref.get("value") or {}).get("name") if isinstance(ref.get("value"), dict) else None
                            if not isinstance(name, str):
                                continue
                            if name.startswith("gcid-"):
                                global_refs[name]["uses"] += 1
                                global_refs[name]["roles"].add(role)
                            elif name.startswith("gvid-"):
                                var_refs[name]["uses"] += 1
                                var_refs[name]["roles"].add(role)
                                if ltype in VARIABLE_KINDS:
                                    var_refs[name]["kind"] = VARIABLE_KINDS[ltype]
                    if not design_group or res.status != "ok":
                        continue
                    colors = [v] if ltype == "color" else \
                        [s.get("color") for s in v if isinstance(s, dict)] if ltype == "gradient" and isinstance(v, list) \
                        else []
                    for c in colors:
                        if _is_literal_color(c):
                            p = palette[normalize_color(c)]
                            p["uses"] += 1
                            p["roles"].add(role)
                    if ltype == "radius" and v and bp == "desktop" and st == "value":
                        radii[json.dumps(v, sort_keys=True)] += 1
                # walk_value splits a box shadow into leaves; count the whole desktop value once.
                if _family(mod, attr) == "box-shadow" and bp == "desktop" and st == "value" \
                        and isinstance(value, dict) and value.get("style") not in (None, "", "none"):
                    shadows[json.dumps(value, sort_keys=True)] += 1

            for level, entry in _heading_levels(block, mod, schema5):
                levels[level][json.dumps(entry, sort_keys=True)] += 1
            if block.name == "divi/text":
                font = _get(block.attrs, "content.decoration.bodyFont.body.font")
                if isinstance(font, dict):
                    entry = _font_entry(font)
                    if any(entry.values()):
                        body[json.dumps(entry, sort_keys=True)] += 1

            design = design_attrs(block, mod)
            html_attrs = _value(block, HTML_ATTRS)
            html_attrs = {k: v for k, v in (html_attrs or {}).items() if v} if isinstance(html_attrs, dict) else {}
            css_slots = _css_slots(block)
            module_preset, gp = _preset_list(block), _group_presets(block)
            key = json.dumps([design, module_preset, gp, html_attrs, css_slots], sort_keys=True)
            section, column, cur = None, None, parent
            while cur is not None:
                if cur.name in ("divi/column", "divi/column-inner") and column is None:
                    column = cur
                if cur.name == "divi/section":
                    section = cur
                cur = parents.get(id(cur))
            ctx = _section_context(section, section_index) if section is not None else {}
            ctx["column_type"] = (_value(column, "module.advanced.type") or "") if column is not None else ""
            ctx["admin_label"] = _value(block, ADMIN_LABEL)
            ctx["index_in_parent"] = index_in_parent.get(id(block), 0)
            entry = styles[block.name].setdefault(key, {
                "uses": 0, "attrs": design, "module_preset": module_preset, "group_presets": gp,
                "html_attributes": html_attrs, "custom_css_slots": css_slots, "media": [], "contexts": []})
            entry["uses"] += 1
            if len(entry["contexts"]) < MAX_CONTEXTS:
                entry["contexts"].append(ctx)
            entry["media"] = sorted(set(entry["media"]) | set(_media(block, mod)))

    scale = {lvl: {**json.loads(c.most_common(1)[0][0]), "uses": sum(c.values())} for lvl, c in sorted(levels.items())}
    heading_fonts = Counter(v["font"] for v in scale.values() if v["font"])
    body_entry = json.loads(body.most_common(1)[0][0]) if body else {}
    group_out: Dict[str, list] = defaultdict(list)
    for spec_key, cnt in group_presets.items():
        group_name, module, group_id = json.loads(spec_key)
        for pid, uses in cnt.most_common():
            group_out[group_name or ""].append({"id": pid, "uses": uses, "module": module, "group_id": group_id})
    return {
        "colors": {"palette": sorted(({"hex": h, "uses": v["uses"], "roles": sorted(v["roles"])}
                                      for h, v in palette.items()), key=lambda p: -p["uses"]),
                   "global_refs": _refs_out(global_refs)},
        "variables_refs": _refs_out(var_refs),
        "typography": {"heading_font": heading_fonts.most_common(1)[0][0] if heading_fonts else "",
                       "body_font": body_entry.get("font") or "", "body": body_entry, "scale": scale},
        "spacing": {"section_padding": _counted(section_padding),
                    "row": {"width": _counted(row_width), "max_width": _counted(row_max)},
                    "gutters": _counted(gutters), "gaps": _counted(gaps)},
        "shapes": {"radii": _counted(radii), "shadows": _counted(shadows)},
        "presets": {name: [{"id": i, "uses": c} for i, c in cnt.most_common()] for name, cnt in presets.items()},
        "group_presets": {name: sorted(v, key=lambda e: -e["uses"]) for name, v in group_out.items()},
        "module_styles": {name: sorted(entries.values(), key=lambda e: -e["uses"]) for name, entries in styles.items()},
        "section_exemplars": exemplars,
    }
