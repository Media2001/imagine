"""C15 single native A-VIR action and C09 reset; no other fixture invented."""
from pathlib import Path
from html import unescape
import json
import re
import sys
from urllib.parse import urlencode, unquote
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import c15


def snapshot():
    return c15.wp(r'''$f=get_option('imagine_c09_fixture');$out=['fixture'=>$f,'seeded'=>get_option('imagine_c09_seeded_at'),'decouverte'=>[],'orders'=>[],'subs'=>[],'members'=>[]];foreach(['V-DEC','V-DEC-FIN'] as $key){$id=$f['users'][$key];$out['decouverte']['imagine_decouverte_compte_'.$id]=get_option('imagine_decouverte_compte_'.$id,null);}$out['roles']=wp_roles()->roles;foreach(array_merge(array_values($f['orders']),array_values($f['renewals'])) as $id){$o=wc_get_order($id);$out['orders'][$id]=[$o->get_status(),$o->get_date_paid()?->getTimestamp(),$o->get_total(),$o->get_payment_method(),$o->get_customer_id(),$o->get_address('billing'),$o->get_address('shipping')];}foreach($f['subscriptions'] as $k=>$id){$s=wcs_get_subscription($id);$out['subs'][$k]=[$s->get_status(),$s->get_time('start'),$s->get_time('end'),$s->get_time('next_payment'),$s->get_address('shipping')];}foreach($f['memberships'] as $k=>$id){$m=wc_memberships_get_user_membership($id);$out['members'][$k]=[$m->get_status(),$m->get_start_date(),$m->get_end_date('mysql',false)];}echo wp_json_encode($out);''')


def reset(before):
    # C09 canonical reset at its original fixture clock, not a new fixture date.
    # Its C12 initializer resets discovery; restore those dependent profiles exactly.
    code = '$GLOBALS["imagine_c09_now"]=new DateTimeImmutable(' + json.dumps(before['seeded']) + ',new DateTimeZone("UTC"));ob_start();(static function(){require WP_CONTENT_DIR."/imagine-demo-build/c09-seed.php";})();ob_end_clean();$old=json_decode(' + json.dumps(json.dumps(before['decouverte'])) + ',true);foreach($old as $k=>$v){if($v===null){delete_option($k);}else{update_option($k,$v);}}echo "true";'
    c15.wp(code)
    # The dependent C14 initializer computes its own paid date. Preserve that
    # previously observed native date, rather than moving P-NUMERO with C15.
    pnum = before['fixture']['orders']['P-NUMERO']
    paid = before['orders'][str(pnum)][1]
    c15.wp('$o=wc_get_order(' + str(pnum) + ');if($o->get_meta("_imagine_c09_fixture")!=="P-NUMERO")throw new RuntimeException("Wrong owner");$o->set_date_paid(' + ('null' if paid is None else str(paid)) + ');$o->save();echo "true";')
    after = snapshot()
    c15.save('restauration', {'C09_reset': True, 'dependent_discovery_restored': before['decouverte'] == after['decouverte'], 'baseline_semantic_equal': before == after, 'theme_written': False})
    if before != after:
        c15.save('restore-diff', {'before': before, 'after': after})
        raise RuntimeError('C09 semantic restore mismatch; inspect C15/restore-diff.json')


def verify():
    c15.profils.guard('imagine-test-demo')
    h = c15.load_test('c12-http')
    accounts = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))['c09_accounts']
    clients = {k: h.login(accounts[k]) for k in ('E-ABO', 'E-ADMIN', 'E-REDAC', 'A-CARTE')}
    f = c15.wp('echo wp_json_encode(get_option("imagine_c09_fixture"));')
    oid = f['orders']['A-VIR']
    endpoint = '/wp-admin/admin-post.php'
    _, _, page = h.fetch('/wp-admin/admin.php?page=imagine-echeances&vue=virements', clients['E-ABO'])
    match = re.search(r'name="action" value="imagine_virement_recu".*?name="_wpnonce" value="([^"]+)"', page, re.S)
    checks = {'formulaire_paiement_recu': match is not None}
    if not match:
        c15.save('action-red', {'checks': checks}); print(checks); raise SystemExit(1)
    payload = {'action': 'imagine_virement_recu', 'commande': str(oid), '_wpnonce': unescape(match.group(1))}
    before = snapshot()
    paid_state = lambda: c15.wp('$o=wc_get_order(' + str(oid) + ');echo wp_json_encode([$o->is_paid(),$o->get_date_paid()?->getTimestamp(),$o->get_status()]);')
    for role in ('E-REDAC', 'A-CARTE'):
        status, _, _ = h.fetch(endpoint, clients[role], urlencode(dict(payload, confirmer='oui')).encode())
        checks['paiement_cap_refus_' + role] = status == 403 and not paid_state()[0]
    for name, data in [('absent', {k:v for k,v in payload.items() if k != '_wpnonce'}), ('invalide', dict(payload, _wpnonce='invalide')), ('tableau', dict(payload, **{'_wpnonce[]': 'invalide', '_wpnonce': ''}))]:
        status, _, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(data).encode())
        checks['paiement_nonce_' + name] = status == 403 and not paid_state()[0]
    status, _, review = h.fetch(endpoint, clients['E-ABO'], urlencode(payload).encode())
    checks['confirmation_serveur_sans_ecriture'] = status == 200 and 'name="confirmer" value="oui"' in review and 'A-VIR' in review and not paid_state()[0] and snapshot() == before
    status, _, _ = h.fetch(endpoint + '?' + urlencode(dict(payload, confirmer='oui')), clients['E-ABO'])
    checks['paiement_GET_refuse'] = status == 405 and not paid_state()[0]
    status, _, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(dict(payload, commande=str(f['orders']['A-CARTE']), confirmer='oui')).encode())
    checks['nonce_lie_commande'] = status == 403 and not paid_state()[0]
    # Valid user-specific nonces for wrong native objects: guard must reject independently.
    for name, target in [('deja_paye', f['orders']['A-CARTE']), ('echec_pas_virement', f['renewals']['A-GRACE']), ('souscription_pas_commande', f['subscriptions']['A-VIR'])]:
        jar = next(handler.cookiejar for handler in clients['E-ABO'].handlers if hasattr(handler, 'cookiejar'))
        cookie = unquote(next(c.value for c in jar if c.name.startswith('wordpress_logged_in_')))
        nonce = c15.wp('$_COOKIE[LOGGED_IN_COOKIE]=' + json.dumps(cookie) + ';wp_set_current_user(' + str(f['users']['E-ABO']) + ');echo wp_json_encode(wp_create_nonce("imagine_virement_recu:' + str(target) + '"));')
        status, _, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(dict(payload, commande=str(target), _wpnonce=nonce, confirmer='oui')).encode())
        checks['objet_refuse_' + name] = status == 409 and not paid_state()[0]
    if not all(checks.values()):
        c15.save('action', {'checks': checks}); print(checks); raise SystemExit(1)
    prior_notes = c15.wp('echo wp_json_encode(array_map(static fn($n)=>$n->content,wc_get_order_notes(["order_id"=>' + str(oid) + '])));')
    prior_own_count = sum('C15' in n and 'e-abo' in n for n in prior_notes)
    # Only authorized mutation: existing A-VIR. Always reset, even on ambiguous HTTP.
    try:
        status, _, text = h.fetch(endpoint, clients['E-ABO'], urlencode(dict(payload, confirmer='oui')).encode())
        state = paid_state()
        checks['paiement_natif_paye_date'] = status == 200 and state[0] and bool(state[1]) and state[2] in ('processing', 'completed')
        notes = c15.wp('echo wp_json_encode(array_map(static fn($n)=>$n->content,wc_get_order_notes(["order_id"=>' + str(oid) + '])));')
        own = [n for n in notes if 'C15' in n and 'e-abo' in n and re.search(r'\d{4}-\d{2}-\d{2}.*UTC', n)]
        checks['note_operateur_datee_native'] = len(own) == prior_own_count + 1
        status, _, _ = h.fetch(endpoint, clients['E-ABO'], urlencode(dict(payload, confirmer='oui')).encode())
        notes2 = c15.wp('echo wp_json_encode(count(wc_get_order_notes(["order_id"=>' + str(oid) + '])));')
        checks['double_validation_refusee_sans_double_note'] = status == 409 and notes2 == len(notes)
        c15.save('paiement-readback', {'order_id': oid, 'native_state': state, 'dated_operator_note': bool(own)})
    finally:
        reset(before)
        checks['reset_C09_relu'] = snapshot() == before and not paid_state()[0]
    c15.save('action', {'total': len(checks), 'checks': checks, 'failures': [k for k,v in checks.items() if v is not True]})
    print(json.dumps({'total': len(checks), 'failures': [k for k,v in checks.items() if v is not True]}))
    if not all(v is True for v in checks.values()):
        raise SystemExit(1)
    return checks


if __name__ == '__main__':
    verify()
