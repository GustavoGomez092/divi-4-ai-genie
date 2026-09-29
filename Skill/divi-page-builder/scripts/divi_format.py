#!/usr/bin/env python3
"""Tell Divi 4 shortcode from Divi 5 block content, and find a site's Divi version.

  python3 divi_format.py content PAGE      -> shortcode | blocks | mixed | empty
  python3 divi_format.py site URL          -> JSON {divi_version, divi_major, evidence}
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
from typing import Callable, Optional

_BLOCK_OPEN = re.compile(r"<!--\s+wp:divi/[a-z0-9-]+")
# A whole block delimiter comment; its JSON may hold a raw `>` (WordPress escapes `--`, so `-->` ends it).
_JSON_BLOCK = re.compile(r"<!--\s+/?wp:(?:(?!-->).)*-->", re.S)
_SHORTCODE = re.compile(r"\[et_pb_[a-z0-9_]+[\s\]/]")
_VERSION = re.compile(r"^\s*Version:\s*([0-9][0-9.]*)", re.M)
_ASSET_VER = re.compile(r"/themes/Divi/[^\"'?\s]*\?ver=([0-9]+\.[0-9][0-9.]*)")
_GENERATOR = re.compile(r'<meta content="Divi v\.([0-9][0-9.]*)" name="generator"')
# Markers only Divi 5 front-end output carries (see research/tools/divi5/detect_divi.py).
_D5_HTML_MARKERS = re.compile(
    r"/includes/builder-5/"
    r'|<style class="et-vb-global-data'
    r"""|id=["']divi-script-library-"""
    r"|\bet_block_(?:section|row|module)\b"
    r"|var diviBreakpointData\b")


def detect_content(text: str) -> str:
    has_blocks = bool(_BLOCK_OPEN.search(text))
    outside = _JSON_BLOCK.sub(" ", text) if has_blocks else text
    has_shortcode = bool(_SHORTCODE.search(outside))
    if has_blocks and has_shortcode:
        return "mixed"
    if has_blocks:
        return "blocks"
    if has_shortcode:
        return "shortcode"
    return "empty"


def major_from_version(v: Optional[str]) -> Optional[int]:
    m = re.match(r"^\s*(\d+)\.", v or "")
    return int(m.group(1)) if m else None


def parse_style_css_version(css_text: str) -> Optional[str]:
    m = _VERSION.search(css_text[:4000])
    return m.group(1) if m else None


def _default_fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "divi-page-builder/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def detect_site(url: str, fetch: Optional[Callable[[str], bytes]] = None) -> dict:
    fetch = fetch or _default_fetch
    base = url.rstrip("/")
    try:
        v = parse_style_css_version(fetch(base + "/wp-content/themes/Divi/style.css").decode("utf-8", "replace"))
        if v:
            return {"divi_version": v, "divi_major": major_from_version(v), "evidence": "style.css"}
    except Exception:
        pass
    try:
        html = fetch(base + "/").decode("utf-8", "replace")
    except Exception as exc:
        return {"divi_version": None, "divi_major": None, "evidence": f"unreachable: {exc}"}
    versions = _ASSET_VER.findall(html)
    if not versions:
        # Active theme name+version; only trusted when the theme is Divi itself (not a child theme).
        versions = _GENERATOR.findall(html)
    v = max(versions, key=lambda s: tuple(int(x) for x in s.split(".") if x.isdigit())) if versions else None
    major = major_from_version(v)
    if _D5_HTML_MARKERS.search(html):
        major = 5
    return {"divi_version": v, "divi_major": major, "evidence": "assets" if (v or major) else "none"}


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2 or argv[0] not in ("content", "site"):
        print(__doc__, file=sys.stderr)
        return 2
    if argv[0] == "content":
        with open(argv[1], encoding="utf-8") as fh:
            print(detect_content(fh.read()))
    else:
        print(json.dumps(detect_site(argv[1])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
