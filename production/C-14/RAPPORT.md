# Rapport voie 2 — C-14 — 25 novembre 2026

1. **Fait** : C14-01 : acquisition fondée sur l’instantané immuable, indépendante du catalogue ; C14-02 : portée du remboursement configurable et testée ; C14-03 : état documentaire aligné.
2. **Prêt à relire** : corrections C-14 livrées avec preuves actuelles ; **PRET initial du parent existant, inchangé**, pas une validation des corrections. Relecture uniquement.
3. **À valider ou à arbitrer** : aucun blocage technique ; validation visuelle et toute opération sur le réel restent hors livraison. Achat invité : revendication après création du compte non livrée, accès fermé.
4. **Bloqué** : rien pour le périmètre du brief connecté ; aucune banque, passerelle, adresse réelle ou licence exercée.
5. **Ensuite** : retour au parent pour vérification indépendante ; aucune prise de lot suivant par ce sous-agent.

## Résultat

Démo `imagine-test-demo` uniquement, WP 7.0.9 / Woo 11.2.2 / PHP 8.3.32 / HPOS actif, versions lues sans mise à jour. Dernier rejeu : **686/686** contrôles C14/raccords ; **205/205** régressions complémentaires (paquet site C11/C13/C14 48 tests/258 assertions, C12 7/63, C12 natif 32, HTTP 85, Python 33). Suite autorisée complète **T01 : 1012 tests / 34006 assertions, 0 échec, 0 erreur, 0 ignoré**. Préparation image obligatoire et PSR-12 des deux classes/test C14 : codes 0. Les suites se recouvrent, aucun total de tests distincts inventé. `validation-corrections.json` et `validation-*.log` donnent les commandes et résultats réels ; `COMMANDES.md` les explique.

`AchatNumero` reste pur ; `AchatsNumeros` lit les commandes/lignes/remboursements CRUD et transmet `achat` à C08/C06 inchangé. Réaffecter/vider/supprimer le produit **conserve A sans ouvrir B** ; seul un nouvel achat prend B. Le numéro acquis doit rester publié. Retrait d’instantané, quantité zéro, ligne/commande supprimée, propriétaire/paiement invalide ou lecture défaillante : fermé. Articles/PDF testés avant/après mutations, sans invalidation manuelle. Réglage Settings API, nonce/capacité/persistance réelle contrôlés. Tous les remboursements exercés : zéro euro, `refund_payment=false`, aucune passerelle/transaction. Les canaris propres sont supprimés et leur absence relue.

## Décisions prises à défaut

- **Technique** : « V-NUM » n'existe pas dans le catalogue. Conserver compte/login/commande **P-NUMERO** et ajouter l'alias explicite V-NUM ; 30 profils/27 comptes inchangés. T1 ouvert, autres numéros fermés. État/date payés sont des fixtures déclarées à zéro euro, pas un paiement bancaire inventé.
- **Technique** : instantané seul, acquis durable conformément au §3.9 ; catalogue mutable sans révocation ni rétro-octroi. Produits simples, aucune migration implicite. Aucun plan Memberships ni second circuit PDF ajouté. Aucun reset de profil pour ces corrections.
- **Métier configurable** : `imagine_achat_remboursement=commande|ligne`, défaut prudent `commande` y compris absent/invalide. Alternative `ligne` : seule la ventilation native sur une ligne produit retire son achat ; un partiel non ventilé ne retire aucune ligne. Le complet ferme tout dans les deux modes. Commandes à deux numéros, ventilé/non ventilé/complet, articles et PDF testés dans chaque mode. Question Imagine explicite ; ne bloque pas le lot.
- **Invité** : le cahier §3.7 le prévoit pour le papier, avec compte proposé après achat. Sans rattachement natif à un compte : fermé, même si l'email correspond. Le parcours sécurisé de revendication reste hors lot.
- **Référence** : le brief cite §3.11 (événements) ; application des dispositions pertinentes §3.7/§3.9.

## Fichiers livrés

- Plugin modifié par les corrections : `AchatNumero.php`, `AchatsNumeros.php`, `README.md` ; nouveau `tests/AchatNumeroTest.php`, découvert par T01 via le paquet racine C13 conservé.
- Outils C14 : `c14.py` (dont `--deploy-code`, transaction du témoin C11), `c14-regressions.py`, nouveau `c14-validation.py`.
- Tests C14 : `c14-unit.php`, `c14-runtime.php`, `c14-http.py` ; nouveaux `c14-corrections-fixture.php`, `c14-corrections-runtime.php`, `c14-corrections-http.py`.
- Preuves : ce rapport, `A-VOIR.md`, `COMMANDES.md`, `PROPOSITIONS-DOCS.md`, reçus JSON/journaux `validation-*`, audit en lecture seule et `incident-observations-c13.json`. PRET non touché.

Aucun fichier de voie 1, bibliothèque close, script staging/T01, verrou ou fichier de file n'a été modifié. Aucun Git. Le rapport conventionnel `files/rapports/` reste à intégrer par le parent, hors périmètre d'écriture délégué.

## Incident et conservation C13/B02

Les deux diagnostics initiaux de C11 (25 novembre, **14:25:02 et 14:28:30 UTC**) ont déclenché **12 nouvelles observations synthétiques C13** sur les souscriptions C08 77/79, via les plans temporaires offert/groupe puis restaurés. Aucun événement préexistant n’a été modifié/effacé ; cet historique append-only n’a pas été « nettoyé » silencieusement. Inventaire exact : `incident-observations-c13.json`. Le wrapper C14 exécute désormais la recette C11 dans une transaction InnoDB réellement rollbackée, callbacks inclus. Derniers rejeux : égalité exacte des options/historiques C13, fixtures, fichiers C13/MonCompte et thème, bibliothèques closes ; PRET inchangé. Cette égalité finale ne réécrit pas l’incident antérieur. Le parent doit en prendre connaissance.

Instruction 5 optionnelle : N+1 remboursements conservé, volume synthétique. Instruction 6 : propositions documentaires dans `PROPOSITIONS-DOCS.md`, aucun `docs/` modifié. Relecture indépendante attendue ; aucune clôture, validation visuelle ou autorisation réelle revendiquée.
