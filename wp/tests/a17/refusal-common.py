"""Exercise six real PHP output boundaries in one owned offline fixture."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid
sys.dont_write_bytecode = True
LOTS = ['a11', 'a12', 'a14', 'a15', 'a16', 'a17']
ENTRY = dict(zip(LOTS, ['inventorier-adresses', 'inventorier-contenus', 'command.php', 'inventorier-emails', 'inventorier-numeros', 'inventorier-securite']))

def inside():
    site = Path('/scratch/site');site.mkdir(parents=True)
    (site/'wp-content/uploads').mkdir(parents=True)
    config = "<?php define('DB_NAME','fictif_test'); define('DB_USER','fictif'); define('DB_PASSWORD',''); define('DB_HOST','localhost'); $table_prefix='wp_';"
    (site/'wp-config.php').write_text(config)
    report = Path('/report');(report/'audit').mkdir()
    (report/'audit/audit.json').write_text(json.dumps({'schema':'imagine-a02-audit-v1','read_only':True,'sections':{'database':{'tables':[]},'commerce':{'order_storage':'classic'}}}))
    mapping={'version':1,'numero_type':'numero','article_type':'article','date_cle':'date','pdf_cle':'pdf','liaison':{'source':'postmeta','cle':'numero_id'},'thematique':'theme'}
    (report/'mapping.json').write_text(json.dumps(mapping))
    sys.path.insert(0,'/subject/a12')
    import confine
    checks=[];cases=[]
    canary='IDENTITE_CONFIDENTIELLE_CANARY'
    dropins=['wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php','wp-content/sunrise.php','wordfence-waf.php','.user.ini']
    for case in ['symlink-file','symlink-directory','config-define','config-const',*dropins]:
        path=None
        if case.startswith('symlink'):
            path=site/'wp-content/uploads'/canary
            path.symlink_to(site/'wp-content' if case.endswith('directory') else site/'wp-config.php',target_is_directory=case.endswith('directory'))
            expected='A11_SYMLINK_UNSUPPORTED\n'
        elif case.startswith('config'):
            tail=(" define('"+canary+"',true);" if case.endswith('define') else ' const '+canary+'=true;')
            (site/'wp-config.php').write_text(config+tail);expected='A11_CONFIG_OVERRIDE_UNSUPPORTED\n'
        else:
            path=site/case;path.write_text('<?php throw new RuntimeException("NEVER_EXECUTE");')
            expected='A11_DROPIN_UNSUPPORTED '+json.dumps({'file':case},separators=(',',':'))+'\n'
        try:
            for lot in LOTS:
                out=report/(lot+'-output')
                args=['--wp-path='+str(site),'--audit=/report/audit/audit.json','--output='+str(out)]
                if lot=='a16':args.append('--correspondance=/report/mapping.json')
                # Real kernel fence and real production PHP entrypoint, no mock runtime.
                code="import os,sys;sys.path.insert(0,'/subject/a12');import confine;from pathlib import Path;confine.confine(Path('/report'));os.execvp('php',sys.argv[1:])"
                php=['php','-d','display_errors=0','-d','log_errors=0','-d','disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec','/subject/'+lot+'/'+ENTRY[lot],*args]
                p=subprocess.run(['python3','-c',code,*php],input='[]',text=True,capture_output=True,env={**os.environ,lot.upper()+'_CONFINED':'1'},timeout=20)
                generated=[f for f in report.rglob('*') if f.is_file() and f.name not in ['audit.json','mapping.json']]
                absent=all(canary.encode() not in f.read_bytes() and canary not in str(f.relative_to(report)) for f in generated)
                ok=p.returncode==1 and p.stdout=='' and p.stderr==expected and canary not in p.stdout+p.stderr and absent and not out.exists()
                key=lot+':'+case
                checks.append({'check':key,'status':'PASS' if ok else 'FAIL'})
                cases.append({'case':key,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'canary_absent_all_artifacts':absent,'output_created':out.exists()})
        finally:
            if path:path.unlink()
            (site/'wp-config.php').write_text(config)
    result={'exit_code':int(any(c['status']!='PASS' for c in checks)),'checks':checks,'cases':cases,'landlock_abi':confine.libc.syscall(confine.NR_CREATE_RULESET,0,0,1) if hasattr(confine,'NR_CREATE_RULESET') else 'required_by_confine'}
    (report/'refusal-common.json').write_text(json.dumps(result,indent=2)+'\n')
    return result['exit_code']

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    root=Path(__file__).resolve().parents[3];out=a.output.resolve();assert not out.is_relative_to(root);out.mkdir(parents=True,exist_ok=False)
    spec=importlib.util.spec_from_file_location('bench',root/'wp/tests/a02-audit/run.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);b.LABEL='org.imagine.a17-refusal'
    name='imagine-a17-refusal-'+uuid.uuid4().hex[:12];created=False;checks=[]
    source={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for key in ['a11','a12','a14','a15','a16','a17'] for p in (root/'wp/outils/bascule'/key).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    source[Path(__file__).resolve().relative_to(root).as_posix()]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    try:
        b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pull','never','--entrypoint','sleep',b.IMAGE,'infinity']);created=True
        b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name);checks.append({'check':'isolation_before','status':'PASS'})
        b.call(['start',name]);b.call(['exec',name,'mkdir','-p','/subject','/report','/opt/probe'])
        for lot in LOTS:b.call(['cp',b.local(root/'wp/outils/bascule'/lot),name+':/subject/'+lot])
        b.call(['cp',b.local(root/'wp/outils/bascule/audit'),name+':/subject/audit'])
        b.call(['cp',b.local(Path(__file__)),name+':/opt/probe/refusal-common.py'])
        p=b.call(['exec',name,'python3','/opt/probe/refusal-common.py','--inside'],check=False)
        (out/'execution.log').write_text(p.stdout+p.stderr,encoding='utf8');checks.append({'check':'native_exit','status':'PASS' if p.returncode==0 else 'FAIL','exit_code':p.returncode})
        b.call(['cp',name+':/report/refusal-common.json',b.local(out/'refusal-common.json')])
        b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name);checks.append({'check':'isolation_after','status':'PASS'})
    except Exception as e:checks.append({'check':'exception','status':'FAIL','detail':str(e)})
    finally:
        if created:
            info=json.loads(b.call(['inspect',name]).stdout)[0];assert info['Name']=='/'+name and info['Config']['Labels'].get(b.LABEL)==name
            b.call(['rm','-f',name]);p=b.call(['inspect',name],check=False);checks.append({'check':'cleanup','status':'PASS' if p.returncode!=0 and re.search('no such (object|container)',p.stderr,re.I) else 'FAIL'})
        checks.append({'check':'source_snapshot_stable','status':'PASS' if all(hashlib.sha256((root/k).read_bytes()).hexdigest()==v for k,v in source.items()) else 'FAIL'})
        receipt={'exit_code':int(any(c['status']!='PASS' for c in checks)),'checks':checks,'container':name,'sources':source}
        (out/'refusal-runner.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8');print(json.dumps(receipt['checks'],indent=2))
    return receipt['exit_code']

if __name__=='__main__':sys.exit(inside() if '--inside' in sys.argv else main())
