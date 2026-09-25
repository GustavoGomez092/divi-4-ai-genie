# Replace section

**Use for:** swapping out an entire section for a better one — a thin, unstyled section a client
built by hand becomes a proper recipe-built section, or a section built for an old brand gets
rebuilt for the current one. Keep the old section's `admin_label` (so the page's outline still
reads the same way) and, where `tokens.json` has a `section_exemplars` entry with a similar shape,
match its design attributes (`background_color`, `custom_padding` + responsive) — don't invent new
ones when a real exemplar already establishes them.

## Command sequence

```bash
# 1. See exactly what's there today.
python3 scripts/page_edit.py page.txt outline
python3 scripts/page_edit.py page.txt extract "et_pb_section[N]"

# 2. Write the new section in its own file:
#    - same admin_label as the old section (unless the page's own outline is changing on purpose)
#    - background_color / custom_padding (+ responsive) from the closest section_exemplars entry
#      in tokens.json, not invented
#    - module content/attributes from the chosen section recipe's Token mapping table

# 3. Replace — this touches only the old section's span; everything before and after is untouched.
python3 scripts/page_edit.py page.txt replace \
  "et_pb_section[N]" new-section.txt --out page.txt

# 4. Validate against a baseline of the page before the replacement.
python3 scripts/validate.py page.txt --baseline original.txt \
  --tokens tokens.json
```

## Fetching a live page first

```bash
python3 scripts/publish.py fetch --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --out original.txt
cp original.txt page.txt
# ...extract the old section, compose new-section.txt, then replace against page.txt...
```

## Applying the result safely

```bash
# 1. Draft a review copy (a NEW draft — no --page-id — the live page stays untouched for now).
python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" \
  --title "Review: <page title> section rebuild"
# 2. Share that draft's preview_url; only proceed once a human approves it.
# 3. Apply the approved content to the live page and publish it in the same request.
python3 scripts/publish.py publish --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --content page.txt --yes
```

## Worked example (`tests/fixtures/valid/handwritten-landing.txt`)

The fixture's `et_pb_section[1]` ("Services") is a thin, hand-built section: three unlinked blurbs
and an accordion crammed into the same section, no heading. Replace it with the
[Services grid](../sections/services-grid.md) recipe's own worked example, which already carries
`admin_label="Services"` and whose section attributes (`background_color="#ffffff"`,
`custom_padding="90px||90px||true|false"` + responsive) match `sample-tokens.json`'s
`section_exemplars[admin_label="Why Choose Us"]` entry — the closest exemplar shape (full-width
heading row + three-up blurb row) to what this section needs to become:

```bash
python3 scripts/page_edit.py handwritten-landing.txt extract "et_pb_section[1]"
#   [et_pb_section admin_label="Services" _builder_version="4.27.9" _module_preset="default"]
#   ...three blurbs (Burst Pipes / Water Heaters / Drain Clogs, no urls) + an accordion...
#   [/et_pb_section]

python3 scripts/page_edit.py handwritten-landing.txt replace \
  "et_pb_section[1]" new-services.txt --out replaced.txt

python3 scripts/validate.py replaced.txt \
  --baseline handwritten-landing.txt \
  --tokens recipes/sample-tokens.json
#   1 pre-existing finding(s) also present in the baseline (not blocking):
#     ...W_EXTERNAL_IMAGE et_pb_section[0] > et_pb_row[0] > et_pb_column[1] > et_pb_image[0]
#   Summary: 0 error(s), 0 warning(s), 1 pre-existing
```

`diff -u` (reformatted one tag per line, same caveat as [change-copy](change-copy.md)) shows the
replacement is contained entirely inside the old section's span — the Hero section above it and
the Specialty/Closing sections below it are untouched. Note the old section's FAQ-style accordion
is gone: it moved out of Services because this page didn't have a dedicated FAQ section — a real
migration would relocate it with [insert-section](insert-section.md) rather than delete it outright,
but this worked example only demonstrates the mechanics of a section swap.

```diff
--- handwritten-landing.pretty.txt
+++ replaced.pretty.txt
@@ -14,31 +14,27 @@
 [/et_pb_column]
 [/et_pb_row]
 [/et_pb_section]
-[et_pb_section admin_label="Services" _builder_version="4.27.9" _module_preset="default"]
+[et_pb_section admin_label="Services" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"]
+[et_pb_row _builder_version="4.27.9" _module_preset="default"]
+[et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"]
+[et_pb_heading title="Our Plumbing Services" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"]
+[/et_pb_heading]
+[/et_pb_column]
+[/et_pb_row]
 [et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.9" _module_preset="default"]
 [et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"]
-[et_pb_blurb title="Burst Pipes" use_icon="on" font_icon="&#xe03b;||divi||400" icon_color="#f97316" header_level="h2" _builder_version="4.27.9" _module_preset="default"]
-<p>Fast shut-off and repair.</p>[/et_pb_blurb]
+[et_pb_blurb title="Drain Cleaning" url="https://miamirapidplumbing.example/services/drain-cleaning/" use_icon="on" font_icon="&#xe036;||divi||400" header_level="h3" _builder_version="4.27.9" _module_preset="default" icon_color="#f97316" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569"]
+<p>Fast, hydro-jet drain clearing for kitchens, showers and main lines.</p>[/et_pb_blurb]
 [/et_pb_column]
 [et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"]
-[et_pb_blurb title="Water Heaters" use_icon="on" font_icon="&#xe03b;||divi||400" icon_color="#f97316" header_level="h2" _builder_version="4.27.9" _module_preset="default"]
-<p>Same-day repair or replacement.</p>[/et_pb_blurb]
+[et_pb_blurb title="Water Heater Repair" url="https://miamirapidplumbing.example/services/water-heater-repair/" use_icon="on" font_icon="&#xe038;||divi||400" header_level="h3" _builder_version="4.27.9" _module_preset="default" icon_color="#f97316" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569"]
+<p>Same-day repair and replacement for tank and tankless water heaters.</p>[/et_pb_blurb]
 [/et_pb_column]
 [et_pb_column type="1_3" _builder_version="4.27.9" _module_preset="default"]
-[et_pb_blurb title="Drain Clogs" use_icon="on" font_icon="&#xe03b;||divi||400" icon_color="#f97316" header_level="h2" _builder_version="4.27.9" _module_preset="default"]
-<p>Camera inspection and hydro-jetting.</p>[/et_pb_blurb]
+[et_pb_blurb title="Leak Detection" url="https://miamirapidplumbing.example/services/leak-detection/" use_icon="on" font_icon="&#xe054;||divi||400" header_level="h3" _builder_version="4.27.9" _module_preset="default" icon_color="#f97316" header_font="Montserrat|700|||||||" header_text_color="#0b2a3c" body_font="Lato||||||||" body_text_color="#475569"]
+<p>Non-invasive leak detection that finds the problem before we open a wall.</p>[/et_pb_blurb]
 [/et_pb_column]
 [/et_pb_row]
-[et_pb_row _builder_version="4.27.9" _module_preset="default"]
-[et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"]
-[et_pb_accordion toggle_level="h3" _builder_version="4.27.9" _module_preset="default"]
-[et_pb_accordion_item title="How fast can you arrive?" open="on" _builder_version="4.27.9" _module_preset="default"]
-<p>Within 60 minutes anywhere in Miami-Dade.</p>[/et_pb_accordion_item]
-[et_pb_accordion_item title="Are you licensed?" open="off" _builder_version="4.27.9" _module_preset="default"]
-<p>Yes, licensed and insured.</p>[/et_pb_accordion_item]
-[/et_pb_accordion]
-[/et_pb_column]
-[/et_pb_row]
 [/et_pb_section]
 [et_pb_section specialty="on" admin_label="Specialty" _builder_version="4.27.9" _module_preset="default"]
 [et_pb_column type="1_4" _builder_version="4.27.9" _module_preset="default"]
```
