# Team

**Use for:** introducing the people behind the business — owners, lead technicians, office staff —
to build trust before a visitor calls. · **SEO:** one `h2` introduces the section; each member's
`name` renders at `header_level`, set to `h3` here: the module's `h4` default would skip a level
right after the section's `h2` (`validate.py` warns `W_HEADING_SKIP`). **`et_pb_team_member` has no `alt`/`image_alt` attribute of its own**
(confirmed against the module's schema — there is no such field to set here): Divi renders the
member photo's `<img alt="...">` from the uploaded attachment's own Media Library "Alt Text" field,
not from anything settable on this module. Fill in that field (a real description, e.g. "Marcus
Diaz, licensed master plumber," not the filename) on every headshot at upload time. **Real people
only.** Use real names and real photos supplied by the client — never a stock photo captioned with a
fictional name, and never a placeholder name/title invented to fill out a "3-4 people" pattern; if
the client has only two team members to show, use two.

## Structure
```text
section (Our Team, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row column_structure="1_3,1_3,1_3"
   ├─ column 1_3: team_member
   ├─ column 1_3: team_member
   └─ column 1_3: team_member
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=90px].attrs.background_color` (the "Why Choose Us" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| member `header_font`, `header_text_color` (name) | no `et_pb_team_member` bundle exists in tokens — `typography.heading_font` + `"\|700\|\|\|\|\|\|\|"` + `colors.customizer.heading` | same |
| member `position_font`, `position_text_color` (job title) | no bundle — `typography.body_font` + `colors.customizer.accent` (the orange accent, so the job title reads as secondary but branded) | `typography.body_font` + `colors.customizer.body_text` |
| member `body_font`, `body_text_color` (bio, if any) | no bundle — `typography.body_font` + `colors.customizer.body_text` | same |
| member `icon_color` (social links) | no bundle — `colors.customizer.accent` (`#f97316`) | same |
| name, position, headshot photo, alt text, social URLs | the client's own brief/roster — never a token, never invented (see the note above) | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_heading`](../../reference/modules/et_pb_heading.md) `title`,
`title_level="h2"`, `title_font`, `title_text_color`, `title_font_size`; one
[`et_pb_team_member`](../../reference/modules/et_pb_team_member.md) per person with `name`,
`position`, `image_url`, `header_font`, `header_text_color`, `position_font`, `position_text_color`.

Optional: `content` (a short one/two-sentence bio); `facebook_url`/`linkedin_url`/`twitter_url` for
social links (only the ones the client's brief actually supplies — don't invent an empty profile
link); `icon_color` to brand the social icons.

## Responsive rules

`title_font_size` on the section's `h2` needs `_tablet`/`_phone` (40px → 32px → 28px) plus
`title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. `column_structure="1_3,1_3,1_3"` needs no phone-specific value: Divi
stacks all three members to full width, one per line, on phone.

## Variations

- **Four-person variant:** `column_structure="1_4,1_4,1_4,1_4"` with a fourth
  `et_pb_team_member` — nothing else changes.
- **Two-person variant:** `column_structure="1_2,1_2"` for an owner-operator pair — the most common
  case for a small local business.
- **With-bio variant:** add a short `content` paragraph under each member's `position` for a page
  that wants more than a name/title/photo (e.g. an "About the owners" page rather than a compact
  team strip).

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Our Team" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="Meet The Team" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][/et_pb_column][/et_pb_row][et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_team_member header_level="h3" name="Marcus Diaz" position="Owner &amp; Master Plumber" image_url="https://miamirapidplumbing.example/wp-content/uploads/2026/09/team-marcus.jpg" icon_color="#f97316" _builder_version="4.27.9" _module_preset="default" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" position_font="Lato||||||||" position_text_color="#f97316"]<p>Licensed master plumber with 18 years in Miami-Dade.</p>[/et_pb_team_member][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_team_member header_level="h3" name="Lena Ford" position="Lead Technician" image_url="https://miamirapidplumbing.example/wp-content/uploads/2026/09/team-lena.jpg" icon_color="#f97316" _builder_version="4.27.9" _module_preset="default" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" position_font="Lato||||||||" position_text_color="#f97316"]<p>Specializes in water heater installs and repipes.</p>[/et_pb_team_member][/et_pb_column][et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"][et_pb_team_member header_level="h3" name="Rosa Delgado" position="Office Manager" image_url="https://miamirapidplumbing.example/wp-content/uploads/2026/09/team-rosa.jpg" icon_color="#f97316" _builder_version="4.27.9" _module_preset="default" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" position_font="Lato||||||||" position_text_color="#f97316"]<p>Runs dispatch and keeps every job on schedule.</p>[/et_pb_team_member][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — fast visual check
- [ ] `research/tools/push_local.sh <file> "Team"` — push to divi-test.local, note the printed id/url
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> team <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
- [ ] exactly one `h2` — no `h1` on this section; every member name is `h4`, never `h1`/`h2`
- [ ] every headshot has a real, non-filename Media Library "Alt Text" set (this module can't set it); every name/title/photo is real, supplied by the client, never invented
