"""Final C15 correction replay: authorized T01 preparation, then real isolated/native/HTTP tests."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
import c15


def sources():
    paths=list((ROOT/'wp/plugins/imagine-site').glob('Echeances*.php'))
    paths+=list((ROOT/'wp/plugins/imagine-site/tests').glob('Echeances*Test.php'))
    paths+=list((ROOT/'wp/tests/demo').glob('c15*'))
    paths+=list((ROOT/'wp/outils/demo').glob('c15*'))
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}


def native_files():
    return c15.wp(r'''$out=[];foreach([WP_CONTENT_DIR.'/themes/imagine',WP_PLUGIN_DIR.'/imagine-site'] as $dir){foreach(new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir,FilesystemIterator::SKIP_DOTS)) as $p){if($p->isFile()&&!str_contains($p->getPathname(),'/vendor/')&&!in_array($p->getFilename(),['EcheancesRegles.php','EcheancesNatives.php','EcheancesAdmin.php'],true))$out[$p->getPathname()]=hash_file('sha256',$p->getPathname());}}ksort($out);echo wp_json_encode($out);''')


def main():
    c15.profils.guard('imagine-test-demo')
    result={'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','status':'RUNNING','sources':sources()}
    protected=native_files()
    baseline=c15.load_test('c15-action').snapshot()
    c15.save('corrections-final-before',{'protected_files':protected,'semantic':baseline})
    def powershell(script,label):
        p=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'wp/tests'/script)],capture_output=True,text=True,encoding='utf-8',errors='replace')
        text=p.stdout+p.stderr
        (c15.PROOF/(label+'.log')).write_text(text,encoding='utf-8')
        result[label]={'exit':p.returncode}
        c15.save('corrections-final',result)
        print(label,': exit',p.returncode,flush=True)
        if p.returncode:
            raise RuntimeError(label+' failed; see exact log')
        return text
    try:
        powershell('preparer-image.ps1','corrections-preparation-image')
        text=powershell('rejouer.ps1','corrections-t01')
        markers=re.findall(r'^T01_RESULT (\{[^\r\n]+\})',text,re.M)
        if len(markers)!=1:
            raise RuntimeError('T01 summary missing/ambiguous')
        result['T01']=json.loads(markers[0])
        if not result['T01']['pass'] or 'Imagine.Site.Tests.EcheancesReglesTest' not in text:
            raise RuntimeError('C15 PHPUnit discovery/execution not proven')
        result['T01_C15_discovered']=True
        spec=importlib.util.spec_from_file_location('c15_pure',ROOT/'wp/outils/demo/c15-unit.py')
        pure=importlib.util.module_from_spec(spec);spec.loader.exec_module(pure)
        result['standalone_pure']=pure.run('corrections-pure-final')
        if c15.load_test('c15-t01').run('corrections-phpunit-final'):
            raise RuntimeError('C15 pure PHPUnit failed')
        c15.deploy()
        phases=[('paper','c15-witness',()),('action','c15-action',()),('concurrent','c15-concurrent',()),('native_false','c15-concurrent',(True,)),('french','c15-labels',())]
        for key,module,extra in phases:
            if key=='action':
                checks=c15.load_test(module).verify()
                result[key]={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True]}
                c15.save('corrections-action-final',result[key])
            else:
                label='corrections-'+key+'-final'
                if not c15.load_test(module).verify(label,*extra):
                    raise RuntimeError(key+' failed')
                result[key]=json.loads((c15.PROOF/(label+'.json')).read_text(encoding='utf-8'))
            c15.save('corrections-final',result)
        result['runtime']=c15.runtime('corrections-runtime-final')
        result['HTTP']=c15.load_test('c15-http').verify()
        c15.save('corrections-http-final',{'checks':result['HTTP'],'total':len(result['HTTP']),'failures':[k for k,v in result['HTTP'].items() if v is not True]})
        raw=c15.profils.b00.wp('eval','require WP_CONTENT_DIR."/imagine-demo-build/c09-payments.php";',check=False)
        native=json.loads(raw['stdout'])
        if raw['code'] or raw['stderr'] or native['failures']:
            raise RuntimeError('C09 native payment readback failed')
        result['C09']={'total':native['total'],'failures':native['failures'],'exit':raw['code']}
        result['protected_remote_files_unchanged']=protected==native_files()
        result['all_fixture_semantics_exact']=baseline==c15.load_test('c15-action').snapshot()
        result['sources_unchanged_during_replay']=result['sources']==sources()
        result['no_temporary_MU']=c15.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/mu-plugins/imagine-c15-concurrent-witness.php"));')
        if not all(result[k] is True for k in ['protected_remote_files_unchanged','all_fixture_semantics_exact','sources_unchanged_during_replay','no_temporary_MU']):
            raise RuntimeError('Final preservation/source seal failed')
        result['theme_written']=False
        result['shared_bootstrap_written']=False
        result['C09_source_written']=False
        result['global_C09_reset']=False
        result['status']='PRET_RELECTURE_CORRECTIONS'
    except BaseException as error:
        result['status']='FAILED'
        result['error']=str(error)
        raise
    finally:
        result['finished_at']=datetime.now(timezone.utc).isoformat()
        c15.save('corrections-final',result)
    print(json.dumps({'status':result['status'],'T01':result['T01'],'runtime':len(result['runtime']),'HTTP':len(result['HTTP']),'C09':result['C09']},ensure_ascii=False),flush=True)

if __name__=='__main__':
    main()
