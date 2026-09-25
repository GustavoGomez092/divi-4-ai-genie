# Video

**Use for:** an embedded YouTube/Vimeo (or self-hosted MP4) video — a company intro, a technique
walkthrough, a customer testimonial video — shown behind a poster image and play button rather than
auto-loading the player. · **SEO:** the module has no heading of its own; give the section a real
`h2` if a caption/introduction is needed above it. **Lazy-load note.** Divi's `et_pb_video` module
is lazy by design: with `image_src` set, the front end renders only the static overlay image and a
play-icon button on first load — the actual YouTube/Vimeo iframe (and its own third-party scripts)
is only requested after a visitor clicks play. Always set `image_src`; without it, Divi still shows
a play button over a black box, but skips the chance to show a real, fast-loading preview frame and
to avoid the oEmbed request until the visitor actually wants the video. **Validator note.**
`validate.py`'s `W_EXTERNAL_IMAGE` check only looks at image fields (upload fields whose media type
is an image), so a YouTube/Vimeo `src` on `et_pb_video` is never flagged; `image_src` (the poster
image) is an image field and must be a real Media Library upload on the site's own domain.

## Structure
```text
section (Video, light tone)
├─ row (heading only)
│  └─ column 4_4: heading (h2)
└─ row
   └─ column 4_4: video
```

## Token mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `background_color` | `module_styles.et_pb_section[background=#ffffff,custom_padding=90px].attrs.background_color` (the "Why Choose Us" bundle, reused for its light tone) | `colors.palette[1].hex` (`#ffffff`) |
| section `custom_padding` (+`_tablet`/`_phone`) | the same bundle's `attrs.custom_padding` | `spacing.section_padding[2][0]` |
| heading (`h2`) `title_font`, `title_text_color`, `title_font_size` | `module_styles.et_pb_heading[section_tone=light,column_type=4_4].attrs` | `typography.scale.h2.font` / `.color` / `.size` |
| video `play_icon_color` | no `et_pb_video` bundle exists in tokens — `colors.customizer.accent` (`#f97316`), so the play button reads as the brand's call-to-action color | same |
| video `thumbnail_overlay_color` | no bundle exists in tokens for this module — `colors.palette[0].hex` (navy) at full opacity; the site's tokens don't record a translucent variant, and `validate.py`'s `W_OFF_PALETTE_COLOR` check only matches colors present verbatim in `tokens.json`, so an invented `rgba()` tint would flag as off-palette even though it's "just" the same navy with alpha | `colors.palette[0].hex` |
| `src` (the YouTube/Vimeo/MP4 URL), `image_src` (poster image) | the client's own brief/media (the actual video URL and a real still frame from it) — never a token, never a stock/placeholder frame passed off as the video's own thumbnail | — |

## Required fields · Optional fields

Required: [`et_pb_section`](../../reference/modules/et_pb_section.md) `background_color`,
`custom_padding` (+responsive); [`et_pb_video`](../../reference/modules/et_pb_video.md) `src`,
`image_src`.

Optional: `play_icon_color`, `thumbnail_overlay_color` for brand-matched overlay styling;
`font_icon` to swap the default play glyph for a different one (verify the glyph visually before
using it — see `reference/modules/README.md`'s note on icon fonts); `src_webm` for a self-hosted
video that should offer a WebM source alongside the MP4/embed URL; the optional heading row above
the module.

## Responsive rules

`title_font_size` on the section's `h2` (if used) needs `_tablet`/`_phone` (40px → 32px → 28px)
plus `title_font_size_last_edited="on|phone"`. The section's `custom_padding` needs its usual
`_tablet`/`_phone` pair. `icon_font_size` (the play button's size) can optionally get
`_tablet`/`_phone` values if the default 96px play icon feels oversized on a narrow phone preview
image; the video player itself already reflows to the column's full width at every breakpoint with
no extra attributes.

## Variations

- **No-heading variant:** drop the heading row entirely for a video that's self-explanatory in
  context (e.g. directly under a heading that already introduces it in the section above).
- **Self-hosted MP4 variant:** point `src` at an MP4 file URL from the Media Library instead of a
  YouTube/Vimeo URL, and add `src_webm` for broader format support — Divi renders its own native
  HTML5 player instead of an oEmbed iframe.
- **Icon-swap variant:** set `font_icon` to a different glyph for the play button, verified visually
  first (this recipe uses the module's own default play triangle, which needs no `font_icon`
  override).

## Worked example (sample-tokens.json)
```divi
[et_pb_section admin_label="Video" _builder_version="4.27.9" _module_preset="default" background_color="#ffffff" custom_padding="90px||90px||true|false" custom_padding_tablet="60px||60px||true|false" custom_padding_phone="45px||45px||true|false" custom_padding_last_edited="on|phone"][et_pb_row _builder_version="4.27.9" _module_preset="default"][et_pb_column type="4_4" _builder_version="4.27.9" _module_preset="default"][et_pb_heading title="See Us In Action" title_level="h2" _builder_version="4.27.9" _module_preset="default" title_font="Montserrat|700|||||||" title_text_color="#0b2a3c" title_font_size="40px" title_font_size_tablet="32px" title_font_size_phone="28px" title_font_size_last_edited="on|phone"][/et_pb_heading][et_pb_video src="https://www.youtube.com/watch?v=dQw4w9WgXcQ" image_src="https://miamirapidplumbing.example/wp-content/uploads/2026/09/video-poster.jpg" _builder_version="4.27.9" _module_preset="default" play_icon_color="#f97316" thumbnail_overlay_color="#0b2a3c"][/et_pb_video][/et_pb_column][/et_pb_row][/et_pb_section]
```

## Checklist
- [ ] `python3 Skill/divi-page-builder/scripts/validate.py <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — 0 errors; exactly one expected `W_EXTERNAL_IMAGE` warning on `et_pb_video`'s `src` (see the Validator note above) and no other warnings
- [ ] `python3 Skill/divi-page-builder/scripts/preview.py render <file> --tokens Skill/divi-page-builder/recipes/sample-tokens.json` — fast visual check; the actual YouTube/Vimeo oEmbed fetch needs network — the Python preview shows what the oEmbed iframe would look like and counts it in the coverage report, `--exact` shows the real embed when it has network access
- [ ] `research/tools/push_local.sh <file> "Video"` — push to divi-test.local, note the printed id/url
- [ ] `node research/python-renderer-spike/shoot.mjs <outdir> video <url> --width 1440,390` — screenshot at desktop (1440) and phone (390)
- [ ] `research/tools/wp-local.sh post delete <id> --force` — delete the test page once the screenshots look right
- [ ] no `h1` introduced by this section; the optional heading is `h2`
- [ ] `image_src` is a real poster frame, not a generic stock/placeholder image passed off as the video's own thumbnail
