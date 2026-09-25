# Hero split

**Use for:** the primary above-the-fold section on a home or service page — a strong headline and
call to action next to a supporting photo. · **SEO:** exactly one `h1` per page; this section
supplies it. The `et_pb_image` needs real `alt` text describing the photo, not the filename.

## Structure
```text
section (Hero, dark tone)
└─ row column_structure="1_2,1_2"
   ├─ column 1_2: text (eyebrow) · heading (h1) · text (body) · button
   └─ column 1_2: image
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `section_exemplars[admin_label=Hero].attrs.background_color` | `colors.palette[0].hex` |
| section `custom_padding` (+`_tablet`/`_phone`) | `section_exemplars[admin_label=Hero].attrs.custom_padding` (+`_tablet`/`_phone`) | `spacing.section_padding[0][0]` |
| row `width`, `max_width` | `module_styles.et_pb_row[section_label=Hero].attrs.width` / `.max_width` | `spacing.row.width` / `spacing.row.max_width` |
| eyebrow text `text_font`, `text_text_color`, `text_font_size` | no bundle for an eyebrow style exists in tokens — build one from `typography.heading_font` + `"\|600\|\|on\|\|\|\|\|"` and `colors.customizer.accent` | same (there is no thinner fallback below this) |
| heading `title_font`, `title_text_color`, `title_font_size` (+`_tablet`/`_phone`) | `module_styles.et_pb_heading[section_tone=dark,column_type=1_2].attrs` | `typography.scale.h1.font` / `.color` / `.size` (+`.size_tablet`/`.size_phone`) |
| body text `text_font`, `text_text_color`, `text_font_size` | `module_styles.et_pb_text[section_tone=dark,column_type=1_2].attrs` | `typography.body_font` + `colors.customizer.body_text` |
| button `custom_button`, `button_bg_color`, `button_bg_color__hover`(`_enabled`), `button_text_color`, `button_border_radius` | `module_styles.et_pb_button[section_tone=dark,column_type=1_2].attrs` | `colors.customizer.accent` + `shapes.radii[0][0]` |
| button `button_font` | `colors.customizer.body_font` | `typography.body_font` (`Lato||||||||`) |
| image `border_radii` | `shapes.radii[0][0]` (rendered as `"on\|<r>\|<r>\|<r>\|<r>"`) | `"off"` (square corners) |
| image `src`, `alt` | the site's own Media Library — never a token | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_row`](../../reference/modules/et_pb_row.md)
`column_structure`, `width`, `max_width`; [`et_pb_column`](../../reference/modules/et_pb_column.md)
`type`; [`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`, `title_level="h1"`,
`title_font`, `title_text_color`, `title_font_size` (+responsive); one
[`et_pb_text`](../../reference/modules/et_pb_text.md) with `content`, `text_font`,
`text_text_color`, `text_font_size`; [`et_pb_button`](../../reference/modules/et_pb_button.md)
`button_text`, `button_url`, `custom_button="on"`, `button_bg_color`, `button_text_color`,
`button_border_radius`, `button_bg_color__hover` (+`_enabled`), `button_font`;
[`et_pb_image`](../../reference/modules/et_pb_image.md) `src`, `alt`.

Optional: `admin_label` on the section; a second, "eyebrow" `et_pb_text` above the heading;
`button_text_size` on the button; `border_radii` on the image.

## Responsive rules

`title_font_size` needs `_tablet`/`_phone` (56px → 42px → 34px) plus
`title_font_size_last_edited="on|phone"`, so the headline doesn't wrap awkwardly on a narrow
screen. The section's `custom_padding` needs `_tablet`/`_phone` (96px → 64px → 48px) plus
`custom_padding_last_edited="on|phone"` so the hero doesn't feel oversized on phone. The row's
`width`/`max_width` are already percentage/max-based and need no responsive variant.

## Variations

- **Image-left variant:** swap the two columns' children (image column first, text column
  second) — no attribute changes.
- **No-eyebrow variant:** drop the eyebrow `et_pb_text` module; nothing else changes.
- **Video-poster variant:** replace `et_pb_image` with `et_pb_video` in the second column,
  keeping the same `1_2,1_2` split and column attributes.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Hero" _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" custom_padding="96px||96px||true|false" custom_padding_tablet="64px||64px||true|false" custom_padding_phone="48px||48px||true|false" custom_padding_last_edited="on|phone"][et_pb_row column_structure="1_2,1_2" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Eyebrow" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|600||on|||||" text_text_color="#f97316" text_font_size="14px" text_letter_spacing="2px"]<p>24/7 Emergency Plumbing</p>[/et_pb_text][et_pb_heading title="Emergency Plumber in Miami" title_level="h1" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#ffffff" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone" title_line_height="1.1em"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#cbd5e1" text_font_size="18px" text_line_height="1.7em"]<p>Licensed, insured plumbers at your door in 60 minutes, day or night, anywhere in Miami-Dade.</p>[/et_pb_text][et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_text_color="#ffffff" button_bg_color="#f97316" button_border_width="0px" button_border_radius="6px" button_font="Lato||||||||" button_text_size="16px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover"][/et_pb_button][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/plumber-at-work.jpg" alt="Licensed plumber repairing a burst pipe under a Miami kitchen sink" _builder_version="4.27.9" _module_preset="default" border_radii="on|6px|6px|6px|6px"][/et_pb_image][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — fast visual check
- [ ] `research/tools/push_local.sh <file> "Hero split"` — push to divi-test.local, note the printed id/url
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> hero-split <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
- [ ] exactly one H1 on the page
- [ ] every image has alt text and a Media Library URL
