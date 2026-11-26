"""B06 : une recette complémentaire entière, reçus immuables et mutations négatives obligatoires."""
import sys
sys.dont_write_bytecode = True
import importlib.util, json, hashlib, subprocess, uuid
from pathlib import Path
import b06


def sources():
    paths = [b06.ROOT/'wp/plugins/imagine-site'/n for n in ['CooperateursRegles.php','Cooperateurs.php','README-B06.md']]
    for d in ['wp/outils/demo','wp/tests/demo']:
        paths += [p for p in (b06.ROOT/d).glob('b06*') if p.is_file()]
    return {p.relative_to(b06.ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))}


def rules(label):
    def docker(*args, check=True):
        p = subprocess.run(['wsl.exe','-d','Ubuntu','--','docker',*args],capture_output=True,text=True,encoding='utf-8')
        if check: assert p.returncode == 0, p.stderr
        return p
    name = 'imagine-b06-pure-' + uuid.uuid4().hex
    image = json.loads(docker('image','inspect','imagine-tests-t01:1').stdout)[0]
    assert image['Config']['Labels']['org.imagine.t01-image'] == '1'
    docker('create','--name',name,'--pull','never','--network','none','--read-only','--user','65534:65534',
           '--cap-drop','ALL','--security-opt','no-new-privileges','--mount',
           'type=bind,source=/mnt/c/Users/Ced/imagine/wp,target=/repo/wp,readonly','--entrypoint','php',image['Id'],'/repo/wp/tests/demo/b06-rules.php')
    try:
        info = json.loads(docker('inspect',name).stdout)[0]
        assert info['HostConfig']['NetworkMode']=='none' and info['HostConfig']['ReadonlyRootfs']
        assert len(info['Mounts'])==1 and not info['Mounts'][0]['RW']
        p = docker('start','-a',name,check=False)
        data = json.loads(p.stdout)
        data.update(exit=p.returncode,stderr=p.stderr,image=image['Id'])
    finally:
        docker('rm','-f',name)
        absent = docker('inspect',name,check=False)
        assert absent.returncode != 0 and 'no such' in absent.stderr.lower()
    data['container_removed'] = True
    b06.save(label,data)
    assert data['exit']==0 and not data['failures'] and not data['stderr']
    return data


def run(label):
    assert label.endswith('-V2') and not (b06.PROOF/(label+'.json')).exists()
    identity = b06.guard()
    prefix = label[:-3]
    recorded = sources()
    closed = b06.hashes(['plugins/imagine-site/Confidentialite.php','plugins/imagine-site/Paywall.php'])
    before = b06.state()
    stages = []
    def stage(name):
        value = prefix+'-'+name+'-V2'; stages.append(value); return value
    pure = rules(stage('rules'))
    for case in ['attribute','privacy','space']:
        b06.runtime(stage(case),case)
    mutations = {'page':('space','anonyme_page_sans_contenu'),
                 'rest':('space','anonyme_rest_sans_contenu'),
                 'search':('space','anonyme_recherche_exclut_espace'),
                 'feed':('space','anonyme_flux_exclut_espace'),
                 'sitemap':('space','sitemap_fournisseur_natif_espace_absent'),
                 'edition':('space','ecran_edition_non_coop_interdit'),
                 'erase_noop':('privacy','effacement_natif_attribut_absent'),
                 'export_other':('privacy','export_autre_personne_absente'),
                 'mail':('attribute','aucun_mail_tente'),
                 'http':('attribute','aucun_http_tente'),
                 'listener':('attribute','accroche_nommee_sans_ecouteur')}
    mutation_records=[]
    for mutation,(case,expected) in mutations.items():
        name = stage('mutation-'+mutation.replace('_','-'))
        try: b06.runtime(name,case,mutation)
        except AssertionError: pass
        r = json.loads((b06.PROOF/(name+'.json')).read_text(encoding='utf-8'))
        assert r['exit']==1 and expected in r['failures'] and r['state_preserved'] and not r['stderr'], (mutation,r['failures'])
        mutation_records.append({'receipt':name,'required_failure':expected})
    spec=importlib.util.spec_from_file_location('b06_http',Path(__file__).with_name('b06-http.py'))
    http=importlib.util.module_from_spec(spec);spec.loader.exec_module(http)
    http.run(stage('http'))
    assert sources()==recorded, 'Sources B06 modifiées pendant la recette'
    assert b06.hashes(list(closed))==closed, 'Bibliothèque close modifiée'
    normal=[json.loads((b06.PROOF/(n+'.json')).read_text(encoding='utf-8')) for n in stages if '-mutation-' not in n]
    assert all(not r['failures'] for r in normal)
    total=sum(r['total'] for r in normal)
    final={'identity':identity,'sources':recorded,'closed_sources':closed,
           'bootstrap_contract':b06.BLOCK in (b06.ROOT/'wp/plugins/imagine-site/imagine-site.php').read_text(encoding='utf-8'),
           'normal_receipts':[n for n in stages if '-mutation-' not in n],
           'mutation_receipts':mutation_records,'total':total,'failures':[],
           'mutation_count':len(mutation_records),'result':'VERIFIED','sources_remote':b06.hashes(b06.NAMES),
           'native_cases_restored':all(r.get('state_preserved',True) for r in normal),
           'exception':'P-COOP garde son attribut, posé et relu par écran natif ; autres comptes/options/actions restaurés exactement.'}
    b06.save(label,final)
    print(json.dumps({'result':'VERIFIED','normal_checks':total,'mutations_detected':len(mutation_records)},ensure_ascii=False))

if __name__=='__main__': run(sys.argv[1])
