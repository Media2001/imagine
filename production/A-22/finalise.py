"""Publish one genuinely executed A22 packet; never run parent gates or create PRET."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'production/A-22/preuves/final'
SCRATCH=Path(os.environ.get('TMPDIR','C:/Users/Ced/AppData/Local/hermes/cache/scratch'))
spec=importlib.util.spec_from_file_location('a22_verify',ROOT/'wp/tests/a22/verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


def load(path):
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=v.unique)


def checked(packet):
    output=io.StringIO()
    with contextlib.redirect_stdout(output):code=v.verify(packet)
    result=json.loads(output.getvalue(),object_pairs_hook=v.unique)
    assert code==result['exit_code']==0 and result['readiness_claimed'] is False
    return result


def publish(matrix,style):
    matrix=matrix.resolve();style=style.resolve()
    assert matrix.is_relative_to(SCRATCH.resolve()) and style.is_relative_to(SCRATCH.resolve())
    assert not PACKET.exists() and not PACKET.is_symlink() and not PACKET.parent.is_symlink()
    assert not (ROOT/'production/A-22/PRET').exists()
    assert load(matrix/'windows-matrix.json')['exit_code']==0
    assert load(matrix/'sources.json')==v.m.sources() and load(style/'style.json')['exit_code']==0
    with tempfile.TemporaryDirectory(prefix='a22-finalise-',dir=SCRATCH) as temporary:
        stage=Path(temporary)/'packet';shutil.copytree(matrix,stage);shutil.copytree(style,stage/'style')
        (stage/'manifest.json').write_text(json.dumps(v.hashes(stage),indent=2)+'\n',encoding='utf-8')
        checked(stage)
        PACKET.parent.mkdir(parents=True,exist_ok=True)
        assert PACKET.parent.resolve().is_relative_to(ROOT/'production/A-22')
        stage.rename(PACKET)
    return checked(PACKET)


def seal():
    result=checked(PACKET)
    manifest=ROOT/'production/A-22/manifest.json'
    if manifest.exists():load(manifest)
    files=v.m.sources()
    files.update({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(manifest.parent.rglob('*')) if p.is_file() and p!=manifest
        and p.name!='PRET' and '__pycache__' not in p.parts})
    value={'lot':'A-22','status':'CANDIDAT_GATE_PARENT','readiness_claimed':False,
           'parent_preparation':'not_executed_by_child','parent_global_T01':'not_executed_by_child',
           'PRET_created_by_child':False,'packet':'production/A-22/preuves/final',
           'inventory_scope':'executed_source_snapshot_and_owned_A22_delivery','file_count':len(files),'files':files}
    manifest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
    assert load(manifest)==value
    assert all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in files.items())
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--matrix',type=Path);ap.add_argument('--style',type=Path)
    ap.add_argument('--seal-only',action='store_true');args=ap.parse_args()
    if args.seal_only:
        if args.matrix or args.style:ap.error('--seal-only does not publish')
        result=seal()
    else:
        if args.matrix is None or args.style is None:ap.error('--matrix and --style are required')
        result=publish(args.matrix,args.style)
    print(json.dumps({'packet':str(PACKET),'packet_files':len(v.hashes(PACKET)),
          'verifier_checks':len(result['checks']),'exit_code':result['exit_code'],
          'readiness_claimed':False,'PRET_created_by_child':False},indent=2));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except Exception as error:
        print(json.dumps({'exit_code':1,'code':'A22_FINALISATION_FAILED','class':type(error).__name__}));sys.exit(1)
