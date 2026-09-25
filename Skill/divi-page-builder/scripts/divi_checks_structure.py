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


def _stray_text(node, path, report):
    for child in node.children:
        if isinstance(child, Text) and child.value.strip():
            report("error", "E_STRAY_TEXT", f"Text directly inside [{node.tag}] is not rendered",
                   offset=child.start, path=path, hint="Put copy inside a text module.")


def _check_columns(node, path, cols, expected, report, schema, structure_attr_present):
    types = [c.attrs.get("type", "") for c in cols]
    for c, t in zip(cols, types):
        if t not in schema.column_types:
            report("error", "E_COLUMN_TYPE", f"Column type '{t}' is not a Divi column type", node=c,
                   path=path, attr="type", value=t, hint="Use types such as 4_4, 1_2, 1_3, 2_3, 1_4, 3_4, 1_5, 2_5, 3_5, 1_6.")
    fracs = [fraction(t) for t in types]
    if cols and all(fracs) and sum(fracs) != 1:
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

        if mod.kind == "child" and (parent is None or parent.tag not in mod.parents):
            report("error", "E_CHILD_PLACEMENT", f"[{tag}] must be a direct child of {' or '.join(mod.parents)}",
                   node=node, path=path)

        if tag == "et_pb_section":
            _stray_text(node, path, report)
            if node.value("fullwidth") == "on":
                for c in kids:
                    m = schema.module(c.tag)
                    if m is not None and not m.fullwidth:
                        report("error", "E_FULLWIDTH_CHILD", f"Fullwidth sections accept only fullwidth modules, not [{c.tag}]",
                               node=c, path=path)
            elif node.value("specialty") == "on":
                cols = [c for c in kids if c.tag == "et_pb_column"]
                for c in kids:
                    if c.tag != "et_pb_column":
                        report("error", "E_SECTION_CHILD", f"Specialty sections contain columns, not [{c.tag}]", node=c, path=path)
                _check_columns(node, path, cols, None, report, schema, False)
                special = [c for c in cols if c.value("specialty_columns")]
                if len(special) != 1:
                    report("error", "E_SPECIALTY_COLUMN", "A specialty section needs exactly one column with specialty_columns",
                           node=node, path=path, hint='Set specialty_columns="2|3|4" on the column that holds inner rows.')
                for c in cols:
                    for g in c.modules:
                        if any(c is s for s in special) and g.tag != "et_pb_row_inner":
                            report("error", "E_SPECIALTY_CONTENT", f"The specialty column holds only [et_pb_row_inner], not [{g.tag}]",
                                   node=g, path=path)
            else:
                for c in kids:
                    if c.tag != "et_pb_row":
                        report("error", "E_SECTION_CHILD", f"Regular sections contain only [et_pb_row], not [{c.tag}]",
                               node=c, path=path)
        elif tag in COLUMN_FOR_ROW:
            _stray_text(node, path, report)
            col_tag = COLUMN_FOR_ROW[tag]
            cols = [c for c in kids if c.tag == col_tag]
            for c in kids:
                if c.tag != col_tag:
                    report("error", "E_ROW_CHILD", f"[{tag}] contains only [{col_tag}], not [{c.tag}]", node=c, path=path)
            present = "column_structure" in node.attrs
            structure = node.value("column_structure", "4_4")
            if present and structure not in schema.column_structures[tag]:
                report("error", "E_COLUMN_STRUCTURE", f"'{structure}' is not a legal column_structure for [{tag}]",
                       node=node, path=path, attr="column_structure", value=structure,
                       hint="Legal values: " + ", ".join(schema.column_structures[tag]))
            _check_columns(node, path, cols, structure.split(",") if present else None, report, schema, present)
        elif tag in ("et_pb_column", "et_pb_column_inner"):
            _stray_text(node, path, report)
            in_specialty = parent is not None and parent.tag == "et_pb_section" and parent.value("specialty") == "on"
            for c in kids:
                m = schema.module(c.tag)
                if c.tag == "et_pb_row_inner":
                    if not (in_specialty and node.value("specialty_columns")):
                        report("error", "E_INNER_ROW_PLACEMENT", "[et_pb_row_inner] is only allowed in a specialty section's specialty column",
                               node=c, path=path)
                elif m is None or m.kind == "child":
                    continue  # reported at the child itself
                elif m.kind == "structure":
                    report("error", "E_COLUMN_CHILD", f"[{c.tag}] cannot be inside a column", node=c, path=path)
                elif m.fullwidth:
                    report("error", "E_FULLWIDTH_IN_COLUMN", f"[{c.tag}] only works in a fullwidth section",
                           node=c, path=path, hint='Put it in [et_pb_section fullwidth="on"].')
        elif mod.child:
            _stray_text(node, path, report)
            for c in kids:
                if c.tag != mod.child:
                    report("error", "E_BAD_CHILD", f"[{tag}] can only contain [{mod.child}], not [{c.tag}]", node=c, path=path)
        else:
            for c in kids:
                report("error", "E_NESTED_MODULE", f"[{c.tag}] cannot be nested inside [{tag}]", node=c, path=path)
