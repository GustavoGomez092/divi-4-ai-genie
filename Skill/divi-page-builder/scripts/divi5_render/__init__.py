"""Pure-Python (stdlib) Divi 5 renderer: Divi 5 block markup in, full HTML preview page out.

    from divi5_render import render_page
    result = render_page(source, divi_version="5.13.1", tokens=tokens_dict, embed_assets=True)
    result.html, result.coverage

It re-implements Divi 5's front-end output for the supported modules (SUPPORTED_MODULES): the block tree walk
with order classes, markup copied from each module's render_callback, and a generic style engine (a port of
ElementStyle + Utils::get_statements) driven by the theme's own metadata: each module's module.json (element
selectors, styleProps important flags and propertySelectors) and its default printed/render attribute JSON,
read at runtime from the cached Divi 5 theme and never copied into the repo. Anything else renders as a visible
placeholder and is listed in the coverage report, with every attribute value the renderer does not honour; the
Playground preview (--exact) covers those.

Layout: values (attr access, variables, relative colours) · css (sheet, selectors, statement engine) ·
options (ElementStyle groups) · base (context, presets, Module::render) · structure (section/row/column + inner) ·
modules/ (one file per module family) · page (document shell, fonts, token seed) · coverage (key-level report) ·
meta (the cached theme, sharing divi_render.assets.Theme).

Research record: research/divi5/python-renderer-spike.md; fidelity: research/divi5/render-fidelity.md.
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

import divi5_blocks  # noqa: E402

from . import modules, structure  # noqa: E402,F401  (registers the handlers)
from .base import HANDLERS, Ctx, render_block  # noqa: E402
from .coverage import report  # noqa: E402
from .meta import MissingDivi5, Theme5  # noqa: E402
from .page import document  # noqa: E402

SUPPORTED_MODULES = frozenset(HANDLERS)

__all__ = ["render_page", "RenderResult", "SUPPORTED_MODULES", "theme_for", "MissingDivi5"]


@dataclass
class RenderResult:
    html: str
    coverage: dict = field(default_factory=dict)


@lru_cache(maxsize=16)
def theme_for(divi_version: Optional[str], asset_base: Optional[str] = None, embed: bool = False,
              keys_path: Optional[str] = None) -> Theme5:
    """One Theme5 per (version, delivery mode, keys_path): its static CSS, font list and module metadata are
    read once."""
    return Theme5.for_version(divi_version, asset_base=asset_base, embed=embed, keys_path=keys_path)


def render_builder(source: str, theme: Theme5, tokens: Optional[dict] = None):
    """(builder markup, builder CSS, ctx, parse problems) for Divi 5 block markup."""
    doc = divi5_blocks.parse(source)
    ctx = Ctx(theme, tokens)
    builder = "".join(render_block(n, ctx, {"index": i, "last": False})
                      for i, n in enumerate(doc.nodes) if isinstance(n, divi5_blocks.Block))
    return builder, ctx.css.text(), ctx, doc.problems


def render_page(source: str, divi_version: Optional[str] = None, tokens: Optional[dict] = None,
                title: str = "Preview", embed_assets: bool = False, asset_base: Optional[str] = None,
                keys_path: Optional[str] = None) -> RenderResult:
    """Renders Divi 5 block markup to a complete HTML document.

    divi_version: a cached Divi 5 build (default: the newest cached 5.x). tokens: the site's tokens.json (global
    colours for relative colours, and the design-system seed the Playground preview uses too).
    embed_assets: inline fonts/images of the static CSS as data: URIs (standalone files); asset_base: reference
    them under that URL prefix instead (a preview server's /__divi/). Never emits file:// URLs.
    """
    t0 = time.perf_counter()
    theme = theme_for(divi_version, asset_base, embed_assets, keys_path)
    builder, css, ctx, problems = render_builder(source, theme, tokens)
    t_render = time.perf_counter() - t0
    html = document(ctx, builder, css, title)
    cov = report(ctx)
    cov["stats"] = {"render_ms": round(t_render * 1000, 1), "total_ms": round((time.perf_counter() - t0) * 1000, 1),
                    "builder_css_bytes": len(css), "parse_problems": [p.message for p in problems],
                    "divi_version": theme.version}
    return RenderResult(html, cov)
