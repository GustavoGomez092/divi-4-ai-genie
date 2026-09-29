# Contact (Divi 5)

Purpose, SEO notes and variations: [the shared recipe](../../sections/contact.md). This page is its Divi 5
structure, field mapping and worked example; how to read them is in the [Divi 5 recipes README](../README.md).

**Use the contact form, not the email opt-in.** Divi's converter leaves the email opt-in (`divi/signup`) module's
custom fields as a Divi 4 shortcode string, so this recipe never uses signup custom fields; the contact form below
converts cleanly and was rendered and submitted on Divi 5.13.1 (live check, [Checklist](#checklist)). The
recipient `email` comes from the client's brief (their intake inbox), never guessed; the map needs a Google Maps
API key configured on the site (Divi → Theme Options → Integration), or it shows Google's "can't load Google Maps"
box, as on the test site.

## Structure
```text
section (adminLabel "Contact Us")
├─ row columnStructure "4_4"
│  └─ column 4_4: heading (h2)
└─ row columnStructure "1_2,1_2"
   ├─ column 1_2: contact-form (title h3)
   │  ├─ contact-field (Name)
   │  ├─ contact-field (Email)
   │  ├─ contact-field (Phone, optional)
   │  └─ contact-field (Message)
   └─ column 1_2: map
      └─ map-pin
```

Every section, row and column carries `module.decoration.layout` → `{"display": "block"}` (a single-column row
states `columnStructure` `"4_4"`); every block `builderVersion` = `site.divi_version`.

## Field mapping
| attribute | token path | fallback if the site has none |
|---|---|---|
| section `module.decoration.background` → `color`, `module.decoration.spacing` → `padding` | `section_exemplars[adminLabel=About].attrs.module.decoration` (`#ffffff`; 80/55/40px on all three breakpoints) | a light `colors.palette` hex; `spacing.section_padding[3][0]` |
| heading `title.decoration.font.font` | `module_styles["divi/heading"][section_label=Why Choose Us, column_type=4_4]`: `h2`, Montserrat 700, navy, 40/32/28px | `typography.scale.h2` |
| form `title.decoration.font.font` | `headingLevel` `"h3"` (one below the section's `h2`; the module's default is `h1`), Montserrat 700, navy, 28px, 24px on tablet and phone | same |
| form `email.advanced.receiver` | the client's intake inbox, from the brief | — |
| form `module.advanced.successMessage` | the client's wording, or leave it out for Divi's default | — |
| form `field.decoration.background` → `color` | `#f1f5f9` (the light neutral in `colors.palette`) | same |
| form `field.decoration.font.font`, `field.decoration.placeholderFont.font` → `color` | the navy global `gcid-r6navy0001` (typed text; Divi prints it as `color:var(--gcid-r6navy0001)` on the form's inputs, live check) and `#475569` (placeholders): Divi's default placeholder is `#999`, 2.6:1 on the field | the navy hex |
| form `captcha.decoration.font.font` → `color` | `#475569` (the "7 + 4 =" question) | same |
| form `button.decoration` | the Free Quote CTA button look: orange `gcid-r6orange001`, navy label, hover `gcid-r6orangelt1`, radius `gvid-r6radius01`, border width 0, Lato 16px (Divi 4 put a white label on the orange, 2.8:1) | the accent with a navy label |
| field `fieldItem.innerContent` (label), `fieldItem.advanced.id`, `.type` (`email`, `text` = the multi-line message; default `input`), `.required` (`"off"` for Phone) | the client's brief | — |
| map `map.innerContent` → `address`, `zoom`; map-pin `pin.innerContent` → `address`, `title.innerContent`, `content.innerContent` | the client's real address | — |

**Every field is full width.** A half-width field (`module.decoration.sizing` → `flexType` `"12_24"`, what the
converter writes for Divi 4's default) stays half width on a phone: a phone `"24_24"` value is written into the
field's class but Divi 5.13.1 prints no CSS for it inside a contact form (live check, 390px). So the recipe leaves
`flexType` at its default, `"24_24"`.

## Responsive rules

- The `h2` size varies per breakpoint: `title.decoration.font.font` → `tablet` `{"size": "32px"}`, `phone` `{"size": "28px"}`, from the heading bundle; the form title drops from 28px to 24px on tablet and phone.
- The section padding copies all three breakpoints of the bundle it comes from; no `_last_edited` flag, the `tablet`/`phone` keys are the switch.
- The `1_2,1_2` row stacks below 981px, form first, map second: the right order for a visitor on a phone.

## Worked example (sample-tokens.json)

```divi5
<!-- wp:divi/section {"module":{"meta":{"adminLabel":{"desktop":{"value":"Contact Us"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}},"background":{"desktop":{"value":{"color":"#ffffff"}}},"spacing":{"desktop":{"value":{"padding":{"top":"80px","bottom":"80px","syncVertical":"on","syncHorizontal":"off"}}},"tablet":{"value":{"padding":{"top":"55px","bottom":"55px","syncVertical":"on","syncHorizontal":"off"}}},"phone":{"value":{"padding":{"top":"40px","bottom":"40px","syncVertical":"on","syncHorizontal":"off"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"4_4"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/heading {"title":{"innerContent":{"desktop":{"value":"Get In Touch"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h2","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"40px"}},"tablet":{"value":{"size":"32px"}},"phone":{"value":{"size":"28px"}}}}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- wp:divi/row {"module":{"advanced":{"columnStructure":{"desktop":{"value":"1_2,1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/contact-form {"title":{"innerContent":{"desktop":{"value":"Request A Free Quote"}},"decoration":{"font":{"font":{"desktop":{"value":{"headingLevel":"h3","family":"Montserrat","weight":"700","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"28px"}},"tablet":{"value":{"size":"24px"}},"phone":{"value":{"size":"24px"}}}}}},"email":{"advanced":{"receiver":{"desktop":{"value":"quotes@miamirapidplumbing.example"}}}},"module":{"advanced":{"successMessage":{"desktop":{"value":"Thanks! We'll call you back within the hour."}}}},"field":{"decoration":{"background":{"desktop":{"value":{"color":"#f1f5f9"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$"}}}},"placeholderFont":{"font":{"desktop":{"value":{"color":"#475569"}}}}}},"captcha":{"decoration":{"font":{"font":{"desktop":{"value":{"color":"#475569"}}}}}},"button":{"innerContent":{"desktop":{"value":{"text":"Send Message"}}},"decoration":{"button":{"desktop":{"value":{"enable":"on"}}},"background":{"desktop":{"value":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orange001\u0022,\u0022settings\u0022:{}}})$"},"hover":{"color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6orangelt1\u0022,\u0022settings\u0022:{}}})$"}}},"font":{"font":{"desktop":{"value":{"family":"Lato","weight":"400","color":"$variable({\u0022type\u0022:\u0022color\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gcid-r6navy0001\u0022,\u0022settings\u0022:{}}})$","size":"16px"}}}},"border":{"desktop":{"value":{"styles":{"all":{"width":"0px"}},"radius":{"sync":"on","topLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","topRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomRight":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$","bottomLeft":"$variable({\u0022type\u0022:\u0022content\u0022,\u0022value\u0022:{\u0022name\u0022:\u0022gvid-r6radius01\u0022,\u0022settings\u0022:{}}})$"}}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/contact-field {"fieldItem":{"advanced":{"id":{"desktop":{"value":"name"}}},"innerContent":{"desktop":{"value":"Name"}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/contact-field {"fieldItem":{"advanced":{"id":{"desktop":{"value":"email"}},"type":{"desktop":{"value":"email"}}},"innerContent":{"desktop":{"value":"Email"}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/contact-field {"fieldItem":{"advanced":{"id":{"desktop":{"value":"phone"}},"required":{"desktop":{"value":"off"}}},"innerContent":{"desktop":{"value":"Phone"}}},"builderVersion":"5.13.1"} /--><!-- wp:divi/contact-field {"fieldItem":{"advanced":{"id":{"desktop":{"value":"message"}},"type":{"desktop":{"value":"text"}}},"innerContent":{"desktop":{"value":"Message"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/contact-form --><!-- /wp:divi/column --><!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_2"}}},"decoration":{"layout":{"desktop":{"value":{"display":"block"}}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/map {"map":{"innerContent":{"desktop":{"value":{"address":"1200 Brickell Ave, Miami, FL 33131","zoom":14}}}},"builderVersion":"5.13.1"} --><!-- wp:divi/map-pin {"pin":{"innerContent":{"desktop":{"value":{"address":"1200 Brickell Ave, Miami, FL 33131"}}}},"title":{"innerContent":{"desktop":{"value":"Miami Rapid Plumbing"}}},"content":{"innerContent":{"desktop":{"value":"\u003cp\u003e1200 Brickell Ave, Miami, FL 33131\u003c/p\u003e"}}},"builderVersion":"5.13.1"} /--><!-- /wp:divi/map --><!-- /wp:divi/column --><!-- /wp:divi/row --><!-- /wp:divi/section -->
```

## Checklist
- [ ] `python3 scripts/validate.py page.html --tokens tokens.json` — 0 errors, no `W5_UNKNOWN_VARIABLE`/`W5_UNKNOWN_PRESET`; this section alone: `python3 scripts/validate.py section.html --tokens tokens.json --fragment` (`tokens.json` is the target site's own; `recipes/divi5/sample-tokens.json` is only the example's fictional brand)
- [ ] `python3 scripts/preview.py render page.html --tokens tokens.json --out preview.html` — show the user and **stop until they approve it** ([README §7](../README.md#7-the-verification-loop))
- [ ] Only after that approval: `python3 scripts/publish.py draft page.html --site "$SITE" --user "$WP_USER" --title "…"` — review its `preview_url` before publishing ([publishing](../../../reference/publishing.md))
- [ ] on the draft, the form behaves: sending it empty lists the required fields (Name, Email, Message, Captcha), a wrong captcha answer says so, and a right one replaces the form with the success message; each field keeps a `<label for>` (visually hidden: the labels show as placeholders)
- [ ] no `divi/signup` module and no signup custom field in this section
- [ ] exactly one `h2` and no `h1` on this section; the form title is `h3` (the map pin's title also prints as an `h3`, in the map's markup, live check)
- [ ] the recipient `email` matches the client's brief; a Google Maps API key is configured on the live site before relying on the map
- [ ] contrast: every text color on its background is at least 4.5:1 (3:1 only for text of 24px, or 19px bold, and up), hover and active states included ([README §2](../README.md#contrast)): navy typed text on the `#f1f5f9` fields 13.6:1, `#475569` placeholders and captcha question 6.9:1 (the captcha on white 7.6:1); the button's navy label on orange 5.3:1 and on the hover 10.3:1
