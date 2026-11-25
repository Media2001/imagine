# B-03 — Rejouer sans réensemencer

Depuis `C:/Users/Ced/imagine`. Aucun accès réel, Git, nettoyage de site, compte ou fixture. Le site fictif **imagine-test-demo** doit déjà être démarré et garder sa garde locale B00. Les transports B00/C08 existants sont utilisés tels quels ; aucune modification de l’outil de staging.

## Dépendances de test locales, sans installation globale

Node est déjà présent. Les six wheels publics verrouillés de B01 sont réutilisés **hors ligne** dans un environnement jetable sous le scratch Hermes :

```text
uv venv --no-python-downloads --python python C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests
uv pip install --python C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe --no-index --find-links production/B-01/validation --require-hashes -r production/B-01/validation/requirements.lock
```

Si l’environnement existe déjà, ne pas le recréer. Utiliser son Python pour les tests HTTP/HTML ; `PYTHONDONTWRITEBYTECODE=1` évite des écritures de cache dans les tests voisins. Les mots de passe sont lus uniquement en mémoire par le mécanisme HTTP privé déjà présent ; aucun cookie ni corps HTML connecté n’est enregistré.

## Dépôt ciblé et recette

```text
python wp/tests/demo/b03-work.py deploy release
C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe wp/tests/demo/b03-final.py
```

`deploy` n’envoie que six fichiers B03 du thème, parse les PHP et relit les SHA-256. Il sauvegarde les préimages dans `theme-before-<phase>.json` et ne touche pas aux extensions. Ne pas appeler le constructeur B00 global, les seeds C08/C09, les recettes mutatrices C12/C14 ou les fixtures du parent.

`b03-final.py` relit les six fichiers, exécute les dix assertions PHP B03 via le seul fichier `imagine-demo-build/b03-runtime.php`, les vrais HTTP, les tests Node et les régressions locales. Il utilise ensuite **l’exécuteur canonique T01** dans un conteneur éphémère isolé, montage du dépôt en lecture seule, réseau absent, sans site ni extension commerciale. Il ne passe pas par le balayage global d’orphelins de `rejouer.ps1`, pour ne pas interrompre un autre worker. Les reçus des contrôles navigateur anonymes déjà exercés sont liés aux mêmes octets CSS/JS/tokens/gabarit ; les manipulations pour les rejouer sont dans `A-VOIR.md`.

La commande obligatoire `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1` a été réellement exécutée avec succès : `preparer-image.txt`. Ce script n’a pas été modifié ; aucun nouveau paquet Composer n’est créé par B03. Si les manifests des bibliothèques changent, refaire cette préparation explicitement avant le rejeu.

## Historique TDD et incompatibilité attendue

- `http-red.json` → `http-button-green.json` : bouton réel et absence sans JS.
- `php-red.json` → `php-time-green.json` : durée serveur ; `php-boundaries-red.json` → `php-release.json` : mots adjacents entre paragraphes.
- `js-red-*.txt` → `js-green-*.txt`, puis `js-release.txt` : préférences, stockage, progression, parcours DOM et reprise.
- `css-red.txt` / `progress-css-red.txt` → `css-final.txt` et contrat local final : palettes et barre permanente.
- `local-regression.json` conserve le résultat brut des quatre anciens tests B01 : un échec est attendu, car B01 interdisait **tout JS**, alors que B03 en demande un. Le rejeu B03 remplace **en mémoire seulement cette assertion** par la liste fermée `assets/reading.js` ; les tests historiques sur disque ne sont pas modifiés. Les autres contrôles B01/C08 sont conservés.

`browser-narrow.json` conserve un premier contrôle où l’onglet était en arrière-plan et le bref délai ne laissait pas passer son animation-frame. Le contrôle final remet l’onglet au premier plan et vérifie progression/reprise : `browser-narrow-final.json`. Un appel de capture a aussi expiré ; il n’est pas utilisé comme preuve de réussite. Ce n’est ni un banc de navigateurs ni une certification WCAG.

## Standard utilisé

WordPress reste responsable de l’enqueue conditionnel et différé, du HTML et de la sortie autorisée C08. Le sur-mesure se limite au mode de présentation, car le brief demande un changement de classe local sans extension. Références officielles consultées et reçues dans `references-officielles.json` :

- `https://developer.wordpress.org/reference/functions/wp_enqueue_script/` — options `defer`, `in_footer`, sans dépendance.
- `https://developer.wordpress.org/reference/functions/is_singular/` — restriction aux articles (`post`).
- `https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage` — stockage par origine, persistance et possibilité de refus ; le script intercepte les erreurs.

La préférence de mouvement réduit est respectée sans déplacement animé. Les tests prouvent le fonctionnement du squelette, pas une validation graphique ni un GO de déploiement réel.
