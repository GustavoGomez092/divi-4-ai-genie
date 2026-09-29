#!/usr/bin/env python3
"""Port a Divi 4 recipe's worked example to Divi 5 (maintainer tool; spec §3 decision 8, plan Task 16).

  python3 research/tools/divi5/port_recipe.py Skill/divi-page-builder/recipes/sections/hero-split.md
          [--out recipes/divi5/sections/hero-split.md] [--tokens recipes/divi5/sample-tokens.json]
          [--converted FILE] [--force]

1. Extract the Divi 4 recipe's ```divi worked example.
2. Convert it with Divi's own converter: research/tools/divi5/convert.php through WP-CLI on the local Divi 5
   site (tests/_paths.py LOCAL5_ENV). `--converted FILE` skips this and reads converter output from FILE.
3. Clean it (clean()): drop the divi/placeholder wrapper (recipes hold sections); on every block set
   `builderVersion` to the schema's Divi version, drop `locked`, drop `modulePreset` unless it names a preset
   in the tokens (["default"] is the site default anyway); drop values equal to the module's render
   defaults (heading levels excepted: a recipe states its h1/h2 outright) and empty-string values ("" means
   unset); keep `display: "block"` only on structure blocks, adding it where missing; replace literal colors,
   fonts and lengths with the tokens' `$variable()$` reference when a global color or variable has that exact
   value *and* is used in that role (its `roles`); give custom attribute rows fresh ids,
   uuid5(NAMESPACE_URL, "divi-genie/recipes/divi5/<recipe>/<n>").
4. Validate it (validate_source, fragment mode, against the tokens) and print the findings; any error makes the
   exit status 1 (the draft is still written, the findings in its comment, for the human pass to fix).
5. Write a draft recipes/divi5/sections/<name>.md: pointer to the shared recipe, structure tree, field-mapping
   and responsive stubs listing what the example sets, the canonical worked example, the Divi 5 checklist.
   An existing file is never overwritten without --force (it has had its human pass).

The draft is a starting point. The human pass then fixes awkward converter output, keeps only the attributes a
person would set, fills in the field mapping (token path per attribute) and checks the render.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "Skill" / "divi-page-builder"
sys.path.insert(0, str(SKILL / "scripts"))

import divi5_blocks as d5  # noqa: E402
from divi5_schema import load_schema5  # noqa: E402
from divi_checks_values import normalize_color  # noqa: E402
from validate import validate_source  # noqa: E402

CONVERT_PHP = Path(__file__).resolve().parent / "convert.php"
WP_LOCAL = ROOT / "research" / "tools" / "wp-local.sh"
LOCAL5_ENV = {"LOCAL_SITE_ID": "fTZ3hcgdI",
              "LOCAL_SITE_PATH": str(Path.home() / "Local Sites" / "divi-5-test" / "app" / "public")}
SAMPLE_TOKENS = SKILL / "recipes" / "divi5" / "sample-tokens.json"
EXAMPLE_RE = re.compile(r"^```divi\n(.*?)^```", re.S | re.M)
STRUCTURE = ("divi/section", "divi/row", "divi/column", "divi/row-inner", "divi/column-inner")
LAYOUT = {"desktop": {"value": {"display": "block"}}}
KEEP_DEFAULTS = {"headingLevel"}          # stated outright even where it is the default
UUID_PREFIX = "divi-genie/recipes/divi5/"


# ---------------------------------------------------------------------------------------------- 1. extract

def extract_example(markdown: str) -> str:
    """The Divi 4 recipe's worked example (its last ```divi block, under "## Worked example")."""
    part = markdown.split("## Worked example", 1)[-1]
    blocks = EXAMPLE_RE.findall(part) or EXAMPLE_RE.findall(markdown)
    if not blocks:
        raise ValueError("no ```divi worked example found")
    return blocks[-1].strip()


# ---------------------------------------------------------------------------------------------- 2. convert

def convert(shortcode: str, timeout: int = 180) -> str:
    """Divi's own Divi 4 → Divi 5 conversion (convert.php through WP-CLI on the local Divi 5 site)."""
    with tempfile.TemporaryDirectory() as tmp:
        src, out = Path(tmp) / "in.txt", Path(tmp) / "out.html"
        src.write_text(shortcode, encoding="utf-8")
        env = dict(os.environ, **LOCAL5_ENV)
        run = subprocess.run([str(WP_LOCAL), "eval-file", str(CONVERT_PHP), str(src), str(out)],
                             capture_output=True, text=True, env=env, timeout=timeout)
        if run.returncode != 0 or not out.exists():
            raise RuntimeError(f"convert.php failed ({run.returncode}): {run.stderr.strip() or run.stdout.strip()}")
        return out.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------------------------- 3. clean

def _ref(kind: str, name: str) -> str:
    return "$variable(" + json.dumps({"type": kind, "value": {"name": name, "settings": {}}},
                                     separators=(",", ":")) + ")$"


def _replacements(tokens: dict):
    """(colors, others): {normalized color: [(gcid, roles)]}, {value: [(gvid, roles, kind)]} from the tokens.
    Only ids with recorded roles: an id the sampled pages never used in a role gives no evidence of one."""
    colors, others = {}, {}
    for gcid, entry in ((tokens.get("colors") or {}).get("global") or {}).items():
        value, roles = (entry or {}).get("value"), (entry or {}).get("roles") or []
        if isinstance(value, str) and roles:
            colors.setdefault(normalize_color(value), []).append((gcid, set(roles)))
    for gvid, entry in (tokens.get("variables") or {}).items():
        value, roles = (entry or {}).get("value"), (entry or {}).get("roles") or []
        if isinstance(value, str) and roles and entry.get("kind") in ("numbers", "fonts"):
            others.setdefault(value.strip(), []).append((gvid, set(roles)))
    return colors, others


def _role_match(entries, role):
    for name, roles in entries:
        if role in roles or any(role.startswith(r + ".") for r in roles):
            return name
    return None


def _swap(value, role: str, ltype: str, colors: dict, others: dict):
    """The reference replacing one literal leaf value (or a structured value's string members), else value."""
    if isinstance(value, dict):
        return {k: _swap(v, role, ltype, colors, others) for k, v in value.items()}
    if not isinstance(value, str) or not value or "$variable(" in value:
        return value
    if ltype == "color":
        name = _role_match(colors.get(normalize_color(value), ()), role)
        return _ref("color", name) if name else value
    name = _role_match(others.get(value.strip(), ()), role)
    return _ref("content", name) if name else value


def _set_path(root: dict, keys: list, value) -> None:
    cur = root
    for k in keys[:-1]:
        cur = cur[k]
    cur[keys[-1]] = value


def _references(block, mod, colors: dict, others: dict) -> None:
    for attr, bp, st, value in list(d5.iter_leaves(block.attrs)):
        if bp is None:
            continue
        for res, v in mod.walk_value(attr, bp, st, value):
            if res.status != "ok" or res.leaf is None:
                continue
            ltype = res.leaf.get("type")
            if ltype not in ("color", "font-family", "length", "spacing", "radius"):
                continue
            role = (res.attr_path or attr) + (f".{res.sub_path}" if res.sub_path else "")
            new = _swap(v, role, ltype, colors, others)
            if new != v:
                keys = attr.split(".") + [bp, st] + (res.sub_path.split(".") if res.sub_path else [])
                _set_path(block.attrs, keys, new)


def _strip_defaults(value, default):
    """value with every key equal to the render default removed (None when nothing is left)."""
    if isinstance(value, dict) and isinstance(default, dict):
        out = {}
        for k, v in value.items():
            if k in default and k not in KEEP_DEFAULTS:
                v = _strip_defaults(v, default[k])
                if v is None:
                    continue
            out[k] = v
        return out or None
    return None if value == default else value


def _drop_defaults(block, mod) -> None:
    for attr, bps in (mod.defaults or {}).items():
        holder = d5.get_attr(block, attr, None, None)
        if not isinstance(holder, dict):
            continue
        for bp, states in bps.items():
            for st, default in (states or {}).items():
                if bp in holder and isinstance(holder[bp], dict) and st in holder[bp]:
                    kept = _strip_defaults(holder[bp][st], default)
                    if kept is None:
                        del holder[bp][st]
                    else:
                        holder[bp][st] = kept


def _drop_empty(node, top: bool = True):
    """Remove "" leaves ("" means unset) and the empty objects left behind; content (innerContent) and the
    block-level keys are kept as they are."""
    if not isinstance(node, dict):
        return node
    out = {}
    for k, v in node.items():
        if k == "innerContent" or (top and k in ("builderVersion", "modulePreset", "groupPreset")):
            out[k] = v
            continue
        if isinstance(v, dict):
            v = _drop_empty(v, False)
            if not v:
                continue
        elif v == "":
            continue
        out[k] = v
    return out


def _fresh_row_ids(block, recipe: str, counter: list) -> None:
    holder = d5.get_attr(block, "module.decoration.attributes", None, None)
    for states in (holder or {}).values() if isinstance(holder, dict) else ():
        for value in (states or {}).values():
            for row in (value or {}).get("attributes") or [] if isinstance(value, dict) else []:
                if isinstance(row, dict) and "id" in row:
                    row["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{UUID_PREFIX}{recipe}/{counter[0]}"))
                    counter[0] += 1


def _clean_block(block, recipe: str, tokens: dict, schema, version: str, known: set, subs, counter) -> None:
    attrs = copy.deepcopy(block.attrs) if isinstance(block.attrs, dict) else {}
    attrs.pop("locked", None)
    attrs.pop("builderVersion", None)
    preset = attrs.pop("modulePreset", None)
    block.attrs = attrs
    mod = schema.module(block.name)
    if block.name in STRUCTURE:
        d5.set_attr(block, "module.decoration.layout", LAYOUT, None, None)
    elif d5.get_attr(block, "module.decoration.layout", None, None) == LAYOUT:
        del block.attrs["module"]["decoration"]["layout"]
    if mod is not None:
        _drop_defaults(block, mod)
        _references(block, mod, *subs)
    _fresh_row_ids(block, recipe, counter)
    block.attrs = _drop_empty(block.attrs)
    if preset and [p for p in preset if p != "default"] and set(preset) - {"default"} <= known:
        block.attrs["modulePreset"] = [p for p in preset if p != "default"]
    block.attrs["builderVersion"] = version
    block.dirty = True


def clean(converted: str, recipe: str, tokens: dict, schema=None) -> list:
    """The cleaned top-level blocks (sections) of converter output; see the module docstring, step 3."""
    schema = schema or load_schema5()
    version = schema.meta["divi_version"]
    doc = d5.parse(converted)
    if doc.problems:
        raise ValueError("converter output does not parse: " + "; ".join(p.message for p in doc.problems))
    nodes = [n for n in doc.nodes if isinstance(n, d5.Block)]
    if len(nodes) == 1 and nodes[0].name == "divi/placeholder":
        nodes = nodes[0].blocks
    known = {p.get("id") for lst in (tokens.get("presets") or {}).values() for p in lst or []}
    subs, counter = _replacements(tokens), [0]

    def rec(block):
        block.children = [c for c in block.children if isinstance(c, d5.Block)]   # converter whitespace
        _clean_block(block, recipe, tokens, schema, version, known, subs, counter)
        for child in block.children:
            rec(child)
    for n in nodes:
        rec(n)
    return nodes


# ---------------------------------------------------------------------------------------------- 5. draft

def _label(block) -> str:
    short = block.name[5:]
    admin = d5.get_attr(block, "module.meta.adminLabel")
    level = d5.get_attr(block, "title.decoration.font.font", default={}) or {}
    extra = f" ({admin})" if admin else (f" ({level['headingLevel']})" if level.get("headingLevel") else "")
    return short + extra


def structure_tree(sections: list) -> str:
    lines = []

    def rec(block, prefix, last, top):
        name = block.name
        if name in ("divi/section",):
            kind = d5.get_attr(block, "module.advanced.type")
            text = "section" + (f" {kind}" if kind else "") + (f" ({d5.get_attr(block, 'module.meta.adminLabel')})"
                                                               if d5.get_attr(block, "module.meta.adminLabel") else "")
        elif name in ("divi/row", "divi/row-inner"):
            text = f"{name[5:]} columnStructure \"{d5.get_attr(block, 'module.advanced.columnStructure')}\""
        elif name in ("divi/column", "divi/column-inner"):
            text = f"{name[5:]} {d5.get_attr(block, 'module.advanced.type')}: " + \
                " · ".join(_label(c) for c in block.blocks)
        else:
            text = _label(block)
        lines.append(("" if top else prefix + ("└─ " if last else "├─ ")) + text)
        if name in ("divi/column", "divi/column-inner"):
            return
        kids = block.blocks
        for i, c in enumerate(kids):
            rec(c, prefix + ("" if top else ("   " if last else "│  ")), i == len(kids) - 1, False)
    for s in sections:
        rec(s, "", True, True)
    return "\n".join(lines)


def _leaves(sections: list):
    for s in sections:
        for block, path, _parent in d5.parse(d5.render_block(s)).walk():
            for attr, bp, st, value in d5.iter_leaves(block.attrs):
                if bp is not None:
                    yield block.name, path, attr, bp, st, value


def draft(name: str, title: str, sections: list, findings: list) -> str:
    example = "".join(d5.render_block(s) for s in sections)
    rows = [f"| `{blk[5:]}` `{attr}` ({bp}{'' if st == 'value' else ' ' + st}) | "
            f"`{json.dumps(value, ensure_ascii=False)[:60]}` | TODO |"
            for blk, _p, attr, bp, st, value in _leaves(sections)
            if not attr.endswith("innerContent") and attr not in ("module.decoration.layout", "module.advanced.type",
                                                                  "module.advanced.columnStructure")]
    responsive = sorted({f"`{blk[5:]}` `{attr}` ({bp})" for blk, _p, attr, bp, _st, _v in _leaves(sections)
                         if bp in ("tablet", "phone")})
    notes = "\n".join(f"- {f.level} {f.code} {f.attr or ''}: {f.message}" for f in findings) or "- none"
    return f"""# {title} (Divi 5)

<!-- DRAFT from research/tools/divi5/port_recipe.py: do the human pass, then delete this comment.
Validation findings on the ported example:
{notes}
-->

Purpose, SEO notes and variations: [the shared recipe](../../sections/{name}.md). This page is its Divi 5
structure, field mapping and worked example ([README](../README.md)).

## Structure
```text
{structure_tree(sections)}
```

## Field mapping
| attribute | value in the example | token path |
|---|---|---|
{chr(10).join(rows)}

## Responsive rules

{chr(10).join('- ' + r for r in responsive) or '- TODO'}

## Worked example (sample-tokens.json)
```divi5
{example}
```

## Checklist
- [ ] `python3 scripts/validate.py section.html --tokens tokens.json --fragment` — 0 errors (a whole page without `--fragment`)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it**
- [ ] `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — only after that approval
- [ ] exactly one H1 on the page
- [ ] every image has alt text and a Media Library URL
"""


# ---------------------------------------------------------------------------------------------- main

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("recipe", help="a Divi 4 recipe, e.g. Skill/divi-page-builder/recipes/sections/hero-split.md")
    ap.add_argument("--out", help="default: recipes/divi5/<sections|pages>/<name>.md next to the recipe")
    ap.add_argument("--tokens", default=str(SAMPLE_TOKENS), help="Divi 5 tokens (default: the D5 sample tokens)")
    ap.add_argument("--converted", help="read converter output from this file instead of running convert.php")
    ap.add_argument("--force", action="store_true", help="overwrite an existing --out file")
    a = ap.parse_args(argv)
    recipe = Path(a.recipe)
    name = recipe.stem
    out = Path(a.out) if a.out else recipe.parent.parent / "divi5" / recipe.parent.name / recipe.name
    if out.exists() and not a.force:
        print(f"{out} exists (it may have had its human pass); pass --force to overwrite it", file=sys.stderr)
        return 1
    text = recipe.read_text(encoding="utf-8")
    title = (re.search(r"^# (.+)$", text, re.M) or [None, name])[1]
    tokens = json.loads(Path(a.tokens).read_text(encoding="utf-8"))
    converted = Path(a.converted).read_text(encoding="utf-8") if a.converted else convert(extract_example(text))
    sections = clean(converted, name, tokens)
    example = "".join(d5.render_block(s) for s in sections)
    findings = validate_source(example, tokens=tokens, fragment=True)
    for f in findings:
        print(f"{f.level} {f.code} {f.attr or ''}: {f.message}")
    errors = sum(1 for f in findings if f.level == "error")
    print(f"Summary: {errors} error(s), {len(findings) - errors} warning(s)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(draft(name, title, sections, findings), encoding="utf-8")
    print(f"wrote {out}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
