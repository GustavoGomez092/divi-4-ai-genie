"""Attribute-path, value-type, escaping, preset and variable rules for Divi 5 blocks.

The Divi 5 counterpart of divi_checks_values.py; findings go through validate.Reporter. Paths and leaf types come
from the compiled schema (divi5_schema): every responsive value (attrs … {breakpoint: {state: value}}) is resolved,
object values are walked leaf by leaf (ModuleSchema5.walk_value), and each typed leaf value is checked by
value_problems5() against the grammar of its type (families5.json `_types`).
"""
from __future__ import annotations

import difflib
import json
import re
from collections import defaultdict
from fractions import Fraction
from typing import Dict, Iterator, List, Optional, Set, Tuple
from urllib.parse import urlparse

from divi5_blocks import BREAKPOINTS, DISABLED_ON_BREAKPOINTS, STATES, Block, get_attr
from divi5_schema import is_legacy_column_attr

PLACEHOLDER = "divi/placeholder"
# Breakpoints Divi 5 ships switched off (Settings > Breakpoints); values there apply only once the site enables them.
DISABLED_BREAKPOINTS = ("phoneWide", "tabletWide", "widescreen", "ultraWide")
# The five Customizer colors Divi 5 exposes as global colors: always defined (tokens-and-detection.md §2).
CUSTOMIZER_COLOR_IDS = frozenset({"gcid-primary-color", "gcid-secondary-color", "gcid-heading-color",
                                  "gcid-body-color", "gcid-link-color"})
IMAGE_MODULES = ("divi/image", "divi/fullwidth-image")
_KNOWN_BP = frozenset(BREAKPOINTS + DISABLED_ON_BREAKPOINTS)
_STATE_SET = frozenset(STATES)

_HEX = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")
_COLOR_FUNC = re.compile(r"(?i:rgba?|hsla?)\(.+\)", re.S)
_VAR_FUNC = re.compile(r"var\(--[\w-]+(?:\s*,.*)?\)", re.S)
_LENGTH_FUNC = re.compile(r"(?i:calc|clamp|min|max|var)\(.+\)", re.S)
_NUMBER = re.compile(r"-?(?:\d+\.?\d*|\.\d+)")
_NUM_UNIT = re.compile(r"(-?(?:\d+\.?\d*|\.\d+))([a-zA-Z%]*)")
# Divi 4 CSS_KEYWORDS (divi_checks_values.py) plus the intrinsic sizing keywords.
_LENGTH_KEYWORDS = frozenset({"auto", "none", "inherit", "initial", "unset", "normal", "fit-content", "min-content",
                              "max-content"})
_GENERIC_UNITS = frozenset({"px", "%", "em", "rem", "ex", "ch", "vw", "vh", "vmin", "vmax", "cm", "mm", "in", "pt",
                            "pc", "deg", "rad", "turn", "ms", "s", "fr"})
_FONT_WEIGHT_WORDS = frozenset({"normal", "bold", "lighter", "bolder"})
_SPACING_SIDES = ("top", "right", "bottom", "left")
_SPACING_SYNC = ("syncVertical", "syncHorizontal")
_RADIUS_CORNERS = ("topLeft", "topRight", "bottomRight", "bottomLeft")
_ICON_TYPES = ("divi", "fa")
_SHORTCODE_OPEN = re.compile(r"\[[A-Za-z]")
# Which `$variable()$` types may stand for a whole value of each leaf type (tokens-and-detection.md §2: the VB emits
# color, content and gradient; numbers, fonts, strings, links and images are all `content`).
_VARIABLE_TYPES = {
    "color": {"color"}, "gradient": {"gradient"}, "radius": {"content"},
    "length": {"content"}, "number": {"content"}, "text": {"content"}, "html": {"content"}, "url": {"content"},
    "image": {"content"}, "font-family": {"content"}, "font-weight": {"content"},
}

# Length leaves whose CSS property needs a unit (doc-experiments.md §8: Divi prints a unitless value verbatim, e.g.
# padding-top:41!important, and the browser drops the declaration). Matched on the leaf's last key; lineHeight,
# durations, delays, filters, opacities, gradient directions and stroke widths are not listed, so a unitless number
# stays valid there (CSS takes <number> for line-height, and Divi feeds the others to JS or adds its own unit).
_UNIT_KEYS = frozenset({"width", "height", "minWidth", "maxWidth", "minHeight", "maxHeight", "letterSpacing",
                        "columnGap", "rowGap", "horizontalOffset", "verticalOffset"})
_SHADOW_KEYS = frozenset({"horizontal", "vertical", "blur", "spread"})  # under a …Shadow (textShadow, boxShadow)
_OFFSET_KEYS = frozenset({"horizontal", "vertical"})                    # position family offset.*
_SIDE_PARENTS = frozenset({"padding", "margin"})                         # per-side lengths (legacy column spacing)
_NO_UNIT_PARENTS = frozenset({"stroke"})                                 # SVG stroke width takes a number
_FONT_STYLE_HINT = "size, color, weight, family, lineHeight, letterSpacing, headingLevel, style, …"

_VAR_MARK = "$variable("
_DECODER = json.JSONDecoder()

# Attribute values that validate against the schema but that Divi 5.13.1 renders nothing for (W5_NO_EFFECT), each
# verified live on the local Divi 5 site (research/divi5/doc-experiments.md §9). blocks: block names, or "*" for any;
# attr: the attribute path; keys: keys of its value (None = the whole value); breakpoints: the breakpoints concerned
# (None = all); when: the named page condition under which it renders nothing (None = always; _NO_EFFECT_WHEN);
# use: the path that works; why: what Divi does; doc: the note on the generated reference pages. generate_docs5.py
# reads the same table.
NO_EFFECT = (
    {"blocks": ("divi/blurb",), "attr": "imageIcon.advanced.width", "keys": None, "breakpoints": None,
     "when": "divi_skips_the_5_1_1_migration",
     "use": "imageIcon.decoration.sizing → iconFontSize (icon size) or width (image width)",
     "why": "BlurbModule.php sizes the icon and image only from imageIcon.decoration.sizing; Divi moves this "
            "attribute there only on a page whose blocks all predate 5.1.1 (ComposibleOptionsMigration)",
     "doc": "use `imageIcon.decoration.sizing` → `iconFontSize` (icon) or `width` (image)",
     "evidence": "doc-experiments.md §9: 77px/181px printed nothing; sizing 78px/182px printed"},
    {"blocks": ("divi/blurb",), "attr": "imageIcon.advanced.alignment", "keys": None, "breakpoints": None,
     "when": "divi_skips_the_5_1_1_migration",
     "use": 'imageIcon.decoration.sizing → alignSelf "flex-start" (left), "center" or "end" (right; "flex-end" '
            "prints nothing on a blurb)",
     "why": "BlurbModule.php aligns the icon and image only from imageIcon.decoration.sizing; Divi moves this "
            "attribute there only on a page whose blocks all predate 5.1.1 (ComposibleOptionsMigration)",
     "doc": 'use `imageIcon.decoration.sizing` → `alignSelf` `"flex-start"` / `"center"` / `"end"`',
     "evidence": "doc-experiments.md §9: left/right printed nothing; alignSelf flex-start/center/end printed "
                 "text-align left/center/right"},
    {"blocks": ("divi/slider", "divi/fullwidth-slider"), "attr": "module.advanced.text.text",
     "keys": ("orientation",), "breakpoints": None, "when": None,
     "use": "module.advanced.text.text → orientation on each divi/slide child",
     "why": "every slide prints its own default text-align:start with a more specific selector, which wins",
     "doc": "its `orientation` (each slide's default wins): set `orientation` on each `divi/slide`",
     "evidence": "doc-experiments.md §9: slides computed text-align start under a slider set to right"},
    {"blocks": "*", "attr": "module.decoration.sizing", "keys": ("flexType",), "breakpoints": ("tablet", "phone"),
     "when": "flex_grid_css_not_loaded",
     "use": 'the block\'s css at that breakpoint, e.g. phone {"mainElement": "width: 100%;"} (or one flexType on '
            "every breakpoint)",
     "why": "Divi loads the tablet/phone flex-grid CSS only when a non-self-closing block with an un-hyphenated "
            "name has a flexType and no desktop display block, or the page has pricing tables "
            "(DetectFeature::get_flex_grid_responsive_breakpoints); otherwise the et_flex_column_*_phone class has "
            "no rule",
     "doc": "unless the page loads Divi's flex-grid CSS (it has pricing tables, or a flex row/column that states a "
            "`flexType`): set the width with the block's `css` at that breakpoint instead",
     "evidence": "doc-experiments.md §9: a contact field and a text in a group stayed half width at 390px"},
    {"blocks": ("divi/team-member",), "attr": "module.decoration.layout", "keys": None, "breakpoints": None,
     "when": "team_member_forced_to_block",
     "use": 'css → memberImage "margin-bottom: 20px;" for the photo gap, or layout display "grid" (its rowGap '
            "works)",
     "why": "in a 1_2, 1_3, 1_4, 1_5, 1_6, 2_5, 3_4, 3_5 or 3_8 column Divi's team_member.css sets a flex "
            "team member to display:block!important",
     "doc": 'a flex layout in a 1_2, 1_3, 1_4, 1_5, 1_6, 2_5, 3_4, 3_5 or 3_8 column (forced to `display:block`): '
            'use `display` `"grid"`, or `css` → `memberImage` `"margin-bottom: 20px;"`',
     "evidence": "doc-experiments.md §9: display flex + rowGap 37px in a 1_3 column computed display block, no gap"},
)
_MIGRATION_5_1_1 = "5.1.1"
_BUILDER_VERSION_RE = re.compile(r'"builderVersion":"([^"]+)"')
# DetectFeature::get_flex_grid_responsive_breakpoints (server/FrontEnd/Assets/DetectFeature.php:1805), verbatim.
_FLEX_BLOCK_RE = re.compile(r"<!-- wp:divi/\w+\s+(\{.+?\})\s*-->", re.S)
_DESKTOP_BLOCK_LAYOUT_RE = re.compile(r'"layout":\{.*?"desktop":\{"value":\{"display"\s*:\s*"block"', re.S)
# Column widths whose class team_member.css lists in its display:block!important rules.
_TEAM_BLOCK_WIDTHS = frozenset(Fraction(*map(int, t.split("_"))) for t in
                               ("1_2", "1_3", "1_4", "1_5", "1_6", "2_5", "3_4", "3_5", "3_8"))


# ----------------------------------------------------------------------------- $variable() references

def _variable_problem(obj) -> Optional[str]:
    if not isinstance(obj, dict):
        return "its payload is not a JSON object"
    if not isinstance(obj.get("type"), str) or not obj["type"]:
        return 'it has no "type"'
    value = obj.get("value")
    if not isinstance(value, dict) or not isinstance(value.get("name"), str) or not value["name"]:
        return 'it has no "value.name"'
    return None


def scan_variables(text: str) -> Iterator[Tuple[int, int, Optional[dict], Optional[str]]]:
    """(start, end, payload, problem) for every `$variable(` in a string; problem is None for a well-formed
    reference (JSON object with a type and value.name, closed by `)$`)."""
    i = 0
    while True:
        i = text.find(_VAR_MARK, i)
        if i < 0:
            return
        j = i + len(_VAR_MARK)
        try:
            obj, end = _DECODER.raw_decode(text, j)
        except ValueError:
            yield i, j, None, "its payload is not valid JSON"
            i = j
            continue
        if not text.startswith(")$", end):
            yield i, end, None, "it is not closed with )$"
            i = end
            continue
        problem = _variable_problem(obj)
        yield i, end + 2, (None if problem else obj), problem
        i = end + 2


_MALFORMED = object()


def _whole_variable(value: str):
    """The payload when `value` is exactly one `$variable(…)$`; _MALFORMED when it is one but broken; None when it
    is not a whole-value reference."""
    if not (value.startswith(_VAR_MARK) and value.endswith(")$")):
        return None
    refs = list(scan_variables(value))
    if len(refs) == 1 and refs[0][0] == 0 and refs[0][1] == len(value):
        return refs[0][2] if refs[0][3] is None else _MALFORMED
    if refs and refs[0][3] is not None:
        return _MALFORMED
    return None


# ----------------------------------------------------------------------------- value grammar per leaf type

def _balanced(s: str) -> bool:
    depth = 0
    for c in s:
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _is_number(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    return isinstance(value, str) and bool(_NUMBER.fullmatch(value))


def _color_ok(value) -> bool:
    if not isinstance(value, str):
        return False
    if value == "" or value.lower() == "transparent" or _HEX.fullmatch(value):
        return True
    if _COLOR_FUNC.fullmatch(value) or _VAR_FUNC.fullmatch(value):
        return _balanced(value)
    return False


def _length_problem(value, units=None) -> Optional[str]:
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        return "expected a CSS length string such as 10px"
    if not isinstance(value, str):
        return None  # a unitless number, as Divi 4 accepts (Divi 5 writes it into the CSS verbatim)
    if value == "" or value.lower() in _LENGTH_KEYWORDS:
        return None
    if _LENGTH_FUNC.fullmatch(value):
        return None if _balanced(value) else "unbalanced parentheses"
    m = _NUM_UNIT.fullmatch(value)
    if not m:
        return "not a number with a CSS unit"
    unit = m.group(2).lower()
    if unit == "":
        return None  # unitless (line-height 1.5, a 0), as Divi 4's _length_ok accepts whatever the units
    allowed = [u.lower() for u in units] if units else _GENERIC_UNITS
    if unit not in allowed:
        return f"unit '{m.group(2)}' is not one of {', '.join(units) if units else 'the CSS length units'}"
    return None


def _font_weight_ok(value) -> bool:
    """1..1000 (Divi writes a numeric weight into the CSS verbatim; off the hundreds is W_FONT_WEIGHT), a CSS weight
    keyword, "variable" (Divi 5.13 variable-font mode, Font.php:360) or a global-font "<Font>_weight" token."""
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return 1 <= value <= 1000
    if not isinstance(value, str):
        return False
    if value.isdigit():
        return _font_weight_ok(int(value))
    return value in _FONT_WEIGHT_WORDS or value == "variable" or (value.endswith("_weight")
                                                                  and len(value) > len("_weight"))


def _off_hundreds(value) -> bool:
    """A valid numeric weight that is not 100, 200 … 900 (Divi 4's W_FONT_WEIGHT)."""
    n = value if isinstance(value, int) and not isinstance(value, bool) else \
        int(value) if isinstance(value, str) and value.isdigit() else None
    return n is not None and 1 <= n <= 1000 and not (n % 100 == 0 and n <= 900)


def _url_ok(value) -> bool:
    return isinstance(value, str) and not re.search(r"\s", value)


def _onoff_ok(value) -> bool:
    return value in ("on", "off", "")


def _spacing_problems(value) -> List[str]:
    if not isinstance(value, dict):
        return ["expected an object {top, right, bottom, left, syncVertical, syncHorizontal}"]
    out = []
    for k, v in value.items():
        if k in _SPACING_SIDES:
            p = _length_problem_or_var(v)
            if p:
                out.append(f"{k}: {p}")
        elif k in _SPACING_SYNC:
            if not _onoff_ok(v):
                out.append(f"{k} must be on or off")
        else:
            out.append(f"'{k}' is not a spacing key (top, right, bottom, left, syncVertical, syncHorizontal)")
    return out


def _radius_problems(value) -> List[str]:
    if isinstance(value, str):
        p = _length_problem(value)
        return [p] if p else []
    if not isinstance(value, dict):
        return ["expected an object {topLeft, topRight, bottomRight, bottomLeft, sync} or a length"]
    out = []
    for k, v in value.items():
        if k in _RADIUS_CORNERS:
            p = _length_problem_or_var(v)
            if p:
                out.append(f"{k}: {p}")
        elif k == "sync":
            if not _onoff_ok(v):
                out.append("sync must be on or off")
        else:
            out.append(f"'{k}' is not a radius key (topLeft, topRight, bottomRight, bottomLeft, sync)")
    return out


def _length_problem_or_var(v) -> Optional[str]:
    if isinstance(v, str) and _VAR_MARK in v:
        whole = _whole_variable(v)
        if whole is _MALFORMED or (whole is not None and whole.get("type") == "content"):
            return None
    return _length_problem(v)


def _icon_problems(value) -> List[str]:
    if not isinstance(value, dict):
        return ['expected an icon object {"unicode": "&#xf0a9;", "type": "fa", "weight": "900"}']
    out = [f"'{k}' is not an icon key (unicode, type, weight)" for k in value if k not in ("unicode", "type", "weight")]
    missing = [k for k in ("unicode", "type", "weight") if k not in value]
    if missing:
        out.append(f"missing {', '.join(missing)}")
    if "unicode" in value and (not isinstance(value["unicode"], str) or not value["unicode"]):
        out.append("unicode must be the icon's character entity, e.g. &#xf0a9;")
    if "type" in value and value["type"] not in _ICON_TYPES:
        out.append("type must be divi or fa")
    if "weight" in value and not (_is_number(value["weight"]) or value["weight"] in _FONT_WEIGHT_WORDS):
        out.append("weight must be a number such as 400 or 900")
    return out


def _gradient_problems(value) -> List[str]:
    if not isinstance(value, list):
        return ['expected a list of stops [{"position": 0, "color": "#fff"}, …]']
    out = []
    for i, stop in enumerate(value):
        if not isinstance(stop, dict):
            out.append(f"stop {i} is not an object {{position, color}}")
            continue
        if "position" not in stop or "color" not in stop:
            out.append(f"stop {i} needs position and color")
            continue
        pos = stop["position"]
        if not (_is_number(pos) or (isinstance(pos, str) and _NUM_UNIT.fullmatch(pos))):
            out.append(f"stop {i} position {pos!r} is not a number")  # a unit is E5_GRADIENT_STOP_POSITION
        color = stop["color"]
        if not _color_value_ok(color):
            out.append(f"stop {i} color {color!r} is not a color")
    return out


def _unit_positions(value) -> List[str]:
    """Stop positions written with a unit ("0%", "10px"): Divi renders no gradient at all (doc-experiments.md §8)."""
    return [stop["position"] for stop in (value if isinstance(value, list) else ())
            if isinstance(stop, dict) and isinstance(stop.get("position"), str)
            and _NUM_UNIT.fullmatch(stop["position"]) and _NUM_UNIT.fullmatch(stop["position"]).group(2)]


def _unitless_nonzero(value) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return value != 0
    return isinstance(value, str) and bool(_NUMBER.fullmatch(value)) and float(value) != 0


def _needs_unit(path: str) -> bool:
    parts = path.split(".")
    key, parent = parts[-1], (parts[-2] if len(parts) > 1 else "")
    if parent in _NO_UNIT_PARENTS:
        return False
    if key in _UNIT_KEYS or (key == "size" and parent == "font"):
        return True
    if key in _SHADOW_KEYS and any(p.endswith("Shadow") for p in parts[:-1]):
        return True
    if key in _OFFSET_KEYS and parent == "offset":
        return True
    return key in _SPACING_SIDES and parent in _SIDE_PARENTS


def unitless_lengths5(path: str, leaf: dict, value) -> List[Tuple[str, object]]:
    """(path, value) for every non-zero unitless number (JSON number or numeric string) in a length, spacing or
    radius leaf value where CSS requires a unit (E5_UNITLESS_LENGTH). 0 is fine; so is a leaf whose `units` list
    includes "" (unitless allowed there)."""
    if "" in (leaf.get("units") or ()):
        return []
    t = leaf.get("type")
    if t == "length":
        return [(path, value)] if _needs_unit(path) and _unitless_nonzero(value) else []
    if t in ("spacing", "radius") and isinstance(value, dict):
        keys = _SPACING_SIDES if t == "spacing" else _RADIUS_CORNERS
        return [(f"{path}.{k}", v) for k, v in value.items() if k in keys and _unitless_nonzero(v)]
    if t == "radius":
        return [(path, value)] if _unitless_nonzero(value) else []
    return []


def _color_value_ok(value) -> bool:
    if isinstance(value, str) and value.startswith(_VAR_MARK):
        whole = _whole_variable(value)
        if whole is _MALFORMED or (whole is not None and whole.get("type") == "color"):
            return True
    return _color_ok(value)


_EXPECT = {
    "color": "a color (#hex, rgb()/rgba()/hsl()/hsla(), transparent, or a $variable color reference)",
    "number": "a number",
    "onoff": "on or off",
    "url": "a URL string without spaces",
    "image": "an image URL string without spaces",
    "text": "a string",
    "html": "an HTML string",
    "font-family": "a font family name string",
    "font-weight": "a font weight (1-1000, normal, bold, lighter, bolder, variable or a <Font>_weight token)",
    "object": "a JSON object",
}


def _show(value) -> str:
    return value if isinstance(value, str) else json.dumps(value)


def value_problems5(leaf_spec: dict, value) -> List[str]:
    """Messages for one leaf value against its leaf spec ({type, options?, units?, multiple?}); [] when it fits.
    "" is an unset value and fits every type. A whole-value `$variable(…)$` fits when its type suits the leaf
    (color for color, gradient for gradient, content for lengths, numbers, text, URLs, images and fonts); a
    malformed one is left to check_attributes5's E5_BAD_VARIABLE."""
    t = leaf_spec.get("type")
    if t == "json" or value == "":
        return []
    if isinstance(value, str) and value.startswith(_VAR_MARK):
        whole = _whole_variable(value)
        if whole is _MALFORMED:
            return []
        if whole is not None:
            if whole["type"] in _VARIABLE_TYPES.get(t, ()):
                return []
            return [f"a $variable of type '{whole['type']}' cannot be a {t} value"]
    if t == "color":
        ok = _color_ok(value)
    elif t == "length":
        p = _length_problem(value, leaf_spec.get("units"))
        return [f"'{_show(value)}' is not a CSS length: {p}"] if p else []
    elif t == "number":
        ok = _is_number(value)
    elif t == "enum":
        options = leaf_spec.get("options") or []
        vals = value if isinstance(value, list) and leaf_spec.get("multiple") else [value]
        bad = [v for v in vals if not isinstance(v, str) or v not in options]
        if bad:
            return [f"'{_show(v)}' is not one of {', '.join(options)}" for v in bad]
        return []
    elif t == "onoff":
        ok = _onoff_ok(value)
    elif t in ("url", "image"):
        ok = _url_ok(value)
    elif t in ("text", "html", "font-family"):
        ok = isinstance(value, str)
    elif t == "font-weight":
        ok = _font_weight_ok(value)
    elif t == "icon":
        return _icon_problems(value)
    elif t == "spacing":
        return _spacing_problems(value)
    elif t == "radius":
        return _radius_problems(value)
    elif t == "gradient":
        return _gradient_problems(value)
    elif t == "object":
        ok = isinstance(value, (dict, list))
    else:
        return []
    return [] if ok else [f"'{_show(value)}' is not {_EXPECT.get(t, 'a ' + str(t))}"]


# ----------------------------------------------------------------------------- walking a block's attributes

def _responsive_like(d: dict) -> bool:
    """A {breakpoint: {state: value}} dict, including ones with a breakpoint or state Divi doesn't have (those are
    reported by the resolver as bad_breakpoint / bad_state)."""
    return bool(d) and all(isinstance(v, dict) and v and (k in _KNOWN_BP or all(s in _STATE_SET for s in v))
                           for k, v in d.items())


def _leaves(attrs, prefix: str = "") -> Iterator[Tuple[str, Optional[str], Optional[str], object]]:
    """divi5_blocks.iter_leaves, but a breakpoint or state that isn't Divi's is yielded (to be reported) instead of
    being read as part of the attribute path."""
    if not isinstance(attrs, dict):
        return
    for k, v in attrs.items():
        path = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            if _responsive_like(v):
                for bp, states in v.items():
                    for st, val in states.items():
                        yield path, bp, st, val
            else:
                yield from _leaves(v, path)
        else:
            yield path, None, None, v


def _strings(value) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)


def noncanonical_reasons(raw: str) -> List[str]:
    """What in a block's raw attribute JSON differs from WordPress's serialize_block_attributes() output in a way
    that matters: a raw <, >, & or -- (written \\u003c, \\u003e, \\u0026, \\u002d\\u002d) and the \\" quote form
    (written \\u0022). A `\\\\` backslash escape (the Visual Builder's form) is harmless and not reported."""
    found: List[str] = []
    in_str, i = False, 0
    while i < len(raw):
        c = raw[i]
        if in_str and c == "\\":
            if raw[i + 1:i + 2] == '"' and '\\"' not in found:
                found.append('\\"')
            i += 2
            continue
        if c == '"':
            in_str = not in_str
        elif c in "<>&" and c not in found:
            found.append(c)
        elif c == "-" and raw[i + 1:i + 2] == "-" and "--" not in found:
            found.append("--")
        i += 1
    return found


def _alt_text(block: Block) -> str:
    inner = get_attr(block, "image.innerContent")
    alt = inner.get("alt") if isinstance(inner, dict) else None
    if isinstance(alt, str) and alt.strip():
        return alt
    items = get_attr(block, "module.decoration.attributes")
    items = items.get("attributes") if isinstance(items, dict) else None
    for item in items if isinstance(items, list) else ():
        if isinstance(item, dict) and item.get("name") == "alt" and item.get("targetElement", "image") == "image" \
                and isinstance(item.get("value"), str) and item["value"].strip():
            return item["value"]
    return ""


def _preset_ids(attrs: dict) -> List[Tuple[str, str]]:
    """(label, id) for every preset reference: modulePreset entries and groupPreset presetIds."""
    out: List[Tuple[str, str]] = []
    mp = attrs.get("modulePreset")
    for pid in ([mp] if isinstance(mp, str) else mp if isinstance(mp, list) else []):
        if isinstance(pid, str):
            out.append(("modulePreset", pid))
    gp = attrs.get("groupPreset")
    for group, spec in (gp.items() if isinstance(gp, dict) else ()):
        ids = spec.get("presetId") if isinstance(spec, dict) else None
        for pid in ([ids] if isinstance(ids, str) else ids if isinstance(ids, list) else []):
            if isinstance(pid, str):
                out.append((f"groupPreset {group}", pid))
    return out


def _close_match(name: str, candidates) -> str:
    close = difflib.get_close_matches(name, list(candidates), n=1, cutoff=0.75)
    return f"did you mean '{close[0]}'?" if close else ""


def check_attributes5(doc, schema5, report, known_presets=frozenset(), known_vars: Optional[frozenset] = None,
                      site_host: Optional[str] = None, site_version: Optional[str] = None) -> None:
    """Attribute paths, breakpoints/states, value types, escaping, presets and variables of every Divi block.
    known_vars=None means no tokens were given: unknown gcid-/gvid- ids are then not reported."""
    page = _Page(doc)
    for block, path, _parent in doc.walk():
        if block.raw_json:
            reasons = noncanonical_reasons(block.raw_json)
            if reasons:
                report("error", "E5_NONCANONICAL",
                       f"[{block.name}] attribute JSON is not in WordPress canonical form: it contains raw "
                       + ", ".join(f"'{r}'" for r in reasons), node=block, path=path, value=" ".join(reasons),
                       hint="re-render the block in WordPress canonical form with divi5_blocks.render_block() (or "
                            "canonical_json() for its attributes); no script rewrites it for you (publish stores "
                            "the JSON as given, page_edit re-renders only a block it edits): "
                            "< > & -- and \" inside strings are \\u003c \\u003e \\u0026 \\u002d\\u002d \\u0022")
        if block.name == PLACEHOLDER or not block.name.startswith("divi/") or not isinstance(block.attrs, dict):
            continue
        mod = schema5.module(block.name)
        if mod is None:
            continue
        _check_block(block, path, mod, schema5, report, known_presets, known_vars, site_host, site_version, page)


_BUILDER_VERSION_HINT = ("Blocks you create: set builderVersion to the site's Divi version. Don't change builderVersion "
                         "on existing blocks you edit — Divi's render-time migrations depend on it.")


def _check_block(block, path, mod, schema5, report, known_presets, known_vars, site_host, site_version,
                 page=None) -> None:
    attrs = block.attrs
    version = attrs.get("builderVersion")
    if not isinstance(version, str) or not version:
        report("warning", "W5_BUILDER_VERSION", f"[{block.name}] has no builderVersion", node=block, path=path,
               attr="builderVersion", hint=_BUILDER_VERSION_HINT + (f" (site: {site_version})" if site_version else ""))
    elif site_version and version != site_version:
        report("warning", "W5_BUILDER_VERSION", f"[{block.name}] builderVersion {version} is not the site's Divi "
                                                f"{site_version}", node=block, path=path, attr="builderVersion",
               value=version, hint=_BUILDER_VERSION_HINT)
    for label, pid in _preset_ids(attrs):
        if pid != "default" and pid not in known_presets:
            report("warning", "W5_UNKNOWN_PRESET",
                   f"{label} id '{pid}' is not a preset known on this site: an unknown preset id makes Divi drop the "
                   "module's default preset styling; omit modulePreset or use [\"default\"]",
                   node=block, path=path, attr=label.split(" ")[0], value=pid,
                   hint="Use a preset id listed in tokens.json.")
    if block.name in IMAGE_MODULES and not _alt_text(block):
        report("warning", "W5_NO_ALT", f"[{block.name}] has no alt text", node=block, path=path,
               attr="image.innerContent.alt",
               hint='Set image.innerContent desktop value "alt" to a short description of the image.')

    seen: Dict[str, Set[Tuple[str, str]]] = defaultdict(set)
    unknown: Set[str] = set()
    warned_bp: Set[Tuple[str, str]] = set()
    warned_legacy: Set[str] = set()
    no_effect: Dict[Tuple[int, str], Set[str]] = defaultdict(set)
    for attr, bp, st, value in _leaves(attrs):
        rep = _scoped(report, bp, st)
        for s in _strings(value):
            _check_variables(s, block, path, attr, rep, known_vars)
        if bp is None:
            res = mod.resolve(attr, None, None)
            if res.status == "nonresponsive":
                continue
            if res.status == "unknown_attr":
                if attr not in unknown:
                    unknown.add(attr)
                    _unknown(block, path, attr, value, mod.attrs, rep)
            else:
                rep("error", "E5_BAD_BREAKPOINT", f"{attr} is not wrapped in a breakpoint and state",
                       node=block, path=path, attr=attr, value=_show(value),
                       hint='Divi 5 values are stored as {"desktop":{"value":…}}.')
            continue
        seen[attr].add((bp, st))
        _no_effect_hits(block.name, attr, bp, value, no_effect)
        if attr in mod.legacy and attr not in warned_legacy:
            warned_legacy.add(attr)
            _legacy(block, path, attr, report)
        _check_whole_value(block, path, mod, schema5, attr, bp, st, value, rep)
        if bp in DISABLED_BREAKPOINTS and (attr, bp) not in warned_bp:
            warned_bp.add((attr, bp))
            rep("warning", "W5_BREAKPOINT_DISABLED",
                   f"{attr} sets the {bp} breakpoint, which Divi 5 ships switched off", node=block, path=path,
                   attr=attr, value=bp, hint="Its values apply only once the site enables that breakpoint "
                                             "(Divi > Theme Options > Breakpoints); use desktop/tablet/phone.")
        for res, v in mod.walk_value(attr, bp, st, value):
            full = (res.attr_path or attr) + (f".{res.sub_path}" if res.sub_path else "")
            if res.status == "unknown_attr":
                if full in unknown:
                    continue
                unknown.add(full)
                if res.attr_path is None:
                    _unknown(block, path, attr, value, mod.attrs, rep)
                else:
                    table = schema5.leaf_spec(mod.attrs[res.attr_path]) if res.attr_path in mod.attrs else {}
                    _unknown(block, path, full, v, [f"{res.attr_path}.{k}" for k in table if k], rep)
            elif res.status == "bad_breakpoint":
                rep("error", "E5_BAD_BREAKPOINT", f"'{bp}' is not a Divi breakpoint ({full})", node=block,
                       path=path, attr=full, value=bp,
                       hint="Breakpoints are desktop, tablet, phone (and phoneWide, tabletWide, widescreen, "
                            "ultraWide when enabled).")
            elif res.status == "bad_state":
                allowed = ", ".join(res.leaf["states"]) if res.leaf else "value"
                rep("error", "E5_BAD_STATE", f"State '{st}' is not allowed on {full} (allowed: {allowed})",
                       node=block, path=path, attr=full, value=st)
            else:
                _check_leaf(block, path, full, bp, res.leaf, v, rep, site_host)
    _report_no_effect(block, path, no_effect, page or _Page(None), schema5, report)
    for attr, pairs in seen.items():
        if attr in unknown or ("desktop", "value") in pairs or attr.endswith("disabledOn"):
            continue
        extra = sorted(f"{bp}.{st}" for bp, st in pairs
                       if st in ("hover", "sticky") or (bp in BREAKPOINTS and bp != "desktop"))
        if extra:
            report("warning", "W5_HOVER_WITHOUT_DESKTOP",
                   f"{attr} sets {', '.join(extra)} but no desktop.value", node=block, path=path, attr=attr,
                   value=",".join(extra), hint="Set the desktop value too; the other breakpoints and states vary it.")


def _no_effect_hits(name, attr, bp, value, hits) -> None:
    """Record (NO_EFFECT index, reported path) -> breakpoints for one attribute value of a block."""
    for i, entry in enumerate(NO_EFFECT):
        if entry["attr"] != attr or (entry["blocks"] != "*" and name not in entry["blocks"]):
            continue
        if entry["breakpoints"] is not None and bp not in entry["breakpoints"]:
            continue
        if entry["keys"] is None:
            hits[(i, attr)].add(bp)
        elif isinstance(value, dict):
            for k in entry["keys"]:
                if k in value:
                    hits[(i, f"{attr}.{k}")].add(bp)


def _report_no_effect(block, path, hits, page, schema5, report) -> None:
    version = schema5.meta.get("divi_version", "5")
    for (i, where), bps in sorted(hits.items()):
        entry = NO_EFFECT[i]
        if entry["when"]:
            bps = _NO_EFFECT_WHEN[entry["when"]](page, block, bps)
        if not bps:
            continue
        report("warning", "W5_NO_EFFECT", f"[{block.name}] {where} renders nothing on Divi {version}: {entry['why']}",
               node=block, path=path, attr=where, value=",".join(sorted(bps)), hint=f"Use {entry['use']}.")


def version_key(version: str) -> Tuple[Tuple[int, ...], int]:
    """A sortable key for a Divi version: 5.0.0-public-beta.1 < 5.0.0 < 5.1.1 (a pre-release sorts before its
    release, as PHP's version_compare has it)."""
    m = re.match(r"(\d+(?:\.\d+)*)(.*)", version or "")
    if not m:
        return (0,), 0
    nums = tuple(int(n) for n in m.group(1).split("."))
    nums += (0,) * (4 - len(nums))
    return nums, 0 if m.group(2) else 1


def flex_grid_breakpoints(source: str) -> Set[str]:
    """The breakpoints whose flex-grid column CSS (et_flex_column_*_tablet/_phone) Divi 5.13.1 loads for this
    content: DetectFeature::get_flex_grid_responsive_breakpoints, ported regex for regex. Its block regex skips
    self-closing blocks and hyphenated names, so a leaf module's own flexType never loads it."""
    has_pricing = "wp:divi/pricing-tables" in source
    if '"flexType"' not in source and not has_pricing:
        return set()
    valid = any('"flexType"' in j and not _DESKTOP_BLOCK_LAYOUT_RE.search(j) for j in _FLEX_BLOCK_RE.findall(source))
    if not valid and not has_pricing:
        return set()
    out = set()
    for bp in ("tablet", "phone"):
        if (bp == "phone" and has_pricing) \
                or re.search(r'"flexType":\{.*?"%s":\{"value":' % bp, source, re.S) \
                or re.search(r'"%s":\{"value":\{.*?"flexType":' % bp, source, re.S):
            out.add(bp)
    return out


def _fraction(value) -> Optional[Fraction]:
    m = re.fullmatch(r"(\d+)_(\d+)", value) if isinstance(value, str) else None
    return Fraction(int(m.group(1)), int(m.group(2))) if m and int(m.group(2)) else None


class _Page:
    """Page-level facts the W5_NO_EFFECT conditions need, computed on first use."""

    def __init__(self, doc):
        self.source = doc.source if doc is not None else ""
        self.parents = {id(b): p for b, _path, p in doc.walk()} if doc is not None else {}
        self._cache: Dict[str, object] = {}

    def _once(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    def migrates_5_1_1(self) -> bool:
        """MigrationUtils::content_needs_migration: Divi migrates a page only if no builderVersion on it is 5.1.1
        or newer (blocks without one count as 0.0.0)."""
        return self._once("migrates", lambda: not any(
            version_key(v) >= version_key(_MIGRATION_5_1_1) for v in _BUILDER_VERSION_RE.findall(self.source)))

    def flex_grid(self) -> Set[str]:
        return self._once("flex_grid", lambda: flex_grid_breakpoints(self.source))

    def column_width(self, block) -> Optional[Fraction]:
        """The rendered width of the nearest layout-form column around a block (an inner column's width scaled by
        its specialty column's, as Divi's et_pb_column_3_8 class has it); None outside such a column."""
        parent = self.parents.get(id(block))
        while parent is not None and parent.name not in ("divi/column", "divi/column-inner"):
            parent = self.parents.get(id(parent))
        if parent is None or _desktop_key(parent, "module.decoration.layout", "display") != "block":
            return None
        width = _fraction(get_attr(parent, "module.advanced.type"))
        if width is not None and parent.name == "divi/column-inner":
            outer = self.parents.get(id(parent))
            while outer is not None and outer.name != "divi/column":
                outer = self.parents.get(id(outer))
            outer_width = _fraction(get_attr(outer, "module.advanced.type")) if outer is not None else None
            width = width * outer_width if outer_width is not None else width
        return width


def _desktop_key(block, attr: str, key: str):
    value = get_attr(block, attr)
    return value.get(key) if isinstance(value, dict) else None


def _team_member_forced_to_block(page: _Page, block, bps: Set[str]) -> Set[str]:
    """Divi decides flex or grid from the desktop display (Module.php); a flex team member in a narrow column is
    display:block!important on every breakpoint."""
    display = _desktop_key(block, "module.decoration.layout", "display") or "flex"
    return bps if display == "flex" and page.column_width(block) in _TEAM_BLOCK_WIDTHS else set()


# when -> fn(page, block, breakpoints found) -> the breakpoints at which the value renders nothing.
_NO_EFFECT_WHEN = {
    "divi_skips_the_5_1_1_migration": lambda page, block, bps: set() if page.migrates_5_1_1() else bps,
    "flex_grid_css_not_loaded": lambda page, block, bps: bps - page.flex_grid(),
    "team_member_forced_to_block": _team_member_forced_to_block,
}


def _legacy(block, path, attr, report) -> None:
    if is_legacy_column_attr(attr):
        hint = ("Style each column on its own divi/column block (its module.decoration.* attributes and css) instead "
                "of the parent's per-column attributes.")
    else:
        hint = (f"Use the block's own Divi 5 attributes instead (reference/divi5/modules/{block.name[5:]}.md lists "
                "them; this one is in its Legacy table).")
    report("warning", "W5_LEGACY_ATTR", f"[{block.name}] {attr} exists only for Divi 4 conversion: no Divi 5 module "
                                        "code reads it", node=block, path=path, attr=attr, hint=hint)


def _check_whole_value(block, path, mod, schema5, attr, bp, st, value, report) -> None:
    """Checks that need a whole attribute value (one breakpoint/state) rather than one leaf of it."""
    if not isinstance(value, dict) or not value:
        return
    spec = mod.attrs.get(attr) or {}
    if spec.get("family") == "font" and not spec.get("prefix"):
        report("warning", "W5_BARE_FONT",
               f"{attr} sets {', '.join(sorted(value))} directly on the font container: Divi styles text only from "
               f"{attr}.font, .textShadow and .textEffects, so these render nothing", node=block, path=path,
               attr=attr, value=_show(value)[:200],
               hint=f"Move them to {attr}.font ({_FONT_STYLE_HINT} all go there).")
    gradient = value.get("gradient")
    if isinstance(gradient, dict) and "enabled" not in gradient and gradient.keys() & {"stops", "type", "direction"} \
            and "gradient.enabled" in schema5.leaf_spec(spec) and not _inherits_enabled(block, attr, bp, st):
        message = f"{attr}.gradient has stops/type/direction but no \"enabled\": \"on\": Divi renders no gradient"
        if _preset_may_style_background(block.attrs):
            report("warning", "W5_GRADIENT_MAYBE_DISABLED", message + " unless its preset enables the gradient",
                   node=block, path=path, attr=f"{attr}.gradient", value=_show(gradient)[:200],
                   hint='Add "enabled": "on" to the gradient object unless the preset already enables it.')
        else:
            report("error", "E5_GRADIENT_DISABLED", message, node=block, path=path, attr=f"{attr}.gradient",
                   value=_show(gradient)[:200], hint='Add "enabled": "on" to the gradient object.')


def _inherits_enabled(block, attr, bp, st) -> bool:
    """Whether a value without gradient.enabled inherits one: Divi's cascade is the breakpoint's own `value` (for
    hover/sticky), then tablet.value (for phone), then desktop.value; the first gradient carrying the key wins."""
    chain = ([(bp, "value")] if st != "value" else []) + ([("tablet", "value")] if bp == "phone" else []) \
        + [("desktop", "value")]
    for cbp, cst in chain:
        if (cbp, cst) == (bp, st):
            continue
        base = get_attr(block, attr, cbp, cst)
        inherited = base.get("gradient") if isinstance(base, dict) else None
        if isinstance(inherited, dict) and "enabled" in inherited:
            return True
    return False


def _preset_may_style_background(attrs: dict) -> bool:
    """A non-default modulePreset, or a background/button group preset, may supply gradient.enabled."""
    for label, pid in _preset_ids(attrs):
        if pid == "default":
            continue
        if label == "modulePreset":
            return True
        group = label.split(" ", 1)[1]
        spec = (attrs.get("groupPreset") or {}).get(group)
        name = spec.get("groupName") if isinstance(spec, dict) else None
        if name in ("divi/background", "divi/button") or "background" in group.lower():
            return True
    return False


def _scoped(report, bp, st):
    """report, but every finding's attr gets ':<breakpoint>:<state>' appended (the baseline key of a block finding:
    dotted path + ':' + breakpoint + ':' + state). Non-responsive values keep the bare path."""
    if bp is None:
        return report

    def scoped(level, code, message, node=None, path="", offset=None, attr="", value="", hint=""):
        report(level, code, message, node=node, path=path, offset=offset,
               attr=f"{attr}:{bp}:{st}" if attr else attr, value=value, hint=hint)
    return scoped


def _unknown(block, path, attr, value, candidates, report) -> None:
    report("error", "E5_UNKNOWN_ATTR", f"[{block.name}] has no attribute '{attr}'", node=block, path=path, attr=attr,
           value=_show(value)[:200], hint=_close_match(attr, candidates) or
           f"See reference/divi5/modules/{block.name[5:]}.md for its attributes.")


def _check_leaf(block, path, full, bp, leaf, value, report, site_host) -> None:
    if not leaf.get("bp", True) and bp != "desktop" and bp not in leaf.get("breakpoints_extra", ()):
        report("error", "E5_BAD_BREAKPOINT", f"{full} is not responsive: it only takes a desktop value, not {bp}",
               node=block, path=path, attr=full, value=bp, hint="Move the value to desktop.")
        return
    for msg in value_problems5(leaf, value):
        report("error", "E5_BAD_VALUE", f"{full}: {msg}", node=block, path=path, attr=full, value=_show(value)[:200])
    for where, v in unitless_lengths5(full, leaf, value):
        report("error", "E5_UNITLESS_LENGTH",
               f"{where}: {_show(v)} has no unit: Divi writes it into the CSS as is and the browser ignores it",
               node=block, path=path, attr=where, value=_show(v), hint=f"add a unit, e.g. {_show(v)}px")
    t = leaf.get("type")
    if t == "gradient":
        bad = _unit_positions(value)
        if bad:
            report("error", "E5_GRADIENT_STOP_POSITION",
                   f"{full}: stop position {', '.join(_show(b) for b in bad)} has a unit: Divi renders no gradient",
                   node=block, path=path, attr=full, value=", ".join(_show(b) for b in bad),
                   hint='Write positions as plain numbers (percent of the gradient length): 0, 100 or "0", "100".')
    if t == "font-weight" and _off_hundreds(value):
        report("warning", "W_FONT_WEIGHT", f"{full}: font weight '{value}' is not 100–900 in steps of 100",
               node=block, path=path, attr=full, value=str(value),
               hint="Use 100…900; fonts rarely ship other static weights.")
    if t == "image" and site_host and isinstance(value, str) and _VAR_MARK not in value:
        host = urlparse(value).hostname
        if host and host.lower() != site_host.lower():
            report("warning", "W_EXTERNAL_IMAGE", f"{full} points to {host}, not the site", node=block, path=path,
                   attr=full, value=value, hint="Upload the image to the site's Media Library and use that URL.")
    if t in ("html", "text") and ".innerContent" in f".{full}" and isinstance(value, str) \
            and _SHORTCODE_OPEN.search(value):
        report("warning", "W5_SHORTCODE_BRACKETS",
               f"{full} contains '[' followed by a letter, which WordPress runs as a shortcode", node=block, path=path,
               attr=full, value=value[:200], hint="Write literal brackets as &#91; and &#93;.")


def _check_variables(text: str, block, path, attr, report, known_vars) -> None:
    if _VAR_MARK not in text:
        return
    for start, end, obj, problem in scan_variables(text):
        if problem:
            report("error", "E5_BAD_VARIABLE", f"{attr}: malformed $variable reference: {problem}", node=block,
                   path=path, attr=attr, value=text[start:end + 40][:200],
                   hint='Write $variable({"type":"color","value":{"name":"gcid-…","settings":{}}})$ '
                        '(type content for gvid- design variables).')
            continue
        name = obj["value"]["name"]
        if known_vars is not None and name.startswith(("gcid-", "gvid-")) and name not in known_vars \
                and name not in CUSTOMIZER_COLOR_IDS:
            report("warning", "W5_UNKNOWN_VARIABLE", f"{attr} references {name}, which is not in tokens.json",
                   node=block, path=path, attr=attr, value=name,
                   hint="An unknown global color or variable renders as nothing; use an id from tokens.json or an "
                        "inline value.")
