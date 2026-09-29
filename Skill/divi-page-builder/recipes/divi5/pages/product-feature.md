# Product feature (Divi 5)

Purpose, SEO notes and internal links: [the shared page recipe](../../pages/product-feature.md). This page is the
Divi 5 assembly: which Divi 5 section recipes, in what order, the one adapted section, and the heading outline;
the [service landing](service-landing.md) page shows a whole Divi 5 page put together the same way.

## Sections
| # | Section | Divi 5 recipe | Tone | Headings it adds |
|---|---|---|---|---|
| 1 | Hero | [Hero background image](../sections/hero-background-image.md) | photo + navy gradient | `h1` |
| 2 | Features | [Alternating features](../sections/alternating-features.md), with a heading row (below) | white | `h2` (added) + `h3` (feature titles) |
| 3 | Options | [Tabs](../sections/tabs.md) | white | `h2` |
| 4 | Pricing | [Pricing](../sections/pricing.md) | white | `h2` + `h3` (plan titles) |
| 5 | FAQ | [FAQ](../sections/faq.md) | white | `h2` + `h3` (questions) |
| 6 | CTA band | [CTA band](../sections/cta-band.md) | navy | `h4` |

### Adapting Alternating features with its own heading

[Alternating features](../sections/alternating-features.md) has no section heading: on the service landing page it
follows the Services `h2`. Here it comes straight after the hero, and `h1` → `h3` skips a level. Add a first row to
the section, before the feature rows: `columnStructure` `"4_4"` with one `4_4` column holding a `divi/heading`
styled exactly like the other section headings (`module_styles["divi/heading"][section_label=Why Choose Us,
column_type=4_4]`: `h2`, Montserrat 700, the navy global, 40/32/28px). Nothing else in the section changes.

## Rhythm

Photo hero → four white sections → navy. The four white sections in a row read as one long page: give Tabs or
Pricing the light grey (`#f1f5f9`) to split the run, and keep each section's own padding.

## Headings

- **One `h1`:** the hero headline.
- **`h2`:** the added Features heading, Tabs, Pricing, FAQ.
- **`h3`:** the feature titles, the plan titles and the FAQ questions. Tab labels are not headings.
- **`h4`:** the CTA band, one below the FAQ questions just before it.

## Assembling on Divi 5

- Build the sections from their recipes (Features with its heading row), wrap them in one `divi/placeholder`
  (`divi5_blocks.wrap_placeholder`), and validate the whole page ([service landing](service-landing.md#assembling-on-divi-5)).
- The pricing tables' and CTA's buttons are the only links off the page.
- Prices, plan features and FAQ answers come from the client's price sheet and brief.

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors and no heading warnings, as a whole page (no `--fragment`); no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET` (`tokens.json` is the target site's own)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one `h1`; no skipped heading level (the Features `h2` row is present)
- [ ] every price and FAQ answer traces back to the client — none invented; the FAQ JSON-LD matches its accordion
- [ ] every image has alt text and a Media Library URL
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): each section recipe's contrast line holds here, the hero's copy on its navy-tinted photo included; a section moved to `#f1f5f9` keeps `#475569` text (6.9:1) and navy headings (13.6:1)
