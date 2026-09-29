# Services grid (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/services-grid.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Services")
├─ row columnStructure "4_4"
│  └─ column 4_4: heading (h2)
└─ row columnStructure "1_3,1_3,1_3"
   ├─ column 1_3: blurb (icon, title h3 linked to the service page, body)
   ├─ column 1_3: blurb
   └─ column 1_3: blurb
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Why Choose Us].attrs.module.decoration.background` (`#ffffff`) | a light `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | the same exemplar's `module.decoration.spacing`, all three breakpoints (90/60/45px) | `spacing.section_padding[2][0]` |
| heading `title.decoration.font.font` (desktop/tablet/phone) | `module_styles["divi/heading"][section_label=Why Choose Us, column_type=4_4].attrs.title.decoration.font.font`: `h2`, Montserrat 700, navy `gcid-r6navy0001`, 40/32/28px | `typography.scale.h2` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`) |
| blurb row `module.advanced.columnStructure` | `section_exemplars[adminLabel=Why Choose Us].children[1]` (`"1_3,1_3,1_3"`) | `"1_3,1_3,1_3"` |
| blurb `title.decoration.font.font` → `headingLevel` | `module_styles["divi/blurb"][section_label=Why Choose Us, column_type=1_3].attrs.title.decoration.font.font` (`"h3"`; the blurb's own default is `h4`) | `"h3"` |
| blurb `title.decoration.font.font` → `family`, `weight`, `color` | no blurb font bundle: `typography.heading_font` + `"700"` + the `h2` color (`gcid-r6navy0001`) | same |
| blurb `imageIcon.advanced.color` | the same blurb bundle (`gcid-r6orange001`) | leave it out: the default is `gcid-primary-color` |
| blurb `imageIcon.decoration.sizing` → `alignSelf` `"flex-start"`, `iconFontSize` `"56px"` | a layout choice: the icon sits over the left-aligned title instead of centered, at 56px instead of 96px | — |
| blurb `imageIcon.innerContent` → `useIcon` `"on"`, `icon` `{unicode, type, weight}` | not a token: a real glyph per service ([value-formats §Icons](../../../reference/divi5/value-formats.md#icons)) | — |
| blurb `title.innerContent` → `url` | the service's own page on this site, never a token | — |
| blurb `content.decoration.bodyFont.body.font` | `typography.body_font` + `"400"` + `#475569` (the light-section body color) | same |

The blurb bundle also carries `imageIcon.decoration.animation` (a slide-in): Divi's converter writes it on every
Divi 4 blurb (Divi 4's default icon animation), so leave it out ([README §1](../README.md#1-from-a-token-path-to-an-attribute-path)).
Icon placement is `imageIcon.decoration.sizing`: the schema's `imageIcon.advanced.alignment` and
`imageIcon.advanced.width` validate but print no CSS on Divi 5.13.1 (live check).

## Responsive rules

- The `h2` size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "32px"}`, `phone` `{"size": "28px"}`, from the heading bundle.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The three `1_3` columns stack below 981px, one blurb per line, with no attribute; the 56px icon needs no phone
  value.

## Worked example (sample-tokens.json)

Heading and blurb titles in the navy global, icons in the orange global (`gcid-r6orange001`), section color and
paddings literal as in the "Why Choose Us" exemplar (the sample has no ids for them).

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Services"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#ffffff"}}},"spacing":{"desktop":{"value":{"padding":{"top":"90px","bottom":"90px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"60px","bottom":"60px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"45px","bottom":"45px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Our Plumbing Services"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_3,1_3,1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Drain Cleaning","url":"https://miamirapidplumbing.example/services/drain-cleaning/"}}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xe036;","type":"divi","weight":"400"}}}},"advanced":{"color":{"desktop":{"value":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"}}},"decoration":{"sizing":{"desktop":{"value":{"alignSelf":"flex-start","iconFontSize":"56px"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eFast, hydro-jet drain clearing for kitchens, showers and main lines.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569"}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Water Heater Repair","url":"https://miamirapidplumbing.example/services/water-heater-repair/"}}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xe038;","type":"divi","weight":"400"}}}},"advanced":{"color":{"desktop":{"value":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"}}},"decoration":{"sizing":{"desktop":{"value":{"alignSelf":"flex-start","iconFontSize":"56px"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eSame-day repair and replacement for tank and tankless water heaters.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569"}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_3"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/blurb {"title":{"innerContent":{"desktop":{"value":{"text":"Leak Detection","url":"https://miamirapidplumbing.example/services/leak-detection/"}}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}}}},"imageIcon":{"innerContent":{"desktop":{"value":{"useIcon":"on","icon":{"unicode":"\u0026#xe054;","type":"divi","weight":"400"}}}},"advanced":{"color":{"desktop":{"value":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"}}},"decoration":{"sizing":{"desktop":{"value":{"alignSelf":"flex-start","iconFontSize":"56px"}}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eNon-invasive leak detection that finds the problem before we open a wall.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569"}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one `h2`, and every blurb title renders as `h3` — no `h1` on this section
- [ ] every blurb with a matching service page has `title.innerContent` → `url` set
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): navy titles on white 14.9:1, `#475569` body on white 7.6:1; the orange icons (2.8:1 on white) are decorative next to their text titles, so never use that orange for text here
