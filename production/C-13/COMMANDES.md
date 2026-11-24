# C13 — commandes réellement exécutées et rejeu parent

Répertoire de travail exact : `C:/Users/Ced/imagine`. Shell bash ; `python`, pas `python3`. Toutes les commandes ci-dessous ont été exécutées, certaines répétées pendant les cycles RED/GREEN. Aucun Git.

## Tracers TDD

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

Résultat technique réel : **47 assertions PHP/HTTP**, dont deux exports HTTP non vides de **2 lignes**, injection neutralisée, nonce/capacité/méthode contrôlés, format C10 lu, journal relu et panne du journal exercée. Préservation des sources installées, manifestes, C09, rôles, réglages et contenus contrôlée.

La commande technique sort en **0** ; la commande stricte sort en **2**, avec `recette_complete=false` : **12/12 souscriptions C09 sans date de paiement validé ; A-SANSMAIL non inclus ; offert/groupe natifs absents**. Ce n'est pas un échec masqué ni un succès complet.

## Non-régression locale

```bash
PYTHONDONTWRITEBYTECODE=1 python -c "import sys,unittest,pathlib;sys.path[:0]=[str(p) for p in pathlib.Path('production/B-01/validation').glob('*.whl')];s=unittest.defaultTestLoader.discover('wp/tests/demo',pattern='test_*.py');r=unittest.TextTestRunner(verbosity=1).run(s);print('UNITAIRES',r.testsRun,'SUCCES',r.wasSuccessful());sys.exit(not r.wasSuccessful())"
```

Résultat réellement obtenu : **33 tests, OK**. Wheels B01 lues seulement ; aucune installation, aucun réseau de dépendances.

## Livrables absolus

- `C:/Users/Ced/imagine/wp/plugins/imagine-site/EnvoiNatif.php` — nouveau raccord C01/C07 et relevés natifs datés.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/ListeEnvoiAdmin.php` — nouvel écran natif et contrôleur CSV/journal.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/imagine-site.php` — chargement des deux classes ; C11/C12 conservés.
- `C:/Users/Ced/imagine/wp/plugins/imagine-site/README.md` — documentation C13 ajoutée.
- `C:/Users/Ced/imagine/wp/outils/demo/c13.py` — nouveau déploiement/rejeu borné à la démonstration.
- `C:/Users/Ced/imagine/wp/outils/demo/c13-fixture.php` — deux témoins supplémentaires C13, sans toucher C09.
- `C:/Users/Ced/imagine/wp/tests/demo/c13-runtime.php` — recette PHP native et contrats temporels.
- `C:/Users/Ced/imagine/wp/tests/demo/c13-http.py` — vraie recette des quatre profils, anonyme et exports.
- `C:/Users/Ced/imagine/production/C-13/` — `A-VOIR.md`, `COMMANDES.md`, `references.md`, `resultats.json`, `RAPPORT.md`, `PRET`.

Aucun fichier de bibliothèque close, adaptateur C10, profil C09, verrou ou file de travail n'est modifié. Les mutations de démonstration se limitent au code chargé, aux deux témoins C13, aux relevés C13 et au journal C13 ; le témoin de suppression temporaire est supprimé et son nettoyage relu.
