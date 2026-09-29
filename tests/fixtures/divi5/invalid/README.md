# Invalid Divi 5 fixtures

Each page is built from the section of `converted/unicode.html` (section → row → column → heading + text,
inside `divi/placeholder`) and changed so that exactly one validator error appears.
`tests/test_divi5_validate_structure.py` checks the codes below.

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
