"""Preserve A09 delivery and qualify only named sibling transitions, without Git."""
import hashlib
import json
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[2]
LOT = ROOT/'production/A-09'
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    archive = LOT/'avant-corrections'
    assert not archive.exists()
    old = json.loads((LOT/'baseline.json').read_text())
    a08 = json.loads((ROOT/'production/A-08/manifeste.json').read_text())
    a08sources = a08['sources']
    drift = {n: {'old': h, 'new': sha(ROOT/n)} for n,h in old.items() if sha(ROOT/n) != h}
    readme = 'wp/tests/a02-audit/README.md'
    extra = (b'Complement A-10 : php wp/outils/bascule/inventorier-codes --wp-path=/copie-verifiee --audit=/hors-web/audit-date/audit.json --output=/hors-web/codes-date\n'
             b'Lecture seule ; sortie soeur du rapport A-02, hors site et depot ; noms de codes autorises, emails comptes uniquement ; rejeu : python wp/tests/a10/run.py\n')
    data = (ROOT/readme).read_bytes()
    assert data.endswith(extra) and hashlib.sha256(data[:-len(extra)]).hexdigest() == old[readme]
    allowed = {'wp/outils/bascule/a08/sequence.py','wp/outils/bascule/repetition.md','wp/tests/a08/test_sequence.py','wp/tests/a08/inside.py'}
    assert set(drift) <= allowed|{readme}, drift
    for n in set(drift)-{readme}:
        assert a08sources[n] == drift[n]['new'], n
    hist = {p.relative_to(ROOT).as_posix(): sha(p) for p in (LOT/'preuves').rglob('*') if p.is_file()}
    archive.mkdir()
    for name in ['baseline.json','manifeste.json','PRET','notes.md','verifier.py','verification-avant-pret.json','verification-finale.json']:
        shutil.copyfile(LOT/name,archive/name)
        assert sha(LOT/name)==sha(archive/name)
    hist.update({p.relative_to(ROOT).as_posix():sha(p) for p in archive.iterdir()})
    protected = {n:sha(ROOT/n) for n in old}
    # All other accepted bascule tools must remain at current bytes.
    for folder in ['wp/outils/bascule','wp/tests/a09','wp/tests/a10']:
        for p in (ROOT/folder).rglob('*'):
            n=p.relative_to(ROOT).as_posix()
            if p.is_file() and '__pycache__' not in p.parts and not n.startswith('wp/tests/a09/') and n not in ['wp/outils/bascule/a09/check.py','wp/outils/bascule/tester-redirections.md']:
                protected[n]=sha(p)
    def write(name,obj):
        (LOT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    write('historique-corrections.json',hist)
    write('baseline.json',protected)
    write('transition-corrections.json',{'drift':drift,'readme_exact_two_line_removal_restores_old_sha256':True,'a08_manifest_sha256':sha(ROOT/'production/A-08/manifeste.json'),'a08_proof':a08['proof'],'new_test_package':False,'image_preparation':'Existing A09 Python package extended; historical preparation preserved; no new package.'})
    (LOT/'PRET').unlink()
    print(json.dumps({'drift':drift,'historical_files':len(hist),'protected':len(protected)},indent=2))
if __name__=='__main__':
    main()
