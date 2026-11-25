"""Actualisation C09 : texte de démonstration, aucun raccord métier ou droit ajouté."""
from pathlib import Path
import json
p = Path(__file__).resolve().parents[2] / 'outils/demo/c09-profils.json'
rows = json.loads(p.read_text(encoding='utf-8'))
updates = {
    'A-CARTE': ('partiel', 'Commande initiale processing et date payée fictives, tarif normal-1 ; abonnement actif et lecture complète.', 'Aucune carte réelle. Reconduction automatique non posée ; renouvellement manuel maintenu. Compteur 3 numéros et historique C01 non raccordés.'),
    'A-SEPA4': ('partiel', 'Deux paiements natifs fictifs sur quatre : commande initiale et un renouvellement processing ; prochaine échéance manuelle planifiée, deux échéances restant à venir.', 'Aucun mandat SEPA ni jeton. WCS planifie seulement la prochaine action, pas une seconde action pour la quatrième échéance. B02 ne lit encore que la commande initiale : sa table ne montre qu’une Payée ; marge C05/dates théoriques non raccordées.'),
    'A-PAYPAL': ('partiel', 'Commande initiale payée fictive, abonnement actif normal-1 et lecture complète.', 'Aucun accord PayPal ni jeton ; renouvellement manuel uniquement.'),
    'A-PAPIER': ('partiel', 'Commande initiale payée fictive normal-4, abonnement actif ; prochaine échéance manuelle ce mois-ci.', 'Aucun mandat papier ou IBAN, aucun export bancaire. Quatre fois reste une fixture, pas une règle de domiciliation.'),
    'A-GRACE': ('créé', 'Renouvellement natif failed fictif daté à J-1 ; abonnement on-hold, adhésion paused ; lecture et régularisation pendant la fenêtre J-1/J+2.', 'Rejet et fenêtre explicitement fictifs ; aucun rejet bancaire réel. Durée de fixture, pas une règle métier décidée.'),
    'A-SUSP': ('créé', 'Renouvellement natif failed fictif daté à J-4 ; grâce finie à J-1, lecture fermée et exclusion postale suspendu.', 'Rejet explicitement fictif, jamais un incident bancaire réel ; aucune reconduction automatique.'),
    'A-NONRENOUV': ('partiel', 'Commande initiale payée fictive, souscription pending-cancel jusqu’au terme J+30 ; lecture complète.', 'Fin native de renouvellement démontrée ; compteur métier 1 numéro restant et historique non raccordés.'),
    'A-ETRANGER': ('partiel', 'Commande initiale payée fictive, adresse France et ligne de port fictif zéro ; inclusion postale positive.', 'Supplément de port non chiffré : zéro n’est pas un supplément appliqué ni un tarif Imagine.'),
    'A-SANSMAIL': ('partiel', 'Commande initiale payée fictive, adresse technique a-sansmail@example.org ; inclusion positive dans la liste et le CSV postaux C13.', 'Exclusion individuelle des emails non raccordée. Le coupe-circuit global garantit aucun email mais ne prouve pas ce critère individuel.'),
    'A-ECHEANCE': ('partiel', 'Commande initiale payée fictive ; abonnement actif, terme J+30, prochaine échéance manuelle J+29.', 'Reconduction automatique non posée. Rappel/non-envoi non raccordés ; aucun email envoyé.'),
    'E-ABO': ('partiel', 'Rôle dédié Référent abonnements : commandes, liste d’envoi C13 et export accessibles ; lecture équipe sans capacité éditoriale.', 'Échéances, justificatifs et extractions métier non entièrement raccordés. Aucun manage_woocommerce, manage_options ou gestion générale des utilisateurs.')
}
for row in rows:
    if row['code'] in updates:
        row['etat'], row['vue'], row['limite'] = updates[row['code']]
p.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print({state: sum(r['etat'] == state for r in rows) for state in ['créé', 'partiel', 'impossible']})
