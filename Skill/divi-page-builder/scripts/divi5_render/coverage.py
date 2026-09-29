"""Key-level coverage: which attribute values of a page the Python renderer honours, and which it ignores.

Every module handler declares the attribute paths it renders (`handled`: path -> a family name from FAMILIES,
or "*" for a value it uses whole, such as `content.innerContent`). check() walks every leaf of the block's attrs
(breakpoint and state included) and, inside each value, every sub-key (`module.decoration.border.styles.all.width`),
and lists what no handler covers: an unknown path, a sub-key the family does not print, a hover value of a family
without hover support, or a state/breakpoint this renderer never prints (sticky, and Divi 5's optional
widescreen/tablet-wide/phone-wide breakpoints). The spike showed why the granularity matters: a report that
marked all of `module.decoration.background` handled hid an unsupported background image.

"Honoured" is still not "correct": a special case such as the Button's `:hover` padding copy is read and can
be wrong. Only the parity corpus (tests/test_render5_fidelity.py) catches those.
"""
from __future__ import annotations

import divi5_blocks as B

from .values import BREAKPOINTS, STATES

_SIDES = ("top", "right", "bottom", "left")
FAMILIES = {
    "background": {"color", "image.url", "image.size", "image.position", "image.repeat", "gradient.enabled",
                   "gradient.direction", "gradient.stops", "gradient.overlaysImage", "gradient.type",
                   "gradient.length", "gradient.directionRadial",
                   "enableColor"},  # enableColor: a legacy conversion key, no front-end effect (no PHP reads it)
    "spacing": {f"{k}.{s}" for k in ("padding", "margin") for s in _SIDES + ("syncVertical", "syncHorizontal")},
    "sizing": {"width", "maxWidth", "minWidth", "minHeight", "height", "maxHeight", "alignment"},
    "imageSizing": {"width", "maxWidth", "minHeight", "height", "maxHeight", "alignment", "forceFullwidth"},
    "border": {f"radius.{k}" for k in ("sync", "topLeft", "topRight", "bottomRight", "bottomLeft")}
              | {f"styles.{side}.{k}" for side in ("all",) + _SIDES for k in ("width", "color", "style")},
    "boxShadow": {"style", "horizontal", "vertical", "blur", "spread", "color", "position"},
    "font": {"family", "weight", "style", "capitalization", "color", "size", "letterSpacing", "lineHeight",
             "textAlign", "headingLevel"},
    "layout": {"display"},
    "button": {"enable"},
    "htmlAttributes": {"id", "class"},
    "css": {"mainElement"},
    "gutter": {"makeEqual"},
}
HOVER = {"background", "font", "spacing", "sizing", "border", "boxShadow"}
# Bookkeeping attributes that never affect the front end.
META_PATHS = ("builderVersion", "locked", "collapsed", "module.meta", "_originalContent")


def _flat(v, prefix=""):
    if isinstance(v, dict) and v:
        for k, x in v.items():
            yield from _flat(x, f"{prefix}.{k}" if prefix else k)
    else:
        yield prefix


def check(ctx, slug: str, attrs: dict, handled: dict, extra_ignored=(), targets=("main",)):
    """Records one module instance's coverage in ctx.coverage. `targets`: the elements the handler puts custom
    attributes (module.decoration.attributes) on; one aimed elsewhere is listed."""
    ignored, n = [], 0
    items = (((((attrs or {}).get("module") or {}).get("decoration") or {}).get("attributes") or {})
             .get("desktop") or {}).get("value") or {}
    for item in items.get("attributes") or [] if isinstance(items, dict) else []:
        if isinstance(item, dict) and (item.get("targetElement") or "main") not in targets:
            ignored.append(f"module.decoration.attributes[{item.get('name')}@{item.get('targetElement')}]")
    for path, bp, st, v in B.iter_leaves(attrs if isinstance(attrs, dict) else {}):
        if any(path == m or path.startswith(m + ".") for m in META_PATHS):
            continue
        spec = handled.get(path)
        if spec is None:  # a whole-value ("*") entry covers the non-responsive keys under it (groupPreset.<id>.…)
            spec = next((s for h, s in handled.items() if s == "*" and path.startswith(h + ".")), None)
        subs = list(_flat(v)) if isinstance(v, dict) and v else [""]
        for sub in subs:
            n += 1
            full = f"{path}.{sub}" if sub else path
            if spec is None:
                ignored.append(full)
                continue
            if bp is not None and bp not in BREAKPOINTS:
                ignored.append(f"{full}@{bp}")
                continue
            if st is not None and st not in STATES:
                ignored.append(f"{full}@{st}")
                continue
            if st == "hover" and spec != "*" and spec not in HOVER:
                ignored.append(f"{full}@hover")
                continue
            if spec == "*" or not sub:
                continue
            keys = FAMILIES.get(spec, set())
            if sub not in keys and sub.split(".")[0] not in keys:
                ignored.append(full)
    ignored += list(extra_ignored)
    ctx.coverage.append({"module": slug, "attrs": n, "ignored": sorted(set(ignored))})


def report(ctx) -> dict:
    """Per module type: count, attribute values set, and the ones never honoured ('ignored'); plus the module
    types rendered as placeholders (`unsupported_modules`, which the --exact Playground preview renders) and
    the ones that show the live site's data (`needs_site_data`, which neither preview can show)."""
    by_module: dict = {}
    for c in ctx.coverage:
        t = by_module.setdefault(c["module"], {"count": 0, "attrs": 0, "ignored": {}})
        t["count"] += 1
        t["attrs"] += c["attrs"]
        for a in c["ignored"]:
            t["ignored"][a] = t["ignored"].get(a, 0) + 1
    total = sum(c["attrs"] for c in ctx.coverage)
    ign = sum(len(c["ignored"]) for c in ctx.coverage)
    return {"modules": len(ctx.coverage), "unsupported_modules": dict(ctx.unsupported),
            "needs_site_data": dict(ctx.site_data), "attrs_total": total, "attrs_ignored": ign,
            "attr_coverage_pct": round(100 * (total - ign) / total, 1) if total else 100.0,
            "by_module": by_module,
            "ignored": sorted({f"{c['module']}:{p}" for c in ctx.coverage for p in c["ignored"]})}
