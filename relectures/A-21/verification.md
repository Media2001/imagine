# Vérification A-21 — second et dernier tour

Vérificateur : Claude. Objet : contrôler que les corrections de `corrections/A-21.md` ont été appliquées par Hermès après la fusion, relancer les tests, repérer toute régression.

Méthode : `git diff 16b0e6d2..HEAD` (fusion → HEAD) sur `wp/outils/bascule/a21`, `wp/tests/a21`, le nouveau module partagé `wp/outils/bascule/stream_guard.py` et `production/A-21`. Lecture du code modifié. Relance des tests exécutables en local (Windows, sans Docker). Pas de nouvelle relecture complète.

## 1. Instructions de corrections/A-21.md

### Instruction 1 — R1, filtrage des sorties du processus PHP (bloquant) : **Appliquée**

Correction de fond, par extraction d'un superviseur Python partagé.

- **Superviseur à deux flux jusqu'à terminaison.** Nouveau `wp/outils/bascule/stream_guard.py:22` (`supervise`). Le PHP confiné est lancé par `subprocess.Popen` avec `stdout`/`stderr` en tubes, drainés par deux fils dédiés jusqu'aux deux EOF **et** à la terminaison du processus (`stream_guard.py:45-58`). Plus d'`os.execvp`. Plafond mémoire 64 Kio par flux, délai 120 s.
- **Restitution depuis une liste fermée.** `confine.py:14-25` reconstruit l'unique succès exact (`SUCCESS`) et les refus (`REFUSALS`/`CODES`) ; toute autre sortie → `A21_UNEXPECTED_OUTPUT` (`confine.py:131-133`). Succès incomplet → `A21_SUCCESS_INCOMPLETE` (`confine.py:135`).
- **Sortie après l'annonce de succès refusée.** Le succès n'est publié qu'après terminaison : la restitution `A21_OK` est écrite par le parent (`confine.py:138`), jamais par l'enfant. Une sortie de shutdown après `A21_OK` casse l'égalité `stdout==SUCCESS` → refus.
- **Publication sous dossier privé.** L'enfant écrit dans un `TemporaryDirectory` 0700 ; le rapport n'est renommé vers la sortie publique qu'après `complete_report()` (`confine.py:123-137`), qui vérifie la projection fermée, le JSON canonique, la cohérence JSON/Markdown et l'empreinte de l'audit.
- **Suppression du tampon PHP.** `inventorier-portes` n'a plus `ob_start()`/`ob_end_clean()` (il ne capturait que stdout) ; le filtrage est désormais côté superviseur.
- **Fixtures de bootstrap hostiles ajoutées.** `inside.py:131-157` : extension écrivant sur stdout, sur stderr, `exit('A21_FLOW_CANARY')` précoce, exit vide, faux succès, shutdown stdout, shutdown stderr, sortie volumineuse, stderr binaire, double succès en shutdown, suppression du JSON en shutdown, altération d'un rapport en shutdown. Pour chacune : absence de canari sur tous les flux et dans tout rapport, aucun artefact publié, confinement et base inchangés (`inside.py:153-157`). Confirmé au vert dans le paquet (`result.json`, checks `supervised_bootstrap:*`, `hostile_artifacts_absent:*`, `hostile_confinement_unchanged:*`), exigés par `verify.py:53-57`.

### Instruction 2 — R2, sceller les dépendances courantes dans verify.py (mineur) : **Appliquée**

- `wp/tests/a21/verify.py:11` : liste `DEPENDENCIES` (A-02, A-19, audit, A-11, A-12, staging, module partagé, A-22).
- `verify.py:39-42` : check `exact_current_dependencies` comparant `dependency-snapshot.json` à l'inventaire courant, avec l'exception documentée du README partagé (`readme_contract`, `a02-audit/README.md` retiré du hash).
- `verify.py:71` : `executed_dependency_snapshot` par console (cp1252/utf8).
- Cas de dérive qui doit faire rougir : `test_dependencies.py:18` (dérive réelle sur 6 dépendances → FAIL attendu) et `probes.py:62-75` (mutant délibéré qui retire le scellé → rouge observé, journal `red-drift.json`). Les deux au vert chez moi.

### Instruction 3 — magasin d'extensions, aligner code et README (mineur, décision technique) : **Appliquée** (défaut retenu : lecture directe + README corrigé)

- `Inventory.php` lit `get_option('woocommerce_helper_data', [])` ; `Analysis.php` teste `!empty($helper['auth']['access_token'])` ; aucun appel `WC_Helper::`.
- `README.md:13` reformulé : « A-21 lit directement cette option via `get_option()` […] sans appeler `WC_Helper::is_site_connected()`, pour ne déclencher aucun effet de bord ».
- Test de garde : `test_contract.py:12` (`test_store_option_is_direct_and_documented`), au vert.

### Instruction 4 — test de webhook actif à hôte IP/IPv6 (mineur) : **Appliquée** (défaut retenu : classement best-effort par chaîne + test)

- `unit.php:54-76` : IPv4 littérale, IPv6 entre crochets avec port, casse et formes compactes ; vérifie le classement exact (`same_domain`/`external_domain`), l'absence de résolution DNS/équivalence binaire, et l'absence de projection des littéraux (`CANARY|192.0.2|2001:db8`).
- Garde côté vérificateur : `verify.py:65-67` (`literal_ip_ipv6_pure_cases`), au vert.

## 2. Résultat des tests

Environnement : NUC Windows 11, Python 3.14.6. PHP et Docker ne sont **pas** exécutables ici (non autorisés dans cette session non-interactive) ; le banc natif e2e (`run.py`/`inside.py`) exige un conteneur Linux avec Landlock et les extensions sous licence, hors de ma portée d'exécution — déjà noté à la fusion (Docker/WSL indisponibles).

Ce que j'ai lancé :

- **Suite portable** `python -m unittest discover -p "test_*.py"` dans `wp/tests/a21` : **`Ran 12 tests … OK`** (contract, dependencies, launcher, supervisor).
- **Vérificateur** `python wp/tests/a21/verify.py production/A-21/preuves/final` : **49 checks, `exit_code` 0, aucun FAIL.** Il revalide le paquet de preuves livré par Hermès, y compris : scellés de dépendances et dérive refusée, cas IP/IPv6, tous les cas `supervised_bootstrap:*` hostiles, neutralisation « inconnu, jamais zéro », JSON canonique, cohérence JSON/Markdown, deux consoles (cp1252 + utf8), rejouabilité, empreintes identiques avant/après.

Le paquet atteste donc le vert du banc natif que je ne peux rejouer localement ; mon contrôle porte sur sa cohérence interne et sur les tests portables, tous au vert.

## 3. Régressions ou modifications non demandées

Aucune régression constatée. Deux modifications dépassent le strict périmètre des instructions ; toutes deux sont additives, testées, et vont dans le sens des garanties du lot :

1. **Extraction d'un superviseur partagé** (`stream_guard.py`, `stream_bridge.php`, `stream_refusals.json`) réutilisé par A-22. C'est le mécanisme choisi pour R1 ; A-22 entre en dépendance scellée de A-21 (`verify.py:11`, `run.py:20`). Choix d'architecture sain, mais il élargit la surface au-delà de A-21 seul — à garder en tête si A-22 bouge.
2. **Blocage des quatre pré-filtres Action Scheduler** (`Inventory.php:15-25`) : asynchrone, unique, récurrent, cron, comptés dans `outbound_attempts.scheduled`. Non demandé, mais cohérent avec la règle « aucun appel sortant » de la voie 1. Couvert par `inside.py:50-53` et le compteur attendu passe de 1 à 5 (`inside.py:122`). Pas d'effet de bord : la file reste intacte, la base inchangée (checks `guard_probe_database_unchanged`).

L'ancien `echo 'A21_BOOT_PRIVATE_CANARY'` du bootstrap de sonde a été retiré (il serait désormais refusé par le superviseur) : cohérent, remplacé par les fixtures hostiles dédiées.

Les modifications restantes de l'arbre de travail (`wp/outils/bascule/a25/*`, `wp/tests/a25/*`, `a24/*`) relèvent d'autres lots et n'entrent pas dans cette vérification.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions de la fusion, dont le bloquant R1, sont appliquées et vérifiables dans le code et dans les tests. La suite portable est au vert (12/12) et le vérificateur revalide le paquet complet (49/49, exit 0) sans aucun FAIL. Aucun problème de fond restant ; les deux ajouts hors périmètre sont sains et testés.

Rappel doctrine : ce verdict clôt la vérification de code ; il n'est pas un GO au sens du §3 (aucune bascule, aucun accès au réel). La décision d'avancer appartient à Ced.
