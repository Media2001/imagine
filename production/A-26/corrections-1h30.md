# A-26 — Corrections, file du 27 novembre 2026 à 1 h 30

**Aucun fichier commun, gardien ou import modifié. Aucun PHP Windows, Docker ou WSL exécuté. Aucun sceau renouvelé, aucun PRET posé.** Lecture complète du brief A-26, de sa fusion, de la doctrine et de la consigne permanente ; priorité donnée au code, réception commune après stabilisation A-28. Écritures bornées à `wp/outils/bascule/a26/`, `wp/tests/a26/` et `production/A-26/`.

## Résultat par instruction

- **I1 — code et bancs livrés, preuve native encore attendue.** `Analysis::htmlUrls()` lit les vraies balises et attributs avec `WP_HTML_Tag_Processor::next_token()` / `get_attribute()`. Aucune extraction HTML ni d'attributs par regex, aucun repli vers l'ancien scanner, aucun rendu ou réseau. La regex restante ne reconnaît que les URL seules des jetons texte ; commentaires, exemples PRE/CODE et texte brut de SCRIPT ne sont pas scannés comme du HTML. Liste fermée de ressources conservée.
- **Deux contre-exemples préparés RED/GREEN dans le vrai WordPress du banc parent.** `html-unit.php` exige YouTube pour `<iframe title="a > b" src="https://www.youtube.com/embed/…">` et aucun Vimeo pour `<img title='src="https://vimeo.com/123"' src="/local.png">`. Les trois anciennes assertions HTML quittent la banque PHP pure et sont conservées dans cette banque native, sans doublure de parseur. La banque pure d'agrégation, son inclusion sans extensions/écritures et son témoin de neutralisation restent dans le runner.
- **Rapports classique et HPOS préparés.** Le seed ajoute les deux articles, liés aux numéros retenus dans les trois modes A-16. Le banc remplace uniquement la méthode HTML, dans sa copie jetable `/subject/a26/Analysis.php`, par la méthode d'origine conservée dans `html-regex-before.txt`, puis restaure ses octets exacts même en cas d'exception. RED attendu : total YouTube=3, Vimeo=2 ; dix derniers YouTube=1, Vimeo=1. GREEN attendu : total YouTube=4, Vimeo=1 ; année 2026 YouTube=2 et Vimeo=0 ; dix derniers YouTube=2, Vimeo=0. Les autres services restent soumis aux tableaux exacts existants. Les résultats RED restent identifiés comme rouges ; pas de sortie PHP inventée ici.
- **Vérificateur renforcé.** Il exigera les deux échecs HTML nommés, la banque native verte, les témoins de rapports annuels et des trois sélections, le hash restauré et les nouveaux nombres dans les rapports de chaque magasin. Les fichiers attendus sont `<magasin>-html-red-unit.json`, `<magasin>-html-unit.json` et `<magasin>-html-red-green.json` ; ils seront produits par le parent, pas présents comme résultats exécutés de cette correction.
- **M1 — partie propre corrigée, ligne commune déléguée.** `readme-ajout.txt` contient les deux lignes exactes corrigées. `readme-parent.delta.patch` remplace **une seule ligne de pointage**, à la ligne 98 du mode d'emploi réel `wp/tests/a02-audit/README.md`, vers `wp/outils/bascule/a26/README.md`. La ligne de commande reste identique et unique. Application vérifiée **en mémoire uniquement** : aucune écriture du fichier commun. Le README propre pointe maintenant vers ce rapport courant et emploie les chemins complets de l'import ; les anciennes finalisations/réceptions sont explicitement historiques.
- **B1 — préparation faite, levée différée au parent conformément à la file.** `run.py:DEPS` exige explicitement `wp/outils/staging/form-policy.json`, en plus de l'arbre staging déjà inventorié. Son absence est un refus, pas un gel silencieusement réduit. Le dernier manifeste local Python contient réellement cette dépendance. Les vieux `dependencies.json`, manifests, reçus et sceaux ne sont ni remplacés ni réputés actuels. Le parent rejouera une seule fois sur l'import A-28 final.
- **Défaut retenu :** `illisible` hors schéma Site Kit qualifié est conservé ; aucune nouvelle affirmation `non`.

Références HTML officielles consultées et archivées avec empreintes : `production/A-26/standard/html-tag-processor-sources.json` et ses trois fichiers HTML. Le contrôle du standard installé préparé dans `standard.php` vérifiera également le vrai lecteur HTML du cœur.

## Exécutions réelles Windows/Python

Interpréteur mesuré : **`C:/Python314/python.exe`, Python 3.14.6**, plateforme win32. Matrice finale après la dernière modification des sources : **30 tests réussis en UTF-8, 30 en cp1252**, aucun échec, sorties console UTF-8/mode 1 et cp1252/mode 0 mesurées ; locale système cp1252 dans les deux cas. Les sous-processus Python fixent leur encodage. `native_executed=false`, `readiness_claimed=false`.

```sh
# Depuis C:/Users/Ced/imagine ; résultats externes au dépôt.
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a26/matrix.py --python-only --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-corrections-1h30/python-final3
PYTHONIOENCODING=utf-8 PYTHONUTF8=1 C:/Python314/python.exe -B wp/tests/a26/verify.py --python-only --packet=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-corrections-1h30/python-final3
```

Les deux commandes ont retourné 0 ; vérificateur : `PYTHON_ONLY_VERIFIED_NATIVE_PENDING`, `python_tests_per_console=30`. Logs, empreintes des sources/dépendances et mesures d'encodage : dossier scratch ci-dessus (`windows-matrix.json`, `utf8/`, `cp1252/`). C'est une validation Python, **pas** une preuve des comportements HTML en PHP.

Pendant le contrôle final, le reçu précédent `python-final2` a été refusé avec `A26_SOURCE_DRIFT` : **aucune source A-26 n'avait changé**, mais `wp/outils/staging/lib.php` avait évolué de `32b0f658…` à `20808706…` sous la responsabilité de l'autre lot. Ses empreintes n'ont pas été remplacées. Une matrice Python entière neuve `python-final3` a alors été réellement rejouée et vérifiée, avec les résultats ci-dessus. Toute nouvelle évolution commune peut de nouveau périmer ce reçu ; ce n'est pas un gel de l'import ni une réception native.

RED Python observé avant corrections : les trois contrats initiaux (API native présente, dépendance form-policy obligatoire, chemin README explicite) ont réellement échoué, exit 1 ; journal `C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-corrections-1h30/python-red.log`. Cela ne remplace pas le RED PHP encore réservé au parent.

Contrôles supplémentaires réellement exécutés :

- `verify.py --python-only --require-shared-doc` sur le premier rejeu : exit 1 attendu, **`A26_SHARED_DOC_PENDING`**, car le parent n'a pas encore remplacé sa ligne commune ; aucun contrôle affaibli.
- `C:/Python314/python.exe -B wp/tests/a26/verify.py` sur l'ancien paquet : exit 1 attendu, **`A26_SOURCE_DRIFT`** ; journal scratch `historical-rejection.log`.
- **152 fichiers** du paquet historique `production/A-26/preuves/final/` exactement identiques au manifeste historique, sans ajout ni retrait. Les trois snapshots officiels correspondent à leurs SHA-256. `PRET` absent.
- Delta documentaire : ancienne ligne commune présente une fois, nouvelle absente, commande présente une fois ; remplacement simulé donnant les deux lignes exactes chacune une fois. Le contrôle global de la documentation reste donc ouvert jusqu'à l'intervention du parent.

## Réception restant au parent, après A-28

1. Appliquer le delta documentaire d'une ligne, relire les deux lignes exactes une fois chacune ; ne pas ajouter un deuxième bloc A-26.
2. Si nécessaire, finaliser le style PHP dans le conteneur réservé, **avant** le gel ; aucun lint/PSR-12 de ces corrections n'a été exécuté par ce worker.
3. Sur dépendances communes stabilisées, préparer l'image et rejouer la matrice complète, puis son vérificateur et les portes communes. Commandes A-26, dossiers neufs obligatoires :

```sh
C:/Python314/python.exe -B wp/tests/a26/style.py --fix --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-corrections-style-parent
C:/Python314/python.exe -B wp/tests/a26/matrix.py --output=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-corrections-native-parent
C:/Python314/python.exe -B wp/tests/a26/verify.py --packet=C:/Users/Ced/AppData/Local/hermes/cache/scratch/a26-corrections-native-parent --require-shared-doc
```

Ne pas recopier de résultats historiques dans ce nouveau paquet. Le contrôle `--unit-only` reste purement PHP d'agrégation : les contre-exemples HTML exigent la matrice **complète** avec le cœur WordPress, classique et HPOS. Le parent conserve la responsabilité de la préparation commune, du futur paquet unique, de ses gates et de son sceau ; aucun de ces résultats n'est présumé ici.

## Fichiers

- Modifiés : `wp/outils/bascule/a26/{Analysis.php,README.md}` ; `wp/tests/a26/{inside.py,run.py,seed.php,standard.php,unit.php,verify.py}` ; `production/A-26/readme-ajout.txt`.
- Créés : `wp/tests/a26/{html-unit.php,html_mutation.py,html-regex-before.txt,test_corrections.py}` ; `production/A-26/readme-parent.delta.patch`, ce rapport et les quatre fichiers de références HTML sous `production/A-26/standard/`.
- La preuve historique et ses documents de finalisation, le verrou parent, le README commun, l'import, le gardien, Git, la voie 2, les archives, sites et comptes n'ont pas été modifiés.

**Limite explicite :** aucun RED/GREEN HTML/PHP ni rapport natif nouveau exécuté par ce worker. B1 et la réception native d'I1 restent ouverts jusqu'au rejeu parent ; M1 commun attend le delta. Aucun nouvel arbitrage métier ou accès au réel demandé. L'extracteur web étant indisponible, les références officielles ont été récupérées par HTTPS direct ; ce problème n'a pas empêché les tests Python.
