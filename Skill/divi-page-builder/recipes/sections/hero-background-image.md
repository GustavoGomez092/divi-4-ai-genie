# Hero background image

**Use for:** an atmospheric, full-bleed photo hero (e.g. a job-site or storefront photo) for a
page that wants more visual weight than a flat color background. · **SEO:** exactly one `h1` per
page; this section supplies it. There's no `et_pb_image` here — the photo is the section's own
`background_image`, not an `<img>` — so there's no `alt` text to set for it.

## Structure
```text
section (Hero, dark tone, background_image + dark gradient overlay)
└─ row column_structure="4_4"
   └─ column 4_4: text (eyebrow) · heading (h1) · text (body) · button
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_image` | not a token — the site's own Media Library photo, on the tokens site's own host | — |
| section `background_size`, `background_position` | fixed pattern values (`cover`, `center`) — not tokenized | same |
| section `use_background_color_gradient`, `background_color_gradient_overlays_image` | fixed `"on"` — required to place a readable overlay above the photo, not tokenized | same |
| section `background_color_gradient_stops` | derived from `colors.palette[0].hex` (`#0b2a3c` → `rgb(11,42,60)`) at two opacities, so the tint matches the brand navy rather than a generic black | plain `rgba(0,0,0,0.6) 0%\|rgba(0,0,0,0.6) 100%` |
| section `custom_padding` (+`_tablet`/`_phone`) | `section_exemplars[admin_label=Hero].attrs.custom_padding` (+`_tablet`/`_phone`) | `spacing.section_padding[0][0]` |
| row `width`, `max_width` | `spacing.row.width` / `spacing.row.max_width` (no bundle for a `4_4` column here) | same |
| heading `title_font`, `title_text_color`, `title_font_size` (+`_tablet`/`_phone`) | no `column_type=4_4` dark-tone `h1` bundle exists, so read straight off `typography.scale.h1.font` / `.color` / `.size` (+`.size_tablet`/`.size_phone`) | same |
| body text `text_font`, `text_text_color`, `text_font_size` | `module_styles.et_pb_text[section_tone=dark,column_type=4_4].attrs` (the "Free Quote CTA" bundle — the only one matching this tone + column type) | `typography.body_font` + `colors.customizer.body_text` |
| button `custom_button`, `button_bg_color`, `button_bg_color__hover`(`_enabled`), `button_text_color`, `button_border_radius`, `preset` | `module_styles.et_pb_button[section_tone=dark,column_type=4_4].attrs` + its `preset` UUID | `colors.customizer.accent` + `shapes.radii[0][0]`, preset `"default"` |
| button `button_font` | `colors.customizer.body_font` | `typography.body_font` (`Lato||||||||`) |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_image`,
`background_size`, `background_position`, `use_background_color_gradient="on"`,
`background_color_gradient_stops`, `background_color_gradient_overlays_image="on"`,
`custom_padding` (+responsive); [`et_pb_row`](../../reference/modules/et_pb_row.md)
`column_structure="4_4"`, `width`, `max_width`;
[`et_pb_column`](../../reference/modules/et_pb_column.md) `type="4_4"`;
[`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`, `title_level="h1"`,
`title_font`, `title_text_color`, `title_font_size` (+responsive); one
[`et_pb_text`](../../reference/modules/et_pb_text.md) with `content`, `text_font`,
`text_text_color`, `text_font_size`; [`et_pb_button`](../../reference/modules/et_pb_button.md)
`button_text`, `button_url`, `custom_button="on"`, `button_bg_color`, `button_text_color`,
`button_border_radius`, `button_bg_color__hover` (+`_enabled`), `button_font`.

Optional: `admin_label` on the section; a second, "eyebrow" `et_pb_text` above the heading;
`background_color_gradient_direction` to angle the overlay; `title_text_align` on the heading,
`text_orientation`/`max_width`/`module_alignment` on the text modules, and `button_alignment` on
the button, to center the copy (see Variations).

## Responsive rules

`title_font_size` needs `_tablet`/`_phone` (56px → 42px → 34px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs `_tablet`/`_phone`
(96px → 64px → 48px) plus `custom_padding_last_edited="on|phone"`. `background_size="cover"` and
`background_position="center"` need no responsive variant unless the photo needs a different crop
on phone (art-direction, not a token concern — see Variations).

## Variations

- **Centered variant:** add `title_text_align="center"` to the heading, `text_orientation="center"`
  to the body text, `max_width="720px"` + `module_alignment="center"` to both, and
  `button_alignment="center"` to the button — same combination
  [hero-centered.md](hero-centered.md) uses.
- **Lighter overlay:** lower the gradient stops' alpha (e.g. `0.35` instead of `0.6`/`0.85`) for a
  more photo-forward look, keeping the same brand-navy color.
- **Different phone crop:** add `background_position_phone` (e.g. `top_center`) with
  `background_position_last_edited="on|phone"` when the photo's focal point needs to shift on a
  narrow screen.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Hero" _builder_version="4.27.9" _module_preset="default" background_image="https://miamirapidplumbing.example/wp-content/uploads/2026/09/plumbing-van-job-site.jpg" background_size="cover" background_position="center" use_background_color_gradient="on" background_color_gradient_stops="rgba(11,42,60,0.85) 0%|rgba(11,42,60,0.55) 100%" background_color_gradient_direction="180deg" background_color_gradient_overlays_image="on" custom_padding="96px||96px||true|false" custom_padding_tablet="64px||64px||true|false" custom_padding_phone="48px||48px||true|false" custom_padding_last_edited="on|phone"][et_pb_row column_structure="4_4" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Eyebrow" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|600||on|||||" text_text_color="#f97316" text_font_size="14px" text_letter_spacing="2px"]<p>24/7 Emergency Plumbing</p>[/et_pb_text][et_pb_heading title="Burst Pipe? We're On Our Way" title_level="h1" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#ffffff" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone" title_line_height="1.1em"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#f1f5f9" text_font_size="18px" text_line_height="1.7em"]<p>Licensed, insured plumbers dispatched across Miami-Dade around the clock.</p>[/et_pb_text][et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="11111111-2222-3333-4444-555555555555" button_font="Lato||||||||" custom_button="on" button_text_color="#0b2a3c" button_bg_color="#f97316" button_border_radius="6px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover"][/et_pb_button][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `section.txt --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one H1 on the page
- [ ] every image has alt text and a Media Library URL
