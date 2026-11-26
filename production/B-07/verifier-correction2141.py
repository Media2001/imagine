"""Contrôle canonique B07 fusion21h41, hors réseau et sans WordPress."""
import hashlib,json,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
EXPECTED={'r1':'testLiensDuCorpsPartenaireEtContreExemples','r2':'testProjectionFicheSchemaExecuteLeContenuUneSeuleFois','double-contenu':'testProjectionFicheSchemaExecuteLeContenuUneSeuleFois','r4':'testExportErreurArreteEtRepriseNeSauteAucunePage','formulaire':'testPartenairePasseConserveSonLienSansInscription','alerte':'testAdministrationSignaleLaSaisieInvalideSansMasquerLeDefaut'}
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name):return json.loads((HERE/name).read_text(encoding='utf-8'))
def junit(name):
 raw=(HERE/name).read_text(encoding='utf-8');assert raw.count('B07 JUNIT BEGIN')==raw.count('B07 JUNIT END')==1
 return ET.fromstring(raw.split('B07 JUNIT BEGIN\n',1)[1].split('B07 JUNIT END',1)[0])
def verify():
 m=load('manifest-correction2141.json');checks={};counts={}
 for name,sha in m['files'].items():
  assert not Path(name).is_absolute() and '..' not in Path(name).parts
  checks['sha256:'+name]=(ROOT/name).is_file() and digest(ROOT/name)==sha
 source=(ROOT/'wp/themes/imagine/functions.php').read_text(encoding='utf-8')
 assert source.count('function imagine_partner_content(')==1
 contract=source.split('function imagine_partner_content(',1)[1].split("add_filter('the_content'",1)[0]
 checks['filtre_B05_contrat_seul']=hashlib.sha256(contract.encode()).hexdigest()==m['filter_contract_sha256']
 bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
 block="// B07 — raccord agenda additif.\nrequire_once __DIR__ . '/AgendaRegles.php';\nrequire_once __DIR__ . '/Agenda.php';\nrequire_once __DIR__ . '/AgendaConfidentialite.php';\nAgenda::register();\nAgendaConfidentialite::register();\n\n"
 checks['bootstrap_contrat_seul']=bootstrap.count(block)==1
 for name in m['green_receipts']:
  r=load(name);counts[name]=r['total']
  checks['receipt:'+name]=r.get('scope')=='imagine-test-demo' and r['total']==len(r['checks']) and bool(r['checks']) and all(v is True for v in r['checks'].values()) and not r.get('failures') and not r.get('error') and not r.get('stderr') and r.get('exit',0)==0 and r.get('business_preserved',True) is True
  for rel,sha in r.get('sources',{}).items():
   if rel!='themes/imagine/functions.php':checks['receipt-source:'+name+':'+rel]=digest(ROOT/'wp'/rel)==sha
 for receipt,key,source in [('correction2141-recette-finale-V2.json','runner_sha256','wp/outils/demo/b07-corrections.py'),('correction2141-privacy-V2.json','source_sha256','wp/tests/demo/b07-corrections-privacy.php'),('correction2141-readback-V2.json','runner_sha256','wp/outils/demo/b07-corrections-readback.py'),('correction2141-compat-privacy-V2.json','source_sha256','wp/tests/demo/b07-privacy.php')]:
  checks['harnais_execute:'+receipt]=load(receipt)[key]==digest(ROOT/source)
 checks['readback_filtre']=load('correction2141-readback-V2.json')['filter_contract_sha256']==m['filter_contract_sha256']
 xml=junit('correction2141-horslive-final.log');suite=xml.find('testsuite');cases=list(xml.iter('testcase'))
 checks['PHPUnit_final']=int(suite.attrib['tests'])==len(cases)==9 and int(suite.attrib['assertions'])==159 and all(int(suite.attrib[k])==0 for k in ['errors','failures','skipped'])
 for name in set(EXPECTED.values())|{'testLibellesLitterauxEtDomainesDesGabarits','testBorneOuvertEtDoublonTraversentLeVraiAdaptateur'}:checks['cas:'+name]=sum(x.attrib['name']==name for x in cases)==1
 mutations=load('correction2141-mutations-sources.json')
 checks['six_sources_mutees']=set(mutations['cases'])==set(EXPECTED) and mutations['total']==len(EXPECTED)
 for mutant,name in EXPECTED.items():
  x=junit('correction2141-mutant-'+mutant+'.log');s=x.find('testsuite');failed=[c.attrib['name'] for c in x.iter('testcase') if c.find('failure') is not None]
  checks['mutation:'+mutant]=failed==[name] and int(s.attrib['tests'])==9 and int(s.attrib['errors'])==0 and mutations['cases'][mutant]=={'exit':1,'failures':failed,'errors':0,'detected':True}
 raw=(HERE/'correction2141-suite-finale.log').read_text(encoding='utf-8');markers=[x[11:] for x in raw.splitlines() if x.startswith('T01_RESULT ')]
 assert len(markers)==1
 general=json.loads(markers[0]);checks['suite_canonique_PASS']=general['pass'] is True and general['tests']>0 and all(general[k]==0 for k in ['failures','errors','skipped']) and general['tools']['failures']==0 and ' — PASS' in raw
 checks['Agenda_dans_JUnit_canonique']=all(('name="'+x.attrib['name']+'"') in raw for x in cases)
 checks['image_preparee']='PREPARATION T01 : image verifiee sha256:' in (HERE/'correction2141-preparer-image.log').read_text(encoding='utf-8')
 failures=[k for k,v in checks.items() if not v]
 print(json.dumps({'scope':'B-07-correction2141','status':'FAIL' if failures else 'PASS','total':len(checks),'failures':failures,'controls_by_receipt':counts,'horslive':{'tests':len(cases),'assertions':int(suite.attrib['assertions'])},'source_mutants_detected':len(EXPECTED),'global_suite':general},ensure_ascii=True))
 return int(bool(failures))
if __name__=='__main__':raise SystemExit(verify())
