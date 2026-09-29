# PPC lead gen (Divi 5)

Purpose, SEO notes and internal links: [the shared page recipe](../../pages/ppc-lead-gen.md). This page is the
Divi 5 assembly: which Divi 5 section recipes, in what order, the one adapted section, and the heading outline;
the [service landing](service-landing.md) page shows a whole Divi 5 page put together the same way.

## Sections
| # | Section | Divi 5 recipe | Tone | Headings it adds |
|---|---|---|---|---|
| 1 | Hero + form | [Hero split](../sections/hero-split.md), adapted (below) | navy | `h1` + `h2` (the form title) |
| 2 | Trust bar | [Trust bar](../sections/trust-bar.md) | light grey | none |
| 3 | How it works | [Process steps](../sections/process-steps.md) | white | `h2` + `h3` (step titles) |
| 4 | Testimonials | [Testimonials](../sections/testimonials.md) | white | `h2` |
| 5 | CTA band | [CTA band](../sections/cta-band.md) | navy | `h3` |

### Adapting Hero split for a form instead of a photo

Keep the left column of [Hero split](../sections/hero-split.md) (eyebrow, `h1`, body text) and **drop its
button**: the form is the page's one call to action. In the right column, replace the image with the
[Contact](../sections/contact.md) recipe's `divi/contact-form` and its fields, unchanged except:

- the form's `title.innerContent` fits the placement ("Get Your Free Quote") and its `headingLevel` is `"h2"`:
  there is no section `h2` above it here;
- the right column becomes a white card, since the form is styled for a light background:
  `module.decoration.background` → `{"color": "#ffffff"}`, `module.decoration.spacing` → `padding` 32px on all four
  sides, `module.decoration.border` → `radius` `gvid-r6radius01` on all four corners (the column keeps its layout
  form and `type` `"1_2"`). No bundle covers a form in a dark hero; this is a design choice, stated here.

Checked on Divi 5.13.1: the card, the navy-on-white title, the fields and the orange button render inside the navy
hero, and stack under the copy on a phone.

## Rhythm

Navy → grey → white → white → navy: the same bookends as the other pages, shorter. Nothing on the page invites
the visitor elsewhere (no services grid, service-area links or tabs).

## Headings

- **One `h1`:** the hero headline, matching the ad's promise.
- **`h2`:** the hero form's title, How it works, Testimonials.
- **`h3`:** the four step titles, and the CTA band, one below the Testimonials `h2` just before it (set the CTA
  recipe's `h4` to `"h3"` here: `h4` would skip a level).

## Assembling on Divi 5

- Build the sections from their recipes (with the hero adapted), wrap them in one `divi/placeholder`
  (`divi5_blocks.wrap_placeholder`), and validate the whole page ([service landing](service-landing.md#assembling-on-divi-5)).
- The form's recipient `email` and success message come from the brief; the CTA band's button is a `tel:` link.
- If the ad platform needs the page `noindex`, set it on the page (an SEO plugin field), not in the layout.

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors and no heading warnings, as a whole page (no `--fragment`); no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET` (`tokens.json` is the target site's own)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] exactly one `h1`; no skipped heading level; the hero has one call to action (the form), no button
- [ ] the form submits on the draft (empty, wrong captcha, right captcha); testimonials come from the brief, none invented
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): the form keeps the Contact recipe's colors on its white card (navy title 14.9:1, `#475569` placeholders on `#f1f5f9` 6.9:1, navy button label on orange 5.3:1); the other sections keep their own recipe's pairs
