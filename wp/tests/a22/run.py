"""Replay one accepted native runner into A22 scratch, with additive channel probes.

No accepted proof package is rewritten. Only the legacy output assignment is
redirected in memory for A02/A10/A11; all test assertions remain unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import types
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
LOTS={'A02':'a02-audit','A03':'a03-non-regression','A10':'a10','A11':'a11',
      **{'A'+str(n):'a'+str(n) for n in [12,14,15,16,17,18,19,20,21]}}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--lot',choices=LOTS,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    out=args.output.resolve();assert not out.is_relative_to(ROOT) and not out.exists()
    path=ROOT/'wp/tests'/LOTS[args.lot]/'run.py'
    source=path.read_text(encoding='utf-8')
    if args.lot in {'A02','A10','A11'}:
        literals={
          'A02':"out = REPO / 'production/A-02/preuves' / run_id",
          'A10':"out=REPO/'production/A-10/preuves'/run_id",
          'A11':"out = pathlib.Path.home()/'AppData/Local/hermes/cache/scratch/a11'/run_id",
        }
        literal=literals[args.lot];assert source.count(literal)==1
        source=source.replace(literal,'out = A22_OUTPUT')
    runner=types.ModuleType('a22_'+args.lot);runner.__file__=str(path)
    sys.modules[runner.__name__]=runner
    exec(compile(source,str(path),'exec'),runner.__dict__)
    runner.A22_OUTPUT=out
    bench=getattr(runner,'b',getattr(runner,'bench',runner))
    original_call=bench.call
    native_executions=[]
    def dispatch(command,**kw):
        if len(command)>=4 and command[0]=='exec' and command[2]=='python3' and command[3].endswith('/inside.py'):
            name=command[1]
            if args.lot not in {'A02','A10'}:
                original_call(['exec',name,'mkdir','-p','/opt/a22'])
                for file in ['replay.py','channels.py','documented.json']:
                    original_call(['cp',bench.local(HERE/file),name+':/opt/a22/'+file])
                native_executions.append(command)
                command=[*command[:3],'/opt/a22/replay.py',command[3],args.lot]
        return original_call(command,**kw)
    def call(command,**kw):
        # WSL service cannot reliably dispatch many concurrent Windows clients.
        # Cross-process lease affects only our proof runners, never a site/daemon.
        import msvcrt
        import time
        lock=Path(os.environ.get('TMPDIR',str(Path.home()/'AppData/Local/hermes/cache/scratch')))/'a22-docker-call.lock'
        with lock.open('a+b') as handle:
            handle.seek(0,2)
            if handle.tell()==0:handle.write(b'0');handle.flush()
            while True:
                try:handle.seek(0);msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1);break
                except OSError:time.sleep(.1)
            try:return dispatch(command,**kw)
            finally:handle.seek(0);msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
    bench.call=call
    argv=[str(path)]
    if args.lot=='A03':argv+=['--name',out.name,'--output-root',str(out.parent)]
    elif args.lot not in {'A02','A10','A11'}:argv+=['--output='+str(out)]
    sys.argv=argv
    result=runner.main()
    # Source and command provenance belongs to A22, not to a re-sealed closed lot.
    receipt={'lot':args.lot,'runner':path.relative_to(ROOT).as_posix(),
      'runner_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'native_calls':native_executions,'exit_code':result}
    if out.exists():(out/'a22-replay.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':sys.exit(main())
