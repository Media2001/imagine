# C-15 — corrections de la fusion, rapport

- **Fait** : les huit instructions de `corrections/C-15.md` appliquées, avec RED→GREEN conservés.
- **Prêt à relire** : rejeu terminé le 25 novembre 2026 à 22 h 07 CET ; `corrections-final.json` : `PRET_RELECTURE_CORRECTIONS`.
- **À valider par Ced** : le visuel des cinq vues (`A-VOIR.md`) ; aucun GO sur le réel demandé.
- **Bloqué** : rien ; les états A-PAPIER impayé/payé ont été exercés puis restaurés, aucun profil manquant à fabriquer.
- **Périmètre** : trois classes `Echeances*`, test PHPUnit, runners/tests C15 et ce dossier. Aucun fichier C09, MonCompte/B02, thème, bootstrap, README partagé, bibliothèque close, préparateur, file, verrou ou rapport global modifié ; aucune opération Git.

## Corrections / décisions prises à défaut

- **Papier dû** : relations WCS de renouvellement, même propriétaire, commande sans remboursement ni méthode explicitement différente ; montant/devise/création UTC de la commande exigible impayée. La dette remplace la projection future ; pas d'admission globale des `on-hold`. Référence absente visible et exportée comme **Référence manquante**.
- **Virement** : mutex consultatif MySQL par base/site/commande, relecture après acquisition, libération en `finally`. Retour `false` de `payment_complete()` refusé même si un hook a déjà persisté l'état payé ; pas de note de succès C15 dans ce cas.
- **Règles pures** : nouveau `tests/EcheancesReglesTest.php`, découvert/exercé par T01 ; filtrage/tri/CSV, bornes exactes J+30/J+90/J+180 et ±1 seconde, égalités présentées par ID décroissant, absence de dates, dette/payé/référence absente. Banque autonome renforcée également.
- **Français** : libellés traduisibles/échappés, adaptés commande/souscription. Repli français explicite : les catalogues Woo/WCS de cette démo renvoient encore des noms anglais.
- **Écarts annoncés** : CSV à **5 colonnes**, **Devise** ajoutée aux quatre champs du §3.13, conservée pour éviter l'ambiguïté. Attente/virements **limités aux commandes liées à une souscription du même propriétaire**, achats à l'unité exclus (Q1). Échéances incluant `pending`/`on-hold` avec date native, en plus de `active`/`pending-cancel`, sans décision de droit d'accès. Q2 : papier `on-hold` seulement avec renouvellement exigible impayé.

## Résultats réels — catégories distinctes, pas de total doublonné

| Parcours | Vert |
|---|---|
| T01 standard global, après `preparer-image.ps1` inchangé | **1 030 tests / 34 124 assertions**, zéro échec/erreur/ignoré |
| Dont C15 découvert par T01 ; banque autonome distincte | **9 tests / 45 assertions** ; 28 contrôles |
| Lecture native ; HTTP vues/export ; action/restauration A-VIR | 21 ; 43 ; 16 contrôles |
| A-PAPIER impayé puis payé natifs | 6 contrôles |
| Deux confirmations HTTP simultanées | 7 contrôles : **un succès 302, un refus 409, une note C15** |
| Retour natif false injecté après état payé | 7 contrôles : **409, aucune note C15 de succès** |
| Libellés français HTTP ; paiements natifs C09 relus | 4 ; 149 contrôles |

Le mutex est vérifié libéré **dans la connexion vivante avant réponse**, y compris sur refus. Les RED réels montraient deux succès/deux notes, puis le faux succès sur retour natif false.

Témoins sous **A-PAPIER C09 existant**, via `wcs_create_renewal_order()`, transition native d'impayé puis statut payé fictif ; aucun nouveau profil ni paiement de passerelle. Commandes témoins 2521/2522/2523 supprimées et absence relue séparément. Restauration **du seul A-PAPIER ou A-VIR concerné**, sans reset global C09 : dates métier observées, statuts, rôle et adhésion exacts ; découverte C12 et date payée P-NUMERO inchangées. Notes d'audit/dates techniques de modification peuvent évoluer.

Empreintes distantes thème/bootstrap/autres fichiers plugin inchangées pendant le rejeu ; sources C15 scellées ; MU temporaire retiré. Aucun email/appel sortant de paiement : gardes contrôlées, passerelles indisponibles.

**Incidents de harnais résolus** : expansion `$` WSL évitée par fichier PHP ; suppression MU refusée depuis WP-CLI, effectuée côté dashboard sur le seul chemin/empreinte possédés, puis absence et restauration relues. La restauration est indépendante d'un échec de suppression. L'injection de refus produit volontairement une note/trace d'erreur Woo fictive. L'avertissement T01 « thème sans tests » ne vaut pas validation visuelle.

**Preuves faisant foi** : `corrections-final.json`, `corrections-t01.log`, `corrections-*-final*`, `corrections-renewals-deleted-readback.json`. Les anciens `verification.json`, total 257 et `restore-diff.json` sont historiques, antérieurs à la correction.
