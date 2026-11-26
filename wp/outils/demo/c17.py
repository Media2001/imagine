"""C17 targeted code deployment, readback and two-profile documentary reset."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import re
import sys
sys.dont_write_bytecode=True
import profils
ROOT=profils.b00.ROOT
PROOF=ROOT/'production/C-17'
BLOCK="require_once __DIR__ . '/JustificatifRegles.php';\nrequire_once __DIR__ . '/JustificatifsReglages.php';\nrequire_once __DIR__ . '/Justificatifs.php';\nJustificatifsReglages::register();\nJustificatifs::register();\n\n"
SEED="if (is_file(__DIR__ . '/c17-profils.php') && class_exists(\\Imagine\\Site\\Justificatifs::class)) {\n    require_once __DIR__ . '/c17-profils.php';\n    \\Imagine\\Demo\\C17\\profils(true);\n}\n"
THEME='<ul data-imagine-factures><li><?php esc_html_e(\'Aucune facture disponible — raccord documentaire Odoo non disponible.\', \'imagine\'); ?></li></ul>\n<?php if (function_exists(\'do_action\')) { do_action(\'imagine_compte_justificatif\'); } ?>'
OLD_THEME='<ul data-imagine-factures><li><?php esc_html_e(\'Aucune facture ou justificatif disponible — raccord documentaire non disponible.\', \'imagine\'); ?></li></ul>'
def wp(code):
    r=profils.b00.wp('eval',code)
    if r['stderr']:raise RuntimeError('PHP diagnostic; private output not exported')
    return json.loads(r['stdout'])
def save(name,value):
    PROOF.mkdir(parents=True,exist_ok=True)
    (PROOF/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def targets():
    out={'plugins/imagine-site/'+n:ROOT/'wp/plugins/imagine-site'/n for n in ['JustificatifRegles.php','Justificatifs.php','JustificatifsReglages.php','PdfNumero.php','imagine-site.php']}
    out.update({'themes/imagine/parts/mon-compte.php':ROOT/'wp/themes/imagine/parts/mon-compte.php',
        'imagine-demo-build/c09-seed.php':ROOT/'wp/outils/demo/c09-seed.php',
        'imagine-demo-build/c17-profils.php':ROOT/'wp/outils/demo/c17-profils.php'})
    return out
def readback():
    names=list(targets())
    actual=wp('$o=[];foreach(json_decode('+json.dumps(json.dumps(names))+',true) as $n){$p=WP_CONTENT_DIR."/".$n;token_get_all(file_get_contents($p),TOKEN_PARSE);$o[$n]=hash_file("sha256",$p);}echo wp_json_encode($o);')
    assert actual=={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in targets().items()}
    return actual
def state():
    return wp(r'''$out=["commandes"=>[],"produits"=>[],"adherents"=>[],"profils"=>[],"options"=>[],"pdf"=>[]];
foreach(["shop_order","shop_subscription"] as $type){foreach(wc_get_orders(["type"=>$type,"limit"=>-1,"status"=>"any"]) as $o){$out["commandes"][$o->get_id()]=hash("sha256",serialize($o->get_data()));}}
foreach(wc_get_products(["limit"=>-1,"status"=>["publish","private","draft"]]) as $p){$out["produits"][$p->get_id()]=hash("sha256",serialize($p->get_data()));}
foreach(get_posts(["post_type"=>"wc_user_membership","post_status"=>"any","numberposts"=>-1]) as $p){$out["adherents"][$p->ID]=hash("sha256",serialize([$p,get_post_meta($p->ID)]));}
$f=get_option("imagine_c09_fixture");$out["manifeste"]=$f;
foreach($f["users"] as $k=>$id){$u=get_userdata($id);$out["profils"][$k]=[$id,$u->roles];$out["options"]["decouverte_".$id]=get_option("imagine_decouverte_compte_".$id,null);}
foreach(["imagine_acces_reglages","imagine_c05_reglages","imagine_envoi_colonnes_export","imagine_decouverte_reglages","imagine_decouverte_relecture","imagine_achat_remboursement","imagine_demo_calendrier"] as $k){$out["options"][$k]=get_option($k,null);}
foreach(glob(Imagine\Site\PdfNumero::directory()."/*.pdf") as $p){$out["pdf"][basename($p)]=hash_file("sha256",$p);}
global $wpdb;$out["reserve_native_C09_action8103"]=$wpdb->get_row("SELECT action_id,status,scheduled_date_gmt,last_attempt_gmt FROM {$wpdb->prefix}actionscheduler_actions WHERE action_id=8103",ARRAY_A);
ksort($out["commandes"]);ksort($out["produits"]);ksort($out["adherents"]);echo wp_json_encode($out);''')
def reset():
    return wp('require_once WP_CONTENT_DIR."/imagine-demo-build/c17-profils.php";echo wp_json_encode(Imagine\\Demo\\C17\\profils(true));')
def deploy():
    profils.guard('imagine-test-demo')
    before=state();old={}
    previous=json.loads((PROOF/'installation.json').read_text(encoding='utf-8')) if (PROOF/'installation.json').is_file() else None
    if previous:
        assert previous['scope']=='imagine-test-demo'
        stamp=re.sub(r'[^0-9]','',previous['at'])
        archived=PROOF/('installation-'+stamp+'.json')
        if not archived.exists():save(archived.stem,previous)
    for name,path in targets().items():
        data=path.read_bytes();text=data.decode('utf-8')
        if name.endswith('imagine-site.php'):prior=text.replace(BLOCK,'')
        elif name.endswith('c09-seed.php'):prior=text.replace(SEED,'')
        elif name.endswith('PdfNumero.php'):prior=text.replace('public static function privateHeaders()', 'private static function privateHeaders()')
        elif name.endswith('mon-compte.php'):prior=text.replace(THEME,OLD_THEME)
        else:prior=None
        current=wp('$p=WP_CONTENT_DIR.'+json.dumps('/'+name)+';echo wp_json_encode(is_file($p)?hash_file("sha256",$p):null);')
        allowed={hashlib.sha256(data).hexdigest()}
        if prior is not None:allowed.add(hashlib.sha256(prior.encode()).hexdigest())
        if previous and name in previous['sha256_readback']:allowed.add(previous['sha256_readback'][name])
        if current is not None and current not in allowed:raise RuntimeError('Source drift; refusing overwrite: '+name)
        old[name]=current
    # Dependencies first, shared bootstrap last. No other theme or global seed.
    files=targets();bootstrap=files.pop('plugins/imagine-site/imagine-site.php');files['plugins/imagine-site/imagine-site.php']=bootstrap
    for name,path in files.items():profils.b00.upload(name,path.read_bytes())
    hashes=readback()
    fixtures=wp('require_once WP_CONTENT_DIR."/imagine-demo-build/c17-profils.php";echo wp_json_encode(Imagine\\Demo\\C17\\profils());')
    after=state();assert before==after,'Commercial/access/native state drift'
    result={'at':datetime.now(timezone.utc).isoformat(),'scope':'imagine-test-demo','sha256_before':old,'sha256_readback':hashes,
        'before':before,'after':after,'etat_commercial_acces_preserve':before==after,'fixtures':fixtures,'global_seed_replayed':False}
    save('installation',result);print(json.dumps({'installed':len(hashes),'readback':True,'state_preserved':True}))
if __name__=='__main__':
    if '--deploy' in sys.argv:deploy()
    elif '--reset' in sys.argv:
        profils.guard('imagine-test-demo');a=state();s=reset();b=state();assert a==b;save('reset-manuel',{'states':s,'native_preserved':a==b});print('C17 reset: two synthetic documentary profiles only; native state preserved')
    else:
        profils.guard('imagine-test-demo');save('readback',{'sha256_readback':readback(),'state':state()});print('C17 exact source readback verified')
