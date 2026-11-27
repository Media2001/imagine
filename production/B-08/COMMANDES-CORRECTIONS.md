# B-08 — commandes exécutées pour les corrections

Répertoire : `C:/Users/Ced/imagine`. Shell Bash Windows. Interpréteur réellement relevé : Python 3.11.15 ; runtime isolé PHP 8.2.33 / PHPUnit 11.5.58. Aucun Git, verrou ou file manipulé.

## Rouge avant code

Chaque ligne a été exécutée avec le préfixe exact `PYTHONIOENCODING=utf-8` :

| Commande | Sortie réelle |
|---|---|
| `python -B wp/outils/demo/b08-local.py corrections-red-slash` | **1** ; 7 tests, 182 assertions, 1 échec, 0 erreur ; POST valide refusé. Le bouchon avait été corrigé avant cette exécution, pas le code applicatif. |
| `python -B wp/outils/demo/b08-local.py corrections-red-https` | **1** ; 8 tests, 191 assertions, 1 échec, 0 erreur ; URL HTTP acceptée. |
| `python -B wp/outils/demo/b08-corrections.py runtime corrections-red-reprise` | **1** ; troisième item interrompu, rejeu « Collision menu B08 », restauration exacte verte. |
| `python -B wp/outils/demo/b08-corrections.py runtime corrections-red-cibles-oracle cibles` | **1** ; page compte supprimée dans la transaction, URL retombant sur l’accueil ; autres contrôles verts ; restauration exacte. |

Les exécutions intermédiaires restent dans `corrections-green-*`, `corrections-reprise-precoce.json` et `historique-corrections-essai1/`. Elles ne qualifient pas le paquet final. Un premier test de collision utilisait une variable écrasée par le `require` et un premier oracle regardait la méta URL vide des items natifs plutôt que leur vraie URL : corrigés dans les tests, jamais présentés comme défauts applicatifs. La première campagne de mutations s’est arrêtée sur un TypeError du nouveau test d’export vide : assertion de présence ajoutée avant lecture, campagne entière rejouée ensuite avec 0 erreur PHP.

## Qualification finale

**Préfixe exact de chaque commande Python ci-dessous : `PYTHONIOENCODING=utf-8`.** Les deux mutants seed sont exécutés séparément avec contrôle explicite de leur retour **1** ; leur faux métier est exigé dans le vérificateur final.

| Commande | Résultat |
|---|---|
| `python -B wp/outils/demo/b08-gates.py prepare corrections-final-preparation` | **0** ; image reconstruite par le script existant et vérifiée hors ligne. |
| `python -B wp/outils/demo/b08-local.py corrections-final-local` | **0** ; 8 tests, 194 assertions. |
| `python -B wp/outils/demo/b08-mutations.py corrections-final-mutations` | **0** ; 14 mutants produisant chacun **1**, échecs métiers positifs, 0 erreur PHP. |
| `python -B wp/outils/demo/b08-gates.py regression corrections-final-canonique` | **0** ; 1 153 tests, 36 075 assertions, 0 échec/erreur/ignoré ; 22 outils, 582 contrôles ; 9 paquets, 0 échec (A-30 hors rejeu : déclaration absente, limite du runner). |
| `python -B wp/outils/demo/b08-corrections.py runtime corrections-final-reprise` | **0** ; 5 contrôles, interruptions après sauvegarde et avant rattachement ; reprise de 15 items sans doublon ; état initial restauré. |
| `python -B wp/outils/demo/b08-corrections.py runtime corrections-final-cibles cibles` | **0** ; 7 contrôles ; 4 cibles absentes sans URL, témoins positifs préalables ; état restauré. |
| `python -B wp/outils/demo/b08-corrections.py runtime corrections-final-collisions collisions` | **0** ; 10 contrôles, cinq collisions refusées sans création ; état restauré. |
| `python -B wp/outils/demo/b08-corrections.py runtime corrections-final-mutant-item collisions item-etranger` | **1 attendu** ; seul `item_refuse=false`, toutes les autres gardes et restaurations vraies. |
| `python -B wp/outils/demo/b08-corrections.py runtime corrections-final-mutant-cible cibles cible-absente` | **1 attendu** ; seul `compte_sans_url_si_cible_absente=false`, reste et restauration vrais. |
| `python -B wp/outils/demo/b08-corrections.py deploy corrections-final-deploiement` | **0** ; deux fichiers applicatifs téléversés puis relus sur la seule démo ; bootstrap préservé. |
| `python -B wp/outils/demo/b08.py seed corrections-final-pages-menu` | **0** ; deux rejeux égaux ; mêmes 10 pages et 15 items que le paquet initial. |
| `python -B wp/outils/demo/b08-recette.py corrections-final-http` | **0** ; 35 contrôles HTTP/natifs ; nom/sujet à antislash exacts du POST au détail admin et au callback natif d’export ; nettoyage et restauration exacts. |
| `python -B wp/outils/demo/b08-corrections-finaliser.py` | **0** ; 18 gardes vertes, syntaxe PHP native et octets livrés vérifiés, seed retiré et absence relue ; paquet scellé puis vérificateur exécuté. |
| `python -B production/B-08/verifier.py` | **0**, rejoué après sceau puis après PRET ; sources, preuves, comptes et signatures vérifiés sans accès au site ni réseau. |

Les wrappers ont réellement exécuté ces commandes exactes, sans argument de script ajouté :

```text
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1
```

`b08-gates.py standard corrections-standard-officiel` a aussi été exécuté (préfixe UTF-8, `python -B`) : quatre sources officielles WordPress, quatre HTTP 200. Une extraction via l’outil web ne supportait pas le backend recherche seul ; repli effectif sur le script officiel déjà existant, aucun résultat inventé.

## Fichiers de code et documentation changés

- `wp/plugins/imagine-site/{Sujet.php,Soutenir.php,README.md}`.
- `wp/plugins/imagine-site/tests/{SujetWPStubs.php,SujetAdapterTest.php,SoutenirAdapterTest.php}`.
- `wp/outils/demo/{b08-seed.php,b08-recette.py,b08-mutations.py}` ; nouveaux `b08-corrections.py`, `b08-corrections-finaliser.py`.
- `wp/tests/demo/b08-horslive.php` ; nouveaux `b08-seed-reprise.php`, `b08-seed-cibles.php`, `b08-seed-collisions.php`.
- `production/B-08/{A-VOIR.md,NOTE.md,verifier.py,PRET}` ; nouveaux `verifier-corrections.py`, copie historique `verifier-historique.py`, archive du PRET initial, reçus/logs `corrections-*` et archive d’essai. Aucun fichier du thème modifié par ces corrections.
- Rapports `files/rapports/2026-11-27-05h03-V2.md` et `files/rapports/2026-11-27-05h39-V2.md`.

Sceau courant : `production/B-08/corrections-final.json`, SHA-256 `834adeacaaef1acce1a509bf20b981222900f47e9ed4e559e40a280de7d578b0` ; 29 fichiers de manifeste et 33 pièces de preuve. Les préimages contenant sessions/base restent privées dans le scratch, jamais dans le dépôt.

## Limites

Validation visuelle de Ced attendue ; colonne de confort admin non ajoutée. Pas de paiement, de don, de mail, de compte/service réel, d’intégration CoopHub ou de production. Le site local reste en HTTP : **HTTPS seul concerne l’adresse sortante de prise de parts**, pas une migration TLS du serveur fictif. Les interruptions sont injectées par exception dans les hooks réels, pas par arrêt forcé de Docker. Les horodatages techniques des items du lot peuvent être réécrits par le seed ; identifiants, structure et URL restent identiques, objets hors lot strictement préservés. C-26 reste à qualifier séparément par le parent.

Observation hors périmètre, non corrigée : `Agenda.php:131-134` (B-07 clos) écrit aussi du texte libre dans `meta_input` sans `wp_slash` ; risque analogue à faire confirmer dans un lot autorisé, **pas une reproduction ni une réouverture de B-07 ici**.
