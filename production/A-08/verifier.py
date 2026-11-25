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
    transition=json.loads((LOT/'transition-corrections-2140.json').read_text())
    original=json.loads((LOT/'baseline.json').read_text())
    update=transition['approved_a10_two_lines']
    assert update['actual_path']=='wp/tests/a02-audit/README.md'
    data=(ROOT/update['actual_path']).read_bytes()
    assert hashlib.sha256(b''.join(data.splitlines(keepends=True)[:-2])).hexdigest()==original[update['actual_path']]
    assert sha(ROOT/update['actual_path'])==update['current_sha256']
    assert sha(ROOT/'wp/outils/bascule/README.md')==original['wp/outils/bascule/README.md']
    platform=json.loads((LOT/'windows-importerror.json').read_text())
    assert platform['exit']==1 and platform['no_state_created'] is True
    assert 'A08_LINUX_REQUIRED' in platform['stderr'] and 'A08_REPORT_NOT_UPDATED' in platform['stderr'] and 'Traceback' not in platform['stderr']
    perimeter=json.loads((LOT/'controle-perimetre-corrections.json').read_text())
    assert perimeter['protected_and_history_drift']==[] and perimeter['parent_lock_unchanged'] is True
    assert perimeter['corrections_a08_unchanged'] is True
    assert manifest['technical_ready_only'] is True and manifest['not_a_real_go'] is True
    assert 'III.6' in manifest['ced_question_deferred']
    import importlib.util
    spec=importlib.util.spec_from_file_location('a08_verified_closure',ROOT/'wp/outils/bascule/a08/sequence.py')
    sequence=importlib.util.module_from_spec(spec);spec.loader.exec_module(sequence)
    closure={name:sha(ROOT/'wp/outils/bascule'/name) for name in sequence.DEPENDENCIES}
    assert len(closure)==23
    assert not any('a09' in n or 'a10' in n or 'inventorier-codes' in n for n in closure)
    assert '../../plugins/imagine-non-regression/src/Report.php' in closure
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
        for key in ['external_comparison_change_refused_before_native','incomplete_new_pass_current_stop_report',
                    'missing_input_current_stop_report','success_revalidated_after_adversary','per_pass_comparison_and_duration_report']:
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
        assert final['schema']=='imagine-a08-v2' and final['identity']['tools']==closure
        assert len(final['attempts'])==13 and final['comparison']=={'attendu':0,'anormal':0}
        assert final['comparisons']=={'1':{'attendu':len(one['changes']),'anormal':0},'2':{'attendu':0,'anormal':0}}
        assert [row['pass'] for row in final['attempts']]==[1]*7+[2]*6
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
        sections=text.split('## Passage ')
        assert len(sections)==3
        durations[storage]={}
        for number,section in enumerate(sections[1:],1):
            assert section.startswith(str(number)+'\n') and 'cumulées dans ce passage' in section
            comparison=final['comparisons'][str(number)]
            assert 'attendus : '+str(comparison['attendu'])+', anormaux : '+str(comparison['anormal']) in section
            times={name:sum(row['duration_seconds'] for row in final['attempts'] if row['step']==name and row['pass']==number) for name in steps}
            for name,seconds in times.items():
                assert '| '+name+' | '+format(seconds,'.3f')+' | OK |' in section
            durations[storage][str(number)]={name:round(seconds,3) for name,seconds in times.items()}
        assert 'ARRÊT' in (proof/(storage+'-missing-input-report.md')).read_text(encoding='utf8')
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
    assert transition['new_test_package'] is False
    for key in ['unit','a02_regression','a03_regression','a03-boundary_regression','a04_regression','a05_regression','integration','cleanup_exact_owned','sources_unchanged']:
        assert any(row['check']==key and row['ok'] for row in runner['checks']),key
    for method in ['test_dependency_closure_refuses_external_code_but_ignores_other_lots',
                   'test_missing_input_after_success_replaces_stale_report','test_incomplete_new_pass_refreshes_report',
                   'test_concurrent_refusal_leaves_report_and_warns_stderr','test_missing_fcntl_stable_no_traceback',
                   'test_pass_reports_retain_first_comparison_and_attributed_durations']:
        assert method in unit,method
    documentation=(ROOT/'wp/outils/bascule/repetition.md').read_text(encoding='utf8')
    assert '**Code 2 :**' in documentation and 'sauvegarde de départ vérifiée' in documentation and '**nouvel état**' in documentation
    if sys.argv[1:]==['--sans-pret']:
        assert not (LOT/'PRET').exists()
    else:
        assert not sys.argv[1:],'Unknown verifier option'
        pret=json.loads((LOT/'PRET').read_text(encoding='utf8'))
        assert pret['manifest_sha256']==sha(LOT/'manifeste.json') and pret['technical_ready_only'] is True
        assert pret['ced_question_deferred']==manifest['ced_question_deferred']
    print(json.dumps({'exit_code':0,'verified_files':verified,'counts':manifest['counts'],'durations_seconds_by_pass':durations,'proof':manifest['proof']},indent=2))
    return 0


if __name__=='__main__':
    sys.exit(main())
