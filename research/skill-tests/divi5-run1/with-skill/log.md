# Build log (skill1) - Drain Cleaning & Hydro Jetting in Miami

## Files of the skill read (in order)
1. Skill/divi-page-builder/SKILL.md
2. research/skill-tests/divi5-brief-01.md (the brief, not part of the skill)
3. recipes/divi5/README.md (via cat, whole file)
4. recipes/divi5/pages/service-landing.md (whole, including the worked example)
5. recipes/divi5/sections/{hero-split, services-grid, stats-counters, faq, cta-band}.md (with the divi5 example blocks stripped by sed)
6. scripts/divi5_blocks.py (only grep of the def names, to learn new_block / wrap_placeholder / serialize)
7. recipes/divi5/sample-tokens.json (top-level keys and `site` only; copied as tokens.json)
8. reference/divi5/modules/number-counter.md (head + tables); reference/divi5/value-formats.md (grep "icon" only); reference/icons.md (head + grep for water/bath/etc.)
9. recipes/sections/stats-counters.md (Divi 4 shared recipe, a few lines/grep)
10. recipes/divi5/sections/hero-centered.md (structure, mapping, worked example)
Not read (relied on the recipes' worked examples instead): reference/divi5/page-format.md, structure.md, design-families.md, design-tokens.md, preview.md, modules/blurb.md, accordion.md, cta.md, button.md.

## Commands
- cat recipes/divi5/README.md + ls: ok.
- Read service-landing.md: ok.
- Section recipes / grep for functions / sample-tokens keys: ok. site.divi_version = 5.13.1.
- python3 build.py page.html (my script, in this folder, uses divi5_blocks.new_block/wrap_placeholder/serialize): wrote page.html (23.7 KB).
- validate.py page.html --tokens tokens.json (first run): 4 errors E5_UNKNOWN_ATTR - I had nested the button background hover wrongly ("background":{"desktop":{"value":..},"hover":..} instead of hover INSIDE "desktop"). Fixed.
  - My first sed fix failed (path contains "/" used as sed delimiter); redid with python. Final validate: "Summary: 0 error(s), 0 warning(s), 0 pre-existing".
- preview.py render page.html --tokens tokens.json --out preview.html: ok, Divi 5.13.1 in Playground, 1.5s, 1379 KB. (Ran once with the erroneous page too; harmless.)

## Choices
- Sections: Hero centered (no hero image in the brief, so not the split hero) -> Services grid (5 blurbs: 3+2 rows) -> Stats counters (3) -> FAQ (2 items + FAQPage JSON-LD) -> CTA band with the phone CTA. No trust bar / testimonials / alternating features / pricing: nothing in the brief to fill them (no invented content).
- Tokens: sample-tokens.json copied as tokens.json, as the brief says. Colors/radius/padding use its gcid/gvid ids; hero button uses the CTA-bundle preset 11111111-... as in the hero-centered example.
- Copy that I wrote beyond the brief (not verbatim): eyebrow "Same-day drain service", H2 "Our Drain Cleaning Services", blurb one-liners, H2 "Frequently Asked Questions", CTA title/text. Kept claims to what the brief already says.
- Icons: fa solid glyphs picked from icons.md (faucet, bath, toilet, water, video).

## Unsure / stuck / docs unclear
- Stats "25+", "4.9★": stats-counters recipes never say how to show a "+" or a symbol. enablePercentSign only controls "%"; the Divi 5 example uses "15" plain and the Divi 4 recipe says "15+" in prose. I put "25+", "60", "4.9★" straight into number.innerContent and titles "years in business" / "minute response" / "from 1,200 reviews". The validator accepts it, but I could not verify how Divi's count-up JS treats "25+" or "4.9★" (the static preview HTML has empty percent-value spans, filled by JS); the "+"/"★" may be dropped or the count-up may misbehave. Docs (number-counter.md) list no value format for number.innerContent (type "text"). Also "1,200" in the title is fine, but there is no doc on thousands separators in the number.
- Number-counter as a stat for a rating ("4.9★ from 1,200 reviews") is a poor fit; a text/heading block might be safer.
- Hover nesting: the recipe README table says `.background -> color (+ hover state)`, but does not show the exact nesting; I only got it right after the validator error by copying the worked example. A one-line example in the README mapping table would help.
- service-landing.md heading table says CTA band title is h4 "one below the FAQ questions"; that held here (FAQ h3 -> CTA h4), no warning.
- The recipe says the preview's variable padding/radius "show only on the draft" (hero-split checklist) yet the README says render seeds the variables into options; not checked visually here (I did not open preview.html in a browser).
- The user's hero has no image; the recipes give no guidance on a hero with no image except hero-centered (I found it only by browsing the recipe index).
- Brief's H1 contains "&": stored as plain "&" in the heading text (JSON) - validator had no complaint; I did not verify how Divi escapes it.
- zoxide warning noise on every shell command (environment, not the skill).
