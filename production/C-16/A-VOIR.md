# C-16 — À voir

**C-16 prêt à relire techniquement : `PRET` déposé. T01 canonique corrigé ; réserve C09 historique explicitement conservée.** Ce n’est ni une validation visuelle, ni un GO sur des données/paiements réels. C17 et C18 ne sont pas traités.

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
# Relecture courante, sans paiement ni reset global :
python wp/tests/demo/c16-gates.py                # exit 0 : C16 recevable, réserve C09 affichée
python wp/tests/demo/c16-gates.py --strict-global # exit 2 : C09 conserve son échec historique
python production/B-04/sceller-portabilite.py --check

# Pour rejouer les tests (enregistrer de nouveaux reçus sans effacer les anciens) :
python wp/outils/demo/c16-unit.py unit-gates
python wp/outils/demo/b04-unit.py portabilite-c16
python wp/tests/demo/c16-http.py http-gates
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Les commandes de qualification ont été réellement exécutées ; leurs sorties sont conservées dans les fichiers `*-gates*` ci-dessous. `c16-etat.py`, les anciens `*-final*` et `final-before-gates.json` documentent l'arrêt précédent, **pas l'état courant**. Le déploiement C16 est déjà relu identique : ne pas le relancer pour regarder les écrans.

Le runner HTTP utilise les outils/identifiants privés existants de B00/C09/C12. Il crée puis supprime ses objets **pending**, par l’extension C16 du reset C09 (`c16-reset.php`), également incluse par le seed C09 avant son prévol. Il ne relance pas le reset global des profils : C09/C12/C14 sont préservés. Un objet payé/modifié/étranger fait refuser le nettoyage, pas une suppression aveugle. Les relevés postaux append-only sont conservés. Ne pas lancer de seed global pour simplement montrer ces écrans.

## Preuves et état exact

Tout est dans `production/C-16/` :

- `natif.md` : dix lignes de comparaison avec le parcours standard, sources officielles consultées.
- `installation.json` : SHA-256 relus des fichiers réellement déployés, cible fixe, aucune installation commerciale ni téléversement du thème.
- `unit-gates.json` : **6 tests C16, 14 assertions**, PHPUnit réel hors réseau, conteneur supprimé et absence vérifiée.
- `../B-04/unit-portabilite-c16.json` et JUnit associés : **76 tests racine / 481 assertions**, **7 tests C12 / 63 assertions** ; **4 tests B04 / 91 assertions** (sous-ensemble de la racine, ne pas additionner). Tous réussis. C16 est aussi inclus dans la racine.
- `http-gates.json` : **70 contrôles, zéro échec** : cinq souscriptions (existant, nouveau, sans email, email connu, vente directe), un achat de numéro sans souscription, refus de droits/nonces/saisie, reprise sans doublon et reset. Lectures natives : `native-*.json`, décision fermée : `acces-sansmail.json`.
- `reset.json`, `final.json` : **11 objets natifs et 3 comptes C16 supprimés**, inventaires finaux vides ; nombre de comptes, manifeste C09 et état C12 restaurés. Les six commandes temporaires du rejeu courant étaient **2625, 2627, 2629, 2631, 2633, 2635**. Les cinq souscriptions liées ont aussi été retirées.
- `red-regles.json`, `red-http.json` : RED avant implémentation. Les échecs historiques et le rapport de 00 h 29 restent conservés, sans réécriture.
- `preparer-image-gates.log` : préparation réelle après correction du test B04, exit 0, image vérifiée ; ni édition de T01 ni dépendance commerciale.

### Les deux gates : correction et classement explicite

1. **T01 réellement vert : exit 0, 1 040 tests / 34 229 assertions, 0 échec, 0 erreur, 0 ignoré** (`rejouer-t01-gates-final.log`). RED reproduit avant correction dans `rejouer-t01-gates-red.log`. Seul changement B04 : `wp/plugins/imagine-site/tests/b04-status-fixture.php` lit d'abord le thème frère du checkout puis, si absent du paquet copié, le vrai thème au montage en lecture seule `/repo/wp` documenté par le runner. Si les deux manquent : exception. **Aucune assertion ni test supprimé** ; le mapping livré et l'absence de hooks restent testés, **55 assertions** pour ce test. Aucun changement de thème, de runner T01 ou de bibliothèque close. Nouveau sceau B04 : `../B-04/verification-portabilite-c16.json`, preuves natives antérieures conservées et empreintes relues, sans rejouer leur matrice.
2. **C09 ne devient pas tout vert : 381/382 contrôles réussis**, même échec `A-PAPIER:action_native_planifiee_ou_absente_selon_statut` (`c09-non-regression-gates.json`). Diagnostic natif : action **8103**, prévue pour le **25 novembre 2026 à 19:01:50 UTC**, **annulée le 25 novembre à 20:38:22 UTC** ; elle n'a donc pas été « consommée naturellement ». L'installation C16 enregistrée est postérieure, à **23:18:01 UTC**. L'abonnement #101 et l'action sont identiques avant/après le nouveau parcours HTTP C16 et au readback final (`gates-c09-diagnostic.json`, `gates-c09-after-http.json`, `gates-c09-final-readback.json`). Le calendrier C09 crée A-PAPIER à +1 h ; la restauration C15 des anciennes dates est une explication cohérente, **pas une attribution prouvée de l'annulation**. L'API WCS installée ne recrée pas une action pour une date passée. Aucun seed global, changement de #101, exécution de file ou replanification arbitraire n'a été fait.

**Décision technique à défaut** : le défaut historique de fixture C09 est classé hors C16, non bloquant pour sa réception ciblée ; il reste visible, non corrigé et doit être traité dans une consigne dédiée. `c16-gates.py` ne tolère que cet état précisément documenté et inchangé ; toute autre régression refuse le lot. Le mode `--strict-global` retourne toujours **2**, avec `global_all_green=false`. `PRET` signifie seulement **C16 prêt à relire techniquement**, pas « tous les lots verts », ni clôture ni validation visuelle de Ced.
