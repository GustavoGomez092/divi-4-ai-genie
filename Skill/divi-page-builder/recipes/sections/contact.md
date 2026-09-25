# Contact

**Use for:** a contact page/section pairing a lead-capture form with an optional map showing the
business's location. · **SEO:** the form's own `title` renders at `title_level` (set to `h2` here);
give the section an `admin_label` but no second heading above it. **Map note — Google Maps API key
required.** `et_pb_map` will not render a usable map on a real site until a **Google Maps API key
is configured in the site's Divi theme options** (Divi Theme Options → Integration, or the
module's own `google_api_key` field) — without one, Google's own map tiles return a "For
development purposes only" watermark or fail to load entirely. This is a site-level (or
per-module) configuration step outside what this recipe's shortcode can set; document it as a
deployment prerequisite whenever this recipe includes the map. **Email note.** `email` below is the
address the form's submissions are delivered to; on a real client site it must be set from what the
client's brief specifies (their intake inbox), never guessed or left as the site owner's personal
address without asking.

## Structure
```text
section (Contact Us, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row column_structure="1_2,1_2"
   ├─ column 1_2: contact_form
   │  ├─ contact_field (Name)
   │  ├─ contact_field (Email)
   │  ├─ contact_field (Phone)
   │  └─ contact_field (Message)
   └─ column 1_2: map
      └─ map_pin
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=80px].attrs.background_color` (the "About" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[3][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| contact form `form_field_background_color` | no bundle exists in tokens for this module — `colors.palette[5].hex` (`#f1f5f9`), the site's own light neutral | same |
| contact form submit button (`custom_button`, `button_bg_color`, `button_text_color`, `button_bg_color__hover`, `button_bg_color__hover_enabled`, `button_border_radius`) | `module_styles.et_pb_button[section_tone=dark,column_type=1_2].attrs` (the hero's dark-section button bundle — reused here purely for its brand button colors) | `colors.customizer.accent` for `button_bg_color`, `colors.palette[1].hex` for `button_text_color` |
| contact form submit button `button_font` | `colors.customizer.body_font` | `typography.body_font` (`Lato||||||||`) |
| business address, map pin title/content | the client's own brief (their real service address) — never a token | — |
| form recipient `email` | the client's own brief (their intake inbox) — never a token, never guessed (see the note above) | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`,
`title_level="h2"`, `title_font`, `title_text_color`, `title_font_size`;
[`et_pb_contact_form`](../../reference/modules/et_pb_contact_form.md) `email`, `title`,
`title_level="h2"`, `submit_button_text`, `button_font`, plus the shared button attributes above; four
[`et_pb_contact_field`](../../reference/modules/et_pb_contact_field.md)s, each with a unique
`field_id`, a `field_title`, and `field_type` (`input` for Name and Phone, `email` for Email,
`text` for Message — `text` is Divi's multi-line textarea field type, not a plain single-line
input).

Optional: `success_message` on the form (Divi supplies a default if omitted); `captcha="on"` (the
module's default) for a basic math captcha with no external service; `use_spam_service`/
`recaptcha_list` only if the client's brief specifies a reCAPTCHA account to use; the whole
`et_pb_map`/`et_pb_map_pin` pairing is optional — omit both entirely for a contact page that
doesn't need a map (e.g. a service-area business with no public storefront).

## Responsive rules

`title_font_size` on the section's `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. The `column_structure="1_2,1_2"` row needs no phone-specific value: Divi
stacks the form above the map on phone automatically (form first is the right order — a visitor on
mobile wants to fill in the form, not scroll past a map first).

## Variations

- **Form-only variant:** drop the map column entirely and use `column_structure` with no split (a
  single `4_4` column) for a business with no public address to show.
- **Map-first variant:** swap the two columns (map on the left, form on the right) for a client who
  wants the location to be the first thing a visitor sees.
- **Fewer fields variant:** drop the Phone field for a client that only wants email-based inquiries
  — `et_pb_contact_form` accepts any number of `et_pb_contact_field` children.

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Contact Us" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="80px||80px||true|false" custom_padding_tablet="55px||55px||true|false" custom_padding_phone="40px||40px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Get In Touch" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][/et_pb_column][/et_pb_row][et_pb_row column_structure="1_2,1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_contact_form title="Request A Free Quote" title_level="h2" email="quotes@miamirapidplumbing.example" submit_button_text="Send Message" success_message="Thanks! We'll call you back within the hour." _builder_version="4.27.9" _module_preset="default" button_font="Lato||||||||" form_field_background_color="#f1f5f9" custom_button="on" button_bg_color="#f97316" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_border_radius="6px" button_text_color="#ffffff"][et_pb_contact_field field_id="name" field_title="Name" field_type="input" required_mark="on" _builder_version="4.27.9" _module_preset="default"][/et_pb_contact_field][et_pb_contact_field field_id="email" field_title="Email" field_type="email" required_mark="on" _builder_version="4.27.9" _module_preset="default"][/et_pb_contact_field][et_pb_contact_field field_id="phone" field_title="Phone" field_type="input" required_mark="off" _builder_version="4.27.9" _module_preset="default"][/et_pb_contact_field][et_pb_contact_field field_id="message" field_title="Message" field_type="text" fullwidth_field="on" required_mark="on" _builder_version="4.27.9" _module_preset="default"][/et_pb_contact_field][/et_pb_contact_form][/et_pb_column][et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"][et_pb_map address="1200 Brickell Ave, Miami, FL 33131" zoom_level="14" _builder_version="4.27.9" _module_preset="default"][et_pb_map_pin pin_address="1200 Brickell Ave, Miami, FL 33131" title="Miami Rapid Plumbing" _builder_version="4.27.9" _module_preset="default"]<p>1200 Brickell Ave, Miami, FL 33131</p>[/et_pb_map_pin][/et_pb_map][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 scripts/validate.py page.txt --tokens tokens.json` — 0 errors; to check this section on its own, `python3 scripts/validate.py section.txt --tokens tokens.json --fragment` (`tokens.json` is the target site's own, from `scripts/extract_tokens.py`; `recipes/sample-tokens.json` is only the worked example's fictional brand)
- [ ] `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` — show the user `preview.html` (or `preview.py serve`) and **stop until they approve it**; fast visual check (open `preview.html`; see [preview](../../reference/preview.md))
- [ ] Only after the user approves the local preview: `python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "…"` — saves a **draft** (validates first) and prints its `preview_url`; share it and publish only after the user approves ([publishing](../../reference/publishing.md))
- [ ] exactly one `h2` — no `h1` on this section
- [ ] the form's recipient `email` matches the client's brief; a Google Maps API key is confirmed configured on the live site before relying on the map rendering for real visitors
