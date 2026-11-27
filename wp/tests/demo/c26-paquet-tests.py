"""Qualification du vrai paquet : offline, sans write production, faux reçus rescellés."""
import sys
sys.dont_write_bytecode = True
from contextlib import redirect_stdout
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import socket
import tempfile
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[3]
PROOF = ROOT/'production/C-26'
spec = importlib.util.spec_from_file_location('c26_offline_verifier', Path(__file__).with_name('c26-verifier.py'))
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def fingerprint():
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in PROOF.iterdir() if p.is_file()}


def evaluate(packet):
    output = io.StringIO()
    with patch.object(socket.socket,'connect',side_effect=AssertionError('network forbidden')), \
         patch.object(Path,'write_text',side_effect=AssertionError('write forbidden')), \
         patch.object(Path,'write_bytes',side_effect=AssertionError('write forbidden')), \
         redirect_stdout(output):
        ok = v.verify(packet)
    return ok,json.loads(output.getvalue())


def run():
    before = fingerprint()
    ok, nominal = evaluate(PROOF)
    assert ok, nominal['failures']
    manifest = json.loads((PROOF/'manifest.json').read_text(encoding='utf-8'))
    delivery,mutations = manifest['delivery'],manifest['mutations']
    cases = []
    # Le sceau externe est recalculé après chaque falsification : les contrôles sémantiques doivent rougir.
    def drop_extras(d):
        d['results']=[r for r in d['results'] if r['name'] not in ['identite-REST','inverse-article','inverse-pdf','inverse-C08','inverse-achat-C14']]
        d['total']=len(d['results'])
    def duplicate_identity(d):
        d['results'].append(copy.deepcopy(next(r for r in d['results'] if r['name']=='identite-REST')))
        d['total']=len(d['results'])
    changes = [('total',delivery+'.json',lambda d:d.update(total=d['total']+1)),
               ('matrice-vide',delivery+'.json',lambda d:d.update(results=[])),
               ('case-manquante',delivery+'.json',lambda d:d['results'].pop()),
               ('restauration',delivery+'-restauration.json',lambda d:d['exact_restoration'].update(usermeta=False)),
               ('privacy-inverse',delivery+'-privacy.json',lambda d:d['results'].pop()),
               ('privacy-inverse-vide-redesigne',delivery+'-privacy.json',lambda d:[r.update(positive=False,witnesses_found=0) for r in d['results'] if r['public']=='inverse-proprietaire']),
               ('privacy-tiers-positive',delivery+'-privacy.json',lambda d:[r.update(positive=True,witnesses_found=1) for r in d['results'] if r['public']=='anonyme']),
               ('c23-extras-supprimes',delivery+'-c23.json',drop_extras),
               ('c23-identite-dupliquee',delivery+'-c23.json',duplicate_identity),
               ('c23-inverse-vide',delivery+'-c23.json',lambda d:[r.update(witnesses_found=0) for r in d['results'] if r['name']=='inverse-article']),
               ('c23-echec-cache',delivery+'-c23.json',lambda d:[r.update(ok=False,leak=True) for r in d['results'] if r['name']=='inverse-C08']),
               ('oracle-b06-circulaire',delivery+'-inventaire.json',lambda d:d['cooperator_publics'].append('connecte-sans-abonnement')),
               ('restauration-etape-erreur',delivery+'-restauration.json',lambda d:d['restoration_steps']['b06'].update(ok=False)),
               ('mutation-blanchie',mutations+'-mutation-agenda.json',lambda d:[r.update(ok=True,leak=False,witnesses_found=0) for r in d['results']]),
               ('decouverte-forcee',delivery+'-c23.json',lambda d:d['discovery']['policy'].update(ouverture='premiere_lecture')),
               ('tests-inventes','tests.json',lambda d:d['utf8'].update(tests=999)),
               ('mutation-c08-b06-incomplete',mutations+'-mutation-cooperative.json',lambda d:d['families'].update(B06=False)),
               ('mutation-archive-blanchie',mutations+'-mutation-archive.json',lambda d:[r.update(ok=True,leak=False,witnesses_found=0) for r in d['results']]),
               ('mutation-autorisation-blanchie',mutations+'-mutation-autorisation-b06.json',lambda d:d.update(observed=d['expected'])),
               ('source-fausse','manifest.json',lambda d:d['sources'].update({'wp/outils/demo/c26.py':'0'*64}))]
    scratch = Path(os.environ.get('TMPDIR') or str(Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData/Local')))/'hermes/cache/scratch'))
    scratch.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='c26-packet-',dir=scratch) as folder:
        for name,target,alter in changes:
            packet = Path(folder)/name
            packet.mkdir()
            for filename in list(manifest['artifacts'])+['manifest.json']:
                shutil.copyfile(PROOF/filename,packet/filename)
            data = json.loads((packet/target).read_text(encoding='utf-8'))
            alter(data)
            (packet/target).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            if target != 'manifest.json':
                seal = copy.deepcopy(manifest)
                seal['artifacts'][target] = hashlib.sha256((packet/target).read_bytes()).hexdigest()
                (packet/'manifest.json').write_text(json.dumps(seal),encoding='utf-8')
            accepted,result = evaluate(packet)
            cases.append({'case':name,'rejected':not accepted,'failures':result['failures'],'outer_seal_refreshed':target!='manifest.json'})
    after = fingerprint()
    receipt = {'scope':'imagine-test-demo','nominal_exit':0 if ok else 1,'nominal_controls':nominal['total'],
               'network_blocked':True,'write_methods_blocked':True,'production_unchanged':before==after,
               'mutations':cases,'all_rejected':all(x['rejected'] for x in cases)}
    print(json.dumps(receipt,ensure_ascii=True,indent=2))
    return 0 if before==after and receipt['all_rejected'] else 1


if __name__ == '__main__':
    raise SystemExit(run())
