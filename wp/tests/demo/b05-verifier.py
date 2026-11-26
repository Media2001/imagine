"""B05 final seal and read-only parent gate, exact source/native readback."""
from pathlib import Path
import hashlib, json, re, sys
from urllib.request import urlopen
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import b05
ROOT, PROOF = b05.ROOT, b05.PROOF
OWNED = ['wp/plugins/imagine-site/Partenaires.php','wp/themes/imagine/inc/partenaires.php',
         'wp/outils/demo/b05.py','wp/tests/demo/b05-runtime.php','wp/tests/demo/b05-http.py',
         'wp/tests/demo/b05-admin.py','wp/tests/demo/b05-verifier.py',
         'production/B-05/A-VOIR.md','production/B-05/README-CONTRAT.md',
         'files/rapports/2026-11-26-08h24-V2.md']
RECEIPTS = ['final-runtime.json','final-http.json','final-admin.json','preparer-image.log',
            'rejouer-final.log','psr12-final.log','accueil-partenaire.png','fiche-partenaire.png','natif-sources.json']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((PROOF / name).read_text(encoding='utf-8'))


def shared():
    before = read('baseline.json')['source_before']
    transforms = {
        'plugins/imagine-site/imagine-site.php': (b05.BLOCK, ''),
        'themes/imagine/functions.php': ("require_once __DIR__ . '/inc/partenaires.php';\n", ''),
        'themes/imagine/front-page.php': ('<?php imagine_partner_month(); ?>\n',''),
        'themes/imagine/archive-imagine_partenaire.php': ("<h1><?php esc_html_e('Nos partenaires', 'imagine'); ?></h1>","<h1><?php esc_html_e('Partenaires', 'imagine'); ?></h1>\n<p><?php esc_html_e('Partenariat', 'imagine'); ?></p>"),
        'themes/imagine/single-imagine_partenaire.php': ('<article class="imagine-partnership">\n    <?php imagine_partner_label(); ?>','<article>'),
    }
    contracts = {}
    for name,(new,old) in transforms.items():
        text = (ROOT / 'wp' / name).read_text(encoding='utf-8')
        assert text.count(new) == 1
        prior = text.replace(new,old,1)
        if name.endswith('archive-imagine_partenaire.php'):
            prior = prior.replace("imagine_partner_list($GLOBALS['wp_query']);", "imagine_list($GLOBALS['wp_query']);",1)
        assert hashlib.sha256(prior.encode()).hexdigest() == before[name], 'Predecessor changed: ' + name
        contracts[name] = {'inserted':new,'predecessor_sha256':before[name]}
    section = (PROOF / 'README-CONTRAT.md').read_text(encoding='utf-8')
    text = (ROOT / 'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
    assert text.count(section) == 1
    original = text.replace(section,'',1)
    assert hashlib.sha256(original.encode()).hexdigest() == read('readme-predecessor.json')['sha256']
    contracts['README_section'] = section
    return contracts


def receipts():
    counts = {}
    for name in ('final-runtime','final-http','final-admin'):
        data = read(name + '.json')
        assert data['scope'] == 'imagine-test-demo' and data['total'] == len(data['checks'])
        assert not data['failures'] and all(v is True for v in data['checks'].values())
        counts[name] = data['total']
    log = (PROOF / 'rejouer-final.log').read_text(encoding='utf-8-sig')
    markers = re.findall(r'^T01_RESULT (\{[^\r\n]+\})',log,re.M)
    assert len(markers) == 1
    canonical = json.loads(markers[0])
    assert canonical['pass'] and canonical['failures'] == canonical['errors'] == canonical['skipped'] == 0
    assert 'T01 IMAGE READY' in (PROOF / 'preparer-image.log').read_text(encoding='utf-8-sig')
    assert not (PROOF / 'psr12-final.log').read_text(encoding='utf-8-sig').strip()
    return counts, canonical


def live():
    b05.profils.guard('imagine-test-demo')
    expected = {n:sha(ROOT/'wp'/n) for n in b05.NAMES}
    expected['imagine-demo-build/b05-runtime.php'] = sha(ROOT/'wp/tests/demo/b05-runtime.php')
    assert b05.hashes(list(expected)) == expected, 'Exact native code readback differs'
    assert b05.state() == read('baseline.json')['state'], 'Native state/business actions differ'
    checks = b05.wp(r'''echo wp_json_encode([
        'choix_manuel_48'=>(int)get_option('imagine_partenaire_du_mois')===48,
        'mail_coupe'=>apply_filters('pre_wp_mail',null,['to'=>['fictif@example.org']])===false,
        'HTTP_externe_coupe'=>is_wp_error(apply_filters('pre_http_request',false,[],'https://example.org/')),
        'passerelles_coupees'=>apply_filters('woocommerce_available_payment_gateways',[])===[]
    ]);''')
    assert all(v is True for v in checks.values())
    c09 = b05.wp('require WP_CONTENT_DIR."/imagine-demo-build/c09-runtime.php";')
    assert c09['total'] == len(c09['checks']) == 382 and not c09['failures'] and all(c09['checks'].values())
    state = b05.state()
    assert state == read('baseline.json')['state']
    action = state['schedule_business']['action8793']
    assert action['action_id'] == '8793' and action['status'] == 'pending' and json.loads(action['args']) == {'subscription_id':101}
    for path, needle in [('/', 'data-imagine-partenaire-mois="48"'),('/partenaires/','Nos partenaires'),('/partenaires/demo-partners-1/','imagine-partnership-label')]:
        with urlopen('http://192.168.129.32:8085'+path,timeout=30) as response:
            assert response.status == 200 and needle in response.read().decode('utf-8')
    return {'source_readback':expected,'C09':{'total':382,'failures':[]},'safety':checks,'action8793':action}


def run(seal=False):
    counts, canonical = receipts()
    if seal:
        contracts = shared()
        native = live()
        data = {'status':'PRET_TECHNIQUE_B05','counts':counts,'canonical':canonical,
                'source_sha256':{n:sha(ROOT/n) for n in OWNED},
                'receipt_sha256':{n:sha(PROOF/n) for n in RECEIPTS},
                'shared_contracts':contracts,'native':native,'visual_approval':False,'real_deployment_authorized':False}
        b05.save('final',data)
    else:
        data = read('final.json')
        assert data['status'] == 'PRET_TECHNIQUE_B05' and data['counts'] == counts and data['canonical'] == canonical
        for name,value in data['source_sha256'].items(): assert sha(ROOT/name) == value,name
        for name,value in data['receipt_sha256'].items(): assert sha(PROOF/name) == value,name
        text = (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8')
        assert text.count(data['shared_contracts']['README_section']) == 1
        live()
    print(json.dumps({'B05':'VERIFIE','counts':counts,'canonical':canonical,'C09':'382/382','action8793':'pending abonnement 101 intacte','validation_visuelle':False},ensure_ascii=False))


if __name__ == '__main__':
    # Historical helpers above describe V1 receipts. The current entry point is V2,
    # which validates shared files by contract and does not need the live demo.
    import runpy
    runpy.run_path(str(Path(__file__).with_name('b05-verifier-v2.py')), run_name='__main__')
