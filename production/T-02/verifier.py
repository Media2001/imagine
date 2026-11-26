"""Read-only T02 packet verifier; PRET and parent gates are not inferred."""
import hashlib
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(text):
    markers = re.findall(r'^T01_RESULT (.+)$', text, re.M)
    require(len(markers) == 1, 'T01_RESULT absent or ambiguous')
    lines = text.splitlines()
    require(len(lines) >= 2 and lines[-2].startswith('OUTILS : '), 'OUTILS not penultimate')
    require(re.fullmatch(r'REJEU : \d+ tests, \d+ assertions, \d+ échecs, \d+ erreurs, \d+ ignorés — (PASS|FAIL)', lines[-1]), 'REJEU format changed')
    return json.loads(markers[0])


def verify(root):
    root = Path(root)
    lot = root / 'production/T-02'
    packet = lot / 'preuves/final'
    manifest = json.loads((lot / 'manifest.json').read_text(encoding='utf-8'))
    files = manifest['files']
    require(manifest['file_count'] == len(files), 'Manifest count differs')
    for name, expected in files.items():
        relative = Path(name)
        require(not relative.is_absolute() and '..' not in relative.parts, 'Invalid manifest path')
        require(name.startswith(('production/T-02/', 'wp/tests/')), 'Manifest outside T02 scope')
        require(digest(root / relative) == expected, 'Manifest hash differs: ' + name)
    notes = (root / 'production/T-01/notes.md').read_text(encoding='utf-8').splitlines()
    contexts = {}
    for mode, encoding, utf8 in [('utf8', 'utf-8', 1), ('cp1252', 'cp1252', 0)]:
        directory = packet / mode
        receipt = json.loads((directory / 'verification.json').read_text(encoding='utf-8'))
        require(receipt['correction_verified'] is True, 'Correction not verified')
        require(receipt['parent_gates_claimed'] is False and receipt['preparer_image_executed'] is False
                and receipt['pret_written_by_collector'] is False, 'Collector cannot claim parent gates')
        require(receipt['python']['stdout'] == encoding and receipt['python']['stderr'] == encoding
                and receipt['python']['utf8_mode'] == utf8, 'Console context differs')
        for name, expected in receipt['source_sha256'].items():
            require(files.get(name) == expected and digest(root / name) == expected, 'Source differs: ' + name)
        for line in receipt['t01_documentation_contract']:
            require(notes.count(line) == 1, 'T01 owned documentation line differs')
        for name, command in receipt['commands'].items():
            data = (directory / (name + '.log')).read_bytes()
            require(hashlib.sha256(data).hexdigest() == command['output_sha256'], 'Receipt/log hash differs: ' + mode + '/' + name)
            require(command['exit_code'] == command['expected_exit'], 'Unexpected command exit: ' + name)
            require(data.decode('utf-8').splitlines()[-1] == command['last_line'], 'Receipt last line differs: ' + name)
        require(digest(directory / 'cleanup.log') == receipt['cleanup']['output_sha256']
                and receipt['cleanup']['exit_code'] == 0 and not (directory / 'cleanup.log').read_bytes()
                and receipt['cleanup_verified'] is True and receipt['owned_containers_remaining'] == [], 'Cleanup not verified')
        logs = {name: (directory / (name + '.log')).read_text(encoding='utf-8') for name in receipt['commands']}
        require('T02 CONTRACT : 24 tests, 0 failures' in logs['t02-contracts'], 'T02 contracts missing')
        require('T02 OUTPUT CONTRACT : 7/7 PASS (boundary doubles only)' in logs['t02-output'], 'Output contracts missing')
        require('T01 CORRECTIONS : 32 tests, 0 failures' in logs['t01-php-regressions'], 'PHP regression missing')
        require('T01 CONTRACT : 18/18 PASS' in logs['t01-boundary'], 'Boundary regression missing')
        result = replay(logs['rejeu'])
        require(result == receipt['result'] and result['pass'] is True, 'Rejeu receipt differs')
        require(all(result[key] == 0 for key in ('failures', 'errors', 'skipped'))
                and result['tools']['failures'] == 0, 'Rejeu contains failure')
        banks = re.findall(r'^T01 TOOL : ([a-z0-9-]+) ; (\d+) controls ; (\d+) failures ; exit=(\d+)$', logs['rejeu'], re.M)
        require(len(banks) == result['tools']['tools'] and sum(int(bank[1]) for bank in banks) == result['tools']['checks'], 'Tool counters differ')
        require(len({bank[0] for bank in banks}) == len(banks), 'Duplicate bank')
        require(len(re.findall(r'<testcase name="testPureCoherenceRule with data set', logs['rejeu'])) == 9, 'A19 JUnit cases missing')
        for name in ('assertion-rouge', 'recu-mixte-refuse'):
            require(receipt['commands'][name]['exit_code'] == 1 and replay(logs[name])['pass'] is False
                    and logs[name].splitlines()[-1].endswith('FAIL'), 'Red witness missing: ' + name)
        require('T01 TOOL : a10 ; 0 controls ; 1 failures ; exit=0' in logs['recu-mixte-refuse'], 'Mixed receipt did not fail closed')
        require(replay(logs['mutation-garde-absente'])['pass'] is True
                and receipt['commands']['mutation-garde-absente']['exit_code'] == 0
                and 'T01 TOOL : a10 ; 1 controls ; 0 failures ; exit=0' in logs['mutation-garde-absente'], 'Guard mutation witness missing')
        require('FAIL a mixed tests and checks receipt vetoes real PHPUnit success' in logs['mutation-contrat-rouge']
                and 'T02 CONTRACT : 24 tests, 5 failures' in logs['mutation-contrat-rouge'], 'Contract did not catch removed guard')
        require(replay(logs['miroir-vert']) == replay(logs['miroir-restaure']) == receipt['mirror_baseline'], 'Mirror restoration differs')
        require(receipt['mutation']['original_unchanged'] is True and receipt['mutation']['mirror_removed'] is True, 'Mutation not cleaned')
        contexts[mode] = result
    require(contexts['utf8'] == contexts['cp1252'], 'Matrix results differ')
    return {'verified': True, 'contexts': contexts, 'parent_gates_claimed': False,
            'pret_is_parent_owned_and_not_a_verification_condition': True}


if __name__ == '__main__':
    try:
        print(json.dumps(verify(ROOT), ensure_ascii=True, sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(json.dumps({'verified': False, 'error': str(error)}, ensure_ascii=True))
        raise SystemExit(1)
