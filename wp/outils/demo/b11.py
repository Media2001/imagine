"""B11 : transport gardé existant, aucun autre site ni lot écrit."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
from pathlib import Path
import b10
ROOT=b10.ROOT
OUT=ROOT/'production/B-11'
wp,php,guard,upload,state=b10.wp,b10.php,b10.guard,b10.upload,b10.state
FILES=['plugins/imagine-site/'+n for n in ['MediasRegles.php','Medias.php','AudioNumero.php','imagine-site.php']]+['themes/imagine/single.php','themes/imagine/single-imagine_numero.php']
BLOCK="// B11 — liens sans oEmbed et audio privé réutilisant C11/C06.\nrequire_once __DIR__ . '/MediasRegles.php';\nrequire_once __DIR__ . '/Medias.php';\nrequire_once __DIR__ . '/AudioNumero.php';\nMedias::register();\nAudioNumero::register();\n\n"


def save(label,data):
    OUT.mkdir(exist_ok=True)
    p=OUT/(label+'.json')
    assert not p.exists(),p
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')


def sources():
    files=[ROOT/'wp'/n for n in FILES]
    for pat in ['wp/outils/demo/b11*','wp/tests/demo/b11*','wp/plugins/imagine-site/tests/MediasB11*']:
        files.extend(p for p in ROOT.glob(pat) if p.is_file())
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


def private(label,data):
    import tempfile
    root=Path(os.environ.get('TMPDIR') or str(Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData/Local')))/'hermes/cache/scratch'))
    root.mkdir(parents=True,exist_ok=True)
    assert ROOT.resolve() not in [root.resolve(),*root.resolve().parents]
    folder=Path(tempfile.mkdtemp(prefix='b11-private-',dir=root))
    raw=json.dumps({'label':label,'scope':'imagine-test-demo','payload':data},ensure_ascii=False).encode()
    path=folder/'snapshot.json'
    with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    os.chmod(path,0o600)
    assert path.read_bytes()==raw
    return {'file':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'private':True}


def inspect(label):
    data=wp('''$u=get_option('imagine_c09_fixture')['users'];$out=['users'=>$u,'issues'=>[],'purchases'=>Imagine\\Site\\AchatsNumeros::droits((int)$u['P-NUMERO'])];foreach(get_posts(['post_type'=>'imagine_numero','numberposts'=>-1]) as $p){$out['issues'][]=['id'=>$p->ID,'slug'=>$p->post_name,'url'=>get_permalink($p)];}echo wp_json_encode($out);''')
    save(label,data);print(json.dumps(data,ensure_ascii=False))


def deploy(label):
    identity=guard(); before=state()
    old=wp('$o=[];foreach('+php(FILES)+' as $n){$p=WP_CONTENT_DIR."/".$n;$o[$n]=is_file($p)?file_get_contents($p):null;}echo wp_json_encode($o);')
    local={n:(ROOT/'wp'/n).read_text(encoding='utf-8') for n in FILES}
    assert old[FILES[3]] in [local[FILES[3]],local[FILES[3]].replace(BLOCK,'')], 'Bootstrap divergent'
    for n in FILES[:3]:assert old[n] in [None,local[n]],n
    single=local[FILES[4]].replace("        <?php echo class_exists('Imagine\\Site\\Medias') ? \\Imagine\\Site\\Medias::rendre(get_post()) : ''; ?>\n",'')
    issue=local[FILES[5]].replace("    <?php echo class_exists('Imagine\\Site\\Medias') ? \\Imagine\\Site\\Medias::rendre($issue) : ''; ?>\n",'').replace("        <?php echo class_exists('Imagine\\Site\\AudioNumero') ? \\Imagine\\Site\\AudioNumero::lecteur($issue) : ''; ?>","        <p><?php esc_html_e('Emplacement du sommaire audio — aucun enregistrement fourni.', 'imagine'); ?></p>")
    single='\n'.join(line for line in local[FILES[4]].split('\n') if 'Medias::rendre(get_post())' not in line)
    issue='\n'.join(line if 'AudioNumero::lecteur($issue)' not in line else "        <p><?php esc_html_e('Emplacement du sommaire audio — aucun enregistrement fourni.', 'imagine'); ?></p>" for line in local[FILES[5]].split('\n') if 'Medias::rendre($issue)' not in line)
    assert old[FILES[4]] in [local[FILES[4]],single], 'Article divergent'
    assert old[FILES[5]] in [local[FILES[5]],issue], 'Numéro divergent'
    snapshot=private(label,{'files':old,'business':before})
    save(label+'-avant',{'identity':identity,'private_snapshot':snapshot,'hashes':{n:hashlib.sha256(v.encode()).hexdigest() if v is not None else None for n,v in old.items()}})
    for n in FILES:upload(n,(ROOT/'wp'/n).read_bytes())
    actual=b10.b09.b08.c25.b06.hashes(FILES)
    assert actual=={n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in FILES}
    assert state()==before
    save(label,{'identity':identity,'readback':actual,'business_preserved':True})
    print('B11 code relu :',len(actual))


def seed(label):
    guard();src=(ROOT/'wp/outils/demo/b11-seed.php').read_text().split('<?php',1)[1]
    before=state();snapshot=private(label,{'business':before,'existing':wp('echo wp_json_encode(get_option("imagine_b11_fixture",null));')})
    first=wp(src);second=wp(src)
    assert first==second
    save(label,{'fixture':first,'idempotent':True,'private_snapshot':snapshot})
    print(json.dumps(first,ensure_ascii=False))


def runtime(label):
    guard();f=wp('echo wp_json_encode(get_option("imagine_b11_fixture"));');before=state()
    code='''global $wpdb;$wpdb->query('START TRANSACTION');try{$GLOBALS['b11_issue']='''+str(f['issue'])+''';$GLOBALS['b11_article']='''+str(f['article'])+''';eval('''+php((ROOT/'wp/tests/demo/b11-runtime.php').read_text().split('<?php',1)[1])+''');}finally{$wpdb->query('ROLLBACK');wp_cache_flush();}'''
    r=b10.b09.b08.c25.b06.profils.b00.wp('eval',code,check=False)
    save(label,{'native':r,'business_preserved':before==state(),'sources':sources()})
    print(json.dumps(r,ensure_ascii=False));assert r['code']==0 and not r['stderr'] and before==state()

if __name__=='__main__':globals()[sys.argv[1]](sys.argv[2])
