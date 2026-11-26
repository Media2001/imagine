"""Read-only fourth-pass receipt/source verification, no Docker or archive access."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('acceptance',type=Path)
    p.add_argument('units',type=Path)
    args=p.parse_args()
    acceptance=json.loads(args.acceptance.read_text(encoding='utf-8'))
    units=json.loads(args.units.read_text(encoding='utf-8'))
    for receipt in (acceptance,units):
        assert receipt['status']=='PASS' and receipt['cleanup']['absent'] and receipt['sources_unchanged']
        assert receipt['synthetic_only']
        for rel,digest in receipt['source_manifest'].items():
            assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,rel
    inside=acceptance['inside']; cli=acceptance['database_cli']
    assert inside['status']=='PASS' and inside['database_bytes']>474*1024**2
    required={'retained_large_database_import','wide_rows_readback','json_generated_zero_dates','myisam_memory_engines',
              'mysql8_collation_emulation','duplicate_key_failure','actual_timeout','actual_php_exception','three_native_phases'}
    assert set(inside['checks'])==required
    assert inside['native']['data_verified'] is True and [s['exit'] for s in inside['native']['steps']]==[0,0,0]
    failure=inside['checks']['duplicate_key_failure']
    assert failure['stage']=='database_import' and failure['database']['errno']==1062
    assert failure['database']['sqlstate']=='23000' and failure['database']['line']>0
    assert failure['database']['statement']=='INSERT' and failure['database']['table']=='SERVMASK_PREFIX_options'
    assert inside['checks']['actual_php_exception']['php']=={'class':'LogicException','file':'plugins/fiction/fatal.php','line':1}
    assert inside['checks']['actual_timeout']['timeout_seconds']==.1
    assert cli['status']=='DATABASE_IMPORTED_NATIVE_DEFERRED' and not cli['data_verified'] and not cli['full_staging_ready']
    assert not cli['created_sites'] and cli['extracted_wp_content_files']==0 and not cli['non_database_payloads_read']
    assert cli['cleanup']['absent'] and cli['sources_unchanged'] and not cli['native_phases']['executed']
    assert acceptance['scratch_removed']
    for label in ('isolation_before','isolation_after'):
        for receipt in (acceptance,cli,units):
            isolation=receipt[label]
            assert isolation['network']=='none' and not isolation['ports'] and not isolation['mounts'] and not isolation['privileged']
    assert all(command['exit']==0 for command in units['commands'])
    log=(args.units.parent/'tests.log').read_text(encoding='utf-8')
    match=re.search(r'Ran (\d+) tests? in ',log)
    assert match and log.rstrip().endswith('OK')
    for text in (json.dumps(acceptance),json.dumps(units)):
        assert 'FICTION_PRIVATE@example.org' not in text and 'Duplicate entry' not in text
    print(json.dumps({'verified':True,'acceptance':str(args.acceptance),'units':str(args.units),
          'unit_tests':int(match[1]),'runtime_checks':len(required),'database_bytes':inside['database_bytes'],
          'validation_seconds':inside['validation_seconds'],'retained_import_seconds':inside['checks']['retained_large_database_import']['elapsed_seconds'],
          'database_cli_seconds':cli['elapsed_seconds'],'native_three_phases':True,'all_owned_runners_removed':True,
          'real_archive_accessed':False,'publication_or_real_go':False},indent=2))
    return 0


if __name__=='__main__': raise SystemExit(main())
