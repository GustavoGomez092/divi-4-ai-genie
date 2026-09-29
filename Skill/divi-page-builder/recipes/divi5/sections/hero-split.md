# Hero split (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/hero-split.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Hero")
└─ row columnStructure "1_2,1_2"
   ├─ column 1_2: text (Eyebrow) · heading (h1) · text (body) · button
   └─ column 1_2: image
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}`; every block
`builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Hero].attrs.module.decoration.background` | the `colors.global` id whose `roles` include `module.decoration.background.color` and whose value is dark, else a dark `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | `section_exemplars[adminLabel=Hero].attrs.module.decoration.spacing`, all breakpoints it has | `spacing.section_padding[0][0]` |
| row `module.decoration.sizing` → `width`, `maxWidth` | `module_styles["divi/row"][section_label=Hero].attrs.module.decoration.sizing` | `spacing.row.width[0][0]` / `spacing.row.max_width[0][0]` |
| eyebrow `content.decoration.bodyFont.body.font` → `family`, `weight`, `capitalization`, `size`, `letterSpacing` | no eyebrow bundle exists: `typography.heading_font` + fixed `"600"`, `"uppercase"`, `"14px"`, `"2px"` | same |
| eyebrow … → `color` | the accent: `colors.customizer.primary.id` (`gcid-primary-color`) as a `$variable` | same (it always exists) |
| heading `title.decoration.font.font` (desktop/tablet/phone) | `module_styles["divi/heading"][section_label=Hero, column_type=1_2].attrs.title.decoration.font.font`, plus `lineHeight` `"1.1em"` | `typography.scale.h1` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`) |
| body text `content.decoration.bodyFont.body.font` | `module_styles["divi/text"][section_label=Hero, column_type=1_2].attrs.content.decoration.bodyFont.body.font`, plus `lineHeight` `"1.7em"` | `typography.body` (or `typography.body_font` + `colors.customizer.body`) |
| button `button.decoration.button`, `button.decoration.background` → `color` | `module_styles["divi/button"][section_label=Hero, column_type=1_2].attrs` (`enable`, the orange `gcid-r6orange001`); **not** its `module_preset` `r6btnpreset1`, whose white label on the orange is 2.8:1 ([README §2](../README.md#contrast)) | `button.decoration.button` `{"enable": "on"}`, background `gcid-primary-color` |
| button `button.decoration.background` → `hover` `color` | the light orange `gcid-r6orangelt1`: the bundle's `#ea580c` hover is 4.2:1 against the navy label | a lighter shade of the button color that keeps 4.5:1 |
| button `button.decoration.font.font` → `color` | the navy global `gcid-r6navy0001` (its `roles` include `button.decoration.font.font.color`) | the darkest `colors.palette` hex that reaches 4.5:1 on the button |
| button `button.decoration.border` → `radius` (4 corners, `sync` `"on"`) | `shapes.radii[0][0]` (the corners the preset gave) | square corners: leave it out |
| button `button.decoration.font.font` → `family`, `weight`, `size` | `typography.body_font` (never from a bundle, [README §1](../README.md#1-from-a-token-path-to-an-attribute-path)) + `"16px"` | same |
| button `button.decoration.border` → `styles.all.width` | fixed `"0px"`: a flat button | same |
| image `image.decoration.border` → `radius` (4 corners, `sync` `"on"`) | `shapes.radii[0][0]` (a radius variable here) | square corners: leave it out |
| image `image.innerContent` → `src`, `alt` | the site's Media Library and a real description, never a token | — |

The Hero button bundle comes with the preset `r6btnpreset1` (orange, white label, 12px corners). White on the brand
orange is 2.8:1, below WCAG AA, so the example leaves the preset out and states the look itself: the bundle's
orange, a navy label, the radius variable and a light-orange hover.

## Responsive rules

- The heading's size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "42px"}`, `phone`
  `{"size": "34px"}` next to the desktop 56px. No `_last_edited` flag: the keys are the switch.
- The section padding follows the Hero exemplar. Here it is one fluid variable (`clamp(48px, 8vw, 96px)`), so no
  tablet/phone values; a site whose exemplar has literal paddings gets its `tablet`/`phone` values too.
- The two `1_2` columns stack below 981px (image under the copy) with no attribute; to show the image first on
  phone, see the shared recipe's image-left variant.

## Worked example (sample-tokens.json)

The navy background, the padding and the image corners are references (`gcid-r6navy0001`, `gvid-r6secpad01`,
`gvid-r6radius01`), the eyebrow is the accent (`gcid-primary-color`), the button is the orange
`gcid-r6orange001` with the navy label `gcid-r6navy0001` (5.3:1) and the light-orange hover `gcid-r6orangelt1`
(10.3:1); the white heading and the body color have no id and stay literal.

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Hero"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}},"spacing":{"desktop":{"value":{"padding":{"top":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","bottom":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_2,1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"sizing":{"desktop":{"value":{"width":"90%","maxWidth":"1200px"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003e24/7 Emergency Plumbing\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"600","capitalization":"uppercase","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$","size":"14px","letterSpacing":"2px"}}}}}}},"module":{"meta":{"adminLabel":{"desktop":{"value":"Eyebrow"}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Emergency Plumber in Miami"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h1","family":"Montserrat","weight":"700","color":"#ffffff","size":"56px","lineHeight":"1.1em"}},"tablet":{"value":{"size":"42px"}},"phone":{"value":{"size":"34px"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eLicensed, insured plumbers at your door in 60 minutes, day or night, anywhere in Miami-Dade.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#cbd5e1","size":"18px","lineHeight":"1.7em"}}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call (305) 555-0100","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orangelt1\u0022,\u0022settings\u0022:{}}})$"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","size":"16px","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"0px"}},"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/image {"image":{"innerContent":{"desktop":{"value":{"src":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/plumber-at-work.jpg","alt":"Licensed plumber repairing a burst pipe under a Miami kitchen sink"}}},"decoration":{"border":{"desktop":{"value":{"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one H1 on the page
- [ ] the image has alt text and a Media Library URL
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover states included ([README §2](../README.md#contrast)): here white on navy 14.9:1, `#cbd5e1` on navy 10.0:1, the orange eyebrow on navy 5.3:1, the navy button label on orange 5.3:1 and on its hover 10.3:1
