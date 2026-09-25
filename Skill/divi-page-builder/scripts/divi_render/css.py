"""The style sheet the modules write into, plus selector helpers.

Mirrors ET_Builder_Element::set_style() + get_style(): rules are bucketed per device (desktop,
tablet media query, phone media query), keyed by the minified selector in first-seen order, and
declarations keep their insertion order (duplicates included, as Divi prints them).
"""
from __future__ import annotations

import re

from .values import MEDIA

ORDER_CLASS = "%%order_class%%"


# ----------------------------------------------------------------------------- minifying
def minify_decl(d: str) -> str:
    d = re.sub(r"\s+", " ", d).strip().rstrip(";").strip()
    d = re.sub(r"\s*!important", "!important", d)
    d = re.sub(r"\s*,\s*", ",", d)
    d = re.sub(r"^([-\w]+)\s*:\s*", r"\1:", d)
    return d


def minify_sel(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*,\s*", ",", s)
    s = re.sub(r"\s*>\s*", ">", s)
    return s


def split_decls(decl: str) -> list:
    """Splits 'a:b; c:url(x;y)' on top-level semicolons and minifies each declaration."""
    out, depth, cur = [], 0, ""
    for ch in decl:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            if cur.strip():
                out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [minify_decl(x) for x in out if minify_decl(x)]


# ----------------------------------------------------------------------------- selectors
def add_hover_to_order_class(sel: str) -> str:
    """HoverOptions::add_hover_to_order_class(): '.x_0 .a' -> '.x_0:hover .a'."""
    parts = [p.strip() for p in sel.split(",")]
    return ", ".join(re.sub(r"(.*%%order_class%%[^\s:]*)(.*)", r"\1:hover\2", p, count=1) for p in parts)


def add_hover_to_selectors(sel: str) -> str:
    """HoverOptions::add_hover_to_selectors(): ':hover' on the last compound, before pseudo-elements."""
    parts = [p.strip() for p in sel.split(",")]
    return ", ".join(re.sub(r"(.+\s)*([^:]+?)((::?[-a-z()\[\]]+)+)?$", r"\1\2:hover\3", p, count=1, flags=re.I)
                     for p in parts)


def suffix_selectors(sel: str, suffix: str) -> str:
    return ", ".join(p.strip() + suffix for p in sel.split(","))


def prefix_selectors(sel: str, prefix: str) -> str:
    return ", ".join(f"{prefix} {p.strip()}" for p in sel.split(","))


# ----------------------------------------------------------------------------- style sheet
class StyleSheet:
    def __init__(self):
        self.rules = {d: {} for d in MEDIA}  # device -> {selector: [decls]}

    def add(self, order_class: str, selector, decl: str, device: str = "desktop"):
        if not decl or not decl.strip():
            return
        sels = selector if isinstance(selector, list) else [selector]
        for sel in sels:
            s = minify_sel(sel.replace(ORDER_CLASS, "." + order_class))
            self.rules[device].setdefault(s, []).extend(split_decls(decl))

    def text(self) -> str:
        out = []
        for dev in MEDIA:
            rules = [f"{sel}{{{';'.join(decls)}}}" for sel, decls in self.rules[dev].items()]
            if not rules:
                continue
            body = "\n".join(rules)
            out.append(f"{MEDIA[dev]}{{{body}\n}}" if MEDIA[dev] else body)
        return "\n".join(out)
