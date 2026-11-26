"""One bounded PHP stream guardian, extracted from the A21 candidate.

Only reconstructed closed messages leave this process. Raw child bytes stay in
bounded memory and are discarded, including shutdown output. Publication follows
both pipe EOFs, process termination and report validation.
"""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent


def supervise(command,env,write_root,fence,*,input_data=None,timeout=120,
              invalid='A22_OUTPUT_INVALID',expired='A22_PROCESS_TIMEOUT'):
    # Reader threads retain A21's 64 KiB bound and drain both pipes concurrently;
    # unlike select on pipes, this also exercises the real Windows interpreter.
    options={'preexec_fn':lambda:fence.confine(write_root)} if fence is not None else {}
    child=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
        stdin=subprocess.PIPE if input_data is not None else subprocess.DEVNULL,env=env,**options)
    buffers=[bytearray(),bytearray()]
    overflow=threading.Event();stopped=threading.Event()
    deadline=time.monotonic()+timeout
    def drain(stream,index):
        descriptor=stream.fileno()
        try:
            while not stopped.is_set():
                try:block=os.read(descriptor,8192)
                except OSError:return
                if not block:return
                if len(buffers[index])+len(block)<=65536:buffers[index].extend(block)
                else:overflow.set()
        finally:
            # Only the reader closes its pipe: on Windows a concurrent close can
            # wait for a descendant's inherited handle past the deadline.
            stream.close()
    readers=[threading.Thread(target=drain,args=(stream,i),daemon=True)
             for i,stream in enumerate([child.stdout,child.stderr])]
    for reader in readers:reader.start()
    def feed():
        try:child.stdin.write(input_data)
        except (BrokenPipeError,OSError):pass
        finally:
            try:child.stdin.close()
            except (BrokenPipeError,OSError):pass
    if input_data is not None:threading.Thread(target=feed,daemon=True).start()
    try:
        code=child.wait(timeout=max(.001,deadline-time.monotonic()))
        for reader in readers:reader.join(timeout=max(0,deadline-time.monotonic()))
        if any(reader.is_alive() for reader in readers):raise subprocess.TimeoutExpired(command,timeout)
    except subprocess.TimeoutExpired:
        stopped.set();child.kill();child.wait()
        raise RuntimeError(expired) from None
    if overflow.is_set():raise RuntimeError(invalid)
    return code,bytes(buffers[0]),bytes(buffers[1])


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def closed_refusal(code,stdout,stderr,allowed,invalid):
    # Exact complete byte messages, not a prefix or regex over site-controlled text.
    messages={(value+'\n').encode():value for value in allowed}
    return messages[stderr] if code==1 and stdout==b'' and stderr in messages else invalid


SUCCESS={
    'A03':'A03_OK non-regression.json\n',
    'A11':'A11_OK adresses.csv adresses.json resume.md\n',
    'A12':'A12_OK contenus.json contenus.md\n',
    'A14':'A14_OK\n',
    'A15':'A15_OK emails.json emails.md\n',
    'A16':'A16_OK numeros.json numeros.md\n',
    'A17':'A17_OK securite.json securite.md\n',
    'A18':'A18_OK conservation.json conservation.md\n',
    'A19':'A19_OK coherence.json coherence.md\n',
}
FILES={
    'A03':{'non-regression.json'},
    'A11':{'adresses.csv','adresses.json','resume.md'},
    'A12':{'contenus.json','contenus.md'},
    'A14':{'resume.json','resume.md','rapproches.csv'},
    'A15':{'emails.json','emails.md'},
    'A16':{'numeros.json','numeros.md'},
    'A17':{'securite.json','securite.md'},
    'A18':{'conservation.json','conservation.md'},
    'A19':{'coherence.json','coherence.md'},
}


def allowed_messages():
    codes=json.loads((HERE/'stream_refusals.json').read_text(encoding='utf-8'))
    codes += ['A11_DROPIN_UNSUPPORTED '+json.dumps({'file':name},separators=(',',':'))
              for name in ('wp-content/db.php','wp-content/object-cache.php','wp-content/advanced-cache.php',
                           'wp-content/sunrise.php','wordfence-waf.php','.user.ini')]
    codes += ['A16_MAPPING_KEY_ABSENT '+json.dumps({'field':name},separators=(',',':'))
              for name in ('numero_type','thematique','pdf_cle','liaison.cle')]
    return codes


def public_error(error,tool):
    allowed=set(allowed_messages())|{tool+suffix for suffix in
        ('_PROCESS_OUTPUT_INVALID','_PROCESS_TIMEOUT','_SUCCESS_INCOMPLETE')}
    return str(error) if isinstance(error,RuntimeError) and str(error) in allowed else tool+'_CONFINEMENT_FAILED'


def complete(output,files):
    if output.is_symlink() or not output.is_dir() or {p.name for p in output.iterdir()}!=files:return False
    for p in output.iterdir():
        if p.is_symlink() or not p.is_file() or not 0<p.stat().st_size<=16777216:return False
        if p.suffix=='.json':
            try:json.loads(p.read_bytes())
            except (ValueError,UnicodeError):return False
    return True


def inventory(tool,entry,options,*,fence=None,input_data=None,arguments=None):
    site=Path(options['--wp-path']).resolve(strict=True)
    parent=Path(options['--output']).parent.resolve(strict=True)
    output=parent/Path(options['--output']).name
    candidate=HERE.parents[2] if len(HERE.parents)>2 else HERE
    repository=candidate if (candidate/'wp/outils/bascule/audit').is_file() else HERE
    if (not re.fullmatch(r'[A-Za-z0-9_-]+',output.name) or str(parent)=='/'
        or any(parent==root or root in parent.parents or parent in root.parents for root in (site,repository))):
        raise RuntimeError(tool+'_OUTPUT_UNSAFE')
    if output.exists() or output.is_symlink():raise RuntimeError(tool+'_OUTPUT_EXISTS')
    audit=Path(options['--audit']) if '--audit' in options else None
    if audit is not None and (audit.is_symlink() or not audit.is_file() or audit.stat().st_size>16777216
                              or audit.resolve().parent.parent!=parent):raise RuntimeError(tool+'_AUDIT_GUARD')
    with tempfile.TemporaryDirectory(prefix='.a22-private-',dir=parent) as temporary:
        stage=Path(temporary);os.chmod(stage,0o700)
        staged=dict(options);staged['--output']=str(stage/'result')
        if audit is not None:
            (stage/'audit').mkdir(mode=0o700)
            shutil.copyfile(audit,stage/'audit/audit.json');staged['--audit']=str(stage/'audit/audit.json')
        args=[key+'='+value for key,value in staged.items()]
        if arguments:args.extend(arguments)
        command=['php','-d','display_errors=0','-d','log_errors=0','-d','error_log=/dev/null']
        if fence is not None:command+=['-d','disable_functions=mail,exec,shell_exec,system,passthru,popen,proc_open,pcntl_exec']
        command += [str(entry),*args]
        code,stdout,stderr=supervise(command,{**os.environ,tool+'_CONFINED':'1','A22_SUPERVISED':tool},
            stage,fence,input_data=input_data,invalid=tool+'_PROCESS_OUTPUT_INVALID',expired=tool+'_PROCESS_TIMEOUT')
        if code!=0 or stdout!=SUCCESS[tool].encode() or stderr:
            raise RuntimeError(closed_refusal(code,stdout,stderr,allowed_messages(),tool+'_PROCESS_OUTPUT_INVALID'))
        if not complete(stage/'result',FILES[tool]):raise RuntimeError(tool+'_SUCCESS_INCOMPLETE')
        (stage/'result').rename(output)
    sys.stdout.write(SUCCESS[tool])
    return 0


def cli():
    tool=sys.argv[1]
    entry={'A03':HERE/'non-regression','A11':HERE/'a11/inventorier-adresses'}[tool]
    options={};flags=[]
    try:
        for arg in sys.argv[2:]:
            if arg=='--renewal-test' and tool=='A03' and arg not in flags:flags.append(arg);continue
            key,sep,value=arg.partition('=')
            keys={'--wp-path','--output','--config'} if tool=='A03' else {'--wp-path','--output','--audit'}
            if not sep or not value or key not in keys or key in options:raise RuntimeError(tool+'_USAGE')
            options[key]=value
        if len(options)!=3:raise RuntimeError(tool+'_USAGE')
        return inventory(tool,entry,options,arguments=flags)
    except Exception as error:
        message=str(error)
        if tool=='A03' and isinstance(error,OSError):message='A03_OUTPUT_FAILED'
        codes=set(allowed_messages())|{tool+x for x in ('_OUTPUT_UNSAFE','_OUTPUT_EXISTS','_PROCESS_OUTPUT_INVALID','_PROCESS_TIMEOUT','_SUCCESS_INCOMPLETE')}
        print(message if message in codes and isinstance(error,(RuntimeError,OSError)) else tool+'_EXECUTION_FAILED',file=sys.stderr)
        return 1

if __name__=='__main__':sys.exit(cli())
