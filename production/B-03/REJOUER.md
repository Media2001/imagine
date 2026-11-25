# B-03 — Rejouer sans réensemencer

Depuis `C:/Users/Ced/imagine`. Aucun accès réel, Git, nettoyage de site, compte ou fixture. Le site fictif **imagine-test-demo** doit déjà être démarré et garder sa garde locale B00. Les transports B00/C08 existants sont utilisés tels quels ; aucune modification de l’outil de staging.

## Dépendances de test locales, sans installation globale

Les interpréteurs déjà installés ont été retrouvés et exercés, sans nouveau paquet :

- **HTTP/HTML et final** : `C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe` (BeautifulSoup 4.14.3, html5lib 1.1).
- **Navigateur** : `C:/Users/Ced/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe` (Playwright et Chromium existants).

Le Python par défaut et le venv Hermes n’ont pas `html5lib` : **ne pas les utiliser pour le final ou HTTP**. Le venv B03 n’a pas Playwright : ne pas l’utiliser pour le navigateur. Ne recréer aucun environnement ; aucun paquet n’a été ajouté pendant les corrections. Node est déjà présent. L’option `-B` évite les caches Python dans les tests voisins. Les identifiants fictifs restent lus en mémoire ; aucun cookie, mot de passe ou corps connecté n’est enregistré.

## Recette finale après C15, sans dépôt

```text
C:/Users/Ced/AppData/Local/hermes/cache/scratch/imagine-b03-tests/Scripts/python.exe -B wp/tests/demo/b03-final.py
```

Le final utilise les PHP B03/C09 déjà déployés après vérification de leurs octets et n'envoie aucun fichier. Les sous-commandes historiques isolées peuvent écraser leurs anciens reçus : ne pas les exécuter pour cette réconciliation. Les corrections avaient seulement envoyé `assets/reading.css` et `assets/reading.js`, relus dans `deploy-corrections.json`, préimages dans `theme-before-corrections.json`. Ne pas appeler le constructeur B00 global, `deploy release`, les seeds C08/C09, les actions/reset C15, les recettes mutatrices C12/C14 ou les fixtures du parent. La preuve navigateur existante est réutilisée après liaison aux octets actuels, pas réécrite.

`b03-final.py` relit les six fichiers, exécute les dix assertions PHP B03 via `imagine-demo-build/b03-runtime.php`, les 43 contrôles HTTP, les 8 tests Node, les 15 tests locaux et huit tests unitaires de la garde. Il utilise ensuite **l’exécuteur canonique T01** (1 012 tests / 34 006 assertions) dans un conteneur éphémère isolé, dépôt en lecture seule, réseau absent, sans site ni extension commerciale et sans balayage d'orphelins. Il relit les **149 contrôles C09 natifs** sur le site, sans seed ni upload C09. Les 77 contrôles navigateur existants restent liés aux SHA-256 actuels CSS/JS. Chaque final écrit dans un **nouveau dossier horodaté** `reconciliation-c15/<horodatage>/`; `reconciliation-c15-current.json` pointe le reçu et son SHA-256. Les anciens reçus racine, dont le final `FAILED`, et `corrections-before.json` restent intacts.

L'amendement CSS de 19h30 est déjà déployé : ne pas relancer `b03-reduced-motion.py`. Son reçu est chaîné à `deploy-corrections.json`. Les seuls deltas historiques de sources doivent être exactement les deux assets B03 et les quatre fichiers C15 `EcheancesRegles.php`, `EcheancesNatives.php`, `EcheancesAdmin.php`, `imagine-site.php`. Les octets C15 finaux doivent correspondre localement et à distance à leurs reçus verification/installation/livraison. L'action/reset sémantiquement restaurée doit être documentée par les reçus C15 et le script lié à leur livraison. Aucune exemption C15 dans le contrôle courant : même photographie PHP avant/après les tests B03, égalité exacte des fichiers et des quatre tables non-utilisateur, sinon échec. Snapshot métier natif aussi comparé exactement en mémoire ; aucune adresse ni table utilisateur publiée.

Exception documentaire locale, strictement liée : `plugins/imagine-site/README.md` doit être exactement au SHA-256 de `C-15/livraison.json` et absent des snapshots distants. Aucun autre document ou chemin supplémentaire n'est toléré. Le premier reçu de réconciliation, qui refusait ce README avant qualification, reste conservé ; aucune modification de ce fichier par B03.

La commande obligatoire `powershell.exe -NoProfile -ExecutionPolicy Bypass -File wp/tests/preparer-image.ps1` a été réellement exécutée avec succès : `preparer-image.txt`. Ce script n’a pas été modifié ; aucun nouveau paquet Composer n’est créé par B03. Si les manifests des bibliothèques changent, refaire cette préparation explicitement avant le rejeu.

## Réserve historique conservée, portée du verdict courant

L'ancien final racine `FAILED` n'est pas effacé ni présenté comme vert. Les quatre tables `wp_posts`, `wp_postmeta`, `wp_wc_orders`, `wp_wc_orders_meta` diffèrent vraiment de l'ancienne photographie ; `preservation-reconciliation.json` conserve les paires d'empreintes et les chemins historiques changés. Les seules empreintes ne prouvent pas l'attribution exhaustive de chaque ligne à C15. Le reset autorisé et la restauration sémantique C15 sont liés documentairement ; notes d'audit/dates techniques ne sont pas effacées. Le verdict courant B03 peut être `VERIFIED` sur **sa propre fenêtre exactement stable**, ses sources strictement attribuées, le C09 frais et son HTTP frais, tout en gardant cette réserve rétrospective. PRET désigne prêt à relire dans cette portée, pas une identité historique de tables ni un GO production.

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
