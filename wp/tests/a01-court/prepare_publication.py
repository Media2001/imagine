"""Build only invented archives in this disposable offline runner."""
import contextlib
import hashlib
import io
import json
import re
from pathlib import Path
import secrets
import sys

sys.path.insert(0, '/opt/court')
sys.path.insert(0, '/opt/e2e')
import inside as native
import inside_commercial as commercial
import struct


def write_archive(path, source, sql):
    def entry(stream, relative, value):
        parts = relative.rsplit('/', 1)
        prefix, name = parts if len(parts) == 2 else ('', parts[0])
        stream.write(struct.pack('255s14s12s4096s', name.encode(), str(len(value)).encode(), b'0', prefix.encode()))
        stream.write(value)
    with path.open('xb') as stream:
        entry(stream, 'database.sql', sql)
        version = re.search(r"^\$wp_version\s*=\s*'([^']+)';", (source / 'wp-includes/version.php').read_text(), re.M)[1]
        entry(stream, 'package.json', json.dumps({'SyntheticFixtureOnly': True, 'WordPress': {'Version': version}}).encode())
        for p in sorted((source / 'wp-content').rglob('*')):
            if p.is_file():
                entry(stream, p.relative_to(source / 'wp-content').as_posix(), p.read_bytes())
        stream.write(bytes(4377))


def main():
    storage = sys.argv[1]
    trapped = sys.argv[2] == 'trapped'
    native.isolation()
    process = native.database_start()
    # Existing fixture API behavior, with all newly seeded email addresses @example.org.
    cases = Path('/opt/e2e/cases.php')
    cases.write_text(cases.read_text().replace('@invented.invalid', '@example.org'))
    with contextlib.redirect_stdout(io.StringIO()):
        site, database, available = commercial.install(storage)
        assert all(available.values())
        commercial.case(site, 'seed')
        commercial.case(site, 'seed-subscriptions')
        before = commercial.case(site, 'snapshot')
        rights = commercial.case(site, 'rights')
    theme = site / 'wp-content/themes/a01-fiction'
    theme.mkdir()
    (theme / 'style.css').write_text('/*\nTheme Name: A01 Fiction Only\n*/\n')
    (theme / 'index.php').write_text('<?php echo "A01_FICTION_PUBLICATION_OK";')
    native.wp(site, ['theme', 'activate', 'a01-fiction'])
    native.wp(site, ['option', 'update', 'imagine_publication_setting', '{"layout":"fiction","quantity":7}', '--format=json'])
    # A retained MU canary replenishes a bogus service key only on the restored site.
    # The key exists in the archived PHP, never references a real service/account.
    if trapped:
        mu = site / 'wp-content/mu-plugins'
        mu.mkdir(exist_ok=True)
        canary = "<?php add_action('init', static function (): void { update_option('a01_fiction_residual', '" + 'sk_' + "live_A01_FICTION_NOT_A_CREDENTIAL'); });"
        (mu / 'a01-fiction-persistent-key.php').write_text(canary)
    plugins = json.loads(native.wp(site, ['option', 'get', 'active_plugins', '--format=json']).stdout)
    sql = native.command(['php', '/opt/court/export.php'], env={'E2E_DATABASE': database}).stdout.encode()
    archive = Path('/scratch/fiction.wpress')
    write_archive(archive, site, sql)
    result = {'fixture_only': True, 'storage': storage, 'trapped': trapped,
              'persistent_service_key_canary_in_archived_php': trapped,
              'versions': before['versions'], 'business': before['business'],
              'membership': before['membership'], 'rules_sha256': before['rules_sha256'],
              'rights': rights, 'plugins': plugins, 'theme': 'a01-fiction',
              'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'archive_bytes': archive.stat().st_size,
              'source_files': {p.relative_to(site / 'wp-content').as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in (site / 'wp-content').rglob('*') if p.is_file()}}
    Path('/report/fixture.json').write_text(json.dumps(result, indent=2))
    # Source DB remains alive for restore_and_verify, no TCP listener, no published service.
    print(json.dumps({'fixture_only': True, 'storage': storage, 'trapped': trapped}))


if __name__ == '__main__':
    main()
