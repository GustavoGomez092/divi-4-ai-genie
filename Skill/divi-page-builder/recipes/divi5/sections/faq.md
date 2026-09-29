# FAQ (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/faq.md). This page is its Divi 5 structure,
field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

**Never invent FAQ content.** Questions and answers come from the client's brief, copied word for word into both
the accordion and the `FAQPage` JSON-LD. The example's three are the Divi 4 recipe's placeholders for the sample
brand.

## Structure
```text
section (adminLabel "FAQ")
└─ row columnStructure "4_4"
   └─ column 4_4: heading (h2) · accordion · code
      accordion
      ├─ accordion-item (Q1, open)
      ├─ accordion-item (Q2)
      └─ accordion-item (Q3)
      code: <script type="application/ld+json"> FAQPage with the same three questions
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color`, `module.decoration.spacing` → `padding` | `section_exemplars[adminLabel=Why Choose Us].attrs.module.decoration` (`#ffffff`; 90/60/45px) | a light `colors.palette` hex; `spacing.section_padding[2][0]` |
| heading `title.decoration.font.font` | `module_styles["divi/heading"][section_label=Why Choose Us, column_type=4_4]`: `h2`, Montserrat 700, navy, 40/32/28px | `typography.scale.h2` |
| accordion `title.decoration.font.font` → `headingLevel` | `"h3"`, one below the section's `h2` (the module's default is `h5`, which skips two levels); set on the accordion, it applies to every item | `"h3"` |
| accordion `title.decoration.font.font`, `closedToggle.decoration.font.font` | `typography.heading_font` + `"700"` + the navy global, 18px (the closed state needs its own copy) | same |
| accordion `openToggle.decoration.font.font` → `color` | the navy global: Divi 4 turned the open question orange, 2.8:1 on white | same |
| accordion `closedToggleIcon.decoration.icon` → `color` | the orange global `gcid-r6orange001` (a decorative marker: the question text is the control) | leave it out |
| accordion `content.decoration.bodyFont.body.font` | Lato 400 `#475569`, 16px / 1.7em | `typography.body_font` + the body color |
| item `module.advanced.open` | `"on"` on the first item only | same |
| item `title.innerContent`, `content.innerContent` | the client's brief, word for word | — |
| code `content.innerContent` | the `FAQPage` JSON-LD in a `<script type="application/ld+json">`, generated from the same question and answer strings as the items, never typed a second time | — |

**The JSON-LD survives Divi 5's escaping.** Build the code block with `divi5_blocks` like any other: in the stored
JSON its quotes and angle brackets are the escapes `\u0022` and `\u003c`/`\u003e`, and WordPress decodes them when
it parses the block. On the live check the page printed exactly one `<script type="application/ld+json">`, its text
parsed with `json.loads`, and its three `name`/`text` pairs equalled the rendered accordion titles and answers. No
Divi 4 `%22`/`%91` escaping applies here: that was for shortcode attributes. The Divi 4 recipe's `wptexturize()`
caveat still holds: keep `--`, `...` and straight quotes next to words out of the answers, or the on-page text and
the JSON-LD stop matching.

```python
import json
pairs = [("Do you provide free estimates?", "Yes. We give you an upfront, flat-rate price before any work begins.")]
ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
script = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + "</script>"
# script goes into the code block's content.innerContent; the same q/a strings into the accordion items
```

## Responsive rules

- The `h2` size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "32px"}`, `phone` `{"size": "28px"}`, from the heading bundle.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The accordion is one stacked list and the JSON-LD prints nothing visible: neither needs a responsive attribute.

## Worked example (sample-tokens.json)

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"FAQ"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#ffffff"}}},"spacing":{"desktop":{"value":{"padding":{"top":"90px","bottom":"90px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"60px","bottom":"60px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"45px","bottom":"45px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Frequently Asked Questions"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/accordion {"title":{"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"18px"}}}}}},"closedToggle":{"decoration":{"font":{"font":{"desktop":{"value":{"family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"18px"}}}}}},"openToggle":{"decoration":{"font":{"font":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}}}},"closedToggleIcon":{"decoration":{"icon":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"}}}}},"content":{"decoration":{"bodyFont":{"body":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"#475569","size":"16px","lineHeight":"1.7em"}}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":{"value":"Do you offer 24/7 emergency plumbing service?"}}},"module":{"advanced":{"open":{"desktop":{"value":"on"}}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eYes. We answer calls day and night, 365 days a year, with a licensed plumber typically on site within 60 minutes.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":{"value":"Do you provide free estimates?"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eYes. We give you an upfront, flat-rate price before any work begins, with no hidden fees.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/accordion-item {"title":{"innerContent":{"desktop":{"value":"Are your plumbers licensed and insured?"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003eYes. Every technician is a licensed, insured Florida plumber.\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/accordion --><!-- wp:divi/code {"content":{"innerContent":{"desktop":{"value":"\u003cscript type=\u0022application/ld+json\u0022\u003e{\u0022@context\u0022:\u0022https://schema.org\u0022,\u0022@type\u0022:\u0022FAQPage\u0022,\u0022mainEntity\u0022:[{\u0022@type\u0022:\u0022Question\u0022,\u0022name\u0022:\u0022Do you offer 24/7 emergency plumbing service?\u0022,\u0022acceptedAnswer\u0022:{\u0022@type\u0022:\u0022Answer\u0022,\u0022text\u0022:\u0022Yes. We answer calls day and night, 365 days a year, with a licensed plumber typically on site within 60 minutes.\u0022}},{\u0022@type\u0022:\u0022Question\u0022,\u0022name\u0022:\u0022Do you provide free estimates?\u0022,\u0022acceptedAnswer\u0022:{\u0022@type\u0022:\u0022Answer\u0022,\u0022text\u0022:\u0022Yes. We give you an upfront, flat-rate price before any work begins, with no hidden fees.\u0022}},{\u0022@type\u0022:\u0022Question\u0022,\u0022name\u0022:\u0022Are your plumbers licensed and insured?\u0022,\u0022acceptedAnswer\u0022:{\u0022@type\u0022:\u0022Answer\u0022,\u0022text\u0022:\u0022Yes. Every technician is a licensed, insured Florida plumber.\u0022}}]}\u003c/script\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] in the draft's page source there is one `<script type="application/ld+json">`; its text parses as JSON (`python3 -m json.tool`) and its questions and answers match the accordion word for word
- [ ] exactly one `h2` and no `h1` on this section; every question renders as `h3`; only the first item is open
- [ ] every question and answer traces back to the client's brief — none invented
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): navy questions on the open item's white 14.9:1 and the closed items' `#f4f4f4` 13.5:1; `#475569` answers on white 7.6:1; the orange toggle icon is decorative next to its question
