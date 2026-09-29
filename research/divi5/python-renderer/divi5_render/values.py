"""Attribute values: responsive/state access with Divi 5's inheritance, and design variables.

- get() walks nested dicts; attr_value() is ModuleUtils::get_attr_value (desktop -> tablet -> phone
  inheritance, a state falling back to the breakpoint's `value`, the getOrInherit*/getAndInherit* modes).
- Values resolves `$variable({...})$` references the way Divi prints them: `var(--gcid-…)` / `var(--gvid-…)`, or,
  for a colour variable with settings (opacity, hue, saturation, lightness), the relative colour
  `hsl(from <the colour's value> calc(h + H) calc(s + S) calc(l + L) / A)`, which needs the site's global colour
  values (tokens.json `colors.global`).
"""
from __future__ import annotations

import html as _html
import json
import re

BREAKPOINTS = ("desktop", "tablet", "phone")
# States this renderer prints. Divi also has sticky (and focus/checked/active on form fields); those are
# reported by the coverage report instead (sticky/scroll effects are outside the Python preview's scope).
STATES = ("value", "hover")

_VAR = re.compile(r"\$variable\((\{.*?\})\)\$")


def get(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict) or p not in d:
            return default
        d = d[p]
    return d


def _merge(base, over):
    """PHP array_replace_recursive for dicts."""
    if not isinstance(base, dict) or not isinstance(over, dict):
        return over
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(out.get(k), dict) and isinstance(v, dict) else v
    return out


merge = _merge


def inherit_value(attr: dict, bp: str, state: str, closest: bool = False):
    """ModuleUtils::inherit_attr_value for the desktop base breakpoint."""
    if not isinstance(attr, dict) or (bp == "desktop" and state == "value"):
        return None
    inherited = None
    if state != "value":
        inherited = get(attr, bp, "value")
    larger = list(reversed(BREAKPOINTS[:BREAKPOINTS.index(bp)])) if bp in BREAKPOINTS else []
    for lb in larger:
        v = get(attr, lb, "value")
        if isinstance(v, dict) and not closest:
            inherited = _merge(v, inherited if isinstance(inherited, dict) else ({} if inherited is None else inherited))
        elif v is not None and inherited is None:
            inherited = v
            break
        elif inherited is not None and closest:
            break
    return inherited


def attr_value(attr, bp: str = "desktop", state: str = "value", mode: str = "getOrInheritAll", default=None):
    """ModuleUtils::get_attr_value."""
    own = get(attr, bp, state)
    inherited = inherit_value(attr, bp, state, closest="Closest" in mode)
    if mode.startswith("getAnd"):
        out = _merge(inherited, own) if isinstance(own, dict) and isinstance(inherited, dict) else (
            own if own is not None else inherited)
    elif mode.startswith("getOr"):
        out = own if own is not None else inherited
    elif mode.startswith("inherit"):
        out = inherited
    else:
        out = own
    return out if out is not None else default


def esc_attr(s) -> str:
    return _html.escape(str(s), quote=True)


def esc_url(url: str) -> str:
    """WordPress esc_url() as far as the preview needs it: `&` -> `&#038;`, quotes and angle brackets dropped."""
    url = str(url or "").strip()
    url = re.sub(r"[\s<>\"'`]", lambda m: "%20" if m.group(0) == " " else "", url)
    return url.replace("&amp;", "&").replace("&#038;", "&").replace("&", "&#038;")


class Values:
    """Variable resolution for one render (the site's global colour values come from tokens.json)."""

    def __init__(self, tokens: dict | None = None):
        tokens = tokens if isinstance(tokens, dict) else {}
        colors = tokens.get("colors") if isinstance(tokens.get("colors"), dict) else {}
        self.colors = {}
        for gid, e in (colors.get("global") or {}).items():
            v = e.get("value") if isinstance(e, dict) else e
            if isinstance(v, str) and v:
                self.colors[gid] = v
        for e in (colors.get("customizer") or {}).values():
            if isinstance(e, dict) and e.get("id") and isinstance(e.get("value"), str) and e["value"]:
                self.colors.setdefault(e["id"], e["value"])

    def resolve(self, v):
        if not isinstance(v, str) or "$variable(" not in v:
            return v

        def rep(m):
            try:
                d = json.loads(m.group(1))
            except ValueError:
                return m.group(0)
            val = d.get("value") or {}
            name, st = val.get("name", ""), val.get("settings") or {}
            if d.get("type") == "color" and st and name in self.colors:
                h, s_, l_ = (st.get(k, 0) or 0 for k in ("hue", "saturation", "lightness"))
                op = st.get("opacity")
                alpha = f" / {op / 100:g}" if op not in (None, 100) else ""
                return f"hsl(from {self.colors[name]} calc(h + {h}) calc(s + {s_}) calc(l + {l_}){alpha})"
            return f"var(--{name})"
        return _VAR.sub(rep, v)


def is_variable(v) -> bool:
    return isinstance(v, str) and "$variable(" in v
