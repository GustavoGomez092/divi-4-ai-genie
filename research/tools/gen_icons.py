#!/usr/bin/env python3
"""Generate Skill/divi-page-builder/reference/icons.md from a cached Divi build's icon list.

Usage: gen_icons.py [--divi THEME_DIR] [--out PATH]

THEME_DIR defaults to the newest cached Divi (…/Divi-<version>/Divi, see scripts/fetch_divi.py).
Reads includes/builder/feature/icon-manager/full_icons_list.json (read-only; the Divi build itself is
never copied into the repo) and writes one list line per icon with the exact value Divi stores and
validate.py accepts: `<unicode entity>||divi|fa||<weight>` (et_pb_build_extended_font_icon_value()).
Output is deterministic: Divi's own list order, the common list in the order written below.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Skill" / "divi-page-builder" / "scripts"))
import fetch_divi  # noqa: E402

ICON_LIST = Path("includes/builder/feature/icon-manager/full_icons_list.json")
DEFAULT_OUT = ROOT / "Skill" / "divi-page-builder" / "reference" / "icons.md"

# Icons a local-business / landing page reaches for most, Font Awesome names (solid weight when it exists).
COMMON_FA = """phone phone-alt phone-volume mobile-alt envelope envelope-open map-marker-alt map-marker map-marked-alt
location-arrow directions route clock calendar-alt calendar-check check check-circle check-square star
star-half-alt quote-left quote-right user users user-tie user-check home building store wrench tools hammer
screwdriver toolbox hard-hat truck truck-moving car shield-alt award medal trophy certificate dollar-sign
money-bill-wave credit-card hand-holding-usd piggy-bank percent tag tags gift heart thumbs-up smile comment
comments comment-dots headset search shopping-cart shopping-bag lightbulb leaf seedling tree tint water faucet
shower bath toilet bolt plug fire fire-extinguisher snowflake fan thermometer-half temperature-high sun
paint-roller paint-brush broom trash-alt recycle key lock unlock globe wifi arrow-right arrow-left arrow-up
arrow-down chevron-right chevron-left chevron-down chevron-up angle-right angle-double-right
long-arrow-alt-right caret-right plus minus times info-circle question-circle exclamation-triangle
exclamation-circle bell clipboard-check clipboard-list file-alt file-pdf download upload play play-circle video
camera image images link external-link-alt share-alt handshake hands-helping briefcase chart-line chart-bar
bullhorn rocket cog cogs stethoscope tooth heartbeat paw utensils coffee graduation-cap book calculator
balance-scale gavel file-signature laptop desktop code facebook-f facebook twitter instagram linkedin-in
youtube google yelp whatsapp tiktok pinterest-p""".split()
# Divi's own icon font: every variant (line/solid/…) of these names.
COMMON_DIVI = ["Phone", "Envelop", "Map Pin", "Clock", "Check", "Star", "Quote", "Home", "Tools", "Toolbox",
               "Shield", "Dollar", "Calendar", "Heart", "Thumbs Up", "Chat", "Lightbulb", "Gear", "Person", "Group"]


def value(icon: dict) -> str:
    family = "divi" if icon["is_divi_icon"] else "fa"
    return f"{icon['unicode']}||{family}||{int(icon['font_weight'])}"


def style(icon: dict) -> str:
    if icon["is_divi_icon"]:
        return "divi, " + "/".join(s for s in icon["styles"] if s != "divi")
    if int(icon["font_weight"]) == 900:
        return "fa, solid"
    return "fa, regular" if "line" in icon["styles"] else "fa, brands"


def terms(icon: dict) -> str:
    name_words = set(re.split(r"[\s-]+", icon["name"].lower())) | {icon["name"].lower()}
    out = []
    for w in icon.get("search_terms", "").lower().split():
        if w not in name_words and w not in out:
            out.append(w)
    return " ".join(out[:8])


def line(icon: dict) -> str:
    t = terms(icon)
    return f"- `{value(icon)}` {icon['name']} ({style(icon)})" + (f" — {t}" if t else "")


def build(icons: list, version: str) -> str:
    fa_by_name = {}
    for i in icons:
        if not i["is_divi_icon"]:
            fa_by_name.setdefault(i["name"], []).append(i)
    common = []
    for name in COMMON_FA:
        if name not in fa_by_name:
            raise SystemExit(f"gen_icons.py: common icon {name!r} is not in Divi {version}'s list")
        variants = fa_by_name[name]
        common.append(next((v for v in variants if int(v["font_weight"]) == 900), variants[0]))
    for name in COMMON_DIVI:
        picks = [i for i in icons if i["is_divi_icon"] and i["name"] == name]
        if not picks:
            raise SystemExit(f"gen_icons.py: common Divi icon {name!r} is not in Divi {version}'s list")
        common += picks

    groups = [
        ("Divi icon font", "Divi's own icons (`||divi||`), line and solid variants.",
         [i for i in icons if i["is_divi_icon"]]),
        ("Font Awesome solid", "`||fa||900`.",
         [i for i in icons if not i["is_divi_icon"] and int(i["font_weight"]) == 900]),
        ("Font Awesome regular", "`||fa||400` outline versions.",
         [i for i in icons if not i["is_divi_icon"] and int(i["font_weight"]) != 900 and "line" in i["styles"]]),
        ("Font Awesome brands", "`||fa||400` brand logos.",
         [i for i in icons if not i["is_divi_icon"] and int(i["font_weight"]) != 900 and "line" not in i["styles"]]),
    ]
    assert sum(len(g[2]) for g in groups) == len(icons)

    out = [
        "# Icons",
        "",
        f"Every icon Divi {version}'s icon picker offers, with the exact value to write in an icon field",
        "(`font_icon`, `button_icon`, `hover_icon`, …; field type `select_icon`, see `value-formats.md` →",
        "Icons). Copy the value in backticks as-is: `<entity>||divi|fa||<weight>`. Search this file for a",
        "word (\"phone\", \"water\", \"calendar\"); each line is `value` name (family, style) — search terms.",
        "",
        "Blurbs need `use_icon=\"on\"` for `font_icon` to show; buttons need `custom_button=\"on\"` for",
        "`button_icon`. Divi icons (`||divi||`) always use weight `400`; Font Awesome solid is `900`, regular",
        "and brands are `400`.",
        "",
        f"Generated from Divi {version}'s built-in icon list (repo only: `research/tools/gen_icons.py`); do",
        "not edit by hand.",
        "",
        f"## Common icons ({len(common)})",
        "",
        "Contact, location, trust, trades and navigation icons for business pages, Font Awesome first.",
        "",
        *[line(i) for i in common],
    ]
    for title, blurb, items in groups:
        out += ["", f"## {title} ({len(items)})", "", blurb, "", *[line(i) for i in items]]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--divi", help="unpacked Divi theme dir (default: newest cached)")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args(argv)
    if a.divi:
        theme = Path(a.divi)
    else:
        version = fetch_divi.newest_cached()
        theme = fetch_divi.theme_dir(version) if version else None
        if theme is None:
            print("gen_icons.py: no Divi build cached; run scripts/preview.py fetch-divi VERSION", file=sys.stderr)
            return 2
    m = re.search(r"^Version:\s*(\S+)", (theme / "style.css").read_text(encoding="utf-8", errors="replace"), re.M)
    version = m.group(1) if m else "?"
    icons = json.loads((theme / ICON_LIST).read_text(encoding="utf-8"))
    Path(a.out).write_text(build(icons, version), encoding="utf-8")
    print(f"wrote {a.out}: {len(icons)} icons from Divi {version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
