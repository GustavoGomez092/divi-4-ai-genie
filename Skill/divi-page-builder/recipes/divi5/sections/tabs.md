# Tabs (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/tabs.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Tabs")
└─ row columnStructure "4_4"
   └─ column 4_4: heading (h2) · tabs
      ├─ tab "Residential"
      ├─ tab "Commercial"
      └─ tab "Emergency"
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Why Choose Us].attrs.module.decoration.background` (`#ffffff`) | a light `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | the same exemplar's `module.decoration.spacing`, all three breakpoints (90/60/45px) | `spacing.section_padding[2][0]` |
| heading `title.decoration.font.font` (desktop/tablet/phone) | `module_styles["divi/heading"][section_label=Why Choose Us, column_type=4_4].attrs.title.decoration.font.font`: `h2`, Montserrat 700, navy `gcid-r6navy0001`, 40/32/28px | `typography.scale.h2` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`) |
| tabs `activeTab.decoration.background` → `color` | no tabs bundle: the accent, `colors.customizer.primary.id` (`gcid-primary-color`) | same (it always exists) |
| tabs `activeTab.decoration.font.font` → `color` | the navy global (`gcid-r6navy0001`): 5.3:1 on the orange | the darkest `colors.palette` hex that reaches 4.5:1 on the accent |
| tabs `tab.decoration.background` → `color` (inactive tabs) | the section's background (`#ffffff`) | same |
| tabs `tab.decoration.font.font` → `family`, `weight`, `color`, `size` | `typography.body_font` + `"400"`, the navy global, `"16px"` | same |
| each tab `content.decoration.bodyFont.body.font` | `typography.body_font` + `"400"` + `#475569` + `"16px"`, `lineHeight` `"1.7em"` | same |
| each tab `title.innerContent`, `content.innerContent` | the client's copy | — |

The Divi 4 recipe puts a white label on the orange active tab (2.8:1); the label is navy here.

## Responsive rules

- The `h2` size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "32px"}`, `phone` `{"size": "28px"}`, from the heading bundle.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The tab controls stack into a list on phone by themselves (live check at 390px); no tabs attribute needs a
  `tablet`/`phone` value.

## Worked example (sample-tokens.json)

Live check: clicking the second control moved `et_pb_tab_active` to it and showed its panel in place of the first.

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Tabs"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#ffffff"}}},"spacing":{"desktop":{"value":{"padding":{"top":"90px","bottom":"90px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"60px","bottom":"60px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"45px","bottom":"45px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Plumbing Services By Property Type"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/tabs {"activeTab":{"decoration":{"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$"}}},"font":{"font":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}}}},"tab":{"decoration":{"background":{"desktop":{"value":{"color":"#ffffff"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"16px"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/tab {"title":{"innerContent":{"desktop":{"value":"Residential"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eRepairs, repipes and fixture installs for single-family homes and condos across Miami-Dade.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569","size":"16px","lineHeight":"1.7em"}}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/tab {"title":{"innerContent":{"desktop":{"value":"Commercial"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eScheduled maintenance and emergency response for restaurants, offices and multi-family buildings.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569","size":"16px","lineHeight":"1.7em"}}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/tab {"title":{"innerContent":{"desktop":{"value":"Emergency"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003e24/7 dispatch for burst pipes, active leaks and sewage backups — on site within 60 minutes.\u003c/p\u003e"}},"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569","size":"16px","lineHeight":"1.7em"}}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/tabs --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one `h2` above the tabs — no `h1` on this section; every tab's copy reads on its own (all panels are in the page source)
- [ ] on the draft, clicking each tab control shows its panel
- [ ] on the draft, the tabs work from the keyboard: Tab reaches every tab control with a visible focus, Enter opens its panel, and check whether the arrow keys move between tabs
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): the navy active label on orange 5.3:1, navy inactive labels on white 14.9:1, `#475569` panel text on white 7.6:1
