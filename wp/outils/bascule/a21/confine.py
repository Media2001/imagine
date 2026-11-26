#!/usr/bin/env python3
"""Supervise every confined PHP byte; publish only after complete termination."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import sys
import tempfile
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
SUCCESS=b'A21_OK portes.json portes.md\n'
CODES=frozenset('''A11_CONFIG_OVERRIDE_UNSUPPORTED A11_CONFIG_UNSAFE A11_DROPIN_UNSUPPORTED
A11_HOME_INVALID A11_MULTISITE_UNSUPPORTED A11_READONLY_TRANSACTION_FAILED
A11_SYMLINK_UNSUPPORTED A11_WRITE_FORBIDDEN A21_USAGE A21_OUTPUT_UNSAFE A21_OUTPUT_EXISTS
A21_AUDIT_GUARD A21_CONFINEMENT_REQUIRED A21_CLOCK_INVALID A21_NATIVE_API_UNAVAILABLE
A21_QUERY_FAILED A21_STORE_SCHEMA_UNSUPPORTED A21_AUDIT_STORAGE_MISMATCH A21_OUTPUT_CREATE
A21_OUTPUT_WRITE A21_RUNTIME_WARNING A21_INVENTORY_FAILED A21_CONFINEMENT_FAILED
A21_UNEXPECTED_OUTPUT A21_SUCCESS_INCOMPLETE A21_PROCESS_TIMEOUT'''.split())
DROPINS=('wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php',
         'wp-content/sunrise.php','wordfence-waf.php','.user.ini')
REFUSALS={ (code+'\n').encode():code+'\n' for code in CODES }
REFUSALS.update({('A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))+'\n').encode():
                 'A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))+'\n' for name in DROPINS})

def supervise(command,env,write_root,fence):
    # No site PHP runs in this supervisor. Only the child gets staging write rights.
    with subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,
                          preexec_fn=lambda:fence.confine(write_root)) as child:
        buffers={child.stdout:bytearray(),child.stderr:bytearray()}
        overflow=False
        deadline=time.monotonic()+120
        with selectors.DefaultSelector() as streams:
            for stream in buffers:
                streams.register(stream,selectors.EVENT_READ)
            while streams.get_map():
                if time.monotonic()>deadline:
                    child.kill()
                    child.wait()
                    raise RuntimeError('A21_PROCESS_TIMEOUT')
                for key,_ in streams.select(0.1):
                    block=os.read(key.fileobj.fileno(),8192)
                    if not block:
                        streams.unregister(key.fileobj)
                    elif len(buffers[key.fileobj])+len(block)<=65536:
                        buffers[key.fileobj].extend(block)
                    else:
                        overflow=True
        try:
            code=child.wait(timeout=max(0.01,deadline-time.monotonic()))
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
            raise RuntimeError('A21_PROCESS_TIMEOUT') from None
        if overflow:
            raise RuntimeError('A21_UNEXPECTED_OUTPUT')
        return code,bytes(buffers[child.stdout]),bytes(buffers[child.stderr])

def complete_report(output,audit):
    try:
        if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!={'portes.json','portes.md'}:
            return False
        for p in output.iterdir():
            if p.is_symlink() or not p.is_file() or p.stat().st_size>1048576:
                return False
        raw=(output/'portes.json').read_bytes()
        data=json.loads(raw)
        return (data['schema']=='imagine-a21-external-doors-v1' and data['read_only'] is True
                and data['storage'] in {'classic','hpos'}
                and data['audit_sha256']==hashlib.sha256(audit.read_bytes()).hexdigest()
                and all(key in data for key in ('api_keys','webhooks','extension_store','as_of_utc','outbound_attempts','basis'))
                and (output/'portes.md').read_bytes()==
                '# Portes vers l’extérieur — lecture seule\n\nComptes seulement ; aucune révocation ni décision.\n\n```json\n'.encode()+raw+b'```\n')
    except (OSError,ValueError,KeyError,TypeError):
        return False

def main():
    options={}
    for arg in sys.argv[1:]:
        key,sep,value=arg.partition('=')
        if not sep or not value or key not in {'--wp-path','--output','--audit','--as-of'} or key in options:
            raise RuntimeError('A21_USAGE')
        options[key]=value
    if not {'--wp-path','--output','--audit'}.issubset(options):
        raise RuntimeError('A21_USAGE')
    spec=importlib.util.spec_from_file_location('a12_fence',HERE.parent/'a12/confine.py')
    fence=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fence)
    site=Path(options['--wp-path']).resolve(strict=True)
    parent=Path(options['--output']).parent.resolve(strict=True)
    output=parent/Path(options['--output']).name
    candidate=HERE.parents[3] if len(HERE.parents)>3 else HERE.parent
    repo=candidate if (candidate/'wp/outils/bascule/audit').is_file() else HERE.parent
    if not site.is_dir() or not re.fullmatch(r'[A-Za-z0-9_-]+',output.name) or not fence.disjoint_output(parent,site,repo):
        raise RuntimeError('A21_OUTPUT_UNSAFE')
    if output.exists() or output.is_symlink():
        raise RuntimeError('A21_OUTPUT_EXISTS')
    audit=Path(options['--audit'])
    if audit.is_symlink() or not audit.is_file() or audit.stat().st_size>16777216 or audit.resolve().parent.parent!=parent:
        raise RuntimeError('A21_AUDIT_GUARD')
    # PHP cannot write under the public parent, nor publish before shutdown ends.
    with tempfile.TemporaryDirectory(prefix='.a21-private-',dir=parent) as temporary:
        stage=Path(temporary)
        (stage/'audit').mkdir(mode=0o700)
        staged_audit=stage/'audit/audit.json'
        shutil.copyfile(audit,staged_audit)
        staged_output=stage/'portes'
        args=['--wp-path='+str(site),'--output='+str(staged_output),'--audit='+str(staged_audit)]
        if '--as-of' in options:
            args.append('--as-of='+options['--as-of'])
        command=['php','-d','display_errors=0','-d','log_errors=0','-d',
                 'disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec',
                 str(HERE/'inventorier-portes'),*args]
        code,stdout,stderr=supervise(command,{**os.environ,'A21_CONFINED':'1'},stage,fence)
        if code==1 and stdout==b'' and stderr in REFUSALS:
            sys.stderr.write(REFUSALS[stderr])
            return 1
        if code!=0 or stdout!=SUCCESS or stderr!=b'':
            raise RuntimeError('A21_UNEXPECTED_OUTPUT')
        if not complete_report(staged_output,staged_audit):
            raise RuntimeError('A21_SUCCESS_INCOMPLETE')
        staged_output.rename(output)
    sys.stdout.write(SUCCESS.decode('ascii'))
    return 0

if __name__=='__main__':
    try:
        sys.exit(main())
    except Exception as error:
        code=str(error) if isinstance(error,RuntimeError) and str(error) in CODES else 'A21_CONFINEMENT_FAILED'
        print(code,file=sys.stderr)
        sys.exit(1)
