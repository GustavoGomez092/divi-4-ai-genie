"""Load the compact Divi schema and resolve attribute names to field definitions (stdlib only)."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

SCHEMA_DIR = Path(__file__).resolve().parent / "schema"
RESP_SUFFIXES = ("_tablet", "_phone", "_last_edited")
# (suffix, state flag on the base field, is the *_enabled toggle)
STATE_SUFFIXES = (("__hover_enabled", "hover", True), ("__sticky_enabled", "sticky", True),
                  ("__hover", "hover", False), ("__sticky", "sticky", False))
BG_ENABLE_RE = re.compile(r"^(?P<prefix>.+)_enable_(?:color|image|video_mp4|video_webm|pattern_style|mask_style)$")


@dataclass(frozen=True)
class Resolution:
    kind: str
    base: str
    field: Optional[dict]


class ModuleSchema:
    def __init__(self, data: dict, global_attrs: Dict[str, dict]):
        self.slug: str = data["slug"]
        self.name: str = data["name"]
        self.kind: str = data["kind"]
        self.fullwidth: bool = data.get("fullwidth", False)
        self.child: Optional[str] = data.get("child")
        self.parents: List[str] = data.get("parents", [])
        self.fields: Dict[str, dict] = data["fields"]
        self.extras: Dict[str, dict] = data.get("extras", {})
        self._global = global_attrs
        self._groups: Dict[tuple, bool] = {}

    def attribute_names(self) -> List[str]:
        return sorted(set(self.fields) | set(self.extras) | set(self._global))

    def _has_state_group(self, prefix: str, state: str) -> bool:
        key = (prefix, state)
        if key not in self._groups:
            self._groups[key] = any(n.startswith(prefix + "_") and f.get(state) for n, f in self.fields.items())
        return self._groups[key]

    def resolve(self, attr: str) -> Optional[Resolution]:
        if attr in self.fields:
            return Resolution("field", attr, self.fields[attr])
        if attr in self.extras:
            return Resolution("extra", attr, self.extras[attr])
        if attr in self._global:
            return Resolution("global", attr, self._global[attr])
        for suffix, state, is_toggle in STATE_SUFFIXES:
            if attr.endswith(suffix):
                base = attr[: -len(suffix)]
                f = self.fields.get(base)
                if f is not None and f.get(state):
                    return Resolution("state_toggle" if is_toggle else state, base, f)
                if is_toggle and self._has_state_group(base, state):
                    return Resolution("state_toggle", base, None)
                return None
        for suffix in RESP_SUFFIXES:
            if attr.endswith(suffix):
                inner = self.resolve(attr[: -len(suffix)])
                if inner is not None and (inner.kind == "bg_enable" or (inner.field or {}).get("responsive")):
                    return Resolution("responsive", inner.base, inner.field)
                return None
        m = BG_ENABLE_RE.match(attr)
        if m and any(f"{m['prefix']}_{s}" in self.fields for s in ("color", "use_color_gradient")):
            return Resolution("bg_enable", attr, {"type": "yes_no_button", "options": ["on", "off"]})
        return None


class Schema:
    def __init__(self, directory: Path):
        meta = json.loads((directory / "_meta.json").read_text())
        self.directory = directory
        self.divi_version: str = meta["divi_version"]
        self.global_attrs: Dict[str, dict] = meta["global_attrs"]
        self.column_structures: Dict[str, List[str]] = meta["column_structures"]
        self.column_types = {t for lst in self.column_structures.values() for s in lst for t in s.split(",")}
        self._aliases: Dict[str, str] = meta["aliases"]
        self.slugs: List[str] = [s for s in meta["modules"] if s not in self._aliases]
        self._known = set(meta["modules"])
        self._cache: Dict[str, ModuleSchema] = {}

    def module(self, slug: str) -> Optional[ModuleSchema]:
        if slug not in self._known:
            return None
        real = self._aliases.get(slug, slug)
        if real not in self._cache:
            data = json.loads((self.directory / f"{real}.json").read_text())
            self._cache[real] = ModuleSchema(data, self.global_attrs)
        return self._cache[real]


def load_schema(directory: Optional[Path] = None) -> Schema:
    return Schema(Path(directory) if directory else SCHEMA_DIR)
