# Vérification A-20 — tour 3 (après reprise d'Hermès sur le gardien commun)

Vérificateur : Claude. Date : 2026-11-26. Base « déjà vérifiée » : commit `4d4efd77` (HEAD au moment de `verification.md`, 17 h 23). Comparaison jusqu'à HEAD `ab843bc2` (19 h 23). Diff lu sur `wp/outils/bascule/`, `wp/tests/a20/`, `wp/tests/a22/`, `production/A-20/`. Pas de relecture complète refaite : seuls les écarts depuis le dernier tour sont examinés. Aucun fichier modifié.

**Ce qui a changé, et pourquoi.** Hermès a repris A-20 **après la fusion A22 de 17 h 53**, qui a durci le gardien commun des flux. Le code métier d'A-20 (`Analysis.php`, `Inventory.php`, `Command.php`, `confine.py`, `report.py`, `README.md`) est **inchangé** : `git diff 4d4efd77..HEAD -- wp/outils/bascule/a20/` = 0 ligne. Les seuls changements de code sous A-20 sont dans le **gardien partagé** et les **dépendances rejouées** :
- `wp/outils/bascule/stream_guard.py` (+24 lignes) ;
- `wp/tests/a20/run.py` (liste des dépendances), `wp/tests/a20/verify.py` (contrat de réception) ;
- `wp/tests/a22/*` (canaris et témoins communs).

Tout le reste du delta `production/A-20/` est le **re-scellé** du paquet neuf `a22-corrections-1753/a20-matrix-final-02` (reçus, empreintes, manifeste, PRET).

## 1. Consignes et arbitrages concernés

### C-0 — « A-20, A-21, A-22 ensemble, sur les mêmes sources ; si une source commune change, les trois matrices se rejouent » (`A-FAIRE.md:19`) — **Appliquée**
Le gardien commun a bougé (fusion A22 de 17 h 53) ; A-20 a été rejoué et re-scellé en paquet neuf. Dépendances exécutées réalignées : `wp/tests/a20/run.py:18` ajoute `stream_reports.py` et `stream_contract.php`. Le vérificateur du lot lie bien le paquet aux sources courantes (`all_executed_dependencies_unchanged` dans `candidate-verification.json`, exit 0).

### Règle « un canari par canal » — affichage / deux flux / arrêt anticipé / fin de processus (`A-FAIRE.md:31`) — **Appliquée et étendue au canal fichier**
La reprise ajoute deux canaux qui manquaient : une fonction d'arrêt (`register_shutdown_function`) qui écrit **directement dans un fichier de sortie** (`.md`/`.csv`/`.json`), en dehors des flux surveillés.
- Canaris : `wp/tests/a22/channels.py:17` (`shutdown_file`) et `:18` (`shutdown_json`).
- Côté A-20, ces deux canaux sont refusés en **`A20_REPORT_INVALID`** (`wp/tests/a22/channels.py:79-81`), code fermé, sans donnée source.
- Garde : le jeton de succès est désormais **lié à l'empreinte SHA-256 des fichiers produits** (`wp/outils/bascule/stream_guard.py:119` `final_binding`, appelé `:175`) et `complete()` exige en plus `stream_reports.validate(...)` (`:132-140`) ; un contrat PHP est préchargé (`auto_prepend_file=stream_contract.php`, `:170`). Un fichier modifié après coup par une fonction d'arrêt casse l'empreinte → refus.
- Contrat de réception A-20 relevé en conséquence : `wp/tests/a20/verify.py:65` exige **25** contrôles de canaux (était 21), dont exactement **2 `shutdown_file` et 2 `shutdown_json`**.

### « Un seul gardien, pas deux » (`docs/arbitrages-2026-11-26.md`, passage de 13 h, §A-20/A-21) — **Appliquée**
Une seule implémentation des tuyaux : `wp/outils/bascule/stream_guard.py`, partagée. A-20 ne duplique rien ; il garde son contrôle strict propre (`report.py`/`report-contract.json`, inchangés).

### Ordre des `PRET` : A-20/A-21/A-22 ensemble sur mêmes sources, sur gardien figé (`docs/arbitrages-2026-11-26.md`, passage de 16 h, §A-20…A-23 ; `A-FAIRE.md:19`) — **Appliquée**
Gardien figé par la fusion A22 ; `production/A-20/PRET` repassé à `2026-11-26T19:21:…` (preuves `files/rapports/2026-11-26-19h21-verification`), cohérent avec la finalisation parent (`FINALISATION.md:1-5`, rejeu global 1 126 tests).

### Défauts techniques Q1/Q2 de `corrections/A-20.md` (`without_product_line` ; « annuel » = `1 year` ∪ `12 month`) — **Appliquée, inchangée**
Garantie par l'absence de diff sur `wp/outils/bascule/a20/` : `Analysis.php` non modifié depuis le tour 2. Les deux défauts restent conformes à ce qu'`verification.md` a vérifié.

### Arbitrage A-22 « `error_log` vers le périphérique de rejet, seul chemin inscriptible, prouvé par un test » (passage de 16 h, §A-20…A-23) — **Non applicable à A-20 (traité en A-12/A-22)**
Se reflète dans les tests partagés : `wp/tests/a22/channels.py:22` (`discard_fence_probe`, 12 contrôles de droits noyau), et l'ajout d'`A12_PATH_INVALID` au gardien (`stream_guard.py:144`). Hors périmètre A-20 ; à juger dans les relectures d'A-12 et d'A-22.

## 2. Résultat des tests

Commande autorisée, écrite exactement : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1`

Dernière ligne :

> `REJEU : 1126 tests, 35550 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS`

Dont `T01 TOOL : a20 ; 23 controls ; 0 failures ; exit=0`. Conteneur jetable, `network=none`, dépôt monté en lecture seule, nettoyage vérifié.

Limite inchangée (déjà actée aux tours 1 et 2) : `rejouer.ps1` ne joue que la couche **PHP pure** d'A-20 (23 contrôles de `unit.php`). La matrice native confinée (classique + HPOS, empreintes avant/après, canaux de canaris, parcours du mode d'emploi) exige un conteneur Linux + staging et n'est **pas** rejouable indépendamment sur ce poste Windows. Je me suis donc appuyé, comme aux tours précédents, sur les reçus scellés, contrôlés cohérents avec le nouveau contrat :
- `production/A-20/preuves/final/{utf8,cp1252}/native/a22-channels.json` : exit 0, **25 contrôles, 2 `shutdown_file` + 2 `shutdown_json`, tous PASS** dans les deux consoles ;
- `production/A-20/candidate-verification.json` : **111 contrôles, 0 FAIL, exit 0** ;
- `production/A-20/verification-probes.json` : **7 sondes anti-recyclage/anti-altération, 0 FAIL, exit 0**.

## 3. Régressions ou modifications non demandées

- **Aucune régression dans le périmètre A-20.** Code métier intact (diff vide), suite PHP pure au vert, paquet interne cohérent avec le contrat relevé.
- **Modifications non littéralement listées mais justifiées** par la règle « un canari par canal » et la fusion A22 : le durcissement du gardien (`final_binding` + contrat PHP + empreinte SHA-256 des fichiers) et les deux nouveaux canaux. Elles corrigent un trou réel (écriture directe dans un fichier de sortie par une fonction d'arrêt) et sont couvertes par témoin (mutation `mutation_without_final_contract_leaks`, `wp/tests/a22/replay.py:67-79`).
- **Point d'attention hors périmètre A-20** (déjà signalé au tour 2, toujours vrai) : `stream_guard.py` est partagé (A-03/A-11/A-12/A-20/A-21/A-22). L'ajout d'`A12_PATH_INVALID` (`:144`) et de la sonde `discard_fence_probe` relève d'A-12/A-22 : à vérifier dans leurs relectures, pas ici. La suite globale (1 126 tests) les couvre au vert.

## 4. Verdict

**Prêt pour la clôture.**

La reprise d'Hermès est entièrement justifiée par la fusion A22 de 17 h 53 et la règle « un canari par canal » : elle ne rouvre aucune décision métier (sources A-20 inchangées), elle ferme un canal de fuite supplémentaire (fichier de sortie altéré en fin de processus) et le prouve par canari + témoin. Toutes les consignes et tous les arbitrages concernés sont appliqués. Suite autorisée au vert (1 126 tests ; a20 23/23). Paquet re-scellé, lié aux sources courantes, interne cohérent (111 contrôles, 7 sondes, 25 canaux dont 2+2, 0 FAIL partout). Aucune régression, aucune modification A-20 non demandée, aucune question visuelle ou touchant au réel.

**Réserve non bloquante, inchangée :** le rejeu **indépendant** de la matrice native confinée n'est pas reproductible sur ce poste Windows (limite d'environnement actée dès le tour 1) ; la finalisation parent du 19 h 21 en porte le rejeu global. **Et, comme tout verdict de relecture/vérification, celui-ci n'est pas un GO** au sens du §3 de la doctrine : import, staging et déploiement restent des commandes de Ced.
