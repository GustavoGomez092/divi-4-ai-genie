# Skill test results: Divi 5, brief divi5-brief-01 (Drain Cleaning & Hydro Jetting in Miami)

Brief: [divi5-brief-01.md](divi5-brief-01.md). It's a service landing page for the sample brand in
`recipes/divi5/sample-tokens.json` (Miami Rapid Plumbing on Divi 5.13.1): an H1, an intro, five services, three
stats (`25+ years`, `60-minute response`, `4.9★ from 1,200 reviews`), two FAQs and a phone CTA. Both agents were
fresh sonnet contexts started by the controller. Their pages and logs are in [divi5-run1/](divi5-run1/).

Validator command for every run:
`python3 Skill/divi-page-builder/scripts/validate.py page.html --tokens Skill/divi-page-builder/recipes/divi5/sample-tokens.json --json`

## Baseline (no skill; the brief and sample-tokens.json only)

| metric | result |
|---|---|
| validator | **13 errors, 45 warnings** |
| errors by code | `E5_BAD_VALUE` ×5: blurb `title.innerContent` written as a string, where Divi 5 expects `{"text": …}`. `E5_UNKNOWN_ATTR` ×4: button `background` → `{"desktop":{"value":…},"hover":…}`, with the state beside the breakpoint. `E5_NONCANONICAL` ×3: a raw `--` in `var(--gcid-…)` inline CSS. `E5_COLUMNS` ×1: a `1_3,1_3` row |
| warnings by code | `W5_BUILDER_VERSION` ×43 (no `builderVersion` on any block), `W5_NO_PLACEHOLDER` ×1, `W_HEADING_SKIP` ×1 (accordion titles left at the default `h5`) |
| exactly one H1 | yes |
| heading outline (rendered) | H1, H2, H2, **H5, H5**, H2. The five blurb `h3`s never render (see below) |
| brand fonts / colors | Montserrat ×9 and Lato ×5 in the attributes. Colors are `$variable` refs (navy ×9, orange ×7) plus literals that are all in the tokens palette. The tokens handed it the brand, unlike the Divi 4 baseline |
| variables / presets | `gvid-r6secpad01` ×2; `modulePreset` `r6btnpreset1` ×2 (a real id) |
| stats | not counters. Three `divi/text` blocks with inline-styled numbers, because the agent assumed Divi would drop the `+` and `★` |
| preview | renders (Playground accepts it: 1.5 s, 365 KB) |

Rendered (Playground, 1440 and 390): the navy hero and CTA band and the Montserrat headings are right. But **the
Services section is empty.** All five blurbs render as zero-height `<div class="et_pb_blurb_container"></div>`,
because Divi drops a string title. The "stats" are big text ("60-minute" wraps the row). The buttons and both FAQ
titles are in Open Sans (h5, 16px). There's no horizontal overflow at 390.

## With skill, run 1 (fresh sonnet; SKILL.md + file access, stopped before publishing per the harness)

| metric | result |
|---|---|
| validator | **0 errors, 0 warnings** (re-run independently). The agent's first run had 4 `E5_UNKNOWN_ATTR` (the same hover nesting error as the baseline). It fixed them by copying the worked example |
| exactly one H1 | yes (`divi/heading` `h1`) |
| heading outline (rendered, live) | H1 · H2 · H3×5 (blurbs) · H3×3 (counter titles) · H2 · H3×2 (FAQ) · H4 (CTA): no skips |
| fonts | Montserrat ×15, Lato ×13; buttons Lato, FAQ titles Montserrat: nothing falls back to Open Sans |
| colors | `$variable` refs: navy ×18, orange ×8, `gcid-r6orangelt1` ×2 (button hover), `gcid-primary-color` ×1 (eyebrow). The literals `#ffffff`/`#f1f5f9`/`#475569` are all in the palette |
| variables / presets | `gvid-r6secpad01` ×2, `gvid-r6radius01` ×8; `modulePreset` `11111111-…` ×1 (the hero-centered CTA bundle, as its recipe says) |
| structure | placeholder → 5 sections: hero-centered, services-grid (3 + 2 blurbs with fa icons), stats-counters (3), faq (accordion + `FAQPage` JSON-LD with 2 questions), cta-band (`divi/cta`); `tel:+13055550100` on both CTAs |
| preview | `preview.py render --tokens`: Divi 5.13.1 in Playground, 1.4 s, 1380 KB |
| draft | `publish.py draft` → page 865, status `draft`, stored `post_content` byte-identical to page.html; then deleted |

Workflow followed (from its log): SKILL.md → recipes/divi5/README.md → pages/service-landing.md → five section
recipes → `divi5_blocks` helpers → sample tokens copied as tokens.json → number-counter module page +
value-formats (icons) + icons.md → hero-centered.md → wrote build.py (`new_block`/`wrap_placeholder`/`serialize`)
→ validate (4 errors, fixed) → validate 0/0 → preview. It dropped the trust bar, testimonials and alternating
features because the brief gave no content for them, and it used hero-centered because there was no photo.

Copy it wrote beyond the brief: the eyebrow, the two H2s, five one-line blurb bodies, the CTA title and text. None
of it adds a claim the brief doesn't make.

### Stumbles (agent log) and what was done

| # | stumble | verdict | fix |
|---|---|---|---|
| 1 | Counter numbers `"25+"`, `"4.9★"`: nothing says what the count-up does with a suffix; the Divi 5 example writes `"15"` while the shared recipe's prose said `15+` | **doc gap**, now measured (below) | new `notes/number-counter.md` → generated Gotchas in `reference/divi5/modules/number-counter.md`; rule + link in `recipes/divi5/sections/stats-counters.md`; shared recipe's placeholder list now matches its example |
| 2 | Button hover nesting: the README mapping table said `.background → color (+ hover state)` with no shape; first validate failed | **doc gap** (the baseline made the same mistake) | README §1: one-line example of a state beside `value`, and the wrong form named with its error code |
| 3 | hero-split checklist says variables in padding/radius "show only on the draft", but README §7 says render seeds them | **stale doc**: preview and live both give the hero 96px (1440) / 48px (390) from the `clamp()` variable | removed the stale clause |
| 4 | No guidance for a hero without an image; found hero-centered only by browsing the index | **doc gap** | service-landing (Divi 5): "Fit the list to the brief" (no photo → hero-centered; skip sections without content; outline still holds) |
| 5 | Rating as a counter is a poor fit | covered by #1 | `"4.9"` + star in the title |
| 6 | `&` in the H1 | no gap: `divi5_blocks.serialize` escapes it and page-format.md documents the escape. The live H1 reads "Drain Cleaning & Hydro Jetting in Miami" | none |
| 7 | CTA `h4` after FAQ `h3` | held; no warning | none |

Found in the visual check, not in the log:

| # | finding | fix |
|---|---|---|
| 8 | Five services became rows `1_3,1_3,1_3` + `1_2,1_2`. The second row's blurb titles render at 22px against 20px above: Divi's CSS gives an unsized `h3` 20px in `1_3`/`1_4` columns (`.et_pb_column_1_3 h3{font-size:20px}`) and 22px elsewhere. The recipe covered only three services | services-grid (Divi 5): "Not three services?" (row layouts for 4/5+, `E5_COLUMNS`, set a blurb title `size`) |
| 9 | The shared stats recipe said a counter title "is plain text, not a heading element". It renders as `h3` on both Divi 4 (`title_level` default `h3`) and Divi 5, and the same file's "Optional" paragraph already said so | corrected the SEO note |

## Visual check

Playground preview (`preview.py render --tokens`, then headless Chrome through `research/python-renderer-spike/shoot.mjs`,
scrolled so that the counters and animations run):

- **1440:** navy hero with an orange uppercase eyebrow and a centered Montserrat H1 on two lines, the verbatim
  intro and an orange pill button (Lato, navy label, 12px radius). The white Services section has a navy H2 and
  five orange fa icons (faucet, bath, toilet, water, video) over Montserrat titles. The second row spreads two
  wider cards (finding 8). Light-grey stats band: `25+`, `60`, `4.9★` in navy Montserrat 56px over Lato titles.
  The FAQ has the first item open, bold Montserrat questions and an orange toggle icon. The navy CTA band has a
  centered title, text and an orange button.
- **390:** everything stacks to one column, H1 34px, no horizontal overflow, the stats one per line, and the CTA
  title on two lines.

Live (divi-5-test.local, Divi 5.13.1). First the site's design system was seeded with
`research/tools/divi5/r6_setup.php` (the sample tokens' ids and values; its Customizer primary was set to the
sample's `#F97316` for this run). Then a throwaway Application Password was used for `publish.py draft`, deleted
right after. The page was published temporarily with `wp post update --post_status=publish` and screenshotted at
1440/390. The result: **the same layout as the preview.** The builder area is the same height
(2446.5px at 1440, 3118.6px at 390), with the same computed fonts, sizes, button colors and hero padding. Every
test page was then deleted, and `r6_restore.php` put back the options (verified: no global colors, variables,
presets, `D5TEST`/`R6` pages or application passwords left).

Contrast: navy label on the orange button is 5.3:1 (white on that orange would be 2.8:1, which is why the bundle uses navy).

### Counters on the live site

Divi 5's `module-library-script-number-counter.js` parses `number.innerContent` with `parseFloat` after removing
commas, animates for 1.8 s, and at the end writes the original text back. The `.percent-value` text was sampled
every 80 ms after scrolling the counters into view:

| `number.innerContent` | during the count | final |
|---|---|---|
| `25+` (agent) | 0, 1, … 24, 25 | `25+` |
| `60` (agent) | 0 … 59, 60 | `60` |
| `4.9★` (agent) | 0.00, 0.02, … 4.85, 4.89 (the `★` counts as a second decimal) | `4.9★` |
| `1,200+` (probe) | 0, 5, … 1,038, 1,198 (separator kept) | `1,200+` |
| `5,000` (probe) | 0, 20, … 4,992 | `5,000` |
| `98%` (probe, `enablePercentSign` off) | 0 … 98 | `98%` |
| `24/7` (probe) | 0 … 24 | `24/7` |
| `$49` (probe) | `NaN` the whole time | `$49` |
| `4.9` (probe) | 0.0 … 4.9 | `4.9` |

So the agent's page is correct: `+` and `★` survive, and `enablePercentSign` `"off"` keeps the `%` span empty.
Only `4.9★` counts with one extra decimal before it snaps. The probe values ran on a throwaway `D5TEST` page,
deleted afterwards.

## Doc fixes (this commit)

1. `research/tools/divi5/notes/number-counter.md` (new) → regenerated `reference/divi5/modules/number-counter.md` Gotchas: suffix, prefix, decimals, text-like values, percent sign.
2. `recipes/divi5/sections/stats-counters.md`: the value rules under the field mapping, linked to those Gotchas.
3. `recipes/sections/stats-counters.md`: the counter title is an `h3` heading, and the placeholder list matches the example (`15`, `5000`, `24`, `100`).
4. `recipes/divi5/README.md` §1: where a `hover` state sits, with an example.
5. `recipes/divi5/sections/hero-split.md`: dropped the stale "variables show only on the draft".
6. `recipes/divi5/pages/service-landing.md`: "Fit the list to the brief".
7. `recipes/divi5/sections/services-grid.md`: "Not three services?".

SKILL.md unchanged (1186 words). Full suite: 894 tests OK (34 skipped). `check_doc_examples`: 105 Divi 4 + 122 Divi 5
examples, 0 failing.

## Verdict

Baseline → skill: 13 errors / 45 warnings → **0 / 0**. The baseline had the tokens, so its palette and fonts were
right, but it loses all five services on the rendered page, fakes the stats and skips to `h5`. The with-skill page
has one H1, no skips, brand fonts everywhere including buttons and toggles, and the same look in the preview and
on the live Divi 5 site. It meets the success criteria, apart from the two cosmetic items that the fixes above
address (the `4.9★` count-up digit and the mixed blurb title sizes).

A second with-skill run is warranted to confirm that the new guidance changes behaviour. The agent should write
`"4.9"` (star in the title) or knowingly keep `"4.9★"`, give every blurb title a `size`, and get the hover
nesting right the first time. The page should still validate to 0/0.

## With skill, run 2 (fresh sonnet; same brief; after the run-1 doc fixes)

Files: [divi5-run2/with-skill/](divi5-run2/with-skill/) (page.html, log.md, build.py; the preview is not kept because it contains Divi CSS).

| metric | result |
|---|---|
| validator | **0 errors, 0 warnings** (re-run independently). It was clean on the first and only validate; run 1 needed a fix round (4 `E5_UNKNOWN_ATTR`) |
| counters | `"25+"`, `"60"`, `"4.9"` with the star in the title (`"★ from 1,200 reviews"`), `enablePercentSign` off: the run-1 fix worked |
| blurb titles | every one has a font size (20px), so the 3 + 2 rows match |
| outline | one `h1`, no skipped level; it added its own `h2` above the counters. `FAQPage` JSON-LD once |
| preview | Divi 5.13.1 in Playground, 1.6 s. It stopped before publishing |

What changed vs run 1: the hover nesting, the counter values, the blurb sizing and the no-photo hero (hero-centered) were all right without a retry.

Remaining stumbles from its log, and what was done:

| # | stumble | fix |
|---|---|---|
| 1 | SKILL.md steps name `page.txt` while Divi 5 recipes use `page.html` | step 6 says `page.txt` is Divi 4, `page.html` Divi 5 (SKILL.md 1193 words) |
| 2 | Stats band with no heading above it: the page recipe said counters add no section heading, so the `h3`s would sit beside the blurb `h3`s | service-landing: the stats band gets its own `h2` ("By the Numbers"); stats-counters checklist points to it as the default |
| 3 | The button recipe keeps a preset whose look is unknown (`11111111-…`, `css: null`) | README Presets: keep such a preset only when its bundle's attrs set every visible property; otherwise write the button inline with no `modulePreset` |
| 4 | Heading-row layout and `1_3` x3 counters row not shown | not changed (validator accepts it; mirrors services-grid) |

Verdict: the fixes change behaviour as intended; run 2 met every success criterion with no validator round-trip.
