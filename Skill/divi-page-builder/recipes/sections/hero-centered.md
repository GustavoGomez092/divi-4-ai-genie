# Hero centered

**Use for:** a simpler above-the-fold hero with no supporting photo — a centered headline, short
pitch and single call to action, for a page that doesn't have (or doesn't need) hero art. · **SEO:**
exactly one `h1` per page; this section supplies it.

## Structure
```text
section (Hero, dark tone)
└─ row column_structure="4_4"
   └─ column 4_4: text (eyebrow) · heading (h1) · text (body) · button — all centered, 720px wide
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `section_exemplars[admin_label=Hero].attrs.background_color` | `colors.palette[0].hex` |
| section `custom_padding` (+`_tablet`/`_phone`) | `section_exemplars[admin_label=Hero].attrs.custom_padding` (+`_tablet`/`_phone`) | `spacing.section_padding[0][0]` |
| row `width`, `max_width` | no bundle matches a single `4_4` column on a dark section — use the generic `spacing.row.width` / `spacing.row.max_width` | same |
| eyebrow text `text_font`, `text_text_color`, `text_font_size` | no eyebrow bundle in tokens — build one from `typography.heading_font` + `"\|600\|\|on\|\|\|\|\|"` and `colors.customizer.accent` | same |
| heading `title_font`, `title_text_color`, `title_font_size` (+`_tablet`/`_phone`) | no `column_type=4_4` dark-tone `h1` bundle exists, so read straight off `typography.scale.h1.font` / `.color` / `.size` (+`.size_tablet`/`.size_phone`) | same |
| body text `text_font`, `text_text_color`, `text_font_size` | `module_styles.et_pb_text[section_tone=dark,column_type=4_4].attrs` — the only bundle whose tone **and** column type both match, even though its `section_label` is "Free Quote CTA" (§2 of the README: match tone + column_type first) | `typography.body_font` + `colors.customizer.body_text` |
| button `custom_button`, `button_bg_color`, `button_bg_color__hover`(`_enabled`), `button_text_color`, `button_border_radius`, `preset` | `module_styles.et_pb_button[section_tone=dark,column_type=4_4].attrs` + its `preset` UUID (same tone+column_type match as the body text above) | `colors.customizer.accent` + `shapes.radii[0][0]`, preset `"default"` |
| button `button_font` | `colors.customizer.body_font` | `typography.body_font` (`Lato||||||||`) |
| text block width | fixed `max_width="720px"` + `module_alignment="center"` on each text-bearing module — a layout choice, not a token |  — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_row`](../../reference/modules/et_pb_row.md)
`column_structure="4_4"`, `width`, `max_width`;
[`et_pb_column`](../../reference/modules/et_pb_column.md) `type="4_4"`;
[`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`, `title_level="h1"`,
`title_font`, `title_text_color`, `title_font_size` (+responsive), `title_text_align="center"`,
`max_width="720px"`, `module_alignment="center"`; one
[`et_pb_text`](../../reference/modules/et_pb_text.md) with `content`, `text_font`,
`text_text_color`, `text_font_size`, `text_orientation="center"`, `max_width="720px"`,
`module_alignment="center"`; [`et_pb_button`](../../reference/modules/et_pb_button.md)
`button_text`, `button_url`, `custom_button="on"`, `button_bg_color`, `button_text_color`,
`button_border_radius`, `button_bg_color__hover` (+`_enabled`), `button_font`,
`button_alignment="center"`.

Optional: `admin_label` on the section; a second, "eyebrow" `et_pb_text` above the heading (also
centered, `max_width="720px"`, `module_alignment="center"`); `_module_preset` on the button, when
the site has a reusable button preset like this one's.

## Responsive rules

`title_font_size` needs `_tablet`/`_phone` (56px → 42px → 34px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs `_tablet`/`_phone`
(96px → 64px → 48px) plus `custom_padding_last_edited="on|phone"`. `max_width="720px"` needs no
responsive variant — it already shrinks to fit a narrow column since it's a *maximum*, not a fixed
width.

## Variations

- **Narrower/wider copy block:** change the `max_width="720px"` on the text modules (e.g. `600px`
  for punchier copy, `880px` for a longer pitch) — nothing else changes.
- **Add a second button:** place a second `et_pb_button` beside the first inside the same column;
  give both `button_alignment="center"` and rely on `module_class` if the two need a gap.
- **Light-tone variant:** swap the section to a light-tone background bundle
  (`module_styles.et_pb_section` with a light `background_color`) and re-pick the heading/body/
  button bundles by that new tone — every token lookup above changes with it.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Hero" _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" custom_padding="96px||96px||true|false" custom_padding_tablet="64px||64px||true|false" custom_padding_phone="48px||48px||true|false" custom_padding_last_edited="on|phone"][et_pb_row column_structure="4_4" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Eyebrow" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|600||on|||||" text_text_color="#f97316" text_font_size="14px" text_letter_spacing="2px" text_orientation="center" max_width="720px" module_alignment="center"]<p>24/7 Emergency Plumbing</p>[/et_pb_text][et_pb_heading title="Miami's Fastest Emergency Plumbers" title_level="h1" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#ffffff" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone" title_line_height="1.1em" title_text_align="center" max_width="720px" module_alignment="center"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#f1f5f9" text_font_size="18px" text_line_height="1.7em" text_orientation="center" max_width="720px" module_alignment="center"]<p>Licensed, insured plumbers dispatched anywhere in Miami-Dade, day or night.</p>[/et_pb_text][et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="11111111-2222-3333-4444-555555555555" button_font="Lato||||||||" custom_button="on" button_text_color="#0b2a3c" button_bg_color="#f97316" button_border_radius="6px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_alignment="center"][/et_pb_button][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one H1 on the page
- [ ] every image has alt text and a Media Library URL
