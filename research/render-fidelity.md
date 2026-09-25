# Render fidelity: the Python renderer against real Divi

The Python renderer (`Skill/divi-page-builder/scripts/divi_render/`) is the default portable
preview. `tests/test_render_fidelity.py` compares it with real Divi, rendered through Playground by
`research/tools/ground_truth.py` (Divi 4.27.9, cached outside the repo), for every fixture in
`tests/fixtures/render/manifest.json`. `research/tools/fidelity.py` measures two things:

- **Markup ratio:** the difflib ratio over the `(tag, class list)` sequence of the `.et-l` block.
  1.0 means the sequence is identical.
- **CSS ratio:** the Jaccard similarity of the builder CSS as `(media, selector, declaration)`
  triples. 1.0 means no missing or extra declarations.

Recording is opt-in: run
`RENDER_FIDELITY_RECORD=1 RENDER_FIDELITY_STAGE='T26 held-out pre-fix' python3 -m unittest discover -s tests -p 'test_render_fidelity.py'`
to upsert the held-out rows below. The stage label is required (the test fails without it). Rows
are keyed by fixture and stage: a new stage always adds a row, so no task overwrites another's
history, while recording the same stage again updates its row. Without `RENDER_FIDELITY_RECORD`
the test only checks and never writes this file.

Tuned fixtures (`tuned: true`) must match exactly: the sequences are equal and 0 declarations are
missing or extra. With recording on, the test upserts a row below for each held-out fixture
(`tuned: false`) under the given stage. Following the procedure for Tasks 25–27, a held-out page is
measured **before** any fix. That pre-fix row is the honest number for how well the renderer
generalizes. After the fixes, the page becomes tuned and gets a post-fix row.

## Notes

- Task 24 (port into the skill) came first. The package reproduces the spike's output byte for
  byte on all 11 fixture pages, covering markup, builder CSS and the coverage report, whether it
  reads the raw research dump or the compact schema.
- The spike's own held-out numbers (`research/python-renderer-spike.md` §2) were measured against
  LocalWP with a different CSS count. The rows below use Playground truth and `fidelity.py`.
- `heldout2-inscope.txt` was never tuned in the spike. Its first two rows are the spike renderer
  before any fix (pre-fix) and the Task 24 package after the fixes (post-fix). The fixes were:
  - the section's `et_pb_inner_shadow` class;
  - the image's `et_pb_image_sticky` classes, and its `width:auto` rule following Image.php;
  - the hidden divider dropping its `et_pb_divider` and position classes;
  - `background__hover_enabled` driving background-colour hover, the
    `et_pb_section_video_on_hover` class and its transition;
  - the per-module hover transition maps (`get_transition_fields_css_props`);
  - the row's desktop padding copy;
  - Divi's icon `content` quirk: a backslash followed by digits is swallowed, so `&#x50;` prints
    `content:""`. This was verified against Playground renders of six icons.
- `heldout-outofscope.txt` uses modules that are not supported until Tasks 25–27. They render as
  placeholders and are listed in the coverage report, so a ratio of 0.9 cannot be reached yet.
  Until they are supported, the test checks that every one of them appears in the coverage report
  instead of checking the ratio.
- Task 25 (content modules: icon, code, fullwidth code, fullwidth image, video, audio, gallery,
  testimonial, team member, social media follow + network) added one tuned fixture per module
  (`content-tuned-*.txt`) and the held-out page `content-heldout.txt`. The held-out page's first
  row was measured before any fix: the markup matched exactly and 4 of 110 CSS declarations were
  missing, 1 extra. All five came from one engine gap: an inset box shadow on an option whose
  `overlay` is `inset` goes on `X>.box-shadow-overlay, X.et-box-shadow-no-overlay`
  (`BoxShadow::get_overlay_selector()`), and the box-shadow hover transition lists those
  selectors too. After that fix the page became tuned (second row).
- Engine fixes found while tuning the Task 25 fixtures (each checked against the existing
  fixtures, which still match exactly): background hover goes on `css.hover` or
  `add_hover_to_selectors(main)` (Background.php), and `important: true` counts like `"all"`;
  font hover rules use `add_hover_to_selectors` (`process_advanced_fonts_options`); a phone
  margin/padding no longer inherits the tablet value (`process_advanced_custom_margin_options`);
  width/max-width default to the order class, not `main_css`, and move into a
  `min-width:981px` query when responsive (`process_max_width_options`); `text.css.text_orientation`
  prints `text-align` (`process_advanced_text_options`); props equal to their ET_Global_Settings
  default are emptied (`_maybe_remove_global_default_values_from_props`, read from the cached
  theme's `class-et-global-settings.php`); social follow networks skip the border-radius
  `overflow:hidden`.
- Media that needs WordPress or the network: the gallery's `gallery_ids` are media-library IDs.
  A fresh Playground site has no attachments, so real Divi prints only the gallery's CSS, and the
  tuned fixture checks exactly that. With IDs, the Python renderer draws Divi's grid (or slider)
  markup with grey placeholder images and counts them as `gallery_attachments` in the coverage
  report (`tests/test_render_fallbacks.py`). YouTube and Vimeo URLs need oEmbed. Instead, the
  renderer prints the iframe oEmbed would return and counts it as `video_oembed`. Self-hosted
  video and audio use Divi's own `<video>` and `wp_audio_shortcode()` markup, and the fixtures
  use those.
- Metrics rows gained a Stage column (Task 25 fix round): the earlier rows were labelled with the
  stage they were measured at, and `heldout-outofscope.txt` got a "T25 re-measure" row next to
  its T24 row, now that icon, testimonial and social follow render (the remaining unsupported
  modules still keep it below 0.9).
- Task 26 (interactive and data modules: tabs + tab, circle counter, bar counters + counter,
  countdown timer, pricing tables + table, video slider + video, fullwidth slider sharing the
  Slide) added one tuned fixture per family (`interactive-tuned-*.txt`) and the held-out page
  `interactive-heldout.txt`. Its pre-fix row (measured before its real render was looked at) was
  already exact, 184/184 elements and 86/86 declarations, so there was nothing to fix; it became
  tuned with an identical post-fix row. Engine changes made while tuning (the older tuned
  fixtures still match exactly): a slide now inherits the slider's settings the way
  `SliderItem::maybe_inherit_values()` does (empty-or-default slide values take the slider's
  non-default value, including `background__hover_enabled` and `header_level`; the enable-colour
  toggles are never inherited), so an inherited background hover prints its rule and transition;
  the slide's image markup, `alignment` class and the constant `.et_pb_slider[data-active-slide]`
  prefix follow SliderItem.php; `generate_styles()` takes an explicit hover selector (the PHP
  `hover_selector` argument, used by Tabs and Pricing Tables); a background hover on a module
  whose colour option is `fields_only` (Bar Counters, and the bar counter that inherits it)
  still prints `background-image: initial` but no colour (Background.php hover mode); a child's
  inherited `__hover_enabled` values count for its hover transitions. Bar Counters and the
  fullwidth slider never call `video_background()`, so they don't get
  `et_pb_section_video_on_hover` (the bar counter items do).
- Countdown timer determinism: the server-side output depends only on `date_time` and the site's
  `gmt_offset` (0 on a fresh Playground site); `data-end-timestamp` is the date read as UTC and
  the digits are left empty for the JS. The fixtures still use fixed past dates (2019–2022) so
  the page never shows a live countdown.
- `heldout-outofscope.txt` "T26 re-measure": markup 0.9015, CSS 0.7674. What is left is Task 27's
  contact form and engine features no batch covers yet: section dividers, transforms and
  filters.

## Metrics

| Fixture | Stage | Modules | Tuned | Markup ratio | CSS ratio | Date |
|---|---|---|---|---|---|---|
| heldout2-inscope.txt | T24 held-out pre-fix | accordion, accordion_item, blurb, button, cta, divider, fullwidth_header, heading, image, number_counter, slide, slider, text | no | 0.9574 | 0.9469 | 2026-09-24 |
| heldout2-inscope.txt | T24 held-out post-fix | accordion, accordion_item, blurb, button, cta, divider, fullwidth_header, heading, image, number_counter, slide, slider, text | yes | 1.0000 | 1.0000 | 2026-09-24 |
| heldout-outofscope.txt | T24 held-out | circle_counter, contact_field, contact_form, countdown_timer, counter, counters, heading, icon, pricing_table, pricing_tables, social_media_follow, social_media_follow_network, tab, tabs, testimonial, text | no | 0.2022 | 0.1860 | 2026-09-24 |
| content-heldout.txt | T25 held-out pre-fix | audio, code, fullwidth_code, fullwidth_image, gallery, icon, social_media_follow, social_media_follow_network, team_member, testimonial, video | no | 1.0000 | 0.9550 | 2026-09-24 |
| content-heldout.txt | T25 held-out post-fix | audio, code, fullwidth_code, fullwidth_image, gallery, icon, social_media_follow, social_media_follow_network, team_member, testimonial, video | yes | 1.0000 | 1.0000 | 2026-09-24 |
| heldout-outofscope.txt | T25 re-measure | circle_counter, contact_field, contact_form, countdown_timer, counter, counters, heading, icon, pricing_table, pricing_tables, social_media_follow, social_media_follow_network, tab, tabs, testimonial, text | no | 0.3938 | 0.4884 | 2026-09-24 |
| interactive-heldout.txt | T26 held-out pre-fix | circle_counter, countdown_timer, counter, counters, fullwidth_slider, pricing_table, pricing_tables, slide, tab, tabs, video_slider, video_slider_item | no | 1.0000 | 1.0000 | 2026-09-25 |
| interactive-heldout.txt | T26 held-out post-fix | circle_counter, countdown_timer, counter, counters, fullwidth_slider, pricing_table, pricing_tables, slide, tab, tabs, video_slider, video_slider_item | yes | 1.0000 | 1.0000 | 2026-09-25 |
| heldout-outofscope.txt | T26 re-measure | circle_counter, contact_field, contact_form, countdown_timer, counter, counters, heading, icon, pricing_table, pricing_tables, social_media_follow, social_media_follow_network, tab, tabs, testimonial, text | no | 0.9015 | 0.7674 | 2026-09-25 |
