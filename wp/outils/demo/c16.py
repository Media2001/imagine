"""C16 targeted demo deployment; no global rebuild or library edits."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode=True
import profils
ROOT=profils.b00.ROOT
PROOF=ROOT/'production/C-16'
FILES=['CommandeRegles.php','CommandeNative.php','CommandeAdmin.php','SansEmail.php']

def wp(code):
    r=profils.b00.wp('eval',code)
    if r['stderr']: raise RuntimeError('PHP diagnostic; not exporting private output')
    return json.loads(r['stdout'])

def save(name,value):
    PROOF.mkdir(parents=True,exist_ok=True)
    (PROOF/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def upload(target,source):
    data=source.read_bytes()
    profils.b00.upload(target,data)
    digest=wp('$p=WP_CONTENT_DIR.'+json.dumps('/'+target)+';token_get_all(file_get_contents($p),TOKEN_PARSE);echo wp_json_encode(hash_file("sha256",$p));')
    assert digest==hashlib.sha256(data).hexdigest()
    return digest

def shared_contract():
    result=wp(r'''$out=['classes'=>[],'C16_mail'=>has_filter('pre_wp_mail',['Imagine\\Site\\SansEmail','filtrer'])!==false,'C16_refus'=>has_action('admin_post_imagine_c16_creer',['Imagine\\Site\\CommandeAdmin','refus'])!==false,'shared_sha256'=>[]];foreach(['CommandeRegles','SansEmail','CommandeNative','CommandeAdmin','Justificatifs','ExtractionsAdmin','TableauBordAdmin','MonCompte'] as $c){$out['classes'][$c]=class_exists('Imagine\\Site\\'.$c);}foreach(['plugins/imagine-site/imagine-site.php','imagine-demo-build/c09-seed.php'] as $p){$out['shared_sha256'][$p]=hash_file('sha256',WP_CONTENT_DIR.'/'.$p);}echo wp_json_encode($out);''')
    assert all(result['classes'].values()) and result['C16_mail'] and result['C16_refus'], 'Shared bootstrap contract missing; never overwrite successor lots'
    return result


def deploy():
    profils.guard('imagine-test-demo')
    before=shared_contract()
    hashes={}
    for name in FILES:
        hashes[name]=upload('plugins/imagine-site/'+name,ROOT/'wp/plugins/imagine-site'/name)
    hashes['c16-reset.php']=upload('imagine-demo-build/c16-reset.php',ROOT/'wp/outils/demo/c16-reset.php')
    after=shared_contract()
    assert before==after, 'Shared contract drift during C16-only deployment'
    save('installation-V2',{'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','sha256_readback':hashes,'shared_contract':after,'shared_files_uploaded':False,'theme_uploaded':False,'commercial_install':False})

if __name__=='__main__':
    if '--deploy' in sys.argv: deploy()
