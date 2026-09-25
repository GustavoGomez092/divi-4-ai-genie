"""Warn when a page uses colors, fonts or section spacing that are not part of the site's design tokens."""
from __future__ import annotations

from divi_checks_values import COLOR_TYPES, normalize_color


def _palette(tokens: dict) -> set:
    colors = tokens.get("colors", {})
    values = list(colors.get("global", {}).values()) + list(colors.get("customizer", {}).values())
    values += [p["hex"] for p in colors.get("palette", [])]
    return {normalize_color(v) for v in values if v}


def _fonts(tokens: dict) -> set:
    typo = tokens.get("typography", {})
    fonts = {typo.get("heading_font", ""), typo.get("body_font", "")}
    for level in typo.get("scale", {}).values():
        fonts.add((level.get("font") or "").split("|")[0])
    for entries in tokens.get("module_styles", {}).values():
        for entry in entries:
            for name, value in entry.get("attrs", {}).items():
                if name.endswith("_font"):
                    fonts.add(value.split("|")[0])
    return {f.lower() for f in fonts if f}


def check_tokens(doc, schema, tokens: dict, report) -> None:
    palette, fonts = _palette(tokens), _fonts(tokens)
    gcids = set(tokens.get("colors", {}).get("global", {}))
    paddings = {v for v, _ in tokens.get("spacing", {}).get("section_padding", [])}
    for node, path, _parent in doc.walk():
        mod = schema.module(node.tag)
        if mod is None:
            continue
        for name in node.attrs:
            res = mod.resolve(name)
            if res is None or not res.field:
                continue
            value = node.value(name)
            if not value:
                continue
            ftype = res.field.get("type")
            if ftype in COLOR_TYPES:
                color = normalize_color(value)
                if color.startswith("gcid-"):
                    if color not in gcids:
                        report("warning", "W_UNKNOWN_GLOBAL_COLOR", f"{name} uses global color {value}, which the site does not define",
                               node=node, path=path, attr=name, value=value)
                elif palette and color not in palette and color not in ("transparent", "rgba(0,0,0,0)", "rgba(255,255,255,0)"):
                    report("warning", "W_OFF_PALETTE_COLOR", f"{name}={value} is not in the site's palette",
                           node=node, path=path, attr=name, value=value, hint="Use a color from tokens.json colors.")
            elif ftype == "font" and fonts:
                family = value.split("|")[0]
                if family and family.lower() not in fonts:
                    report("warning", "W_OFF_BRAND_FONT", f"{name} uses '{family}', which the site does not use",
                           node=node, path=path, attr=name, value=value)
        if node.tag == "et_pb_section" and paddings and "custom_padding" in node.attrs:
            value = node.value("custom_padding")
            if value and value not in paddings:
                report("warning", "W_OFF_SCALE_SPACING", f"Section padding {value} is not one the site uses",
                       node=node, path=path, attr="custom_padding", value=value,
                       hint="Reuse a value from tokens.json spacing.section_padding.")
