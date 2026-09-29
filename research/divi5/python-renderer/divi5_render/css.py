"""The builder style sheet, selector helpers and the generic statement engine.

statements() is a port of Divi 5's Utils::get_statements (GetStatementsTrait): for every breakpoint and state of
a responsive attribute it picks the selector (Utils::get_selector, hover via _generate_pseudo_state_selector),
the important flags (a bool, or per-property flags inherited like the attribute), calls a declaration function,
and splits the declarations over `propertySelectors` (with the shorthand map: `padding` covers padding-top …).
"""
from __future__ import annotations

import json
import re

from .values import BREAKPOINTS, STATES, attr_value, get

MEDIA = {"desktop": "", "tablet": "@media only screen and (max-width:980px)",
         "phone": "@media only screen and (max-width:767px)"}
SHORTHAND = {
    "padding": ["padding-top", "padding-right", "padding-bottom", "padding-left"],
    "margin": ["margin-top", "margin-right", "margin-bottom", "margin-left"],
    "border-radius": ["border-top-left-radius", "border-top-right-radius", "border-bottom-right-radius",
                      "border-bottom-left-radius"],
}


class Sheet:
    """(media, selector, [declarations]) in insertion order; printed minified, desktop rules first, then the
    tablet and phone media queries (what Divi's style grouping amounts to for a set comparison)."""

    def __init__(self):
        self.rules: list = []

    def add(self, sel: str, decls, bp: str = "desktop"):
        decls = [d for d in decls if d]
        if decls and sel:
            self.rules.append((MEDIA.get(bp, ""), sel, decls))

    def text(self) -> str:
        by_media: dict = {}
        for media, sel, decls in self.rules:
            by_media.setdefault(media, []).append(f"{sel}{{{';'.join(decls)}}}")
        out = ["".join(by_media.pop("", []))]
        for media in (MEDIA["tablet"], MEDIA["phone"]):
            if media in by_media:
                out.append(f"{media}{{{''.join(by_media[media])}}}")
        return "".join(out)


def split_selectors(sel: str) -> list:
    return [s.strip() for s in re.split(r",\s?", sel) if s.strip()]


def hover_selector(sel: str) -> str:
    """Utils::_generate_pseudo_state_selector(…, 'hover')."""
    out = []
    for s in split_selectors(sel):
        if ":hover" in s:
            out.append(s)
        elif ":" in s:
            head, tail = s.split(":", 1)
            out.append(f"{head}:hover:{tail}")
        else:
            out.append(s + ":hover")
    return ", ".join(out)


def state_selector(sel: str, state: str) -> str:
    return hover_selector(sel) if state == "hover" else sel


def get_selector(selectors: dict, bp: str, state: str) -> str:
    """Utils::get_selector for the states this renderer prints."""
    base = get(selectors, "desktop", "value") or ""
    bp_base = get(selectors, bp, "value") if (bp != "desktop" and state != "value" and get(selectors, bp, "value")) \
        else base
    current = get(selectors, bp, state) or ""
    effective = current or bp_base
    if state == "hover":
        return hover_selector(effective)
    return current or bp_base


def minify(sel: str) -> str:
    return re.sub(r"\s*,\s*", ",", sel.strip())


def expand(tpl: str, oc: str, **extra) -> str:
    """A module.json selector template for one module instance ({{selector}} = its order class)."""
    s = tpl.replace("{{selector}}", oc).replace("{{baseSelector}}", oc).replace("{{selectorPrefix}}", "")
    s = s.replace("{{nestedModuleNameSelector}}", "")
    for k, v in extra.items():
        s = s.replace("{{" + k + "}}", v)
    return s


def expand_props(props, oc: str, **extra):
    return json.loads(expand(json.dumps(props), oc, **extra)) if props else {}


def is_important(imp, prop: str) -> bool:
    """StyleDeclarations: `important` is a bool or a {property: bool} map."""
    if imp is True:
        return True
    return bool(imp.get(prop)) if isinstance(imp, dict) else False


def current_important(important, bp: str, state: str):
    if isinstance(important, bool) or important is None:
        return bool(important)
    imp = important
    # shorthand keys ({"padding": true}) cover their longhands
    out = attr_value(imp, bp, state, "getOrInheritAll", {}) or {}
    if isinstance(out, dict):
        out = dict(out)
        for short, longs in SHORTHAND.items():
            if short in out:
                for p in longs:
                    out.setdefault(p, out[short])
    return out


def _prop_selectors_for(property_selectors: dict, bp: str, state: str) -> dict:
    """{longhand property: selector} active for this breakpoint/state (getAndInheritAll of the map)."""
    cur = attr_value(property_selectors, bp, state, "getAndInheritAll", {}) or {}
    out = {}
    for name, sel in cur.items():
        for p in SHORTHAND.get(name, [name]):
            out[p] = sel
    return out


def _prop_selector(property_selectors: dict, prop: str, bp: str, state: str) -> str:
    """Utils::get_selector_of_property_selectors."""
    def lookup(b, st):
        m = get(property_selectors, b, st) or {}
        for name, sel in m.items():
            if prop in SHORTHAND.get(name, [name]):
                return sel
        return None
    base = lookup("desktop", "value") or ""
    bp_base = lookup(bp, "value") if (bp != "desktop" and state != "value" and lookup(bp, "value")) else base
    current = lookup(bp, state) or ""
    effective = current or bp_base
    if state == "hover":
        return hover_selector(effective)
    return current or bp_base


def statements(ctx, attr, decl_fn, selector: str = "", selectors: dict | None = None, important=False,
               property_selectors: dict | None = None, printed: dict | None = None, selector_fn=None,
               bp_filter=None) -> list:
    """Prints the rules for one responsive attribute. `decl_fn(value, default, bp, state, attr)` returns a list of
    (property, value[, important]) tuples (important None = decided by `important`). Returns the states that
    printed something, e.g. ["value", "hover"]."""
    if not isinstance(attr, dict) or not attr:
        return []
    selectors = selectors or {"desktop": {"value": selector}}
    printed = printed or {}
    used = []
    for bp in BREAKPOINTS:
        if bp not in attr or not isinstance(attr[bp], dict):
            continue
        if bp_filter and bp not in bp_filter:
            continue
        for state in STATES:
            if state not in attr[bp]:
                continue
            value = attr[bp][state]
            sel = get_selector(selectors, bp, state)
            imp = current_important(important, bp, state)
            decls = decl_fn(value, get(printed, bp, state) or {}, bp, state, attr) or []
            if not decls:
                continue
            groups: dict = {}
            psel = _prop_selectors_for(property_selectors, bp, state) if property_selectors else {}
            for d in decls:
                prop, val = d[0], d[1]
                flag = d[2] if len(d) > 2 and d[2] is not None else is_important(imp, prop)
                target = _prop_selector(property_selectors, prop, bp, state) if prop in psel else sel
                if selector_fn:
                    target = selector_fn(target, bp, state)
                groups.setdefault(target, []).append(f"{prop}:{val}{'!important' if flag else ''}")
            for target, ds in groups.items():
                ctx.css.add(minify(target), ds, bp)
            used.append(state)
    return used
