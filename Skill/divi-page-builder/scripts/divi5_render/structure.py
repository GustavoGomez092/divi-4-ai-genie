"""Section, row, column and their inner versions (SectionModule, RowModule, RowInnerModule, ColumnModule).

Markup is the render_callback output; classes follow each module_classnames. Styles use the generic element
style with the module-specific overrides of each module_styles: the section's background-colour selector, the
column's `--et-pb-icon-self-align` default, the overflow a border radius adds.
"""
from __future__ import annotations

from . import coverage
from .base import Mod, register, render_children
from .options import custom_css, element_style
from .values import get

COLUMN_CLASSNAMES = {
    "1_4,1_4,1_4,1_4": "4col", "1_5,1_5,1_5,1_5,1_5": "5col", "1_6,1_6,1_6,1_6,1_6,1_6": "6col",
    "1_4,3_4": "1-4_3-4", "3_4,1_4": "3-4_1-4", "1_4,1_2,1_4": "1-4_1-2_1-4", "1_4,1_4,1_2": "1-4_1-4_1-2",
    "1_2,1_4,1_4": "1-2_1-4_1-4", "1_5,1_5,3_5": "1-5_1-5_3-5", "3_5,1_5,1_5": "3-5_1-5_1-5",
    "1_6,1_6,1_6,1_2": "1-6_1-6_1-6_1-2", "1_2,1_6,1_6,1_6": "1-2_1-6_1-6_1-6",
}
ROW_INNER_STRUCTURES = {"1_2-1_2,1_2": "1-4_1-4", "1_2-1_3,1_3,1_3": "1-6_1-6_1-6", "3_4-1_3,1_3,1_3": "1-4_1-4_1-4",
                        "2_3-1_4,1_4,1_4,1_4": "1-6_1-6_1-6_1-6"}
SPECIALTY_ROWS = {"1-4_3-4", "3-4_1-4", "1-4_1-4_1-2", "1-4_1-2_1-4", "1-2_1-4_1-4"}
# The option groups the structure handlers print (coverage families), per attribute path.
DECO = {"background": "background", "spacing": "spacing", "sizing": "sizing", "border": "border",
        "boxShadow": "boxShadow", "layout": "layout"}


def handled_common(extra: dict | None = None) -> dict:
    h = {f"module.decoration.{k}": fam for k, fam in DECO.items()}
    h.update({"modulePreset": "*", "groupPreset": "*", "module.advanced.htmlAttributes": "htmlAttributes",
              "module.decoration.attributes": "*", "css": "css"})
    h.update(extra or {})
    return h


def _layout_ignored(m: Mod) -> list:
    """Flex/grid layout is outside the Python preview (its LayoutStyle CSS isn't ported): name it."""
    display = m.layout()
    if display == "block":
        return []
    explicit = get(m.attrs, "module", "decoration", "layout", "desktop", "value", "display") is not None
    return [f"module.decoration.layout.display={display}{'' if explicit else ' (default)'}"]


def _structure_style(m: Mod, background_selector: str | None = None):
    el = m.element("module")
    if background_selector:
        bg = dict(el.props.get("background") or {})
        bg["propertySelectors"] = {"desktop": {"value": {"background-color": background_selector}}}
        el.props["background"] = bg
    element_style(m.ctx, m.deco(), el, overflow_selector=m.oc)
    custom_css(m.ctx, m.a("css") or {}, m.oc)


def _html_attrs_decl(m: Mod, classes: str) -> str:
    return f'<div class="{classes}"{m.html_attrs()}>'


@register("section")
def r_section(b, ctx, info):
    m = Mod(ctx, b, "section")
    stype = m.a("module", "advanced", "type", "desktop", "value") or "regular"
    lk = m.layout()
    own = []
    if stype == "fullwidth":
        own.append("et_pb_fullwidth_section")
    if stype == "specialty":
        own.append("et_section_specialty")
        if get(m.attrs, "module", "advanced", "gutter", "desktop", "value", "makeEqual") == "on":
            own.append("et_pb_equal_columns")
        gw = get(m.attrs, "module", "advanced", "gutter", "desktop", "value", "width")
        gw = 3 if gw is None else gw
        if gw != "" and lk != "flex":
            own.append(f"et_pb_gutters{gw}")
    else:
        own.append("et_section_regular")
    own.append({"flex": "et_flex_section", "grid": "et_grid_section"}.get(lk, "et_block_section"))
    _structure_style(m, f".et-l--post>.et_builder_inner_content .et_pb_section{m.oc}")
    coverage.check(ctx, "section", m.attrs,
                   handled_common({"module.advanced.type": "*", "module.advanced.gutter": "gutter"}),
                   _layout_ignored(m))
    kids = b.blocks
    if stype == "specialty":
        info2 = {"section_type": "specialty", "parent_layout": lk}
        inner = render_children(b, ctx, info2)
        types = "_".join((get(k.attrs, "module", "advanced", "type", "desktop", "value") or "").replace("_", "-")
                         for k in kids)
        rcls = ["et_pb_row"]
        if types in SPECIALTY_ROWS:
            rcls.append(f"et_pb_row-{types}")
        rcls.append({"flex": "et_flex_row", "grid": "et_grid_row"}.get(lk, "et_block_row"))
        inner = f'<div class="{" ".join(rcls)}">{inner}</div>'
    else:
        inner = render_children(b, ctx, {"section_type": stype})
    return f'{_html_attrs_decl(m, m.classes(own, module=False))}{inner}</div>'


def _row(b, ctx, info, slug: str):
    m = Mod(ctx, b, slug)
    lk = m.layout()
    structure = m.a("module", "advanced", "columnStructure", "desktop", "value")
    gutter = get(m.attrs, "module", "advanced", "gutter", "desktop", "value") or {}
    own = []
    block = lk not in ("flex", "grid")
    if slug == "row":
        col_cls = f"et_pb_row_{COLUMN_CLASSNAMES[structure]}" if structure in COLUMN_CLASSNAMES else None
        if col_cls and block:
            own.append(col_cls)
        if not b.blocks:
            own.append("et_pb_row_empty")
        if gutter.get("makeEqual") == "on" and gutter.get("alignColumns", "stretch") == "stretch" and block:
            own.append("et_pb_equal_columns")
        gw = gutter.get("width")
        if gw not in (None, "") and lk != "flex":
            own.append(f"et_pb_gutters{gw}")
        if info.get("in_specialty_column"):
            own.append("et_pb_row_nested")
        own.append({"flex": "et_flex_row", "grid": "et_grid_row"}.get(lk, "et_block_row"))
        if block and col_cls:
            own.append(col_cls.replace("et_pb_row_", "et_block_row_"))
    else:
        col_cls = f"et_pb_row_{COLUMN_CLASSNAMES[structure]}" if structure in COLUMN_CLASSNAMES else None
        if col_cls and block:
            own.append(col_cls)
        if not b.blocks:
            own.append("et_pb_row_empty")
        if gutter.get("makeEqual") == "on" and gutter.get("alignColumns", "stretch") == "stretch" and block:
            own.append("et_pb_equal_columns")
        if gutter.get("enable") == "on" and gutter.get("width") not in (None, "") and block:
            own.append(f"et_pb_gutters{gutter['width']}")
        own.append({"flex": "et_flex_row", "grid": "et_grid_row"}.get(lk, "et_block_row"))
        sct = info.get("section_column_type") or m.a("module", "advanced", "sectionColumnType", "desktop", "value")
        ri = ROW_INNER_STRUCTURES.get(f"{sct}-{structure}")
        if ri:
            own.append(f"et_pb_row-{ri}")
    _structure_style(m)
    coverage.check(ctx, slug, m.attrs,
                   handled_common({"module.advanced.columnStructure": "*", "module.advanced.gutter": "gutter"}),
                   _layout_ignored(m))
    inner = render_children(b, ctx, {"parent_layout": lk, "inner": slug == "row-inner",
                                     "section_type": info.get("section_type"),
                                     "section_column_type": info.get("section_column_type")})
    return f'{_html_attrs_decl(m, m.classes(own, module=False))}{inner}</div>'


@register("row")
def r_row(b, ctx, info):
    return _row(b, ctx, info, "row")


@register("row-inner")
def r_row_inner(b, ctx, info):
    return _row(b, ctx, info, "row-inner")


COLUMN_INNER_TYPES = {("1_2", "1_2"): "1_4", ("1_2", "3_4"): "3_8", ("1_2", "2_3"): "1_3",
                      ("1_3", "1_2"): "1_6", ("1_3", "3_4"): "1_4", ("1_3", "2_3"): "2_9", ("1_4", "2_3"): "1_6"}


def _column(b, ctx, info, slug: str):
    m = Mod(ctx, b, slug)
    inner = slug == "column-inner"
    ctype = m.a("module", "advanced", "type", "desktop", "value") or "4_4"
    specialty_cols = m.a("module", "advanced", "specialtyColumns", "desktop", "value") or ""
    parent_block = (info.get("parent_layout") or "flex") not in ("flex", "grid")
    own = []
    if parent_block:
        if specialty_cols:
            own.append("et_pb_specialty_column")
        if inner:
            own.append("et_pb_column")
        if info.get("section_type") == "specialty" and not inner and not specialty_cols:
            own.append("et_pb_column_single")
        if inner:
            sct = info.get("section_column_type") or \
                m.a("module", "advanced", "savedSpecialtyColumnType", "desktop", "value") or ""
            own.append("et_pb_column_" + COLUMN_INNER_TYPES.get((ctype, sct), "4_4"))
        else:
            own.append(f"et_pb_column_{ctype}")
    if info.get("last"):
        own.append("et-last-child")
    lk = m.layout()
    own.append({"flex": "et_flex_column", "grid": "et_grid_column"}.get(lk, "et_block_column"))
    if not b.blocks:
        own.append("et_pb_column_empty")
    blend = get(m.attrs, "module", "decoration", "filters", "desktop", "value", "blendMode")
    own.append("et_pb_css_mix_blend_mode" if blend else "et_pb_css_mix_blend_mode_passthrough")
    if not inner:  # ColumnModule::icon_self_align_style_declaration (ColumnInnerModule has no such style)
        align = get(m.attrs, "module", "decoration", "layout", "desktop", "value", "alignItems")
        m.ctx.css.add(m.oc, ["--et-pb-icon-self-align:" + (align if align and align != "stretch" else "center")])
    _structure_style(m)
    coverage.check(ctx, slug, m.attrs,
                   handled_common({"module.advanced.type": "*", "module.advanced.specialtyColumns": "*",
                                   "module.advanced.savedSpecialtyColumnType": "*"}),
                   _layout_ignored(m))
    kid_info = {"parent_layout": lk, "in_specialty_column": bool(specialty_cols), "section_type": None,
                "section_column_type": ctype if specialty_cols else info.get("section_column_type")}
    body = render_children(b, ctx, kid_info)
    return f'{_html_attrs_decl(m, m.classes(own, module=False))}{body}</div>'


@register("column")
def r_column(b, ctx, info):
    return _column(b, ctx, info, "column")


@register("column-inner")
def r_column_inner(b, ctx, info):
    return _column(b, ctx, info, "column-inner")


@register("placeholder")
def r_placeholder(b, ctx, info):
    return render_children(b, ctx, info)
