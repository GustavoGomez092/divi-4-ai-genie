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
- Task 26 fix round: slides now render their own fonts (header/body, responsive and hover),
  the background overlay (`use_bg_overlay`: `.et_pb_slide_overlay_container` markup and colour),
  the text overlay (`use_text_overlay`: `.et_pb_text_overlay_wrapper` around title and content,
  its colour) and the text overlay radius, plus a desktop background video (the slide gets
  `et_pb_section_video et_pb_preload`). The slider itself never gets `et_pb_preload`: FullwidthSlider.php
  checks `$et_pb_slider_has_video`, but nothing in 4.27.9 sets it to true.
  `interactive-tuned-slide-fonts-overlays.txt` measured markup 0.6667 and CSS 0.2391 (11/46)
  before the fix and matches exactly after it. The fonts engine also gained Divi's letter-spacing
  ligature fix (`maybe_push_element_to_letter_spacing_fix_list()`): a font rule that is only a
  non-default letter-spacing puts its selector, prefixed with `body.safari`/`body.iphone`/
  `body.uiwebview`, on a list kept per module type; from then on, every module of that type on
  the page prints `font-variant-ligatures: no-common-ligatures` for it with its own order class.
  Background handling moved from `options.py` into `background.py`.
- Blind spot: `fidelity.py` only counts selectors that contain an order class as a class
  (`.x_0`). Rules scoped by an attribute, such as the slider's
  `.et_pb_slider[data-active-slide="et_pb_slide_0"] .et-pb-slider-arrows …`, have the order
  class inside quotes and aren't counted, so a CSS ratio of 1.0 does not verify them. They are
  ported from SliderItem.php but unchecked.
- Countdown timer determinism: the server-side output depends only on `date_time` and the site's
  `gmt_offset` (0 on a fresh Playground site); `data-end-timestamp` is the date read as UTC and
  the digits are left empty for the JS. The fixtures still use fixed past dates (2019–2022) so
  the page never shows a live countdown.
- `heldout-outofscope.txt` "T26 re-measure": markup 0.9015, CSS 0.7674. What is left is Task 27's
  contact form and engine features no batch covers yet: section dividers, transforms and
  filters.
- Task 27 (forms, maps and fallbacks: contact form + field, email optin + custom field, map,
  fullwidth map + pin) added `forms-tuned-contact-form.txt`, `forms-tuned-signup.txt`,
  `maps-tuned-map.txt`, `maps-tuned-fullwidth-map.txt` and the held-out page `forms-heldout.txt`
  (conditional logic, captcha off with a left-icon submit button, an AWeber single-name optin
  with responsive name width, custom fields of four types, a map with three pins and a fullwidth
  map on one page, forms and optins inside a specialty section's inner row). Its pre-fix row was
  measured before its real render was looked at: CSS exact, markup 197 of 198 elements. The one
  miss was not a T27 module: the Fullwidth Header prints `.et_pb_header_content_wrapper` even
  without content (`render_element(..., 'required' => false)`). After that fix the page became
  tuned. Engine changes made while tuning (the older tuned fixtures still match exactly):
  the `form_field` family (`process_advanced_form_field_options()`: field background/text
  colours for normal, hover and focus, with placeholder selectors; `MarginPadding::
  process_advanced_css()` for the fields' own margin and padding; `formfield.py`); the `height`
  family (`process_height_options()`, generic: responsive values print on every device, falling
  back to the option's `default_tablet`/`default_phone`, e.g. the map's 350px/200px); border radii
  print whenever they differ from the option's default (`'on||||'` unless the option sets one,
  such as the optin fields' `on|3px|3px|3px|3px`), no longer skipping all-zero values; the
  optin's focus border only with `use_focus_border_color`; a button's background uses the
  option's `css.important` (Contact Form's `plugin_only`); hover transitions for `custom_margin`,
  `height`/`max_height` and the form-field colours (`get_transition_*_fields_css_props`); the
  CSS minifier drops spaces around `+`; `property_values()` gives tablet/phone the default when
  responsive editing is off (`get_property_values()`). `build_schema.py` now keeps the `height`
  and `form_field` families in the compact schema.
- Forms and determinism: real Divi prints a new nonce and random captcha digits (`rand(1, 15)`)
  on every contact form render, and a checksum input in the optin. None of them reaches the
  comparison, which reads tags, classes and builder CSS only, so no normalization is needed
  (`fidelity.py` docstring, pinned by `tests/test_fidelity.py`). The Python renderer prints a
  fixed `1 + 1` captcha and a placeholder nonce; the optin checksum is Divi's own
  `md5(serialize($attrs))` and matches Playground. Attribute values the harness can't see
  (input patterns, conditional-logic JSON, the checksum) are unit-tested against the values real
  Divi printed (`tests/test_render_engine.py`).
- Email Optin: the form prints only once a list is chosen. Real pages store it as
  `<account>|<list id>` from the site's connected provider account, so the fixtures use values
  like `mailchimp_list="Studio|a1b2c3d4"` (the validator now accepts that pair for `*_list`
  fields). No provider API is called at render time; a signup custom field without a type
  prints only its label, as in Divi (its default type is `none`).
- Maps: Divi prints an empty `.et_pb_map` with data attributes and the pins as hidden children;
  its JS draws the Google map with the site's key. The preview matches the markup and CSS; the
  canvas stays empty without a key. An inset box shadow targets `.box-shadow-overlay`, but the
  map's markup has no overlay element (Divi's JS adds none either). The map's CSS filters
  (`child_filter_*`) are not ported.
- WordPress-data modules (Task 27): blog, portfolio, filterable portfolio, fullwidth portfolio,
  post slider, fullwidth post slider, post title, fullwidth post title, post content, fullwidth
  post content, post navigation, comments, sidebar, menu and fullwidth menu show the live site's
  posts, projects, menus, comments or widgets. The Python preview renders a blue dashed block
  naming what the module shows; the coverage report lists them under `needs_site_data`, apart
  from `unsupported_modules`, because the `--exact` preview can't show them either (a fresh
  Playground WordPress has no posts, menus or media): the WordPress draft preview is the check.
  Gallery attachment IDs (the media library) moved to `needs_site_data` too. oEmbed videos
  (`video_oembed`) stay in `unsupported_modules`: they need the network, not the site's data, and
  the `--exact` preview fetches the real embed when it has network (fix round 1: a Playground
  render of a YouTube `et_pb_video` produced the real oEmbed iframe).
  Search and Login need no site data and are not ported: they stay in `unsupported_modules`
  with a red block that points to `--exact` (tests/test_render_fallbacks.py,
  tests/test_preview_cli.py).
- `heldout-outofscope.txt` "T27 re-measure": markup 0.9893, CSS 0.7674. Every module on it is
  now supported, so the test checks its ratio (>= 0.9) again. What is left is engine features
  no batch covers: the section divider, the heading's transform and the text's CSS filter.

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
| forms-heldout.txt | T27 held-out pre-fix | button, contact_field, contact_form, countdown_timer, fullwidth_header, fullwidth_map, map, map_pin, signup, signup_custom_field, text | no | 0.9975 | 1.0000 | 2026-09-25 |
| forms-heldout.txt | T27 held-out post-fix | button, contact_field, contact_form, countdown_timer, fullwidth_header, fullwidth_map, map, map_pin, signup, signup_custom_field, text | yes | 1.0000 | 1.0000 | 2026-09-25 |
| heldout-outofscope.txt | T27 re-measure | circle_counter, contact_field, contact_form, countdown_timer, counter, counters, heading, icon, pricing_table, pricing_tables, social_media_follow, social_media_follow_network, tab, tabs, testimonial, text | no | 0.9893 | 0.7674 | 2026-09-25 |
