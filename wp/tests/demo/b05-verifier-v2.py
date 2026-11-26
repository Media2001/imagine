"""B05 V2 seal: own hashes, shared contracts, offline default; --live read-only."""
from pathlib import Path
import hashlib, json, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import b05
ROOT, PROOF = b05.ROOT, b05.PROOF
OWNED = ['wp/plugins/imagine-site/Partenaires.php', 'wp/themes/imagine/inc/partenaires.php',
    'wp/themes/imagine/archive-imagine_partenaire.php',
    'production/B-05/A-VOIR.md', 'production/B-05/CORRECTIONS-V2.md']
OWNED += [p.relative_to(ROOT).as_posix() for directory in ['wp/tests/demo','wp/outils/demo'] for p in (ROOT/directory).glob('b05*') if p.is_file()]
RECEIPTS = ['offline-final-V2.json','browser-offline-green-V2.json','quality-green-V2.json',
    'quality-green-V2.log','final-runtime-V2.json','final-http-V2.json','final-admin-V2.json',
    'c09-final-V2.json','installation-corrections-V2.json','corrections-baseline-V2.json',
    'preparer-image-V2.log','rejouer-final-V2.log','standard-sources-V2.json',
    'accueil-partenaire-V2.png','fiche-partenaire-V2.png']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name): return json.loads((PROOF/name).read_text(encoding='utf-8'))

def shared_contracts():
    bootstrap = (ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8')
    assert bootstrap.count(b05.BLOCK)==1, 'B05 bootstrap contract missing/duplicate'
    text = (ROOT/'wp/themes/imagine/functions.php').read_text(encoding='utf-8')
    assert text.count("require_once __DIR__ . '/inc/partenaires.php';") == 1
    start = text.index('function imagine_partner_content(')
    end = text.index("add_filter('the_content',",start)
    partner_filter = text[start:end]
    front = (ROOT/'wp/themes/imagine/front-page.php').read_text(encoding='utf-8')
    assert front.count('<?php imagine_partner_month(); ?>')==1
    assert 'aria-labelledby="imagine-latest-posts"' in front
    section = (PROOF/'README-CONTRAT.md').read_text(encoding='utf-8')
    assert (ROOT/'wp/plugins/imagine-site/README.md').read_text(encoding='utf-8').count(section)==1
    return {'bootstrap':b05.BLOCK,'partner_filter':partner_filter,'README_section':section}

def validate_receipts():
    counts = {}
    for name in ['final-runtime-V2','final-http-V2','final-admin-V2','c09-final-V2','browser-offline-green-V2','quality-green-V2']:
        data=read(name+'.json')
        assert data['total']==len(data['checks'])>0 and not data['failures'] and all(v is True for v in data['checks'].values()),name
        counts[name]=data['total']
    offline=read('offline-final-V2.json')
    assert offline['isolation_verified'] and offline['owned_container_removed'] and offline['exit']==0 and not offline['stderr']
    unit=json.loads(offline['stdout']); assert unit['total']==len(unit['checks'])>0 and not unit['failures'] and all(unit['checks'].values())
    counts['offline-final-V2']=unit['total']
    for name in ['final-runtime-V2','final-http-V2','final-admin-V2']:
        data=read(name+'.json'); assert data['scope']=='imagine-test-demo'
    assert read('final-runtime-V2.json')['state_preserved']
    assert read('final-http-V2.json')['checks']['restauration_profils_et_corps_exacte']
    admin=read('final-admin-V2.json'); assert admin['checks']['lecture_sans_sauvegarde_C10']
    assert read('installation-corrections-V2.json')['native_preserved']
    assert 'T01 IMAGE READY' in (PROOF/'preparer-image-V2.log').read_text(encoding='utf-8-sig')
    markers=re.findall(r'^T01_RESULT (\{[^\r\n]+\})',(PROOF/'rejouer-final-V2.log').read_text(encoding='utf-8-sig'),re.M)
    assert len(markers)==1
    canonical=json.loads(markers[0]); assert canonical['pass'] and canonical['tests']>0 and canonical['errors']==canonical['failures']==canonical['skipped']==0
    assert canonical['tools']['failures']==0
    return counts,canonical

def live():
    b05.profils.guard('imagine-test-demo')
    expected={name:sha(ROOT/'wp'/name) for name in b05.NAMES}
    actual=b05.hashes(list(expected)); assert actual==expected
    state=b05.state(); assert state==read('corrections-baseline-V2.json')['state'], 'Business state drift'
    checks=b05.wp(r'''echo wp_json_encode([
        'bootstrap_B05'=>str_contains(file_get_contents(WP_PLUGIN_DIR.'/imagine-site/imagine-site.php'),"require_once __DIR__ . '/Partenaires.php';\nPartenaires::register();"),
        'manual_48'=>(int)get_option('imagine_partenaire_du_mois')===48,
        'mail_blocked'=>apply_filters('pre_wp_mail',null,['to'=>['fictif@example.org']])===false,
        'HTTP_blocked'=>is_wp_error(apply_filters('pre_http_request',false,[],'https://example.org/')),
        'payments_blocked'=>apply_filters('woocommerce_available_payment_gateways',[])===[]
    ]);''')
    assert checks and all(v is True for v in checks.values())
    shared_hash=b05.hashes(['plugins/imagine-site/imagine-site.php'])
    historical=read('final.json')['native']['source_readback']['plugins/imagine-site/imagine-site.php']
    return {'source_readback':actual,'safety':checks,'shared_bootstrap_observed_sha256':shared_hash,
        'historical_bootstrap_sha256':historical,'shared_bootstrap_pinned':False,
        'business_state_preserved':True,'action8793':state['schedule_business']['action8793']}

def run(seal=False, check_live=False):
    counts,canonical=validate_receipts(); contracts=shared_contracts()
    if seal:
        native=live()
        data=dict(status='PRET_TECHNIQUE_B05_V2',counts=counts,canonical=canonical,
            source_sha256={n:sha(ROOT/n) for n in sorted(set(OWNED))},
            receipt_sha256={n:sha(PROOF/n) for n in RECEIPTS},shared_contracts=contracts,
            native=native,visual_approval=False,real_deployment_authorized=False,
            historical_receipt='final.json preserved; superseded by final-V2.json')
        b05.save('final-V2',data)
    else:
        data=read('final-V2.json')
        assert data['status']=='PRET_TECHNIQUE_B05_V2' and data['counts']==counts and data['canonical']==canonical
        assert data['shared_contracts']==contracts
        for name,value in data['source_sha256'].items(): assert sha(ROOT/name)==value,name
        for name,value in data['receipt_sha256'].items(): assert sha(PROOF/name)==value,name
        if check_live: live()
    print(json.dumps({'B05':'VERIFIE_V2','counts':counts,'canonical':canonical,'live_readback':seal or check_live,'visual_approval':False},ensure_ascii=False))
if __name__=='__main__':
    assert sys.argv[1:] in ([],['--seal'],['--live'])
    run('--seal' in sys.argv,'--live' in sys.argv)
