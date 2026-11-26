"""A15 final packet verifier, source membership + native privacy and safety."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OWN=['wp/tests/a15','wp/outils/bascule/a15']
AUDIT_BASE='3ca4c1bff4350ad7e5c5d0725b6f42958889842dcb60007e74a2ccf7b0d53af3'
APPENDIX=(
    'Complément A-15 (emails natifs, lecture seule) : python3 wp/outils/bascule/a15/confine.py --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/emails-date\n'
    "Noms et oui/non uniquement, jamais destinataire/objet/corps ; conteneur déconnecté + Landlock, garde d'envoi éprouvée ; limites des services extérieurs et mode d'emploi : wp/outils/bascule/a15/README.md\n"
).encode('utf-8')

def doc_contract(data):
    lines=data.splitlines(keepends=True)
    return all(lines.count(line)==1 for line in APPENDIX.splitlines(keepends=True))

def inventory(roots):
    files=[]
    for key in roots:
        p=ROOT/key;files.extend([p] if p.is_file() else [x for x in p.rglob('*') if x.is_file()])
    return {p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if '__pycache__' not in p.parts}

def verify(packet):
    checks=[]
    def check(name,ok):checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    sources=json.loads((packet/'sources.json').read_text());check('exact_owned_source_inventory',sources==inventory(OWN))
    for name in ['unit','result','runner']:
        data=json.loads((packet/(name+'.json')).read_text());names=[c['check'] for c in data['checks']]
        check(name+'_actual_green',data['exit_code']==0 and bool(names) and all(c['status']=='PASS' for c in data['checks']))
        check(name+'_unique_assertion_names',len(names)==len(set(names)))
    runner=json.loads((packet/'runner.json').read_text());check('native_and_runner_cleanup',runner['mode']=='native' and {'isolation_before','isolation_after','cleanup_exact_owned_runner','owned_sources_stable','dependencies_stable'}.issubset(c['check'] for c in runner['checks']))
    native=json.loads((packet/'result.json').read_text());names={c['check'] for c in native['checks']}
    for storage in ['classic','hpos']:
        required=['cli_and_actual_mail_sql_file_http_cron_guards','exact_native_registry','exact_active_counts_by_extension','disabled_subject_body_client','exact_theme_override','internal_custom_recipient_without_address','present_active_and_inactive_transport_versions','memberships_plan_body_customisation','native_formatter_not_transport','no_address_subject_body_canary_secret_path','transaction_blocks_even_privileged_root','canonical_repository_output_refused','storage_mismatch_refused','dropin_named_no_execution','all_tables_scheduler_identical','files_identical','config_not_executed']
        required += ['native_variants_defaults_empty_and_recipient_defaults','collected_refund_variant_and_invoice_default','common_templates_alone_counted_once_child_priority','common_template_parent_fallback']
        check(storage+'_mandatory_cases',all(storage+':'+key in names for key in required))
        before=json.loads((packet/(storage+'-db-before.json')).read_text());after=json.loads((packet/(storage+'-db-after.json')).read_text())
        check(storage+'_all_table_fingerprint',before==after and {'wp_options','wp_actionscheduler_actions','wp_actionscheduler_logs'}.issubset(before['tables']))
        data=json.loads((packet/(storage+'-emails/emails.json')).read_text());oracle=json.loads((packet/(storage+'-oracle.json')).read_text())
        check(storage+'_exact_registry_and_summary',data['registry']['email_count']==oracle['count']==len(data['emails']) and data['summary']['active_by_extension']==oracle['summary'])
        check(storage+'_audit_binding',data['storage']==storage and data['read_only'] is True and data['audit_sha256']==hashlib.sha256((packet/(storage+'-audit/audit.json')).read_bytes()).hexdigest())
        text=''.join(p.read_text() for p in (packet/(storage+'-emails')).iterdir())
        check(storage+'_report_privacy',not re.search(r'@|PRIVATE_CANARY|DB_PASSWORD|/scratch',text))
    style=json.loads((packet/'style/style.json').read_text())
    check('strict_psr12_final_sources',style['exit_code']==style['phpcs_exit']==0 and style['totals']['errors']==style['totals']['warnings']==0 and style['sources']==sources)
    prep=json.loads((packet/'preparation.json').read_text())
    check('real_preparer_image_success',prep['exit_code']==0 and prep['command'][-1]=='wp/tests/preparer-image.ps1' and 'image verifiee' in (packet/'preparation.log').read_text(encoding='utf-8'))
    doc=(ROOT/'wp/tests/a02-audit/README.md').read_bytes()
    check('shared_audit_doc_original_plus_exact_two_lines',doc_contract(doc))
    check('doc_contract_owns_only_exact_two_lines',doc_contract(b'other\n'+APPENDIX+b'later\n') and all(not doc_contract(x) for x in [APPENDIX[:-1],APPENDIX+APPENDIX,APPENDIX.replace(b'A-15',b'A-XX')]))
    payload=''.join(p.read_text(encoding='utf-8',errors='replace') for p in packet.rglob('*') if p.is_file())
    check('canary_absent_from_entire_packet',not re.search(r'a15-[\w-]+@example\.org|A15_[A-Z_]*PRIVATE_CANARY',payload))
    manifest=json.loads((packet/'manifest.json').read_text());expected=inventory(OWN+[packet.relative_to(ROOT).as_posix()]);expected.pop((packet/'manifest.json').relative_to(ROOT).as_posix(),None)
    check('exact_sealed_own_files_and_one_packet',manifest==expected)
    check('no_foreign_lot_pinned',all(k.startswith(tuple(OWN+[packet.relative_to(ROOT).as_posix()+'/'])) for k in manifest))
    result={'exit_code':int(any(c['status']!='PASS' for c in checks)),'checks':checks}
    print(json.dumps(result,indent=2));return result['exit_code']

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('packet',type=Path);a=ap.parse_args()
    try:sys.exit(verify(a.packet.resolve()))
    except Exception as e:print(json.dumps({'exit_code':1,'error':type(e).__name__}));sys.exit(1)
