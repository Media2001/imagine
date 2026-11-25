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


def verify(label, refuse=False):
    c15.profils.guard('imagine-test-demo')
    w=c15.load_test('c15-witness')
    c15.upload('imagine-demo-build/c15-state.php',c15.ROOT/'wp/tests/demo/c15-state.php')
    h=c15.load_test('c12-http')
    credentials=json.loads((Path.home()/'.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients=[h.login(credentials[k]) for k in ('E-ABO','E-ADMIN')]
    from urllib.request import build_opener, HTTPRedirectHandler, HTTPCookieProcessor
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    clients=[build_opener(NoRedirect(),HTTPCookieProcessor(next(handler.cookiejar for handler in client.handlers if hasattr(handler,'cookiejar')))) for client in clients]
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
        payloads.append(urlencode({'action':'imagine_virement_recu','commande':str(oid),'_wpnonce':unescape(match.group(1)),'confirmer':'oui', 'imagine_c15_refus':'apres' if refuse else ''}).encode())
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
            if not refuse:
                barrier.wait(timeout=15)
            start=time.monotonic()
            status,headers,body=h.fetch('/wp-admin/admin-post.php',clients[index],payloads[index])
            return {'status':status,'elapsed':round(time.monotonic()-start,3),'success':status==302 and 'recu=1' in headers.get('location',''), 'lock':headers.get('x-imagine-c15-lock')}
        if refuse:
            responses=[request(0)]
        else:
            with ThreadPoolExecutor(max_workers=2) as pool:
                responses=list(pool.map(request,range(2)))
        after_notes=notes()
        if refuse:
            checks['native_false_despite_paid_is_refused']=responses[0]['status']==409 and not responses[0]['success']
            checks['native_false_no_C15_success_note']=len(after_notes)==len(prior)
        else:
            checks['two_simultaneous_one_success_one_refusal']=sorted(r['status'] for r in responses)==[302,409] and sum(r['success'] for r in responses)==1
            checks['single_C15_audit_note']=len(after_notes)==len(prior)+1
        checks['finally_unlock_before_response']=all(r['lock']=='free' for r in responses)
        state=c15.wp('$o=wc_get_order('+str(oid)+');echo wp_json_encode([$o->is_paid(),$o->get_date_paid()?->getTimestamp(),$o->get_transaction_id(),$o->get_payment_method()]);')
        checks['native_paid_no_gateway_no_transaction']=state[0] and bool(state[1]) and state[2:]==['','']
        c15.save(label+'-native',{'responses':responses,'note_delta':len(after_notes)-len(prior),'state':state})
    finally:
        if installed:
            import subprocess
            cleanup = 'from pathlib import Path; import hashlib; p=Path("/app/sites/imagine-test-demo/wp-content/mu-plugins/imagine-c15-concurrent-witness.php"); assert hashlib.sha256(p.read_bytes()).hexdigest()=='+repr(digest)+'; p.unlink(); print(not p.exists())'
            p=subprocess.run(['wsl.exe','docker','exec','-i','staging-wp-dashboard','python'],input=cleanup,capture_output=True,text=True,check=True)
            checks['temporary_MU_removed']=p.stdout.strip()=='True' and c15.wp('echo wp_json_encode(!file_exists(WP_CONTENT_DIR.'+json.dumps('/'+target)+'));') is True
        w.restore(before)
        checks['owned_all_dates_restored']=w.snapshot()==before
        checks['catalogue_semantic_exact']=c15.load_test('c15-action').snapshot()==broad
    result={'checks':checks,'total':len(checks),'failures':[k for k,v in checks.items() if v is not True],'responses':responses,'global_C09_reset':False}
    c15.save(label,result)
    print(json.dumps(result))
    return not result['failures']

if __name__=='__main__':
    sys.exit(0 if verify(sys.argv[1], '--refus' in sys.argv) else 1)
