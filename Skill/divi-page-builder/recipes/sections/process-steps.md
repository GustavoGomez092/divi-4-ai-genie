# Process steps

**Use for:** a numbered "how it works" walkthrough (e.g. "1. Call → 2. We Diagnose → 3. We Fix →
4. You're Covered") that turns an abstract service into a concrete, low-anxiety sequence. · **SEO:**
one `h2` introduces the section; each step's title is an `h3` beneath it. The step number itself is
a large styled numeral, not a heading — it's decorative eyebrow text, so it must not be marked up as
an `h1`-`h6`.

## Structure
```text
section (How It Works, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row column_structure="1_4,1_4,1_4,1_4"
   ├─ column 1_4: text (number eyebrow "01") · heading (h3) · text (body)
   ├─ column 1_4: text (number eyebrow "02") · heading (h3) · text (body)
   ├─ column 1_4: text (number eyebrow "03") · heading (h3) · text (body)
   └─ column 1_4: text (number eyebrow "04") · heading (h3) · text (body)
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=80px].attrs.background_color` (the "About" bundle, reused here for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[3][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| step number eyebrow `text_font`, `text_text_color`, `text_font_size` | no bundle for a numeral eyebrow exists in tokens — **fixed design choice**: `typography.heading_font` (`Montserrat`) at weight `800`, `colors.customizer.accent` (`#f97316`), `40px` | same |
| step title (`h3`) `title_font`, `title_text_color`, `title_font_size` | no `column_type=1_4` light-tone `h3` bundle exists — read `typography.scale.h3.font` / `.color` / `.size` directly | same |
| step body `text_font`, `text_text_color`, `text_font_size` | no light-tone `1_4` text bundle exists — build from `typography.body_font` + `colors.customizer.body_text` + `colors.customizer.body_size` | same |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); the heading `et_pb_row` and the steps
`et_pb_row` `column_structure="1_4,1_4,1_4,1_4"`;
[`et_pb_column`](../../reference/modules/et_pb_column.md) `type="4_4"` / `type="1_4"`;
[`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`, `title_level="h2"` for the
section title and `title_level="h3"` for each step title, both with `title_font`,
`title_text_color`, `title_font_size`; one `et_pb_text` per step for the number eyebrow, with
`text_font`, `text_text_color`, `text_font_size`; one `et_pb_text` per step for the body, with
`content`, `text_font`, `text_text_color`, `text_font_size`.

Optional: `admin_label` on the section; `text_letter_spacing` on the eyebrow for a tighter numeral;
an `et_pb_image`/icon in place of the numeral for a more illustrated variant (see Variations).

## Responsive rules

`title_font_size` on the `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The step-number eyebrow's `text_font_size` should shrink
on phone (e.g. `40px` → `32px`) so four stacked steps don't feel oversized on a narrow screen. The
step title's `title_font_size` needs no `_tablet`/`_phone` override: `typography.scale.h3` in
`sample-tokens.json` has empty `size_phone`/`size_tablet` strings — the site's own extraction found
no responsive value for `h3` at all, so this recipe leaves it as a single value at every breakpoint
rather than inventing a tablet/phone size the site's own tokens don't define. The section's
`custom_padding` needs its usual `_tablet`/`_phone` pair. The steps row's `column_structure` needs
no phone-specific value: Divi stacks all four steps to full width, one per line, on phone.

## Variations

- **Stacked variant:** for a longer, more detailed walkthrough, use a single `column_structure="4_4"`
  row with all four steps inside one column, each step as its own eyebrow/heading/text group,
  instead of the `1_4,1_4,1_4,1_4` side-by-side layout.
- **Blurb variant:** replace the eyebrow-`et_pb_text` + `et_pb_heading` pair in each column with a
  single `et_pb_blurb` (`use_icon="on"`, a numeral rendered via `font_icon` or the blurb's own
  `title` prefixed with the digit) — fewer modules, at the cost of the numeral no longer being
  independently stylable.
- **Three-step variant:** `column_structure="1_3,1_3,1_3"` with three steps instead of four —
  nothing else changes.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="How It Works" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="80px||80px||true|false" custom_padding_tablet="55px||55px||true|false" custom_padding_phone="40px||40px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="How It Works" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][/et_pb_column][/et_pb_row][et_pb_row column_structure="1_4,1_4,1_4,1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Step Number" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|800|||||||" text_text_color="#f97316" text_font_size="40px" text_font_size_tablet="40px" text_font_size_phone="32px" text_font_size_last_edited="on|phone"]<p>01</p>[/et_pb_text][et_pb_heading title="Call or Book Online" title_level="h3" _builder_version="4.27.9" _module_preset="default" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px"]<p>Reach us by phone or through our online form, any time of day.</p>[/et_pb_text][/et_pb_column][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Step Number" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|800|||||||" text_text_color="#f97316" text_font_size="40px" text_font_size_tablet="40px" text_font_size_phone="32px" text_font_size_last_edited="on|phone"]<p>02</p>[/et_pb_text][et_pb_heading title="We Diagnose the Problem" title_level="h3" _builder_version="4.27.9" _module_preset="default" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px"]<p>A licensed plumber arrives, inspects the issue and gives you an upfront price.</p>[/et_pb_text][/et_pb_column][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Step Number" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|800|||||||" text_text_color="#f97316" text_font_size="40px" text_font_size_tablet="40px" text_font_size_phone="32px" text_font_size_last_edited="on|phone"]<p>03</p>[/et_pb_text][et_pb_heading title="We Fix It Right Away" title_level="h3" _builder_version="4.27.9" _module_preset="default" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px"]<p>Most repairs are completed in the same visit, with parts stocked on the truck.</p>[/et_pb_text][/et_pb_column][et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"][et_pb_text admin_label="Step Number" _builder_version="4.27.9" _module_preset="default" text_font="Montserrat|800|||||||" text_text_color="#f97316" text_font_size="40px" text_font_size_tablet="40px" text_font_size_phone="32px" text_font_size_last_edited="on|phone"]<p>04</p>[/et_pb_text][et_pb_heading title="You're Covered by Our Guarantee" title_level="h3" _builder_version="4.27.9" _module_preset="default" title_font="Lato||||||||" title_text_color="#475569" title_font_size="18px"][/et_pb_heading][et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#475569" text_font_size="16px"]<p>Every job is backed by our workmanship guarantee, in writing.</p>[/et_pb_text][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — show the user `preview.html` (or `preview.py serve`) and **stop until they approve it**; fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] Only after the user approves the local preview: `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one `h2`, and every step title renders as `h3` — no `h1` on this section; step numerals are plain text, not headings
- [ ] every step's number/title/body appears in the same order as its sibling steps
