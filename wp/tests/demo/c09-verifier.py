"""C09 : vérification finale ciblée, rapports et PRET seulement après preuves réelles."""
from pathlib import Path
import collections
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import profils

ROOT = profils.b00.ROOT
PROOF = ROOT / 'production/C-09'
TESTS = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), TESTS / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save(name, data):
    (PROOF / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def secret_scan():
    base = json.loads((Path.home() / '.imagine-demo/identifiants.json').read_text(encoding='utf-8'))
    extra = json.loads((Path.home() / '.imagine-demo/c08-identifiants.json').read_text(encoding='utf-8'))
    tokens = []
    def collect(value, key=''):
        if isinstance(value, dict):
            for k,v in value.items():
                collect(v, k)
        elif isinstance(value, str) and 'password' in key and len(value) >= 16:
            tokens.append(value.encode())
    collect(base)
    collect(extra)
    paths = list(PROOF.rglob('*')) + [ROOT / 'wp/outils/demo/profils.py'] + list((ROOT / 'wp/outils/demo').glob('c09-*')) + list(TESTS.glob('*c09*'))
    matches = []
    checked = 0
    for path in paths:
        if path.is_file() and path.suffix != '.pyc':
            checked += 1
            if any(token in path.read_bytes() for token in tokens):
                matches.append(path.relative_to(ROOT).as_posix())
    return {'files_checked': checked, 'matches': matches}


def run():
    profils.guard('imagine-test-demo')
    PROOF.mkdir(parents=True, exist_ok=True)
    # Seuls les tests C09 : aucune découverte historique pouvant cibler d'autres sites.
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.discover(str(TESTS), pattern='test_c09_profils.py'))
    local = {'total': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors), 'output': stream.getvalue()}
    save('local-tests.json', local)
    if not result.wasSuccessful():
        raise RuntimeError('Tests locaux C09 échoués')
    profils.run(label='relance')
    load('c09-reset').run()
    readback = profils.run(label='readback', readback_only=True)
    safety_source = TESTS / 'c09-safety.php'
    profils.b00.upload('imagine-demo-build/c09-safety.php', safety_source.read_bytes())
    safety_raw = profils.b00.wp('eval', 'token_get_all(file_get_contents(WP_CONTENT_DIR . "/imagine-demo-build/c09-safety.php"),TOKEN_PARSE);require WP_CONTENT_DIR . "/imagine-demo-build/c09-safety.php";', check=False)
    safety = json.loads(safety_raw['stdout'])
    save('safety.json', safety)
    if safety_raw['code']:
        raise RuntimeError('Garde native C09 échouée')
    http = load('c09-http').run()
    original = json.loads((PROOF / 'installation.json').read_text(encoding='utf-8'))
    replay = json.loads((PROOF / 'relance.json').read_text(encoding='utf-8'))
    reset = json.loads((PROOF / 'reset-preuve.json').read_text(encoding='utf-8'))
    baseline = profils.preserve()
    source_hashes = {}
    for directory in ['wp/plugins/imagine-pilotage/src', 'wp/plugins/imagine-connecteur/src', 'wp/themes/imagine']:
        for source in (ROOT / directory).rglob('*'):
            if source.is_file() and source.suffix in ['.php', '.css', '.js', '.json', '.svg', '.png']:
                source_hashes[source.relative_to(ROOT / 'wp').as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
    code = '$names=json_decode(' + json.dumps(json.dumps(list(source_hashes))) + ',true);$out=[];foreach($names as $name){$path=WP_CONTENT_DIR . "/" . $name;$out[$name]=is_file($path)?hash_file("sha256",$path):null;}echo wp_json_encode($out);'
    deployed = json.loads(profils.b00.wp('eval', code)['stdout'])
    safety_hash = profils.b00.wp('eval', 'echo hash_file("sha256",WP_CONTENT_DIR . "/imagine-demo-build/c09-safety.php");')['stdout'].strip()
    rows = profils.catalogue()
    native = readback['native']
    categories = {state: [r['code'] for r in rows if r['etat'] == state] for state in ['créé','partiel','impossible']}
    initial_b00 = ROOT / 'production/B-00/tests/b00-snapshot-initial.json'
    integrity = {
        'ids_identiques_installation_relance_reset_readback': original['native']['fixture'] == replay['native']['fixture'] == native['fixture'],
        'b00_c08_preserves_depuis_installation': original['before'] == baseline,
        'b00_snapshot_initial_conserve': baseline['snapshot_b00'] == json.loads(initial_b00.read_text(encoding='utf-8')),
        'sources_closes_theme_egales_aux_fichiers_deployes': source_hashes == deployed,
        'safety_octets_exactement_relus': safety_hash == hashlib.sha256(safety_source.read_bytes()).hexdigest(),
        'trente_profils_categorises': len(rows) == 30 and sum(map(len, categories.values())) == 30,
        'preuve_acces_27_comptes_et_2_scenarios': len(native['proof']) == 29,
        'aucun_echec_des_suites': not native['failures'] and not http['failures'] and not safety['failures'] and not reset['failures'] and not readback['c08_regression']['failures'],
    }
    save('integrite.json', {'checks': integrity, 'total': len(integrity), 'failures': [k for k,v in integrity.items() if not v],
                            'source_file_count': len(source_hashes), 'source_sha256': source_hashes, 'deployed_sha256': deployed})
    if not all(integrity.values()):
        raise RuntimeError('Intégrité ou conservation non démontrée')
    totals = {'unitaires': local['total'], 'natifs': native['total'], 'http': http['total'], 'securite': safety['total'],
              'reset': reset['total'], 'regression_c08': readback['c08_regression']['total'], 'integrite': len(integrity)}
    fixture = native['fixture']
    counts = {k:len(fixture[k]) for k in ['users','orders','subscriptions','memberships']}
    lines = ['# C09 — À voir sur la démonstration fictive', '',
        '## Ouvrir', '',
        '- Connexion : http://192.168.129.32:8085/wp-login.php',
        '- Article réservé testé : http://192.168.129.32:8085/c08-article-reserve-article/ (ID 81).',
        '- Administration : http://192.168.129.32:8085/wp-admin/ ; utilisateurs, commandes, abonnements et adhésions selon le rôle.',
        '- Mots de passe : `C:\\Users\\Ced\\.imagine-demo\\identifiants.json`, entrée `c09_accounts`. Rien de secret dans le dépôt.', '',
        '## Lecture des résultats', '',
        f"30 profils : {len(categories['créé'])} créés, {len(categories['partiel'])} partiels, {len(categories['impossible'])} impossible. **27 vrais comptes**, et non 30 : V-ANON, V-FAUX et V-ROBOT sont des scénarios de visite.",
        f"Objets C09 relus par les API natives : {counts['orders']} commandes, {counts['subscriptions']} souscriptions, {counts['memberships']} adhésions, un plan (ID {fixture['plan']}) et un produit Subscription privé à zéro (ID {fixture['product']}).",
        '« Créé » signifie état de départ entièrement disponible ; « partiel » signifie compte et objets possibles créés, mais éléments manquants détaillés ci-dessous. Toutes les commandes sont non payées, à zéro, sans transaction et sans passerelle ; tous les renouvellements sont manuels. Cela ne démontre aucun débit ni paiement passé.',
        'Les motifs ci-dessous proviennent du vrai `Imagine\\Site\\Paywall::decision` C08/C06, après lecture native Memberships/Subscriptions. 29 décisions relues et 27 connexions C09 réellement réalisées. V-ROBOT n’a pas de preuve positive inventée.', '',
        '| Profil | État | Identifiant / ID | Objets natifs (C/S/M) | Ce qu’on voit | Décision réelle sur ID81 | Limite précise |',
        '|---|---|---|---|---|---|---|']
    for row in rows:
        key = row['code']
        account = f"`{row['login']}` / {fixture['users'][key]}" if row['compte'] else 'Sans compte'
        objects = '/'.join(str(fixture[group].get(key,'—')) for group in ['orders','subscriptions','memberships'])
        decision = native['proof'].get(key, {}).get('decision')
        named = f"`{decision['motif']}` ; {'complet' if decision['complet'] else 'fermé'} ; bloc `{decision['bloc']}`" if decision else 'Non testable : robot vérifié indisponible'
        lines.append(f"| {key} | {row['etat']} | {account} | {objects} | {row['vue']} | {named} | {row['limite']} |")
    lines += ['', '## Profils et documentation à préciser — propositions seulement', '',
        'Aucun fichier de `docs/` n’a été modifié.', '',
        '1. **V-ANON/V-ROBOT/V-FAUX** : distinguer explicitement scénarios de requête et comptes. Définir la preuve DNS/IP pour V-ROBOT ; hors ligne, il reste impossible, jamais remplacé par une UA ou une IP déclarée.',
        '2. **V-DEC/V-DEC-FIN/V-INSCRIT** : préciser la preuve de vérification email, la forme de découverte choisie, ses dates/compteurs et le raccord natif. Un compte WordPress utilisable ne prouve pas un email vérifié.',
        '3. **A-CARTE/A-SEPA4/A-PAYPAL/A-PAPIER/A-ECHEANCE** : séparer l’état de lecture démontrable des mandats/accords et paiements réellement prouvés. Aucun 2/4 payé ni accord PayPal ne doit être déclaré ici ; les prochaines actions natives manuelles sont vérifiées. A-ECHEANCE a son terme à J+30 et une action à J+29 car WCS exige le prochain paiement avant la fin.',
        '4. **A-VIR** : définir le motif attendu pour pending Subscriptions ; C08 renvoie actuellement suspendu malgré adhésion pending. Ne pas le présenter comme virement_non_valide. Le mode de règlement reste vide sur la démo.',
        '5. **A-GRACE/A-SUSP/A-NONRENOUV/A-SANSMAIL** : distinguer fenêtre UTC de fixture d’une durée métier ; préciser le raccord des compteurs de numéros et de la liste postale. Le blocage global des emails ne prouve pas l’exclusion individuelle d’A-SANSMAIL.',
        '6. **A-ETRANGER** : préciser pays, barème et supplément avant d’affirmer « supplément appliqué ». La ligne de port à zéro actuelle n’est pas un vrai supplément.',
        '7. **P-OFFRANT/P-OFFERT/P-GEST/P-BENEF** : préciser les objets/relations du module offert et de Teams, leurs propriétaires et bénéficiaires. Aucun droit indépendant substitutif n’est accordé en attendant ces raccords.',
        '8. **P-PRO** : remplacer « numéro valide » par « cohérence locale » ou « existence BCE attestée » selon la preuve voulue. 0000000097 est uniquement une entrée synthétique cohérente, pas une entreprise attestée ni un attribut de compte raccordé.',
        '9. **P-SOL-ATT/P-SOL-OK** : préciser dépôt, décision, tarif et durée de validité du justificatif séparément de la fin d’adhésion. Une adhésion native de démonstration ne remplace pas une validation de justificatif.',
        '10. **P-NUMERO/P-COOP** : définir la preuve d’achat et le rattachement après achat, puis les adaptateurs achat/CoopHub. La commande en attente n’est pas un achat acquis ; aucun attribut coopérateur non raccordé n’est maquillé en droit.',
        '11. **E-ABO** : définir un rôle administratif dédié et sa matrice de capacités. Le rôle Woo shop_manager actuel est partiel et plus large (capacités éditoriales natives) ; C08 ne le considère pas comme équipe de lecture. Ne pas le réutiliser tel quel en production.',
        '12. **Données communes** : B00 fournit cinq numéros de 2026 avec articles et PDF ; ni le calendrier sur trois ans ni la grille native trois tarifs × une/quatre fois ne sont complets. Le produit C09 à zéro est une fixture privée, pas une grille commerciale validée. Ces limites n’ont pas été masquées par des montants ou des compteurs inventés.', '',
        '## Preuves et rejeu', '',
        '- `installation.json` : première installation réelle historique ; `relance.json`, `reset.json` et `readback.json` : contrôles après les sources finales. Les ID principaux restent identiques.',
        '- `readback.json` : objets natifs et décisions nominatives ; `http.json` : connexions, témoin de contenu et blocs, sans cookie/nonce/mot de passe enregistré.',
        '- `red-runtime.json`, `red-safety.json`, `red-reset.json` : échecs réellement observés avant installation/correction ou après altérations ; `reset-preuve.json` : restauration après altérations et ajout de doublons possédés.',
        '- `safety.json`, `integrite.json`, `references.md`, `local-tests.json` et `verification-finale.json`.', '',
        '```bash', 'python wp/outils/demo/profils.py --site imagine-test-demo',
        'python wp/outils/demo/profils.py --preuve readback --readback-only',
        'python wp/tests/demo/c09-verifier.py', '```', '',
        'Le vérificateur complet altère intentionnellement uniquement les comptes C09 avant de les restaurer ; il ne faut pas l’exécuter pendant une lecture manuelle de ces comptes. Les sessions C09 sont révoquées à chaque reset. Aucun autre site, création/arrêt de site, Git, verrou ou rapport global n’est touché. Si un objet est étranger à C09, le script refuse de l’écraser.']
    (PROOF / 'A-VOIR.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    table_count = sum(1 for line in lines if any(line.startswith('| ' + row['code'] + ' |') for row in rows))
    if table_count != 30:
        raise RuntimeError('Le tableau ne couvre pas les 30 profils')
    # Supprimer uniquement les captures textuelles officielles de ce lot après lecture ; extraits et reçus restent.
    for i in range(6):
        capture = PROOF / 'references' / (str(i) + '.txt')
        if capture.is_file():
            capture.unlink()
    all_assertions = sum(totals.values())
    report = f'''# C09 — Rapport final

- **Fait** : script rejouable installé sur imagine-test-demo ; 27 comptes natifs, {counts['orders']} commandes non payées, {counts['subscriptions']} souscriptions manuelles et {counts['memberships']} adhésions, sans transaction/passerelle/email sortant.
- **Prêt à relire** : C09, avec les partiels/impossibles explicitement admis par le brief ; ce n’est pas une validation métier ni une démonstration de paiements.
- **À arbitrer** : aucun choix financier ou droit réel inventé ; propositions de précision et raccords manquants dans A-VOIR.md, sans modifier docs.
- **Bloqué partiellement** : robot vérifié impossible hors ligne ; découverte/validation email, paiements/mandats/accords, compteurs, listes d’envoi, offert/groupé/solidaire/achat/coopérateur non entièrement raccordés.
- **Périmètre** : seulement fichiers C09/profils sous wp/outils/demo, wp/tests/demo et production/C-09. Aucun hook, thème, bibliothèque close, Git, verrou, rapport global ou autre site modifié.

## Catégories

''' + '\n'.join(f"- **{state} ({len(codes)})** : {', '.join(codes)}." for state,codes in categories.items()) + f'''

Les trois V-ANON/V-FAUX/V-ROBOT ne sont pas des comptes. Les 27 comptes existants sont tous testés par authentification et par la décision native ; deux scénarios sans compte complètent les 29 décisions. V-ROBOT n’a aucune preuve positive inventée.

## Résultats après les sources finales

''' + '\n'.join(f'- {key} : **{number}/{number}**.' for key,number in totals.items()) + f'''
- Total de la dernière passe, sans compter les répétitions : **{all_assertions} contrôles/tests réussis, 0 échec** ({local['total']} tests unittest et assertions de recettes pour les autres catégories).
- Installation, relance, altérations puis reset réel : ID principaux inchangés. Les altérations sont bien détectées avant restauration ; doublons natifs possédés supprimés, objet supplémentaire sur V-INSCRIT retiré.
- B00 conservé par comparaison avec le snapshot initial ; trois comptes C08, abonnements, adhésions, articles et manifestes conservés. Les fichiers PHP des bibliothèques closes et le thème installé correspondent aux sources ({len(source_hashes)} fichiers vérifiés).

## Limites et incidents résolus

- Le dossier littéral « C:\\Users\\Ced\\imagine voie2 » n’existe pas. La consigne permanente définit voie 2 dans C:\\Users\\Ced\\imagine ; aucune lecture de la file voie 1.
- L’extracteur officiel était indisponible (backend search-only). Les six pages officielles ont été récupérées par HTTP 200 et leurs passages ciblés lus avant l’implémentation native.
- Premier état expiré refusé par WCS : son alias historique last_payment reflétait la création de commande, même sans paiement. Dates administratives de création de fixture remises avant le terme ; aucune date_paid ni transaction ajoutée.
- Une première recette de reset a révélé un objet possédé supplémentaire sur un profil sans commande attendue : suppression ciblée ajoutée et vérifiée. Un test natif a aussi révélé l’absence de garde URL directe PHP : corrigée avant le feu vert.
- Les inventaires natifs utilisent les statuts explicites propres à Subscriptions (les statuts Woo par défaut omettaient les actifs) et le type natif string de billing_interval est interprété comme entier. Aucun objet n’a été inventé pour adapter les nombres aux tests.

Voir A-VOIR.md pour la vue profil par profil et readback.json/http.json pour les preuves nominatives. Le calendrier trois ans et la grille trois tarifs × une/quatre fois sont explicitement incomplets ; le zéro de fixture n’est pas un prix réel.
'''
    (PROOF / 'RAPPORT.md').write_text(report, encoding='utf-8')
    sources = [ROOT / 'wp/outils/demo/profils.py'] + list((ROOT / 'wp/outils/demo').glob('c09-*')) + list(TESTS.glob('*c09*'))
    source_receipt = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.is_file()}
    secret = secret_scan()
    final = {'status': 'PRET' if not secret['matches'] else 'FAILED', 'scope': 'imagine-test-demo',
             'at': datetime.now(timezone.utc).isoformat(), 'categories': categories, 'counts': counts, 'totals': totals,
             'total_checks': all_assertions, 'table_rows': table_count, 'decision_count': len(native['proof']),
             'secret_scan': secret, 'source_sha256': source_receipt, 'limitations_accepted_by_brief': True,
             'closed_libraries_and_theme_unchanged': True, 'b00_c08_preserved': True}
    save('verification-finale.json', final)
    if secret['matches']:
        raise RuntimeError('Une valeur privée est présente dans les fichiers C09')
    (PROOF / 'PRET').write_text('C09 — PRET pour relecture du brief, partiels/impossible explicités.\n30 profils : ' +
        ', '.join(f'{len(v)} {k}' for k,v in categories.items()) + f'.\n27 comptes natifs ; {all_assertions} contrôles/tests de dernière passe réussis, zéro échec.\nVoir A-VOIR.md, RAPPORT.md et verification-finale.json.\n', encoding='utf-8')
    print(json.dumps({k:final[k] for k in ['status','categories','counts','totals','total_checks','table_rows','decision_count','secret_scan']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    run()
