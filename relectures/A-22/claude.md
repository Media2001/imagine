# Relecture A-22 — Un seul gardien pour les sorties des outils d'inventaire

Relecteur : Claude (indépendant). Date : 2026-11-26.
Brief : `briefs/A-22-superviseur-des-sorties.md`. Cahier des charges cité : §4.4, §2.5.
Production relue : `production/A-22/`, `wp/outils/bascule/`, `wp/tests/a22/`.

> Je n'ai **pas** lu `relectures/A-22/codex.md`. Pas de fusion à ce stade.

## Rejeu de la suite PHP (commande autorisée)

Commande lancée, sans argument, telle quelle :

```
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ./wp/tests/rejouer.ps1
```

Conteneur jetable, dépôt monté en lecture seule, sans réseau. Lignes reportées :

```
T01 ISOLATION : network=none ; rootfs=ro ; mount=/mnt/c/Users/Ced/imagine/wp:/repo/wp:ro ; ports=none ; cap-drop=ALL ; no-new-privileges
T01 CLEANUP : absence verifiee de imagine-t01-80d3e5feed6048a2b629abfb1ed7da8c
OUTILS : 16 outils, 306 contrôles, 0 échecs ; hors rejeu : aucun
REJEU : 1123 tests, 34569 assertions, 0 échecs, 0 erreurs, 0 ignorés — PASS
```

Non-régression des lots clos : verte. C'est la preuve exigée par le brief pour les lots clos (« le rejeu de sa suite existante, verte, suffit »).

**Limite de vérification.** Le paquet de preuves propre à A-22 est une matrice Python/Docker sous Windows (`wp/tests/a22/matrix.py`, Python 3.14, deux consoles). Je ne l'ai pas rejouée : elle demande Docker/WSL et un interpréteur Windows 3.14, hors de ma commande autorisée (seul `rejouer.ps1`). Je l'ai **relue**, pas réexécutée. Le reçu livré (`production/A-22/candidate-verification.json`) atteste **159 contrôles PASS en UTF-8, 159 en cp1252, code 0, stderr vide**, sur le paquet `preuves/final` (matrice `a22-matrix-final-07`, 42 commandes, code 0).

## 1. Conformité

- **Un seul gardien.** `wp/outils/bascule/stream_guard.py` est l'unique lecteur de processus et des deux flux (`supervise`). A20 et A21 l'appellent (`a20/confine.py:68`, `a21/confine.py:33` ; test `test_a20_a21_call_same_function_not_copies`). A12, A14, A15–A19 passent par `guard.inventory(...)`. A03/A11 gardent leur ligne PHP via le pont `stream_bridge.php` qui relance `stream_guard.py`. Conforme au « point commun » demandé.
- **Tableau des outils** présent dans `production/A-22/notes.md`. J'ai vérifié ses deux affirmations centrales : A02 (`audit`) et A10 (`inventorier-codes`) **ne bootstrappent pas** le WordPress du site (recherche `wp-load|wp-settings|Runtime::boot|wp-blog-header` sur `wp/outils/bascule/` : ni `audit` ni `inventorier-codes` n'y figurent ; A10 charge seulement la bibliothèque d'audit en `IMAGINE_AUDIT_LIBRARY_ONLY` + PDO). A13 est un lecteur CSV hors ligne, sans PHP. Leur exclusion du gardien est donc fondée : aucune extension tierce ne s'exécute dans ces processus.
- **Commandes du mode d'emploi inchangées.** `documented.json` fige les lignes documentées ; le test `test_documented_commands_are_exact_source_lines` et la sonde `documented_only_literal_arguments` (deux par lot concerné) vérifient qu'elles tournent telles quelles. Arguments et codes de refus historiques préservés (tests `test_legacy_php_path_refusals_are_preserved_by_the_proxy`, `..._basename_and_exists_codes...`, `test_a14_legacy_generic_refusal_is_preserved`).
- **Arrêt précoce et sortie tardive = refus.** Couverts (voir §2).
- **Rien de retenu n'est écrit.** `channels.py:40` vérifie, par canari, l'absence des octets dans tout fichier produit ; `verify.py:120` (`no_retained_untrusted_payload`) rebalaie tout le paquet. Conforme.
- **Ligne du mode d'emploi commun** : livrée dans `readme-ajout.txt` et déjà intégrée, à l'identique et une seule fois, dans `wp/tests/a02-audit/README.md:83` (le README partagé des outils). A23 la référence déjà comme dépendance (`.../README.md:87`).
- **`production/A-22/PRET`** présent (« prêt à relire, non clos », écrit par le parent). Mon verdict ne vaut pas GO (doctrine §6).

**Interprétations à signaler (doctrine §1).**
1. *Rattachement au cahier des charges.* §4.4 (paywall côté serveur) et §2.5 (protection du flux vers Odoo) ne régissent pas littéralement l'outillage interne d'inventaire. Le brief les cite par analogie : « aucun chemin ni aucun nom tiré du site ne sort, sortie d'erreur comprise ». L'esprit est respecté ; le lien reste analogique, pas une règle métier directe.
2. *A14.* Le brief suggérait de le **contrôler** par les mêmes canaris « pas réécrit » (ou de partager le gardien « au besoin »). Hermès l'a fait passer par `guard.inventory`, ce qui corrige les deux défauts que le « Pourquoi » du brief lui reproche (refus par expression régulière trop large, fichiers partiels survivants). Choix cohérent et documenté (`notes.md`), mais il **remplace les anciens codes de refus d'A14 par la liste fermée commune** (repli `A14_FAILED`). C'est « ce qui peut sortir du processus », donc dans le périmètre ; à confirmer qu'aucun appelant externe ne dépendait des anciens codes A14.

## 2. Exactitude — déroulé à la main

Gardien : `supervise` lit les deux flux en threads bornés (64 Kio/flux), attend la fin du processus **et** l'EOF des deux tubes, puis `inventory` statue : succès **seulement si** `code==0` **et** `stdout==SUCCESS[outil]` exact **et** `stderr==b''` **et** rapport `complete()`. Sinon `closed_refusal` renvoie un code de la liste fermée, jamais les octets bruts.

Cas déroulés (extension fictive `000-a22-hostile.php`, active sous `A22_SUPERVISED`/`*_CONFINED`) :

- **Canari 1 — écriture directe sur stdout** (`fwrite(STDOUT,…)`, A15). stdout ≠ `A15_OK …` → `stream_guard.py:159` → `closed_refusal` → `A15_PROCESS_OUTPUT_INVALID`, stdout vide côté opérateur, aucun fichier produit. **Refus net.**
- **Canari 2 — écriture directe sur stderr** (A16/A12). `stderr!=b''` → même branche → refus. Le canari n'étant pas dans la liste fermée, `closed_refusal` retourne le code générique, pas l'octet reçu (test `test_closed_refusal_never_accepts_prefix_or_site_names`). **Refus net.**
- **Canari 3 — affichage puis arrêt pendant le chargement** (`echo …; exit(0)`). Code 0 mais stdout ≠ SUCCESS → refus. **« Arrêt avant la fin, même code 0 » honoré.**
- **Cas limite — arrêt silencieux** (`exit(0)` sans sortie). stdout vide ≠ SUCCESS → refus. Couvert par le canari `silent_exit`.
- **Canari 4 — fonction de fin de processus qui imprime** (`register_shutdown_function` écrivant après le succès). `supervise` attend l'EOF, donc stdout = `…_OK…` + octets de shutdown ≠ SUCCESS → refus. Confirmé par `test_common_guard_waits_for_real_child_termination` (un `atexit` tardif est bien capturé). **« Sortie après l'annonce de succès » honoré.**
- **Mutation témoin** (`replay.py:43`) : on remplace **uniquement** `supervise` par un passe-plat dans une copie jetable ; le canari ressort alors dans les flux (`mutation_without_guard_leaks`), prouvant que c'est bien le gardien qui ferme la porte. Exigée par le brief, présente deux fois (deux magasins), jamais conservée en octets.

Les sept canaux (stdout/stderr directs, echo+exit, exit silencieux, shutdown stdout/stderr/echo) sont exercés par outil concerné, sur magasin classique **et** HPOS, et le site est rephotographié avant/après (`channels.py:45`). Déroulé cohérent avec le code.

## 3. Tests

- **Suite PHP** : verte (ligne REJEU ci-dessus), lancée par moi.
- **Suite Python A-22** (`test_guard.py`, `test_contract.py`) et **matrice** : attestées vertes par le reçu du producteur (159/159 par console) ; relues, non réexécutées (voir limite).
- **TDD** documenté (rouge puis vert) dans `notes.md` (quatre tests du gardien d'abord rouges ; frontières d'arguments A12/A20 d'abord rouges).
- **Les tests vérifient la règle, pas le code.** Bons exemples : `test_closed_refusal_never_accepts_prefix_or_site_names` (un nom tiré du site est rejeté vers un code fermé), `test_partial_report_is_not_complete` (rapport partiel ou fichier en trop refusé), `test_empty_wp_path_is_not_promoted_to_the_current_directory`, `test_descendant_holding_pipes_cannot_extend_deadline` (un descendant tenant les tubes ne prolonge pas le délai), `test_nonexistent_python_banks_are_declared_not_reported_green` (A03/A11 sans banque Python : absence déclarée, jamais un code 5 maquillé en vert).
- **Cas limites couverts** : débordement > 64 Kio, délai dépassé, transport Unicode stdin, deux formes de reçus hérités (A02 `tests` absent d'`exit_code`, A03 dictionnaire `tests`).

## 4. Sécurité et données

- Aucun secret, aucune donnée réelle : banc fictif, canaris inventés, adresses d'essai.
- **Aucun octet tiers ne sort** : flux jamais réémis bruts ; seuls une constante de succès ou un code fermé sont écrits ; dictionnaire de messages à clé = octets exacts (pas de préfixe, pas de regex sur du texte du site).
- **Confinement** conservé : Landlock en écriture limitée au dossier privé (+ `/dev/null` major 1/minor 3 pour `error_log`), `disable_functions=mail,exec,shell_exec,…`, `display_errors=0`, `log_errors=0`, `error_log=/dev/null`. Publication par `rename` depuis un `TemporaryDirectory` privé `0700`, sortie forcée hors du dépôt et hors du site (`inventory` lignes 139–142).
- Rien n'est journalisé ni mis en reçu : vérifié par balayage du paquet.

## 5. Doctrine

- Entrées PHP (`non-regression`, `a11/inventorier-adresses`, `stream_bridge.php`) : `declare(strict_types=1)`, espace de noms `Imagine\`, PSR-12 — contrôle de style vert (`strict_psr12_current_common_entrypoints`), zéro erreur/avertissement.
- **Standard d'abord** : le gardien est extrait du candidat A21 existant, pas réinventé ; une seule implémentation.
- **Mineur (DRY).** Le vrai point commun est `supervise`. La logique d'enclos de sortie (dossier privé, regex de nom, garde d'audit, refus d'existant) est en revanche ré-implémentée en trois endroits : `stream_guard.inventory`, `a20/confine.py`, `a21/confine.py`. Acceptable car A20/A21 conservent leurs validateurs de rapport propres, mais la duplication mérite d'être notée.
- **Mineur.** `a20/confine.py:69` mappe le délai dépassé sur `A20_PROCESS_OUTPUT_INVALID` (pas de code de délai dédié). Les deux sont des refus fermés sans fuite ; seule la granularité de diagnostic est perdue.

## Verdict

**Conforme.**

Le lot fait ce que le brief demande : un gardien unique, les outils concernés y passent, arrêt précoce et sortie tardive refusés, rien de retenu n'est écrit, commandes et codes de refus préservés (sauf A14, assumé), non-régression PHP verte, ligne commune intégrée.

Points classés :

- **Bloquant** : aucun.
- **Important** : aucun.
- **Mineur**
  1. Rattachement §4.4/§2.5 analogique — interprétation à acter.
  2. A14 : codes de refus désormais la liste fermée commune ; confirmer qu'aucun appelant ne dépendait des anciens.
  3. Duplication de l'enclos de sortie entre `inventory`, `a20`, `a21` (§5).
  4. A20 : délai mappé sur `PROCESS_OUTPUT_INVALID` (§5).
- **Limite de relecture** : la matrice Python/Docker d'A-22 n'a pas été réexécutée par moi (hors commande autorisée) ; verdict appuyé sur le reçu `candidate-verification.json` (159/159, code 0), relu.

Rappel doctrine : ce verdict **n'est pas un GO**.

## Suite

`relectures/A-22/codex.md` existe mais n'a pas été ouvert, conformément à la consigne. Fusion non réalisée (demandé de ne pas la faire encore).
