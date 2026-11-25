"""Native A10 acceptance on the unchanged A02 synthetic bench."""
import importlib.util
import json
import pathlib
import re
import sys
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('a02', '/opt/a02/inside.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
OUT=pathlib.Path('/report')
original_check=b.check
def safe_check(name,ok,detail=None):
    if name.endswith(':commercial_fixture') and isinstance(detail,dict):
        detail={k:detail[k] for k in ['versions','hpos','subscriptions','rules','restriction_real']}
    return original_check(name,ok,detail)
b.check=safe_check

def inventory(site,out,*extra):
    return b.cmd(['php','/subject/inventorier-codes','--wp-path='+str(site),'--output='+str(out),*extra],check=False)

def run_storage(storage):
    site,db,_=b.install(storage)
    (OUT/(storage+'-seed.json')).unlink()
    config=(site/'wp-config.php').read_text()
    writable=config.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')").split("\nfile_put_contents('/scratch/a02-bootstrap-trap'")[0]
    (site/'wp-config.php').write_text(writable)
    try:
        p=b.wp(site,['eval-file','/opt/a10/seed.php','--use-include'],check=False)
        if p.returncode:
            (OUT/(storage+'-fixture-error.log')).write_text(p.stderr)
            raise RuntimeError('A10_NATIVE_SEED_FAILED')
        data=json.loads(next(x[9:] for x in p.stdout.splitlines() if x.startswith('A10_JSON=')))
    finally:
        (site/'wp-config.php').write_text(config)
    (OUT/(storage+'-oracle.json')).write_text(json.dumps(data,indent=2)+'\n')
    b.check(storage+':native_renewal_carries_coupon',data['renewal_carries_coupon'])
    # Audit guard: an existing A02 photograph in the same external parent is mandatory.
    auditdir=OUT/(storage+'-audit')
    old=b.audit(site,auditdir)
    b.check(storage+':a02_audit_compatible',old.returncode==0)
    before=b.fingerprint(db); fb=b.files(site)
    (OUT/(storage+'-db-before.json')).write_text(json.dumps(before,indent=2)+'\n')
    target=OUT/(storage+'-codes')
    p=inventory(site,target,'--audit='+str(auditdir/'audit.json'))
    b.check(storage+':command_available',pathlib.Path('/subject/inventorier-codes').exists())
    if p.returncode != 0:
        debug = b.cmd(['php'], env={'A10_SITE':str(site)}, data=r"<?php define('IMAGINE_AUDIT_LIBRARY_ONLY',true); require '/subject/audit'; require '/subject/a10/Projection.php'; require '/subject/a10/Inventory.php'; try { (new Imagine\CouponInventory\Inventory(getenv('A10_SITE')))->collect(); } catch (Throwable $e) { echo get_class($e).' '.$e->getMessage().' at '.$e->getFile().':'.$e->getLine(); }", check=False)
        (OUT/(storage+'-diagnostic.log')).write_text(debug.stdout+debug.stderr)
    b.check(storage+':cli_success',p.returncode==0,{'exit_code':p.returncode,'stderr':p.stderr if re.fullmatch(r'A(?:10|02)_[A-Z_]+\n',p.stderr) else 'suppressed'})
    report=json.loads((target/'codes.json').read_text())
    rows={x['code']:x for x in report['codes']}
    b.check(storage+':exact_inventory',set(rows)==set(data['expected']) and len(rows)==10)
    b.check(storage+':authoritative_storage',report['storage']==storage)
    for code,expected in data['expected'].items():
        actual=rows[code]
        b.check(storage+':native_fields:'+code,all(actual.get(k)==v for k,v in expected.items()))
    rec=rows['a10-recurring-fee']
    b.check(storage+':distinct_subscription_counts',rec['subscriptions']=={'active':1,'on_hold':1,'pending':1,'pending_cancel':1})
    b.check(storage+':exact_12month_orders',rec['orders_12_months']==5)
    b.check(storage+':other_coupon_counts_zero',all(v['orders_12_months']==0 and sum(v['subscriptions'].values())==0 for k,v in rows.items() if k!='a10-recurring-fee'))
    b.check(storage+':renewal_types',all(rows['a10-'+t.replace('_','-')]['recurring_on_renewals'] is (t in ['recurring_fee','recurring_percent']) for t in ['percent','fixed_cart','fixed_product','recurring_fee','recurring_percent','sign_up_fee','sign_up_fee_percent']))
    b.check(storage+':expired_separate',report['expired']==['a10-expired','a10-expired-never-used'])
    b.check(storage+':never_used_separate',report['never_used']==['a10-expired-never-used','a10-never-used'])
    full=(target/'codes.json').read_text()+(target/'codes.md').read_text()+p.stdout+p.stderr
    b.check(storage+':privacy',not re.search(r'@|PRIVATE_CANARY|customer_id|user_id|billing_|subscription_id|order_id',full))
    b.check(storage+':file_modes',target.stat().st_mode&0o777==0o700 and all(x.stat().st_mode&0o777==0o600 for x in target.iterdir()))
    again=OUT/(storage+'-repeat')
    repeat=inventory(site,again,'--audit='+str(auditdir/'audit.json'))
    b.check(storage+':repeat_exact_business_fields',repeat.returncode==0 and json.loads((again/'codes.json').read_text())['codes']==report['codes'])
    for key,args,dest in [
        ('missing_audit',[],OUT/(storage+'-no-audit')),
        ('output_in_web',['--audit='+str(auditdir/'audit.json')],site/'forbidden'),
        ('existing_output',['--audit='+str(auditdir/'audit.json')],target),
        ('output_in_source',['--audit='+str(auditdir/'audit.json')],pathlib.Path('/subject/forbidden')),
        ('unknown_argument',['--audit='+str(auditdir/'audit.json'),'--oops=yes'],OUT/(storage+'-bad-arg')),
    ]:
        reject=inventory(site,dest,*args)
        b.check(storage+':guard:'+key,reject.returncode==1 and (dest==target or not dest.exists()))
    # Symlink destination parent must resolve outside, never into site/source.
    link=OUT/(storage+'-web-link'); link.symlink_to(site,target_is_directory=True)
    bad=inventory(site,link/'forbidden','--audit='+str(auditdir/'audit.json'))
    b.check(storage+':guard:symlink_web_parent',bad.returncode==1 and not (site/'forbidden').exists()); link.unlink()
    wrong=OUT/(storage+'-bad-audit.json'); wrong.write_text('{"schema":"wrong","read_only":true}')
    bad=inventory(site,OUT/(storage+'-bad-audit'),'--audit='+str(wrong))
    b.check(storage+':guard:invalid_audit',bad.returncode==1 and not (OUT/(storage+'-bad-audit')).exists())
    # Root credential still cannot write inside the subject transaction.
    (site/'wp-config.php').write_text(config.replace("define('DB_USER', 'a02_"+storage+"')", "define('DB_USER', 'root')"))
    try:
        probe=b.cmd(['php','/opt/a10/readonly-probe.php'],env={'A10_SITE':str(site)},check=False)
        b.check(storage+':root_transaction_write_denied',probe.returncode==0 and json.loads(probe.stdout)['blocked'])
    finally: (site/'wp-config.php').write_text(config)
    # Exercise the real checkout-layout repository guard, not only standalone fallback.
    import shutil
    canonical=pathlib.Path('/checkout/wp/outils/bascule')
    if not canonical.exists():
        canonical.parent.mkdir(parents=True,exist_ok=True)
        shutil.copytree('/subject',canonical)
    guarded=b.cmd(['php',str(canonical/'inventorier-codes'),'--wp-path='+str(site),'--output=/checkout/forbidden','--audit='+str(auditdir/'audit.json')],check=False)
    b.check(storage+':guard:canonical_repository',guarded.returncode==1 and guarded.stderr=='A10_OUTPUT_UNSAFE\n' and not pathlib.Path('/checkout/forbidden').exists())
    wrongphoto=json.loads((auditdir/'audit.json').read_text())
    wrongphoto['sections']['commerce']['order_storage']='classic' if storage=='hpos' else 'hpos'
    # The audit must be nested in a photograph directory with the common report parent.
    # Place the synthetic bad photograph there to reach the storage-specific guard.
    wrongnested=OUT/(storage+'-wrong-audit'); wrongnested.mkdir()
    (wrongnested/'audit.json').write_text(json.dumps(wrongphoto))
    mismatch=inventory(site,OUT/(storage+'-storage-mismatch'),'--audit='+str(wrongnested/'audit.json'))
    b.check(storage+':guard:storage_mismatch',mismatch.returncode==1 and mismatch.stderr=='A10_AUDIT_STORAGE_MISMATCH\n' and not (OUT/(storage+'-storage-mismatch')).exists())
    (site/'wp-config.php').write_text(config.replace("define('DB_PASSWORD', '')", "define('DB_PASSWORD', getenv('A10_PRIVATE_CONFIG_CANARY'))"))
    try:
        dynamic=inventory(site,OUT/(storage+'-dynamic'),'--audit='+str(auditdir/'audit.json'))
        b.check(storage+':guard:dynamic_config',dynamic.returncode==1 and dynamic.stderr=='A02_CONFIG_NON_LITERAL\n' and not (OUT/(storage+'-dynamic')).exists())
    finally: (site/'wp-config.php').write_text(config)
    b.check(storage+':existing_output_bytes_preserved',json.loads((target/'codes.json').read_text())==report)
    after=b.fingerprint(db)
    (OUT/(storage+'-db-after.json')).write_text(json.dumps(after,indent=2)+'\n')
    b.check(storage+':database_identical_all_tables',before==after,{'before':before['logical_sha256'],'after':after['logical_sha256'],'tables':len(before['tables'])})
    b.check(storage+':site_files_identical',fb==b.files(site))
    b.check(storage+':never_bootstrap',not pathlib.Path('/scratch/a02-bootstrap-trap').exists())
    # No DB mutations after this point; A02 independent snapshot equality includes cron/actions.

b.run_storage=run_storage
if __name__=='__main__':
    for file in sorted(pathlib.Path('/subject/a10').glob('*.php')) + [pathlib.Path('/subject/inventorier-codes')] + sorted(pathlib.Path('/opt/a10').glob('*.php')):
        lint=b.cmd(['php','-l',str(file)],check=False)
        b.check('a10_lint:'+file.name,lint.returncode==0)
    result=b.main()
    path=OUT/'result.json'
    payload=json.loads(path.read_text())
    payload['suite']='A10-native-coupon-inventory-on-A02-bench'
    path.write_text(json.dumps(payload,indent=2)+'\n')
    sys.exit(result)
