# Services grid

**Use for:** a three- or four-up overview of the business's core services, each with an icon,
short pitch and a link into that service's own page. · **SEO:** exactly one `h2` introduces the
section, and every blurb title is an `h3` beneath it — never skip to `h4` or repeat `h2`. Give each
`et_pb_blurb` a `url` pointing at that service's own page: this is the internal-linking backbone
that tells search engines (and visitors) which pages on the site are the authoritative ones for
"drain cleaning," "water heater repair," and so on, so don't leave `url` blank when a service page
exists.

## Structure
```text
section (Why Choose Us / Services, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row column_structure="1_3,1_3,1_3"
   ├─ column 1_3: blurb (icon, title h3, body, url → service page)
   ├─ column 1_3: blurb (icon, title h3, body, url → service page)
   └─ column 1_3: blurb (icon, title h3, body, url → service page)
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `section_exemplars[admin_label=Why Choose Us].attrs.background_color` | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | `section_exemplars[admin_label=Why Choose Us].attrs.custom_padding` (+`_tablet`/`_phone`) | `spacing.section_padding[2][0]` (`"90px\|\|90px\|\|true\|false"`) |
| heading row `et_pb_row` | `section_exemplars[admin_label=Why Choose Us].children[0]` — a bare `et_pb_row` with one `4_4` column, no `column_structure` attribute | `spacing.row.width` / `spacing.row.max_width` on a `4_4` row |
| heading `title_font`, `title_text_color`, `title_font_size` (+`_tablet`/`_phone`) | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` (+`.size_tablet`/`.size_phone`) |
| blurb row `column_structure` | `section_exemplars[admin_label=Why Choose Us].children[1].attrs.column_structure` (`"1_3,1_3,1_3"`) | `"1_3,1_3,1_3"` (the pattern's own default) |
| blurb `header_level`, `icon_color` | `module_styles.et_pb_blurb[section_tone=light,column_type=1_3].attrs` | `header_level="h3"` + `colors.customizer.accent` |
| blurb body `header_font`/`body_font` (title/body typography) | no dedicated blurb font bundle beyond `icon_color`/`header_level` — build the title from `typography.scale.h3.font`/`.color` and the body from `typography.body_font` + `colors.customizer.body_text` | same |
| blurb `font_icon` | not a token — pick a real Divi icon glyph per service (see [value-formats.md](../../reference/value-formats.md#icons)) | — |
| blurb `url` | the service's own page on this site — never a token | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); the heading `et_pb_row` (no `column_structure` needed for a single
`4_4` column) and the blurb `et_pb_row` `column_structure="1_3,1_3,1_3"`;
[`et_pb_column`](../../reference/modules/et_pb_column.md) `type="4_4"` / `type="1_3"`;
[`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`, `title_level="h2"`,
`title_font`, `title_text_color`, `title_font_size` (+responsive); one
[`et_pb_blurb`](../../reference/modules/et_pb_blurb.md) per column with `title`, `content`,
`use_icon="on"`, `font_icon`, `header_level="h3"`, `icon_color`, `url`.

Optional: `admin_label` on the section; `url_new_window` if the service page should open in a new
tab (usually leave `off`); `icon_placement="left"` for a more compact, left-aligned icon-and-title
layout instead of the default icon-on-top.

## Responsive rules

`title_font_size` on the `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs `_tablet`/`_phone`
(90px → 60px → 45px) plus `custom_padding_last_edited="on|phone"`. The blurb row's
`column_structure="1_3,1_3,1_3"` needs no phone-specific value: Divi stacks all three blurbs to
full width, one per line, on phone automatically.

## Variations

- **Four-up variant:** `column_structure="1_4,1_4,1_4,1_4"` with four blurbs instead of three —
  nothing else changes.
- **Left-icon variant:** set `icon_placement="left"` on every blurb for a more compact list-style
  presentation, useful when a service's description runs longer than one line.
- **No-link variant:** for a business that doesn't yet have individual service pages, drop `url`
  from every blurb — but create the linked variant as soon as those pages exist, since the internal
  links are the point of this section.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Services" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Our Plumbing Services" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][/et_pb_column][/et_pb_row][et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb title="Drain Cleaning" url="https://miamirapidplumbing.example/services/drain-cleaning/" use_icon="on" font_icon="&#xe036;||divi||400" header_level="h3" _builder_version="4.27.9" _module_preset="default" icon_color="#f97316" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569"]<p>Fast, hydro-jet drain clearing for kitchens, showers and main lines.</p>[/et_pb_blurb][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb title="Water Heater Repair" url="https://miamirapidplumbing.example/services/water-heater-repair/" use_icon="on" font_icon="&#xe038;||divi||400" header_level="h3" _builder_version="4.27.9" _module_preset="default" icon_color="#f97316" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569"]<p>Same-day repair and replacement for tank and tankless water heaters.</p>[/et_pb_blurb][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_blurb title="Leak Detection" url="https://miamirapidplumbing.example/services/leak-detection/" use_icon="on" font_icon="&#xe054;||divi||400" header_level="h3" _builder_version="4.27.9" _module_preset="default" icon_color="#f97316" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569"]<p>Non-invasive leak detection that finds the problem before we open a wall.</p>[/et_pb_blurb][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `section.txt --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one `h2`, and every blurb title renders as `h3` — no `h1` on this section
- [ ] every blurb with a matching service page has `url` set
