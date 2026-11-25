"""C09 : vérification finale ciblée, rapports et PRET seulement après preuves réelles."""
from pathlib import Path

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


def native_test(name):
    source = TESTS / ('c09-' + name + '.php')
    target = 'imagine-demo-build/' + source.name
    data = source.read_bytes()
    profils.b00.upload(target, data)
    code = '$p=WP_CONTENT_DIR . "/' + target + '";token_get_all(file_get_contents($p),TOKEN_PARSE);echo hash_file("sha256",$p);'
    if profils.b00.wp('eval', code)['stdout'].strip() != hashlib.sha256(data).hexdigest():
        raise RuntimeError('Fichier cible différent : ' + target)
    raw = profils.b00.wp('eval', 'require WP_CONTENT_DIR . "/' + target + '";', check=False)
    if not raw['stdout'].strip():
        raise RuntimeError('Recette sans résultat : ' + name + ' : ' + raw['stderr'][-1500:])
    result = json.loads(raw['stdout'])
    save(name + '.json', result)
    if result['total'] != len(result['checks']) or raw['code'] or result['failures']:
        raise RuntimeError('Recette C09 échouée : ' + name)
    return result


def run():
    profils.guard('imagine-test-demo')
    PROOF.mkdir(parents=True, exist_ok=True)
    if (PROOF / 'PRET').exists():
        (PROOF / 'PRET').unlink()
    # Seuls les tests C09 : aucune découverte historique pouvant cibler d'autres sites.
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.discover(str(TESTS), pattern='test_c09_profils.py'))
    local = {'total': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors), 'skipped': len(result.skipped), 'output': stream.getvalue()}
    save('local-tests.json', local)
    if not result.wasSuccessful() or result.skipped:
        raise RuntimeError('Tests locaux C09 échoués')
    profils.run(label='installation')
    profils.run(label='relance')
    plan = native_test('plan')
    clock = native_test('clock')
    load('c09-reset').run()
    corrections = native_test('corrections')
    readback = profils.run(label='readback', readback_only=True)
    safety = native_test('safety')
    http = load('c09-http').run()
    original = json.loads((PROOF / 'installation.json').read_text(encoding='utf-8'))
    replay = json.loads((PROOF / 'relance.json').read_text(encoding='utf-8'))
    reset = json.loads((PROOF / 'reset-preuve.json').read_text(encoding='utf-8'))
    baseline = profils.preserve()
    # Pas de nouvelle lecture/empreinte des bibliothèques closes ni du thème.
    rows = profils.catalogue()
    native = readback['native']
    categories = {state: [r['code'] for r in rows if r['etat'] == state] for state in ['créé','partiel','impossible']}
    initial_b00 = ROOT / 'production/B-00/tests/b00-snapshot-initial.json'
    integrity = {
        'ids_identiques_installation_relance_reset_readback': original['native']['fixture'] == replay['native']['fixture'] == native['fixture'],
        'b00_c08_preserves_depuis_installation': original['before'] == baseline,
        'b00_snapshot_initial_conserve': baseline['snapshot_b00'] == json.loads(initial_b00.read_text(encoding='utf-8')),
        'inventaires_reconcilies_catalogue': {k: len(native['fixture'][k]) for k in ['users','orders','subscriptions','memberships','tariffs']} == {
            'users': sum(r['compte'] for r in rows), 'orders': sum('native' in r or bool(r.get('order_only')) for r in rows),
            'subscriptions': sum('native' in r for r in rows), 'memberships': sum('native' in r or 'membership' in r for r in rows), 'tariffs': 6},
        'totaux_natifs_reconcilies': native['total'] == len(native['checks']),
        'trente_profils_categorises': len(rows) == 30 and sum(map(len, categories.values())) == 30,
        'preuve_acces_27_comptes_et_2_scenarios': len(native['proof']) == 29,
        'aucun_echec_des_suites': all(not s['failures'] for s in [native, http, safety, reset, corrections, clock, plan, readback['c08_regression']]),
    }
    save('integrite.json', {'checks': integrity, 'total': len(integrity), 'failures': [k for k,v in integrity.items() if not v]})
    if not all(integrity.values()):
        raise RuntimeError('Intégrité ou conservation non démontrée')
    totals = {'unitaires': local['total'], 'natifs': native['total'], 'http': http['total'], 'securite': safety['total'],
              'reset': reset['total'], 'regression_c08': readback['c08_regression']['total'], 'integrite': len(integrity),
              'corrections': corrections['total'], 'horloge': clock['total'], 'plan': plan['total']}
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
        f"Objets C09 relus par les API natives : {counts['orders']} commandes, {counts['subscriptions']} souscriptions, {counts['memberships']} adhésions, un plan (ID {fixture['plan']}), un produit historique privé à zéro (ID {fixture['product']}) et six produits Subscription tarifaires FICTIFS privés et cachés.",
        'Classement strict uniforme (arbitrage 21h10) : « créé » exige tout l’état de départ disponible ; « partiel » signifie qu’au moins une composante manque, même si le compte fonctionne ; « impossible » signifie que le scénario ne peut être attesté. E-REDAC et V-INSCRIT sont donc partiels.',
        'Les montants de la grille sont exclusivement synthétiques, jamais des tarifs Imagine ni une règle de droit. Commandes non payées on-hold, sans transaction ni passerelle ; renouvellements manuels. Aucun débit, mandat ou paiement antérieur inventé.',
        'Calendrier de parution 2026–2028 complet : 15 parutions avec sortie et clôture. Cinq numéros de 2026 sont matérialisés avec articles/PDF ; les raccords métier C05/compteurs/listes restent distincts et absents.',
        '« Renouvellement activé » (A-CARTE/A-ECHEANCE) est non démontrable sur la démo hors ligne, explicitement accepté par l’arbitrage du 23/11/2026 à 21h10. Aucun drapeau de reconduction automatique sans moyen de paiement.',
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
        '4. **A-VIR** : motif arbitré `virement_non_valide`, corrigé dans C08/C10 et constaté par C09. Le mode de règlement reste vide sur la démo.',
        '5. **A-GRACE/A-SUSP/A-NONRENOUV/A-SANSMAIL** : distinguer fenêtre UTC de fixture d’une durée métier ; préciser le raccord des compteurs de numéros et de la liste postale. Le blocage global des emails ne prouve pas l’exclusion individuelle d’A-SANSMAIL.',
        '6. **A-ETRANGER** : préciser pays, barème et supplément avant d’affirmer « supplément appliqué ». La ligne de port à zéro actuelle n’est pas un vrai supplément.',
        '7. **P-OFFRANT/P-OFFERT/P-GEST/P-BENEF** : préciser les objets/relations du module offert et de Teams, leurs propriétaires et bénéficiaires. Aucun droit indépendant substitutif n’est accordé en attendant ces raccords.',
        '8. **P-PRO** : remplacer « numéro valide » par « cohérence locale » ou « existence BCE attestée » selon la preuve voulue. 0000000097 est uniquement une entrée synthétique cohérente, pas une entreprise attestée ni un attribut de compte raccordé.',
        '9. **P-SOL-ATT/P-SOL-OK** : préciser dépôt, décision, tarif et durée de validité du justificatif séparément de la fin d’adhésion. Une adhésion native de démonstration ne remplace pas une validation de justificatif.',
        '10. **P-NUMERO/P-COOP** : définir la preuve d’achat et le rattachement après achat, puis les adaptateurs achat/CoopHub. La commande en attente n’est pas un achat acquis ; aucun attribut coopérateur non raccordé n’est maquillé en droit.',
        '11. **E-ABO** : rôle dédié Référent abonnements installé, matrice §3.13 limitée et lecture équipe prouvée. Les capacités dédiées réservent les futurs écrans métier, elles ne prouvent pas que ces écrans existent. Aucun droit éditorial, manage_woocommerce, manage_options, gestion générale des utilisateurs ou suppression de commandes. E-REDAC reste partiel : calendrier consultable, pas d’écran d’édition pour editor ; la capacité réelle de sauvegarde native manage_options est refusée et testée.',
        '12. **Données communes** : calendrier 2026–2028 complet (15 parutions avec sortie/clôture), cinq numéros de 2026 matérialisés avec articles/PDF, six tarifs natifs FICTIFS complets. Les raccords métier C05/compteurs/listes restent absents. Aucune grille commerciale validée ni compteur inventé.', '',
        '## Six combinaisons natives entièrement fictives', '',
        '| Combinaison | ID produit | EUR synthétiques par échéance | Période / intervalle / durée |',
        '|---|---|---|---|',
        *[f"| {key} | {p['id']} | {p['price']} | {p['period']} / {p['interval']} / {p['length']} |" for key,p in corrections['tariffs'].items()], '',
        'Raccords natifs commande/souscription/produit de l’adhésion : A-CARTE et A-PAYPAL → normal-1 ; A-SEPA4 et A-PAPIER → normal-4. Pour A-PAPIER, quatre fois est un choix de fixture, pas une règle de domiciliation. Variantes solidaire/soutien préparées sans justificatif ni nouveau droit. Quatre fois signifie périodicité trimestrielle sur douze mois, pas preuve de deux échéances payées.', '',
        'Matrice persistante exacte du rôle `imagine_referent_abonnements` (Référent abonnements) : ' + ', '.join('`' + k + '`' for k in corrections['role_capabilities']) + '.', '',
        '## Preuves et rejeu', '',
        '- `installation.json`, `relance.json`, `reset.json` et `readback.json` : contrôles de la dernière recette complète après les sources finales. Les ID principaux restent identiques.',
        '- `readback.json` : objets natifs et décisions nominatives ; `http.json` : 27 connexions, témoin de contenu et blocs ; E-ABO ouvre les écrans natifs liste/création de commande (200), mais pas éditorial/réglages (403). E-REDAC ne peut ouvrir le parcours natif de réglages (403). Aucun cookie/nonce/mot de passe enregistré.',
        '- `red-runtime.json`, `red-safety.json`, `red-reset.json` : échecs réellement observés avant installation/correction ou après altérations ; `reset-preuve.json` : restauration après altérations et ajout de doublons possédés.',
        '- `corrections.json` : six tarifs et raccords natifs, classement strict, capacité réelle E-REDAC, matrice E-ABO, lecture équipe et motif A-VIR indépendants du catalogue.',
        '- `clock.json` : générateur réellement exécuté aux 30/11/2026 23:59:59, 31/12/2026 23:59:59 et 01/01/2027 00:00:00 UTC ; échéance dans le mois, puis restauration à l’horloge réelle relue.',
        '- `plan.json` : plan altéré par API Memberships, restauré par la même API avec décision d’accès et nettoyage relus. `reset-preuve.json` exerce également cette altération dans la recette de reset complète.',
        '- `safety.json` : chargement et filtres MU vérifiés passivement ; fichier présent/filtres morts refusés, sentinelles de transport non appelées. Aucun envoi ou requête pour prouver leur interdiction.',
        '- `integrite.json`, `local-tests.json` et `verification-finale.json` : décomptes réconciliés par code. Les red-* sont des échecs attendus de développement, pas la recette finale.', '',
        '```bash', 'python -B -m unittest discover -s wp/tests/demo -p test_c09_profils.py -v',
        'python -B wp/outils/demo/profils.py --site imagine-test-demo',
        'python wp/outils/demo/profils.py --preuve readback --readback-only',
        'python -B wp/tests/demo/c09-verifier.py', '```', '',
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
- B00 conservé par comparaison exacte avec son snapshot initial ; trois comptes C08, abonnements, adhésions, articles et manifestes conservés. Aucune nouvelle collecte d’empreintes des bibliothèques closes ou du thème.

## Limites et incidents résolus

- Le dossier littéral « C:\\Users\\Ced\\imagine voie2 » n’existe pas. La consigne permanente définit voie 2 dans C:\\Users\\Ced\\imagine ; aucune lecture de la file voie 1.
- Les échecs de garde passive, de plan et de grille/rôle/classement ont été observés avant leur correction. Les tests de transports utilisent des sentinelles qui interdisent l’acte même sur le code fautif : aucun transport réel déclenché.
- Les prix synthétiques ont été relus avec leurs types PHP ; les assertions comparent explicitement des float. Aucun objet inventé pour adapter les nombres aux tests.
- Lecture et création administrative de commande réellement ouvertes pour E-ABO (HTTP 200) ; éditorial/réglages refusés (403). E-REDAC est également refusé par le parcours natif de réglages (403), en plus du contrôle de sa capacité réelle.

Une première recette PHP incluait le seed dans sa portée et son $id local a été écrasé : le numéro fictif B00 ID32 a subi une mutation transitoire. Restauration ciblée immédiate, snapshot B00 relu exactement égal au snapshot initial ; seed désormais isolé dans une fermeture dans les tests plan/horloge. Aucun compte ni donnée réel. Incident signalé, pas masqué par un reseed général.

Le calendrier trois ans et les six produits tarifaires fictifs sont complets ; cinq numéros sont matérialisés, raccords métier toujours distincts. E-REDAC partiel, E-ABO rôle dédié sans éditorial et lecture équipe ; renouvellement activé explicitement non démontrable accepté à 21h10. Inventaire C10 27/13/12/14 inchangé ; six produits ajoutés, pas six commandes. Aucun cron ajouté, aucun C10/Paywall.php, verrou ou rapport central modifié. Voir A-VOIR.md, corrections.json, clock.json, plan.json, safety.json et readback.json.
'''
    (PROOF / 'RAPPORT.md').write_text(report, encoding='utf-8')

    secret = secret_scan()
    final = {'status': 'PRET' if not secret['matches'] else 'FAILED', 'scope': 'imagine-test-demo',
             'at': datetime.now(timezone.utc).isoformat(), 'categories': categories, 'counts': counts, 'totals': totals,
             'total_checks': all_assertions, 'table_rows': table_count, 'decision_count': len(native['proof']),
             'secret_scan': secret, 'tariff_count': len(fixture['tariffs']), 'limitations_accepted_by_brief': True,
             'b00_c08_preserved': True}
    save('verification-finale.json', final)
    if secret['matches']:
        raise RuntimeError('Une valeur privée est présente dans les fichiers C09')
    (PROOF / 'PRET').write_text('C09 — PRET pour relecture du brief, partiels/impossible explicités.\n30 profils : ' +
        ', '.join(f'{len(v)} {k}' for k,v in categories.items()) + f'.\n27 comptes natifs ; {all_assertions} contrôles/tests de dernière passe réussis, zéro échec.\nVoir A-VOIR.md, RAPPORT.md et verification-finale.json.\n', encoding='utf-8')
    print(json.dumps({k:final[k] for k in ['status','categories','counts','totals','total_checks','table_rows','decision_count','secret_scan']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    # Le complément remplace les anciennes attentes « aucun paiement » ; conserver
    # les anciens reçus et ne jamais régénérer leur prose comme un résultat actuel.
    load('c09-complement').run_final()
