"""The cached Divi 5 theme: its static files (shared with the Divi 4 renderer's assets.Theme: static CSS, Google
Fonts list, data: URI embedding, /__divi/ URLs) plus the per-module metadata Divi 5 keeps as JSON next to its
Visual Builder sources, read at runtime and never copied into the repo:

- module.json: every element's selector, and the styleProps (important flags, propertySelectors) its
  ElementStyle call uses;
- module-default-printed-style-attributes.json: the values Divi's static CSS already prints, which the builder
  CSS leaves out;
- module-default-render-attributes.json: the defaults a module_styles merges before styling (the Button module).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import fetch_divi  # noqa: E402
from divi_render.assets import Theme  # noqa: E402  (shared static-file handling)

COMPONENTS = "includes/builder-5/visual-builder/packages/module-library/src/components"


class MissingDivi5(RuntimeError):
    pass


class Theme5(Theme):
    """A cached Divi 5 build: static files (see divi_render.assets.Theme) and module metadata."""

    def __init__(self, path, asset_base: Optional[str] = None, embed: bool = False):
        super().__init__(path, asset_base=asset_base, embed=embed)
        self._meta: dict = {}

    @classmethod
    def for_version(cls, version: Optional[str], keys_path: Optional[str] = None, **kw) -> "Theme5":
        """The newest cached Divi 5 by default (a cached Divi 4 is never picked). Cache-first: an already cached
        version never touches the Elegant Themes API; otherwise fetch_divi downloads it (credentials needed)."""
        version = version or fetch_divi.newest_cached(major=5) or "latest5"
        path = fetch_divi.theme_dir(version) if not version.startswith("latest") else None
        if path is None:
            path = fetch_divi.ensure_divi(version, keys_path=keys_path)
        theme = cls(path, **kw)
        if not theme.file(f"{COMPONENTS}/text/module.json"):
            raise MissingDivi5(f"{path} is not a Divi 5 theme (no {COMPONENTS}/text/module.json)")
        return theme

    def _json(self, rel: str) -> dict:
        text = self.read_text(rel)
        if not text:
            return {}
        data = json.loads(text)
        if isinstance(data, dict):
            data.pop("_comment", None)
        return data if isinstance(data, dict) else {}

    def module(self, slug: str) -> dict:
        """{"module": module.json, "printed": default printed style attrs, "defaults": default render attrs}."""
        if slug not in self._meta:
            base = f"{COMPONENTS}/{slug}"
            self._meta[slug] = {"module": self._json(f"{base}/module.json"),
                                "printed": self._json(f"{base}/module-default-printed-style-attributes.json"),
                                "defaults": self._json(f"{base}/module-default-render-attributes.json")}
        return self._meta[slug]
