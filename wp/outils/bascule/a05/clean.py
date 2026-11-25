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
    return next((row['action'] for row in plan['plugins'] if row['plugin'] == name), 'garder')

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
                need(key.endswith('.php') and isinstance(row['uninstall'],bool) and (not row['uninstall'] or row['action']=='retirer'),'A05_PLUGIN',key)
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
        kept+=['theme:'+inv['theme']]+['mu:'+n for n in inv.get('mu_plugins',[])]
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
