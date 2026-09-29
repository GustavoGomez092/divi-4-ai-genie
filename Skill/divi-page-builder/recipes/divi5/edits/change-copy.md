# Change copy (Divi 5)

**Use for:** editing text on an existing Divi 5 page without touching its design: a reworded headline,
a button label, a paragraph of body copy, an image's alt text. Nothing about layout, color, font or spacing
should change; if it does, you've drifted into [restyle-to-tokens](restyle-to-tokens.md) or
[replace-section](replace-section.md). The Divi 4 version is [edits/change-copy.md](../../edits/change-copy.md).

## One verb for all copy: `set-attr`

In Divi 5 every piece of copy lives in a block's JSON attributes, body HTML included
([page-format.md → All content lives in the JSON](../../../reference/divi5/page-format.md#all-content-lives-in-the-json)),
so [`page_edit.py`](../../../scripts/page_edit.py) `set-attr` reaches all of it. There is no extract/edit/replace
dance as in Divi 4.

- `NAME` is a dotted attribute path: `title.innerContent` (heading, blurb, CTA, toggle titles),
  `content.innerContent` (text, blurb, CTA and toggle bodies, HTML), `button.innerContent.text` (a button label;
  the link stays), `image.innerContent.alt`. The module's reference page
  (`reference/divi5/modules/<module>.md`) lists every attribute.
- `VALUE` is plain text or HTML: `page_edit.py` escapes it canonically for you (`<` becomes `\u003c`, `&` becomes
  `\u0026`, and so on). A VALUE that parses as JSON is stored as JSON, so quote a number you mean as text
  (`'"2026"'`).
- It writes the desktop value (`--breakpoint tablet` / `--breakpoint phone` for the others). A path that goes
  inside a value object (`button.innerContent.text`) changes that one key and keeps the others (`linkUrl`).
- Only the block you edit is rewritten, in WordPress's canonical form, with its `builderVersion` unchanged;
  every other byte of the page stays as it was. On a page saved by the Visual Builder that block's other
  values may come out escaped differently (`\\` becomes `\u005c`): the same value, written the way WordPress
  writes it.

## Command sequence

```bash
# 1. Find the path of the module. Paths may leave out the leading "placeholder[0] >".
python3 scripts/page_edit.py page.html outline

# 2. Change the copy (each command reads one file and writes another; --out may also be the same file).
python3 scripts/page_edit.py page.html set-attr "section[0] > row[0] > column[0] > heading[0]" \
  title.innerContent "New headline" --out page.html

# 3. Validate against the page as it was before the edit: only new findings block.
python3 scripts/validate.py page.html --baseline original.html --tokens tokens.json
```

If the page is live, fetch it first (`publish.py fetch ... --out original.html`, then `cp original.html page.html`)
and apply the result through a reviewed draft, exactly as in the
[Divi 4 recipe](../../edits/change-copy.md#applying-the-result-safely). `page_edit.py --tokens tokens.json`
(or `--site-major 5`) refuses to touch Divi 4 shortcode on a Divi 5 site, and block content on a Divi 4 site.

## Worked example (`tests/fixtures/divi5/converted/heldout-inscope.html`)

Reword the hero headline, the hero button and the hero paragraph:

```bash
python3 scripts/page_edit.py heldout-inscope.html outline
#   placeholder[0]  admin_label=None  (22559 chars)
#   placeholder[0] > section[0]  admin_label=Hero image  (6442 chars)
#   placeholder[0] > section[0] > row[0]  admin_label=None  (5436 chars)
#   placeholder[0] > section[0] > row[0] > column[0]  admin_label=None  (2850 chars)
#   placeholder[0] > section[0] > row[0] > column[0] > heading[0]  admin_label=None  title="Kitchen & Bath Remodeling Done Right"  (624 chars)
#   placeholder[0] > section[0] > row[0] > column[0] > text[0]  admin_label=None  (929 chars)
#   placeholder[0] > section[0] > row[0] > column[0] > button[0]  admin_label=None  title="Start Your Project"  (1055 chars)
#   ...

COL='section[0] > row[0] > column[0]'
python3 scripts/page_edit.py heldout-inscope.html set-attr "$COL > heading[0]" \
  title.innerContent "Kitchen & Bath Remodels, Done Right" --out step1.html
python3 scripts/page_edit.py step1.html set-attr "$COL > button[0]" \
  button.innerContent.text "Get a Free Quote" --out step2.html
python3 scripts/page_edit.py step2.html set-attr "$COL > text[0]" content.innerContent \
  '<p>Design, permits and build under one roof — nights and weekends too. <a href="#quote">Get a quote</a>.</p><ul><li>Licensed contractors</li><li>Fixed-price bids</li></ul>' \
  --out step3.html

python3 scripts/page_edit.py step3.html extract "$COL > button[0]"
#   <!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Get a Free Quote","linkUrl":"#start","linkTarget":"on"}}},...

python3 scripts/validate.py step3.html --baseline heldout-inscope.html
#   3 pre-existing finding(s) also present in the baseline (not blocking):
#   step3.html:2:21226 error E5_MULTIPLE_H1 placeholder[0] > section[4] > fullwidth-header[0]
#   step3.html:2:4843 warning W_HEADING_SKIP placeholder[0] > section[0] > row[0] > column[1] > number-counter[0]
#   step3.html:2:13344 warning W_HEADING_SKIP placeholder[0] > section[2] > row[0] > column[0] > toggle[0]
#   Summary: 0 error(s), 0 warning(s), 3 pre-existing
```

The three findings were already in the fixture; the edit adds none. To see that nothing else moved, compare
each step with the one before it: the byte counts that match at the start and the end of the file cover
everything except the changed words (this fixture is already canonical, so re-rendering the edited block
changes nothing else in it):

```bash
same() { python3 -c 'import os,sys;a,b=(open(p,"rb").read() for p in sys.argv[1:]);i=len(os.path.commonprefix([a,b]));j=len(os.path.commonprefix([a[i:][::-1],b[i:][::-1]]));print(f"{i} bytes same before, {j} same after; {len(a)-i-j} -> {len(b)-i-j} bytes changed")' "$@"; }
same heldout-inscope.html step1.html
#   1678 bytes same before, 20892 same after; 3 -> 2 bytes changed
same step1.html step2.html
#   3211 bytes same before, 19343 same after; 18 -> 16 bytes changed
same step2.html step3.html
#   2729 bytes same before, 19841 same after; 0 -> 28 bytes changed
```
