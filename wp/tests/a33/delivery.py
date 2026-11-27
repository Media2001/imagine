"""A33 packet contract. Pure read-only validation; no subprocess or site access."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
BASE = 'production/A-33'
OWN = ['wp/outils/bascule/a33', 'wp/tests/a33', BASE]
EXCLUDE = {BASE + '/manifest.json', BASE + '/PRET'}
PREVIOUS = {'A-20', 'A-21', 'A-22', 'A-23', 'A-24', 'A-25', 'A-26', 'A-27', 'A-28', 'A-30', 'A-31', 'A-32'}
REQUIRED_NATIVE = {'native_audit', 'native_success', 'twelve_selects_ten_exact', 'published_outside_exact_closed_types_years', 'outside_files_exact_years_missing_not_zero', 'orphan_zero_and_missing_parent', 'recent_comparison_exact', 'nonpublished_parent_separate', 'no_media_content_open_or_access', 'no_site_identifiers_all_nominal_channels', 'db_identical_nominal', 'files_identical_nominal', 'deterministic_replay', 'common_and_owned_readme_commands_identical', 'readme_only_exact_arguments', 'a16_variant_parent_exact', 'a16_variant_taxonomy_ten_no_term_post_id_inference', 'symlink_closed_refusal', 'all_base_tables_and_scheduler_unchanged', 'all_site_files_unchanged', 'imported_excluded_unknown_not_zero', 'imported_readable_local_counts_unchanged', 'imported_db_files_identical', 'no_network_interfaces'}
REQUIRED_NATIVE |= {'same_a16_refusal_' + f for f in ('numero_type', 'thematique', 'pdf_cle', 'liaison.cle', 'article_type', 'date_cle')}
REQUIRED_NATIVE |= {prefix + label for prefix in ('channel_', 'immutable_channel_') for label in ('echo', 'stdout', 'stderr', 'early', 'shutdown', 'file', 'exception')}
REQUIRED_NATIVE |= {'media_watch_positive_inverse', 'no_commerce_mapping_bootstrap'} | {'output_guard_' + name for name in ('existing', 'site', 'repository', 'ancestor', 'root')}


def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(path):
    def unique(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate')
            d[k] = v
        return d
    return json.loads(path.read_bytes(), object_pairs_hook=unique)


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inventory(roots, root=ROOT, exclude=()):
    result = {}
    for name in roots:
        p = root / name
        if not p.exists() or p.is_symlink():
            raise ValueError('missing source')
        for f in ([p] if p.is_file() else p.rglob('*')):
            if f.is_symlink():
                raise ValueError('symlink')
            if f.is_file() and '__pycache__' not in f.parts:
                key = f.relative_to(root).as_posix()
                if key not in exclude:
                    result[key] = digest(f)
    return dict(sorted(result.items()))


def checks_valid(d, required=()):
    rows = d.get('checks')
    if d.get('exit_code') != 0 or type(d.get('exit_code')) is not int or type(rows) is not list or not rows:
        return False
    names = []
    for r in rows:
        if type(r) is not dict or type(r.get('check')) is not str or r.get('status') != 'PASS':
            return False
        names.append(r['check'])
    return len(names) == len(set(names)) and set(required) <= set(names)


def readme_valid(raw, contract):
    lines = raw.splitlines(keepends=True)
    owned = contract.splitlines(keepends=True)
    return len(owned) == 3 and all(lines.count(line) == 1 for line in owned)


def native_valid(folder, root=ROOT):
    runner = load('a33_delivery_runner', root / 'wp/tests/a33/run.py')
    report = load('a33_delivery_report', root / 'wp/outils/bascule/a33/report.py')
    if read(folder / 'sources.json') != inventory(runner.OWN, root) or read(folder / 'dependencies.json') != inventory(runner.DEPS, root):
        return False
    if not checks_valid(read(folder / 'runner.json'), {'unit_green', 'native_green', 'isolation_before', 'isolation_after', 'cleanup_exact_owned_container', 'owned_sources_stable', 'dependencies_stable'}):
        return False
    if not checks_valid(read(folder / 'unit.json')):
        return False
    result = read(folder / 'result.json')
    if result.get('stores') != ['classic'] or not checks_valid(result, REQUIRED_NATIVE):
        return False
    if read(folder / 'db-before.json') != read(folder / 'db-after.json') or read(folder / 'imported-db-before.json') != read(folder / 'imported-db-after.json'):
        return False
    files = read(folder / 'files.json')
    if set(files) != {'before', 'after'} or files['before'] != files['after'] or not re.fullmatch('[a-f0-9]{64}', files['before']):
        return False
    if len(read(folder / 'oracle.json')['issues']) != 12:
        return False
    nominal = folder / 'r1-nominal'
    if not report.complete_report(nominal, folder / 'audit/audit.json', root / 'wp/outils/bascule/a33/correspondance.exemple.json'):
        return False
    d = read(nominal / 'archives.json')
    expected = [{'type': 'article', 'type_group': 0, 'year': 2010, 'count': 1}, {'type': 'article', 'type_group': 0, 'year': 2011, 'count': 1}, {'type': 'autre', 'type_group': 1, 'year': 2023, 'count': 1}, {'type': 'autre', 'type_group': 2, 'year': 2023, 'count': 1}, {'type': 'numero', 'type_group': 0, 'year': 2010, 'count': 1}, {'type': 'numero', 'type_group': 0, 'year': 2011, 'count': 1}, {'type': 'post', 'type_group': 0, 'year': 2022, 'count': 1}]
    return (d['selected_issues'] == 10 and d['published_outside'] == expected
            and d['outside_media_by_year'] == [{'year': 2010, 'files': {'count': 3, 'present': 2, 'missing': 1, 'known_bytes': 18, 'total_bytes': 'inconnu fichiers absents'}}, {'year': 2011, 'files': {'count': 1, 'present': 1, 'missing': 0, 'known_bytes': 13, 'total_bytes': 13}}, {'year': 2022, 'files': {'count': 1, 'present': 1, 'missing': 0, 'known_bytes': 0, 'total_bytes': 0}}]
            and d['orphan_media'] == {'count': 2, 'present': 2, 'missing': 0, 'known_bytes': 52, 'total_bytes': 52}
            and d['recent_media'] == {'count': 2, 'present': 2, 'missing': 0, 'known_bytes': 36, 'total_bytes': 36})


def local_valid(packet, root=ROOT):
    runner = load('a33_matrix_runner', root / 'wp/tests/a33/run.py')
    matrix = read(packet / 'windows-matrix.json')
    if (matrix.get('exit_code') != 0 or matrix.get('sources_stable') is not True or matrix.get('scope') != 'python_and_native'
            or read(packet / 'sources.json') != inventory(runner.OWN, root)
            or read(packet / 'dependencies.json') != inventory(runner.DEPS, root)):
        return False
    expected_count = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test_') for f in (root / 'wp/tests/a33').glob('test_*.py') for n in ast.walk(ast.parse(f.read_text(encoding='utf-8'))))
    expected_rows = [('python', 'utf-8'), ('native', 'utf-8'), ('python', 'cp1252'), ('native', 'cp1252'), ('style', 'utf-8')]
    rows = matrix.get('rows')
    if type(rows) is not list or [(r.get('kind'), r.get('console')) for r in rows] != expected_rows:
        return False
    for row in rows:
        log = packet / row['log']
        if row['exit_code'] != 0 or digest(log) != row['log_sha256']:
            return False
        if row['kind'] == 'python':
            text = log.read_text(encoding='utf-8')
            if row.get('all_pass') is not True or row.get('tests_run') != expected_count or not re.search(r'Ran ' + str(expected_count) + r' tests? in ', text) or 'OK' not in text.splitlines():
                return False
    for console, encoding, mode in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
        env = read(packet / console / 'environment.json')
        if env.get('platform') != 'win32' or env.get('stdout') != encoding or env.get('stderr') != encoding or env.get('utf8_mode') != mode or env.get('tmpdir') is not None or not env.get('version'):
            return False
        if not native_valid(packet / console / 'native', root):
            return False
    style = read(packet / 'style/style.json')
    return (checks_valid(style, {'strict_psr12', 'cleanup_exact_owned_container'})
            and style.get('totals', {}).get('errors') == 0 and style.get('totals', {}).get('warnings') == 0
            and style.get('sources') == inventory(runner.OWN, root))


def global_result(text):
    rows = [json.loads(x[len('T01_RESULT '):]) for x in text.splitlines() if x.startswith('T01_RESULT ')]
    if len(rows) != 1:
        raise ValueError('global result')
    return rows[0]


def global_valid(d, require_self=False):
    if d.get('pass') is not True or any(d.get(k) != 0 for k in ('failures', 'errors', 'skipped')) or not d.get('tests'):
        return False
    t, p = d.get('tools', {}), d.get('packets', {})
    lots = p.get('lots', [])
    return (t.get('tools', 0) >= 23 and t.get('checks', 0) >= 852 and t.get('failures') == 0 and t.get('excluded') == []
            and p.get('failures') == [] and p.get('excluded') == [] and p.get('verified') == len(lots)
            and len(lots) == len(set(lots)) and PREVIOUS <= set(lots) and (not require_self or 'A-33' in lots))


def gates_valid(folder, require_self=False, root=ROOT):
    runner = load('a33_gate_snapshot', root / 'wp/tests/a33/run.py')
    if read(folder / 'sources.json') != inventory(runner.OWN + runner.DEPS, root):
        return False
    rows = read(folder / 'commands.json')
    if [r.get('name') for r in rows] != ['prepare-image', 'global-utf8', 'global-cp1252']:
        return False
    for row in rows:
        script = 'wp/tests/preparer-image.ps1' if row['name'] == 'prepare-image' else 'wp/tests/rejouer.ps1'
        if row.get('command') != ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script]:
            return False
        if row.get('encoding') != ('cp1252' if row['name'] == 'global-cp1252' else 'utf-8'):
            return False
        if row.get('exit_code') != 0 or row.get('tmpdir_present') is not False or row.get('sources_stable') is not True:
            return False
        for stream in ('stdout', 'stderr'):
            if digest(folder / row[stream]) != row[stream + '_sha256']:
                return False
        text = (folder / row['stdout']).read_text(encoding='utf-8')
        if row['name'].startswith('global-') and not global_valid(global_result(text), require_self):
            return False
    return read(folder / 'result.json').get('exit_code') == 0


def verify(root=ROOT):
    base = root / BASE
    manifest = read(base / 'manifest.json')
    if manifest.get('lot') != 'A-33' or manifest.get('files') != inventory(OWN, root, EXCLUDE):
        return 'A33_PACKAGE_DRIFT'
    if not readme_valid((root / 'wp/outils/bascule/README.md').read_bytes(), (base / 'readme-ajout.txt').read_bytes()):
        return 'A33_README_CONTRACT_DRIFT'
    packet = base / 'preuves/final'
    if not local_valid(packet, root):
        return 'A33_PARTIAL_EVIDENCE'
    if not gates_valid(packet / 'gates', (base / 'PRET').exists(), root):
        return 'A33_GATES_INVALID'
    return None
