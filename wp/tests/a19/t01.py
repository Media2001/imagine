"""Run only the A19 pure rules through the unchanged T01 root configuration.

Offline disposable container, existing prepared dependencies; never rebuilds T01.
The parent owns the full-suite and preparation gates.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
import uuid
import xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('a19_runner',HERE/'run.py');r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
TEST='wp/plugins/imagine-pilotage/tests/Administration/A19SubscriptionCoherenceTest.php'
OWN=r.OWN

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(r.ROOT);out.mkdir(parents=True,exist_ok=False)
    b=r.b;name='imagine-a19-t01-'+uuid.uuid4().hex[:12];created=False
    source=r.manifest(OWN);receipt={'scope':'A19-only; not the global T01 gate','checks':[],'exit_code':1}
    def check(key,ok,detail=None):
        receipt['checks'].append({'check':key,'status':'PASS' if ok else 'FAIL','detail':detail})
    try:
        image=json.loads(b.call(['image','inspect','imagine-tests-t01:1']).stdout)[0]
        assert image['Config']['Labels'].get('org.imagine.t01-image')=='1'
        assert not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
        b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pull','never','--entrypoint','sleep',image['Id'],'infinity']);created=True
        check('isolation_before',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
        b.call(['start',name]);b.call(['exec','-u','0',name,'mkdir','-p','/repo/wp/tests/a19','/repo/wp/outils/bascule/a19','/report','/work/wp/plugins','/opt/a19','/repo/wp/tests/t01'])
        b.call(['exec','-u','0',name,'chmod','0777','/report'])
        for p,dest in [(HERE/'unit.php','/repo/wp/tests/a19/unit.php'),(r.ROOT/'wp/outils/bascule/a19/Analysis.php','/repo/wp/outils/bascule/a19/Analysis.php'),(HERE/'t01-probe.php','/opt/a19/t01-probe.php')]:
            b.call(['cp',b.local(p),name+':'+dest])
        for f in ['executer.php','discovery.php']:b.call(['cp',b.local(r.ROOT/'wp/tests/t01'/f),name+':/repo/wp/tests/t01/'+f])
        b.call(['cp',b.local(r.ROOT/'wp/plugins/imagine-pilotage'),name+':/work/wp/plugins/imagine-pilotage'])
        b.call(['exec','-u','0',name,'cp','-a','/opt/t01/imagine-pilotage/vendor','/work/wp/plugins/imagine-pilotage/vendor'])
        pure=b.call(['exec',name,'php','-n','-d','disable_functions=file_put_contents,fopen,mkdir,rename,unlink,mail,exec,shell_exec,system,passthru,popen,proc_open','/opt/a19/t01-probe.php','--pure'],check=False)
        (out/'pure.log').write_text(pure.stdout+pure.stderr,encoding='utf-8')
        check('pure_no_extensions_database_network_writes',pure.returncode==0 and pure.stdout=='A19_PURE_NO_EXTENSIONS_NO_WRITES_OK\n' and pure.stderr=='')
        probe=b.call(['exec',name,'php','-r','define("T01_FUNCTIONS_ONLY", true); require "/opt/a19/t01-probe.php";'],check=False)
        (out/'discovery.log').write_text(probe.stdout+probe.stderr,encoding='utf-8');check('unchanged_t01_discovery_and_full_coverage',probe.returncode==0)
        command=['php','vendor/bin/phpunit','--configuration','phpunit.xml','--filter','A19SubscriptionCoherenceTest','--fail-on-warning','--fail-on-risky','--fail-on-deprecation','--fail-on-skipped','--fail-on-incomplete','--do-not-cache-result','--colors=never','--log-junit','/report/t01-junit.xml']
        p=b.call(['exec','-w','/work/wp/plugins/imagine-pilotage',name,*command],check=False)
        (out/'phpunit.log').write_text(p.stdout+p.stderr,encoding='utf-8');receipt['command']=command
        check('real_phpunit_exit',p.returncode==0,{'exit_code':p.returncode})
        copied=b.call(['cp',name+':/report/t01-junit.xml',b.local(out/'t01-junit.xml')],check=False)
        if copied.returncode==0:
            tree=ET.parse(out/'t01-junit.xml');cases=tree.findall('.//testcase');suite=tree.getroot().find('testsuite')
            receipt['cases']=[c.get('name') for c in cases]
            check('nine_named_pure_cases_discovered',len(cases)==9 and len(set(receipt['cases']))==9 and all(c.get('class','').endswith('A19SubscriptionCoherenceTest') for c in cases))
            check('nine_assertions_no_failures_errors_skips',sum(int(c.get('assertions','0')) for c in cases)==9 and not any(tree.findall('.//'+tag) for tag in ['failure','error','skipped']))
        else:check('fresh_junit_present',False)
        check('isolation_after',True,b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name))
    except Exception as error:check('exception',False,{'class':type(error).__name__,'code':str(error)[:180]})
    finally:
        if created:
            info=json.loads(b.call(['inspect',name]).stdout)[0];assert info['Config']['Labels'].get(b.LABEL)==name
            b.call(['rm','-f',name]);missing=b.call(['inspect',name],check=False)
            check('cleanup_exact_owned_runner',missing.returncode!=0 and re.search('no such (object|container)',missing.stderr,re.I) is not None)
        check('owned_sources_stable',source==r.manifest(OWN));receipt['sources']=source
        receipt['exit_code']=int(any(c['status']!='PASS' for c in receipt['checks']))
        (out/'t01.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
    return receipt['exit_code']

if __name__=='__main__':sys.exit(main())
