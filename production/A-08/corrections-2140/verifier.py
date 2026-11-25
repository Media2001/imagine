"""Read-only parent acceptance: final bytes, native receipts, counts and scope."""
import hashlib
import json
import pathlib
import re
import sys
sys.dont_write_bytecode=True
ROOT=pathlib.Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-08'


def sha(path):
    with open(path,'rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    manifest=json.loads((LOT/'manifeste.json').read_text(encoding='utf8'))
    verified={}
    for kind in ['protected','sources','evidence','history','delivery']:
        entries=manifest[kind]
        assert entries,kind
        for name,digest in entries.items():
            path=ROOT/name
            assert path.is_file() and sha(path)==digest,(kind,name)
        verified[kind]=len(entries)
    proof=ROOT/manifest['proof']
    runner=json.loads((proof/'runner.json').read_text())
    assert runner['exit_code']==0 and all(row['ok'] for row in runner['checks'])
    assert runner['label']=='org.imagine.a08-repetition'
    for filename in ['inspect-before.json','inspect-after.json']:
        info=json.loads((proof/filename).read_text())
        assert info['Name']=='/'+runner['container']
        assert info['Config']['Labels'][runner['label']]==runner['container']
        assert info['HostConfig']['NetworkMode']=='none' and not info['Mounts']
        assert not info['HostConfig'].get('PortBindings') and not info['HostConfig']['Privileged']
    cleanup=next(row for row in runner['checks'] if row['check']=='cleanup_exact_owned')
    assert cleanup['ok'] and re.search(r'no such (object|container)',cleanup['detail']['diagnostic'],re.I)
    inner=json.loads((proof/'result.json').read_text())
    assert inner['exit_code']==0 and all(row['ok'] for row in inner['checks'])
    names={row['check'] for row in inner['checks']}
    steps=['audit','avant','mise-a-jour','nettoyage','apres','comparaison']
    durations={}
    for storage in ['classic','hpos']:
        for key in ['real_middle_refusal','refusal_no_later_step','refusal_database_files_exact',
                    'resume_update_cleanup_native','complete_native_expected_only','second_native_business_invariants',
                    'second_comparison_identical','second_all_six_tools_really_run','staging_guard_bytes_unchanged']:
            assert storage+':'+key in names,(storage,key)
        assert storage+':native_timeout_refresh_source' in names
        fingerprints=json.loads((proof/(storage+'-second-mutation-fingerprints.json')).read_text())
        before,after=fingerprints['before'],fingerprints['after']
        assert {k:v for k,v in before['files'].items() if k!='.maintenance'}=={k:v for k,v in after['files'].items() if k!='.maintenance'}
        assert set(fingerprints['file_changes'])<={'.maintenance'}
        assert {k:v for k,v in before['database']['tables'].items() if k!='wp_options'}=={k:v for k,v in after['database']['tables'].items() if k!='wp_options'}
        assert before['database']['tables']['wp_options']['schema_sha256']==after['database']['tables']['wp_options']['schema_sha256']
        options=json.loads((proof/(storage+'-second-option-fingerprints.json')).read_text())
        expiry='_transient_timeout_wcs_woocommerce_active_version'
        assert set(options['changed'])<={expiry} and set(options['before'])==set(options['after'])
        assert {k:v for k,v in options['before'].items() if k!=expiry}=={k:v for k,v in options['after'].items() if k!=expiry}
        source=json.loads((proof/(storage+'-native-timeout-source.json')).read_text())
        assert source['sha256']==before['files']['wp-content/plugins/'+source['file']]
        assert source['hook']=='woocommerce_init' and 'set_transient(' in source['statement']
        state=proof/(storage+'-sequence')
        refused=json.loads((proof/(storage+'-refused-checkpoint.json')).read_text())
        assert list(refused['done'])==steps[:2] and len(refused['attempts'])==3
        assert refused['attempts'][-1]['step']=='mise-a-jour' and refused['attempts'][-1]['exit']==1
        assert (state/'mise-a-jour-1-stderr.log').read_text()=='A04_MAINTENANCE\n'
        first=json.loads((proof/(storage+'-first-complete.json')).read_text())
        assert list(first['done'])==steps and first['comparison']['anormal']==0
        one=json.loads((state/'comparaison-1-stdout.log').read_text())
        assert one['anormal']==0 and one['changes'] and all(row['class']=='attendu' for row in one['changes'])
        assert json.loads((state/'comparaison-1-receipt.json').read_text())['exit']==3
        final=json.loads((state/'etat.json').read_text())
        assert list(final['done'])==steps and len(final['passes'])==1
        assert len(final['attempts'])==13 and final['comparison']=={'attendu':0,'anormal':0}
        two=json.loads((state/'comparaison-2-stdout.log').read_text())
        assert two['changes']==[] and two['anormal']==0
        assert json.loads((state/'comparaison-2-receipt.json').read_text())['exit']==0
        for entry in [*final['done'].values(),*final['passes'][0].values()]:
            for relative,digest in entry['seals'].items():assert sha(state/relative)==digest
        for label in ['avant-1','avant-2','apres-1','apres-2']:
            photo=json.loads((state/label/'non-regression.json').read_text())
            assert photo['storage']==storage and photo['php_log']['checked'] is True and photo['php_log']['errors']==0
        assert len(list(state.glob('rapport*.md')))==1
        text=(state/'rapport.md').read_text(encoding='utf8')
        assert 'TERMINÉ' in text and 'anormaux : 0' in text
        assert all('| '+name+' |' in text for name in steps)
        durations[storage]={name:round(sum(row['duration_seconds'] for row in final['attempts'] if row['step']==name),3) for name in steps}
    unit=(proof/'unit.log').read_text()
    assert unit.rstrip().endswith('OK')
    count=int(re.search(r'Ran (\d+) tests?',unit)[1])
    assert count==manifest['counts']['a08_unit']
    assert len(inner['checks'])==manifest['counts']['native_checks']
    assert len(runner['checks'])==manifest['counts']['runner_checks']
    audit=json.loads((proof/'a02-unit.json').read_text())['checks']
    assert len(audit)==manifest['counts']['a02_unit'] and all(row['status']=='PASS' for row in audit)
    a03=json.loads((proof/'a03-unit.json').read_text())
    assert a03['exit_code']==0 and all(a03['tests'].values()) and len(a03['tests'])==manifest['counts']['a03_unit']
    boundary=json.loads((proof/'output-boundary.json').read_text())
    assert all(boundary.values()) and len(boundary)==manifest['counts']['a03_boundaries']
    for lot in ['a04','a05']:
        log=(proof/(lot+'-regression.log')).read_text()
        assert log.rstrip().endswith('OK') and int(re.search(r'Ran (\d+) tests?',log)[1])==manifest['counts'][lot+'_unit']
    prep=json.loads((LOT/'preparer-image.json').read_text())
    assert prep['exit']==0 and prep['command'][-1]=='wp/tests/preparer-image.ps1'
    assert 'T01 IMAGE READY' in (LOT/'preparer-image.log').read_text(encoding='utf8',errors='replace')
    if sys.argv[1:]==['--sans-pret']:
        assert not (LOT/'PRET').exists()
    else:
        assert not sys.argv[1:],'Unknown verifier option'
        pret=json.loads((LOT/'PRET').read_text(encoding='utf8'))
        assert pret['manifest_sha256']==sha(LOT/'manifeste.json')
    print(json.dumps({'exit_code':0,'verified_files':verified,'counts':manifest['counts'],'durations_seconds_cumulative':durations,'proof':manifest['proof']},indent=2))
    return 0


if __name__=='__main__':
    sys.exit(main())
