"""Vérification autonome, hors réseau et sans mutation, du complément B07 antislash."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

PROOF = Path(__file__).resolve().parent
ROOT = PROOF.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(name):
    return json.loads((PROOF/name).read_text(encoding='utf-8'))


def junit(name):
    data=load('antislash-'+name+'.json')
    path=PROOF/data['log']
    assert sha(path)==data['log_sha256'], name+' log divergent'
    text=path.read_text(encoding='utf-8')
    match=re.search(r'B07 JUNIT BEGIN\s*(.*?)B07 JUNIT END',text,re.S)
    assert match, name+' JUnit absent'
    suite=ET.fromstring(match[1]).find('testsuite')
    return data, {k:int(suite.attrib[k]) for k in ['tests','assertions','errors','failures','skipped']}


def verify():
    receipt=load('antislash-recu.json')
    for name,digest in receipt['files_readbacks'].items():
        assert sha(ROOT/name)==digest, 'Fichier divergent : '+name
    for name,digest in receipt['historical_untouched'].items():
        assert sha(PROOF/name)==digest, 'Historique B07 modifié : '+name
    red,rc=junit('red')
    green,gc=junit('green')
    mutant,mc=junit('mutation')
    full,fc=junit('suite')
    assert red['exit']==1 and rc['failures']==1 and rc['errors']==0
    assert mutant['exit']==1 and mc['failures']==1 and mc['errors']==0
    assert green['exit']==0 and gc=={'tests':11,'assertions':206,'errors':0,'failures':0,'skipped':0}
    assert full['exit']==0 and fc['tests']>=gc['tests'] and all(fc[k]==0 for k in ['errors','failures','skipped'])
    path=ROOT/'wp/plugins/imagine-site/Agenda.php'
    source=path.read_bytes()
    old=b"'imagine_agenda_nom' => $nom"
    new=b"'imagine_agenda_nom' => wp_slash($nom)"
    assert source.count(new)==1
    assert hashlib.sha256(source.replace(new,old)).hexdigest()==red['sources']['wp/plugins/imagine-site/Agenda.php'], 'Delta hors frontière'
    assert sha(path)==green['sources']['wp/plugins/imagine-site/Agenda.php']
    for data in [red,green,mutant,full]:
        for name,digest in data['sources'].items():
            if name!='wp/plugins/imagine-site/Agenda.php' or data is not red:
                assert sha(ROOT/name)==digest, name
    prep=load('antislash-prepare.json')
    assert prep['exit']==0 and sha(PROOF/prep['log'])==prep['log_sha256']
    assert 'T01 IMAGE READY' in (PROOF/prep['log']).read_text(encoding='utf-8')
    native=load('antislash-native.json')
    # Ce premier reçu a acquis les parcours et la restauration ; son assertion
    # tous-HTTP-zéro trop large n'est PAS déclarée verte. Le complément suivant
    # observe séparément l'infrastructure bloquée, sans changer aucun gardien.
    assert native['native_red']=={'http':400,'no_registration':True}
    assert len(native['cases'])==4 and native['observer_witness']['mail_and_http_detected']
    for case in native['cases']:
        assert len(case['post'])==2 and all(p['http']==303 for p in case['post'])
        assert all(case[k] is True for k in ['unique_registration','stored_exact','admin_display_exact','native_export_exact'])
    assert all(native['cleanup'].values()) and all(native['restoration'].values()) and native['business_preserved']
    assert native['final_remote_sha256']==sha(path) and native['corrected_agenda_deployed']
    observation=load('antislash-observation-native.json')
    assert observation['prior_native_receipt_sha256']==sha(PROOF/'antislash-native.json')
    assert observation['checks_passed'] and observation['unique_registration'] and observation['post_codes']==[303,303]
    rows=observation['observations']['rows']
    assert rows and observation['observations']['requests']==len(rows)
    for row in rows:
        assert all(row[k]==0 for k in ['mail','http_agenda','http_autre','transport_mail','transport_http'])
        assert row['http']==row['http_infrastructure']
    assert all(observation['absence_mutations_detected'].values())
    assert all(observation['restoration'].values()) and all(observation['temporary_files_absent'])
    assert observation['business_preserved'] and observation['registrations_removed']
    regression=load('antislash-regression.json')
    assert sha(PROOF/regression['log'])==regression['log_sha256']
    assert regression['exit']!=0, 'Le rejeu global interrompu ne doit pas être déclaré vert'
    print('B07 ANTISLASH PASS : delta unique ligne 132 ; agenda '+str(gc['tests'])+' tests / '+str(gc['assertions'])+' assertions ; imagine-site '+str(fc['tests'])+' tests / '+str(fc['assertions'])+' assertions ; 4 parcours natifs et doublons ; restauration métier PASS ; '+str(len(receipt['historical_untouched']))+' fichiers historiques inchangés.')
    print('Hors verdict complément : rejeu.ps1 interrompu (conteneur absent) ; aucun paquet réparé ni PRET rescellé.')


if __name__=='__main__':
    verify()
