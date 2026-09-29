# Stats counters

**Use for:** a short "by the numbers" band of 3-4 large counters (years in business, jobs
completed, average response time) that builds credibility through scale. · **SEO:** no heading
required by the pattern itself, though an `h2` may introduce it on a longer page; each counter's
`title` renders as a heading (`title_level`, default `h3`), so the band must sit below an `h2` for the
outline not to skip a level. **Data note — never invent these numbers.** The figures below (`15`, `5000`, `24`,
`100`) are illustrative placeholders for `sample-tokens.json`'s fictional brand only. On a real
client site, every number in this section must come from the client's own brief or fact sheet — do
not estimate, round up, or fabricate a statistic to fill the pattern.

## Structure
```text
section (By The Numbers, light tone)
└─ row column_structure="1_4,1_4,1_4,1_4"
   ├─ column 1_4: number counter
   ├─ column 1_4: number counter
   ├─ column 1_4: number counter
   └─ column 1_4: number counter
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `section_exemplars[admin_label=By The Numbers].attrs.background_color` | `colors.palette[5].hex` (`#f1f5f9`) |
| section `custom_padding` (+`_tablet`/`_phone`) | `section_exemplars[admin_label=By The Numbers].attrs.custom_padding` (+`_tablet`/`_phone`) | `spacing.section_padding[0][0]` |
| row `column_structure` | this pattern's own 4-up default; the exemplar uses `"1_2,1_2"` for 2 counters, so widen to `"1_4,1_4,1_4,1_4"` for 4 | `"1_4,1_4,1_4,1_4"` |
| counter `number_font`, `number_text_color`, `number_font_size` | `module_styles.et_pb_number_counter[section_tone=light,column_type=1_2].attrs` (`number_font`/`number_text_color`/`number_font_size`) — the same bundle applies regardless of the row's actual column count, since it's keyed on tone, not width | `typography.scale.h1.font` (for the bold numeral weight) + `colors.customizer.heading` + `typography.scale.h1.size` |
| counter `title_font`, `title_text_color`, `title_font_size` | the same bundle's `title_font`/`title_text_color`/`title_font_size` | `typography.body_font` + `colors.customizer.body_text` + `colors.customizer.body_size` |
| counter `percent_sign` | not a token — set per counter based on what the number represents (`"off"` for a count or a time value, `"on"` only for an actual percentage) | — |
| counter `number`, `title` | the client's brief/fact sheet — **never** a token, and never invented (see the note above) | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_row`](../../reference/modules/et_pb_row.md)
`column_structure="1_4,1_4,1_4,1_4"`; [`et_pb_column`](../../reference/modules/et_pb_column.md)
`type="1_4"`; [`et_pb_number_counter`](../../reference/modules/et_pb_number_counter.md) `number`,
`title`, `percent_sign`, `number_font`, `number_text_color`, `number_font_size`, `title_font`,
`title_text_color`, `title_font_size`.

Optional: `admin_label` on the section; `title_level` on each counter (default `h3` — leave it
unless the surrounding page outline needs otherwise); `link_option_url` to make an individual
counter clickable (e.g. a "jobs completed" counter linking to a reviews page).

## Responsive rules

`number_font_size` should get `_tablet`/`_phone` values (e.g. 56px → 40px → 32px) plus
`number_font_size_last_edited="on|phone"` so four large numerals don't force horizontal cramping
once the row stacks to two-per-line on tablet and one-per-line on phone. The section's
`custom_padding` needs its usual `_tablet`/`_phone` pair. The row's `column_structure` needs no
phone-specific value: Divi stacks all four counters to full width automatically.

## Variations

- **Three-counter variant:** `column_structure="1_3,1_3,1_3"` with three counters instead of four —
  nothing else changes.
- **Percentage counter:** for a genuine percentage stat (e.g. "98% satisfaction rate" from a real
  survey the client provides), set `percent_sign="on"` and give `number` the bare numeral (`98`,
  not `98%`) — Divi appends the `%` itself.
- **Dark-tone variant:** swap the section to the dark navy bundle and re-pick the counter's
  `number_text_color`/`title_text_color` for contrast against it (e.g. white numerals, light-gray
  titles) — every token lookup above changes with the new tone.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="By The Numbers" _builder_version="4.27.9" _module_preset="default" background_color="#f1f5f9" custom_padding="70px||70px||true|false" custom_padding_tablet="50px||50px||true|false" custom_padding_phone="40px||40px||true|false" custom_padding_last_edited="on|phone"][et_pb_row column_structure="1_4,1_4,1_4,1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_number_counter number="15" title="Years in Business" percent_sign="off" _builder_version="4.27.9" _module_preset="default" number_font="Montserrat|700|||||||" number_text_color="#0b2a3c" number_font_size="56px" number_font_size_tablet="40px" number_font_size_phone="32px" number_font_size_last_edited="on|phone" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_number_counter][/et_pb_column][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_number_counter number="5000" title="Jobs Completed" percent_sign="off" _builder_version="4.27.9" _module_preset="default" number_font="Montserrat|700|||||||" number_text_color="#0b2a3c" number_font_size="56px" number_font_size_tablet="40px" number_font_size_phone="32px" number_font_size_last_edited="on|phone" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_number_counter][/et_pb_column][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_number_counter number="24" title="Hour Emergency Response" percent_sign="off" _builder_version="4.27.9" _module_preset="default" number_font="Montserrat|700|||||||" number_text_color="#0b2a3c" number_font_size="56px" number_font_size_tablet="40px" number_font_size_phone="32px" number_font_size_last_edited="on|phone" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_number_counter][/et_pb_column][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_number_counter number="100" title="Satisfaction Guarantee" percent_sign="on" _builder_version="4.27.9" _module_preset="default" number_font="Montserrat|700|||||||" number_text_color="#0b2a3c" number_font_size="56px" number_font_size_tablet="40px" number_font_size_phone="32px" number_font_size_last_edited="on|phone" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_number_counter][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — show the user `preview.html` (or `preview.py serve`) and **stop until they approve it**; fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] Only after the user approves the local preview: `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] no `h1`/`h2` introduced by this section itself (counter titles are plain text, not headings)
- [ ] every number in this section, on a real page, traces back to the client's brief — none invented
