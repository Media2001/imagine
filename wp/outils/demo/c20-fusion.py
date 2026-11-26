"""C20 fusion only: disposable mutation proofs and two-file demo install."""
from pathlib import Path
import hashlib, importlib, json, os, re, subprocess, sys, tempfile, uuid
sys.dont_write_bytecode = True
import c20
ROOT, PROOF = c20.ROOT, c20.PROOF / 'fusion-V2'
NAMES = ['plugins/imagine-site/' + n for n in ('Renouvellement.php', 'RenouvellementRegles.php')]

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(name, data):
    path = PROOF / (name + '.json')
    assert not path.exists(), path
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def wp_hashes(names):
    return c20.wp('$o=[];foreach(json_decode(' + json.dumps(json.dumps(names)) + ',true) as $n){$o[$n]=hash_file("sha256",WP_CONTENT_DIR."/".$n);}echo wp_json_encode($o);')

def deploy():
    c20.profils.guard('imagine-test-demo')
    prior = wp_hashes(NAMES)
    expected = {n: sha(ROOT / 'wp' / n) for n in NAMES}
    for n in NAMES:
        assert prior[n] in {sha(PROOF / (Path(n).name + '.before')), expected[n]}, n
    second = importlib.import_module('c20-second')
    before = second.snapshot()
    for n in NAMES:
        c20.profils.b00.upload(n, (ROOT / 'wp' / n).read_bytes())
    actual = wp_hashes(NAMES)
    after = second.snapshot()
    assert actual == expected and before['profiles'] == after['profiles']
    save('installation', {'source_readback': actual, 'profiles_actions_exact': True})
    print('C20: only two presentation files installed; exact source and native readback')

def mutations():
    path = ROOT / 'wp/plugins/imagine-site/Paywall.php'
    source = path.read_text(encoding='utf-8')
    prior = sha(path)
    cases = {
        'sans-garde-fin': source.replace("&& $subscription->get_date('end', 'gmt') !== ''", '&& true', 1),
        'sans-minimum-memberships': source.replace("$end = min($end, self::date($subscription->get_date('end', 'gmt'), true));", "$end = self::date($subscription->get_date('end', 'gmt'), true);", 1),
        'sans-ouverture-pending-cancel': source.replace("$subStatus === 'pending-cancel' && $status === 'pending'", "$subStatus === 'C20_mutant_closed' && $status === 'pending'", 1),
    }
    def cmd(args, check=True):
        p = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', timeout=120)
        if check:
            assert p.returncode == 0, p.stdout + p.stderr
        return p
    def linux(path):
        return cmd(['wsl.exe', '-d', 'Ubuntu', '--', 'wslpath', '-a', '-u', str(path).replace('\\', '/')]).stdout.strip()
    mount = linux(ROOT / 'wp')
    results = {}
    with tempfile.TemporaryDirectory(prefix='c20-fusion-', dir=os.environ['TMPDIR']) as temp:
        for label, content in cases.items():
            assert content != source
            mutant = Path(temp) / (label + '.php')
            mutant.write_text(content, encoding='utf-8')
            name = 'imagine-c20-fusion-' + uuid.uuid4().hex
            try:
                p = cmd(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'run', '--rm', '--name', name,
                    '--pull', 'never', '--network', 'none', '--read-only', '--user', '65534:65534',
                    '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
                    '--tmpfs', '/tmp:rw,nosuid,nodev,size=128m,mode=1777',
                    '--mount', 'type=bind,source=' + mount + ',target=/repo/wp,readonly',
                    '--mount', 'type=bind,source=' + linux(mutant) + ',target=/repo/wp/plugins/imagine-site/Paywall.php,readonly',
                    '--entrypoint', 'php', 'imagine-tests-t01:1', '/repo/wp/tests/demo/c16-unit-runtime.php', 'C20PaywallAdapter'], False)
            finally:
                inspect = cmd(['wsl.exe', '-d', 'Ubuntu', '--', 'docker', 'inspect', name], False)
                assert inspect.returncode and 'no such' in (inspect.stdout + inspect.stderr).lower()
            assert p.returncode == 1 and 'FAILURES!' in p.stdout and 'Errors:' not in p.stdout and not p.stderr, p.stdout + p.stderr
            results[label] = {'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr, 'removed': True, 'network': 'none'}
            print(label + ': killed by real Paywall tests', flush=True)
    assert sha(path) == prior
    save('mutations', {'cases': results, 'live_source_unchanged': True, 'Paywall_sha256': prior})

if __name__ == '__main__':
    assert sys.argv[1:] in (['deploy'], ['mutations'])
    globals()[sys.argv[1]]()
