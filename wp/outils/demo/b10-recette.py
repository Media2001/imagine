"""B10 : vrais formulaires navigateur, import HTTP multipart, réseau observé, readback WP."""
import sys
sys.dont_write_bytecode=True
import json
import hashlib
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import b10


def run(label):
    identity=b10.guard();business=b10.recette_state();nav=b10.navigation()
    observer='mu-plugins/b10-observer.php'
    assert not (b10.OUT/(label+'.json')).exists()
    assert b10.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR."/'+observer+'"));') is False
    sessions=b10.wp('''global $wpdb;$out=[];foreach(['admin'=>get_users(['role'=>'administrator','number'=>1])[0]->ID,'lecteur'=>28] as $k=>$id){$u=get_userdata($id);if(!$u||!str_ends_with($u->user_email,'@example.org')){throw new RuntimeException('Compte fictif requis');}$out[$k]=['id'=>$id,'rows'=>$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key='session_tokens'",$id),ARRAY_A)];}echo wp_json_encode($out);''')
    owned=b10.wp('echo wp_json_encode(["ids"=>get_option(Imagine\\Site\\PointsVente::ACTIFS),"rows"=>Imagine\\Site\\PointsVente::lignes(),"config"=>get_option(Imagine\\Site\\PointsVente::CONFIG),"pending"=>get_option(Imagine\\Site\\PointsVente::NETTOYAGE,null)]);')
    assert b10.wp('echo wp_json_encode(get_option("imagine_b10_refus_suppression",null));') is None
    durable=b10.b09.b08.c25.b06.private_snapshot(label, {'sessions':sessions,'owned':owned,'business':business})
    auth={}; checks={}; browser_requests=[]; outgoing=[]; maps={}; cleanup={}
    try:
        b10.upload(observer,(b10.ROOT/'wp/tests/demo/b10-observer.php').read_bytes())
        positive=b10.wp("wp_mail('fictif@example.org','Fictif','Fictif');wp_remote_get('https://example.org/');$v=get_option('imagine_b10_observations');delete_option('imagine_b10_observations');echo wp_json_encode($v);")
        checks['observateur_serveur_temoin_positif']=positive=={'ambiance_mail':1,'ambiance_http':1}
        auth=b10.wp("$out=[];foreach("+b10.php({k:v['id'] for k,v in sessions.items()})+" as $k=>$id){$t=WP_Session_Tokens::get_instance($id)->create(time()+3600);$out[$k]=[LOGGED_IN_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'logged_in',$t),AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'auth',$t),SECURE_AUTH_COOKIE=>wp_generate_auth_cookie($id,time()+3600,'secure_auth',$t)];}echo wp_json_encode($out);")
        with sync_playwright() as p:
            try: browser=p.chromium.launch(headless=True)
            except Exception: browser=p.chromium.launch(headless=True,channel='msedge')
            def context(role='',mobile=False):
                ctx=browser.new_context(viewport={'width':390,'height':844} if mobile else {'width':1280,'height':900})
                def route(r):
                    u=r.request.url
                    if urlsplit(u).netloc != urlsplit(identity['url']).netloc:
                        outgoing.append(u);r.abort()
                    else: r.continue_()
                ctx.route('**/*',route)
                ctx.on('request',lambda r:browser_requests.append(r.url))
                if role: ctx.add_cookies([{'name':k,'value':v,'url':identity['url']} for k,v in auth[role].items()])
                return ctx
            admin=context('admin'); page=admin.new_page()
            settings=identity['url']+'/wp-admin/options-general.php?page=imagine-points-vente'
            response=page.goto(settings);page.wait_for_load_state('networkidle')
            checks['ecran_natif_admin']=response.status==200 and page.locator('h1').inner_text()=='Points de vente'
            mapping=json.loads((b10.OUT/'mapping-exemple.json').read_text(encoding='utf-8'))
            def config(value):
                page.goto(settings)
                page.locator('textarea[name=mapping]').fill(json.dumps(mapping,ensure_ascii=False))
                page.locator('select[name=separateur]').select_option(';')
                page.locator('select[name=carte]').select_option(value)
                page.locator('button[value=enregistrer]').click();page.wait_for_load_state('networkidle')
                assert page.get_by_role('status').inner_text()=='Configuration enregistrée.'
                actual=b10.wp('echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::CONFIG));')
                assert actual=={'mapping':mapping,'separateur':';','carte':value}
            def upload(content=None):
                page.goto(settings)
                if content is None:page.locator('input[name=csv]').set_input_files(str(b10.OUT/'commerces-fictifs.csv'))
                else: page.locator('input[name=csv]').set_input_files({'name':'fictif.csv','mimeType':'text/csv','buffer':content.encode()})
                page.locator('button[value=importer]').click();page.wait_for_load_state('networkidle')
                return page.content()
            config('0')
            # Commerce personnel fictif ciblé ; trois requêtes de recherche Unicode réelles.
            fictive='enseigne;rue;ville;cp;personne\nCommerce fictif Unicode;Rue inventée;Ḉœur-Æther-Fictif;00000;PERSONNE_FICTIVE_A_EFFACER\n'
            old=b10.wp('$m='+b10.php(mapping | {'personne':'personne'})+';Imagine\\Site\\PointsVente::importer('+b10.php(fictive)+',$m,";");echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::ACTIFS)[0]);')
            early=context();unicode_page=early.new_page();unicode_found=[]
            for term in ['Ḉœur-Æther-Fictif','C\u0327\u0301œur-Æther-Fictif','coeur-aether-fictif']:
                unicode_page.goto(identity['url']+'/points-de-vente/?localite='+__import__('urllib.parse',fromlist=['quote']).quote(term))
                unicode_found.append(unicode_page.locator('#imagine-points-vente > li').all_inner_texts())
            checks['recherche_nfc_nfd_hors_table_oe_ae_native']=all(len(v)==1 and v==unicode_found[0] for v in unicode_found)
            b10.wp('update_option("imagine_b10_refus_suppression",'+str(old)+',false);echo wp_json_encode(get_option("imagine_b10_refus_suppression"));')
            first=upload()
            ids=b10.wp('echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::ACTIFS));')
            residue=b10.wp('echo wp_json_encode([get_option(Imagine\\Site\\PointsVente::NETTOYAGE),get_post_meta('+str(old)+',"imagine_vente_ligne",true)]);')
            checks['bascule_reussie_nettoyage_refuse_persistant']=len(ids)==30 and 'Liste remplacée ; nettoyage incomplet.' in first and 'Opération refusée' not in first and residue[0]==[old] and residue[1]['personne']=='PERSONNE_FICTIVE_A_EFFACER'
            incomplete=upload()
            checks['rejeu_identique_retente_sans_nouveaux_ids']='Liste inchangée ; nettoyage incomplet.' in incomplete and b10.wp('echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::ACTIFS));')==ids
            b10.wp('delete_option("imagine_b10_refus_suppression");echo wp_json_encode(get_option("imagine_b10_refus_suppression",null)===null);')
            resumed=upload()
            recovered=b10.wp('echo wp_json_encode([get_option(Imagine\\Site\\PointsVente::ACTIFS),get_option(Imagine\\Site\\PointsVente::NETTOYAGE),get_post('+str(old)+'),metadata_exists("post",'+str(old)+',"imagine_vente_ligne")]);')
            checks['reprise_autre_requete_supprime_post_meta_ids_stables']=recovered==[ids,[],None,False] and 'nettoyage incomplet' not in resumed
            # Une méta active cassée est réparée par le vrai formulaire de remplacement.
            b10.wp('delete_post_meta('+str(ids[0])+',"imagine_vente_ligne");echo wp_json_encode(metadata_exists("post",'+str(ids[0])+',"imagine_vente_ligne"));')
            repaired=upload()
            repaired_ids=b10.wp('echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::ACTIFS));')
            checks['import_repare_liste_illisible']='Opération refusée' not in repaired and len(repaired_ids)==30 and repaired_ids!=ids
            ids=repaired_ids
            checks['CSV_multipart_30_et_ligne32_refusee']=len(ids)==30 and '30 lignes prises ; 1 refusées.' in first and 'Ligne 32 : Nombre de colonnes incorrect.' in first
            checks['refus_sans_recopie_donnee']='REFUS_DONNEE_NE_JAMAIS_AFFICHER' not in first
            second=upload()
            checks['rechargement_30_ids_identiques']=ids==b10.wp('echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::ACTIFS));') and '30 lignes prises ; 1 refusées.' in second
            malformed=upload('colonne;inconnue\nseulement;fictif\n')
            checks['mauvaise_entete_conserve_liste']='Opération refusée' in malformed and ids==b10.wp('echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::ACTIFS));')
            refused=upload('enseigne;rue;ville;cp;personne;telephone\nSECRET;incomplet\n')
            checks['tous_refuses_comptes_numerotes_sans_remplacement']='0 lignes prises ; 1 refusées.' in refused and 'Ligne 2 : Nombre de colonnes incorrect.' in refused and 'SECRET' not in refused and ids==b10.wp('echo wp_json_encode(get_option(Imagine\\Site\\PointsVente::ACTIFS));')
            # Vrai POST avec nonce invalide, configuration inchangée.
            page.goto(settings)
            page.locator('form').filter(has=page.locator('textarea[name=mapping]')).locator('input[name=_b10]').evaluate("e=>e.value='invalide'")
            page.locator('select[name=carte]').select_option('1');page.locator('button[value=enregistrer]').click();page.wait_for_load_state('networkidle')
            checks['nonce_invalide_refuse']='Opération refusée' in page.content() and b10.wp('echo wp_json_encode(Imagine\\Site\\PointsVente::configuration()["carte"]);')=='0'
            reader=context('lecteur');rpage=reader.new_page();r=rpage.goto(settings)
            checks['lecteur_sans_acces_import']=r.status==403 and rpage.locator('input[name=csv]').count()==0
            anonymous=context();public=anonymous.new_page();response=public.goto(identity['url']+'/points-de-vente/');public.wait_for_load_state('networkidle')
            checks['page_publique_30_et_declaration_fictive']=response.status==200 and public.locator('#imagine-points-vente > li').count()==30 and 'entièrement fictifs' in public.content()
            checks['colonnes_personnelles_absentes']='PERSONNE_NON_MAPPEE_' not in public.content() and 'TEL_FICTIF_NON_MAPPE_' not in public.content()
            checks['antislash_affichage']='Librairie fictive \\ Étoile' in public.locator('#imagine-points-vente').inner_text()
            localities=public.locator('#imagine-points-vente > li').all_inner_texts()
            checks['tri_localite_initial']='Étoile-Fictive' in localities[0] and 'Zéphyr-Inventé' in localities[-1]
            found=[]
            for term in ['Étoile-Fictive','etoile-fictive','ETOILE-FICTIVE','E\u0301toile-Fictive','00001']:
                public.locator('input[name=localite]').fill(term);public.get_by_role('button',name='Rechercher',exact=True).click();public.wait_for_load_state('networkidle')
                found.append(public.locator('#imagine-points-vente > li').all_inner_texts())
            checks['recherche_accent_casse_postal_exact']=all(len(v)==5 and v==found[0] for v in found)
            for term in ['000','étoile','<script>fictif</script>']:
                public.locator('input[name=localite]').fill(term);public.get_by_role('button',name='Rechercher',exact=True).click()
                checks['recherche_sans_prefixe_'+term]=public.locator('#imagine-points-vente > li').count()==0
            for value in ['0','1']:
                config(value)
                start=len(browser_requests);external=len(outgoing)
                public.goto(identity['url']+'/points-de-vente/');public.wait_for_load_state('networkidle')
                maps[value]={'placeholder':public.locator('#imagine-carte-emplacement').count(),'requests':browser_requests[start:],'third_party':outgoing[external:]}
                checks['carte_'+value+'_rendu_sans_sortant']=maps[value]['placeholder']==int(value) and bool(maps[value]['requests']) and maps[value]['third_party']==[]
            # Témoin actif du détecteur réseau navigateur, bloqué AVANT transport.
            positive_start=len(outgoing)
            public.evaluate("fetch('https://example.invalid/b10-temoin').catch(()=>{})")
            public.wait_for_timeout(300)
            checks['detecteur_reseau_navigateur_temoin_bloque']=len(outgoing)==positive_start+1
            outgoing.pop()
            config('0')
            mobile=context(mobile=True);m=mobile.new_page();m.goto(identity['url']+'/points-de-vente/');m.wait_for_load_state('networkidle')
            checks['mobile_liste_sans_debordement']=m.locator('#imagine-points-vente > li').count()==30 and m.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
            m.screenshot(path=str(b10.OUT/'page-mobile.png'),full_page=True)
            checks['footer_B09_et_principal_preserves']=b10.navigation()==nav and public.locator('nav[aria-label="Navigation de pied de page"]').get_by_role('link',name='Points de vente',exact=True).count()==1
            browser.close()
        observations=b10.wp('echo wp_json_encode(get_option("imagine_b10_observations",[]));')
        checks['serveur_B10_zero_email_HTTP']=not any(v for k,v in (observations.items() if isinstance(observations,dict) else []) if k.startswith('b10_'))
        checks['navigateur_public_zero_tiers']=all(v['third_party']==[] and bool(v['requests']) for v in maps.values())
        checks['seuls_gravatars_admin_bloques']=all(urlsplit(u).netloc=='secure.gravatar.com' for u in outgoing)
    finally:
        # L'inverse métier est indépendante du retrait de l'observateur et des sessions.
        b10.wp('delete_option("imagine_b10_refus_suppression");Imagine\\Site\\PointsVente::importer('+b10.php((b10.OUT/'commerces-fictifs.csv').read_text(encoding='utf-8'))+','+b10.php(json.loads((b10.OUT/'mapping-exemple.json').read_text(encoding='utf-8')))+',";");update_option(Imagine\\Site\\PointsVente::CONFIG,'+b10.php({'mapping':json.loads((b10.OUT/'mapping-exemple.json').read_text(encoding='utf-8')),'separateur':';','carte':'0'})+',false);echo wp_json_encode(true);')
        final_owned=b10.wp('echo wp_json_encode([count(Imagine\\Site\\PointsVente::lignes()),Imagine\\Site\\PointsVente::configuration()["carte"],get_option(Imagine\\Site\\PointsVente::NETTOYAGE),get_option("imagine_b10_refus_suppression",null)]);')
        assert final_owned==[30,'0',[],None]
        b10.b09.remove_remote([observer])
        b10.wp('delete_option("imagine_b10_observations");echo wp_json_encode(true);')
        for session in sessions.values():
            uid=session['id'];rows=session['rows']
            b10.wp('global $wpdb;$wpdb->delete($wpdb->usermeta,["user_id"=>'+str(uid)+',"meta_key"=>"session_tokens"]);foreach('+b10.php(rows)+' as $r){$wpdb->insert($wpdb->usermeta,$r);}wp_cache_delete('+str(uid)+',"user_meta");echo wp_json_encode(true);')
            actual=b10.wp('global $wpdb;echo wp_json_encode($wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->usermeta} WHERE user_id=%d AND meta_key=\'session_tokens\'",'+str(uid)+'),ARRAY_A));')
            assert actual==rows
        absent=b10.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR."/'+observer+'")&&get_option("imagine_b10_observations",null)===null);')
        assert absent
        b10.save(label+'-nettoyage',{'observer_removed':absent,'sessions_restored':True})
    after_business=b10.recette_state()
    checks['etat_metier_apres_restauration_sessions']=after_business==business
    if after_business!=business:
        # Résumé sans données : isoler le type de dérive, pas accepter un état inconnu.
        print('Business changed keys:',[k for k in business if business[k]!=after_business.get(k)])
    b10.save(label,{'identity':identity,'private_snapshot':durable,'restored_30_carte_off':final_owned==[30,'0',[],None],'checks':checks,'map_observations':maps,'server_observations':observations,'fixture_ids':ids,'browser_requests_count':len(browser_requests),'admin_gravatars_blocked':len(outgoing),'public_outgoing_third_party':[]})
    print(json.dumps({'checks':checks,'total':len(checks)},ensure_ascii=False))
    assert all(checks.values())

if __name__=='__main__':run(sys.argv[1])
