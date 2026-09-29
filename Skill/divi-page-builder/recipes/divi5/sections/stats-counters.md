# Stats counters (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/stats-counters.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "By The Numbers")
└─ row columnStructure "1_4,1_4,1_4,1_4"
   ├─ column 1_4: number-counter
   ├─ column 1_4: number-counter
   ├─ column 1_4: number-counter
   └─ column 1_4: number-counter (a percentage)
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=By The Numbers].attrs.module.decoration.background` (`#f1f5f9`) | a light `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | the same exemplar's spacing, all three breakpoints (70/50/40px) | `spacing.section_padding[0][0]` |
| row `module.advanced.columnStructure` | the pattern's four-up `"1_4,1_4,1_4,1_4"` (the exemplar's `"1_2,1_2"` holds two counters) | same |
| counter `number.decoration.font.font` | `module_styles["divi/number-counter"][section_label=By The Numbers].attrs.number.decoration.font.font`: Montserrat 700, navy `gcid-r6navy0001`, 56px; plus `tablet` `"40px"` / `phone` `"32px"` | `typography.scale.h1` → `family`, `weight` + the `h2` color + `size` |
| counter `title.decoration.font.font` | the same bundle's `title.decoration.font.font`: Lato 400, `#475569`, 18px; plus `headingLevel` `"h3"` stated (the module's default, written out so the outline is visible; only `h1`–`h6` validate) | `typography.body_font` + the body color |
| counter `number.advanced.enablePercentSign` | the same bundle: `"off"` on every counter that is not a percentage (the module's default is `"on"`); leave it out on a real percentage | same |
| counter `number.innerContent`, `title.innerContent` | the client's brief or fact sheet — never a token, never invented | — |

The number is free text that counts up and then prints verbatim ([number-counter gotchas](../../../reference/divi5/modules/number-counter.md#gotchas)):
a trailing `+` or `%` is fine (`"25+"`, `"1,200+"`); a leading `$` shows `NaN` while it counts; a symbol after a
decimal adds a digit to the count (`"4.9★"` counts `0.00` … `4.89`), so a rating is `"4.9"` with the star in the
title; `"24/7"` or `"60-minute"` belong in the title or a text block, not the number.

## Responsive rules

- The numbers shrink per breakpoint: `number.decoration.font.font` → `tablet` `{"size": "40px"}`, `phone`
  `{"size": "32px"}`.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The four `1_4` columns show two per line at tablet width and one per line on phone, with no attribute.

## Worked example (sample-tokens.json)

The numbers are the sample brand's placeholders: on a real page every figure comes from the client.

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"By The Numbers"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#f1f5f9"}}},"spacing":{"desktop":{"value":{"padding":{"top":"70px","bottom":"70px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"50px","bottom":"50px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"40px","bottom":"40px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_4,1_4,1_4,1_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/number-counter {"number":{"innerContent":{"desktop":{"value":"15"}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"56px"}},"tablet":{"value":{"size":"40px"}},"phone":{"value":{"size":"32px"}}}}},"advanced":{"enablePercentSign":{"desktop":{"value":"off"}}}},"title":{"innerContent":{"desktop":{"value":"Years in Business"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Lato","weight":"400","color":"#475569","size":"18px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/number-counter {"number":{"innerContent":{"desktop":{"value":"5000"}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"56px"}},"tablet":{"value":{"size":"40px"}},"phone":{"value":{"size":"32px"}}}}},"advanced":{"enablePercentSign":{"desktop":{"value":"off"}}}},"title":{"innerContent":{"desktop":{"value":"Jobs Completed"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Lato","weight":"400","color":"#475569","size":"18px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/number-counter {"number":{"innerContent":{"desktop":{"value":"24"}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"56px"}},"tablet":{"value":{"size":"40px"}},"phone":{"value":{"size":"32px"}}}}},"advanced":{"enablePercentSign":{"desktop":{"value":"off"}}}},"title":{"innerContent":{"desktop":{"value":"Hour Emergency Response"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Lato","weight":"400","color":"#475569","size":"18px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/number-counter {"number":{"innerContent":{"desktop":{"value":"100"}},"decoration":{"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"56px"}},"tablet":{"value":{"size":"40px"}},"phone":{"value":{"size":"32px"}}}}}},"title":{"innerContent":{"desktop":{"value":"Satisfaction Guarantee"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Lato","weight":"400","color":"#475569","size":"18px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

The heading row (put it first in the section, before the counters row):

```text
<!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Our Plumbing Services"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] the counter titles are `h3`: the section sits under an `h2` on the page (or gets its own `h2` heading row, which is the default on a service landing page: the row below, the Services grid's heading row with a different title, goes above the counters row) so the outline doesn't jump from the hero's `h1` to `h3`; change `headingLevel` if the page's outline needs another level
- [ ] every number in this section, on a real page, traces back to the client's brief — none invented
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): navy numbers on `#f1f5f9` 13.6:1, `#475569` titles on `#f1f5f9` 6.9:1
