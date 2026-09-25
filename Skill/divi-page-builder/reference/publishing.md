# Publishing over REST

## Using publish.py

`scripts/publish.py` wraps the REST flow below into four commands. The password always comes
from env `WP_APP_PASSWORD` (never a flag, never printed); set `WP_USER`/`SITE` however you
like, but pass them explicitly as `--user`/`--site`.

```bash
export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"

# 1. Fetch the current content.raw before editing an existing page
python3 scripts/publish.py fetch --site "$SITE" --user "$WP_USER" --page-id 15 --out original.txt

# 2. Upload one image directly (rarely needed — draft uploads local images automatically)
python3 scripts/publish.py media --site "$SITE" --user "$WP_USER" hero.jpg --alt "Plumber repairing a burst pipe"

# 3. Draft-first: validates the page, uploads any local images, and creates/updates a draft
python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "Emergency Plumber in Miami"

# updating an existing page keeps it a draft (does not publish)
python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "..." --page-id 15

# full-bleed landing page: strip header/nav/footer via the one REST-settable layout field
python3 scripts/publish.py draft page.txt --site "$SITE" --user "$WP_USER" --title "..." \
  --page-fields '{"template":"page-template-blank.php"}'

# 4. Publish only after the user has reviewed the draft's preview_url and approved it
python3 scripts/publish.py publish --site "$SITE" --user "$WP_USER" --page-id 15 --yes
```

**Draft-first, always.** `draft` never publishes — the page is created or updated with
`status: draft` regardless of whether it's new or existing. `publish` is a separate,
explicit step that flips `status` to `publish`, and it refuses (exit 1, no HTTP call) unless
`--yes` is given. Only pass `--yes` after the user has looked at the draft's `preview_url`
(from `draft`'s JSON output) and approved it — never as a default or automatic follow-up to
`draft`.

**Local images.** Reference images in the page source as `./images/hero.jpg`, `../hero.jpg`,
or `file:///abs/path.jpg` (paths resolved relative to the page file's own folder, or absolute
for `file://`) instead of a live URL. `draft` finds every image attribute
(`divi_checks_values.IMAGE_ATTRS`, plus anything ending `_image`) with such a value, uploads
the file to the Media Library, sets `alt_text` from the module's `alt`/`title_text` attribute,
and rewrites the attribute to the returned `source_url` before creating/updating the page.
Each distinct local file is uploaded once even if referenced by multiple modules; the JSON
output's `uploaded` array lists every file that was uploaded (`id`, `url`, `file`).

**`--page-fields`** takes a JSON object merged into the page body, for fields not covered by
the standard flags — most commonly the layout template found in Task 10's REST experiments:
`--page-fields '{"template":"page-template-blank.php"}'` removes the site's header, primary
nav, and footer chrome for a true full-bleed landing page. No sidebar is Divi's own default
for any builder-active page (`meta._et_pb_use_builder: "on"`) — nothing needs to be set for
that.

**Validation.** `draft` runs `validate_source` before doing anything else and refuses (exit 1,
no HTTP calls at all — no uploads, no draft) if there are any blocking errors, printing each
finding to stderr the same way `validate.py` does.

**Exit codes:** `0` success · `1` validation errors, or `publish` without `--yes` · `2` usage
error (including a missing `WP_APP_PASSWORD`), HTTP error, or I/O error. HTTP error messages
include only the method/path and WordPress's own `code`/`message` — never the password or a
full URL with credentials.

## Raw REST reference

Everything below was verified live against a real WordPress + Divi 4.27.9 install
(`http://divi-test.local`, a LocalWP site) using the WordPress REST API and Application
Passwords. See `research/tools/notes/rest-experiments.md` for the exact commands and raw
results this page is built from.

## 1. Auth

Use a WordPress **Application Password**, not the account's login password:

1. On the client site: **Users → Profile → Application Passwords**, or (for scripted setup on
   a site you control) WP-CLI: `wp user application-password create <user> <name> --porcelain`.
2. Requests use HTTP Basic auth: `-u "$WP_USER:$WP_APP_PASSWORD"`.
3. **HTTPS is required on live sites.** Application Passwords are transmitted as Basic auth
   (base64, not encrypted) on every request; WordPress core disables the feature entirely over
   plain HTTP unless `wp_is_application_passwords_available()` is forced true (e.g. by setting
   `WP_ENVIRONMENT_TYPE` to `local` — only appropriate for local development, never for a
   client's real site).
4. Store credentials as environment variables, never in code or config files. Every `curl`
   example on this page also uses `$SITE` for the site's base URL (no trailing slash):
   ```bash
   export SITE="https://client-site.example"
   export WP_USER="editor@client.example"
   export WP_APP_PASSWORD="xxxx xxxx xxxx xxxx xxxx xxxx"
   ```
5. **Never** paste `$WP_APP_PASSWORD`'s value into chat, logs, commit messages, or any file.
   Every example on this page writes the literal string `$WP_APP_PASSWORD` — substitute the
   real value only in your shell, and unset it when you're done:
   ```bash
   unset WP_APP_PASSWORD
   ```

Verified: `wp_is_application_passwords_available()` returned `true` on the local test site
without any config changes (LocalWP already reports `WP_ENVIRONMENT_TYPE=local`). If it
returns `false` on a site you control (never on a client's live site), the local-only escape
hatch is `wp config set WP_ENVIRONMENT_TYPE local --type=constant`.

## 2. Upload images

Two calls: upload the binary, then set `alt_text` (the REST create endpoint doesn't accept
`alt_text` in the same request body as the binary upload).

```bash
curl -s -u "$WP_USER:$WP_APP_PASSWORD" \
  -H 'Content-Disposition: attachment; filename="hero.jpg"' \
  -H 'Content-Type: image/jpeg' \
  --data-binary @hero.jpg \
  "$SITE/wp-json/wp/v2/media"
```

Response includes `id` and `source_url`:

```json
{"id": 26, "source_url": "http://divi-test.local/wp-content/uploads/2026/09/hero.jpg", "mime_type": "image/jpeg", ...}
```

Then set alt text as a second call:

```bash
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"alt_text": "Plumber repairing a burst pipe"}' \
  "$SITE/wp-json/wp/v2/media/26"
```

Use the returned `source_url` verbatim as the module's `src`/`background_image` attribute
value in the shortcode:

```
[et_pb_image src="http://divi-test.local/wp-content/uploads/2026/09/hero.jpg" alt="Plumber repairing a burst pipe" ...][/et_pb_image]
```

## 3. Create a draft

```bash
python3 -c 'import json; print(json.dumps({
  "title": "Emergency Plumber in Miami",
  "status": "draft",
  "content": open("page.txt").read(),
  "meta": {"_et_pb_use_builder": "on"}
}))' > body.json

curl -s -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d @body.json "$SITE/wp-json/wp/v2/pages"
```

- `content` is the raw Divi shortcode string (see `page-format.md`) — send it as plain text in
  the JSON `content` field, **not** wrapped or escaped beyond normal JSON string encoding.
  Verified byte-for-byte round trip: `content.raw` read back via `GET ?context=edit`
  matched the sent file exactly, for both a plain-ASCII fixture and one full of curly quotes,
  an em dash, and an emoji (`tests/fixtures/valid/unicode.txt`) — WordPress does not
  re-escape or texturize `post_content` on write or on the `context=edit` read.
- `meta._et_pb_use_builder: "on"` is **required** — without it Divi's PHP treats the page as
  a plain (non-builder) page (`wpautop` may run on the content, and the sidebar layout rules
  differ — see the layout note below). It round-trips as `"on"` in the response's `meta`
  object.

**Layout — no sidebar / full width.** A page created this way (`_et_pb_use_builder = "on"`,
regular `page` post type) already renders with Divi's `et_no_sidebar` body class
automatically — this is forced by Divi's own `et_divi_sidebar_class()` for any builder-active
Page, regardless of anything else. **You do not need to set anything for this.** In
particular, do **not** bother with `_et_pb_page_layout` meta — it is not a registered REST
meta field (it never appears in the REST `meta` object, and a REST `POST` targeting it is
silently ignored, no error), and even set directly in the database via WP-CLI it makes no
observable difference on a builder-active Page.

If you also want to remove the site's header, primary nav, and footer widgets entirely (a
true blank canvas, e.g. a landing page supplying its own header section), set the `template`
field — this is the one REST-settable field that actually changes the rendered layout:

```json
{"template": "page-template-blank.php"}
```

Verified: setting this dropped `et_fixed_nav`, `et_show_nav`, `et_header_style_left`, and
`et_pb_footer_columns4` from the rendered body class, alongside the pre-existing
`et_no_sidebar`. This is publish.py's `--page-fields` default recommendation for a full-bleed
landing page; omit it for a normal page that should keep the site's header/nav/footer.

(`_et_pb_page_layout` *does* affect rendering on a **non-builder** page, but there both
`et_no_sidebar` and `et_full_width_page` meta values render the identical
`et_full_width_page` body class — Divi renames `et_no_sidebar` to `et_full_width_page` for
any post type that isn't one of its own custom post types. This case shouldn't come up for a
skill-authored page, which always sets `_et_pb_use_builder`.)

## 4. Preview

The create/update response's `link` field plus `&preview=true` is the built-in WordPress
preview URL for a draft, visible only to a logged-in user with edit rights on that post (it
needs a browser session cookie — `curl` alone can't view it without also authenticating the
cookie-based session, which Application Passwords don't provide).

```
http://divi-test.local/?page_id=15&preview=true
```

**The WordPress draft, opened in a real logged-in browser tab, is the authoritative visual
check** — not a local shortcode renderer. Divi's actual PHP renders the shortcode tree,
applies the theme's CSS, and reflects any real site customizations (Divi Theme Options,
active plugins, global presets) that a local preview tool cannot fully replicate.

## 5. Publish

Flip `status` to `publish`, either at creation or as an update to an existing draft:

```bash
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d '{"status": "publish"}' \
  "$SITE/wp-json/wp/v2/pages/15"
```

The response's `link` field becomes the page's real permalink
(`http://divi-test.local/plan-test-rest-create/` in testing, rather than the `?page_id=`
form used for unpublished content). Loading that permalink the first time after publish
triggers Divi to generate its `et-cache` CSS for the page (see the cache section below) —
there is no separate "build" or "compile" step to call.

## 6. Edit an existing page

Always fetch the current authoritative content before editing, so you can diff against it and
avoid clobbering changes made in the WordPress admin since your last publish:

```bash
curl -s -u "$WP_USER:$WP_APP_PASSWORD" "$SITE/wp-json/wp/v2/pages/15?context=edit" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["content"]["raw"], end="")' \
  > original.txt

# edit a copy, then validate the edit against the original as a baseline
python3 Skill/divi-page-builder/scripts/validate.py edited.txt --baseline original.txt

# push the update
python3 -c 'import json; print(json.dumps({"content": open("edited.txt").read()}))' > update.json
curl -s -X POST -u "$WP_USER:$WP_APP_PASSWORD" -H 'Content-Type: application/json' \
  -d @update.json "$SITE/wp-json/wp/v2/pages/15"
```

`--context=edit` is required to get the raw (unfiltered) `content.raw` — a plain `GET` without
it returns `content.rendered`, which has already been through `do_shortcode()` and is
**not** valid shortcode to feed back in.

**Decision point on `validate.py --baseline`'s exit status.** `--baseline original.txt` tells
`validate.py` to only fail on findings that are *new* relative to the original page — anything
already present in `original.txt` (a pre-existing warning/error on the live page, not
introduced by this edit) does not block. Concretely:
- **Exit 1** (new errors, not present in the baseline) — **stop, fix the edit, and do not
  `POST`** until it exits 0.
- **Exit 0** — safe to `POST`, even if `validate.py` still reports pre-existing findings that
  were already there in `original.txt`; those aren't your edit's fault and don't block the
  update.

You only need to send the fields you're changing — a `POST` update with just `{"content":
...}` leaves title, status, template, and everything else untouched.

## 7. CSS cache behavior

Divi caches per-page CSS under `wp-content/et-cache/<page-id>/` (5 files:
`et-core-unified-<id>.min.css`, `et-core-unified-deferred-<id>.min.css`,
`et-divi-dynamic-<id>-critical.css`, `et-divi-dynamic-<id>-late.css`, `et-divi-dynamic-<id>.css`).

**Verified: a REST `content` update deletes the page's entire `et-cache/<id>/` directory
synchronously, as part of the save** — not a lazy invalidation, not a partial touch. The very
next front-end page load regenerates all 5 files from scratch and reflects the new content
immediately. **No manual cache-purge call is needed after a REST update** — this is handled
by WordPress/Divi's own save hooks the same as an edit made in the block editor or Divi
Builder UI.

## 8. Troubleshooting

**401 Unauthorized.** Wrong username/password, or Application Passwords disabled (see
Auth above). Typical bodies:

```json
{"code":"rest_forbidden_context","message":"Sorry, you are not allowed to edit posts in this post type.","data":{"status":401}}
{"code":"rest_cannot_create","message":"Sorry, you are not allowed to create posts as this user.","data":{"status":401}}
```

Note that a plain `GET /wp/v2/pages` (no `context=edit`) succeeds with `200` even with no/bad
credentials — it just returns the public page list. Auth is only enforced on routes that
need elevated access: `context=edit`, creating, updating, deleting, or reading unpublished
content.

**403 Forbidden, `rest_cannot_edit`.** The credentials are valid, but that WordPress user
lacks `edit_post` capability on the specific page being targeted (for example, a Contributor
account trying to edit a page it doesn't own, or trying to publish without `publish_pages`).
Fix by using an account with sufficient capability (Editor or Administrator) for content
management, or granting the specific capability needed.

**Content altered on save.** In testing, `content.raw` round-tripped byte-for-byte through
REST for both a plain-ASCII fixture and a fixture containing curly quotes, an em dash, an
emoji, and already-percent-encoded escape sequences (`%22`, `%91`, `%93`, `%92`, `%5c`) inside
a `custom_css_*` attribute — none of it was altered by WordPress on write or read. If you
*do* see altered characters (most commonly this would be a raw `<` inside an attribute
desyncing `wptexturize()`, or unescaped `"`/`[`/`]` breaking attribute parsing — see the
escaping table in `page-format.md`), diff `content.raw` against what you sent with
`difflib.unified_diff` and check the offending page against `page-format.md`'s escaping rules
before re-sending.

## Reference: request/response shapes seen in testing

Create (`POST /wp/v2/pages`):
```json
{"title": "Plan Test: REST create", "status": "draft", "content": "<shortcode text>", "meta": {"_et_pb_use_builder": "on"}}
```

Read for editing (`GET /wp/v2/pages/<id>?context=edit`) — relevant fields:
```json
{"id": 15, "status": "draft", "content": {"raw": "<shortcode text>", "rendered": "<... do_shortcode output ...>"}, "meta": {"_et_pb_use_builder": "on", ...}, "link": "http://divi-test.local/?page_id=15"}
```

Update (`POST /wp/v2/pages/<id>`), any subset of fields:
```json
{"content": "<new shortcode text>"}
{"status": "publish"}
{"template": "page-template-blank.php"}
```

Delete (`DELETE /wp/v2/pages/<id>?force=true`) — bypasses trash, used for cleanup in testing.
