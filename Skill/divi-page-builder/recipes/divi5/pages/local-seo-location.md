# Local SEO location (Divi 5)

Purpose, SEO notes and internal links: [the shared page recipe](../../pages/local-seo-location.md). This page is
the Divi 5 assembly: which Divi 5 section recipes, in what order, and the heading outline they produce; the
[service landing](service-landing.md) page shows a whole Divi 5 page put together the same way.

## Sections
| # | Section | Divi 5 recipe | Tone | Headings it adds |
|---|---|---|---|---|
| 1 | Hero | [Hero centered](../sections/hero-centered.md) | navy | `h1`, with the city in it ("Miami's Fastest Emergency Plumbers") |
| 2 | Services | [Services grid](../sections/services-grid.md) | white | `h2` + `h3` (blurbs) |
| 3 | Service areas | [Service area list](../sections/service-area-list.md) | white | `h2` |
| 4 | Testimonials (local customers) | [Testimonials](../sections/testimonials.md) | white | `h2` |
| 5 | FAQ (local questions + JSON-LD) | [FAQ](../sections/faq.md) | white | `h2` + `h3` (questions) |
| 6 | Contact with map | [Contact](../sections/contact.md) | white | `h2` + `h3` (the form title) |
| 7 | CTA band | [CTA band](../sections/cta-band.md) | navy | `h4` |

## Rhythm

Navy → five white sections → navy. Five white sections in a row read as one long page: give the Service areas or
the Testimonials section the light grey (`#f1f5f9`, the By The Numbers exemplar's color) to split the run, and
keep each section's own padding. No hero photo: the centered hero puts the city name first.

## Headings

- **One `h1`:** the hero headline, naming the city.
- **`h2`:** Services, Service areas, Testimonials, FAQ, Contact.
- **`h3`:** the blurb titles, the FAQ questions, the contact form's title and the map pin's title (Divi prints it
  as an `h3`). On Divi 5 the Contact recipe sets the
  form title to `h3` under its section `h2` (the Divi 4 page used two `h2`s); the form module's own default is
  `h1`, which would make a second `h1`.
- **`h4`:** the CTA band, one below the form title just before it.

## Assembling on Divi 5

- Build the sections from their recipes, then wrap them in one `divi/placeholder`
  (`divi5_blocks.wrap_placeholder`), and validate the whole page ([service landing](service-landing.md#assembling-on-divi-5)).
- The FAQ questions are local ones from the brief, and its `FAQPage` JSON-LD is generated from the same strings.
- The service-area links point only at location pages that exist; the blurbs link to the shared service pages.
- The map needs the site's Google Maps API key before this page goes live.

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors and no heading warnings, as a whole page (no `--fragment`); no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET` (`tokens.json` is the target site's own)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one `h1`, naming the city; no skipped heading level
- [ ] the FAQ's on-page questions and its JSON-LD match word for word; testimonials and answers come from the brief, none invented
- [ ] the contact form submits on the draft (empty, wrong captcha, right captcha), and the map loads with the site's API key
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): each section recipe's contrast line holds here; a section moved to `#f1f5f9` keeps `#475569` text (6.9:1) and navy headings (13.6:1)
