"""Structural rules for Divi 4 pages: section → row → column → module, specialty and fullwidth sections,
parent/child module pairs."""
from __future__ import annotations

import re
from fractions import Fraction
from typing import Optional

from divi_shortcode import Node, Text

COLUMN_FOR_ROW = {"et_pb_row": "et_pb_column", "et_pb_row_inner": "et_pb_column_inner"}


def fraction(col_type: str) -> Optional[Fraction]:
    m = re.fullmatch(r"(\d+)_(\d+)", col_type or "")
    return Fraction(int(m.group(1)), int(m.group(2))) if m and int(m.group(2)) else None


def _child_path(path: str, kids: list, c) -> str:
    """Path for Node `c`, a member of `kids` (its parent's node.modules), following the same
    counting convention as Document.walk(): index = number of preceding siblings with the same tag."""
    idx = 0
    for k in kids:
        if k is c:
            break
        if k.tag == c.tag:
            idx += 1
    return f"{path} > {c.tag}[{idx}]" if path else f"{c.tag}[{idx}]"


def _stray_text(node, path, report):
    for child in node.children:
        if isinstance(child, Text) and child.value.strip():
            report("error", "E_STRAY_TEXT", f"Text directly inside [{node.tag}] is not rendered",
                   offset=child.start, path=path, hint="Put copy inside a text module.")


def _check_columns(node, path, kids, cols, expected, report, schema, structure_attr_present):
    types = [c.attrs.get("type", "") for c in cols]
    for c, t in zip(cols, types):
        if t not in schema.column_types:
            report("error", "E_COLUMN_TYPE", f"Column type '{t}' is not a Divi column type", node=c,
                   path=_child_path(path, kids, c), attr="type", value=t,
                   hint="Use types such as 4_4, 1_2, 1_3, 2_3, 1_4, 3_4, 1_5, 2_5, 3_5, 1_6.")
    legal = all(t in schema.column_types for t in types)
    fracs = [fraction(t) for t in types]
    if cols and legal and all(fracs) and sum(fracs) != 1:
        report("error", "E_COLUMN_SUM", f"Column widths {','.join(types)} do not add up to one full row",
               node=node, path=path, hint="Column fractions in a row must sum to 1.")
    if structure_attr_present and expected is not None and types != expected:
        report("warning", "W_COLUMN_STRUCTURE_MISMATCH",
               f"Columns are {','.join(types)} but column_structure says {','.join(expected)}",
               node=node, path=path, attr="column_structure",
               hint="Divi renders by column type; make column_structure match so the builder shows the same layout.")


def check_structure(doc, schema, report) -> None:
    for problem in doc.problems:
        report("error", problem.code, problem.message, offset=problem.offset, path="(parser)")

    for child in doc.nodes:
        if isinstance(child, Text) and child.value.strip():
            report("error", "E_TEXT_OUTSIDE_SECTION", "Content outside any [et_pb_section] is not part of the layout",
                   offset=child.start, path="(top level)", hint="Wrap it in section → row → column → text module.")
        elif isinstance(child, Node) and child.tag != "et_pb_section":
            report("error", "E_TOP_LEVEL", f"[{child.tag}] must be inside a section", node=child, path="(top level)")

    for node, path, parent in doc.walk():
        mod = schema.module(node.tag)
        if mod is None:
            report("error", "E_UNKNOWN_TAG", f"Unknown Divi module [{node.tag}]", node=node, path=path,
                   hint="Valid slugs are listed in reference/modules/README.md.")
            continue
        kids = node.modules
        tag = node.tag

        if mod.kind == "child" and parent is not None and parent.tag not in mod.parents:
            parent_mod = schema.module(parent.tag)
            if parent_mod is None or parent_mod.child is None:
                report("error", "E_CHILD_PLACEMENT", f"[{tag}] must be a direct child of {' or '.join(mod.parents)}",
                       node=node, path=path)

        if tag == "et_pb_section":
            _stray_text(node, path, report)
            if node.value("fullwidth") == "on":
                for c in kids:
                    m = schema.module(c.tag)
                    if m is not None and not m.fullwidth:
                        report("error", "E_FULLWIDTH_CHILD", f"Fullwidth sections accept only fullwidth modules, not [{c.tag}]",
                               node=c, path=_child_path(path, kids, c))
            elif node.value("specialty") == "on":
                cols = [c for c in kids if c.tag == "et_pb_column"]
                for c in kids:
                    if c.tag != "et_pb_column":
                        report("error", "E_SECTION_CHILD", f"Specialty sections contain columns, not [{c.tag}]",
                               node=c, path=_child_path(path, kids, c))
                _check_columns(node, path, kids, cols, None, report, schema, False)
                special = [c for c in cols if c.value("specialty_columns")]
                if len(special) != 1:
                    report("error", "E_SPECIALTY_COLUMN", "A specialty section needs exactly one column with specialty_columns",
                           node=node, path=path, hint='Set specialty_columns="2|3|4" on the column that holds inner rows.')
                for c in cols:
                    c_path = _child_path(path, kids, c)
                    for g in c.modules:
                        if any(c is s for s in special) and g.tag != "et_pb_row_inner":
                            report("error", "E_SPECIALTY_CONTENT", f"The specialty column holds only [et_pb_row_inner], not [{g.tag}]",
                                   node=g, path=_child_path(c_path, c.modules, g))
            else:
                for c in kids:
                    if c.tag != "et_pb_row":
                        report("error", "E_SECTION_CHILD", f"Regular sections contain only [et_pb_row], not [{c.tag}]",
                               node=c, path=_child_path(path, kids, c))
        elif tag in COLUMN_FOR_ROW:
            _stray_text(node, path, report)
            col_tag = COLUMN_FOR_ROW[tag]
            cols = [c for c in kids if c.tag == col_tag]
            for c in kids:
                if c.tag != col_tag:
                    report("error", "E_ROW_CHILD", f"[{tag}] contains only [{col_tag}], not [{c.tag}]",
                           node=c, path=_child_path(path, kids, c))
            present = "column_structure" in node.attrs
            structure = node.value("column_structure", "4_4")
            if present and structure not in schema.column_structures[tag]:
                report("error", "E_COLUMN_STRUCTURE", f"'{structure}' is not a legal column_structure for [{tag}]",
                       node=node, path=path, attr="column_structure", value=structure,
                       hint="Legal values: " + ", ".join(schema.column_structures[tag]))
            _check_columns(node, path, kids, cols, structure.split(",") if present else None, report, schema, present)
        elif tag in ("et_pb_column", "et_pb_column_inner"):
            _stray_text(node, path, report)
            in_specialty = parent is not None and parent.tag == "et_pb_section" and parent.value("specialty") == "on"
            for c in kids:
                m = schema.module(c.tag)
                if c.tag == "et_pb_row_inner":
                    if not (in_specialty and node.value("specialty_columns")):
                        report("error", "E_INNER_ROW_PLACEMENT", "[et_pb_row_inner] is only allowed in a specialty section's specialty column",
                               node=c, path=_child_path(path, kids, c))
                elif m is None or m.kind == "child":
                    continue  # reported at the child itself
                elif m.kind == "structure":
                    report("error", "E_COLUMN_CHILD", f"[{c.tag}] cannot be inside a column",
                           node=c, path=_child_path(path, kids, c))
                elif m.fullwidth:
                    report("error", "E_FULLWIDTH_IN_COLUMN", f"[{c.tag}] only works in a fullwidth section",
                           node=c, path=_child_path(path, kids, c), hint='Put it in [et_pb_section fullwidth="on"].')
        elif mod.child:
            _stray_text(node, path, report)
            for c in kids:
                if c.tag != mod.child:
                    report("error", "E_BAD_CHILD", f"[{tag}] can only contain [{mod.child}], not [{c.tag}]",
                           node=c, path=_child_path(path, kids, c))
        else:
            for c in kids:
                report("error", "E_NESTED_MODULE", f"[{c.tag}] cannot be nested inside [{tag}]",
                       node=c, path=_child_path(path, kids, c))


# ----------------------------------------------------------------------------- heading structure
# Every heading-level field in the schema (a *_level field with h1–h6 options), with what makes the
# module actually render that heading:
#   ("text", ATTR)    the heading shows ATTR's text, so it renders only when ATTR is non-empty;
#   ("toggle", ATTR)  site-data headings (post/portfolio/image titles…): rendered unless ATTR is "off";
#   ("always", None)  site-data headings that are always shown (blog/post-slider post titles).
# Site-data headings count once, whatever the number of posts/images the live site has.
HEADING_FIELDS = {
    "et_pb_heading": [("title_level", "text", "title")],
    "et_pb_audio": [("title_level", "text", "title")],
    "et_pb_circle_counter": [("title_level", "text", "title")],
    "et_pb_number_counter": [("title_level", "text", "title")],
    "et_pb_contact_form": [("title_level", "text", "title")],
    "et_pb_toggle": [("title_level", "text", "title")],
    "et_pb_fullwidth_header": [("title_level", "text", "title")],
    "et_pb_blurb": [("header_level", "text", "title")],
    "et_pb_cta": [("header_level", "text", "title")],
    "et_pb_countdown_timer": [("header_level", "text", "title")],
    "et_pb_login": [("header_level", "text", "title")],
    "et_pb_signup": [("header_level", "text", "title")],
    "et_pb_team_member": [("header_level", "text", "name")],
    "et_pb_slide": [("header_level", "text", "heading")],
    "et_pb_pricing_table": [("header_level", "text", "title")],
    "et_pb_accordion_item": [("toggle_level", "text", "title")],
    "et_pb_fullwidth_portfolio": [("portfolio_header_level", "text", "title"), ("title_level", "toggle", "show_title")],
    "et_pb_portfolio": [("title_level", "toggle", "show_title")],
    "et_pb_filterable_portfolio": [("title_level", "toggle", "show_title")],
    "et_pb_gallery": [("title_level", "toggle", "show_title_and_caption")],
    "et_pb_post_title": [("title_level", "toggle", "title")],
    "et_pb_fullwidth_post_title": [("title_level", "toggle", "title")],
    "et_pb_comments": [("title_level", "toggle", "show_count"), ("header_level", "toggle", "show_reply")],
    "et_pb_blog": [("header_level", "always", None)],
    "et_pb_post_slider": [("header_level", "always", None)],
    "et_pb_fullwidth_post_slider": [("header_level", "always", None)],
}
# Parents whose *_level only sets the default for their children (which inherit it when theirs is empty).
HEADING_CONTAINERS = {
    "et_pb_accordion": "toggle_level", "et_pb_slider": "header_level",
    "et_pb_fullwidth_slider": "header_level", "et_pb_pricing_tables": "header_level",
}
HEADING_LEVELS = ("h1", "h2", "h3", "h4", "h5", "h6")
CONTENT_HEADING_RE = re.compile(r"<h([1-6])\b", re.I)


def _level_value(node, parent, attr, schema) -> str:
    """The module's heading level: its own value, else (for a container's child) the parent's value,
    else the schema default of the module, then of the parent."""
    value = node.value(attr)
    if value:
        return value
    if parent is not None and HEADING_CONTAINERS.get(parent.tag) == attr:
        if parent.value(attr):
            return parent.value(attr)
    default = ((schema.module(node.tag).fields.get(attr) or {}).get("default") or "")
    if not default and parent is not None and HEADING_CONTAINERS.get(parent.tag) == attr:
        default = ((schema.module(parent.tag).fields.get(attr) or {}).get("default") or "")
    return default


def collect_headings(doc, schema) -> list:
    """(offset, level, node, path, attr) for every heading the page renders, in document order:
    heading-level fields (with schema defaults when unset) and <h1>–<h6> tags in module content."""
    found = []
    for node, path, parent in doc.walk():
        if schema.module(node.tag) is None:
            continue
        for attr, rule, source in HEADING_FIELDS.get(node.tag, ()):
            if rule == "text" and not node.value(source).strip():
                continue
            if rule == "toggle" and node.value(source) == "off":
                continue
            level = _level_value(node, parent, attr, schema)
            if level in HEADING_LEVELS:
                found.append((node.start, int(level[1]), node, path, attr))
        for child in node.children:
            if isinstance(child, Text):
                for m in CONTENT_HEADING_RE.finditer(child.value):
                    found.append((child.start + m.start(), int(m.group(1)), node, path, "content"))
    found.sort(key=lambda h: h[0])
    return found


def check_headings(doc, schema, report, fragment: bool = False) -> None:
    """E_MULTIPLE_H1 (more than one h1), W_NO_H1 (none; skipped for a fragment such as one section),
    W_HEADING_SKIP (a level jumps by more than one going deeper, e.g. h2 -> h4)."""
    headings = collect_headings(doc, schema)
    h1s = [h for h in headings if h[1] == 1]
    for _pos, _level, node, path, attr in h1s[1:]:
        report("error", "E_MULTIPLE_H1", f"Page has {len(h1s)} h1 headings; this [{node.tag}] {attr} is another h1",
               node=node, path=path, attr=attr, value="h1",
               hint="Keep one h1 (the page's main heading). Make the others h2: set title_level/header_level "
                    "(or the accordion's toggle_level), or change the <h1> tag in the content.")
    if not h1s and not fragment:
        report("warning", "W_NO_H1", "Page has no h1 heading", path="(page)",
               hint="Give the page one h1, usually the hero heading (et_pb_heading title_level defaults to h1). "
                    "Validating a single section or snippet: pass --fragment.")
    prev = None
    for _pos, level, node, path, attr in headings:
        if prev is not None and level > prev + 1:
            report("warning", "W_HEADING_SKIP", f"Heading level jumps from h{prev} to h{level} at [{node.tag}] {attr}",
                   node=node, path=path, attr=attr, value=f"h{prev}>h{level}",
                   hint=f"Use h{prev + 1} here, or add the missing level above it; screen readers and search "
                        "engines read the heading outline in order.")
        prev = level
