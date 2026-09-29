# Structure (Divi 5)

Which blocks go inside which, and the attributes that shape a layout. The Divi 4 counterpart is
[../structure.md](../structure.md); the block grammar is in [page-format.md](page-format.md). Evidence is in the
repo only: `research/divi5/…` (the spikes) and `research/divi5/doc-experiments.md` (the live checks cited below).

## Nesting diagram

```
<!-- wp:divi/placeholder -->            the page wrapper: top level only, holds only sections
  divi/section                          regular section (module.advanced.type unset): only divi/row
    divi/row                            module.advanced.columnStructure "1_2,1_2"
      divi/column                       module.advanced.type "1_2", one per entry of columnStructure
        <module>                        divi/text, divi/heading, divi/blurb, ...
          <child module>                only for parents such as divi/accordion → divi/accordion-item
  divi/section  type "fullwidth"        no row/column layer
    <fullwidth module>                  divi/fullwidth-header, divi/fullwidth-image, ...
  divi/section  type "specialty"        only divi/column
    divi/column  type "1_4"             an ordinary column: modules
    divi/column  type "3_4"             the specialty column: specialtyColumns "3", holds only divi/row-inner
      divi/row-inner                    columnStructure "1_2,1_2"
        divi/column-inner               type "1_2", savedSpecialtyColumnType "3_4"
          <module>
```

Every structure attribute is a responsive value like any other: `"module": {"advanced": {"type": {"desktop":
{"value": "1_2"}}}}`. Set only the `desktop` value.

## The layout form: `display: "block"` on structure blocks

Divi 5's native layout is flexbox; Divi 4's was block layout with fractional column widths. Divi's own
converter keeps converted pages looking like Divi 4 by writing `module.decoration.layout` → `{"display": "block"}`
on every section, row and column, with the row's `module.advanced.columnStructure` and each column's
`module.advanced.type` (`schema.md` §4, §5). New content uses that same form: it is the form with Divi-written
ground truth (the 35 converted fixtures and Divi AI output), and the Divi 4 layout knowledge carries over.

**Write this on every `divi/section`, `divi/row`, `divi/column`, `divi/row-inner` and `divi/column-inner`:**

```json
"module": {"decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}}
```

What happens without it (live check, `doc-experiments.md` §2): with `builderVersion` 5.13.1 and the layout attribute
the blocks render `et_block_section`, `et_block_row`, `et_block_column et_pb_column_1_2`. The same `1_2,1_2` row
without it renders `et_flex_row` and both columns `et_flex_column_24_24`: the `1_2` widths are ignored and each
column is **full width**.

Modules don't need it: without their own `layout` they render as Divi 5 flex modules (`et_flex_module`, a flex
column), and every module in these references rendered that way. Divi's converter also writes
`display: "block"` on modules; keep it when you edit converted content. Don't author Divi 5's flex or grid
options (`module.decoration.layout` `display: "flex"`/`"grid"`, `module.decoration.sizing` `flexType`) on new pages:
they have no Divi-written ground truth yet.

The smallest legal section:

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eOne full-width column.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Regular, fullwidth and specialty sections

The section type is `module.advanced.type` on `divi/section` (desktop value): unset or `""` for regular,
`"fullwidth"` or `"specialty"`. Anything else is `E5_SECTION_TYPE`. Rendered classes (live check):
`et_section_regular` for regular sections, `et_pb_fullwidth_section et_section_regular` for fullwidth ones,
`et_section_specialty` for specialty ones.

**Regular:** only `divi/row` children (a column directly in it is `E5_SECTION_TYPE`, a module `E5_BAD_PARENT`);
each row holds only `divi/column`:

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_2,1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Why homeowners call us"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eUpfront pricing, no overtime fees.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

**Fullwidth:** no row or column; the section holds fullwidth modules directly (`divi/fullwidth-header`,
`divi/fullwidth-image`, `divi/fullwidth-slider`, `divi/fullwidth-code`, `divi/fullwidth-map`). A row or column in
it is `E5_SECTION_TYPE`, a regular module `E5_BAD_PARENT`. A fullwidth module in a column is `E5_BAD_PARENT`, and
in a regular section `E5_SECTION_TYPE`.

```divi5
<!-- wp:divi/section {"module":{"advanced":{"type":{"desktop":{"value":"fullwidth"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/fullwidth-header {"title":{"innerContent":{"desktop":{"value":"Need a plumber now?"}}},"subhead":{"innerContent":{"desktop":{"value":"Licensed, insured, on call 24/7"}}},"buttonOne":{"innerContent":{"desktop":{"value":{"text":"Call now","linkUrl":"tel:+13055550100"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/section -->
```

**Specialty:** only `divi/column` children, which together fill one row (their `type`s sum to one, `E5_COLUMNS`).
Exactly one of them is the **specialty column**: it sets `module.advanced.specialtyColumns` and holds only
`divi/row-inner` blocks (`E5_SPECIALTY_COLUMN` if no column or more than one sets it; `E5_SECTION_TYPE` for anything
but inner rows in it). The other columns hold modules. Inner rows and inner columns work like rows and columns and
get the same `display: "block"`. A `divi/row-inner` anywhere else is `E5_INNER_ROW_PLACEMENT`.

```divi5
<!-- wp:divi/section {"module":{"advanced":{"type":{"desktop":{"value":"specialty"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eSidebar.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"3_4"}},"specialtyColumns":{"desktop":{"value":"3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row-inner {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_2,1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column-inner {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}},"savedSpecialtyColumnType":{"desktop":{"value":"3_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eDrains\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column-inner --><!-- wp:divi/column-inner {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}},"savedSpecialtyColumnType":{"desktop":{"value":"3_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eWater heaters\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column-inner --><!-- /wp:divi/row-inner --><!-- /wp:divi/column --><!-- /wp:divi/section -->
```

The nine arrangements Divi's builder offers, with the specialty column and its `specialtyColumns` value
(Divi 5 `columnSpecialty` constants and `edit-post.js`, the same as Divi 4; `doc-experiments.md` §6):

| columns (`type`s in order) | specialty column | `specialtyColumns` |
|---|---|---|
| `1_2`, `1_2` | first | `"3"` |
| `1_2`, `1_2` | second | `"3"` |
| `1_4`, `3_4` | second (`3_4`) | `"3"` |
| `3_4`, `1_4` | first (`3_4`) | `"3"` |
| `1_4`, `1_2`, `1_4` | middle (`1_2`) | `"3"` |
| `1_2`, `1_4`, `1_4` | first (`1_2`) | `"3"` |
| `1_4`, `1_4`, `1_2` | last (`1_2`) | `"3"` |
| `1_3`, `2_3` | second (`2_3`) | `"4"` |
| `2_3`, `1_3` | first (`2_3`) | `"4"` |

The validator checks only that exactly one column sets `specialtyColumns`; use the table's value. On each
`divi/column-inner`, set `savedSpecialtyColumnType` to the specialty column's `type` (Divi 4's
`saved_specialty_column_type`, which the converter carries over). Inner column widths are relative to the
specialty column: `1_2,1_2` inside a `3_4` column rendered as two `et_pb_column_3_8` columns (live check).

## `columnStructure` and column `type`

Set `module.advanced.columnStructure` on every `divi/row` / `divi/row-inner`: the column `type`s in order, comma
separated. Set `module.advanced.type` on every `divi/column` / `divi/column-inner`. Legal column types: `4_4`,
`1_2`, `1_3`, `2_3`, `1_4`, `3_4`, `1_5`, `2_5`, `3_5`, `1_6`. `validate.py` reports `E5_COLUMNS` for a type outside
that list, for widths that don't add up to one row, and for a `columnStructure` that differs from the columns you
wrote.

**`divi/row`**: the 20 structures of Divi 5's layout picker (the `regular` constants, identical to Divi 4's list):

| `columnStructure` | column `type`s |
|---|---|
| `4_4` | `4_4` |
| `1_2,1_2` | `1_2`, `1_2` |
| `1_3,1_3,1_3` | `1_3` × 3 |
| `1_4,1_4,1_4,1_4` | `1_4` × 4 |
| `1_5,1_5,1_5,1_5,1_5` | `1_5` × 5 |
| `1_6,1_6,1_6,1_6,1_6,1_6` | `1_6` × 6 |
| `2_5,3_5` | `2_5`, `3_5` |
| `3_5,2_5` | `3_5`, `2_5` |
| `1_3,2_3` | `1_3`, `2_3` |
| `2_3,1_3` | `2_3`, `1_3` |
| `1_4,3_4` | `1_4`, `3_4` |
| `3_4,1_4` | `3_4`, `1_4` |
| `1_4,1_2,1_4` | `1_4`, `1_2`, `1_4` |
| `1_5,3_5,1_5` | `1_5`, `3_5`, `1_5` |
| `1_4,1_4,1_2` | `1_4`, `1_4`, `1_2` |
| `1_2,1_4,1_4` | `1_2`, `1_4`, `1_4` |
| `1_5,1_5,3_5` | `1_5`, `1_5`, `3_5` |
| `3_5,1_5,1_5` | `3_5`, `1_5`, `1_5` |
| `1_6,1_6,1_6,1_2` | `1_6`, `1_6`, `1_6`, `1_2` |
| `1_2,1_6,1_6,1_6` | `1_2`, `1_6`, `1_6`, `1_6` |

**`divi/row-inner`** (inside a specialty column): `4_4`, `1_2,1_2`, `1_3,1_3,1_3` (Divi 5's `columnInner`), plus
`1_4,1_4,1_4,1_4` (`columnInnerWide`, for the wide `2_3` specialty column).

The validator accepts any legal types that sum to one row; stick to these structures, which are the ones the
Visual Builder can show and edit.

## Parent → child pairs

Parents that hold one kind of child block (from `scripts/schema5`, `childrenName` in Divi's `module.json`;
`schema.md` §5). The child goes directly inside its parent and nowhere else; anything else inside the parent,
or the child anywhere else, is `E5_BAD_PARENT`.

| parent | child |
|---|---|
| `divi/accordion` | `divi/accordion-item` |
| `divi/contact-form` | `divi/contact-field` |
| `divi/counters` | `divi/counter` |
| `divi/fullwidth-map`, `divi/map` | `divi/map-pin` |
| `divi/fullwidth-slider`, `divi/slider` | `divi/slide` |
| `divi/group-carousel` | `divi/group` |
| `divi/icon-list` | `divi/icon-list-item` |
| `divi/pricing-tables` | `divi/pricing-table` |
| `divi/signup` | `divi/signup-custom-field` |
| `divi/social-media-follow` | `divi/social-media-follow-network` |
| `divi/tabs` | `divi/tab` |
| `divi/timeline` | `divi/timeline-item` |
| `divi/video-slider` | `divi/video-slider-item` |
| `divi/row` | `divi/column` |
| `divi/row-inner` | `divi/column-inner` |

Every other module is a leaf: it holds no blocks (`E5_BAD_PARENT` for anything inside it). A parent's heading
level set on its own `title.decoration.font.font` is inherited by children that don't set one (accordion, slider,
pricing tables), which is how the accordion below renders both items as `<h3>` (live check):

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Questions"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/accordion {"title":{"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":{"value":"Do you pull permits?"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eYes. We handle permits and inspections.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":{"value":"Are you open on weekends?"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eYes, 24/7.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/accordion --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

Divi 5 also has `divi/group`, a container block that holds modules inside a column (or inside
`divi/group-carousel`). It is in scope and documented in [modules/group.md](modules/group.md), but no recipe needs
it; lay pages out with rows and columns.

Signup custom fields: Divi's converter leaves Divi 4 `[et_pb_signup_custom_field]` children as shortcode inside
the signup's `content`, where Divi 5 does not render them (`storage-and-serialization.md` §7). Write them as
`divi/signup-custom-field` child blocks.

## Module numbering and custom CSS

Every rendered block gets an **order class**, `et_pb_<name>_<N>`, first in its class list:
`class="et_pb_text_0 et_pb_text et_pb_module …"`, `et_pb_section_0`, `et_pb_row_0`, `et_pb_column_0`
(`storage-and-serialization.md` §2.4, live check). `<name>` is the block name after `divi/` with `-` turned into
`_` (`et_pb_fullwidth_header_0`, `et_pb_accordion_item_0`; `ModuleUtils::get_module_class_by_name()`). Note
`divi/cta` is `et_pb_cta_N`, not Divi 4's `et_pb_promo_N`. `N` counts blocks of that name in document order. It
is assigned at render time, is never stored, and **shifts whenever a block is added, removed or moved before it**.
Divi's generated CSS targets these classes; your own CSS should not. Instead:

- Put CSS on the block itself with its `css` attribute. Its keys are the module's CSS slots (listed on each module
  page; `mainElement`, `before`, `after`, `freeForm` everywhere, plus module parts such as `blurbTitle`), and the
  values are declarations. Divi scopes them to the block's order class for you:
  `"css": {"desktop": {"value": {"mainElement": "letter-spacing: 1px;"}}}` rendered
  `.et_pb_text_0{…letter-spacing:1px}` (live check).
- Or give the block a stable class or id with `module.advanced.htmlAttributes` → `{"class": "…", "id": "…"}`
  (desktop only) and target that from site CSS. Divi's converter writes classes as attribute rows instead
  (`module.decoration.attributes`, [value-formats.md → json](value-formats.md#json)); Divi 5.13.1 renders both.

```divi5
<!-- wp:divi/section {"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eSame-day service.\u003c/p\u003e"}}},"module":{"advanced":{"htmlAttributes":{"desktop":{"value":{"class":"hero-lead","id":"intro"}}}}},"css":{"desktop":{"value":{"mainElement":"letter-spacing: 1px;"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Structural validator codes

| code | level | meaning | fix |
|---|---|---|---|
| `E5_TOPLEVEL` | error | a block other than `divi/section` at the top level (inside the placeholder) | wrap it in section → row → column, or a fullwidth section for a fullwidth module |
| `E5_UNKNOWN_BLOCK` | error | a `divi/…` name Divi doesn't have | check [modules/README.md](modules/README.md) |
| `W5_OUT_OF_SCOPE` | warning | a real Divi block this skill doesn't build (WooCommerce, integrations, Theme Builder) | use an in-scope module |
| `E5_BAD_PARENT` | error | a block inside a parent that doesn't accept it (a child module outside its parent, a module in a leaf, a fullwidth module in a column, a nested placeholder) | move it to a parent the tables above allow |
| `E5_SECTION_TYPE` | error | an unknown section type, or a child the section type doesn't allow (regular → rows, fullwidth → fullwidth modules, specialty → columns; the specialty column → inner rows) | fix the type or the children |
| `E5_SPECIALTY_COLUMN` | error | a specialty section without exactly one column that sets `specialtyColumns` | set it on the one column that holds the inner rows |
| `E5_INNER_ROW_PLACEMENT` | error | `divi/row-inner` outside a specialty section's specialty column | use a specialty section, or a regular row |
| `E5_COLUMNS` | error | an illegal column type, widths that don't sum to one row, or `columnStructure` ≠ the columns' types | use the tables above |
| `E5_MULTIPLE_H1` | error | more than one `h1` on the page | one `h1`; set `headingLevel` `h2`… on the others |
| `W_NO_H1` | warning | no `h1` (not reported with `--fragment`) | make the hero heading the `h1` (`divi/heading` defaults to `h1`) |
| `W_HEADING_SKIP` | warning | a heading goes two levels deeper than the one before (`h2` → `h4`) | use the next level; blurb titles default to `h4`, accordion items to `h5` |

Headings are counted from each module's `headingLevel` (its default when unset, and a parent's for children that
inherit it) and from `<h1>`–`<h6>` tags in HTML content, in document order, exactly as for Divi 4
([../structure.md → Heading outline](../structure.md#heading-outline)). The level lives in
`<element>.decoration.font.font` → `headingLevel`, desktop only.
