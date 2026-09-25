"""Pure-Python (stdlib) Divi 4 renderer: page shortcode in, full HTML preview page out.

    from divi_render import render_page
    result = render_page(source, divi_version="4.27.9", embed_assets=True)
    result.html, result.coverage

It re-implements Divi's PHP front-end output for the supported modules (SUPPORTED_MODULES):
markup templates copied from each module's render() plus a generic CSS engine driven by the
compact schema's `advanced_fields`. Anything else renders as a visible placeholder and is listed
in the coverage report; the exact preview (scripts/preview/preview.mjs, real Divi on Playground)
covers those. Divi's static CSS, fonts and JS are read at runtime from the cached theme.

Layout: values (value parsing) · css (style sheet, selectors) · options + buttons (the design-option
engine) · base (context, Module, dispatch) · structure (section/row/column) · modules/ (one file
per module family) · page (document shell, coverage) · assets (theme files, delivery modes) ·
data (module definitions from the compact schema).
"""
from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from divi_shortcode import Node, parse  # noqa: E402

from . import modules, structure  # noqa: E402,F401  (registers the handlers)
from .assets import Theme  # noqa: E402
from .base import HANDLERS, Ctx, render_node  # noqa: E402
from .page import coverage_report, document  # noqa: E402

SUPPORTED_MODULES = frozenset(HANDLERS)

__all__ = ["render_page", "RenderResult", "SUPPORTED_MODULES", "theme_for"]


@dataclass
class RenderResult:
    html: str
    coverage: dict = field(default_factory=dict)


@lru_cache(maxsize=16)
def theme_for(divi_version: Optional[str], asset_base: Optional[str] = None, embed: bool = False) -> Theme:
    """One Theme per (version, delivery mode), so its static CSS and font list are read once."""
    return Theme.for_version(divi_version, asset_base=asset_base, embed=embed)


def render_page(source: str, divi_version: Optional[str] = None, title: str = "Preview", with_js: bool = True,
                embed_assets: bool = False, asset_base: Optional[str] = None) -> RenderResult:
    """Renders page content (Divi shortcodes) to a complete HTML document.

    divi_version: a cached Divi build (default: the newest cached one, else downloads latest).
    embed_assets: inline fonts/images as data: URIs (standalone files); asset_base: reference
    them under that URL prefix instead (the preview server's /__divi/). Never emits file:// URLs.
    """
    t0 = time.perf_counter()
    theme = theme_for(divi_version, asset_base, embed_assets)
    doc = parse(source)
    ctx = Ctx(theme)
    builder = "".join(render_node(n, ctx) for n in doc.nodes if isinstance(n, Node))
    builder_css = ctx.styles.text()
    t_render = time.perf_counter() - t0
    html = document(ctx, builder, builder_css, title, with_js)
    cov = coverage_report(ctx)
    cov["stats"] = {"render_ms": round(t_render * 1000, 1), "total_ms": round((time.perf_counter() - t0) * 1000, 1),
                    "builder_css_bytes": len(builder_css), "parse_problems": [p.message for p in doc.problems],
                    "divi_version": theme.version}
    return RenderResult(html, cov)
