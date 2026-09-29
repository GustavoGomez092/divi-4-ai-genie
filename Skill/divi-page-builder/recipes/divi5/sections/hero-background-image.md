# Hero background image (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/hero-background-image.md). This page is its
Divi 5 structure, field mapping and worked example; how to read them is in the
[Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Hero"; background image + brand-navy gradient over it)
└─ row columnStructure "4_4"
   └─ column 4_4: text (Eyebrow) · heading (h1) · text (body) · button
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}`; every block
`builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `image.url` | the site's own Media Library photo, never a token | — |
| … → `image.size` `"cover"`, `image.position` `"center"` | fixed pattern values | same |
| … → `gradient` `{"enabled": "on", "direction": "180deg", "overlaysImage": "on", "stops": […]}` | fixed: `enabled` (without it no gradient renders) and `overlaysImage` (the tint goes over the photo) | same |
| … → `gradient.stops[].color` | the Hero exemplar's background color reference (`gcid-r6navy0001`) with `settings` `{"opacity": 85}` at `position` `0` and `{"opacity": 55}` at `100` ([README §2](../README.md#2-variable-or-literal)) | the navy as `rgba(…, 0.85)` / `rgba(…, 0.55)` literals |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | `section_exemplars[adminLabel=Hero].attrs.module.decoration.spacing` | `spacing.section_padding[0][0]` |
| row `module.decoration.sizing` → `width`, `maxWidth` | `spacing.row.width[0][0]` / `spacing.row.max_width[0][0]` (no bundle for a `4_4` column here) | same |
| eyebrow `content.decoration.bodyFont.body.font` | as in [hero-split](hero-split.md#field-mapping): `typography.heading_font` + `"600"`/`"uppercase"`/`"14px"`/`"2px"`, color `gcid-primary-color` | same |
| heading `title.decoration.font.font` (desktop/tablet/phone) | `typography.scale.h1` (no `4_4` dark `h1` bundle), plus `lineHeight` `"1.1em"` | same |
| body text `content.decoration.bodyFont.body.font` | `module_styles["divi/text"][column_type=4_4]` on a dark section ("Free Quote CTA"), plus `lineHeight` `"1.7em"` | `typography.body` |
| button `modulePreset` + `button.decoration.*` | `module_styles["divi/button"][column_type=4_4]` on a dark section → `module_preset` + `attrs`; `family`/`weight` from `typography.body_font`; `border.styles.all.width` `"0px"` | as in [hero-centered](hero-centered.md#field-mapping) |

A gradient stop `position` is a plain number (`0`, `100`), never `"0%"`: a unit renders no gradient at all
(`E5_GRADIENT_STOP_POSITION`).

## Responsive rules

- The heading's size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "42px"}`, `phone`
  `{"size": "34px"}`.
- The section padding follows the Hero exemplar (one fluid variable here, so no tablet/phone values).
- `image.size` `"cover"` and `image.position` `"center"` need no phone value, unless the photo's focal point
  needs a different crop: a `phone` value of `module.decoration.background` → `{"image": {"position": "center
  top"}}` (art direction, not a token).

## Worked example (sample-tokens.json)

The overlay is the brand navy global at 85% and 55% opacity, so the tint follows a later re-theme of the navy;
Divi prints it as `hsl(from var(--gcid-r6navy0001) … / 0.85)`.

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Hero"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"image":{"url":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/plumbing-van-job-site.jpg","size":"cover","position":"center"},"gradient":{"enabled":"on","direction":"180deg","overlaysImage":"on","stops":[{"position":0,"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{\u0022opacity\u0022:85}}})$"},{"position":100,"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{\u0022opacity\u0022:55}}})$"}]}}}},"spacing":{"desktop":{"value":{"padding":{"top":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","bottom":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"sizing":{"desktop":{"value":{"width":"90%","maxWidth":"1200px"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003e24/7 Emergency Plumbing\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"600","capitalization":"uppercase","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$","size":"14px","letterSpacing":"2px"}}}}}}},"module":{"meta":{"adminLabel":{"desktop":{"value":"Eyebrow"}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Burst Pipe? We're On Our Way"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h1","family":"Montserrat","weight":"700","color":"#ffffff","size":"56px","lineHeight":"1.1em"}},"tablet":{"value":{"size":"42px"}},"phone":{"value":{"size":"34px"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/text {"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eLicensed, insured plumbers dispatched across Miami-Dade around the clock.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#f1f5f9","size":"18px","lineHeight":"1.7em"}}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/button {"button":{"innerContent":{"desktop":{"value":{"text":"Call (305) 555-0100","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"#ea580c"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"0px"}},"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}}}},"modulePreset":["11111111-2222-3333-4444-555555555555"],"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — it uploads a local photo to the Media Library; review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one H1 on the page
- [ ] the background photo is a Media Library URL, and the heading and body text stay readable over it
