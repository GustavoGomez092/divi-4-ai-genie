# Replace section (Divi 5)

**Use for:** swapping an entire section on a Divi 5 page for a rebuilt one: a thin section the converter
carried over from Divi 4 becomes a proper Divi 5 section, or a section built for an old brand is rebuilt for
the current one. Keep the old section's admin label (`module.meta.adminLabel`) so the page's outline reads the
same, and take design values from `tokens.json` (its `section_exemplars` and `module_styles`), not invented
ones. The Divi 4 version is [edits/replace-section.md](../../edits/replace-section.md).

## What `replace` does

[`page_edit.py`](../../../scripts/page_edit.py) `replace PATH FILE` cuts out exactly the span of the block at
`PATH`, from its opening delimiter through its closing one, and puts the file's block markup there as
written. Every byte before and after that span stays as it was, including the blank lines and escapes of a
Visual Builder page. The file is checked first, like [insert-section](insert-section.md#what-insert-after--insert-before-do)'s:
clean Divi 5 block markup only, and a warning for any block without `builderVersion`.

The new blocks are new content, so they carry the site's Divi version as `builderVersion`, even where the old
section's blocks carried an older one: that version decides which render-time migrations Divi runs on the
blocks you wrote ([page-format.md → builderVersion](../../../reference/divi5/page-format.md#builderversion)).

To change one module rather than a whole section, the same verb takes any path
(`"section[1] > row[0] > column[1] > text[0]"`); for copy or a few values, [change-copy](change-copy.md) and
[restyle-to-tokens](restyle-to-tokens.md) are smaller edits.

## Command sequence

```bash
# 1. See what's there today.
python3 scripts/page_edit.py page.html outline
python3 scripts/page_edit.py page.html extract "section[N]"

# 2. Write the new section to its own file (same admin label; values from tokens.json) and check it alone.
python3 scripts/validate.py new-section.html --fragment --tokens tokens.json

# 3. Replace: only the old section's span changes.
python3 scripts/page_edit.py page.html replace "section[N]" new-section.html --out page.html

# 4. Validate against the page as it was.
python3 scripts/validate.py page.html --baseline original.html --tokens tokens.json
```

Fetch a live page first and apply the result through a reviewed draft, as in the
[Divi 4 recipe](../../edits/replace-section.md#applying-the-result-safely).

## Worked example (`tests/fixtures/divi5/converted/heldout-inscope.html`)

The fixture's `section[3]` ("CTA") is one converted Call To Action module in a full-width column. Rebuild it
as a split band: headline and line of copy on the left, the button on the right. `tokens5.json` is the one
[insert-section](insert-section.md#worked-example-testsfixturesdivi5convertedheldout-inscopehtml) extracts from
the fixture.

```bash
python3 scripts/page_edit.py heldout-inscope.html outline | grep "section\[3\]"
#   placeholder[0] > section[3]  admin_label=CTA  (2070 chars)
#   placeholder[0] > section[3] > row[0]  admin_label=None  (1767 chars)
#   placeholder[0] > section[3] > row[0] > column[0]  admin_label=None  (1577 chars)
#   placeholder[0] > section[3] > row[0] > column[0] > cta[0]  admin_label=None  title="Ready to plan your remodel?"  (1333 chars)
python3 scripts/page_edit.py heldout-inscope.html extract "section[3]"
#   <!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"CTA"}}},"decoration":{"background":{"desktop":{"value":{"color":"#fef3c7"}}},...
```

`new-cta.html` keeps the admin label `CTA` and the section's `#fef3c7` background, takes the section padding from
`spacing.section_padding` (`120px`), the heading and body fonts from `typography` (Playfair Display, Open Sans)
in colors the old section used (`#0f172a`, `#334155`), and the button colors the old CTA's button had
(`#b45309`, hover `#92400e`, both in `colors.palette`):

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"CTA"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#fef3c7"}}},"spacing":{"desktop":{"value":{"padding":{"top":"120px","right":"","bottom":"120px","left":""}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_2,1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Ready to plan your remodel?"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Playfair Display","weight":"700","color":"#0f172a","size":"40px"}}}}}},"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eFree 45-minute in-home consultation within 10 miles.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Open Sans","color":"#334155","size":"20px"}}}}}}},"module":{"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Book a Consultation","linkUrl":"#book"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"600","color":"#ffffff","size":"18px"}}}},"background":{"desktop":{"value":{"color":"#b45309"},"hover":{"color":"#92400e"}}}}},"module":{"advanced":{"alignment":{"desktop":{"value":"right"},"tablet":{"value":"left"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

```bash
python3 scripts/validate.py new-cta.html --fragment --tokens tokens5.json
#   Summary: 0 error(s), 0 warning(s), 0 pre-existing

python3 scripts/page_edit.py heldout-inscope.html replace "section[3]" new-cta.html --out replaced.html
python3 scripts/page_edit.py replaced.html outline | grep "section\[3\]\|section\[4\]  "
#   placeholder[0] > section[3]  admin_label=CTA  (2263 chars)
#   placeholder[0] > section[3] > row[0]  admin_label=None  (1906 chars)
#   placeholder[0] > section[3] > row[0] > column[0]  admin_label=None  (936 chars)
#   placeholder[0] > section[3] > row[0] > column[0] > heading[0]  admin_label=None  title="Ready to plan your remodel?"  (357 chars)
#   placeholder[0] > section[3] > row[0] > column[0] > text[0]  admin_label=None  (379 chars)
#   placeholder[0] > section[3] > row[0] > column[1]  admin_label=None  (761 chars)
#   placeholder[0] > section[3] > row[0] > column[1] > button[0]  admin_label=None  title="Book a Consultation"  (561 chars)
#   placeholder[0] > section[4]  admin_label=Closing header  (1586 chars)

python3 scripts/validate.py replaced.html --baseline heldout-inscope.html --tokens tokens5.json
#   3 pre-existing finding(s) also present in the baseline (not blocking):
#   replaced.html:2:21396 error E5_MULTIPLE_H1 placeholder[0] > section[4] > fullwidth-header[0]
#   replaced.html:2:4820 warning W_HEADING_SKIP placeholder[0] > section[0] > row[0] > column[1] > number-counter[0]
#   replaced.html:2:13321 warning W_HEADING_SKIP placeholder[0] > section[2] > row[0] > column[0] > toggle[0]
#   Summary: 0 error(s), 0 warning(s), 3 pre-existing
```

The result is exactly the original with the old section's span swapped for the new file's markup:

```bash
python3 -c '
import sys; sys.path.insert(0, "scripts"); import divi5_blocks as d
r = lambda p: open(p, encoding="utf-8", newline="").read()
src, new, out = r("heldout-inscope.html"), r("new-cta.html").strip(), r("replaced.html")
old = d.parse(src).find("placeholder[0] > section[3]")
print(out == src[:old.start] + new + src[old.end:])'
#   True
```
