"""Seal only a genuinely passing A08 packet, then independently verify before PRET."""
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-08'


def sha(path):
    with open(path,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def mapping(paths):
    return {str(path.relative_to(ROOT)).replace('\\','/'):sha(path) for path in paths}


def write(path,value):
    assert not path.exists(),str(path)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def main():
    assert len(sys.argv)==3,'Usage: sceller.py proof-id report-relative-path'
    proof=LOT/'preuves'/sys.argv[1]
    assert proof.parent==LOT/'preuves' and proof.is_dir()
    report=ROOT/sys.argv[2]
    assert report.parent==ROOT/'files/rapports' and report.is_file()
    runner=json.loads((proof/'runner.json').read_text())
    inner=json.loads((proof/'result.json').read_text())
    assert runner['exit_code']==inner['exit_code']==0
    assert all(row['ok'] for row in runner['checks']+inner['checks'])
    assert not (LOT/'PRET').exists() and not (LOT/'manifeste.json').exists()
    protected=json.loads((LOT/'baseline.json').read_text())
    for name,digest in protected.items():assert sha(ROOT/name)==digest,name
    sources=json.loads((proof/'sources.json').read_text())
    for name,digest in sources.items():assert sha(ROOT/name)==digest,name
    expected_new={'wp/outils/bascule/a08/sequence.py','wp/outils/bascule/repeter','wp/outils/bascule/repetition.md'}
    accepted_paths=[path for directory in ['a02-audit','a03-non-regression','a04','a05','t01'] for path in (ROOT/'wp/tests'/directory).rglob('*') if path.is_file()]
    accepted_paths += [path for path in (ROOT/'wp/outils/bascule').rglob('*') if path.is_file()]
    accepted_paths += [ROOT/'wp/tests/preparer-image.ps1',ROOT/'wp/tests/rejouer.ps1']
    accepted_paths=[path for path in accepted_paths if '__pycache__' not in path.parts]
    source_baseline={name for name in protected if '__pycache__' not in pathlib.PurePosixPath(name).parts}
    assert set(mapping(accepted_paths))==source_baseline|expected_new,'Accepted source inventory changed'
    def count_tests(filename):
        log=(proof/filename).read_text()
        assert log.rstrip().endswith('OK'),filename
        return int(re.search(r'Ran (\d+) tests?',log)[1])
    counts={'a08_unit':count_tests('unit.log'),'a02_unit':len(json.loads((proof/'a02-unit.json').read_text())['checks']),
            'a03_unit':len(json.loads((proof/'a03-unit.json').read_text())['tests']),
            'a03_boundaries':len(json.loads((proof/'output-boundary.json').read_text())),
            'a04_unit':count_tests('a04-regression.log'),'a05_unit':count_tests('a05-regression.log'),
            'native_checks':len(inner['checks']),'runner_checks':len(runner['checks'])}
    history=[]
    for ident in ['b5f500c89800','ff8cfcb0e2cb','5a321d32d802','eaf29aea5303','86139c81dd7e','8413ef37ee04']:
        history += [LOT/'preuves'/ident/filename for filename in ['unit.log','runner.json']]
    history += [LOT/'preuves/09979d166e7e'/filename for filename in ['result.json','runner.json','classic-second-option-fingerprints.json','hpos-second-option-fingerprints.json']]
    delivery=[LOT/name for name in ['baseline.json','precontrole.json','notes.md','sceller.py','verifier.py','preparer-image.json','preparer-image.log','dependances/public.json','dependances/wordpress-7.0.zip','dependances/woocommerce-11.0.1.zip']]+[report]
    manifest={'schema':'imagine-a08-delivery-v1','created_at':datetime.datetime.now().astimezone().isoformat(),
              'proof':str(proof.relative_to(ROOT)).replace('\\','/'),'report':str(report.relative_to(ROOT)).replace('\\','/'),
              'counts':counts,'protected':protected,'sources':sources,
              'evidence':mapping(path for path in proof.rglob('*') if path.is_file()),'history':mapping(history),'delivery':mapping(delivery),
              'scope':'Chaîne fictive classique+HPOS ; idempotence métier, contrôles techniques natifs rafraîchissables ; deux rendez-vous opérateur.',
              'not_a_real_go':True}
    write(LOT/'manifeste.json',manifest)
    command=[sys.executable,'-B',str(LOT/'verifier.py'),'--sans-pret']
    verified=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace')
    write(LOT/'verification-avant-pret.json',{'command':command,'exit':verified.returncode,'stdout':verified.stdout,'stderr':verified.stderr})
    print(verified.stdout,verified.stderr)
    assert verified.returncode==0,'PRET withheld: verifier failed'
    write(LOT/'PRET',{'lot':'A-08','manifest':'production/A-08/manifeste.json','manifest_sha256':sha(LOT/'manifeste.json'),
                      'scope':manifest['scope'],'not_a_real_go':True})
    return 0


if __name__=='__main__':sys.exit(main())
