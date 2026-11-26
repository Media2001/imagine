"""Independent real-verifier mutations on a scratch clone; no live repository writes."""
import argparse
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    out=args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('a21_probe_verifier',HERE/'verify.py')
    verifier=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    root=out/'repository'
    for name in verifier.OWN+verifier.DEPENDENCIES:
        source=ROOT/name
        if source.is_dir():
            shutil.copytree(source,root/name,ignore=shutil.ignore_patterns('__pycache__'))
        else:
            (root/name).parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,root/name)
    for name in ['readme-ajout.txt','readme-delta.txt','notes.md']:
        target=root/'production/A-21'/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'production/A-21'/name,target)
    packet=root/'production/A-21/preuves/final'
    shutil.copytree(ROOT/'production/A-21/preuves/final',packet)
    verifier.ROOT=root
    checks=[]
    def record(name,ok,detail=None):
        checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
        assert ok,name
    def inspect(module=verifier):
        stream=io.StringIO()
        with contextlib.redirect_stdout(stream):
            code=module.verify(packet)
        return code,json.loads(stream.getvalue())
    def save(path,data):
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
    def seal():
        save(packet/'manifest.json',verifier.packet_manifest(packet))
    record('complete_current_copy_green',inspect()[0]==0)
    readme=root/'wp/tests/a02-audit/README.md'
    before=readme.read_bytes()
    readme.write_bytes(before+b'\nIndependent unrelated appendix.\n')
    record('unrelated_readme_appendix_accepted',inspect()[0]==0)
    readme.write_bytes(before)
    targets=['wp/outils/bascule/a11/Runtime.php','wp/outils/bascule/a12/confine.py',
             'wp/outils/bascule/audit','wp/outils/staging/lib.php',
             'wp/tests/a02-audit/inside.py','wp/tests/a19/run.py']
    for name in targets:
        path=root/name
        original=path.read_bytes()
        path.write_bytes(original+b'\n# independent dependency drift\n')
        code,data=inspect()
        failed=[row['check'] for row in data['checks'] if row['status']=='FAIL']
        record('dependency_drift_refused:'+name,code==1 and set(failed)=={
            'exact_current_dependencies','cp1252:executed_dependency_snapshot','utf8:executed_dependency_snapshot'},failed)
        if name==targets[0]:
            # Deliberate mutant restores the former bug: no current dependency seal.
            text=(HERE/'verify.py').read_text(encoding='utf-8')
            text=text.replace("load(packet/'dependency-snapshot.json')==dependencies",'True')
            text=text.replace("load(folder/'dependency-snapshot.json')==dependencies",'True')
            namespace={'__file__':str(root/'wp/tests/a21/verify.py'),'__name__':'a21_deliberate_mutant'}
            exec(compile(text,'a21-deliberate-mutant','exec'),namespace)
            mutant=type('Mutant',(),{})()
            mutant.verify=namespace['verify']
            mutant_code,mutant_data=inspect(mutant)
            save(out/'red-drift.json',{'deliberate_mutation':'ignore_current_dependency_seals',
                 'expected_rejection':1,'actual_exit_code':mutant_code,'red_observed':mutant_code==0,
                 'result':mutant_data})
            record('real_red_false_green_without_dependency_seals',mutant_code==0)
        path.write_bytes(original)
    for mode in ['omitted','duplicate','crlf']:
        appendix=(root/'production/A-21/readme-ajout.txt').read_bytes()
        line=appendix.splitlines(keepends=True)[0]
        changed=before.replace(line,b'',1) if mode=='omitted' else before+line if mode=='duplicate' else before.replace(line,line.rstrip(b'\n')+b'\r\n',1)
        readme.write_bytes(changed)
        record('readme_contract_refused:'+mode,inspect()[0]==1)
        readme.write_bytes(before)
    result=packet/'result.json'
    original=result.read_bytes()
    data=json.loads(original)
    data['checks']=[row for row in data['checks'] if row['check']!='hpos:supervised_bootstrap:shutdown_stderr']
    save(result,data)
    seal()
    code,data=inspect()
    record('required_shutdown_case_missing_even_after_reseal',code==1 and any(
        row['check']=='cp1252:hpos:required_native_cases' and row['status']=='FAIL' for row in data['checks']))
    result.write_bytes(original)
    seal()
    record('restored_copy_green',inspect()[0]==0)
    receipt={'suite':'A21-independent-verifier-probes','checks':checks,'exit_code':0,
             'red_log_scratch_only':str(out/'red-drift.json')}
    save(out/'verification-probes.json',receipt)
    print(json.dumps(receipt,indent=2))
    return 0

if __name__=='__main__':
    sys.exit(main())
