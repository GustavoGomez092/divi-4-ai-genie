"""Fallbacks for modules the Python preview doesn't render: a visible dashed block that still
renders its children, counted in the coverage report.

Two kinds, reported apart (page.coverage_report(), preview.py's summary and banner):
- SITE_DATA modules show the live site's own content (posts, projects, menus, comments, widgets,
  the current post). Neither preview has it: the --exact preview runs real Divi on a fresh
  WordPress with no posts, menus or media. The block says so and points to the WordPress draft
  preview (`needs_site_data`).
- Anything else is simply not ported to Python; the --exact preview renders it
  (`unsupported_modules`). After Task 27 that is Search and Login, whose forms need no site data.
"""
from __future__ import annotations

from ..base import FALLBACK, Module, base_classes, render_children
from ..values import esc

# module -> (name, what it shows from the live site)
SITE_DATA = {
    "et_pb_blog": ("Blog", "this site's posts"),
    "et_pb_portfolio": ("Portfolio", "this site's projects"),
    "et_pb_filterable_portfolio": ("Filterable Portfolio", "this site's projects and their categories"),
    "et_pb_fullwidth_portfolio": ("Fullwidth Portfolio", "this site's projects"),
    "et_pb_post_slider": ("Post Slider", "this site's posts"),
    "et_pb_fullwidth_post_slider": ("Fullwidth Post Slider", "this site's posts"),
    "et_pb_post_title": ("Post Title", "the current post's title, meta and featured image"),
    "et_pb_fullwidth_post_title": ("Fullwidth Post Title", "the current post's title, meta and featured image"),
    "et_pb_post_content": ("Post Content", "the current post's content (Theme Builder)"),
    "et_pb_fullwidth_post_content": ("Fullwidth Post Content", "the current post's content (Theme Builder)"),
    "et_pb_post_nav": ("Post Navigation", "links to the neighbouring posts"),
    "et_pb_comments": ("Comments", "the current post's comments"),
    "et_pb_sidebar": ("Sidebar", "the widgets of one of this site's widget areas"),
    "et_pb_menu": ("Menu", "one of this site's WordPress menus"),
    "et_pb_fullwidth_menu": ("Fullwidth Menu", "one of this site's WordPress menus"),
}
STYLE = "outline:2px dashed {c};padding:12px;font:12px/1.4 monospace;color:{c}"


class Unsupported(Module):
    def render(self):
        tag = self.node.tag
        base_classes(self)
        inner = render_children(self.node, self.ctx, self) if self.node.modules else esc(self.node.content[:200])
        if tag in SITE_DATA:
            self.ctx.count_site_data(tag)
            name, shows = SITE_DATA[tag]
            msg = (f"[{tag}] {name}: shows {shows}. Neither preview can show the live site's data (posts, menus, "
                   f"media, comments, widgets); check the WordPress draft preview.")
            return (f'<div class="{self.classname()} pp-site-data" style="{STYLE.format(c="#1d4ed8")}">'
                    f'{esc(msg)}{inner}</div>')
        self.ctx.count_unsupported(tag)
        msg = f"[{tag}] not rendered by the Python preview; run the preview with --exact to see real Divi."
        return (f'<div class="{self.classname()} pp-unsupported" style="{STYLE.format(c="#e11d48")}">'
                f'{esc(msg)}{inner}</div>')


FALLBACK[:] = [Unsupported]
