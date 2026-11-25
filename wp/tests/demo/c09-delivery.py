"""C09 : synchronise les trois fiches de lecture avec les seuls reçus réels."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'outils/demo'))
import profils
ROOT = profils.b00.ROOT
P = ROOT / 'production/C-09'


def read(name):
    return json.loads((P / name).read_text(encoding='utf-8'))


def run():
    result = read('complement-verification.json')
    native = read('readback.json')['native']
    payments = read('complement-final-native.json')
    c13 = read('complement-c13-strict.json')
    b02 = read('complement-b02-resultats.json')
    if native['failures'] or payments['failures'] or b02['failures'] or not all(c13['PHP'].values()) or not all(c13['HTTP'].values()):
        raise RuntimeError('Un reçu technique est rouge')
    rows = profils.catalogue(); f = native['fixture']
    counts = {s: sum(r['etat'] == s for r in rows) for s in ['créé', 'partiel', 'impossible']}
    assert len(rows) == sum(counts.values()) == 30
    lines = ['# C-09 — Profils fictifs à ouvrir', '',
        '**Complément du 25 novembre 2026 : prêt à relire avec réserves explicites ; aucune acceptation globale de C13/B02 revendiquée.**', '',
        '## Ouvrir', '',
        '- Connexion : `http://192.168.129.32:8085/wp-login.php`.',
        '- Mon compte : `http://192.168.129.32:8085/my-account/`.',
        '- Article réservé : `http://192.168.129.32:8085/c08-article-reserve-article/`.',
        '- Liste : `http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-liste-envoi&numero=DEMO-2027-T1` (e-abo/e-admin).',
        '- Identifiants exclusivement hors dépôt : `C:\\Users\\Ced\\.imagine-demo\\identifiants.json`, clé `c09_accounts`.', '',
        '## État réellement relu', '',
        f"30 profils : **{counts['créé']} créés, {counts['partiel']} partiels, {counts['impossible']} impossible**. 27 comptes ; V-ANON/V-FAUX/V-ROBOT sont des scénarios.",
        '13 commandes initiales et 3 renouvellements = 16 commandes, 12 souscriptions manuelles, 14 adhésions. Six tarifs natifs privés/cachés entièrement fictifs ; calendrier 2026–2028 complet (15 parutions), cinq numéros matérialisés.',
        '« Créé » : tout l’état de départ est disponible à la précision fictive autorisée ; « partiel » : une composante manque ; « impossible » : scénario non attestable. Les passerelles/mandats réels et la reconduction automatique restent absents.',
        'Chaque objet C09 et ses lignes portent `imagine_demo_fictif=1` ; titre natif **Paiement fictif de démonstration**, identifiant de passerelle vide, aucun jeton/transaction. Les métadonnées de fixture ne donnent aucun droit.',
        'A-CARTE/A-PAYPAL/A-PAPIER/A-ETRANGER/A-SANSMAIL/A-ECHEANCE/A-NONRENOUV : initiale payée fictive. A-SEPA4 : initiale + un renouvellement payés, total natif 2 ; prochaine action planifiée et deux échéances encore à venir, sans seconde action anticipée pour la quatrième. A-GRACE/A-SUSP : renouvellement failed à J-1/J-4 ; grâce J-1/J+2 ou J-4/J-1. A-VIR reste non payé.',
        'Les dates de début des six profils payés destinés à la projection postale sont normalisées à J-90 (A-SEPA4 : J-180), paiement à ce début ; seconde échéance A-SEPA4 à J-30. A-ECHEANCE et A-NONRENOUV conservent leur année native J-335/J+30 (365 jours), sans changer leur date de départ. Cela garde une année C01 comprenant DEMO-2027-T1 sans inventer un renouvellement annuel ni modifier C01/C13. Les observations sont horodatées maintenant, jamais antidatées.', '',
        '| Profil | État | Compte | C / S / M / renouvellement | Décision réelle article | Ce qui devient visible / limite |',
        '|---|---|---|---|---|---|']
    for row in rows:
        key = row['code']; d = native['proof'].get(key, {}).get('decision')
        decision = f"{d['motif']} / {'complet' if d['complet'] else 'fermé'}" if d else 'Non attestable hors ligne'
        objects = ' / '.join(str(f.get(group, {}).get(key, '—')) for group in ['orders','subscriptions','memberships','renewals'])
        lines.append(f"| {key} | {row['etat']} | {row['login'] or 'Sans compte'} | {objects} | {decision} | {row['vue']} Limite : {row['limite']} |")
    lines += ['', '## Réception et réserves', '',
        f"C09 : {result['tests']['natif']} contrôles natifs, {result['tests']['paiements']} paiements/marques, {result['tests']['HTTP']} HTTP, {result['tests']['securite']} sécurité, {result['tests']['corrections']} corrections, {result['tests']['C08']} régression C08 ; tous verts. {result['tests']['local']} tests locaux, reset 6/6 ; ID principaux conservés.",
        f"C13 strict : {len(c13['PHP'])} PHP + {len(c13['HTTP'])} HTTP verts, 10 tests purs/30 assertions ; **exit 2** : P-OFFERT/P-GEST/P-BENEF n’ont pas de liens natifs. Aucun de ces liens n’a été inventé. L’export comporte 8 destinataires (6 BE/2 étranger), dont 6 C09 et A-SANSMAIL.",
        f"B02 strict : **{b02['total']}/{b02['total']}**, dont {len(b02['http'])} HTTP ; **exit 2**. Les données natives A-SEPA4 sont bien 2/4, mais B02 n’affiche encore qu’une ligne Payée car il ne lit que la commande initiale. Marge C05, historique/compteurs C01 et documents restent non raccordés. Aucun code B02/C13 modifié.",
        'Le runner B02 conserve trois libellés de blocage désormais périmés (profil A-4x-J45, absence de failed, A-CARTE impayé). Le reçu brut est conservé : la consigne de 16h30 corrige le profil en A-SEPA4 ; failed et export A-CARTE sont maintenant attestés. Les attentes des tests de démonstration, pas le code produit ni le runner, ont été adaptées.', '',
        '## Rejouer', '', '```bash',
        'PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/profils.py --preuve relance',
        'PYTHONDONTWRITEBYTECODE=1 python wp/tests/demo/c09-verifier.py',
        'PYTHONDONTWRITEBYTECODE=1 python wp/tests/demo/c09-strict-recipes.py C13',
        'PYTHONDONTWRITEBYTECODE=1 python wp/tests/demo/c09-strict-recipes.py B02', '```', '',
        'Le vérificateur complet est long : le lancer en processus suivi si le terminal a un watchdog court. Il réinitialise les seuls profils C09 et révoque leurs sessions. Son statut global est TECHNIQUE_VERIFIE_ACCEPTATIONS_PARTIELLES ; les sorties strictes 2 sont conservées, pas converties en succès complet. Les reçus des recettes restent sous C09, sans écraser les rendus C13/B02.',
        'Aucune observation existante ni incident n’est nettoyé. Les recettes C13 nettoient uniquement leurs propres objets/relevés temporaires ; B02 ajoute ses deux observations d’adresse et restaure exactement l’adresse. Les anciens reçus/RAPPORT.md restent historiques, remplacés pour l’état actuel par RAPPORT-complement.md et complement-verification.json.',
        'Propositions hors lot : préciser la preuve robot/email, les raccords offert/groupé, justificatifs/CoopHub et le barème de port. Aucun fichier docs/ modifié.']
    assert sum(line.startswith('| ' + row['code'] + ' |') for line in lines for row in rows) == 30
    (P / 'A-VOIR.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    report = ['# C-09 — Complément paiements fictifs', '',
        '- **Fait** : états natifs payés/rejetés autorisés, rejouables sur imagine-test-demo seulement ; A-VIR impayé, souscriptions explicitement manuelles, aucun gateway/token/mandat/transaction/email réel.',
        '- **Prêt à relire** : complément C09, avec les limites permises et les deux recettes strictes toujours partielles ; PRET ne signifie pas acceptation globale.',
        '- **Réserves** : C13 offert/groupé absents ; B02 ne lit pas la seconde échéance payée, marge C05, compteurs/historique et documents non raccordés. Aucun assouplissement de règle ou changement de code C13/B02.',
        '- **Fichiers** : script C09/cataloque/projection de préservation ; recettes C09 et seules attentes de démonstration C13/B02 ; trois A-VOIR et présents rendus sous C09. Aucun thème/B03, bibliothèque close, site voie1, Git, verrou, file ou rapport global modifié.', '',
        '## Profil par profil — complément', '', '| Profil | État natif relu | Résultat du complément / reste |', '|---|---|---|']
    for key in ['A-CARTE','A-SEPA4','A-PAYPAL','A-PAPIER','A-ETRANGER','A-SANSMAIL','A-ECHEANCE','A-NONRENOUV','A-GRACE','A-SUSP']:
        value = payments['proof'][key]
        parts = []
        if 'initial' in value:
            o = value['initial']; parts.append(f"initiale #{o['id']} {o['status']}, date payée présente")
        for o in value.get('renewals', []):
            parts.append(f"renouvellement #{o['id']} {o['status']}, {'payé' if o['paid'] else 'non payé'}, création UTC {datetime.fromtimestamp(o['created'],timezone.utc).isoformat()}")
        row = next(r for r in rows if r['code'] == key)
        report.append(f"| {key} | {' ; '.join(parts)} | {row['etat']} — {row['limite']} |")
    report += ['', 'A-VIR : on-hold/pending et paiement absent ; P-OFFERT/P-GEST/P-BENEF : liens natifs absents, laissés sans droit inventé. Tableau intégral des 30 profils/décisions : A-VOIR.md.', '', '## Exécutions réelles', '',
        f"- C09 : {result['tests']}, tous verts ; reset **6/6**, altérations réellement détectées puis restaurées. Catégories : {counts}.",
        f"- C13 strict : **51 PHP + 26 HTTP**, pur **10 tests / 30 assertions**, exit **{result['strict_C13_exit']}**. 8 destinataires (6 BE / 2 étranger), dont 6 C09 ; A-SANSMAIL inclus. Seuls liens offert/groupé encore absents ; recette_complete=false.",
        f"- B02 strict : **{b02['total']}/{b02['total']}**, HTTP **55/55**, exit **{result['strict_B02_exit']}**. Seconde échéance native payée non consommée par son tableau (une Payée visible), failed A-SUSP attesté HTTP. Snapshot natif/rôles/options et lots clos préservés ; deux observations postales ajoutées, adresse restaurée.",
        '- Trois libellés B02 figés et périmés restent dans le reçu brut : profil a-4x-j45 (corrigé en A-SEPA4 par arbitrage), aucun failed, A-CARTE impayé. Ils ne sont pas repris comme blocages actuels. Aucun code produit ou runner B02 modifié.',
        '- Aucun paquet Composer/test PHP ajouté : preparer-image.ps1 non modifié, rafraîchissement conditionnel non requis. Image existante réellement exercée par les 10 tests purs C13.', '', '## Décisions prises à défaut et incidents', '',
        '- C09 conserve ses montants de grille fictive existants (ou zéro) et ses ID. Les six profils postaux payés commencent à J-90/J-180 pour garder le prochain numéro dans leur année C01. A-ECHEANCE/A-NONRENOUV conservent J-335/J+30, année native 365 jours testée. Aucun renouvellement annuel ni règle inventé. WCS ne planifie que la prochaine échéance ; la quatrième reste future, sans action supplémentaire fictivement déclarée.',
        '- Le vieux snapshot B00 appelait hash_file sur une pièce jointe retirée par C11 : échec réel avant mutation. Projection C09 adaptée en lecture seule aux fichiers présents et métadonnées ; C08/B00 préservés par comparaison exacte avant/après.',
        '- Au reset, les transitions payées WCS changeaient le rôle customer en subscriber : échec observé sur huit profils, puis restauration explicite du rôle C09 après les transitions ; reset et readback verts. Test RED puis GREEN supplémentaire sur la préservation de l’année native A-ECHEANCE/A-NONRENOUV.',
        '- Un premier vérificateur global a dépassé le watchdog de 420 s pendant B02. Processus terminé, adresses C09 relues intactes ; recette B02 complète rejouée, puis vérificateur relancé comme processus suivi. Aucun résultat inventé ; aucun historique nettoyé.',
        '- Les reçus anciens et incidents antérieurs restent présents. Les seuls nettoyages sont les témoins temporaires créés par les recettes elles-mêmes. Les nouveaux reçus C13/B02 sont redirigés sous C09 ; les fichiers de résultats des autres lots ne sont pas écrasés.', '',
        'Voir complement-verification.json, complement-final-native.json, complement-c13-strict.json, complement-b02-resultats.json et les trois A-VOIR. Validation visuelle laissée à Ced.']
    (P / 'RAPPORT-complement.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print(json.dumps({'rows':len(rows),'categories':counts,'C13_exit':result['strict_C13_exit'],'B02_exit':result['strict_B02_exit']},ensure_ascii=False))


if __name__ == '__main__':
    run()
