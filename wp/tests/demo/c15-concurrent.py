"""C15 two truly simultaneous HTTP confirmations; restore existing A-VIR only."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from html import unescape
from urllib.parse import urlencode
import hashlib
import json
import re
import sys
import time
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'outils/demo'))
import c15


def verify(label):
    c15.profils.guard('imagine-test-demo')
    w=c15.load_test('c15-witness')
    c15.upload('imagine-demo-build/c15-state.php',c15.ROOT/'wp/tests/demo/c15-state.php')
    h=c15.load_test('c12-http')
    credentials=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients=[h.login(credentials[k]) for k in ('E-ABO','E-ADMIN')]
    f=c15.wp('echo wp_json_encode(get_option("imagine_c09_fixture"));')
    oid=f['orders']['A-VIR']
    before=w.snapshot()
    broad=c15.load_test('c15-action').snapshot()
    def notes():
        return c15.wp('echo wp_json_encode(array_values(array_filter(array_map(static fn($n)=>$n->content,wc_get_order_notes(["order_id"=>'+str(oid)+',"limit"=>0])),static fn($s)=>str_starts_with($s,"C15 — Paiement reçu confirmé"))));')
    prior=notes()
    payloads=[]
    for client in clients:
        status,_,page=h.fetch('/wp-admin/admin.php?page=imagine-echeances&vue=virements',client)
        match=re.search(r'name="action" value="imagine_virement_recu".*?name="_wpnonce" value="([^"]+)"',page,re.S)
        if status!=200 or not match:
            raise RuntimeError('A-VIR form absent; refusing fixture write')
        payloads.append(urlencode({'action':'imagine_virement_recu','commande':str(oid),'_wpnonce':unescape(match.group(1)),'confirmer':'oui'}).encode())
    target='mu-plugins/imagine-c15-concurrent-witness.php'
    exists=c15.wp('echo wp_json_encode(file_exists(WP_CONTENT_DIR.'+json.dumps('/'+target)+'));')
    if exists:
        raise RuntimeError('Existing owned witness must be inspected, not overwritten')
    source=c15.ROOT/'wp/tests/demo/c15-concurrent-mu.php'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    checks={}; responses=[]
    c15.save(label+'-before',{'owned':before,'catalogue':broad,'prior_notes':len(prior)})
    installed=False
    try:
        c15.upload(target,source)
        installed=True
        barrier=Barrier(2)
        def request(index):
            barrier.wait(timeout=15)
            start=time.monotonic()
            status,_,body=h.fetch('/wp-admin/admin-post.php',clients[index],payloads[index])
            return {'status':status,'elapsed':round(time.monotonic()-start,3),'success':status==200 and '<h1>Échéances</h1>' in body}
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses=list(pool.map(request,range(2)))
        after_notes=notes()
        checks['two_simultaneous_one_success_one_refusal']=sorted(r['status'] for r in responses)==[200,409] and sum(r['success'] for r in responses)==1
        checks['single_C15_audit_note']=len(after_notes)==len(prior)+1
        state=c15.wp('$o=wc_get_order('+str(oid)+');echo wp_json_encode([$o->is_paid(),$o->get_date_paid()?->getTimestamp(),$o->get_transaction_id(),$o->get_payment_method()]);')
        checks['native_paid_no_gateway_no_transaction']=state[0] and bool(state[1]) and state[2:]==['','']
        c15.save(label+'-native',{'responses':responses,'note_delta':len(after_notes)-len(prior),'state':state})
    finally:
        if installed:
            deleted=c15.wp('$p=WP_CONTENT_DIR.'+json.dumps('/'+target)+';if(!is_file($p)||hash_file("sha256",$p)!=='+json.dumps(digest)+')throw new RuntimeException("Witness ownership mismatch");unlink($p);echo wp_json_encode(!file_exists($p));')
            checks['temporary_MU_removed']=deleted is True
        w.restore(before)
        checks['owned_all_dates_restored']=w.snapshot()==before
        checks['catalogue_semantic_exact']=c15.load_test('c15-action').snapshot()==broad
    result={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'responses':responses,'global_C09_reset':False}
    c15.save(label,result)
    print(json.dumps(result))
    return not result['failures']

if __name__=='__main__':
    sys.exit(0 if verify(sys.argv[1]) else 1)
