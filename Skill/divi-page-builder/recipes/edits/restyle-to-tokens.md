# Restyle to tokens

**Use for:** bringing an existing page's off-brand values back in line with the site's
`tokens.json` — a color that was picked with the eyedropper instead of the palette, a font that
snuck in from a pasted Google Doc, padding that doesn't match the site's spacing scale. This edit
never changes copy or structure, only design attribute values, and it's driven entirely by what
`validate.py --tokens` reports, not by eyeballing the page.

## Command sequence

```bash
# 1. List every off-brand/off-palette finding.
python3 Skill/divi-page-builder/scripts/validate.py page.txt --tokens tokens.json
#   W_OFF_PALETTE_COLOR  <attr>=<value> is not in the site's palette
#   W_OFF_BRAND_FONT     <attr> uses '<family>', which the site does not use
#   W_OFF_SCALE_SPACING  Section padding <value> is not one the site uses
#   W_UNKNOWN_GLOBAL_COLOR  <attr> uses global color <gcid>, which the site does not define

# 2. Fix each one with set-attr, using the *actual* token value (colors.palette, typography.*,
#    spacing.section_padding — never a value that merely looks close).
python3 Skill/divi-page-builder/scripts/page_edit.py page.txt set-attr \
  "et_pb_section[0] > ... > et_pb_button[0]" button_bg_color "#f97316" --out page.txt
python3 Skill/divi-page-builder/scripts/page_edit.py page.txt set-attr \
  "et_pb_section[0] > ... > et_pb_button[0]" button_font "Montserrat|600|||||||" --out page.txt

# 3. Re-run validate to confirm every off-brand warning is gone, with --baseline so any warning
#    that existed before this restyle (e.g. an unrelated off-site image) still reports as
#    pre-existing rather than blocking.
python3 Skill/divi-page-builder/scripts/validate.py page.txt --tokens tokens.json \
  --baseline original.txt
```

Fix warnings one attribute at a time and re-run `validate.py --tokens` after each batch — a single
`set-attr` only ever changes the one attribute named, so there's no risk of a color fix silently
resetting a font, and the finding list shrinking confirms each fix landed before moving to the next.

## Fetching a live page first

```bash
python3 Skill/divi-page-builder/scripts/publish.py fetch --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --out original.txt
cp original.txt page.txt
# ...run validate.py --tokens, then set-attr each finding against page.txt...
```

## Applying the result safely

```bash
# 1. Draft a review copy (a NEW draft — no --page-id — the live page stays untouched for now).
python3 Skill/divi-page-builder/scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" \
  --title "Review: <page title> restyle to tokens"
# 2. Share that draft's preview_url; only proceed once a human approves it.
# 3. Apply the approved content to the live page and publish it in the same request.
python3 Skill/divi-page-builder/scripts/publish.py publish --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --content page.txt --yes
```

## Worked example (`tests/fixtures/valid/handwritten-landing.txt`)

The fixture's hero button is on-brand by default, so this worked example first simulates an
off-brand edit (a blue picked outside the palette, a font the site doesn't use) to demonstrate what
`validate.py --tokens` catches, then restyles it back:

```bash
BTN='et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_button[0]'

# Simulate the drift: an eyedropper blue and a pasted-in Arial.
python3 Skill/divi-page-builder/scripts/page_edit.py handwritten-landing.txt set-attr \
  "$BTN" button_bg_color "#2563eb" --out step1.txt
python3 Skill/divi-page-builder/scripts/page_edit.py step1.txt set-attr \
  "$BTN" button_font "Arial|700|||||||" --out offbrand.txt

python3 Skill/divi-page-builder/scripts/validate.py offbrand.txt \
  --tokens Skill/divi-page-builder/recipes/sample-tokens.json
#   warning W_OFF_PALETTE_COLOR  button_bg_color=#2563eb is not in the site's palette
#     hint: Use a color from tokens.json colors.
#   warning W_OFF_BRAND_FONT     button_font uses 'Arial', which the site does not use
#   warning W_EXTERNAL_IMAGE     ...src points to client.example, not the site (pre-existing)
#   Summary: 0 error(s), 3 warning(s), 0 pre-existing

# Fix both, reading the correct values from sample-tokens.json's colors.customizer.accent and
# typography.heading_font (the same button-on-dark-hero bundle module_styles.et_pb_button uses).
python3 Skill/divi-page-builder/scripts/page_edit.py offbrand.txt set-attr \
  "$BTN" button_bg_color "#f97316" --out restyle1.txt
python3 Skill/divi-page-builder/scripts/page_edit.py restyle1.txt set-attr \
  "$BTN" button_font "Montserrat|600|||||||" --out restyled.txt

python3 Skill/divi-page-builder/scripts/validate.py restyled.txt \
  --tokens Skill/divi-page-builder/recipes/sample-tokens.json \
  --baseline handwritten-landing.txt
#   1 pre-existing finding(s) also present in the baseline (not blocking):
#     ...W_EXTERNAL_IMAGE et_pb_section[0] > et_pb_row[0] > et_pb_column[1] > et_pb_image[0]
#   Summary: 0 error(s), 0 warning(s), 1 pre-existing
```

Both off-brand warnings are gone, and the one remaining finding is the fixture's pre-existing hero
image warning (unrelated to this restyle), correctly demoted to non-blocking by `--baseline`.

`diff -u` (reformatted one tag per line, same caveat as [change-copy](change-copy.md)) from the
off-brand version to the restyled version shows only the button's `button_bg_color` and
`button_font` changed — nothing else in the file moved:

```diff
--- offbrand.pretty.txt
+++ restyled.pretty.txt
@@ -5,7 +5,7 @@
 [/et_pb_heading]
 [et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#cbd5e1" text_font_size="18px"]
 <p>Licensed, insured plumbers at your door in 60 minutes.</p>[/et_pb_text]
-[et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_text_color="#ffffff" button_bg_color="#2563eb" button_border_radius="6px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_font="Arial|700|||||||"]
+[et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_text_color="#ffffff" button_bg_color="#f97316" button_border_radius="6px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover" button_font="Montserrat|600|||||||"]
 [/et_pb_button]
 [/et_pb_column]
 [et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"]
```
