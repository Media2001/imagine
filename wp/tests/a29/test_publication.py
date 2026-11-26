"""Real Python publication/pipe flow; explicit PHP + kernel boundary double.

Never a native PHP, Landlock, database or Docker acceptance claim.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / 'wp/outils/bascule/a29'
CHILD = r'''
import atexit,hashlib,json,os,sys
from pathlib import Path
stage=Path(sys.argv[1]); mode=sys.argv[2]
audit=stage/'audit/audit.json'; photo=json.loads(audit.read_bytes())
data={'schema':'imagine-a29-scheduled-tasks-v1','read_only':True,'storage':'classic',
 'neutralisation':'observe','failed_scope':'action_scheduler_only','window':'eight_rolling_utc_weeks',
 'counts':{**{k:{'groups':[],'autres':0} for k in ('pending','overdue','failed','renewal_weeks')},
           'other_tasks':0,'other_active_extensions':0},
 'as_of_utc':photo['generated_at_utc'],'audit_sha256':hashlib.sha256(audit.read_bytes()).hexdigest()}
out=stage/'result'
if mode=='display_exit':
 os.write(1,b'A29_DISPLAY_PRIVATE_CANARY'); sys.exit(0)
if mode=='silent_exit':sys.exit(0)
if mode=='extra_key_before_binding':data['private']='A29_JSON_PRIVATE_CANARY'
out.mkdir()
def publish():
 raw=(json.dumps(data,ensure_ascii=False,indent=4)+'\n').encode()
 (out/'taches.json').write_bytes(raw)
 (out/'taches.md').write_bytes('# Tâches planifiées — lecture seule\n\nComptes seulement ; aucune tâche exécutée.\n\n```json\n'.encode()+raw+b'```\n')
publish()
digest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir())}
os.write(1,b'A29_OK taches.json taches.md\nA29_FINAL '+json.dumps(digest,separators=(',',':')).encode()+b'\n')
if mode=='direct_stdout':os.write(1,b'A29_STDOUT_PRIVATE_CANARY')
if mode=='direct_stderr':os.write(2,b'A29_STDERR_PRIVATE_CANARY')
if mode=='shutdown_stdout':atexit.register(lambda:os.write(1,b'A29_SHUTDOWN_PRIVATE_CANARY'))
if mode=='shutdown_stderr':atexit.register(lambda:os.write(2,b'A29_SHUTDOWN_PRIVATE_CANARY'))
if mode=='shutdown_valid_counts':
 def alter():
  data['counts']['pending']['autres']=7
  publish()
 atexit.register(alter)
if mode=='shutdown_markdown':atexit.register(lambda:(out/'taches.md').write_bytes(b'A29_FILE_PRIVATE_CANARY'))
'''
HARNESS = r'''
import importlib.util,os,sys
from pathlib import Path
sys.dont_write_bytecode=True
script=Path(sys.argv[1]); mode=sys.argv[2]; body=sys.argv[3]; source_root=Path(sys.argv[4]); options=sys.argv[5:]
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
m=module('a29_subject',script)
g=module('a29_real_guard',source_root/'stream_guard.py')
f=module('a29_real_fence_geometry_only',source_root/'a12/confine.py')
class Boundary:
 closed_refusal=staticmethod(g.closed_refusal)
 @staticmethod
 def supervise(command,env,stage,fence,**kw):
  return g.supervise([sys.executable,'-B','-c',body,str(stage),mode],
    {**env,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'},None,None,**kw)
original=m.load
def load(name,path):
 if path.name=='stream_guard.py':return Boundary
 if path.name=='confine.py':return f
 return original(name,path)
m.load=load
sys.argv=[str(script),*options]
try:sys.exit(m.main())
except Exception as error:
 message=str(error) if isinstance(error,RuntimeError) and str(error) in m.REFUSALS else 'A29_CONFINEMENT_FAILED'
 print(message,file=sys.stderr);sys.exit(1)
'''


class PublicationBoundaryTests(unittest.TestCase):
    def flow(self, mode, mutation=None):
        with tempfile.TemporaryDirectory(prefix='a29-boundary-', dir=os.environ.get('TMPDIR')) as tmp:
            base = Path(tmp)
            tools = base / 'repository/wp/outils/bascule/a29'
            tools.mkdir(parents=True)
            for name in ('confine.py', 'report.py', 'refusals.json'):
                shutil.copyfile(TOOLS / name, tools / name)
            shutil.copyfile(TOOLS.parent / 'stream_guard.py', tools.parent / 'stream_guard.py')
            (tools.parent / 'audit').write_bytes(b'fixture repository marker')
            if mutation:
                p = tools / 'confine.py'
                text = p.read_text(encoding='utf-8')
                old = ('not report.final_binding(stdout, staged_output) or ' if mutation == 'binding'
                       else ' or not report.complete_report(staged_output, audit)')
                self.assertEqual(text.count(old), 1)
                p.write_text(text.replace(old, ''), encoding='utf-8')
            site = base / 'site'
            site.mkdir()
            (site / 'untouched').write_bytes(b'fictional no-site-bootstrap')
            reports = base / 'reports'
            (reports / 'audit').mkdir(parents=True)
            audit = reports / 'audit/audit.json'
            audit.write_text(json.dumps({'generated_at_utc':'2026-11-26T12:00:00+00:00',
                                         'sections':{'commerce':{'order_storage':'classic'}}}), encoding='utf-8')
            output = reports / 'result'
            before = {str(p.relative_to(site)): hashlib.sha256(p.read_bytes()).hexdigest() for p in site.rglob('*') if p.is_file()}
            p = subprocess.run([sys.executable, '-B', '-c', HARNESS, str(tools / 'confine.py'), mode, CHILD,
                                str(TOOLS.parent), '--wp-path=' + str(site), '--audit=' + str(audit), '--output=' + str(output)],
                               capture_output=True, timeout=30, text=True, encoding='utf-8', errors='strict',
                               env={**os.environ, 'PYTHONIOENCODING':'utf-8', 'PYTHONUTF8':'1', 'PYTHONDONTWRITEBYTECODE':'1'})
            self.assertEqual(before, {str(q.relative_to(site)): hashlib.sha256(q.read_bytes()).hexdigest() for q in site.rglob('*') if q.is_file()})
            self.assertFalse(list(reports.glob('.a29-private-*')))
            data = json.loads((output / 'taches.json').read_bytes()) if output.exists() else None
            return (p.returncode, p.stdout, p.stderr), data

    def test_actual_python_publication_nominal(self):
        result, data = self.flow('nominal')
        self.assertEqual(result, (0, 'A29_OK taches.json taches.md\n', ''))
        self.assertEqual(data['counts']['pending'], {'groups': [], 'autres': 0})

    def test_all_stream_channels_refuse_without_publication(self):
        for mode in ('direct_stdout', 'direct_stderr', 'display_exit', 'silent_exit', 'shutdown_stdout', 'shutdown_stderr'):
            with self.subTest(mode=mode):
                result, data = self.flow(mode)
                self.assertEqual(result, (1, '', 'A29_PROCESS_OUTPUT_INVALID\n'))
                self.assertIsNone(data)

    def test_file_channel_valid_counts_and_markdown(self):
        for mode in ('shutdown_valid_counts', 'shutdown_markdown', 'extra_key_before_binding'):
            with self.subTest(mode=mode):
                result, data = self.flow(mode)
                self.assertEqual(result, (1, '', 'A29_REPORT_INVALID\n'))
                self.assertIsNone(data)

    def test_real_red_remove_only_final_binding_in_disposable_copy(self):
        result, data = self.flow('shutdown_valid_counts', 'binding')
        self.assertEqual(result, (0, 'A29_OK taches.json taches.md\n', ''))
        self.assertEqual(data['counts']['pending']['autres'], 7)

    def test_real_red_remove_only_closed_schema_in_disposable_copy(self):
        result, data = self.flow('extra_key_before_binding', 'schema')
        self.assertEqual(result, (0, 'A29_OK taches.json taches.md\n', ''))
        self.assertEqual(data['private'], 'A29_JSON_PRIVATE_CANARY')


if __name__ == '__main__':
    unittest.main()
