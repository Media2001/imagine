"""Contre-exemples du vrai lecteur livré, aucune mutation du dépôt/site."""
import sys
sys.dont_write_bytecode = True
import contextlib
import importlib.util
import io
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[2]
lot = sys.argv[1] if len(sys.argv) > 1 else 'B-13'
spec = importlib.util.spec_from_file_location('qualification_reader', ROOT/'production'/lot/'verifier.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
owner = v.owner
m = v.load('reception-V2.json')
boot = ROOT/'wp/plugins/imagine-site/imagine-site.php'
readme = ROOT/'wp/plugins/imagine-site/README.md'
original_bytes = Path.read_bytes
original_text = Path.read_text
raw = boot.read_bytes()
text = readme.read_text(encoding='utf-8')
results = {}
def run(name, context, refused):
    caught = False
    with context, contextlib.redirect_stdout(io.StringIO()):
        try:
            v.verify(False, m, False)
        except AssertionError:
            caught = True
    assert caught == refused, name
    results[name] = True

def bytes_at(path, new):
    return patch.object(Path, 'read_bytes', lambda p: new if p == path else original_bytes(p))
def text_at(new):
    return patch.object(Path, 'read_text', lambda p,*a,**kw: new if p == readme else original_text(p,*a,**kw))
run('fichier_propre_modifie_refuse', bytes_at(ROOT/'wp'/owner.FILES[0], (ROOT/'wp'/owner.FILES[0]).read_bytes()+b'\n// mutant\n'), True)
run('bloc_absent_refuse', bytes_at(boot, raw.replace(owner.BLOCK.encode(), b'', 1)), True)
run('bloc_duplique_refuse', bytes_at(boot, raw+owner.BLOCK.encode()), True)
run('bloc_modifie_refuse', bytes_at(boot, raw.replace(owner.BLOCK.encode(), owner.BLOCK.replace('::register();', '::register(1);').encode(), 1)), True)
run('bloc_etranger_accepte', bytes_at(boot, raw+b"\nrequire_once __DIR__ . '/Futur.php';\nFutur::register();\n"), False)
run('section_propre_modifiee_refusee', text_at(text.replace(owner.HEADING, owner.HEADING+'\nMutation', 1)), True)
run('section_absente_refusee', text_at(text.replace(owner.HEADING, '## Absent', 1)), True)
run('section_dupliquee_refusee', text_at(text+'\n'+owner.HEADING+'\nDoublon\n'), True)
run('section_etrangere_acceptee', text_at(text+'\n## Lot futur\nAucun lien métier.\n'), False)
print({'lot':lot,'checks':len(results),'PASS':all(results.values()),'results':results})
