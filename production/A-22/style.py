import importlib.util,json,re,sys,uuid,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path('C:/Users/Ced/imagine')
spec=importlib.util.spec_from_file_location('b',ROOT/'wp/tests/a02-audit/run.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
b.LABEL='org.imagine.a22-streams'
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
name='imagine-a22-style-'+uuid.uuid4().hex[:12];created=False
receipt={'container':name,'checks':[],'exit_code':1}
def check(key,ok):receipt['checks'].append({'check':key,'status':'PASS' if ok else 'FAIL'})
try:
 image=json.loads(b.call(['image','inspect','imagine-tests-t01:1']).stdout)[0]
 assert image['Config']['Labels'].get('org.imagine.t01-image')=='1' and not image['Config'].get('Volumes') and not image['Config'].get('ExposedPorts')
 b.call(['create','--name',name,'--label',b.LABEL+'='+name,'--network','none','--no-healthcheck','--cap-drop','ALL','--security-opt','no-new-privileges','--pull','never','--entrypoint','sleep',image['Id'],'infinity']);created=True
 b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name);check('isolation_before',True)
 b.call(['start',name]);b.call(['exec','-u','0',name,'mkdir','/subject'])
 tool=json.loads(b.call(['exec',name,'php','-r',"echo json_encode(glob('/opt/t01/*/vendor/bin/phpcs'));"]).stdout)[0]
 files=['wp/outils/bascule/non-regression','wp/outils/bascule/a11/inventorier-adresses','wp/outils/bascule/stream_bridge.php'];mapping={}
 receipt['sources']={key:hashlib.sha256((ROOT/key).read_bytes()).hexdigest() for key in files}
 for i,p in enumerate(files):
  target='/subject/'+str(i)+'.php';b.call(['cp',b.local(ROOT/p),name+':'+target]);mapping[target]=p
  lint=b.call(['exec',name,'php','-l',target],check=False);check('lint:'+p,lint.returncode==0)
 p=b.call(['exec',name,'php',tool,'--standard=PSR12','--report=json',*mapping],check=False)
 (out/'phpcs.json').write_text(p.stdout,encoding='utf-8');(out/'stderr.log').write_text(p.stderr,encoding='utf-8')
 receipt['totals']=json.loads(p.stdout)['totals'];receipt['phpcs_exit']=p.returncode;check('strict_psr12',p.returncode==0)
 b.validate(json.loads(b.call(['inspect',name]).stdout)[0],name);check('isolation_after',True)
except Exception as e:check('exception:'+type(e).__name__,False)
finally:
 if created:
  info=json.loads(b.call(['inspect',name]).stdout)[0];assert info['Config']['Labels'].get(b.LABEL)==name
  b.call(['rm','-f',name]);p=b.call(['inspect',name],check=False);check('cleanup_exact_owned_runner',p.returncode!=0 and re.search('no such (object|container)',p.stderr,re.I) is not None)
 if 'sources' in receipt:check('executed_sources_stable',receipt['sources']=={key:hashlib.sha256((ROOT/key).read_bytes()).hexdigest() for key in receipt['sources']})
 receipt['exit_code']=int(any(x['status']!='PASS' for x in receipt['checks']))
 (out/'style.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt,indent=2))
sys.exit(receipt['exit_code'])
