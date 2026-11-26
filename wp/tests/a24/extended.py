"""A24 exact native assertions, operator path and real neutralisation."""
import copy
import importlib.util
import json
from pathlib import Path
import re
import shlex

OUT = Path('/report')
FIELDS = ['first_name', 'last_name', 'company', 'country', 'address_1', 'address_2', 'city', 'state', 'postcode', 'phone']
UNKNOWN = 'inconnu après neutralisation'


def metrics(n=0, empty=0, missing=0, absent=0, invalid=0, different=0, unavailable=0, fields=None):
    return {'subscriptions': n, 'shipping_empty': empty, 'empty_with_billing': empty,
            'missing_any': missing, 'missing_required': {'shipping_' + field: (fields or {}).get(field, 0) for field in FIELDS},
            'country_absent': absent, 'country_unknown': invalid,
            'different_from_account': different, 'account_unavailable': unavailable}


def clean():
    return not any(b'CANARY' in f.read_bytes() for f in OUT.rglob('*') if f.is_file())


def exercise(b, cmd, inventory, site, db, storage, audit, dest, cfg, base_mu, before, files):
    def check(key, ok, detail=None):
        b.check(storage + ':' + key, ok, detail)

    grants = b.sql('information_schema', "SELECT PRIVILEGE_TYPE FROM SCHEMA_PRIVILEGES WHERE GRANTEE=\"'a02_" + storage + "'@'localhost'\" AND TABLE_SCHEMA='" + db + "'")
    check('select_only_account', grants.stdout.splitlines() == ['PRIVILEGE_TYPE', 'SELECT'])
    d = json.loads((dest / 'expedition.json').read_text(encoding='utf-8'))
    required = {'first_name': 1, 'last_name': 1, 'country': 2, 'address_1': 1, 'city': 1, 'state': 2, 'postcode': 2}
    expected = {'overall': metrics(12, 1, 5, 2, 1, 2, 1, required), 'countries': [
        {'country': 'BE', 'counts': metrics(6, different=2, unavailable=1)},
        {'country': 'autres pays', 'counts': metrics(6, 1, 5, 2, 1, fields=required)}]}
    check('exact_all_metrics_and_country_groups', d['counts'] == expected)
    payload = ''.join(f.read_text(encoding='utf-8') for f in dest.iterdir())
    check('all_private_values_absent', not re.search(r'CANARY|@|/scratch|a24-fictif|1000|Ville inventee|Exemple invente|ZZ', payload))
    check('private_report_permissions', dest.stat().st_mode & 0o777 == 0o700
          and all(f.stat().st_mode & 0o777 == 0o600 for f in dest.iterdir()))
    repeat = OUT / (storage + '-repeat')
    q = inventory(site, repeat, audit)
    check('replay_identical', q.returncode == 0 and q.stderr == '' and
          {f.name: f.read_bytes() for f in dest.iterdir()} == {f.name: f.read_bytes() for f in repeat.iterdir()})
    line = next(x for x in Path('/subject/a24/README.md').read_text(encoding='utf-8').splitlines()
                if x.startswith('python3 wp/outils/bascule/a24/confine.py '))
    documented = OUT / (storage + '-documented')
    substitutions = {'wp/outils/bascule/a24/confine.py': '/subject/a24/confine.py',
                     '--wp-path=/copie-verifiee': '--wp-path=' + str(site),
                     '--audit=/hors-web/audit-date/audit.json': '--audit=' + str(audit),
                     '--output=/hors-web/expedition-date': '--output=' + str(documented)}
    command = [substitutions.get(x, x) for x in shlex.split(line)]
    q = cmd(command, check=False)
    check('documented_only_given_arguments', len(command) == 5 and (q.returncode, q.stdout, q.stderr)
          == (0, 'A24_OK expedition.json expedition.md\n', '')
          and (documented / 'expedition.json').read_bytes() == (dest / 'expedition.json').read_bytes())
    spec = importlib.util.spec_from_file_location('a24_boundaries', '/opt/a24/boundaries.py')
    boundary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(boundary)
    boundary.exercise(b, cmd, inventory, site, storage, audit, dest, cfg, base_mu, clean)
    check('all_tables_and_scheduler_identical_before_neutralisation', before == b.fingerprint(db))
    after_files = b.files(site)
    (OUT / (storage + '-files.json')).write_text(json.dumps({'before': files, 'after': after_files}), encoding='utf-8')
    check('site_files_identical_before_neutralisation', files == after_files)
    check('config_never_executed', not Path('/scratch/a02-bootstrap-trap').exists())
    clone = 'a24_' + storage + '_test'
    b.sql('mysql', 'CREATE DATABASE ' + clone)
    dump = cmd(['mariadb-dump', '--socket=' + b.SOCKET, '-uroot', db]).stdout
    cmd(['mariadb', '--socket=' + b.SOCKET, '-uroot', clone], data=dump)
    phase = cmd(['php', '/opt/a24/neutralise.php'], env={'A24_DB': clone, 'A24_STORAGE': storage})
    provenance = json.loads(phase.stdout)
    (OUT / (storage + '-neutralisation.json')).write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    check('actual_import_preserves_three_country_columns', provenance['neutraliser_and_anonymiser_executed'] is True
          and provenance['marker_count'] == 1
          and all(provenance[k + '_countries_preserved'] for k in ('shipping', 'billing', 'customer')))
    check('actual_import_erases_non_country_fields', all(value == 0 for key, value in provenance['remaining_nonempty_counts'].items()
          if not key.endswith('_country')) and provenance['changed_counts']['shipping_address_1'] >= 11)
    b.sql('mysql', "GRANT SELECT ON " + clone + ".* TO 'a02_" + storage + "'@'localhost'")
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_NAME', '" + db + "')",
                                                  "define('DB_NAME', '" + clone + "')"), encoding='utf-8')
    try:
        clone_before, clone_files = b.fingerprint(clone), b.files(site)
        neutral_audit = OUT / (storage + '-neutralised-audit')
        check('neutralised_audit', b.audit(site, neutral_audit).returncode == 0)
        neutral = OUT / (storage + '-neutralised')
        q = inventory(site, neutral, neutral_audit / 'audit.json')
        check('neutralised_success', q.returncode == 0 and q.stderr == '',
              {'exit': q.returncode, 'closed_code': q.stderr.strip() if re.fullmatch(r'A(?:24|11|12|02)_[A-Z_]+\n', q.stderr) else 'NON_CODE'})
        n = json.loads((neutral / 'expedition.json').read_text(encoding='utf-8'))
        expected_neutral = copy.deepcopy(expected)
        for section in [expected_neutral['overall'], *[g['counts'] for g in expected_neutral['countries']]]:
            for key in ('shipping_empty', 'empty_with_billing', 'missing_any', 'different_from_account'):
                section[key] = UNKNOWN
            for field in section['missing_required']:
                if field != 'shipping_country':
                    section['missing_required'][field] = UNKNOWN
        check('unknown_for_every_erased_count_country_counts_preserved', n['neutralisation'] == UNKNOWN and n['counts'] == expected_neutral)
        clone_after = b.fingerprint(clone)
        for suffix, value in [('before', clone_before), ('after', clone_after)]:
            (OUT / (storage + '-neutralised-db-' + suffix + '.json')).write_text(json.dumps(value), encoding='utf-8')
        clone_after_files = b.files(site)
        (OUT / (storage + '-neutralised-files.json')).write_text(json.dumps({'before': clone_files, 'after': clone_after_files}), encoding='utf-8')
        check('neutralised_all_tables_files_identical', clone_before == clone_after and clone_files == clone_after_files)
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    check('all_output_artifacts_clean', clean())
