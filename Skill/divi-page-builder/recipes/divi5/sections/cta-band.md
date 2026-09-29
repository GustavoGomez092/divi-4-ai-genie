# CTA band (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/cta-band.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Free Quote CTA", navy band)
└─ row columnStructure "4_4"
   └─ column 4_4: cta (title h4, text, button)
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Free Quote CTA].attrs.module.decoration.background`: the navy global `gcid-r6navy0001` | the darkest `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | the same exemplar's spacing, all three breakpoints (70/50/40px) | `spacing.section_padding[0][0]` |
| cta `title.decoration.font.font` | `module_styles["divi/heading"][section_label=Free Quote CTA, column_type=4_4]`: `h4`, Montserrat 700, `#ffffff`, 30px | `typography.scale.h4` |
| cta `content.decoration.bodyFont.body.font` | `module_styles["divi/text"][section_label=Free Quote CTA, column_type=4_4]`: Lato 400 `#f1f5f9` 18px | `typography.body` |
| cta `button.decoration` → `button`, `background`, `font.font`, `border` | `module_styles["divi/button"][section_label=Free Quote CTA, column_type=4_4]`: orange `gcid-r6orange001`, navy label, radius `gvid-r6radius01`; plus hover `gcid-r6orangelt1` (not the bundle's `#ea580c`, [contrast](../README.md#contrast)), border width 0, Lato 16px | the accent with a navy label |
| cta `module.decoration.background` → `color` | the section's own color (the navy global): the module's default background is the accent `gcid-primary-color`, which would paint an orange box behind white text | same |
| cta `module.decoration.spacing` → `padding` 0 on all sides | Divi 4's `use_background_color="off"` (the module sits flush in the band; the converter writes the same) | same |
| cta `title.innerContent`, `content.innerContent`, `button.innerContent` → `text`, `linkUrl` | the client's brief: the offer, the phone number or booking link | — |

The bundle's button carries the preset `11111111-2222-3333-4444-555555555555`; it is a `divi/button` preset, so the
`divi/cta` module doesn't take it (the button's attributes are written out instead).

## Responsive rules

- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The 30px `h4` needs no smaller phone size; the CTA module stacks title, text and button at every width.
- **Heading level:** the band's title is `h4` here, one level below the `h3` it follows in the
  [service landing](../pages/service-landing.md) page. In your page, make it one level below the heading just
  before the band (`W_HEADING_SKIP` otherwise).

## Worked example (sample-tokens.json)

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Free Quote CTA"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}},"spacing":{"desktop":{"value":{"padding":{"top":"70px","bottom":"70px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"50px","bottom":"50px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"40px","bottom":"40px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/cta {"title":{"innerContent":{"desktop":{"value":"Ready To Fix That Leak?"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h4","family":"Montserrat","weight":"700","color":"#ffffff","size":"30px"}}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eNo obligation, no hidden fees, just an honest number.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#f1f5f9","size":"18px"}}}}}}},"button":{"innerContent":{"desktop":{"value":{"text":"Get My Free Quote","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orangelt1\u0022,\u0022settings\u0022:{}}})$"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"16px"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"0px"}},"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}}}},"module":{"decoration":{"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}},"spacing":{"desktop":{"value":{"padding":{"top":"0px","right":"0px","bottom":"0px","left":"0px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] no `h1`/`h2` from this band; its title is one level below the heading just before it
- [ ] the CTA module shows no second (orange) box inside the navy band
- [ ] the button text names the action ("Get My Free Quote"), and its link is the client's number or booking page
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): `#ffffff` title on navy 14.9:1, `#f1f5f9` text 13.6:1; the button's navy label on orange 5.3:1 and on the hover 10.3:1
