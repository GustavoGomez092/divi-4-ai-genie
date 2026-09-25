"""Fallback for modules the Python preview doesn't render: a visible dashed placeholder that
still renders its children, and a count in the coverage report ("use --exact")."""
from __future__ import annotations

from ..base import FALLBACK, Module, base_classes, render_children
from ..values import esc


class Unsupported(Module):
    def render(self):
        self.ctx.count_unsupported(self.node.tag)
        base_classes(self)
        inner = render_children(self.node, self.ctx, self) if self.node.modules else esc(self.node.content[:200])
        return (f'<div class="{self.classname()} pp-unsupported" style="outline:2px dashed #e11d48;padding:12px;'
                f'font:12px/1.4 monospace;color:#e11d48">[{self.node.tag} not supported by the Python preview]{inner}</div>')


FALLBACK[:] = [Unsupported]
