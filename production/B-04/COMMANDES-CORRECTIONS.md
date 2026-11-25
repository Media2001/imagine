# B-04 — Vérification des corrections

Depuis `C:/Users/Ced/imagine` en bash, sans Git :

```bash
QA='C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe'
"$QA" wp/outils/demo/b04-unit.py parent
"$QA" wp/tests/demo/test_b04_http_contract.py
"$QA" wp/tests/demo/b04-corrections.py http parent
"$QA" wp/tests/demo/b04-http.py parent-corrections
"$QA" wp/tests/demo/b04-catalogue-test.py parent-corrections
"$QA" wp/tests/demo/b04-work.py php parent-corrections
"$QA" wp/tests/demo/b04-safety.py
```

- Le premier appel utilise l'image T01 déjà préparée : paquet racine `imagine-site`, configuration C12 distincte, sous-suite B04. Dépôt monté en lecture seule, réseau coupé, aucun port, propriétaire du conteneur contrôlé avant suppression et absence relue. Les JUnit sont récupérés par PHP/stdin : `docker cp` ne voit pas les fichiers tmpfs de ce démon. Les sources testées viennent du dépôt, pas du cache de l'image.
- `b04-corrections.py http` utilise les comptes synthétiques existants V-DEC et P-NUMERO. Il ouvre temporairement la découverte pour le témoin C12, puis restaure exactement les options/état/confirmation et les relations thématiques. Il met temporairement la date du numéro fictif 11 dans le futur puis après sortie, sans créer ni modifier une commande/paiement. La possession attendue vient de l'achat natif préexistant, jamais de la décision PDF. **Sérialiser ces recettes avec toute autre mutation de la démo.**
- Le rejeu HTTP ordinaire refuse immédiatement tout numéro/article témoin ou marqueur de corps vide. Les marqueurs restent en mémoire ; reçus sans corps privé, cookies ni identifiants.
- La décision à la **seconde exacte de sortie** est éprouvée par PHPUnit avec le vrai raccord et moteur C06 ; les GET natifs exercent avant/après la sortie, sans changer l'horloge serveur.

## Mesure et navigateur, si nécessaire

```bash
"$QA" wp/tests/demo/b04-queries.py
'C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe' -c "import sys,runpy;sys.path.append('C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Lib/site-packages');runpy.run_path('wp/tests/demo/b04-browser.py',run_name='__main__')"
```

La mesure crée vingt articles et leur numéro **propres B04**, puis retire leurs 21 IDs exacts et son contrôleur dans `finally`, avec relecture. Ne pas l'exécuter en parallèle des autres recettes natives. Le navigateur réutilise Playwright installé, sans paquet ajouté ni achat déclenché.

## Installation ciblée, uniquement en cas de besoin

```bash
"$QA" wp/tests/demo/b04-corrections.py deploy parent-unique
```

Cinq fichiers seulement, sauvegarde préalable et empreintes relues : deux adaptateurs, deux fichiers du thème, le mu-plugin issu de `wp/outils/demo/b04-preview.php`. Le nom de phase doit être inédit pour ne pas écraser de préimage. Aucun bootstrap, bibliothèque close, reset C09/C14/C15 ou réglage de visibilité Woo n'est déployé.

`wp/tests/preparer-image.ps1` a été exécuté sans édition, sortie 0 (`preparer-image-corrections.log`). Le runner global n'a pas été modifié ni déclaré rejoué dans cette correction ; le parent peut le lancer par `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/rejouer.ps1`.

Le contrôle PSR-12 strict retrouve **33 défauts de forme préexistants, zéro nouveau** dans les trois fichiers hérités (`phpcs-baseline-comparison.json`). Ce n'est pas un lint strict vert ; les fichiers ne sont pas reformatés hors correction. Les nouveaux raccords passent la syntaxe PHP native avant téléversement.
