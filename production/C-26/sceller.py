"""Générer l'inventaire et le sceau C26, sans site/réseau ni réécriture des reçus."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import hashlib
import json
PROOF = Path(__file__).resolve().parent
ROOT = PROOF.parents[1]
sys.path.insert(0, str(ROOT/'wp/outils/demo'))
import c23


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seal(delivery='livraison-finale', mutations='mutations-livraison'):
    read = lambda n:json.loads((PROOF/n).read_text(encoding='utf-8'))
    f, record = read(delivery+'-inventaire.json'),read(delivery+'.json')
    coop = c23.cooperator_routes(f)
    text = '# C26 — Inventaire des sorties, une ligne chacune\n\n'
    text += 'Source : inventaire natif relu sur `imagine-test-demo` ; bootstrap courant comparé avant les essais. Aucun envoi, transport extérieur ou changement du code métier.\n\n'
    text += f"**{len(record['routes'])} sorties HTTP**, chacune jouée sur les **{len(record['publics'])} publics** : "+', '.join(record['publics'])+'.\n\n'
    text += 'Tous sont des tiers de V-DEC, propriétaire fictif des données C26. Abonné actif ou coopérateur ne donne aucun droit sur ses réponses, demandes et inscriptions. T = texte réservé d’un numéro non possédé ; D = donnée privée d’un autre compte. Les droits C14 sont respectés. Les surfaces publiques ne sont pas artificiellement classées privées : leur contenu doit exister sans embarquer T ou D.\n\n'
    text += 'Les pages publiques exigent le bon h1, les recherches publiques un vrai lien de résultat vers le bon objet, les collections l’ID attendu, le flux événementiel des entrées et liens d’événements, les oEmbed un objet riche au bon titre. Les refus REST sont des erreurs JSON natives ; les recherches privées ont le résultat vide natif attendu, la réflexion étant masquée seulement aux positions exactes.\n\n'
    text += '## Sorties nouvelles et surfaces communes réinspectées\n\nNom | Famille | Voie | Chemin GET exact | Risques / public\n---|---|---|---|---\n'
    for r in record['routes']:
        note = 'T + D ; 15 tiers'
        if r['kind']=='private-feed':
            note += ' ; repli natif articles publics, pas flux privé non vide'
        text += ' | '.join([r['name'],r['family'],r['kind'],'`'+r['path']+'`',note])+'\n'
    text += '\n## Privacy : vrais callbacks enregistrés, en lecture seule\n\nNom | Famille | Voie et registre natif | Risque / publics\n---|---|---|---\n'
    for family,key,cls in [('agenda','imagine-agenda','AgendaConfidentialite'),('personnalisation','imagine-personnalisation','PersonnalisationConfidentialite'),('retractation','imagine-retractation','RetractationConfidentialite'),('sujet','imagine-sujets','SujetConfidentialite')]:
        text += f'privacy-{family} | {family} | callback `{key}` → `{cls}::exporter()` | D ; 15 tiers + propriétaire positif\n'
    text += '\nPas de demande native ni d’archive/email généré. Les réponses privées ne sont pas conservées dans les reçus : seulement empreintes et verdicts. Aucun effaceur n’est exécuté par la matrice ; leurs pages administratives sont lues en GET et refusées. Les types privés n’ont pas de REST/oEmbed/flux privé natif : les URL risquées sont sondées sans inventer de surface privée. Les callbacks positifs prouvent que les données existent.\n\n'
    text += '## Pages coopérateurs maintenues dans C23 et soumises à relecture C26\n\nCes **35 voies sont déjà comprises dans les 136 voies / 1 922 contrôles C23** : ne pas les ajouter une seconde fois aux sorties nouvelles. Les 14 publics C23 sont ceux ci-dessus moins abonne-actif ; P-COOP est l’inverse autorisé, les 13 autres sont refusés. Risque : contenu de l’espace réservé, sans droit d’article. Aucun faux flux de pages n’est crédité.\n\nNom | Page | Voie | Chemin GET exact | Publics\n---|---|---|---|---\n'
    for r in coop:
        text += ' | '.join([r['name'],str(r['cooperator_page']),r['cooperator_kind'],'`'+r['path']+'`','13 refus + P-COOP inverse'])+'\n'
    text += '\nAutres voies historiques : `c23.build_routes()` inchangé et `livraison-finale-c23.md`. Plans de site fermés qualifiés comme fermés, pas comme collections ouvertes. Les six mutations sont qualifiées dans A-VOIR.md ; les anciennes mutations de corps en mémoire ne sont pas des parcours applicatifs mutés.\n'
    (PROOF/'INVENTAIRE.md').write_text(text,encoding='utf-8')
    sources = {p.relative_to(ROOT).as_posix():sha(p) for folder in ['wp/outils/demo','wp/tests/demo'] for p in (ROOT/folder).glob('c26*') if p.is_file()}
    sources['wp/tests/demo/c23-tests.py'] = sha(ROOT/'wp/tests/demo/c23-tests.py')
    artifacts = ['A-VOIR.md','INVENTAIRE.md','sceller.py','tests.json','tests-utf8.log','tests-cp1252.log','image.json','image.log']
    for label in [delivery,mutations]:
        artifacts += [label+s for s in ['.json','.md','.log','-avant.json','-restauration.json','-privacy.json','-inventaire.json','-extension.json','-c23.json','-c23.md']]
    artifacts += [mutations+'-mutation-'+family+'.json' for family in ['agenda','personnalisation','retractation','sujet','cooperateurs','cooperative']]
    manifest = {'scope':'imagine-test-demo','delivery':delivery,'mutations':mutations,'sources':sources,
                'artifacts':{n:sha(PROOF/n) for n in artifacts}}
    (PROOF/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'sources':len(sources),'artifacts':len(artifacts),'HTTP_routes':len(record['routes']),
                      'controls':record['total']+read(delivery+'-c23.json')['total']+read(delivery+'-privacy.json')['total']},ensure_ascii=False))


if __name__ == '__main__':
    seal(*sys.argv[1:])
