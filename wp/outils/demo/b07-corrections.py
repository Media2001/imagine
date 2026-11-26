"""Corrections fusion21h41 : cible gardée, préimages durables, vraies recettes WP/HTTP."""
import sys
sys.dont_write_bytecode = True
import json, hashlib, importlib.util, re, html, os
from pathlib import Path
import b07
wp, php = b07.wp, b07.php
FILES = ['plugins/imagine-site/Agenda.php','plugins/imagine-site/AgendaConfidentialite.php','themes/imagine/single-imagine_evenement.php','themes/imagine/archive-imagine_evenement.php','themes/imagine/functions.php']
HERE = b07.ROOT/'production/B-07'
SPEC = importlib.util.spec_from_file_location('b07_http_corrections', b07.ROOT/'wp/outils/demo/b07-recette.py')
http = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(http)
def sources(): return b07.b06.hashes(FILES)
def business(): return b07.b06.state()
def deploy(label):
    identity = b07.b06.guard(); before = business()
    old = wp('$out=[];foreach('+php(FILES)+' as $n){$out[$n]=file_get_contents(WP_CONTENT_DIR."/".$n);}echo wp_json_encode($out);')
    # La source historique est conservée, pas remplacée par le reçu courant.
    manifest = json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
    for name in FILES[:-1]:
        assert hashlib.sha256(old[name].encode()).hexdigest() == manifest['files']['wp/'+name], 'Dérive avant correction : '+name
    local = {name:(b07.ROOT/'wp'/name).read_text(encoding='utf-8') for name in FILES}
    gate = "    if (get_post_type() !== 'imagine_partenaire') {\n        return $content;\n    }"
    replacement = "    $type = get_post_type();\n    if ($type !== 'imagine_partenaire'\n        && !($type === 'imagine_evenement' && get_post_meta(get_the_ID(), 'imagine_type', true) === 'partenaire')) {\n        return $content;\n    }"
    assert old[FILES[-1]].count(gate) == 1
    assert old[FILES[-1]].replace(gate, replacement) == local[FILES[-1]], 'Hors extension minimale B05 : refus'
    snap = b07.private(label, {'files':old,'database':b07.snapshot(),'business':before})
    for name in FILES:
        assert wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/'+name+'"));') == old[name], 'CAS avant écriture'
        b07.b06.profils.b00.upload(name,local[name].encode())
    actual = sources()
    checks = {'sources_relues_exactes':actual == {n:hashlib.sha256(local[n].encode()).hexdigest() for n in FILES}, 'etat_metier_preserve':before == business(), 'B05_extension_seule':True}
    b07.save(label, {'identity':identity,'sources':actual,'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if not v],'private_snapshot':snap})
    assert all(checks.values())
    print(json.dumps(checks))
def privacy(label):
    b07.b06.guard(); before = business(); database = b07.snapshot()
    snap = b07.private(label, {'database':database,'business':before})
    source = b07.ROOT/'wp/tests/demo/b07-corrections-privacy.php'; remote = 'imagine-demo-build/b07-corrections-privacy.php'
    b07.b06.profils.b00.upload(remote,source.read_bytes())
    assert b07.b06.hashes([remote])[remote] == hashlib.sha256(source.read_bytes()).hexdigest()
    p = b07.b06.profils.b00.wp('eval','require WP_CONTENT_DIR."/'+remote+'";',check=False)
    data = json.loads(p['stdout'])
    data['checks']['etat_metier_exact'] = before == business()
    data['checks']['evenements_et_metadonnees_exacts'] = {k:v for k,v in database.items() if k in ['posts','meta']} == {k:v for k,v in b07.snapshot().items() if k in ['posts','meta']}
    data.update(exit=p['code'],stderr=p['stderr'],sources=sources(),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),private_snapshot=snap)
    data['total'] = len(data['checks']); data['failures'] = [k for k,v in data['checks'].items() if not v]
    b07.save(label,data); print(json.dumps(data,ensure_ascii=False)); assert not data['failures'] and not data['error'] and not p['code']
def recipe(label):
    identity=b07.b06.guard(); before=business(); database=b07.snapshot(); initial=sources()
    admin=wp('echo wp_json_encode(get_user_by("login","admin")->ID);')
    snap=b07.private(label,{'database':database,'business':before,'sources':initial,'admin':admin})
    owned=[]; session=None; checks={}; error=None; observer='mu-plugins/b07-observer.php'
    assert wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+observer+'")&&get_option("imagine_b07_observer",null)===null);')
    raw=(b07.ROOT/'wp/tests/demo/b07-observer.php').read_bytes()+b'''\nadd_action('init', static function (): void { add_shortcode('imagine_b07_probe', static function (): string { $GLOBALS['b07_probe_count']=($GLOBALS['b07_probe_count']??0)+1; return '<strong id="b07-projection">Rendu fictif &amp; visible '.$GLOBALS['b07_probe_count'].'</strong>'; }); });\n'''
    digest=hashlib.sha256(raw).hexdigest()
    try:
        b07.b06.profils.b00.upload(observer,raw); assert b07.b06.hashes([observer])[observer]==digest
        empty={'mail':0,'http':0,'agenda_mail':0,'agenda_http':0,'transport_mail':0,'transport_http':0}
        control=wp('update_option("imagine_b07_observer",'+php(empty)+',false);wp_mail("b07-fictif@example.org","Sonde fictive","Aucun envoi");wp_remote_get("https://example.org/b07");echo wp_json_encode(get_option("imagine_b07_observer"));')
        checks['observateur_controle_positif']=control=={**empty,'mail':1,'http':1}
        wp('update_option("imagine_b07_observer",'+php(empty)+',false);echo "true";')
        session=wp('$id='+str(admin)+';$exp=time()+3600;$token=WP_Session_Tokens::get_instance($id)->create($exp);echo wp_json_encode(["token"=>$token,"cookie"=>LOGGED_IN_COOKIE."=".wp_generate_auth_cookie($id,$exp,"logged_in",$token)."; ".AUTH_COOKIE."=".wp_generate_auth_cookie($id,$exp,"auth",$token)]);')
        b07.private(label+'-session',session)
        links='<p><a id="b07-externe" href="https://outside.example.org/" rel="nofollow">Externe</a><a id="b07-ambigu" href=" https:////outside.example.org/">Ambigu</a><a id="b07-interne" href="/evenements/">Interne</a></p>'
        for key,kind,date in [('partenaire','partenaire','2020-01-01'),('rencontre','rencontre','2030-01-01'),('invalide','rencontre','2030-02-30')]:
            data={'post_type':'imagine_evenement','post_status':'publish','post_title':'B07 correction fictive '+key,'post_content':'[imagine_b07_probe]'+links,'meta_input':{'imagine_type':kind,'imagine_date':date,'imagine_heure':'12:00','imagine_lieu':'Lieu fictif correction B07','imagine_url_partenaire':'https://partner.example.org/b07/'}}
            obj=wp('$id=wp_insert_post('+php(data)+',true);if(is_wp_error($id)){throw new RuntimeException("Fixture refusée");}echo wp_json_encode(["id"=>$id,"path"=>wp_parse_url(get_permalink($id),PHP_URL_PATH)]);')
            owned.append({**obj,'key':key})
        for event in owned[:2]:
            code,headers,body,url=http.request(event['path']); parser=http.Inputs();parser.feed(body)
            checks[event['key']+'_fiche_reelle']=code==200 and 'id="evenement-'+str(event['id'])+'"' in body
            schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',body,re.S).group(1))
            visible=html.unescape(re.sub('<[^>]+>','',re.search(r'<strong id="b07-projection">(.*?)</strong>',body,re.S).group(1)))
            checks[event['key']+'_shortcode_execute_une_fois']=visible=='Rendu fictif & visible 1' and schema['description'].startswith(visible) and '[imagine_b07_probe]' not in schema['description']
            anchors={a.get('id'):a for a in parser.links if a.get('id')}
            checks[event['key']+'_liens_corps_regle_B05']=all(('sponsored' in anchors[k].get('rel','').split())==(event['key']=='partenaire') for k in ['b07-externe','b07-ambigu']) and 'sponsored' not in anchors['b07-interne'].get('rel','').split()
            if event['key']=='partenaire':
                checks['partenaire_passe_label_lien_sans_cloture']= 'Partenariat' in body and any(a.get('href')=='https://partner.example.org/b07/' and 'sponsored' in a.get('rel','').split() for a in parser.links) and 'inscriptions closes' not in body
                checks['partenaire_passe_sans_formulaire']='id="imagine-agenda-inscription"' not in body
                nonce=wp('wp_set_current_user(0);echo wp_json_encode(wp_create_nonce("imagine_agenda_'+str(event['id'])+'"));')
                result=http.request('/wp-admin/admin-post.php',data={'action':'imagine_agenda','evenement':event['id'],'imagine_agenda_nonce':nonce,'nom':'Fictif interdit','email':'b07-correction-http@example.org'})
                checks['partenaire_POST_direct_refuse']=result[0]==400
            else:
                checks['rencontre_formulaire_reel']='id="imagine-agenda-inscription"' in body
                data={k:parser.values[k] for k in ['action','evenement','imagine_agenda_nonce']};data.update(nom='Fictif correction B07',email='b07-correction-http@example.org')
                first=http.request('/wp-admin/admin-post.php',data=data); second=http.request('/wp-admin/admin-post.php',data={**data,'email':'B07-CORRECTION-HTTP@EXAMPLE.ORG'})
                checks['deux_POST_reels_meme_resultat']=first[0]==second[0]==200 and first[3]==second[3] and 'Votre demande a été enregistrée.' in html.unescape(first[2]) and first[2]==second[2]
                ids=wp('echo wp_json_encode(Imagine\\Site\\Agenda::inscriptions("b07-correction-http@example.org",'+str(event['id'])+'));')
                checks['doublon_une_ligne_native']=len(ids)==1
                code,h,adminbody,url=http.request('/wp-admin/edit.php?post_type=imagine_inscription',session)
                checks['inscription_visible_admin']=code==200 and 'post-'+str(ids[0]) in adminbody
        invalid=owned[2]
        code,h,body,url=http.request('/wp-admin/post.php?post='+str(invalid['id'])+'&action=edit',session)
        checks['saisie_invalide_alerte_admin_reelle']=code==200 and 'imagine-agenda-incomplet' in body and 'Type, date ou heure invalide' in body
        code,h,body,url=http.request('/evenements/')
        rows=re.findall(r'data-evenement="(\d+)"',body)
        checks['agenda_non_vide_exclut_saisie_invalide']=code==200 and str(owned[0]['id']) in rows and str(owned[1]['id']) in rows and str(invalid['id']) not in rows
        # Témoin applicatif : corriger la vraie métadonnée réintroduit la fiche à l'agenda et retire l'alerte.
        wp('update_post_meta('+str(invalid['id'])+',"imagine_date","2030-01-01");echo "true";')
        code,h,body,url=http.request('/evenements/')
        checks['temoin_saisie_corrigee_reintegree']=code==200 and str(invalid['id']) in re.findall(r'data-evenement="(\d+)"',body)
        code,h,body,url=http.request('/wp-admin/post.php?post='+str(invalid['id'])+'&action=edit',session)
        checks['temoin_saisie_corrigee_alerte_retiree']=code==200 and 'imagine-agenda-champs' in body and 'imagine-agenda-incomplet' not in body
        # Témoin applicatif de l'absence de formulaire partenaire : vrai changement type/date.
        partner=owned[0]['id']
        wp('update_post_meta('+str(partner)+',"imagine_type","rencontre");update_post_meta('+str(partner)+',"imagine_date","2030-01-01");echo "true";')
        code,h,body,url=http.request(owned[0]['path'])
        checks['temoin_partenaire_devenu_rencontre_formulaire_present']=code==200 and 'id="imagine-agenda-inscription"' in body
        counts=wp('echo wp_json_encode(get_option("imagine_b07_observer"));')
        checks['aucun_transport_sujet_reel']=all(counts[k]==0 for k in ['agenda_mail','agenda_http','transport_mail','transport_http'])
    except Exception as exc: error=type(exc).__name__+': '+str(exc)
    finally:
        # Nettoyage des seuls identifiants créés ; la préimage durable précède les sessions.
        ids=[p['id'] for p in owned]
        wp('$ids='+php(ids)+';foreach($ids as $id){foreach(get_posts(["post_type"=>"imagine_inscription","post_status"=>"any","numberposts"=>-1,"post_parent"=>$id]) as $p){wp_delete_post($p->ID,true);}wp_delete_post($id,true);}echo "true";')
        if session: wp('WP_Session_Tokens::get_instance('+str(admin)+')->destroy('+php(session['token'])+');echo "true";')
        # Préférence UI créée par Woo à la première visite admin seulement.
        if not any(int(r['user_id'])==admin and r['meta_key']=='meta-box-order_product' for r in database['usermeta']):
            wp('delete_user_meta('+str(admin)+',"meta-box-order_product");echo "true";')
        removed=b07.remove_observer(digest);wp('delete_option("imagine_b07_observer");echo "true";')
        checks['observateur_retire_relu']=removed and wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+observer+'")&&get_option("imagine_b07_observer",null)===null);')
        # Restaurer seulement les nouvelles préférences d'écran de nos visites, depuis la préimage.
        now=b07.snapshot()
        added=[r for r in now['usermeta'] if r not in database['usermeta'] and int(r['user_id'])==admin and r['meta_key'] in ['closedpostboxes_imagine_evenement','metaboxhidden_imagine_evenement','meta-box-order_imagine_evenement','screen_layout_imagine_evenement']]
        if added: wp('global $wpdb;foreach('+php(added)+' as $row){$wpdb->delete($wpdb->usermeta,["umeta_id"=>(int)$row["umeta_id"]]);}clean_user_cache('+str(admin)+');echo "true";')
        now=b07.snapshot()
        checks['evenements_et_metadonnees_restaurees_exactement']=all(now[k]==database[k] for k in ['posts','meta'])
        checks['etat_metier_exact']=before==business()
        checks['sources_exactes']=initial==sources()
    data={'identity':identity,'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if not v],'error':error,'sources':initial,'private_snapshot':snap,'transport_counts':locals().get('counts'),'created_ids':[p['id'] for p in owned]}
    b07.save(label,data);print(json.dumps(data,ensure_ascii=False));assert not data['failures'] and not error
if __name__=='__main__':
    assert sys.argv[1] in ['deploy','privacy','recipe']
    globals()[sys.argv[1]](sys.argv[2])
