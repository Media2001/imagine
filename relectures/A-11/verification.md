# Vérification A-11 — second et dernier tour

Date : 2026-11-26. Vérificateur : Claude. Objet : contrôler l'application de `corrections/A-11.md` après correction par Hermès (`production/A-11/corrections-26nov.md`). Base de comparaison : état relu au commit `18f8b57` (01:53) → HEAD. Diff lu sur `wp/outils/bascule/a11/`, `wp/tests/a11/`, `wp/tests/a02-audit/README.md` et `production/A-11/`. Ceci n'est pas une relecture complète.

## 1. Instructions de la fusion, une à une

| # | Instruction | État | Preuve (fichier:ligne) |
|---|---|---|---|
| 1 | **(C1)** Refuser avant bootstrap la personnalisation du dossier mu-plugins ; de préférence refus par défaut de toute constante de disposition non reconnue | **Appliquée** | `Runtime.php:19-39` nouvelle `validateConfiguration()` : tout `define(...)` hors liste blanche connue et tout `const` sont refusés (`A11_CONFIG_OVERRIDE_UNSUPPORTED`). `WPMU_PLUGIN_DIR` n'est pas dans la liste → refusé. Appelée avant `define('ABSPATH')` (`Runtime.php:53`). |
| 2 | **(C2)** Distinguer lecture `posts` échouée d'un résultat vide ; contrôler `last_error` ; même fail-closed sur toute lecture native ; test d'échec SELECT | **Appliquée** | `Inventory.php:59-61` : `last_error`/`!is_array` → `A11_POSTS_FAILED`. `Inventory.php:64-66` : `get_post` non-`WP_Post` → `A11_POST_READ_FAILED`. Double barrière `ReadOnlyDb.php:30-33` : tout `SELECT` faux sous clôture → `A11_READ_FAILED`. |
| 3 | **(Mineur)** Reformuler la justification du périmètre des auteurs (comportement réel, pas « parité sitemap ») | **Appliquée** | Commentaire `Inventory.php:101` réécrit (« All public types except pages/attachments, including types without author support »). README `a11/README.md:43` réécrit en ce sens. Comportement inchangé. |
| 4 | **(Mineur)** Nommer `adresses.json` et son rôle dans le mode d'emploi partagé | **Appliquée** | `wp/tests/a02-audit/README.md:64` : `adresses.json` nommé avec son rôle (données structurées + preuve + empreinte du rapport A-02 pour l'outillage A-09). |
| 5 | **(Hors A-11)** Relayer la suite autorisée rouge (3 échecs WIP `ExtractionsRegles`) | **Relayée, non re-vérifiable ici** | `corrections-26nov.md` déclare T01 global vert (1 062 tests), les 3 échecs WIP n'étant plus observés. Non reproductible dans ma session (Docker/MySQL absents). À confirmer par Ced hors A-11. |

Décisions techniques (défauts proposés dans la fusion) : le défaut n°4 « refus par défaut des constantes non reconnues » a bien été retenu pour C1, forme la plus robuste. Périmètre des auteurs et `adresses.json` conservés comme prévu.

## 2. Tests

- **Contrôle pur indépendant** `python wp/tests/a11/verifier.py production/A-11/preuves/8b3b9bdcf308` → `verified: true`, **0 FAIL** : 19 checks unitaires, 300 checks natifs, 7 checks runner. Les 14 fichiers source du paquet ont une empreinte SHA-256 **identique au dépôt actuel** : le paquet correspond bien au code corrigé, pas à l'ancien.
- Ma ré-exécution reproduit à l'identique `production/A-11/verification-corrections-26nov.json` (mêmes comptes : `classic-pretty = 25`, `plain = 26`, `attachments-disabled = 22`, `static-front = 24`, idem HPOS).
- Le verifier contrôle la présence nominale des **nouveaux tests C1/C2** : `custom_mu_before_bootstrap`, `site_symlink_named`, `failed_select_no_validated_packet`, et `dropin_refused_before_execution` pour les 6 fichiers (`object-cache.php`, `advanced-cache.php`, `db.php`, `sunrise.php`, `wordfence-waf.php`, `.user.ini`), classic et hpos. Tests effectivement présents côté code (`wp/tests/a11/inside.py:127-160`, `wp/tests/a11/unit.php:28-57`).
- **Non rejoué** : la suite native Docker (`run.py`) — Docker et MySQL absents de la session, contrainte identique à celle des deux relecteurs du premier tour. Le contrôle pur ci-dessus est la barrière indépendante disponible : il lie cryptographiquement le paquet de preuves au code corrigé et refuse tout FAIL ou toute empreinte divergente. Pas d'accès site/base ouvert (conforme doctrine §3).

## 3. Régressions ou modifications non demandées

- **Dans le périmètre A-11 : aucune régression.** Les seuls fichiers A-11 modifiés sont `a11/` (Runtime, Inventory, ReadOnlyDb, README, `inventorier-adresses`), les tests `a11/` (inside, unit, verifier) et une ligne du mode d'emploi partagé `a02-audit/README.md` (instruction 4). Chaque modification correspond à une instruction.
- **Durcissement volontaire, pas une régression.** Le passage d'une liste d'exclusion à un refus par défaut des constantes non reconnues est le défaut technique n°4 retenu ; il est documenté (`a11/README.md`, section « Refus nommé »). Il élargit le refus, conformément à l'objectif « ne jamais publier un inventaire partiel comme complet ».
- **Modification d'un doc d'un lot clos (A-02) :** `a02-audit/README.md` a été touché — c'est exactement l'instruction 4 (« les deux lignes du mode d'emploi A-02 »), donc demandé. Une ligne, rôle de `adresses.json` ajouté, rien d'autre.
- **Hors périmètre, à ne pas imputer à A-11 :** le diff `wp/` depuis la base de relecture contient du travail parallèle sur d'autres chantiers (a12, a14, a15, c09, c16, c19, staging-court, imagine-site). Rien de cela n'est une régression A-11 ; c'est de l'activité concurrente du NUC, hors de ce lot.

## 4. Verdict

**Prêt pour la validation de Ced.**

Les quatre instructions A-11 (C1, C2, deux mineures) sont appliquées, au bon fichier et à la bonne ligne. Le contrôle pur indépendant est vert, 0 FAIL, et le paquet est lié au code corrigé par empreinte. Aucune régression dans le périmètre A-11. Aucune question visuelle ni touchant au réel n'est ouverte (la fusion l'avait déjà constaté). L'instruction 5 est un sujet hors A-11 à confirmer par ailleurs ; elle ne bloque pas ce lot.

Réserve honnête, non bloquante : la suite native Docker n'a pas pu être rejouée dans cette session (Docker/MySQL absents), comme pour les deux relecteurs. La confiance repose sur le vérificateur pur qui ancre le paquet au code actuel. Ce n'est pas un problème de fond ; c'est la contrainte d'environnement déjà actée en fusion.

**Rappel : un verdict de vérification n'est pas un GO (§3/§6 doctrine).** Il clôt la vérification du second tour ; la validation finale appartient à Ced.
