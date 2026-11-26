"""A24 canary on each real PHP channel, plus guardian-bypass mutations."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

OUT = Path('/report')


def exercise(b, cmd, inventory, site, storage, audit, dest, cfg, base_mu, clean):
    def check(key, ok, detail=None):
        b.check(storage + ':' + key, ok, detail)

    def refusal(label, want):
        out = OUT / (storage + '-' + label.replace(':', '-'))
        q = inventory(site, out, audit)
        check(label, (q.returncode, q.stdout, q.stderr) == (1, '', want + '\n') and not out.exists(),
              {'exit': q.returncode, 'closed_code': q.stderr.strip() if re.fullmatch(r'A(?:24|11|12|02)_[A-Z_]+\n', q.stderr) else 'NON_CODE'})
        check('no_retained_payload:' + label, not list(OUT.glob('.a24-private-*')) and clean())

    mu = site / 'wp-content/mu-plugins/a24-probe.php'
    for label, path in [('exists', dest), ('site', site / 'forbidden'), ('repo', Path('/subject/forbidden')),
                        ('ancestor', site.parent / 'forbidden'), ('root', Path('/forbidden'))]:
        q = inventory(site, path, audit)
        check('guard:' + label, q.returncode == 1 and q.stdout == ''
              and re.fullmatch(r'A(?:24|12)_[A-Z_]+\n', q.stderr) is not None and (path == dest or not path.exists()))
    q = cmd(['php', '/subject/a24/inventorier-expedition', '--wp-path=' + str(site),
             '--audit=' + str(audit), '--output=/report/' + storage + '-raw'], check=False)
    check('unconfined_php_refused', (q.returncode, q.stdout, q.stderr) == (1, '', 'A24_CONFINEMENT_REQUIRED\n'))
    for directory in (False, True):
        link = site / ('A24_SITE_PERSON_PRIVATE_CANARY_' + str(directory))
        link.symlink_to(site / 'wp-content' if directory else site / 'wp-config.php', target_is_directory=directory)
        try:
            refusal('symlink_closed:' + str(directory), 'A11_SYMLINK_UNSUPPORTED')
        finally:
            link.unlink()
    for i, name in enumerate(('wp-content/db.php', 'wp-content/object-cache.php', 'wp-content/advanced-cache.php',
                              'wp-content/sunrise.php', 'wordfence-waf.php', '.user.ini')):
        dropin = site / name
        dropin.write_text('<?php die("A24_DROPIN_PRIVATE_CANARY");', encoding='utf-8')
        try:
            refusal('closed_dropin:' + str(i), 'A11_DROPIN_UNSUPPORTED ' + json.dumps({'file': name}, separators=(',', ':')))
        finally:
            dropin.unlink()
    for label, statement in [('define', "define('A24_CONFIG_PRIVATE_CANARY','A24_VALUE_PRIVATE_CANARY');"),
                             ('const', "const A24_CONFIG_PRIVATE_CANARY='A24_VALUE_PRIVATE_CANARY';")]:
        (site / 'wp-config.php').write_text(cfg + '\n' + statement + '\n', encoding='utf-8')
        try:
            refusal('config_closed:' + label, 'A11_CONFIG_OVERRIDE_UNSUPPORTED')
        finally:
            (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    (site / 'wp-config.php').write_text(cfg.replace("define('DB_USER', 'a02_" + storage + "')", "define('DB_USER', 'root')"), encoding='utf-8')
    try:
        before = b.fingerprint('a02_' + storage)
        out = OUT / (storage + '-root-readonly')
        q = inventory(site, out, audit)
        check('transaction_readonly_even_root', q.returncode == 0 and q.stderr == ''
              and (out / 'expedition.json').read_bytes() == (dest / 'expedition.json').read_bytes()
              and before == b.fingerprint('a02_' + storage))
    finally:
        (site / 'wp-config.php').write_text(cfg, encoding='utf-8')
    bad = OUT / (storage + '-bad-audit')
    bad.mkdir()
    try:
        for label, photo, want in [('schema', {'schema': 'A24_AUDIT_PRIVATE_CANARY'}, 'A24_AUDIT_GUARD'),
                                  ('storage', json.loads(audit.read_text()), 'A24_AUDIT_STORAGE_MISMATCH')]:
            if label == 'storage':
                photo['sections']['commerce']['order_storage'] = 'hpos' if storage == 'classic' else 'classic'
            (bad / 'audit.json').write_text(json.dumps(photo), encoding='utf-8')
            out = OUT / (storage + '-bad-' + label)
            q = inventory(site, out, bad / 'audit.json')
            check('audit_guard:' + label, (q.returncode, q.stdout, q.stderr) == (1, '', want + '\n') and not out.exists())
    finally:
        (bad / 'audit.json').unlink()
        bad.rmdir()
    target = "foreach($_SERVER['argv'] as $arg){if(str_starts_with($arg,'--output=')){$dir=substr($arg,9);}}"
    cases = [
        ('direct_stdout', "fwrite(STDOUT,'A24_STDOUT_PRIVATE_CANARY');", 'A24_PROCESS_OUTPUT_INVALID', True),
        ('direct_stderr', "fwrite(STDERR,'A24_STDERR_PRIVATE_CANARY');", 'A24_PROCESS_OUTPUT_INVALID', True),
        ('display_early_exit', "echo 'A24_EXIT_PRIVATE_CANARY';exit(0);", 'A24_PROCESS_OUTPUT_INVALID', True),
        ('silent_early_exit', 'exit(0);', 'A24_PROCESS_OUTPUT_INVALID', False),
        ('shutdown_stdout', "register_shutdown_function(function(){fwrite(STDOUT,'A24_SHUTDOWN_PRIVATE_CANARY');});", 'A24_PROCESS_OUTPUT_INVALID', True),
        ('shutdown_stderr', "register_shutdown_function(function(){fwrite(STDERR,'A24_SHUTDOWN_PRIVATE_CANARY');});", 'A24_PROCESS_OUTPUT_INVALID', True),
        ('shutdown_display', "register_shutdown_function(function(){echo 'A24_SHUTDOWN_PRIVATE_CANARY';});", 'A24_PROCESS_OUTPUT_INVALID', True),
        ('invalid_utf8', 'fwrite(STDERR,chr(255));', 'A24_PROCESS_OUTPUT_INVALID', False),
        ('oversize_output', "fwrite(STDOUT,str_repeat('A24_PRIVATE_CANARY',8192));", 'A24_PROCESS_OUTPUT_INVALID', False),
        ('plugin_exception', "throw new RuntimeException('A24_PERSON_PATH_PRIVATE_CANARY');", 'A24_INVENTORY_FAILED', False),
        ('forged_refusal', "throw new RuntimeException('A24_QUERY_FAILED A24_PATH_PRIVATE_CANARY');", 'A24_INVENTORY_FAILED', False),
        ('forged_success', 'fwrite(STDOUT,"A24_OK expedition.json expedition.md\\n");exit(0);', 'A24_REPORT_INVALID', False),
        ('shutdown_invalid_json', "register_shutdown_function(function(){" + target + "file_put_contents($dir.'/expedition.json','{');});", 'A24_REPORT_INVALID', False),
        ('shutdown_extra_string', "register_shutdown_function(function(){" + target + "$p=$dir.'/expedition.json';$d=json_decode(file_get_contents($p),true);$d['private']='A24_JSON_PRIVATE_CANARY';file_put_contents($p,json_encode($d));});", 'A24_REPORT_INVALID', False),
        ('shutdown_markdown', "register_shutdown_function(function(){" + target + "file_put_contents($dir.'/expedition.md','A24_MARKDOWN_PRIVATE_CANARY',FILE_APPEND);});", 'A24_REPORT_INVALID', False),
        ('shutdown_extra_file', "register_shutdown_function(function(){" + target + "file_put_contents($dir.'/extra.txt','A24_EXTRA_PRIVATE_CANARY');});", 'A24_REPORT_INVALID', False),
        ('shutdown_partial', "register_shutdown_function(function(){" + target + "unlink($dir.'/expedition.md');});", 'A24_REPORT_INVALID', False),
        ('native_free_field', "add_filter('woocommerce_shipping_fields',function($f){$f['shipping_A24_FIELD_PRIVATE_CANARY']=['required'=>true];return $f;});", 'A24_NATIVE_FIELDS_UNSUPPORTED', False),
        ('native_free_country', "add_filter('woocommerce_countries',function($c){$c['A24_COUNTRY_PRIVATE_CANARY']='A24_LABEL_PRIVATE_CANARY';return $c;});", 'A24_NATIVE_COUNTRIES_UNSUPPORTED', False),
    ]
    spec = importlib.util.spec_from_file_location('a24_fence', '/subject/a12/confine.py')
    fence = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fence)
    try:
        for label, statement, want, witness in cases:
            mu.write_text("<?php if(getenv('A24_CONFINED')==='1'){" + statement + '}\n' + base_mu[5:], encoding='utf-8')
            refusal('closed_channel:' + label, want)
            if witness:
                # The only removed boundary is the A22 guardian/publication seam.
                with tempfile.TemporaryDirectory(prefix='a24-mutation-', dir='/scratch') as tmp:
                    stage = Path(tmp)
                    (stage / 'audit').mkdir()
                    shutil.copyfile(audit, stage / 'audit/audit.json')
                    command = ['php', '-d', 'display_errors=0', '-d', 'log_errors=0', '-d', 'error_log=/dev/null', '-d',
                               'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                               '/subject/a24/inventorier-expedition', '--wp-path=' + str(site),
                               '--audit=' + str(stage / 'audit/audit.json'), '--output=' + str(stage / 'out')]
                    mutant = subprocess.run(command, capture_output=True, timeout=120,
                                            env={**os.environ, 'A24_CONFINED': '1', 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'},
                                            preexec_fn=lambda: fence.confine(stage))
                    check('mutation_without_guard_detected:' + label, b'CANARY' in mutant.stdout + mutant.stderr)
    finally:
        mu.write_text(base_mu, encoding='utf-8')
    override = "add_filter('woocommerce_shipping_fields',function($f,$c){if($c==='BE'){foreach(['shipping_company','shipping_address_2','shipping_phone'] as $k){$f[$k]['required']=true;}$f['shipping_postcode']['required']=false;}return $f;},10,2);"
    mu.write_text("<?php if(getenv('A24_CONFINED')==='1'){" + override + '}\n' + base_mu[5:], encoding='utf-8')
    try:
        out = OUT / (storage + '-native-required-override')
        q = inventory(site, out, audit)
        check('native_filter_requirements_success', q.returncode == 0 and q.stderr == '')
        variant = json.loads((out / 'expedition.json').read_text(encoding='utf-8'))['counts']['overall']
        check('native_filter_requirements_not_hardcoded', variant['missing_any'] == 11
              and all(variant['missing_required']['shipping_' + key] == 8 for key in ('company', 'address_2', 'phone'))
              and variant['missing_required']['shipping_postcode'] == 1)
    finally:
        mu.write_text(base_mu, encoding='utf-8')
