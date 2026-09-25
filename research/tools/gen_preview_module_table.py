#!/usr/bin/env python3
"""Generate the supported-modules table in the divi-page-builder skill's `reference/preview.md`
from `divi_render`'s handler registry (`divi_render.SUPPORTED_MODULES`), so the doc can never
silently drift from what the Python preview actually renders.

Usage: gen_preview_module_table.py [preview.md path]   (default: the skill's own reference/preview.md)

`tests/test_preview_docs.py` fails if `preview.md`'s table doesn't match what this script would
write; re-run this script to fix it.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[1] / "Skill" / "divi-page-builder"
SCRIPTS = SKILL / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import divi_render as dr  # noqa: E402
from divi_schema import load_schema  # noqa: E402

BEGIN = "<!-- BEGIN GENERATED MODULES: research/tools/gen_preview_module_table.py -->"
END = "<!-- END GENERATED MODULES -->"


def module_table() -> str:
    """The `| Module | Tag |` table, one row per tag in divi_render.SUPPORTED_MODULES, sorted by
    tag. The module name comes from the compact schema (falls back to the tag itself for a tag
    the schema doesn't know, which shouldn't happen for a registered handler)."""
    schema = load_schema()
    lines = ["| Module | Tag |", "|---|---|"]
    for tag in sorted(dr.SUPPORTED_MODULES):
        mod = schema.module(tag)
        name = mod.name if mod else tag
        lines.append(f"| {name} | `{tag}` |")
    return "\n".join(lines)


def main(preview_md: Path) -> int:
    text = preview_md.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        print(f"{preview_md}: missing {BEGIN!r} / {END!r} markers", file=sys.stderr)
        return 1
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    preview_md.write_text(head + BEGIN + "\n" + module_table() + "\n" + END + tail, encoding="utf-8")
    return 0


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else SKILL / "reference" / "preview.md"
    sys.exit(main(path))
