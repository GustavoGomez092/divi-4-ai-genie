# Experiments backing `reference/page-format.md`, `reference/structure.md`, `reference/value-formats.md`

All commands run from the repo root against the LocalWP site `divi-test.local` (Divi 4.27.9),
via `research/tools/wp-local.sh`. Divi source is read from
`~/Local Sites/divi-test/app/public/wp-content/themes/Divi` (read-only; never modified). Every
test page created below was titled `Plan Test: …` and deleted immediately after use; page 11 was
never touched.

## 1. Custom CSS newlines are stored as `||`

Command:

```
export DIVI="$HOME/Local Sites/divi-test/app/public/wp-content/themes/Divi"
grep -n "replace( /\\\\|\\\\|/g" "$DIVI/includes/builder/class-et-builder-element.php"
```

Observation: four hits, two in the Visual Builder's field-template generator and two in the
per-column custom-CSS template:

- `includes/builder/class-et-builder-element.php:11596` and `:11653` — the generic per-module
  custom-CSS field template builds its live-preview JS as
  `'.replace( /\|\|/g, "\n" ).replace( /%22/g, "&quot;" ).replace( /%92/g, "\\\" )'` — i.e. the
  textarea shown to the author is built by turning the *stored* attribute's `||` into real
  newlines (and un-escaping `%22`/`%92`) for display.
- `includes/builder/class-et-builder-element.php:24209`, `:24223`, `:24237` — the same
  `.replace( /\|\|/g, "\n" )` call for the three per-column custom-CSS textareas
  (`custom_css_before`/`custom_css_main`/`custom_css_after` on `et_pb_column`).

Conclusion: a multi-line `custom_css_*` value is saved in shortcode as a single line with `||`
standing in for each newline (in addition to the usual `%22`/`%92` escaping for literal `"`/`\`).
Authoring a two-line rule as `a: 1;||b: 2;` is equivalent to what the Visual Builder saves for two
lines of CSS. No test page was needed; this is a static, unconditional string transform in Divi's
own JS templates, not something that varies at runtime.

## 2. The `<` rule corrupts, rather than just emptying, the surrounding shortcode

Command:

```
research/tools/wp-local.sh post create --post_type=page \
  --post_title="Plan Test: lt-rule" --post_status=publish \
  --post_content='[et_pb_section _builder_version="4.27.9" _module_preset="default"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="a < b" _builder_version="4.27.9" _module_preset="default"][/et_pb_heading][/et_pb_column][/et_pb_row][/et_pb_section]' \
  --porcelain
research/tools/wp-local.sh post meta update <id> _et_pb_use_builder on
research/tools/wp-local.sh post meta update <id> _et_pb_page_layout et_full_width_page
curl -sL "http://divi-test.local/?page_id=<id>"
```

Observation: the raw `post_content` in the database kept the literal `title="a < b"` untouched
(confirmed with `wp post get <id> --field=post_content`) — nothing strips it at save time. But the
rendered page was **not** "heading renders empty" as such; it was worse: the section/row/column
divs rendered as empty containers and then the entire remainder of the shortcode string —
starting at `[et_pb_heading title=...]` and including its own closing tag and the row/column/
section closers that were supposed to close the *earlier* tags — was dumped as **literal,
unprocessed text** after the column's closing `</div>`:

```
...</div>[et_pb_heading title=&#8221;a < b" _builder_version="4.27.9" _module_preset="default"][/et_pb_heading][/et_pb_column][/et_pb_row][/et_pb_section]		</div>
```

Isolating the cause: `the_content`'s filter chain runs `wptexturize` and `wpautop` (priority 10)
*before* `do_shortcode` (also priority 10, registered after) and before Divi's own
`et_pb_fix_builder_shortcodes` cleanup. Running `wptexturize()` alone on the raw content shows
exactly where it breaks:

```
wptexturize($c):
[et_pb_section _builder_version=&#8221;4.27.9&#8243; ... ][et_pb_heading title=&#8221;a < b" _builder_version="4.27.9" _module_preset="default"][/et_pb_heading]...
```

Every straight `"` **before** the bare `<` gets converted to a curly quote (`&#8221;`/`&#8243;`);
every `"` **after** the `<` is left alone. `wptexturize()` treats the unmatched `<` as the start
of an HTML tag and stops tracking quote pairs from that point on, which desyncs the attribute
parsing that runs afterward. Divi's shortcode-tree builder then can no longer find where the
inner `et_pb_heading` shortcode (and the tags that should close *after* it) actually begin, so it
gives up and treats the rest of the string as plain text glued onto the end of the container that
was open at the point of failure.

Conclusion: `E_ATTR_LT` is correctly conservative — a raw `<` in *any* shortcode attribute value is
not merely "that one attribute becomes empty," it can silently corrupt the parse of everything
after it in the same section, leaving broken markup and unrendered shortcode text on the live
page. The fix is the one the validator already suggests: never write a bare `<` in an attribute
value; use `&lt;` (in HTML content) or rephrase.

Cleanup: `research/tools/wp-local.sh post delete <id> --force`.

## 3. Global colors: two different `gcid-` shapes, both real

Command:

```
export DIVI="$HOME/Local Sites/divi-test/app/public/wp-content/themes/Divi"
grep -rn "gcid-" "$DIVI/includes/builder" --include=*.php | head
```

Observation (resolution, `includes/builder/class-et-builder-element.php:13470-13499`, and the
duplicate hover-attrs path at `includes/builder/functions.php:11609-11630`): for any attribute
whose *name* contains `color` (and isn't `global_colors_info` itself), if its *value* contains the
literal substring `gcid-…`, Divi looks up `et_builder_get_all_global_colors(true)` and does a
plain `str_replace($gcid, $details['color'], ...)` — a substring replace, not an exact-match
replace, specifically so it also works inside composite values such as gradient stops. If the
value doesn't contain `gcid-`, this code path is skipped entirely and the value is used as-is.

`global_colors_info`'s shape, confirmed two ways:

- From `_prepare_global_colors_info()` (`class-et-builder-element.php:13391-13431`): it's a JSON
  object, `{ "<key>": [...attribute names...], ... }`, saved with `wp_json_encode()` and escaped
  in shortcode the same way as any other attribute (`%91`→`[`, `%93`→`]`, `%22`→`"`, confirmed
  identically in `research/tools/notes/escaping.md`; direct `str_replace`, no HTML-entity round
  trip, at `class-et-builder-element.php:4003`).
- Two real shapes appear in the required fixtures:
  - **True global colors** (`tests/fixtures/valid/divi-ai-section.txt`): the key *is* the
    `gcid-<uuid>` id used as the color attribute's value, e.g.
    `global_colors_info="{%22gcid-36fd78a7-34bc-404d-873c-dafa34efaae5%22:%91%22button_text_color%22,%22button_text_color%22,...%93}"`
    — decodes to `{"gcid-36fd78a7-...": ["button_text_color", "button_text_color", ...]}`. The
    array can repeat the same attribute name more than once (observed 6 times here); this appears
    to be one entry per state/breakpoint slot the color is applied to under that same base field
    name, not a deduplicated set.
  - **Inline/"smart" colors, no true global color defined**
    (`tests/fixtures/valid/divi-ai-layout-skeleton.txt`): the key is the literal hex value itself,
    e.g. `global_colors_info="{%22#F97316%22:%91%22background_color%22%93}"` — decodes to
    `{"#F97316": ["background_color"]}`. Because the value never contains `gcid-`, the
    color-resolution code above never fires for it: `#F97316` renders as `#F97316`.
    `global_colors_info` here is purely informational bookkeeping (used by the Visual Builder's
    bulk-recolor tooling), not a live reference.

Conclusion: `gcid-<uuid>` is the only value that Divi actually *resolves* to a color at render
time; a `global_colors_info` entry keyed by a literal hex/rgba value is legal and appears in
real (AI-generated) content, but it's inert — changing that entry's value does nothing to the
page. `tokens.json`'s `colors.global` map (see `tests/fixtures/tokens-min.json`) uses human-
readable `gcid-brand`-style ids, which is a slug convention for that map, not evidence that
Divi's real UUIDs are ever readable — real ids are UUIDs like the one above.

## 4. Section types: `fullwidth`/`specialty` markup, and the specialty-column width scaling

Command:

```
research/tools/wp-local.sh post create --post_type=page \
  --post_title="Plan Test: section-types" --post_status=publish \
  --post_content="$(cat tests/fixtures/valid/handwritten-landing.txt)" --porcelain
research/tools/wp-local.sh post meta update <id> _et_pb_use_builder on
research/tools/wp-local.sh post meta update <id> _et_pb_page_layout et_full_width_page
curl -sL "http://divi-test.local/?page_id=<id>" | grep -o 'class="et_pb_section[^"]*"'
```

Observation:

```
class="et_pb_section et_pb_section_0 et_pb_with_background et_section_regular"   <- plain section
class="et_pb_section et_pb_section_1 et_section_regular"                          <- plain section
class="et_pb_section et_pb_section_2 et_section_specialty"                        <- specialty="on"
class="et_pb_section et_pb_section_3 et_pb_fullwidth_section et_section_regular"  <- fullwidth="on"
```

confirming: every section always carries `et_section_regular` **or** `et_section_specialty`
(never both); `fullwidth="on"` adds the extra `et_pb_fullwidth_section` class on top of
`et_section_regular` (a fullwidth section is not a third "type" at the section-class level — it's
a regular section whose child isn't `et_pb_row`). The specialty column got
`class="... et_pb_specialty_column ..."`, and its nested `et_pb_row_inner`'s columns rendered as
`et_pb_column_3_8` / `et_pb_column_3_8` — **not** `et_pb_column_1_2` as written
(`column_structure="1_2,1_2"` on the `et_pb_row_inner`). 3/8 = (1/2) × (3/4): the inner row's
column *fractions* are scaled by the specialty column's own width (`type="3_4"`) for the rendered
CSS class, even though the `column_structure`/`type` attributes you author stay relative to the
inner row itself (`1_2,1_2`), not to the page.

Conclusion: confirms `E_SECTION_CHILD`'s two extra section shapes structurally (fullwidth sections
skip the row/column layer entirely; specialty sections contain only `et_pb_column`s, exactly one
of which holds `et_pb_row_inner`s) and documents the width-scaling behavior as a "don't be
surprised" note for `structure.md`'s specialty-section example.

Cleanup: `research/tools/wp-local.sh post delete <id> --force`.

## 5. Legal specialty column arrangements and their `specialty_columns` values

Command:

```
export DIVI="$HOME/Local Sites/divi-test/app/public/wp-content/themes/Divi"
grep -o "specialty[^,]*columns[^}]*" "$DIVI/includes/builder/frontend-builder/build/bundle.js" | head
```

That grep (matching the brief) only turned up minified JS fragments, not the layout table itself;
the actual table lives in the un-minified `includes/builder/functions.php`, in
`et_builder_get_columns_layout()`'s `<li data-layout="..." data-specialty="..."
data-specialty_columns="...">` markup (lines 6197–6349) plus the (partially self-overwriting, see
below) PHP array in `et_builder_get_columns()` (lines 6128–6156). Observation — every legal
specialty `column_structure` for `et_pb_row`, which column is "the" specialty column (the one that
takes `specialty_columns` and holds `et_pb_row_inner`), and that column's `specialty_columns`
value:

| `column_structure` | specialty column | `specialty_columns` |
|---|---|---|
| `1_2,1_2` | column 0 (first) | `3` |
| `1_2,1_2` | column 1 (second) | `3` |
| `1_4,3_4` | column 1 (`3_4`) | `3` |
| `3_4,1_4` | column 0 (`3_4`) | `3` |
| `1_4,1_2,1_4` | column 1 (middle, `1_2`) | `3` |
| `1_2,1_4,1_4` | column 0 (`1_2`) | `3` |
| `1_4,1_4,1_2` | column 2 (last, `1_2`) | `3` |
| `1_3,2_3` | column 1 (`2_3`) | `4` |
| `2_3,1_3` | column 0 (`2_3`) | `4` |

(`handwritten-landing.txt`'s specialty section uses the `1_4,3_4` row exactly: `type="1_4"` then
`type="3_4" specialty_columns="3"`, matching experiment 4's render.)

`specialty_columns` is not "how many columns" (both `1_2,1_2` and `1_4,1_2,1_4` share the value
`3`); it looks like an internal layout-profile id, not a value our validator needs to cross-check
against `column_structure` — the validator only checks that *exactly one* column in a specialty
section sets `specialty_columns` at all (`E_SPECIALTY_COLUMN`), which is the part of this table
that generalizes.

Also note (`et_builder_get_columns()`, lines 6133–6136): the PHP array literal defines the key
`'1_2,1_2'` twice with different `position` values; PHP silently keeps only the second
(`0,1`) in that array. The two `1_2,1_2` variants (`3,0` and `0,1`, i.e. either column can be the
specialty one) are still both real and both offered in the UI — they just live in the separate
`et_builder_get_columns_layout()` template, which the array above doesn't gate.

Conclusion: recorded verbatim in `structure.md`'s specialty-section section, with the same
citations.
