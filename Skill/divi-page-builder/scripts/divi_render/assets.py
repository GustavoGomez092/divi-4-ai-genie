"""Divi's static files (CSS, icon fonts, JS, font list, mask SVGs), read at runtime from the
cached theme (fetch_divi.theme_dir), never copied into the repo.

Three delivery modes for the assets a page references (fonts and images in Divi's CSS, the logo):
- asset_base (serve mode): URLs under that prefix, e.g. "/__divi/core/admin/fonts/...", which
  the preview server maps back onto the theme dir (resolve_asset guards against traversal);
- embed (standalone files): fonts and images inlined as data: URIs. Browsers refuse file://
  sub-resources on a page served over http(s), which left every icon an empty box in the spike;
- neither: left relative (never file://), for in-process comparisons that don't load assets.
"""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import fetch_divi  # noqa: E402

MIME = {".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".eot": "application/vnd.ms-fontobject",
        ".png": "image/png", ".gif": "image/gif", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml", ".webp": "image/webp", ".css": "text/css", ".js": "text/javascript",
        ".json": "application/json"}
EMBED_SUFFIXES = (".woff2", ".woff", ".png", ".gif", ".jpg", ".jpeg", ".webp")
# Static files the preview server may hand out from the theme dir (never PHP or anything else).
SERVABLE_SUFFIXES = tuple(MIME)
DIVI_JS = ["js/scripts.min.js", "includes/builder/feature/dynamic-assets/assets/js/jquery.fitvids.js",
           "includes/builder/feature/dynamic-assets/assets/js/jquery.mobile.js",
           "includes/builder/feature/dynamic-assets/assets/js/easypiechart.js", "core/admin/js/common.js"]
JQUERY_CDN = "https://code.jquery.com/jquery-3.7.1.min.js"
_URL_RE = re.compile(r"url\((['\"]?)(?!data:|https?:|/|#)([^)'\"]+)\1\)")


def resolve_asset(theme: Path, rel: str) -> Optional[Path]:
    """The theme file for a /__divi/<rel> request, or None if it escapes the theme dir, isn't a
    regular file or isn't a static asset type."""
    root = Path(theme).resolve()
    try:
        f = (root / rel.lstrip("/")).resolve()
    except (OSError, ValueError):
        return None
    if root not in f.parents or not f.is_file() or f.suffix.lower() not in SERVABLE_SUFFIXES:
        return None
    return f


def mime_type(path: Path) -> str:
    return MIME.get(path.suffix.lower(), "application/octet-stream")


class Theme:
    """One Divi version's static files, with the asset delivery mode used for a render."""

    def __init__(self, path: Optional[Path], asset_base: Optional[str] = None, embed: bool = False):
        self.path = Path(path) if path else None
        # .../Divi-<version>/Divi (fetch_divi's cache layout)
        parent = self.path.parent.name if self.path else ""
        self.version = parent[len("Divi-"):] if parent.startswith("Divi-") else None
        self.asset_base = asset_base
        self.embed = embed and not asset_base
        self._gfonts = None
        self._static_css = None
        self._globals = None
        self._uris: dict = {}

    @classmethod
    def for_version(cls, version: Optional[str], keys_path: Optional[str] = None, **kw) -> "Theme":
        """Cache-first: an already cached version never touches the Elegant Themes API. keys_path
        is only used if a download is actually needed (see fetch_divi.ensure_divi). The default is the newest
        cached Divi 4: this renderer reproduces Divi 4 only, so a cached Divi 5 is never picked."""
        version = version or fetch_divi.newest_cached(major=4) or "latest"
        path = fetch_divi.theme_dir(version) if version != "latest" else None
        return cls(path or fetch_divi.ensure_divi(version, keys_path=keys_path), **kw)

    # -- files
    def file(self, rel: str) -> Optional[Path]:
        p = self.path / rel if self.path else None
        return p if p and p.is_file() else None

    def data_uri(self, rel: str) -> Optional[str]:
        if rel not in self._uris:
            p = self.file(rel)
            self._uris[rel] = (f"data:{mime_type(p)};base64,{base64.b64encode(p.read_bytes()).decode()}"
                               if p else None)
        return self._uris[rel]

    def url(self, rel: str) -> str:
        """How the page references a theme file in the current delivery mode."""
        if self.asset_base:
            return self.asset_base + rel
        if self.embed and rel.lower().endswith(EMBED_SUFFIXES):
            return self.data_uri(rel) or rel
        return rel

    def read_text(self, rel: str) -> str:
        p = self.file(rel)
        return p.read_text(encoding="utf-8", errors="replace") if p else ""

    # -- Divi data
    def static_css(self) -> str:
        """style-static.min.css with its relative url()s rewritten for the delivery mode."""
        if self._static_css is None:
            def fix(m):
                q, rel = m.group(1), m.group(2)
                clean = rel.split("?")[0].split("#")[0]
                if self.embed and clean.lower().endswith(EMBED_SUFFIXES):
                    uri = self.data_uri(clean)
                    if uri:
                        return f"url({uri})"
                return f"url({q}{self.asset_base or ''}{rel}{q})"
            self._static_css = _URL_RE.sub(fix, self.read_text("style-static.min.css"))
        return self._static_css

    def google_fonts(self) -> dict:
        if self._gfonts is None:
            self._gfonts = {}
            text = self.read_text("core/json-data/google-fonts.json")
            if text:
                for it in json.loads(text)["items"]:
                    self._gfonts[it["family"]] = it
        return self._gfonts

    def mask_svg(self, style: str, variant: str, ratio: str = "landscape") -> Optional[str]:
        src = self.read_text(f"includes/builder/feature/background-masks/mask/{style}.php")
        if not src:
            return None
        m = re.search(r"'%s'\s*=>\s*array\((.*?)\)," % re.escape(variant), src, re.S)
        if not m:
            return None
        m2 = re.search(r"'%s'\s*=>\s*'([^']*)'" % ratio, m.group(1))
        return m2.group(1) if m2 else None

    def global_settings(self) -> dict:
        """ET_Global_Settings' module defaults ('et_pb_gallery-hover_overlay_color' -> value) from
        includes/builder/class-et-global-settings.php: literal values and the $font_defaults-style
        helper arrays they reference (other expressions are skipped)."""
        if self._globals is None:
            src = self.read_text("includes/builder/class-et-global-settings.php")
            helpers = {name: dict(re.findall(r"'(\w+)'\s*=>\s*'([^']*)'", body))
                       for name, body in re.findall(r"\$(\w+)\s*=\s*array\((.*?)\);", src, re.S)}
            # Anything the regexes don't parse (other expressions, a missing file) is simply
            # absent or "", which _clear_global_defaults() treats as "no global default": it
            # degrades to a no-op, never to a wrong value being cleared.
            self._globals = {}
            for key, lit, var, sub in re.findall(
                    r"'(et_pb_\w+-\w+)'\s*=>\s*(?:'([^']*)'|\$(\w+)\['(\w+)'\])", src):
                self._globals.setdefault(key, lit if not var else helpers.get(var, {}).get(sub, ""))
        return self._globals

    def scripts(self) -> list:
        return [js for js in (self.read_text(r) for r in DIVI_JS) if js]


def find_jquery() -> Optional[Path]:
    """WordPress's jQuery from the Playground cache (Task 14), if one was downloaded."""
    root = fetch_divi.cache_root()
    for pattern in ("wordpress/*/wordpress/wp-includes/js/jquery/jquery.min.js",
                    "sites/*/wordpress/wp-includes/js/jquery/jquery.min.js"):
        hits = sorted(root.glob(pattern))
        if hits:
            return hits[-1]
    return None
