"""Value parsing shared by the renderer: ranges, escaping, icons, text filters and
responsive/hover access to module props (Divi's ResponsiveOptions / HoverOptions)."""
from __future__ import annotations

import html
import re

DEVICES = ("desktop", "tablet", "phone")
MEDIA = {"desktop": "", "desktop_only": "@media only screen and (min-width:981px)",
         "tablet": "@media only screen and (max-width:980px)", "phone": "@media only screen and (max-width:767px)"}
SIDES = ("top", "right", "bottom", "left")
# Box/text shadow presets (Divi's BoxShadow and TextShadow option classes).
TEXT_SHADOW_PRESETS = {"preset1": ("0em", "0.1em", "0.1em"), "preset2": ("0.08em", "0.08em", "0.08em"),
                       "preset3": ("0em", "0em", "0.3em"), "preset4": ("0em", "0.08em", "0em"),
                       "preset5": ("0.08em", "0.08em", "0em")}
BOX_SHADOW_PRESETS = {"preset1": ("0px", "2px", "18px", "0px", "outer"), "preset2": ("6px", "6px", "18px", "0px", "outer"),
                      "preset3": ("0px", "12px", "18px", "-6px", "outer"), "preset4": ("10px", "10px", "0px", "0px", "outer"),
                      "preset5": ("0px", "6px", "0px", "10px", "outer"), "preset6": ("0px", "0px", "18px", "0px", "inner"),
                      "preset7": ("10px", "10px", "0px", "0px", "inner")}


# ----------------------------------------------------------------------------- numbers
def to_css_decimal(v: float) -> str:
    s = ("%.6f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def range_value(val: str, option_type: str = "") -> str:
    """et_builder_process_range_value()."""
    val = val.strip()
    if option_type == "line_height" and val in ("normal", "inherit", "initial"):
        return val
    m = re.match(r"^(-?[\d.]+)(.*)$", val)
    if not m:
        return val
    try:
        num = float(m.group(1))
    except ValueError:
        return val
    unit = m.group(2)
    if unit == "":
        unit = "em" if option_type == "line_height" and num <= 3 else "px"
    return to_css_decimal(num) + unit


def four_sides(value: str) -> list:
    """'10px|auto||5px|true|false' -> the four side values (top, right, bottom, left)."""
    return (value.split("|") + [""] * 4)[:4]


# ----------------------------------------------------------------------------- escaping
def esc(s: str) -> str:
    return html.escape(s, quote=True)


def esc_url(s: str) -> str:
    """WordPress esc_url(): keeps the URL, encodes & as &#038;."""
    s = s.strip().replace("&amp;", "&").replace("&", "&#038;")
    return s.replace('"', "%22").replace("'", "&#039;")


def new_window(p) -> str:
    return ' target="_blank"' if p.get("url_new_window", "") == "on" else ""


# ----------------------------------------------------------------------------- icons
def decode_icon(v: str) -> str:
    """'&#xe03b;||divi||400' -> the private-use glyph."""
    code = v.split("|")[0]
    m = re.match(r"&#x([0-9a-fA-F]+);?", code)
    if m:
        return chr(int(m.group(1), 16))
    m = re.match(r"%%(\d+)%%", code)   # legacy numeric icon index: not resolved
    return "" if m else html.unescape(code)


def icon_font(v: str) -> tuple:
    parts = v.split("|")
    fam = parts[2] if len(parts) > 2 else ""
    weight = parts[4] if len(parts) > 4 and parts[4] else "400"
    return ("FontAwesome" if fam == "fa" else "ETmodules"), weight


def icon_css_content(v: str) -> str:
    """et_pb_get_extended_icon_value_for_css() as it reaches the page: real Divi's CSS output
    treats a backslash followed by digits as a regex backreference (empty), so the ASCII-range
    Divi icons print e.g. content:"" for &#x50; and content:"c" for &#x4c;."""
    code = v.split("|")[0]
    m = re.match(r"&#x([0-9a-fA-F]+);?", code)
    if not m:
        return '""'
    return '"%s"' % re.sub(r"\\\d{1,2}", "", "\\" + m.group(1).lower())


# ----------------------------------------------------------------------------- text
def wptexturize(s: str) -> str:
    """Subset of WordPress wptexturize() (runs on the_content): apostrophes + straight quotes in text."""
    parts = re.split(r"(<[^>]*>)", s)
    for i, part in enumerate(parts):
        if part.startswith("<"):
            continue
        part = re.sub(r"(?<=\w)'(?=\w)", "&#8217;", part)
        part = re.sub(r"(^|\s)'", r"\1&#8216;", part)
        part = re.sub(r"'", "&#8217;", part)
        part = re.sub(r'(^|\s|>)"', r"\1&#8220;", part)
        part = re.sub(r'"', "&#8221;", part)
        part = part.replace(" -- ", " &#8212; ").replace("...", "&#8230;")
        parts[i] = part
    return "".join(parts)


def module_content(node) -> str:
    """Module body as Divi outputs it: builder pages skip wpautop; wptexturize still runs."""
    return wptexturize(node.content.strip("\n"))


# ----------------------------------------------------------------------------- props
class Props(dict):
    """Module props (defaults + attrs) that records which keys were read (coverage)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.read = set()

    def __getitem__(self, k):
        self.read.add(k)
        return super().get(k, "")

    def get(self, k, d=""):
        self.read.add(k)
        return super().get(k, d)


def resp_enabled(p: Props, name: str) -> bool:
    return p.get(f"{name}_last_edited", "").startswith("on")


def any_value(p: Props, name: str, device: str = "desktop", default: str = "", force: bool = False) -> str:
    """ResponsiveOptions::get_any_value()."""
    base = re.sub(r"_(tablet|phone)$", "", name)
    key = base if device == "desktop" else f"{base}_{device}"
    cur = dict.get(p, key, "") if key in p else ""
    p.read.add(key)
    if device == "desktop":
        prev = default
    else:
        desktop = dict.get(p, base, "") or default
        prev = desktop if device == "tablet" else (dict.get(p, f"{base}_tablet", "") or desktop)
    if force:
        return cur or prev
    return "" if cur == prev else cur


def property_values(p: Props, name: str, default: str = "", force: bool = False) -> dict:
    vals = {d: default for d in DEVICES}
    vals["desktop"] = any_value(p, name, "desktop", default, force)
    if resp_enabled(p, name):
        vals["tablet"] = any_value(p, name, "tablet", default, force)
        vals["phone"] = any_value(p, name, "phone", default, force)
    else:
        vals["tablet"] = vals["phone"] = ""
    return vals


def hover_enabled(p: Props, name: str) -> bool:
    """HoverOptions::is_enabled(): background_color/background_image share the `background` toggle."""
    base = "background" if name in ("background_color", "background_image") else name
    return p.get(f"{base}__hover_enabled", "").startswith("on")


def hover_value(p: Props, name: str, default=None):
    if hover_enabled(p, name):
        v = p.get(f"{name}__hover", "")
        return v if v != "" else default
    return default
