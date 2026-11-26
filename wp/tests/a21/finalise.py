"""Publish the last green A21 scratch matrix only; never set parent gates or PRET."""
import argparse
import json
from pathlib import Path
import shutil
import sys
sys.dont_write_bytecode=True
import verify

ROOT=Path(__file__).resolve().parents[3]
PACKET=ROOT/'production/A-21/preuves/final'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def save(path,data):
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

def seal():
    sources=verify.inventory(verify.OWN)
    dependencies=verify.inventory(verify.DEPENDENCIES)
    dependencies.pop('wp/tests/a02-audit/README.md',None)
    for folder in [PACKET,PACKET/'utf8']:
        assert load(folder/'sources.json')==sources,'A21_SOURCE_DRIFT_REPLAY_REQUIRED'
        assert load(folder/'dependency-snapshot.json')==dependencies,'A21_DEPENDENCY_DRIFT_REPLAY_REQUIRED'
    assert load(PACKET/'style/style.json')['sources']==sources,'A21_STYLE_DRIFT_REPLAY_REQUIRED'
    save(PACKET/'manifest.json',verify.packet_manifest(PACKET))
    return verify.verify(PACKET)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix',type=Path)
    parser.add_argument('--style',type=Path)
    parser.add_argument('--seal-only',action='store_true')
    args=parser.parse_args()
    if not args.seal_only:
        assert args.matrix and args.style
        matrix=args.matrix.resolve()
        style=args.style.resolve()
        assert not matrix.is_relative_to(ROOT) and not style.is_relative_to(ROOT)
        assert load(matrix/'windows-matrix.json')['exit_code']==0
        assert load(style/'style.json')['exit_code']==0
        source=verify.inventory(verify.OWN)
        for console in ['cp1252','utf8']:
            folder=matrix/(console+'-native')
            assert load(folder/'sources.json')==source
            for kind in ['unit','result','runner']:
                assert load(folder/(kind+'.json'))['exit_code']==0
        if PACKET.exists():
            shutil.rmtree(PACKET)
        shutil.copytree(matrix/'cp1252-native',PACKET)
        shutil.copytree(matrix/'utf8-native',PACKET/'utf8')
        shutil.copytree(style,PACKET/'style')
        for path in matrix.iterdir():
            if path.is_file():
                shutil.copyfile(path,PACKET/path.name)
        save(PACKET/'candidate.json',{'status':'CANDIDAT_GATE_PARENT','parent_preparation':'pending',
             'parent_global_T01':'pending','readiness_claimed':False})
    return seal()

if __name__=='__main__':
    sys.exit(main())
