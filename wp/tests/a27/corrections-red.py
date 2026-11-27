"""Container-only mutation witnesses; always restore copied subject bytes."""
import json
from pathlib import Path
import subprocess


def witness(label, source, old, new, script, receipt, expected):
    original = source.read_bytes()
    text = original.decode('utf-8')
    if text.count(old) != 1:
        raise RuntimeError('A27_RED_TARGET_INVALID')
    try:
        source.write_text(text.replace(old, new), encoding='utf-8')
        p = subprocess.run(['php', '/opt/a27/' + script], capture_output=True, timeout=60)
        data = json.loads((Path('/report') / receipt).read_text(encoding='utf-8'))
        (Path('/report') / ('red-' + label + '.json')).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
        failed = {row['check'] for row in data['checks'] if row['status'] == 'FAIL'}
        if p.returncode != 1 or p.stderr or data['exit_code'] != 1 or not set(expected).issubset(failed):
            raise RuntimeError('A27_RED_NOT_REPRODUCED')
    finally:
        source.write_bytes(original)


if __name__ == '__main__':
    witness('r2', Path('/subject/a27/Inventory.php'),
            "return $opaque && $reference === 'absent' ? 'unknown' : $reference;", 'return $reference;',
            'adapter-unit.php', 'adapter-unit.json',
            ['opaque_adapted_presence', 'opaque_five_automatic_illisible', 'opaque_five_relation_unknown'])
    witness('r3', Path('/subject/a27/Analysis.php'),
            "            if ($ids && (count($matches) !== 1 || !in_array($matches[0]['id'], $ids, true))) {\n"
            "                return ['type' => 'illisible', 'link' => 'unknown', 'expiry' => null, 'present' => true];\n"
            "            }\n", '', 'unit.php', 'unit.json', ['explicit_contradiction_stripe_sepa'])
    print('A27_CORRECTION_RED_OK')
