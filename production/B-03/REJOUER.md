# B-03 — Rejouer sans réensemencer

Depuis `C:/Users/Ced/imagine`. Aucun accès réel, Git, nettoyage de site, compte ou fixture. Le site fictif **imagine-test-demo** doit déjà être démarré et garder sa garde locale B00. Les transports B00/C08 existants sont utilisés tels quels ; aucune modification de l’outil de staging.

## Dépendances de test locales, sans installation globale

Les interpréteurs déjà installés ont été retrouvés et exercés, sans nouveau paquet :

- **HTTP/HTML et final** : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe` (BeautifulSoup 4.14.3, html5lib 1.1).
- **Navigateur** : `C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe` (Playwright et Chromium existants).

Le Python par défaut et le venv Hermes n’ont pas `html5lib` : **ne pas les utiliser pour le final ou HTTP**. Le venv B03 n’a pas Playwright : ne pas l’utiliser pour le navigateur. Ne recréer aucun environnement ; aucun paquet n’a été ajouté pendant les corrections. Node est déjà présent. L’option `-B` évite les caches Python dans les tests voisins. Les identifiants fictifs restent lus en mémoire ; aucun cookie, mot de passe ou corps connecté n’est enregistré.

## Dépôt ciblé et recette

```text
C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe -B wp/tests/demo/b03-work.py php corrections
C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe -B wp/tests/demo/b03-http.py corrections
C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -B wp/tests/demo/b03-colors.py corrections
C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe -B wp/tests/demo/b03-final.py
```

Ces commandes ont réellement réussi. Ne pas redéployer pour vérifier : les corrections n’ont envoyé que `assets/reading.css` et `assets/reading.js`, relus dans `deploy-corrections.json`, préimages dans `theme-before-corrections.json`. Les quatre autres fichiers B03 sont relus mais pas renvoyés. Ne pas appeler le constructeur B00 global, le `deploy release` historique, les seeds C08/C09, les recettes mutatrices C12/C14 ou les fixtures du parent.

`b03-final.py` relit les six fichiers, exécute les dix assertions PHP B03 via le seul fichier `imagine-demo-build/b03-runtime.php`, les 43 contrôles HTTP, les 8 tests Node et les 15 tests locaux. Il utilise ensuite **l’exécuteur canonique T01** (1 012 tests / 34 006 assertions) dans un conteneur éphémère isolé, dépôt en lecture seule, réseau absent, sans site ni extension commerciale et sans balayage d’orphelins. Les 77 contrôles navigateur de `browser-colors-corrections.json` sont liés aux SHA-256 actuels du CSS/JS : les anciens reçus ne servent pas à valider les nouveaux octets. `preservation-corrections.json` compare les empreintes préalables de `corrections-before.json` : seuls les deux assets changent, ni contenus, métadonnées, commandes, dates, extensions ni autres sources. Ne jamais recréer cette photographie après coup pour masquer une divergence.

La commande obligatoire `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1` a été réellement exécutée avec succès : `preparer-image.txt`. Ce script n’a pas été modifié ; aucun nouveau paquet Composer n’est créé par B03. Si les manifests des bibliothèques changent, refaire cette préparation explicitement avant le rejeu.

## Historique TDD et incompatibilité attendue

- **Corrections B03-C1** : `browser-colors-red.json` → `browser-colors-corrections.json`, paragraphe noir et bloc rouge, ≥ 4,5:1 dans les trois palettes à 390 et 1440 px. Sondes DOM client temporaires, supprimées ; images et contenu enregistré intacts.
- **Corrections B03-C2** : `js-corrections-red.txt` (deux reprises à 0 au lieu de 1200 avant rAF) → `js-corrections-green.txt` (pagehide, visibilité, préservation en mode inactif).
- Le contrat HTTP a échoué avant ajout du lecteur de constante ; il teste désormais deux vitesses substituées (137, 299), et le HTTP lit réellement la constante du serveur. Le bloc de mouvement réduit redondant est supprimé (instruction prioritaire de 19h30) ; `behavior:'instant'` est le verrou réel.

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
