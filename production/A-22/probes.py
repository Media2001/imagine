"""Exercise delivered verifiers and post-PRET seals in disposable mirrors only."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
SCRATCH=Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch')


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def run(lot,output):
    code=lot.lower().replace('-','')
    verifier=module(ROOT/'wp/tests'/code/'verify.py','probe_'+code)
    if lot=='A-22':sources=verifier.m.sources()
    else:
        sources=verifier.inventory(verifier.OWN)
        dependencies=(module(ROOT/'wp/tests/a20/run.py','a20_probe_runner').DEPENDENCIES
                      if lot=='A-20' else verifier.DEPENDENCIES)
        sources.update(verifier.inventory(dependencies))
    receipt={'lot':lot,'mutations_only_in_scratch':True,'checks':[],'exit_code':1}
    def check(name,ok):
        receipt['checks'].append({'check':name,'status':'PASS' if ok else 'FAIL'})
        if not ok:raise AssertionError(name)
    env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(SCRATCH)}
    with tempfile.TemporaryDirectory(prefix=code+'-verifier-correction-',dir=SCRATCH) as temporary:
        mirror=Path(temporary)/'mirror';mirror.mkdir()
        for name in sources:
            target=mirror/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,target)
        shutil.copytree(ROOT/'production'/lot,mirror/'production'/lot)
        shared=mirror/'wp/tests/a02-audit/README.md';shared.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'wp/tests/a02-audit/README.md',shared)
        packet=mirror/'production'/lot/'preuves/final'
        path=mirror/'wp/tests'/code/'verify.py'
        def verify():
            p=subprocess.run([sys.executable,'-B',str(path),str(packet)],cwd=mirror,env=env,
                capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=120)
            value=json.loads(p.stdout)
            return p,value
        p,value=verify();check('actual_verifier_baseline_green',p.returncode==value['exit_code']==0 and not p.stderr)
        (mirror/'production'/lot/'PRET').write_text('Future parent marker, disposable mirror only.\n',encoding='utf-8')
        p,value=verify();check('future_parent_PRET_does_not_invalidate_packet',p.returncode==value['exit_code']==0 and not p.stderr)
        if lot in {'A-21','A-22'}:
            wrapper=(mirror/'wp/tests/a21/finalise.py' if lot=='A-21' else mirror/'production/A-22/finalise.py')
            p=subprocess.run([sys.executable,'-B',str(wrapper),'--seal-only'],cwd=mirror,env=env,
                capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=120)
            check('actual_post_PRET_seal_wrapper_green',p.returncode==0 and not p.stderr)
        target=mirror/('wp/outils/bascule/a03/Policy.php' if lot=='A-22' else 'wp/outils/bascule/stream_guard.py')
        original=target.read_bytes();target.write_bytes(original+b'\n# disposable source mutation\n')
        p,value=verify();check('a03_policy_source_mutation_refused' if lot=='A-22' else 'shared_guard_source_mutation_refused',p.returncode==value['exit_code']==1)
        if lot=='A-22':
            check('a03_mutation_fails_exact_executed_sources_gate',any(row['check']=='exact_current_executed_sources' and row['status']=='FAIL' for row in value['checks']))
        target.write_bytes(original)
        if lot=='A-22':
            folder=mirror/'wp/outils/bascule/a03';hidden=folder.with_name('a03-hidden');folder.rename(hidden)
            p,value=verify();check('missing_expected_a03_source_root_refused',p.returncode==value['exit_code']==1)
            hidden.rename(folder)
        if lot=='A-22':target=packet/'utf8/A12/classic-a22-documented/contenus.md'
        elif lot=='A-20':target=packet/'utf8/native/classic-prices/tarifs.md'
        else:target=packet/'utf8/classic-portes/portes.md'
        original=target.read_bytes();target.write_bytes(original+b'\nnot an accepted report\n')
        p,value=verify();check('packet_content_mutation_refused',p.returncode==value['exit_code']==1)
        target.write_bytes(original)
        channels=packet/('utf8/A12/a22-channels.json' if lot=='A-22' else 'utf8/native/a22-channels.json' if lot=='A-20' else 'utf8/a22-channels.json')
        original=channels.read_bytes();data=json.loads(original)
        data['checks']=[row for row in data['checks'] if not row['check'].endswith(':channels:shutdown_file')]
        channels.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        manifest=packet/'manifest.json';old_manifest=manifest.read_bytes()
        v=module(path,'mutated_'+code)
        if lot=='A-22':manifest_data=v.hashes(packet)
        elif lot=='A-21':manifest_data=v.packet_manifest(packet)
        else:
            manifest_data=v.inventory(v.OWN+[packet.relative_to(mirror).as_posix()])
            manifest_data.pop(manifest.relative_to(mirror).as_posix(),None)
        manifest.write_text(json.dumps(manifest_data,indent=2)+'\n',encoding='utf-8')
        p,value=verify();check('omitted_file_canary_refused_even_after_reseal',p.returncode==value['exit_code']==1)
        check('resealed_omission_fails_named_channel_gate',any('channels' in row['check'] and row['status']=='FAIL' for row in value['checks']))
        channels.write_bytes(original);manifest.write_bytes(old_manifest)
        p,value=verify();check('restored_mirror_green',p.returncode==value['exit_code']==0 and not p.stderr)
    receipt['exit_code']=int(any(row['status']!='PASS' for row in receipt['checks']))
    output.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,indent=2))
    return receipt['exit_code']


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lot',required=True,choices=['A-20','A-21','A-22'])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();sys.exit(run(args.lot,args.output))
