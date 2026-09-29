#!/usr/bin/env python3
"""Detect whether a WordPress site runs Divi 4 or Divi 5 (and the exact version) from the outside.

Research helper for R7 (research/divi5/tokens-and-detection.md). Stdlib only.

  detect_divi.py --url https://site.example/some-page/
  detect_divi.py --url https://site.example/ --user USER    (password from env WP_APP_PASSWORD;
                                                             adds /wp/v2/themes?status=active)
  detect_divi.py --html saved-page.html                     (offline: HTML signals only)
  detect_divi.py --content-file page.txt                    (classify one post_content / content.raw)

HTTPS needs SSL_CERT_FILE=/etc/ssl/cert.pem on this machine.

Signals, strongest first (see the research note for evidence):
  version  1. REST /wp/v2/themes?status=active (auth: any user with edit_posts) -> version when the
              active theme *is* Divi; with a child theme you get template="Divi" only.
           2. GET /wp-content/themes/<template>/style.css -> "Version:" header (public, child-theme safe).
           3. ?ver=X on assets under /themes/Divi/ (Divi enqueues its own assets with the theme version).
           4. <meta content="Divi v.X" name="generator"> -- ACTIVE theme name+version, so a child theme
              prints e.g. "Divi Child v.1.0" (epanel/custom_functions.php head_addons()).
  major    5. X.Y.Z from 1-4 (5.x => Divi 5).
           6. HTML markers: /includes/builder-5/ asset paths, et_pb_custom.builder_images_uri,
              <style class="et-vb-global-data ...">, divi-script-library-* handles, et_block_section /
              et_block_row / et_block_module classes, var diviBreakpointData.
           7. REST index /wp-json/: D5 registers /divi/v1/global-data/*, /divi/v1/settings-data/nonces, ...;
              D4 only /divi/v1/get_layout_content and /divi/v1/block/layout/builder_edit_data.
"""
from __future__ import annotations

import argparse
import base64
import collections
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "divi-genie-detect/0.1"}


def _get(url: str, auth: str = "", timeout: int = 30) -> tuple[int, str]:
    req = urllib.request.Request(url, headers=dict(UA))
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001 -- network errors are reported, not fatal
        return 0, str(e)


D5_HTML_MARKERS = {
    "builder-5 asset path": r"/includes/builder-5/",
    "et-vb-global-data style": r'<style class="et-vb-global-data',
    "divi-script-library handle": r"id=[\"']divi-script-library-",
    "et_block_* classes": r"\bet_block_(?:section|row|module)\b",
    "diviBreakpointData var": r"var diviBreakpointData\b",
}
D4_HTML_MARKERS = {
    "D4 builder_images_uri": r'"builder_images_uri":"[^"]*?(?:\\/|/)includes(?:\\/|/)builder(?:\\/|/)images"',
}


def html_signals(html: str) -> dict:
    out: dict = {"d5_markers": [], "d4_markers": []}
    for name, pat in D5_HTML_MARKERS.items():
        if re.search(pat, html):
            out["d5_markers"].append(name)
    for name, pat in D4_HTML_MARKERS.items():
        if re.search(pat, html):
            out["d4_markers"].append(name)
    m = re.search(r'<meta content="([^"]+) v\.([\w.\-]+)" name="generator"', html)
    if m:
        out["generator"] = {"theme": m.group(1), "version": m.group(2)}
    vers = re.findall(r"/themes/Divi/[^\"'\s?]+\?ver=([0-9][\w.\-]*)", html)
    if vers:
        out["divi_asset_ver"] = collections.Counter(vers).most_common(1)[0][0]
    m = re.search(r"/themes/([^/\"']+)/style\.css", html)
    tmpl = re.search(r"/wp-content/themes/([^/\"']+)/", html)
    out["template_dir"] = "Divi" if "/themes/Divi/" in html else (tmpl.group(1) if tmpl else "")
    if m:
        out["stylesheet_dir"] = m.group(1)
    out["has_legacy_d4_render"] = "et_d4_element" in html  # D4 shortcode rendered by D5's bundled D4 framework
    return out


def classify_content(raw: str) -> dict:
    """Classify a post_content / REST content.raw string."""
    s = raw.strip()
    blocks = collections.Counter(re.findall(r"<!-- wp:(divi/[a-z0-9-]+)", s))
    has_sc = bool(re.search(r"\[et_pb_[a-z_]+", s))
    if not blocks and has_sc:
        kind = "d4-shortcode"
    elif blocks and "divi/layout" in blocks and has_sc:
        kind = "d4-block-editor-layout"  # D4's Gutenberg "Divi Layout" block wrapping shortcode
    elif blocks and "divi/placeholder" in blocks and has_sc and len(blocks) == 1:
        kind = "d4-shortcode-in-placeholder"
    elif blocks:
        kind = "d5-blocks" + ("+shortcode-module" if "divi/shortcode-module" in blocks else "")
    else:
        kind = "no-divi"
    bv = collections.Counter(re.findall(r'"builderVersion":"([^"]+)"', s))
    sv = collections.Counter(re.findall(r'_builder_version="([^"]+)"', s))
    return {"kind": kind, "divi_blocks": dict(blocks.most_common(8)),
            "d5_builderVersion": dict(bv.most_common(3)), "d4__builder_version": dict(sv.most_common(3))}


def detect(url: str = "", user: str = "", password: str = "", html: str = "") -> dict:
    res: dict = {"signals": []}
    base = ""
    if url:
        p = urllib.parse.urlsplit(url)
        base = f"{p.scheme}://{p.netloc}"
        st, html = _get(url)
        res["page_status"] = st
    hs = html_signals(html or "")
    res["html"] = hs
    version, source = "", ""

    if base and user and password:
        st, body = _get(base + "/wp-json/wp/v2/themes?status=active", f"{user}:{password}")
        if st == 200:
            try:
                t = json.loads(body)[0]
                res["rest_theme"] = {k: t.get(k) for k in ("stylesheet", "template", "version")}
                if t.get("stylesheet") == "Divi":
                    version, source = t.get("version", ""), "rest /wp/v2/themes"
            except Exception:  # noqa: BLE001
                pass
        else:
            res["rest_theme_status"] = st

    if base and not version:
        tpl = (res.get("rest_theme") or {}).get("template") or hs.get("template_dir") or "Divi"
        st, css = _get(f"{base}/wp-content/themes/{tpl}/style.css")
        m = re.search(r"Theme Name:\s*(.+)\n(?:.*\n){0,4}?Version:\s*([\w.\-]+)", css) if st == 200 else None
        if m and "Divi" in m.group(1):
            version, source = m.group(2), f"themes/{tpl}/style.css"
    if not version and hs.get("divi_asset_ver"):
        version, source = hs["divi_asset_ver"], "?ver= on /themes/Divi/ assets"
    if not version and hs.get("generator", {}).get("theme", "").startswith("Divi"):
        version, source = hs["generator"]["version"], "generator meta"

    if base:
        st, body = _get(base + "/wp-json/")
        if st == 200:
            try:
                routes = json.loads(body).get("routes", {})
                divi = [r for r in routes if r.startswith("/divi/")]
                res["rest_index"] = {"divi_routes": len(divi),
                                     "d5_routes": any(r.startswith("/divi/v1/global-data") or r.startswith("/divi/v1/settings-data") for r in divi)}
            except Exception:  # noqa: BLE001
                pass

    major = version.split(".")[0] if version else ""
    if not major:
        if hs["d5_markers"] or (res.get("rest_index") or {}).get("d5_routes"):
            major = "5"
        elif hs["d4_markers"]:
            major = "4"
    res.update({"divi_version": version, "version_source": source, "divi_major": major})
    if major == "5" and not hs["d5_markers"] and html:
        res["signals"].append("warning: version says 5 but no D5 HTML markers (cached/optimised HTML?)")
    if major == "4" and hs["d5_markers"]:
        res["signals"].append("warning: version says 4 but D5 markers present")
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--user")
    ap.add_argument("--html", help="offline: a saved page HTML file")
    ap.add_argument("--content-file", help="classify a post_content/content.raw file")
    a = ap.parse_args()
    if a.content_file:
        print(json.dumps(classify_content(open(a.content_file, encoding="utf-8").read()), indent=1))
        return 0
    html = open(a.html, encoding="utf-8", errors="replace").read() if a.html else ""
    print(json.dumps(detect(a.url or "", a.user or "", os.environ.get("WP_APP_PASSWORD", ""), html), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
