"""C17 categories through the real C10 Settings API form and audit."""
from pathlib import Path
from html import unescape
import sys,json,re
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import c17_http as t
from urllib.parse import urlencode

def run(label='reglages-final'):
    t.c17.profils.guard('imagine-test-demo')
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    admin=t.h.login(accounts['E-ADMIN']);owner=t.h.login(accounts['P-SOL-ATT']);checks={}
    uid=t.c17.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["P-SOL-ATT"]);')
    before=t.c17.state();old=t.c17.wp('echo wp_json_encode(get_option("imagine_solidaire_categories",null));')
    try:
        s,_,page=t.h.fetch('/wp-admin/admin.php?page=imagine-reglages',admin)
        checks['champ_dans_formulaire_C10']=s==200 and 'name="imagine_solidaire_categories"' in page and 'à préciser' in unescape(page)
        nonce=unescape(re.search(r'name="_wpnonce" value="([^"]+)"',page).group(1))
        settings={'option_page':'imagine_reglages','action':'update','_wpnonce':nonce,'_wp_http_referer':'/wp-admin/admin.php?page=imagine-reglages'}
        native=t.c17.wp('$v=[];foreach((new Imagine\\Pilotage\\Administration\\Reglages())->defauts() as $k=>$d){$v[$k]=get_option($k,$d);}echo wp_json_encode($v);')
        for k,v in native.items():
            if isinstance(v,dict):settings.update({k+'['+a+']':b for a,b in v.items()})
            else:settings[k]='\n'.join(v)
        dec=t.c17.wp('echo wp_json_encode(Imagine\\Site\\Decouverte::reglages());')
        settings.update({'imagine_decouverte_reglages['+k+']':','.join(v) if isinstance(v,list) else v for k,v in dec.items()})
        settings['imagine_decouverte_relecture']=t.c17.wp('echo wp_json_encode(get_option("imagine_decouverte_relecture","fermee"));')
        settings['imagine_solidaire_categories']='à préciser\nÉtudiant fictif'
        s,_,_=t.h.fetch('/wp-admin/options.php',admin,urlencode(settings).encode())
        checks['POST_C10_persistant']=s==200 and t.c17.wp('echo wp_json_encode(Imagine\\Site\\JustificatifsReglages::categories());')==['à préciser','Étudiant fictif']
        s,_,_=t.upload(owner,t.form(owner),t.dummy_pdf('C17 CATEGORIE FICTIVE'),{'categorie':'Étudiant fictif'})
        checks['categorie_configuree_depot']=s==200 and t.stored(uid)['state']['categorie']=='Étudiant fictif'
        settings['imagine_solidaire_categories']=''
        t.h.fetch('/wp-admin/options.php',admin,urlencode(settings).encode())
        checks['vide_refuse_liste_conservee']=t.c17.wp('echo wp_json_encode(Imagine\\Site\\JustificatifsReglages::categories());')==['à préciser','Étudiant fictif']
        settings['imagine_solidaire_categories']='Interdite'
        settings['_wpnonce']='invalide'
        s,_,_=t.h.fetch('/wp-admin/options.php',admin,urlencode(settings).encode())
        checks['nonce_invalide_refuse']=s==403 and t.c17.wp('echo wp_json_encode(Imagine\\Site\\JustificatifsReglages::categories());')==['à préciser','Étudiant fictif']
        checks['journal_C10_operateur']=t.c17.wp('global $wpdb;$rows=$wpdb->get_col("SELECT option_value FROM {$wpdb->options} WHERE option_name LIKE \'imagine_reglages_journal_%\'");$out=false;foreach($rows as $row){$v=maybe_unserialize($row);if(($v["option"]??"")==="imagine_solidaire_categories"&&($v["qui_login"]??"")==="e-admin")$out=true;}echo wp_json_encode($out);')
    finally:
        t.c17.wp('$v=json_decode('+json.dumps(json.dumps(old))+',true);if($v===null){delete_option("imagine_solidaire_categories");}else{update_option("imagine_solidaire_categories",$v,false);}echo "true";')
        restore={k:v for k,v in before['options'].items() if not k.startswith('decouverte_')}
        t.c17.wp('$old=json_decode('+json.dumps(json.dumps(restore))+',true);foreach($old as $key=>$v){if($v===null){delete_option($key);}else{update_option($key,$v);}}echo "true";')
        t.c17.reset()
        checks['categories_restaurees']=t.c17.wp('echo wp_json_encode(get_option("imagine_solidaire_categories",null));')==old
        checks['autres_options_commercial_acces_preserves']=t.c17.state()==before
        result={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True]}
        t.c17.save(label,result);print(json.dumps(result,ensure_ascii=False))
    return int(bool(result['failures']))
if __name__=='__main__':sys.exit(run(sys.argv[1] if len(sys.argv)>1 else 'reglages-final'))
