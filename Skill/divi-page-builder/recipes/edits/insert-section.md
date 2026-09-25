# Insert section

**Use for:** adding a new section to an existing page without disturbing anything already there —
a trust bar under the hero, a testimonials block before the closing CTA, an FAQ near the bottom.
The new section should be composed the same way any new page is: from a
[section recipe](../README.md#4-recipe-index)'s worked example, adapted to the target site's own
`tokens.json`, not hand-typed.

## Command sequence

```bash
# 1. Find the anchor section's path — the existing section the new one goes after (or before).
python3 scripts/page_edit.py page.txt outline

# 2. Compose the new section in its own file, following the chosen recipe's Token mapping table
#    against the real site's tokens.json (not sample-tokens.json, once this isn't a worked example).

# 3. Insert it — insert-after appends right after the anchor's closing tag; insert-before prepends
#    right before its opening tag. Both leave every other byte in the file untouched.
python3 scripts/page_edit.py page.txt insert-after \
  "et_pb_section[0]" new-section.txt --out page.txt

# 4. Validate against a baseline of the page before the insert, with --tokens so the new section's
#    own colors/fonts/spacing are checked against the site's palette too.
python3 scripts/validate.py page.txt --baseline original.txt \
  --tokens tokens.json
```

## Fetching a live page first

```bash
python3 scripts/publish.py fetch --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --out original.txt
cp original.txt page.txt
# ...compose new-section.txt from a recipe, then insert-after/insert-before against page.txt...
```

## Applying the result safely

```bash
# 1. Draft a review copy (a NEW draft — no --page-id — the live page stays untouched for now).
python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" \
  --title "Review: <page title> + <new section>"
# 2. Share that draft's preview_url; only proceed once a human approves it.
# 3. Apply the approved content to the live page and publish it in the same request.
python3 scripts/publish.py publish --site "$SITE" --user "$WP_USER" \
  --page-id <ID> --content page.txt --yes
```

## Worked example (`tests/fixtures/valid/handwritten-landing.txt`)

Add a [Trust bar](../sections/trust-bar.md) right after the Hero section:

```bash
python3 scripts/page_edit.py handwritten-landing.txt outline
#   et_pb_section[0]  admin_label=Hero  (1642 chars)
#   et_pb_section[1]  admin_label=Services  (1769 chars)
#   ...

# new-section.txt is Trust bar's own worked example, copied verbatim (sample-tokens.json values).
python3 scripts/page_edit.py handwritten-landing.txt insert-after \
  "et_pb_section[0]" new-section.txt --out inserted.txt

python3 scripts/validate.py inserted.txt \
  --baseline handwritten-landing.txt \
  --tokens recipes/sample-tokens.json
#   1 pre-existing finding(s) also present in the baseline (not blocking):
#     ...W_EXTERNAL_IMAGE et_pb_section[0] > et_pb_row[0] > et_pb_column[1] > et_pb_image[0]
#        src points to client.example, not the site
#   Summary: 0 error(s), 0 warning(s), 1 pre-existing
```

The one warning is the fixture's own pre-existing hero image (unrelated to this edit); the new
Trust Bar section introduces no new errors or warnings because its image URLs already match
`sample-tokens.json`'s site host.

`diff -u` (tags reformatted one-per-line for readability, same caveat as
[change-copy](change-copy.md)) shows the new section landing as a clean insertion, with every byte
of the Hero section above it and the Services/Specialty/Closing sections below it unchanged:

```diff
--- handwritten-landing.pretty.txt
+++ inserted.pretty.txt
@@ -14,6 +14,30 @@
 [/et_pb_column]
 [/et_pb_row]
 [/et_pb_section]
+[et_pb_section admin_label="Trust Bar" _builder_version="4.27.9" _module_preset="default" background_color="#f1f5f9" custom_padding="70px||70px||true|false" custom_padding_tablet="50px||50px||true|false" custom_padding_phone="40px||40px||true|false" custom_padding_last_edited="on|phone"]
+[et_pb_row column_structure="1_5,1_5,1_5,1_5,1_5" _builder_version="4.27.9" _module_preset="default" width="90%" max_width="1200px"]
+[et_pb_column type="1_5" _builder_version="4.27.9" _module_preset="default"]
+[et_pb_image src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-bbb.png" alt="Better Business Bureau A+ Rating" _builder_version="4.27.9" _module_preset="default" max_width="140px" module_alignment="center" filter_saturate="0%" filter_saturate__hover="100%" filter_saturate__hover_enabled="on|hover"]
+[/et_pb_image]
+[/et_pb_column]
+... (four more 1_5 logo columns, then) ...
+[/et_pb_row]
+[/et_pb_section]
 [et_pb_section admin_label="Services" _builder_version="4.27.9" _module_preset="default"]
 [et_pb_row column_structure="1_3,1_3,1_3" _builder_version="4.27.9" _module_preset="default"]
 ...
```

Everything before the insertion point (`et_pb_section[0]`'s full contents) and everything after it
(Services, Specialty, Closing) is byte-identical to the original — `insert-after` only ever writes
at `node.end`, never touching the span before or after it (see `page_edit.py`'s `replace_span(src,
node.end, node.end, snippet)`).
