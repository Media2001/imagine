# A-16 — relais instructions 2 à 5, 26/11/2026 07h54 CET

**Corrections réalisées ; intégration des refus encore nécessaire. Lot non clos.** Aucun nouveau PRET ni scellement, aucun paquet supplémentaire dans le dépôt. Le PRET et les manifestes préexistants décrivent l'ancienne livraison et sont périmés pour ces sources ; le parent les remplacera après intégration. Aucun Runtime.php, `inventorier-numeros` ni test commun de refus modifié par cet enfant.

## Réalisé

- `Inventory.php` : présence indépendante de l'emplacement ; `racine_privee` locale déclarée et contrôlée, PDF privé présent/absent avec `pdf_public=false`, sans chemin en sortie. Parent symbolique détecté même si le fichier est absent.
- `Mapping.php` : ensemble exact des clés de `liaison`, ordre indifférent ; racine privée facultative, syntaxe locale stricte.
- `Command.php` : un seul encodage après les deux empreintes.
- Banc : deux numéros supplémentaires de même date ; article publié rattaché à janvier, exclu de N=2, plus un vrai orphelin ; PDF privés présent/absent. Vérificateur renforcé.
- Exemple et README A16 documentés ; lignes de refus ajoutées concurremment conservées. Contrat des deux lignes du README partagé conforme, sans empreinte globale.

## Preuves réelles — scratch, non scellées

Racine `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a16-final-owned-py3147-20261126/` :

- `windows-matrix.json`, `*-environment.json` : vrai Python Windows **3.14.7**, locale cp1252 ; stdout/stderr cp1252 et UTF8=0 sur la ligne cp1252.
- Chaque contexte UTF-8/cp1252 : **23/23 unités PHP PASS**, **3/3 tests Python PASS** ; `result.json` natif classic/HPOS **64 PASS, 4 FAIL**, uniquement l'attente de refus ci-dessous et les deux exceptions associées. Nouveaux cas, variantes post_parent/taxonomie, répétition, empreintes base complète/fichiers et confinement passent avant ce conflit.
- `runner.json` : suppression du conteneur exact vérifiée, sources et dépendances stables ; seul `native_return` échoue.
- `style/style.json` : sortie **0**, PSR-12 **0 erreur/0 avertissement**.
- `preparation.json`, `preparation.log` : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1`, sortie **0**, image vérifiée après les nouveaux tests. Avertissement natif du thème sans tests conservé.
- `current-source-hashes.json` : les **14 sources A16** correspondent aux deux snapshots exécutés ; bases avant/après égales sur les deux stockages dans les deux contextes.

Commande matrice exécutée : `C:/Users/Ced/AppData/Local/hermes/tools/python-3.14.7+20260901-win32-x64/python.exe -B C:/Users/Ced/AppData/Local/hermes/cache/scratch/a16-final-integration-20261126.py`. Commandes enfants exactes et retours dans `windows-matrix.json`. Le premier essai employait réellement **3.14.6** (`C:/Python314/python.exe`) ; historique scratch remplacé par cette matrice 3.14.7.

TDD sous la racine scratch : `a16-r2-red-20261126/unit.json` (ordre inversé FAIL), puis `a16-r2-green-20261126` ; `a16-r1-red-20261126/result.json` (racine privée refusée classic/HPOS), cas privés verts ensuite ; `a16-r5-red-20261126/unit.json` (double encodage FAIL), puis unités vertes. `a16-r3-mutations-20261126/result.json` : deux mutants réellement détectés en classic ET HPOS, ID croissant → `equal_dates_id_descending` FAIL ; orphelins limités à N → `excluded_number_article_not_orphan` FAIL. Mutants et essais intermédiaires hors dépôt.

## Action parent avant PRET

1. **Conflit localisé** dans `wp/tests/a16/inside.py`, assertion `absent_mapping_key_named` : attend encore `A16_MAPPING_KEY_ABSENT {"key":"absent_key"}`, Runtime concurrent ne rend que le code. Aligner sur le seul code suivi d'un saut de ligne ; je n'ai pas changé cette assertion. Bloc uniquement déplacé après les empreintes pour permettre la preuve nominale complète. Détail fermé du drop-in autorisé et passant.
2. Après fin des écritures refus, rejouer les deux contextes complets, style et éventuel gate global partagé ; récolter le **seul dernier paquet vert** dans `production/A-16/preuves/final`.
3. Finaliser manifestes, vérificateur du paquet, LIVRAISON/verification.json puis PRET. Aucun PASS global revendiqué ici.

Modifiés par cet enfant : `wp/outils/bascule/a16/{Inventory.php,Mapping.php,Command.php,correspondance.exemple.json,README.md}`, `wp/tests/a16/{unit.php,seed.php,inside.py,verify.py}`, cette note et `files/rapports/2026-11-26-07h54-A16.md`.

