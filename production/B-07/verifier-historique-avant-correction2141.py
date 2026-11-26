"""Vérificateur B07 hors réseau, sans WordPress, Docker, données privées ni secret."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
BLOCK="// B07 — raccord agenda additif.\nrequire_once __DIR__ . '/AgendaRegles.php';\nrequire_once __DIR__ . '/Agenda.php';\nrequire_once __DIR__ . '/AgendaConfidentialite.php';\nAgenda::register();\nAgendaConfidentialite::register();\n\n"
def verify():
 manifest=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
 checks={}
 for rel,expected in manifest['files'].items():
  p=ROOT/rel
  assert not Path(rel).is_absolute() and '..' not in Path(rel).parts
  checks['sha256:'+rel]=p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==expected
 bootstrap=(ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
 checks['bootstrap_contrat_B07']=bootstrap.count(BLOCK)==1
 controls={};mutations={}
 for name in manifest['green_receipts']:
  r=json.loads((HERE/name).read_text(encoding='utf-8'))
  checks['receipt:'+name]=r.get('scope')=='imagine-test-demo' and not r.get('failures') and not r.get('error') and r.get('exit',0)==0 and bool(r.get('checks')) and all(r['checks'].values()) and r['total']==len(r['checks'])
  controls[name]=r['total'];mutations[name]=sum(k.startswith('mutation_') for k in r['checks'])
  for path,digest in r.get('sources',{}).items():
   # Les sources partagées évoluent : B07 n'épingle que son bloc d'amorçage.
   if path.endswith('/imagine-site.php'):continue
   checks['receipt-source:'+name+':'+path]=hashlib.sha256((ROOT/'wp'/path).read_bytes()).hexdigest()==digest
 global_log=(HERE/'regression-livraison.log').read_text(encoding='utf-8')
 summary=re.findall(r'REJEU : (\d+) tests, (\d+) assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS',global_log)
 checks['suite_globale_PASS']=len(summary)==1 and 'AgendaReglesTest' in global_log
 checks['preparation_image_PASS']='PREPARATION T01 : image verifiee sha256:' in (HERE/'preparer-image-final.log').read_text(encoding='utf-8')
 checks['privacy_source_finale']=json.loads((HERE/'confidentialite-V2.json').read_text(encoding='utf-8'))['source_sha256']==hashlib.sha256((ROOT/'wp/tests/demo/b07-privacy.php').read_bytes()).hexdigest()
 checks['runtime_source_finale']=json.loads((HERE/'adaptateur-livraison-V2.json').read_text(encoding='utf-8'))['source_sha256']==hashlib.sha256((ROOT/'wp/tests/demo/b07-runtime.php').read_bytes()).hexdigest()
 failures=[k for k,v in checks.items() if not v]
 result={'status':'PASS' if not failures else 'FAIL','total':len(checks),'failures':failures,'controls_by_receipt':controls,'mutations_by_receipt':mutations,'global_suite':summary}
 print(json.dumps(result,ensure_ascii=True));return 1 if failures else 0
if __name__=='__main__':raise SystemExit(verify())
