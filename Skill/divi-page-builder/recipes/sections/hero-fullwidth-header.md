# Hero fullwidth header

**Use for:** a fast, copy-first hero built from Divi's dedicated Fullwidth Header module — no row/
column layer to author, useful for an inner page or landing page that needs a title, a short pitch
and up to two buttons without a custom two-column layout. · **SEO:** exactly one `h1` per page —
set `title_level="h1"`; this section supplies it. If a `header_image_url`/`logo_image_url` is added
later, also set `image_alt_text`/`logo_alt_text` (Advanced tab) — the module has no plain `alt`
attribute of its own.

## Structure
```text
section fullwidth="on"
└─ fullwidth_header (title h1 · subhead · button_one · button_two)
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `section_exemplars[admin_label=Hero].attrs.background_color` | `colors.palette[0].hex` |
| section `custom_padding` (+`_tablet`/`_phone`) | `section_exemplars[admin_label=Hero].attrs.custom_padding` (+`_tablet`/`_phone`) | `spacing.section_padding[0][0]` |
| `et_pb_fullwidth_header`'s own `background_color` | same as the section's, `section_exemplars[admin_label=Hero].attrs.background_color` — **must be set explicitly**, or the module falls back to Divi's own default fill (`#7EBEC5`, an off-brand teal) instead of inheriting the section's color | `colors.palette[0].hex` |
| `title_font`, `title_text_color`, `title_font_size` (+`_tablet`/`_phone`) | tokens has no `et_pb_fullwidth_header` bundle at all — read straight off `typography.scale.h1.font` / `.color` / `.size` (+`.size_tablet`/`.size_phone`) | same |
| `subhead_font`, `subhead_text_color`, `subhead_font_size` | no bundle for this module — reuse the Hero split's body-copy bundle, `module_styles.et_pb_text[section_tone=dark,column_type=1_2].attrs`, since it's the closest analog (light body copy over this same dark section) | `typography.body_font` + `colors.customizer.body_text` |
| `custom_button_one`, `button_one_bg_color`, `button_one_bg_color__hover`(`_enabled`), `button_one_text_color`, `button_one_border_radius` | `module_styles.et_pb_button[section_tone=dark,column_type=1_2].attrs` | `colors.customizer.accent` + `shapes.radii[0][0]` |
| `button_one_font`, `button_two_font` | `colors.customizer.body_font` | `typography.body_font` (`Lato||||||||`) |
| `custom_button_two`, `button_two_bg_color`, `button_two_border_color`, `button_two_border_width`, `button_two_text_color`, `button_two_border_radius` | no secondary/outline button bundle in tokens — build one from `"transparent"` + `colors.palette[1].hex` (`#ffffff`) for the border/text, keeping the same `shapes.radii[0][0]` radius | same |
| `content_max_width` | `spacing.row.max_width` | same |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `fullwidth="on"`,
`background_color`, `custom_padding` (+responsive);
[`et_pb_fullwidth_header`](../../reference/modules/et_pb_fullwidth_header.md) its own
`background_color` (see the note above — omitting it shows Divi's teal default, not the section's
color), `title`, `title_level="h1"`, `title_font`, `title_text_color`, `title_font_size`
(+responsive), `subhead`, `subhead_font`, `subhead_text_color`, `subhead_font_size`,
`button_one_text`, `button_one_url`, `custom_button_one="on"`, `button_one_bg_color`,
`button_one_text_color`, `button_one_border_radius`, `button_one_bg_color__hover` (+`_enabled`),
`button_one_font`, `header_fullscreen`, `text_orientation`.

Optional: `button_two_text`/`button_two_url` and its own `custom_button_two`/color/border/
`button_two_font` fields (drop the whole pair for a single-CTA hero); `content_max_width`; `header_image_url`/
`logo_image_url` (with their own `image_alt_text`/`logo_alt_text`, if used); the scroll-down icon
fields.

## Responsive rules

`title_font_size` needs `_tablet`/`_phone` (56px → 42px → 34px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs `_tablet`/`_phone`
(96px → 64px → 48px) plus `custom_padding_last_edited="on|phone"`. `header_fullscreen` and
`text_orientation` are on/off and alignment switches, not sizes — they need no responsive variant.

## Variations

- **Fullscreen variant:** `header_fullscreen="on"` makes the section fill the viewport height —
  best on a true landing/splash page, not an inner page with content right below it.
- **Single-button variant:** omit every `button_two_*` field when the page only needs one CTA.
- **Left-aligned variant:** the module's own default; set `text_orientation="left"` (or omit it)
  instead of `"center"`.

## Worked example (sample-tokens.json)
```divi
[et_pb_section fullwidth="on" admin_label="Hero" _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" custom_padding="96px||96px||true|false" custom_padding_tablet="64px||64px||true|false" custom_padding_phone="48px||48px||true|false" custom_padding_last_edited="on|phone"][et_pb_fullwidth_header title="Emergency Plumber in Miami" title_level="h1" subhead="Licensed, insured plumbers at your door in 60 minutes, day or night, anywhere in Miami-Dade." button_one_text="Call (305) 555-0100" button_one_url="tel:+13055550100" button_two_text="Get a Free Quote" button_two_url="/free-quote/" header_fullscreen="off" text_orientation="center" content_max_width="1200px" _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" title_font="Montserrat|700|||||||" title_text_color="#ffffff" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone" subhead_font="Lato||||||||" subhead_text_color="#cbd5e1" subhead_font_size="18px" button_one_font="Lato||||||||" custom_button_one="on" button_one_bg_color="#f97316" button_one_text_color="#ffffff" button_one_border_radius="6px" button_one_bg_color__hover="#ea580c" button_one_bg_color__hover_enabled="on|hover" button_two_font="Lato||||||||" custom_button_two="on" button_two_bg_color="transparent" button_two_text_color="#ffffff" button_two_border_color="#ffffff" button_two_border_width="2px" button_two_border_radius="6px"][/et_pb_fullwidth_header][/et_pb_section]
```

## Checklist
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — fast visual check
- [ ] `research/tools/push_local.sh <file> "Hero fullwidth header"` — push to divi-test.local, note the printed id/url
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> hero-fullwidth-header <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
- [ ] exactly one H1 on the page
- [ ] every image has alt text and a Media Library URL
