# Trust bar (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/trust-bar.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

**Only badges the client holds.** Each logo is a membership, rating or license from the client's brief, with its
logo file in the site's Media Library. The example's five are the Divi 4 recipe's placeholders for the sample
brand; never add a badge to fill the row.

## Structure
```text
section (adminLabel "Trust Bar", light grey band)
└─ row columnStructure "1_5,1_5,1_5,1_5,1_5" (90% / 1200px)
   ├─ column 1_5: image (logo, grey → color on hover)
   ├─ column 1_5: image
   ├─ column 1_5: image
   ├─ column 1_5: image
   └─ column 1_5: image
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}`; every block
`builderVersion` = `site.divi_version`. No heading: the bar adds nothing to the outline.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color`, `module.decoration.spacing` → `padding` | `section_exemplars[adminLabel=By The Numbers].attrs.module.decoration` (`#f1f5f9`; 70/50/40px on all three breakpoints) | the light grey in `colors.palette`; `spacing.section_padding[0][0]` |
| row `module.decoration.sizing` → `width`, `maxWidth` | `spacing.row.width[0][0]` / `spacing.row.max_width[0][0]` (`90%` / `1200px`) | same |
| image `image.innerContent` → `src`, `alt` | the logo file and the organization's name ("Better Business Bureau A+ Rating"), never the filename or "logo" | — |
| image `module.advanced.sizing` → `maxWidth` `"140px"`, `alignment` `"center"` | a layout choice: five logos of different shapes at one size (printed as `max-width:140px` with auto side margins, live check) | same |
| image `module.decoration.filters` → `saturate` `"0%"`, `hover` `{"saturate": "100%"}` | a design convention, not a token: grey at rest, color on hover (a `:hover` state; no `__hover_enabled` flag on Divi 5) | same |

`alt` goes in `image.innerContent`. Divi's converter moves Divi 4's `alt` into a custom attribute row
(`module.decoration.attributes`); that works too, but it is not where a person would set it.

## Responsive rules

- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The five `1_5` columns stack one logo per line below 981px with no attribute; `maxWidth` needs no phone value.
- Touch screens don't hover, so on a phone the logos stay grey: fine for a trust signal, but don't put
  information only in the logo's colors.

## Worked example (sample-tokens.json)

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Trust Bar"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#f1f5f9"}}},"spacing":{"desktop":{"value":{"padding":{"top":"70px","bottom":"70px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"50px","bottom":"50px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"40px","bottom":"40px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_5,1_5,1_5,1_5,1_5"}}},"decoration":{"sizing":{"desktop":{"value":{"width":"90%","maxWidth":"1200px"}}},"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_5"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-bbb.png","alt":"Better Business Bureau A+ Rating"}}}},"module":{"advanced":{"sizing":{"desktop":{"value":{"maxWidth":"140px","alignment":"center"}}}},"decoration":{"filters":{"desktop":{"value":{"saturate":"0%"},"hover":{"saturate":"100%"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_5"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-angi.png","alt":"Angi Super Service Award"}}}},"module":{"advanced":{"sizing":{"desktop":{"value":{"maxWidth":"140px","alignment":"center"}}}},"decoration":{"filters":{"desktop":{"value":{"saturate":"0%"},"hover":{"saturate":"100%"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_5"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-google-guaranteed.png","alt":"Google Guaranteed"}}}},"module":{"advanced":{"sizing":{"desktop":{"value":{"maxWidth":"140px","alignment":"center"}}}},"decoration":{"filters":{"desktop":{"value":{"saturate":"0%"},"hover":{"saturate":"100%"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_5"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-nexstar.png","alt":"Nexstar Network Member"}}}},"module":{"advanced":{"sizing":{"desktop":{"value":{"maxWidth":"140px","alignment":"center"}}}},"decoration":{"filters":{"desktop":{"value":{"saturate":"0%"},"hover":{"saturate":"100%"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_5"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/logo-florida-licensed.png","alt":"State of Florida Licensed Contractor"}}}},"module":{"advanced":{"sizing":{"desktop":{"value":{"maxWidth":"140px","alignment":"center"}}}},"decoration":{"filters":{"desktop":{"value":{"saturate":"0%"},"hover":{"saturate":"100%"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] no heading module in this section
- [ ] every image has an `alt` naming the organization and a Media Library `src`; every badge is one the client holds
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): the section has no text; logos are images whose meaning is carried by their `alt`, so a greyed logo needs no ratio, but a logo that is mostly text should stay readable on `#f1f5f9`
