"""One bounded contract migration; no PHP/demo/bootstrap writes or general replay."""
import sys
sys.dont_write_bytecode = True
import copy
import importlib.util
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'wp/tests/demo'))
import lot_reception_contract as contract


def reader(lot):
    path = ROOT/('wp/tests/demo/b11-verifier1330.py' if lot == 'B11' else 'production/C-29/verifier.py')
    spec = importlib.util.spec_from_file_location(lot+'_contract_reader', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def manifest(lot):
    _, folder, _, changes = contract.config(lot)
    out = ROOT/'production'/folder
    old_name = 'reception-politique1330-V2.json' if lot == 'B11' else 'reception-V2.json'
    old = json.loads((out/old_name).read_text(encoding='utf-8'))
    m = copy.deepcopy(old)
    # Historic C29 verifier is itself evidence. Its exact original is archived,
    # never silently rehashed or relabelled as the current verifier.
    evidence = {}
    for name, value in old['evidence'].items():
        target = changes.get(f'production/{folder}/{name}')
        name = Path(target).name if target else name
        assert contract.digest(out/name) == value, ('OLD_EVIDENCE', name)
        evidence[name] = value
    historical = {old_name: contract.digest(out/old_name), 'PRET-avant-contrat-V2': contract.digest(out/'PRET-avant-contrat-V2')}
    historical.update(old.get('historical_receipts', {}))
    for original, archived in changes.items():
        value = old['sources'].get(original, old['evidence'].get(Path(original).name))
        assert value and contract.digest(ROOT/archived) == value, 'ARCHIVED_READER'
        historical[Path(archived).name] = value
    m.update({'at':datetime.now(timezone.utc).isoformat(), 'contract_version':1,
              'contract_policy':'A-FAIRE-2 2026-11-27 16h30, consignes 0/1',
              'sources':contract.sources(lot), 'bootstrap_contract':contract.registration(lot),
              'readme_section':__import__('hashlib').sha256(contract.section(lot).encode()).hexdigest(),
              'evidence':evidence, 'historical_files':historical,
              'verification_only_changes':changes,
              'runtime_evidence':'Historical pure/native/browser experiments preserved verbatim; owned functional and probe bytes checked against them. No new PHP, browser matrix, bootstrap deployment or general replay.',
              'shared_contract':'Own exact unique registration and bounded README section only; no whole bootstrap digest and no neighbor PRET/readiness gate.'})
    m.pop('neighbors', None)
    return m


def finish():
    for lot in ['B11', 'C29']:
        _, folder, _, _ = contract.config(lot)
        out = ROOT/'production'/folder
        assert not (out/contract.RECEIPT).exists(), 'RECEIPT_EXISTS'
        m = manifest(lot)
        v = reader(lot)
        for name in ['NOTE-contrat-V2.md', 'A-VOIR-contrat-V2.md']:
            m['evidence'][name] = contract.digest(out/name)
        script = ROOT/'wp/tests/demo/b11-c29-contract-tests.py'
        log = out/'qualification-contrat-V2.log'
        with log.open('xb') as stream:
            result = subprocess.run([sys.executable,'-B',str(script),lot],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
        assert result.returncode == 0, log.read_text(encoding='utf-8')
        m['evidence'][log.name] = contract.digest(log)
        # Actual offline and guarded read-only live checks before publication.
        v.verify(False,m,False)
        v.verify(True,m,False)
        with (out/contract.RECEIPT).open('x',encoding='utf-8') as stream:
            json.dump(m,stream,ensure_ascii=False,indent=2)
        pret = ('B11 PRET TECHNIQUE — UI_save_verified=false, politique13h30 conservée; 16 options effectives et témoin backend 8/8.\n' if lot=='B11' else 'C29 PRET TECHNIQUE — preuves intactes 21 pures, 51 natives, 73 HTTP, 27 profils.\n')
        # Scope is explicit: only the two current pointers, archived byte-for-byte.
        (out/'PRET').write_text(pret+'Réception courante : reception-contrat-V2.json ; NOTE-contrat-V2.md et A-VOIR-contrat-V2.md.\nContrat16h30 : fichiers propres, bloc propre exact unique, section README bornée; pas de sceau global ni de PRET voisin.\nLecteurs offline/live-readonly réels PASS; aucune modification fonctionnelle ou nouvelle matrice. Historiques conservés. Ni clôture, validation visuelle ou GO réel.\n',encoding='utf-8')
        for args, label in [([], 'offline'), (['--live'], 'live')]:
            entry = ROOT/('wp/tests/demo/b11-verifier.py' if lot=='B11' else 'production/C-29/verifier.py')
            with (out/('verification-contrat-'+label+'-V2.log')).open('xb') as stream:
                result = subprocess.run([sys.executable,'-B',str(entry),*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONIOENCODING':'utf-8'})
            assert result.returncode == 0, label
            print((out/('verification-contrat-'+label+'-V2.log')).read_text(encoding='utf-8').strip())
        assert (out/'PRET').read_text(encoding='utf-8').startswith(lot+' PRET TECHNIQUE')
        assert contract.RECEIPT in (out/'PRET').read_text(encoding='utf-8')


if __name__ == '__main__':
    assert sys.argv[1:] == []
    finish()
