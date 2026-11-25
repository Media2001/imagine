"""C15 French native-state labels over real HTTP."""
from pathlib import Path
import json
import re
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c15

def verify(label):
    c15.profils.guard('imagine-test-demo')
    h=c15.load_test('c12-http')
    accounts=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    client=h.login(accounts['E-ABO'])
    checks={}
    for view,expected in [('mandats','Actif'),('attente','En attente'),('virements','En attente'),('echecs','Échec')]:
        status,_,page=h.fetch('/wp-admin/admin.php?page=imagine-echeances&vue='+view,client)
        states=re.findall(r'<tr data-imagine-echeance="\d+"><td>.*?</td><td>.*?</td><td>(.*?)</td>',page,re.S)
        checks[view+'_libelle_francais']=status==200 and bool(states) and all(s==expected for s in states)
    record={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True]}
    c15.save(label,record);print(json.dumps(record))
    return not record['failures']

if __name__=='__main__':
    sys.exit(0 if verify(sys.argv[1]) else 1)
