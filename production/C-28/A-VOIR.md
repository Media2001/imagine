# C-28 — à ouvrir et à rejouer

**Site unique `imagine-test-demo`, entièrement fictif. Aucune passerelle, transaction bancaire, donnée réelle ou extension commerciale ajoutée.**

## Adresses

- Fiche publique : http://192.168.129.32:8085/product/c28-pack-thematique-fictif/ — produit **3592**, titre explicite, trois couvertures/titres/dates, prix **3.28 EUR fictifs**, bouton **Acheter ce pack** et panier Woo natif. Aucun texte réservé sur la fiche.
- Administration : http://192.168.129.32:8085/wp-admin/post.php?post=3592&action=edit — données générales du produit simple, **Pack : numéros inclus**, sélection multiple. Liste laissée : **11, 18, 25**. Une modification n'accorde aucun numéro aux achats passés.
- Mon compte : http://192.168.129.32:8085/my-account/ — la recette démontre les trois numéros dans la même rubrique que les achats unitaires ; à la livraison V-INSCRIT est de nouveau sans achat, comme au départ.
- Réglage existant de remboursement C14 : http://192.168.129.32:8085/wp-admin/options-general.php?page=imagine-achats — aucune section ni politique de remboursement propre aux packs.

Le mode Woo Coming Soon de la boutique reste inchangé. Le MU fictif C28 exempte seulement cette fiche de produit, pas la boutique entière. Les accès aux comptes utilisent les identifiants fictifs habituels, rangés hors dépôt ; aucun secret nouveau.

## Ce qui reste en place

Seul produit pack C28 et option `imagine_c28_fixture`, déclarés fictifs. Trois anciens numéros existants, leurs articles et PDF existants : aucun corps éditorial modifié. Numéro d'ajout temporaire **32**. **Pas de commande payée C28 permanente ni de droit nouveau laissé sur un profil C09.** Les commandes et remboursements d'essai ont été retirés, profils/sessions/réglages/actions restaurés et relus. Capture publique : `recette-finale-pack.png`.

## Vérifier — commande parent

Depuis `C:\Users\Ced\imagine` :

```powershell
python -B wp/tests/demo/c28-verifier.py
python -B wp/tests/demo/c28-verifier.py --live
```

La première vérifie le paquet **hors réseau**, sans mutation ; la seconde ajoute uniquement une relecture gardée de `imagine-test-demo`, des sources, de la fixture et de l'état métier restauré. `reception.json` scelle les sources et preuves finales ; tout écart refuse. `PRET` signifie prêt à relire, pas clôture ni validation visuelle.

Rejeu autonome avec un **LABEL réellement neuf**, jamais en parallèle d'une autre recette de cette voie :

```powershell
python -B wp/outils/demo/c28-local.py parent-unitaire-NOM-NEUF
python -B wp/outils/demo/c28.py runtime parent-natif-NOM-NEUF
python -B wp/outils/demo/c28.py regressions parent-C14-NOM-NEUF
python -B wp/outils/demo/c28-recette.py parent-recette-NOM-NEUF
python -B wp/outils/demo/c28.py preservation parent-preservation-NOM-NEUF
```

`runtime` et `regressions` utilisent de vrais objets natifs dans un rollback vérifié. La recette navigateur est **temporairement mutante sur la seule démo** : formulaire produit, panier, `payment_complete()` fictif, remboursements natifs sans transfert, sessions, sélection du pack et une mutation de source C28. Préimage privée durable avant action et retour relu obligatoires ; aucun reset C09. Ne pas relancer les scripts de récupération historiques.

Commandes générales inchangées, déjà réellement exécutées après ajout des tests et avant PRET :

```powershell
.\wp\tests\preparer-image.ps1
.\wp\tests\rejouer.ps1
```

## Résultats constatés

- PHPUnit C28 : **2 tests / 18 assertions** ; natif C28 : **25/25 contrôles** ; complément C14 existant : **45/45**.
- Recette HTTP/navigateur : **200/200**, avant/après paiement pour acheteur/tiers/anonyme, articles et vrais PDF, compte ; ajout du quatrième refusé, retrait conservé, politiques C14 inchangées.
- **7 sorties non vides** de la fiche inspectées avec les **32 témoins C26** ; redirection de recherche inspectée ; **32 injections de réponse détectées** et **1 mutation de source détectée/restaurée**. Matrice C26 non étendue.
- **16 fichiers PHP** sans erreur de syntaxe. Image reconstruite, sortie **0**.
- Rejeu général : **1 189 tests / 36 512 assertions**, aucun échec/erreur/ignoré, **PASS** ; outils : **22 / 584 contrôles**, tous verts.
- Paquets : **12 vérifiés, 1 échec connu A-32 / A32_PARTIAL_EVIDENCE**, hors périmètre et inchangé.
- Réseau : **40 tentatives HTTP et 4 emails natifs/ambiants**, toutes bloquées avant transport ; **6 Gravatar admin** bloqués côté navigateur ; aucun tiers public chargé. Ce n'est pas un « zéro tentative ».

Les sources et compteurs définitifs sont ceux de `recette-finale.json`, `natif-final.json`, `c14-regressions-finales.json`, `preservation-finale.json` et `regression-finale.log`. `NOTE.md` détaille le choix standard, le point d'expansion du raccord C14, les reprises d'essais rouges restaurées exactement et les limites de crash/concurrence et de comparaison métier. Aucun paiement financier ni checkout fournisseur testé ; aucune validation visuelle ou juridique acquise.
