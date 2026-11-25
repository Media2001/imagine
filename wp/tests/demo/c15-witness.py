"""C15 real native A-PAPIER paid/unpaid witnesses; own cleanup only."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c15
PREFIX='require_once WP_CONTENT_DIR."/imagine-demo-build/c15-state.php";'
NS='Imagine\\Demo\\C15Corrections\\'

def call(code):
    return c15.wp(PREFIX+code)

def snapshot():
    return call('echo wp_json_encode('+NS+'snapshot());')

def restore(before, renewals=()):
    call('$before=json_decode('+json.dumps(json.dumps(before))+',true);echo wp_json_encode('+NS+'restore($before,'+json.dumps(list(renewals))+'));')
    after={k:v for k,v in snapshot().items() if k in before}
    if before!=after:
        c15.save('corrections-restore-diff',{'before':before,'after':after})
        raise RuntimeError('Owned semantic restore differs')

def verify(label):
    c15.profils.guard('imagine-test-demo')
    c15.upload('imagine-demo-build/c15-state.php',c15.ROOT/'wp/tests/demo/c15-state.php')
    action=c15.load_test('c15-action')
    all_before=action.snapshot()
    before=snapshot()
    c15.save(label+'-before',{'owned':before,'catalogue':all_before})
    checks={}; renewals=[]
    try:
        oid=call('echo wp_json_encode('+NS+'unpaid());')
        renewals.append(oid)
        c15.save(label+'-owned-renewals',renewals)
        state=call('$f=get_option("imagine_c09_fixture");$s=wcs_get_subscription($f["subscriptions"]["A-PAPIER"]);$o=wc_get_order('+str(oid)+');echo wp_json_encode(["status"=>$s->get_status(),"order_status"=>$o->get_status(),"paid"=>$o->is_paid(),"date"=>$o->get_date_created()->getTimestamp(),"total"=>$o->get_total(),"related"=>array_values($s->get_related_orders("ids","renewal")),"rows"=>Imagine\\Site\\EcheancesNatives::lire("mandats",30)]);')
        c15.save(label+'-unpaid-native',state)
        rows=[r for r in state['rows'] if r['id']==oid]
        checks['native_unpaid_onhold']=state['status']=='on-hold' and not state['paid'] and oid in state['related']
        checks['due_renewal_not_lost']=len(rows)==1 and rows[0]['montant']==state['total'] and rows[0]['echeance']==state['date']
        checks['no_future_duplicate']=not any(r['id']==all_before['fixture']['subscriptions']['A-PAPIER'] for r in state['rows'])
        # Native status transition only: a fictitious paid state, never gateway or payment_complete.
        paid=call('$o=wc_get_order('+str(oid)+');$o->update_status("completed","C15 — témoin fictif C09 renouvellement payé, aucune transaction.");echo wp_json_encode(["paid"=>wc_get_order('+str(oid)+')->is_paid(),"rows"=>Imagine\\Site\\EcheancesNatives::lire("mandats",30)]);')
        checks['native_paid_renewal_excluded']=paid['paid'] and not any(r['id']==oid for r in paid['rows'])
        c15.save(label+'-paid-native',paid)
    finally:
        restore({'A-PAPIER':before['A-PAPIER']},renewals)
        checks['owned_all_dates_restored']=snapshot()==before
        checks['catalogue_semantic_exact']=action.snapshot()==all_before
        c15.save(label+'-restore',{'checks':{k:v for k,v in checks.items() if 'restore' in k or 'exact' in k},'global_c09_reset':False,'removed_owned_renewals':renewals})
    record={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True]}
    c15.save(label,record)
    print(json.dumps(record))
    return not record['failures']

if __name__=='__main__':
    sys.exit(0 if verify(sys.argv[1]) else 1)
