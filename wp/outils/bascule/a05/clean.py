"""A05 explicit cleanup. Linux only. Guards imported unchanged from A04."""
import argparse
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time
sys.dont_write_bytecode = True
ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('a04_guard', ROOT.parent / 'a04/update.py')
a04 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a04)

class Refusal(RuntimeError):
    pass

def need(ok, code, name=''):
    if not ok: raise Refusal(code + (':' + name if name else ''))

def plugin_action(plan, name):
    rows=[row for row in plan['plugins'] if row['plugin']==name or row['plugin']==name.split('/')[0]]
    return 'garder' if not rows or any(row['action']=='garder' for row in rows) else rows[0]['action']

def relative(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*', value)) and all(x not in ['.','..'] for x in value.split('/'))

def validate(plan):
    need(isinstance(plan, dict) and set(plan)=={'schema','site_status','plugins','tables','options','cron','uploads','table_owners'}, 'A05_PLAN')
    need(plan['schema']=='imagine-a05-v1' and plan['site_status'] in ['verified-staging','frozen-production'], 'A05_STATUS')
    for kind in ['plugins','tables','options','cron','uploads']:
        rows=plan[kind]; need(isinstance(rows,list) and len(rows)<=1000,'A05_PLAN')
        seen=set()
        for row in rows:
            fields={'plugin','action','uninstall'} if kind=='plugins' else {'path','action'} if kind=='uploads' else {'match','name','action'}
            need(isinstance(row,dict) and set(row)==fields,'A05_PLAN')
            key=row.get('plugin',row.get('path',row.get('name')))
            need(isinstance(key,str) and relative(key) and (kind in ['plugins','uploads'] or '/' not in key),'A05_NAME',str(key))
            need(key not in seen,'A05_DUPLICATE',key);seen.add(key)
            need(row['action'] in (['garder','desactiver','retirer'] if kind=='plugins' else ['garder','supprimer']),'A05_ACTION',key)
            if kind=='plugins':
                need((key.endswith('.php') or (row['action']=='garder' and '/' not in key)) and isinstance(row['uninstall'],bool) and (not row['uninstall'] or row['action']=='retirer'),'A05_PLUGIN',key)
            elif kind!='uploads':
                need(row['match'] in (['exact'] if kind=='cron' else ['exact','prefix']),'A05_MATCH',key)
    need(isinstance(plan['table_owners'],dict),'A05_OWNERS')
    for owner,families in plan['table_owners'].items():
        need(isinstance(owner,str) and (relative(owner) or owner.startswith(('theme:','mu:'))) and isinstance(families,list),'A05_OWNERS')
        need(all(isinstance(f,str) and re.fullmatch('[A-Za-z0-9_]+',f) for f in families),'A05_OWNERS',owner)
    return plan

def selected(rows,name):
    matching=[r for r in rows if (name==r['name'] if r['match']=='exact' else name.startswith(r['name']))]
    return bool(matching) and not any(r['action']=='garder' for r in matching)

def protected_plugin(name,meta):
    slug=name.split('/')[0].lower()
    return slug in ['woocommerce','woocommerce-subscriptions','woocommerce-memberships'] or bool(meta.get('gateway')) or bool(re.search(r'gateway|stripe|paypal|mollie|payment',slug))

def protect(plan,inv):
    plugins=inv['plugins']
    for name,meta in plugins.items():
        action=plugin_action(plan,name)
        if action!='garder': need(not protected_plugin(name,meta),'A05_PROTECTED_PLUGIN',name)
        if action=='garder':
            for dependency in meta.get('requires',[]):
                for target in plugins:
                    if target.split('/')[0]==dependency:
                        need(plugin_action(plan,target)=='garder','A05_DEPENDENCY',target)
    deleted=[r['name'] for r in inv['tables'] if selected(plan['tables'],r['name'])]
    if deleted:
        kept=[n for n in plugins if plugin_action(plan,n)!='retirer']
        kept+=['theme:'+inv['theme']]+['mu:'+n for n in inv.get('mu_plugins',[]) if n!='001-imagine-a04-maintenance.php']
        for name in kept: need(name in plan['table_owners'],'A05_TABLE_OWNERSHIP_REQUIRED',name)
        for name in deleted:
            prefix=inv['prefix'];suffix=name[len(prefix):] if name.startswith(prefix) else name
            core=['posts','postmeta','users','usermeta','options','terms','termmeta','term_taxonomy','term_relationships','comments','commentmeta','links','blogs','blogmeta','site','sitemeta','signups','registration_log']
            need(suffix not in core and not suffix.startswith(('woocommerce_','wc_','wcs_','actionscheduler_')),'A05_PROTECTED_TABLE',name)
            for owner in kept:
                need(not any(name.startswith(f) for f in plan['table_owners'][owner]),'A05_KEPT_PLUGIN_TABLE',name)
    for row in inv['options']:
        name=row['name']
        if selected(plan['options'],name):
            need(not re.match(r'^(?:woocommerce|wc_|wcs_|wp_|cron$|active_plugins$|uninstall_plugins$|template$|stylesheet$|siteurl$|home$|theme_|_site_transient_)',name),'A05_PROTECTED_OPTION',name)
    for row in inv['cron']:
        if selected(plan['cron'],row['name']):
            need(not re.match(r'^(?:woocommerce|wc_|wcs_|wp_|action_scheduler)',row['name']),'A05_PROTECTED_CRON',row['name'])

def safe_upload(site,path):
    need(relative(path),'A05_UPLOAD_PATH',str(path))
    base=a04.safe_path(site,'wp-content/uploads')
    need(base.is_dir() and base.resolve()==base,'A05_UPLOAD_ROOT',str(base))
    target=base/path
    for parent in [target,*target.parents]:
        if parent==base.parent: break
        need(not parent.is_symlink(),'A05_UPLOAD_SYMLINK',path)
    need(target.resolve().is_relative_to(base.resolve()) and target.resolve()!=base.resolve(),'A05_UPLOAD_PATH',path)
    if target.exists():
        need(target.is_dir(),'A05_UPLOAD_DIRECTORY',path)
        for child in target.rglob('*'):
            need(not child.is_symlink() and (child.is_file() or child.is_dir()),'A05_UPLOAD_SYMLINK',path)
    return target

def files_size(path):
    if not path.exists(): return {'files':0,'bytes':0}
    files=[path] if path.is_file() else [p for p in path.rglob('*') if p.is_file()]
    for p in [path,*path.rglob('*')] if path.is_dir() else [path]:
        need(not p.is_symlink() and (p.is_file() or p.is_dir()),'A05_FILE_TYPE',str(path))
    return {'files':len(files),'bytes':sum(p.stat().st_size for p in files)}

def database(site, mode='inspect', operation=None):
    result=subprocess.run(['php',str(ROOT/'database.php')],input=json.dumps({'site':str(site),'mode':mode,'operation':operation}),capture_output=True,text=True,timeout=300,pass_fds=a04.LOCK_FDS)
    need(result.returncode==0, result.stderr.strip() if re.fullmatch(r'A05_[A-Z_]+\n?',result.stderr) else 'A05_DATABASE_FAILED')
    return json.loads(result.stdout)

def inspect_site(site):
    inv=database(site)
    plugins={}; directory=a04.safe_path(site,'wp-content/plugins')
    for path in sorted(directory.glob('*.php'))+sorted(directory.glob('*/*.php')):
        need(not path.is_symlink(),'A05_PLUGIN_SYMLINK',str(path))
        text=path.read_text(encoding='utf8',errors='replace')[:8192]
        if not re.search(r'^\s*(?:/\*+|\*|//|#)?\s*Plugin Name:',text,re.M|re.I): continue
        name=path.relative_to(directory).as_posix(); component=name.split('/')[0]
        a04.safe_path(directory,name)
        header=re.search(r'^\s*(?:\*)?\s*Requires Plugins:\s*([^\r\n]+)',text,re.M|re.I)
        base=directory/component if '/' in name else path
        files_size(base)
        sources=base.rglob('*.php') if base.is_dir() else [base]
        gateway=any('WC_Payment_Gateway' in file.read_text(encoding='utf8',errors='replace') for file in sources)
        plugins[name]={'requires':[v.strip() for v in header[1].split(',')] if header else [],'gateway':gateway,'active':name in inv['active']}
    need(set(inv['active'])<=set(plugins),'A05_ACTIVE_PLUGIN_METADATA')
    inv['plugins']=plugins
    inv['mu_plugins']=[p.name for p in a04.safe_path(site,'wp-content/mu-plugins').glob('*.php')]
    return inv

def native(site, operation, environment):
    env={**os.environ,'IMAGINE_A04_SITE':str(site),'IMAGINE_A04_COMPONENT':'core','IMAGINE_A04_MODE':'guard','IMAGINE_A04_EXPECTED_ENV':environment,'IMAGINE_A04_JOURNAL':'','IMAGINE_A05_OPERATION':json.dumps(operation)}
    p=subprocess.run(['wp','--allow-root','--no-color','--path='+str(site),'--require='+str(ROOT/'bootstrap.php'),'eval-file',str(ROOT/'native.php'),'--use-include'],capture_output=True,text=True,env=env,pass_fds=a04.LOCK_FDS,timeout=300)
    if p.returncode:
        codes=re.findall(r'\bA0[45]_[A-Z_]+(?::[A-Za-z0-9_.\/-]+)?',p.stderr)
        raise Refusal(codes[-1] if codes else 'A05_NATIVE_FAILED')
    need('A05_JSON={"complete":true}' in p.stdout,'A05_NATIVE_RECEIPT')

def operations(site,plan,inv):
    protect(plan,inv); ops=[]
    for row in plan['plugins']:
        name=row['plugin'];a04.safe_path(site,'wp-content/plugins/'+name)
        if name not in inv['plugins']: continue
        if plugin_action(plan,name)=='garder':continue
        if inv['plugins'][name]['active']:ops.append({'kind':'deactivate','name':name,'rows':1,'bytes':0,'phase':'pending'})
        if row['action']=='retirer':
            if row['uninstall']:ops.append({'kind':'uninstall','name':name,'rows':0,'bytes':0,'phase':'pending'})
            base=name.split('/')[0] if '/' in name else name
            need(not any(n!=name and n.startswith(base+'/') and plugin_action(plan,n)=='garder' for n in inv['plugins']),'A05_SHARED_PLUGIN_DIRECTORY',base)
            path=a04.safe_path(site,'wp-content/plugins/'+base)
            ops.append({'kind':'plugin','name':name,**files_size(path),'phase':'pending'})
    for kind,plural in [('table','tables'),('option','options'),('cron','cron')]:
        for row in inv[plural]:
            if selected(plan[plural],row['name']): ops.append({'kind':kind,'name':row['name'],'rows':int(row.get('rows',1)),'bytes':int(row['bytes']),'phase':'pending'})
    for row in plan['uploads']:
        path=safe_upload(site,row['path'])
        if row['action']=='garder':continue
        for kept in plan['uploads']:
            need(not (kept['action']=='garder' and (kept['path']==row['path'] or kept['path'].startswith(row['path']+'/'))),'A05_UPLOAD_KEEP_CONFLICT',row['path'])
        if path.exists():ops.append({'kind':'upload','name':row['path'],**files_size(path),'phase':'pending'})
    return ops

def authorize(plan,site,identity,gofile):
    if plan['site_status']=='verified-staging':return a04.authorize('verified-staging',site,identity,None)
    # A04 authorizes task A-04 only: an old update GO must NOT authorize cleanup.
    need(bool(gofile),'A05_PRODUCTION_GO_REQUIRED')
    go=a04.load_json(gofile)
    need(set(go)=={'author','task','go','site','plan_sha256','expires_at'} and go['author']=='Ced' and go['task']=='A-05-nettoyage' and go['go'] is True and go['site']==str(site) and go['plan_sha256']==identity and isinstance(go['expires_at'],int) and 0<go['expires_at']-time.time()<=21600,'A05_PRODUCTION_GO_INVALID')
    return 'production'

def execute(args):
    need(sys.platform=='linux','A05_LINUX_REQUIRED');import fcntl
    site=pathlib.Path(args.wp_path)
    need(site.is_absolute() and site.is_dir() and site.resolve()==site,'A05_SITE_PATH')
    plan=validate(a04.load_json(args.plan));identity=a04.digest(args.plan)
    environment=authorize(plan,site,identity,args.go)
    state_dir=pathlib.Path(args.state)
    need(state_dir.is_absolute() and state_dir.resolve()==state_dir and not state_dir.is_relative_to(site),'A05_STATE_PATH')
    # The existing shared A04 lock is deliberately never created by a dry-run.
    lock_path=a04.safe_path(site,'.imagine-a04-bascule.lock')
    need(lock_path.is_file(),'A05_SHARED_LOCK_REQUIRED',str(lock_path))
    with open(lock_path,'r') as site_lock:
        try:fcntl.flock(site_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise Refusal('A04_ALREADY_RUNNING') from None
        a04.LOCK_FDS=(site_lock.fileno(),)
        if environment=='staging':
            marker=a04.load_json(a04.safe_path(site,'.imagine-staging-verified.json'))
            need(marker.get('status')=='verified' and marker.get('offline_verified') is True and marker.get('runtime_probe_passed') is True,'A04_NOT_VERIFIED')
            safety=a04.safe_path(site,'wp-content/mu-plugins/000-imagine-staging-safety.php')
            reference=ROOT.parents[1]/'staging/mu-plugins/000-imagine-staging-safety.php'
            need(safety.is_file() and reference.is_file() and a04.digest(safety)==a04.digest(reference),'A04_SAFETY_BYTES')
        for name in ['db.php','object-cache.php','advanced-cache.php']:
            path=site/'wp-content'/name;need(not path.exists() and not path.is_symlink(),'A04_DROPIN',name)
        a04.check_backup(a04.load_json(args.backup),site)
        config=a04.digest(a04.safe_path(site,'wp-config.php'))
        state_file=a04.safe_path(state_dir,'etat.json')
        state=a04.load_json(state_file) if state_file.exists() else None
        persistent=a04.safe_path(site,'wp-content/mu-plugins/001-imagine-a04-maintenance.php')
        template=ROOT.parent/'a04/maintenance.php'
        if persistent.exists():need(a04.digest(persistent)==a04.digest(template),'A04_MAINTENANCE_BYTES')
        if state:
            need(state.get('schema')=='imagine-a05-state-v1' and state.get('site')==str(site) and state.get('plan_sha256')==identity and state.get('config_sha256')==config and isinstance(state.get('operations'),list),'A05_STATE')
            need(persistent.is_file() and a04.digest(persistent)==a04.digest(template),'A04_MAINTENANCE_BYTES')
            if not args.dry_run and not state['complete']:a04.refresh_maintenance(site)
            else:a04.maintenance(site)
        else:a04.maintenance(site)
        inv=inspect_site(site); proposed=operations(site,plan,inv)
        if args.dry_run:
            print(json.dumps({'mode':'dry-run','operations':proposed,'table_bytes':'allocated data+indexes; rows exact','uninstall_effects':'unknown third-party routine; not executed'},ensure_ascii=False,indent=2));return 0
        if state and state['complete']:
            need(not proposed,'A05_COMPLETED_DRIFT');print('A05_NOOP');return 0
        if state is None:
            if not proposed: print('A05_NOOP');return 0
            state={'schema':'imagine-a05-state-v1','site':str(site),'plan_sha256':identity,'config_sha256':config,'operations':proposed,'events':[],'complete':False}
        state_dir.mkdir(mode=0o700,parents=True,exist_ok=True)
        with open(a04.safe_path(state_dir,'execution.lock'),'a') as state_lock:
            try:fcntl.flock(state_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Refusal('A04_ALREADY_RUNNING') from None
            a04.LOCK_FDS=(site_lock.fileno(),state_lock.fileno())
            # No state writes, MU creation or deletion before full plan safety preflight.
            native(site,{'kind':'preflight','hooks':[o['name'] for o in state['operations'] if o['kind']=='cron']},environment)
            if persistent.exists():need(a04.digest(persistent)==a04.digest(template),'A04_MAINTENANCE_BYTES')
            else:shutil.copyfile(template,persistent)
            def save():
                a04.atomic_json(state_file,state);a04.atomic_json(state_dir/'journal.json',state['events'])
                (state_dir/'journal.txt').write_text('A-05 — maintenance conservée\n'+'\n'.join(json.dumps(e,ensure_ascii=False,sort_keys=True) for e in state['events'])+'\n',encoding='utf8')
            def event(op,phase):
                state['events'].append({'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'kind':op['kind'],'name':op['name'],'stage':phase});save()
            save()
            for index,op in enumerate(state['operations'],1):
                if op['phase']=='done':continue
                need(op['phase'] in ['pending','started'],'A05_STATE')
                # Arbitrary third-party uninstall routines cannot be made atomic.
                need(not(op['kind']=='uninstall' and op['phase']=='started'),'A05_UNINSTALL_AMBIGUOUS',op['name'])
                op['phase']='started';event(op,'start')
                if op['kind'] in ['deactivate','uninstall']:native(site,op,environment)
                elif op['kind']=='plugin':
                    rel=op['name'].split('/')[0] if '/' in op['name'] else op['name'];path=a04.safe_path(site,'wp-content/plugins/'+rel);files_size(path)
                    if path.is_dir():shutil.rmtree(path)
                    elif path.exists():path.unlink()
                    need(not path.exists(),'A05_FILE_READBACK',op['name'])
                elif op['kind']=='upload':
                    path=safe_upload(site,op['name'])
                    if path.exists():shutil.rmtree(path)
                    need(not path.exists(),'A05_FILE_READBACK',op['name'])
                elif op['kind'] in ['table','option','cron']:database(site,'apply',op)
                else:raise Refusal('A05_OPERATION')
                op['phase']='done';event(op,'done')
                if args.stop_after==index:
                    event(op,'interruption_requested')
                    if args.pause:
                        while True:time.sleep(1)
                    return 75
            state['complete']=True;event({'kind':'all','name':'all'},'complete')
            print('A05_OK');return 0

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for option in ['wp-path','plan','backup','state']:p.add_argument('--'+option,required=True)
    p.add_argument('--go');p.add_argument('--dry-run',action='store_true');p.add_argument('--stop-after',type=int,default=0);p.add_argument('--pause',action='store_true')
    try:return execute(p.parse_args())
    except Exception as error:
        message=str(error)
        print(message if isinstance(error,(Refusal,a04.Refusal)) and re.fullmatch(r'A0[45]_[A-Z_]+(?::[^\r\n]+)?',message) else 'A05_EXECUTION_FAILED',file=sys.stderr);return 1


