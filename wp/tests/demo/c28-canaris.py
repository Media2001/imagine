"""Replayable RED/GREEN C28 mutants, isolated source copy; no site/network."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]

def run(label):
    scratch = Path(os.environ.get('TMPDIR', Path.home()/'AppData/Local/hermes/cache/scratch'))
    scratch.mkdir(parents=True, exist_ok=True)
    assert ROOT not in [scratch.resolve(), *scratch.resolve().parents]
    source = ROOT/'wp/plugins/imagine-site'
    names = ['PacksRegles.php', 'PacksThematiques.php', 'AchatsNumeros.php', 'tests/fixtures/c28-adapter.php']
    originals = {name: (source/name).read_bytes() for name in names}
    mutants = {
        'C28-01-direct': ('PacksThematiques.php', b"if (!self::achetable(true, wc_get_product($productId)))", b'if (false)'),
        'C28-01-checkout': ('PacksThematiques.php', b"self::ajouter(true, $line['product_id']);", b'// guard removed'),
        'C28-02-late-reconstruction': ('PacksThematiques.php', b"if ($persisted && ($persisted->is_paid() || $persisted->get_date_paid('edit')))", b'if (false)'),
        'C28-02-paid-missing-date': ('PacksThematiques.php', b"if ($persisted && ($persisted->is_paid() || $persisted->get_date_paid('edit')))", b"if ($persisted && $persisted->get_date_paid('edit'))"),
        'C28-symmetry': ('AchatsNumeros.php', b"$product->delete_meta_data('imagine_pack_numeros');", b'// unlink removed'),
    }
    results = {}
    with tempfile.TemporaryDirectory(prefix='c28-canary-', dir=scratch) as tmp:
        dest = Path(tmp)
        wsl = '/mnt/'+dest.drive[0].lower()+dest.as_posix()[2:]
        for case in [*mutants, 'GREEN']:
            data = dict(originals)
            if case in mutants:
                name, old, new = mutants[case]
                assert data[name].count(old) == 1, case
                data[name] = data[name].replace(old, new)
            for name, raw in data.items():
                path = dest/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            cmd = ['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--mount', f'type=bind,source={wsl},target=/probe,readonly', '--entrypoint', 'php', 'imagine-tests-t01:1', '/probe/tests/fixtures/c28-adapter.php']
            p = subprocess.run(cmd, capture_output=True, encoding='utf-8')
            assert not p.stderr, p.stderr
            parsed = json.loads(p.stdout)
            assert parsed['total'] == len(parsed['checks']) >= 24
            assert parsed['failures'] == sum(not v for v in parsed['checks'].values())
            assert p.returncode == (0 if case == 'GREEN' else 1), (case, p.stdout)
            assert (parsed['failures'] == 0) == (case == 'GREEN')
            results[case] = {'exit': p.returncode, **parsed}
    receipt = {'scope': 'offline-doubles-no-site', 'cases': results, 'sources': {n: hashlib.sha256(b).hexdigest() for n, b in originals.items()}}
    target = ROOT/'production/C-28'/(label+'.json')
    assert not target.exists(), target
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({name: {'exit': r['exit'], 'failures': r['failures']} for name, r in results.items()}))

if __name__ == '__main__':
    run(sys.argv[1])
