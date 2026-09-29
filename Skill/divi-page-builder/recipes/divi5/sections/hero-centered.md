# Hero centered (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/hero-centered.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Hero")
└─ row columnStructure "4_4"
   └─ column 4_4: text (Eyebrow) · heading (h1) · text (body) · button — all centered, 720px wide
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}`; every block
`builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Hero].attrs.module.decoration.background` | the `colors.global` id whose `roles` include `module.decoration.background.color` and whose value is dark, else a dark `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | `section_exemplars[adminLabel=Hero].attrs.module.decoration.spacing` | `spacing.section_padding[0][0]` |
| row `module.decoration.sizing` → `width`, `maxWidth` | no row bundle for a single `4_4` column on a dark section: `spacing.row.width[0][0]` / `spacing.row.max_width[0][0]` | same |
| eyebrow `content.decoration.bodyFont.body.font` | as in [hero-split](hero-split.md#field-mapping): `typography.heading_font` + `"600"`/`"uppercase"`/`"14px"`/`"2px"`, color `gcid-primary-color`; plus `textAlign` `"center"` | same |
| heading `title.decoration.font.font` (desktop/tablet/phone) | no `column_type=4_4` dark `h1` bundle: `typography.scale.h1` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`); plus `lineHeight` `"1.1em"`, `textAlign` `"center"` | same |
| body text `content.decoration.bodyFont.body.font` | `module_styles["divi/text"][column_type=4_4]` on a dark section (the "Free Quote CTA" bundle: tone and column type match, [README §3](../README.md#3-choosing-a-module_styles-bundle-by-context)), plus `lineHeight` `"1.7em"`, `textAlign` `"center"` | `typography.body` |
| button `modulePreset`, `button.decoration.button`, `.background` (+`hover`), `.font.font` → `color`, `.border` → `radius` | `module_styles["divi/button"][column_type=4_4]` on a dark section → `module_preset` + `attrs` | no preset; `{"enable": "on"}`, background `gcid-primary-color`, radius `shapes.radii[0][0]` |
| button `button.decoration.font.font` → `family`, `weight` | `typography.body_font` | same |
| button `button.decoration.border` → `styles.all.width` | fixed `"0px"`: without it Divi draws a 2px border in the label color | same |
| copy block width: `module.decoration.sizing` → `maxWidth` `"720px"`, `alignment` `"center"` on the eyebrow, heading and body text; the button's `module.advanced.alignment` `"center"` | a layout choice, not a token | — |

`textAlign` centers the lines inside each module; `sizing.alignment` centers the 720px-wide module itself in the
column. Both are needed.

## Responsive rules

- The heading's size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "42px"}`, `phone`
  `{"size": "34px"}`.
- The section padding follows the Hero exemplar (one fluid variable here, so no tablet/phone values).
- `maxWidth` `"720px"` needs no phone value: it is a maximum, so the modules shrink to the column.

## Worked example (sample-tokens.json)

The button is the "Free Quote CTA" bundle: preset `11111111-2222-3333-4444-555555555555` (its CSS is unknown, so
the bundle's own attributes come with it), navy label `gcid-r6navy0001`, orange background `gcid-r6orange001`,
corners `gvid-r6radius01`.

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Hero"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}},"spacing":{"desktop":{"value":{"padding":{"top":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","bottom":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"sizing":{"desktop":{"value":{"width":"90%","maxWidth":"1200px"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003e24/7 Emergency Plumbing\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"600","capitalization":"uppercase","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$","size":"14px","letterSpacing":"2px","textAlign":"center"}}}}}}},"module":{"meta":{"adminLabel":{"desktop":{"value":"Eyebrow"}}},"decoration":{"sizing":{"desktop":{"value":{"maxWidth":"720px","alignment":"center"}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Miami's Fastest Emergency Plumbers"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h1","family":"Montserrat","weight":"700","color":"#ffffff","size":"56px","lineHeight":"1.1em","textAlign":"center"}},"tablet":{"value":{"size":"42px"}},"phone":{"value":{"size":"34px"}}}}}},"module":{"decoration":{"sizing":{"desktop":{"value":{"maxWidth":"720px","alignment":"center"}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eLicensed, insured plumbers dispatched anywhere in Miami-Dade, day or night.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#f1f5f9","size":"18px","lineHeight":"1.7em","textAlign":"center"}}}}}}},"module":{"decoration":{"sizing":{"desktop":{"value":{"maxWidth":"720px","alignment":"center"}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call (305) 555-0100","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"#ea580c"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"0px"}},"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}}}},"module":{"advanced":{"alignment":{"desktop":{"value":"center"}}}},"modulePreset":["11111111-2222-3333-4444-555555555555"],"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one H1 on the page
