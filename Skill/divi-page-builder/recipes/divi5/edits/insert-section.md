# Insert section (Divi 5)

**Use for:** adding a new section to an existing Divi 5 page without disturbing anything already there: a
financing band under the hero, testimonials before the closing CTA, an FAQ near the bottom. Compose the new
section as you would for a new page, from the site's own `tokens.json`, not hand-typed values. The Divi 4
version is [edits/insert-section.md](../../edits/insert-section.md).

## What `insert-after` / `insert-before` do

[`page_edit.py`](../../../scripts/page_edit.py) splices the file's block markup, exactly as written, right after
the anchor block's closing delimiter (`insert-after`) or right before its opening one (`insert-before`). Nothing
else in the page is rewritten, so blank lines and escapes a Visual Builder page carries stay as they are. It
refuses the file (exit 1, page untouched) when it isn't clean Divi 5 block markup: Divi 4 shortcode, a block
that doesn't parse or is never closed, stray text between blocks, or a `divi/placeholder` wrapper (the page
already has one; insert the sections, not the wrapper).

- **Anchor on sections.** `section[N]` (short for `placeholder[0] > section[N]`) keeps the new section inside the
  page's `divi/placeholder`.
- **`builderVersion` on every new block**: the site's Divi version (`tokens.json` → `site.divi_version`, else
  `5.13.1`), [page-format.md → builderVersion](../../../reference/divi5/page-format.md#builderversion).
  `page_edit.py` warns about a block without one and inserts it as written; it never fills it in.
- **Structure blocks state their layout** (`"display":"block"`),
  [structure.md → layout form](../../../reference/divi5/structure.md#the-layout-form-display-block-on-structure-blocks).
- **Heading levels follow the page**: run `outline`, and let `validate.py` tell you when the new heading skips a
  level (below).

## Command sequence

```bash
# 1. Find the anchor section.
python3 scripts/page_edit.py page.html outline

# 2. Write the new section to its own file, from tokens.json, and check it on its own.
python3 scripts/validate.py new-section.html --fragment --tokens tokens.json

# 3. Insert it after (or before) the anchor.
python3 scripts/page_edit.py page.html insert-after "section[0]" new-section.html --out page.html

# 4. Validate against the page as it was: only new findings block.
python3 scripts/validate.py page.html --baseline original.html --tokens tokens.json
```

Fetch a live page first and apply the result through a reviewed draft, as in the
[Divi 4 recipe](../../edits/insert-section.md#applying-the-result-safely).

## Worked example (`tests/fixtures/divi5/converted/heldout-inscope.html`)

Add a financing band right after the hero. The fixture has no `tokens.json`, so this example extracts one from
the page itself; with a real site, use the site's own:

```bash
python3 scripts/extract_tokens.py --content-file heldout-inscope.html --out tokens5.json
#   wrote tokens5.json: 33 style bundles across 17 modules, 21 palette colors, 5 section exemplars, 0 presets
```

`financing-section.html` takes every value from `tokens5.json`: the dark background (`#0f172a`) and the
section padding (`spacing.section_padding`, `120px`) of the hero, the heading font (`typography.heading_font`,
Playfair Display, in the `#fef3c7` the hero heading uses) and the body font of the hero text (Open Sans 300,
`#e2e8f0`, 20px). No site version is known, so `builderVersion` is the schema's `5.13.1`:

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Financing"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#0f172a"}}},"spacing":{"desktop":{"value":{"padding":{"top":"120px","right":"","bottom":"120px","left":""}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Remodel now, pay over time"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Playfair Display","weight":"700","color":"#fef3c7","size":"30px"}}}}}},"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003e0% financing for 12 months on remodels over $10,000 \u0026mdash; \u003ca href=\u0022#quote\u0022\u003eask about it\u003c/a\u003e when you get your quote.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Open Sans","weight":"300","color":"#e2e8f0","size":"20px","lineHeight":"1.6em"}}}}}}},"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

```bash
python3 scripts/validate.py financing-section.html --fragment --tokens tokens5.json
#   Summary: 0 error(s), 0 warning(s), 0 pre-existing

python3 scripts/page_edit.py heldout-inscope.html insert-after "section[0]" financing-section.html \
  --out inserted.html
python3 scripts/page_edit.py inserted.html outline | grep -v "> row"
#   placeholder[0]  admin_label=None  (24199 chars)
#   placeholder[0] > section[0]  admin_label=Hero image  (6442 chars)
#   placeholder[0] > section[1]  admin_label=Financing  (1640 chars)
#   placeholder[0] > section[2]  admin_label=Features  (6199 chars)
#   placeholder[0] > section[3]  admin_label=FAQ + testimonials  (6203 chars)
#   placeholder[0] > section[4]  admin_label=CTA  (2070 chars)
#   placeholder[0] > section[5]  admin_label=Closing header  (1586 chars)
#   placeholder[0] > section[5] > fullwidth-header[0]  admin_label=None  title="Your dream kitchen starts here"  (1273 chars)

python3 scripts/validate.py inserted.html --baseline heldout-inscope.html --tokens tokens5.json
#   inserted.html:2:9267 warning W_HEADING_SKIP placeholder[0] > section[2] > row[0] > column[0] > blurb[0]
#     Heading level jumps from h2 to h4 at [divi/blurb] title.decoration.font.font
#   3 pre-existing finding(s) also present in the baseline (not blocking):
#   ...
#   Summary: 0 error(s), 1 warning(s), 3 pre-existing
```

The page's outline runs h1 (hero) → h3 (counters) → h4 (feature blurbs), so an h2 here makes the blurbs below
it skip a level. Fix the new heading, not the page:

```bash
python3 scripts/page_edit.py inserted.html set-attr "section[1] > row[0] > column[0] > heading[0]" \
  title.decoration.font.font.headingLevel h3 --out inserted.html
python3 scripts/validate.py inserted.html --baseline heldout-inscope.html --tokens tokens5.json
#   Summary: 0 error(s), 0 warning(s), 3 pre-existing
```

(`title.decoration.font.font.headingLevel` goes inside the font value: only `headingLevel` changes, the family,
weight, color and size stay.) The three pre-existing findings were in the fixture before the insert.

Every byte of the original is still there, in order, around the new section (`insert-before "section[1]"`
gives the same file):

```bash
python3 -c '
import sys; sys.path.insert(0, "scripts"); import divi5_blocks as d
r = lambda p: open(p, encoding="utf-8", newline="").read()
src, new, out = r("heldout-inscope.html"), r("financing-section.html").strip(), r("inserted.html")
end = d.parse(src).find("placeholder[0] > section[0]").end
print(out[:end] == src[:end], out[end + len(new):] == src[end:])'
#   True True
```

The first `True` is everything up to the end of the hero section, the second everything from the new section's
end to the end of the file.
