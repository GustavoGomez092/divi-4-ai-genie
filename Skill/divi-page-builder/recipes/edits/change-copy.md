# Change copy

**Use for:** editing text on an existing page without touching its design — a new phone number,
a reworded headline, a button label, a paragraph of body copy. Nothing about layout, color, font
or spacing should change; if it does, you've drifted into [restyle-to-tokens](restyle-to-tokens.md)
or [replace-section](replace-section.md) instead.

## When to use `set-attr` vs. `extract`/`replace`

- **Attribute copy** (titles, button text, eyebrow labels, alt text) — use
  [`page_edit.py`](../../scripts/page_edit.py)'s `set-attr` command. It rebuilds only the one
  opening tag being changed; every other byte in the file, including that same tag's other
  attributes, is untouched.
- **Body copy** (an `et_pb_text`'s inner HTML, a blurb's paragraph) — `set-attr` can't reach
  content between an opening and closing tag, so `extract` the node first to see its exact current
  HTML, edit that HTML in a scratch file, then `replace` the whole node with the edited version.
  `replace` still only touches that one node's span — copy the node's own opening tag byte-for-byte
  into the replacement file so you don't accidentally change its `_builder_version`, font or color
  attributes along with the copy.

## Command sequence

```bash
# 1. Find the exact path of the module you want to change.
python3 scripts/page_edit.py page.txt outline

# 2a. Attribute copy: set-attr writes straight to --out (or stdout).
python3 scripts/page_edit.py page.txt set-attr \
  "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_button[0]" \
  button_text "New Button Text" --out page.txt

# 2b. Body copy: extract, edit, replace.
python3 scripts/page_edit.py page.txt extract \
  "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]" > /tmp/node.txt
#   ...edit /tmp/node.txt's inner HTML in place, keeping its opening/closing tags as-is...
python3 scripts/page_edit.py page.txt replace \
  "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]" /tmp/node.txt --out page.txt

# 3. Validate against a baseline of the page *before* this edit, so any finding that already
#    existed (e.g. an off-site image the copy change didn't touch) is reported as pre-existing,
#    not blocking — only genuinely new problems fail the check.
python3 scripts/validate.py page.txt --baseline original.txt \
  --tokens tokens.json
```

## Fetching a live page first

If the page being edited is live, fetch its current content before editing anything:

```bash
python3 scripts/publish.py fetch --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --out original.txt
cp original.txt page.txt
# ...run the set-attr / extract+replace sequence above against page.txt...
```

Keep `original.txt` around unmodified — it's both the `--baseline` input for validation and the
thing `diff -u` compares the edited file against to prove only the intended lines changed.

## Applying the result safely

Never publish an edited copy straight over a **published** page — `draft --page-id` refuses to
touch a page whose status is already `publish`/`future`/`private`. Draft a review copy first, get
it approved, then apply the edit and publish the live page in one request:

```bash
# 1. Draft a review copy (a NEW draft — no --page-id — so the live page is never touched yet).
python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" \
  --title "Review: <page title> copy update"
# 2. Share that draft's preview_url; only proceed once a human approves it.
# 3. Apply the approved content to the live page and publish it in the same request.
python3 scripts/publish.py publish --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --content page.txt --yes
```

## Worked example (`tests/fixtures/valid/handwritten-landing.txt`)

Change the hero's button label from "Call (305) 555-0100" to something less number-heavy, and
extend the hero body copy to mention after-hours availability:

```bash
python3 scripts/page_edit.py handwritten-landing.txt set-attr \
  "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_button[0]" \
  button_text "Call Now — We Answer 24/7" --out step1.txt

# extract shows the current node so the replacement's opening/closing tags can be copied exactly:
python3 scripts/page_edit.py step1.txt extract \
  "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]"
#   -> [et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||"
#       text_text_color="#cbd5e1" text_font_size="18px"]<p>Licensed, insured plumbers at your door
#       in 60 minutes.</p>[/et_pb_text]

python3 scripts/page_edit.py step1.txt replace \
  "et_pb_section[0] > et_pb_row[0] > et_pb_column[0] > et_pb_text[0]" new-body.txt --out step2.txt

python3 scripts/validate.py step2.txt --baseline handwritten-landing.txt
#   Summary: 0 error(s), 0 warning(s), 0 pre-existing
```

`diff -u` proves only the two targeted tags changed — the fixture is one line of shortcode, so for
readability here each tag is put on its own line before diffing (`page_edit.py` itself never
reformats the file; `tests/test_page_edit.py` proves the real output stays byte-for-byte identical
outside the target span):

```diff
--- handwritten-landing.pretty.txt
+++ step2.pretty.txt
@@ -4,8 +4,8 @@
 [et_pb_heading title="Emergency Plumber in Miami" title_level="h1" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#ffffff" title_font_size="56px" title_font_size_tablet="42px" title_font_size_phone="34px" title_font_size_last_edited="on|phone"]
 [/et_pb_heading]
 [et_pb_text _builder_version="4.27.9" _module_preset="default" text_font="Lato||||||||" text_text_color="#cbd5e1" text_font_size="18px"]
-<p>Licensed, insured plumbers at your door in 60 minutes.</p>[/et_pb_text]
-[et_pb_button button_text="Call (305) 555-0100" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_text_color="#ffffff" button_bg_color="#f97316" button_border_radius="6px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover"]
+<p>Licensed, insured plumbers at your door in 60 minutes — nights, weekends and holidays.</p>[/et_pb_text]
+[et_pb_button button_text="Call Now — We Answer 24/7" button_url="tel:+13055550100" _builder_version="4.27.9" _module_preset="default" custom_button="on" button_text_color="#ffffff" button_bg_color="#f97316" button_border_radius="6px" button_bg_color__hover="#ea580c" button_bg_color__hover_enabled="on|hover"]
 [/et_pb_button]
 [/et_pb_column]
 [et_pb_column type="1_2" _builder_version="4.27.9" _module_preset="default"]
```

Every other section (Services, Specialty, Closing) is byte-identical, confirmed by `diff -u`
showing no other hunks.
