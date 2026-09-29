"""Warn when a Divi 5 page uses literal colors, fonts or section spacing that are not the site's design tokens.

The Divi 5 counterpart of divi_checks_tokens.py: same codes (W_OFF_PALETTE_COLOR, W_OFF_BRAND_FONT,
W_OFF_SCALE_SPACING), same palette/font reading (imported from it). Only literal values are checked: a
`$variable(...)$` reference is a global color/font and is never off-palette. Tokens are read defensively (the Divi 5
tokens shape is still settling), and a check whose token list is empty stays silent, as in Divi 4.
"""
from __future__ import annotations

from divi5_blocks import Block, iter_leaves
from divi_checks_tokens import _fonts, _palette
from divi_checks_values import COLOR_RE, normalize_color

_TRANSPARENT = ("transparent", "rgba(0,0,0,0)", "rgba(255,255,255,0)")
SPACING_ATTR = "module.decoration.spacing"


def _safe(fn, tokens):
    try:
        return fn(tokens)
    except (AttributeError, TypeError, KeyError):
        return set()


def _paddings(tokens: dict) -> set:
    """Section paddings the site uses as (top, bottom) pairs, from tokens spacing.section_padding: Divi 4 entries
    "top|right|bottom|left|syncV|syncH" (or [that, count]), or Divi 5 {top, bottom} objects."""
    spacing = tokens.get("spacing")
    entries = spacing.get("section_padding") if isinstance(spacing, dict) else None
    out = set()
    for entry in entries if isinstance(entries, list) else ():
        if isinstance(entry, (list, tuple)) and entry:
            entry = entry[0]
        if isinstance(entry, str):
            parts = entry.split("|")
            parts += [""] * (3 - len(parts))
            out.add((parts[0], parts[2]))
        elif isinstance(entry, dict):
            out.add((str(entry.get("top", "")), str(entry.get("bottom", ""))))
    return out


def check_tokens5(doc, schema5, tokens: dict, report) -> None:
    if not isinstance(tokens, dict) or not tokens:
        return
    palette, fonts = _safe(_palette, tokens), _safe(_fonts, tokens)
    paddings = _paddings(tokens)
    for block, path, _parent in doc.walk():
        if not isinstance(block, Block) or not block.name.startswith("divi/") or not isinstance(block.attrs, dict):
            continue
        mod = schema5.module(block.name)
        if mod is None:
            continue
        for attr, bp, st, value in iter_leaves(block.attrs):
            if bp is None:
                continue
            if paddings and block.name == "divi/section" and attr == SPACING_ATTR and bp == "desktop" \
                    and st == "value":
                _padding(block, path, paddings, value, report)
            for res, v in mod.walk_value(attr, bp, st, value):
                if res.status != "ok" or res.leaf is None or not isinstance(v, str) or "$variable(" in v:
                    continue
                full = (res.attr_path or attr) + (f".{res.sub_path}" if res.sub_path else "")
                where = f"{full}:{bp}:{st}"
                ltype = res.leaf.get("type")
                if ltype == "color" and palette and COLOR_RE.match(v.strip()):
                    color = normalize_color(v)
                    if not color.startswith("gcid-") and color not in palette and color not in _TRANSPARENT:
                        report("warning", "W_OFF_PALETTE_COLOR", f"{full}={v} is not in the site's palette",
                               node=block, path=path, attr=where, value=v,
                               hint="Use a color from tokens.json colors.")
                elif ltype == "font-family" and fonts and v.strip():
                    family = v.split("|")[0]
                    if family and family.lower() not in fonts:
                        report("warning", "W_OFF_BRAND_FONT", f"{full} uses '{family}', which the site does not use",
                               node=block, path=path, attr=where, value=v)


def _padding(block, path, paddings, value, report) -> None:
    pad = value.get("padding") if isinstance(value, dict) else None
    if not isinstance(pad, dict):
        return
    top, bottom = pad.get("top"), pad.get("bottom")
    if not (isinstance(top, str) and isinstance(bottom, str) and top and bottom):
        return
    if "$variable(" in top or "$variable(" in bottom:
        return  # a variable reference is never off-token
    if (top, bottom) not in paddings:
        report("warning", "W_OFF_SCALE_SPACING", f"Section padding {top} / {bottom} is not one the site uses",
               node=block, path=path, attr=f"{SPACING_ATTR}.padding:desktop:value", value=f"{top}|{bottom}",
               hint="Reuse a value from tokens.json spacing.section_padding.")
