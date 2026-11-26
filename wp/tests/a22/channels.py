"""A22 extension-channel probes, reused by each existing native fixture."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode=True
CASES={
    'direct_stdout':"fwrite(STDOUT,'A22_PRIVATE_FLOW_CANARY');",
    'direct_stderr':"fwrite(STDERR,'A22_PRIVATE_FLOW_CANARY');",
    'echo_exit':"echo 'A22_PRIVATE_FLOW_CANARY'; exit(0);",
    'silent_exit':"exit(0);",
    'shutdown_stdout':"register_shutdown_function(static function () { fwrite(STDOUT,'A22_PRIVATE_FLOW_CANARY'); });",
    'shutdown_stderr':"register_shutdown_function(static function () { fwrite(STDERR,'A22_PRIVATE_FLOW_CANARY'); });",
    'shutdown_echo':"register_shutdown_function(static function () { echo 'A22_PRIVATE_FLOW_CANARY'; });",
    'shutdown_file':"register_shutdown_function(static function () { foreach ($GLOBALS['argv'] as $arg) { if (str_starts_with($arg, '--output=')) { $out=substr($arg,9); $files=array_merge(glob($out.'/*.md'),glob($out.'/*.csv'),glob($out.'/*.json')); if ($files) { file_put_contents($files[0], \"\\nA22_PRIVATE_FLOW_CANARY\\n\", FILE_APPEND); } } } });",
    'shutdown_json':"register_shutdown_function(static function () { foreach ($GLOBALS['argv'] as $arg) { if (str_starts_with($arg, '--output=')) { foreach (glob(substr($arg,9).'/*.json') as $file) { $data=json_decode(file_get_contents($file),true); $data['A22_PRIVATE_FLOW_CANARY']='private/path'; file_put_contents($file,json_encode($data)); } } } });",
}


def discard_fence_probe():
    """Real kernel rights on a synthetic tree; never target a site in RED."""
    import tempfile
    import importlib.util
    with tempfile.TemporaryDirectory(prefix='a22-fence-',dir='/scratch') as temporary:
        base=Path(temporary);allowed=base/'private';allowed.mkdir()
        outside=base/'outside';outside.mkdir();(outside/'keep').write_bytes(b'unchanged')
        (outside/'empty').mkdir()
        code='''<?php
$root=$argv[1];$outside=$root.'/outside';$private=$root.'/private';
$checks=[
'discard_only'=>@file_put_contents('/dev/null','discard')===7,
'private_write'=>@file_put_contents($private.'/result','private')===7,
'other_device_denied'=>@file_put_contents('/dev/zero','discard')===false,
'create_denied'=>@file_put_contents($outside.'/new','bad')===false,
'truncate_denied'=>@file_put_contents($outside.'/keep','bad')===false,
'append_denied'=>@file_put_contents($outside.'/keep','bad',FILE_APPEND)===false,
'unlink_denied'=>@unlink($outside.'/keep')===false,
'rename_denied'=>@rename($outside.'/keep',$private.'/stolen')===false,
'mkdir_denied'=>@mkdir($outside.'/newdir')===false,
'rmdir_denied'=>@rmdir($outside.'/empty')===false,
'link_denied'=>@link($outside.'/keep',$outside.'/newlink')===false,
'symlink_denied'=>@symlink($outside.'/keep',$outside.'/newsym')===false,
];
error_log('discard canary');
echo json_encode($checks);
'''
        script=base/'probe.php';script.write_text(code,encoding='utf-8')
        spec=importlib.util.spec_from_file_location('a22_fence','/subject/a12/confine.py')
        fence=importlib.util.module_from_spec(spec);spec.loader.exec_module(fence)
        p=subprocess.run(['php','-d','error_log=/dev/null',str(script),str(base)],capture_output=True,
            preexec_fn=lambda:fence.confine(allowed),timeout=30)
        values=json.loads(p.stdout)
        unchanged={p.relative_to(outside).as_posix() for p in outside.rglob('*')}=={'keep','empty'} and (outside/'keep').read_bytes()==b'unchanged'
        return p.returncode==0 and p.stderr==b'' and len(values)==12 and all(v is True for v in values.values()) and unchanged


def exercise(b,tool,command,site,output,*,input_data=None):
    """Use the real tool command and native MU boundary, never a fake PHP child."""
    env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'}
    plugin=site/'wp-content/mu-plugins/000-a22-hostile.php'
    # Metadata only here: A18's kernel media-read watch surrounds the nominal call.
    # The unchanged bank separately hashes the complete site before/after execution.
    photograph=lambda:{p.relative_to(site).as_posix():(p.stat().st_size,p.stat().st_mtime_ns,p.stat().st_mode)
                       for p in site.rglob('*') if p.is_file()}
    baseline=photograph()
    channel_rows=[]
    try:
        for label,statement in CASES.items():
            plugin.write_text("<?php if (getenv('A22_SUPERVISED') === '"+tool+"' || getenv('"+tool+"_CONFINED') === '1') { "+statement+' }',encoding='utf-8')
            out=output/(tool.lower()+'-'+label)
            args=[part.replace('{output}',str(out)) for part in command]
            p=subprocess.run(args,input=input_data,capture_output=True,env=env,timeout=180)
            closed=(p.returncode==1 and p.stdout==b'' and p.stderr==
                    (tool+'_PROCESS_OUTPUT_INVALID\n').encode())
            if tool=='A20':closed=(p.returncode==1 and p.stdout==b'' and p.stderr==b'A20_PROCESS_OUTPUT_INVALID\n')
            if tool=='A21':closed=(p.returncode==1 and p.stdout==b'' and p.stderr==b'A21_UNEXPECTED_OUTPUT\n')
            if label in {'shutdown_file','shutdown_json'}:
                expected={'A20':b'A20_REPORT_INVALID\n','A21':b'A21_SUCCESS_INCOMPLETE\n'}.get(tool,(tool+'_PROCESS_OUTPUT_INVALID\n').encode())
                closed=p.returncode==1 and p.stdout==b'' and p.stderr==expected
            clean=not out.exists() and not list(output.glob('.a22-private-*')) and not any(
                b'A22_PRIVATE_FLOW_CANARY' in f.read_bytes() for f in output.rglob('*') if f.is_file())
            b.check(tool+':channels:'+label,closed and clean)
            channel_rows.append({'channel':label,'closed':closed,'artifacts_absent':clean})
    finally:plugin.unlink(missing_ok=True)
    b.check(tool+':channel_site_restored',photograph()==baseline)
    return channel_rows
