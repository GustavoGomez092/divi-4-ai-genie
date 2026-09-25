# Structure

## Nesting diagram

```
[et_pb_section]                              <- top level only, one or more per page
  [et_pb_row]                                <- regular section: only et_pb_row children
    [et_pb_column]                           <- one per column in column_structure
      <module>                               <- et_pb_text, et_pb_image, et_pb_blurb, ...
        <child module, if the module has one>  <- e.g. et_pb_accordion_item inside et_pb_accordion
[et_pb_section fullwidth="on"]               <- fullwidth section: no row/column layer
  <fullwidth module>                         <- et_pb_fullwidth_header, et_pb_fullwidth_slider, ...
[et_pb_section specialty="on"]               <- specialty section: only et_pb_column children
  [et_pb_column]                             <- ordinary column, any non-structure module
  [et_pb_column specialty_columns="…"]       <- exactly one column holds inner rows
    [et_pb_row_inner]
      [et_pb_column_inner]
        <module>
```

Every page's `post_content` is a flat sequence of one or more `et_pb_section` tags at the top
level — nothing else is legal outside a section (`E_TOP_LEVEL`, `E_TEXT_OUTSIDE_SECTION`).

## Regular, fullwidth and specialty sections

Confirmed on the real site (`research/tools/notes/doc-experiments.md`, experiment 4): every
rendered section carries the CSS class `et_section_regular` **or** `et_section_specialty` —
never both — and `fullwidth="on"` adds an *additional* `et_pb_fullwidth_section` class on top of
`et_section_regular`. A fullwidth section is a regular section whose child isn't `et_pb_row`, not
a third class of section.

**Regular** — `et_pb_section` (no `fullwidth`/`specialty`) contains only `et_pb_row`, which
contains only `et_pb_column`:

```divi
[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Regular section.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

**Fullwidth** — `et_pb_section fullwidth="on"` skips the row/column layer entirely and contains a
single fullwidth-only module directly (`et_pb_fullwidth_header`, `et_pb_fullwidth_slider`,
`et_pb_fullwidth_menu`, `et_pb_fullwidth_code`, `et_pb_fullwidth_image`, `et_pb_fullwidth_map`,
`et_pb_fullwidth_portfolio`, `et_pb_fullwidth_post_content`, `et_pb_fullwidth_post_slider`,
`et_pb_fullwidth_post_title` — the full `fullwidth: true` list below). Putting a non-fullwidth
module directly in a fullwidth section is `E_FULLWIDTH_CHILD`; putting a fullwidth module inside a
regular column is `E_FULLWIDTH_IN_COLUMN`.

```divi
[et_pb_section fullwidth="on" _builder_version="4.27.9" _module_preset="default"][et_pb_fullwidth_header title="Need a plumber now?" _builder_version="4.27.9" _module_preset="default"][/et_pb_fullwidth_header][/et_pb_section]
```

**Specialty** — `et_pb_section specialty="on"` contains only `et_pb_column`s directly (no
`et_pb_row` layer; a non-column child is `E_SECTION_CHILD`). Exactly one of those columns must set
`specialty_columns` (`E_SPECIALTY_COLUMN` if none or more than one does); only that column may
hold `et_pb_row_inner` (`E_INNER_ROW_PLACEMENT`/`E_SPECIALTY_CONTENT` otherwise), and its
`et_pb_row_inner`/`et_pb_column_inner` children work exactly like a regular row/column, just
narrower. See experiment 5 in `doc-experiments.md` for the full table of legal column arrangements
and their `specialty_columns` values (`1_4,3_4` with `specialty_columns="3"` on the `3_4` column,
used below, is one of nine legal shapes).

Also confirmed by experiment 4: the *rendered* width class of a specialty column's inner columns
is the inner column's own fraction scaled by the specialty column's width — a `column_structure`
of `1_2,1_2` inside a `type="3_4"` specialty column rendered as `et_pb_column_3_8` (3/8 = 1/2 ×
3/4), even though you still write `1_2,1_2` (relative to the inner row, not the page) as the
`column_structure`/`type` values.

```divi
[et_pb_section specialty="on" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Sidebar.</p>[/et_pb_text][/et_pb_column][et_pb_column type="3_4" specialty_columns="3" _builder_version="4.27.9" _module_preset="default"][et_pb_row_inner _builder_version="4.27.9" _module_preset="default"][et_pb_column_inner type="4_4" saved_specialty_column_type="3_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text _builder_version="4.27.9" _module_preset="default"]<p>Main.</p>[/et_pb_text][/et_pb_column_inner][/et_pb_row_inner][/et_pb_column][/et_pb_section]
```

## `column_structure` values

`column_structure` is set on `et_pb_row`/`et_pb_row_inner` and must list one column `type` per
column, comma-separated, summing to a whole row (`E_COLUMN_SUM`); if you set it, the columns you
actually write must match it or `validate.py` warns `W_COLUMN_STRUCTURE_MISMATCH`. Divi will
render by the columns' own `type` attributes regardless — `column_structure` just has to describe
them accurately so the Visual Builder shows the same layout.

**`et_pb_row`** — 20 legal values:

| `column_structure` | column `type`s |
|---|---|
| `4_4` | `4_4` |
| `1_2,1_2` | `1_2`, `1_2` |
| `1_3,1_3,1_3` | `1_3`, `1_3`, `1_3` |
| `1_4,1_4,1_4,1_4` | `1_4`, `1_4`, `1_4`, `1_4` |
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

**`et_pb_row_inner`** — 4 legal values (a narrower set; used inside a specialty section's
specialty column):

| `column_structure` | column `type`s |
|---|---|
| `4_4` | `4_4` |
| `1_2,1_2` | `1_2`, `1_2` |
| `1_3,1_3,1_3` | `1_3`, `1_3`, `1_3` |
| `1_4,1_4,1_4,1_4` | `1_4`, `1_4`, `1_4`, `1_4` |

An unrecognized `column_structure` value is `E_COLUMN_STRUCTURE`; a column `type` that isn't one of
the fractions above (used anywhere, with or without `column_structure` set) is `E_COLUMN_TYPE`.

## Parent → child pairs

Ten modules have exactly one child slug they may contain (structural section/row/column pairs use
their own rules above, not this table). Generated with:

```
PYTHONPATH=Skill/divi-page-builder/scripts python3 -c "from divi_schema import load_schema; s=load_schema(); print([(x, s.module(x).child) for x in s.slugs if s.module(x).child])"
```

| parent | child |
|---|---|
| `et_pb_accordion` | `et_pb_accordion_item` |
| `et_pb_contact_form` | `et_pb_contact_field` |
| `et_pb_counters` | `et_pb_counter` |
| `et_pb_fullwidth_map` | `et_pb_map_pin` |
| `et_pb_fullwidth_slider` | `et_pb_slide` |
| `et_pb_map` | `et_pb_map_pin` |
| `et_pb_pricing_tables` | `et_pb_pricing_table` |
| `et_pb_row` | `et_pb_column` |
| `et_pb_row_inner` | `et_pb_column_inner` |
| `et_pb_signup` | `et_pb_signup_custom_field` |
| `et_pb_slider` | `et_pb_slide` |
| `et_pb_social_media_follow` | `et_pb_social_media_follow_network` |
| `et_pb_tabs` | `et_pb_tab` |
| `et_pb_video_slider` | `et_pb_video_slider_item` |

Putting anything else inside one of these parents is `E_BAD_CHILD`; putting one of the ten child
modules (`et_pb_accordion_item`, `et_pb_contact_field`, `et_pb_counter`, `et_pb_map_pin`,
`et_pb_pricing_table`, `et_pb_signup_custom_field`, `et_pb_slide`,
`et_pb_social_media_follow_network`, `et_pb_tab`, `et_pb_video_slider_item`) anywhere other than
directly inside its listed parent is `E_CHILD_PLACEMENT`.

## Fullwidth-only modules

These ten modules (`fullwidth: true` in the schema) may only appear directly inside
`[et_pb_section fullwidth="on"]`, never inside a column:

`et_pb_fullwidth_code`, `et_pb_fullwidth_header`, `et_pb_fullwidth_image`, `et_pb_fullwidth_map`,
`et_pb_fullwidth_menu`, `et_pb_fullwidth_portfolio`, `et_pb_fullwidth_post_content`,
`et_pb_fullwidth_post_slider`, `et_pb_fullwidth_post_title`, `et_pb_fullwidth_slider`.

## Module numbering

Divi assigns each module on a page a running number per tag — `et_pb_text_0`, `et_pb_text_1`,
`et_pb_heading_0`, ... — visible in generated CSS selectors (a module's `main_css_element` is
usually `%%order_class%%`, which expands to `.et_pb_<slug>_<N>`) and in the ordinal classes seen
in rendered HTML (`et_pb_section_0`, `et_pb_column_3`, etc., as seen in experiment 4). **This
number is assigned at render time from the module's position in the tree — it is never stored in
`post_content`, and it shifts whenever you add, remove, or reorder modules before it.** Do not
write CSS (in `custom_css_*`, or off-page) that targets `.et_pb_text_3` and expect it to survive an
edit. Instead:

- give the module a stable identifier with `module_class="my-stable-name"` or `module_id="..."`
  (from the CSS ID & classes family — [design-families.md](design-families.md#css-id-and-classes))
  and target `.my-stable-name` instead; or
- use that module's own `custom_css_*` fields, which are scoped to the module itself and don't
  need a selector at all.

## Structural validator codes

Every error/warning `check_structure()` (`Skill/divi-page-builder/scripts/divi_checks_structure.py`)
can raise, in the order it can fire, with a one-line fix:

| code | level | meaning | fix |
|---|---|---|---|
| `E_UNCLOSED` | error | a `[et_pb_*]` tag is never closed (parser-level, from `divi_shortcode.parse`) | add the matching `[/et_pb_*]`, in the right place relative to any tag it wraps. |
| `E_STRAY_CLOSE` | error | a `[/et_pb_*]` has no matching opening tag (parser-level) | remove the stray closing tag, or add the opening tag it belongs to. |
| `E_TEXT_OUTSIDE_SECTION` | error | non-blank text sits outside every `et_pb_section` at the top level | delete it, or move it inside a text module inside a section. |
| `E_TOP_LEVEL` | error | a tag other than `et_pb_section` appears at the top level | wrap it in `et_pb_section` → `et_pb_row` → `et_pb_column` (or a fullwidth section, if it's a fullwidth module). |
| `E_UNKNOWN_TAG` | error | the tag isn't a Divi 4 module slug this schema knows | check the spelling against `reference/modules/README.md`; Divi 5 block markup and made-up slugs both land here. |
| `E_CHILD_PLACEMENT` | error | a "child kind" module (e.g. `et_pb_accordion_item`) sits outside its required parent | move it directly inside the parent listed in the Parent → child table above. |
| `E_STRAY_TEXT` | error | non-blank text sits directly inside a section/row/column (which don't render text of their own) | move the text into a text module. |
| `E_FULLWIDTH_CHILD` | error | a fullwidth section (`fullwidth="on"`) contains a non-fullwidth module | replace it with the fullwidth equivalent, or move it to a regular/specialty section instead. |
| `E_SECTION_CHILD` | error | a regular section contains something other than `et_pb_row`, or a specialty section contains something other than `et_pb_column` | fix the section's children to match its type (regular → rows only, specialty → columns only). |
| `E_SPECIALTY_COLUMN` | error | a specialty section doesn't have exactly one column with `specialty_columns` set | add `specialty_columns="…"` to exactly one column (see experiment 5's table for the legal value per layout). |
| `E_SPECIALTY_CONTENT` | error | the specialty column (the one with `specialty_columns`) contains something other than `et_pb_row_inner` | move non-`et_pb_row_inner` content to a different (non-specialty) column, or wrap it in `et_pb_row_inner` → `et_pb_column_inner`. |
| `E_ROW_CHILD` | error | `et_pb_row`/`et_pb_row_inner` contains something other than `et_pb_column`/`et_pb_column_inner` | move the offending module inside a column. |
| `E_COLUMN_STRUCTURE` | error | `column_structure` is set to a value that isn't legal for that tag | use one of the values in the `column_structure` tables above. |
| `E_COLUMN_TYPE` | error | a column's `type` isn't a legal fraction | use one of `4_4`, `1_2`, `1_3`, `2_3`, `1_4`, `3_4`, `1_5`, `2_5`, `3_5`, `1_6`. |
| `E_COLUMN_SUM` | error | a row's column `type` fractions don't add up to 1 | fix the column widths so they sum to a whole row, or add/remove a column. |
| `W_COLUMN_STRUCTURE_MISMATCH` | warning | the columns you wrote don't match the `column_structure` you declared | make `column_structure` list the columns' actual `type`s in order (or drop `column_structure` and let it default). |
| `E_INNER_ROW_PLACEMENT` | error | `et_pb_row_inner` appears somewhere other than a specialty section's specialty column | move it inside the one column that has `specialty_columns` set, inside a `specialty="on"` section. |
| `E_COLUMN_CHILD` | error | a structural element (section/row/column) is nested directly inside a column | only modules (and `et_pb_row_inner`, in a specialty column) belong directly inside a column. |
| `E_FULLWIDTH_IN_COLUMN` | error | a fullwidth-only module is placed inside a regular column | move it to `[et_pb_section fullwidth="on"]` instead. |
| `E_BAD_CHILD` | error | a module with exactly one legal child slug (see the Parent → child table) contains something else | replace the offending tag with the module's actual child slug. |
| `E_NESTED_MODULE` | error | any other module has something nested inside it (leaf modules can't contain modules at all) | remove the nested tag, or move it to sit alongside the leaf module instead of inside it. |
