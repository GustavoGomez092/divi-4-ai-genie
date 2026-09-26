import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from _paths import SCRIPTS  # noqa: F401  (puts scripts/ on sys.path via _paths)
import wp_keys
from wp_keys import KeysError, list_keys, load_keys, normalize_site, resolve_credentials, resolve_et_credentials

KEY_A = {"name": "Test Key Local site", "site": "http://divi-test.local", "user": "user",
         "key": "aaaa BBBB cccc DDDD eeee FFFF"}
KEY_B = {"name": "Client A", "site": "https://client-a.com", "user": "seo-bot",
         "key": "zzzz YYYY xxxx WWWW vvvv UUUU"}
ET = {"username": "you@example.com", "api_key": "et-secret-api-key-value"}
ALL_SECRETS = (KEY_A["key"], KEY_B["key"], ET["api_key"])


class TempKeysMixin:
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.dir = Path(self._tmpdir.name)

    def write_keys(self, entries, name="keys.json"):
        path = self.dir / name
        path.write_text(json.dumps({"keys": entries}))
        return path

    def write_object(self, obj, name="keys.json"):
        path = self.dir / name
        path.write_text(json.dumps(obj))
        return path

    def assert_no_secret_leak(self, err):
        text = str(err)
        for secret in ALL_SECRETS:
            self.assertNotIn(secret, text)


class LoadKeysTest(TempKeysMixin, unittest.TestCase):
    def test_load_valid_file(self):
        path = self.write_keys([KEY_A, KEY_B])
        entries = load_keys(path)
        self.assertEqual(entries, [KEY_A, KEY_B])

    def test_missing_file_is_keys_error(self):
        with self.assertRaises(KeysError) as ctx:
            load_keys(self.dir / "does-not-exist.json")
        self.assert_no_secret_leak(ctx.exception)

    def test_invalid_json_is_keys_error(self):
        path = self.dir / "keys.json"
        path.write_text("{not json")
        with self.assertRaises(KeysError) as ctx:
            load_keys(path)
        self.assert_no_secret_leak(ctx.exception)

    def test_top_level_must_be_object_with_keys_list(self):
        path = self.dir / "keys.json"
        path.write_text(json.dumps({"keys": "not-a-list"}))
        with self.assertRaises(KeysError) as ctx:
            load_keys(path)
        self.assert_no_secret_leak(ctx.exception)

    def test_top_level_without_keys_field_means_no_entries(self):
        # "keys" is optional (relaxed for the elegant_themes-only case); other top-level keys are
        # ignored. Only an explicitly non-list "keys" value is an error (see the test above).
        path = self.dir / "keys.json"
        path.write_text(json.dumps({"other": []}))
        self.assertEqual(load_keys(path), [])

    def test_missing_field_is_keys_error(self):
        bad = {"name": "X", "site": "https://x.example", "user": "u"}  # no key
        path = self.write_keys([bad])
        with self.assertRaises(KeysError) as ctx:
            load_keys(path)
        msg = str(ctx.exception)
        self.assertIn("0", msg)
        self.assertIn("X", msg)
        self.assert_no_secret_leak(ctx.exception)

    def test_empty_value_is_keys_error(self):
        bad = {"name": "X", "site": "", "user": "u", "key": "aaaa"}
        path = self.write_keys([bad])
        with self.assertRaises(KeysError) as ctx:
            load_keys(path)
        self.assertIn("X", str(ctx.exception))

    def test_non_string_value_is_keys_error(self):
        bad = {"name": "X", "site": 123, "user": "u", "key": "aaaa"}
        path = self.write_keys([bad])
        with self.assertRaises(KeysError):
            load_keys(path)

    def test_entry_without_name_still_named_by_index(self):
        bad = {"name": "", "site": "https://x.example", "user": "u", "key": "aaaa"}
        path = self.write_keys([bad])
        with self.assertRaises(KeysError) as ctx:
            load_keys(path)
        self.assertIn("0", str(ctx.exception))

    def test_duplicate_names_case_insensitive_is_keys_error(self):
        dup = dict(KEY_B, name="client a")
        path = self.write_keys([KEY_B, dup])
        with self.assertRaises(KeysError) as ctx:
            load_keys(path)
        msg = str(ctx.exception)
        self.assertIn("Client A", msg)
        self.assert_no_secret_leak(ctx.exception)

    @unittest.skipUnless(os.name == "posix", "POSIX file mode only")
    def test_warns_when_file_is_group_or_other_readable(self):
        path = self.write_keys([KEY_A])
        path.chmod(0o644)
        import io
        from contextlib import redirect_stderr
        buf = io.StringIO()
        with redirect_stderr(buf):
            load_keys(path)
        self.assertIn("chmod 600", buf.getvalue())
        self.assertIn(str(path), buf.getvalue())

    @unittest.skipUnless(os.name == "posix", "POSIX file mode only")
    def test_warns_once_per_path_per_process(self):
        path = self.write_keys([KEY_A], name="warn-once.json")
        path.chmod(0o644)
        import io
        from contextlib import redirect_stderr
        buf = io.StringIO()
        with redirect_stderr(buf):
            load_keys(path)
            list_keys(path)
            wp_keys.file_elegant_themes(path)
        self.assertEqual(buf.getvalue().count("chmod 600"), 1)

    def test_doctor_source_reports_keys_json_problem_without_secret(self):
        import preview
        path = self.write_object({"elegant_themes": {"username": "et-user", "api_key": ""}})
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ET_USERNAME", None)
            os.environ.pop("ET_API_KEY", None)
            source = preview.et_credential_source(str(path))
        self.assertTrue(source.startswith("none (keys.json problem:"), source)
        self.assert_no_secret_leak(source)

    @unittest.skipUnless(os.name == "posix", "POSIX file mode only")
    def test_no_warning_when_mode_is_600(self):
        path = self.write_keys([KEY_A])
        path.chmod(0o600)
        import io
        from contextlib import redirect_stderr
        buf = io.StringIO()
        with redirect_stderr(buf):
            load_keys(path)
        self.assertEqual(buf.getvalue(), "")

    @unittest.skipUnless(os.name == "posix", "POSIX file mode only")
    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root ignores file permissions")
    def test_unreadable_file_is_keys_error(self):
        path = self.write_keys([KEY_A])
        path.chmod(0o000)
        self.addCleanup(path.chmod, 0o600)
        with self.assertRaises(KeysError) as ctx:
            load_keys(path)
        self.assert_no_secret_leak(ctx.exception)


class ListKeysTest(TempKeysMixin, unittest.TestCase):
    def test_never_includes_key_field(self):
        path = self.write_keys([KEY_A, KEY_B])
        result = list_keys(path)
        self.assertEqual(result, [
            {"name": "Test Key Local site", "site": "http://divi-test.local", "user": "user"},
            {"name": "Client A", "site": "https://client-a.com", "user": "seo-bot"},
        ])
        for entry in result:
            self.assertNotIn("key", entry)

    def test_default_missing_file_returns_empty_list(self):
        # Never touches the real ~/.config/divi-page-builder/keys.json: HOME is patched to an
        # empty temp dir so the *default* path resolution is exercised safely.
        with mock.patch.dict(os.environ, {"HOME": str(self.dir)}, clear=False):
            os.environ.pop("DIVI_KEYS_FILE", None)
            self.assertEqual(list_keys(None), [])


class NormalizeSiteTest(unittest.TestCase):
    def test_lowercases_scheme_and_host_and_strips_trailing_slash(self):
        self.assertEqual(normalize_site("HTTP://Client-A.com/"), normalize_site("http://client-a.com"))

    def test_keeps_path(self):
        self.assertEqual(normalize_site("https://client-a.com/blog/"), "https://client-a.com/blog")


class ResolveCredentialsTest(TempKeysMixin, unittest.TestCase):
    def test_resolve_by_name_case_insensitive(self):
        path = self.write_keys([KEY_A, KEY_B])
        site, user, password = resolve_credentials(key_name="client a", keys_path=path)
        self.assertEqual((site, user, password), (KEY_B["site"], KEY_B["user"], KEY_B["key"]))

    def test_resolve_by_site_trailing_slash_and_case(self):
        path = self.write_keys([KEY_A, KEY_B])
        site, user, password = resolve_credentials(site="HTTPS://Client-A.com/", keys_path=path)
        self.assertEqual((site, user, password), (KEY_B["site"], KEY_B["user"], KEY_B["key"]))

    def test_two_entries_same_site_disambiguated_by_user(self):
        other = dict(KEY_B, name="Client A (dev)", user="dev-bot", key="qqqq RRRR ssss TTTT uuuu VVVV")
        path = self.write_keys([KEY_B, other])
        with self.assertRaises(KeysError) as ctx:
            resolve_credentials(site=KEY_B["site"], keys_path=path)
        msg = str(ctx.exception)
        self.assertIn("Client A", msg)
        self.assertIn("Client A (dev)", msg)
        self.assert_no_secret_leak(ctx.exception)

        site, user, password = resolve_credentials(site=KEY_B["site"], user="dev-bot", keys_path=path)
        self.assertEqual((site, user, password), (other["site"], other["user"], other["key"]))

    def test_key_with_conflicting_site_is_keys_error(self):
        path = self.write_keys([KEY_B])
        with self.assertRaises(KeysError) as ctx:
            resolve_credentials(key_name="Client A", site="https://not-client-a.example", keys_path=path)
        self.assert_no_secret_leak(ctx.exception)

    def test_unknown_key_name_lists_available_names(self):
        path = self.write_keys([KEY_A, KEY_B])
        with self.assertRaises(KeysError) as ctx:
            resolve_credentials(key_name="Nope", keys_path=path)
        msg = str(ctx.exception)
        self.assertIn(KEY_A["name"], msg)
        self.assertIn(KEY_B["name"], msg)
        self.assert_no_secret_leak(ctx.exception)

    def test_env_fallback_when_keys_file_does_not_exist(self):
        with mock.patch.dict(os.environ, {"WP_APP_PASSWORD": "env-password-value"}, clear=False):
            os.environ.pop("DIVI_KEYS_FILE", None)
            with mock.patch.dict(os.environ, {"HOME": str(self.dir)}, clear=False):
                site, user, password = resolve_credentials(site="https://client.example", user="editor",
                                                            keys_path=None)
        self.assertEqual((site, user, password), ("https://client.example", "editor", "env-password-value"))

    def test_explicit_missing_keys_path_is_keys_error(self):
        with self.assertRaises(KeysError) as ctx:
            resolve_credentials(site="https://client.example", user="editor",
                                 keys_path=self.dir / "nope.json")
        self.assert_no_secret_leak(ctx.exception)

    def test_no_credentials_at_all_is_keys_error(self):
        with mock.patch.dict(os.environ, {"WP_APP_PASSWORD": ""}, clear=False), \
                mock.patch.dict(os.environ, {"HOME": str(self.dir)}, clear=False):
            os.environ.pop("DIVI_KEYS_FILE", None)
            with self.assertRaises(KeysError) as ctx:
                resolve_credentials(keys_path=None)
        self.assertIn("WP_APP_PASSWORD", str(ctx.exception))
        self.assert_no_secret_leak(ctx.exception)


class ResolveEtCredentialsTest(TempKeysMixin, unittest.TestCase):
    def test_from_file_only(self):
        path = self.write_object({"elegant_themes": ET})
        self.assertEqual(resolve_et_credentials(path), (ET["username"], ET["api_key"]))

    def test_env_wins_over_file(self):
        path = self.write_object({"elegant_themes": ET})
        with mock.patch.dict(os.environ, {"ET_USERNAME": "env-user", "ET_API_KEY": "env-secret-key"}):
            self.assertEqual(resolve_et_credentials(path), ("env-user", "env-secret-key"))

    def test_partial_env_does_not_win(self):
        # Only ET_USERNAME set (no ET_API_KEY): per the spec, both must be set for env to win.
        path = self.write_object({"elegant_themes": ET})
        with mock.patch.dict(os.environ, {"ET_USERNAME": "env-user"}, clear=False):
            os.environ.pop("ET_API_KEY", None)
            self.assertEqual(resolve_et_credentials(path), (ET["username"], ET["api_key"]))

    def test_none_when_neither_env_nor_file_section(self):
        path = self.write_object({"keys": []})
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ET_USERNAME", None)
            os.environ.pop("ET_API_KEY", None)
            self.assertIsNone(resolve_et_credentials(path))

    def test_none_when_default_path_does_not_exist(self):
        with mock.patch.dict(os.environ, {"HOME": str(self.dir)}, clear=False):
            os.environ.pop("DIVI_KEYS_FILE", None)
            os.environ.pop("ET_USERNAME", None)
            os.environ.pop("ET_API_KEY", None)
            self.assertIsNone(resolve_et_credentials(None))

    def test_explicit_missing_path_is_keys_error(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ET_USERNAME", None)
            os.environ.pop("ET_API_KEY", None)
            with self.assertRaises(KeysError) as ctx:
                resolve_et_credentials(self.dir / "nope.json")
        self.assert_no_secret_leak(ctx.exception)

    def test_missing_api_key_is_keys_error_without_leaking(self):
        path = self.write_object({"elegant_themes": {"username": ET["username"]}})
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ET_USERNAME", None)
            os.environ.pop("ET_API_KEY", None)
            with self.assertRaises(KeysError) as ctx:
                resolve_et_credentials(path)
        self.assert_no_secret_leak(ctx.exception)

    def test_empty_username_is_keys_error(self):
        path = self.write_object({"elegant_themes": {"username": "", "api_key": ET["api_key"]}})
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ET_USERNAME", None)
            os.environ.pop("ET_API_KEY", None)
            with self.assertRaises(KeysError) as ctx:
                resolve_et_credentials(path)
        self.assert_no_secret_leak(ctx.exception)

    def test_only_elegant_themes_keeps_list_keys_empty(self):
        path = self.write_object({"elegant_themes": ET})
        self.assertEqual(list_keys(path), [])
        self.assertEqual(resolve_et_credentials(path), (ET["username"], ET["api_key"]))

    def test_only_keys_still_works_with_no_elegant_themes(self):
        path = self.write_keys([KEY_A])
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("ET_USERNAME", None)
            os.environ.pop("ET_API_KEY", None)
            self.assertIsNone(resolve_et_credentials(path))
        self.assertEqual(load_keys(path), [KEY_A])

    @unittest.skipUnless(os.name == "posix", "POSIX file mode only")
    def test_permission_warning_still_fires_for_elegant_themes_only_file(self):
        path = self.write_object({"elegant_themes": ET})
        path.chmod(0o644)
        import io
        from contextlib import redirect_stderr
        buf = io.StringIO()
        with redirect_stderr(buf):
            resolve_et_credentials(path)
        self.assertIn("chmod 600", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
