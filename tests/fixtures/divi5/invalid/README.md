# Invalid Divi 5 fixtures

Each page is built from the section of `converted/unicode.html` (section → row → column → heading + text,
inside `divi/placeholder`) and changed so that exactly one validator error appears.
`tests/test_divi5_validate_structure.py` checks the structure and heading codes below, and
`tests/test_divi5_validate_values.py` the attribute/value ones (the rows from `unknown-attr.html` on). The
attribute/value pages were written with `divi5_blocks.canonical_json`, so the JSON is WordPress-canonical
except where the change is the point (`noncanonical-lt.html`). The last five rows are warnings: those pages have
no error at all.

| File | Expected code | What was changed |
|---|---|---|
| `mixed.html` | `E5_MIXED_FORMAT` | Divi 4 shortcode section appended after the block page |
| `bad-json.html` | `E5_BAD_JSON` | trailing comma in the text module's attribute JSON |
| `unclosed.html` | `E5_UNCLOSED` | `<!-- /wp:divi/placeholder -->` removed |
| `unknown-block.html` | `E5_UNKNOWN_BLOCK` | text module renamed `divi/fancy-text` |
| `text-in-section.html` | `E5_BAD_PARENT` | text module moved out of the column, directly into the section |
| `row-at-top.html` | `E5_TOPLEVEL` | a row placed directly inside the placeholder |
| `fullwidth-with-row.html` | `E5_SECTION_TYPE` | section `module.advanced.type` set to `fullwidth`, still holding a row |
| `columns-mismatch.html` | `E5_COLUMNS` | row `columnStructure` `1_2,1_2` over columns `1_3`, `2_3` |
| `two-h1.html` | `E5_MULTIPLE_H1` | second section with another `headingLevel: h1` heading |
| `freeform.html` | `E5_NOT_DIVI` | plain text between the section and the placeholder close |
| `specialty-no-specialty-column.html` | `E5_SPECIALTY_COLUMN` | specialty section of two module columns, none with `module.advanced.specialtyColumns` |
| `inner-row-misplaced.html` | `E5_INNER_ROW_PLACEMENT` | a `divi/row-inner` inside a regular row's column |
| `unknown-attr.html` | `E5_UNKNOWN_ATTR` | heading gets an attribute `titel.innerContent` (typo of `title`) |
| `bad-breakpoint.html` | `E5_BAD_BREAKPOINT` | heading `title.innerContent` gets a `mobile` breakpoint beside `desktop` |
| `bad-state.html` | `E5_BAD_STATE` | heading `title.innerContent` gets a `desktop.sticky` value (the leaf takes value/hover) |
| `bad-color.html` | `E5_BAD_VALUE` | text `content.decoration.bodyFont.body.font` color `#12345` (5 hex digits) |
| `bad-unit.html` | `E5_BAD_VALUE` | heading title font size `40pz` |
| `bad-enum.html` | `E5_BAD_VALUE` | heading title font `headingLevel` `h7` |
| `bad-variable.html` | `E5_BAD_VARIABLE` | text body font color `$variable({"type":"color","value":{"settings":{}}})$` (no `value.name`) |
| `noncanonical-lt.html` | `E5_NONCANONICAL` | text innerContent JSON with raw `<` / `>` instead of `\u003c` / `\u003e` |
| `unitless-length.html` | `E5_UNITLESS_LENGTH` | text `module.decoration.spacing` padding `{"top": 41, "bottom": "42px"}` (a JSON number: Divi prints `padding-top:41`) |
| `gradient-disabled.html` | `E5_GRADIENT_DISABLED` | section background `gradient` with type, direction and stops but no `"enabled": "on"` |
| `gradient-stop-position.html` | `E5_GRADIENT_STOP_POSITION` | section background gradient (enabled) with stop positions `"0%"` / `"100%"` |
| `unknown-preset.html` | `W5_UNKNOWN_PRESET` | heading `modulePreset` `["doesnotexist"]` |
| `shortcode-brackets.html` | `W5_SHORTCODE_BRACKETS` | text innerContent `<p>See [gallery] for photos.</p>` |
| `bare-font.html` | `W5_BARE_FONT` | heading title font (`headingLevel`, `size`, `color`) written on the bare `title.decoration.font` instead of `title.decoration.font.font` |
| `legacy-attr.html` | `W5_LEGACY_ATTR` | row gets the Divi 4 conversion attribute `columns.column-1.spacing` |

Specialty sections follow the Divi 4 rules exactly, with codes named after Divi 4's:
`E5_SPECIALTY_COLUMN` (Divi 4 `E_SPECIALTY_COLUMN`) = a specialty section needs exactly one column with
`module.advanced.specialtyColumns`; `E5_INNER_ROW_PLACEMENT` (Divi 4 `E_INNER_ROW_PLACEMENT`) = `divi/row-inner`
only inside that column of a specialty section. Other content in the specialty column, and non-column children
of a specialty section, are `E5_SECTION_TYPE`.
| `no-effect.html` | `W5_NO_EFFECT` | heading font moved to `title.decoration.font.font`; a `builderVersion` 5.13.1 blurb added whose icon size is written on `imageIcon.advanced.width` (renders nothing on Divi 5.13.1; the size goes in `imageIcon.decoration.sizing` → `iconFontSize`) |
