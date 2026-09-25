# REST publishing experiments (Task 10)

Verified live against `http://divi-test.local` (LocalWP, Divi 4.27.9, PHP 8.2, one
administrator user `user`). All commands below ran with `WP_USER` and `WP_APP_PASSWORD`
exported in the shell only; the password value itself is never shown or written to disk here
or anywhere else. Every test page was titled `Plan Test: …` and deleted at the end of each
run; the pre-existing probe page (ID 11, "Probe: Divi AI Emergency Plumber") was never
modified — verified by `wp post get 11 --field=post_title` after every run.

## Setup

```bash
research/tools/wp-local.sh eval 'var_dump( wp_is_application_passwords_available() );'
# => bool(true)  (LocalWP's divi-test site already reports WP_ENVIRONMENT_TYPE=local; no
#    config change was needed)

ADMIN=$(research/tools/wp-local.sh user list --role=administrator --field=user_login | head -1)
export WP_USER="$ADMIN"
export WP_APP_PASSWORD="$(research/tools/wp-local.sh user application-password create "$ADMIN" plan-test --porcelain)"
```

Note on process boundaries: this shell's tool runs each `Bash` call in a *fresh* shell (only
the working directory persists), so `WP_APP_PASSWORD` does not survive between separate tool
calls. Every experiment below that needs the password was written as a single script and run
in one shell invocation, creating and deleting its own Application Password each time. This
does not affect real usage — a human/agent working in one continuous terminal session keeps
the exported variable for as long as they need it.

## Experiment 1: create + read-back round-trip (`handwritten-landing.txt`)

```bash
SITE=http://divi-test.local
python3 -c 'import json; print(json.dumps({"title": "Plan Test: REST create", "status": "draft",
  "content": open("tests/fixtures/valid/handwritten-landing.txt").read(),
  "meta": {"_et_pb_use_builder": "on"}}))' > /tmp/pp-body.json
curl -s -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d @/tmp/pp-body.json "$SITE/wp-json/wp/v2/pages" > /tmp/pp-created.json
ID=$(python3 -c "import json;print(json.load(open('/tmp/pp-created.json'))['id'])")
curl -s -u "$WP_USER:$WP_APP_PASSWORD" "$SITE/wp-json/wp/v2/pages/$ID?context=edit" > /tmp/pp-read.json
```

**Result:** `roundtrip identical: True | meta: on | link: http://divi-test.local/?page_id=15`

`content.raw` from `GET ?context=edit` was byte-for-byte identical to the file sent — no
attribute re-escaping, no whitespace changes, no entity conversion. `meta._et_pb_use_builder`
round-tripped as `"on"`.

**Conclusion:** a `POST /wp/v2/pages` with `content` = raw shortcode text and
`meta._et_pb_use_builder = "on"` stores the shortcode exactly as sent; the create/read cycle is
transparent for ordinary Divi shortcode.

## Experiment 2: CSS cache behavior on REST update

Ran as one script per page (see script sketch below); repeated once for confirmation after
fixing a curl redirect bug (see "gotcha" note).

```bash
# publish, load once (curl -L to follow the page_id -> pretty-permalink redirect), inspect et-cache
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"status":"publish"}' "$SITE/wp-json/wp/v2/pages/$ID"
curl -sL "$LINK" > /tmp/page1.html
ls -la ~/"Local Sites/divi-test/app/public/wp-content/et-cache/$ID/"
# -> et-core-unified-<ID>.min.css, et-core-unified-deferred-<ID>.min.css,
#    et-divi-dynamic-<ID>-critical.css, et-divi-dynamic-<ID>-late.css, et-divi-dynamic-<ID>.css

# update content over REST (change one heading)
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"content": "...heading changed..."}' "$SITE/wp-json/wp/v2/pages/$ID"
ls -la ~/"Local Sites/divi-test/app/public/wp-content/et-cache/$ID/"
# -> ls: No such file or directory  (the whole et-cache/<ID>/ directory was deleted)

curl -sL "$LINK" > /tmp/page2.html   # second load
ls -la ~/"Local Sites/divi-test/app/public/wp-content/et-cache/$ID/"
# -> the 5 CSS files are back, freshly regenerated
```

**Result:**
- Immediately after `POST` an update to `content`, the entire `et-cache/<ID>/` directory is
  deleted (not merely truncated or marked stale) — confirmed by `ls` returning
  "No such file or directory" right after the update, before any further page load.
- The very next front-end request to the page regenerates all 5 cache files from scratch
  (confirmed by `ls` again after a second `curl -sL "$LINK"`).
- The regenerated page's HTML reflects the new content (`Orlando` present, old `Miami` heading
  gone) on the very next load — no manual cache-purge step is required after a REST update.

**Gotcha found and fixed:** the brief's suggested `curl "$SITE/?page_id=$ID"` (no `-L`)
returns an empty body once the page is published, because WordPress 301-redirects
`?page_id=N` to the page's pretty permalink and curl without `-L` doesn't follow it. All page
loads in this and the layout experiment use `curl -sL` against the `link` field from the
REST response instead.

**Conclusion:** a REST `content` update on a Divi page invalidates (deletes) its et-cache
directory synchronously as part of the save; regeneration is automatic and lazy (on next
render). No extra "purge cache" call is needed — document this as the answer to "does a REST
update clear Divi's et-cache CSS": **yes, unconditionally and immediately.**

## Experiment 3: layout without a sidebar

Traced against Divi's own source
(`~/Local Sites/divi-test/app/public/wp-content/themes/Divi/functions.php`,
`et_divi_sidebar_class()`, around line 8246) to explain the observed body classes.

Tested five page configurations, all read via `curl -sL "$LINK" | grep -o '<body[^>]*>'`:

| # | Setup | Rendered sidebar-related class |
|---|---|---|
| A | `meta._et_pb_use_builder="on"`, plain shortcode content, no `_et_pb_page_layout` meta | `et_no_sidebar` |
| B | plain WP page, no builder meta at all | `et_right_sidebar` (theme default) |
| C | page A + REST `{"template":"page-template-blank.php"}` | still `et_no_sidebar`, **but** `et_fixed_nav`, `et_show_nav`, `et_header_style_left`, `et_pb_footer_columns4` are all gone from body class — the header/nav/footer chrome itself is stripped |
| D | page A + `wp post meta update $ID _et_pb_page_layout et_no_sidebar` | still `et_no_sidebar` (meta value made no difference) |
| D2 | page A + `wp post meta update $ID _et_pb_page_layout et_full_width_page` | still `et_no_sidebar` (meta value made no difference) |
| E | page A + `wp post meta update $ID _et_pb_page_layout et_right_sidebar`, then REST `{"meta":{"_et_pb_page_layout":"et_no_sidebar"}}` | still `et_no_sidebar`; REST response `meta` object never contains `_et_pb_page_layout` at all, and `wp post meta get $ID _et_pb_page_layout` afterward still returns the wp-cli-set value (`et_right_sidebar`) — **the REST call was silently ignored, not applied and not errored** |

Follow-up on a **non-builder** page (no `_et_pb_use_builder` meta) to isolate whether
`_et_pb_page_layout` ever has an effect at all:

| Setup | Rendered class |
|---|---|
| no meta | `et_right_sidebar` |
| `_et_pb_page_layout = et_full_width_page` (wp-cli) | `et_full_width_page` |
| `_et_pb_page_layout = et_no_sidebar` (wp-cli) | `et_full_width_page` (same as above!) |

**Root cause (from `functions.php`):**

```php
} elseif ( ! is_singular() || ( ! ( $page_layout = get_post_meta( $post_id, '_et_pb_page_layout', true ) ) && ! $is_builder_active ) ) {
    $page_layout = $default_sidebar_class;               // et_right_sidebar by default
} elseif ( $is_builder_active && ( $is_blank_page_tpl || ! $page_layout || is_page() ) ) {
    $page_layout = 'et_no_sidebar';                       // forced for ANY builder-active Page
}

if ( 'et_no_sidebar' === $page_layout && is_singular() ) {
    if ( et_builder_post_is_of_custom_post_type( $post_id ) || $is_builder_active ) {
        $classes[] = 'et_no_sidebar';
    } else {
        $classes[] = 'et_full_width_page';                // backward-compat rename for a plain Page
    }
} else {
    $classes[] = $page_layout;
}
```

Two independent things are going on:
1. **When `_et_pb_use_builder = "on"` and the post type is `page`,** the middle branch's
   `is_page()` condition is always true, so `$page_layout` is *forced* to `et_no_sidebar`
   regardless of whatever `_et_pb_page_layout` says. This is why methods D/D2/E all rendered
   identically to A — **the meta key is simply irrelevant on a builder-enabled Page.**
2. **On a non-builder Page,** `_et_pb_page_layout` does take effect, but the class-emission
   step renames `et_no_sidebar` to `et_full_width_page` for any post type that isn't a Divi
   custom post type (i.e. any ordinary Page) — so on a plain page, meta values `et_no_sidebar`
   and `et_full_width_page` are indistinguishable in the rendered class; both come out as
   `et_full_width_page`.
3. `_et_pb_page_layout` is **not** a registered REST meta field — it never appears in a REST
   response's `meta` object and a REST `POST` targeting it is silently dropped (no error, no
   effect on the DB value).
4. `template: "page-template-blank.php"` is the *only* REST-settable field of the three that
   changes anything observable — it swaps the whole page template, stripping the site header,
   primary nav, and footer widgets entirely (a true blank/full-bleed layout), independent of
   the sidebar class question.

**Conclusion (this is publish.py's `--page-fields` guidance):**
- A normal skill-authored Divi page (`meta._et_pb_use_builder = "on"`) already renders with
  `et_no_sidebar` automatically. **Do nothing** — setting `_et_pb_page_layout` has no effect
  and isn't reachable over REST anyway.
- To also remove the site header/nav/footer chrome (a true blank canvas, e.g. for a landing
  page that supplies its own header section), set, over REST, on the page:
  ```json
  {"template": "page-template-blank.php"}
  ```
  This is the one field that produced a real, REST-settable layout change.
- `_et_pb_page_layout` should only be touched via `wp post meta update <id> _et_pb_page_layout <value>`
  (SSH/WP-CLI) on **non-builder** pages, and even then `et_no_sidebar` and `et_full_width_page`
  are equivalent in the rendered output.

## Experiment 4: entities / unicode round-trip (`unicode.txt`)

Fixture content includes an em dash, curly quotes, an emoji, and already-encoded `%22`/`%92`/
`%5c` sequences inside `custom_css_main_element` (per `page-format.md`'s escaping table),
plus an HTML entity (`&amp;`) inside tag content:

```
[et_pb_heading title="Odontología en Miami — "sonrisa" %22real%22 %91VIP%93 & más 😀" ...]
[et_pb_text custom_css_main_element="content: %22a%92b%5cc%22;" ...]<p>Precio: $99 &amp; "garantía" — sin sorpresas.</p>[/et_pb_text]
```

```bash
python3 -c 'import json; print(json.dumps({"title": "Plan Test: unicode", "status": "draft",
  "content": open("tests/fixtures/valid/unicode.txt").read(),
  "meta": {"_et_pb_use_builder": "on"}}))' > /tmp/pp-unicode-body.json
curl -s -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d @/tmp/pp-unicode-body.json "$SITE/wp-json/wp/v2/pages" > /tmp/pp-unicode-created.json
ID2=$(python3 -c "import json;print(json.load(open('/tmp/pp-unicode-created.json'))['id'])")
curl -s -u "$WP_USER:$WP_APP_PASSWORD" "$SITE/wp-json/wp/v2/pages/$ID2?context=edit" > /tmp/pp-unicode-read.json
```

**Result:** `unicode roundtrip identical: True` — `content.raw` matched the file exactly,
including the é, em dash, curly quotes, emoji, and the already-percent-encoded escape
sequences. WordPress did not run `wptexturize()` or any entity conversion against
`content.raw` on write or on the `context=edit` read.

**Conclusion:** no update needed to `page-format.md`'s escaping table — REST transport is
byte-transparent for `post_content`, unicode included. Added a short confirmation note to
`page-format.md` under a new "Transport" heading pointing at this experiment and at
`publishing.md`, since Task 22 and other readers should know this was verified over REST, not
just via `wp post create`.

## Supplementary: media upload (not in the brief's script, verified anyway)

`publishing.md` needs an exact media example; verified live:

```bash
curl -s -u "$WP_USER:$WP_APP_PASSWORD" \
  -H 'Content-Disposition: attachment; filename="pp-test.png"' \
  -H 'Content-Type: image/png' \
  --data-binary @pp-test.png \
  "$SITE/wp-json/wp/v2/media"
# -> {"id":26,"source_url":"http://divi-test.local/wp-content/uploads/2026/09/pp-test.png",...}

curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"alt_text":"Plan Test alt text"}' "$SITE/wp-json/wp/v2/media/26"
# -> alt_text: "Plan Test alt text"
```

Both calls worked as documented in the WP REST API handbook; the media item was deleted with
`curl -X DELETE ... "$SITE/wp-json/wp/v2/media/26?force=true"` immediately after.

## Supplementary: auth error shapes (for troubleshooting section)

```bash
curl -s -w '\nHTTP %{http_code}\n' -u "user:wrong-password" "$SITE/wp-json/wp/v2/pages?context=edit"
# {"code":"rest_forbidden_context","message":"Sorry, you are not allowed to edit posts in this post type.","data":{"status":401}}
# HTTP 401

curl -s -w '\nHTTP %{http_code}\n' -X POST -u "user:wrong-password" -H 'Content-Type: application/json' \
  -d '{"title":"x","status":"draft","content":"x"}' "$SITE/wp-json/wp/v2/pages"
# {"code":"rest_cannot_create","message":"Sorry, you are not allowed to create posts as this user.","data":{"status":401}}
# HTTP 401
```

Note: `GET /wp/v2/pages` **without** `context=edit` returns `200` and the public page list
even with wrong/no credentials — invalid auth is only rejected on routes that need elevated
access (editing, `context=edit`, creating, private content).

`rest_cannot_edit` (403) specifically fires for an *authenticated* user who lacks
`edit_post` capability on that specific post (e.g. a Contributor editing someone else's
page). This test site has only one user (an administrator), so this exact 403 was **not**
reproduced live — it's documented in `publishing.md` from WordPress core's REST API
Controller behavior (`WP_REST_Posts_Controller::update_item_permissions_check()`), which is
standard, stable, versioned WordPress behavior, not something specific to this site.

## Cleanup verification

```bash
research/tools/wp-local.sh post list --post_type=page --s="Plan Test" --format=count
# => 0

research/tools/wp-local.sh user application-password list user --format=table
# => (empty — header row only)

research/tools/wp-local.sh post get 11 --field=post_title
# => Probe: Divi AI Emergency Plumber   (untouched)
```

All test pages (IDs 15, 18, 19, 21, 22, 24, 25) and the one test media item (ID 26) created
during these experiments were deleted with `force=true`. No Application Password named
`plan-test` remains on the `user` account. `WP_ENVIRONMENT_TYPE` did not need to be set —
`wp_is_application_passwords_available()` was already `true` on this LocalWP site.
