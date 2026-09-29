# Gallery (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/gallery.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Our Work")
└─ row columnStructure "4_4"
   └─ column 4_4: heading (h2) · gallery
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Why Choose Us].attrs.module.decoration.background` (`#ffffff`) | a light `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | the same exemplar's `module.decoration.spacing`, all three breakpoints (90/60/45px) | `spacing.section_padding[2][0]` |
| heading `title.decoration.font.font` (desktop/tablet/phone) | `module_styles["divi/heading"][section_label=Why Choose Us, column_type=4_4].attrs.title.decoration.font.font`: `h2`, Montserrat 700, navy `gcid-r6navy0001`, 40/32/28px | `typography.scale.h2` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`) |
| gallery `image.advanced.galleryIds` | the target site's own attachment ids (`wp media list`), comma-separated, never a token and never invented | — |
| gallery `module.advanced.postsNumber` | the number of photos to show per page (`"6"`; the default is `"4"`) | — |
| gallery `galleryGrid.decoration.layout` → `gridColumnCount` | a layout choice: `"3"` / `"2"` / `"1"` for desktop / tablet / phone, so six photos fill two rows (the default grid is four columns) | leave it out |
| gallery `title.decoration.font.font` (captions, `h3` by default) | `typography.heading_font` + `"700"` + the `h2` color (`gcid-r6navy0001`) | same |
| gallery `overlay.advanced.zoomIconColor` | the accent, `gcid-primary-color` | same |
| gallery `overlay.advanced.hoverOverlayColor` | the navy global at 60% (`settings` `{"opacity": 60}`), so the photo shows through on hover | leave it out |

Each thumbnail's `alt` comes from the attachment's Media Library "Alt Text" (live check: the `img` printed it); the
module has no alt attribute. Divi's converter writes only the `tablet`/`phone` column counts of a Divi 4 gallery,
which `validate.py` flags (`W5_HOVER_WITHOUT_DESKTOP`): the recipe states `desktop` too.

## Responsive rules

- The `h2` size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "32px"}`, `phone` `{"size": "28px"}`, from the heading bundle.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- `galleryGrid.decoration.layout` → `gridColumnCount` per breakpoint (3 / 2 / 1) is the gallery's only
  responsive attribute.

## Worked example (sample-tokens.json)

Live check: six attachments rendered as a 3 × 2 grid (one column at 390px); clicking a photo opened Divi's
lightbox with the full-size image and "1 of 6".

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Our Work"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#ffffff"}}},"spacing":{"desktop":{"value":{"padding":{"top":"90px","bottom":"90px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"60px","bottom":"60px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"45px","bottom":"45px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Our Work"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/gallery {"image":{"advanced":{"galleryIds":{"desktop":{"value":"301,302,303,304,305,306"}}}},"module":{"advanced":{"postsNumber":{"desktop":{"value":"6"}}}},"galleryGrid":{"decoration":{"layout":{"desktop":{"value":{"gridColumnCount":"3"}},"tablet":{"value":{"gridColumnCount":"2"}},"phone":{"value":{"gridColumnCount":"1"}}}}},"title":{"decoration":{"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}}}},"overlay":{"advanced":{"zoomIconColor":{"desktop":{"value":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$"}},"hoverOverlayColor":{"desktop":{"value":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{\u0022opacity\u0022:60}}})$"}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one `h2` — no `h1` on this section (the photo captions render as `h3`; turn them off with `module.advanced.showTitleAndCaption` `"off"` if the titles aren't real captions)
- [ ] every `galleryIds` entry exists on the target site, and every photo has its Media Library "Alt Text" filled in
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): navy captions on white 14.9:1; the orange zoom icon sits on the navy tint and is not text
