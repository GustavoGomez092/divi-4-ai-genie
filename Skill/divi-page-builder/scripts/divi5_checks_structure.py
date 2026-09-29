"""Structural and heading rules for Divi 5 block pages: placeholder → section → row → column → module,
specialty and fullwidth sections, parent/child modules (from schema5 `children`/`parents`), column widths.
The Divi 5 counterpart of divi_checks_structure.py; findings go through validate.Reporter."""
from __future__ import annotations

from typing import Dict, List, Optional

from divi5_blocks import Block, Freeform, get_attr, iter_leaves
from divi_checks_structure import CONTENT_HEADING_RE, HEADING_LEVELS, fraction

PLACEHOLDER = "divi/placeholder"
SECTION_TYPES = ("regular", "fullwidth", "specialty")
COLUMN_FOR_ROW = {"divi/row": "divi/column", "divi/row-inner": "divi/column-inner"}
_PARSER_FREEFORM = frozenset({"E5_STRAY_CLOSE", "E5_MISNESTED"})
_column_types = None


def _legal_column_types() -> set:
    """Divi's column widths (1_2, 1_3, …): the same set as Divi 4 (divi_schema _meta column_structures)."""
    global _column_types
    if _column_types is None:
        from divi_schema import load_schema
        _column_types = load_schema().column_types
    return _column_types


def _is_divi(block: Block) -> bool:
    return block.name.startswith("divi/")


def _section_type(section: Block) -> str:
    t = get_attr(section, "module.advanced.type")
    return "regular" if t in (None, "") else t


def _is_specialty_column(col: Block) -> bool:
    """The column of a specialty section that holds the inner rows (Divi 4 specialty_columns)."""
    return get_attr(col, "module.advanced.specialtyColumns") not in (None, "")


def _col_type(col: Block):
    return get_attr(col, "module.advanced.type")


def _check_freeform(doc, report) -> None:
    """Non-whitespace text between blocks is not part of the Divi layout (E5_NOT_DIVI)."""
    parser_spans = {p.offset for p in doc.problems if p.code in _PARSER_FREEFORM}

    def rec(children, path):
        counts: Dict[str, int] = {}
        for child in children:
            if isinstance(child, Freeform):
                if child.value.strip() and child.start not in parser_spans:
                    report("error", "E5_NOT_DIVI", "Text outside any Divi block is not part of the layout",
                           offset=child.start, path=path or "(top level)",
                           hint="Put copy inside a module's innerContent (e.g. divi/text) in a column.")
            elif _is_divi(child):  # a non-divi block's own content is reported with the block
                idx = counts.get(child.name, 0)
                counts[child.name] = idx + 1
                seg = f"{child.name[5:]}[{idx}]"
                rec(child.children, f"{path} > {seg}" if path else seg)
    rec(doc.nodes, "")


def _check_columns5(row: Block, path: str, cols: List[Block], paths: Dict[int, str], report,
                    structure: Optional[str]) -> None:
    """E5_COLUMNS: illegal column types, widths that don't sum to one row, and a columnStructure that differs from
    the columns' type sequence (the Divi 4 _check_columns fraction rules)."""
    legal = _legal_column_types()
    types = [_col_type(c) for c in cols]
    for c, t in zip(cols, types):
        if t is not None and t not in legal:
            report("error", "E5_COLUMNS", f"Column type '{t}' is not a Divi column type", node=c, path=paths[id(c)],
                   attr="module.advanced.type", value=str(t),
                   hint="Use types such as 4_4, 1_2, 1_3, 2_3, 1_4, 3_4, 1_5, 2_5, 3_5, 1_6.")
    if not cols or any(t is None or t not in legal for t in types):
        return
    fracs = [fraction(t) for t in types]
    if all(fracs) and sum(fracs) != 1:
        report("error", "E5_COLUMNS", f"Column widths {','.join(types)} do not add up to one full row",
               node=row, path=path, attr="module.advanced.type", value=",".join(types),
               hint="Column fractions in a row must sum to 1.")
    elif structure is not None and structure.split(",") != types:
        report("error", "E5_COLUMNS", f"Columns are {','.join(types)} but columnStructure says {structure}",
               node=row, path=path, attr="module.advanced.columnStructure", value=structure,
               hint="Make module.advanced.columnStructure list the columns' types in order.")


def _check_section(section: Block, path: str, schema5, paths: Dict[int, str], report) -> None:
    stype = _section_type(section)
    if stype not in SECTION_TYPES:
        report("error", "E5_SECTION_TYPE", f"Section type '{stype}' is not one of regular, fullwidth, specialty",
               node=section, path=path, attr="module.advanced.type", value=str(stype),
               hint='Leave module.advanced.type unset for a regular section, or use "fullwidth" / "specialty".')
        return
    allowed = schema5.module("divi/section").children or []
    kids = [c for c in section.blocks if _is_divi(c) and c.name in allowed]  # the rest is E5_BAD_PARENT
    if stype == "regular":
        for c in kids:
            if c.name != "divi/row":
                report("error", "E5_SECTION_TYPE", f"Regular sections contain only [divi/row], not [{c.name}]",
                       node=c, path=paths[id(c)])
    elif stype == "fullwidth":
        for c in kids:
            m = schema5.module(c.name)
            if m is None or m.category != "fullwidth-module":
                report("error", "E5_SECTION_TYPE", f"Fullwidth sections accept only fullwidth modules, not [{c.name}]",
                       node=c, path=paths[id(c)])
    else:
        for c in kids:
            if c.name != "divi/column":
                report("error", "E5_SECTION_TYPE", f"Specialty sections contain columns, not [{c.name}]",
                       node=c, path=paths[id(c)])
        cols = [c for c in kids if c.name == "divi/column"]
        _check_columns5(section, path, cols, paths, report, None)
        special = [c for c in cols if _is_specialty_column(c)]
        if len(special) != 1:
            report("error", "E5_SPECIALTY_COLUMN",
                   f"A specialty section needs exactly one column with specialtyColumns, not {len(special)}",
                   node=section, path=path, attr="module.advanced.specialtyColumns",
                   hint='Set module.advanced.specialtyColumns (desktop value "2" or "3") on the one column that '
                        "holds the divi/row-inner blocks.")
        for c in special:
            for g in c.blocks:
                if g.name != "divi/row-inner":
                    report("error", "E5_SECTION_TYPE",
                           f"The specialty column holds only [divi/row-inner], not [{g.name}]",
                           node=g, path=paths[id(g)])


def _check_parent(block: Block, mod, parent: Block, grandparent: Optional[Block], path: str, schema5,
                  report) -> None:
    pmod = schema5.module(parent.name)
    if pmod is None:
        return  # the parent is already reported as unknown
    if pmod.children is None or block.name not in pmod.children:
        report("error", "E5_BAD_PARENT", f"[{block.name}] cannot be inside [{parent.name}]", node=block, path=path,
               hint=(f"Put it in {' or '.join(mod.parents)}." if mod.parents else
                     f"[{parent.name}] holds no blocks." if not pmod.children else ""))
    elif mod.parents and parent.name not in mod.parents:
        report("error", "E5_BAD_PARENT", f"[{block.name}] must be a direct child of {' or '.join(mod.parents)}",
               node=block, path=path)
    elif block.name == "divi/row-inner" and parent.name == "divi/column" and not (
            _is_specialty_column(parent) and grandparent is not None and grandparent.name == "divi/section"
            and _section_type(grandparent) == "specialty"):
        report("error", "E5_INNER_ROW_PLACEMENT",
               "[divi/row-inner] is only allowed in a specialty section's specialty column",
               node=block, path=path,
               hint='Use a section with module.advanced.type "specialty" and put the inner rows in its one column '
                    "that sets module.advanced.specialtyColumns.")


def check_structure5(doc, schema5, report, fragment: bool = False) -> None:
    for problem in doc.problems:
        report("error", problem.code, problem.message, offset=problem.offset, path="(parser)")
    _check_freeform(doc, report)

    tops = [n for n in doc.nodes if isinstance(n, Block)]
    loose = [b for b in tops if b.name != PLACEHOLDER]
    if loose and not fragment:
        report("warning", "W5_NO_PLACEHOLDER", "Top-level blocks are not wrapped in divi/placeholder",
               node=loose[0], path="(top level)",
               hint="Wrap the page's sections in <!-- wp:divi/placeholder --> … <!-- /wp:divi/placeholder -->.")
    paths: Dict[int, str] = {}
    parents: Dict[int, Optional[Block]] = {}
    walked = list(doc.walk())
    for block, path, parent in walked:
        paths[id(block)] = path
        parents[id(block)] = parent

    pool = [c for b in tops if b.name == PLACEHOLDER for c in b.blocks] + loose
    for b in pool:
        if _is_divi(b) and b.name != "divi/section" and schema5.module(b.name) is not None:
            report("error", "E5_TOPLEVEL", f"[{b.name}] must be inside a section", node=b, path=paths[id(b)],
                   hint="The page (inside divi/placeholder) holds only divi/section blocks.")

    for block, path, parent in walked:
        if not _is_divi(block):
            report("error", "E5_NOT_DIVI", f"[{block.name}] is not a Divi block", node=block, path=path,
                   hint="Divi 5 pages hold only divi/* blocks; rebuild this content as Divi modules.")
            continue
        if block.name == PLACEHOLDER:
            if parent is not None:
                report("error", "E5_BAD_PARENT", "[divi/placeholder] only wraps the whole page at the top level",
                       node=block, path=path)
            continue
        mod = schema5.module(block.name)
        if mod is None:
            report("error", "E5_UNKNOWN_BLOCK", f"Unknown Divi block [{block.name}]", node=block, path=path,
                   hint="Divi 5 module blocks are divi/<module> (e.g. divi/text, divi/blurb); check the name.")
            continue
        if not schema5.in_scope(block.name):
            report("warning", "W5_OUT_OF_SCOPE", f"[{block.name}] ({mod.scope}) is outside the modules this skill "
                                                 "builds and validates", node=block, path=path)
        if parent is not None and _is_divi(parent) and parent.name != PLACEHOLDER:
            _check_parent(block, mod, parent, parents.get(id(parent)), path, schema5, report)
        if block.name == "divi/section":
            _check_section(block, path, schema5, paths, report)
        elif block.name in COLUMN_FOR_ROW:
            cols = [c for c in block.blocks if c.name == COLUMN_FOR_ROW[block.name]]
            structure = get_attr(block, "module.advanced.columnStructure")
            _check_columns5(block, path, cols, paths, report, structure if isinstance(structure, str) else None)


# ----------------------------------------------------------------------------- heading structure
# Every Divi 5 element whose font carries a headingLevel (schema5 `defaults` or the block's own
# `<element>.decoration.font.font` desktop value), with what makes the module render that heading — the
# Divi 4 HEADING_FIELDS rules:
#   ("text", ATTR)    renders only when ATTR (an innerContent) is non-empty;
#   ("toggle", ATTR)  site-data headings: rendered unless ATTR is "off";
#   ("always", None)  site-data headings that are always shown.
HEADING_FIELDS5 = {
    "divi/heading": [("title", "text", "title.innerContent")],
    "divi/audio": [("title", "text", "title.innerContent")],
    "divi/circle-counter": [("title", "text", "title.innerContent")],
    "divi/number-counter": [("title", "text", "title.innerContent")],
    "divi/contact-form": [("title", "text", "title.innerContent")],
    "divi/toggle": [("title", "text", "title.innerContent")],
    "divi/fullwidth-header": [("title", "text", "title.innerContent")],
    "divi/blurb": [("title", "text", "title.innerContent")],
    "divi/cta": [("title", "text", "title.innerContent")],
    "divi/countdown-timer": [("title", "text", "title.innerContent")],
    "divi/login": [("title", "text", "title.innerContent")],
    "divi/signup": [("title", "text", "title.innerContent")],
    "divi/team-member": [("name", "text", "name.innerContent")],
    "divi/slide": [("title", "text", "title.innerContent")],
    "divi/pricing-table": [("title", "text", "title.innerContent")],
    "divi/accordion-item": [("title", "text", "title.innerContent")],
    "divi/table-of-contents": [("title", "text", "title.innerContent")],
    "divi/fullwidth-portfolio": [("title", "text", "title.innerContent"),
                                 ("portfolio", "toggle", "portfolio.advanced.showTitle")],
    "divi/portfolio": [("title", "toggle", "portfolio.advanced.showTitle")],
    "divi/filterable-portfolio": [("title", "toggle", "portfolio.advanced.showTitle")],
    "divi/gallery": [("title", "toggle", "module.advanced.showTitleAndCaption")],
    "divi/post-title": [("title", "toggle", "title.advanced.showTitle")],
    "divi/fullwidth-post-title": [("title", "toggle", "title.advanced.showTitle")],
    "divi/comments": [("commentCount", "toggle", "commentCount.advanced.showCount"),
                      ("formTitle", "toggle", "module.advanced.showReply")],
    "divi/blog": [("title", "always", None)],
    "divi/post-slider": [("title", "always", None)],
    "divi/fullwidth-post-slider": [("title", "always", None)],
}
# Parents whose title headingLevel only sets the default for their children (which inherit it when theirs is unset).
HEADING_CONTAINERS5 = {"divi/accordion": "title", "divi/slider": "title", "divi/fullwidth-slider": "title",
                       "divi/pricing-tables": "title"}
_FONT = "{}.decoration.font.font"


def _level_of(block: Block, elem: str) -> str:
    value = get_attr(block, _FONT.format(elem))
    level = value.get("headingLevel") if isinstance(value, dict) else None
    return level if isinstance(level, str) else ""


def _default_level(mod, elem: str) -> str:
    value = (((mod.defaults.get(_FONT.format(elem)) or {}).get("desktop") or {}).get("value")) if mod else None
    level = value.get("headingLevel") if isinstance(value, dict) else None
    return level if isinstance(level, str) else ""


def _level5(block: Block, parent: Optional[Block], elem: str, schema5) -> str:
    """Own headingLevel, else (for a container's child) the parent's, else the schema default of the module,
    then of the parent."""
    inherit = parent is not None and HEADING_CONTAINERS5.get(parent.name) == elem
    return (_level_of(block, elem) or (_level_of(parent, elem) if inherit else "")
            or _default_level(schema5.module(block.name), elem)
            or (_default_level(schema5.module(parent.name), elem) if inherit else ""))


def _non_empty(value) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def collect_headings5(doc, schema5) -> list:
    """(offset, seq, level, block, path, attr) for every heading the page renders, in document order:
    headingLevel of heading elements (with schema5 defaults when unset) and <h1>–<h6> tags in innerContent HTML."""
    found = []
    for block, path, parent in doc.walk():
        if not _is_divi(block) or schema5.module(block.name) is None:
            continue
        for elem, rule, source in HEADING_FIELDS5.get(block.name, ()):
            if rule == "text" and not _non_empty(get_attr(block, source)):
                continue
            if rule == "toggle" and get_attr(block, source) == "off":
                continue
            level = _level5(block, parent, elem, schema5)
            if level in HEADING_LEVELS:
                found.append((block.start, len(found), int(level[1]), block, path, _FONT.format(elem)))
        for attr, bp, state, value in iter_leaves(block.attrs):
            if not attr.endswith("innerContent") or bp not in (None, "desktop") or state not in (None, "value") \
                    or not isinstance(value, str):
                continue
            for m in CONTENT_HEADING_RE.finditer(value):
                found.append((block.start, len(found), int(m.group(1)), block, path, attr))
    found.sort(key=lambda h: (h[0], h[1]))
    return found


def check_headings5(doc, schema5, report, fragment: bool = False) -> None:
    """E5_MULTIPLE_H1 (more than one h1), W_NO_H1 (none; skipped for a fragment), W_HEADING_SKIP (a level jumps
    by more than one going deeper). Same rules and messages as divi_checks_structure.check_headings."""
    headings = collect_headings5(doc, schema5)
    h1s = [h for h in headings if h[2] == 1]
    for *_x, block, path, attr in h1s[1:]:
        report("error", "E5_MULTIPLE_H1", f"Page has {len(h1s)} h1 headings; this [{block.name}] {attr} is another h1",
               node=block, path=path, attr=attr, value="h1",
               hint="Keep one h1 (the page's main heading). Make the others h2: set headingLevel in the module's "
                    "font (e.g. title.decoration.font.font desktop value), or change the <h1> tag in the content.")
    if not h1s and not fragment:
        report("warning", "W_NO_H1", "Page has no h1 heading", path="(page)",
               hint="Give the page one h1, usually the hero heading (divi/heading's title defaults to h1). "
                    "Validating a single section or snippet: pass --fragment.")
    prev = None
    for _pos, _seq, level, block, path, attr in headings:
        if prev is not None and level > prev + 1:
            report("warning", "W_HEADING_SKIP", f"Heading level jumps from h{prev} to h{level} at [{block.name}] {attr}",
                   node=block, path=path, attr=attr, value=f"h{prev}>h{level}",
                   hint=f"Use h{prev + 1} here, or add the missing level above it; screen readers and search "
                        "engines read the heading outline in order.")
        prev = level
