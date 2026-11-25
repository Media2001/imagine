# C-16 — À voir

**Code et parcours fictif exercés ; qualification globale bloquée, aucun `PRET`.** Ce n’est ni une validation visuelle, ni un GO sur des données/paiements réels. C17 et C18 ne sont pas traités.

## Compte et adresse

Sur le seul site `imagine-test-demo`, se connecter comme **E-ABO**, login `e-abo` (ou **E-ADMIN**, `e-admin`). Les identifiants C09 sont dans le fichier privé `C:\Users\Ced\.imagine-demo\identifiants.json`, jamais dans les preuves.

Ouvrir **Imagine → Commande pour un client** :

`http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-commandes`

1. **Client** : rechercher `V-INSCRIT`, `v-inscrit@example.org` ou `Ville Fictive` ; sélectionner le compte. Ou saisir un nom manifestement fictif et une adresse en `@example.org`, ou cocher **Sans email**. **Vente directe** choisit le compte générique fictif en un clic. Une adresse déjà connue reprend le compte existant sans changer son nom/adresse. La création est différée à la confirmation, pour ne laisser aucun compte abandonné.
2. **Commande** : choisir **C09 FICTIF — normal-1 — pas une offre Imagine** (120 EUR de fixture, pas un tarif Imagine), conserver/saisir une adresse fictive (`16 rue Imaginaire`, `1000`, `Ville Fictive`, `BE`), puis **Virement** ou **Mandat papier**. Un produit simple C14 lié à un numéro est également disponible. Sans identité : adresse facultative. Pas de taxe/port Imagine inventé, pas de quantité/prix libre.
3. **Confirmation** : récapitulatif, case obligatoire, **Créer la commande en attente**. Le résultat reste dans ce troisième écran. Il donne l’ID natif ; un double envoi reprend le même ID, pas une seconde commande. Aucune commande ni compte n’existe avant cette confirmation.

Puis ouvrir **Imagine → Échéances → Virements à valider** :

`http://192.168.129.32:8085/wp-admin/admin.php?page=imagine-echeances&vue=virements`

La commande d’abonnement par virement apparaît, liée à une souscription native `pending`. **Ne pas cliquer Paiement reçu pour cette recette C16.** Le lot n’exécute aucun paiement ni activation d’accès. Les commandes à l’unité restent hors de cette vue selon le périmètre C15 actuel ; les mandats n’ont ni référence bancaire fabriquée ni prélèvement exécuté.

Le nouveau compte sans email porte `imagine_sans_email=1`, adresse interne `@sans-email.imagine.invalid`. C’est le marqueur déjà employé par la fixture C13 ; A-SANSMAIL C09, qui n’en portait aucun au départ, le reçoit désormais dans le seed sans changer son adresse historique. Le filtre individuel WP refuse les destinataires TO/CC/BCC marqués, en plus du coupe-circuit global. Aucun raccord Brevo externe n’est annoncé prouvé. La décision réelle C06 du nouveau compte reste `complet=false`, `motif=sans_droit`, `bloc=abonnement` ; aucune adhésion n’est créée.

Don, pack, abonnement offert et abonnement groupé ne sont que des emplacements nommés. Aucun réglage métier inventé ni changement des bibliothèques closes/C10. Les trois écrans sont un squelette natif, pas une maquette validée par Ced.

## Rejouer depuis la racine

```powershell
python wp/outils/demo/c16.py --deploy
python wp/outils/demo/c16-unit.py unit-final
python wp/tests/demo/c16-http.py http-final
python wp/outils/demo/c16-unit.py unit-root-final --root
python wp/tests/demo/c16-etat.py # contrôle sans paiement, exit 2 tant que les gates globaux sont rouges
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Le runner HTTP utilise les outils/identifiants privés existants de B00/C09/C12. Il crée puis supprime ses objets **pending**, par l’extension C16 du reset C09 (`c16-reset.php`), également incluse par le seed C09 avant son prévol. Il ne relance pas le reset global des profils : C09/C12/C14 sont préservés. Un objet payé/modifié/étranger fait refuser le nettoyage, pas une suppression aveugle. Les relevés postaux append-only sont conservés. Ne pas lancer de seed global pour simplement montrer ces écrans.

## Preuves et état exact

Tout est dans `production/C-16/` :

- `natif.md` : dix lignes de comparaison avec le parcours standard, sources officielles consultées.
- `installation.json` : SHA-256 relus des fichiers réellement déployés, cible fixe, aucune installation commerciale ni téléversement du thème.
- `unit-final.json` : **6 tests C16, 14 assertions**, PHPUnit réel hors réseau, conteneur supprimé et absence vérifiée.
- `unit-root-final.json` : **76 tests racine, 481 assertions**, zéro échec/erreur. Ce total inclut C16, il ne s’y additionne pas ; la configuration C12 séparée n’est pas annoncée rejouée.
- `http-final.json` : **70 contrôles, zéro échec** : cinq souscriptions (existant, nouveau, sans email, email connu, vente directe), un achat de numéro sans souscription, refus de droits/nonces/saisie, reprise sans doublon et reset. Les lectures natives sont dans `native-*.json`, la décision fermée dans `acces-sansmail.json`.
- `reset.json`, `etat-final-readback.json` : objets/comptes C16 supprimés ; inventaires finaux vides, nombre de comptes et manifestes C09/état C12 restaurés. Les six commandes temporaires du dernier rejeu étaient **2614, 2616, 2618, 2620, 2622, 2624**, puis supprimées.
- `red-regles.json`, `red-http.json` : RED avant implémentation. `http-first.json` a découvert trois mauvais statuts HTTP de nonce (refus après les en-têtes admin), corrigés par le traitement sur `admin_init`. `unit-current.json` est un ancien échec de banc copié sans ses frères ; le banc final lit le dépôt monté en lecture seule et passe.
- `preparer-image.log` : préparation réelle exécutée, exit 0, image vérifiée ; ni édition de T01 ni dépendance commerciale.

### Gates rouges conservés, sans faux PRET

1. **Commande canonique `wp/tests/rejouer.ps1` : exit 1**, **1 040 tests / 34 176 assertions, 1 échec, 0 erreur, 0 ignoré** (`rejouer-t01.log`). Seul échec : `CatalogueStatusTest::testDeliveredFunctionAloneMapsAllFourCodesAndBothDiscoveryReasons`, car le banc canonique cherche `/tmp/t01/themes/imagine/inc/catalogue.php`, qui n’a pas été copié. Le même test passe lorsque le dépôt monté `/repo/wp` est utilisé (suite racine ci-dessus). Aucun fichier B04 ni runner T01 n’a été corrigé dans C16 : ce point est rendu au parent, pas masqué par une exclusion.
2. **Lecture native C09 : 382 contrôles, un échec** (`c09-non-regression.json`) : `A-PAPIER:action_native_planifiee_ou_absente_selon_statut`. L’abonnement existant #101 reste `active`, prochaine date native **25 novembre 2026 à 19:01:50 UTC**, mais `as_next_scheduled_action(...)` vaut `false`. Constat relu à **23:24:34 UTC** (`etat-final-readback.json`). C16 n’a pas réparé/replanifié ce profil ni exécuté sa file ; origine non attribuée sans preuve de départ sur ce point.

Les gates C16 ciblés sont verts ; ces deux gates globaux sont réellement rouges. `PRET` n’est donc pas déposé. Le parent peut faire la vérification de C16 et classer les problèmes de banc/fixture sans rouvrir ici B04 ou C15. La validation visuelle de Ced reste à faire, comme pour les autres écrans de cette voie.
