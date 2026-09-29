# Baseline log

## Format assumptions (from memory, unverified)
- Divi 5 post_content = WP block comments: `<!-- wp:divi/section {json} -->` nesting section > row > column > module; leaf modules self-closing `/-->`.
- Attrs use responsive shape `{"desktop":{"value":...}}`; text content at `<module>.innerContent.desktop.value`; HTML/quotes/&/<> JSON-escaped as " & < >.
- Row: `module.advanced.columnStructure`; column: `module.advanced.type`; heading level in `title.decoration.font.font.desktop.value.headingLevel`.
- Button: `button.innerContent.desktop.value.{text,linkUrl}`; preset via top-level `modulePreset` array.
- Accordion: `divi/accordion` with `divi/accordion-item` children (title/content innerContent, `module.advanced.open`).
- Variables: `$variable({"type":"color|content","value":{"name":"<id>","settings":{}}})$`.

## Unsure about
- Exact attr paths for accordion-item open state, blurb title/content, button linkUrl/linkTarget, adminLabel (`module.meta.adminLabel`), heading textAlign.
- Whether innerContent for text needs extra wrapping; whether blurb needs icon settings (left with no icon/image, only color).
- Number-counter would drop the "+" of "25+" and the "★", so I used divi/text with inline-styled big numbers for stats (verbatim copy over native counters). Inline style uses var(--gcid-r6navy0001).
- Service blurbs have titles only (no invented descriptions). Extra copy invented: "Our Drain Services", "Drain Cleaning FAQ", closing CTA heading/line.
- Layout: services 3+2 blurbs in 1_3 columns (second row only has two columns of 1_3 -- may leave a gap).

## Token usage
- Colors: navy via global color gcid-r6navy0001 (hero/CTA backgrounds, h2, blurb titles); orange gcid-r6orange001 for button bg and blurb icon color; hover #ea580c; literals #ffffff, #f1f5f9, #cbd5e1, #475569 as in tokens (no global ids exist for them).
- Variables: gvid-r6secpad01 for hero section vertical padding; gvid-r6radius01 was NOT applied directly -- relied on button preset r6btnpreset1 (radius/bg/color) via modulePreset.
- Type: Montserrat 700 headings (h1 56/42/34, h2 40/32/28), Lato body 18px; body color #cbd5e1 on dark, #475569 on light.
- Section paddings mirror tokens (80/70px etc.; no tablet/phone overrides added).
