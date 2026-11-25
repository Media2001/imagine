"""One-shot preservation and explicit corrected baseline, never touch sibling bytes."""
import hashlib
import json
import pathlib
import shutil

ROOT=pathlib.Path(__file__).resolve().parents[2]
LOT=ROOT/'production/A-08'
START=pathlib.Path('C:/Users/Ced/AppData/Local/hermes/cache/scratch/a08-start-2140.json')


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    initial=json.loads(START.read_text())
    archive=LOT/'corrections-2140'
    assert not archive.exists()
    old=json.loads((LOT/'baseline.json').read_text())
    readme='wp/tests/a02-audit/README.md'
    # Exactly the two A10 lines, not a blanket baseline refresh.
    extra=(b'Complement A-10 : php wp/outils/bascule/inventorier-codes --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/codes-date\n'
           b'Lecture seule ; sortie soeur du rapport A-02, hors site et depot ; noms de codes autorises, emails comptes uniquement ; rejeu : python wp/tests/a10/run.py\n')
    data=(ROOT/readme).read_bytes()
    assert data.endswith(extra)
    assert hashlib.sha256(data[:-len(extra)]).hexdigest()==old[readme]
    for name,digest in old.items():
        assert sha(ROOT/name)==(initial[name] if name==readme else digest),name
    history={name:digest for name,digest in initial.items() if name.startswith('production/A-08/preuves/')}
    for name,digest in history.items():
        assert sha(ROOT/name)==digest,name
    archive.mkdir()
    copies={}
    for filename in ['PRET','manifeste.json','verification-avant-pret.json','verification-finale.json','notes.md','sceller.py','verifier.py']:
        p=LOT/filename
        assert sha(p)==initial[p.relative_to(ROOT).as_posix()]
        target=archive/filename
        shutil.copyfile(p,target)
        assert sha(target)==sha(p)
        copies[target.relative_to(ROOT).as_posix()]=sha(target)
    protected=dict(old)
    protected[readme]=sha(ROOT/readme)
    for p in (ROOT/'wp/outils/bascule').rglob('*'):
        if p.is_file() and '__pycache__' not in p.parts and p.relative_to(ROOT).as_posix() not in ['wp/outils/bascule/a08/sequence.py','wp/outils/bascule/repeter','wp/outils/bascule/repetition.md']:
            name=p.relative_to(ROOT).as_posix()
            assert sha(p)==initial[name],name
            protected[name]=initial[name]
    for name,digest in initial.items():
        if (name.startswith(('production/A-09/','production/A-10/','wp/tests/a09/','wp/tests/a10/'))
                or name in ['wp/plugins/imagine-non-regression/src/Report.php','wp/plugins/imagine-non-regression/src/Policy.php','wp/plugins/imagine-non-regression/src/PhpLog.php','wp/outils/staging/runtime-probe.php','wp/outils/staging/mu-plugins/000-imagine-staging-safety.php']):
            assert sha(ROOT/name)==digest,name
            protected[name]=digest
    def write(name,value):
        p=LOT/name
        assert not p.exists()
        p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    write('baseline-corrections-2140.json',protected)
    write('historique-corrections-2140.json',history|copies)
    write('transition-corrections-2140.json',{
        'original_baseline_sha256':sha(LOT/'baseline.json'),
        'approved_a10_two_lines':{'actual_path':readme,'old_sha256':old[readme],'current_sha256':protected[readme],'removed_exact_append_restores_old_hash':True},
        'context_path_discrepancy':'wp/outils/bascule/README.md remains at original hash; actual two-line A10 append is wp/tests/a02-audit/README.md. Neither file modified by A08.',
        'preserved_history_files':len(history),'archived_delivery_files':copies,
        'protected_current_files':len(protected),'new_test_package':False,
        'image_preparation':'No new package, existing A08 tests extended; old preparation evidence retained, no shared/image modification.'})
    # Invalidate readiness only after immutable copies were verified.
    for name in ['PRET','manifeste.json','verification-avant-pret.json','verification-finale.json']:
        (LOT/name).unlink()
    print(json.dumps({'protected':len(protected),'history':len(history),'archived':len(copies)},indent=2))


if __name__=='__main__':
    main()
