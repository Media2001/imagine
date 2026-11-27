"""B14 corrections et compléments ciblés, aucun reçu voisin réécrit."""
import sys
sys.dont_write_bytecode = True
import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import traceback
import b14
import b13
ROOT, OUT = b14.ROOT, b14.OUT

def install(name):
    b14.guard()
    import b06
    prior = json.loads((OUT/'code-ancre-demo-V2.json').read_text(encoding='utf-8'))['readback']
    expected = {'plugins/imagine-site/Accueil.php':prior['plugins/imagine-site/Accueil.php'],
        'themes/imagine/front-page.php':hashlib.sha256((ROOT/'wp/themes/imagine/front-page.php').read_bytes()).hexdigest(),
        'themes/imagine/inc/catalogue.php':hashlib.sha256((OUT/'catalogue-avant-corrections-V2.php').read_bytes()).hexdigest(),
        'themes/imagine/single-imagine_numero.php':hashlib.sha256((OUT/'single-imagine_numero-avant-corrections-V2.php').read_bytes()).hexdigest()}
    old = b06.hashes(b14.FILES)
    assert old == expected
    previous = b14.wp('echo wp_json_encode(file_get_contents(WP_CONTENT_DIR."/plugins/imagine-site/Accueil.php"));')
    with (OUT/'Accueil-avant-corrections-V2.php').open('x', encoding='utf-8') as f:
        f.write(previous)
    for n in b14.FILES:
        b13.b11.upload(n, (ROOT/'wp'/n).read_bytes())
    actual = b06.hashes(b14.FILES)
    assert actual == {n:hashlib.sha256((ROOT/'wp'/n).read_bytes()).hexdigest() for n in b14.FILES}
    b13.save(b14, name, {'before':old,'readback':actual})
    print('B14 correction, lecture exacte', len(actual))

def b11(name):
    import b11 as closed
    closed.OUT = OUT
    closed.runtime(name)
    old = (OUT/'single-imagine_numero-avant-corrections-V2.php').read_text(encoding='utf-8')
    expected = old.replace('    $free = null;', '    $free = imagine_issue_free_article($issue);')
    expected = expected.replace("        if ($free === null && $statuses[$article->ID]['code'] === 'libre') {\n            $free = $article;\n        }", '')
    current = (ROOT/'wp/themes/imagine/single-imagine_numero.php').read_text(encoding='utf-8')
    assert current == expected, 'B11_SEAM_CHANGED_BEYOND_APPROVED_FREE_SELECTION'
    original = json.loads((ROOT/'production/B-11/reception-contrat-V2.json').read_text(encoding='utf-8'))
    assert original['sources']['wp/themes/imagine/single-imagine_numero.php'] == hashlib.sha256((OUT/'single-imagine_numero-avant-corrections-V2.php').read_bytes()).hexdigest()
    b13.save(b14, name+'-source', {'old_hash_matches_B11_receipt':True,'only_approved_free_selection_change':True,'media_and_audio_markup_unchanged':True})

def legacy(name):
    b14.guard()
    commands = [[sys.executable,'-B',str(ROOT/'wp/tests/demo/test_b01_theme.py')]]
    rows = []
    for command in commands:
        r = subprocess.run(command, capture_output=True, encoding='utf-8')
        rows.append({'command':command,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    spec = importlib.util.spec_from_file_location('b01_legacy',ROOT/'wp/tests/demo/b01-verifier.py')
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT/'wp/tests/demo'))
    spec.loader.exec_module(module)
    module.PROOF = OUT/(name+'-b01-artifacts')
    module.PROOF.mkdir(exist_ok=False)
    remote = 'imagine-demo-build/b01-inventory.php'
    before = b14.wp('$p=WP_CONTENT_DIR."/'+remote+'";echo wp_json_encode(is_file($p)?hash_file("sha256",$p):null);')
    assert before in [None,hashlib.sha256((ROOT/'wp/tests/demo/b01-inventory.php').read_bytes()).hexdigest()]
    stream = io.StringIO()
    outcome = 0
    error = None
    try:
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            module.run()
    except BaseException as exc:
        outcome = exc.code if isinstance(exc, SystemExit) and isinstance(exc.code,int) else 1
        error = repr(exc)
        stream.write(traceback.format_exc())
    finally:
        if before is None:
            b13.b11.b10.b09.remove_remote([remote])
    rows.append({'command':['b01-verifier.py','run() with owned PROOF override only'],'exit':outcome,'stdout':stream.getvalue(),'error':error})
    b13.save(b14, name, {'legacy_runs':rows,'all_legacy_pass':all(r['exit']==0 for r in rows),'historical_contracts_not_rewritten':True})
    print(json.dumps({'legacy_exits':[r['exit'] for r in rows],'error':error,'note':'Actual legacy failures retained; current anchors tested separately in B14 native/browser'},ensure_ascii=False))

if __name__ == '__main__':
    globals()[sys.argv[1]](sys.argv[2])
