"""Load the compiled Divi 5 schema (scripts/schema5/) and resolve block attribute paths to typed leaves (stdlib).

A module's `attrs` maps each responsive attribute path (what divi5_blocks.iter_leaves yields, e.g.
`title.decoration.font.font`) to either an inline leaf spec or a family reference `{"family", "prefix"}` into
schema5/families5.json. `Schema5.leaf_spec(spec)` turns either into a leaf table {sub_path: leaf}, where the
sub_path is the key path inside the attribute's value object ("" = the whole value). A leaf is
`{type, options?, units?, multiple?, open?, breakpoints_extra?, bp, states, note?}`; the types are listed in
families5.json `_types`. breakpoints_extra lists pseudo-breakpoints a leaf accepts besides _meta.breakpoints_all
(disabledOn: desktopAbove, tabletOnly).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

SCHEMA5_DIR = Path(__file__).resolve().parent / "schema5"
# Block-level bookkeeping keys that are not responsive module settings.
NONRESPONSIVE = frozenset({"builderVersion", "modulePreset", "groupPreset", "locked", "globalModule", "globalParent",
                           "nonconvertible", "shortcodeName"})
# Leaf types whose value is a structure of its own: a deeper key inside the value belongs to that leaf.
STRUCTURED = frozenset({"object", "json", "icon", "spacing", "radius", "gradient"})
OPAQUE = frozenset({"object", "json"})


@dataclass(frozen=True)
class Resolution5:
    status: str                 # ok | unknown_attr | bad_breakpoint | bad_state | nonresponsive
    leaf: Optional[dict]        # the leaf spec ({"type": ...}); for an object-valued attr, {"type": "object", "sub": {...}}
    attr_path: Optional[str]    # the responsive attribute path the value is stored under
    sub_path: Optional[str]     # path inside the attribute's value object (None = the whole value); a path deeper
                                # than a structured leaf (e.g. spacing padding.top) resolves to that leaf
    family: Optional[str]       # family name when the attribute is a family reference


def _has_children(table: Dict[str, dict], key: str) -> bool:
    if not key:
        return any(k for k in table)
    prefix = key + "."
    return any(k.startswith(prefix) for k in table)


def _children(table: Dict[str, dict], key: str) -> Dict[str, dict]:
    if not key:
        return {k: v for k, v in table.items() if k}
    prefix = key + "."
    return {k[len(prefix):]: v for k, v in table.items() if k.startswith(prefix)}


def _composite(table: Dict[str, dict]) -> dict:
    """Leaf spec for an object value made of the leaves in `table`."""
    states: List[str] = []
    extra: List[str] = []
    for leaf in table.values():
        states.extend(s for s in leaf["states"] if s not in states)
        extra.extend(b for b in leaf.get("breakpoints_extra", ()) if b not in extra)
    out = {"type": "object", "sub": table, "bp": any(leaf["bp"] for leaf in table.values()), "states": states}
    if extra:
        out["breakpoints_extra"] = extra
    return out


def _covering(table: Dict[str, dict], sub: str) -> Optional[Tuple[str, dict]]:
    """(key, leaf) typing `sub` inside a leaf table:
    - an exact entry;
    - an intermediate path with entries below it (an object; the result is a composite leaf);
    - the nearest ancestor entry whose value holds `sub`: a structured leaf (spacing, icon, radius, gradient), or
      an opaque object/json that has no declared sub-leaves or is marked open (then `sub` is typed json).
    """
    if sub in table and not _has_children(table, sub):
        return sub, table[sub]
    if _has_children(table, sub):  # an object value (a declared scalar beside it is handled by _walk)
        leaf = _composite(_children(table, sub))
        if sub in table:
            leaf["states"] = list(dict.fromkeys(table[sub]["states"] + leaf["states"]))
        return sub, leaf
    parts = sub.split(".")
    for i in range(len(parts) - 1, -1, -1):
        key = ".".join(parts[:i])
        anc = table.get(key)
        if anc is None:
            continue
        if anc["type"] in OPAQUE:
            if anc.get("open") or not _has_children(table, key):
                return sub, {"type": "json", "bp": anc["bp"], "states": anc["states"]}
            return None
        return (key, anc) if anc["type"] in STRUCTURED else None
    return None


class ModuleSchema5:
    def __init__(self, data: dict, schema: "Schema5"):
        self.name: str = data["name"]
        self.d4: Optional[str] = data.get("d4")
        self.category: Optional[str] = data.get("category")
        self.scope: str = data["scope"]
        self.children: Optional[List[str]] = data.get("children")
        self.parents: List[str] = data.get("parents") or []
        self.attrs: Dict[str, dict] = data["attrs"]
        self.css: List[str] = data.get("css") or []
        self.defaults: Dict[str, dict] = data.get("defaults") or {}
        self._schema = schema

    def _find(self, path: str) -> Optional[Tuple[str, Optional[str], str, dict, Optional[str]]]:
        """(attr_path, sub_path, key, leaf, family) for a dotted path: exact attr, else the longest attr prefix
        whose leaf table types the remainder."""
        if path in self.attrs:
            spec = self.attrs[path]
            table = self._schema.leaf_spec(spec)
            fam = spec.get("family")
            if set(table) == {""}:
                return path, None, "", table[""], fam
            hit = _covering(table, "")
            return (path, None, "", hit[1], fam) if hit else None
        parts = path.split(".")
        for i in range(len(parts) - 1, 0, -1):
            attr = ".".join(parts[:i])
            spec = self.attrs.get(attr)
            if spec is None:
                continue
            hit = _covering(self._schema.leaf_spec(spec), ".".join(parts[i:]))
            if hit:
                return attr, ".".join(parts[i:]), hit[0], hit[1], spec.get("family")
        return None

    def _status(self, leaf: dict, breakpoint: Optional[str], state: Optional[str]) -> str:
        if breakpoint is None or (breakpoint not in self._schema.breakpoints_all
                                  and breakpoint not in leaf.get("breakpoints_extra", ())):
            return "bad_breakpoint"
        if state is None or state not in leaf["states"]:
            return "bad_state"
        return "ok"

    def resolve(self, path: str, breakpoint: Optional[str], state: Optional[str]) -> Resolution5:
        """Resolve an attribute path (attrName, optionally followed by a sub-path inside its value)."""
        head = path.split(".", 1)[0]
        if breakpoint is None and (head in NONRESPONSIVE or head.startswith("_")):
            return Resolution5("nonresponsive", None, path, None, None)
        found = self._find(path)
        if found is None:
            return Resolution5("unknown_attr", None, None, None, None)
        attr, sub, _key, leaf, fam = found
        return Resolution5(self._status(leaf, breakpoint, state), leaf, attr, sub, fam)

    def walk_value(self, attr: str, breakpoint: Optional[str], state: Optional[str],
                   value) -> Iterator[Tuple[Resolution5, object]]:
        """Resolve every leaf inside one attribute value (one breakpoint/state). Yields (resolution, value) per
        typed leaf; unknown keys yield status unknown_attr with their sub_path. Descends into objects until the
        value reaches a leaf entry (a structured leaf such as spacing/icon, or a scalar)."""
        top = self.resolve(attr, breakpoint, state)
        if top.status != "ok" or top.attr_path != attr or top.leaf is None or top.leaf.get("type") != "object" \
                or "sub" not in top.leaf:
            yield top, value
            return
        spec = self.attrs[attr]
        table = self._schema.leaf_spec(spec)
        fam = spec.get("family")
        yield from self._walk(table, attr, "", value, breakpoint, state, fam)

    def _walk(self, table, attr, sub, value, breakpoint, state, fam):
        hit = _covering(table, sub) if sub else ("", _composite(_children(table, "")))
        if hit is None:
            yield Resolution5("unknown_attr", None, attr, sub or None, fam), value
            return
        key, leaf = hit
        if leaf["type"] == "object" and "sub" in leaf:
            if isinstance(value, dict) and value:
                for k, v in value.items():
                    yield from self._walk(table, attr, f"{sub}.{k}" if sub else str(k), v, breakpoint, state, fam)
                return
            if sub in table:  # a declared whole value (e.g. a plain string) beside the object form
                leaf = table[sub]
        yield Resolution5(self._status(leaf, breakpoint, state), leaf, attr, sub or None, fam), value


class Schema5:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.meta: dict = json.loads((self.directory / "_meta.json").read_text())
        families = json.loads((self.directory / "families5.json").read_text())
        self.families: Dict[str, dict] = families["families"]
        self.types: Dict[str, str] = families["_types"]
        self.breakpoints_all = frozenset(self.meta["breakpoints_all"])
        self.breakpoints_default = tuple(self.meta["breakpoints_default"])
        self._names = sorted(f"divi/{p.stem}" for p in self.directory.glob("*.json")
                             if not p.name.startswith("_") and p.name != "families5.json")
        self._modules: Dict[str, Optional[ModuleSchema5]] = {}
        self._tables: Dict[tuple, Dict[str, dict]] = {}

    def names(self) -> List[str]:
        """Every module name in the compiled schema (divi/<short>)."""
        return list(self._names)

    def module(self, name: str) -> Optional[ModuleSchema5]:
        """Module schema by `divi/<short>` or `<short>`; None when unknown."""
        full = name if name.startswith("divi/") else f"divi/{name}"
        if full not in self._modules:
            path = self.directory / f"{full[5:]}.json"
            if full[5:].startswith("_") or full == "divi/families5" or not path.is_file():
                self._modules[full] = None
            else:
                self._modules[full] = ModuleSchema5(json.loads(path.read_text()), self)
        return self._modules[full]

    def in_scope(self, name: str) -> bool:
        mod = self.module(name)
        return mod is not None and mod.scope in self.meta["scopes_in"]

    def leaf_spec(self, spec: dict) -> Dict[str, dict]:
        """The leaf table {sub_path: leaf} of one attrs entry ("" = the whole value)."""
        if "family" in spec:
            key = (spec["family"], spec.get("prefix", ""), tuple(spec.get("states_extra", ())))
            if key not in self._tables:
                table = self.families[spec["family"]]["attrs"][spec.get("prefix", "")]
                extra = spec.get("states_extra") or ()
                if extra:
                    table = {s: (dict(leaf, states=leaf["states"] + [x for x in extra if x not in leaf["states"]])
                                 if "hover" in leaf["states"] else leaf) for s, leaf in table.items()}
                self._tables[key] = table
            return self._tables[key]
        if "sub" in spec:
            return spec["sub"]
        return {"": spec}

    def leaf_types(self) -> set:
        """The leaf type names defined in families5.json `_types`."""
        return set(self.types)


_CACHE: Dict[Path, Schema5] = {}


def load_schema5(directory=None) -> Schema5:
    path = Path(directory) if directory else SCHEMA5_DIR
    if path not in _CACHE:
        _CACHE[path] = Schema5(path)
    return _CACHE[path]
