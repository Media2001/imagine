"""Real native account/admin forms and private document lifecycle."""
from pathlib import Path
from html import unescape
import importlib.util
import sys,json,re,hashlib,uuid
from urllib.parse import urlencode,urlsplit
from urllib.request import Request
from urllib.error import HTTPError
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c17
from b00_fixtures import dummy_pdf,cover_png
spec=importlib.util.spec_from_file_location('c17_http_transport',Path(__file__).with_name('c12-http.py'))
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
ADMIN='/wp-admin/admin.php?page=imagine-justificatifs'
POST='/wp-admin/admin-post.php'
def fields(text):
    return {unescape(k):unescape(v) for k,v in re.findall(r'<input[^>]+type="hidden"[^>]+name="([^"]+)"[^>]+value="([^"]*)"',text)}
def form(client,uid=None):
    status,_,page=h.fetch(ADMIN if uid else '/my-account/',client)
    pattern=r'<article data-imagine-justificatif-titulaire="'+str(uid)+r'">(.*?)</article>' if uid else r'<div data-imagine-justificatif>(.*?)</div>'
    match=re.search(pattern,page,re.S)
    if status!=200 or not match:raise RuntimeError('C17 native form missing')
    return match.group(1)
def upload(client,text,content,patch=None,name='document-fictif.pdf'):
    values=dict(fields(text),categorie='à préciser');values.update(patch or {})
    boundary='c17-'+uuid.uuid4().hex
    parts=[('--'+boundary+'\r\nContent-Disposition: form-data; name="'+k+'"\r\n\r\n'+v+'\r\n').encode() for k,v in values.items()]
    parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="justificatif"; filename="'+name+'"\r\nContent-Type: application/pdf\r\n\r\n').encode()+content+b'\r\n')
    parts.append(('--'+boundary+'--\r\n').encode())
    return h.fetch(POST,client,b''.join(parts),headers={'Content-Type':'multipart/form-data; boundary='+boundary})
def decision(client,text,patch=None):
    values=dict(fields(text),decision='valide',fin='2027-12-31',confirmer='oui');values.update(patch or {})
    return h.fetch(POST,client,urlencode(values).encode())
def raw(path,client):
    try:r=client.open(Request(h.BASE+path),timeout=45)
    except HTTPError as e:r=e
    return r.code,{k.lower():v for k,v in r.headers.items()},r.read()
def stored(uid):
    return c17.wp('$s=Imagine\\Site\\Justificatifs::etat('+str(uid)+');$p=isset($s["blob"])?Imagine\\Site\\Justificatifs::chemin($s):null;echo wp_json_encode(["state"=>$s,"path"=>$p,"exists"=>$p?is_file($p):false,"sha256"=>$p&&is_file($p)?hash_file("sha256",$p):null]);')
def absent(path):
    return c17.wp('$p='+json.dumps(path)+';clearstatcache(true,$p);echo wp_json_encode(!file_exists($p)&&!is_link($p));')
def file_url(text):
    found=re.search(r'href="([^"]*imagine_justificatif[^"]+)"',text)
    if not found:raise RuntimeError('Protected URL missing')
    u=urlsplit(unescape(found.group(1)));return u.path+'?'+u.query

def run(label='http-final'):
    c17.profils.guard('imagine-test-demo')
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients={k:h.login(accounts[k]) for k in ['P-SOL-ATT','P-SOL-OK','E-ABO','E-REDAC','A-CARTE']}
    uid=c17.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]["P-SOL-ATT"]);')
    abo=clients['E-ABO'];owner=clients['P-SOL-ATT'];checks={};evidence={}
    before=c17.state();initial=stored(uid)
    c17.save(label+'-before',{'native':before,'document':initial})
    try:
        text=form(owner)
        checks['depot_natif_B02']='name="justificatif"' in text and 'Masquez votre numéro de registre national' in text
        checks['P_SOL_OK_valide']='Validé jusqu’au' in form(clients['P-SOL-OK'])
        s,_,page=h.fetch(ADMIN,abo)
        checks['file_referent_menu_unique']=s==200 and 'data-imagine-file-justificatifs' in page and page.count('id="toplevel_page_imagine"')==1
        for role in ['E-REDAC','A-CARTE']:
            s,_,p=h.fetch(ADMIN,clients[role]);checks['file_refuse_'+role]='data-imagine-file-justificatifs' not in p
        first=form(owner);pdf=dummy_pdf('C17 FICTIF - aucune personne reelle')
        s,_,_=upload(owner,first,pdf,name='nom-trompeur.php');checks['depot_PDF_contenu_pas_extension']=s==200
        a=stored(uid);url=file_url(form(owner));evidence['premier_depot']=a
        checks['octets_sur_disque']=a['exists'] and a['sha256']==hashlib.sha256(pdf).hexdigest()
        checks['ancien_depot_remplace']=initial['path'] is None or absent(initial['path'])
        checks['hors_racine_C11']=c17.wp('$p='+json.dumps(a['path'])+';$r=realpath(ABSPATH);echo wp_json_encode(!str_starts_with(realpath($p),$r."/")&&dirname($p)===Imagine\\Site\\PdfNumero::directory());')
        s,headers,data=raw(url,owner)
        checks['lecture_titulaire_hash']=s==200 and hashlib.sha256(data).hexdigest()==a['sha256']
        checks['telechargement_pas_preview']=headers.get('content-disposition','').startswith('attachment;') and headers.get('x-content-type-options')=='nosniff' and 'sandbox' in headers.get('content-security-policy','')
        checks['lecture_no_store']='private' in headers.get('cache-control','') and 'no-store' in headers.get('cache-control','')
        s,_,data=raw(url,abo);checks['lecture_referent_hash']=s==200 and hashlib.sha256(data).hexdigest()==a['sha256']
        for role,client in [('anonyme',None),('autre_abonne',clients['A-CARTE']),('redaction',clients['E-REDAC'])]:
            s,_,body=h.fetch(url,client);checks['lecture_refuse_'+role]=s==403 and '%PDF-' not in body
        s,_,body=h.fetch(url,owner,method='HEAD');checks['HEAD_sans_corps']=s==200 and body==''
        s,_,_=h.fetch(url,owner,b'x');checks['lecture_POST_refuse']=s==405
        q=form(abo,uid);checks['depot_visible_file']='Télécharger le fichier protégé' in q
        for name,data in [('executable',b'<?php echo "non";'),('SVG',b'<svg/>'),('PDF_actif',pdf.replace(b'/Type /Catalog',b'/OpenAction /JS /Type /Catalog')),('trop_gros',b'a'*5242881)]:
            s,_,_=upload(owner,form(owner),data);checks['refus_'+name+'_conserve_document']=s==409 and stored(uid)==a
        for name,patch,status in [('nonce',{'_wpnonce':'invalide'},403),('categorie',{'categorie':'inconnue'},409)]:
            s,_,_=upload(owner,form(owner),pdf,patch);checks['depot_refus_'+name]=s==status and stored(uid)==a
        s,_,_=upload(owner,first,pdf);checks['ancien_formulaire_depot_refuse']=s==409 and stored(uid)==a
        s,_,_=h.fetch(POST,None,urlencode({'action':'imagine_justificatif_deposer'}).encode());checks['depot_anonyme_refuse']=s==403
        s,_,_=h.fetch(POST+'?action=imagine_justificatif_decider',abo);checks['decision_GET_refuse']=s==405
        for name,patch,status in [('nonce',{'_wpnonce':'invalide'},403),('sans_confirmation',{'confirmer':'non'},409),('date_invalide',{'fin':'2027-02-29'},409)]:
            s,_,_=decision(abo,q,patch);checks['decision_refus_'+name]=s==status and stored(uid)==a
        s,_,_=decision(clients['A-CARTE'],q);checks['decision_autre_abonne_refusee']=s==403 and stored(uid)==a
        png=cover_png('1','#32664D')
        s,_,_=upload(owner,form(owner),png,name='image-fictive.pdf');b=stored(uid);evidence['remplacement']=b
        checks['remplacement_PNG_contenu']=s==200 and b['exists'] and b['sha256']==hashlib.sha256(png).hexdigest() and absent(a['path'])
        s,_,_=h.fetch(url,owner);checks['ancienne_URL_fermee']=s==404
        s,_,_=decision(abo,q);checks['decision_ancienne_revision_refusee']=s==409 and stored(uid)==b
        q=form(abo,uid);newurl=file_url(form(owner))
        s,_,data=raw(newurl,owner);checks['PNG_lecture_hash']=s==200 and hashlib.sha256(data).hexdigest()==b['sha256']
        s,_,_=decision(abo,q);valid=stored(uid);evidence['validation']=valid
        checks['valider_supprime_disque']=s==200 and absent(b['path']) and not valid['exists']
        checks['decision_champs_minimaux']=set(valid['state'])=={'categorie','decision','date_decision','fin','operateur'} and valid['state']['operateur']=='e-abo' and valid['state']['decision']=='valide'
        checks['compte_valide_fin']='Validé jusqu’au 2027-12-31' in form(owner)
        s,_,_=h.fetch(newurl,abo);checks['URL_validee_fermee_referent']=s==404
        s,_,_=decision(abo,q);checks['decision_rejeu_refuse']=s==409 and stored(uid)==valid
        upload(owner,form(owner),pdf);refused_source=stored(uid)
        s,_,_=decision(abo,form(abo,uid),{'decision':'refuse'});refused=stored(uid);evidence['refus']=refused
        checks['refuser_supprime_disque']=s==200 and absent(refused_source['path']) and not refused['exists'] and refused['state']['decision']=='refuse' and refused['state']['fin']==''
        checks['compte_refuse']='Refusé' in form(owner)
        s,_,page=h.fetch(ADMIN,abo);checks['decision_retire_file']='data-imagine-justificatif-titulaire="'+str(uid)+'"' not in page
    finally:
        olddoc=stored(uid);reset=c17.reset();c17.save(label+'-reset',reset)
        checks['reset_document_test_supprime']=olddoc['path'] is None or absent(olddoc['path'])
        checks['reset_deux_profils']=set(reset)=={'P-SOL-ATT','P-SOL-OK'} and reset['P-SOL-ATT']['decision']=='en_attente' and reset['P-SOL-OK']['decision']=='valide'
        after=c17.state();checks['prix_commandes_abonnements_droits_options_PDF_preserves']=after==before
        checks['reserve_C09_action8103_inchangee']=before['reserve_native_C09_action8103']==after['reserve_native_C09_action8103']
        c17.save(label+'-after',{'native':after,'document':stored(uid)})
        files=c17.wp('$files=glob(Imagine\\Site\\PdfNumero::directory()."/c17-*.bin");echo wp_json_encode(array_map("basename",$files));')
        checks['un_seul_fichier_apres_reset']=sorted(files)==['c17-'+reset['P-SOL-ATT']['blob']+'.bin']
        result={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'evidence':evidence,'remaining_private_files':files}
        c17.save(label,result);print(json.dumps(result,ensure_ascii=False))
    return int(bool(result['failures']))
