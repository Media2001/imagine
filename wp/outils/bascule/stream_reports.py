"""Final report contracts. No site code is imported by this validator."""
import csv
import io
import json
import re
from collections import Counter

KEYS={
'A03':'schema generated_at_utc versions storage sample_states samples memberships access subscriptions subscription_counts actions action_days order_months orders php_log pages renewal',
'A11':'schema read_only total par_nature exclus autres_etats_non_listes permaliens native_guards adresses audit_sha256',
'A12':'schema read_only storage registry post_types taxonomies attachments product_links native_guards conventions limitations audit_sha256',
'A14':'schema read_only storage audit_sha256 counts anomalies',
'A15':'schema read_only storage registry emails transport_plugins summary audit_sha256',
'A16':'schema read_only storage limit issues orphan_published_by_year audit_sha256 mapping_sha256',
'A17':'schema read_only storage as_of_utc cutoff_utc unique_management_accounts roles two_factor_adapter two_factor_coverage last_login_adapter protections configuration audit_sha256',
'A18':'schema read_only storage database payment_tokens media count_basis server_rules token_basis audit_sha256',
'A19':'schema read_only storage as_of_utc counts payment_reference_basis mode_basis scope audit_sha256',
}
SCHEMAS={'A03':'imagine-a03-v1','A11':'imagine-a11-public-addresses-v1','A12':'imagine-a12-content-v1','A14':'imagine-a14-v1','A15':'imagine-a15-v1','A16':'imagine-a16-issues-v1','A17':'imagine-a17-security-v1','A18':'imagine-a18-retention-v1','A19':'imagine-a19-coherence-v1'}
PREFIX={
'A12':'# Structure des contenus — lecture seule\n\nRegistre natif apres wp_loaded. Declarants observes pendant les enregistrements effectifs. Aucune decision de rattachement.\n\n',
'A16':'# Numeros — lecture seule\n\nComptes et identifiants uniquement ; aucun rattachement choisi.\n\n',
'A17':'# Securite des comptes — lecture seule\n\nComptes par role, jamais identites.\n\n',
'A18':'# Conservation — lecture seule\n\nComptes uniquement ; aucune valeur ni decision de suppression.\n\n',
'A19':'# Cohérence — lecture seule\n\nComptes uniquement ; aucune valeur ni decision de suppression.\n\n',
}
LABELS=['Total des contacts','Contacts avec compte','Contacts sans compte','Lignes ambiguës','Comptes sans contact','Comptes injoignables','Lignes avec adresse invalide','Lignes concernées par un doublon','Contacts désinscrits','Contacts bloqués']
COUNTS='contacts_total contacts_with_account contacts_without_account ambiguous_contact_lines accounts_without_contact accounts_unmatchable invalid_contact_lines duplicate_contact_lines unsubscribed_contacts blocked_contacts'.split()

def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate')
        result[key]=value
    return result

def read(text):
    return json.loads(text,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))

def integer(value):
    return type(value) is int and 0<=value<=9007199254740991

def counters(value):
    if isinstance(value,dict):
        return all(isinstance(k,str) and counters(v) for k,v in value.items())
    if isinstance(value,list):return all(counters(v) for v in value)
    if type(value) is int:return True
    return value is None or type(value) in (str,bool,float)

def count_contract(tool,data):
    def numbers(value):
        return isinstance(value,(dict,list)) and all(integer(v) for v in (value.values() if isinstance(value,dict) else value))
    def fields(row,names):
        return all(integer(row[k]) for k in names.split())
    if tool=='A03':
        return (numbers(data['samples']) and numbers(data['action_days'])
            and all(numbers(value) for value in data['subscription_counts'].values())
            and all(fields(row,'user_id plan_id') for row in data['memberships'].values())
            and all(fields(row,'interval') for row in data['subscriptions'].values())
            and all(fields(row,'count decimals') and type(row['amount_minor']) is int for row in data['orders'].values())
            and fields(data['php_log'],'errors')
            and all(fields(row,'status final_status') for row in data['pages'].values()))
    if tool=='A11':return fields(data,'total') and numbers(data['par_nature']) and numbers(data['exclus']) and numbers(data['native_guards'])
    if tool=='A12':
        return (fields(data['registry'],'post_type_count taxonomy_count')
            and numbers(data['native_guards'])
            and all(fields(row,'content_count') and numbers(row['states'])
                and all(fields(meta,'content_count') for meta in row['metadata_keys']) for row in data['post_types'])
            and all((row['content_count'] is None or integer(row['content_count'])) and fields(row,'term_count') for row in data['taxonomies'])
            and fields(data['attachments'],'pdf_count orphan_count missing_files')
            and all(fields(row,'count bytes orphan_count') for row in data['attachments']['by_mime'])
            and all(fields(row,'linked_contents distinct_pairs non_scalar_rows') for row in data['product_links']))
    if tool=='A14':return numbers(data['counts']) and all(fields(row,'line') for row in data['anomalies'])
    if tool=='A15':return fields(data['registry'],'email_count') and numbers(data['summary']['active_by_extension']) and fields(data['summary'],'overridden_template_files') and data['registry']['email_count']==len(data['emails'])
    if tool=='A16':
        return fields(data,'limit') and all(fields(row,'id articles published_articles unpublished_articles without_theme multiple_themes without_featured_image attached_media missing_media_files') for row in data['issues']) and all(fields(row,'year articles') for row in data['orphan_published_by_year'])
    if tool=='A17':
        return fields(data,'unique_management_accounts') and all(fields(row,'accounts') and (integer(row['application_password_accounts']) or row['application_password_accounts']=='inconnu après neutralisation') and (row['two_factor_active'] is None or integer(row['two_factor_active'])) and all(value is None or integer(value) for key,value in row['last_login'].items() if key!='status') for row in data['roles'])
    if tool=='A18':
        groups=data['database']['groups']
        return ((groups is None and data['database']['status']=='inconnu après neutralisation') or isinstance(groups,list) and all(fields(row,'iban card national') for row in groups)) and all(fields(row,'count') for row in data['payment_tokens']) and all(fields(row,'directories bytes') and numbers(row['files']) for row in data['media'])
    if tool=='A19':
        return all(isinstance(value,dict) if key=='definitions' else integer(value) if key in ('multiple_active_subscription_accounts','multiple_active_membership_accounts','active_past_next_payment','active_without_paid_order') else isinstance(value,list) and all(fields(row,'count') and ('plan' not in row or integer(row['plan'])) for row in value) for key,value in data['counts'].items())
    return False

def fenced(text,prefix,data,suffix='\n'):
    start=prefix+'```json\n';end='\n```'+suffix
    return text.startswith(start) and text.endswith(end) and read(text[len(start):-len(end)])==data

def validate(tool,output):
    try:
        files={p.name:p.read_text(encoding='utf-8') for p in output.iterdir()}
        name=next(n for n in files if n.endswith('.json'));data=read(files[name])
        if tool=='A03' and isinstance(data,dict) and data.get('mode')=='renewal_probe':
            return (set(data)=={'schema','mode','renewal'} and data['schema']==SCHEMAS[tool]
                and set(data['renewal'])=={'enabled','manual_only','created','linked','pending','cleaned'}
                and all(type(value) is bool for value in data['renewal'].values()))
        if not isinstance(data,dict) or set(data)!=set(KEYS[tool].split()) or data['schema']!=SCHEMAS[tool]:return False
        if tool!='A03' and data['read_only'] is not True:return False
        if 'storage' in data and data['storage'] not in ('classic','hpos'):return False
        if not counters(data) or not count_contract(tool,data):return False
        for key in ('audit_sha256','mapping_sha256'):
            if key in data and not re.fullmatch('[a-f0-9]{64}',data[key]):return False
        if tool=='A03':return True
        md=files[next(n for n in files if n.endswith('.md'))]
        if tool in PREFIX:
            if tool=='A16' and (not integer(data['limit']) or len(data['issues'])>data['limit']):return False
            return fenced(md,PREFIX[tool],data)
        if tool=='A15':
            summary=data['summary'];active=summary['active_by_extension']
            if not all(integer(n) for n in active.values()) or not integer(summary['overridden_template_files']):return False
            prefix='# Emails declares — lecture seule\n\nRegistre WC_Emails reellement charge, pas un historique d\'envoi. Aucun email declenche.\n\n'
            prefix+=''.join(k+' : '+str(v)+' actif(s)\n' for k,v in active.items())
            prefix+='Gabarits surcharges distincts : '+str(summary['overridden_template_files'])+'\n\n'
            return fenced(md,prefix,data)
        if tool=='A14':
            counts=data['counts']
            if set(counts)!=set(COUNTS) or not all(integer(n) for n in counts.values()):return False
            if counts['contacts_total']!=sum(counts[k] for k in ['contacts_with_account','contacts_without_account','ambiguous_contact_lines','invalid_contact_lines']):return False
            prefix='# Rapprochement — lecture seule\n\nAucune réinscription ; coopérateur et tarif inconnus.\nLes contacts sont comptés par ligne source, pas par personne distincte. Le compteur technique duplicate_contact_lines indique les lignes concernées par un doublon ; il ne donne pas, à lui seul, le nombre de personnes distinctes.\n\n'
            if md!=prefix+''.join(label+' : '+str(counts[key])+'\n' for label,key in zip(LABELS,COUNTS)):return False
            rows=list(csv.reader(io.StringIO(files['rapproches.csv']),delimiter=';',strict=True))
            if rows[0]!=['ligne','abonnement_actif','statut','cooperateur','tarif'] or len(rows)-1!=counts['contacts_with_account']:return False
            lines=[]
            for row in rows[1:]:
                if len(row)!=5 or not re.fullmatch('[1-9][0-9]*',row[0]) or row[1] not in ('oui','non') or row[2] not in ('inscrit','desinscrit','bloque','inconnu') or row[3:]!=['','']:return False
                lines.append(int(row[0]))
            return len(lines)==len(set(lines)) and all(n>=2 for n in lines)
        if tool=='A11':
            addresses=data['adresses'];total=data['total'];nature=data['par_nature']
            if not integer(total) or total!=len(addresses) or not all(integer(n) for n in nature.values()):return False
            observed=Counter(nature for row in addresses for nature in {c['nature'] for c in row['contextes']})
            if dict(observed)!=nature:return False
            rows=list(csv.reader(io.StringIO(files['adresses.csv'].lstrip('\ufeff')),delimiter=';',strict=True))
            if rows[0]!=['ancienne','nature','type_contenu','etat_publication','derniere_modification_utc','autres_contextes']:return False
            expected=[]
            for row in addresses:
                extra=' | '.join(c['nature']+' : '+c['type_contenu'] for c in row['contextes'][1:])
                cells=[row['ancienne'],row['nature'],row['type_contenu'],row['etat_publication'],row['derniere_modification_utc'] or '',extra]
                expected.append(["'"+cell if re.match('[=+@\\-\\t\\r\\n]',cell) else cell for cell in cells])
            if rows[1:]!=expected:return False
            prefix='# Adresses publiques — lecture seule\n\n'+str(total)+' adresses uniques. Aucun plan de redirections décidé.\n\n## Par nature\n\n'
            prefix+=''.join('- '+k+' : '+str(v)+'\n' for k,v in nature.items())
            prefix+='\nUne adresse commune (page boutique et archive produit) garde tous ses contextes; les nombres par nature ne sont pas additifs.\n\n## Exclus (comptés, jamais listés) et permaliens\n\n'
            suffix='\n\nDates UTC des contenus seulement; les archives et termes n\'ont pas de date native de modification : cellule vide. Pièces jointes : pages natives, pas fichiers téléchargeables.\n'
            return fenced(md,prefix,{k:data[k] for k in ['exclus','autres_etats_non_listes','permaliens']},suffix)
        return False
    except (ValueError,TypeError,KeyError,IndexError,StopIteration,OSError):return False
