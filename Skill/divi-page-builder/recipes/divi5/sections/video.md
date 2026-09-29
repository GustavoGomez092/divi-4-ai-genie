# Video (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/video.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

## Structure
```text
section (adminLabel "Video")
└─ row columnStructure "4_4"
   └─ column 4_4: heading (h2) · video
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color` | `section_exemplars[adminLabel=Why Choose Us].attrs.module.decoration.background` (`#ffffff`) | a light `colors.palette` hex |
| section `module.decoration.spacing` → `padding` (+`tablet`/`phone`) | the same exemplar's `module.decoration.spacing`, all three breakpoints (90/60/45px) | `spacing.section_padding[2][0]` |
| heading `title.decoration.font.font` (desktop/tablet/phone) | `module_styles["divi/heading"][section_label=Why Choose Us, column_type=4_4].attrs.title.decoration.font.font`: `h2`, Montserrat 700, navy `gcid-r6navy0001`, 40/32/28px | `typography.scale.h2` → `family`, `weight`, `color`, `size` (+`size_tablet`/`size_phone`) |
| video `video.innerContent` → `src` | the client's YouTube/Vimeo URL or a Media Library MP4 (`webm` beside it for a self-hosted file), never a token; the example's `CLIENT-VIDEO-ID` is a placeholder to replace | — |
| video `thumbnail.innerContent` → `src` | a real still from the video, uploaded to the Media Library | — |
| video `playIcon.decoration.icon` → `color` | no video bundle: the accent, `gcid-primary-color` | same |
| video `overlay.decoration.background` → `color` | the navy global at 60% (`gcid-r6navy0001` with `settings` `{"opacity": 60}`), the brand version of Divi's default `rgba(0,0,0,.6)` | leave it out: Divi's black at 60% |

Divi prints the overlay color only on hover (`.et_pb_video_overlay_hover:hover`, live check): it tints the poster
under the play icon, so a fully opaque color would hide the poster.

## Responsive rules

- The `h2` size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "32px"}`, `phone` `{"size": "28px"}`, from the heading bundle.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The player and its poster scale to the column at every width; the 96px default play icon needs no phone value.

## Worked example (sample-tokens.json)

The Divi 5 module is not lazy: the page source holds the YouTube `<iframe>` from the start, behind the poster
overlay; clicking play hides the overlay and reloads the iframe with `autoplay=1` (live check). Budget for the
embed's weight on every page view.

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Video"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#ffffff"}}},"spacing":{"desktop":{"value":{"padding":{"top":"90px","bottom":"90px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"60px","bottom":"60px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"45px","bottom":"45px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"See Us In Action"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/video {"video":{"innerContent":{"desktop":{"value":{"src":"https://www.youtube.com/watch?v=CLIENT-VIDEO-ID"}}}},"thumbnail":{"innerContent":{"desktop":{"value":{"src":"https://miamirapidplumbing.example/wp-content/uploads/2026/09/video-poster.jpg"}}}},"playIcon":{"decoration":{"icon":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-primary-color\u0022,\u0022settings\u0022:{}}})$"}}}}},"overlay":{"decoration":{"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{\u0022opacity\u0022:60}}})$"}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] no `h1` introduced by this section; the heading is `h2`
- [ ] the poster is a real frame from the video, from the Media Library, not a stock image passed off as the video's own
- [ ] on the draft, clicking play starts the video
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): the navy heading on white 14.9:1. The play icon is a control, so it needs 3:1 against what is behind it **at rest** (WCAG 1.4.11): the poster itself, since the navy tint shows only on hover; pick the icon color (or a darker poster frame) for the real poster
