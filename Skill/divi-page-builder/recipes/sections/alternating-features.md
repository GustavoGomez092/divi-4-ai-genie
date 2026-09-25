# Alternating features

**Use for:** two or more feature blocks — a photo beside a headline and description — that zigzag
left/right down the page for visual rhythm, common on a services or product page below the hero. ·
**SEO:** each feature gets its own `h3` (never `h1`; the page's one `h1` lives in its hero); every
`et_pb_image` needs real `alt` text describing that photo. The phone-only duplicate row described
below (Responsive rules) must carry *identical* copy to its desktop/tablet counterpart — it is the
same content shown at a different breakpoint, not new content, so edit both halves together.

## Structure
```text
section (Alternating features, light tone)
├─ row column_structure="1_2,1_2" (Feature 1 — image left, all breakpoints)
│  ├─ column 1_2: image
│  └─ column 1_2: heading (h3) · text
├─ row column_structure="1_2,1_2" disabled_on="on|off|off" (Feature 2, desktop+tablet — text left, image right)
│  ├─ column 1_2: heading (h3) · text
│  └─ column 1_2: image
└─ row column_structure="1_2,1_2" disabled_on="off|on|on" (Feature 2, phone only — image first, same copy)
   ├─ column 1_2: image
   └─ column 1_2: heading (h3) · text
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,uses=1,custom_padding=90px].attrs.background_color` (the "Why Choose Us" bundle, reused here for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| row `width`, `max_width` | no bundle matches a light-tone `1_2,1_2` row (README §2: match `section_tone` **and** `column_type` first) — read `spacing.row.width[0][0]` / `spacing.row.max_width[0][0]` directly | same |
| heading (`h3`) `title_font`, `title_text_color`, `title_font_size` | no `column_type=1_2` light-tone `h3` bundle exists — read `typography.scale.h3.font` / `.color` / `.size` | same |
| body text `text_font`, `text_text_color`, `text_font_size` | no light-tone `1_2` text bundle exists — build from `typography.body_font` + `colors.customizer.body_text` + `colors.customizer.body_size` | same |
| image `border_radii` | `shapes.radii[0][0]` (rendered `"on\|<r>\|<r>\|<r>\|<r>"`) | `"off"` |
| image `src`, `alt` | the site's own Media Library — never a token | — |
| row `disabled_on` (the phone-reorder pair) | **fixed technique value, not a token** — see Responsive rules | same (always fixed) |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_row`](../../reference/modules/et_pb_row.md)
`column_structure="1_2,1_2"`, `width`, `max_width`, and — on the second feature's two rows only —
`disabled_on`; [`et_pb_column`](../../reference/modules/et_pb_column.md) `type="1_2"`;
[`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`, `title_level="h3"`,
`title_font`, `title_text_color`, `title_font_size`; one
[`et_pb_text`](../../reference/modules/et_pb_text.md) with `content`, `text_font`,
`text_text_color`, `text_font_size`; [`et_pb_image`](../../reference/modules/et_pb_image.md) `src`,
`alt`.

Optional: `admin_label` on each section/row (e.g. "Feature 1", "Feature 2 — Desktop", "Feature 2 —
Phone"); `border_radii` on the image; an `et_pb_button` per feature linking to a relevant service
page.

## Responsive rules

**Why the duplicate row exists.** Divi renders a row's columns in the same source order at every
breakpoint — there is no built-in, non-CSS way to show "text, then image" on desktop but "image,
then image's text" on phone from a single row, because the row has no `disabled_on`-style toggle
for column *order*, only for column *visibility*
([design-families.md#visibility](../../reference/design-families.md#visibility)). Feature 1 needs
no special handling: its image column is already first in the markup, so it's naturally image-first
on both desktop (image on the left) and phone (image on top). Feature 2 is the opposite: its
desktop/tablet layout puts the image column *second* (image on the right, text on the left), which
would put the *text* on top when that same row stacks on phone — violating the "image first" rule.
This recipe resolves it with the standard Divi, no-custom-CSS technique: author Feature 2 as **two
sibling rows carrying identical copy**, each targeting different breakpoints via `disabled_on`
(`phone|tablet|desktop`, positional — see
[value-formats.md](../../reference/value-formats.md#multiple_checkboxes-positional)):
- the desktop/tablet row uses `disabled_on="on|off|off"` (hidden on phone, shown on tablet+desktop),
  with the column order that puts the image on the right;
- the phone-only row uses `disabled_on="off|on|on"` (shown on phone, hidden on tablet+desktop), with
  the column order reversed so the image is first.

Since `disabled_on` toggles CSS visibility per breakpoint rather than removing markup, this is a
standard responsive pattern (not cloaking), but it does mean the same paragraph of copy exists
twice in the page source — keep both copies byte-identical whenever the content changes.

Beyond that: `title_font_size` and the section's `custom_padding` need their usual `_tablet`/
`_phone` variants (see the hero recipes for the same rationale); `max_width` on the image needs
none.

## Variations

- **Three-plus features:** repeat the Feature 1 pattern (image-left, no duplication needed) for
  odd-numbered features and the Feature 2 pattern (duplicate pair) for even-numbered ones, so the
  image always alternates sides on desktop while always leading on phone.
- **With a button:** add an `et_pb_button` under the body text in both rows of a duplicated pair —
  keep its `button_text`/`button_url` identical between the two.
- **Single-direction variant (no duplication):** if the client doesn't need true zigzag, keep every
  row's image column first — desktop shows every feature image-left, and no `disabled_on` pair is
  needed at all.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Alternating Features" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row admin_label="Feature 1" column_structure="1_2,1_2" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/tankless-water-heater.jpg" alt="Tankless water heater freshly installed against a garage wall" _builder_version="4.27.9" _module_preset="default" border_radii="on|6px|6px|6px|6px"][/et_pb_image][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Never Run Out of Hot Water Again" title_level="h3" _builder_version="4.27.9" _module_preset="default" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px" text_line_height="1.7em"]<p>We install and service tankless water heaters that deliver endless hot water while using less energy than a tank.</p>[/et_pb_text][/et_pb_column][/et_pb_row][et_pb_row admin_label="Feature 2 - Desktop" column_structure="1_2,1_2" disabled_on="on|off|off" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Camera Inspections Before We Dig" title_level="h3" _builder_version="4.27.9" _module_preset="default" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px" text_line_height="1.7em"]<p>Every sewer line inspection includes a live video feed, so you see exactly what we see before any excavation begins.</p>[/et_pb_text][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/sewer-camera-inspection.jpg" alt="Plumber reviewing a sewer camera inspection monitor" _builder_version="4.27.9" _module_preset="default" border_radii="on|6px|6px|6px|6px"][/et_pb_image][/et_pb_column][/et_pb_row][et_pb_row admin_label="Feature 2 - Phone" column_structure="1_2,1_2" disabled_on="off|on|on" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/sewer-camera-inspection.jpg" alt="Plumber reviewing a sewer camera inspection monitor" _builder_version="4.27.9" _module_preset="default" border_radii="on|6px|6px|6px|6px"][/et_pb_image][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Camera Inspections Before We Dig" title_level="h3" _builder_version="4.27.9" _module_preset="default" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px" text_line_height="1.7em"]<p>Every sewer line inspection includes a live video feed, so you see exactly what we see before any excavation begins.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] at 1440px: Feature 1 shows image-left, Feature 2 shows image-right; at 390px: **both** features show the image before its text — no `h1` on this section, headings are `h3`
- [ ] every image has alt text and a Media Library URL; the two Feature 2 rows carry identical copy
