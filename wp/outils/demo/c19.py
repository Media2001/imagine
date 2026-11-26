"""C19 code-only scoped installation; no fixture, role or option writes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys
sys.dont_write_bytecode = True
import c18
ROOT = c18.ROOT
PROOF = ROOT / 'production/C-19'
BLOCK = "require_once __DIR__ . '/TableauBordRegles.php';\nrequire_once __DIR__ . '/TableauBordNatives.php';\nrequire_once __DIR__ . '/TableauBordAdmin.php';\nTableauBordAdmin::register();\n\n"
wp = c18.wp


def matches_predecessor(name, data, expected):
    """Only the additive C19 shared sections may succeed old source seals."""
    if hashlib.sha256(data).hexdigest() == expected:
        return True
    if name == 'wp/plugins/imagine-site/imagine-site.php' and data.count(BLOCK.encode()) == 1:
        predecessor = data.replace(BLOCK.encode(), b'', 1)
    elif name == 'wp/plugins/imagine-site/README.md' and data.count('\n## C-19 — tableau de bord\n'.encode()) == 1:
        predecessor = data.split('\n## C-19 — tableau de bord\n'.encode(), 1)[0]
    else:
        return False
    return hashlib.sha256(predecessor).hexdigest() == expected


def save(name, data):
    PROOF.mkdir(parents=True, exist_ok=True)
    (PROOF / (name + '.json')).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def targets():
    paths = [ROOT / 'wp/plugins/imagine-site' / n for n in ('TableauBordRegles.php', 'TableauBordNatives.php', 'TableauBordAdmin.php')]
    paths += sorted((ROOT / 'wp/plugins/imagine-site/indicateurs').glob('*.php'))
    paths += [ROOT / 'wp/plugins/imagine-site/imagine-site.php']
    return {p.relative_to(ROOT / 'wp').as_posix(): p for p in paths}


def readback():
    names = list(targets())
    actual = wp('$out=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$p=WP_CONTENT_DIR."/".$n;token_get_all(file_get_contents($p),TOKEN_PARSE);$out[$n]=hash_file("sha256",$p);}echo wp_json_encode($out);')
    assert actual == {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in targets().items()}
    return actual


def state():
    out = c18.state()
    # Exact bootstrap-only volatility observed before/after ordinary native admin.
    # Business options, journals, roles and ALL scheduler actions/logs remain protected.
    exclusions = "('_transient_timeout_wcs_woocommerce_active_version','_transient_timeout_novamira-pro_update_checker','action_scheduler_lock_async-request-runner')"
    out['all_options_fingerprint'] = wp(r'''global $wpdb;$rows=$wpdb->get_results("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name NOT IN ''' + exclusions + r''' ORDER BY option_name",ARRAY_A);echo wp_json_encode(hash('sha256',serialize($rows)));''')
    out['option_fingerprints'] = wp(r'''global $wpdb;$out=[];foreach($wpdb->get_results("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name NOT IN ''' + exclusions + r''' ORDER BY option_name",ARRAY_A) as $row){$out[$row['option_name']]=hash('sha256',serialize($row));}echo wp_json_encode($out);''')
    return out


def deploy():
    c18.c17.profils.guard('imagine-test-demo')
    before = state()
    prior = {}
    for name, source in targets().items():
        current = wp('$p=WP_CONTENT_DIR.' + json.dumps('/' + name) + ';echo wp_json_encode(is_file($p)?hash_file("sha256",$p):null);')
        allowed = {hashlib.sha256(source.read_bytes()).hexdigest()}
        if name.endswith('/imagine-site.php'):
            allowed.add(hashlib.sha256(source.read_text(encoding='utf-8').replace(BLOCK, '').encode()).hexdigest())
        if (PROOF / 'installation.json').is_file():
            old = json.loads((PROOF / 'installation.json').read_text(encoding='utf-8'))
            allowed.add(old['sha256_readback'].get(name))
        if current is not None and current not in allowed:
            raise RuntimeError('Drift: no overwrite: ' + name)
        prior[name] = current
    for name, source in targets().items():
        c18.c17.profils.b00.upload(name, source.read_bytes())
    hashes = readback()
    assert before == state(), 'Native state or options changed on code installation'
    if (PROOF / 'installation.json').is_file():
        stamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        (PROOF / ('installation-before-' + stamp + '.json')).write_bytes((PROOF / 'installation.json').read_bytes())
    save('installation', {'at': datetime.now(timezone.utc).isoformat(), 'scope': 'imagine-test-demo',
        'sha256_before': prior, 'sha256_readback': hashes, 'baseline': before, 'native_unchanged': True,
        'role_write': False, 'fixture_reset': False})
    print('C19 code installed; source readback exact; all native state/options unchanged')


def runtime(label='runtime-final'):
    c18.c17.profils.guard('imagine-test-demo')
    source = ROOT / 'wp/tests/demo/c19-runtime.php'
    name = 'imagine-demo-build/c19-runtime.php'
    c18.c17.profils.b00.upload(name, source.read_bytes())
    assert wp('echo wp_json_encode(hash_file("sha256",WP_CONTENT_DIR.' + json.dumps('/' + name) + '));') == hashlib.sha256(source.read_bytes()).hexdigest()
    before = state()
    result = wp('require WP_CONTENT_DIR . "/imagine-demo-build/c19-runtime.php";')
    result['native_unchanged'] = before == state()
    save(label, result)
    print(json.dumps(result, ensure_ascii=False))
    assert result['checks'] and all(v is True for v in result['checks'].values()) and result['native_unchanged']
    return result


if __name__ == '__main__':
    if '--deploy' in sys.argv:
        deploy()
    elif '--runtime' in sys.argv:
        runtime(sys.argv[-1] if sys.argv[-1] != '--runtime' else 'runtime-final')
    else:
        c18.c17.profils.guard('imagine-test-demo')
        save('readback', {'sha256_readback': readback(), 'state': state()})
        print('C19 exact source readback verified')
