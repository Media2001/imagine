"""Narrow B01 work driver, no secrets and no unrelated deployment."""
from pathlib import Path
import sys, json, hashlib, subprocess
ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT/'production/B-01'
sys.path.insert(0,str(ROOT/'wp/outils/demo'))
from construire import wp, upload

def save(name,data):
    (PROOF/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

def snapshot(name):
    upload('imagine-demo-build/b00-integre-snapshot.php',(ROOT/'wp/tests/demo/b00-integre-snapshot.php').read_bytes())
    data=json.loads(wp('eval','require WP_CONTENT_DIR . "/imagine-demo-build/b00-integre-snapshot.php";')['stdout'])
    # Explicit C08 source preservation, including theme seam and parts.
    code='''$out=[]; foreach ([WP_PLUGIN_DIR . '/imagine-site/Paywall.php', ...glob(get_template_directory() . '/parts/paywall-*.php')] as $f) {$out[basename($f)]=hash_file('sha256',$f);} echo wp_json_encode($out);'''
    data['c08_code']=json.loads(wp('eval',code)['stdout'])
    save(name,data)
    return data

if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='before':
        snapshot('scope-before-runtime.json')
        code='''echo wp_json_encode(['url'=>home_url(),'wp'=>get_bloginfo('version'),'locale'=>get_locale(),'manifest'=>get_option('imagine_demo_manifest'),'c08'=>get_option('imagine_c08_fixture'),'posts'=>array_map(static fn($p)=>['id'=>$p->ID,'slug'=>$p->post_name,'date'=>$p->post_date,'key'=>get_post_meta($p->ID,'imagine_demo_key',true)],get_posts(['post_type'=>'post','numberposts'=>-1]))]);'''
        data=json.loads(wp('eval',code)['stdout']); save('baseline.json',data); print(json.dumps(data,ensure_ascii=False,indent=2))
    elif mode=='deploy-plugin':
        import base64
        code='''$out=[]; $files=glob(get_template_directory().'/*.php'); $files[]=get_template_directory().'/style.css'; $files[]=WP_PLUGIN_DIR.'/imagine-site/imagine-site.php'; foreach($files as $f){$out[str_replace(WP_CONTENT_DIR.'/', '',$f)]=base64_encode(file_get_contents($f));} echo wp_json_encode($out);'''
        backup=json.loads(wp('eval',code)['stdout']); save('runtime-backup-before-deployment.json',backup)
        expected=json.loads((PROOF/'scope-before-local.json').read_text())['wp/plugins/imagine-site/imagine-site.php']
        if hashlib.sha256(base64.b64decode(backup['plugins/imagine-site/imagine-site.php'])).hexdigest()!=expected:
            raise RuntimeError('Plugin bootstrap drift before deployment')
        hashes={}
        for name in ['NumeroPublication.php','imagine-site.php']:
            content=(ROOT/'wp/plugins/imagine-site'/name).read_bytes(); hashes[name]=hashlib.sha256(content).hexdigest()
            upload('plugins/imagine-site/'+name,content)
        code='''$out=[]; foreach(['NumeroPublication.php','imagine-site.php'] as $f){$p=WP_PLUGIN_DIR.'/imagine-site/'.$f; token_get_all(file_get_contents($p),TOKEN_PARSE);$out[$f]=hash_file('sha256',$p);} echo wp_json_encode($out);'''
        actual=json.loads(wp('eval',code)['stdout']); save('plugin-installation.json',{'expected':hashes,'actual':actual,'exact':actual==hashes})
        assert actual==hashes
        print('Targeted issue-date guard deployed and exact readback passed')
    elif mode=='after':
        before=json.loads((PROOF/'scope-before-runtime.json').read_text(encoding='utf-8'))
        after=snapshot('scope-after-runtime.json')
        save('scope-integrity.json',{'runtime_exact':before==after})
        print('protected runtime identical:',before==after)
        if before!=after: raise SystemExit(1)
    elif mode=='tests':
        for script in ['b01-corrections.py','test_b01_theme.py']:
            r=subprocess.run([sys.executable,str(ROOT/'wp/tests/demo'/script)],capture_output=True,text=True,encoding='utf-8')
            (PROOF/'tests'/(sys.argv[2]+'-'+script+'.txt')).write_text(r.stdout+r.stderr,encoding='utf-8')
            print(script,r.returncode,r.stdout+r.stderr)
    elif mode=='php':
        source=ROOT/'wp/tests/demo'/sys.argv[2]
        upload('imagine-demo-build/'+source.name,source.read_bytes())
        r=wp('eval','require WP_CONTENT_DIR . "/imagine-demo-build/'+source.name+'";',check=False)
        save('tests/'+sys.argv[3]+'.json',r); print(json.dumps(r,ensure_ascii=False))
        raise SystemExit(r['code'])
