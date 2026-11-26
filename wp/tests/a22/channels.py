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
}


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
            clean=not out.exists() and not list(output.glob('.a22-private-*')) and not any(
                b'A22_PRIVATE_FLOW_CANARY' in f.read_bytes() for f in output.rglob('*') if f.is_file())
            b.check(tool+':channels:'+label,closed and clean)
            channel_rows.append({'channel':label,'closed':closed,'artifacts_absent':clean})
    finally:plugin.unlink(missing_ok=True)
    b.check(tool+':channel_site_restored',photograph()==baseline)
    return channel_rows
