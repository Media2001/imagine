"""Read-only final A22 verifier; PRET and parent gates are independent."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('a22_matrix',HERE/'matrix.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def green(data):
    if data.get('exit_code')!=0:return False
    rows=[]
    for key in ['tests','checks']:
        if key in data:
            if not isinstance(data[key],list) or not data[key]:return False
            rows+=data[key]
    return bool(rows) and all(isinstance(r,dict) and
        (r.get('status')=='PASS' if 'status' in r else r.get('ok') is True) for r in rows)


def hashes(folder):
    return {p.relative_to(folder).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file() and p!=folder/'manifest.json'}


def verify(packet,parent_proof=None):
    rows=[];counts={}
    load=lambda p:json.loads(p.read_text(encoding='utf-8'))
    def check(name,ok):rows.append({'check':name,'status':'PASS' if ok else 'FAIL'})
    source=load(packet/'sources.json')
    check('exact_current_executed_sources',source==m.sources())
    matrix=load(packet/'windows-matrix.json')
    check('complete_real_windows_matrix',matrix['exit_code']==0 and matrix['sources_stable'] is True
          and len(matrix['rows'])==46 and all(r['exit_code']==0 for r in matrix['rows']))
    for console in ['utf8','cp1252']:
        folder=packet/console
        env=load(folder/'environment.json')
        check(console+':measured_windows_console',env['platform']=='win32' and env['version_info'][:2]==[3,14]
              and env['stdout']==('utf-8' if console=='utf8' else 'cp1252') and env['stderr']==env['stdout']
              and env['utf8_mode']==int(console=='utf8'))
        for lot in m.LOTS:
            base=folder/lot
            for name in ['unit','result','runner']:
                d=load(base/(name+'.json'));check(console+':'+lot+':'+name+':green',green(d))
                counts[console+':'+lot+':'+name]=len(d.get('checks',[]))+len(d.get('tests',[]))
            runner=load(base/'runner.json')
            cleanup=[r for r in runner['checks'] if any(x in r.get('check','') for x in ['cleanup','sources_unchanged','sources_stable','protected_sources','accepted_sources','dependencies_stable'])]
            check(console+':'+lot+':owned_cleanup_sources_unchanged',bool(cleanup) and all(r.get('status')=='PASS' if 'status' in r else r.get('ok') is True for r in cleanup))
            replay=load(base/'a22-replay.json')
            path=ROOT/replay['runner']
            check(console+':'+lot+':actual_legacy_bank',replay['exit_code']==0 and replay['lot']==lot and replay['runner_sha256']==hashlib.sha256(path.read_bytes()).hexdigest())
            if lot not in {'A02','A10'}:
                d=load(base/'a22-channels.json');names={r['check'] for r in d['checks']}
                check(console+':'+lot+':all_channels_mutation_documentation',green(d) and len(d['checks'])==23 and len(names)==23
                      and all(any(name.endswith(':'+lot+':channels:'+c) for name in names) for c in
                              ['direct_stdout','direct_stderr','echo_exit','silent_exit','shutdown_stdout','shutdown_stderr','shutdown_echo'])
                      and sum(name.endswith(':mutation_without_guard_leaks') for name in names)==2
                      and sum(name.endswith(':documented_only_literal_arguments') for name in names)==2)
            log=(folder/(lot+'-python.log')).read_text(encoding='utf-8')
            match=re.search(r'Ran (\d+) tests?\b',log)
            check(console+':'+lot+':python_bank_executed',bool(match) and '\nOK\n' in log)
            counts[console+':'+lot+':python']=int(match[1]) if match else -1
        log=(folder/'A22-python.log').read_text(encoding='utf-8')
        check(console+':A22_python_tests','\nOK\n' in log)
    style=load(packet/'style/style.json')
    php=['wp/outils/bascule/non-regression','wp/outils/bascule/a11/inventorier-adresses','wp/outils/bascule/stream_bridge.php']
    check('strict_psr12_current_common_entrypoints',green(style) and style['phpcs_exit']==0
          and style['totals']['errors']==style['totals']['warnings']==0
          and style['sources']=={key:source[key] for key in php})
    check('no_retained_untrusted_payload',not any(b'A22_PRIVATE_FLOW_CANARY' in p.read_bytes() for p in packet.rglob('*') if p.is_file()))
    check('exact_packet_inventory_and_hashes',load(packet/'manifest.json')==hashes(packet))
    # Optional, never inferred from PRET or substituted for actual execution.
    if parent_proof is not None:
        proof=load(parent_proof)
        check('optional_parent_sources_current',proof['sources']==source)
        line=(ROOT/'production/A-22/readme-ajout.txt').read_bytes()
        shared=(ROOT/'wp/tests/a02-audit/README.md').read_bytes()
        check('optional_parent_shared_line_contract',line.endswith(b'\n') and shared.splitlines(keepends=True).count(line)==1)
        for gate in ['preparation','T01']:
            check('optional_parent_'+gate,green(load(Path(proof[gate]))))
    result={'status':'CANDIDAT_GATE_PARENT','readiness_claimed':False,'counts':counts,'checks':rows,
            'exit_code':int(any(r['status']!='PASS' for r in rows))}
    print(json.dumps(result,indent=2));return result['exit_code']

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('packet',type=Path);ap.add_argument('--parent-proof',type=Path)
    a=ap.parse_args()
    try:sys.exit(verify(a.packet.resolve(),a.parent_proof))
    except Exception as error:print(json.dumps({'exit_code':1,'code':'A22_PACKET_INVALID','class':type(error).__name__}));sys.exit(1)
