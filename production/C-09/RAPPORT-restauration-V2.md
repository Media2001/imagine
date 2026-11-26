# Restauration C09 A-PAPIER — 26 novembre 2026 — voie 2

- **Fait** : profil A-PAPIER restauré sur `imagine-test-demo`, lecture native **382/382**, sans réserve.
- **Prêt à relire** : preuves successeurs C17 et C18, en lecture seule ; aucun nouveau lot.
- **À valider ou arbitrer par Ced** : rien pour cette restauration ; les validations visuelles antérieures restent inchangées.
- **Bloqué** : non.
- **Ensuite** : retour au parent ; aucun autre travail engagé.

## Exécution autorisée

Consigne 1 de `A-FAIRE-2.md`, version du 26 novembre à 1 h 30, et arbitrage du même jour : réemploi du calendrier du jeu C09, pas d'échéance inventée. Le rejeu est **ciblé A-PAPIER**, pas un reset global. Le fichier `c09-papier.php` appelle les mêmes fonctions `now()` / `papierDue()` de `c09-calendar.php` que `c09-seed.php`, puis la même API native `update_dates()` / `save()`, uniquement pour `next_payment`. Le seed général, les autres profils, les comptes, les commandes payées fictives et les droits ne sont pas réinitialisés.

Relecture persistée, dans des processus PHP distincts : abonnement **101**, `active`, manuel, passerelle et transaction vides. Échéance **2026-11-26 02:13:28 UTC**, soit **03:13:28 CET**, issue de l'horloge C09 à 01:13:28 UTC. Action **8793**, `woocommerce_scheduled_subscription_payment`, `pending`, arguments `{"subscription_id":101}`, même échéance ; `as_next_scheduled_action` = **1795659208**, identique à `get_time('next_payment')`. L'action historique **8103** reste annulée, sans modification de ses journaux.

Reçu exact : `production/C-09/papier-restauration-V2.json`.
SHA-256 : `0607a745fac5edec912ae623e1e221b86046c78a1e02203d71281adfbd176a6e`.

## Vérification et difficulté rencontrée

Avant : **381/382**, seule l'action A-PAPIER manquait. Après : **382/382**, code 0, aucune erreur native. Seul l'abonnement 101 change dans les empreintes commerciales ; produits, adhésions, profils, manifeste et options sont conservés. Les deux nouveaux enregistrements du scheduler sont l'action 8793 et une invalidation du cache natif WCS de rapport (8794, remplaçant 8789 annulée). Aucun email ni paiement n'est exécuté.

Le premier wrapper a effectué la réparation puis a refusé cette invalidation de cache, trop strictement classée « hors cible ». **Aucun second rejeu** : diagnostic et complément de reçu exclusivement en lecture seule. L'inversion en mémoire de ces seuls deltas reproduit exactement les empreintes et nombres de lignes du scheduler conservés avant l'écriture ; aucune ligne SQL ni preuve ancienne n'a été réécrite. Cette difficulté et la limite du premier wrapper figurent dans le reçu.

## Gates successeurs, pas de réécriture historique

`c17-verifier.py` et `c18-verifier.py` exigent désormais C09 réellement vert. Le pont de baseline exige l'ancien état exact du reçu de réparation, puis son état restauré exact ; il ne tolère pas une dérive arbitraire. Mode `--readback-only` ajouté, sans upload, reset ni changement de données. Les preuves `installation.json`, `final.json`, les reçus HTTP et les CSV antérieurs restent identiques ; aucun code fonctionnel de plugin/thème n'a changé. Le bootstrap partagé C17 est contrôlé contre son successeur C18 déjà documenté.

- C17 : **6/6 gates** en lecture seule, C09 **382/382** ; preuve `production/C-17/verification-successeur-20261126T011902245301-V2.json`.
- C18 : **8/8 gates**, C09 **382/382**, **14/14 contrôles natifs C18** rejoués et **9 CSV historiques rouverts** ; preuve `production/C-18/verification-successeur-20261126T011932299347-V2.json`.
- Régression locale : **9/9 tests Python**, dont refus de l'ancien état cassé et des dérives de commande, scheduler ou baseline ; `production/C-09/tests-successeurs-V2.json`. Les deux attentes historiques fautives ont été observées rouges avant correction.
- Les suites PHP/HTTP complètes précédentes sont relues comme preuves **historiques**, pas présentées comme rejouées : aucun changement d'entrée PHP fonctionnelle, donc pas de rebuild ni de campagne globale.

## Commandes légères pour le parent

```text
python wp/outils/demo/c09-papier.py --readback
python wp/tests/demo/c17-verifier.py --readback-only
python wp/tests/demo/c18-verifier.py --readback-only
python wp/tests/demo/c09-successor-test.py
```

Nouveaux fichiers : helpers `wp/outils/demo/c09-papier.php`, `c09-papier.py`, `c09-papier-receipt.py` ; contrôles `wp/tests/demo/c09-successor-gates.py`, `c09-successor-test.py` ; preuves `*-V2` dans C09/C17/C18. Seuls les deux vérificateurs C17/C18 préexistants ont été modifiés. Pas de Git, pas de verrou manipulé, pas d'autre site, pas d'enfant.
