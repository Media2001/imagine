"""Execute an unchanged native bank with additive channel probes at first success."""
import importlib.util
import json
import os
from pathlib import Path
import sys
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('channels','/opt/a22/channels.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
original_path,tool=sys.argv[1:]
spec=importlib.util.spec_from_file_location('original_native',original_path)
native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
b=getattr(native,'b',native)
original_cmd=b.cmd
seen=set();checks=[]

def check(name,ok,detail=None):checks.append({'check':name,'status':'PASS' if ok else 'FAIL'})


def wrapped(args,*pos,**kw):
    result=original_cmd(args,*pos,**kw)
    options={part.partition('=')[0]:part.partition('=')[2] for part in args if part.startswith('--') and '=' in part}
    # Only an actual native inventory success can unlock the adversarial probes.
    expected=(tool+'_OK').encode()
    stdout=result.stdout.encode() if isinstance(result.stdout,str) else result.stdout
    if result.returncode==0 and stdout.startswith(expected) and '--wp-path' in options and '--output' in options:
        site=Path(options['--wp-path'])
        if site not in seen:
            seen.add(site)
            command=[('--output={output}' if part.startswith('--output=') else part) for part in args]
            original_check=b.check;b.check=lambda name,ok,detail=None:check(site.name+':'+name,ok)
            try:c.exercise(b,tool,command,site,Path('/report'))
            finally:b.check=original_check
            # Positive witness: bypass ONLY the common guard in a disposable copy.
            roots=[Path('/checkout/wp/outils/bascule'),Path('/subject')] if any(str(x).startswith('/checkout/') for x in command) else [Path('/subject')]
            guard=next((p/'stream_guard.py' for p in roots if (p/'stream_guard.py').is_file()),None)
            if guard is None:raise RuntimeError('A22_GUARD_COPY_MISSING')
            source=guard.read_bytes()
            marker=b'def supervise(command,env,write_root,fence,'
            assert source.count(marker)==1
            start=source.index(marker);end=source.index(b'\n\ndef load(',start)
            mutant=b'''def supervise(command,env,write_root,fence,*,input_data=None,**kwargs):
    options={'preexec_fn':lambda:fence.confine(write_root)} if fence is not None else {}
    subprocess.run(command,input=input_data,env=env,**options)
    return 0,b'',b''
'''
            hostile=site/'wp-content/mu-plugins/000-a22-hostile.php'
            try:
                guard.write_bytes(source[:start]+mutant+source[end:])
                hostile.write_text("<?php if (getenv('A22_SUPERVISED') === '"+tool+"' || getenv('"+tool+"_CONFINED') === '1') { fwrite(STDERR,'A22_PRIVATE_FLOW_CANARY'); }",encoding='utf-8')
                import subprocess
                dest=Path('/report')/(site.name+'-mutation')
                witness=subprocess.run([x.replace('{output}',str(dest)) for x in command],capture_output=True,timeout=180,
                    env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
                check(site.name+':'+tool+':mutation_without_guard_leaks',b'A22_PRIVATE_FLOW_CANARY' in witness.stdout+witness.stderr)
                # Raw bytes are intentionally NEVER saved, even for the positive witness.
            finally:
                guard.write_bytes(source);hostile.unlink(missing_ok=True)
                import shutil
                if dest.exists():shutil.rmtree(dest)
                for p in Path('/report').glob('.a22-private-*'):shutil.rmtree(p)
            check(site.name+':'+tool+':guard_restored',guard.read_bytes()==source)
            if tool not in {'A20','A21'}:
                import shlex
                literal=json.loads(Path('/opt/a22/documented.json').read_text(encoding='utf-8'))[tool]
                documented=shlex.split(literal)
                base='/checkout/wp/outils/bascule' if any(str(x).startswith('/checkout/') for x in command) else '/subject'
                documented[1]=base+'/'+documented[1].split('wp/outils/bascule/',1)[1]
                docout=Path('/report')/(site.name+'-a22-documented')
                paths={'--wp-path','--audit','--config','--correspondance','--contacts'}
                for index,part in enumerate(documented):
                    key=part.partition('=')[0]
                    if key in paths:documented[index]=key+'='+options[key]
                    if key=='--output':documented[index]='--output='+str(docout)
                p=subprocess.run(documented,capture_output=True,timeout=180,
                    env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
                check(site.name+':'+tool+':documented_only_literal_arguments',p.returncode==0 and
                      p.stdout.startswith((tool+'_OK').encode()) and p.stderr==b'' and docout.is_dir())
    return result

b.cmd=wrapped
try:exit_code=b.main()
finally:
    check('two_native_storage_boundaries',len(seen)==2)
    receipt={'tool':tool,'checks':checks,'exit_code':int(any(row['status']!='PASS' for row in checks))}
    Path('/report/a22-channels.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
sys.exit(exit_code or receipt['exit_code'])
