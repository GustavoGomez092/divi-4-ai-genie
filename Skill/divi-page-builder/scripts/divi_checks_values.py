"""Attribute-name and attribute-value rules for Divi 4 modules."""
from __future__ import annotations

import difflib
import json
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from divi_shortcode import wp_blanks_value

COLOR_RE = re.compile(r"^(#[0-9a-fA-F]{3,4}|#[0-9a-fA-F]{6}|#[0-9a-fA-F]{8}|(?i:rgba?|hsla?)\([^)]*\)|transparent|gcid-[\w-]+|var\(--[\w-]+\))$")
NUMBER_UNIT_RE = re.compile(r"^(-?(?:\d+\.?\d*|\.\d+))([a-z%]*)$", re.I)
CSS_KEYWORDS = {"auto", "none", "inherit", "initial", "unset", "normal"}
GENERIC_UNITS = {"%", "em", "rem", "px", "cm", "mm", "in", "pt", "pc", "ex", "vh", "vw", "deg", "ms", "s", ""}
ICON_RE = re.compile(r"^(&#x[0-9a-fA-F]+;|&amp;#x[0-9a-fA-F]+;|[^|]*)\|\|(divi|fa)\|\|(\d{3})?$|^%%\d+%%$")
LAST_EDITED_RE = re.compile(r"^(on|off)\|(desktop|tablet|phone|hover|sticky)$")
STATE_TOGGLE_RE = re.compile(r"^(on|off)(\|\w+)?$")
SELECT_TYPES = {"select", "select_animation", "select-pattern", "select-mask", "text_align", "align", "position",
                "divider", "select_with_option_groups", "select_box_shadow", "presets_shadow", "yes_no_button"}
COLOR_TYPES = {"color", "color-alpha"}
# `<provider>_list` of every email provider the Email Optin offers (Signup.php init():
# providers()->names_by_slug(), i.e. core/components/api/email/*; FeedBurner has no list).
EMAIL_PROVIDER_LISTS = {f"{p}_list" for p in (
    "activecampaign", "aweber", "campaign_monitor", "constant_contact", "convertkit", "emma", "feedblitz",
    "fluentcrm", "getresponse", "hubspot", "icontact", "infusionsoft", "madmimi", "mailchimp", "mailerlite",
    "mailpoet", "mailster", "ontraport", "salesforce", "sendinblue")}
LINE_STYLES = {"", "solid", "double", "dotted", "dashed", "wavy"}
# Attribute names publish.py scans for local files to upload (any media: images, and video/audio src).
IMAGE_ATTRS = ("src", "image", "background_image", "logo", "image_url", "portrait_url", "logo_image_url")

Problem = Tuple[str, str, str, str]  # (level, code, message, hint)


def normalize_color(value: str) -> str:
    v = value.strip().lower().replace(" ", "")
    if re.fullmatch(r"#[0-9a-f]{3}", v):
        v = "#" + "".join(c * 2 for c in v[1:])
    return v


def is_color_field(name: str, field: Optional[dict]) -> bool:
    """True for a plain color field, or a "background-field" composite whose base attribute
    (e.g. button_bg_color) is itself the hex/rgba color, as opposed to its image/gradient/video
    siblings."""
    field = field or {}
    ftype = field.get("type")
    if ftype in COLOR_TYPES:
        return True
    return ftype == "background-field" and name.endswith("_color")


def is_image_field(res) -> bool:
    """True when the resolved attribute holds an image URL: an upload field whose media type is image
    (et_pb_image src, blurb image, background_image, a video's image_src poster), or a button's
    *_bg_image background. False for video/audio uploads (et_pb_video src, background_video_mp4)."""
    if res is None:
        return False
    field = res.field or {}
    if field.get("type") == "upload":
        return field.get("data_type", "image") == "image"
    return res.base.endswith("_bg_image")


def _length_ok(part: str, units) -> bool:
    if part == "" or part.lower() in CSS_KEYWORDS or part.startswith(("calc(", "var(", "clamp(", "min(", "max(")):
        return True
    m = NUMBER_UNIT_RE.match(part)
    return bool(m) and (m.group(2).lower() in (units or GENERIC_UNITS) or m.group(2) == "")


def value_problems(res, attr: str, value: str) -> List[Problem]:
    if value == "":
        return []
    if attr.endswith("_last_edited"):
        return [] if LAST_EDITED_RE.match(value) else [(
            "error", "E_VALUE_FORMAT", f"{attr} must look like 'on|phone' or 'off|desktop'", "")]
    if res.kind == "state_toggle":
        return [] if STATE_TOGGLE_RE.match(value) else [(
            "error", "E_VALUE_FORMAT", f"{attr} must be 'on|hover' / 'on|sticky' or 'off|desktop'", "")]
    field = res.field or {}
    ftype = field.get("type", "")
    if ftype == "global_colors_info":
        try:
            json.loads(value)
            return []
        except ValueError:
            return [("error", "E_VALUE_FORMAT", "global_colors_info must be JSON (escape \" as %22, [ as %91, ] as %93)", "")]
    options = field.get("options")
    if ftype in SELECT_TYPES and options:
        # Email Optin lists: the schema only knows '0|none' and the manage actions; real values
        # are '<account>|<list id>' pairs from the site's connected accounts (Signup.php render()
        # splits them on the last '|'). Only the email providers' lists: recaptcha_list (spam
        # protection) never holds such a pair.
        if attr in EMAIL_PROVIDER_LISTS and "|" in value and not value.startswith("manage|"):
            return []
        if value not in options:
            shown = ", ".join(options[:12]) + (" …" if len(options) > 12 else "")
            return [("error", "E_BAD_OPTION", f"'{value}' is not an option for {attr}", f"Options: {shown}")]
        return []
    if ftype == "multiple_buttons" and options:
        bad = [p for p in value.split("|") if p and p not in options]
        return [("error", "E_BAD_OPTION", f"{bad} not in options for {attr}", "Options: " + ", ".join(options))] if bad else []
    if ftype == "multiple_checkboxes" and options:
        parts = value.split("|")
        if len(parts) != len(options) or any(p not in ("on", "off", "") for p in parts):
            return [("error", "E_VALUE_FORMAT", f"{attr} needs {len(options)} on/off flags joined by '|' ({'|'.join(options)})", "")]
        return []
    if ftype == "range":
        if _length_ok(value, [u.lower() for u in field.get("units", [])] or None):
            return []
        m = NUMBER_UNIT_RE.match(value)
        code = "E_BAD_UNIT" if m else "E_VALUE_FORMAT"
        return [("error", code, f"'{value}' is not a valid length for {attr}",
                 "Allowed units: " + ", ".join(field.get("units", sorted(GENERIC_UNITS - {''}))))]
    if is_color_field(res.base, field):
        return [] if COLOR_RE.match(value.strip()) else [(
            "error", "E_VALUE_FORMAT", f"'{value}' is not a color", "Use #hex, rgba(), or a gcid- global color id.")]
    if ftype == "font":
        parts = value.split("|")
        if len(parts) > 9:
            return [("error", "E_VALUE_FORMAT", f"Font string has {len(parts)} parts; Divi uses 9",
                     "Family|weight|italic|uppercase|underline|smallcaps|strikethrough|line_color|line_style")]
        out: List[Problem] = []
        parts += [""] * (9 - len(parts))
        if parts[1] not in ("", "on", "off") and not re.fullmatch(r"[1-9]00", parts[1]):
            out.append(("warning", "W_FONT_WEIGHT", f"Font weight '{parts[1]}' is not 100–900", "Use 100…900, or leave empty."))
        if any(p not in ("", "on", "off") for p in parts[2:7]):
            out.append(("error", "E_VALUE_FORMAT", "Font style flags (parts 3–7) must be on, off or empty", ""))
        if parts[7] and not COLOR_RE.match(parts[7]):
            out.append(("error", "E_VALUE_FORMAT", "Font line color (part 8) must be a color", ""))
        if parts[8] not in LINE_STYLES:
            out.append(("error", "E_VALUE_FORMAT", f"Font line style must be one of {sorted(LINE_STYLES - {''})}", ""))
        return out
    if ftype in ("custom_margin", "custom_padding"):
        parts = value.split("|")
        units = [u.lower() for u in field.get("units", [])] or None
        if len(parts) > 6 or not all(_length_ok(p, units) for p in parts[:4]) or any(p not in ("", "true", "false") for p in parts[4:6]):
            return [("error", "E_VALUE_FORMAT", f"'{value}' is not a Divi spacing value",
                     "top|right|bottom|left|linked_top_bottom|linked_left_right, e.g. 80px||80px||true|false")]
        return []
    if ftype == "border-radius":
        parts = value.split("|")
        units = [u.lower() for u in field.get("units", [])] or None
        if len(parts) != 5 or parts[0] not in ("", "on", "off") or not all(_length_ok(p, units) for p in parts[1:]):
            return [("error", "E_VALUE_FORMAT", f"'{value}' is not a Divi border radius", "on|top-left|top-right|bottom-right|bottom-left")]
        return []
    if ftype == "select_icon":
        return [] if ICON_RE.match(value) else [(
            "error", "E_VALUE_FORMAT", f"'{value}' is not a Divi icon value", "e.g. &#xf0a9;||fa||900 or &#xe03b;||divi||400")]
    return []


def check_attributes(doc, schema, report, known_presets=frozenset(), site_host: Optional[str] = None) -> None:
    for node, path, _parent in doc.walk():
        mod = schema.module(node.tag)
        if mod is None:
            continue
        for name in node.duplicate_attrs:
            report("warning", "W_DUPLICATE_ATTR", f"'{name}' is set more than once; the last value wins", node=node, path=path, attr=name)
        for token in node.positional:
            report("error", "E_POSITIONAL_ATTR", f"Stray token {token!r} in the [{node.tag}] tag", node=node, path=path,
                   hint='Attributes must be name="value".')
        for name, raw in node.attrs.items():
            if node.quoting.get(name, '"') != '"':
                report("warning", "W_ATTR_QUOTING", f"{name} is not double-quoted", node=node, path=path, attr=name,
                       hint="Divi always writes name=\"value\".")
                if '"' in raw:
                    report("error", "E_RAW_QUOTE", f"{name} contains a raw double quote", node=node, path=path, attr=name,
                           value=raw, hint="Write \" as %22 and double-quote the value.")
            if "[" in raw or "]" in raw:
                report("error", "E_RAW_BRACKET", f"{name} contains a raw [ or ]", node=node, path=path, attr=name, value=raw,
                       hint="Write [ as %91 and ] as %93.")
            if wp_blanks_value(raw):
                report("error", "E_ATTR_LT", f"WordPress will empty {name}: it contains a '<' that is not a complete tag",
                       node=node, path=path, attr=name, value=raw, hint="Rephrase without '<', or use &lt; in HTML content.")
            res = mod.resolve(name)
            if res is None:
                close = difflib.get_close_matches(name, mod.attribute_names(), n=1, cutoff=0.75)
                report("error", "E_UNKNOWN_ATTR", f"[{node.tag}] has no attribute '{name}'", node=node, path=path, attr=name,
                       value=raw, hint=f"did you mean '{close[0]}'?" if close else f"See reference/modules/{mod.slug}.md.")
                continue
            for level, code, message, hint in value_problems(res, name, node.value(name)):
                report(level, code, message, node=node, path=path, attr=name, value=raw, hint=hint)
            if site_host and is_image_field(res):
                host = urlparse(node.value(name)).hostname
                if host and host != site_host:
                    report("warning", "W_EXTERNAL_IMAGE", f"{name} points to {host}, not the site", node=node, path=path,
                           attr=name, hint="Upload the image to the site's Media Library and use that URL.")
        for name in node.attrs:
            for state in ("hover", "sticky"):
                suffix = f"__{state}"
                if name.endswith(suffix) and mod.resolve(name) is not None:
                    base = name[: -len(suffix)]
                    key = "background" if base in ("background_color", "background_image") else base
                    if not node.value(f"{key}__{state}_enabled").startswith("on"):
                        report("warning", f"W_{state.upper()}_DISABLED",
                               f"{name} is ignored until {key}__{state}_enabled starts with 'on'", node=node, path=path, attr=name)
            for suffix in ("_tablet", "_phone"):
                if name.endswith(suffix) and mod.resolve(name) is not None:
                    base = name[: -len(suffix)]
                    if not node.value(f"{base}_last_edited").startswith("on"):
                        report("warning", "W_RESPONSIVE_DISABLED", f"{name} is ignored until {base}_last_edited starts with 'on'",
                               node=node, path=path, attr=name, hint=f'Add {base}_last_edited="on|phone".')
        preset = node.value("_module_preset")
        if preset and preset != "default" and preset not in known_presets:
            report("warning", "W_UNKNOWN_PRESET", f"_module_preset {preset} is not a preset known on this site",
                   node=node, path=path, attr="_module_preset",
                   hint="Use a preset UUID listed in tokens.json, or 'default' with inline styles.")
