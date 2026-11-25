# C13 — commandes réellement exécutées et rejeu parent

Répertoire de travail exact : `C:/Users/Ced/imagine`. Shell bash ; `python`, pas `python3`. Toutes les commandes ci-dessous ont été exécutées, certaines répétées pendant les cycles RED/GREEN. Aucun Git.

## Tracers TDD du premier livrable (historique)

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --php-only
```

RED réellement observé, code 1 : raccord absent ; puis raccord natif absent ; puis témoins positifs/formules absents ; puis méthode de calcul historique absente ; puis modification de création après clôture altérant le gel. Chaque ajout/correction a ensuite été exercé en GREEN. Le test de suppression native a, lui, immédiatement confirmé le comportement natif déjà présent ; aucun correctif de suppression inventé.

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy --php-only
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy
```

Déploiements ciblés relus octet pour octet. La première recette HTTP a réellement échoué : page absente puis référent redirigé par WooCommerce vers Mon compte. Le filtre Woo n'a été ouvert que pour les deux routes de l'écran C13 et sa capacité, sans élargir les rôles. Rejeu ensuite vert pour `e-abo` et `e-admin`.

## Rejeu technique et gate d'acceptation

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --require-complete
```

Résultat technique final après corrections : **10 tests purs / 30 assertions**, puis **75 contrôles PHP/HTTP**, dont deux exports HTTP non vides de **2 lignes**. Nonce/capacité/méthode, format C10, injection, journal/panne conservés ; cadeau/groupe/renouvellement/gel persistant ajoutés. Octets installés relus ; sources B02/C14/fermées et états C09/rôles/options/contenus préservés.

La commande technique sort en **0** ; la commande stricte sort en **2**, avec `recette_complete=false` : **12/12 souscriptions C09 sans date de paiement validé ; A-SANSMAIL non inclus ; offert/groupe natifs absents**. Ce n'est pas un échec masqué ni un succès complet.

## Banc pur autonome et intégration dans le runner autorisé

```bash
PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13-unit.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

Résultats : pur C13 **10 tests / 30 assertions**, code **0** ; préparation **0**, image vérifiée ; T01 **1010 tests / 33978 assertions**, **0** échec/erreur/ignoré, code **0**. Paquet `imagine-site` : **46 tests / 230 assertions**, comprenant C11 conservé et C13. Découverte automatique via `phpunit.xml` racine, `composer.json` et lock dans le paquet autorisé ; aucune modification du runner fermé ni de T01. Dépendances publiques verrouillées seulement pendant préparation ; rejeu hors réseau, montage du dépôt en lecture seule et nettoyage vérifié.

Corrections RED/GREEN observées : classe pure absente ; bénéficiaires remplacés à tort par le payeur ; renouvellement absent ; calendrier incomplet non fermé ; rejeu contradictoire non refusé ; paiement futur accepté. Intégration native : fin WCS à `0`, intervalle chaîne `"1"`, dernier paiement recopié par WCS à ne pas réutiliser comme paiement initial ; nonce d’export distinct du nouveau nonce de réglages. Rejeux après corrections et formatage final.

Pour réinstaller uniquement C13 : `PYTHONDONTWRITEBYTECODE=1 python wp/outils/demo/c13.py --deploy --require-complete`, réellement exécuté : technique verte, **2** sur acceptation C09. Sans `--deploy`, le parent ne réinstalle pas le code ni les témoins persistants ; les recettes créent/nettoient leurs objets jetables et journalisent les vrais exports.

## Livrables absolus

- `C:/Users/Ced/imagine/wp/plugins/imagine-site/EnvoiNatif.php` — nouveau raccord C01/C07 et relevés natifs datés.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/ListeEnvoiAdmin.php` — nouvel écran natif et contrôleur CSV/journal.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/EnvoiRegles.php` — règles pures, blocs et gel historique injectables.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/EnvoiRelations.php` — liens cadeau/attributions Memberships, paiements et renouvellements natifs.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/{composer.json,composer.lock,phpunit.xml,phpunit.c13.xml,tests/EnvoiReglesTest.php,tests-c13/bootstrap.php}` — paquet autonome, découvert par T01.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/README.md` — documentation C13 ajoutée.
- `C:/Users/Ced/imagine/wp/outils/demo/c13.py` — nouveau déploiement/rejeu borné à la démonstration.
- `C:/Users/Ced/imagine/wp/outils/demo/c13-fixture.php` — deux témoins supplémentaires C13, sans toucher C09.
- `C:/Users/Ced/imagine/wp/outils/demo/c13-unit.py` — rejeu pur hors réseau, sans site.
- `C:/Users/Ced/imagine/wp/tests/demo/c13-corrections-runtime.php` — nouveaux témoins natifs jetables et nettoyage relu.
- `C:/Users/Ced/imagine/wp/tests/demo/c13-runtime.php` — recette PHP native et contrats temporels.
- `C:/Users/Ced/imagine/wp/tests/demo/c13-http.py` — vraie recette des quatre profils, anonyme et exports.
- `C:/Users/Ced/imagine/production/C-13/` — `A-VOIR.md`, `COMMANDES.md`, `references.md`, `resultats.json`, `resultats-purs.json`, `RAPPORT.md` ; PRET laissé au parent.

Aucun bootstrap B02/C14, fichier de bibliothèque close, adaptateur C10, profil C09, verrou ou file modifié. Aucun fichier de thème modifié. Les tests natifs utilisent de nouveaux objets fictifs jetables et restaurent leurs options/adresses temporaires ; états C09 protégés et nettoyage relus. Aucun compte, paiement ou transport réel. Réserves et propositions pour Claude : `RAPPORT.md`.
