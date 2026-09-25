# Testimonials

**Use for:** a social-proof section showing customer quotes — either a static three-up grid or a
single-column slider that cycles through more quotes than fit on screen at once. · **SEO:** the
section intro is one `h2`; testimonial `content`/`author`/`job_title`/`company_name` are plain
text/HTML, not headings, so they never compete with the page's own outline. **Data note — never
invent testimonials.** The three quotes below name fictional customers and are illustrative
placeholders for `sample-tokens.json`'s fictional brand only. On a real client site, every
testimonial's wording, author name, and star rating must be copied **word for word** from what the
client supplies in their brief — never rewritten, summarized, condensed, or invented, and never
sourced by guessing at what a typical review "would probably say." **Neither `et_pb_testimonial`
nor `et_pb_slide` has its own alt-text attribute for `portrait_url`/`image`** (confirmed against
both modules' schemas — there is no `portrait_alt`/`image_alt` field on either): Divi renders the
`<img>`'s `alt` from the uploaded attachment's own Media Library "Alt Text" field, so make sure
every portrait photo has that field filled in on upload — it cannot be set from this module.

## Structure

Grid variant:
```text
section (Testimonials, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row column_structure="1_3,1_3,1_3"
   ├─ column 1_3: testimonial
   ├─ column 1_3: testimonial
   └─ column 1_3: testimonial
```

Slider variant (swap the second row for a single-column slider):
```text
section (Testimonials, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row
   └─ column 4_4: slider
      ├─ slide (quote 1, heading = customer name)
      ├─ slide (quote 2, heading = customer name)
      └─ slide (quote 3, heading = customer name)
```

## Token mapping

| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=90px].attrs.background_color` (the "Why Choose Us" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| testimonial (grid) `body_font`, `body_text_color`, `body_font_size` (the quote itself, on the light section background) | no `et_pb_testimonial` bundle exists in tokens — build from `typography.body_font` + `colors.customizer.body_text` + `colors.customizer.body_size` | same |
| testimonial `author_font`, `author_text_color` (grid variant author name) | no bundle — build from `typography.heading_font` + `"\|700\|\|\|\|\|\|\|"` + `colors.customizer.heading` | same |
| testimonial `position_font`, `position_text_color` (grid variant job title/company) | no bundle — build from `typography.body_font` + `colors.customizer.body_text` | same |
| testimonial `quote_icon_color` | no bundle — `colors.customizer.accent` (`#f97316`) | same |
| slider `background_color` | this pattern's own choice, not a token lookup by context (no `et_pb_slider` bundle exists) — `colors.palette[0].hex` (navy), so the slider reads as an intentional brand-dark band rather than Divi's own default slider teal | `colors.palette[0].hex` |
| slide `body_font`, `body_text_color`, `body_font_size` (the quote itself, on the slider's dark background) | no bundle — build from `typography.body_font` + a **light** text color for contrast against the navy slider background; this site's dark-tone body text token is `module_styles.et_pb_text[section_tone=dark,column_type=4_4].attrs.text_text_color` (`#f1f5f9`), applied here via the slide's own `body_` prefix | `colors.palette[5].hex` (a light neutral) |
| slide `header_level` (customer name) | this pattern's own choice, not a token — `"h3"`, so the slider's per-slide name never outranks the section's own `h2` | `"h3"` |
| slider `arrows_custom_color`, `dot_nav_custom_color` | no bundle — `colors.customizer.accent` | same |
| quote text, author, job title, company, star rating | the client's own brief — **never** a token, and never invented (see the note above) | — |

## Required fields · Optional fields

Grid variant required: [`et_pb_section`](../../reference/modules/et_pb_section.md)
`background_color`, `custom_padding` (+responsive); [`et_pb_heading`](../../reference/modules/et_pb_heading.md)
`title`, `title_level="h2"`, `title_font`, `title_text_color`, `title_font_size`; one
[`et_pb_testimonial`](../../reference/modules/et_pb_testimonial.md) per column with `content`,
`author`, `body_font`, `body_text_color`, `body_font_size`, `author_font`, `author_text_color`.

Grid variant optional: `job_title`, `company_name` (styled via `position_font`/`position_text_color`);
`portrait_url` — omit it and Divi shows no portrait, just the quote/author block;
`quote_icon="off"` to hide the decorative quote mark (default `on`); `url`/`link_option_url` to
link the testimonial to a review platform.

Slider variant required: [`et_pb_slider`](../../reference/modules/et_pb_slider.md)
`background_color`, `arrows_custom_color`, `dot_nav_custom_color`; one
[`et_pb_slide`](../../reference/modules/et_pb_slide.md) per quote with `content`, `heading`,
`header_level="h3"`, `body_font`, `body_text_color`, `body_font_size`.

Slider variant optional: `show_arrows`/`show_pagination` (both default `on`); `image` on a slide for
a customer photo (same "no alt attribute" caveat as the grid's `portrait_url`); `button_text`/
`button_link` if a slide should also link out (e.g. to a full review on Google).

## Responsive rules

`title_font_size` on the section's `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. The grid row's `column_structure="1_3,1_3,1_3"` needs no phone-specific
value: Divi stacks all three testimonials to full width, one per line. The slider needs no
responsive attributes of its own — it's already a single column at every width.

## Variations

- **Grid vs. slider:** use the grid for 2-3 testimonials that should all be visible without user
  interaction; use the slider once there are more quotes than comfortably fit in a row (4+), or
  when vertical space is tight.
- **Quote-icon-off variant:** `quote_icon="off"` on any grid testimonial for a plainer look, e.g.
  when the portrait photo already carries enough visual weight.
- **Company-badge variant:** set `url`/`url_new_window` on a grid testimonial so `company_name`
  links out to the customer's own site (only when the client's brief explicitly authorizes it).

## Worked example — grid variant (sample-tokens.json)
```divi
[et_pb_section admin_label="Testimonials" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="What Our Customers Say" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][/et_pb_column][/et_pb_row][et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_testimonial author="Marisol Reyes" job_title="Homeowner" company_name="Coral Gables" portrait_url="https://miamirapidplumbing.example/wp-content/uploads/2026/09/testimonial-marisol.jpg" quote_icon="on" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#475569" body_font_size="16px" author_font="Montserrat|700|||||||" author_text_color="#0b2a3c" position_font="Lato||||||||" position_text_color="#475569" quote_icon_color="#f97316"]<p>They had a plumber at our door in 40 minutes on a Sunday night and fixed the burst pipe without tearing up half the kitchen. Couldn't ask for more.</p>[/et_pb_testimonial][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_testimonial author="Devon Clarke" job_title="Property Manager" company_name="Brickell Bay Apartments" portrait_url="https://miamirapidplumbing.example/wp-content/uploads/2026/09/testimonial-devon.jpg" quote_icon="on" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#475569" body_font_size="16px" author_font="Montserrat|700|||||||" author_text_color="#0b2a3c" position_font="Lato||||||||" position_text_color="#475569" quote_icon_color="#f97316"]<p>We manage 90 units and they're our only call for anything plumbing-related. Upfront pricing, no surprises, always show up when they say they will.</p>[/et_pb_testimonial][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_testimonial author="Priya Nair" job_title="Homeowner" quote_icon="on" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#475569" body_font_size="16px" author_font="Montserrat|700|||||||" author_text_color="#0b2a3c" position_font="Lato||||||||" position_text_color="#475569" quote_icon_color="#f97316"]<p>Explained exactly what was wrong with our water heater before doing anything, gave us a flat price, and stuck to it. Would call again in a heartbeat.</p>[/et_pb_testimonial][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Worked example — slider variant (sample-tokens.json)
```divi
[et_pb_section admin_label="Testimonials Slider" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="What Our Customers Say" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][et_pb_slider background_color="#0b2a3c" arrows_custom_color="#f97316" dot_nav_custom_color="#f97316" _builder_version="4.27.9" _module_preset="default"][et_pb_slide heading="Marisol Reyes, Coral Gables" header_level="h3" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#f1f5f9" body_font_size="16px"]<p>They had a plumber at our door in 40 minutes on a Sunday night and fixed the burst pipe without tearing up half the kitchen. Couldn't ask for more.</p>[/et_pb_slide][et_pb_slide heading="Devon Clarke, Brickell Bay Apartments" header_level="h3" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#f1f5f9" body_font_size="16px"]<p>We manage 90 units and they're our only call for anything plumbing-related. Upfront pricing, no surprises, always show up when they say they will.</p>[/et_pb_slide][et_pb_slide heading="Priya Nair, Homeowner" header_level="h3" _builder_version="4.27.9" _module_preset="default" body_font="Lato||||||||" body_text_color="#f1f5f9" body_font_size="16px"]<p>Explained exactly what was wrong with our water heater before doing anything, gave us a flat price, and stuck to it. Would call again in a heartbeat.</p>[/et_pb_slide][/et_pb_slider][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors (both variants)
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — fast visual check
- [ ] `research/tools/push_local.sh <file> "Testimonials"` — push to divi-test.local, note the printed id/url
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> testimonials <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
- [ ] exactly one `h2` — no `h1` on this section; the slider's per-slide name is `h3`, never `h1`/`h2`
- [ ] every uploaded portrait/photo has its Media Library "Alt Text" filled in (the module itself can't set it)
- [ ] every quote/author/rating on a real page traces back to the client's brief — none invented
