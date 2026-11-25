"""Full HTTP/real SQL counters for twenty real articles, then exact owned cleanup."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
from urllib.parse import urlsplit
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
s=importlib.util.spec_from_file_location('m',HERE/'b04-http.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.work;w.guard()
python=sys.executable
seed=w.ROOT/'wp/outils/demo/b04.py'
def fixture(action,phase):
    r=subprocess.run([python,str(seed),action,phase],capture_output=True,text=True,encoding='utf-8',timeout=180)
    if r.returncode:raise RuntimeError('Fixture B04 failed: '+action)
    return json.loads(r.stdout)
source=HERE/'b04-query-http.php';target='imagine-demo-build/b04-query-http.php'
checks={};measurements={};created=False;uploaded=False
try:
    f=fixture('witness','witness');created=True
    ids=f['witness']['articles'];issue=f['witness']['id']
    checks['vingt_vrais_articles_distincts']=len(ids)==len(set(ids))==20
    # Same replay must preserve every owned id.
    replay=fixture('witness','witness-replay')
    checks['seed_rejouable_identifiants_stables']=replay['fixture']==f['fixture']
    r=subprocess.run([python,str(HERE/'b04-witness-test.py'),'green'],capture_output=True,text=True,encoding='utf-8',timeout=180)
    checks['fixture_native_verifiee']=r.returncode==0
    assert w.readback([target])[target] is None, 'Endpoint collision refused'
    w.c08.b00.upload(target,source.read_bytes());uploaded=True
    checks['instrumentation_octets_exacts']=w.readback([target])[target]==w.digest(source)
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients={'anonyme':None,'a-carte':m.http.login(accounts['A-CARTE']),'p-numero':m.http.login(accounts['P-NUMERO'])}
    for label,client in clients.items():
        code,headers,text=m.http.fetch('/wp-content/'+target,client)
        soup=m.BeautifulSoup(text,'html.parser')
        actual=[int(li['data-imagine-id']) for li in soup.select('#imagine-contents-list > li')]
        checks[label+':page_normale_20_articles']=code==200 and actual==ids
        checks[label+':compteur_reel']=headers.get('x-imagine-b04-issue')==str(issue) and int(headers.get('x-imagine-b04-queries','0'))>0
        checks[label+':HTML5']=not m.validate_html(text)
        checks[label+':pas_corps_reserve']='Corps réservé fictif B04' not in text
        checks[label+':aucun_PDF']='imagine_pdf=' not in text and '_imagine_pdf_blob' not in text
        measurements[label]={'full_request_sql':int(headers.get('x-imagine-b04-queries','0')),
            'template_sql':int(headers.get('x-imagine-b04-template-queries','0')),'articles':len(actual),'issue':issue,
            'instrumented_HTTP_status':code,'cache':headers.get('cache-control','')}
        # Check the uninstrumented normal route returns the very same list.
        _,_,normal=m.http.fetch(urlsplit(f['witness']['url']).path,client)
        ns=m.BeautifulSoup(normal,'html.parser')
        checks[label+':route_canonique_reelle']=[int(li['data-imagine-id']) for li in ns.select('#imagine-contents-list > li')]==ids
finally:
    if uploaded:
        # Same verified host mount as B00 uploads, exact byte CAS before unlink.
        remote_code=('from pathlib import Path;import hashlib;'
            'p=Path("/app/sites/imagine-test-demo/wp-content/'+target+'");'
            'assert hashlib.sha256(p.read_bytes()).hexdigest()=='+repr(w.digest(source))+';p.unlink();assert not p.exists();print("B04_REMOVED")')
        r=subprocess.run(['wsl.exe','docker','exec','staging-wp-dashboard','python','-c',remote_code],capture_output=True,text=True,timeout=60)
        checks['endpoint_temporaire_retire']=r.returncode==0 and r.stdout.strip()=='B04_REMOVED' and w.readback([target])[target] is None
    if created:
        cleanup=fixture('cleanup-witness','witness-cleanup')
        checks['vingt_et_numero_exacts_supprimes']=len(cleanup['exact_owned_deleted_ids'])==21 and cleanup['fixture']=={'product':f['fixture']['product']}
result={'scope':'imagine-test-demo','method':'Real HTTP front controller: SAVEQUERIES; native wp(), template-loader and exact theme; no SQL strings saved; counters include bootstrap vs template_redirect onward.',
        'total':len(checks),'checks':checks,'failures':[k for k,v in checks.items() if not v],'measurements':measurements,'fixture_article_ids':ids,'fixture_issue':issue}
(w.PROOF/'queries-20.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
if result['failures']:raise SystemExit(1)
