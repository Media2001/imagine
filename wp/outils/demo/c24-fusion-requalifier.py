"""Requalification des sept mutations natives C24 historiques, reçus neufs."""
import sys
sys.dont_write_bytecode=True
import json,runpy,os
from pathlib import Path
import c24

def run(prefix):
    os.environ['TMPDIR']=str(Path(os.environ['LOCALAPPDATA'])/'hermes/cache/scratch')
    c24.guard()
    m=runpy.run_path(str(c24.ROOT/'wp/tests/demo/c24-http.py'))
    fixture=c24.wp('echo wp_json_encode(get_option("imagine_c09_fixture")["users"]);')
    ids=[fixture[k] for k in ['A-PAPIER','A-SEPA4','A-SANSMAIL','E-ADMIN']]
    expected={'sansmail':'sansmail_rubrique_presente_sans_case','listener':'accroche_sans_ecouteur','mail':'aucun_mail_tente','http':'aucun_http_tente','export_empty':'export_reponses_consentement_resultat','export_other':'export_tiers_absent','erase_noop':'effacement_resultat_absence_deux_metas'}
    receipts=[]
    for mutation,failure in expected.items():
        label=prefix[:-3]+'-'+mutation.replace('_','-')+'-V2'
        before=m['snapshot'](ids);native=c24.state()
        private=c24.b06.private_snapshot(label,{'snapshot':before,'native':native,'ids':ids})
        try:c24.runtime(label,mutation)
        except AssertionError:pass
        r=json.loads((c24.PROOF/(label+'.json')).read_text(encoding='utf-8'))
        assert r['exit']==1 and failure in r['failures'] and r['state_preserved'] and not r['stderr']
        assert m['business_snapshot'](before)==m['business_snapshot'](m['snapshot'](ids)) and native==c24.state()
        receipts.append({'receipt':label,'required_failure':failure,'private_snapshot':private,'all_business_rows_preserved':True})
    c24.save(prefix,{'result':'PASS','receipts':receipts,'mutations':len(receipts)})

if __name__=='__main__':run(sys.argv[1])
