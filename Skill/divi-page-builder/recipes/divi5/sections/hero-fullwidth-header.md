# Hero fullwidth header (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/hero-fullwidth-header.md). This page is its
Divi 5 structure, field mapping and worked example; how to read them is in the
[Divi 5 recipes README](../README.md). The module is [`divi/fullwidth-header`](../../../reference/divi5/modules/fullwidth-header.md).

## Structure
```text
section type "fullwidth" (adminLabel "Hero")
└─ fullwidth-header (title h1 · subhead · buttonOne · buttonTwo)
```

The section sets `module.advanced.type` → `"fullwidth"` and holds the module directly (no row or column); it
carries `module.decoration.layout` → `{"display": "block"}`. Every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Hero].attrs.module.decoration.background` | the `colors.global` id whose `roles` include `module.decoration.background.color` and whose value is dark, else a dark `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | `section_exemplars[adminLabel=Hero].attrs.module.decoration.spacing` | `spacing.section_padding[0][0]` |
| header `module.decoration.background` → `color` | the same as the section's. **Set it**: the module's own default background is `gcid-primary-color` (the site's accent), not the section's color | same |
| header `title.decoration.font.font` (desktop/tablet/phone) | no `divi/fullwidth-header` bundle: `typography.scale.h1` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`); plus `lineHeight` `"1.1em"`, `textWrap` `"balance"` | same |
| header `subhead.decoration.font.font` | the split hero's body copy bundle, `module_styles["divi/text"][section_label=Hero, column_type=1_2].attrs.content.decoration.bodyFont.body.font` (light copy on the same dark section), plus `lineHeight` `"1.7em"` | `typography.body` |
| header `buttonOne.decoration.button`, `.background` | `module_styles["divi/button"][section_label=Hero]` → its `attrs`' `button.decoration.button` and `.background` color, moved to `buttonOne` (a preset of `divi/button` doesn't apply to this module) | `{"enable": "on"}`, background `gcid-primary-color` |
| header `buttonOne.decoration.background` → `hover` `color` | the light orange `gcid-r6orangelt1`, not the bundle's `#ea580c` (4.2:1 against the navy label, [README §2](../README.md#contrast)) | a lighter shade of the button color that keeps 4.5:1 |
| header `buttonOne.decoration.font.font` → `color` | the navy global `gcid-r6navy0001` (5.3:1 on the orange; white would be 2.8:1) | the darkest `colors.palette` hex that reaches 4.5:1 on the button |
| header `buttonOne`/`buttonTwo` `.border` → `radius` | `shapes.radii[0][0]` | square corners: leave it out |
| header `buttonOne.decoration.border` → `styles.all.width` `"0px"` | fixed: a flat button (Divi otherwise draws a 2px border in the label color) | same |
| header `buttonTwo` (outline): `.background` `"transparent"`, `.border.styles.all` `{"width": "2px", "color": "#ffffff"}`, label `#ffffff` | no secondary-button bundle: build it from `"transparent"` and the heading color | same |
| both buttons' `.font.font` → `family`, `weight`, `size` | `typography.body_font` + `"16px"` | same |
| both buttons' `.spacing` → `margin` `{"top": "6px", "bottom": "6px"}` | fixed: a gap when the buttons stack on phone | same |
| header `module.advanced.text.text` → `orientation` `"center"` | a layout choice | — |

Don't set `content.advanced.maxWidth` from `spacing.row.max_width`: the header keeps its text inside a container
of 80% of at most 1080px, so a wider maximum changes nothing. `textWrap` `"balance"` keeps the two-line title
even instead of leaving one word on the second line.

## Responsive rules

- The title's size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "42px"}`, `phone`
  `{"size": "34px"}`.
- The section padding follows the Hero exemplar (one fluid variable here, so no tablet/phone values).
- On phone the two buttons stack; the 6px top/bottom margins keep them apart, and the 16px label keeps
  "Call (305) 555-0100" on one line in the narrow header.
- `module.advanced.headerFullscreen` stays unset (its default is `"off"`); see the shared recipe's fullscreen
  variant.

## Worked example (sample-tokens.json)

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Hero"}}},"advanced":{"type":{"desktop":{"value":"fullwidth"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}},"spacing":{"desktop":{"value":{"padding":{"top":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","bottom":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6secpad01\u0022,\u0022settings\u0022:{}}})$","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/fullwidth-header {"title":{"innerContent":{"desktop":{"value":"Emergency Plumber in Miami"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h1","family":"Montserrat","weight":"700","color":"#ffffff","size":"56px","lineHeight":"1.1em","textWrap":"balance"}},"tablet":{"value":{"size":"42px"}},"phone":{"value":{"size":"34px"}}}}}},"subhead":{"innerContent":{"desktop":{"value":"Licensed, insured plumbers at your door in 60 minutes, day or night, anywhere in Miami-Dade."}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#cbd5e1","size":"18px","lineHeight":"1.7em"}}}}}},"buttonOne":{"innerContent":{"desktop":{"value":{"text":"Call (305) 555-0100","linkUrl":"tel:+13055550100"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orangelt1\u0022,\u0022settings\u0022:{}}})$"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"16px"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"0px"}},"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}},"spacing":{"desktop":{"value":{"margin":{"top":"6px","bottom":"6px","syncVertical":"on","syncHorizontal":"off"}}}}}},"buttonTwo":{"innerContent":{"desktop":{"value":{"text":"Get a Free Quote","linkUrl":"/free-quote/"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"transparent"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#ffffff","size":"16px"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"2px","color":"#ffffff"}},"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}},"spacing":{"desktop":{"value":{"margin":{"top":"6px","bottom":"6px","syncVertical":"on","syncHorizontal":"off"}}}}}},"module":{"advanced":{"text":{"text":{"desktop":{"value":{"orientation":"center"}}}}},"decoration":{"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one H1 on the page (the header's title defaults to `h1`; the recipe states it)
- [ ] a header or logo image, if added, has its `alt` in `image.innerContent` / `logo.innerContent`
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover states included ([README §2](../README.md#contrast)): here white on navy 14.9:1 (title and the outline button), `#cbd5e1` on navy 10.0:1, the navy label on orange 5.3:1 and on its hover 10.3:1
