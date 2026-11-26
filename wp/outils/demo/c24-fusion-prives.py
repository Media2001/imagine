"""Retrouver les préimages C24 de ce passage par leur empreinte exacte."""
import sys
sys.dont_write_bytecode=True
import json,os,hashlib
from pathlib import Path
import c24

def run():
    root=Path(os.environ['LOCALAPPDATA'])/'hermes/cache/scratch'
    hosttemp=Path(os.environ['LOCALAPPDATA'])/'Temp'
    items={}
    def visit(v):
        if isinstance(v,dict):
            if 'file' in v and 'sha256' in v and str(v['file']).startswith(('c24-http-','b06-private-')):items[v['file']]=v['sha256']
            for x in v.values():visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
    for path in c24.PROOF.glob('fusion2050-*.json'):visit(json.loads(path.read_text(encoding='utf-8')))
    moved=0
    for name,sha in items.items():
        p=Path(name);assert not p.is_absolute() and '..' not in p.parts
        target=root/p
        if not target.is_file():
            source=hosttemp/p
            raw=source.read_bytes();assert hashlib.sha256(raw).hexdigest()==sha
            target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            with target.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
            os.chmod(target,0o600);moved+=1
        assert hashlib.sha256(target.read_bytes()).hexdigest()==sha
    c24.save('fusion2050-prives-V2',{'result':'PASS','durable_snapshots':len(items),'relocated_from_inherited_TMPDIR':moved,'bytes_preserved':True,'originals_not_deleted':True})
    print(json.dumps({'snapshots_verified':len(items),'relocated':moved}))

if __name__=='__main__':run()
