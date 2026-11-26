"""Rejoue toute la suite A-13 et trois vrais appels CLI, sans données réelles."""
import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TESTS = ROOT / 'wp/tests/a13'
FIXTURES = ROOT / 'wp/tests/fixtures'
TOOL = ROOT / 'wp/outils/bascule/controler-export'
CONFIG = ROOT / 'wp/outils/bascule/a13/correspondance.exemple.json'
ENV = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verifier():
    inputs = [TOOL, CONFIG, ROOT/'wp/outils/bascule/controler-export.md']
    inputs += [p for p in TESTS.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    inputs += list(FIXTURES.glob('a13-*-fictif.csv'))
    source_hashes = {p.relative_to(ROOT).as_posix():digest(p) for p in inputs}
    log = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(TESTS), pattern='test_*.py')
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    assert result.testsRun > 0 and result.wasSuccessful() and not result.skipped, log.getvalue()
    evidence = {
        'horodatage': datetime.now().astimezone().isoformat(),
        'python': platform.python_version(), 'systeme': platform.system(),
        'date_reference': '2026-11-25',
        'suite': {'commande': 'python -m unittest discover -s wp/tests/a13 -v',
                  'tests': result.testsRun, 'echecs': len(result.failures),
                  'erreurs': len(result.errors), 'ignores': len(result.skipped)},
        'cli': [], 'sources_sha256': source_hashes,
    }
    scratch = Path(os.environ.get('TMPDIR', tempfile.gettempdir()))
    with tempfile.TemporaryDirectory(prefix='a13-livraison-', dir=scratch) as temporary:
        work = Path(temporary)
        assert not work.resolve().is_relative_to(ROOT.resolve())
        for name, code, rejected in [('propre', 0, 0), ('defauts', 1, 25), ('iban', 2, None)]:
            fixture = FIXTURES / f'a13-export-{name}-fictif.csv'
            with fixture.open(encoding='utf-8', newline='') as stream:
                rows = list(csv.reader(stream, delimiter=';'))
            assert len(rows) - 1 == 30
            folder = work / name
            folder.mkdir()
            source = folder / 'export.csv'
            shutil.copyfile(fixture, source)
            before = digest(source)
            command = [sys.executable, str(TOOL), str(source), '--correspondance', str(CONFIG), '--au', '2026-11-25']
            run = subprocess.run(command, capture_output=True, encoding='utf-8', env=ENV, timeout=30)
            assert run.returncode == code, (name, run.returncode, run.stderr)
            assert before == digest(source)
            outputs = sorted(path for path in folder.iterdir() if path != source)
            texts = run.stdout + run.stderr + ''.join(path.read_text(encoding='utf-8') for path in outputs)
            for forbidden in ('ZZ00', 'Licorne', 'Éléphant', '@example.org', 'MANDAT-FICTIF', 'illisible-fictif'):
                assert forbidden not in texts, (name, 'fuite')
            case = {'fixture': fixture.relative_to(ROOT).as_posix(), 'lignes': 30, 'code': run.returncode,
                    'fichier_source_inchange': True, 'nombre_sorties': len(outputs),
                    'sorties': {path.name: digest(path) for path in outputs}}
            if code == 2:
                assert not outputs and 'IBAN suspect : colonne 14' in run.stderr and not run.stdout
                case['valeur_iban_dans_sorties'] = False
            else:
                assert len(outputs) == 2
                summary = source.with_name('export.controle-resume.txt').read_text(encoding='utf-8')
                with source.with_name('export.controle-rejets.csv').open(encoding='utf-8', newline='') as stream:
                    errors = list(csv.DictReader(stream, delimiter=';'))
                assert len({entry['ligne'] for entry in errors}) == rejected
                assert f'Lignes rejetées : {rejected}\n' in summary
                case.update({'lignes_rejetees': rejected, 'motifs': len(errors), 'resume': summary})
            evidence['cli'].append(case)
    assert source_hashes == {p.relative_to(ROOT).as_posix():digest(p) for p in inputs}
    evidence['statut'] = 'A13_VERIFIE_LOCALEMENT'
    evidence['integration'] = 'Reconstruction image partagée à vérifier par le parent avant PRET.'
    return evidence, log.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preuve', type=Path, help='JSON de preuve synthétique, sans donnée de contact.')
    args = parser.parse_args()
    evidence, log = verifier()
    if args.preuve:
        args.preuve.parent.mkdir(parents=True, exist_ok=True)
        args.preuve.with_suffix('.tests.txt').write_text(log, encoding='utf-8')
        args.preuve.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(evidence, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
