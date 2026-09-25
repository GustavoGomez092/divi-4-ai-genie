"""Module definitions for the renderer, from the skill's compact schema (scripts/schema/):
field defaults (default_on_front wins over default, as in PHP get_default_props()), and the
`render` block research/tools/build_schema.py (repo only) adds for this package: the module's main CSS
element and its advanced_fields (selectors, important flags and option defaults per design
family). Most of Divi's CSS output is driven by that configuration, not hand-written code.
"""
from __future__ import annotations

from functools import lru_cache

from divi_schema import load_schema


class ModuleDef:
    def __init__(self, fields: dict, render: dict):
        self.fields = fields
        self.advanced_fields = render.get("advanced_fields") or {}
        self.main_css = render.get("main_css") or "%%order_class%%"
        self.defaults = {}
        for k, f in fields.items():
            if "default_on_front" in f:
                self.defaults[k] = f["default_on_front"]
            elif "default" in f:
                self.defaults[k] = f["default"]

    def field_default(self, name: str) -> str:
        return self.fields.get(name, {}).get("default", "")


EMPTY = ModuleDef({}, {})


@lru_cache(maxsize=1)
def _schema():
    return load_schema()


@lru_cache(maxsize=None)
def module_def(slug: str) -> ModuleDef:
    mod = _schema().module(slug)
    return ModuleDef(mod.fields, mod.render) if mod else EMPTY
