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
FILES=['CommandeRegles.php','CommandeNative.php','CommandeAdmin.php','SansEmail.php','imagine-site.php']

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

def deploy():
    profils.guard('imagine-test-demo')
    hashes={}
    bootstrap=ROOT/'wp/plugins/imagine-site/imagine-site.php'
    before=wp('echo wp_json_encode(hash_file("sha256",WP_PLUGIN_DIR."/imagine-site/imagine-site.php"));')
    block="\nrequire_once __DIR__ . '/CommandeRegles.php';\nrequire_once __DIR__ . '/SansEmail.php';\nrequire_once __DIR__ . '/CommandeNative.php';\nrequire_once __DIR__ . '/CommandeAdmin.php';\nSansEmail::register();\nCommandeAdmin::register();\n"
    allowed={hashlib.sha256(bootstrap.read_bytes()).hexdigest(),hashlib.sha256(bootstrap.read_bytes().replace(block.encode(),b'')).hexdigest()}
    if before not in allowed: raise RuntimeError('Shared bootstrap drift: no overwrite')
    for name in FILES:
        hashes[name]=upload('plugins/imagine-site/'+name,ROOT/'wp/plugins/imagine-site'/name)
    hashes['c16-reset.php']=upload('imagine-demo-build/c16-reset.php',ROOT/'wp/outils/demo/c16-reset.php')
    hashes['c09-seed.php']=upload('imagine-demo-build/c09-seed.php',ROOT/'wp/outils/demo/c09-seed.php')
    # Idempotent marker upgrade only; never replay C09/C12/C14 seeds to deploy.
    marked=wp('$f=get_option("imagine_c09_fixture");$id=(int)$f["users"]["A-SANSMAIL"];if(get_user_meta($id,"_imagine_c09_fixture",true)!=="A-SANSMAIL")throw new RuntimeException("Foreign profile");update_user_meta($id,"imagine_sans_email","1");echo wp_json_encode(get_user_meta($id,"imagine_sans_email",true)==="1");')
    assert marked
    save('installation',{'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','sha256_readback':hashes,'A-SANSMAIL_marker':marked,'theme_uploaded':False,'commercial_install':False})

if __name__=='__main__':
    if '--deploy' in sys.argv: deploy()
