#!/usr/bin/env python3
"""Generate reference/modules/*.md and the design-family tables from the raw Divi schema dump.

Usage: generate_docs.py <raw_schema_dir> <skill_dir> [--notes <notes_dir>]
Exit 1 if any non-skip field would be left undocumented.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "Skill" / "divi-page-builder" / "scripts"))
from divi_schema import load_schema  # noqa: E402
from validate import validate_source  # noqa: E402

FAMILY_TOGGLES = {
    "background": "background", "margin_padding": "spacing", "border": "border", "box_shadow": "box-shadow",
    "filters": "filters", "transform": "transform", "animation": "animation", "position_fields": "position",
    "scroll_effects": "scroll-effects", "visibility": "visibility", "hover_transitions": "transitions",
    "conditions": "display-conditions", "classes": "css-id-and-classes", "custom_css": "custom-css",
    "width": "sizing", "text": "text", "attributes": "attributes",
}
FAMILY_TITLES = {"font": "Font", "button": "Button", "background": "Background", "spacing": "Spacing",
                 "border": "Border", "box-shadow": "Box shadow", "filters": "Filters", "transform": "Transform",
                 "animation": "Animation", "position": "Position", "scroll-effects": "Scroll effects",
                 "visibility": "Visibility", "transitions": "Transitions", "display-conditions": "Display conditions",
                 "css-id-and-classes": "CSS ID & classes", "custom-css": "Custom CSS", "sizing": "Sizing",
                 "text": "Text", "attributes": "Attributes"}
MEMBERSHIP = 0.5          # canonical field must appear in ≥50% of a family's instances
TAB_TITLES = {"general": "Content tab", "advanced": "Design tab", "custom_css": "Advanced tab"}
# Suffixes (relative to a font-derived prefix, e.g. "body", "header", "body_ul") that really are
# font/text-shaped. Kept narrow on purpose: a field like "button_bg_color" starts with a font
# prefix ("button", from "button_font") and shares its toggle, but "_bg_color" isn't a font
# suffix, so it must NOT be pulled into the font family (it belongs to the Button family instead).
# The body_ul_*/body_ol_*/body_quote_* extras are real fields confirmed against the raw schema
# (see research/divi-schema/modules/*.json) -- list/blockquote sub-styling that ships alongside
# the standard font fields under the same "body"/"header"-style prefix.
FONT_SUFFIXES = (
    "_font", "_font_size", "_letter_spacing", "_line_height", "_text_align", "_text_color",
    "_text_shadow_blur_strength", "_text_shadow_color", "_text_shadow_horizontal_length",
    "_text_shadow_style", "_text_shadow_vertical_length",
    "_ul_type", "_ul_position", "_ul_item_indent",
    "_ol_type", "_ol_position", "_ol_item_indent",
    "_quote_border_weight", "_quote_border_color",
)


def _real_fields(data):
    return {n: f for n, f in data["fields"].items() if f.get("type") != "skip"}


def _font_prefixes(fields):
    return {n[: -len("_font")]: f.get("toggle_slug") for n, f in fields.items() if f.get("type") == "font" and n.endswith("_font")}


def _button_prefixes(data):
    adv = data["module"].get("advanced_fields") or {}
    return list((adv.get("button") or {}).keys())


def _candidate(slug, data, name, f):
    toggle = f.get("toggle_slug") or ""
    # Button fields are checked first: a module's own button toggle(s) (from
    # advanced_fields.button) always win over the font-prefix check below, so button_font,
    # button_text_color, etc. join the Button family instead of leaking into Font.
    button_prefixes = _button_prefixes(data)
    if toggle in button_prefixes and toggle in name:
        return ("button", toggle, name.replace(toggle, "{p}", 1))
    for p, t in _font_prefixes(data["fields"]).items():
        if toggle == t and name.startswith(p + "_"):
            suffix = name[len(p):]
            if suffix in FONT_SUFFIXES:
                return ("font", p, "{p}" + suffix)
    if toggle in FAMILY_TOGGLES:
        return (FAMILY_TOGGLES[toggle], "", name)
    return None


def _choose_canonical_def(entries):
    """Pick one field definition to represent a canonical family field, deterministically:
    the definition that is most common among the contributing (slug, field_def) instances
    (compared as JSON with sort_keys=True), ties broken by the alphabetically-first
    contributing slug. Regenerating with modules in a different order always picks the same
    winner. If the contributing instances don't agree on a default value, flags that so the
    render can show "(varies)" instead of silently baking in one module's specific default."""
    keyed = [(slug, json.dumps(f, sort_keys=True), f) for slug, f in entries]
    counts = Counter(k for _, k, _ in keyed)
    best_slug, best_def = {}, {}
    for slug, k, f in keyed:
        if k not in best_slug or slug < best_slug[k]:
            best_slug[k] = slug
            best_def[k] = f
    best_key = min(counts, key=lambda k: (-counts[k], best_slug[k]))
    chosen = dict(best_def[best_key])
    defaults = {json.dumps(f.get("default"), sort_keys=True) for _, f in entries}
    if len(defaults) > 1:
        chosen["_default_varies"] = True
    return chosen


def classify(raw):
    slugs = sorted(raw)
    counts = defaultdict(Counter)
    instances = defaultdict(set)
    candidates = {}
    contributors = defaultdict(list)
    for slug in slugs:
        data = raw[slug]
        for name, f in sorted(_real_fields(data).items()):
            cand = _candidate(slug, data, name, f)
            candidates[(slug, name)] = cand
            if cand:
                fam, prefix, canon = cand
                counts[fam][canon] += 1
                instances[fam].add((slug, prefix))
                contributors[(fam, canon)].append((slug, f))
    families = {}
    for fam, counter in counts.items():
        n = len(instances[fam])
        families[fam] = {"canonical": {}, "instances": n}
        for canon, c in counter.items():
            if c >= MEMBERSHIP * n:
                families[fam]["canonical"][canon] = _choose_canonical_def(contributors[(fam, canon)])
    placement = {}
    for slug in slugs:
        data = raw[slug]
        placement[slug] = {}
        for name, f in sorted(_real_fields(data).items()):
            cand = candidates[(slug, name)]
            if cand and cand[2] in families[cand[0]]["canonical"]:
                placement[slug][name] = ("family", cand[0], cand[1], cand[2])
            else:
                placement[slug][name] = ("module", f.get("toggle_slug") or "")
    return placement, families


def _flags(f):
    return " ".join(x for x, k in (("R", "mobile_options"), ("H", "hover"), ("S", "sticky")) if f.get(k)) or "·"


def _truncation_note(n_total, slug):
    # Module pages know their own slug and can point straight at its schema file. Family-table
    # rows aren't specific to one module (that's the point of the family), so they get a
    # placeholder "<module>" -- naming a real module there would just bake that module's
    # specifics back into the shared table.
    target = f"scripts/schema/{slug}.json" if slug else "scripts/schema/<module>.json"
    return f" … ({n_total} options; full list in {target})"


def _values(f, slug=None):
    opts = f.get("options")
    if isinstance(opts, dict) and opts:
        keys = [str(k) for k in opts]
        shown = ", ".join(f"`{k}`" for k in keys[:15])
        return shown + (_truncation_note(len(keys), slug) if len(keys) > 15 else "")
    if isinstance(opts, list) and opts:
        shown = ", ".join(f"`{o}`" for o in opts[:15])
        return shown + (_truncation_note(len(opts), slug) if len(opts) > 15 else "")
    if f.get("allowed_units"):
        return "length: " + ", ".join(f.get("allowed_units")[:6]) + ("…" if len(f["allowed_units"]) > 6 else "")
    return {"color-alpha": "color", "font": "font string", "custom_margin": "spacing string",
            "custom_padding": "spacing string", "select_icon": "icon string", "upload": "URL",
            "tiny_mce": "HTML (between the tags)", "border-radius": "radius string"}.get(f.get("type"), "")


def _cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def _default(f):
    default = f.get("default", f.get("default_on_front", ""))
    # Some defaults are conditional on another field's value: [dependent_field, {preset: value}].
    # Dumping the raw Python repr reads as broken data, so name the dependency instead.
    if isinstance(default, list) and len(default) == 2 and isinstance(default[1], dict):
        default = f"depends on `{default[0]}`"
    # Family-table canonical defs are chosen from many contributing modules; if they don't all
    # agree on a default, say so instead of silently showing just the most common one as if it
    # were the only one.
    if f.get("_default_varies"):
        default = f"{default} (varies)".strip()
    return default


def _field_row(name, f, slug=None):
    return f"| {_cell(name)} | {_cell(f.get('type', ''))} | {_cell(_values(f, slug))} | {_cell(_default(f))} | {_flags(f)} | {_cell(f.get('label', ''))} |"


HEADER = "| attribute | type | values | default | R H S | label |\n|---|---|---|---|---|---|"


def minimal_example(slug, schema):
    mod = schema.module(slug)
    base = '_builder_version="%s" _module_preset="default"' % schema.divi_version
    def content_for(tag):
        m = schema.module(tag)
        return "<p>Example text.</p>" if m and m.fields.get("content", {}).get("type") == "tiny_mce" else ""

    content = content_for(slug)

    def leaf(tag):
        return f"[{tag} {base}]{content_for(tag)}[/{tag}]"

    def in_column(inner):
        return (f"[et_pb_section {base}][et_pb_row {base}][et_pb_column type=\"4_4\" {base}]"
                f"{inner}[/et_pb_column][/et_pb_row][/et_pb_section]")

    if slug == "et_pb_section":
        return in_column("")
    if slug in ("et_pb_row", "et_pb_column"):
        return in_column("")
    if slug in ("et_pb_row_inner", "et_pb_column_inner"):
        return (f"[et_pb_section specialty=\"on\" {base}][et_pb_column type=\"1_4\" {base}][/et_pb_column]"
                f"[et_pb_column type=\"3_4\" specialty_columns=\"3\" {base}][et_pb_row_inner {base}]"
                f"[et_pb_column_inner type=\"4_4\" saved_specialty_column_type=\"3_4\" {base}][/et_pb_column_inner]"
                f"[/et_pb_row_inner][/et_pb_column][/et_pb_section]")
    if mod.kind == "child":
        parent = schema.module(mod.parents[0])
        inner = f"[{mod.parents[0]} {base}]{leaf(slug)}[/{mod.parents[0]}]"
        return f"[et_pb_section fullwidth=\"on\" {base}]{inner}[/et_pb_section]" if parent.fullwidth else in_column(inner)
    body = f"[{slug} {base}]{leaf(mod.child) if mod.child else content}[/{slug}]"
    return f"[et_pb_section fullwidth=\"on\" {base}]{body}[/et_pb_section]" if mod.fullwidth else in_column(body)


def missing_family_fields(slug, raw, placement, families):
    """{(family, prefix): [attribute, …]} for every design family the module links: the family's
    canonical fields (prefix filled in) that this module does NOT have. A reader who follows the
    family link must not assume these exist here (e.g. et_pb_heading links Text but has no
    text_orientation; it aligns with title_text_align)."""
    present = defaultdict(set)
    for name in _real_fields(raw[slug]):
        place = placement[slug][name]
        if place[0] == "family":
            present[(place[1], place[2])].add(place[3])
    missing = {}
    for (fam, prefix), have in sorted(present.items()):
        names = sorted(c.replace("{p}", prefix) for c, d in families[fam]["canonical"].items() if d and c not in have)
        names = [n for n in names if n not in raw[slug]["fields"]]
        if names:
            missing[(fam, prefix)] = names
    return missing


def render_module(slug, raw, placement, families, schema, notes_dir):
    data = raw[slug]
    meta = data["module"]
    mod = schema.module(slug)
    fields = _real_fields(data)
    lines = [f"# {meta['name']} — {slug}", ""]
    rel = "structure element" if mod.kind == "structure" else mod.kind
    parents = ", ".join(f"`{p}`" for p in mod.parents) or ("fullwidth section" if mod.fullwidth else "column" if mod.kind == "module" else "—")
    lines += [f"- **Kind:** {rel}", f"- **Goes inside:** {parents}",
              f"- **Children:** {'`' + mod.child + '`' if mod.child else 'none'}",
              f"- **CSS selector:** `{meta.get('main_css_element') or ''}`", "",
              "## Minimal valid example", "", "```divi", minimal_example(slug, schema), "```", ""]
    by_tab = defaultdict(lambda: defaultdict(list))
    fam_use = defaultdict(set)
    for name, f in fields.items():
        place = placement[slug][name]
        if place[0] == "module":
            by_tab[f.get("tab_slug") or "general"][place[1]].append((name, f))
        else:
            fam_use[place[1]].add(place[2])
    toggles = meta.get("settings_modal_toggles") or {}
    for tab in ("general", "advanced", "custom_css"):
        if not by_tab.get(tab):
            continue
        lines += [f"## {TAB_TITLES[tab]}", ""]
        labels = (toggles.get(tab) or {}).get("toggles") or {}
        for toggle, rows in by_tab[tab].items():
            label = labels.get(toggle)
            title = label.get("title") if isinstance(label, dict) else label
            lines += [f"### {title or toggle or 'Other'} — `{toggle or '-'}`", "", HEADER]
            lines += [_field_row(n, f, slug) for n, f in sorted(rows)]
            lines.append("")
    if fam_use:
        lines += ["## Shared design families", "", "| family | prefix(es) | reference |", "|---|---|---|"]
        for fam in sorted(fam_use):
            prefixes = ", ".join(f"`{p}_`" for p in sorted(fam_use[fam]) if p) or "(none)"
            lines.append(f"| {FAMILY_TITLES.get(fam, fam)} | {prefixes} | [design-families.md#{fam}](../design-families.md#{fam}) |")
        lines.append("")
        missing = missing_family_fields(slug, raw, placement, families)
        if missing:
            lines += ["**Family fields not on this module.** These rows of a linked family's table do not exist "
                      "here (writing one is `E_UNKNOWN_ATTR`); use this module's own fields above instead.", ""]
            for (fam, prefix), names in missing.items():
                label = FAMILY_TITLES.get(fam, fam) + (f" (`{prefix}_`)" if prefix else "")
                lines.append(f"- {label}: " + ", ".join(f"`{n}`" for n in names))
            lines.append("")
    note = notes_dir / f"{slug}.md" if notes_dir else None
    if note and note.exists():
        lines += ["## Gotchas", "", note.read_text().strip(), ""]
    lines += ["R = responsive (`_tablet`, `_phone`, `_last_edited`), H = hover (`__hover`), S = sticky (`__sticky`). "
              "See [value-formats.md](../value-formats.md)."]
    return "\n".join(lines) + "\n"


def render_families(families):
    out = []
    for fam in sorted(families, key=lambda k: FAMILY_TITLES.get(k, k)):
        canon = {k: v for k, v in families[fam]["canonical"].items() if v}
        out += [f"## {FAMILY_TITLES.get(fam, fam)}", f'<a id="{fam}"></a>', "",
                f"Used by {families[fam]['instances']} module/prefix combinations. `{{p}}` = the prefix listed on each module page.", "",
                HEADER]
        out += [_field_row(n, f) for n, f in sorted(canon.items())]
        out.append("")
    return "\n".join(out)


def check_coverage(raw, placement, pages, families_text):
    """The real coverage check: not "did classify() place it" (it always does), but "does the
    field actually show up somewhere a reader can find it" -- as a row on its module's own
    rendered page, or as its canonical row in the rendered families table with that family
    linked from the module page. A field can be placed and still get silently dropped from the
    page (e.g. an unrecognized tab_slug means render_module never emits its section); this
    catches that instead of only checking the in-memory placement dict."""
    missing = []
    for slug in sorted(raw):
        page = pages[slug]
        for name in sorted(_real_fields(raw[slug])):
            place = placement[slug][name]
            if place[0] == "module":
                if f"| {_cell(name)} |" not in page:
                    missing.append((slug, name))
            else:
                fam, canon = place[1], place[3]
                if f"| {_cell(canon)} |" not in families_text or f"design-families.md#{fam}" not in page:
                    missing.append((slug, name))
    return missing


def main(raw_dir, skill_dir, notes_dir):
    raw_dir, skill_dir = Path(raw_dir), Path(skill_dir)
    notes_dir = Path(notes_dir) if notes_dir else None
    raw = {p.stem: json.loads(p.read_text()) for p in (raw_dir / "modules").glob("*.json")}
    schema = load_schema()
    placement, families = classify(raw)
    pages = {}
    for slug in sorted(raw):
        example = minimal_example(slug, schema)
        errors = [f for f in validate_source(example, schema) if f.level == "error"]
        if errors:
            print(f"{slug}: example fails validation: {[(e.code, e.attr) for e in errors]}", file=sys.stderr)
            return 1
        pages[slug] = render_module(slug, raw, placement, families, schema, notes_dir)
    families_text = render_families(families)
    missing = check_coverage(raw, placement, pages, families_text)
    if missing:
        print("UNDOCUMENTED FIELDS:", missing[:20], file=sys.stderr)
        return 1
    out = skill_dir / "reference" / "modules"
    out.mkdir(parents=True, exist_ok=True)
    rows = ["# Module index", "", "| slug | name | kind | goes inside | children | fields |", "|---|---|---|---|---|---|"]
    for slug in sorted(raw):
        (out / f"{slug}.md").write_text(pages[slug])
        mod = schema.module(slug)
        rows.append(f"| [{slug}]({slug}.md) | {raw[slug]['module']['name']} | {mod.kind} | "
                    f"{', '.join(mod.parents) or ('fullwidth section' if mod.fullwidth else 'column')} | {mod.child or ''} | {len(_real_fields(raw[slug]))} |")
    (out / "README.md").write_text("\n".join(rows) + "\n")
    fam_path = skill_dir / "reference" / "design-families.md"
    text = fam_path.read_text()
    begin, end = "<!-- BEGIN GENERATED FAMILIES -->", "<!-- END GENERATED FAMILIES -->"
    head, rest = text.split(begin, 1)
    _, tail = rest.split(end, 1)
    fam_path.write_text(head + begin + "\n" + families_text + "\n" + end + tail)
    print(f"wrote {len(raw)} module pages, {len(families)} families")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("raw_dir")
    ap.add_argument("skill_dir")
    ap.add_argument("--notes")
    a = ap.parse_args()
    sys.exit(main(a.raw_dir, a.skill_dir, a.notes))
