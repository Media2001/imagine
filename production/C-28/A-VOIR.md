# C-28 — corrections de la fusion du 27 novembre 2026, 12 h 40

**Site unique `imagine-test-demo`, entièrement fictif. Aucune passerelle, transaction bancaire, donnée réelle ou extension commerciale ajoutée.**

## Adresses

- Fiche publique : http://192.168.129.32:8085/product/c28-pack-thematique-fictif/ — produit **3592**, titre explicite, trois couvertures/titres/dates, prix **3.28 EUR fictifs**, bouton **Acheter ce pack** et panier Woo natif. Aucun texte réservé sur la fiche.
- Administration : http://192.168.129.32:8085/wp-admin/post.php?post=3592&action=edit — données générales du produit simple, **Pack : numéros inclus**, sélection multiple. Liste laissée : **11, 18, 25**. Une modification n'accorde aucun numéro aux achats passés.
- Mon compte : http://192.168.129.32:8085/my-account/ — la recette démontre les trois numéros dans la même rubrique que les achats unitaires ; à la livraison V-INSCRIT est de nouveau sans achat, comme au départ.
- Réglage existant de remboursement C14 : http://192.168.129.32:8085/wp-admin/options-general.php?page=imagine-achats — aucune section ni politique de remboursement propre aux packs.

Le mode Woo Coming Soon de la boutique reste inchangé. Le MU fictif C28 exempte seulement cette fiche de produit, pas la boutique entière. Les accès aux comptes utilisent les identifiants fictifs habituels, rangés hors dépôt ; aucun secret nouveau.

## Ce qui reste en place

Seul produit pack C28 et option `imagine_c28_fixture`, déclarés fictifs. Trois anciens numéros existants, leurs articles et PDF existants : aucun corps éditorial modifié. Numéro d'ajout temporaire **32**. **Pas de commande payée C28 permanente ni de droit nouveau laissé sur un profil C09.** Les commandes et remboursements d'essai ont été retirés, profils/sessions/réglages/actions restaurés et relus. Capture publique courante : `correction-recette-finale-pack.png`.

**À vérifier dans le code et les preuves** : le serveur refuse l'ajout direct et le checkout d'un panier devenu invalide après dépublication ; le pack entier est bloqué sans recalcul de prix. La composition n'est capturée qu'à la première persistance du paiement. Après panne de ligne sur paiement déjà persisté, recharge de commande et édition du pack, la sauvegarde tardive ne reconstruit rien : accès fermé et anomalie visible `imagine_pack_anomalie`. Déliement pack/numéro symétrique, accès/remboursements C14 inchangés.

## Vérifier — commande parent

Depuis `C:\Users\Ced\imagine` :

```powershell
python -B wp/tests/demo/c28-verifier.py
python -B wp/tests/demo/c28-verifier.py --live
```

La première vérifie le paquet **hors réseau**, sans mutation ; la seconde ajoute uniquement une relecture gardée de `imagine-test-demo`, des sources, de la fixture et de l'état métier restauré. `reception-corrections.json` scelle les sources et preuves finales ; tout écart refuse. `reception.json` est historique. `PRET` signifie prêt à relire, pas clôture ni validation visuelle.

Rejeu autonome avec un **LABEL réellement neuf**, jamais en parallèle d'une autre recette de cette voie :

```powershell
python -B wp/outils/demo/c28-local.py parent-unitaire-NOM-NEUF
python -B wp/tests/demo/c28-canaris.py parent-canaris-NOM-NEUF
python -B wp/outils/demo/c28-corrections.py native parent-fenetre-NOM-NEUF
python -B wp/outils/demo/c28.py runtime parent-natif-NOM-NEUF
python -B wp/outils/demo/c28.py regressions parent-C14-NOM-NEUF
python -B wp/outils/demo/c28-recette.py parent-recette-NOM-NEUF
python -B wp/outils/demo/c28.py preservation parent-preservation-NOM-NEUF
```

`c28-canaris.py` produit cinq rouges puis un vert dans une copie jetable hors réseau. PHPUnit inclut la couche de branchement sur doubles persistés. `native`, `runtime` et `regressions` utilisent de vrais objets natifs dans un rollback vérifié. `native` provoque réellement la panne après paiement persisté puis recharge la commande avant édition/sauvegarde tardive. La recette navigateur est **temporairement mutante sur la seule démo** : formulaire produit, panier, `payment_complete()` fictif, remboursements natifs sans transfert, sessions, sélection du pack et une mutation de source C28. Préimage privée durable avant action et retour relu obligatoires ; aucun reset C09. Ne pas relancer les scripts de récupération historiques.

Commandes générales inchangées, déjà réellement exécutées après ajout des tests et avant PRET :

```powershell
.\wp\tests\preparer-image.ps1
.\wp\tests\rejouer.ps1
```

## Résultats constatés

- PHPUnit C28 : **3 tests / 54 assertions**, dont branchement `candidat`/`payer`/`instantanes` ; **5 canaris de source rouges puis vert** ; natif nominal **25/25**, panne après paiement persisté **18/18**, complément C14 **45/45**.
- Recette HTTP/navigateur : **200/200**, avant/après paiement pour acheteur/tiers/anonyme, articles et vrais PDF, compte ; ajout du quatrième refusé, retrait conservé, politiques C14 inchangées.
- **7 sorties non vides** de la fiche inspectées avec les **32 témoins C26** ; redirection de recherche inspectée ; **32 injections de réponse détectées** et **1 mutation de source détectée/restaurée**. Matrice C26 non étendue.
- **19 fichiers PHP** sans erreur de syntaxe. Image reconstruite après ajout des tests, sortie **0**.
- Rejeu général : **1 190 tests / 36 548 assertions**, aucun échec/erreur/ignoré, **PASS** ; outils : **22 / 720 contrôles**, tous verts.
- Paquets : **11 vérifiés, 1 échec A-32 / A32_PACKAGE_DRIFT** ; **A-31 hors rejeu, journaux absents**. Hors périmètre, aucun resceau/réparation.
- Réseau : tentatives natives mail/HTTP observées bloquées avant transport ; tentatives Gravatar admin bloquées côté navigateur, aucun tiers public chargé. Ce n'est pas un « zéro tentative » ; compteurs exacts dans le reçu courant.

Les sources et compteurs définitifs sont ceux des reçus `correction-*-final*` scellés dans `reception-corrections.json`. `NOTE.md` distingue réception corrigée et historique. Panne par exception au vrai point de sauvegarde, pas arrêt brutal du conteneur ; comparaison métier/ciblée, pas identité intégrale de base ni nouvelle garantie de concurrence. Aucun paiement financier ni checkout fournisseur testé ; aucune validation visuelle ou juridique acquise. **B-11 reste BLOQUÉ sans PRET et n'a pas été touché.**

## Lanceurs non rejoués par les relecteurs initiaux

Claude avait rejoué la suite PHP générale. Codex n'avait pas pu lancer PHPUnit (`Wsl/Service/E_ACCESSDENIED`) et avait lancé seulement le vérificateur hors ligne (27 contrôles). **Ni Claude ni Codex n'avaient rejoué les recettes `--live`/mutantes**. Les preuves mutantes et natives corrigées ci-dessus ont été exécutées à la livraison ; elles ne sont pas présentées comme un nouveau rejeu indépendant des relecteurs. Les commandes exactes ci-dessus permettent ce rejeu.
