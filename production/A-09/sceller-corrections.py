"""Seal the current A09 correction packet after real Docker execution."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
LOT = ROOT/'production/A-09'
PROOF = 'a1671ceb23d2'
REPORT = 'files/rapports/2026-11-25-22h11-A09.md'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
    assert not (LOT/'PRET').exists(), 'Do not replace a sealed correction delivery'
    assert sha(ROOT/'corrections/A-09.md') == '7dc15f6d34fd166235b575c9635e5475e6b4008869be0db43d874a6663744e5f', 'New correction: reread first'
    history = json.loads((LOT/'historique-corrections.json').read_text())
    for n,h in history.items():
        assert sha(ROOT/n)==h,n
    prior = json.loads((LOT/'avant-corrections/manifeste.json').read_text())
    packet = LOT/'preuves'/PROOF
    log = (packet/'tests.log').read_text()
    tests = re.findall(r'^test_\w+ \([^\n]+\) \.\.\. ok$',log,re.M)
    count = int(re.search(r'^Ran (\d+) tests in ',log,re.M)[1])
    assert count == len(tests) == 28 and log.rstrip().endswith('OK')
    sources = set(prior['sources']) | {
        'production/A-09/preparer-corrections.py','production/A-09/sceller-corrections.py',
        'production/A-09/notes-corrections.md',REPORT,'corrections/A-09.md',
        'A-FAIRE.md','prompts/consigne-permanente.md','doctrine/doctrine.md',
        'briefs/A-09-test-des-redirections.md'}
    evidence = dict(history)
    for p in (LOT/'preuves').rglob('*'):
        if p.is_file():
            evidence[p.relative_to(ROOT).as_posix()] = sha(p)
    for filename in ['baseline.json','historique-corrections.json','transition-corrections.json','preparer-image.json','preparer-image.log']:
        p=LOT/filename
        evidence[p.relative_to(ROOT).as_posix()]=sha(p)
    cycles=prior['tdd_cycles']+[
        {'feature':'R1 path/query exact transport','red':'5d086f34747b','green':'1f0bd8f9256a'},
        {'feature':'R2 explicit empty query refusal','red':'7a23637d6669','green':'5aeae2f21554'},
        {'feature':'R3 whole ASCII before any HTTP','red':'0c8c40532852','green':'e1ae232504e9'}]
    manifest={**prior,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'proof':PROOF,'tests':count,'sources':{n:sha(ROOT/n) for n in sorted(sources)},
              'evidence':dict(sorted(evidence.items())),'tdd_cycles':cycles,
              'correction_file':'corrections/A-09.md','report':REPORT,
              'new_test_package':False,'preparation':'Historical receipt retained; existing A09 package extended, no new test package.',
              'historical_files_preserved':len(history),'protected_current_files':len(json.loads((LOT/'baseline.json').read_text()))}
    write(LOT/'manifeste.json',manifest)
    def verify(args,target):
        r=subprocess.run([sys.executable,'-B',str(LOT/'verifier.py')]+args,cwd=ROOT,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=450)
        assert r.returncode == 0,r.stdout+r.stderr
        data=json.loads(r.stdout)
        assert data['exit_code']==0
        write(LOT/target,data)
        print(r.stdout)
    verify(['--pre-pret'],'verification-corrections-avant-pret.json')
    (LOT/'PRET').write_text('A-09 — corrections techniques R1/R2/R3 prêtes à relire.\n'
                          +'Preuve Docker/HTTP : '+PROOF+' ; 28 tests réussis, 0 échec.\n'
                          +'Manifeste SHA-256 : '+sha(LOT/'manifeste.json')+'\n'
                          +'Historique préservé ; aucun GO production.\n'
                          +'Rejeu parent : python -B production/A-09/verifier.py --replay\n',encoding='utf8')
    verify([],'verification-corrections-finale.json')
if __name__=='__main__':
    main()
