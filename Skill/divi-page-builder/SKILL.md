---
name: divi-page-builder
description: Use when creating a new Divi 4 page, landing page or section, editing an existing Divi page's copy, sections or styling, matching new content to a Divi site's existing design, or when Divi et_pb_ shortcode or post_content must be written, checked, previewed or pushed to WordPress.
---

# Divi Page Builder

Write Divi 4 pages as raw shortcode (the exact `post_content` Divi stores), styled with the target site's own design tokens, and validated before anything is pushed. There are no templates: every section is composed from documented fields.

**Not for:** Divi 5 sites (block format), Theme Builder templates, WooCommerce product layouts.

## Workflow
1. **Intake:** get the content brief, the site URL, and whether this is a new page or an edit. For an edit, fetch the current page (`reference/publishing.md` → "6. Edit an existing page") and save it as `original.txt`.
2. **Tokens:** reuse the site's `tokens.json` if you have one; otherwise run `python3 scripts/extract_tokens.py --site URL --user USER --page ID --out tokens.json` with the password in `WP_APP_PASSWORD`. See `reference/design-tokens.md`.
3. **Plan:** map the brief to recipes (`recipes/README.md`, `recipes/pages/`). Show the user the section outline and get a yes before writing.
4. **Compose:** for each section, follow its recipe. Look up every module in `reference/modules/<slug>.md`, and take every color, font, spacing and button style from `tokens.json`.
5. **Validate:** `python3 scripts/validate.py page.txt --tokens tokens.json` (add `--baseline original.txt` for edits). Repeat until there are 0 errors; read every warning, including the heading-outline ones. For a single section, add `--fragment`.
6. **Preview:** `python3 scripts/preview.py render page.txt --tokens tokens.json --out preview.html` (or `serve` for live reload), then open it. If the coverage report lists unsupported modules, or something looks off, re-run with `--exact` (real Divi in Playground; needs Node 20+). See `reference/preview.md`. Client Customizer and preset styling looks generic in both.
7. **Publish:** `python3 scripts/publish.py draft page.txt --site URL --user USER --title "…"` uploads local images and saves a **draft** (it validates first). Share the printed `preview_url`; after the user approves, run `publish.py publish --page-id ID --yes` (`reference/publishing.md`). The WordPress draft is the authoritative visual check.

## Hard rules
- **Never invent attributes.** An attribute not on the module's page (or in its linked design families) does not exist; `validate.py` reports it as `E_UNKNOWN_ATTR`.
- **Styles:** use inline attributes, or `_module_preset` UUIDs listed in `tokens.json`. Never use preset UUIDs from anywhere else.
- **Escaping inside attribute values:** `"` → `%22`, `[` → `%91`, `]` → `%93` (`reference/page-format.md`).
- **Headings:** exactly one H1 per page, and no skipped heading levels. `validate.py` enforces this (`E_MULTIPLE_H1`, `W_NO_H1`, `W_HEADING_SKIP`).
- **Images:** upload to the site's Media Library and use that URL. Never hotlink. Always write `alt`.
- **Edits:** use `scripts/page_edit.py`. Everything you weren't asked to change stays byte-identical.
- **Testimonials, reviews, prices and stats:** only as provided in the brief. Never invent them.
- **Always push as a draft first.**
- **Never print or write credentials.** Commands read `WP_APP_PASSWORD` / `ET_USERNAME` / `ET_API_KEY` from the environment only.

## Scripts
| script | purpose |
|---|---|
| `scripts/validate.py` | structure, heading outline, attributes, value formats, tokens; `--baseline` for edits; `--fragment`; `--json` |
| `scripts/extract_tokens.py` | site design tokens via REST (Application Password) + public CSS |
| `scripts/page_edit.py` | outline / extract / replace / insert-after / insert-before / set-attr / delete, surgically |
| `scripts/preview.py` | default preview, Python only: `render`, `serve` (live reload), `doctor`, `fetch-divi`; `--exact` hands off to Playground |
| `scripts/preview/preview.mjs` | exact real-Divi preview in WordPress Playground (Node 20+), used by `--exact` |
| `scripts/publish.py` | `fetch` / `media` / `draft` / `publish` over REST with an Application Password |

## Reference index
| file | read it when |
|---|---|
| `reference/page-format.md` | writing any shortcode: grammar, escaping, what's stored where |
| `reference/structure.md` | choosing section, row and column layouts; parent/child modules |
| `reference/value-formats.md` | writing colors, fonts, spacing, icons, responsive/hover/sticky values |
| `reference/icons.md` | picking an icon: name → exact `font_icon`/`button_icon` value |
| `reference/design-families.md` | styling: background, font, border, shadow, spacing, animation… |
| `reference/modules/README.md` | finding a module; each `reference/modules/<slug>.md` lists all of its fields |
| `reference/design-tokens.md` | extracting and applying a site's styles |
| `reference/publishing.md` | uploading images, creating drafts, editing live pages |
| `reference/preview.md` | local preview setup and limits |
| `recipes/README.md` | how recipes map tokens to fields |
| `recipes/sections/alternating-features.md` | zigzagging photo/copy feature blocks below a hero |
| `recipes/sections/contact.md` | lead-capture form paired with an optional map |
| `recipes/sections/cta-band.md` | short high-contrast call-to-action band between sections |
| `recipes/sections/faq.md` | FAQ accordion plus `FAQPage` JSON-LD for a rich result |
| `recipes/sections/gallery.md` | grid of job photos with a lightbox |
| `recipes/sections/hero-background-image.md` | full-bleed photo hero using `background_image` |
| `recipes/sections/hero-centered.md` | simple centered hero with no supporting photo |
| `recipes/sections/hero-fullwidth-header.md` | copy-first hero from the Fullwidth Header module |
| `recipes/sections/hero-split.md` | primary above-the-fold hero: headline + CTA beside a photo |
| `recipes/sections/pricing.md` | side-by-side comparison of 2-4 service tiers |
| `recipes/sections/process-steps.md` | numbered "how it works" walkthrough |
| `recipes/sections/service-area-list.md` | multi-column list of cities/neighborhoods served |
| `recipes/sections/services-grid.md` | three/four-up services overview with icons |
| `recipes/sections/stats-counters.md` | "by the numbers" band of large counters |
| `recipes/sections/tabs.md` | grouping related content behind clickable tabs |
| `recipes/sections/team.md` | introducing the people behind the business |
| `recipes/sections/testimonials.md` | social-proof customer quotes, grid or slider |
| `recipes/sections/trust-bar.md` | strip of partner/certification logos |
| `recipes/sections/video.md` | embedded video behind a poster image |
| `recipes/pages/local-seo-location.md` | one page per city/neighborhood served |
| `recipes/pages/ppc-lead-gen.md` | single-form, no-navigation ad landing page |
| `recipes/pages/product-feature.md` | page selling one specific product or plan |
| `recipes/pages/service-landing.md` | primary money page for one service line |
| `recipes/edits/change-copy.md` | editing text only, no layout/design change |
| `recipes/edits/insert-section.md` | adding a new section without disturbing the rest |
| `recipes/edits/replace-section.md` | swapping out an entire section for a rebuilt one |
| `recipes/edits/restyle-to-tokens.md` | bringing off-brand values back in line with `tokens.json` |
