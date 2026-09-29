# Divi 5 support: final verification (Task 22)

Run 2026-09-29 on branch `divi5-support` (base `6397768`), macOS, Python 3.10.0, Node v24.1.0.
Sites: `http://divi-test.local` (Divi 4.27.9) and `http://divi-5-test.local` (Divi 5.13.1, LocalWP id `fTZ3hcgdI`).
Live runs used `SSL_CERT_FILE=/etc/ssl/cert.pem`. Every command runs from the repo root.

The whole-branch code review is recorded separately (done by the controller).

## 1. Offline suite

```
python3 -m unittest discover -s tests
```

| Run | Summary |
|---|---|
| before the fixes below | `Ran 914 tests in 65.3s` / `OK (skipped=34, expected failures=1)` |
| final (with the fixes) | `Ran 916 tests in 70.3s` / `OK (skipped=36, expected failures=1)` |

- All 36 skips are live gates (`live test: touches the local ... set PP_LIVE_TESTS=1 ...`): 31 Divi 5 site,
  5 Divi 4 site. No other skip.
- The one expected failure is by design: `test_render5_fidelity` "The binding gate of Task 21-R5b, on the pre-fix
  engine" (the parked Divi 5 Python renderer missed its gate; see `render-fidelity.md`).

## 2. Live suite (both sites)

Chunks first (before the fixes), then the full run twice.

```
PP_LIVE_TESTS=1 SSL_CERT_FILE=/etc/ssl/cert.pem python3 -m unittest discover -s tests -p <pattern> -v
```

| Pattern | Summary |
|---|---|
| `test_*judge*.py` | `Ran 7 tests in 25.1s` / `OK` |
| `test_publish*.py` | `Ran 79 tests in 9.8s` / `OK` |
| `test_divi5_*live*.py` | `Ran 4 tests in 35.0s` / `OK` |
| `test_*tokens_fidelity*.py` | `Ran 10 tests in 11.9s` / `OK` |
| `test_preview*.py` | `Ran 111 tests in 107.0s` / `OK (skipped=1)`: the skip was `page 11 not reachable` (bug 1 below) |
| `test_render*.py` | `Ran 48 tests in 2.0s` / `OK (expected failures=1)` |

```
PP_LIVE_TESTS=1 SSL_CERT_FILE=/etc/ssl/cert.pem python3 -m unittest discover -s tests -v
```

| Run | Summary |
|---|---|
| full, before the fixes | `Ran 914 tests in 214.5s` / `OK (skipped=2, expected failures=1)` |
| full, final | `Ran 916 tests in 213.2s` / `OK (skipped=2, expected failures=1)` |

The 2 live-mode skips are `test_live_gating`'s two checks that only apply when the flag is off
(`live tests enabled; gating not in effect`); both ran and passed in the offline run. The expected failure is the
parked renderer gate (above).

Every live-gated test ran and passed in the final run:

- **Divi 4 site (5):** `test_publish.PublishLiveTest.test_draft_roundtrip_on_local_site`,
  `test_divi_judge.DiviJudgeTest.test_parse_agrees_with_divi`, `test_tokens_fidelity.TokensFidelityTest.test_round_trip_through_wordpress`,
  `test_preview.PreviewTest.test_page11_builder_css_matches_live`, `test_preview.PreviewTest.test_no_credentials_in_output`.
- **Divi 5 site (31):** `test_divi5_judge.DiviJudge5Test` (5: every fixture renders, tree/attrs agree,
  canonical JSON, invalid-input verdicts, rare values), `test_divi5_publish_live.Divi5PublishLiveTest` (4),
  `test_divi5_tokens_fidelity.Divi5TokensFidelityTest` (10), `test_preview.Divi5PreviewParityTest` (3),
  `test_preview.Divi5SeedOptionsTest` (6), `test_preview` warm-Playground serve across page switches and edits (1),
  `test_divi5_schema.Schema5DumpLiveTest` (2, new: bug 2 below).

No environmental flakes: nothing needed a re-run.

## 3. Regeneration

```
python3 research/tools/divi5/build_schema5.py research/divi5-schema research/tools/divi5/families5.json Skill/divi-page-builder/scripts/schema5
python3 research/tools/divi5/generate_docs5.py research/divi5-schema Skill/divi-page-builder --notes research/tools/divi5/notes   # wrote 64 module pages, 40 families
python3 research/tools/build_schema.py research/divi-schema research/tools/extras.json Skill/divi-page-builder/scripts/schema   # wrote 64 modules + _meta.json
python3 research/tools/generate_docs.py research/divi-schema Skill/divi-page-builder --notes research/tools/notes             # wrote 64 module pages, 19 families
git diff --exit-code -- Skill research   # exit 0: empty
```

Live re-dumps into a temp dir, diffed against the committed dumps:

- **Divi 5:** `LOCAL_SITE_ID=fTZ3hcgdI LOCAL_SITE_PATH=... research/tools/wp-local.sh --exec='$_SERVER["REQUEST_URI"]="/wp-json/";' eval-file research/tools/divi5/dump-schema.php <tmp>`
  then `diff -r research/divi5-schema <tmp>`: **identical** (118 files). The first attempt, with the command as
  written in `research/tools/README.md` (no `--exec`), differed in 87 files: bug 2 below. Now also a live test.
- **Divi 4:** `research/tools/wp-local.sh --require=research/tools/force-all-modules.php eval-file research/tools/dump-divi-schema.php <tmp>`
  then `diff -r research/divi-schema <tmp>`: 65 files, the only difference is `index.json`'s `generated` timestamp
  (the Divi 4 dump records its run time by design).

## 4. Doc examples

```
python3 research/tools/check_doc_examples.py Skill/divi-page-builder
```

`105 Divi 4 and 122 Divi 5 example(s) checked` / `0 failing block(s)`, exit 0.

## 5. Credential scan

```
git grep -nE "api_key=|Basic [A-Za-z0-9+/=]{20,}|WP_APP_PASSWORD=[^ \"$]"
```

24 hits before this file (it adds 3 more: the command and the placeholders quoted here), none sensitive: `api_key=K` / `api_key=<API_KEY>` / `api_key=…` placeholders in endpoint docs
(`fetch_divi.py`, `fetch-divi.mjs` and its two prototypes, `playground-spike.md`, the plans/specs), and
`WP_APP_PASSWORD=<python variable>` in tests, the plan and `d5_tokens_probe.py` usage (`WP_APP_PASSWORD=...`).
The one literal test password is the fake `"abcd EFGH ijkl MNOP qrst UVWX"` (`tests/test_publish.py`). No `Basic` header.

Value scan: every credential value (and, for the rest, every string of 6+ characters) in `/Volumes/Content/projects/TFM/Test/keys.json` (read in Python, never
printed) searched in all tracked files, in `git log -p main..HEAD` (re-run after the commits below) and in `git log -p --all`:

| keys.json field | tracked files | `main..HEAD` history | all history |
|---|---|---|---|
| `elegant_themes.username` | 0 | 0 | 0 |
| `elegant_themes.api_key` | 0 | 0 | 0 |
| `keys[0].key`, `keys[1].key` (Application Passwords) | 0 | 0 | 0 |
| `keys[1].user`, `keys[1].name`, `keys[1].site` | 0 | 0 | 0 |
| `keys[0].name`, `keys[0].site` (not secrets: a label and the local site URL) | 4 / 69 | 0 / 0 | 9 / 88 |
| `keys[0].user` (not a secret: a 4-letter local WordPress login that is also a common English word) | many | 286 | many |

`python3 -m unittest test_no_divi_assets` (from `tests/`): `Ran 2 tests` / `OK` (no Divi zip, no Divi stylesheet
markers in tracked files).

## 6. Sites left clean

Snapshot before any live run and after the final one, on both sites (`wp eval-file` printing every non-transient
option name + md5 of its value, every post except revisions/changesets/oembed with type, status and title, every
Application Password per user, and the postmeta row count):

- **Divi 4:** `diff` of the snapshots: **identical** (options, posts, the one pre-existing Application Password
  `divi-page-builder`, 20 postmeta rows).
- **Divi 5:** identical except `_et_builder_da_feature_cache` and `_et_builder_gf_feature_cache` are gone. These are
  Divi's own per-post feature caches: Divi deletes them when design data or posts change and the next front-end
  request rebuilds them (verified: one `curl` of the home page recreated both). `fidelity_setup.php` documents the
  same. `et_divi`, `et_divi_builder_global_presets_d5` and every other option are byte-identical (same md5); no
  `D5TEST*` post in any status (`wp post list --post_type=any --post_status=any --s=D5TEST`: 0), no trashed pages or
  posts, no Application Password on any user; no new file under `wp-content/uploads` (outside `et-cache`).
- No Playground process left running; no `pp-*` dir in `$TMPDIR` or `/tmp`. The runs here created none. 324 stale
  `pp-bp-*` dirs (only a `blueprint.json` each, dated 2026-09-28 and 2026-09-29 before 06:42, i.e. from earlier
  tasks) were deleted; `test_preview.Divi5SeedOptionsTest.test_renders_leave_no_temp_dirs` passes on the current code.

## 7. Bugs found and fixed

1. **`test_page11_builder_css_matches_live` silently skipped.** Page 11 is the Divi 4 site's static front page
   (`page_on_front=11`), so WordPress 301s its slug URL to `/`; the test's `curl -s` got an empty body and skipped
   with "page 11 not reachable" although the site was up. Fix: `curl -sL` (`tests/test_preview.py`). Red: skipped;
   green: passes (Divi 4 builder CSS of the Playground render matches the live page's).
2. **`dump-schema.php` produced a wrong Divi 5 dump from the documented command.** `research/tools/README.md` step 1
   and the root `README.md` omitted the `--exec='$_SERVER["REQUEST_URI"]="/wp-json/";'` that makes Divi register
   every module (the script's own header and `schema.md` had it). Without it the script "succeeded" with every core
   module `registered:false`, after deleting the previous dump (87 of 118 files differed). Fix: the script now
   refuses (`WP_CLI::error`, naming the `--exec`) when `divi/section` is not registered, before touching the output
   dir; both READMEs show the full command. Regression tests (live, `tests/test_divi5_schema.py`
   `Schema5DumpLiveTest`): without `--exec` the dump exits non-zero, mentions `REQUEST_URI` and keeps the old dump
   (red before the fix: exit 0 and the old file deleted); with it the dump reproduces `research/divi5-schema`
   byte for byte.
