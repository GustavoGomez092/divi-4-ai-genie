# Service area list (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/service-area-list.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Service Areas")
├─ row columnStructure "4_4"
│  └─ column 4_4: heading (h2)
└─ row columnStructure "1_3,1_3,1_3"
   ├─ column 1_3: text (<ul> of cities, some linked)
   ├─ column 1_3: text
   └─ column 1_3: text
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `module_styles["divi/section"][admin_label=About].attrs.module.decoration.background` (`#ffffff`, a light section reused for its tone) | a light `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | the same bundle's `module.decoration.spacing`, all three breakpoints (80/55/40px) | `spacing.section_padding[3][0]` |
| heading `title.decoration.font.font` (desktop/tablet/phone) | `module_styles["divi/heading"][section_label=Why Choose Us, column_type=4_4].attrs.title.decoration.font.font`: `h2`, Montserrat 700, navy `gcid-r6navy0001`, 40/32/28px | `typography.scale.h2` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`) |
| body text `content.decoration.bodyFont.body.font` | `typography.body_font` + `"400"` + the light-section body color `#475569` (the "About" text bundle's color; a `colors.palette` entry whose `roles` include `content.decoration.bodyFont.body.font.color`) + `"16px"` | same |
| list `content.decoration.bodyFont.link.font` → `color`, `weight`, `style` | the navy global (`gcid-r6navy0001`), `"700"`, `["underline"]` | the heading color, bold, underlined |
| city names, city page URLs (in `content.innerContent`) | the client's service-area list and site map, never a token | — |

The Divi 4 recipe colors the links with the accent orange: 2.8:1 on white, too low for text. Navy passes
(14.9:1), but navy against the `#475569` list text is only 2.0:1, so the links are also bold and underlined:
something other than color marks them as links.

## Responsive rules

- The `h2` size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "32px"}`, `phone` `{"size": "28px"}`, from the heading bundle.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The three `1_3` columns stack below 981px, one list after another, with no attribute.

## Worked example (sample-tokens.json)

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Service Areas"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#ffffff"}}},"spacing":{"desktop":{"value":{"padding":{"top":"80px","bottom":"80px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"55px","bottom":"55px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"40px","bottom":"40px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Areas We Serve"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_3,1_3,1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cul\u003e\u003cli\u003e\u003ca href=\u0022https://miamirapidplumbing.example/service-areas/miami/\u0022\u003eMiami\u003c/a\u003e\u003c/li\u003e\u003cli\u003e\u003ca href=\u0022https://miamirapidplumbing.example/service-areas/miami-beach/\u0022\u003eMiami Beach\u003c/a\u003e\u003c/li\u003e\u003cli\u003e\u003ca href=\u0022https://miamirapidplumbing.example/service-areas/coral-gables/\u0022\u003eCoral Gables\u003c/a\u003e\u003c/li\u003e\u003cli\u003eBrickell\u003c/li\u003e\u003c/ul\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569","size":"16px"}}}},"link":{"font":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","weight":"700","style":["underline"]}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cul\u003e\u003cli\u003e\u003ca href=\u0022https://miamirapidplumbing.example/service-areas/hialeah/\u0022\u003eHialeah\u003c/a\u003e\u003c/li\u003e\u003cli\u003eKendall\u003c/li\u003e\u003cli\u003eHomestead\u003c/li\u003e\u003cli\u003eCutler Bay\u003c/li\u003e\u003c/ul\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569","size":"16px"}}}},"link":{"font":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","weight":"700","style":["underline"]}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cul\u003e\u003cli\u003e\u003ca href=\u0022https://miamirapidplumbing.example/service-areas/doral/\u0022\u003eDoral\u003c/a\u003e\u003c/li\u003e\u003cli\u003eAventura\u003c/li\u003e\u003cli\u003ePinecrest\u003c/li\u003e\u003cli\u003ePalmetto Bay\u003c/li\u003e\u003c/ul\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569","size":"16px"}}}},"link":{"font":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","weight":"700","style":["underline"]}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one `h2` — no `h1` on this section
- [ ] every city with an existing location page is linked; no city links to a page that doesn't exist
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): navy underlined links on white 14.9:1, `#475569` list text on white 7.6:1
