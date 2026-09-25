#!/usr/bin/env python3
"""Compile the raw Divi schema dump into the compact schema used by the skill's scripts.

Usage: build_schema.py <raw_schema_dir> <extras.json> <out_dir>
"""
import json
import sys
from pathlib import Path

RESP_SUFFIXES = ("_tablet", "_phone", "_last_edited")
STRUCTURE = {"et_pb_section", "et_pb_row", "et_pb_row_inner", "et_pb_column", "et_pb_column_inner"}


def option_values(field: dict):
    opts = field.get("options")
    if isinstance(opts, list):
        return [str(o) for o in opts]
    if not isinstance(opts, dict) or not opts:
        return None
    if field.get("type") == "select_with_option_groups":
        return [str(k) for group in opts.values() if isinstance(group, dict) for k in group]
    return [str(k) for k in opts]


def compact_field(name: str, d: dict, raw: dict) -> dict:
    out = {"type": d.get("type", ""), "tab": d.get("tab_slug") or "general", "toggle": d.get("toggle_slug") or ""}
    if d.get("label"):
        out["label"] = d["label"]
    values = option_values(d)
    if values is not None:
        out["options"] = values
    if d.get("allowed_units"):
        out["units"] = list(d["allowed_units"])
    if d.get("default_unit"):
        out["default_unit"] = str(d["default_unit"])
    for key in ("default", "default_on_front"):
        if isinstance(d.get(key), (str, int, float)):
            out[key] = str(d[key])
    if d.get("mobile_options") or d.get("responsive") or f"{name}_tablet" in raw:
        out["responsive"] = True
    if d.get("hover"):
        out["hover"] = True
    if d.get("sticky"):
        out["sticky"] = True
    if d.get("composite_of"):
        out["composite_of"] = d["composite_of"]
    return out


def is_derived(name: str, raw: dict) -> bool:
    """A skip entry that only exists as a responsive variant of another field."""
    return any(name.endswith(s) and name[: -len(s)] in raw for s in RESP_SUFFIXES) and raw[name].get("type") == "skip"


def main(raw_dir: str, extras_path: str, out_dir: str) -> None:
    raw_dir, out = Path(raw_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    extras = json.loads(Path(extras_path).read_text())
    index = json.loads((raw_dir / "index.json").read_text())
    raw = {p.stem: json.loads(p.read_text()) for p in (raw_dir / "modules").glob("*.json")}
    parents: dict = {}
    for slug, data in raw.items():
        child = data["module"].get("child_slug")
        if child:
            parents.setdefault(child, []).append(slug)

    for slug, data in sorted(raw.items()):
        fields = data["fields"]
        kind = "structure" if slug in STRUCTURE else ("child" if slug in parents or data["module"].get("type") == "child" else "module")
        compact = {
            "slug": slug,
            "name": data["module"]["name"],
            "kind": kind,
            "fullwidth": bool(data["module"].get("fullwidth")),
            "child": data["module"].get("child_slug"),
            "parents": sorted(parents.get(slug, [])),
            "fields": {n: compact_field(n, d, fields) for n, d in fields.items() if not is_derived(n, fields)},
            "extras": extras["modules"].get(slug, {}),
        }
        (out / f"{slug}.json").write_text(json.dumps(compact, indent=1, sort_keys=True))

    meta = {
        "divi_version": index["divi_version"],
        "modules": sorted(raw) + sorted(extras["aliases"]),
        "aliases": extras["aliases"],
        "global_attrs": extras["global"],
        "column_structures": {
            "et_pb_row": option_values(raw["et_pb_row"]["fields"]["column_structure"]),
            "et_pb_row_inner": option_values(raw["et_pb_row_inner"]["fields"]["column_structure"]),
        },
    }
    (out / "_meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True))
    print(f"wrote {len(raw)} modules + _meta.json to {out}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
