"""Thin A08 sequence. Native tools retain all validation and mutation logic."""
import argparse
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys
import time


def digest(path):
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix+'.tmp')
    with open(temporary, 'w', encoding='utf8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def report(state, checkpoint):
    rows = ['# Répétition A-08', '', 'Statut : '+checkpoint['status'], '',
            '| Étape | Durée (s) | Résultat | Preuves relatives à cet état |',
            '|---|---:|---|---|']
    for name in ['audit','avant','mise-a-jour','nettoyage','apres','comparaison']:
        attempts = [r for r in checkpoint['attempts'] if r['step']==name]
        duration = sum(r['duration_seconds'] for r in attempts)
        latest = attempts[-1] if attempts else None
        result = 'OK' if name in checkpoint['done'] else ('arrêt code '+str(latest['exit']) if latest else 'non lancée')
        evidence = ', '.join(r['receipt'] for r in attempts) or '—'
        rows.append('| '+name+' | '+format(duration,'.3f')+' | '+result+' | '+evidence+' |')
    comparison = checkpoint.get('comparison')
    if comparison:
        rows += ['', 'Comparaison native : attendus : '+str(comparison['attendu'])+', anormaux : '+str(comparison['anormal'])+'.']
    rows += ['', 'À regarder : '+checkpoint.get('look_at','etat.json et reçus des étapes')+'.',
             'Les durées excluent les attentes opérateur. Aucun résultat ne vaut GO de mise en ligne.',
             'Aucune valeur de base n’est reproduite ici. Les noms de ressources restent dans les preuves natives.']
    (state/'rapport.md').write_text('\n'.join(rows)+'\n', encoding='utf8')


def main(argv=None, runner=subprocess.run):
    parser = argparse.ArgumentParser(description='A08 : outils natifs, deux rendez-vous opérateur, aucun changement de garde.')
    for key in ['wp-path','state','update-plan','clean-plan','config','backup']:
        parser.add_argument('--'+key, type=pathlib.Path, required=True)
    parser.add_argument('--go-update', type=pathlib.Path)
    parser.add_argument('--go-clean', type=pathlib.Path)
    parser.add_argument('--mutations-ready', action='store_true')
    parser.add_argument('--reception-ready', action='store_true')
    parser.add_argument('--new-pass', action='store_true', help='nouvelle réception complète ; checkpoints A04/A05 conservés')
    args = parser.parse_args(argv)
    base = pathlib.Path(__file__).resolve().parents[1]
    checkpoint = None
    try:
        import fcntl
        for path in [args.wp_path,args.state,args.update_plan,args.clean_plan,args.config,args.backup]:
            if any(p.is_symlink() for p in [path,*path.parents]):
                raise ValueError('A08_SYMLINK')
        site = args.wp_path.resolve(strict=True)
        state = args.state.resolve()
        if state==site or site in state.parents:
            raise ValueError('A08_STATE_IN_SITE')
        state.mkdir(parents=True,exist_ok=True)
        identity = {'site':str(site),'inputs':{str(p.resolve()):digest(p) for p in [args.update_plan,args.clean_plan,args.config,args.backup]},
                    'tools':{str(p.relative_to(base)):digest(p) for p in base.rglob('*') if p.is_file()}}
        lock_path = pathlib.Path('/tmp')/('imagine-a08-'+hashlib.sha256(str(site).encode()).hexdigest()+'.lock')
        with open(lock_path,'a') as site_lock, open(state/'sequence.lock','a') as state_lock:
            try:
                for lock in [site_lock,state_lock]:
                    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                raise ValueError('A08_ALREADY_RUNNING')
            path = state/'etat.json'
            if path.exists():
                checkpoint = json.loads(path.read_text())
                if checkpoint['schema']!='imagine-a08-v1' or checkpoint['identity']!=identity:
                    raise ValueError('A08_IDENTITY_CHANGED')
                for entry in [*checkpoint['done'].values(),*[entry for previous in checkpoint.get('passes',[]) for entry in previous.values()]]:
                    if any(not (state/name).is_file() or digest(state/name)!=sha for name,sha in entry['seals'].items()):
                        raise ValueError('A08_EVIDENCE_CHANGED')
            else:
                checkpoint = {'schema':'imagine-a08-v1','identity':identity,'done':{},'attempts':[],'status':'en cours','passes':[]}
            if args.new_pass:
                if len(checkpoint['done'])!=6:
                    raise ValueError('A08_PASS_NOT_COMPLETE')
                checkpoint['passes'].append(checkpoint['done'])
                checkpoint['done']={}
                checkpoint.pop('comparison',None)
            def persist():
                save(path,checkpoint)
                report(state,checkpoint)
            for step in ['audit','avant','mise-a-jour','nettoyage','apres','comparaison']:
                if step in checkpoint['done']:
                    continue
                if (step in ['mise-a-jour','nettoyage'] and not args.mutations_ready) or (step=='apres' and not args.reception_ready):
                    checkpoint['status']='attente opérateur avant '+step
                    checkpoint['look_at']='repetition.md : '+('compte écriture, sauvegarde et maintenance ; puis --mutations-ready' if step!='apres' else 'réception isolée, compte SELECT ; puis --reception-ready')
                    persist()
                    return 75
                number = 1+sum(r['step']==step for r in checkpoint['attempts'])
                command = commands(base,site,state,args.config,args.update_plan,args.clean_plan,args.backup,args.go_update,args.go_clean,number)[step]
                if step=='comparaison':
                    command[-2:] = [str(state/checkpoint['done'][name]['artifact']/'non-regression.json') for name in ['avant','apres']]
                prefix = step+'-'+str(number)
                receipt_path = state/(prefix+'-receipt.json')
                started = time.monotonic()
                checkpoint['status']='en cours : '+step
                checkpoint['look_at']=receipt_path.name+' et journal natif '+('a04/' if step=='mise-a-jour' else 'a05/' if step=='nettoyage' else '')
                row = {'step':step,'command':command,'exit':None,'duration_seconds':0,'receipt':receipt_path.name}
                checkpoint['attempts'].append(row)
                persist()
                try:
                    process = runner(command,text=True,capture_output=True,pass_fds=(site_lock.fileno(),state_lock.fileno()))
                    code = process.returncode
                    stdout,stderr = process.stdout,process.stderr
                except (OSError,subprocess.SubprocessError):
                    code,stdout,stderr = 1,'','A08_CHILD_FAILED\n'
                row['exit']=code
                row['duration_seconds']=time.monotonic()-started
                (state/(prefix+'-stdout.log')).write_text(stdout,encoding='utf8')
                (state/(prefix+'-stderr.log')).write_text(stderr,encoding='utf8')
                artifact = None
                accepted = code==0
                try:
                    if step in ['audit','avant','apres']:
                        artifact = prefix
                        expected = state/artifact/('audit.json' if step=='audit' else 'non-regression.json')
                        accepted = accepted and expected.is_file()
                        if accepted and step!='audit':
                            photo = json.loads(expected.read_text())
                            accepted = photo.get('php_log',{}).get('checked') is True and photo['php_log']['errors']==0
                    if step=='comparaison':
                        comparison = json.loads(stdout)
                        checkpoint['comparison'] = {'attendu':sum(c['class']=='attendu' for c in comparison['changes']), 'anormal':comparison['anormal']}
                        accepted = code in [0,3] and comparison['anormal']==0 and all(c['class']=='attendu' for c in comparison['changes'])
                except (ValueError,KeyError,TypeError,OSError):
                    accepted = False
                save(receipt_path,row)
                if not accepted:
                    checkpoint['status']='ARRÊT : '+step+' (code '+str(code)+')'
                    persist()
                    return code if code not in [0,3] and code>0 else 1
                evidence = [receipt_path,state/(prefix+'-stdout.log'),state/(prefix+'-stderr.log')]
                if artifact:
                    evidence += [p for p in (state/artifact).rglob('*') if p.is_file()]
                checkpoint['done'][step] = {'artifact':artifact,'seals':{str(p.relative_to(state)):digest(p) for p in evidence}}
                persist()
            checkpoint['status']='TERMINÉ — réception sans anomalie'
            checkpoint['look_at']='rapport.md ; maintenance non pilotée par A08 ; aucun GO implicite'
            persist()
            return 0
    except (ValueError,KeyError,OSError,TypeError) as error:
        code = str(error) if re.fullmatch(r'A08_[A-Z_]+',str(error)) else 'A08_STATE_OR_PROOF_INVALID'
        print(code,file=sys.stderr)
        return 1


def commands(base, site, state, settings, update, clean, backup, go_update, go_clean, attempt):
    def mutate(tool, plan, checkpoint, go):
        value = ['python3', '-B', str(base/tool), '--wp-path='+str(site), '--plan='+str(plan),
                 '--backup='+str(backup), '--state='+str(state/checkpoint)]
        return value + (['--go='+str(go)] if go else [])

    def photo(name):
        return ['php', str(base/'non-regression'), '--wp-path='+str(site), '--config='+str(settings),
                '--output='+str(state/(name+'-'+str(attempt)))]

    return {
        'audit': ['php', str(base/'audit'), '--wp-path='+str(site), '--output='+str(state/('audit-'+str(attempt)))],
        'avant': photo('avant'),
        'mise-a-jour': mutate('mettre-a-jour', update, 'a04', go_update),
        'nettoyage': mutate('nettoyer', clean, 'a05', go_clean),
        'apres': photo('apres'),
        'comparaison': ['php', str(base/'comparer'), str(state/('avant-'+str(attempt))/'non-regression.json'),
                        str(state/('apres-'+str(attempt))/'non-regression.json')],
    }
