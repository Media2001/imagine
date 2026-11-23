"""Contrôle final des artefacts B00 : aucun PRET créé par ce vérificateur."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import construire as b00


def run():
    root, proof = b00.ROOT, b00.ROOT / 'production/B-00'
    current = json.loads((proof / 'b00-final-verification.json').read_text(encoding='utf-8'))
    checks = {'suites_vertes': current['status'] == 'VERIFIED' and not current['failures'],
              'total_suites_calcule': current['suite_assertions'] == sum(current['suites'].values()),
              'tous_gardes_vertes': current['total'] == len(current['checks']) and all(current['checks'].values()),
              'source_hashes_actuels': all(hashlib.sha256((root / p).read_bytes()).hexdigest() == value for p,value in current['sources_sha256'].items())}
    paths = {'plugins/imagine-site/Paywall.php': root/'wp/plugins/imagine-site/Paywall.php',
             'plugins/imagine-site/imagine-site.php': root/'wp/plugins/imagine-site/imagine-site.php',
             'mu-plugins/imagine-demo-offline.php': root/'wp/outils/demo/imagine-demo-offline.php',
             'imagine-demo-build/b00-seed.php': root/'wp/outils/demo/b00-seed.php'}
    for name in ['b00-recette.php', 'b00-snapshot.php', 'b00-corrections-runtime.php', 'b00-integre-snapshot.php']:
        paths['imagine-demo-build/'+name] = Path(__file__).with_name(name)
    expected = {name:hashlib.sha256(p.read_bytes()).hexdigest() for name,p in paths.items()}
    code = '$names=json_decode(' + json.dumps(json.dumps(list(paths))) + ',true);$out=[];foreach($names as $n){$p=WP_CONTENT_DIR . "/" . $n;token_get_all(file_get_contents($p),TOKEN_PARSE);$out[$n]=hash_file("sha256",$p);}echo wp_json_encode($out);'
    raw = b00.wp('eval', code)
    deployed = json.loads(raw['stdout'])
    checks['php_syntaxe_et_octets_deployes'] = not raw['stderr'] and expected == deployed
    before = json.loads((proof/'tests/b00-snapshot-initial.json').read_text(encoding='utf-8'))
    after = json.loads(b00.wp('eval','require WP_CONTENT_DIR . "/imagine-demo-build/b00-snapshot.php";')['stdout'])
    checks['snapshot_b00_final_exact'] = before == after and after['total_tagged'] == after['manifest_posts'] == 41 and len(after['rows']) == 45
    previous = json.loads((proof/'tests/b00-snapshot-avant-corrections.json').read_text(encoding='utf-8'))
    checks['migration_limitee_15_indicateurs_password'] = b00.same_snapshot_after_password_retirement(previous, after) and sum(previous['rows'][k] != row for k,row in after['rows'].items()) == 15
    protected = json.loads(b00.wp('eval','require WP_CONTENT_DIR . "/imagine-demo-build/b00-integre-snapshot.php";')['stdout'])
    checks['readback_integre_final_exact'] = protected == json.loads((proof/'tests/b00-integre-final.json').read_text(encoding='utf-8'))
    c10 = json.loads(b00.wp('eval', '$s=new Imagine\\Pilotage\\Administration\\Reglages();$out=[];foreach($s->defauts() as $k=>$v){$out[$k]=get_option($k,$v);}echo wp_json_encode(["current"=>$out,"defaults"=>$s->defauts()]);')['stdout'])
    checks['c10_defauts_conserves'] = c10['current'] == c10['defaults']
    notes = (proof/'notes.md').read_text(encoding='utf-8')
    a_voir = (proof/'A-VOIR.md').read_text(encoding='utf-8')
    checks['notes_cinq_lignes'] = len(notes.splitlines()) == 5
    checks['a_voir_etat_reel'] = all(x in a_voir for x in ['`imagine`', '`fr_FR`', 'six articles', 'entièrement à C08', 'historiques'])
    http = json.loads((proof/'b00-verification-http-idempotence.json').read_text(encoding='utf-8'))
    checks['six_url_http_actuelles'] = not http['failures'] and all(http['responses'][k]['status'] == (302 if k=='administration' else 200) for k in ['accueil','numero','article-reserve','article-ouvert','administration','calendrier'])
    record = {'at': datetime.now(timezone.utc).isoformat(), 'scope': b00.SLUG, 'checks': checks, 'total': len(checks),
              'failures': [k for k,v in checks.items() if not v], 'deployed_php_files': len(deployed), 'deployed_sha256': deployed,
              'suite_assertions': current['suite_assertions'], 'integrated_guards': current['total']}
    record['status'] = 'VERIFIED' if not record['failures'] else 'FAILED'
    (proof/'b00-livraison-verifiee.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:record[k] for k in ['status','total','failures','deployed_php_files','suite_assertions','integrated_guards']},ensure_ascii=False,indent=2))
    if record['failures']:
        raise SystemExit(1)
    return record


if __name__ == '__main__':
    run()
