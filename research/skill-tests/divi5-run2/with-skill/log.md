# Skill test log (t20 / skill2), Divi 5 brief 01

## Files of the skill read, in order
(All under /Volumes/Content/projects/TFM/Divi-genie/Skill/divi-page-builder/; brief: research/skill-tests/divi5-brief-01.md)
1. SKILL.md
2. (brief) research/skill-tests/divi5-brief-01.md
3. recipes/divi5/README.md
4. recipes/divi5/pages/service-landing.md (top part; worked example line truncated on purpose)
5. reference/divi5/page-format.md
6. recipes/divi5/sections/hero-centered.md
7. recipes/divi5/sections/services-grid.md
8. recipes/divi5/sections/stats-counters.md
9. recipes/divi5/sections/faq.md
10. recipes/divi5/sections/cta-band.md
11. reference/divi5/value-formats.md (grep of headings / icon parts only, not read in full)
12. reference/divi5/modules/blurb.md
13. reference/divi5/modules/number-counter.md
14. reference/icons.md (head + grep for faucet/shower/water/tint/camera)
15. recipes/divi5/sample-tokens.json (via python: keys, site, module_styles contexts, typography)
16. scripts/divi5_blocks.py (head + new_block/wrap_placeholder/set_attr), scripts/preview.py --help (tail)
Not read: reference/divi5/structure.md, design-families.md, design-tokens.md, preview.md, modules/README.md, module pages for heading/text/button/cta/accordion/code/section/row/column (I copied attribute shapes from the recipes' worked examples).

## Plan (pre-approved)
Hero centered (h1, brief intro verbatim, phone button) / Services (h2 + 5 blurb h3, rows 1_3x3 + 1_2x2) / Stats (h2 + 3 counters h3) / FAQ (h2 + accordion h3 + FAQPage JSON-LD) / CTA band (h4, phone button). Skipped trust bar, testimonials, alternating features (no content in brief).

## Commands
1. `python3 build.py` (my script in the scratchpad folder, imports scripts/divi5_blocks.py; writes page.html) -> ok
2. `python3 scripts/validate.py .../skill2/page.html --tokens recipes/divi5/sample-tokens.json`
   -> `Summary: 0 error(s), 0 warning(s), 0 pre-existing`   (the only validate run; passed first time)
3. `SSL_CERT_FILE=/etc/ssl/cert.pem python3 scripts/preview.py render .../page.html --tokens recipes/divi5/sample-tokens.json --out .../preview.html`
   -> rendered on Divi 5.13.1 (cached) in Playground, 1379.8 KB, 1.6 s
4. Checked preview.html headings with a regex: one h1, h2/h3/h4 outline as planned, one ld+json script.
5. `git status --short` in the repo: clean (no files changed under the repo).

## Content decisions
- No eyebrow (brief has none). H2 titles "Our Drain Cleaning Services", "Drain Cleaning by the Numbers", "Drain Cleaning FAQ" and CTA title/text "Need a Drain Cleared Today?" / "Call now for same-day service and a written price before we start." are my wording (structural headings); all facts come from the brief.
- Stats: "25+" / "60" / "4.9" with titles "Years in business", "Minute response", "★ from 1,200 reviews" (per number-counter gotchas). `enablePercentSign` off on all three.
- Icons: faucet (kitchen), shower (bathroom), water (sewer), tint (hydro jetting), camera (inspection), all fa/900.
- Blurbs have no body and no link (brief gave none, no service URLs); no invented copy.
- Hero H1 written as `&amp;` (heading title is raw HTML per page-format.md).
- Phone: tel:+13055550100 (from the recipes' example; brief only gives (305) 555-0100).

## Unsure / stuck / docs unclear
- recipes/divi5/README.md: hero-centered field mapping row for the button says take bundle `module_styles["divi/button"][column_type=4_4]` incl. preset `11111111-...` (css null, "look unknown"). I followed it; unclear whether keeping an unknown-look preset is wise, but the doc is explicit.
- service-landing.md says the stats counters "add no section heading" and h3 counter titles sit under the Services h2; with no trust bar, my stats section would have put its h3s as siblings of the service h3s, so I added an h2 to the stats section. Docs (stats-counters checklist) allow "its own h2 heading row" but the row layout for that is not shown; I mirrored the services-grid heading row. No validator complaint.
- services-grid.md: worked example has three blurbs, "Not three services?" paragraph covers five (1_3x3 then 1_2,1_2) and says to set a title size; I set 20px. The heading color/size for the h2 came from the recipe text, not read from tokens.json (I did not query module_styles for the Why Choose Us bundle by script; used the recipe's stated values).
- stats-counters.md: layout is "1_4 x4" pattern; I used "1_3,1_3,1_3" for 3 counters, not stated in docs (only in reasoning that fractions must sum to one, from services-grid). Fine with validator.
- Shell noise: every bash call prints a zoxide warning (environment, not the skill).
- Tool output for long recipe files got truncated by the harness; worked examples are single very long lines. Not a skill bug.
- SKILL.md step 7 says serve/render with `page.txt`; for Divi 5 the recipes use `page.html` (task also says page.html). Minor inconsistency: SKILL.md workflow uses page.txt everywhere.
- The step "Show the user the outline and get a yes" was skipped per harness rules; preview approval step is where I stopped (no publish/draft/media).
