# CTA band

**Use for:** a short, high-contrast call-to-action band between content sections — "ready to book?"
— that interrupts the page's default light rhythm with a colored section and a single clear button.
· **SEO:** the band's own heading renders at `header_level` (set to `h4` here, matching this site's
own "Free Quote CTA" section elsewhere on the page) so it never introduces a second `h1`/`h2`;
`button_text` should describe the action ("Get My Free Quote"), not "Click Here".

## Structure
```text
section (Free Quote CTA, dark tone, full-width colored band)
└─ row
   └─ column 4_4: cta
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `section_exemplars[admin_label=Free Quote CTA].attrs.background_color` (or the equivalent dark 70px `module_styles.et_pb_section` bundle) | `colors.palette[0].hex` (`#0b2a3c`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same exemplar's `attrs.custom_padding` (+`_tablet`/`_phone`) | `spacing.section_padding[0][0]` |
| cta `header_font`, `header_text_color`, `header_font_size` | `module_styles.et_pb_heading[section_tone=dark,column_type=4_4].attrs` (`title_font`/`title_text_color`/`title_font_size` on the h4 bundle, applied here via the CTA's own `header_` prefix) | `typography.scale.h4.font` / `.color` / `.size` |
| cta `body_font`, `body_text_color`, `body_font_size` | `module_styles.et_pb_text[section_tone=dark,column_type=4_4].attrs` (the "Free Quote CTA" text bundle's `text_font`/`text_text_color`/`text_font_size`, applied via the CTA's `body_` prefix) | `typography.body_font` + `colors.customizer.body_text` + `colors.customizer.body_size` |
| cta button (`custom_button`, `button_bg_color`, `button_text_color`, `button_bg_color__hover`, `button_bg_color__hover_enabled`, `button_border_radius`) | `module_styles.et_pb_button[section_tone=dark,column_type=4_4,section_label="Free Quote CTA"].attrs` — a **contrasting** button (dark navy text on the brand's orange) picked specifically for a dark section, not the hero's own dark-section button bundle (see `recipes/README.md` §2 for why there are two dark-tone button bundles) | `colors.customizer.accent` for `button_bg_color`, `colors.palette[0].hex` for `button_text_color` |
| cta `_module_preset` | `presets.et_pb_button[0].uuid` (the same preset this button bundle is keyed to — see the README's worked walkthrough) | `"default"` |
| cta `use_background_color` | this pattern's own choice, not a token — `"off"`, so the CTA sits flush against the section's own color instead of drawing a second background box on top of it | `"off"` |
| title/body copy, phone number/button link | the client's own brief (the offer, the phone number or booking link) — never a token | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_cta`](../../reference/modules/et_pb_cta.md) `title`,
`content`, `button_text`, `button_url`, `header_font`, `header_text_color`, `body_font`,
`body_text_color`, `custom_button`, `button_bg_color`, `button_text_color`, `button_border_radius`.

Optional: `header_level` (defaults to `h2` — override to `h4`/`h5` on a mid-page band so it doesn't
outrank the page's real section headings); `use_background_color="off"` (see the token mapping row
above); `url_new_window` if the button should open in a new tab (rare for a `tel:`/on-page anchor
link).

## Responsive rules

`header_font_size` needs `_tablet`/`_phone` if it's set larger than the default (this recipe keeps
the site's own 30px h4 size, which doesn't need overriding at any width). The section's
`custom_padding` needs its usual `_tablet`/`_phone` pair. The CTA module itself needs no other
responsive attributes: it's already a single stacked block (heading, then body, then button) at
every width.

## Variations

- **Heading + text + button variant:** instead of a single `et_pb_cta`, use the plain
  `et_pb_heading` (h4) + `et_pb_text` + `et_pb_button` combination shown in the site's own
  "Free Quote CTA" `section_exemplars` entry — functionally identical output, useful when the
  heading, body and button each need independent Design-tab controls the combined `et_pb_cta`
  module doesn't expose per-piece (e.g. a different font size on just the button).
- **Light-tone variant:** swap the section to a light bundle and re-pick a button whose colors
  contrast against a light background (e.g. the hero's own light-on-dark bundle inverted, or a
  solid navy button on white) — every token lookup above changes with the new tone.
- **Icon-led variant:** none needed — `et_pb_cta` has no icon field of its own; use the
  heading+text+button variant with an `et_pb_blurb` if an icon is required.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Free Quote CTA" _builder_version="4.27.9" _module_preset="default" background_color="#0b2a3c" custom_padding="70px||70px||true|false" custom_padding_tablet="50px||50px||true|false" custom_padding_phone="40px||40px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_cta title="Ready To Fix That Leak?" header_level="h4" button_text="Get My Free Quote" button_url="tel:+13055550100" use_background_color="off" _builder_version="4.27.9" _module_preset="11111111-2222-3333-4444-555555555555" header_font="Montserrat|700|||||||" header_text_color="#ffffff" header_font_size="30px" body_font="Lato||||||||" body_text_color="#f1f5f9" body_font_size="18px" custom_button="on" button_bg_color="#f97316" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_border_radius="6px" button_text_color="#0b2a3c"]<p>No obligation, no hidden fees, just an honest number.</p>[/et_pb_cta][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — fast visual check
- [ ] `research/tools/push_local.sh <file> "CTA band"` — push to divi-test.local, note the printed id/url
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> cta-band <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
- [ ] no `h1`/`h2` introduced by this band (the CTA heading is `h4`, below the page's real headings)
- [ ] the button's text color is legible against its own background, and both are legible against the section background
