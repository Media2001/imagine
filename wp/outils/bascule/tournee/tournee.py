#!/usr/bin/env python3
"""A32: closed read-only inventory orchestration; never bootstraps WordPress."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def documented_commands(path):
    text = path.read_text(encoding='utf-8').replace('\\\n', '')
    return [' '.join(shlex.split(line)) for line in text.splitlines()
            if line.startswith(('php ', 'python3 '))]


def entries():
    values = [json.loads(line) for line in (HERE / 'outils.jsonl').read_text(encoding='utf-8').splitlines() if line]
    if len({v['lot'] for v in values}) != len(values):
        raise RuntimeError('A32_LIST_INVALID')
    for value in values:
        if (set(value) != {'lot', 'readme', 'command', 'success', 'files'}
                or not re.fullmatch(r'A[0-9]{2}', value['lot'])
                or value['command'] not in documented_commands(ROOT / value['readme'])):
            raise RuntimeError('A32_DOCUMENTED_COMMAND_DRIFT')
    return values


def command(entry, site, audit, mapping, output):
    args = shlex.split(entry['command'])
    # Preserve interpreters, option order, flags and every non-path literal.
    relative = args[1][args[1].index('wp/outils/bascule/'):]
    args[1] = str(ROOT / relative)
    paths = {'--wp-path': site, '--audit': audit, '--correspondance': mapping, '--output': output}
    return [part.split('=', 1)[0] + '=' + str(paths[part.split('=', 1)[0]])
            if '=' in part and part.split('=', 1)[0] in paths else part for part in args]


def allowed_messages():
    guard = load('a32_guard_codes', HERE.parent / 'stream_guard.py')
    messages = set(guard.allowed_messages())
    messages.update(json.loads((HERE / 'refusals.json').read_text(encoding='utf-8')))
    return messages


def classify(entry, code, stdout, stderr, output):
    if (type(code) is int and code == 0 and stdout == entry['success'].encode('ascii') and stderr == b''
            and output.is_dir() and not output.is_symlink()
            and {p.name for p in output.iterdir()} == set(entry['files'])
            and all(p.is_file() and not p.is_symlink() and 0 < p.stat().st_size <= 16777216 for p in output.iterdir())):
        return {'outil': entry['lot'], 'statut': 'réussi', 'rapport': str(output)}
    closed = {(s + '\n').encode('ascii'): s.split(' ', 1)[0] for s in allowed_messages()}
    if code == 1 and stdout == b'' and stderr in closed:
        return {'outil': entry['lot'], 'statut': 'refusé', 'code': closed[stderr], 'rapport': str(output)}
    return {'outil': entry['lot'], 'statut': 'en échec', 'sortie': code if type(code) is int else 1, 'rapport': str(output)}


def run(site, audit, mapping, output, executor=None):
    listing = entries()
    site = Path(site).resolve(strict=True)
    audit = Path(audit).resolve(strict=True)
    mapping = Path(mapping).resolve(strict=True)
    output = Path(output)
    parent = output.parent.resolve(strict=True)
    output = parent / output.name
    if (not re.fullmatch('[A-Za-z0-9_-]+', output.name) or output.exists() or output.is_symlink()
            or str(parent) == parent.anchor
            or any(parent == root or parent in root.parents or root in parent.parents for root in (site, ROOT))
            or audit.parent.parent != parent):
        raise RuntimeError('A32_OUTPUT_UNSAFE')
    targets = [parent / (output.name + '-' + entry['lot'].lower()) for entry in listing]
    if any(p.exists() or p.is_symlink() for p in targets):
        raise RuntimeError('A32_OUTPUT_EXISTS')
    guard = load('a32_guard', HERE.parent / 'stream_guard.py')
    if executor is None:
        def executor(args):
            return guard.supervise(args, {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                                         'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'},
                                   parent, None, timeout=180)
    output.mkdir(mode=0o700)
    rows = []
    def publish(complete):
        document = {'tournee': 'complète' if complete else 'partielle', 'outils': rows}
        text = '# Tournée des inventaires — ' + document['tournee'] + '\n\n'
        for row in rows:
            detail = row.get('code', str(row['sortie']) if 'sortie' in row else '')
            text += row['outil'] + ' : ' + row['statut'] + (' (' + detail + ')' if detail else '') + ' — ' + row['rapport'] + '\n'
        for filename, payload in [('bilan.json', json.dumps(document, ensure_ascii=True, indent=2) + '\n'), ('bilan.md', text)]:
            path = output / filename
            path.write_text(payload, encoding='utf-8')
            path.chmod(0o600)
    publish(False)
    for entry, target in zip(listing, targets):
        try:
            code, stdout, stderr = executor(command(entry, site, audit, mapping, target))
            row = classify(entry, code, stdout, stderr, target)
        except Exception:
            row = {'outil': entry['lot'], 'statut': 'en échec', 'sortie': 1, 'rapport': str(target)}
        rows.append(row)
        publish(False)
    publish(True)
    return int(any(row['statut'] != 'réussi' for row in rows))


def main():
    try:
        options = {}
        for arg in sys.argv[1:]:
            key, sep, value = arg.partition('=')
            if not sep or not value or key not in {'--wp-path', '--audit', '--correspondance', '--output'} or key in options:
                raise RuntimeError('A32_USAGE')
            options[key] = value
        if len(options) != 4:
            raise RuntimeError('A32_USAGE')
        code = run(*(options[k] for k in ('--wp-path', '--audit', '--correspondance', '--output')))
        print('A32_COMPLETE bilan.json bilan.md')
        return code
    except Exception as error:
        known = {'A32_USAGE', 'A32_LIST_INVALID', 'A32_DOCUMENTED_COMMAND_DRIFT', 'A32_OUTPUT_UNSAFE', 'A32_OUTPUT_EXISTS'}
        print(str(error) if isinstance(error, RuntimeError) and str(error) in known else 'A32_FAILED', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
