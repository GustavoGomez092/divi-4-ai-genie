"""Read a Divi 5 site's design data from a public page's HTML/CSS: global colors, the Customizer, design variables,
preset CSS and the Divi version (research/divi5/tokens-and-detection.md §3).

Divi 5 prints its design system as CSS custom properties in `:root` blocks:
- `--gcid-*`: the five Customizer colors always, user global colors only when the page uses them (or all of them when
  Dynamic Assets is off). A derived color prints as `hsl(from var(--gcid-base) calc(h + …) …)`; it is resolved here.
- `--gvid-*`: the number/font/image/gradient design variables the page uses, or *all active ones* on a page that uses
  none. String and link variables are resolved inline and never appear.
- `--et_global_*`: the Customizer heading/body fonts, weights, body size and line height.
Preset CSS is emitted under its own class (`.preset--module--<module>--<id>`,
`.preset--group--<module>--<group>--<hash>--<id>`), so a preset's rendered declarations are recoverable from any page
that uses it. A module type's default preset renders as `…--default` and its real id never appears.

With static CSS files or a cache plugin that CSS moves into same-origin `/et-cache/` stylesheets: `stylesheet_links`
names them, the caller fetches them and passes their text as `css_by_url` (this module does no network I/O).
"""
from __future__ import annotations

import colorsys
import re
from collections import Counter
from typing import Dict, Iterator, List, Optional, Tuple
from urllib.parse import parse_qs, unquote, urljoin, urlsplit

from divi_format import _ASSET_VER, GENERATOR_RE

COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)
DOC_CSS_RE = re.compile(r"<style[^>]*>(.*?)</style>|<link\b[^>]*>", re.S | re.I)
HREF_RE = re.compile(r"""href=["']([^"']+)["']""")
PRESET_CLASS_RE = re.compile(r"\.preset--(module|group)--([A-Za-z0-9_-]+)")
HSL_FROM_RE = re.compile(
    r"^hsl\(\s*from\s+var\(--(gcid-[\w-]+)\)\s+calc\(h\s*([+-])\s*([\d.]+)\)\s+"
    r"(?:max\(\s*0\s*,\s*calc\(s\s*([+-])\s*([\d.]+)\)\s*\)|calc\(s\s*([+-])\s*([\d.]+)\))\s+"
    r"calc\(l\s*([+-])\s*([\d.]+)\)\s*(?:/\s*([\d.]+%?))?\s*\)$")
VAR_ALIAS_RE = re.compile(r"^var\(--(gcid-[\w-]+)\)$")
URL_RE = re.compile(r"""^url\(\s*(["']?)(.*?)\1\s*\)$""", re.I | re.S)
# Customizer role -> (global color id, Divi's default value).
CUSTOMIZER = {"primary": ("gcid-primary-color", "#2ea3f2"), "secondary": ("gcid-secondary-color", "#2ea3f2"),
              "heading": ("gcid-heading-color", "#666666"), "body": ("gcid-body-color", "#666666"),
              "link": ("gcid-link-color", "#2ea3f2")}
ICON_FONTS = frozenset({"etmodules", "fontawesome", "font awesome 5 free", "font awesome 5 brands"})  # not brand fonts
CUSTOMIZER_IDS = {cid: role for role, (cid, _default) in CUSTOMIZER.items()}


def _walk_css(css: str, media: Optional[str] = None) -> Iterator[Tuple[Optional[str], str, str]]:
    """(media, selector, body) of every style rule, descending into @media/@supports blocks; other at-rules
    (@font-face, @keyframes, @import, …) are skipped. A brace-depth scan: CSS nests blocks a flat regex can't split."""
    i, n = 0, len(css)
    while i < n:
        j = i
        while j < n and css[j] not in "{};":
            j += 1
        if j >= n:
            return
        prelude = css[i:j].strip()
        if css[j] == ";" or css[j] == "}":
            i = j + 1  # a statement at-rule (@import …;) or a stray token
            continue
        depth, k = 1, j + 1
        while k < n and depth:
            depth += {"{": 1, "}": -1}.get(css[k], 0)
            k += 1
        body = css[j + 1:k - 1] if depth == 0 else css[j + 1:]  # an unterminated block runs to EOF
        if prelude.startswith("@"):
            name = prelude.split(None, 1)[0].lower()
            if name in ("@media", "@supports"):
                cond = prelude[len(name):].strip()
                yield from _walk_css(body, cond if name == "@media" else media)
        elif prelude:
            yield media, prelude, body
        i = k


def _split_decls(body: str) -> Iterator[str]:
    """The `;`-separated declarations of a rule body; a `;` inside quotes or parentheses (`url(data:…;base64,…)`)
    does not split."""
    start, depth, quote, i = 0, 0, "", 0
    while i < len(body):
        c = body[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = ""
        elif c in "'\"":
            quote = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth = max(0, depth - 1)
        elif c == ";" and not depth:
            yield body[start:i]
            start = i + 1
        i += 1
    yield body[start:]


def _decls(body: str) -> Dict[str, str]:
    out = {}
    for part in _split_decls(body):
        if ":" not in part:
            continue
        prop, value = part.split(":", 1)
        prop, value = prop.strip(), value.replace("!important", "").strip()
        if prop and value:
            out[prop if prop.startswith("--") else prop.lower()] = value
    return out


def stylesheet_links(html: str, page_url: str) -> List[str]:
    """Absolute URLs of the page's same-origin `/et-cache/` stylesheets, in document order."""
    origin = urlsplit(page_url).netloc
    out: List[str] = []
    for m in DOC_CSS_RE.finditer(html):
        if m.group(1) is not None or "stylesheet" not in m.group(0):
            continue
        href = HREF_RE.search(m.group(0))
        if not href:
            continue
        url = urljoin(page_url, href.group(1).replace("&#038;", "&").replace("&amp;", "&"))
        parts = urlsplit(url)
        if parts.netloc == origin and "/et-cache/" in parts.path and parts.path.endswith(".css") and url not in out:
            out.append(url)
    return out


def _css(html: str, css_by_url: Optional[dict]) -> str:
    """Inline <style> text and the given linked stylesheets, in document order (unplaced ones last)."""
    css_by_url = dict(css_by_url or {})
    chunks = []
    for m in DOC_CSS_RE.finditer(html):
        if m.group(1) is not None:
            chunks.append(m.group(1))
            continue
        href = HREF_RE.search(m.group(0))
        url = href.group(1).replace("&#038;", "&").replace("&amp;", "&") if href else ""
        if url in css_by_url:
            chunks.append(css_by_url.pop(url))
    chunks += list(css_by_url.values())
    return COMMENT_RE.sub("", "\n".join(chunks))


def _rgba(value: str) -> Optional[Tuple[float, float, float, float]]:
    v = value.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3,8})", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return None
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)", v)
    if m:
        return (float(m.group(1)) / 255, float(m.group(2)) / 255, float(m.group(3)) / 255,
                float(m.group(4)) if m.group(4) else 1.0)
    return None


def _format(r: float, g: float, b: float, a: float) -> str:
    rgb = [max(0, min(255, round(c * 255))) for c in (r, g, b)]
    if a >= 1:
        return "#%02x%02x%02x" % tuple(rgb)
    return "rgba(%d,%d,%d,%s)" % (*rgb, format(round(a, 3), "g"))


def _signed(sign: Optional[str], num: Optional[str]) -> float:
    return (-1 if sign == "-" else 1) * float(num or 0)


def _resolve(name: str, raw: Dict[str, str], seen=()) -> Tuple[Optional[str], Optional[str]]:
    """(resolved value, base id) of a --gcid-* custom property; value None when it can't be resolved."""
    value = raw.get(name)
    if value is None or name in seen:
        return None, None
    alias = VAR_ALIAS_RE.match(value)
    if alias:
        return _resolve(alias.group(1), raw, seen + (name,))[0], alias.group(1)
    m = HSL_FROM_RE.match(value)
    if not m:
        return (value, None) if not value.startswith(("hsl(from", "var(")) else (None, None)
    base = m.group(1)
    base_value = _resolve(base, raw, seen + (name,))[0]
    rgba = _rgba(base_value) if base_value else None
    if rgba is None:
        return None, base
    h, l, s = colorsys.rgb_to_hls(*rgba[:3])
    h = (h * 360 + _signed(m.group(2), m.group(3))) % 360
    ds = _signed(m.group(4), m.group(5)) if m.group(4) else _signed(m.group(6), m.group(7))
    s = max(0.0, min(100.0, s * 100 + ds))
    l = max(0.0, min(100.0, l * 100 + _signed(m.group(8), m.group(9))))
    alpha = rgba[3]
    if m.group(10):
        alpha = float(m.group(10).rstrip("%")) / (100 if m.group(10).endswith("%") else 1)
    r, g, b = colorsys.hls_to_rgb(h / 360, l / 100, s / 100)
    return _format(r, g, b, alpha), base


def _variable(value: str) -> dict:
    v = value.strip()
    m = URL_RE.match(v)
    if m:
        return {"value": m.group(2), "kind": "images"}
    if "gradient(" in v:
        return {"value": v, "kind": "gradients"}
    if v[:1] in ("'", '"'):
        return {"value": v.strip("'\""), "kind": "fonts"}
    return {"value": v, "kind": "numbers"}


def _preset_ref(token: str) -> Optional[Tuple[str, str, Optional[str], str, bool]]:
    """(kind, module, group_name, id, is_wrapper) from a preset class body like `module--divi-button--abc`."""
    kind, rest = token
    wrapper = rest.endswith("_wrapper")
    if wrapper:
        rest = rest[:-len("_wrapper")]
    parts = rest.split("--")
    slug_to_name = lambda slug: slug.replace("-", "/", 1)  # noqa: E731  divi-row-inner -> divi/row-inner
    if kind == "module" and len(parts) >= 2:
        return kind, slug_to_name(parts[0]), None, "--".join(parts[1:]), wrapper
    if kind == "group" and len(parts) >= 4:
        return kind, slug_to_name(parts[0]), slug_to_name(parts[1]), "--".join(parts[3:]), wrapper
    return None


def _primary(selector: str, token: str) -> bool:
    """True when every selector part naming this preset class targets it (or a descendant) without a pseudo."""
    for part in selector.split(","):
        idx = part.find(token)
        if idx >= 0:
            tail = part[idx + len(token):]
            if tail[:1] not in ("", " ", ".", ">", "[") or ":" in tail:
                return False
    return True


def _presets(rules) -> Tuple[dict, dict]:
    presets: Dict[str, dict] = {}
    defaults: Dict[str, dict] = {}
    for media, selector, body in rules:
        decls = _decls(body)
        if not decls:
            continue
        sel = " ".join(selector.split())
        for token in dict.fromkeys(PRESET_CLASS_RE.findall(sel)):
            ref = _preset_ref(token)
            if ref is None:
                continue
            kind, module, group_name, pid, wrapper = ref
            if pid == "default":
                if kind != "module":
                    continue  # a group default's module/group pairing is ambiguous; not recorded
                entry = defaults.setdefault(module, {"selector": None, "declarations": {}, "rules": []})
            else:
                entry = presets.setdefault(pid, {"kind": kind, "module": module,
                                                 **({"group_name": group_name} if group_name else {}),
                                                 "selector": None, "declarations": {}, "rules": []})
            rule = {"selector": sel, "declarations": decls, **({"media": media} if media else {})}
            if rule not in entry["rules"]:
                entry["rules"].append(rule)
            if media is None and not wrapper and _primary(sel, f".preset--{token[0]}--{token[1]}"):
                entry["selector"] = entry["selector"] or sel
                for k, v in decls.items():
                    entry["declarations"].setdefault(k, v)
    return presets, defaults


def _loaded_fonts(html: str, rules_css: str) -> List[str]:
    fonts: List[str] = []
    for href in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"']+)", html):
        for fam in parse_qs(unquote(href.replace("&#038;", "&"))).get("family", []):
            for part in fam.split("|"):
                fonts.append(part.split(":")[0].replace("+", " ").strip())
    for body in re.findall(r"@font-face\s*\{([^{}]*)\}", rules_css):
        fam = _decls(body).get("font-family")
        if fam:
            fonts.append(fam.strip("'\" "))
    return list(dict.fromkeys(f for f in fonts if f and f.lower() not in ICON_FONTS))


def _version(html: str) -> str:
    versions = _ASSET_VER.findall(html)
    if versions:
        return Counter(versions).most_common(1)[0][0]
    m = GENERATOR_RE.search(html)
    return (m.group(1) or m.group(2)) if m else ""


def tokens5_from_html(html: str, css_by_url: Optional[dict] = None) -> dict:
    css = _css(html, css_by_url)
    rules = list(_walk_css(css))
    root: Dict[str, str] = {}
    for media, selector, body in rules:
        if media is None and selector == ":root":
            root.update({k[2:]: v for k, v in _decls(body).items() if k.startswith("--")})
    gcids = {k: v for k, v in root.items() if k.startswith("gcid-")}

    customizer = {}
    for role, (cid, default) in CUSTOMIZER.items():
        if cid in gcids:
            customizer[role] = {"id": cid, "value": gcids[cid], "overridden": gcids[cid].lower() != default}
    global_colors = {}
    for cid, raw in gcids.items():
        if cid in CUSTOMIZER_IDS:
            continue
        value, base = _resolve(cid, gcids)
        global_colors[cid] = {"value": value, **({"raw": raw, "base": base} if base or value is None else {})}

    fonts = {}
    for key in ("heading", "body"):
        family = root.get(f"et_global_{key}_font")
        if family:
            entry = {"id": f"--et_global_{key}_font", "value": family.strip("'\" ")}
            if root.get(f"et_global_{key}_font_weight"):
                entry["weight"] = root[f"et_global_{key}_font_weight"]
            fonts[f"{key}_font"] = entry
    if root.get("et_global_body_font_size"):
        fonts["body_size"] = root["et_global_body_font_size"]
    if root.get("et_global_body_font_height"):
        fonts["body_line_height"] = root["et_global_body_font_height"]

    presets_css, preset_defaults = _presets(rules)
    return {
        "site": {"divi_version": _version(html)},
        "colors": {"global": global_colors, "customizer": customizer},
        "variables": {k: _variable(v) for k, v in root.items() if k.startswith("gvid-")},
        "fonts": {"customizer": fonts, "loaded": _loaded_fonts(html, css)},
        "presets_css": presets_css,
        "preset_defaults": preset_defaults,
    }
