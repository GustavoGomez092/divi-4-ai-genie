#!/usr/bin/env python3
"""Generate reference/divi5/modules/*.md and the design-family tables of reference/divi5/design-families.md.

Usage: generate_docs5.py <raw_schema5_dir> <skill_dir> [--notes <notes_dir>]

The attribute data comes from the compiled schema (scripts/schema5, divi5_schema.load_schema5); the raw dump
(research/divi5-schema) only adds module titles, descriptions, CSS-slot labels and the Divi 4 -> Divi 5 field
map. One page per in-scope module (Schema5.in_scope), structure blocks included. Every page carries a minimal
example built with divi5_blocks.new_block; generation fails (exit 1) if an example has any validation finding,
or if the coverage check finds an attribute path that is neither listed on its module page nor covered by a
family table the page links to.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[3] / "Skill" / "divi-page-builder" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from divi5_blocks import new_block, render_block  # noqa: E402
from divi5_schema import load_schema5  # noqa: E402
from validate import validate_source  # noqa: E402

BEGIN, END = "<!-- BEGIN GENERATED -->", "<!-- END GENERATED -->"
GROUPS = ("innerContent", "decoration", "advanced", "meta")
GROUP_TITLES = {"innerContent": "Content", "decoration": "Design", "advanced": "Advanced",
                "meta": "Meta and block-level attributes"}
CATEGORY_TITLES = {"structure": "Structure blocks", "module": "Modules", "fullwidth-module": "Fullwidth modules",
                   "child-module": "Child modules"}
FAMILY_TITLES = {"box-shadow": "Box shadow", "disabled-on": "Disabled on", "email-service": "Email service",
                 "font-body": "Body font", "font-header": "Heading fonts", "font-label": "Label font",
                 "font-placeholder": "Placeholder font", "id-classes": "CSS ID & classes",
                 "inline-font": "Inline fonts", "spam-protection": "Spam protection", "z-index": "Z-index",
                 "accent-color": "Accent color", "admin-label": "Admin label"}
MAX_OPTIONS = 15
ROW_HEADER = ("| attribute | key | type | values | R | states | notes |\n"
              "|---|---|---|---|---|---|---|")
FAMILY_HEADER = "| key | type | values | R | states | notes |\n|---|---|---|---|---|---|"
LEGEND = (
    "**Reading the tables.** `attribute` is the dotted path to a responsive object in the block's JSON; `key` is the "
    "key inside its value (`—` = the value itself). So `title.innerContent` + key `text` is written "
    "`\"title\":{\"innerContent\":{\"desktop\":{\"value\":{\"text\":\"…\"}}}}`. **R** = responsive (a value per "
    "breakpoint: `desktop`, `tablet`, `phone`); `desktop` = desktop only. **states** = states allowed besides "
    "`value` (e.g. `hover`, `sticky`). Type grammars: [design-families.md#leaf-types](../design-families.md#leaf-types); "
    "the full value model: [value-formats.md](../value-formats.md).")
EXAMPLE_TEXT = "<p>Licensed, insured plumbers at your door in 60 minutes.</p>"


# ----------------------------------------------------------------------------- minimal examples

def _d(value):
    return {"desktop": {"value": value}}


def _ic(value):
    return {"innerContent": _d(value)}


ICON = {"unicode": "&#xe03b;", "type": "divi", "weight": "400"}
# Content for each example block, in Divi's attribute form. Values follow the Divi-converted and Divi AI
# fixtures (tests/fixtures/divi5); modules not listed get an empty (default) block.
SAMPLES = {
    "accordion-item": {"title": _ic("Do you pull permits?"),
                       "content": _ic("<p>Yes. We handle all permits and inspections.</p>")},
    "audio": {"audio": _ic("https://example.com/wp-content/uploads/2026/09/interview.mp3"),
              "title": _ic("Studio interview"), "artistName": _ic("Jordan Wells")},
    "before-after-image": {"beforeImage": _ic({"src": "https://example.com/wp-content/uploads/2026/09/before.jpg"}),
                           "afterImage": _ic({"src": "https://example.com/wp-content/uploads/2026/09/after.jpg"})},
    "blurb": {"title": _ic({"text": "Fast response"}),
              "imageIcon": _ic({"useIcon": "on", "icon": ICON}),
              "content": _ic("<p>A licensed plumber at your door within the hour.</p>")},
    "button": {"button": _ic({"text": "Call now", "linkUrl": "tel:+13055550100"})},
    "circle-counter": {"title": _ic("Uptime"), "number": _ic("99")},
    "code": {"content": _ic("<div class=\"notice\">Open this <strong>Saturday</strong></div>")},
    "contact-field": {"fieldItem": {"innerContent": _d("Name"),
                                    "advanced": {"id": _d("Name"), "type": _d("input")}}},
    "contact-form": {"title": _ic("Request a site visit")},
    "countdown-timer": {"title": _ic("Open house"), "content": {"advanced": {"dateTime": _d("2026-10-02 10:00")}}},
    "counter": {"title": _ic("Kitchens"), "barProgress": _ic("80")},
    "cta": {"title": _ic("Need a plumber today?"),
            "content": _ic("<p>Same-day service across Miami-Dade.</p>"),
            "button": _ic({"text": "Book a visit", "linkUrl": "/contact/"})},
    "fullwidth-code": {"content": _ic("<div class=\"banner\">Open house this <strong>Saturday</strong></div>")},
    "fullwidth-header": {"title": _ic("Emergency plumbing in Miami"),
                         "subhead": _ic("Licensed, insured, on call 24/7"),
                         "buttonOne": _ic({"text": "Call now", "linkUrl": "tel:+13055550100"})},
    "fullwidth-image": {"image": _ic({"src": "https://example.com/wp-content/uploads/2026/09/crew.jpg",
                                      "alt": "Our crew on a job site"})},
    "fullwidth-map": {"map": _ic({"address": "Miami, FL", "lat": 25.7617, "lng": -80.1918, "zoom": 11})},
    "heading": {"title": {"innerContent": _d("Our services"),
                          "decoration": {"font": {"font": _d({"headingLevel": "h2"})}}}},
    "icon": {"icon": _ic(ICON)},
    "icon-list-item": {"content": _ic("Free estimates")},
    "image": {"image": _ic({"src": "https://example.com/wp-content/uploads/2026/09/team.jpg",
                            "alt": "Our team on a job site"})},
    "link": {"content": _ic("Read the case study")},
    "map": {"map": _ic({"address": "Miami, FL", "lat": 25.7617, "lng": -80.1918, "zoom": 11})},
    "map-pin": {"title": _ic("Downtown office"), "pin": _ic({"lat": 25.7617, "lng": -80.1918})},
    "number-counter": {"title": _ic("Jobs completed"), "number": _ic("9500")},
    "pricing-table": {"title": _ic("Basic"), "price": _ic("99"),
                      "currencyFrequency": _ic({"currency": "$", "per": "mo"}),
                      "content": _ic("+Design consult\n+Permit handling\n-3D renderings"),
                      "button": _ic({"text": "Choose", "linkUrl": "/contact/"})},
    "signup": {"title": _ic("Seasonal tips")},
    "signup-custom-field": {"fieldItem": _ic("Company")},
    "slide": {"title": _ic("Spring tune-up"), "content": _ic("<p>Book before May 1.</p>"),
              "button": _ic({"text": "Book now", "linkUrl": "/contact/"})},
    "social-media-follow-network": {"socialNetwork": _ic({"title": "facebook", "label": "facebook",
                                                          "link": "https://facebook.com/example"})},
    "tab": {"title": _ic("Residential"), "content": _ic("<p>Homes and condos.</p>")},
    "table-of-contents": {"title": _ic("On this page")},
    "team-member": {"name": _ic("Jordan Wells"), "position": _ic("Founder"),
                    "content": _ic("<p>Started the company in 2009.</p>")},
    "testimonial": {"author": _ic("Ravi N."), "jobTitle": _ic("Office manager"),
                    "content": _ic("<p>They fixed our pipes without closing the office for a day.</p>")},
    "text": {"content": _ic(EXAMPLE_TEXT)},
    "timeline-item": {"title": _ic("Founded"), "date": _ic("2009"),
                      "content": _ic("<p>Two plumbers and one van.</p>")},
    "toggle": {"title": _ic("Do you pull permits?"),
               "content": _ic("<p>Yes. We handle all permits and inspections.</p>")},
    "tooltip": {"content": _ic("<p>Available 24/7</p>")},
    "video": {"video": _ic({"src": "https://example.com/wp-content/uploads/2026/09/walkthrough.mp4"})},
    "video-slider-item": {"video": _ic({"src": "https://example.com/wp-content/uploads/2026/09/process.mp4"})},
}
# The child shown inside a parent's example (a parent without an entry is shown empty).
EXAMPLE_CHILD = {"accordion": "accordion-item", "contact-form": "contact-field", "counters": "counter",
                 "fullwidth-map": "map-pin", "fullwidth-slider": "slide", "group": "text", "group-carousel": "group",
                 "icon-list": "icon-list-item", "map": "map-pin", "pricing-tables": "pricing-table",
                 "slider": "slide", "social-media-follow": "social-media-follow-network", "tabs": "tab",
                 "timeline": "timeline-item", "video-slider": "video-slider-item"}
LAYOUT_BLOCK = {"layout": _d({"display": "block"})}


class _Builder:
    def __init__(self, schema):
        self.schema = schema
        self.version = schema.meta["divi_version"]

    def block(self, name, attrs=None, children=None):
        attrs = json.loads(json.dumps(attrs or {}))
        attrs["builderVersion"] = self.version
        return new_block(name, attrs, children)

    def structural(self, name, advanced=None, children=None):
        module = {}
        if advanced:
            module["advanced"] = {k: _d(v) for k, v in advanced.items()}
        module["decoration"] = LAYOUT_BLOCK
        return self.block(name, {"module": module}, children)

    def module(self, short):
        child = EXAMPLE_CHILD.get(short)
        return self.block(short, SAMPLES.get(short), [self.module(child)] if child else None)

    def in_column(self, blocks):
        col = self.structural("column", {"type": "4_4"}, blocks)
        row = self.structural("row", {"columnStructure": "4_4"}, [col])
        return self.structural("section", None, [row])

    def fullwidth(self, blocks):
        return self.structural("section", {"type": "fullwidth"}, blocks)

    def specialty(self, blocks):
        inner_col = self.structural("column-inner", {"type": "4_4", "savedSpecialtyColumnType": "3_4"}, blocks)
        inner_row = self.structural("row-inner", {"columnStructure": "4_4"}, [inner_col])
        side = self.structural("column", {"type": "1_4"}, [self.module("text")])
        main = self.structural("column", {"type": "3_4", "specialtyColumns": "3"}, [inner_row])
        return self.structural("section", {"type": "specialty"}, [side, main])

    def place(self, block):
        """Wrap a (module) block in the smallest valid section for its category."""
        mod = self.schema.module(block.name)
        if mod.category == "fullwidth-module":
            return self.fullwidth([block])
        return self.in_column([block])


def _example_tree(short: str, schema):
    """The top block (a section) of the example for divi/<short>: the block in the smallest legal context."""
    b = _Builder(schema)
    if short in ("section", "row", "column"):
        return b.in_column([b.module("text")])
    if short in ("row-inner", "column-inner"):
        return b.specialty([b.module("text")])
    mod = schema.module(short)
    if mod.category == "child-module":
        parents = [p for p in mod.parents if schema.module(p).category != "fullwidth-module"] or mod.parents
        parent = parents[0][5:]
        return b.place(b.block(parent, SAMPLES.get(parent), [b.module(short)]))
    return b.place(b.module(short))


def minimal_example(short: str, schema) -> str:
    """A canonical section showing divi/<short> (main() fails generation if it has any validation finding)."""
    return render_block(_example_tree(short, schema))


def example_block_attrs(short: str, schema) -> dict:
    """The attributes of the page's own block inside its minimal example (for the formatted view)."""
    stack = [_example_tree(short, schema)]
    while stack:
        block = stack.pop(0)
        if block.name == f"divi/{short}":
            return block.attrs
        stack.extend(block.blocks)
    raise ValueError(f"divi/{short} is not in its own example")


# ----------------------------------------------------------------------------- tables

def _cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _code(text) -> str:
    text = str(text)
    return f"`` {text} ``" if "`" in text else f"`{text}`"


def _values(leaf) -> str:
    opts = leaf.get("options")
    if opts:
        shown = ", ".join(_code(o) for o in opts[:MAX_OPTIONS])
        if len(opts) > MAX_OPTIONS:
            shown += f" … ({len(opts)} options; full list in scripts/schema5)"
        return ("list of: " if leaf.get("multiple") else "") + shown
    if leaf.get("units"):
        return "units: " + ", ".join(leaf["units"])
    if leaf.get("open"):
        return "object (other keys accepted)"
    return ""


def _states(leaf) -> str:
    extra = [s for s in leaf["states"] if s != "value"]
    return ", ".join(extra) if extra else "·"


def _bp(leaf) -> str:
    out = "R" if leaf.get("bp", True) else "desktop"
    if leaf.get("breakpoints_extra"):
        out += " + " + ", ".join(leaf["breakpoints_extra"])
    return out


def _leaf_cells(leaf, notes) -> str:
    return (f"{_cell(leaf['type'])} | {_cell(_values(leaf))} | {_cell(_bp(leaf))} | {_cell(_states(leaf))} | "
            f"{_cell(notes)}")


def _key(sub: str) -> str:
    return _code(sub) if sub else "—"


def _note(leaf, d4_names) -> str:
    parts = []
    if d4_names:
        parts.append("D4 " + ", ".join(_code(n) for n in d4_names))
    note = leaf.get("note", "")
    if note and not (d4_names and ("Divi 4" in note or "D4" in note)):
        parts.append(note)
    return "; ".join(parts)


def d4_field_map(raw_module: dict) -> dict:
    """{(attr path, key): [Divi 4 field names]} from the conversion attributeMap (`a.b.*.key`)."""
    out = defaultdict(list)
    for d4, target in ((raw_module.get("conversion") or {}).get("attributeMap") or {}).items():
        if not isinstance(target, str):
            continue
        attr, _, sub = target.partition(".*")
        out[(attr, sub.lstrip("."))].append(d4)
    return {k: sorted(v)[:3] for k, v in out.items()}


def group_of(path: str) -> str:
    """innerContent / decoration / advanced / meta: the first group segment of an attribute path."""
    for seg in path.split("."):
        if seg in GROUPS:
            return seg
    return "meta"


def family_title(fam: str) -> str:
    return FAMILY_TITLES.get(fam, fam.replace("-", " ").capitalize())


def family_suffix(schema, fam: str, prefix: str) -> str:
    key = schema.families[fam]["key"]
    return f"{key}.{prefix}" if prefix else key


def _prefix_heading(schema, fam: str, prefix: str) -> str:
    return f"### `….{family_suffix(schema, fam, prefix)}`"


# ----------------------------------------------------------------------------- module pages

def _headings_line(mod) -> str:
    parts = []
    for path, value in sorted(mod.defaults.items()):
        level = ((value.get("desktop") or {}).get("value") or {})
        level = level.get("headingLevel") if isinstance(level, dict) else None
        if level and path.endswith(".decoration.font.font"):
            parts.append(f"`{path}` → `headingLevel` defaults to `{level}`")
    if not parts:
        return ""
    return f"- **Headings:** {'; '.join(parts)}."


def _css_line(mod, raw_module) -> str:
    labels = {k: (v or {}).get("label") for k, v in ((raw_module.get("module") or {}).get("customCssFields") or {}).items()}
    slots = [f"`{s}`" + (f" ({labels[s]})" if labels.get(s) else "") for s in mod.css]
    return "- **CSS slots** (keys of the `css` attribute's value): " + (", ".join(slots) or "none")


def _defaults_block(mod) -> list:
    if not mod.defaults:
        return []
    lines = ["<details>", f"<summary>Render defaults ({len(mod.defaults)}): what Divi uses when an attribute is "
             "unset — don't repeat these</summary>", ""]
    for path, bps in sorted(mod.defaults.items()):
        vals = []
        for bp, states in bps.items():
            for st, v in (states or {}).items():
                label = bp if st == "value" else f"{bp} {st}"
                vals.append(f"{label} {_code(json.dumps(v, ensure_ascii=False, separators=(',', ':')))}")
        lines.append(f"- `{path}` — " + "; ".join(vals))
    lines += ["", "</details>", ""]
    return lines


def render_module(short: str, schema, raw_module: dict, notes_dir) -> str:
    name = f"divi/{short}"
    mod = schema.module(name)
    meta = raw_module.get("module") or {}
    title = meta.get("title") or short
    d4map = d4_field_map(raw_module)
    lines = [f"# {title} — {name}", ""]
    if meta.get("description"):
        lines += [meta["description"], ""]
    parents = ", ".join(f"`{p}`" for p in mod.parents) or "the page (`divi/placeholder`)"
    children = ", ".join(f"`{c}`" for c in mod.children or []) or "none"
    if mod.children and len(mod.children) > 20:
        children = (f"any module ({len(mod.children)} blocks, out-of-scope ones included; the in-scope list is "
                    "[README.md](README.md))")
    lines += [f"- **Block:** `{name}`" + (f" (Divi 4: `{mod.d4}`)" if mod.d4 else " (no Divi 4 equivalent)"),
              f"- **Category:** {mod.category} · **scope:** {mod.scope}",
              f"- **Goes inside:** {parents}",
              f"- **Children:** {children}"]
    heads = _headings_line(mod)
    if heads:
        lines.append(heads)
    lines += [_css_line(mod, raw_module), ""]
    lines += ["## Minimal valid example", "",
              "A complete section, in canonical block markup (validated when this page was generated):", "",
              "```divi5", minimal_example(short, schema), "```", "",
              f"The `{name}` block's attributes, formatted for reading only (write them escaped and on one line, as "
              "above):", "", "```json", json.dumps(example_block_attrs(short, schema), indent=2, ensure_ascii=False),
              "```", "", LEGEND, ""]
    by_group = defaultdict(lambda: {"inline": [], "family": []})
    for path in sorted(mod.attrs):
        spec = mod.attrs[path]
        by_group[group_of(path)]["family" if "family" in spec else "inline"].append(path)
    for group in GROUPS:
        rows = by_group.get(group)
        lines += [f"## {GROUP_TITLES[group]}", ""]
        if not rows:
            lines += ["None on this block.", ""]
            continue
        if rows["inline"]:
            if rows["family"]:
                lines += ["Module-specific:", ""]
            lines.append(ROW_HEADER)
            for path in rows["inline"]:
                for sub, leaf in sorted(schema.leaf_spec(mod.attrs[path]).items()):
                    lines.append(f"| `{path}` | {_key(sub)} | {_leaf_cells(leaf, _note(leaf, d4map.get((path, sub))))} |")
            lines.append("")
        if rows["family"]:
            lines += ["Shared families (in the linked family, the table whose heading ends like the attribute "
                      "lists its keys):", "", "| attribute | family |", "|---|---|"]
            for path in rows["family"]:
                spec = mod.attrs[path]
                fam, prefix = spec["family"], spec.get("prefix", "")
                extra = f" (+ {', '.join(spec['states_extra'])} states)" if spec.get("states_extra") else ""
                lines.append(f"| `{path}` | [{family_title(fam)}](../design-families.md#{fam}){extra} |")
            lines.append("")
    lines += _defaults_block(mod)
    note = Path(notes_dir) / f"{short}.md" if notes_dir else None
    if note and note.exists():
        lines += ["## Gotchas", "", note.read_text().strip(), ""]
    return "\n".join(lines).rstrip("\n") + "\n"


# ----------------------------------------------------------------------------- design families

def families_used(schema, names) -> dict:
    """{family: {prefix: sorted [(short, attr path)]}} over the given modules."""
    used = defaultdict(lambda: defaultdict(list))
    for n in names:
        for path, spec in schema.module(n).attrs.items():
            if "family" in spec:
                used[spec["family"]][spec.get("prefix", "")].append((n[5:], path))
    return used


def _table_key(table) -> str:
    return json.dumps(table, sort_keys=True)


DEDUPE_MIN_ROWS = 4    # smaller identical tables are repeated: a pointer would be longer than the table


def _canonical_tables(schema, used) -> dict:
    """{table json: (family, prefix)}: for tables shared by several family attributes, the one to print in full:
    the one most modules use (then by family and table name), so pointers lead to the common case."""
    best = {}
    for fam, prefixes in used.items():
        for prefix, rows in prefixes.items():
            table = schema.families[fam]["attrs"][prefix]
            if len(table) < DEDUPE_MIN_ROWS:
                continue
            key = _table_key(table)
            rank = (-len({m for m, _ in rows}), fam, prefix)
            if key not in best or rank < best[key][0]:
                best[key] = (rank, (fam, prefix))
    return {k: v[1] for k, v in best.items()}


def _examples(rows, limit=3) -> str:
    picks = sorted(rows, key=lambda r: (not r[1].startswith("module."), len(r[1]), r[1], r[0]))
    out, seen = [], set()
    for mod, path in picks:
        if path not in seen:
            seen.add(path)
            out.append(f"`{path}` ({mod})")
        if len(out) == limit:
            break
    return ", ".join(out)


def render_families(schema, names) -> str:
    used = families_used(schema, names)
    canonical = _canonical_tables(schema, used)
    out = ["## Leaf types", '<a id="leaf-types"></a>', "",
           "Every `type` in the module pages and the tables below is one of these value grammars.", "",
           "| type | grammar |", "|---|---|"]
    out += [f"| `{t}` | {_cell(g)} |" for t, g in sorted(schema.types.items())]
    out.append("")
    for fam in sorted(used, key=family_title):
        spec = schema.families[fam]
        modules = sorted({m for rows in used[fam].values() for m, _ in rows})
        out += [f"## {family_title(fam)}", f'<a id="{fam}"></a>', "",
                f"Group key `{spec['key']}` · used by {len(modules)} module(s) · e.g. "
                + _examples([r for rows in used[fam].values() for r in rows]), ""]
        if spec.get("_notes"):
            out += [f"> Schema notes: {spec['_notes']}", ""]
        for prefix in sorted(used[fam]):
            table = spec["attrs"][prefix]
            out += [_prefix_heading(schema, fam, prefix), ""]
            other = canonical.get(_table_key(table), (fam, prefix))
            if other != (fam, prefix):
                out += [f"Same keys as [{family_title(other[0])} → `….{family_suffix(schema, *other)}`]"
                        f"(#{other[0]}).", ""]
                continue
            out.append(FAMILY_HEADER)
            for sub, leaf in sorted(table.items()):
                out.append(f"| {_key(sub)} | {_leaf_cells(leaf, leaf.get('note', ''))} |")
            out.append("")
    return "\n".join(out).rstrip("\n")


# ----------------------------------------------------------------------------- coverage

def _family_sections(families_text: str) -> dict:
    """{family anchor: that family's section text} from the rendered families text."""
    sections = {}
    for chunk in families_text.split('<a id="')[1:]:
        anchor, _, body = chunk.partition('"></a>')
        sections[anchor] = body.split("\n## ", 1)[0]
    return sections


def coverage_gaps(schema, pages: dict, families_text: str) -> list:
    """[(short, attr path)] for every attribute of a paged module that a reader can't find: an inline attribute
    whose leaf rows are not all on its page, or a family attribute whose page row does not link its family,
    or whose family section lacks the table for its prefix."""
    sections = _family_sections(families_text)
    gaps = []
    for short, page in sorted(pages.items()):
        mod = schema.module(short)
        lines = page.splitlines()
        for path, spec in sorted(mod.attrs.items()):
            cell = f"| `{path}` |"
            rows = [l for l in lines if l.startswith(cell)]
            if "family" in spec:
                fam, prefix = spec["family"], spec.get("prefix", "")
                ok = (any(f"design-families.md#{fam})" in r for r in rows)
                      and _prefix_heading(schema, fam, prefix) in sections.get(fam, ""))
            else:
                ok = all(any(r.startswith(f"{cell} {_key(sub)} |") for r in rows)
                         for sub in schema.leaf_spec(spec))
            if not ok:
                gaps.append((short, path))
    return gaps


# ----------------------------------------------------------------------------- README and main

def render_readme(schema, names, raw) -> str:
    rows = ["# Divi 5 module index", "",
            "One page per block the skill writes. Each page has a validated minimal example, every attribute path "
            "with its value type, and links to the shared [design families](../design-families.md). Blocks not "
            "listed here (WooCommerce, integrations, Theme Builder and internal blocks) are out of scope: the "
            "validator warns `W5_OUT_OF_SCOPE`.", ""]
    by_cat = defaultdict(list)
    for n in names:
        by_cat[schema.module(n).category].append(n)
    for cat in ("structure", "module", "fullwidth-module", "child-module"):
        if not by_cat.get(cat):
            continue
        rows += [f"## {CATEGORY_TITLES[cat]}", "", "| block | name | Divi 4 | goes inside | children | attributes |",
                 "|---|---|---|---|---|---|"]
        for n in sorted(by_cat[cat]):
            mod = schema.module(n)
            title = ((raw.get(n[5:]) or {}).get("module") or {}).get("title") or n[5:]
            parents = ", ".join(p[5:] for p in mod.parents) or "page"
            kids = mod.children or []
            kids_cell = ", ".join(c[5:] for c in kids) if len(kids) <= 3 else f"{len(kids)} blocks (see page)"
            rows.append(f"| [{n}]({n[5:]}.md) | {title} | {mod.d4 or '—'} | {parents} | {kids_cell} | "
                        f"{len(mod.attrs)} |")
        rows.append("")
    return "\n".join(rows).rstrip("\n") + "\n"


def main(raw_dir, skill_dir, notes_dir=None) -> int:
    raw_dir, skill_dir = Path(raw_dir), Path(skill_dir)
    schema = load_schema5()
    names = [n for n in schema.names() if schema.in_scope(n)]
    raw = {}
    for n in names:
        path = raw_dir / "modules" / f"{n[5:]}.json"
        raw[n[5:]] = json.loads(path.read_text()) if path.is_file() else {}
    failed = False
    for n in names:
        findings = validate_source(minimal_example(n[5:], schema), fragment=True)
        if findings:
            print(f"{n}: example has findings: {[(f.level, f.code, f.attr) for f in findings]}", file=sys.stderr)
            failed = True
    if failed:
        return 1
    pages = {n[5:]: render_module(n[5:], schema, raw[n[5:]], notes_dir) for n in names}
    families_text = render_families(schema, names)
    gaps = coverage_gaps(schema, pages, families_text)
    if gaps:
        print(f"UNDOCUMENTED ATTRIBUTES ({len(gaps)}):", gaps[:20], file=sys.stderr)
        return 1
    out = skill_dir / "reference" / "divi5" / "modules"
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.md"):
        if stale.stem != "README" and stale.stem not in pages:
            stale.unlink()
    for short, text in pages.items():
        (out / f"{short}.md").write_text(text)
    (out / "README.md").write_text(render_readme(schema, names, raw))
    fam_path = skill_dir / "reference" / "divi5" / "design-families.md"
    head, rest = fam_path.read_text().split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    fam_path.write_text(head + BEGIN + "\n" + families_text + "\n" + END + tail)
    print(f"wrote {len(pages)} module pages, {len(families_used(schema, names))} families")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("raw_dir")
    ap.add_argument("skill_dir")
    ap.add_argument("--notes")
    a = ap.parse_args()
    sys.exit(main(a.raw_dir, a.skill_dir, a.notes))
