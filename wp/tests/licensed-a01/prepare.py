"""Prepare ONLY pinned public packages; never create/import a site."""
import concurrent.futures, datetime, hashlib, json, os, pathlib, subprocess, urllib.request, zipfile
ROOT = pathlib.Path(__file__).resolve().parent
BASE = 'sha256:b2ffa6ad01ffacc6d31b176232c8d0779c0320daba381e05cbbd80f56d5327a0'
URLS = {'wordpress.zip': 'https://wordpress.org/wordpress-7.0.9.zip', 'woocommerce.zip': 'https://downloads.wordpress.org/plugin/woocommerce.11.1.1.zip'}
EXPECTED={'wordpress.zip':('5a46f3c0443a321afa1f511ec3007fc636fdbd2e7598871020351edeffa1e1a0',31438844),'woocommerce.zip':('c5748c60a28c5d4b439109def3955c5a629f7cd66b919ae5aefa588bcaace710',18002436)}
work = pathlib.Path(os.environ['TMPDIR']) / 'imagine-a01-public-20261120'
work.mkdir(exist_ok=True)
def fetch(item):
    name,url=item; path=work/name
    if not path.exists():
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Imagine-offline-fixture/1.0'}),timeout=180) as r: path.write_bytes(r.read())
    with zipfile.ZipFile(path) as z:
        if z.testzip(): raise RuntimeError('ZIP corruption')
    digest=hashlib.sha256(path.read_bytes()).hexdigest();size=path.stat().st_size
    assert (digest,size)==EXPECTED[name],'Pinned public artifact mismatch: '+name
    return name, {'url':url,'sha256':digest,'bytes':size}
artifacts=dict(concurrent.futures.ThreadPoolExecutor(2).map(fetch,URLS.items()))
(work/'SHA256SUMS').write_text(''.join(v['sha256']+'  '+k+'\n' for k,v in artifacts.items()))
(work/'Dockerfile').write_text('FROM '+BASE+'\nLABEL org.imagine.synthetic-e2e="true"\nCOPY wordpress.zip woocommerce.zip SHA256SUMS /opt/compatible-public/\nRUN cd /opt/compatible-public && sha256sum -c SHA256SUMS && rm -rf /opt/wordpress /opt/woocommerce && mkdir /opt/wordpress /opt/woocommerce && unzip -q wordpress.zip -d /opt/wordpress && unzip -q woocommerce.zip -d /opt/woocommerce\nCMD ["sleep", "infinity"]\n')
def docker(args):
    p=subprocess.run(['wsl.exe','-d','Ubuntu','--','docker']+args,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=900)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    return p.stdout
wsl='/mnt/'+str(work).replace('\\','/')[0].lower()+str(work).replace('\\','/')[2:]
base_info=json.loads(docker(['image','inspect','imagine-staging-e2e-public:644662e9cc4f']))[0]
assert base_info['Id']==BASE
p=work/'Dockerfile'
p.write_text(p.read_text().replace('FROM '+BASE, 'FROM imagine-staging-e2e-public:644662e9cc4f'))
log=docker(['build','--network','none','--pull=false','-t','imagine-a01-compatible-public:20261120',wsl])
(ROOT/'prepare.log').write_text(log,encoding='utf8')
info=json.loads(docker(['image','inspect','imagine-a01-compatible-public:20261120']))[0]
assert not info['Config'].get('Volumes') and not info['Config'].get('ExposedPorts')
lock={'prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'base_image_id':BASE,'image_id':info['Id'],'artifacts':artifacts,'public_only':True,'no_site_created_during_prepare':True,'runtime_downloads':False}
(ROOT/'compatible.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
print(json.dumps(lock,indent=2))
