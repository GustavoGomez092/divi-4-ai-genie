# Restyle to tokens (Divi 5)

**Use for:** bringing an existing Divi 5 page's off-brand values back in line with the site's `tokens.json`: a
color picked with the eyedropper instead of the palette, a font pasted in from elsewhere, padding off the site's
spacing scale. This edit never changes copy or structure, only design values, and it is driven by what
`validate.py --tokens` reports, not by eyeballing the page. The Divi 4 version is
[edits/restyle-to-tokens.md](../../edits/restyle-to-tokens.md).

## Reading a finding, writing the fix

`validate.py --tokens` names the block and the dotted attribute path of each off-brand value:

- `W_OFF_PALETTE_COLOR`: `<attr path>=<color> is not in the site's palette`
- `W_OFF_BRAND_FONT`: `<attr path> uses '<family>', which the site does not use`
- `W_OFF_SCALE_SPACING`: section padding that is not one the site uses

That path is what [`page_edit.py`](../../../scripts/page_edit.py) `set-attr` takes. A path that goes inside a
value (`button.decoration.background.color`, `title.decoration.font.font.family`) changes that one key and keeps
the rest of the value: a background's gradient or image stays when only its color changes, a font's size and
weight stay when only its family changes. Pass `--breakpoint tablet|phone` for a tablet or phone value and
`--state hover` for a hover one; the default is the desktop value.

Where the right value comes from, in order:

1. **A global color**, when `tokens.json` → `colors.global` (or `colors.customizer`) has the one you need: write
   the `$variable(...)$` reference rather than its hex, so the page follows the site when the color changes
   ([value-formats.md → `$variable` references](../../../reference/divi5/value-formats.md#variable-references-global-colors-and-design-variables)).
2. **The `module_styles` bundle** for the module, picked by `contexts` (section label and tone, column type) that
   match where the module sits: the site's own value for exactly this spot.
3. **`colors.palette`, `typography`, `spacing`** for anything the bundle doesn't carry. Never a value that merely
   looks close.

Only the edited block is rewritten, with its `builderVersion` unchanged; the rest of the page keeps every byte.

## Command sequence

```bash
# 1. List every off-brand finding (with --baseline to separate what was already there).
python3 scripts/validate.py page.html --tokens tokens.json --baseline original.html

# 2. Fix each one at the path the finding names, with the token value.
python3 scripts/page_edit.py page.html set-attr "section[0] > row[0] > column[0] > button[0]" \
  button.decoration.background.color "#f97316" --out page.html

# 3. Re-run step 1 until the off-brand warnings are gone.
```

Fetch a live page first and apply the result through a reviewed draft, as in the
[Divi 4 recipe](../../edits/restyle-to-tokens.md#applying-the-result-safely).

## Worked example (`tests/fixtures/divi5/converted/heldout-inscope.html`)

The fixture's hero button is on-brand, so the example first simulates drift (an eyedropper blue and a pasted-in
Arial), lets `validate.py` catch it, then restyles it back. `tokens5.json` is the one
[insert-section](insert-section.md#worked-example-testsfixturesdivi5convertedheldout-inscopehtml) extracts from
the fixture.

```bash
BTN='section[0] > row[0] > column[0] > button[0]'

# Simulate the drift.
python3 scripts/page_edit.py heldout-inscope.html set-attr "$BTN" \
  button.decoration.background.color "#2563eb" --out step1.html
python3 scripts/page_edit.py step1.html set-attr "$BTN" \
  button.decoration.font.font.family Arial --out offbrand.html

python3 scripts/validate.py offbrand.html --tokens tokens5.json --baseline heldout-inscope.html
#   offbrand.html:2:3109 warning W_OFF_BRAND_FONT placeholder[0] > section[0] > row[0] > column[0] > button[0]
#     button.decoration.font.font.family uses 'Arial', which the site does not use
#   offbrand.html:2:3109 warning W_OFF_PALETTE_COLOR placeholder[0] > section[0] > row[0] > column[0] > button[0]
#     button.decoration.background.color=#2563eb is not in the site's palette
#   3 pre-existing finding(s) also present in the baseline (not blocking):
#   ...
#   Summary: 0 error(s), 2 warning(s), 3 pre-existing

# The site's own values for this spot: the divi/button bundle whose context is the hero's 2_3 column.
python3 -c 'import json; t = json.load(open("tokens5.json")); b = t["module_styles"]["divi/button"][0]; d = b["attrs"]["button"]["decoration"]; print(b["contexts"][0]["section_label"], b["contexts"][0]["column_type"], d["background"]["desktop"]["value"], d["font"]["font"]["desktop"]["value"]["family"])'
#   Hero image 2_3 {'color': '#fbbf24'} Montserrat

python3 scripts/page_edit.py offbrand.html set-attr "$BTN" \
  button.decoration.background.color "#fbbf24" --out restyle1.html
python3 scripts/page_edit.py restyle1.html set-attr "$BTN" \
  button.decoration.font.font.family Montserrat --out restyled.html

python3 scripts/validate.py restyled.html --tokens tokens5.json --baseline heldout-inscope.html
#   Summary: 0 error(s), 0 warning(s), 3 pre-existing
```

Both warnings are gone; the three pre-existing findings were in the fixture before the drift. Only the button's
two values moved, and since set-attr keeps each key where it was, the restyled page is the original again, byte
for byte (`same` is the helper from [change-copy](change-copy.md#worked-example-testsfixturesdivi5convertedheldout-inscopehtml)):

```bash
same offbrand.html restyled.html
#   3575 bytes same before, 18825 same after; 168 -> 173 bytes changed
cmp restyled.html heldout-inscope.html && echo identical
#   identical
```

On a site whose `tokens.json` lists global colors, write the reference instead of the hex; `page_edit.py`
stores it as a string and escapes its quotes canonically:

```bash
python3 scripts/page_edit.py offbrand.html set-attr "$BTN" button.decoration.background.color \
  '$variable({"type":"color","value":{"name":"gcid-primary-color","settings":{}}})$' --out var.html
python3 scripts/page_edit.py var.html extract "$BTN"
#   ..."background":{"desktop":{"value":{"color":"$variable({"type":"color","value":{"name":"gcid-primary-color","settings":{}}})$"}...
```
